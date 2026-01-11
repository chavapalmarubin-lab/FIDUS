"""
VIKING MT4 Bridge Service
=========================
Receives account data from VIKING_MT4_Bridge.mq4 EA via HTTP POST
Writes directly to MongoDB viking_* collections

Port: 8001 (separate from FIDUS on port 8000)
Collections: viking_accounts, viking_deals_history

This is COMPLETELY SEPARATE from FIDUS MT5 bridge.
"""

import os
import sys
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('viking_bridge.log')
    ]
)
logger = logging.getLogger("VIKING_Bridge")

# Configuration
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'fidus_production')
PORT = int(os.environ.get('VIKING_BRIDGE_PORT', 8001))

if not MONGO_URL:
    logger.error("MONGO_URL environment variable not set!")
    sys.exit(1)

# MongoDB client
mongo_client: Optional[AsyncIOMotorClient] = None
db = None


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class VikingAccountSync(BaseModel):
    """Account data from MT4 EA"""
    account: int
    strategy: str = "CORE"
    broker: str
    server: str
    platform: str = "MT4"
    balance: float
    equity: float
    margin: float
    free_margin: float
    profit: float
    currency: str = "USD"
    leverage: int
    status: str = "active"
    error_message: Optional[str] = None
    sync_timestamp: Optional[str] = None
    sync_type: str = "account"


class VikingDeal(BaseModel):
    """Deal/trade data from MT4 EA"""
    account: int
    viking_account_id: str
    strategy: str
    ticket: int
    symbol: str
    type: str
    volume: float
    open_time: str
    close_time: Optional[str] = None
    open_price: float
    close_price: Optional[float] = None
    profit: float = 0.0
    commission: float = 0.0
    swap: float = 0.0
    comment: str = ""


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MongoDB connection lifecycle"""
    global mongo_client, db
    
    logger.info("=" * 60)
    logger.info("VIKING MT4 Bridge Service Starting...")
    logger.info(f"Port: {PORT}")
    logger.info(f"Database: {DB_NAME}")
    logger.info("=" * 60)
    
    try:
        mongo_client = AsyncIOMotorClient(MONGO_URL)
        db = mongo_client[DB_NAME]
        
        # Test connection
        await mongo_client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully")
        
        # Ensure collections and indexes exist
        await ensure_indexes()
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise
    
    yield
    
    # Cleanup
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="VIKING MT4 Bridge Service",
    description="Receives MT4 data for VIKING trading operations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def ensure_indexes():
    """Create indexes for VIKING collections"""
    try:
        # viking_accounts - unique on account number
        await db.viking_accounts.create_index("account", unique=True)
        
        # viking_deals_history - compound index for efficient queries
        await db.viking_deals_history.create_index([
            ("account", 1),
            ("ticket", 1)
        ], unique=True)
        
        await db.viking_deals_history.create_index([
            ("account", 1),
            ("close_time", -1)
        ])
        
        logger.info("✅ MongoDB indexes ensured")
        
    except Exception as e:
        logger.warning(f"Index creation warning (may already exist): {e}")


def parse_mt4_datetime(dt_str: str) -> datetime:
    """Parse MT4 datetime string to Python datetime"""
    if not dt_str or dt_str == "":
        return None
    
    try:
        # MT4 format: "2026.01.11 22:45:30"
        return datetime.strptime(dt_str, "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except:
        try:
            # Alternative format
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return datetime.now(timezone.utc)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "VIKING MT4 Bridge",
        "status": "running",
        "port": PORT,
        "version": "1.0.0"
    }


@app.get("/api/viking/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        await mongo_client.admin.command('ping')
        
        # Get sync stats
        account_count = await db.viking_accounts.count_documents({})
        deal_count = await db.viking_deals_history.count_documents({})
        
        return {
            "status": "healthy",
            "mongodb": "connected",
            "database": DB_NAME,
            "viking_accounts": account_count,
            "viking_deals": deal_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@app.post("/api/viking/sync")
async def sync_account(data: VikingAccountSync):
    """
    Receive account data from MT4 EA and write to MongoDB
    This is the main sync endpoint called by VIKING_MT4_Bridge.mq4
    """
    try:
        logger.info(f"📥 Received sync from account {data.account}")
        
        # Build document for MongoDB
        doc = {
            "_id": f"VIKING_{data.account}",
            "account": data.account,
            "strategy": data.strategy,
            "broker": data.broker,
            "server": data.server,
            "platform": data.platform,
            "balance": data.balance,
            "equity": data.equity,
            "margin": data.margin,
            "free_margin": data.free_margin,
            "profit": data.profit,
            "currency": data.currency,
            "leverage": data.leverage,
            "status": "active",
            "error_message": None,
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Upsert to viking_accounts
        result = await db.viking_accounts.update_one(
            {"account": data.account},
            {"$set": doc, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
            upsert=True
        )
        
        action = "inserted" if result.upserted_id else "updated"
        logger.info(f"✅ Account {data.account} {action} - Balance: ${data.balance:,.2f}, Equity: ${data.equity:,.2f}")
        
        return {
            "success": True,
            "action": action,
            "account": data.account,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/viking/deals/batch")
async def sync_deals_batch(request: Request):
    """
    Receive batch of deals from MT4 EA
    Upserts based on account + ticket combination
    """
    try:
        deals = await request.json()
        
        if not deals or not isinstance(deals, list):
            return {"success": True, "inserted": 0, "updated": 0, "message": "No deals provided"}
        
        logger.info(f"📥 Received {len(deals)} deals for batch sync")
        
        inserted = 0
        updated = 0
        errors = 0
        
        for deal in deals:
            try:
                # Parse datetime strings
                open_time = parse_mt4_datetime(deal.get("open_time"))
                close_time = parse_mt4_datetime(deal.get("close_time"))
                
                doc = {
                    "account": deal["account"],
                    "viking_account_id": deal.get("viking_account_id", f"VIKING_{deal['account']}"),
                    "strategy": deal.get("strategy", "CORE"),
                    "ticket": deal["ticket"],
                    "symbol": deal["symbol"],
                    "type": deal["type"],
                    "volume": deal["volume"],
                    "open_time": open_time,
                    "close_time": close_time,
                    "open_price": deal["open_price"],
                    "close_price": deal.get("close_price"),
                    "profit": deal.get("profit", 0),
                    "commission": deal.get("commission", 0),
                    "swap": deal.get("swap", 0),
                    "comment": deal.get("comment", ""),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                result = await db.viking_deals_history.update_one(
                    {"account": deal["account"], "ticket": deal["ticket"]},
                    {"$set": doc},
                    upsert=True
                )
                
                if result.upserted_id:
                    inserted += 1
                elif result.modified_count > 0:
                    updated += 1
                    
            except Exception as e:
                logger.warning(f"Error processing deal {deal.get('ticket')}: {e}")
                errors += 1
        
        logger.info(f"✅ Deals sync complete - Inserted: {inserted}, Updated: {updated}, Errors: {errors}")
        
        return {
            "success": True,
            "inserted": inserted,
            "updated": updated,
            "errors": errors,
            "total_processed": len(deals)
        }
        
    except Exception as e:
        logger.error(f"❌ Batch deals sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/viking/status")
async def get_sync_status():
    """Get current sync status for VIKING accounts"""
    try:
        accounts = await db.viking_accounts.find(
            {},
            {"_id": 0, "account": 1, "strategy": 1, "balance": 1, "equity": 1, "last_sync": 1, "status": 1}
        ).to_list(None)
        
        total_deals = await db.viking_deals_history.count_documents({})
        
        return {
            "success": True,
            "accounts": accounts,
            "total_deals": total_deals,
            "service_status": "running",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting VIKING MT4 Bridge Service on port {PORT}...")
    uvicorn.run(
        "viking_mt4_bridge_service:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info"
    )
