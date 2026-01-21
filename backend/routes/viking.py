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
    """
    Seed VIKING accounts:
    - CORE: MT5 #885822 (MexAtlantic) - Active from Jan 20th 2026
    - CORE Legacy: MT4 #33627673 - Archived (historical data preserved)
    - PRO: MT4 #1309411 (Traders Trust)
    
    Uses update_one with upsert to avoid duplicate key errors from _id conflicts
    """
    if db is None:
        return
    
    try:
        now = datetime.now(timezone.utc)
        
        # ========== NEW CORE ACCOUNT: MT5 #885822 ==========
        existing_new_core = await db.viking_accounts.find_one({"account": 885822})
        if not existing_new_core:
            # Pull latest data from mt5_accounts (FIDUS data source)
            mt5_data = await db.mt5_accounts.find_one({"account": 885822})
            
            viking_core_new = {
                "account": 885822,
                "strategy": "CORE",
                "broker": "MexAtlantic",
                "server": "MexAtlantic-MT5",
                "platform": "MT5",
                "balance": mt5_data.get("balance", 0.0) if mt5_data else 0.0,
                "equity": mt5_data.get("equity", 0.0) if mt5_data else 0.0,
                "margin": mt5_data.get("margin", 0.0) if mt5_data else 0.0,
                "free_margin": mt5_data.get("margin_free", 0.0) if mt5_data else 0.0,
                "profit": mt5_data.get("profit", 0.0) if mt5_data else 0.0,
                "currency": mt5_data.get("currency", "USD") if mt5_data else "USD",
                "leverage": mt5_data.get("leverage", 500) if mt5_data else 500,
                "status": "active",
                "error_message": None,
                "replaces_account": 33627673,
                "migration_date": "2026-01-20",
                "updated_at": now
            }
            await db.viking_accounts.update_one(
                {"account": 885822},
                {"$set": viking_core_new, "$setOnInsert": {"created_at": now}},
                upsert=True
            )
            logger.info("✅ Seeded VIKING CORE account 885822 (MT5 - Active)")
        
        # ========== ARCHIVED CORE ACCOUNT: MT4 #33627673 ==========
        existing_old_core = await db.viking_accounts.find_one({"account": 33627673})
        if existing_old_core:
            # Ensure it stays archived - do NOT overwrite if VPS sync changed it
            if existing_old_core.get("status") != "archived":
                await db.viking_accounts.update_one(
                    {"account": 33627673},
                    {"$set": {
                        "strategy": "CORE_LEGACY",
                        "status": "archived",
                        "replaced_by": 885822,
                        "archive_date": "2026-01-20",
                        "error_message": "Archived - Replaced by MT5 #885822 on 2026-01-20",
                        "updated_at": now
                    }}
                )
                logger.info("✅ Re-archived VIKING CORE 33627673 (MT4)")
        else:
            # Create archived record if it doesn't exist
            viking_core_archived = {
                "account": 33627673,
                "strategy": "CORE_LEGACY",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real-2",
                "platform": "MT4",
                "balance": 25250.98,
                "equity": 22074.71,
                "margin": 0.0,
                "free_margin": 22074.71,
                "profit": -3176.27,
                "currency": "USD",
                "leverage": 500,
                "status": "archived",
                "error_message": "Archived - Replaced by MT5 #885822 on 2026-01-20",
                "replaced_by": 885822,
                "archive_date": "2026-01-20",
                "updated_at": now
            }
            await db.viking_accounts.update_one(
                {"account": 33627673},
                {"$set": viking_core_archived, "$setOnInsert": {"created_at": now}},
                upsert=True
            )
            logger.info("✅ Seeded VIKING CORE LEGACY account 33627673 (MT4 - Archived)")
        
        # ========== PRO ACCOUNT: MT4 #1309411 ==========
        existing_pro = await db.viking_accounts.find_one({"account": 1309411})
        if not existing_pro:
            viking_pro = {
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
                "updated_at": now
            }
            await db.viking_accounts.update_one(
                {"account": 1309411},
                {"$set": viking_pro, "$setOnInsert": {"created_at": now}},
                upsert=True
            )
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
        all_accounts = await db.viking_accounts.find({}, {"_id": 0}).to_list(length=100)
        
        # Separate active and archived accounts
        active_accounts = []
        archived_accounts = []
        
        for account in all_accounts:
            # Get latest analytics for each account
            analytics = await db.viking_analytics.find_one(
                {"account": account["account"]},
                {"_id": 0},
                sort=[("calculated_at", -1)]
            )
            account["analytics"] = analytics or {}
            
            if account.get("status") == "archived":
                archived_accounts.append(account)
            else:
                active_accounts.append(account)
        
        # Calculate combined totals (only from active accounts)
        total_balance = sum(a.get("balance", 0) for a in active_accounts)
        total_equity = sum(a.get("equity", 0) for a in active_accounts)
        
        return {
            "success": True,
            "strategies": serialize_doc(active_accounts),
            "archived_strategies": serialize_doc(archived_accounts),
            "combined": {
                "total_balance": total_balance,
                "total_equity": total_equity,
                "total_strategies": len(active_accounts),
                "active_strategies": len(active_accounts),
                "archived_count": len(archived_accounts)
            }
        }
    except Exception as e:
        logger.error(f"Error fetching VIKING accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
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
        # Check if account is archived - don't allow updates to archived accounts
        existing = await db.viking_accounts.find_one({"account": account_number}, {"status": 1})
        if existing and existing.get("status") == "archived":
            logger.warning(f"Rejected update for archived VIKING account {account_number}")
            return {
                "success": False,
                "message": f"Account {account_number} is archived and cannot be updated",
                "account_number": account_number
            }
        
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
        
        # Get ACTIVE account for this strategy (not archived/legacy)
        account = await db.viking_accounts.find_one(
            {"strategy": strategy, "status": {"$ne": "archived"}}, 
            {"_id": 0}
        )
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
        
        # Get ACTIVE account for this strategy (not archived)
        account = await db.viking_accounts.find_one(
            {"strategy": strategy, "status": {"$ne": "archived"}}, 
            {"_id": 0}
        )
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        platform = account.get("platform", "MT4")
        account_num = account["account"]
        
        # Choose collection based on platform
        if platform == "MT5":
            # For MT5 accounts, use mt5_deals collection with 'login' field
            query = {"$or": [
                {"login": account_num},
                {"login": str(account_num)}
            ]}
            if symbol:
                query["symbol"] = {"$regex": symbol, "$options": "i"}
            
            deals = await db.mt5_deals.find(
                query,
                {"_id": 0}
            ).sort("time", -1).skip(skip).limit(limit).to_list(None)
            
            total = await db.mt5_deals.count_documents(query)
        else:
            # For MT4 accounts, use viking_deals_history with 'account' field
            query = {"$or": [
                {"account": account_num},
                {"account": str(account_num)}
            ]}
            if symbol:
                query["symbol"] = {"$regex": symbol, "$options": "i"}
            
            deals = await db.viking_deals_history.find(
                query,
                {"_id": 0}
            ).sort("close_time", -1).skip(skip).limit(limit).to_list(None)
            
            total = await db.viking_deals_history.count_documents(query)
        
        return {
            "success": True,
            "strategy": strategy,
            "account": account_num,
            "platform": platform,
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
        
        # Get ACTIVE account for this strategy
        account = await db.viking_accounts.find_one(
            {"strategy": strategy, "status": {"$ne": "archived"}}, 
            {"_id": 0}
        )
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        platform = account.get("platform", "MT4")
        account_num = account["account"]
        
        # Open orders have no close_time
        if platform == "MT5":
            # For MT5, open positions would be in a different structure
            # Return positions from the account data if available
            orders = account.get("positions", [])
        else:
            orders = await db.viking_deals_history.find(
                {
                    "account": account_num,
                    "close_time": None
                },
                {"_id": 0}
            ).sort("open_time", -1).to_list(None)
        
        return {
            "success": True,
            "strategy": strategy,
            "account": account_num,
            "platform": platform,
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
        
        # Get all accounts but filter archived ones from main display
        accounts = await db.viking_accounts.find({}, {"_id": 0}).to_list(None)
        
        strategies = []
        archived_strategies = []
        
        for account in accounts:
            platform = account.get("platform", "MT4")
            account_num = account["account"]
            is_archived = account.get("status") == "archived"
            
            # Get latest analytics
            analytics = await db.viking_analytics.find_one(
                {"account": account_num},
                {"_id": 0},
                sort=[("calculated_at", -1)]
            )
            
            # Get trade counts based on platform
            if platform == "MT5":
                total_deals = await db.mt5_deals.count_documents(
                    {"$or": [{"login": account_num}, {"login": str(account_num)}]}
                )
                open_orders = 0  # MT5 open orders come from account data
            else:
                total_deals = await db.viking_deals_history.count_documents(
                    {"$or": [
                        {"account": account_num},
                        {"account": str(account_num)}
                    ]}
                )
                open_orders = await db.viking_deals_history.count_documents(
                    {"$or": [
                        {"account": account_num},
                        {"account": str(account_num)}
                    ], "close_time": None}
                )
            
            strategy_data = {
                "strategy": account["strategy"],
                "account": account_num,
                "broker": account.get("broker", "Unknown"),
                "server": account.get("server", ""),
                "platform": platform,
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
            
            if is_archived:
                strategy_data["archived_date"] = account.get("archive_date")
                strategy_data["replaced_by"] = account.get("replaced_by")
                archived_strategies.append(strategy_data)
            else:
                strategies.append(strategy_data)
        
        # Combined totals (only from active accounts)
        active_accounts = [s for s in strategies if s["status"] == "active"]
        total_balance = sum(s["balance"] for s in active_accounts)
        total_equity = sum(s["equity"] for s in active_accounts)
        
        return {
            "success": True,
            "strategies": serialize_doc(strategies),
            "archived_strategies": serialize_doc(archived_strategies),
            "combined": {
                "total_balance": total_balance,
                "total_equity": total_equity,
                "total_floating_pnl": total_equity - total_balance,
                "total_strategies": len(strategies),
                "active_strategies": len(active_accounts),
                "archived_count": len(archived_strategies)
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
    """Sync VIKING accounts data from their respective sources"""
    try:
        results = []
        
        # Sync MT5 CORE account (885822) from FIDUS mt5_accounts
        mt5_core = await db.mt5_accounts.find_one({"account": 885822})
        if mt5_core:
            update_result = await db.viking_accounts.update_one(
                {"account": 885822},
                {"$set": {
                    "balance": mt5_core.get("balance", 0.0),
                    "equity": mt5_core.get("equity", 0.0),
                    "margin": mt5_core.get("margin", 0.0),
                    "free_margin": mt5_core.get("margin_free", 0.0),
                    "profit": mt5_core.get("profit", 0.0),
                    "leverage": mt5_core.get("leverage", 500),
                    "updated_at": datetime.now(timezone.utc),
                    "last_sync_source": "mt5_accounts",
                    "status": "active"
                }}
            )
            results.append({
                "account": 885822,
                "platform": "MT5",
                "synced": update_result.modified_count > 0 or update_result.matched_count > 0,
                "balance": mt5_core.get("balance", 0.0)
            })
        
        # Mark sync requested for MT4 accounts (PRO)
        await db.viking_accounts.update_many(
            {"platform": "MT4", "status": {"$ne": "archived"}},
            {"$set": {"sync_requested": True, "sync_requested_at": datetime.now(timezone.utc)}}
        )
        
        return {
            "success": True,
            "message": "Sync completed for MT5 accounts. MT4 sync requested via VPS bridge.",
            "results": results,
            "note": "MT5 CORE (885822) synced from FIDUS data. MT4 PRO requires VPS bridge."
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
        
        # Get ACTIVE account for this strategy
        account = await db.viking_accounts.find_one(
            {"strategy": strategy, "status": {"$ne": "archived"}}, 
            {"_id": 0}
        )
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        platform = account.get("platform", "MT4")
        account_num = account["account"]
        
        # Choose collection and field based on platform
        if platform == "MT5":
            pipeline = [
                {"$match": {"$or": [
                    {"login": account_num},
                    {"login": str(account_num)}
                ]}},
                {"$group": {
                    "_id": "$symbol",
                    "count": {"$sum": 1},
                    "total_profit": {"$sum": "$profit"},
                    "total_volume": {"$sum": "$volume"}
                }},
                {"$sort": {"count": -1}}
            ]
            results = await db.mt5_deals.aggregate(pipeline).to_list(None)
        else:
            pipeline = [
                {"$match": {"$or": [
                    {"account": account_num},
                    {"account": str(account_num)}
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
            "account": account_num,
            "platform": platform,
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
        
        # Get ACTIVE account for this strategy
        account = await db.viking_accounts.find_one(
            {"strategy": strategy, "status": {"$ne": "archived"}}, 
            {"_id": 0}
        )
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
        
        # Get ACTIVE account for this strategy
        account = await db.viking_accounts.find_one(
            {"strategy": strategy, "status": {"$ne": "archived"}}, 
            {"_id": 0}
        )
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
    
    IMPORTANT: Separates trading P&L from deposits/withdrawals
    """
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        account_num = account["account"]
        
        # Get all records - handle both string and int account numbers
        all_records = await db.viking_deals_history.find(
            {"$or": [
                {"account": account_num},
                {"account": str(account_num)}
            ], "close_time": {"$ne": None}}
        ).to_list(None)
        
        if not all_records:
            return {
                "success": True,
                "message": "No records found to calculate analytics",
                "account": account_num
            }
        
        # Separate trades from balance operations
        trades = []
        total_deposits = 0
        total_withdrawals = 0
        
        for record in all_records:
            record_type = record.get("type", "").upper()
            is_balance_op = record.get("is_balance_operation", False)
            symbol = record.get("symbol")
            
            if is_balance_op or record_type in ["DEPOSIT", "WITHDRAWAL"] or (symbol is None and record_type not in ["BUY", "SELL"]):
                amount = float(record.get("profit", 0))
                if amount >= 0 or record_type == "DEPOSIT":
                    total_deposits += amount
                else:
                    total_withdrawals += abs(amount)
            else:
                trades.append(record)
        
        if not trades:
            return {
                "success": True,
                "message": "No actual trades found to calculate analytics (only balance operations)",
                "account": account_num,
                "deposits": total_deposits,
                "withdrawals": total_withdrawals
            }
        
        # Calculate metrics from TRADES ONLY
        total_trades = len(trades)
        winning_trades = [d for d in trades if d.get("profit", 0) > 0]
        losing_trades = [d for d in trades if d.get("profit", 0) < 0]
        
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
        dates = [parse_mt4_datetime(d.get("close_time")) for d in trades if d.get("close_time")]
        dates = [d for d in dates if d is not None]
        if dates:
            first_date = min(dates)
            last_date = max(dates)
            history_days = (last_date - first_date).days + 1
        else:
            history_days = 0
        
        # Trades per day
        trades_per_day = (total_trades / history_days) if history_days > 0 else 0
        
        # Calculate returns based on deposits (actual capital invested)
        initial_deposit = total_deposits if total_deposits > 0 else 10000
        
        # Calculate returns as percentage gain on invested capital
        total_return = (net_profit / initial_deposit * 100) if initial_deposit > 0 else 0
        monthly_return = (total_return / max(history_days / 30, 1)) if history_days > 0 else 0
        weekly_return = (total_return / max(history_days / 7, 1)) if history_days > 0 else 0
        daily_return = (total_return / history_days) if history_days > 0 else 0
        
        # Average trade length (in hours)
        trade_lengths = []
        for d in trades:
            open_time = parse_mt4_datetime(d.get("open_time"))
            close_time = parse_mt4_datetime(d.get("close_time"))
            if open_time and close_time:
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
            "deposits": round(total_deposits, 2),
            "withdrawals": round(total_withdrawals, 2),
            "net_deposits": round(total_deposits - total_withdrawals, 2),
            "banked_profit": round(gross_profit, 2),
            "loss": round(-gross_loss, 2),
            "net_profit": round(net_profit, 2),
            "best_trade": round(max((d.get("profit", 0) for d in trades), default=0), 2),
            "worst_trade": round(min((d.get("profit", 0) for d in trades), default=0), 2),
            "avg_trade": round(net_profit / total_trades, 2) if total_trades > 0 else 0
        }
        
        # Store analytics
        await db.viking_analytics.insert_one(analytics_doc)
        
        logger.info(f"✅ Calculated analytics for VIKING {strategy}: {total_trades} trades, {win_rate:.1f}% win rate, deposits=${total_deposits:,.2f}")
        
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
# MONTHLY RETURNS ANALYTICS
# ============================================================================

@router.get("/monthly-returns/{strategy}")
async def get_monthly_returns(strategy: str):
    """
    Calculate monthly returns for a strategy
    Returns data for the Monthly Returns bar chart
    
    IMPORTANT: Excludes deposits/withdrawals from profit calculations
    Monthly Return % = Trading Profit / Starting Balance × 100
    Where Trading Profit = Sum of actual trade profits (not deposits/withdrawals)
    """
    try:
        strategy = strategy.upper()
        if strategy not in ["CORE", "PRO"]:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account = await db.viking_accounts.find_one({"strategy": strategy}, {"_id": 0})
        if not account:
            raise HTTPException(status_code=404, detail=f"Strategy {strategy} not found")
        
        account_num = str(account["account"])
        current_balance = float(account.get("balance", 0))
        
        # Get all records from deal history (trades AND balance operations)
        all_records = await db.viking_deals_history.find(
            {"$or": [
                {"account": account_num},
                {"account": int(account_num) if account_num.isdigit() else account_num}
            ], "close_time": {"$ne": None}},
            {"_id": 0, "close_time": 1, "profit": 1, "commission": 1, "swap": 1, 
             "type": 1, "is_balance_operation": 1, "symbol": 1}
        ).sort("close_time", 1).to_list(None)
        
        if not all_records:
            return {
                "success": True,
                "strategy": strategy,
                "account": account_num,
                "metrics": {
                    "avgWeekly": 0,
                    "avgMonthly": 0,
                    "devDaily": 0,
                    "devMonthly": 0,
                    "devYearly": 0
                },
                "data": [],
                "deposits_info": {
                    "total_deposits": 0,
                    "total_withdrawals": 0,
                    "net_deposits": 0
                }
            }
        
        # Separate trades from balance operations
        trades = []
        deposits = []
        withdrawals = []
        
        for record in all_records:
            record_type = record.get("type", "").upper()
            is_balance_op = record.get("is_balance_operation", False)
            symbol = record.get("symbol")
            
            # Identify balance operations by:
            # 1. Explicit is_balance_operation flag
            # 2. Type is DEPOSIT or WITHDRAWAL
            # 3. No symbol (balance operations don't have symbols)
            if is_balance_op or record_type in ["DEPOSIT", "WITHDRAWAL"] or (symbol is None and record_type not in ["BUY", "SELL"]):
                amount = float(record.get("profit", 0))
                if amount >= 0 or record_type == "DEPOSIT":
                    deposits.append(record)
                else:
                    withdrawals.append(record)
            else:
                trades.append(record)
        
        # Calculate total deposits and withdrawals
        total_deposits = sum(float(d.get("profit", 0)) for d in deposits)
        total_withdrawals = abs(sum(float(w.get("profit", 0)) for w in withdrawals))
        net_deposits = total_deposits - total_withdrawals
        
        logger.info(f"[{strategy}] Found {len(trades)} trades, {len(deposits)} deposits (${total_deposits:,.2f}), {len(withdrawals)} withdrawals (${total_withdrawals:,.2f})")
        
        # If no actual trades, return empty
        if not trades:
            return {
                "success": True,
                "strategy": strategy,
                "account": account_num,
                "metrics": {
                    "avgWeekly": 0,
                    "avgMonthly": 0,
                    "devDaily": 0,
                    "devMonthly": 0,
                    "devYearly": 0
                },
                "data": [],
                "deposits_info": {
                    "total_deposits": round(total_deposits, 2),
                    "total_withdrawals": round(total_withdrawals, 2),
                    "net_deposits": round(net_deposits, 2)
                }
            }
        
        # Group TRADES ONLY by month (exclude balance operations)
        monthly_profits = {}
        daily_profits = {}
        weekly_profits = {}
        
        for deal in trades:
            close_time = deal.get("close_time")
            # Only count actual trading P&L
            profit = float(deal.get("profit", 0)) + float(deal.get("commission", 0)) + float(deal.get("swap", 0))
            
            if close_time:
                # Parse date
                if isinstance(close_time, str):
                    try:
                        if '.' in close_time:
                            dt = datetime.strptime(close_time[:10], "%Y.%m.%d")
                        else:
                            dt = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                    except:
                        continue
                elif isinstance(close_time, datetime):
                    dt = close_time
                else:
                    continue
                
                # Group by month (YYYY-MM)
                month_key = dt.strftime("%Y-%m")
                if month_key not in monthly_profits:
                    monthly_profits[month_key] = 0
                monthly_profits[month_key] += profit
                
                # Group by day
                day_key = dt.strftime("%Y-%m-%d")
                if day_key not in daily_profits:
                    daily_profits[day_key] = 0
                daily_profits[day_key] += profit
                
                # Group by week
                week_key = dt.strftime("%Y-W%W")
                if week_key not in weekly_profits:
                    weekly_profits[week_key] = 0
                weekly_profits[week_key] += profit
        
        # Calculate total TRADING profit (excludes deposits/withdrawals)
        total_trading_profit = sum(monthly_profits.values())
        
        # Calculate initial balance:
        # current_balance = initial_deposit + trading_profit + net_deposits
        # So: initial_deposit = current_balance - trading_profit - (deposits - withdrawals)
        # But actually the simplest: initial balance is total deposits
        # since withdrawals reduce balance but not the base we're measuring from
        initial_balance = total_deposits if total_deposits > 0 else 10000
        
        logger.info(f"[{strategy}] Total trading profit: ${total_trading_profit:,.2f}, Initial balance (from deposits): ${initial_balance:,.2f}")
        
        # Calculate monthly returns as percentages
        monthly_returns = []
        sorted_months = sorted(monthly_profits.keys())
        
        for month in sorted_months:
            profit = monthly_profits[month]
            # Calculate return as % of initial deposits (the actual capital invested)
            return_pct = (profit / initial_balance) * 100 if initial_balance > 0 else 0
            
            # Format month label (e.g., "Nov'24")
            try:
                dt = datetime.strptime(month, "%Y-%m")
                month_label = dt.strftime("%b'%y")
            except:
                month_label = month
            
            monthly_returns.append({
                "month": month_label,
                "monthKey": month,
                "return": round(return_pct, 2),
                "profit": round(profit, 2)
            })
        
        # Calculate weekly returns
        weekly_returns_list = []
        for week in sorted(weekly_profits.keys()):
            profit = weekly_profits[week]
            return_pct = (profit / initial_balance) * 100 if initial_balance > 0 else 0
            weekly_returns_list.append(return_pct)
        
        # Calculate daily returns
        daily_returns_list = []
        for day in sorted(daily_profits.keys()):
            profit = daily_profits[day]
            return_pct = (profit / initial_balance) * 100 if initial_balance > 0 else 0
            daily_returns_list.append(return_pct)
        
        # Calculate standard deviations
        import statistics
        
        monthly_return_values = [m["return"] for m in monthly_returns]
        
        avg_weekly = statistics.mean(weekly_returns_list) if weekly_returns_list else 0
        avg_monthly = statistics.mean(monthly_return_values) if monthly_return_values else 0
        
        dev_daily = statistics.stdev(daily_returns_list) if len(daily_returns_list) > 1 else 0
        dev_monthly = statistics.stdev(monthly_return_values) if len(monthly_return_values) > 1 else 0
        
        # Yearly deviation - estimate from monthly
        dev_yearly = dev_monthly * (12 ** 0.5) if dev_monthly > 0 else 0
        
        return {
            "success": True,
            "strategy": strategy,
            "account": account_num,
            "metrics": {
                "avgWeekly": round(avg_weekly, 2),
                "avgMonthly": round(avg_monthly, 2),
                "devDaily": round(dev_daily, 2),
                "devMonthly": round(dev_monthly, 2),
                "devYearly": round(dev_yearly, 2)
            },
            "data": monthly_returns,
            "deposits_info": {
                "total_deposits": round(total_deposits, 2),
                "total_withdrawals": round(total_withdrawals, 2),
                "net_deposits": round(net_deposits, 2),
                "total_trading_profit": round(total_trading_profit, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating monthly returns: {e}")
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
        
        account_num = str(account["account"])
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Try to get actual balance snapshots first
        snapshots = await db.viking_balance_history.find(
            {
                "$or": [{"account": account_num}, {"account": int(account_num) if account_num.isdigit() else account_num}],
                "timestamp": {"$gte": start_date}
            },
            {"_id": 0}
        ).sort("timestamp", 1).to_list(None)
        
        # If no snapshots, reconstruct from deals history
        if not snapshots:
            logger.info(f"No balance snapshots for {strategy}, reconstructing from deals...")
            
            # Get all closed deals sorted by close time
            deals = await db.viking_deals_history.find(
                {"$or": [{"account": account_num}, {"account": int(account_num) if account_num.isdigit() else account_num}]},
                {"_id": 0, "close_time": 1, "profit": 1, "commission": 1, "swap": 1}
            ).sort("close_time", 1).to_list(None)
            
            if deals:
                current_balance = float(account.get("balance", 0))
                
                # Calculate total profit from all deals
                total_profit = sum(
                    float(d.get("profit", 0)) + float(d.get("commission", 0)) + float(d.get("swap", 0))
                    for d in deals
                )
                
                # Estimate starting balance (current - total profit)
                starting_balance = current_balance - total_profit
                
                # Build balance history from deals
                running_balance = starting_balance
                snapshots = []
                
                for deal in deals:
                    deal_profit = float(deal.get("profit", 0)) + float(deal.get("commission", 0)) + float(deal.get("swap", 0))
                    running_balance += deal_profit
                    
                    close_time = deal.get("close_time")
                    if close_time:
                        # Handle different date formats
                        if isinstance(close_time, str):
                            try:
                                close_time = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                            except:
                                try:
                                    close_time = datetime.strptime(close_time, "%Y.%m.%d %H:%M:%S")
                                except:
                                    continue
                        
                        snapshots.append({
                            "account": account_num,
                            "strategy": strategy,
                            "balance": round(running_balance, 2),
                            "equity": round(running_balance, 2),
                            "timestamp": close_time.isoformat() if hasattr(close_time, 'isoformat') else str(close_time)
                        })
                
                # Add current balance as final point
                snapshots.append({
                    "account": account_num,
                    "strategy": strategy,
                    "balance": current_balance,
                    "equity": float(account.get("equity", current_balance)),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
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

