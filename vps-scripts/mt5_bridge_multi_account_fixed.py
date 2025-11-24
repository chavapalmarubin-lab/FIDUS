"""
MT5 Bridge API Service - MULTI-ACCOUNT FIXED
Properly logs into ALL 7 accounts to fetch real balances
Runs in interactive user session for MT5 connection
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import MetaTrader5 as mt5
from datetime import datetime, timezone
import logging
import os
from typing import Dict, List, Optional
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\mt5_bridge_service\\logs\\api_service.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MT5 Bridge API - Multi-Account Fixed", version="4.0-multi-account")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MT5 connection state
MT5_INITIALIZED = False
MT5_SERVER = "MEXAtlantic-Real"
MT5_INVESTOR_PASSWORD = ""[CLEANED_PASSWORD]""  # Investor password for ALL accounts

# All 7 MT5 accounts with complete configuration
MANAGED_ACCOUNTS = {
    885822: {"name": "CORE-CP", "fund_type": "CORE", "provider": "CP Strategy"},
    886066: {"name": "BALANCE-GoldenTrade", "fund_type": "BALANCE", "provider": "GoldenTrade"},
    886528: {"name": "SEPARATION-Reserve", "fund_type": "SEPARATION", "provider": "Interest Reserve"},
    886557: {"name": "BALANCE-Master", "fund_type": "BALANCE", "provider": "Primary"},
    886602: {"name": "BALANCE-Tertiary", "fund_type": "BALANCE", "provider": "Tertiary"},
    891215: {"name": "SEPARATION-Trading", "fund_type": "SEPARATION_TRADING", "provider": "GoldenTrade"},
    891234: {"name": "CORE-GoldenTrade", "fund_type": "CORE", "provider": "GoldenTrade"}
}

# Cache for account data
ACCOUNT_CACHE = {}
CACHE_LOCK = asyncio.Lock()


def initialize_mt5():
    """Initialize MT5 terminal connection"""
    global MT5_INITIALIZED
    
    if MT5_INITIALIZED:
        return True
    
    try:
        logger.info("=" * 60)
        logger.info("[INIT] Initializing MT5 terminal connection...")
        logger.info("=" * 60)
        
        if not mt5.initialize():
            error = mt5.last_error()
            logger.error(f"[FAIL] MT5 initialization failed: {error}")
            return False
        
        MT5_INITIALIZED = True
        version = mt5.version()
        logger.info(f"[OK] MT5 initialized successfully")
        logger.info(f"[INFO] MT5 Version: {version}")
        
        # Get terminal info
        terminal_info = mt5.terminal_info()
        if terminal_info:
            logger.info(f"[INFO] Terminal Company: {terminal_info.company}")
            logger.info(f"[INFO] Terminal Connected: {terminal_info.connected}")
            logger.info(f"[INFO] Trade Allowed: {terminal_info.trade_allowed}")
        
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] Exception during MT5 initialization: {str(e)}")
        return False


def login_to_account(account_number: int, password: str) -> bool:
    """
    Login to a specific MT5 account
    Returns True if successful, False otherwise
    """
    try:
        logger.info(f"[LOGIN] Attempting to login to account {account_number}...")
        
        # Ensure MT5 is initialized
        if not MT5_INITIALIZED:
            if not initialize_mt5():
                logger.error(f"[FAIL] Cannot login - MT5 not initialized")
                return False
        
        # Attempt login
        authorized = mt5.login(login=account_number, password=password, server=MT5_SERVER)
        
        if not authorized:
            error = mt5.last_error()
            logger.error(f"[FAIL] Login failed for account {account_number}: {error}")
            return False
        
        # Verify login
        account_info = mt5.account_info()
        if account_info and account_info.login == account_number:
            logger.info(f"[OK] Successfully logged into account {account_number}")
            logger.info(f"[DATA] Balance: ${account_info.balance}, Equity: ${account_info.equity}")
            return True
        else:
            logger.error(f"[FAIL] Login verification failed for account {account_number}")
            return False
        
    except Exception as e:
        logger.error(f"[FAIL] Exception during login to {account_number}: {str(e)}")
        return False


def get_account_data(account_number: int) -> Optional[Dict]:
    """
    Get current account data from MT5
    Assumes already logged into this account
    """
    try:
        account_info = mt5.account_info()
        
        if not account_info:
            logger.error(f"[FAIL] Failed to get account info for {account_number}")
            return None
        
        if account_info.login != account_number:
            logger.warning(f"[WARN] Expected account {account_number}, but logged into {account_info.login}")
        
        data = {
            "account": account_info.login,
            "balance": float(account_info.balance),
            "equity": float(account_info.equity),
            "profit": float(account_info.profit),
            "margin": float(account_info.margin),
            "margin_free": float(account_info.margin_free),
            "margin_level": float(account_info.margin_level) if account_info.margin_level else 0.0,
            "currency": account_info.currency,
            "leverage": account_info.leverage,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_source": "mt5_live"
        }
        
        logger.info(f"[DATA] Account {account_number}: Balance=${data['balance']}, Equity=${data['equity']}")
        return data
        
    except Exception as e:
        logger.error(f"[FAIL] Error getting account data for {account_number}: {str(e)}")
        return None


async def refresh_all_accounts():
    """
    Background task: Cycle through ALL 7 accounts and fetch real balances
    This is the KEY function that fixes the multi-account issue
    """
    logger.info("[CACHE] Starting account refresh cycle...")
    
    async with CACHE_LOCK:
        for account_number in MANAGED_ACCOUNTS.keys():
            try:
                logger.info(f"[CACHE] Processing account {account_number}...")
                
                # Login to this account
                if login_to_account(account_number, MT5_INVESTOR_PASSWORD):
                    # Get account data
                    data = get_account_data(account_number)
                    
                    if data:
                        # Update cache
                        ACCOUNT_CACHE[account_number] = data
                        logger.info(f"[CACHE] ✅ Cached account {account_number}: ${data['balance']}")
                    else:
                        logger.warning(f"[CACHE] ⚠️ Failed to get data for account {account_number}")
                else:
                    logger.error(f"[CACHE] ❌ Failed to login to account {account_number}")
                
                # Small delay between account switches
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"[CACHE] Error processing account {account_number}: {str(e)}")
                continue
    
    logger.info(f"[CACHE] Refresh cycle complete. Cached accounts: {len(ACCOUNT_CACHE)}/7")


async def account_refresh_loop():
    """
    Background task that runs every 5 minutes to refresh all account data
    """
    # Wait 10 seconds after startup before first refresh
    await asyncio.sleep(10)
    
    while True:
        try:
            logger.info("[LOOP] Starting account refresh cycle...")
            await refresh_all_accounts()
            logger.info("[LOOP] Sleeping for 5 minutes until next refresh...")
            await asyncio.sleep(300)  # 5 minutes
        except Exception as e:
            logger.error(f"[LOOP] Error in refresh loop: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute before retry on error


@app.on_event("startup")
async def startup_event():
    """Initialize MT5 and start background refresh task"""
    logger.info("=" * 60)
    logger.info("MT5 BRIDGE STARTING - MULTI-ACCOUNT FIXED VERSION")
    logger.info("=" * 60)
    
    # Initialize MT5
    if initialize_mt5():
        logger.info("[STARTUP] MT5 initialized successfully")
        
        # Start background refresh task
        asyncio.create_task(account_refresh_loop())
        logger.info("[STARTUP] Background account refresh task started")
        logger.info("[STARTUP] Will refresh all 7 accounts every 5 minutes")
    else:
        logger.error("[STARTUP] Failed to initialize MT5 - service may not work correctly")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup MT5 connection"""
    global MT5_INITIALIZED
    if MT5_INITIALIZED:
        mt5.shutdown()
        MT5_INITIALIZED = False
        logger.info("[SHUTDOWN] MT5 connection closed")


@app.get("/api/mt5/bridge/health")
async def health_check():
    """Health check endpoint"""
    terminal_info = None
    account_info = None
    available = False
    
    if MT5_INITIALIZED:
        try:
            terminal_info = mt5.terminal_info()
            account_info = mt5.account_info()
            if terminal_info and account_info:
                available = True
        except Exception as e:
            logger.error(f"[HEALTH] Error checking status: {str(e)}")
    
    return {
        "status": "healthy" if (MT5_INITIALIZED and available) else "unhealthy",
        "mt5": {
            "initialized": MT5_INITIALIZED,
            "available": available,
            "current_account": account_info.login if account_info else None,
            "terminal_info": {
                "connected": terminal_info.connected if terminal_info else False,
                "trade_allowed": terminal_info.trade_allowed if terminal_info else False
            } if terminal_info else None
        },
        "cache": {
            "accounts_cached": len(ACCOUNT_CACHE),
            "total_accounts": len(MANAGED_ACCOUNTS),
            "cache_complete": len(ACCOUNT_CACHE) == len(MANAGED_ACCOUNTS)
        },
        "version": "4.0-multi-account",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/mt5/accounts/summary")
async def get_accounts_summary():
    """
    Get summary of all 7 managed accounts
    Returns REAL balances from cache (populated by background task)
    """
    try:
        if not MT5_INITIALIZED:
            raise HTTPException(status_code=503, detail="MT5 not initialized")
        
        logger.info("[ENDPOINT] /api/mt5/accounts/summary called")
        
        accounts = []
        for account_number, config in MANAGED_ACCOUNTS.items():
            if account_number in ACCOUNT_CACHE:
                data = ACCOUNT_CACHE[account_number]
                accounts.append({
                    "account": account_number,
                    "name": config["name"],
                    "fund_type": config["fund_type"],
                    "provider": config["provider"],
                    "balance": data["balance"],
                    "equity": data["equity"],
                    "profit": data["profit"],
                    "timestamp": data["timestamp"],
                    "data_source": "cached"
                })
            else:
                # No cache yet - return placeholder
                accounts.append({
                    "account": account_number,
                    "name": config["name"],
                    "fund_type": config["fund_type"],
                    "provider": config["provider"],
                    "balance": 0.0,
                    "equity": 0.0,
                    "profit": 0.0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data_source": "no_cache",
                    "note": "Waiting for first cache refresh"
                })
        
        logger.info(f"[OK] Returning {len(accounts)} accounts ({len(ACCOUNT_CACHE)} cached)")
        
        return {
            "success": True,
            "accounts": accounts,
            "count": len(accounts),
            "cached_count": len(ACCOUNT_CACHE),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FAIL] Error in get_accounts_summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mt5/account/{account_number}/info")
async def get_account_info_endpoint(account_number: int):
    """Get detailed info for a specific account"""
    try:
        if account_number not in MANAGED_ACCOUNTS:
            raise HTTPException(status_code=404, detail=f"Account {account_number} not managed")
        
        logger.info(f"[ENDPOINT] /api/mt5/account/{account_number}/info called")
        
        if not MT5_INITIALIZED:
            raise HTTPException(status_code=503, detail="MT5 not initialized")
        
        # Get from cache
        if account_number in ACCOUNT_CACHE:
            live_data = ACCOUNT_CACHE[account_number]
            logger.info(f"[OK] Returning cached data for {account_number}: ${live_data['balance']}")
        else:
            # No cache - return placeholder
            live_data = {
                "account": account_number,
                "balance": 0.0,
                "equity": 0.0,
                "profit": 0.0,
                "margin": 0.0,
                "margin_free": 0.0,
                "margin_level": 0.0,
                "currency": "USD",
                "leverage": 0,
                "data_source": "no_cache",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": "Waiting for cache refresh"
            }
            logger.warning(f"[WARN] No cached data for account {account_number}")
        
        account_config = MANAGED_ACCOUNTS[account_number]
        
        return {
            "account_id": account_number,
            "name": account_config["name"],
            "fund_type": account_config["fund_type"],
            "provider": account_config.get("provider", "MEX Atlantic"),
            "live_data": live_data,
            "last_sync": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FAIL] Error in get_account_info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mt5/account/{account_number}/trades")
async def get_account_trades(account_number: int, limit: int = 100):
    """
    Get historical trades/deals for an account
    """
    try:
        if account_number not in MANAGED_ACCOUNTS:
            raise HTTPException(status_code=404, detail=f"Account {account_number} not managed")
        
        logger.info(f"[ENDPOINT] /api/mt5/account/{account_number}/trades called")
        
        if not MT5_INITIALIZED:
            raise HTTPException(status_code=503, detail="MT5 not initialized")
        
        # Login to the account to get its trade history
        if not login_to_account(account_number, MT5_INVESTOR_PASSWORD):
            logger.error(f"[FAIL] Could not login to account {account_number} for trade history")
            return {
                "success": False,
                "trades": [],
                "count": 0,
                "error": "Failed to login to account"
            }
        
        # Get deals history
        from_date = datetime(2020, 1, 1)
        to_date = datetime.now()
        
        deals = mt5.history_deals_get(from_date, to_date)
        
        if deals is None or len(deals) == 0:
            logger.warning(f"[WARN] No deals history for account {account_number}")
            return {
                "success": True,
                "trades": [],
                "count": 0,
                "account_number": account_number,
                "note": "No trading history available"
            }
        
        # Convert deals to dict
        account_deals = []
        for deal in deals:
            account_deals.append({
                "ticket": deal.ticket,
                "order": deal.order,
                "time": datetime.fromtimestamp(deal.time, tz=timezone.utc).isoformat(),
                "type": deal.type,
                "entry": deal.entry,
                "magic": deal.magic,  # CRITICAL: Magic number identifies the manager/EA
                "volume": float(deal.volume),
                "price": float(deal.price),
                "commission": float(deal.commission),
                "swap": float(deal.swap),
                "profit": float(deal.profit),
                "symbol": deal.symbol,
                "comment": deal.comment,
                "position_id": deal.position_id if hasattr(deal, 'position_id') else 0,
                "account_number": account_number
            })
        
        # Return last N deals
        trades_to_return = account_deals[-limit:]
        
        logger.info(f"[OK] Retrieved {len(trades_to_return)} deals for account {account_number}")
        
        return {
            "success": True,
            "trades": trades_to_return,
            "count": len(trades_to_return),
            "account_number": account_number,
            "total_available": len(account_deals),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FAIL] Error in get_account_trades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mt5/refresh")
async def force_refresh():
    """Force immediate refresh of all account data"""
    try:
        logger.info("[ENDPOINT] /api/mt5/refresh - Force refresh triggered")
        
        if not MT5_INITIALIZED:
            raise HTTPException(status_code=503, detail="MT5 not initialized")
        
        # Trigger immediate refresh
        await refresh_all_accounts()
        
        return {
            "success": True,
            "message": "Account refresh completed",
            "accounts_refreshed": len(ACCOUNT_CACHE),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"[FAIL] Error in force_refresh: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("MT5 BRIDGE API - MULTI-ACCOUNT FIXED")
    logger.info("Properly logs into ALL 7 accounts")
    logger.info("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
