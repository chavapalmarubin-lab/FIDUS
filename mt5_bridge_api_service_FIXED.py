# -*- coding: utf-8 -*-
"""
FIDUS MT5 Bridge API Service - FastAPI REST API
Provides REST API endpoints for MT5 account data and real-time information
Runs on port 8000 and serves API requests from the FIDUS backend
DEPLOYMENT LOCATION: C:\mt5_bridge_service\mt5_bridge_api_service.py
Python Version: 3.12
FastAPI Version: 0.115.0+
Last Updated: 2025-01-24 - Fixed master account login for live data
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import MetaTrader5 as mt5
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging
import sys

# Force UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 doesn't have reconfigure
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\mt5_bridge_service\\logs\\api_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    logger.error("[ERROR] MONGODB_URI not found in .env file")
    sys.exit(1)

# MT5 Configuration
MT5_PATH = os.getenv('MT5_PATH', 'C:\\Program Files\\MEX Atlantic MT5 Terminal\\terminal64.exe')
MT5_SERVER = os.getenv('MT5_SERVER', 'MEXAtlantic-Real')
MASTER_ACCOUNT = 886557  # Master account for accessing all accounts

# FastAPI App
app = FastAPI(
    title="FIDUS MT5 Bridge Service",
    description="REST API for MT5 account data and real-time information",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
try:
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    db = mongo_client.get_database()
    logger.info("[OK] MongoDB connected successfully")
except Exception as e:
    logger.error(f"[ERROR] MongoDB connection error: {e}")
    db = None

# Initialize MT5 on startup
@app.on_event("startup")
async def startup_event():
    """Initialize MT5 terminal and login to master account on service startup"""
    try:
        # Step 1: Initialize MT5 Terminal
        if not mt5.initialize(path=MT5_PATH):
            logger.error(f"[ERROR] MT5 initialize() failed, error code: {mt5.last_error()}")
            return
        
        version = mt5.version()
        logger.info(f"[OK] MT5 Terminal initialized: v{version}")
        
        # Step 2: Login to master account to access all accounts
        if db is None:
            logger.error("[ERROR] Cannot login - MongoDB not connected")
            return
        
        try:
            # Get master account credentials from MongoDB
            accounts_collection = db['mt5_accounts']
            master_account_doc = accounts_collection.find_one({'account': MASTER_ACCOUNT})
            
            if not master_account_doc:
                # Try mt5_account_config as fallback
                master_account_doc = db['mt5_account_config'].find_one({'account': MASTER_ACCOUNT})
            
            if not master_account_doc:
                logger.error(f"[ERROR] Master account {MASTER_ACCOUNT} not found in MongoDB")
                return
            
            master_password = master_account_doc.get('password', '')
            
            if not master_password:
                logger.error(f"[ERROR] Password not found for master account {MASTER_ACCOUNT}")
                return
            
            # Login to master account
            logger.info(f"[LOGIN] Attempting login to master account {MASTER_ACCOUNT}...")
            authorized = mt5.login(MASTER_ACCOUNT, password=master_password, server=MT5_SERVER)
            
            if authorized:
                account_info = mt5.account_info()
                if account_info:
                    logger.info(f"[OK] ✅ Master account {MASTER_ACCOUNT} logged in successfully")
                    logger.info(f"[OK] Master account balance: ${account_info.balance:,.2f}")
                    logger.info(f"[OK] Server: {MT5_SERVER}, Trade allowed: {account_info.trade_allowed}")
                else:
                    logger.error(f"[ERROR] Login succeeded but cannot get account info")
            else:
                error_code = mt5.last_error()
                logger.error(f"[ERROR] ❌ Master account login failed, error code: {error_code}")
                logger.error(f"[ERROR] Account: {MASTER_ACCOUNT}, Server: {MT5_SERVER}")
                
        except Exception as e:
            logger.error(f"[ERROR] Master account login error: {e}")
            
    except Exception as e:
        logger.error(f"[ERROR] MT5 initialization error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown MT5 terminal on service shutdown"""
    try:
        mt5.shutdown()
        logger.info("[OK] MT5 Terminal shutdown complete")
    except Exception as e:
        logger.error(f"[ERROR] MT5 shutdown error: {e}")

# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
async def root():
    """Root endpoint with service information and available endpoints"""
    return {
        "service": "FIDUS MT5 Bridge API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "health": "/api/mt5/bridge/health",
            "status": "/api/mt5/status",
            "account_info": "/api/mt5/account/{id}/info",
            "account_balance": "/api/mt5/account/{id}/balance",
            "account_trades": "/api/mt5/account/{id}/trades",
            "accounts_summary": "/api/mt5/accounts/summary",
            "system_status": "/api/mt5/admin/system-status",
            "emergency_restart": "/api/admin/emergency-restart",
            "one_time_setup": "/api/admin/one-time-setup"
        }
    }

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================
@app.get("/api/mt5/bridge/health")
async def bridge_health():
    """
    Health check endpoint for the MT5 bridge service
    Returns service status, MT5 connection, and MongoDB connection
    """
    try:
        # Check MT5 connection
        mt5_initialized = mt5.terminal_info() is not None
        mt5_terminal_info = None
        
        if mt5_initialized:
            terminal_info = mt5.terminal_info()
            if terminal_info:
                mt5_terminal_info = {
                    "connected": terminal_info.connected,
                    "trade_allowed": terminal_info.trade_allowed,
                    "name": terminal_info.name,
                    "company": terminal_info.company,
                    "build": terminal_info.build
                }
        
        # Check MongoDB connection
        mongo_connected = False
        try:
            if db is not None:
                mongo_client.admin.command('ping')
                mongo_connected = True
        except Exception:
            mongo_connected = False
        
        # Overall health status
        healthy = mt5_initialized and mongo_connected
        
        return {
            "status": "healthy" if healthy else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mt5": {
                "available": mt5_initialized,
                "terminal_info": mt5_terminal_info
            },
            "mongodb": {
                "connected": mongo_connected
            },
            "service": {
                "version": "1.0.0",
                "uptime": "Running"
            }
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ============================================
# ADMIN RESTART ENDPOINT (For Auto-Healing)
# ============================================
@app.post("/api/admin/emergency-restart")
async def admin_emergency_restart(token: str = None):
    """
    Emergency restart endpoint for auto-healing system
    Requires ADMIN_SECRET_TOKEN for security
    
    This endpoint allows GitHub Actions to trigger a service restart
    without needing SSH/WinRM access to the VPS
    """
    try:
        # Get admin token from environment
        admin_token = os.getenv('ADMIN_SECRET_TOKEN')
        
        if not admin_token:
            logger.error("[ERROR] ADMIN_SECRET_TOKEN not configured")
            raise HTTPException(status_code=500, detail="Admin token not configured")
        
        # Verify token
        if not token or token != admin_token:
            logger.warning("[SECURITY] Unauthorized restart attempt")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info("[ADMIN] Emergency restart triggered via API")
        
        # Reinitialize MT5 connection with master account login
        try:
            mt5.shutdown()
            logger.info("[RESTART] MT5 shutdown complete")
            
            if not mt5.initialize(path=MT5_PATH):
                logger.error(f"[RESTART] MT5 initialize() failed, error code: {mt5.last_error()}")
                return {
                    "success": False,
                    "message": "MT5 reinitialization failed",
                    "error_code": mt5.last_error(),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            version = mt5.version()
            logger.info(f"[RESTART] MT5 reinitialized: v{version}")
            
            # Re-login to master account
            if db is not None:
                accounts_collection = db['mt5_accounts']
                master_account_doc = accounts_collection.find_one({'account': MASTER_ACCOUNT})
                
                if not master_account_doc:
                    master_account_doc = db['mt5_account_config'].find_one({'account': MASTER_ACCOUNT})
                
                if master_account_doc:
                    master_password = master_account_doc.get('password', '')
                    if master_password:
                        authorized = mt5.login(MASTER_ACCOUNT, password=master_password, server=MT5_SERVER)
                        if authorized:
                            logger.info(f"[RESTART] ✅ Master account {MASTER_ACCOUNT} re-logged in")
                        else:
                            logger.error(f"[RESTART] ❌ Master account re-login failed")
            
        except Exception as e:
            logger.error(f"[RESTART] MT5 restart error: {e}")
            return {
                "success": False,
                "message": "MT5 restart error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Verify MongoDB connection
        mongo_ok = False
        try:
            if db is not None:
                mongo_client.admin.command('ping')
                mongo_ok = True
                logger.info("[RESTART] MongoDB connection verified")
        except Exception as e:
            logger.error(f"[RESTART] MongoDB verification error: {e}")
        
        return {
            "success": True,
            "message": "MT5 Bridge service restarted successfully",
            "mt5_reinitialized": True,
            "mongodb_connected": mongo_ok,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Emergency restart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ONE-TIME SETUP ENDPOINT
# ============================================
@app.post("/api/admin/one-time-setup")
async def one_time_setup(request: Request, setup_key: str = None):
    """
    ONE-TIME SETUP ENDPOINT - Remove after successful configuration!
    Allows remote configuration of ADMIN_SECRET_TOKEN via GitHub Actions.
    
    Security: Requires setup key authentication
    """
    # Security: Verify setup key
    EXPECTED_SETUP_KEY = "FIDUS_SETUP_2025_ONE_TIME_USE_KEY_XYZ"
    
    if not setup_key or setup_key != EXPECTED_SETUP_KEY:
        logger.warning("[SECURITY] Invalid setup attempt from client")
        raise HTTPException(status_code=401, detail="Invalid setup key")
    
    try:
        # Get request body
        request_data = await request.json()
        
        if not request_data or 'admin_token' not in request_data:
            raise HTTPException(status_code=400, detail="admin_token required in request body")
        
        admin_token = request_data['admin_token']
        
        # Validate token length
        if len(admin_token) < 32:
            raise HTTPException(status_code=400, detail="Token too short (minimum 32 characters)")
        
        logger.warning("[SETUP] 🔧 ONE-TIME SETUP: Adding ADMIN_SECRET_TOKEN to .env")
        
        # Check if token already exists
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        token_exists = False
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                content = f.read()
                if 'ADMIN_SECRET_TOKEN' in content:
                    token_exists = True
                    logger.warning("[SETUP] ⚠️  Token already exists in .env")
        
        if not token_exists:
            # Add token to .env
            with open(env_path, 'a') as f:
                f.write(f'\n# Auto-Healing Token (Added: {datetime.now().isoformat()})\n')
                f.write(f'ADMIN_SECRET_TOKEN="{admin_token}"\n')
            
            logger.warning("[SETUP] ✅ ADMIN_SECRET_TOKEN added successfully")
            
        return {
            "status": "success",
            "message": "Token configured successfully" if not token_exists else "Token already exists",
            "token_existed": token_exists,
            "next_steps": [
                "Restart MT5 Bridge service to load new token",
                "Test emergency restart workflow",
                "Remove this setup endpoint for security"
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SETUP] Setup failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MT5 STATUS ENDPOINT
# ============================================
@app.get("/api/mt5/status")
async def mt5_status():
    """
    Returns current MT5 service status and account overview
    """
    try:
        # Check MT5 initialization
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            return {
                "status": "offline",
                "error": "MT5 terminal not initialized",
                "accounts": []
            }
        
        # Get all accounts from MongoDB
        if db is None:
            raise HTTPException(status_code=503, detail="MongoDB not available")
        
        accounts_collection = db['mt5_accounts']
        accounts = list(accounts_collection.find({}, {
            'account': 1,
            'name': 1,
            'fund_type': 1,
            'balance': 1,
            'equity': 1,
            'profit': 1,
            'updated_at': 1,
            '_id': 0
        }))
        
        # Get account count by status
        total_accounts = len(accounts)
        active_accounts = len([a for a in accounts if a.get('balance', 0) > 0])
        
        return {
            "status": "online",
            "mt5_initialized": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "accounts": {
                "total": total_accounts,
                "active": active_accounts,
                "list": accounts
            },
            "server": MT5_SERVER,
            "terminal": {
                "connected": terminal_info.connected if terminal_info else False,
                "trade_allowed": terminal_info.trade_allowed if terminal_info else False
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] MT5 status error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ============================================
# ACCOUNT INFO BY ID
# ============================================
@app.get("/api/mt5/account/{account_id}/info")
async def get_account_info(account_id: int):
    """
    Get detailed information for a specific MT5 account
    Retrieves both MT5 live data and MongoDB stored data
    """
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="MongoDB not available")
        
        # Get account from MongoDB
        accounts_collection = db['mt5_accounts']
        account_doc = accounts_collection.find_one({'account': account_id})
        
        if not account_doc:
            # Try mt5_account_config collection as fallback
            account_doc = db['mt5_account_config'].find_one({'account': account_id})
            
        if not account_doc:
            raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
        
        # Try to get live MT5 data for this account
        live_data = None
        
        # Check if MT5 is initialized
        if mt5.terminal_info() is not None:
            password = account_doc.get('password', '')
            
            if password:
                try:
                    authorized = mt5.login(account_id, password=password, server=MT5_SERVER)
                    
                    if authorized:
                        account_info = mt5.account_info()
                        if account_info:
                            live_data = {
                                "balance": account_info.balance,
                                "equity": account_info.equity,
                                "profit": account_info.profit,
                                "margin": account_info.margin,
                                "margin_free": account_info.margin_free,
                                "margin_level": account_info.margin_level,
                                "leverage": account_info.leverage,
                                "currency": account_info.currency,
                                "trade_allowed": account_info.trade_allowed
                            }
                except Exception as e:
                    logger.warning(f"[WARNING] Could not get live data for {account_id}: {e}")
        
        # Combine MongoDB data with live data
        result = {
            "account_id": account_id,
            "name": account_doc.get('name'),
            "fund_type": account_doc.get('fund_type') or account_doc.get('fund_code'),
            "provider": account_doc.get('provider', 'MEXAtlantic'),
            "target_amount": account_doc.get('target_amount'),
            "live_data": live_data,
            "last_sync": account_doc.get('updated_at') or account_doc.get('last_sync'),
            "stored_data": {
                "balance": account_doc.get('balance'),
                "equity": account_doc.get('equity'),
                "profit": account_doc.get('profit')
            }
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Get account info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ACCOUNT BALANCE
# ============================================
@app.get("/api/mt5/account/{account_id}/balance")
async def get_account_balance(account_id: int):
    """
    Get current balance for a specific account
    """
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="MongoDB not available")
        
        accounts_collection = db['mt5_accounts']
        account = accounts_collection.find_one(
            {'account': account_id},
            {'balance': 1, 'equity': 1, 'profit': 1, 'updated_at': 1, '_id': 0}
        )
        
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
        
        return {
            "account_id": account_id,
            "balance": account.get('balance', 0),
            "equity": account.get('equity', 0),
            "profit": account.get('profit', 0),
            "last_updated": account.get('updated_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Get account balance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ACCOUNT TRADES
# ============================================
@app.get("/api/mt5/account/{account_id}/trades")
async def get_account_trades(account_id: int, limit: int = 100):
    """
    Get recent trades/deals for a specific account
    """
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="MongoDB not available")
        
        # Try mt5_deals_history collection first
        trades_collection = db['mt5_deals_history']
        
        trades = list(trades_collection.find(
            {'account_number': account_id},
            {'_id': 0}
        ).sort('time', -1).limit(limit))
        
        # If no trades found, try trades collection
        if len(trades) == 0:
            trades_collection = db['trades']
            trades = list(trades_collection.find(
                {'account_id': account_id},
                {'_id': 0}
            ).sort('close_time', -1).limit(limit))
        
        return {
            "account_id": account_id,
            "count": len(trades),
            "trades": trades
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Get account trades error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# GET ALL ACCOUNTS
# ============================================
@app.get("/api/mt5/accounts")
async def get_all_accounts():
    """
    Get all MT5 accounts from MongoDB
    Returns list of all accounts with their current data
    """
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="MongoDB not available")
        
        accounts_collection = db['mt5_accounts']
        
        # Get all accounts
        accounts = list(accounts_collection.find({}, {'_id': 0}).sort('account', 1))
        
        return accounts
        
    except Exception as e:
        logger.error(f"[ERROR] Get all accounts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ALL ACCOUNTS SUMMARY
# ============================================
@app.get("/api/mt5/accounts/summary")
async def get_accounts_summary():
    """
    Get summary of all MT5 accounts
    """
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="MongoDB not available")
        
        accounts_collection = db['mt5_accounts']
        
        # Get all accounts
        accounts = list(accounts_collection.find({}, {'_id': 0}))
        
        # Calculate totals
        total_balance = sum(acc.get('balance', 0) for acc in accounts)
        total_equity = sum(acc.get('equity', 0) for acc in accounts)
        total_profit = sum(acc.get('profit', 0) for acc in accounts)
        
        # Group by fund type
        by_fund_type = {}
        for acc in accounts:
            fund_type = acc.get('fund_type') or acc.get('fund_code', 'UNKNOWN')
            if fund_type not in by_fund_type:
                by_fund_type[fund_type] = {
                    'count': 0,
                    'total_balance': 0,
                    'total_equity': 0,
                    'total_profit': 0,
                    'accounts': []
                }
            
            by_fund_type[fund_type]['count'] += 1
            by_fund_type[fund_type]['total_balance'] += acc.get('balance', 0)
            by_fund_type[fund_type]['total_equity'] += acc.get('equity', 0)
            by_fund_type[fund_type]['total_profit'] += acc.get('profit', 0)
            by_fund_type[fund_type]['accounts'].append({
                'account': acc.get('account'),
                'name': acc.get('name'),
                'balance': acc.get('balance'),
                'equity': acc.get('equity'),
                'profit': acc.get('profit')
            })
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "totals": {
                "accounts": len(accounts),
                "balance": total_balance,
                "equity": total_equity,
                "profit": total_profit
            },
            "by_fund_type": by_fund_type,
            "accounts": accounts
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Get accounts summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ADMIN SYSTEM STATUS
# ============================================
@app.get("/api/mt5/admin/system-status")
async def get_system_status():
    """
    Get comprehensive system status (admin endpoint)
    """
    try:
        # MT5 Status
        terminal_info = mt5.terminal_info()
        mt5_status = {
            "initialized": terminal_info is not None,
            "connected": terminal_info.connected if terminal_info else False,
            "trade_allowed": terminal_info.trade_allowed if terminal_info else False
        }
        
        # MongoDB Status
        mongo_status = {
            "connected": db is not None
        }
        
        if db is not None:
            try:
                mongo_client.admin.command('ping')
                mongo_status["ping"] = "success"
                
                # Get collection stats
                mongo_status["collections"] = {
                    "mt5_accounts": db['mt5_accounts'].count_documents({}),
                    "mt5_deals_history": db['mt5_deals_history'].count_documents({}),
                    "mt5_account_config": db['mt5_account_config'].count_documents({})
                }
            except Exception as e:
                mongo_status["error"] = str(e)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": {
                "name": "FIDUS MT5 Bridge API",
                "version": "1.0.0",
                "status": "running"
            },
            "mt5": mt5_status,
            "mongodb": mongo_status,
            "overall_health": "healthy" if (mt5_status["initialized"] and mongo_status["connected"]) else "degraded"
        }
        
    except Exception as e:
        logger.error(f"[ERROR] System status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("FIDUS MT5 BRIDGE API SERVICE STARTING")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print(f"MT5 Path: {MT5_PATH}")
    print(f"MT5 Server: {MT5_SERVER}")
    print(f"Master Account: {MASTER_ACCOUNT}")
    print('MongoDB: Connected' if db is not None else 'MongoDB: Not Connected')
    print("Port: 8000")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
