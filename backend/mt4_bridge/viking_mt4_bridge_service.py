"""
VIKING MT4 Bridge Service - SIMPLIFIED VERSION
=============================================
Receives account data from VIKING_MT4_Bridge.mq4 EA via HTTP POST
Writes directly to MongoDB viking_accounts collection

Port: 8001
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import uvicorn

# ============================================================
# CONFIGURATION - HARDCODED FOR RELIABILITY
# ============================================================
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170TenochSecure@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"
DB_NAME = "fidus_production"
PORT = 8001

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("VIKING")

# ============================================================
# MONGODB CONNECTION
# ============================================================
logger.info("Connecting to MongoDB...")
try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    # Test connection
    client.admin.command('ping')
    logger.info("✅ MongoDB connected successfully!")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    raise

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(title="VIKING MT4 Bridge", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# MODELS
# ============================================================
class AccountSync(BaseModel):
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

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {"service": "VIKING MT4 Bridge", "status": "running", "port": PORT}

@app.get("/api/viking/health")
def health():
    try:
        client.admin.command('ping')
        count = db.viking_accounts.count_documents({})
        return {
            "status": "healthy",
            "mongodb": "connected",
            "viking_accounts_count": count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/api/viking/sync")
def sync_account(data: AccountSync):
    """Main sync endpoint - receives data from MT4 EA"""
    try:
        logger.info(f"📥 Sync from account {data.account}: Balance=${data.balance:,.2f}, Equity=${data.equity:,.2f}")
        
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
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Upsert to viking_accounts
        result = db.viking_accounts.update_one(
            {"_id": f"VIKING_{data.account}"},
            {"$set": doc, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
            upsert=True
        )
        
        action = "inserted" if result.upserted_id else "updated"
        logger.info(f"✅ Account {data.account} {action}")
        
        return {"success": True, "action": action, "account": data.account}
        
    except Exception as e:
        logger.error(f"❌ Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/viking/deals/batch")
async def sync_deals(request: Request):
    """Batch sync deals from MT4"""
    try:
        deals = await request.json()
        if not deals:
            return {"success": True, "inserted": 0}
        
        inserted = 0
        for deal in deals:
            try:
                result = db.viking_deals_history.update_one(
                    {"account": deal["account"], "ticket": deal["ticket"]},
                    {"$set": {**deal, "updated_at": datetime.now(timezone.utc)}},
                    upsert=True
                )
                if result.upserted_id:
                    inserted += 1
            except Exception as e:
                logger.warning(f"Deal error: {e}")
        
        logger.info(f"✅ Synced {inserted} new deals")
        return {"success": True, "inserted": inserted, "total": len(deals)}
        
    except Exception as e:
        logger.error(f"❌ Deals sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/viking/status")
def status():
    """Get current status"""
    accounts = list(db.viking_accounts.find({}, {"_id": 0}))
    deals_count = db.viking_deals_history.count_documents({})
    return {
        "accounts": accounts,
        "deals_count": deals_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    logger.info(f"🚀 Starting VIKING MT4 Bridge on port {PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
