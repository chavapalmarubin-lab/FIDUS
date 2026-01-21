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
# VIKING ACCOUNT CONFIGURATION
# CORE strategy has historical continuity: MT4 33627673 (pre-Jan 20) + MT5 885822 (Jan 20+)
# ============================================================================

# VIKING strategies map to specific accounts
VIKING_ACCOUNTS = {
    "CORE": {
        "current_account": 885822,  # Active MT5 account from Jan 20, 2026
        "historical_account": 33627673,  # Archived MT4 account (pre-Jan 20)
        "platform": "MT5",
        "broker": "MEXAtlantic", 
        "description": "VIKING CORE Strategy - Full History",
        "migration_date": "2026-01-20",
        "primary_collection": "mt5_accounts"
    },
    "PRO": {
        "current_account": 1309411,
        "historical_account": None,  # No historical account
        "platform": "MT4",
        "broker": "Traders Trust",
        "description": "VIKING PRO Strategy",
        "primary_collection": "mt5_accounts",
        "fallback_collection": "viking_accounts"
    }
}


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


async def get_viking_account_data(strategy: str):
    """
    Get VIKING account data with full historical context
    For CORE: Returns current MT5 data but tracks both current and historical accounts
    """
    if strategy not in VIKING_ACCOUNTS:
        return None
    
    config = VIKING_ACCOUNTS[strategy]
    current_account = config["current_account"]
    
    # Try primary collection first (mt5_accounts)
    account = await db.mt5_accounts.find_one(
        {"account": current_account},
        {"_id": 0}
    )
    source = "mt5_accounts"
    
    # Fall back to viking_accounts if not found
    if not account and config.get("fallback_collection"):
        account = await db.viking_accounts.find_one(
            {"account": current_account},
            {"_id": 0}
        )
        source = "viking_accounts"
    
    if account:
        account["strategy"] = strategy
        account["viking_broker"] = config["broker"]
        account["viking_description"] = config["description"]
        account["data_source"] = source
        account["current_account"] = current_account
        account["historical_account"] = config.get("historical_account")
        
        # Normalize field names
        if "margin_free" in account and "free_margin" not in account:
            account["free_margin"] = account["margin_free"]
    
    return account


async def get_core_combined_deals_count():
    """Get total deals count for CORE strategy (MT4 + MT5 combined)"""
    config = VIKING_ACCOUNTS["CORE"]
    current = config["current_account"]
    historical = config["historical_account"]
    
    # Count MT5 deals (current account)
    mt5_count = await db.mt5_deals.count_documents(
        {"$or": [{"login": current}, {"login": str(current)}]}
    )
    
    # Count MT4 deals (historical account) from viking_deals_history
    mt4_count = await db.viking_deals_history.count_documents(
        {"$or": [{"account": historical}, {"account": str(historical)}]}
    )
    
    return mt5_count + mt4_count


# ============================================================================
# ACCOUNT ENDPOINTS
# Using SSOT pattern - query from mt5_accounts (shared with FIDUS)
# ============================================================================

