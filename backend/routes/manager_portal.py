"""
FIDUS Manager Portal API
Allows money managers to view ONLY their own strategies' risk analysis.
Read-only. No execution. Scoped by allowed_accounts.
"""

from fastapi import APIRouter, HTTPException, Header
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional
import os, logging, hashlib, jwt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/manager", tags=["Manager Portal"])

JWT_SECRET = os.environ.get("JWT_SECRET", "fidus-manager-secret-2026")
JWT_ALGORITHM = "HS256"
SALT = "fidus_manager_salt_2026"


async def get_db():
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    return client.fidus_production


class ManagerLogin(BaseModel):
    email: str
    password: str


def _hash(pwd):
    return hashlib.sha256(f"{pwd}{SALT}".encode()).hexdigest()


def _create_token(data: dict) -> str:
    payload = {**data, "type": "manager", "exp": datetime.now(timezone.utc) + timedelta(hours=24)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(authorization: str) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "manager":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login")
async def manager_login(creds: ManagerLogin):
    db = await get_db()
    mgr = await db.manager_logins.find_one({"email": creds.email.lower(), "status": "active"})
    if not mgr or mgr.get("password_hash") != _hash(creds.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await db.manager_logins.update_one(
        {"manager_id": mgr["manager_id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )

    token = _create_token({
        "manager_id": mgr["manager_id"],
        "name": mgr["name"],
        "email": mgr["email"],
        "allowed_accounts": mgr["allowed_accounts"]
    })

    return {
        "success": True,
        "token": token,
        "manager": {
            "manager_id": mgr["manager_id"],
            "name": mgr["name"],
            "email": mgr["email"],
            "allowed_accounts": mgr["allowed_accounts"],
            "allowed_account_names": mgr.get("allowed_account_names", [])
        }
    }


@router.get("/strategies")
async def get_manager_strategies(authorization: str = Header(None)):
    """Get the manager's allowed strategies with live data."""
    payload = _decode_token(authorization)
    allowed = payload.get("allowed_accounts", [])
    db = await get_db()

    strategies = []
    for acc_id in allowed:
        acc = await db.mt5_accounts.find_one({"account": acc_id}, {"_id": 0})
        if not acc:
            continue

        # Trade stats
        pipeline = [
            {"$match": {"account": acc_id, "type": {"$ne": 2}, "profit": {"$ne": 0}}},
            {"$group": {
                "_id": None,
                "total_trades": {"$sum": 1},
                "wins": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, 1, 0]}},
                "total_profit": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, "$profit", 0]}},
                "total_loss": {"$sum": {"$cond": [{"$lt": ["$profit", 0]}, "$profit", 0]}},
            }}
        ]
        stats = list(await db.mt5_deals_history.aggregate(pipeline).to_list(1))
        s = stats[0] if stats else {}
        total_trades = s.get("total_trades", 0)
        win_rate = (s.get("wins", 0) / total_trades * 100) if total_trades > 0 else 0
        pf = abs(s.get("total_profit", 0) / s.get("total_loss", 1)) if s.get("total_loss", 0) != 0 else 0

        strategies.append({
            "account": acc_id,
            "manager_name": acc.get("manager_name", ""),
            "equity": acc.get("equity", 0),
            "balance": acc.get("balance", 0),
            "initial_allocation": acc.get("initial_allocation", 0),
            "total_trades": total_trades,
            "win_rate": round(win_rate, 1),
            "profit_factor": round(pf, 2),
            "last_sync": str(acc.get("last_sync_timestamp", "")),
            "fund_type": acc.get("fund_type", ""),
            "status": acc.get("status", "active"),
        })

    return {"success": True, "strategies": strategies}


@router.get("/risk-analysis/{account_id}")
async def get_manager_risk_analysis(account_id: int, authorization: str = Header(None)):
    """Get risk analysis for a specific account — only if allowed."""
    payload = _decode_token(authorization)
    allowed = payload.get("allowed_accounts", [])
    if account_id not in allowed:
        raise HTTPException(status_code=403, detail="You do not have access to this account")

    db = await get_db()
    acc = await db.mt5_accounts.find_one({"account": account_id}, {"_id": 0})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    # Get risk analysis from hull risk engine
    try:
        from services.hull_risk_engine import HullRiskEngine
        engine = HullRiskEngine(db)
        analysis = await engine.get_strategy_risk_analysis(account_id)
        return {"success": True, "analysis": analysis, "account": acc.get("manager_name")}
    except Exception as e:
        logger.error(f"Risk analysis error for {account_id}: {e}")
        # Fallback: return basic data
        return {
            "success": True,
            "analysis": None,
            "account": acc.get("manager_name"),
            "basic_data": {
                "equity": acc.get("equity", 0),
                "balance": acc.get("balance", 0),
                "initial_allocation": acc.get("initial_allocation", 0),
            }
        }
