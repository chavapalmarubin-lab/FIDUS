#!/usr/bin/env python3
"""
MT5 Windows Bridge Service
==========================

This service runs on Windows VM with MetaTrader5 installed.
It provides REST API access to MT5 data for the Linux application.

DEPLOYMENT: Copy this file to Windows VM and run:
pip install fastapi uvicorn MetaTrader5 python-dotenv
python mt5_windows_bridge_service.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import MetaTrader5 as mt5
import uvicorn
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MT5 Windows Bridge Service", version="1.0.0")

# CORS middleware for Linux application access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact Linux app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global connection status
connected_accounts = {}
bridge_status = {
    'service_started': datetime.now(timezone.utc),
    'mt5_initialized': False,
    'active_connections': 0
}

@app.on_event("startup")
async def startup_event():
    """Initialize MT5 on service startup"""
    logger.info("🚀 Starting MT5 Windows Bridge Service")
    
    # Initialize MetaTrader5
    if mt5.initialize():
        bridge_status['mt5_initialized'] = True
        logger.info("✅ MetaTrader5 initialized successfully")
    else:
        logger.error("❌ Failed to initialize MetaTrader5")
        raise Exception("MetaTrader5 initialization failed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on service shutdown"""
    logger.info("🛑 Shutting down MT5 Windows Bridge Service")
    mt5.shutdown()

@app.get("/")
async def root():
    """Service health check"""
    return {
        "service": "MT5 Windows Bridge",
        "status": "running",
        "mt5_initialized": bridge_status['mt5_initialized'],
        "active_connections": bridge_status['active_connections'],
        "uptime_hours": (datetime.now(timezone.utc) - bridge_status['service_started']).total_seconds() / 3600
    }

