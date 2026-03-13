"""
White Label / Franchise API Routes
March 2026 - FIDUS Franchise System

Multi-tenant architecture for franchise companies selling FIDUS BALANCE fund.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import os
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/franchise", tags=["White Label Franchise"])

# Database connection
async def get_database():
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        raise HTTPException(status_code=500, detail="Database not configured")
    client = AsyncIOMotorClient(mongo_url)
    return client.fidus_production


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class FranchiseCompanyCreate(BaseModel):
    company_name: str
    company_code: str  # For subdomain
    contact_email: str
    contact_phone: str = ""
    logo_url: str = ""
    primary_color: str = "#0ea5e9"  # Default cyan
    secondary_color: str = "#1e293b"  # Default slate
    
    # Business Terms
    commission_split_company: int = 50  # Company gets 50% of 0.5%
    commission_split_agent: int = 50    # Agent gets 50% of 0.5%
    
    # OMNIBUS Account (to be assigned later)
    omnibus_account: Optional[int] = None
    omnibus_allocation: float = 0


class FranchiseCompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    commission_split_company: Optional[int] = None
    commission_split_agent: Optional[int] = None
    omnibus_account: Optional[int] = None
    omnibus_allocation: Optional[float] = None
    status: Optional[str] = None


class FranchiseClientCreate(BaseModel):
    company_id: str
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    country: str = ""
    investment_amount: float
    referral_agent_id: Optional[str] = None


class FranchiseAgentCreate(BaseModel):
    company_id: str
    first_name: str
    last_name: str
    email: str
    phone: str = ""
    commission_tier: int = 50  # 30, 40, or 50


# =============================================================================
# FRANCHISE COMPANY ENDPOINTS (FIDUS Admin Only)
# =============================================================================

@router.get("/companies")
async def get_all_franchise_companies():
    """
    Get all franchise companies (FIDUS Admin view).
    """
    try:
        db = await get_database()
        
        companies = await db.franchise_companies.find(
            {"_id": {"$ne": "schema_definition"}},
            {"_id": 0}
        ).to_list(100)
        
        # Calculate stats for each company
        for company in companies:
            company_id = company.get("company_id")
            if company_id:
                # Get client count
                client_count = await db.franchise_clients.count_documents({
                    "company_id": company_id,
                    "_id": {"$ne": "schema_definition"}
                })
                company["total_clients"] = client_count
                
                # Get total AUM
                pipeline = [
                    {"$match": {"company_id": company_id, "status": "active"}},
                    {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
                ]
                aum_result = await db.franchise_investments.aggregate(pipeline).to_list(1)
                company["total_aum"] = aum_result[0]["total"] if aum_result else 0
                
                # Get agent count
                agent_count = await db.franchise_referral_agents.count_documents({
                    "company_id": company_id,
                    "_id": {"$ne": "schema_definition"}
                })
                company["total_agents"] = agent_count
        
        return {
            "success": True,
            "companies": companies,
            "count": len(companies)
        }
        
    except Exception as e:
        logger.error(f"Error fetching franchise companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/companies")
async def create_franchise_company(company: FranchiseCompanyCreate):
    """
    Create a new franchise company (FIDUS Admin only).
    """
    try:
        db = await get_database()
        
        # Check if company_code already exists
        existing = await db.franchise_companies.find_one({
            "company_code": company.company_code.lower()
        })
        if existing:
            raise HTTPException(status_code=400, detail=f"Company code '{company.company_code}' already exists")
        
        # Generate company_id
        company_id = str(uuid.uuid4())
        
        # Build subdomain
        subdomain = f"{company.company_code.lower()}.fidus-balance.com"
        
        company_doc = {
            "company_id": company_id,
            "company_name": company.company_name,
            "company_code": company.company_code.lower(),
            "subdomain": subdomain,
            "contact_email": company.contact_email,
            "contact_phone": company.contact_phone,
            "logo_url": company.logo_url,
            "primary_color": company.primary_color,
            "secondary_color": company.secondary_color,
            
            # Fund Terms (fixed for BALANCE)
            "fund_type": "BALANCE",
            "contract_months": 14,
            "incubation_months": 2,
            "gross_return_pct": 2.5,
            "client_return_pct": 2.0,
            "commission_pool_pct": 0.5,
            
            # Commission Split
            "commission_split": {
                "company": company.commission_split_company,
                "agent": company.commission_split_agent
            },
            
            # OMNIBUS Account
            "omnibus_account": company.omnibus_account,
            "omnibus_allocation": company.omnibus_allocation,
            
            # Status
            "status": "active",
            "agreement_date": datetime.now(timezone.utc),
            
            # Timestamps
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.franchise_companies.insert_one(company_doc)
        
        logger.info(f"✅ Created franchise company: {company.company_name} ({company_id})")
        
        # Remove _id for response
        company_doc.pop("_id", None)
        
        return {
            "success": True,
            "message": f"Franchise company '{company.company_name}' created",
            "company": company_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating franchise company: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies/{company_id}")
async def get_franchise_company(company_id: str):
    """
    Get a specific franchise company by ID.
    """
    try:
        db = await get_database()
        
        company = await db.franchise_companies.find_one(
            {"company_id": company_id},
            {"_id": 0}
        )
        
        if not company:
            raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
        
        # Get stats
        client_count = await db.franchise_clients.count_documents({"company_id": company_id})
        agent_count = await db.franchise_referral_agents.count_documents({"company_id": company_id})
        
        pipeline = [
            {"$match": {"company_id": company_id, "status": "active"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        aum_result = await db.franchise_investments.aggregate(pipeline).to_list(1)
        
        company["total_clients"] = client_count
        company["total_agents"] = agent_count
        company["total_aum"] = aum_result[0]["total"] if aum_result else 0
        
        return {
            "success": True,
            "company": company
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching franchise company: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/companies/{company_id}")
async def update_franchise_company(company_id: str, update: FranchiseCompanyUpdate):
    """
    Update a franchise company.
    """
    try:
        db = await get_database()
        
        update_fields = update.model_dump(exclude_none=True)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Handle commission split update
        if "commission_split_company" in update_fields or "commission_split_agent" in update_fields:
            company = await db.franchise_companies.find_one({"company_id": company_id})
            if company:
                current_split = company.get("commission_split", {"company": 50, "agent": 50})
                if "commission_split_company" in update_fields:
                    current_split["company"] = update_fields.pop("commission_split_company")
                if "commission_split_agent" in update_fields:
                    current_split["agent"] = update_fields.pop("commission_split_agent")
                update_fields["commission_split"] = current_split
        
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.franchise_companies.update_one(
            {"company_id": company_id},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
        
        return {
            "success": True,
            "message": f"Company {company_id} updated",
            "updated_fields": list(update_fields.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating franchise company: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# FRANCHISE CLIENT ENDPOINTS (Multi-tenant)
# =============================================================================

@router.get("/companies/{company_id}/clients")
async def get_franchise_clients(company_id: str):
    """
    Get all clients for a franchise company.
    """
    try:
        db = await get_database()
        
        clients = await db.franchise_clients.find(
            {"company_id": company_id, "_id": {"$ne": "schema_definition"}},
            {"_id": 0}
        ).to_list(1000)
        
        return {
            "success": True,
            "clients": clients,
            "count": len(clients)
        }
        
    except Exception as e:
        logger.error(f"Error fetching franchise clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clients")
async def create_franchise_client(client: FranchiseClientCreate):
    """
    Create a new client for a franchise company.
    """
    try:
        db = await get_database()
        
        # Verify company exists
        company = await db.franchise_companies.find_one({"company_id": client.company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        client_id = str(uuid.uuid4())
        
        # Calculate contract dates
        now = datetime.now(timezone.utc)
        from dateutil.relativedelta import relativedelta
        incubation_end = now + relativedelta(months=2)
        contract_end = now + relativedelta(months=14)
        
        client_doc = {
            "client_id": client_id,
            "company_id": client.company_id,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email,
            "phone": client.phone,
            "country": client.country,
            "investment_amount": client.investment_amount,
            "investment_date": now,
            "contract_start_date": now,
            "contract_end_date": contract_end,
            "incubation_end_date": incubation_end,
            "visible_return_pct": 2.0,  # What client sees
            "actual_return_pct": 2.5,    # Actual FIDUS return
            "referral_agent_id": client.referral_agent_id,
            "status": "incubation",
            "kyc_status": "pending",
            "created_at": now,
            "updated_at": now
        }
        
        await db.franchise_clients.insert_one(client_doc)
        
        # Also create investment record
        investment_doc = {
            "investment_id": str(uuid.uuid4()),
            "company_id": client.company_id,
            "client_id": client_id,
            "referral_agent_id": client.referral_agent_id,
            "amount": client.investment_amount,
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
        
        client_doc.pop("_id", None)
        
        return {
            "success": True,
            "message": f"Client {client.first_name} {client.last_name} created",
            "client": client_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating franchise client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# FRANCHISE AGENT ENDPOINTS (Multi-tenant)
# =============================================================================

@router.get("/companies/{company_id}/agents")
async def get_franchise_agents(company_id: str):
    """
    Get all referral agents for a franchise company.
    """
    try:
        db = await get_database()
        
        agents = await db.franchise_referral_agents.find(
            {"company_id": company_id, "_id": {"$ne": "schema_definition"}},
            {"_id": 0, "password_hash": 0}
        ).to_list(100)
        
        # Get stats for each agent
        for agent in agents:
            agent_id = agent.get("agent_id")
            if agent_id:
                client_count = await db.franchise_clients.count_documents({
                    "referral_agent_id": agent_id
                })
                agent["clients_referred"] = client_count
        
        return {
            "success": True,
            "agents": agents,
            "count": len(agents)
        }
        
    except Exception as e:
        logger.error(f"Error fetching franchise agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents")
async def create_franchise_agent(agent: FranchiseAgentCreate):
    """
    Create a new referral agent for a franchise company.
    """
    try:
        db = await get_database()
        
        # Verify company exists
        company = await db.franchise_companies.find_one({"company_id": agent.company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Check email uniqueness within company
        existing = await db.franchise_referral_agents.find_one({
            "company_id": agent.company_id,
            "email": agent.email
        })
        if existing:
            raise HTTPException(status_code=400, detail="Agent with this email already exists")
        
        agent_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        agent_doc = {
            "agent_id": agent_id,
            "company_id": agent.company_id,
            "first_name": agent.first_name,
            "last_name": agent.last_name,
            "email": agent.email,
            "phone": agent.phone,
            "commission_tier": agent.commission_tier,
            "total_commission_earned": 0,
            "pending_commission": 0,
            "total_clients_referred": 0,
            "total_aum_referred": 0,
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        
        await db.franchise_referral_agents.insert_one(agent_doc)
        
        agent_doc.pop("_id", None)
        
        return {
            "success": True,
            "message": f"Agent {agent.first_name} {agent.last_name} created",
            "agent": agent_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating franchise agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# COMMISSION SPLIT TABLE
# =============================================================================

@router.get("/commission-splits")
async def get_commission_split_options():
    """
    Get available commission split options.
    """
    return {
        "success": True,
        "commission_splits": [
            {
                "name": "70-30",
                "company_share": 70,
                "agent_share": 30,
                "description": "Company gets 70% of 0.5% commission pool, Agent gets 30%"
            },
            {
                "name": "60-40",
                "company_share": 60,
                "agent_share": 40,
                "description": "Company gets 60% of 0.5% commission pool, Agent gets 40%"
            },
            {
                "name": "50-50",
                "company_share": 50,
                "agent_share": 50,
                "description": "Company gets 50% of 0.5% commission pool, Agent gets 50%"
            }
        ],
        "fund_terms": {
            "gross_return": "2.5% monthly",
            "client_return": "2.0% monthly",
            "commission_pool": "0.5% monthly (difference)",
            "payment_frequency": "Quarterly",
            "contract_duration": "14 months",
            "incubation_period": "2 months"
        }
    }


# =============================================================================
# DASHBOARD STATS (Multi-tenant aware)
# =============================================================================

@router.get("/dashboard/stats")
async def get_franchise_dashboard_stats(company_id: Optional[str] = None):
    """
    Get dashboard statistics.
    If company_id provided: stats for that company only (franchise view)
    If no company_id: aggregate stats for all (FIDUS admin view)
    """
    try:
        db = await get_database()
        
        # Build filter
        company_filter = {"company_id": company_id} if company_id else {}
        
        # Total companies (FIDUS admin only)
        total_companies = await db.franchise_companies.count_documents({
            "_id": {"$ne": "schema_definition"}
        }) if not company_id else 1
        
        # Total clients
        client_filter = {**company_filter, "_id": {"$ne": "schema_definition"}}
        total_clients = await db.franchise_clients.count_documents(client_filter)
        
        # Total AUM
        aum_filter = {**company_filter, "status": {"$in": ["incubation", "active"]}}
        pipeline = [
            {"$match": aum_filter},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        aum_result = await db.franchise_investments.aggregate(pipeline).to_list(1)
        total_aum = aum_result[0]["total"] if aum_result else 0
        
        # Total agents
        agent_filter = {**company_filter, "_id": {"$ne": "schema_definition"}}
        total_agents = await db.franchise_referral_agents.count_documents(agent_filter)
        
        # Commission stats
        commission_pipeline = [
            {"$match": company_filter if company_filter else {}},
            {"$group": {
                "_id": None,
                "total_commission_pool": {"$sum": "$commission_pool"},
                "total_company_commission": {"$sum": "$company_commission"},
                "total_agent_commission": {"$sum": "$agent_commission"}
            }}
        ]
        commission_result = await db.franchise_investments.aggregate(commission_pipeline).to_list(1)
        commission_stats = commission_result[0] if commission_result else {
            "total_commission_pool": 0,
            "total_company_commission": 0,
            "total_agent_commission": 0
        }
        
        return {
            "success": True,
            "stats": {
                "total_companies": total_companies,
                "total_clients": total_clients,
                "total_aum": total_aum,
                "total_agents": total_agents,
                "commission": {
                    "pool": commission_stats.get("total_commission_pool", 0),
                    "company_share": commission_stats.get("total_company_commission", 0),
                    "agent_share": commission_stats.get("total_agent_commission", 0)
                }
            },
            "view": "company" if company_id else "admin"
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