@router.get("/accounts")
async def get_viking_accounts():
    """
    Get VIKING accounts data
    Uses SSOT pattern - tries mt5_accounts first, falls back to viking_accounts for MT4
    """
    try:
        strategies = []
        
        # Get data for each VIKING strategy
        for strategy_name, config in VIKING_ACCOUNTS.items():
            account_data = await get_viking_account_data(strategy_name)
            
            if account_data:
                # Build VIKING strategy view
                strategy_data = {
                    "strategy": strategy_name,
                    "account": config["account"],
                    "platform": config["platform"],
                    "broker": config["broker"],
                    "description": config["description"],
                    "balance": account_data.get("balance", 0),
                    "equity": account_data.get("equity", 0),
                    "margin": account_data.get("margin", 0),
                    "free_margin": account_data.get("margin_free") or account_data.get("free_margin", 0),
                    "profit": account_data.get("profit", 0),
                    "leverage": account_data.get("leverage", 0),
                    "currency": account_data.get("currency", "USD"),
                    "status": account_data.get("status", "active"),
                    "last_sync": account_data.get("last_sync_timestamp") or account_data.get("updated_at") or account_data.get("last_sync"),
                    "open_positions": account_data.get("open_positions") or account_data.get("positions", []),
                    "open_positions_count": account_data.get("open_positions_count", 0),
                    "data_source": account_data.get("data_source", "unknown")
                }
                
                # Get analytics if available
                analytics = await db.viking_analytics.find_one(
                    {"account": config["account"]},
                    {"_id": 0},
                    sort=[("calculated_at", -1)]
                )
                strategy_data["analytics"] = analytics or {}
                
                strategies.append(strategy_data)
        
        # Calculate combined totals
        total_balance = sum(s.get("balance", 0) for s in strategies)
        total_equity = sum(s.get("equity", 0) for s in strategies)
        
        return {
            "success": True,
            "strategies": serialize_doc(strategies),
            "combined": {
                "total_balance": total_balance,
                "total_equity": total_equity,
                "total_strategies": len(strategies),
                "active_strategies": len(strategies)
            },
            "note": "Data from mt5_accounts (SSOT) with fallback to viking_accounts for MT4"
        }
    except Exception as e:
        logger.error(f"Error fetching VIKING accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/{account_number}")
async def get_viking_account(account_number: int):
    """Get specific VIKING account by account number from mt5_accounts (SSOT)"""
    try:
        # Verify this is a VIKING account
        strategy_name = None
        for name, config in VIKING_ACCOUNTS.items():
            if config["account"] == account_number:
                strategy_name = name
                break
        
        if not strategy_name:
            raise HTTPException(status_code=404, detail=f"Account {account_number} is not a VIKING account")
        
        # Query from mt5_accounts (SSOT)
        account = await db.mt5_accounts.find_one(
            {"account": account_number},
            {"_id": 0}
        )
        
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {account_number} not found in mt5_accounts")
        
        config = VIKING_ACCOUNTS[strategy_name]
        
        # Build response with VIKING metadata
        result = {
            "strategy": strategy_name,
            "account": account_number,
            "platform": config["platform"],
            "broker": config["broker"],
            "description": config["description"],
            "balance": account.get("balance", 0),
            "equity": account.get("equity", 0),
            "margin": account.get("margin", 0),
            "free_margin": account.get("margin_free", 0),
            "profit": account.get("profit", 0),
            "leverage": account.get("leverage", 0),
            "currency": account.get("currency", "USD"),
            "status": "active",
            "last_sync": account.get("last_sync_timestamp") or account.get("updated_at"),
            "open_positions": account.get("open_positions", []),
            "open_positions_count": account.get("open_positions_count", 0)
        }
        
        # Get latest analytics
        analytics = await db.viking_analytics.find_one(
            {"account": account_number},
            {"_id": 0},
            sort=[("calculated_at", -1)]
        )
        result["analytics"] = analytics or {}
        
        return {
            "success": True,
            "account": serialize_doc(result)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING account {account_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts")
async def create_viking_account(account_data: VikingAccountCreate):
    """
    Create a new VIKING account - DEPRECATED
    VIKING now uses SSOT pattern with mt5_accounts
    """
    return {
        "success": False,
        "message": "VIKING uses SSOT pattern - accounts are managed through mt5_accounts. Contact admin to add new VIKING strategies."
    }


@router.put("/accounts/{account_number}")
async def update_viking_account(account_number: int, update_data: VikingAccountUpdate):
    """
    Update VIKING account data - DEPRECATED
    VIKING now uses SSOT pattern - mt5_accounts is synced by FIDUS VPS bridge
    """
    return {
        "success": False,
        "message": "VIKING uses SSOT pattern - account data is synced from mt5_accounts by FIDUS VPS bridge"
    }


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/{strategy}")
async def get_viking_analytics(strategy: str):
    """Get analytics for CORE or PRO strategy"""
    try:
        strategy = strategy.upper()
        if strategy not in VIKING_ACCOUNTS:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account_num = VIKING_ACCOUNTS[strategy]["account"]
        
        # Get latest analytics
        analytics = await db.viking_analytics.find_one(
            {"account": account_num},
            {"_id": 0},
            sort=[("calculated_at", -1)]
        )
        
        if not analytics:
            # Return default analytics structure
            analytics = {
                "account": account_num,
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
        # Verify this is a VIKING account
        strategy_name = None
        for name, config in VIKING_ACCOUNTS.items():
            if config["account"] == account_number:
                strategy_name = name
                break
        
        if not strategy_name:
            raise HTTPException(status_code=404, detail=f"Account {account_number} is not a VIKING account")
        
        doc = {
            "account": account_number,
            "strategy": strategy_name,
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
# Using SSOT - deals come from mt5_deals collection for MT5 accounts
# ============================================================================

@router.get("/deals/{strategy}")
async def get_viking_deals(
    strategy: str,
    limit: int = 100,
    skip: int = 0,
    symbol: Optional[str] = None
):
    """Get deal history for CORE or PRO strategy from mt5_deals (SSOT)"""
    try:
        strategy = strategy.upper()
        if strategy not in VIKING_ACCOUNTS:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        config = VIKING_ACCOUNTS[strategy]
        account_num = config["account"]
        platform = config["platform"]
        
        # Query from mt5_deals for MT5 accounts, mt5_deals with login field
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
            },
            "source": "mt5_deals (SSOT)"
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
# Using SSOT - open positions from mt5_accounts
# ============================================================================

@router.get("/orders/{strategy}")
async def get_viking_orders(strategy: str):
    """Get open orders/trades for CORE or PRO strategy from mt5_accounts (SSOT)"""
    try:
        strategy = strategy.upper()
        if strategy not in VIKING_ACCOUNTS:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        config = VIKING_ACCOUNTS[strategy]
        account_num = config["account"]
        platform = config["platform"]
        
        # Get open positions from mt5_accounts (SSOT)
        account = await db.mt5_accounts.find_one(
            {"account": account_num},
            {"_id": 0, "open_positions": 1, "open_positions_count": 1}
        )
        
        orders = account.get("open_positions", []) if account else []
        
        return {
            "success": True,
            "strategy": strategy,
            "account": account_num,
            "platform": platform,
            "orders": serialize_doc(orders),
            "count": len(orders),
            "source": "mt5_accounts (SSOT)"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching VIKING orders for {strategy}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUMMARY ENDPOINT
# Using SSOT - combines data from mt5_accounts
# ============================================================================

@router.get("/summary")
async def get_viking_summary():
    """Get combined VIKING summary with all strategies"""
    try:
        strategies = []
        
        for strategy_name, config in VIKING_ACCOUNTS.items():
            account_data = await get_viking_account_data(strategy_name)
            
            if not account_data:
                continue
            
            account_num = config["account"]
            
            # Get latest analytics
            analytics = await db.viking_analytics.find_one(
                {"account": account_num},
                {"_id": 0},
                sort=[("calculated_at", -1)]
            )
            
            # Get deal count from mt5_deals
            total_deals = await db.mt5_deals.count_documents(
                {"$or": [{"login": account_num}, {"login": str(account_num)}]}
            )
            
            strategy_data = {
                "strategy": strategy_name,
                "account": account_num,
                "broker": config["broker"],
                "platform": config["platform"],
                "description": config["description"],
                "balance": account_data.get("balance", 0),
                "equity": account_data.get("equity", 0),
                "floating_pnl": account_data.get("equity", 0) - account_data.get("balance", 0),
                "free_margin": account_data.get("margin_free") or account_data.get("free_margin", 0),
                "margin_in_use": account_data.get("margin", 0),
                "margin_level": (account_data.get("equity", 0) / account_data.get("margin", 1) * 100) if account_data.get("margin", 0) > 0 else 0,
                "status": account_data.get("status", "active"),
                "last_sync": account_data.get("last_sync_timestamp") or account_data.get("updated_at") or account_data.get("last_sync"),
                "total_deals": total_deals,
                "open_orders": account_data.get("open_positions_count", 0),
                "analytics": analytics or {},
                "data_source": account_data.get("data_source", "unknown")
            }
            strategies.append(strategy_data)
        
        # Combined totals
        total_balance = sum(s["balance"] for s in strategies)
        total_equity = sum(s["equity"] for s in strategies)
        
        return {
            "success": True,
            "strategies": serialize_doc(strategies),
            "combined": {
                "total_balance": total_balance,
                "total_equity": total_equity,
                "total_floating_pnl": total_equity - total_balance,
                "total_strategies": len(strategies),
                "active_strategies": len(strategies)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching VIKING summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYNC ENDPOINT - No longer needed for SSOT pattern
# VIKING data comes directly from mt5_accounts which is synced by FIDUS VPS bridge
# ============================================================================

@router.post("/sync")
async def trigger_viking_sync():
    """
    Sync endpoint - now just returns current state
    VIKING uses SSOT pattern - data comes from mt5_accounts synced by FIDUS VPS bridge
    """
    try:
        results = []
        
        for strategy_name, config in VIKING_ACCOUNTS.items():
            account_num = config["account"]
            account = await db.mt5_accounts.find_one({"account": account_num}, {"_id": 0})
            
            if account:
                results.append({
                    "strategy": strategy_name,
                    "account": account_num,
                    "balance": account.get("balance", 0),
                    "equity": account.get("equity", 0),
                    "last_sync": account.get("last_sync_timestamp") or account.get("updated_at"),
                    "status": "synced_via_fidus_bridge"
                })
        
        return {
            "success": True,
            "message": "VIKING uses SSOT pattern - data synced via FIDUS VPS bridge",
            "results": serialize_doc(results),
            "note": "No separate sync needed - VIKING reads from mt5_accounts (SSOT)"
        }
    except Exception as e:
        logger.error(f"Error in VIKING sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYMBOL DISTRIBUTION ENDPOINT
# Using SSOT - data from mt5_deals
# ============================================================================

@router.get("/symbols/{strategy}")
async def get_viking_symbol_distribution(strategy: str):
    """Get symbol distribution for a strategy (for pie charts) from mt5_deals (SSOT)"""
    try:
        strategy = strategy.upper()
        if strategy not in VIKING_ACCOUNTS:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        config = VIKING_ACCOUNTS[strategy]
        account_num = config["account"]
        
        # Aggregate from mt5_deals
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
            "platform": config["platform"],
            "distribution": distribution,
            "total_trades": total_trades,
            "source": "mt5_deals (SSOT)"
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
        if strategy not in VIKING_ACCOUNTS:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account_num = VIKING_ACCOUNTS[strategy]["account"]
        
        # Get historical analytics snapshots
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        history = await db.viking_analytics.find(
            {
                "account": account_num,
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
                "message": "No historical data available yet."
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
        if strategy not in VIKING_ACCOUNTS:
            raise HTTPException(status_code=400, detail="Strategy must be CORE or PRO")
        
        account_num = VIKING_ACCOUNTS[strategy]["account"]
        
        # Get latest analytics for risk metrics
        analytics = await db.viking_analytics.find_one(
            {"account": account_num},
            {"_id": 0},
            sort=[("calculated_at", -1)]
        )
        
        # Default risk metrics if no analytics
        risk_data = {
            "strategy": strategy,
            "account": account_num,
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

