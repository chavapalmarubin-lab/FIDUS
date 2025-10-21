# -*- coding: utf-8 -*-
"""
FIDUS MT5 Bridge API Service - FastAPI REST API
Provides REST API endpoints for MT5 account data and real-time information
Runs on port 8000 and serves API requests from the FIDUS backend

DEPLOYMENT LOCATION: C:\mt5_bridge_service\mt5_bridge_api_service.py
Python Version: 3.12
FastAPI Version: 0.115.0+

Last Updated: 2025-01-19 - Production deployment with automated GitHub Actions
"""

from fastapi import FastAPI, HTTPException
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
    """Initialize MT5 terminal on service startup"""
    try:
        if not mt5.initialize(path=MT5_PATH):
            logger.error(f"[ERROR] MT5 initialize() failed, error code: {mt5.last_error()}")
        else:
            version = mt5.version()
            logger.info(f"[OK] MT5 Terminal initialized: v{version}")
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
            "system_status": "/api/mt5/admin/system-status"
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
    print('MongoDB: Connected' if db is not None else 'MongoDB: Not Connected')
    print(f"Port: 8000")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
# TRIGGER DEPLOYMENT - Sun Oct 19 19:44:16 UTC 2025
