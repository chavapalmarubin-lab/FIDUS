"""
FIDUS Referral System API
Manages salespeople, commissions, and referral tracking
"""

from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel
import sys
import secrets
sys.path.append('/app/backend')

# Use new field_registry for authoritative transformations
from validation.field_registry import transform_salesperson, transform_investment, transform_to_api_format

# JWT Authentication
from auth.jwt_handler import verify_password, get_password_hash, create_access_token, verify_token
from auth.dependencies import get_current_agent, get_current_agent_optional

router = APIRouter(prefix="/api", tags=["Referrals"])

# Database will be injected via init_db()
db = None

def init_db(database):
    """Initialize database connection"""
    global db
    db = database

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SalespersonCreate(BaseModel):
    name: str
    email: str
    phone: str
    wallet_details: Optional[Dict] = None
    notes: Optional[str] = ""

class SalespersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    wallet_details: Optional[Dict] = None
    active: Optional[bool] = None
    notes: Optional[str] = None

class CommissionPaymentDetails(BaseModel):
    method: str = "crypto_wallet"
    reference: str = ""
    hash: str = ""
    notes: str = ""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    from bson.decimal128 import Decimal128
    
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == "_id":
                result["id"] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, Decimal128):
                # Convert Decimal128 to float
                result[key] = float(value.to_decimal())
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = serialize_doc(value)
            elif hasattr(value, "__dict__"):
                result[key] = str(value)
            else:
                result[key] = value
        return result
    
    return doc

