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



@router.get("/trade-history/{account_id}")
async def get_manager_trade_history(account_id: int, days: int = 30, authorization: str = Header(None)):
    """Get recent trade history. Works for both manager tokens (scoped) and admin tokens (full access)."""
    try:
        payload = _decode_token(authorization)
        if account_id not in payload.get("allowed_accounts", []):
            raise HTTPException(status_code=403, detail="Access denied")
    except HTTPException:
        # Try admin token fallback
        try:
            token = authorization.replace("Bearer ", "") if authorization else ""
            admin_payload = jwt.decode(token, os.environ.get("JWT_SECRET_KEY", "fidus-production-secret-2025-secure-key"), algorithms=["HS256"])
            if admin_payload.get("type") not in ("admin", None):
                raise HTTPException(status_code=403, detail="Access denied")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

    db = await get_db()
    since = datetime.now(timezone.utc) - timedelta(days=days)

    trades = await db.mt5_deals_history.find(
        {"account": account_id, "type": {"$ne": 2}, "time": {"$gte": since}},
        {"_id": 0, "symbol": 1, "profit": 1, "volume": 1, "time": 1, "price": 1, "entry": 1, "type": 1}
    ).sort("time", -1).to_list(500)

    # Serialize datetimes
    for t in trades:
        if t.get("time"):
            t["time"] = t["time"].isoformat() if hasattr(t["time"], "isoformat") else str(t["time"])

    return {"success": True, "trades": trades, "count": len(trades)}


@router.get("/daily-pnl/{account_id}")
async def get_manager_daily_pnl(account_id: int, days: int = 30, authorization: str = Header(None)):
    """Daily P&L with breach detection. Works for both manager and admin tokens."""
    try:
        payload = _decode_token(authorization)
        if account_id not in payload.get("allowed_accounts", []):
            raise HTTPException(status_code=403, detail="Access denied")
    except HTTPException:
        try:
            token = authorization.replace("Bearer ", "") if authorization else ""
            admin_payload = jwt.decode(token, os.environ.get("JWT_SECRET_KEY", "fidus-production-secret-2025-secure-key"), algorithms=["HS256"])
            if admin_payload.get("type") not in ("admin", None):
                raise HTTPException(status_code=403, detail="Access denied")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

    db = await get_db()
    acc = await db.mt5_accounts.find_one({"account": account_id}, {"_id": 0, "initial_allocation": 1, "equity": 1})
    initial = acc.get("initial_allocation", 0) if acc else 0

    # Daily P&L aggregation
    pipeline = [
        {"$match": {"account": account_id, "type": {"$ne": 2}}},
        {"$addFields": {"day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$time"}}}},
        {"$group": {
            "_id": "$day",
            "daily_pnl": {"$sum": "$profit"},
            "trade_count": {"$sum": 1},
            "wins": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, 1, 0]}},
            "losses": {"$sum": {"$cond": [{"$lt": ["$profit", 0]}, 1, 0]}},
            "gross_profit": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, "$profit", 0]}},
            "gross_loss": {"$sum": {"$cond": [{"$lt": ["$profit", 0]}, "$profit", 0]}},
            "max_single_loss": {"$min": "$profit"},
            "max_single_win": {"$max": "$profit"},
            "symbols": {"$addToSet": "$symbol"},
        }},
        {"$sort": {"_id": -1}},
        {"$limit": days}
    ]

    daily = list(await db.mt5_deals_history.aggregate(pipeline).to_list(days))

    # Build equity curve and detect breaches
    running_equity = initial
    peak_equity = initial
    result = []

    # Reverse to process oldest first
    for d in reversed(daily):
        running_equity += d["daily_pnl"]
        peak_equity = max(peak_equity, running_equity)
        dd_from_peak = ((running_equity - peak_equity) / peak_equity * 100) if peak_equity > 0 else 0
        dd_from_initial = ((running_equity - initial) / initial * 100) if initial > 0 else 0
        daily_dd = (d["daily_pnl"] / running_equity * 100) if running_equity > 0 else 0

        breaches = []
        if daily_dd <= -3:
            breaches.append({"rule": "Max Daily Loss 3%", "value": f"{daily_dd:.2f}%", "severity": "CRITICAL" if daily_dd <= -5 else "WARNING"})
        if dd_from_peak <= -5:
            breaches.append({"rule": "DD Warning 5%", "value": f"{dd_from_peak:.2f}%", "severity": "WARNING"})
        if dd_from_peak <= -10:
            breaches.append({"rule": "DD Critical 10%", "value": f"{dd_from_peak:.2f}%", "severity": "CRITICAL"})
        if d["max_single_loss"] and initial > 0:
            single_risk = abs(d["max_single_loss"]) / running_equity * 100 if running_equity > 0 else 0
            if single_risk > 1.0:
                breaches.append({"rule": "Max Risk/Trade 1%", "value": f"{single_risk:.2f}%", "severity": "WARNING" if single_risk <= 2 else "CRITICAL"})

        result.append({
            "date": d["_id"],
            "daily_pnl": round(d["daily_pnl"], 2),
            "trade_count": d["trade_count"],
            "wins": d["wins"],
            "losses": d["losses"],
            "gross_profit": round(d["gross_profit"], 2),
            "gross_loss": round(d["gross_loss"], 2),
            "max_single_loss": round(d["max_single_loss"], 2) if d["max_single_loss"] else 0,
            "max_single_win": round(d["max_single_win"], 2) if d["max_single_win"] else 0,
            "symbols": d["symbols"],
            "running_equity": round(running_equity, 2),
            "drawdown_from_peak": round(dd_from_peak, 2),
            "drawdown_from_initial": round(dd_from_initial, 2),
            "daily_drawdown_pct": round(daily_dd, 2),
            "breaches": breaches,
            "has_breach": len(breaches) > 0
        })

    result.reverse()  # Back to newest first

    breach_days = [d for d in result if d["has_breach"]]
    worst_day = min(result, key=lambda x: x["daily_pnl"]) if result else None

    return {
        "success": True,
        "daily_pnl": result,
        "summary": {
            "total_days": len(result),
            "profitable_days": len([d for d in result if d["daily_pnl"] > 0]),
            "losing_days": len([d for d in result if d["daily_pnl"] < 0]),
            "breach_days": len(breach_days),
            "worst_day": worst_day,
            "total_breaches": sum(len(d["breaches"]) for d in result),
        }
    }
