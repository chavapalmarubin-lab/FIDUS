"""
MT5 Bridge API Service - WORKING VERSION WITH HARDCODED PASSWORD
All accounts use same password: "[CLEANED_PASSWORD]"
Cycles every 15 minutes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import MetaTrader5 as mt5
from datetime import datetime, timezone
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="MT5 Bridge API - Working", version="4.0-working")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MT5_INITIALIZED = False
ACCOUNT_CACHE = {}

# ALL accounts use same password
MT5_PASSWORD = ""[CLEANED_PASSWORD]""
MT5_SERVER = "MEXAtlantic-Demo"

MANAGED_ACCOUNTS = {
    886557: {"name": "BALANCE Master", "fund_type": "BALANCE"},
    886066: {"name": "BALANCE-01", "fund_type": "BALANCE"},
    886602: {"name": "BALANCE-02", "fund_type": "BALANCE"},
    885822: {"name": "CORE-01", "fund_type": "CORE"},
    886528: {"name": "CORE-02", "fund_type": "CORE"},
    891215: {"name": "SEPARATION-01", "fund_type": "SEPARATION"},
    891234: {"name": "SEPARATION-02", "fund_type": "SEPARATION"}
}


def initialize_mt5_once():
    global MT5_INITIALIZED
    if MT5_INITIALIZED:
        return True
    
    try:
        logger.info("[INIT] Initializing MT5...")
        if not mt5.initialize():
            logger.error("[FAIL] MT5 init failed")
            return False
        
        MT5_INITIALIZED = True
        logger.info(f"[OK] MT5 initialized: {mt5.version()}")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Init failed: {e}")
        return False


async def refresh_all_accounts():
    """Cycle through ALL accounts every 15 minutes"""
    # Run first cycle immediately after startup
    await asyncio.sleep(10)
    
    while True:
        try:
            if MT5_INITIALIZED:
                logger.info("[CACHE] ========== Starting 15-min refresh cycle ==========")
                
                start_info = mt5.account_info()
                start_account = start_info.login if start_info else None
                success_count = 0
                
                # Login to each account and cache data
                for account_number in MANAGED_ACCOUNTS.keys():
                    try:
                        logger.info(f"[CACHE] Logging into account {account_number}...")
                        
                        if mt5.login(account_number, password=MT5_PASSWORD, server=MT5_SERVER):
                            account_info = mt5.account_info()
                            if account_info:
                                ACCOUNT_CACHE[account_number] = {
                                    "account": account_number,
                                    "balance": float(account_info.balance),
                                    "equity": float(account_info.equity),
                                    "profit": float(account_info.profit),
                                    "margin": float(account_info.margin),
                                    "margin_free": float(account_info.margin_free),
                                    "margin_level": float(account_info.margin_level) if account_info.margin_level else 0.0,
                                    "currency": account_info.currency,
                                    "leverage": account_info.leverage,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                                logger.info(f"[CACHE] ✅ Account {account_number}: ${account_info.balance:.2f}")
                                success_count += 1
                            else:
                                logger.warning(f"[CACHE] ⚠️ No info for {account_number}")
                        else:
                            logger.error(f"[CACHE] ❌ Login failed for {account_number}")
                        
                        await asyncio.sleep(3)  # 3 seconds between accounts
                        
                    except Exception as e:
                        logger.error(f"[CACHE] Error with account {account_number}: {e}")
                
                # Return to starting account
                if start_account:
                    try:
                        mt5.login(start_account, password=MT5_PASSWORD, server=MT5_SERVER)
                        logger.info(f"[CACHE] Returned to account {start_account}")
                    except:
                        pass
                
                logger.info(f"[CACHE] ========== Complete: {success_count}/7 accounts updated ==========")
            
            # Wait 15 minutes (900 seconds)
            logger.info("[CACHE] Waiting 15 minutes until next cycle...")
            await asyncio.sleep(900)
            
        except Exception as e:
            logger.error(f"[CACHE] Fatal error: {e}")
            await asyncio.sleep(900)


@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("MT5 BRIDGE STARTING - WORKING MULTI-ACCOUNT VERSION")
    logger.info("=" * 60)
    initialize_mt5_once()
    asyncio.create_task(refresh_all_accounts())
    logger.info("[STARTUP] Background refresh started (15-min interval)")


@app.on_event("shutdown")
async def shutdown_event():
    global MT5_INITIALIZED
    if MT5_INITIALIZED:
        mt5.shutdown()
        MT5_INITIALIZED = False


@app.get("/api/mt5/bridge/health")
async def health_check():
    return {
        "status": "healthy",
        "mt5": {
            "initialized": MT5_INITIALIZED,
            "available": MT5_INITIALIZED,
            "cached_accounts": len(ACCOUNT_CACHE)
        },
        "version": "4.0-working",
        "refresh_interval": "15 minutes",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/mt5/accounts/summary")
async def get_accounts_summary():
    try:
        if not MT5_INITIALIZED:
            raise HTTPException(status_code=503, detail="MT5 not initialized")
        
        accounts_data = []
        for account_number, account_info in MANAGED_ACCOUNTS.items():
            if account_number in ACCOUNT_CACHE:
                cached = ACCOUNT_CACHE[account_number]
                accounts_data.append({
                    "account": account_number,
                    "name": account_info["name"],
                    "fund_type": account_info["fund_type"],
                    "balance": cached["balance"],
                    "equity": cached["equity"],
                    "last_updated": cached.get("timestamp")
                })
            else:
                accounts_data.append({
                    "account": account_number,
                    "name": account_info["name"],
                    "fund_type": account_info["fund_type"],
                    "balance": 0.0,
                    "equity": 0.0,
                    "note": "Waiting for first refresh (runs every 15 min)"
                })
        
        return {
            "success": True,
            "accounts": accounts_data,
            "count": len(accounts_data),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mt5/account/{account_number}/info")
async def get_account_info(account_number: int):
    try:
        if account_number not in MANAGED_ACCOUNTS:
            raise HTTPException(status_code=404, detail=f"Account {account_number} not managed")
        
        if not MT5_INITIALIZED:
            raise HTTPException(status_code=503, detail="MT5 not initialized")
        
        if account_number in ACCOUNT_CACHE:
            cached = ACCOUNT_CACHE[account_number]
            return {
                "account_id": account_number,
                "name": MANAGED_ACCOUNTS[account_number]["name"],
                "fund_type": MANAGED_ACCOUNTS[account_number]["fund_type"],
                "balance": cached["balance"],
                "equity": cached["equity"],
                "profit": cached["profit"],
                "margin": cached["margin"],
                "margin_free": cached["margin_free"],
                "margin_level": cached["margin_level"],
                "currency": cached["currency"],
                "leverage": cached["leverage"],
                "data_source": "cached",
                "last_sync": cached.get("timestamp"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "account_id": account_number,
                "name": MANAGED_ACCOUNTS[account_number]["name"],
                "fund_type": MANAGED_ACCOUNTS[account_number]["fund_type"],
                "balance": 0.0,
                "equity": 0.0,
                "note": "Waiting for first refresh cycle",
                "data_source": "placeholder",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mt5/account/{account_number}/trades")
async def get_account_trades(account_number: int, limit: int = 100):
    return {
        "success": True,
        "trades": [],
        "count": 0,
        "account_number": account_number
    }


@app.get("/api/mt5/manual-refresh")
async def manual_refresh():
    """Manual trigger for account refresh - for testing"""
    try:
        if not MT5_INITIALIZED:
            return {"error": "MT5 not initialized"}
        
        logger.info("[MANUAL] Starting manual refresh...")
        success_count = 0
        errors = []
        
        for account_number in MANAGED_ACCOUNTS.keys():
            try:
                logger.info(f"[MANUAL] Trying account {account_number}...")
                
                if mt5.login(account_number, password=MT5_PASSWORD, server=MT5_SERVER):
                    account_info = mt5.account_info()
                    if account_info:
                        ACCOUNT_CACHE[account_number] = {
                            "account": account_number,
                            "balance": float(account_info.balance),
                            "equity": float(account_info.equity),
                            "profit": float(account_info.profit),
                            "margin": float(account_info.margin),
                            "margin_free": float(account_info.margin_free),
                            "margin_level": float(account_info.margin_level) if account_info.margin_level else 0.0,
                            "currency": account_info.currency,
                            "leverage": account_info.leverage,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                        logger.info(f"[MANUAL] ✅ Account {account_number}: ${account_info.balance:.2f}")
                        success_count += 1
                    else:
                        errors.append(f"Account {account_number}: No info returned")
                else:
                    error = mt5.last_error()
                    errors.append(f"Account {account_number}: Login failed - {error}")
                    
            except Exception as e:
                errors.append(f"Account {account_number}: Exception - {str(e)}")
        
        return {
            "success": True,
            "accounts_updated": success_count,
            "total_accounts": len(MANAGED_ACCOUNTS),
            "errors": errors,
            "cache_size": len(ACCOUNT_CACHE)
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
