"""
FIDUS MT5 Bridge Service - Production Version
FastAPI service for Windows VPS with comprehensive MT5 integration
"""

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import logging
import os
import asyncio
from datetime import datetime, timezone, timedelta
import uvicorn
from pathlib import Path
import json
import sys

# Import MetaTrader5 (Windows only)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    print("✅ MetaTrader5 package imported successfully")
except ImportError as e:
    MT5_AVAILABLE = False
    print(f"⚠️ MetaTrader5 not available: {e}")

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"mt5_bridge_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="FIDUS MT5 Bridge Service - Production",
    description="REST API Bridge between FIDUS Platform and MetaTrader5",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT", "prod") == "dev" else None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fidus-invest.emergent.host",
        "http://localhost:8001",
        "http://127.0.0.1:8001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MT5Credentials(BaseModel):
    account: int = Field(..., description="MT5 account number")
    password: str = Field(..., description="MT5 account password")
    server: str = Field(..., description="MT5 broker server")

class OrderRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., EURUSD)")
    volume: float = Field(..., gt=0, description="Trade volume in lots")
    order_type: str = Field(..., description="Order type: BUY or SELL")
    sl: Optional[float] = Field(0.0, description="Stop loss price")
    tp: Optional[float] = Field(0.0, description="Take profit price")
    comment: Optional[str] = Field("FIDUS", description="Order comment")
    deviation: Optional[int] = Field(20, description="Price deviation in points")

class HistoryRequest(BaseModel):
    date_from: str = Field(..., description="Start date (YYYY-MM-DD)")
    date_to: str = Field(..., description="End date (YYYY-MM-DD)")
    account: Optional[int] = Field(None, description="MT5 account number")

class SymbolRequest(BaseModel):
    symbol: str = Field(..., description="Symbol to get info for")

# Security
API_KEY = os.environ.get('MT5_BRIDGE_API_KEY', 'fidus-mt5-bridge-key-2025-secure')
if API_KEY == 'fidus-mt5-bridge-key-2025-secure':
    logger.warning("⚠️ Using default API key - change in production!")

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Global MT5 state
class MT5State:
    def __init__(self):
        self.initialized = False
        self.connected_accounts = {}
        self.last_error = None
        self.initialization_time = None

mt5_state = MT5State()

# MT5 Connection Manager
class MT5Manager:
    def __init__(self):
        self.initialize_mt5()
    
    def initialize_mt5(self) -> bool:
        """Initialize MT5 connection"""
        try:
            if not MT5_AVAILABLE:
                logger.error("MetaTrader5 package not available")
                return False
            
            if mt5.initialize():
                mt5_state.initialized = True
                mt5_state.initialization_time = datetime.now(timezone.utc)
                logger.info("✅ MT5 initialized successfully")
                
                # Log MT5 terminal info
                terminal_info = mt5.terminal_info()
                if terminal_info:
                    logger.info(f"MT5 Terminal: {terminal_info.name} v{terminal_info.build}")
                    logger.info(f"Terminal path: {terminal_info.path}")
                
                return True
            else:
                error = mt5.last_error()
                mt5_state.last_error = error
                logger.error(f"❌ MT5 initialization failed: {error}")
                return False
        except Exception as e:
            logger.error(f"❌ MT5 initialization exception: {e}")
            mt5_state.last_error = str(e)
            return False
    
    def is_connected(self) -> bool:
        """Check if MT5 is properly connected"""
        if not MT5_AVAILABLE or not mt5_state.initialized:
            return False
        
        try:
            terminal_info = mt5.terminal_info()
            return terminal_info is not None and terminal_info.connected
        except:
            return False
    
    def get_terminal_info(self) -> Dict:
        """Get MT5 terminal information"""
        try:
            if not self.is_connected():
                return {"error": "MT5 not connected"}
            
            terminal_info = mt5.terminal_info()
            if not terminal_info:
                return {"error": "Failed to get terminal info"}
            
            return {
                "name": terminal_info.name,
                "build": terminal_info.build,
                "path": terminal_info.path,
                "data_path": terminal_info.data_path,
                "commondata_path": terminal_info.commondata_path,
                "connected": terminal_info.connected,
                "trade_allowed": terminal_info.trade_allowed,
                "tradeapi_disabled": terminal_info.tradeapi_disabled,
                "ping_last": terminal_info.ping_last,
                "community_account": terminal_info.community_account,
                "community_connection": terminal_info.community_connection
            }
        except Exception as e:
            logger.error(f"Get terminal info error: {e}")
            return {"error": str(e)}
    
    def login(self, account: int, password: str, server: str) -> Dict:
        """Login to MT5 account"""
        try:
            if not mt5_state.initialized:
                self.initialize_mt5()
            
            if not mt5_state.initialized:
                return {"success": False, "error": "MT5 not initialized"}
            
            # Attempt login
            authorized = mt5.login(account, password=password, server=server)
            
            if authorized:
                # Store connection info
                mt5_state.connected_accounts[account] = {
                    "server": server,
                    "connected_at": datetime.now(timezone.utc).isoformat(),
                    "last_ping": datetime.now(timezone.utc).isoformat()
                }
                
                logger.info(f"✅ Successfully logged in to account {account} on {server}")
                
                # Get account info to verify
                account_info = mt5.account_info()
                if account_info:
                    return {
                        "success": True,
                        "account": account,
                        "server": server,
                        "currency": account_info.currency,
                        "balance": float(account_info.balance),
                        "equity": float(account_info.equity),
                        "login_time": mt5_state.connected_accounts[account]["connected_at"]
                    }
                else:
                    return {"success": True, "account": account, "server": server}
            else:
                error = mt5.last_error()
                logger.error(f"❌ Login failed for account {account}: {error}")
                return {"success": False, "error": f"Login failed: {error}"}
        except Exception as e:
            logger.error(f"Login exception: {e}")
            return {"success": False, "error": str(e)}
    
    def get_account_info(self) -> Dict:
        """Get current account information"""
        try:
            if not self.is_connected():
                return {"error": "MT5 not connected"}
            
            account_info = mt5.account_info()
            if not account_info:
                error = mt5.last_error()
                return {"error": f"Failed to get account info: {error}"}
            
            return {
                "login": account_info.login,
                "trade_mode": account_info.trade_mode,
                "leverage": account_info.leverage,
                "limit_orders": account_info.limit_orders,
                "margin_so_mode": account_info.margin_so_mode,
                "trade_allowed": account_info.trade_allowed,
                "trade_expert": account_info.trade_expert,
                "margin_mode": account_info.margin_mode,
                "currency_digits": account_info.currency_digits,
                "fifo_close": account_info.fifo_close,
                "balance": float(account_info.balance),
                "credit": float(account_info.credit),
                "profit": float(account_info.profit),
                "equity": float(account_info.equity),
                "margin": float(account_info.margin),
                "margin_free": float(account_info.margin_free),
                "margin_level": float(account_info.margin_level) if account_info.margin_level != float('inf') else 0,
                "margin_so_call": float(account_info.margin_so_call),
                "margin_so_so": float(account_info.margin_so_so),
                "margin_initial": float(account_info.margin_initial),
                "margin_maintenance": float(account_info.margin_maintenance),
                "assets": float(account_info.assets),
                "liabilities": float(account_info.liabilities),
                "commission_blocked": float(account_info.commission_blocked),
                "name": account_info.name,
                "server": account_info.server,
                "currency": account_info.currency,
                "company": account_info.company
            }
        except Exception as e:
            logger.error(f"Get account info error: {e}")
            return {"error": str(e)}