async def update_salesperson_metrics(salesperson_id: str):
    """Recalculate all metrics for a salesperson"""
    sp_id = ObjectId(salesperson_id)
    
    # Count clients
    total_clients = await db.clients.count_documents({"referred_by": sp_id})
    active_clients = await db.clients.count_documents({
        "referred_by": sp_id,
        "status": "active"
    })
    
    # Sum investments
    investments = await db.investments.find({"referred_by": sp_id}).to_list(None)
    total_sales = sum(float(inv.get("amount", 0)) for inv in investments)
    active_investments = len([inv for inv in investments if inv.get("status") in ["incubation", "active"]])
    
    # Sum commissions
    all_commissions = await db.referral_commissions.find({"salesperson_id": sp_id}).to_list(None)
    total_earned = sum(float(c.get("commission_amount", 0)) for c in all_commissions)
    paid_commissions = [c for c in all_commissions if c.get("status") == "paid"]
    total_paid = sum(float(c.get("commission_amount", 0)) for c in paid_commissions)
    pending = total_earned - total_paid
    
    # Next payment
    next_commissions = [c for c in all_commissions if c.get("status") in ["pending", "ready_to_pay", "approved"]]
    next_commissions.sort(key=lambda x: x.get("commission_due_date", datetime.max))
    next_date = next_commissions[0].get("commission_due_date") if next_commissions else None
    next_amount = float(next_commissions[0].get("commission_amount", 0)) if next_commissions else 0
    
    # Update salesperson
    await db.salespeople.update_one(
        {"_id": sp_id},
        {
            "$set": {
                "total_clients_referred": total_clients,
                "active_clients": active_clients,
                "total_sales_volume": total_sales,
                "active_investments": active_investments,
                "total_commissions_earned": total_earned,
                "commissions_paid_to_date": total_paid,
                "commissions_pending": pending,
                "next_commission_date": next_date,
                "next_commission_amount": next_amount,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

async def generate_payment_schedule_for_investment(investment: dict) -> list:
    """Generate payment schedule based on investment product type"""
    fund_config = {
        "FIDUS_CORE": {
            "rate": 0.015,
            "frequency_days": 30,
            "first_payment_days": 90
        },
        "FIDUS_BALANCE": {
            "rate": 0.025,
            "frequency_days": 90,
            "first_payment_days": 150
        },
        "FIDUS_DYNAMIC": {
            "rate": 0.035,
            "frequency_days": 180,
            "first_payment_days": 240
        }
    }
    
    product = investment.get("product", "")
    if product not in fund_config:
        raise HTTPException(status_code=400, detail=f"Unknown product: {product}")
    
    config = fund_config[product]
    amount = float(investment.get("amount", 0))
    start_date = investment.get("investment_date")
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    
    contract_end = start_date + timedelta(days=426)
    monthly_interest = amount * config["rate"]
    
    schedule = []
    payment_date = start_date + timedelta(days=config["first_payment_days"])
    payment_num = 1
    
    # Calculate interest per payment based on frequency
    if config["frequency_days"] == 30:
        interest_per_payment = monthly_interest
    elif config["frequency_days"] == 90:
        interest_per_payment = monthly_interest * 3
    elif config["frequency_days"] == 180:
        interest_per_payment = monthly_interest * 6
    else:
        interest_per_payment = monthly_interest
    
    # Regular payments
    while payment_date < contract_end:
        schedule.append({
            "payment_number": payment_num,
            "date": payment_date,
            "interest_amount": interest_per_payment,
            "type": "interest"
        })
        payment_date = payment_date + timedelta(days=config["frequency_days"])
        payment_num += 1
    
    # Final payment
    schedule.append({
        "payment_number": payment_num,
        "date": contract_end,
        "interest_amount": interest_per_payment,
        "principal": amount,
        "type": "final"
    })
    
    return schedule

# ============================================================================
# SALESPEOPLE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/admin/referrals/overview")
async def get_referrals_overview():
    """Get overview statistics for referral system"""
    try:
        from bson import Decimal128
        
        # Count active salespeople  
        active_salespeople = await db.salespeople.count_documents({"active": True})
        total_salespeople = await db.salespeople.count_documents({})
        
        # Calculate total sales volume from all salespeople
        pipeline = [
            {"$match": {"active": True}},
            {"$group": {
                "_id": None,
                "total_sales": {"$sum": "$total_sales_volume"}
            }}
        ]
        sales_result = await db.salespeople.aggregate(pipeline).to_list(1)
        
        if sales_result and sales_result[0].get("total_sales"):
            total_sales_raw = sales_result[0]["total_sales"]
            if isinstance(total_sales_raw, Decimal128):
                total_sales = float(total_sales_raw.to_decimal())
            else:
                total_sales = float(total_sales_raw)
        else:
            total_sales = 0
        
        # Calculate total commissions (all statuses)
        commission_pipeline = [
            {"$group": {
                "_id": None,
                "total": {"$sum": "$commission_amount"},
                "pending_total": {
                    "$sum": {
                        "$cond": [
                            {"$in": ["$status", ["pending", "ready_to_pay", "approved"]]},
                            "$commission_amount",
                            0
                        ]
                    }
                }
            }}
        ]
        commission_result = await db.referral_commissions.aggregate(commission_pipeline).to_list(1)
        
        if commission_result and commission_result[0].get("total"):
            total_comm_raw = commission_result[0]["total"]
            if isinstance(total_comm_raw, Decimal128):
                total_commissions = float(total_comm_raw.to_decimal())
            else:
                total_commissions = float(total_comm_raw)
        else:
            total_commissions = 0
            
        if commission_result and commission_result[0].get("pending_total"):
            pending_comm_raw = commission_result[0]["pending_total"]
            if isinstance(pending_comm_raw, Decimal128):
                pending_commissions = float(pending_comm_raw.to_decimal())
            else:
                pending_commissions = float(pending_comm_raw)
        else:
            pending_commissions = 0
        
        # Get top salespeople
        top_salespeople = []
        salespeople = await db.salespeople.find({"active": True}).sort("total_sales_volume", -1).limit(10).to_list(10)
        
        for sp in salespeople:
            sp_data = transform_salesperson(sp)
            top_salespeople.append(sp_data)
        
        return {
            "totalSalespeople": total_salespeople,
            "activeSalespeople": active_salespeople,
            "totalSalesVolume": total_sales,
            "totalCommissions": total_commissions,
            "pendingCommissions": pending_commissions,
            "topSalespeople": top_salespeople
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting overview: {str(e)}")

@router.get("/admin/referrals/salespeople")
async def get_all_salespeople(active_only: bool = True):
    """Get all salespeople with performance metrics"""
    from bson import Decimal128
    
    query = {}
    if active_only:
        query["active"] = True
    
    salespeople = await db.salespeople.find(query).sort("name", 1).to_list(None)
    
    # Enrich with real-time metrics
    for sp in salespeople:
        # Use salesperson_id field (not MongoDB _id)
        sp_id = sp.get("salesperson_id") or str(sp["_id"])
        
        # Get actual client count from investments
        client_ids = set()
        investments = await db.investments.find({"referral_salesperson_id": sp_id}).to_list(None)
        for inv in investments:
            client_id = inv.get("client_id")
            if client_id:
                client_ids.add(str(client_id))
        sp["actual_client_count"] = len(client_ids)
        
        # Get pending commissions
        pending = await db.referral_commissions.aggregate([
            {
                "$match": {
                    "salesperson_id": sp_id,
                    "status": {"$in": ["pending", "ready_to_pay", "approved"]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$commission_amount"}
                }
            }
        ]).to_list(1)
        
        if pending and pending[0].get("total"):
            pending_total = pending[0]["total"]
            if isinstance(pending_total, Decimal128):
                sp["actual_pending"] = float(pending_total.to_decimal())
            else:
                sp["actual_pending"] = float(pending_total)
        else:
            sp["actual_pending"] = 0
    
    return {"salespeople": [transform_salesperson(sp) for sp in salespeople]}

@router.post("/admin/referrals/salespeople")
async def create_salesperson(data: SalespersonCreate):
    """Create new salesperson with unique referral code"""
    # Generate unique referral code
    initials = ''.join([n[0].upper() for n in data.name.split()])
    year = datetime.now().year
    referral_code = f"{initials}-{year}"
    
    # Check if code exists, append number if needed
    existing = await db.salespeople.find_one({"referral_code": referral_code})
    if existing:
        counter = 1
        while await db.salespeople.find_one({"referral_code": f"{referral_code}-{counter}"}):
            counter += 1
        referral_code = f"{referral_code}-{counter}"
    
    salesperson = {
        "name": data.name,
        "email": data.email,
        "phone": data.phone,
        "referral_code": referral_code,
        "referral_link": f"https://fidus-investment-platform.onrender.com/prospects?ref={referral_code}",
        "total_clients_referred": 0,
        "total_sales_volume": 0,
        "active_clients": 0,
        "active_investments": 0,
        "total_commissions_earned": 0,
        "commissions_paid_to_date": 0,
        "commissions_pending": 0,
        "preferred_payment_method": "crypto_wallet",
        "wallet_details": data.wallet_details or {},
        "active": True,
        "joined_date": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "notes": data.notes
    }
    
    result = await db.salespeople.insert_one(salesperson)
    
    return {
        "success": True,
        "salesperson_id": str(result.inserted_id),
        "referral_code": referral_code,
        "referral_link": salesperson["referral_link"]
    }

@router.get("/admin/referrals/salespeople/{salesperson_id}")
async def get_salesperson_dashboard(salesperson_id: str):
    """Get complete salesperson dashboard with details"""
    try:
        # Try to find salesperson by either salesperson_id field or MongoDB _id
        salesperson = None
        
        # First try by salesperson_id field (e.g., "sp_123")
        salesperson = await db.salespeople.find_one({"salesperson_id": salesperson_id})
        
        # If not found and it looks like an ObjectId, try by _id
        if not salesperson:
            try:
                salesperson_id_obj = ObjectId(salesperson_id)
                salesperson = await db.salespeople.find_one({"_id": salesperson_id_obj})
            except:
                pass
                
        if not salesperson:
            raise HTTPException(status_code=404, detail="Salesperson not found")
        
        # Use the salesperson_id field for queries, or fall back to _id
        query_id = salesperson.get('salesperson_id') or str(salesperson['_id'])
        
        # Get all clients referred (using referral_salesperson_id on investments)
        client_ids = set()
        investments = await db.investments.find({"referral_salesperson_id": query_id}).to_list(None)
        for inv in investments:
            client_id = inv.get('client_id')
            if client_id:
                client_ids.add(str(client_id))
        
        # Get client details
        clients = []
        for client_id in client_ids:
            try:
                client = await db.clients.find_one({"_id": ObjectId(client_id)})
                if client:
                    clients.append(client)
            except:
                pass
        
        # Get all commissions for this salesperson
        all_commissions = await db.referral_commissions.find(
            {"salesperson_id": query_id}
        ).sort("payment_date", 1).to_list(None)
        
        # Calculate upcoming commissions (next 90 days)
        today = datetime.now(timezone.utc).replace(tzinfo=None)  # Make naive for comparison
        ninety_days = today + timedelta(days=90)
        upcoming = []
        for c in all_commissions:
            if c.get("status") in ["pending", "ready_to_pay"]:
                pay_date = c.get("payment_date")
                if pay_date:
                    # Make sure payment_date is naive for comparison
                    if hasattr(pay_date, 'tzinfo') and pay_date.tzinfo:
                        pay_date = pay_date.replace(tzinfo=None)
                    if today <= pay_date <= ninety_days:
                        upcoming.append(c)
        
        # Group by status
        by_status = {
            "pending": [c for c in all_commissions if c.get("status") == "pending"],
            "ready_to_pay": [c for c in all_commissions if c.get("status") == "ready_to_pay"],
            "approved": [c for c in all_commissions if c.get("status") == "approved"],
            "paid": [c for c in all_commissions if c.get("status") == "paid"],
            "cancelled": [c for c in all_commissions if c.get("status") == "cancelled"]
        }
        
        # Calculate summary statistics
        from bson import Decimal128
        
        def get_amount(item, field="principal_amount"):
            val = item.get(field)
            if isinstance(val, Decimal128):
                return float(val.to_decimal())
            return float(val) if val else 0
        
        total_sales = sum(get_amount(inv, "amount") or get_amount(inv, "principal_amount") for inv in investments)
        total_commissions = sum(get_amount(c, "commission_amount") for c in all_commissions)
        commissions_paid = sum(get_amount(c, "commission_amount") for c in by_status["paid"])
        commissions_pending = sum(
            get_amount(c, "commission_amount") 
            for c in by_status["pending"] + by_status["ready_to_pay"] + by_status["approved"]
        )
        
        # Calculate total commissions per client
        client_commissions = {}
        for c in all_commissions:
            client_id_str = str(c.get("client_id"))
            if client_id_str not in client_commissions:
                client_commissions[client_id_str] = 0
            client_commissions[client_id_str] += get_amount(c, "commission_amount")
        
        return {
            "salespersonId": query_id,
            "name": salesperson.get("name"),
            "email": salesperson.get("email"),
            "phone": salesperson.get("phone"),
            "referralCode": salesperson.get("referral_code"),
            "referralLink": salesperson.get("referral_link"),
            "totalSalesVolume": total_sales,
            "totalCommissions": total_commissions,
            "pendingCommissions": commissions_pending,
            "paidCommissions": commissions_paid,
            "clients": [
                {
                    "clientId": str(c.get("_id")),
                    "name": c.get("name", "Unknown"),
                    "email": c.get("email", ""),
                    "totalCommissionsGenerated": client_commissions.get(str(c.get("_id")), 0)
                }
                for c in clients
            ],
            "investments": [
                {
                    "investmentId": inv.get("investment_id"),
                    "clientId": str(inv.get("client_id")),
                    "fundType": inv.get("fund_type"),
                    "amount": get_amount(inv, "amount") or get_amount(inv, "principal_amount"),
                    "startDate": inv.get("start_date").isoformat() if inv.get("start_date") else None
                }
                for inv in investments
            ],
            "commissions": [
                {
                    "commissionId": c.get("commission_id"),
                    "investmentId": c.get("investment_id"),
                    "fundType": c.get("fund_type"),
                    "commissionAmount": get_amount(c, "commission_amount"),
                    "paymentMonth": c.get("payment_month"),
                    "paymentDate": c.get("payment_date").isoformat() if c.get("payment_date") else None,
                    "status": c.get("status")
                }
                for c in all_commissions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting salesperson dashboard: {str(e)}")

@router.put("/admin/referrals/salespeople/{salesperson_id}")
async def update_salesperson(salesperson_id: str, data: SalespersonUpdate):
    """Update salesperson details"""
    update_data = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.salespeople.update_one(
        {"_id": ObjectId(salesperson_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Salesperson not found")
    
    return {"success": True, "modified": result.modified_count > 0}

# ============================================================================
# COMMISSION MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/admin/referrals/commissions/generate/{investment_id}")
async def generate_commission_schedule(investment_id: str):
    """Generate full commission schedule for an investment"""
    COMMISSION_RATE = 0.10
    
    investment = await db.investments.find_one({"_id": ObjectId(investment_id)})
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    if not investment.get("referred_by"):
        raise HTTPException(status_code=400, detail="Investment has no referral")
    
    # Get salesperson
    salesperson = await db.salespeople.find_one({"_id": investment["referred_by"]})
    if not salesperson:
        raise HTTPException(status_code=404, detail="Salesperson not found")
    
    # Get client
    client = await db.clients.find_one({"_id": investment["client_id"]})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Generate payment schedule
    payment_schedule = await generate_payment_schedule_for_investment(investment)
    
    commissions = []
    total_commissions = 0
    
    for payment in payment_schedule:
        if payment.get("interest_amount", 0) > 0:
            commission_amount = float(payment["interest_amount"]) * COMMISSION_RATE
            
            commission = {
                "salesperson_id": investment["referred_by"],
                "salesperson_name": salesperson["name"],
                "client_id": investment["client_id"],
                "client_name": client.get("name", "Unknown"),
                "investment_id": investment["_id"],
                "product_type": investment.get("product", ""),
                
                "commission_rate": COMMISSION_RATE,
                "client_interest_amount": payment["interest_amount"],
                "commission_amount": commission_amount,
                
                "payment_number": payment["payment_number"],
                "client_payment_date": payment["date"],
                "commission_due_date": payment["date"],
                
                "status": "pending",
                "included_in_cash_flow": True,
                "cash_flow_month": payment["date"].strftime("%Y-%m"),
                
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            commissions.append(commission)
            total_commissions += commission_amount
    
    # Insert commission records
    if commissions:
        await db.referral_commissions.insert_many(commissions)
        
        # Update investment
        await db.investments.update_one(
            {"_id": investment["_id"]},
            {
                "$set": {
                    "total_commissions_due": total_commissions,
                    "commissions_paid_to_date": 0,
                    "commissions_pending": total_commissions,
                    "next_commission_date": commissions[0]["commission_due_date"],
                    "next_commission_amount": commissions[0]["commission_amount"]
                }
            }
        )
        
        # Update salesperson metrics
        await update_salesperson_metrics(str(investment["referred_by"]))
    
    return {
        "success": True,
        "commissions_created": len(commissions),
        "total_amount": total_commissions,
        "first_payment_date": commissions[0]["commission_due_date"].isoformat() if commissions else None
    }

@router.get("/admin/referrals/commissions/calendar")
async def get_commission_calendar(
    start_date: str,
    end_date: str,
    salesperson_id: Optional[str] = None
):
    """Get commission calendar for date range"""
    query = {
        "commission_due_date": {
            "$gte": datetime.fromisoformat(start_date),
            "$lte": datetime.fromisoformat(end_date)
        }
    }
    
    if salesperson_id:
        query["salesperson_id"] = ObjectId(salesperson_id)
    
    commissions = await db.referral_commissions.find(query).sort("commission_due_date", 1).to_list(None)
    
    # Group by month
    monthly_calendar = {}
    for commission in commissions:
        due_date = commission.get("commission_due_date")
        month_key = due_date.strftime("%Y-%m")
        
        if month_key not in monthly_calendar:
            monthly_calendar[month_key] = {
                "month": month_key,
                "month_display": due_date.strftime("%B %Y"),
                "total_commissions": 0,
                "payments": []
            }
        
        monthly_calendar[month_key]["total_commissions"] += float(commission.get("commission_amount", 0))
        monthly_calendar[month_key]["payments"].append({
            "id": str(commission["_id"]),
            "date": due_date.isoformat(),
            "salesperson_name": commission.get("salesperson_name", ""),
            "client_name": commission.get("client_name", ""),
            "product": commission.get("product_type", ""),
            "amount": float(commission.get("commission_amount", 0)),
            "status": commission.get("status", ""),
            "payment_number": commission.get("payment_number", 0)
        })
    
    return {"calendar": sorted(monthly_calendar.values(), key=lambda x: x["month"])}

@router.get("/admin/referrals/commissions/pending")
async def get_pending_commissions(
    salesperson_id: Optional[str] = None,
    status_filter: str = "all",
    overdue: bool = False
):
    """Get all pending/ready/approved commissions"""
    query = {}
    
    if status_filter == "all":
        query["status"] = {"$in": ["pending", "ready_to_pay", "approved"]}
    else:
        query["status"] = status_filter
    
    if salesperson_id:
        query["salesperson_id"] = ObjectId(salesperson_id)
    
    if overdue:
        query["commission_due_date"] = {"$lt": datetime.now(timezone.utc)}
    
    commissions = await db.referral_commissions.find(query).sort("commission_due_date", 1).to_list(None)
    
    # Group by salesperson
    by_salesperson = {}
    total_amount = 0
    
    for commission in commissions:
        sp_id = str(commission.get("salesperson_id"))
        if sp_id not in by_salesperson:
            by_salesperson[sp_id] = {
                "salesperson_id": sp_id,
                "salesperson_name": commission.get("salesperson_name", ""),
                "total_pending": 0,
                "count": 0,
                "commissions": []
            }
        
        amount = float(commission.get("commission_amount", 0))
        by_salesperson[sp_id]["total_pending"] += amount
        by_salesperson[sp_id]["count"] += 1
        by_salesperson[sp_id]["commissions"].append({
            "id": str(commission["_id"]),
            "date": commission.get("commission_due_date").isoformat(),
            "client_name": commission.get("client_name", ""),
            "product": commission.get("product_type", ""),
            "amount": amount,
            "status": commission.get("status", ""),
            "payment_number": commission.get("payment_number", 0)
        })
        total_amount += amount
    
    return {
        "by_salesperson": list(by_salesperson.values()),
        "total_amount": total_amount,
        "total_count": len(commissions)
    }

@router.post("/admin/referrals/commissions/{commission_id}/approve")
async def approve_commission_payment(commission_id: str):
    """Admin approves commission for payment"""
    commission = await db.referral_commissions.find_one({"_id": ObjectId(commission_id)})
    
    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")
    
    if commission.get("status") not in ["ready_to_pay", "pending"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve commission with status: {commission.get('status')}"
        )
    
    await db.referral_commissions.update_one(
        {"_id": ObjectId(commission_id)},
        {
            "$set": {
                "status": "approved",
                "approved_date": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {"success": True, "message": "Commission approved for payment"}

@router.post("/admin/referrals/commissions/{commission_id}/mark-paid")
async def mark_commission_paid(commission_id: str, payment_details: CommissionPaymentDetails):
    """Admin marks commission as paid after executing payment"""
    commission = await db.referral_commissions.find_one({"_id": ObjectId(commission_id)})
    
    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")
    
    if commission.get("status") != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Commission must be approved before marking as paid. Current status: {commission.get('status')}"
        )
    
    # Update commission record
    await db.referral_commissions.update_one(
        {"_id": ObjectId(commission_id)},
        {
            "$set": {
                "status": "paid",
                "paid_date": datetime.now(timezone.utc),
                "payment_method": payment_details.method,
                "payment_reference": payment_details.reference,
                "payment_hash": payment_details.hash,
                "notes": payment_details.notes,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Update investment
    commission_amount = float(commission.get("commission_amount", 0))
    await db.investments.update_one(
        {"_id": commission.get("investment_id")},
        {
            "$inc": {"commissions_paid_to_date": commission_amount},
            "$set": {"commissions_pending": {"$max": [{"$subtract": ["$commissions_pending", commission_amount]}, 0]}}
        }
    )
    
    # Update salesperson metrics
    await update_salesperson_metrics(str(commission.get("salesperson_id")))
    
    # Update client
    await db.clients.update_one(
        {"_id": commission.get("client_id")},
        {"$inc": {"commissions_paid_to_date": commission_amount}}
    )
    
    return {"success": True, "message": "Commission marked as paid"}

# ============================================================================
# CLIENT REFERRAL MANAGEMENT
# ============================================================================

@router.put("/admin/referrals/clients/{client_id}/referral")
async def update_client_referral(client_id: str, salesperson_id: str):
    """Assign or update client referral"""
    client = await db.clients.find_one({"_id": ObjectId(client_id)})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    salesperson = await db.salespeople.find_one({"_id": ObjectId(salesperson_id)})
    if not salesperson:
        raise HTTPException(status_code=404, detail="Salesperson not found")
    
    # Update client record
    await db.clients.update_one(
        {"_id": ObjectId(client_id)},
        {
            "$set": {
                "referred_by": ObjectId(salesperson_id),
                "referred_by_name": salesperson["name"],
                "referral_date": datetime.now(timezone.utc),
                "referral_code": salesperson.get("referral_code", ""),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Update all investments
    await db.investments.update_many(
        {"client_id": ObjectId(client_id)},
        {
            "$set": {
                "referred_by": ObjectId(salesperson_id),
                "referred_by_name": salesperson["name"]
            }
        }
    )
    
    # Generate commission schedules for active investments
    investments = await db.investments.find({
        "client_id": ObjectId(client_id),
        "status": {"$in": ["incubation", "active"]}
    }).to_list(None)
    
    for investment in investments:
        # Delete existing commissions
        await db.referral_commissions.delete_many({"investment_id": investment["_id"]})
        
        # Generate new schedule
        await generate_commission_schedule(str(investment["_id"]))
    
    # Update salesperson metrics
    await update_salesperson_metrics(salesperson_id)
    
    return {
        "success": True,
        "message": f"Client assigned to {salesperson['name']}",
        "investments_updated": len(investments)
    }

# ============================================================================
# PUBLIC ENDPOINTS (for Prospects Portal)
# ============================================================================

@router.get("/public/salespeople", tags=["Public"])
async def get_active_salespeople_public():
    """Get active salespeople for prospect forms (no auth required)"""
    salespeople = await db.salespeople.find(
        {"active": True},
        {"_id": 1, "name": 1, "referral_code": 1}
    ).sort("name", 1).to_list(None)
    
    return {
        "salespeople": [
            {
                "id": str(sp["_id"]),
                "name": sp["name"],
                "referral_code": sp.get("referral_code", "")
            }
            for sp in salespeople
        ]
    }

@router.get("/public/salespeople/{referral_code}", tags=["Public"])
async def get_salesperson_by_code_public(referral_code: str):
    """
    Public endpoint to validate referral code and get salesperson info.
    No authentication required - used by prospects form.
    """
    salesperson = await db.salespeople.find_one(
        {"referral_code": referral_code.upper(), "active": True}
    )
    
    if not salesperson:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    
    # Helper to convert Decimal128 to float
    def to_float(val):
        if val is None:
            return 0.0
        if hasattr(val, 'to_decimal'):
            return float(val.to_decimal())
        return float(val)
    
    # Return public-safe data (no sensitive info like wallet details)
    return {
        "id": str(salesperson["_id"]),
        "name": salesperson["name"],
        "email": salesperson.get("email"),
        "phone": salesperson.get("phone"),
        "referral_code": salesperson["referral_code"],
        "active": salesperson.get("active", True),
        # Public stats for transparency
        "total_clients_referred": salesperson.get("total_clients_referred", 0),
        "total_sales_volume": to_float(salesperson.get("total_sales_volume", 0))
    }


# ============================================================================
# DATA FIX ENDPOINTS (One-time use)
# ============================================================================

@router.post("/public/fix-salvador-data-temp", tags=["Public"])
async def fix_salvador_data():
    """
    One-time fix to update Salvador Palma's statistics
    Links ALL of Alejandro's investments and recalculates totals
    """
    try:
        from bson.decimal128 import Decimal128
        
        print("🔧 Starting Salvador data fix...")
        
        # Find Salvador Palma
        salvador = await db.salespeople.find_one({"referral_code": "SP-2025"})
        if not salvador:
            raise HTTPException(404, "Salvador Palma not found")
        
        salvador_id = salvador["_id"]
        print(f"✅ Found Salvador: {salvador_id}")
        
        # Find Alejandro
        alejandro = await db.clients.find_one({"name": {"$regex": "Alejandro", "$options": "i"}})
        if not alejandro:
            raise HTTPException(404, "Alejandro not found")
        
        alejandro_id = str(alejandro["_id"])
        print(f"✅ Found Alejandro: {alejandro_id}")
        
        # Find ALL of Alejandro's investments
        investments = await db.investments.find({"client_id": alejandro_id}).to_list(None)
        print(f"📊 Found {len(investments)} investments")
        
        total_sales = 0
        investment_details = []
        
        # Update each investment to link to Salvador
        for inv in investments:
            # Handle Decimal128
            amount_raw = inv.get("amount", 0)
            if hasattr(amount_raw, 'to_decimal'):
                amount = float(amount_raw.to_decimal())
            else:
                amount = float(amount_raw)
            total_sales += amount
            fund = inv.get("fund_type", "unknown")
            
            investment_details.append({
                "fund": fund,
                "amount": amount
            })
            
            # Link to Salvador if not already
            if inv.get("referred_by") != salvador_id:
                await db.investments.update_one(
                    {"_id": inv["_id"]},
                    {
                        "$set": {
                            "referred_by": salvador_id,
                            "referred_by_name": "Salvador Palma",
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                print(f"  ✅ Linked {fund} (${amount:,.2f}) to Salvador")
        
        print(f"💰 Total Sales Volume: ${total_sales:,.2f}")
        
        # Find all commissions for Salvador
        commissions = await db.referral_commissions.find({
            "salesperson_id": str(salvador_id)
        }).to_list(None)
        
        print(f"💵 Found {len(commissions)} commission records")
        
        total_commissions = 0
        commissions_paid = 0
        commissions_pending = 0
        
        for comm in commissions:
            # Handle Decimal128
            amount_raw = comm.get("amount", 0)
            if hasattr(amount_raw, 'to_decimal'):
                amount = float(amount_raw.to_decimal())
            else:
                amount = float(amount_raw)
            total_commissions += amount
            
            if comm.get("status") == "paid":
                commissions_paid += amount
            else:
                commissions_pending += amount
        
        print(f"💰 Total Commissions: ${total_commissions:,.2f}")
        print(f"   Paid: ${commissions_paid:,.2f}")
        print(f"   Pending: ${commissions_pending:,.2f}")
        
        # Update Salvador's statistics
        update_data = {
            "total_sales_volume": Decimal128(str(total_sales)),
            "total_commissions_earned": Decimal128(str(total_commissions)),
            "commissions_paid_to_date": Decimal128(str(commissions_paid)),
            "commissions_pending": Decimal128(str(commissions_pending)),
            "active_investments": len(investments),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.salespeople.update_one(
            {"_id": salvador_id},
            {"$set": update_data}
        )
        
        print("✅ Updated Salvador's statistics")
        
        # Verify update
        updated_salvador = await db.salespeople.find_one({"_id": salvador_id})
        
        # Convert Decimal128 for verification
        def to_float(val):
            if hasattr(val, 'to_decimal'):
                return float(val.to_decimal())
            return float(val or 0)
        
        return {
            "success": True,
            "message": "Salvador's data updated successfully",
            "data": {
                "salesperson_id": str(salvador_id),
                "salesperson_name": "Salvador Palma",
                "investments_found": len(investments),
                "investments_linked": len(investments),
                "total_sales_volume": total_sales,
                "commission_records": len(commissions),
                "total_commissions_earned": total_commissions,
                "commissions_paid": commissions_paid,
                "commissions_pending": commissions_pending,
                "verification": {
                    "sales_in_db": to_float(updated_salvador.get("total_sales_volume", 0)),
                    "commissions_in_db": to_float(updated_salvador.get("total_commissions_earned", 0))
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Fix failed: {str(e)}")


# ============================================================================
# REFERRAL AGENT PORTAL AUTHENTICATION
# ============================================================================

class AgentLoginRequest(BaseModel):
    """Login request for referral agents"""
    email: str
    password: str

class AgentLoginResponse(BaseModel):
    """Login response with JWT token and agent info"""
    success: bool
    access_token: str
    token_type: str
    expires_in: int
    agent: dict

@router.post("/referral-agent/auth/login", tags=["Agent Portal"])
async def agent_portal_login(login_request: AgentLoginRequest):
    """
    Login endpoint for referral agents - Phase 2 with JWT tokens
    
    Verifies email and password, returns JWT token for authenticated sessions
    
    Returns:
        {
            "success": true,
            "access_token": "jwt_token_here",
            "token_type": "bearer",
            "expires_in": 86400,
            "agent": {...}
        }
    """
    try:
        # Find salesperson by email (case-insensitive using regex)
        salesperson = await db.salespeople.find_one({
            "email": {"$regex": f"^{login_request.email}$", "$options": "i"}
        })
        
        if not salesperson:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Check if account is active
        if salesperson.get("status") != "active" and salesperson.get("active") != True:
            raise HTTPException(
                status_code=403,
                detail="Account is inactive. Contact administrator."
            )
        
        # Verify password exists
        password_hash = salesperson.get("password_hash")
        if not password_hash:
            raise HTTPException(
                status_code=400,
                detail="Password not set. Please contact administrator."
            )
        
        # Verify password
        if not verify_password(login_request.password, password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Create JWT access token
        access_token = create_access_token(
            data={"sub": str(salesperson["_id"])},
            expires_delta=timedelta(hours=24)
        )
        
        # Update login stats
        await db.salespeople.update_one(
            {"_id": salesperson["_id"]},
            {
                "$set": {
                    "last_login": datetime.now(timezone.utc)
                },
                "$inc": {
                    "login_count": 1
                }
            }
        )
        
        # Create session record
        session_record = {
            "salesperson_id": salesperson["_id"],
            "salesperson_name": salesperson.get("name"),
            "session_token": access_token,
            "login_time": datetime.now(timezone.utc),
            "logout_time": None,
            "last_activity": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=24),
            "pages_viewed": [],
            "actions_performed": []
        }
        
        await db.referral_agent_sessions.insert_one(session_record)
        
        # Return success with JWT token
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400,  # 24 hours in seconds
            "agent": {
                "id": str(salesperson["_id"]),
                "name": salesperson.get("name"),
                "email": salesperson.get("email"),
                "referralCode": salesperson.get("referral_code"),
                "referralLink": salesperson.get("referral_link"),
                "stats": salesperson.get("stats", {})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Login error: {str(e)}"
        )


@router.post("/referral-agent/auth/logout", tags=["Agent Portal"])
async def agent_portal_logout(current_agent: dict = Depends(get_current_agent)):
    """
    Logout endpoint - marks current session as ended
    
    Requires: Valid JWT token in Authorization header
    """
    try:
        # Mark all active sessions for this agent as logged out
        await db.referral_agent_sessions.update_many(
            {
                "salesperson_id": current_agent["_id"],
                "logout_time": None
            },
            {
                "$set": {
                    "logout_time": datetime.now(timezone.utc)
                }
            }
        )
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        print(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Logout failed. Please try again."
        )


@router.get("/referral-agent/auth/me", tags=["Agent Portal"])
async def get_current_agent_info(current_agent: dict = Depends(get_current_agent)):
    """
    Get current authenticated agent information
    
    Requires: Valid JWT token in Authorization header
    
    Returns agent profile data without sensitive fields
    """
    try:
        return {
            "id": str(current_agent["_id"]),
            "name": current_agent.get("name"),
            "email": current_agent.get("email"),
            "referralCode": current_agent.get("referral_code"),
            "referralLink": current_agent.get("referral_link"),
            "portalSettings": current_agent.get("portal_settings", {}),
            "leadPipelineStages": current_agent.get("lead_pipeline_stages", []),
            "stats": current_agent.get("stats", {}),
            "lastLogin": current_agent.get("last_login").isoformat() if current_agent.get("last_login") else None,
            "loginCount": current_agent.get("login_count", 0)
        }
        
    except Exception as e:
        print(f"Get current agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve agent information"
        )


@router.put("/referral-agent/auth/change-password", tags=["Agent Portal"])
async def change_password_endpoint(
    current_password: str,
    new_password: str,
    current_agent: dict = Depends(get_current_agent)
):
    """
    Change password for current authenticated agent
    
    Requires: Valid JWT token in Authorization header
    
    Args:
        current_password: Current password for verification
        new_password: New password (min 8 characters)
    """
    try:
        # Validate new password strength
        if len(new_password) < 8:
            raise HTTPException(
                status_code=400,
                detail="New password must be at least 8 characters"
            )
        
        # Verify current password
        current_hash = current_agent.get("password_hash")
        if not current_hash or not verify_password(current_password, current_hash):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_password_hash = get_password_hash(new_password)
        
        # Update password
        await db.salespeople.update_one(
            {"_id": current_agent["_id"]},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "password_reset_token": None,
                    "password_reset_expires": None
                }
            }
        )
        
        # Invalidate all existing sessions (force re-login)
        await db.referral_agent_sessions.update_many(
            {
                "salesperson_id": current_agent["_id"],
                "logout_time": None
            },
            {
                "$set": {
                    "logout_time": datetime.now(timezone.utc)
                }
            }
        )
        
        return {
            "success": True,
            "message": "Password changed successfully. Please login again with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Change password error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to change password"
        )


@router.post("/referral-agent/auth/password-reset", tags=["Agent Portal"])
async def request_password_reset_endpoint(email: str):
    """
    Request password reset - generates reset token
    
    Does not reveal if email exists (security best practice)
    """
    try:
        # Find salesperson (case-insensitive)
        salesperson = await db.salespeople.find_one({
            "email": {"$regex": f"^{email}$", "$options": "i"}
        })
        
        if not salesperson:
            # Don't reveal if email doesn't exist
            return {
                "success": True,
                "message": "If the email address exists in our system, a password reset link has been sent."
            }
        
        # Generate secure reset token (URL-safe)
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Save token to database
        await db.salespeople.update_one(
            {"_id": salesperson["_id"]},
            {
                "$set": {
                    "password_reset_token": reset_token,
                    "password_reset_expires": reset_expires
                }
            }
        )
        
        # TODO: Send email with reset link
        # For now, just log the token (REMOVE THIS IN PRODUCTION)
        print(f"Password reset token for {email}: {reset_token}")
        print(f"Reset link: https://fidus-investment-platform.onrender.com/referral-agent/reset-password?token={reset_token}")
        
        return {
            "success": True,
            "message": "If the email address exists in our system, a password reset link has been sent."
        }
        
    except Exception as e:
        print(f"Password reset request error: {str(e)}")
        # Still return success (don't reveal if email exists)
        return {
            "success": True,
            "message": "If the email address exists in our system, a password reset link has been sent."
        }


@router.post("/referral-agent/auth/password-reset/confirm", tags=["Agent Portal"])
async def confirm_password_reset_endpoint(token: str, new_password: str):
    """
    Confirm password reset with token
    
    Args:
        token: Reset token from email link
        new_password: New password (min 8 characters)
    """
    try:
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters"
            )
        
        # Find salesperson by reset token
        salesperson = await db.salespeople.find_one({
            "password_reset_token": token,
            "password_reset_expires": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not salesperson:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset token. Please request a new password reset."
            )
        
        # Hash new password
        new_password_hash = get_password_hash(new_password)
        
        # Update password and clear reset token
        await db.salespeople.update_one(
            {"_id": salesperson["_id"]},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "password_reset_token": None,
                    "password_reset_expires": None
                }
            }
        )
        
        # Invalidate all existing sessions
        await db.referral_agent_sessions.update_many(
            {
                "salesperson_id": salesperson["_id"],
                "logout_time": None
            },
            {
                "$set": {
                    "logout_time": datetime.now(timezone.utc)
                }
            }
        )
        
        return {
            "success": True,
            "message": "Password reset successfully. You can now login with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Password reset confirm error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Password reset failed. Please try again."
        )


@router.get("/referral-agent/auth/verify", tags=["Agent Portal"])
async def verify_agent_email(email: str):
    """
    Verify if an email exists in the system (for password reset flow)
    
    Returns generic message to prevent email enumeration
    """
    try:
        salesperson = await db.salespeople.find_one({
            "email": email.lower()
        })
        
        # Always return success to prevent email enumeration
        return {
            "success": True,
            "message": "If the email exists in our system, you will receive password reset instructions"
        }
        
    except Exception as e:
        return {
            "success": True,
            "message": "If the email exists in our system, you will receive password reset instructions"
        }


# ==========================================
# REFERRAL AGENT CRM ENDPOINTS
# ==========================================

@router.get("/referral-agent/crm/dashboard", tags=["Agent CRM"])
async def get_agent_dashboard(current_agent: dict = Depends(get_current_agent)):
    """
    Get dashboard statistics and overview for the logged-in agent
    """
    try:
        salesperson_id = current_agent["_id"]
        
        # Get all leads for this agent
        # Note: referred_by can be either referral_code (string) OR salesperson ObjectId
        leads = await db.leads.find({
            "$or": [
                {"referred_by": current_agent.get("referral_code")},
                {"referred_by": str(salesperson_id)},
                {"referred_by": salesperson_id}
            ]
        }, {"_id": 0}).to_list(1000)
        
        # Get all clients (converted leads)
        # Note: referred_by contains salesperson ObjectId (not referral_code)
        clients = await db.clients.find({
            "$or": [
                {"referred_by": str(salesperson_id)},
                {"referred_by": salesperson_id},
                {"referred_by": current_agent.get("referral_code")}
            ]
        }, {"_id": 0}).to_list(1000)
        
        # Get commission data - check multiple formats including sp_ prefix
        commissions = await db.referral_commissions.find({
            "$or": [
                {"salesperson_id": f"sp_{salesperson_id}"},
                {"salesperson_id": str(salesperson_id)},
                {"salesperson_id": salesperson_id}
            ]
        }).to_list(1000)
        
        # Calculate stats
        total_leads = len(leads)
        active_clients = len(clients)
        # Handle Decimal128 for commission amounts
        total_commissions_earned = sum(
            float(c.get("commission_amount").to_decimal()) if hasattr(c.get("commission_amount"), 'to_decimal') 
            else float(c.get("commission_amount", 0)) 
            for c in commissions
        )
        conversion_rate = round((active_clients / total_leads * 100) if total_leads > 0 else 0, 1)
        
        # Pipeline breakdown
        pipeline_breakdown = {}
        for lead in leads:
            status = lead.get("crm_status", "pending")
            pipeline_breakdown[status] = pipeline_breakdown.get(status, 0) + 1
        
        # Recent leads (last 5)
        recent_leads = sorted(
            leads,
            key=lambda x: x.get("registration_date", ""),
            reverse=True
        )[:5]
        
        # Upcoming follow-ups
        upcoming_follow_ups = [
            lead for lead in leads 
            if lead.get("next_follow_up") and lead.get("crm_status") not in ["converted", "lost"]
        ]
        upcoming_follow_ups = sorted(
            upcoming_follow_ups,
            key=lambda x: x.get("next_follow_up", "")
        )[:5]
        
        return {
            "success": True,
            "data": {
                "stats": {
                    "totalLeads": total_leads,
                    "activeClients": active_clients,
                    "totalCommissionsEarned": total_commissions_earned,
                    "conversionRate": conversion_rate
                },
                "pipelineBreakdown": pipeline_breakdown,
                "recentLeads": recent_leads,
                "upcomingFollowUps": upcoming_follow_ups
            }
        }
        
    except Exception as e:
        logging.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")


@router.get("/referral-agent/crm/leads", tags=["Agent CRM"])
async def get_agent_leads(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    current_agent: dict = Depends(get_current_agent)
):
    """
    Get all leads for the logged-in agent with optional filters
    """
    try:
        # Build query
        salesperson_id = current_agent["_id"]
        base_query = {
            "$or": [
                {"referred_by": current_agent.get("referral_code")},
                {"referred_by": str(salesperson_id)},
                {"referred_by": salesperson_id}
            ]
        }
        
        # Add additional filters
        query_parts = [base_query]
        if status:
            query_parts.append({"crm_status": status})
        if priority:
            query_parts.append({"priority": priority})
        if search:
            query_parts.append({
                "$or": [
                    {"email": {"$regex": search, "$options": "i"}},
                    {"name": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}}
                ]
            })
        
        query = {"$and": query_parts} if len(query_parts) > 1 else base_query
        leads = await db.leads.find(query, {"_id": 0}).to_list(1000)
        
        return {
            "success": True,
            "leads": leads
        }
        
    except Exception as e:
        logging.error(f"Get leads error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load leads")


@router.get("/referral-agent/crm/leads/{lead_id}", tags=["Agent CRM"])
async def get_lead_detail(
    lead_id: str,
    current_agent: dict = Depends(get_current_agent)
):
    """
    Get detailed information for a specific lead
    """
    try:
        salesperson_id = current_agent["_id"]
        lead = await db.leads.find_one({
            "id": lead_id,
            "$or": [
                {"referred_by": current_agent.get("referral_code")},
                {"referred_by": str(salesperson_id)},
                {"referred_by": salesperson_id}
            ]
        }, {"_id": 0})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "success": True,
            "lead": lead
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get lead detail error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load lead details")


@router.post("/referral-agent/crm/leads/{lead_id}/notes", tags=["Agent CRM"])
async def add_lead_note(
    lead_id: str,
    note_data: dict,
    current_agent: dict = Depends(get_current_agent)
):
    """
    Add a note to a lead
    """
    try:
        # Verify lead belongs to agent
        salesperson_id = current_agent["_id"]
        lead = await db.leads.find_one({
            "id": lead_id,
            "$or": [
                {"referred_by": current_agent.get("referral_code")},
                {"referred_by": str(salesperson_id)},
                {"referred_by": salesperson_id}
            ]
        })
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Create note
        note = {
            "note_text": note_data.get("note_text"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "added_by": current_agent.get("email")
        }
        
        # Update lead
        await db.leads.update_one(
            {"id": lead_id},
            {
                "$push": {"agent_notes": note},
                "$set": {"last_contacted": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return {
            "success": True,
            "message": "Note added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Add note error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add note")


@router.put("/referral-agent/crm/leads/{lead_id}/status", tags=["Agent CRM"])
async def update_lead_status(
    lead_id: str,
    status_data: dict,
    current_agent: dict = Depends(get_current_agent)
):
    """
    Update the status of a lead
    """
    try:
        # Verify lead belongs to agent
        salesperson_id = current_agent["_id"]
        lead = await db.leads.find_one({
            "id": lead_id,
            "$or": [
                {"referred_by": current_agent.get("referral_code")},
                {"referred_by": str(salesperson_id)},
                {"referred_by": salesperson_id}
            ]
        })
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        new_status = status_data.get("status")
        next_follow_up = status_data.get("next_follow_up")
        
        # Create status history entry
        status_history_entry = {
            "status": new_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "updated_by": current_agent.get("email")
        }
        
        # Update document
        update_doc = {
            "$set": {
                "crm_status": new_status,
                "last_contacted": datetime.now(timezone.utc).isoformat()
            },
            "$push": {"crm_status_history": status_history_entry}
        }
        
        if next_follow_up:
            update_doc["$set"]["next_follow_up"] = next_follow_up
        
        await db.leads.update_one({"id": lead_id}, update_doc)
        
        return {
            "success": True,
            "message": "Status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update status")


@router.get("/referral-agent/crm/clients", tags=["Agent CRM"])
async def get_agent_clients(current_agent: dict = Depends(get_current_agent)):
    """
    Get all clients (converted leads) for the logged-in agent
    """
    try:
        # Get clients referred by this agent
        salesperson_id = current_agent["_id"]
        clients = await db.clients.find({
            "$or": [
                {"referred_by": current_agent.get("referral_code")},
                {"referred_by": str(salesperson_id)},
                {"referred_by": salesperson_id}
            ]
        }).to_list(1000)
        
        # For each client, get their investment data
        client_data = []
        for client in clients:
            # FIX: Use _id from MongoDB, convert to string for user_id matching
            client_id = str(client.get("_id"))
            
            # Get investments - try multiple possible field formats
            investments = await db.investments.find({
                "$or": [
                    {"client_id": client_id},
                    {"user_id": client_id},
                    {"client_id": client.get("_id")}
                ]
            }).to_list(100)
            
            # Calculate totals
            total_investment = sum(float(inv.get("principal_amount", inv.get("amount", 0))) for inv in investments)
            active_investments = len([inv for inv in investments if inv.get("status") == "active"])
            
            client_data.append({
                "clientId": client_id,
                "clientName": client.get("name"),
                "email": client.get("email"),
                "joinDate": client.get("registration_date") or client.get("created_at"),
                "totalInvestment": total_investment,
                "activeInvestments": active_investments,
                "investments": [
                    {
                        "fundCode": inv.get("fund_code") or inv.get("fund_type"),
                        "amount": float(inv.get("principal_amount", inv.get("amount", 0))),
                        "status": inv.get("status")
                    }
                    for inv in investments
                ]
            })
        
        return {
            "success": True,
            "clients": client_data
        }
        
    except Exception as e:
        logging.error(f"Get clients error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load clients")


@router.get("/referral-agent/commissions/schedule", tags=["Agent CRM"])
async def get_commission_schedule(current_agent: dict = Depends(get_current_agent)):
    """
    Get commission schedule and payment history for the logged-in agent
    """
    try:
        salesperson_id = current_agent["_id"]
        
        # Get all commissions - check multiple formats including sp_ prefix
        commissions = await db.referral_commissions.find({
            "$or": [
                {"salesperson_id": f"sp_{salesperson_id}"},
                {"salesperson_id": str(salesperson_id)},
                {"salesperson_id": salesperson_id}
            ]
        }).to_list(1000)
        
        # Get client names
        for commission in commissions:
            client_id = commission.get("client_id")
            if client_id:
                # Try to find client by _id (converted to string)
                client = await db.clients.find_one({
                    "$or": [
                        {"_id": client_id},
                        {"id": client_id}
                    ]
                })
                if client:
                    commission["clientName"] = client.get("name", "Unknown")
        
        return {
            "success": True,
            "commissions": commissions
        }
        
    except Exception as e:
        logging.error(f"Get commissions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load commissions")

