"""
MT5 BRIDGE SERVICE FIX
=====================

This is the corrected MT5 bridge service code that uses the CORRECT MT5 path.
Update your bridge service with this configuration.
"""

import MetaTrader5 as mt5
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Dict, Any

app = FastAPI(title="MT5 Bridge Service - Fixed")

# CRITICAL FIX: Use the correct MT5 installation path
MT5_PATH = r"C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"

# Global MT5 connection state
mt5_initialized = False
current_login = None

class MT5LoginRequest(BaseModel):
    login: int
    password: str
    server: str

@app.on_event("startup")
async def initialize_mt5():
    """Initialize MT5 with the CORRECT path on startup"""
    global mt5_initialized
    
    print(f"🔧 Initializing MT5 with path: {MT5_PATH}")
    
    # Initialize MT5 with the explicit path
    if mt5.initialize(path=MT5_PATH):
        mt5_initialized = True
        version = mt5.version()
        terminal_info = mt5.terminal_info()
        
        print(f"✅ MT5 initialized successfully!")
        print(f"   Version: {version}")
        if terminal_info:
            print(f"   Terminal: {terminal_info.name}")
            print(f"   Company: {terminal_info.company}")
            print(f"   Actual Path: {terminal_info.path}")
    else:
        error = mt5.last_error()
        print(f"❌ MT5 initialization failed!")
        print(f"   Error: {error}")
        print(f"   Path used: {MT5_PATH}")
        mt5_initialized = False

@app.get("/health")
async def health_check():
    """Health check endpoint with MT5 status"""
    terminal_info = None
    
    if mt5_initialized:
        terminal_info = mt5.terminal_info()
        if terminal_info:
            terminal_info = terminal_info._asdict()
    
    return {
        "status": "healthy" if mt5_initialized else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mt5_available": True,  # MetaTrader5 package is installed
        "mt5_initialized": mt5_initialized,
        "mt5_connected": current_login is not None,
        "connected_accounts": 1 if current_login else 0,
        "uptime": None,  # Could implement uptime tracking
        "terminal_info": terminal_info,
        "last_error": None if mt5_initialized else mt5.last_error(),
        "mt5_path": MT5_PATH
    }

@app.post("/api/mt5/initialize")
async def initialize_mt5_endpoint():
    """Force reinitialize MT5 if needed"""
    global mt5_initialized
    
    if not mt5_initialized:
        await initialize_mt5()
    
    return {
        "success": mt5_initialized,
        "message": "MT5 initialized" if mt5_initialized else "MT5 initialization failed",
        "error": None if mt5_initialized else mt5.last_error()
    }

@app.post("/api/mt5/login")
async def mt5_login(request: MT5LoginRequest):
    """Login to MT5 account"""
    global current_login
    
    if not mt5_initialized:
        raise HTTPException(status_code=503, detail="MT5 not initialized")
    
    try:
        # Attempt login
        success = mt5.login(request.login, password=request.password, server=request.server)
        
        if success:
            current_login = request.login
            return {
                "success": True,
                "message": f"Successfully logged into account {request.login}",
                "login": request.login,
                "server": request.server
            }
        else:
            error = mt5.last_error()
            return {
                "success": False,
                "error": f"Login failed: {error}",
                "login": request.login
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Login exception: {str(e)}",
            "login": request.login
        }

@app.get("/api/mt5/account/{login}/info")
async def get_account_info(login: int):
    """Get MT5 account information"""
    if not mt5_initialized:
        raise HTTPException(status_code=503, detail="MT5 not initialized")
    
    try:
        # Get account info
        account_info = mt5.account_info()
        
        if account_info:
            return {
                "success": True,
                "data": {
                    "login": account_info.login,
                    "balance": account_info.balance,
                    "equity": account_info.equity,
                    "margin": account_info.margin,
                    "margin_free": account_info.margin_free,
                    "margin_level": account_info.margin_level,
                    "profit": account_info.profit,
                    "currency": account_info.currency,
                    "leverage": account_info.leverage,
                    "server": account_info.server,
                    "name": account_info.name,
                    "company": account_info.company
                }
            }
        else:
            return {
                "success": False,
                "error": "Could not retrieve account info",
                "login": login
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Account info exception: {str(e)}",
            "login": login
        }

@app.get("/api/mt5/account/{login}/positions")
async def get_positions(login: int):
    """Get current open positions"""
    if not mt5_initialized:
        raise HTTPException(status_code=503, detail="MT5 not initialized")
    
    try:
        positions = mt5.positions_get()
        
        if positions is not None:
            positions_list = []
            total_profit = 0
            
            for pos in positions:
                pos_dict = {
                    "ticket": pos.ticket,
                    "symbol": pos.symbol,
                    "type": pos.type,
                    "type_str": "buy" if pos.type == 0 else "sell",
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "price_current": pos.price_current,
                    "profit": pos.profit,
                    "swap": pos.swap,
                    "commission": pos.commission,
                    "sl": pos.sl,
                    "tp": pos.tp,
                    "time": pos.time,
                    "comment": pos.comment
                }
                positions_list.append(pos_dict)
                total_profit += pos.profit
            
            return {
                "success": True,
                "data": {
                    "positions": positions_list,
                    "count": len(positions_list),
                    "total_profit": total_profit
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "positions": [],
                    "count": 0,
                    "total_profit": 0
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Positions exception: {str(e)}",
            "login": login
        }

@app.post("/api/mt5/history")
async def get_account_history(request: dict):
    """Get account trading history"""
    if not mt5_initialized:
        raise HTTPException(status_code=503, detail="MT5 not initialized")
    
    try:
        # Default to last 30 days if no dates provided
        from datetime import datetime, timedelta
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        if "from_date" in request:
            from_date = datetime.fromisoformat(request["from_date"])
        if "to_date" in request:
            to_date = datetime.fromisoformat(request["to_date"])
        
        # Get deals history
        deals = mt5.history_deals_get(from_date, to_date)
        
        if deals is not None:
            deals_list = []
            
            for deal in deals:
                deal_dict = {
                    "ticket": deal.ticket,
                    "order": deal.order,
                    "time": deal.time,
                    "type": deal.type,
                    "entry": deal.entry,
                    "symbol": deal.symbol,
                    "volume": deal.volume,
                    "price": deal.price,
                    "profit": deal.profit,
                    "swap": deal.swap,
                    "commission": deal.commission,
                    "comment": deal.comment
                }
                deals_list.append(deal_dict)
            
            return {
                "success": True,
                "data": {
                    "deals": deals_list,
                    "count": len(deals_list),
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat()
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "deals": [],
                    "count": 0,
                    "from_date": from_date.isoformat(),
                    "to_date": to_date.isoformat()
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"History exception: {str(e)}"
        }

@app.on_event("shutdown")
async def shutdown_mt5():
    """Cleanup MT5 connection on shutdown"""
    global mt5_initialized
    
    if mt5_initialized:
        mt5.shutdown()
        mt5_initialized = False
        print("🔌 MT5 connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)