@app.post("/api/mt5/connect")
async def connect_mt5_account(connection_data: dict):
    """Connect to MT5 account and store connection"""
    
    mt5_login = connection_data.get('mt5_login')
    password = connection_data.get('password')
    server = connection_data.get('server')
    
    if not all([mt5_login, password, server]):
        raise HTTPException(status_code=400, detail="Missing required fields: mt5_login, password, server")
    
    try:
        logger.info(f"🔌 Connecting to MT5 account {mt5_login} on {server}")
        
        # Connect to MT5 account
        if not mt5.login(mt5_login, password=password, server=server):
            error_code = mt5.last_error()
            raise HTTPException(status_code=400, detail=f"MT5 login failed: {error_code}")
        
        # Store connection info
        connected_accounts[str(mt5_login)] = {
            'login': mt5_login,
            'server': server,
            'connected_at': datetime.now(timezone.utc),
            'last_accessed': datetime.now(timezone.utc)
        }
        
        bridge_status['active_connections'] = len(connected_accounts)
        
        logger.info(f"✅ Successfully connected to MT5 account {mt5_login}")
        
        return {
            'success': True,
            'message': f'Connected to MT5 account {mt5_login}',
            'server': server,
            'connected_at': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Connection failed for {mt5_login}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")

@app.get("/api/mt5/account/{mt5_login}/info")
async def get_account_info(mt5_login: int):
    """Get MT5 account information"""
    
    login_str = str(mt5_login)
    if login_str not in connected_accounts:
        raise HTTPException(status_code=404, detail=f"Account {mt5_login} not connected")
    
    try:
        # Reconnect to ensure fresh connection
        account_info = connected_accounts[login_str]
        if not mt5.login(mt5_login, server=account_info.get('server', '')):
            raise HTTPException(status_code=500, detail="Failed to reconnect to MT5 account")
        
        # Get account information
        account_data = mt5.account_info()
        if account_data is None:
            raise HTTPException(status_code=500, detail="Failed to get account info from MT5")
        
        # Update last accessed time
        connected_accounts[login_str]['last_accessed'] = datetime.now(timezone.utc)
        
        return {
            'login': mt5_login,
            'balance': account_data.balance,
            'equity': account_data.equity,
            'margin': account_data.margin,
            'free_margin': account_data.margin_free,
            'profit': account_data.profit,
            'currency': account_data.currency,
            'leverage': account_data.leverage,
            'server': account_data.server,
            'company': account_data.company,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get account info for {mt5_login}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get account info: {str(e)}")

@app.get("/api/mt5/account/{mt5_login}/history")
async def get_account_history(mt5_login: int, days: int = 365):
    """Get MT5 account transaction history"""
    
    login_str = str(mt5_login)
    if login_str not in connected_accounts:
        raise HTTPException(status_code=404, detail=f"Account {mt5_login} not connected")
    
    try:
        # Reconnect to account
        account_info = connected_accounts[login_str]
        if not mt5.login(mt5_login, server=account_info.get('server', '')):
            raise HTTPException(status_code=500, detail="Failed to reconnect to MT5 account")
        
        # Get deal history
        from_date = datetime.now() - timedelta(days=days)
        to_date = datetime.now()
        
        deals = mt5.history_deals_get(from_date, to_date)
        
        if deals is None:
            return {
                'login': mt5_login,
                'deposits': [],
                'withdrawals': [],
                'total_deposits': 0,
                'total_withdrawals': 0,
                'history_days': days
            }
        
        # Process deals
        deposits = []
        withdrawals = []
        total_deposits = 0
        total_withdrawals = 0
        
        for deal in deals:
            if deal.type == mt5.DEAL_TYPE_BALANCE:
                deal_time = datetime.fromtimestamp(deal.time, timezone.utc)
                
                if deal.profit > 0:  # Deposit
                    deposit_record = {
                        'date': deal_time.isoformat(),
                        'amount': deal.profit,
                        'comment': deal.comment,
                        'ticket': deal.ticket
                    }
                    deposits.append(deposit_record)
                    total_deposits += deal.profit
                    
                elif deal.profit < 0:  # Withdrawal
                    withdrawal_record = {
                        'date': deal_time.isoformat(),
                        'amount': abs(deal.profit),
                        'comment': deal.comment,
                        'ticket': deal.ticket
                    }
                    withdrawals.append(withdrawal_record)
                    total_withdrawals += abs(deal.profit)
        
        # Sort by date
        deposits.sort(key=lambda x: x['date'])
        withdrawals.sort(key=lambda x: x['date'])
        
        # Update last accessed time
        connected_accounts[login_str]['last_accessed'] = datetime.now(timezone.utc)
        
        return {
            'login': mt5_login,
            'deposits': deposits,
            'withdrawals': withdrawals,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'deposit_count': len(deposits),
            'withdrawal_count': len(withdrawals),
            'first_deposit_date': deposits[0]['date'] if deposits else None,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'history_days': days
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get history for {mt5_login}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/api/mt5/account/{mt5_login}/deposits")
async def get_account_deposits(mt5_login: int):
    """Get only deposit history for an account"""
    
    history_data = await get_account_history(mt5_login)
    
    return {
        'login': mt5_login,
        'deposits': history_data['deposits'],
        'total_deposits': history_data['total_deposits'],
        'deposit_count': history_data['deposit_count'],
        'first_deposit_date': history_data['first_deposit_date'],
        'last_updated': history_data['last_updated']
    }

@app.get("/api/mt5/status")
async def get_bridge_status():
    """Get bridge service status"""
    
    return {
        'service': 'MT5 Windows Bridge',
        'status': 'running',
        'bridge_info': bridge_status,
        'connected_accounts': {
            login: {
                'server': info['server'],
                'connected_at': info['connected_at'].isoformat(),
                'last_accessed': info['last_accessed'].isoformat()
            }
            for login, info in connected_accounts.items()
        },
        'mt5_terminal_info': mt5.terminal_info()._asdict() if mt5.terminal_info() else None
    }

@app.post("/api/mt5/disconnect/{mt5_login}")
async def disconnect_account(mt5_login: int):
    """Disconnect MT5 account"""
    
    login_str = str(mt5_login)
    if login_str in connected_accounts:
        del connected_accounts[login_str]
        bridge_status['active_connections'] = len(connected_accounts)
        
        return {
            'success': True,
            'message': f'Disconnected account {mt5_login}'
        }
    else:
        raise HTTPException(status_code=404, detail=f"Account {mt5_login} not connected")

if __name__ == "__main__":
    """Run the bridge service"""
    
    print("🚀 Starting MT5 Windows Bridge Service")
    print("=" * 50)
    print("REQUIREMENTS:")
    print("1. Windows OS with MetaTrader5 terminal installed")
    print("2. Python packages: fastapi uvicorn MetaTrader5 python-dotenv")
    print("3. Network access for Linux application")
    print()
    print("SERVICE ENDPOINTS:")
    print("- POST /api/mt5/connect - Connect to MT5 account")
    print("- GET  /api/mt5/account/{login}/info - Get account info")
    print("- GET  /api/mt5/account/{login}/history - Get transaction history")
    print("- GET  /api/mt5/account/{login}/deposits - Get deposit history")
    print("- GET  /api/mt5/status - Get bridge status")
    print()
    
    # Get port from environment or use default
    port = int(os.environ.get('BRIDGE_PORT', 8080))
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )