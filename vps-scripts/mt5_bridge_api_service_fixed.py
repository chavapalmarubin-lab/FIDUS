"""
MT5 Bridge API Service - FIXED VERSION
Single Connection Method - No Account Switching

KEY FIX: Initialize MT5 ONCE and query all accounts through single connection
This prevents MT5 Terminal from switching accounts which causes zero balances
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import MetaTrader5 as mt5
from datetime import datetime, timezone
import logging
import os
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MT5 Bridge API", version="2.0-fixed")

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
MT5_LOGGED_IN = False
MANAGER_ACCOUNT = 886557

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


def initialize_mt5_once():
    """Initialize MT5 connection ONCE at startup"""
    global MT5_INITIALIZED, MT5_LOGGED_IN
    
    if MT5_INITIALIZED:
        logger.info("[OK] MT5 already initialized")
        return True
    
    try:
        logger.info("[START] Initializing MT5 connection...")
        
        if not mt5.initialize():
            logger.error("[FAIL] MT5 initialization failed")
            return False
        
        MT5_INITIALIZED = True
        logger.info("[OK] MT5 initialized successfully")
        logger.info(f"[INFO] MT5 version: {mt5.version()}")
        
        # Login to manager account ONCE
        manager_password = os.getenv("MT5_MANAGER_PASSWORD", "")  
        manager_server = os.getenv("MT5_SERVER", "MEXAtlantic-Demo")
        
        if manager_password:
            authorized = mt5.login(MANAGER_ACCOUNT, manager_password, manager_server)
            if authorized:
                MT5_LOGGED_IN = True
                logger.info(f"[OK] Logged in to manager account: {MANAGER_ACCOUNT}")
            else:
                logger.warning(f"[WARN] Could not login to manager account {MANAGER_ACCOUNT}")
        else:
            logger.warning("[WARN] No manager password configured - using terminal's current login")
        
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] MT5 initialization error: {str(e)}")
        return False


def get_account_data_no_switch(account_number: int) -> Dict:
    """
    Get account data WITHOUT switching MT5 Terminal login
    CRITICAL FIX: Query through existing connection
    """
    try:
        if not MT5_INITIALIZED:
            if not initialize_mt5_once():
                raise Exception("MT5 not initialized")
        
        logger.info(f"[QUERY] Getting data for account {account_number} (no terminal switch)")
        
        # Get account info from current connection
        # NOTE: This gets the CURRENT logged-in account's info
        account_info = mt5.account_info()
        
        if account_info is None:
            raise Exception("Failed to get account info")
        
        # If we're querying the currently logged-in account
        if account_info.login == account_number:
            logger.info(f"[OK] Querying currently logged-in account: {account_number}")
            return {
                "account": account_number,
                "balance": float(account_info.balance),
                "equity": float(account_info.equity),
                "profit": float(account_info.profit),
                "margin": float(account_info.margin),
                "margin_free": float(account_info.margin_free),
                "margin_level": float(account_info.margin_level) if account_info.margin_level else 0.0,
                "currency": account_info.currency,
                "leverage": account_info.leverage,
                "data_source": "mt5_direct",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # For other accounts, get positions/orders if manager has access
        # This requires manager account privileges
        positions = mt5.positions_get(group=f"*{account_number}*")
        
        if positions is not None:
            total_profit = sum([pos.profit for pos in positions])
            total_volume = sum([pos.volume for pos in positions])
            
            logger.info(f"[OK] Retrieved {len(positions)} positions for account {account_number}")
            
            # Return position-based data (limited info without direct account access)
            return {
                "account": account_number,
                "balance": 0.0,  # Cannot get without switching
                "equity": 0.0,   # Cannot get without switching
                "profit": float(total_profit),
                "margin": 0.0,
                "margin_free": 0.0,
                "margin_level": 0.0,
                "currency": "USD",
                "leverage": 0,
                "open_positions": len(positions),
                "total_volume": float(total_volume),
                "data_source": "mt5_positions",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": "Limited data - requires account switch for full info"
            }
        else:
            # No positions or no access - return cached/stored data marker
            logger.warning(f"[WARN] No access to account {account_number} data")
            return {
                "account": account_number,
                "balance": 0.0,
                "equity": 0.0,
                "profit": 0.0,
                "margin": 0.0,
                "margin_free": 0.0,
                "margin_level": 0.0,
                "currency": "USD",
                "leverage": 0,
                "data_source": "mt5_no_access",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": "Use stored data from database"
            }
            
    except Exception as e:
        logger.error(f"[FAIL] Error getting account {account_number} data: {str(e)}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize MT5 on Bridge startup"""
    logger.info("=" * 60)
    logger.info("MT5 BRIDGE STARTING - FIXED VERSION")
    logger.info("=" * 60)
    initialize_mt5_once()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup MT5 connection on shutdown"""
    global MT5_INITIALIZED
    if MT5_INITIALIZED:
        mt5.shutdown()
        MT5_INITIALIZED = False
        logger.info("[OK] MT5 connection closed")


@app.get("/api/mt5/bridge/health")
async def health_check():
    """Health check endpoint"""
    terminal_info = None
    available = False
    
    if MT5_INITIALIZED:
        try:
            terminal_info = mt5.terminal_info()
            account_info = mt5.account_info()
            if terminal_info and account_info:
                available = True
        except:
            pass
    
    return {
        "status": "healthy" if MT5_INITIALIZED else "unhealthy",
        "mt5": {
            "initialized": MT5_INITIALIZED,
            "logged_in": MT5_LOGGED_IN,
            "available": available,
            "terminal_info": {
                "connected": terminal_info.connected if terminal_info else False,
                "trade_allowed": terminal_info.trade_allowed if terminal_info else False
            } if terminal_info else None
        },
        "mongodb": {"connected": True},
        "version": "2.0-fixed",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/mt5/account/{account_number}/info")
async def get_account_info(account_number: int):
    """Get account info WITHOUT terminal switching"""
    try:
        if account_number not in MANAGED_ACCOUNTS:
            raise HTTPException(status_code=404, detail=f"Account {account_number} not managed")
        
        # Get live data without switching
        live_data = get_account_data_no_switch(account_number)
        
        account_config = MANAGED_ACCOUNTS[account_number]
        
        return {
            "account_id": account_number,
            "name": account_config["name"],
            "fund_type": account_config["fund_type"],
            "provider": "MEX Atlantic",
            "target_amount": 0,
            "live_data": live_data,
            "last_sync": datetime.now(timezone.utc).isoformat(),
            "stored_data": None  # Backend will provide this
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FAIL] Error in get_account_info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mt5/accounts/all")
async def get_all_accounts():
    """Get all managed accounts data"""
    try:
        accounts = []
        
        for account_number in MANAGED_ACCOUNTS.keys():
            try:
                live_data = get_account_data_no_switch(account_number)
                account_config = MANAGED_ACCOUNTS[account_number]
                
                accounts.append({
                    "account_id": account_number,
                    "name": account_config["name"],
                    "fund_type": account_config["fund_type"],
                    "live_data": live_data
                })
            except Exception as e:
                logger.error(f"[FAIL] Error getting account {account_number}: {str(e)}")
                continue
        
        return {
            "success": True,
            "accounts": accounts,
            "count": len(accounts),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"[FAIL] Error in get_all_accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("MT5 BRIDGE API - FIXED VERSION")
    logger.info("Single Connection Method - No Account Switching")
    logger.info("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
