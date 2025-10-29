"""
MT5 Bridge API Service - WORKING MULTI-ACCOUNT VERSION
Cycles through all 7 accounts every 15 minutes to update cache
Backend queries cached data via /api/mt5/account/{id}/info

This restores the working version that successfully managed all 7 accounts.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import MetaTrader5 as mt5
from datetime import datetime, timezone
from pymongo import MongoClient
from cryptography.fernet import Fernet
import logging
import os
import asyncio
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MT5 Bridge API - Multi-Account", version="4.0-working")

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
ACCOUNT_CACHE = {}  # Cache account data
ACCOUNT_PASSWORDS = {}  # Loaded from MongoDB

# MongoDB connection
MONGO_URL = "mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.ylp9be2.mongodb.net/fidus_production"
ENCRYPTION_KEY = "zJe8Q5W1xN_vK4RmPq7sL2dF9HtYbGn3-cXaVwUoIp0="  # From VPS env

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


def load_account_passwords():
    """Load encrypted passwords from MongoDB and decrypt them"""
    global ACCOUNT_PASSWORDS
    
    try:
        logger.info("[INIT] Loading account passwords from MongoDB...")
        
        # Connect to MongoDB
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client.fidus_production
        
        # Initialize encryption
        fernet = Fernet(ENCRYPTION_KEY.encode())
        
        # Load passwords for all managed accounts
        for account_number in MANAGED_ACCOUNTS.keys():
            try:
                account_doc = db.mt5_accounts.find_one({"account_number": account_number})
                if account_doc and 'encrypted_password' in account_doc:
                    # Decrypt password
                    encrypted_pwd = account_doc['encrypted_password']
                    decrypted_pwd = fernet.decrypt(encrypted_pwd.encode()).decode()
                    
                    ACCOUNT_PASSWORDS[account_number] = {
                        "password": decrypted_pwd,
                        "server": account_doc.get('server', 'MEXAtlantic-Demo')
                    }
                    logger.info(f"[OK] Loaded password for account {account_number}")
                else:
                    logger.warning(f"[WARN] No password found for account {account_number}")
            except Exception as e:
                logger.error(f"[ERROR] Failed to load password for {account_number}: {e}")
        
        client.close()
        logger.info(f"[OK] Loaded passwords for {len(ACCOUNT_PASSWORDS)} accounts")
        return len(ACCOUNT_PASSWORDS) > 0
        
    except Exception as e:
        logger.error(f"[ERROR] MongoDB connection failed: {e}")
        return False


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
        
        # Load account passwords from MongoDB
        if not load_account_passwords():
            logger.error("[FAIL] Failed to load account passwords")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] MT5 initialization failed: {e}")
        return False


async def refresh_account_cache():
    """Background task to cycle through all accounts and update cache every 15 minutes"""
    while True:
        try:
            if MT5_INITIALIZED and ACCOUNT_PASSWORDS:
                logger.info("[CACHE] ============ Starting 15-minute refresh cycle ============")
                
                # Remember which account we start on
                start_info = mt5.account_info()
                start_account = start_info.login if start_info else None
                logger.info(f"[CACHE] Starting on account: {start_account}")
                
                successful_updates = 0
                
                # Cycle through each managed account
                for account_number in MANAGED_ACCOUNTS.keys():
                    if account_number not in ACCOUNT_PASSWORDS:
                        logger.warning(f"[CACHE] No password for {account_number}, skipping")
                        continue
                    
                    try:
                        # Login to this account
                        password_info = ACCOUNT_PASSWORDS[account_number]
                        logger.info(f"[CACHE] Logging into account {account_number}...")
                        
                        if mt5.login(account_number, 
                                   password=password_info["password"], 
                                   server=password_info["server"]):
                            
                            # Get account info
                            account_info = mt5.account_info()
                            if account_info:
                                # Cache the data
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
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "last_refresh": "success"
                                }
                                logger.info(f"[CACHE] ✅ Account {account_number}: ${account_info.balance:.2f}")
                                successful_updates += 1
                            else:
                                logger.warning(f"[CACHE] ⚠️ No info returned for {account_number}")
                        else:
                            logger.error(f"[CACHE] ❌ Failed to login to {account_number}")
                        
                        # Small delay between account switches
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"[CACHE] Error processing account {account_number}: {e}")
                
                # Return to starting account if possible
                if start_account and start_account in ACCOUNT_PASSWORDS:
                    try:
                        password_info = ACCOUNT_PASSWORDS[start_account]
                        mt5.login(start_account, 
                                password=password_info["password"],
                                server=password_info["server"])
                        logger.info(f"[CACHE] Returned to account {start_account}")
                    except:
                        pass
                
                logger.info(f"[CACHE] ============ Refresh complete: {successful_updates}/{len(MANAGED_ACCOUNTS)} accounts ============")
            
            # Wait 15 minutes before next cycle (900 seconds)
            logger.info("[CACHE] Waiting 15 minutes until next refresh...")
            await asyncio.sleep(900)
            
        except Exception as e:
            logger.error(f"[CACHE] Fatal error in refresh task: {e}")
            await asyncio.sleep(900)  # Wait 15 min before retry


@app.on_event("startup")
async def startup_event():
    """Initialize MT5 and start background cache refresh"""
    logger.info("=" * 60)
    logger.info("MT5 BRIDGE STARTING - WORKING MULTI-ACCOUNT VERSION")
    logger.info("=" * 60)
    initialize_mt5_once()
    
    # Start background cache refresh task
    asyncio.create_task(refresh_account_cache())
    logger.info("[STARTUP] Background cache refresh started (15-minute interval)")


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
    return {
        "status": "healthy",
        "mt5": {
            "initialized": MT5_INITIALIZED,
            "available": MT5_INITIALIZED,
            "accounts_with_passwords": len(ACCOUNT_PASSWORDS),
            "cached_accounts": len(ACCOUNT_CACHE)
        },
        "version": "4.0-working",
        "refresh_interval": "15 minutes",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/mt5/accounts/summary")
async def get_accounts_summary():
    """Get summary of all managed accounts from cache"""
    try:
        if not MT5_INITIALIZED:
            raise HTTPException(status_code=503, detail="MT5 not initialized")
        
        accounts_data = []
        for account_number, account_info in MANAGED_ACCOUNTS.items():
            if account_number in ACCOUNT_CACHE:
                cached_data = ACCOUNT_CACHE[account_number]
                accounts_data.append({
                    "account": account_number,
                    "name": account_info["name"],
                    "fund_type": account_info["fund_type"],
                    "balance": cached_data["balance"],
                    "equity": cached_data["equity"],
                    "last_updated": cached_data.get("timestamp")
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
    """Get account info from cache - used by backend sync service"""
    try:
        if account_number not in MANAGED_ACCOUNTS:
            raise HTTPException(status_code=404, detail=f"Account {account_number} not managed")
        
        if not MT5_INITIALIZED:
            raise HTTPException(status_code=503, detail="MT5 not initialized")
        
        # Return cached data if available
        if account_number in ACCOUNT_CACHE:
            cached_data = ACCOUNT_CACHE[account_number]
            return {
                "account_id": account_number,
                "name": MANAGED_ACCOUNTS[account_number]["name"],
                "fund_type": MANAGED_ACCOUNTS[account_number]["fund_type"],
                "balance": cached_data["balance"],
                "equity": cached_data["equity"],
                "profit": cached_data["profit"],
                "margin": cached_data["margin"],
                "margin_free": cached_data["margin_free"],
                "margin_level": cached_data["margin_level"],
                "currency": cached_data["currency"],
                "leverage": cached_data["leverage"],
                "data_source": "cached",
                "last_sync": cached_data.get("timestamp"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            # No cached data yet - return placeholder
            return {
                "account_id": account_number,
                "name": MANAGED_ACCOUNTS[account_number]["name"],
                "fund_type": MANAGED_ACCOUNTS[account_number]["fund_type"],
                "balance": 0.0,
                "equity": 0.0,
                "note": "Waiting for first refresh cycle (every 15 minutes)",
                "data_source": "placeholder",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mt5/account/{account_number}/trades")
async def get_account_trades(account_number: int, limit: int = 100):
    """Get historical trades for account"""
    # Placeholder - implement if needed
    return {
        "success": True,
        "trades": [],
        "count": 0,
        "account_number": account_number,
        "note": "Trades endpoint - implement if needed"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
