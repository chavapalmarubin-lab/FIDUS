"""
MT5 Bridge Service - FastAPI Service for Windows VPS
Provides REST API interface to MetaTrader5 Python API
Designed to run on ForexVPS.net Windows VPS
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import os
from datetime import datetime, timezone
import asyncio
import uvicorn

# Import MetaTrader5 (only works on Windows)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 not available - mock mode enabled")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="FIDUS MT5 Bridge Service",
    description="REST API Bridge between FIDUS Platform and MetaTrader5",
    version="1.0.0"
)

# CORS configuration for FIDUS backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fidus-invest.emergent.host", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MT5LoginRequest(BaseModel):
    login: int
    password: str
    server: str

class HistoryRequest(BaseModel):
    login: int
    from_date: Optional[str] = None
    to_date: Optional[str] = None

class DealsRequest(BaseModel):
    login: int
    from_date: Optional[str] = None
    to_date: Optional[str] = None

# Security
API_KEY = os.environ.get('MT5_BRIDGE_API_KEY', 'dev-key-change-in-production')

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Global MT5 state
mt5_initialized = False
connected_accounts = {}

@app.on_startup
async def startup_event():
    """Initialize MT5 on startup"""
    global mt5_initialized
    
    if MT5_AVAILABLE:
        try:
            if mt5.initialize():
                mt5_initialized = True
                logger.info("✅ MT5 initialized successfully on startup")
            else:
                logger.error("❌ MT5 initialization failed on startup")
        except Exception as e:
            logger.error(f"❌ MT5 startup error: {e}")
    else:
        logger.warning("⚠️ MT5 not available - running in mock mode")

@app.on_shutdown
async def shutdown_event():
    """Cleanup MT5 on shutdown"""
    if MT5_AVAILABLE and mt5_initialized:
        mt5.shutdown()
        logger.info("MT5 shutdown completed")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'success': True,
        'status': 'healthy',
        'mt5_available': MT5_AVAILABLE,
        'mt5_initialized': mt5_initialized,
        'connected_accounts': len(connected_accounts),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    }

@app.post("/api/mt5/initialize")
async def initialize_mt5(api_key: str = Depends(verify_api_key)):
    """Initialize MT5 connection"""
    global mt5_initialized
    
    if not MT5_AVAILABLE:
        return {
            'success': False,
            'error': 'MetaTrader5 not available on this system',
            'mock_mode': True
        }
    
    try:
        if not mt5_initialized:
            if mt5.initialize():
                mt5_initialized = True
                logger.info("MT5 initialized via API")
            else:
                return {
                    'success': False,
                    'error': 'MT5 initialization failed',
                    'last_error': mt5.last_error()
                }
        
        return {
            'success': True,
            'initialized': mt5_initialized,
            'version': mt5.version() if hasattr(mt5, 'version') else 'Unknown'
        }
        
    except Exception as e:
        logger.error(f"MT5 initialization error: {e}")
        return {'success': False, 'error': str(e)}

@app.post("/api/mt5/login")
async def login_mt5_account(request: MT5LoginRequest, api_key: str = Depends(verify_api_key)):
    """Login to MT5 account"""
    
    if not MT5_AVAILABLE:
        # Mock response for development
        return {
            'success': True,
            'mock_mode': True,
            'login': request.login,
            'server': request.server,
            'message': 'Mock MT5 login successful'
        }
    
    try:
        # Ensure MT5 is initialized
        if not mt5_initialized:
            await initialize_mt5()
        
        # Attempt login
        if mt5.login(request.login, password=request.password, server=request.server):
            connected_accounts[request.login] = {
                'server': request.server,
                'connected_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ MT5 login successful: {request.login} on {request.server}")
            
            return {
                'success': True,
                'login': request.login,
                'server': request.server,
                'connected_at': connected_accounts[request.login]['connected_at']
            }
        else:
            error = mt5.last_error()
            logger.error(f"❌ MT5 login failed: {request.login} - {error}")
            
            return {
                'success': False,
                'error': f'Login failed: {error}',
                'login': request.login,
                'server': request.server
            }
            
    except Exception as e:
        logger.error(f"MT5 login exception: {e}")
        return {'success': False, 'error': str(e)}

@app.get("/api/mt5/account/{login}/info")
async def get_account_info(login: int, api_key: str = Depends(verify_api_key)):
    """Get MT5 account information"""
    
    if not MT5_AVAILABLE:
        # Mock response
        return {
            'success': True,
            'mock_mode': True,
            'login': login,
            'balance': 100000.00,
            'equity': 105000.00,
            'profit': 5000.00,
            'margin': 2000.00,
            'free_margin': 98000.00,
            'margin_level': 5250.00,
            'currency': 'USD'
        }
    
    try:
        account_info = mt5.account_info()
        
        if account_info is None:
            return {
                'success': False,
                'error': 'Failed to get account info',
                'last_error': mt5.last_error()
            }
        
        return {
            'success': True,
            'login': account_info.login,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'profit': account_info.profit,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'margin_level': account_info.margin_level,
            'currency': account_info.currency,
            'server': account_info.server,
            'leverage': account_info.leverage,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get account info error: {e}")
        return {'success': False, 'error': str(e)}

@app.post("/api/mt5/history")
async def get_account_history(request: HistoryRequest, api_key: str = Depends(verify_api_key)):
    """Get account trading history"""
    
    if not MT5_AVAILABLE:
        # Mock response
        return {
            'success': True,
            'mock_mode': True,
            'login': request.login,
            'history_count': 50,
            'from_date': request.from_date,
            'to_date': request.to_date,
            'message': 'Mock history data - real data requires Windows MT5'
        }
    
    try:
        # Parse dates
        from_date = datetime.fromisoformat(request.from_date.replace('Z', '+00:00')) if request.from_date else datetime(2020, 1, 1)
        to_date = datetime.fromisoformat(request.to_date.replace('Z', '+00:00')) if request.to_date else datetime.now()
        
        # Get history orders
        history_orders = mt5.history_orders_get(from_date, to_date)
        
        if history_orders is None:
            return {
                'success': False,
                'error': 'Failed to get history',
                'last_error': mt5.last_error()
            }
        
        # Convert to list of dicts
        orders = []
        for order in history_orders:
            orders.append({
                'ticket': order.ticket,
                'time_setup': order.time_setup,
                'time_done': order.time_done,
                'type': order.type,
                'state': order.state,
                'volume': order.volume_initial,
                'price_open': order.price_open,
                'price_current': order.price_current,
                'profit': order.profit,
                'symbol': order.symbol,
                'comment': order.comment
            })
        
        return {
            'success': True,
            'login': request.login,
            'orders': orders,
            'count': len(orders),
            'from_date': request.from_date,
            'to_date': request.to_date
        }
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        return {'success': False, 'error': str(e)}

@app.post("/api/mt5/deals")
async def get_account_deals(request: DealsRequest, api_key: str = Depends(verify_api_key)):
    """Get account deals (for deposits/withdrawals analysis)"""
    
    if not MT5_AVAILABLE:
        # Mock response with sample deposit
        return {
            'success': True,
            'mock_mode': True,
            'login': request.login,
            'deals': [
                {
                    'ticket': 123456,
                    'time': 1714521600,  # 2024-05-01
                    'type': 2,  # DEAL_TYPE_BALANCE
                    'profit': 100000.00,  # Deposit amount
                    'comment': 'Deposit'
                }
            ],
            'first_deposit_date': '2024-05-01T00:00:00Z',
            'total_deposits': 100000.00
        }
    
    try:
        # Parse dates
        from_date = datetime.fromisoformat(request.from_date.replace('Z', '+00:00')) if request.from_date else datetime(2020, 1, 1)
        to_date = datetime.fromisoformat(request.to_date.replace('Z', '+00:00')) if request.to_date else datetime.now()
        
        # Get deals history
        deals = mt5.history_deals_get(from_date, to_date)
        
        if deals is None:
            return {
                'success': False,
                'error': 'Failed to get deals',
                'last_error': mt5.last_error()
            }
        
        # Process deals to find deposits/withdrawals
        processed_deals = []
        deposits = []
        withdrawals = []
        first_deposit_date = None
        
        for deal in deals:
            deal_dict = {
                'ticket': deal.ticket,
                'time': deal.time,
                'type': deal.type,
                'profit': deal.profit,
                'volume': deal.volume,
                'symbol': deal.symbol,
                'comment': deal.comment
            }
            processed_deals.append(deal_dict)
            
            # Check for balance operations (deposits/withdrawals)
            if deal.type == 2:  # DEAL_TYPE_BALANCE
                deal_time = datetime.fromtimestamp(deal.time, tz=timezone.utc)
                
                if deal.profit > 0:  # Deposit
                    deposits.append({
                        'date': deal_time.isoformat(),
                        'amount': deal.profit,
                        'comment': deal.comment
                    })
                    
                    if first_deposit_date is None or deal_time < datetime.fromisoformat(first_deposit_date.replace('Z', '+00:00')):
                        first_deposit_date = deal_time.isoformat()
                
                elif deal.profit < 0:  # Withdrawal
                    withdrawals.append({
                        'date': deal_time.isoformat(),
                        'amount': abs(deal.profit),
                        'comment': deal.comment
                    })
        
        return {
            'success': True,
            'login': request.login,
            'deals': processed_deals,
            'deposits': deposits,
            'withdrawals': withdrawals,
            'first_deposit_date': first_deposit_date,
            'total_deposits': sum(d['amount'] for d in deposits),
            'total_withdrawals': sum(w['amount'] for w in withdrawals),
            'count': len(processed_deals)
        }
        
    except Exception as e:
        logger.error(f"Get deals error: {e}")
        return {'success': False, 'error': str(e)}

@app.get("/api/mt5/account/{login}/positions")
async def get_positions(login: int, api_key: str = Depends(verify_api_key)):
    """Get current open positions"""
    
    if not MT5_AVAILABLE:
        return {
            'success': True,
            'mock_mode': True,
            'positions': [],
            'count': 0
        }
    
    try:
        positions = mt5.positions_get()
        
        if positions is None:
            return {
                'success': False,
                'error': 'Failed to get positions',
                'last_error': mt5.last_error()
            }
        
        positions_list = []
        for pos in positions:
            positions_list.append({
                'ticket': pos.ticket,
                'time': pos.time,
                'type': pos.type,
                'volume': pos.volume,
                'symbol': pos.symbol,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'swap': pos.swap,
                'comment': pos.comment
            })
        
        return {
            'success': True,
            'positions': positions_list,
            'count': len(positions_list)
        }
        
    except Exception as e:
        logger.error(f"Get positions error: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )