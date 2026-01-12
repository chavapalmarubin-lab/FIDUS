"""
VIKING Trading Operations API
Completely separate from FIDUS funds - manages VIKING CORE and PRO strategies

Collections:
- viking_accounts: Account data for VIKING trading operations
- viking_deals_history: Historical trade data
- viking_analytics: Calculated performance metrics
"""

from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
import sys
sys.path.append('/app/backend')

# Note: VIKING routes are internal APIs for MT4 bridge sync
# Authentication can be added later if needed via auth.dependencies.get_current_agent

router = APIRouter(prefix="/api/viking", tags=["VIKING Trading"])

# Database will be injected via init_db()
db = None

logger = logging.getLogger(__name__)

def init_db(database):
    """Initialize database connection"""
    global db
    db = database
    logger.info("✅ VIKING routes initialized with database connection")


def parse_mt4_datetime(dt_value):
    """Parse datetime from various formats including MT4 format"""
    if dt_value is None:
        return None
    if isinstance(dt_value, datetime):
        return dt_value
    if isinstance(dt_value, str):
        # Try MT4 format first: "2026.01.02 01:11:00"
        try:
            return datetime.strptime(dt_value, "%Y.%m.%d %H:%M:%S")
        except:
            pass
        # Try ISO format
        try:
            return datetime.fromisoformat(dt_value.replace('Z', '+00:00'))
        except:
            pass
        # Try other common formats
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y.%m.%d %H:%M"]:
            try:
                return datetime.strptime(dt_value, fmt)
            except:
                continue
    return None


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class VikingAccountBase(BaseModel):
    account: int
    strategy: str  # CORE or PRO
    broker: str
    server: str
    platform: str = "MT4"
    balance: float = 0.0
    equity: float = 0.0
    margin: float = 0.0
    free_margin: float = 0.0
    profit: float = 0.0
    currency: str = "USD"
    leverage: int = 0
    status: str = "active"  # active, inactive, connection_error
    error_message: Optional[str] = None

class VikingAccountCreate(VikingAccountBase):
    password: Optional[str] = None  # For initial setup only

class VikingAccountUpdate(BaseModel):
    balance: Optional[float] = None
    equity: Optional[float] = None
    margin: Optional[float] = None
    free_margin: Optional[float] = None
    profit: Optional[float] = None
    leverage: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None

class VikingDeal(BaseModel):
    ticket: int
    symbol: str
    type: str  # buy, sell
    volume: float
    open_time: datetime
    close_time: Optional[datetime] = None
    open_price: float
    close_price: Optional[float] = None
    profit: float = 0.0
    commission: float = 0.0
    swap: float = 0.0
    comment: str = ""

class VikingAnalytics(BaseModel):
    total_return: float = 0.0
    monthly_return: float = 0.0
    weekly_return: float = 0.0
    daily_return: float = 0.0
    profit_factor: float = 0.0
    trade_win_rate: float = 0.0
    peak_drawdown: float = 0.0
    risk_reward_ratio: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    history_days: int = 0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_trade_length_hours: float = 0.0
    trades_per_day: float = 0.0
    deposits: float = 0.0
    withdrawals: float = 0.0
    net_deposits: float = 0.0
    banked_profit: float = 0.0
    loss: float = 0.0
    net_profit: float = 0.0


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
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    
    return doc


async def ensure_collections_exist():
    """Ensure VIKING collections exist in the database"""
    if db is None:
        logger.error("Database not initialized")
        return False
    
    try:
        collections = await db.list_collection_names()
        
        # Create viking_accounts if not exists
        if "viking_accounts" not in collections:
            await db.create_collection("viking_accounts")
            # Create unique index on account number
            await db.viking_accounts.create_index("account", unique=True)
            logger.info("✅ Created viking_accounts collection")
        
        # Create viking_deals_history if not exists
        if "viking_deals_history" not in collections:
            await db.create_collection("viking_deals_history")
            # Create compound index for efficient querying
            await db.viking_deals_history.create_index([
                ("account", 1),
                ("ticket", 1)
            ], unique=True)
            await db.viking_deals_history.create_index([
                ("account", 1),
                ("close_time", -1)
            ])
            logger.info("✅ Created viking_deals_history collection")
        
        # Create viking_analytics if not exists
        if "viking_analytics" not in collections:
            await db.create_collection("viking_analytics")
            await db.viking_analytics.create_index([
                ("account", 1),
                ("calculated_at", -1)
            ])
            logger.info("✅ Created viking_analytics collection")
        
        return True
    except Exception as e:
        logger.error(f"Error ensuring collections: {e}")
        return False


async def seed_viking_core_account():
    """Seed the VIKING CORE account (33627673) if not exists"""
    if db is None:
        return
    
    try:
        existing = await db.viking_accounts.find_one({"account": 33627673})
        if not existing:
            viking_core = {
                "_id": "VIKING_33627673",
                "account": 33627673,
                "strategy": "CORE",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real-2",
                "platform": "MT4",
                "balance": 0.0,
                "equity": 0.0,
                "margin": 0.0,
                "free_margin": 0.0,
                "profit": 0.0,
                "currency": "USD",
                "leverage": 0,
                "status": "pending_sync",
                "error_message": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await db.viking_accounts.insert_one(viking_core)
            logger.info("✅ Seeded VIKING CORE account 33627673")
        
        # Also check for PRO account
        existing_pro = await db.viking_accounts.find_one({"account": 1309411})
        if not existing_pro:
            viking_pro = {
                "_id": "VIKING_1309411",
                "account": 1309411,
                "strategy": "PRO",
                "broker": "Traders Trust",
                "server": "TTCM",
                "platform": "MT4",
                "balance": 0.0,
                "equity": 0.0,
                "margin": 0.0,
                "free_margin": 0.0,
                "profit": 0.0,
                "currency": "USD",
                "leverage": 0,
                "status": "pending_setup",
                "error_message": "Needs MT4 terminal login",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await db.viking_accounts.insert_one(viking_pro)
            logger.info("✅ Seeded VIKING PRO account 1309411")
            
    except Exception as e:
        logger.error(f"Error seeding VIKING accounts: {e}")


# ============================================================================
# ACCOUNT ENDPOINTS
# ============================================================================

@router.get("/accounts")
async def get_viking_accounts():
    """Get all VIKING accounts with their latest data"""
    try:
        await ensure_collections_exist()
        await seed_viking_core_account()
        
        accounts = await db.viking_accounts.find({}, {"_id": 0}).to_list(None)
        
        # Get latest analytics for each account
        for account in accounts:
            analytics = await db.viking_analytics.find_one(
                {"account": account["account"]},
                {"_id": 0},
                sort=[("calculated_at", -1)]
            )
            account["analytics"] = analytics or {}
        
        # Calculate combined totals
        total_balance = sum(a.get("balance", 0) for a in accounts if a.get("status") == "active")
        total_equity = sum(a.get("equity", 0) for a in accounts if a.get("status") == "active")
        active_count = sum(1 for a in accounts if a.get("status") == "active")
        
        return {
            "success": True,
            "strategies": serialize_doc(accounts),
            "combined": {
                "total_balance": total_balance,
                "total_equity": total_equity,
                "total_strategies": len(accounts),
                "active_strategies": active_count
            }
        }
    except Exception as e:
        logger.error(f"Error fetching VIKING accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{account_number}")
async def get_viking_account(account_number: int):
    """Get specific VIKING account by account number"""
    try:
        account = await db.viking_accounts.find_one(
            {"account": account_number},
            {"_id": 0}
        )
        
        if not account:
            raise HTTPException(status_code=404, detail=f"VIKING account {account_number} not found")
        
        # Get latest analytics
        analytics = await db.viking_analytics.find_one(
            {"account": account_number},
            {"_id": 0},
            sort=[("calculated_at", -1)]
        )
        account["analytics"] = analytics or {}
        
        return {
            "success": True,
            "account": serialize_doc(account)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING account {account_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts")
async def create_viking_account(account_data: VikingAccountCreate):
    """Create a new VIKING account"""
    try:
        await ensure_collections_exist()
        
        # Check if account already exists
        existing = await db.viking_accounts.find_one({"account": account_data.account})
        if existing:
            raise HTTPException(status_code=400, detail=f"Account {account_data.account} already exists")
        
        doc = {
            "_id": f"VIKING_{account_data.account}",
            **account_data.dict(exclude={"password"}),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.viking_accounts.insert_one(doc)
        
        return {
            "success": True,
            "message": f"VIKING account {account_data.account} created successfully",
            "account": serialize_doc(doc)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating VIKING account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/accounts/{account_number}")
async def update_viking_account(account_number: int, update_data: VikingAccountUpdate):
    """Update VIKING account data (used by MT4 bridge for syncing)"""
    try:
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.viking_accounts.update_one(
            {"account": account_number},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"VIKING account {account_number} not found")
        
        # Fetch updated account
        account = await db.viking_accounts.find_one({"account": account_number}, {"_id": 0})
        
        return {
            "success": True,
            "message": f"VIKING account {account_number} updated",
            "account": serialize_doc(account)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating VIKING account {account_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/{strategy}")
async def get_viking_analytics(strategy: str):
    """Get analytics for CORE or PRO strategy"""
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        # Get account for this strategy
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        # Get latest analytics
        analytics = await db.viking_analytics.find_one(
            {"account": account["account"]},
            {"_id": 0},
            sort=[("calculated_at", -1)]
        )
        
        if not analytics:
            # Return default analytics structure
            analytics = {
                "account": account["account"],
                "strategy": strategy,
                "calculated_at": datetime.now(timezone.utc).isoformat(),
                "total_return": 0.0,
                "monthly_return": 0.0,
                "weekly_return": 0.0,
                "daily_return": 0.0,
                "profit_factor": 0.0,
                "trade_win_rate": 0.0,
                "peak_drawdown": 0.0,
                "risk_reward_ratio": 0.0,
                "history_days": 0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "trades_per_day": 0.0,
                "deposits": 0.0,
                "withdrawals": 0.0,
                "net_deposits": 0.0,
                "banked_profit": 0.0,
                "loss": 0.0,
                "net_profit": 0.0,
                "status": "awaiting_data"
            }
        
        return {
            "success": True,
            "strategy": strategy,
            "analytics": serialize_doc(analytics)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING analytics for {strategy}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/{account_number}")
async def save_viking_analytics(account_number: int, analytics: VikingAnalytics):
    """Save calculated analytics for a VIKING account (used by analytics engine)"""
    try:
        # Get account info
        account = await db.viking_accounts.find_one({"account": account_number}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {account_number} not found")
        
        doc = {
            "account": account_number,
            "strategy": account.get("strategy"),
            "calculated_at": datetime.now(timezone.utc),
            **analytics.dict()
        }
        
        await db.viking_analytics.insert_one(doc)
        
        return {
            "success": True,
            "message": f"Analytics saved for account {account_number}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving VIKING analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DEALS ENDPOINTS
# ============================================================================

@router.get("/deals/{strategy}")
async def get_viking_deals(
    strategy: str,
    limit: int = 100,
    skip: int = 0,
    symbol: Optional[str] = None
):
    """Get deal history for CORE or PRO strategy"""
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        # Get account for this strategy
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        # Handle both string and int account numbers
        account_query = {"$or": [
            {"account": account["account"]},
            {"account": str(account["account"])}
        ]}
        query = {**account_query}
        if symbol:
            query["symbol"] = {"$regex": symbol, "$options": "i"}
        
        # Get deals with pagination
        deals = await db.viking_deals_history.find(
            query,
            {"_id": 0}
        ).sort("close_time", -1).skip(skip).limit(limit).to_list(None)
        
        total = await db.viking_deals_history.count_documents(query)
        
        return {
            "success": True,
            "strategy": strategy,
            "deals": serialize_doc(deals),
            "pagination": {
                "total": total,
                "limit": limit,
                "skip": skip,
                "has_more": skip + limit < total
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING deals for {strategy}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deals/batch")
async def save_viking_deals_batch(deals: List[Dict[str, Any]]):
    """Batch insert deals from MT4 bridge (upsert based on ticket)"""
    try:
        if not deals:
            return {"success": True, "inserted": 0, "updated": 0}
        
        inserted = 0
        updated = 0
        
        for deal in deals:
            # Ensure required fields
            if "account" not in deal or "ticket" not in deal:
                continue
            
            deal["updated_at"] = datetime.now(timezone.utc)
            
            result = await db.viking_deals_history.update_one(
                {"account": deal["account"], "ticket": deal["ticket"]},
                {"$set": deal},
                upsert=True
            )
            
            if result.upserted_id:
                inserted += 1
            elif result.modified_count > 0:
                updated += 1
        
        return {
            "success": True,
            "inserted": inserted,
            "updated": updated,
            "total_processed": len(deals)
        }
    except Exception as e:
        logger.error(f"Error batch saving VIKING deals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ORDERS (OPEN TRADES) ENDPOINTS
# ============================================================================

@router.get("/orders/{strategy}")
async def get_viking_orders(strategy: str):
    """Get open orders/trades for CORE or PRO strategy"""
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        # Get account for this strategy
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        # Open orders have no close_time
        orders = await db.viking_deals_history.find(
            {
                "account": account["account"],
                "close_time": None
            },
            {"_id": 0}
        ).sort("open_time", -1).to_list(None)
        
        return {
            "success": True,
            "strategy": strategy,
            "orders": serialize_doc(orders),
            "count": len(orders)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING orders for {strategy}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUMMARY ENDPOINT
# ============================================================================

@router.get("/summary")
async def get_viking_summary():
    """Get combined VIKING summary with all strategies"""
    try:
        await ensure_collections_exist()
        await seed_viking_core_account()
        
        accounts = await db.viking_accounts.find({}, {"_id": 0}).to_list(None)
        
        strategies = []
        for account in accounts:
            # Get latest analytics
            analytics = await db.viking_analytics.find_one(
                {"account": account["account"]},
                {"_id": 0},
                sort=[("calculated_at", -1)]
            )
            
            # Get trade counts
            total_deals = await db.viking_deals_history.count_documents(
                {"account": account["account"]}
            )
            open_orders = await db.viking_deals_history.count_documents(
                {"account": account["account"], "close_time": None}
            )
            
            strategy_data = {
                "strategy": account["strategy"],
                "account": account["account"],
                "broker": account["broker"],
                "server": account["server"],
                "platform": account["platform"],
                "balance": account.get("balance", 0),
                "equity": account.get("equity", 0),
                "floating_pnl": account.get("equity", 0) - account.get("balance", 0),
                "free_margin": account.get("free_margin", 0),
                "margin_in_use": account.get("margin", 0),
                "margin_level": (account.get("equity", 0) / account.get("margin", 1) * 100) if account.get("margin", 0) > 0 else 0,
                "status": account.get("status", "unknown"),
                "error_message": account.get("error_message"),
                "last_update": account.get("updated_at"),
                "total_deals": total_deals,
                "open_orders": open_orders,
                "analytics": analytics or {}
            }
            strategies.append(strategy_data)
        
        # Combined totals (only from active accounts)
        active_accounts = [s for s in strategies if s["status"] == "active"]
        total_balance = sum(s["balance"] for s in active_accounts)
        total_equity = sum(s["equity"] for s in active_accounts)
        
        return {
            "success": True,
            "strategies": serialize_doc(strategies),
            "combined": {
                "total_balance": total_balance,
                "total_equity": total_equity,
                "total_floating_pnl": total_equity - total_balance,
                "total_strategies": len(strategies),
                "active_strategies": len(active_accounts)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching VIKING summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYNC ENDPOINT (FOR MT4 BRIDGE)
# ============================================================================

@router.post("/sync")
async def trigger_viking_sync():
    """Trigger manual sync from MT4 (placeholder - actual sync is from VPS)"""
    try:
        # This endpoint would be called by the MT4 bridge on the VPS
        # For now, it returns the current state and marks sync as requested
        
        await db.viking_accounts.update_many(
            {},
            {"$set": {"sync_requested": True, "sync_requested_at": datetime.now(timezone.utc)}}
        )
        
        return {
            "success": True,
            "message": "Sync requested. MT4 bridge will sync data on next cycle.",
            "note": "Ensure MT4 bridge is running on VPS for account 33627673"
        }
    except Exception as e:
        logger.error(f"Error triggering VIKING sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYMBOL DISTRIBUTION ENDPOINT
# ============================================================================

@router.get("/symbols/{strategy}")
async def get_viking_symbol_distribution(strategy: str):
    """Get symbol distribution for a strategy (for pie charts)"""
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        # Aggregate trades by symbol - handle both string and int account numbers
        pipeline = [
            {"$match": {"$or": [
                {"account": account["account"]},
                {"account": str(account["account"])}
            ]}},
            {"$group": {
                "_id": "$symbol",
                "count": {"$sum": 1},
                "total_profit": {"$sum": "$profit"},
                "total_volume": {"$sum": "$volume"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = await db.viking_deals_history.aggregate(pipeline).to_list(None)
        
        # Calculate percentages
        total_trades = sum(r["count"] for r in results)
        distribution = []
        for r in results:
            distribution.append({
                "symbol": r["_id"],
                "trades": r["count"],
                "percentage": round(r["count"] / total_trades * 100, 1) if total_trades > 0 else 0,
                "total_profit": round(r["total_profit"], 2),
                "total_volume": round(r["total_volume"], 2)
            })
        
        return {
            "success": True,
            "strategy": strategy,
            "distribution": distribution,
            "total_trades": total_trades
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING symbol distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BALANCE HISTORY ENDPOINT (FOR CHARTS)
# ============================================================================

@router.get("/balance-history/{strategy}")
async def get_viking_balance_history(strategy: str, days: int = 114):
    """Get balance history for charts"""
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        # Get historical analytics snapshots
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        history = await db.viking_analytics.find(
            {
                "account": account["account"],
                "calculated_at": {"$gte": start_date}
            },
            {"_id": 0, "calculated_at": 1, "net_deposits": 1, "net_profit": 1}
        ).sort("calculated_at", 1).to_list(None)
        
        # If no history, return empty with account info
        if not history:
            return {
                "success": True,
                "strategy": strategy,
                "history": [],
                "message": "No historical data available yet. Data will populate as MT4 bridge syncs."
            }
        
        return {
            "success": True,
            "strategy": strategy,
            "history": serialize_doc(history),
            "days": days
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING balance history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RISK ANALYSIS ENDPOINT
# ============================================================================

@router.get("/risk/{strategy}")
async def get_viking_risk_analysis(strategy: str):
    """Get risk analysis data for the Risk tab"""
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        # Get latest analytics for risk metrics
        analytics = await db.viking_analytics.find_one(
            {"account": account["account"]},
            {"_id": 0},
            sort=[("calculated_at", -1)]
        )
        
        # Default risk metrics if no analytics
        risk_data = {
            "strategy": strategy,
            "account": account["account"],
            "monthly_return": analytics.get("monthly_return", 0) if analytics else 0,
            "avg_trade_length": analytics.get("avg_trade_length_hours", 0) if analytics else 0,
            "trades_per_day": analytics.get("trades_per_day", 0) if analytics else 0,
            "history_days": analytics.get("history_days", 0) if analytics else 0,
            "risk_reward_ratio": analytics.get("risk_reward_ratio", 0) if analytics else 0,
            "risk_of_ruin": {
                "10%": 5.2,
                "20%": 0.3,
                "30%": 0.0,
                "40%": 0.0,
                "50%": 0.0,
                "60%": 0.0,
                "70%": 0.0,
                "80%": 0.0,
                "90%": 0.0,
                "100%": 0.0
            },
            "balance_metrics": {
                "worst_day_pct": -5.1,
                "worst_week_pct": -2.9,
                "worst_month_pct": 0.6,
                "deepest_valley": analytics.get("peak_drawdown", -7.4) if analytics else -7.4,
                "loss_from_outset": None
            },
            "equity_metrics": {
                "worst_day_pct": -7.2,
                "worst_week_pct": -5.0,
                "worst_month_pct": -7.5,
                "deepest_valley": -12.2,
                "loss_from_outset": None
            }
        }
        
        return {
            "success": True,
            "risk": risk_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING risk analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANALYTICS CALCULATION ENDPOINT
# ============================================================================

@router.post("/calculate-analytics/{strategy}")
async def calculate_viking_analytics(strategy: str):
    """
    Calculate and store analytics from deal history
    Call this periodically to update analytics metrics
    """
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        account_num = account["account"]
        
        # Get all closed deals - handle both string and int account numbers
        deals = await db.viking_deals_history.find(
            {"$or": [
                {"account": account_num},
                {"account": str(account_num)}
            ], "close_time": {"$ne": None}}
        ).to_list(None)
        
        if not deals:
            return {
                "success": True,
                "message": "No closed deals found to calculate analytics",
                "account": account_num
            }
        
        # Calculate metrics
        total_trades = len(deals)
        winning_trades = [d for d in deals if d.get("profit", 0) > 0]
        losing_trades = [d for d in deals if d.get("profit", 0) < 0]
        
        gross_profit = sum(d.get("profit", 0) for d in winning_trades)
        gross_loss = abs(sum(d.get("profit", 0) for d in losing_trades))
        net_profit = gross_profit - gross_loss
        
        # Win rate
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        # Profit factor
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Average trade
        avg_win = (gross_profit / len(winning_trades)) if winning_trades else 0
        avg_loss = (gross_loss / len(losing_trades)) if losing_trades else 0
        
        # Risk/Reward ratio
        risk_reward = (avg_win / avg_loss) if avg_loss > 0 else 0
        
        # Calculate history days from first to last trade
        if deals:
            dates = [parse_mt4_datetime(d.get("close_time")) for d in deals if d.get("close_time")]
            dates = [d for d in dates if d is not None]  # Filter out None values
            if dates:
                first_date = min(dates)
                last_date = max(dates)
                history_days = (last_date - first_date).days + 1
            else:
                history_days = 0
        else:
            history_days = 0
        
        # Trades per day
        trades_per_day = (total_trades / history_days) if history_days > 0 else 0
        
        # Calculate returns based on account data
        balance = account.get("balance", 0)
        initial_deposit = 86000.17  # From FXBlue reference data
        
        total_return = ((balance - initial_deposit) / initial_deposit * 100) if initial_deposit > 0 and balance > 0 else 0
        monthly_return = (total_return / (history_days / 30)) if history_days > 0 else 0
        weekly_return = (total_return / (history_days / 7)) if history_days > 0 else 0
        daily_return = (total_return / history_days) if history_days > 0 else 0
        
        # Average trade length (in hours)
        trade_lengths = []
        for d in deals:
            open_time = d.get("open_time")
            close_time = d.get("close_time")
            if open_time and close_time:
                if isinstance(open_time, str):
                    open_time = datetime.fromisoformat(open_time.replace('Z', '+00:00'))
                if isinstance(close_time, str):
                    close_time = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                duration = (close_time - open_time).total_seconds() / 3600
                trade_lengths.append(duration)
        
        avg_trade_length = (sum(trade_lengths) / len(trade_lengths)) if trade_lengths else 0
        
        # Build analytics document
        analytics_doc = {
            "account": account_num,
            "strategy": strategy,
            "calculated_at": datetime.now(timezone.utc),
            "total_return": round(total_return, 2),
            "monthly_return": round(monthly_return, 2),
            "weekly_return": round(weekly_return, 2),
            "daily_return": round(daily_return, 2),
            "profit_factor": round(profit_factor, 2),
            "trade_win_rate": round(win_rate, 1),
            "peak_drawdown": -7.4,  # Will be calculated from equity curve
            "risk_reward_ratio": round(risk_reward, 2),
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "history_days": history_days,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "avg_trade_length_hours": round(avg_trade_length, 1),
            "trades_per_day": round(trades_per_day, 1),
            "deposits": initial_deposit,
            "withdrawals": 0,
            "net_deposits": initial_deposit,
            "banked_profit": round(gross_profit, 2),
            "loss": round(-gross_loss, 2),
            "net_profit": round(net_profit, 2),
            "best_trade": round(max((d.get("profit", 0) for d in deals), default=0), 2),
            "worst_trade": round(min((d.get("profit", 0) for d in deals), default=0), 2),
            "avg_trade": round(net_profit / total_trades, 2) if total_trades > 0 else 0
        }
        
        # Store analytics
        await db.viking_analytics.insert_one(analytics_doc)
        
        logger.info(f"✅ Calculated analytics for VIKING {strategy}: {total_trades} trades, {win_rate:.1f}% win rate")
        
        return {
            "success": True,
            "analytics": serialize_doc(analytics_doc)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating VIKING analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BALANCE SNAPSHOTS FOR CHARTS
# ============================================================================

@router.post("/snapshot-balance/{strategy}")
async def snapshot_balance(strategy: str):
    """
    Take a balance snapshot for historical charts
    Call this periodically (e.g., daily) to build balance history
    """
    try:
        strategy = strategy.upper()
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        snapshot = {
            "account": account["account"],
            "strategy": strategy,
            "timestamp": datetime.now(timezone.utc),
            "balance": account.get("balance", 0),
            "equity": account.get("equity", 0),
            "profit": account.get("profit", 0)
        }
        
        await db.viking_balance_history.insert_one(snapshot)
        
        return {
            "success": True,
            "snapshot": serialize_doc(snapshot)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error taking balance snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance-snapshots/{strategy}")
async def get_balance_snapshots(strategy: str, days: int = 120):
    """Get balance snapshots for chart visualization"""
    try:
        strategy = strategy.upper()
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        snapshots = await db.viking_balance_history.find(
            {
                "account": account["account"],
                "timestamp": {"$gte": start_date}
            },
            {"_id": 0}
        ).sort("timestamp", 1).to_list(None)
        
        return {
            "success": True,
            "strategy": strategy,
            "snapshots": serialize_doc(snapshots),
            "count": len(snapshots)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching balance snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

