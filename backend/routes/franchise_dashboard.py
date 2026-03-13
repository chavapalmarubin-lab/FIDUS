"""
Franchise Admin Dashboard API
March 2026 - FIDUS White Label Franchise System

Multi-tenant dashboard endpoints for franchise company admins.
All endpoints filter data by company_id from JWT token.
"""

from fastapi import APIRouter, HTTPException, Header, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel
import os
import logging
import jwt
import uuid
import hashlib
import csv
import io

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/franchise/dashboard", tags=["Franchise Dashboard"])

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'fidus-franchise-secret-key-2026')
JWT_ALGORITHM = "HS256"


async def get_database():
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        raise HTTPException(status_code=500, detail="Database not configured")
    client = AsyncIOMotorClient(mongo_url)
    return client.fidus_production


def get_company_id_from_token(authorization: str) -> str:
    """Extract company_id from JWT token in Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if payload.get("type") != "franchise_admin":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        company_id = payload.get("company_id")
        if not company_id:
            raise HTTPException(status_code=401, detail="Company ID not in token")
        
        return company_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =============================================================================
# FUND PORTFOLIO (BALANCE ONLY - Multi-tenant)
# =============================================================================

@router.get("/portfolio")
async def get_franchise_portfolio(authorization: str = Header(None)):
    """
    Get fund portfolio for franchise company.
    Shows OMNIBUS account data and client allocations.
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()
        
        # Get company info
        company = await db.franchise_companies.find_one(
            {"company_id": company_id},
            {"_id": 0}
        )
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get total AUM from investments
        pipeline = [
            {"$match": {"company_id": company_id, "status": {"$in": ["incubation", "active"]}}},
            {"$group": {
                "_id": None,
                "total_aum": {"$sum": "$amount"},
                "total_investments": {"$sum": 1}
            }}
        ]
        aum_result = await db.franchise_investments.aggregate(pipeline).to_list(1)
        
        total_aum = aum_result[0]["total_aum"] if aum_result else 0
        total_investments = aum_result[0]["total_investments"] if aum_result else 0
        
        # Calculate obligations (what company owes clients at 2.0%)
        # Monthly obligation = AUM * 2.0% (but paid quarterly)
        monthly_client_return = total_aum * 0.02
        quarterly_client_obligation = monthly_client_return * 3
        
        # Calculate gross return (what FIDUS pays at 2.5%)
        monthly_gross_return = total_aum * 0.025
        quarterly_gross_return = monthly_gross_return * 3
        
        # Commission pool (0.5% difference)
        monthly_commission_pool = total_aum * 0.005
        quarterly_commission_pool = monthly_commission_pool * 3
        
        # Split commission
        split = company.get("commission_split", {"company": 50, "agent": 50})
        company_share = quarterly_commission_pool * (split["company"] / 100)
        agent_share = quarterly_commission_pool * (split["agent"] / 100)
        
        return {
            "success": True,
            "portfolio": {
                "fund_type": "BALANCE",
                "company_name": company.get("company_name"),
                "total_aum": total_aum,
                "total_clients": total_investments,
                "omnibus_account": company.get("omnibus_account"),
                
                # Returns breakdown
                "returns": {
                    "gross_return_pct": 2.5,
                    "client_return_pct": 2.0,
                    "commission_pool_pct": 0.5,
                    
                    "monthly": {
                        "gross_return": monthly_gross_return,
                        "client_obligation": monthly_client_return,
                        "commission_pool": monthly_commission_pool
                    },
                    "quarterly": {
                        "gross_return": quarterly_gross_return,
                        "client_obligation": quarterly_client_obligation,
                        "commission_pool": quarterly_commission_pool,
                        "company_share": company_share,
                        "agent_share": agent_share
                    }
                },
                
                # Commission split
                "commission_split": split,
                
                # Contract terms
                "contract_terms": {
                    "duration_months": 14,
                    "incubation_months": 2,
                    "payment_frequency": "quarterly"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching franchise portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CASH FLOW & PERFORMANCE (Multi-tenant)
# =============================================================================

@router.get("/cashflow")
async def get_franchise_cashflow(authorization: str = Header(None)):
    """
    Get cash flow and performance data for franchise company.
    Based on difference between 2.0% (client) and 2.5% (gross).
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()
        
        # Get company
        company = await db.franchise_companies.find_one({"company_id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get all active investments
        investments = await db.franchise_investments.find(
            {"company_id": company_id, "status": {"$in": ["incubation", "active", "matured"]}},
            {"_id": 0}
        ).to_list(1000)
        
        # Calculate totals
        total_invested = sum(inv.get("amount", 0) for inv in investments)
        total_returns_earned = sum(inv.get("total_returns_earned", 0) for inv in investments)
        total_returns_paid = sum(inv.get("total_returns_paid", 0) for inv in investments)
        total_commission = sum(inv.get("commission_pool", 0) for inv in investments)
        
        # Get quarterly breakdown
        quarterly_data = []
        
        # Commission transactions by period
        commission_pipeline = [
            {"$match": {"company_id": company_id}},
            {"$group": {
                "_id": "$period",
                "total_commission": {"$sum": "$amount"},
                "company_share": {"$sum": {"$cond": [{"$eq": ["$transaction_type", "company_share"]}, "$amount", 0]}},
                "agent_share": {"$sum": {"$cond": [{"$eq": ["$transaction_type", "agent_share"]}, "$amount", 0]}}
            }},
            {"$sort": {"_id": -1}}
        ]
        
        quarters = await db.franchise_commission_transactions.aggregate(commission_pipeline).to_list(8)
        
        return {
            "success": True,
            "cashflow": {
                "summary": {
                    "total_invested": total_invested,
                    "total_returns_earned": total_returns_earned,
                    "total_returns_paid": total_returns_paid,
                    "pending_payments": total_returns_earned - total_returns_paid,
                    "total_commission_earned": total_commission
                },
                
                # Monthly projections based on current AUM
                "monthly_projection": {
                    "gross_return": total_invested * 0.025,
                    "client_payments": total_invested * 0.02,
                    "commission_pool": total_invested * 0.005,
                    "company_share": total_invested * 0.005 * (company.get("commission_split", {}).get("company", 50) / 100),
                    "agent_share": total_invested * 0.005 * (company.get("commission_split", {}).get("agent", 50) / 100)
                },
                
                "quarterly_history": quarters,
                
                "investment_count": len(investments),
                "active_investments": len([i for i in investments if i.get("status") == "active"]),
                "incubation_investments": len([i for i in investments if i.get("status") == "incubation"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching franchise cashflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CLIENTS MANAGEMENT (Multi-tenant)
# =============================================================================

@router.get("/clients")
async def get_franchise_clients(authorization: str = Header(None)):
    """
    Get all clients for franchise company.
    Multi-tenant: Only returns clients belonging to this company.
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()
        
        # Get clients
        clients = await db.franchise_clients.find(
            {"company_id": company_id, "_id": {"$ne": "schema_definition"}},
            {"_id": 0}
        ).to_list(1000)
        
        # Enrich with investment data
        for client in clients:
            client_id = client.get("client_id")
            
            # Get investments
            investments = await db.franchise_investments.find(
                {"client_id": client_id},
                {"_id": 0}
            ).to_list(10)
            
            client["investments"] = investments
            client["total_invested"] = sum(i.get("amount", 0) for i in investments)
            client["total_returns"] = sum(i.get("total_returns_earned", 0) for i in investments)
        
        # Summary stats
        total_clients = len(clients)
        active_clients = len([c for c in clients if c.get("status") == "active"])
        total_aum = sum(c.get("total_invested", 0) for c in clients)
        
        return {
            "success": True,
            "clients": clients,
            "summary": {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "incubation_clients": len([c for c in clients if c.get("status") == "incubation"]),
                "total_aum": total_aum
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching franchise clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{client_id}")
async def get_franchise_client_detail(client_id: str, authorization: str = Header(None)):
    """
    Get detailed client information.
    Multi-tenant: Verifies client belongs to company.
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()
        
        # Get client - verify company_id matches
        client = await db.franchise_clients.find_one(
            {"client_id": client_id, "company_id": company_id},
            {"_id": 0}
        )
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get investments
        investments = await db.franchise_investments.find(
            {"client_id": client_id},
            {"_id": 0}
        ).to_list(10)
        
        # Get referral agent if any
        agent = None
        if client.get("referral_agent_id"):
            agent = await db.franchise_referral_agents.find_one(
                {"agent_id": client["referral_agent_id"]},
                {"_id": 0, "password_hash": 0}
            )
        
        return {
            "success": True,
            "client": client,
            "investments": investments,
            "referral_agent": agent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching franchise client detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# REFERRAL AGENTS MANAGEMENT (Multi-tenant)
# =============================================================================

@router.get("/agents")
async def get_franchise_agents(authorization: str = Header(None)):
    """
    Get all referral agents for franchise company.
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()
        
        agents = await db.franchise_referral_agents.find(
            {"company_id": company_id, "_id": {"$ne": "schema_definition"}},
            {"_id": 0, "password_hash": 0}
        ).to_list(100)
        
        # Enrich with stats
        for agent in agents:
            agent_id = agent.get("agent_id")
            
            # Count referred clients
            client_count = await db.franchise_clients.count_documents({
                "referral_agent_id": agent_id
            })
            agent["total_clients_referred"] = client_count
            
            # Sum AUM from referred clients
            pipeline = [
                {"$match": {"referral_agent_id": agent_id, "status": {"$in": ["incubation", "active"]}}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            aum_result = await db.franchise_investments.aggregate(pipeline).to_list(1)
            agent["total_aum_referred"] = aum_result[0]["total"] if aum_result else 0
        
        return {
            "success": True,
            "agents": agents,
            "count": len(agents)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching franchise agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# COMMISSION MANAGEMENT (Multi-tenant)
# =============================================================================

@router.get("/commissions")
async def get_franchise_commissions(authorization: str = Header(None)):
    """
    Get commission data for franchise company.
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()
        
        # Get company split
        company = await db.franchise_companies.find_one({"company_id": company_id})
        split = company.get("commission_split", {"company": 50, "agent": 50}) if company else {"company": 50, "agent": 50}
        
        # Get commission transactions
        transactions = await db.franchise_commission_transactions.find(
            {"company_id": company_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        
        # Calculate totals
        total_pool = sum(t.get("commission_pool_amount", 0) for t in transactions)
        total_company = sum(t.get("amount", 0) for t in transactions if t.get("transaction_type") == "company_share")
        total_agent = sum(t.get("amount", 0) for t in transactions if t.get("transaction_type") == "agent_share")
        total_paid = sum(t.get("amount", 0) for t in transactions if t.get("status") == "paid")
        total_pending = sum(t.get("amount", 0) for t in transactions if t.get("status") == "pending")
        
        return {
            "success": True,
            "commissions": {
                "split": split,
                "totals": {
                    "pool": total_pool,
                    "company_share": total_company,
                    "agent_share": total_agent,
                    "paid": total_paid,
                    "pending": total_pending
                },
                "transactions": transactions[:50]  # Last 50
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching franchise commissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ONBOARDING: Create Client + Login (Admin action)
# =============================================================================

DEFAULT_TEMP_PASSWORD = "Fidus2026!"

def _hash_password(password: str) -> str:
    salt = "fidus_franchise_salt_2026"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


class OnboardClientRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    country: str = ""
    investment_amount: float
    referral_agent_id: str


class OnboardAgentRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    commission_tier: int = 50


@router.post("/onboard-client")
async def onboard_franchise_client(req: OnboardClientRequest, authorization: str = Header(None)):
    """
    Create a franchise client + investment record + login credentials in one step.
    Auto-generates password Fidus2026!
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()

        # Verify company
        company = await db.franchise_companies.find_one({"company_id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Verify agent belongs to this company
        agent = await db.franchise_referral_agents.find_one({
            "agent_id": req.referral_agent_id, "company_id": company_id
        })
        if not agent:
            raise HTTPException(status_code=400, detail="Referral agent not found in your company")

        # Check duplicate email
        existing = await db.franchise_clients.find_one({
            "company_id": company_id, "email": req.email.lower()
        })
        if existing:
            raise HTTPException(status_code=400, detail="Client with this email already exists")

        client_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        from dateutil.relativedelta import relativedelta
        incubation_end = now + relativedelta(months=2)
        contract_end = now + relativedelta(months=14)

        # 1. Create client
        client_doc = {
            "client_id": client_id,
            "company_id": company_id,
            "first_name": req.first_name,
            "last_name": req.last_name,
            "email": req.email.lower(),
            "phone": req.phone,
            "country": req.country,
            "investment_amount": req.investment_amount,
            "investment_date": now,
            "contract_start_date": now,
            "contract_end_date": contract_end,
            "incubation_end_date": incubation_end,
            "visible_return_pct": 2.0,
            "actual_return_pct": 2.5,
            "referral_agent_id": req.referral_agent_id,
            "status": "incubation",
            "kyc_status": "pending",
            "created_at": now,
            "updated_at": now
        }
        await db.franchise_clients.insert_one(client_doc)

        # 2. Create investment record
        investment_doc = {
            "investment_id": str(uuid.uuid4()),
            "company_id": company_id,
            "client_id": client_id,
            "referral_agent_id": req.referral_agent_id,
            "amount": req.investment_amount,
            "investment_date": now,
            "fund_type": "BALANCE",
            "contract_months": 14,
            "incubation_months": 2,
            "client_return_pct": 2.0,
            "gross_return_pct": 2.5,
            "total_returns_earned": 0,
            "total_returns_paid": 0,
            "commission_pool": 0,
            "company_commission": 0,
            "agent_commission": 0,
            "status": "incubation",
            "created_at": now,
            "updated_at": now
        }
        await db.franchise_investments.insert_one(investment_doc)

        # 3. Create login credentials
        login_doc = {
            "client_id": client_id,
            "company_id": company_id,
            "email": req.email.lower(),
            "password_hash": _hash_password(DEFAULT_TEMP_PASSWORD),
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        await db.franchise_client_logins.insert_one(login_doc)

        # 4. Update agent stats
        await db.franchise_referral_agents.update_one(
            {"agent_id": req.referral_agent_id},
            {"$inc": {"total_clients_referred": 1, "total_aum_referred": req.investment_amount}}
        )

        logger.info(f"Onboarded client {req.first_name} {req.last_name} for company {company_id}")

        return {
            "success": True,
            "message": f"Client {req.first_name} {req.last_name} onboarded successfully",
            "client_id": client_id,
            "credentials": {
                "email": req.email.lower(),
                "temp_password": DEFAULT_TEMP_PASSWORD,
                "login_url": "/franchise/client/login"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error onboarding client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/onboard-agent")
async def onboard_franchise_agent(req: OnboardAgentRequest, authorization: str = Header(None)):
    """
    Create a franchise referral agent + login credentials in one step.
    Auto-generates password Fidus2026!
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()

        company = await db.franchise_companies.find_one({"company_id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Check duplicate email
        existing = await db.franchise_referral_agents.find_one({
            "company_id": company_id, "email": req.email.lower()
        })
        if existing:
            raise HTTPException(status_code=400, detail="Agent with this email already exists")

        agent_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # 1. Create agent
        agent_doc = {
            "agent_id": agent_id,
            "company_id": company_id,
            "first_name": req.first_name,
            "last_name": req.last_name,
            "email": req.email.lower(),
            "phone": req.phone,
            "commission_tier": req.commission_tier,
            "total_commission_earned": 0,
            "pending_commission": 0,
            "total_clients_referred": 0,
            "total_aum_referred": 0,
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        await db.franchise_referral_agents.insert_one(agent_doc)

        # 2. Create login credentials
        login_doc = {
            "agent_id": agent_id,
            "company_id": company_id,
            "email": req.email.lower(),
            "password_hash": _hash_password(DEFAULT_TEMP_PASSWORD),
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        await db.franchise_agent_logins.insert_one(login_doc)

        logger.info(f"Onboarded agent {req.first_name} {req.last_name} for company {company_id}")

        return {
            "success": True,
            "message": f"Agent {req.first_name} {req.last_name} onboarded successfully",
            "agent_id": agent_id,
            "credentials": {
                "email": req.email.lower(),
                "temp_password": DEFAULT_TEMP_PASSWORD,
                "login_url": "/franchise/agent/login"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error onboarding agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# BULK IMPORT CLIENTS (CSV Upload)
# =============================================================================

@router.post("/bulk-import-clients")
async def bulk_import_clients(file: UploadFile = File(...), authorization: str = Header(None)):
    """
    Bulk import franchise clients from CSV file.
    Expected columns: first_name, last_name, email, phone, country, investment_amount, referral_agent_email
    Creates client + investment + login for each valid row. Password = Fidus2026!
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()

        company = await db.franchise_companies.find_one({"company_id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Read CSV
        contents = await file.read()
        try:
            text = contents.decode("utf-8-sig")  # Handle BOM
        except UnicodeDecodeError:
            text = contents.decode("latin-1")

        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        # Pre-load agents for lookup by email
        agents = await db.franchise_referral_agents.find(
            {"company_id": company_id}, {"_id": 0, "agent_id": 1, "email": 1, "first_name": 1, "last_name": 1}
        ).to_list(500)
        agent_map = {a["email"].lower(): a["agent_id"] for a in agents}

        # Pre-load existing client emails to skip duplicates
        existing_emails = set()
        existing = await db.franchise_clients.find(
            {"company_id": company_id}, {"_id": 0, "email": 1}
        ).to_list(10000)
        existing_emails = {c["email"].lower() for c in existing}

        results = {"imported": 0, "skipped": 0, "errors": [], "credentials": []}
        now = datetime.now(timezone.utc)

        for idx, row in enumerate(rows, start=2):  # Row 2 = first data row (1 = header)
            first_name = (row.get("first_name") or "").strip()
            last_name = (row.get("last_name") or "").strip()
            email = (row.get("email") or "").strip().lower()
            phone = (row.get("phone") or "").strip()
            country = (row.get("country") or "").strip()
            amount_str = (row.get("investment_amount") or "").strip().replace(",", "").replace("$", "")
            agent_email = (row.get("referral_agent_email") or "").strip().lower()

            # Validate required fields
            if not first_name or not last_name or not email:
                results["errors"].append({"row": idx, "error": "Missing first_name, last_name, or email"})
                results["skipped"] += 1
                continue

            if not amount_str:
                results["errors"].append({"row": idx, "email": email, "error": "Missing investment_amount"})
                results["skipped"] += 1
                continue

            try:
                investment_amount = float(amount_str)
            except ValueError:
                results["errors"].append({"row": idx, "email": email, "error": f"Invalid investment_amount: {amount_str}"})
                results["skipped"] += 1
                continue

            if email in existing_emails:
                results["errors"].append({"row": idx, "email": email, "error": "Duplicate email (already exists)"})
                results["skipped"] += 1
                continue

            # Resolve agent
            referral_agent_id = agent_map.get(agent_email)
            if not referral_agent_id and agent_email:
                results["errors"].append({"row": idx, "email": email, "error": f"Agent not found: {agent_email}"})
                results["skipped"] += 1
                continue
            if not referral_agent_id:
                # Use first available agent if none specified
                referral_agent_id = agents[0]["agent_id"] if agents else None
            if not referral_agent_id:
                results["errors"].append({"row": idx, "email": email, "error": "No referral agents available"})
                results["skipped"] += 1
                continue

            # Create client
            client_id = str(uuid.uuid4())
            from dateutil.relativedelta import relativedelta
            incubation_end = now + relativedelta(months=2)
            contract_end = now + relativedelta(months=14)

            client_doc = {
                "client_id": client_id,
                "company_id": company_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "country": country,
                "investment_amount": investment_amount,
                "investment_date": now,
                "contract_start_date": now,
                "contract_end_date": contract_end,
                "incubation_end_date": incubation_end,
                "visible_return_pct": 2.0,
                "actual_return_pct": 2.5,
                "referral_agent_id": referral_agent_id,
                "status": "incubation",
                "kyc_status": "pending",
                "created_at": now,
                "updated_at": now
            }
            await db.franchise_clients.insert_one(client_doc)

            investment_doc = {
                "investment_id": str(uuid.uuid4()),
                "company_id": company_id,
                "client_id": client_id,
                "referral_agent_id": referral_agent_id,
                "amount": investment_amount,
                "investment_date": now,
                "fund_type": "BALANCE",
                "contract_months": 14,
                "incubation_months": 2,
                "client_return_pct": 2.0,
                "gross_return_pct": 2.5,
                "total_returns_earned": 0,
                "total_returns_paid": 0,
                "commission_pool": 0,
                "company_commission": 0,
                "agent_commission": 0,
                "status": "incubation",
                "created_at": now,
                "updated_at": now
            }
            await db.franchise_investments.insert_one(investment_doc)

            login_doc = {
                "client_id": client_id,
                "company_id": company_id,
                "email": email,
                "password_hash": _hash_password(DEFAULT_TEMP_PASSWORD),
                "status": "active",
                "created_at": now,
                "updated_at": now
            }
            await db.franchise_client_logins.insert_one(login_doc)

            existing_emails.add(email)
            results["imported"] += 1
            results["credentials"].append({
                "name": f"{first_name} {last_name}",
                "email": email,
                "investment_amount": investment_amount,
                "temp_password": DEFAULT_TEMP_PASSWORD
            })

        logger.info(f"Bulk import: {results['imported']} imported, {results['skipped']} skipped for company {company_id}")

        return {
            "success": True,
            "message": f"Imported {results['imported']} clients, {results['skipped']} skipped",
            "imported": results["imported"],
            "skipped": results["skipped"],
            "errors": results["errors"][:20],  # Limit error list
            "credentials": results["credentials"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk import: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# OVERVIEW STATS (Multi-tenant)
# =============================================================================

@router.get("/overview")
async def get_franchise_overview(authorization: str = Header(None)):
    """
    Get overview dashboard stats for franchise company.
    """
    try:
        company_id = get_company_id_from_token(authorization)
        db = await get_database()
        
        # Get company
        company = await db.franchise_companies.find_one(
            {"company_id": company_id},
            {"_id": 0}
        )
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Client stats
        total_clients = await db.franchise_clients.count_documents({
            "company_id": company_id,
            "_id": {"$ne": "schema_definition"}
        })
        active_clients = await db.franchise_clients.count_documents({
            "company_id": company_id,
            "status": "active"
        })
        
        # Agent stats
        total_agents = await db.franchise_referral_agents.count_documents({
            "company_id": company_id,
            "_id": {"$ne": "schema_definition"}
        })
        
        # AUM
        pipeline = [
            {"$match": {"company_id": company_id, "status": {"$in": ["incubation", "active"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        aum_result = await db.franchise_investments.aggregate(pipeline).to_list(1)
        total_aum = aum_result[0]["total"] if aum_result else 0
        
        # Monthly projections
        monthly_gross = total_aum * 0.025
        monthly_client = total_aum * 0.02
        monthly_commission = total_aum * 0.005
        
        split = company.get("commission_split", {"company": 50, "agent": 50})
        monthly_company_share = monthly_commission * (split["company"] / 100)
        monthly_agent_share = monthly_commission * (split["agent"] / 100)
        
        return {
            "success": True,
            "overview": {
                "company": {
                    "name": company.get("company_name"),
                    "code": company.get("company_code"),
                    "subdomain": company.get("subdomain"),
                    "status": company.get("status"),
                    "logo_url": company.get("logo_url"),
                    "primary_color": company.get("primary_color"),
                    "secondary_color": company.get("secondary_color")
                },
                "stats": {
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "total_agents": total_agents,
                    "total_aum": total_aum
                },
                "monthly_projections": {
                    "gross_return": monthly_gross,
                    "client_payments": monthly_client,
                    "commission_pool": monthly_commission,
                    "company_share": monthly_company_share,
                    "agent_share": monthly_agent_share
                },
                "commission_split": split,
                "fund_terms": {
                    "gross_return_pct": 2.5,
                    "client_return_pct": 2.0,
                    "commission_pool_pct": 0.5,
                    "contract_months": 14,
                    "incubation_months": 2
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching franchise overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# =============================================================================
# INSTRUMENT SPECIFICATIONS (Read-only for franchise admins)
# =============================================================================

@router.get("/instruments")
async def get_franchise_instruments(authorization: str = Header(None)):
    """
    Get FIDUS Tier-1 instrument specifications (read-only view for franchise admins).
    """
    try:
        get_company_id_from_token(authorization)  # Validate token
        db = await get_database()
        
        instruments = await db.instrument_specs.find(
            {},
            {"_id": 0}
        ).to_list(50)
        
        return {
            "success": True,
            "instruments": instruments,
            "count": len(instruments)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching instruments for franchise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# RISK POLICY (Read-only for franchise admins)
# =============================================================================

@router.get("/risk-policy")
async def get_franchise_risk_policy(authorization: str = Header(None)):
    """
    Get FIDUS risk policy parameters (read-only view for franchise admins).
    """
    try:
        get_company_id_from_token(authorization)  # Validate token
        
        # Return the standard FIDUS risk policy
        policy = {
            "max_risk_per_trade_pct": 1.0,
            "max_intraday_loss_pct": 3.0,
            "max_weekly_loss_pct": 6.0,
            "max_monthly_dd_pct": 10.0,
            "max_margin_usage_pct": 25.0,
            "leverage": 200,
            "drawdown_warning_pct": 5.0,
            "drawdown_critical_pct": 10.0,
            "max_single_instrument_x": 10,
            "max_total_notional_x": 20,
            "overnight_exposure": "OFF"
        }
        
        return {
            "success": True,
            "policy": policy
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching risk policy for franchise: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# =============================================================================
# HELPERS FOR CLIENT/AGENT TOKEN DECODING
# =============================================================================

def get_client_id_from_token(authorization: str) -> dict:
    """Extract client_id and company_id from JWT token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "franchise_client":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return {"client_id": payload["client_id"], "company_id": payload["company_id"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_agent_id_from_token(authorization: str) -> dict:
    """Extract agent_id and company_id from JWT token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "franchise_agent":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return {"agent_id": payload["agent_id"], "company_id": payload["company_id"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# =============================================================================
# CLIENT PORTAL ENDPOINTS
# =============================================================================

@router.get("/client/overview")
async def get_client_overview(authorization: str = Header(None)):
    """Client's investment overview — shows only their own data."""
    try:
        ids = get_client_id_from_token(authorization)
        db = await get_database()

        client = await db.franchise_clients.find_one(
            {"client_id": ids["client_id"], "company_id": ids["company_id"]},
            {"_id": 0}
        )
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        investments = await db.franchise_investments.find(
            {"client_id": ids["client_id"]},
            {"_id": 0}
        ).to_list(20)

        total_invested = sum(i.get("amount", 0) for i in investments)
        total_returns = sum(i.get("total_returns_earned", 0) for i in investments)
        total_paid = sum(i.get("total_returns_paid", 0) for i in investments)

        company = await db.franchise_companies.find_one(
            {"company_id": ids["company_id"]},
            {"_id": 0, "company_name": 1, "logo_url": 1, "primary_color": 1, "subdomain": 1}
        )

        return {
            "success": True,
            "client": {
                "first_name": client.get("first_name"),
                "last_name": client.get("last_name"),
                "email": client.get("email"),
                "status": client.get("status"),
                "investment_date": str(client.get("investment_date", "")),
                "contract_start_date": str(client.get("contract_start_date", "")),
                "contract_end_date": str(client.get("contract_end_date", "")),
                "incubation_end_date": str(client.get("incubation_end_date", "")),
                "kyc_status": client.get("kyc_status", "pending"),
            },
            "summary": {
                "total_invested": total_invested,
                "total_returns_earned": total_returns,
                "total_returns_paid": total_paid,
                "pending_returns": total_returns - total_paid,
                "visible_return_pct": client.get("visible_return_pct", 2.0),
            },
            "investments": investments,
            "company": company or {},
            "fund_terms": {
                "contract_months": 14,
                "incubation_months": 2,
                "client_return_pct": 2.0,
                "payment_frequency": "quarterly"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching client overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# AGENT PORTAL ENDPOINTS
# =============================================================================

@router.get("/agent/overview")
async def get_agent_overview(authorization: str = Header(None)):
    """Agent's referral overview — shows only their own referred clients."""
    try:
        ids = get_agent_id_from_token(authorization)
        db = await get_database()

        agent = await db.franchise_referral_agents.find_one(
            {"agent_id": ids["agent_id"], "company_id": ids["company_id"]},
            {"_id": 0, "password_hash": 0}
        )
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Get referred clients
        referred_clients = await db.franchise_clients.find(
            {"referral_agent_id": ids["agent_id"]},
            {"_id": 0}
        ).to_list(500)

        # Get referred investments
        referred_investments = await db.franchise_investments.find(
            {"referral_agent_id": ids["agent_id"]},
            {"_id": 0}
        ).to_list(500)

        total_aum = sum(i.get("amount", 0) for i in referred_investments if i.get("status") in ("incubation", "active"))
        total_commission = sum(i.get("agent_commission", 0) for i in referred_investments)

        # Get commission transactions
        transactions = await db.franchise_commission_transactions.find(
            {"agent_id": ids["agent_id"]},
            {"_id": 0}
        ).sort("created_at", -1).to_list(50)

        company = await db.franchise_companies.find_one(
            {"company_id": ids["company_id"]},
            {"_id": 0, "company_name": 1, "logo_url": 1, "primary_color": 1, "subdomain": 1, "commission_split": 1}
        )

        return {
            "success": True,
            "agent": {
                "first_name": agent.get("first_name"),
                "last_name": agent.get("last_name"),
                "email": agent.get("email"),
                "commission_tier": agent.get("commission_tier", 50),
                "status": agent.get("status"),
            },
            "summary": {
                "total_clients_referred": len(referred_clients),
                "total_aum_referred": total_aum,
                "total_commission_earned": total_commission,
                "active_clients": len([c for c in referred_clients if c.get("status") == "active"]),
                "incubation_clients": len([c for c in referred_clients if c.get("status") == "incubation"]),
            },
            "clients": [
                {
                    "client_id": c.get("client_id"),
                    "first_name": c.get("first_name"),
                    "last_name": c.get("last_name"),
                    "investment_amount": c.get("investment_amount", 0),
                    "status": c.get("status"),
                    "investment_date": str(c.get("investment_date", "")),
                }
                for c in referred_clients
            ],
            "transactions": transactions,
            "company": company or {},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching agent overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
