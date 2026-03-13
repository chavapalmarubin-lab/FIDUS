"""
Franchise Admin Dashboard API
March 2026 - FIDUS White Label Franchise System

Multi-tenant dashboard endpoints for franchise company admins.
All endpoints filter data by company_id from JWT token.
"""

from fastapi import APIRouter, HTTPException, Header
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import Optional
import os
import logging
import jwt

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
