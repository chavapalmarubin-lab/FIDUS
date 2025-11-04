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
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
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

@router.get("/admin/referrals/salespeople")
async def get_all_salespeople(active_only: bool = True):
    """Get all salespeople with performance metrics"""
    query = {}
    if active_only:
        query["active"] = True
    
    salespeople = await db.salespeople.find(query).sort("name", 1).to_list(None)
    
    # Enrich with real-time metrics
    for sp in salespeople:
        # Get actual client count
        client_count = await db.clients.count_documents({"referred_by": sp["_id"]})
        sp["actual_client_count"] = client_count
        
        # Get pending commissions
        pending = await db.referral_commissions.aggregate([
            {
                "$match": {
                    "salesperson_id": sp["_id"],
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
        sp["actual_pending"] = float(pending[0]["total"]) if pending else 0
    
    return {"salespeople": [serialize_doc(sp) for sp in salespeople]}

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
    salesperson = await db.salespeople.find_one({"_id": ObjectId(salesperson_id)})
    if not salesperson:
        raise HTTPException(status_code=404, detail="Salesperson not found")
    
    # Get all clients referred
    clients = await db.clients.find({"referred_by": ObjectId(salesperson_id)}).to_list(None)
    
    # Get all investments
    investments = await db.investments.find({"referred_by": ObjectId(salesperson_id)}).to_list(None)
    
    # Get all commissions
    all_commissions = await db.referral_commissions.find(
        {"salesperson_id": ObjectId(salesperson_id)}
    ).sort("commission_due_date", 1).to_list(None)
    
    # Calculate upcoming commissions (next 90 days)
    today = datetime.now(timezone.utc)
    ninety_days = today + timedelta(days=90)
    upcoming = [
        c for c in all_commissions 
        if c.get("status") in ["pending", "ready_to_pay"] 
        and today <= c.get("commission_due_date", datetime.max) <= ninety_days
    ]
    
    # Group by status
    by_status = {
        "pending": [c for c in all_commissions if c.get("status") == "pending"],
        "ready_to_pay": [c for c in all_commissions if c.get("status") == "ready_to_pay"],
        "approved": [c for c in all_commissions if c.get("status") == "approved"],
        "paid": [c for c in all_commissions if c.get("status") == "paid"],
        "cancelled": [c for c in all_commissions if c.get("status") == "cancelled"]
    }
    
    return {
        "salesperson": serialize_doc(salesperson),
        "clients": [serialize_doc(c) for c in clients],
        "investments": [serialize_doc(inv) for inv in investments],
        "commissions": {
            "all": [serialize_doc(c) for c in all_commissions],
            "upcoming": [serialize_doc(c) for c in upcoming],
            "by_status": {k: [serialize_doc(c) for c in v] for k, v in by_status.items()}
        },
        "summary": {
            "total_clients": len(clients),
            "active_clients": len([c for c in clients if c.get("status") == "active"]),
            "total_investments": len(investments),
            "total_sales_volume": sum(float(inv.get("amount", 0)) for inv in investments),
            "total_commissions_earned": sum(float(c.get("commission_amount", 0)) for c in all_commissions),
            "commissions_paid": sum(float(c.get("commission_amount", 0)) for c in by_status["paid"]),
            "commissions_pending": sum(
                float(c.get("commission_amount", 0)) 
                for c in by_status["pending"] + by_status["ready_to_pay"] + by_status["approved"]
            ),
            "next_payment_date": upcoming[0].get("commission_due_date").isoformat() if upcoming else None,
            "next_payment_amount": float(upcoming[0].get("commission_amount", 0)) if upcoming else 0
        }
    }

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

@router.post("/commissions/{commission_id}/approve")
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

@router.post("/commissions/{commission_id}/mark-paid")
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

@router.put("/clients/{client_id}/referral")
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
    """Get salesperson by referral code (no auth required)"""
    salesperson = await db.salespeople.find_one(
        {"referral_code": referral_code, "active": True}
    )
    
    if not salesperson:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    
    return {
        "id": str(salesperson["_id"]),
        "name": salesperson["name"],
        "referral_code": salesperson["referral_code"]
    }
