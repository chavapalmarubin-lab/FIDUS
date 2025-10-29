"""
MT5 Bridge API Service - WORKING MULTI-ACCOUNT VERSION
Uses environment variables for passwords (simpler, more reliable)
Cycles through all 7 accounts every 15 minutes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import MetaTrader5 as mt5
from datetime import datetime, timezone
import logging
import os
import asyncio
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MT5 Bridge API - Multi-Account", version="4.0-working-env")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
MT5_INITIALIZED = False
ACCOUNT_CACHE = {}
ACCOUNT_PASSWORDS = {}

# Account configuration
MANAGED_ACCOUNTS = {
    886557: {"name": "BALANCE Master", "fund_type": "BALANCE"},
    886066: {"name": "BALANCE-01", "fund_type": "BALANCE"},
    886602: {"name": "BALANCE-02", "fund_type": "BALANCE"},
    885822: {"name": "CORE-01", "fund_type": "CORE"},
    886528: {"name": "CORE-02", "fund_type": "CORE"},
    891215: {"name": "SEPARATION-01", "fund_type": "SEPARATION"},
    891234: {"name": "SEPARATION-02", "fund_type": "SEPARATION"}
}


def load_account_passwords_from_env():
    """Load account passwords from environment variables"""
    global ACCOUNT_PASSWORDS
    
    logger.info("[INIT] Loading account passwords from environment...")
    
    # Load passwords for each account from env vars
    # Format: MT5_PWD_886557, MT5_PWD_886066, etc.
    for account_number in MANAGED_ACCOUNTS.keys():
        env_var = f"MT5_PWD_{account_number}"
        password = os.getenv(env_var, "")
        
        if password:
            ACCOUNT_PASSWORDS[account_number] = {
                "password": password,
                "server": os.getenv("MT5_SERVER", "MEXAtlantic-Demo")
            }
            logger.info(f"[OK] Loaded password for account {account_number} from {env_var}")
        else:
            logger.warning(f"[WARN] No password found in env var {env_var}")
    
    logger.info(f"[OK] Loaded passwords for {len(ACCOUNT_PASSWORDS)} accounts")
    return len(ACCOUNT_PASSWORDS) > 0


def initialize_mt5_once():
    """Initialize MT5 connection ONCE at startup"""
    global MT5_INITIALIZED
    
    if MT5_INITIALIZED:
        return True
    
    try:
        logger.info("[INIT] Initializing MT5 connection...")
        
        if not mt5.initialize():
            logger.error("[FAIL] MT5 initialization failed")
            return False
        
        MT5_INITIALIZED = True
        logger.info(f"[OK] MT5 initialized: {mt5.version()}")
        
        # Load account passwords
        load_account_passwords_from_env()
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] MT5 initialization failed: {e}")
        return False


async def refresh_account_cache():
    """Background task to cycle through all accounts every 15 minutes"""
    # Wait 30 seconds before first run
    await asyncio.sleep(30)
    
    while True:
        try:
            if MT5_INITIALIZED and ACCOUNT_PASSWORDS:
                logger.info("[CACHE] ============ Starting 15-minute refresh cycle ============")
                
                start_info = mt5.account_info()
                start_account = start_info.login if start_info else None
                logger.info(f"[CACHE] Starting on account: {start_account}")
                
                successful_updates = 0
                
                # Cycle through each account
                for account_number in MANAGED_ACCOUNTS.keys():
                    if account_number not in ACCOUNT_PASSWORDS:
                        logger.warning(f"[CACHE] No password for {account_number}, skipping")
                        continue
                    
                    try:
                        password_info = ACCOUNT_PASSWORDS[account_number]
                        logger.info(f"[CACHE] Logging into account {account_number}...")
                        
                        if mt5.login(account_number, 
                                   password=password_info["password"], 
                                   server=password_info["server"]):
                            
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
                                successful_updates += 1
                            else:
                                logger.warning(f"[CACHE] ⚠️ No info for {account_number}")
                        else:
                            logger.error(f"[CACHE] ❌ Login failed for {account_number}")
                        
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"[CACHE] Error with account {account_number}: {e}")
                
                # Return to starting account
                if start_account and start_account in ACCOUNT_PASSWORDS:
                    try:
                        password_info = ACCOUNT_PASSWORDS[start_account]
                        mt5.login(start_account, 
                                password=password_info["password"],
                                server=password_info["server"])
                        logger.info(f"[CACHE] Returned to account {start_account}")
                    except:
                        pass
                
                logger.info(f"[CACHE] ============ Complete: {successful_updates}/{len(MANAGED_ACCOUNTS)} accounts ============")
            
            # Wait 15 minutes
            logger.info("[CACHE] Waiting 15 minutes until next refresh...")
            await asyncio.sleep(900)
            
        except Exception as e:
            logger.error(f"[CACHE] Fatal error: {e}")
            await asyncio.sleep(900)


@app.on_event("startup")
async def startup_event():
    """Initialize MT5 and start background refresh"""
    logger.info("=" * 60)
    logger.info("MT5 BRIDGE STARTING - MULTI-ACCOUNT (ENV PASSWORDS)")
    logger.info("=" * 60)
    initialize_mt5_once()
    asyncio.create_task(refresh_account_cache())
    logger.info("[STARTUP] Background refresh started (15-min interval)")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup"""
    global MT5_INITIALIZED
    if MT5_INITIALIZED:
        mt5.shutdown()
        MT5_INITIALIZED = False
        logger.info("[SHUTDOWN] MT5 closed")


@app.get("/api/mt5/bridge/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "mt5": {
            "initialized": MT5_INITIALIZED,
            "available": MT5_INITIALIZED,
            "accounts_with_passwords": len(ACCOUNT_PASSWORDS),
            "cached_accounts": len(ACCOUNT_CACHE)
        },
        "version": "4.0-working-env",
        "refresh_interval": "15 minutes",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/mt5/accounts/summary")
async def get_accounts_summary():
    """Get all accounts summary from cache"""
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
                    "note": "Waiting for first refresh"
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
    """Get account info from cache"""
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
                "note": "Waiting for first refresh (every 15 minutes)",
                "data_source": "placeholder",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mt5/account/{account_number}/trades")
async def get_account_trades(account_number: int, limit: int = 100):
    """Get trades - placeholder"""
    return {
        "success": True,
        "trades": [],
        "count": 0,
        "account_number": account_number
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