# Initialize MT5 manager
mt5_manager = MT5Manager()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize MT5 on startup"""
    logger.info("🚀 Starting FIDUS MT5 Bridge Service")
    logger.info(f"MT5 Available: {MT5_AVAILABLE}")
    logger.info(f"API Key configured: {'Yes' if API_KEY else 'No'}")
    
    if MT5_AVAILABLE:
        success = mt5_manager.initialize_mt5()
        logger.info(f"MT5 Initialization: {'Success' if success else 'Failed'}")
    
    logger.info("✅ FIDUS MT5 Bridge Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down FIDUS MT5 Bridge Service")
    
    if MT5_AVAILABLE and mt5_state.initialized:
        try:
            mt5.shutdown()
            logger.info("MT5 connection closed")
        except Exception as e:
            logger.error(f"Error during MT5 shutdown: {e}")
    
    logger.info("✅ FIDUS MT5 Bridge Service stopped")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "FIDUS MT5 Bridge Service",
        "version": "1.0.0",
        "status": "running",
        "mt5_available": MT5_AVAILABLE,
        "mt5_initialized": mt5_state.initialized,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_data = {
        "status": "healthy" if mt5_manager.is_connected() else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mt5_available": MT5_AVAILABLE,
        "mt5_initialized": mt5_state.initialized,
        "mt5_connected": mt5_manager.is_connected(),
        "connected_accounts": len(mt5_state.connected_accounts),
        "uptime": None,
        "terminal_info": None,
        "last_error": mt5_state.last_error
    }
    
    # Calculate uptime
    if mt5_state.initialization_time:
        uptime = datetime.now(timezone.utc) - mt5_state.initialization_time
        health_data["uptime"] = str(uptime)
    
    # Get terminal info if connected
    if mt5_manager.is_connected():
        health_data["terminal_info"] = mt5_manager.get_terminal_info()
    
    return health_data

@app.post("/api/mt5/initialize")
async def initialize_mt5_endpoint(api_key: str = Depends(verify_api_key)):
    """Force MT5 initialization"""
    try:
        success = mt5_manager.initialize_mt5()
        return {
            "success": success,
            "initialized": mt5_state.initialized,
            "mt5_available": MT5_AVAILABLE,
            "error": mt5_state.last_error if not success else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Initialize endpoint error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/mt5/login")
async def login_mt5_account(
    credentials: MT5Credentials,
    api_key: str = Depends(verify_api_key)
):
    """Login to MT5 trading account"""
    try:
        result = mt5_manager.login(
            credentials.account,
            credentials.password,
            credentials.server
        )
        
        if result.get("success"):
            logger.info(f"Successful login: Account {credentials.account}")
        else:
            logger.warning(f"Failed login: Account {credentials.account} - {result.get('error')}")
        
        return result
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/mt5/account/info")
async def get_account_info_endpoint(api_key: str = Depends(verify_api_key)):
    """Get MT5 account information"""
    try:
        result = mt5_manager.get_account_info()
        return result
    except Exception as e:
        logger.error(f"Account info endpoint error: {e}")
        return {"error": str(e)}

@app.get("/api/mt5/terminal/info")
async def get_terminal_info_endpoint(api_key: str = Depends(verify_api_key)):
    """Get MT5 terminal information"""
    try:
        result = mt5_manager.get_terminal_info()
        return result
    except Exception as e:
        logger.error(f"Terminal info endpoint error: {e}")
        return {"error": str(e)}

@app.get("/api/mt5/positions")
async def get_positions_endpoint(api_key: str = Depends(verify_api_key)):
    """Get current open positions"""
    try:
        if not mt5_manager.is_connected():
            return {"error": "MT5 not connected"}
        
        positions = mt5.positions_get()
        if positions is None:
            error = mt5.last_error()
            return {"error": f"Failed to get positions: {error}", "positions": []}
        
        positions_list = []
        for pos in positions:
            positions_list.append({
                "ticket": pos.ticket,
                "time": pos.time,
                "time_msc": pos.time_msc,
                "time_update": pos.time_update,
                "time_update_msc": pos.time_update_msc,
                "type": "BUY" if pos.type == 0 else "SELL",
                "magic": pos.magic,
                "identifier": pos.identifier,
                "reason": pos.reason,
                "volume": float(pos.volume),
                "price_open": float(pos.price_open),
                "sl": float(pos.sl),
                "tp": float(pos.tp),
                "price_current": float(pos.price_current),
                "swap": float(pos.swap),
                "profit": float(pos.profit),
                "symbol": pos.symbol,
                "comment": pos.comment,
                "external_id": pos.external_id
            })
        
        return {
            "success": True,
            "positions": positions_list,
            "count": len(positions_list),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Get positions error: {e}")
        return {"error": str(e), "positions": []}

@app.get("/api/mt5/symbols")
async def get_symbols_endpoint(api_key: str = Depends(verify_api_key)):
    """Get available trading symbols"""
    try:
        if not mt5_manager.is_connected():
            return {"error": "MT5 not connected"}
        
        symbols = mt5.symbols_get()
        if symbols is None:
            return {"error": "Failed to get symbols", "symbols": []}
        
        # Return basic symbol info
        symbols_list = []
        for symbol in symbols:
            if symbol.visible:  # Only visible symbols
                symbols_list.append({
                    "name": symbol.name,
                    "description": symbol.description,
                    "currency_base": symbol.currency_base,
                    "currency_profit": symbol.currency_profit,
                    "currency_margin": symbol.currency_margin,
                    "digits": symbol.digits,
                    "trade_mode": symbol.trade_mode
                })
        
        return {
            "success": True,
            "symbols": symbols_list,
            "count": len(symbols_list),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Get symbols error: {e}")
        return {"error": str(e), "symbols": []}

@app.get("/api/mt5/status")
async def get_status_endpoint(api_key: str = Depends(verify_api_key)):
    """Get comprehensive MT5 status"""
    try:
        status = {
            "mt5_available": MT5_AVAILABLE,
            "mt5_initialized": mt5_state.initialized,
            "mt5_connected": mt5_manager.is_connected(),
            "connected_accounts": mt5_state.connected_accounts,
            "initialization_time": mt5_state.initialization_time.isoformat() if mt5_state.initialization_time else None,
            "last_error": mt5_state.last_error,
            "terminal_info": mt5_manager.get_terminal_info() if mt5_manager.is_connected() else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return status
    except Exception as e:
        logger.error(f"Get status error: {e}")
        return {"error": str(e)}

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    # Production server configuration
    config = {
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8000)),
        "log_level": os.getenv("LOG_LEVEL", "info"),
        "access_log": True,
        "reload": os.getenv("ENVIRONMENT", "prod") == "dev"
    }
    
    logger.info(f"Starting server with config: {config}")
    uvicorn.run("main_production:app", **config)