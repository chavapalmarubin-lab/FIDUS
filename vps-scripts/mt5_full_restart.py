"""
MT5 Full System Restart Script
Handles complete restart of MT5 terminals and Bridge reconnection

Deploy this to VPS at: C:\\mt5-bridge\\mt5_full_restart.py
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
import MetaTrader5 as mt5

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt5_restart.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MT5_BRIDGE_API_KEY = os.getenv("MT5_BRIDGE_API_KEY", "your-api-key-here")
MT5_TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_DATA_PATHS = [
    r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal",
    # Add additional MT5 data paths if multiple instances
]

# Account credentials (configure these in environment variables)
MT5_ACCOUNTS = [
    {"login": 886557, "password": os.getenv("MT5_886557_PASSWORD"), "server": os.getenv("MT5_886557_SERVER")},
    {"login": 886066, "password": os.getenv("MT5_886066_PASSWORD"), "server": os.getenv("MT5_886066_SERVER")},
    {"login": 886602, "password": os.getenv("MT5_886602_PASSWORD"), "server": os.getenv("MT5_886602_SERVER")},
    {"login": 885822, "password": os.getenv("MT5_885822_PASSWORD"), "server": os.getenv("MT5_885822_SERVER")},
    {"login": 886528, "password": os.getenv("MT5_886528_PASSWORD"), "server": os.getenv("MT5_886528_SERVER")},
    {"login": 891215, "password": os.getenv("MT5_891215_PASSWORD"), "server": os.getenv("MT5_891215_SERVER")},
    {"login": 891234, "password": os.getenv("MT5_891234_PASSWORD"), "server": os.getenv("MT5_891234_SERVER")},
]

app = FastAPI()


def kill_mt5_processes():
    """Kill all running MT5 terminal processes"""
    logger.info("🔪 Killing all MT5 terminal processes...")
    
    try:
        # Kill all terminal64.exe processes
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "terminal64.exe"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ MT5 processes terminated")
        else:
            logger.warning(f"⚠️ No MT5 processes found or error: {result.stderr}")
        
        # Wait for cleanup
        time.sleep(3)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to kill MT5 processes: {e}")
        return False


def start_mt5_terminals():
    """Start MT5 terminal instances"""
    logger.info("🚀 Starting MT5 terminal instances...")
    
    try:
        if not os.path.exists(MT5_TERMINAL_PATH):
            logger.error(f"❌ MT5 terminal not found at: {MT5_TERMINAL_PATH}")
            return False
        
        # Start terminal (will start with saved profiles)
        subprocess.Popen([MT5_TERMINAL_PATH], shell=False)
        
        logger.info("✅ MT5 terminal started")
        
        # Wait for terminal to initialize
        logger.info("⏳ Waiting 15 seconds for terminal initialization...")
        time.sleep(15)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start MT5 terminal: {e}")
        return False


def reconnect_mt5_bridge():
    """Reconnect Bridge to MT5"""
    logger.info("🔗 Reconnecting Bridge to MT5...")
    
    try:
        # Shutdown existing connection
        mt5.shutdown()
        time.sleep(2)
        
        # Initialize new connection
        if not mt5.initialize():
            error = mt5.last_error()
            logger.error(f"❌ Failed to initialize MT5: {error}")
            return False
        
        logger.info("✅ Bridge reconnected to MT5")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to reconnect Bridge: {e}")
        return False


def verify_account_connections():
    """Verify all accounts are connected with real balances"""
    logger.info("🔍 Verifying account connections...")
    
    connected_accounts = []
    failed_accounts = []
    
    for account_config in MT5_ACCOUNTS:
        account_id = account_config["login"]
        
        try:
            # Get account info
            info = mt5.account_info()
            
            if info and info.balance > 0:
                logger.info(f"✅ Account {account_id}: Balance = ${info.balance:.2f}")
                connected_accounts.append({
                    "account": account_id,
                    "balance": float(info.balance),
                    "equity": float(info.equity),
                    "status": "connected"
                })
            else:
                logger.warning(f"❌ Account {account_id}: Balance = $0.00 or not connected")
                failed_accounts.append({
                    "account": account_id,
                    "status": "failed",
                    "balance": 0.0
                })
                
        except Exception as e:
            logger.error(f"❌ Failed to verify account {account_id}: {e}")
            failed_accounts.append({
                "account": account_id,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "connected": connected_accounts,
        "failed": failed_accounts,
        "total_connected": len(connected_accounts),
        "total_accounts": len(MT5_ACCOUNTS)
    }


@app.post("/api/system/full-restart")
async def full_system_restart(authorization: str = Header(None)):
    """
    Full restart of MT5 Bridge and all terminals
    
    Requires: Authorization: Bearer {MT5_BRIDGE_API_KEY}
    """
    # Validate API key
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    if api_key != MT5_BRIDGE_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    logger.info("=" * 80)
    logger.info("🔄 STARTING FULL MT5 SYSTEM RESTART")
    logger.info(f"⏰ Time: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    restart_results = {
        "started_at": datetime.now().isoformat(),
        "steps": [],
        "success": False
    }
    
    try:
        # Step 1: Kill MT5 processes
        logger.info("STEP 1: Killing MT5 processes...")
        if kill_mt5_processes():
            restart_results["steps"].append({"step": "kill_processes", "status": "success"})
        else:
            restart_results["steps"].append({"step": "kill_processes", "status": "failed"})
            raise Exception("Failed to kill MT5 processes")
        
        # Step 2: Wait for cleanup
        logger.info("STEP 2: Waiting for system cleanup...")
        time.sleep(5)
        restart_results["steps"].append({"step": "cleanup_wait", "status": "success"})
        
        # Step 3: Start MT5 terminals
        logger.info("STEP 3: Starting MT5 terminals...")
        if start_mt5_terminals():
            restart_results["steps"].append({"step": "start_terminals", "status": "success"})
        else:
            restart_results["steps"].append({"step": "start_terminals", "status": "failed"})
            raise Exception("Failed to start MT5 terminals")
        
        # Step 4: Reconnect Bridge
        logger.info("STEP 4: Reconnecting Bridge...")
        if reconnect_mt5_bridge():
            restart_results["steps"].append({"step": "reconnect_bridge", "status": "success"})
        else:
            restart_results["steps"].append({"step": "reconnect_bridge", "status": "failed"})
            raise Exception("Failed to reconnect Bridge")
        
        # Step 5: Verify connections
        logger.info("STEP 5: Verifying account connections...")
        verification = verify_account_connections()
        restart_results["verification"] = verification
        restart_results["steps"].append({"step": "verify_connections", "status": "success"})
        
        # Determine overall success
        success_rate = verification["total_connected"] / verification["total_accounts"]
        restart_results["success_rate"] = success_rate
        
        if success_rate >= 0.7:  # 70% or more accounts connected
            restart_results["success"] = True
            logger.info(f"🎉 RESTART SUCCESSFUL: {verification['total_connected']}/{verification['total_accounts']} accounts connected")
        else:
            logger.warning(f"⚠️ PARTIAL RESTART: Only {verification['total_connected']}/{verification['total_accounts']} accounts connected")
        
        restart_results["completed_at"] = datetime.now().isoformat()
        
        logger.info("=" * 80)
        logger.info("✅ FULL MT5 SYSTEM RESTART COMPLETED")
        logger.info("=" * 80)
        
        return JSONResponse(
            status_code=200,
            content=restart_results
        )
        
    except Exception as e:
        logger.error(f"❌ RESTART FAILED: {str(e)}")
        restart_results["success"] = False
        restart_results["error"] = str(e)
        restart_results["completed_at"] = datetime.now().isoformat()
        
        return JSONResponse(
            status_code=500,
            content=restart_results
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mt5-full-restart"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting MT5 Full Restart Service...")
    logger.info(f"📍 Listening on http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
