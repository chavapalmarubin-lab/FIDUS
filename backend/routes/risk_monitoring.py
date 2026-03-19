"""
FIDUS Layer 2 — Risk Monitoring API Routes
March 2026 — Post-Incident Rebuild

DETECT → ALERT → LOG. No trade execution.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime, timezone, timedelta
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/risk", tags=["Risk Monitoring (Layer 2)"])


# Database helper — reuse the global db from server.py
async def get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ.get("MONGO_URL")
    client = AsyncIOMotorClient(mongo_url)
    return client.fidus_production


# ═══════════════════════════════════════════
# ALERTS ENDPOINTS
# ═══════════════════════════════════════════

@router.get("/alerts")
async def get_alerts(status: Optional[str] = None, limit: int = 50):
    """Get risk alerts. Filter by status: 'unresolved' or 'all'."""
    db = await get_db()
    query = {}
    if status == "unresolved":
        query["resolved_at"] = None
    alerts = await db.alerts.find(query, {"_id": 0}).sort("sent_at", -1).limit(limit).to_list(limit)
    unresolved_count = await db.alerts.count_documents({"resolved_at": None})
    return {"success": True, "alerts": alerts, "unresolved_count": unresolved_count}


@router.get("/alerts/unresolved-count")
async def get_unresolved_alert_count():
    """Quick count for nav badge — poll every 30 seconds."""
    db = await get_db()
    count = await db.alerts.count_documents({"resolved_at": None})
    critical = await db.alerts.count_documents({"resolved_at": None, "alert_type": {"$in": ["halt", "portfolio_critical"]}})
    return {"count": count, "critical": critical}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolved_by: str = "admin"):
    """Mark an alert as resolved."""
    db = await get_db()
    from bson import ObjectId
    try:
        result = await db.alerts.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"resolved_at": datetime.now(timezone.utc), "resolved_by": resolved_by}}
        )
    except Exception:
        # Try matching by sent_at or other field
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True, "message": "Alert resolved"}


# ═══════════════════════════════════════════
# EQUITY SNAPSHOTS
# ═══════════════════════════════════════════

@router.get("/snapshots/{account_id}")
async def get_equity_snapshots(account_id: str, hours: int = 24):
    """Get equity snapshots for an account over the last N hours."""
    db = await get_db()
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    # Handle PORTFOLIO or numeric account
    acc_filter = "PORTFOLIO" if account_id == "PORTFOLIO" else int(account_id)
    snapshots = await db.equity_snapshots.find(
        {"account": acc_filter, "timestamp": {"$gte": since}},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    return {"success": True, "snapshots": snapshots, "count": len(snapshots)}


# ═══════════════════════════════════════════
# RISK STATUS (for dashboard cards)
# ═══════════════════════════════════════════

@router.get("/status")
async def get_risk_status():
    """Get current risk status for all monitored accounts. Poll every 30s from frontend."""
    db = await get_db()
    from services.risk_monitoring_service import MONITORED_ACCOUNTS, INITIAL_ALLOCATIONS, TOTAL_INITIAL

    accounts = []
    total_equity = 0
    for acc_id in MONITORED_ACCOUNTS:
        doc = await db.mt5_accounts.find_one(
            {"account": acc_id},
            {"_id": 0, "equity": 1, "manager_name": 1, "alert_status": 1,
             "last_sync_timestamp": 1, "warning_threshold": 1, "halt_threshold": 1}
        )
        if not doc:
            continue
        equity = doc.get("equity", 0) or 0
        initial = INITIAL_ALLOCATIONS.get(acc_id, 0)
        dd = ((equity - initial) / initial * 100) if initial > 0 else 0
        total_equity += equity

        # Unresolved alerts for this account
        alert_count = await db.alerts.count_documents({"account": acc_id, "resolved_at": None})

        accounts.append({
            "account": acc_id,
            "manager_name": doc.get("manager_name", ""),
            "equity": equity,
            "initial_allocation": initial,
            "drawdown_pct": round(dd, 2),
            "alert_status": doc.get("alert_status", "OK"),
            "unresolved_alerts": alert_count,
            "last_sync": doc.get("last_sync_timestamp"),
            "warning_threshold": doc.get("warning_threshold", 3.0),
            "halt_threshold": doc.get("halt_threshold", 5.0),
        })

    portfolio_dd = ((total_equity - TOTAL_INITIAL) / TOTAL_INITIAL * 100) if TOTAL_INITIAL > 0 else 0

    return {
        "success": True,
        "portfolio": {
            "total_equity": total_equity,
            "total_initial": TOTAL_INITIAL,
            "drawdown_pct": round(portfolio_dd, 2),
            "protection_line": TOTAL_INITIAL * 0.90,
            "breached": total_equity < TOTAL_INITIAL * 0.90
        },
        "accounts": accounts,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ═══════════════════════════════════════════
# EXPOSURE AGGREGATION (Item D)
# ═══════════════════════════════════════════

@router.get("/exposure")
async def get_exposure():
    """Cross-account instrument exposure. Read-only."""
    db = await get_db()
    from services.risk_monitoring_service import get_exposure_aggregation
    return await get_exposure_aggregation(db)


# ═══════════════════════════════════════════
# DATA HEALTH (Item H)
# ═══════════════════════════════════════════

@router.get("/data-health/{account_id}")
async def get_data_health(account_id: int):
    """Data health status for an account."""
    db = await get_db()
    from services.risk_monitoring_service import get_account_data_health
    return await get_account_data_health(db, account_id)


# ═══════════════════════════════════════════
# TEST ALERT (manual trigger for verification)
# ═══════════════════════════════════════════

@router.post("/test-alert")
async def send_test_alert():
    """Send a test alert email to verify SMTP is working."""
    from services.risk_monitoring_service import send_alert_email
    subject = "[FIDUS TEST] Risk Alert System Verification"
    body = f"""
    <div style="font-family: Arial; padding: 20px; background: #1a1a2e; color: #e0e0e0; border-radius: 8px;">
        <h2 style="color: #10b981;">FIDUS Alert System Test</h2>
        <p>This is a test alert from the Layer 2 Risk Monitoring System.</p>
        <p>Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        <p>If you received this, the alert delivery is working correctly.</p>
    </div>
    """
    sent = send_alert_email(subject, body)
    return {"success": sent, "message": "Test alert sent" if sent else "Failed to send test alert"}



# ═══════════════════════════════════════════
# ITEM F — SOCIAL TRADING MONITOR TRACKING
# ═══════════════════════════════════════════

@router.get("/social-monitors")
async def get_social_trading_monitors():
    """Get social trading equity monitor config status for all monitored accounts."""
    db = await get_db()
    from services.risk_monitoring_service import MONITORED_ACCOUNTS
    results = []
    for acc_id in MONITORED_ACCOUNTS:
        doc = await db.mt5_accounts.find_one(
            {"account": acc_id},
            {"_id": 0, "account": 1, "manager_name": 1, "social_trading_monitors": 1}
        )
        if doc:
            monitors = doc.get("social_trading_monitors", [])
            results.append({
                "account": acc_id,
                "manager_name": doc.get("manager_name", ""),
                "monitors": monitors,
                "configured": len(monitors) > 0,
                "verified": all(m.get("verified", False) for m in monitors) if monitors else False
            })
    return {"success": True, "accounts": results}


@router.post("/social-monitors/{account_id}")
async def update_social_trading_monitor(account_id: int, monitor: dict = None):
    """
    Add or update social trading monitor config for an account.
    Body: { type: "equity_protect", threshold_pct: 10, action: "disable_copier", configured_by: "Chava", verified: true }
    """
    from pydantic import BaseModel
    db = await get_db()

    if not monitor:
        raise HTTPException(status_code=400, detail="Monitor config required")

    monitor["configured_at"] = datetime.now(timezone.utc).isoformat()

    result = await db.mt5_accounts.update_one(
        {"account": account_id},
        {"$push": {"social_trading_monitors": monitor}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")

    return {"success": True, "message": f"Monitor added for account {account_id}"}


@router.put("/social-monitors/{account_id}/verify")
async def verify_social_trading_monitor(account_id: int):
    """Mark all social trading monitors for an account as verified."""
    db = await get_db()
    result = await db.mt5_accounts.update_one(
        {"account": account_id},
        {"$set": {"social_trading_monitors.$[].verified": True, "social_trading_monitors.$[].verified_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"success": True, "message": f"Monitors verified for account {account_id}"}


# ═══════════════════════════════════════════
# ITEM G — RISK SCORE (computed from breach events)
# ═══════════════════════════════════════════

@router.get("/risk-scores")
async def get_risk_scores():
    """Get current risk scores for all monitored accounts."""
    db = await get_db()
    from services.risk_monitoring_service import MONITORED_ACCOUNTS, INITIAL_ALLOCATIONS

    scores = []
    for acc_id in MONITORED_ACCOUNTS:
        # Count breach events in last 30 days
        since = datetime.now(timezone.utc) - timedelta(days=30)
        breaches = await db.alerts.count_documents({
            "account": acc_id,
            "sent_at": {"$gte": since}
        })
        critical_breaches = await db.alerts.count_documents({
            "account": acc_id,
            "alert_type": "halt",
            "sent_at": {"$gte": since}
        })

        # Get current drawdown
        doc = await db.mt5_accounts.find_one({"account": acc_id}, {"_id": 0, "equity": 1, "manager_name": 1})
        equity = doc.get("equity", 0) if doc else 0
        initial = INITIAL_ALLOCATIONS.get(acc_id, 0)
        dd_pct = ((equity - initial) / initial * 100) if initial > 0 else 0

        # Compute score (start 100, deduct penalties)
        score = 100
        score -= critical_breaches * 20   # -20 per critical breach
        score -= breaches * 5             # -5 per any breach
        if dd_pct <= -10:
            score -= 40                   # -40 for monthly DD breach
        elif dd_pct <= -5:
            score -= 20
        elif dd_pct <= -3:
            score -= 10
        score = max(0, min(100, score))

        label = "Strong" if score >= 80 else "Moderate" if score >= 60 else "Weak" if score >= 40 else "Critical"

        scores.append({
            "account": acc_id,
            "manager_name": doc.get("manager_name", "") if doc else "",
            "score": score,
            "label": label,
            "drawdown_pct": round(dd_pct, 2),
            "breaches_30d": breaches,
            "critical_breaches_30d": critical_breaches,
            "penalties_applied": {
                "critical_breach": critical_breaches * 20,
                "any_breach": breaches * 5,
                "drawdown": 40 if dd_pct <= -10 else 20 if dd_pct <= -5 else 10 if dd_pct <= -3 else 0
            }
        })

    return {"success": True, "scores": scores, "timestamp": datetime.now(timezone.utc).isoformat()}



# ═══════════════════════════════════════════
# FUND HEALTH CALENDAR (Public — for client portal)
# Returns ONLY green/red status per month, no amounts
# ═══════════════════════════════════════════

@router.get("/fund-health-calendar")
async def get_fund_health_calendar():
    """
    Month-by-month fund health for client portal.
    green = fund can cover obligations, red = underfunded.
    No amounts — just status.
    
    Logic: Net Fund Position = Total Equity - Total Client Capital (principal owed back).
    If net position is negative, fund is underfunded for ALL months.
    Running balance deducts monthly interest obligations from net position.
    """
    db = await get_db()
    try:
        from services.risk_monitoring_service import MONITORED_ACCOUNTS, TOTAL_INITIAL
        from dateutil.relativedelta import relativedelta
        from bson.decimal128 import Decimal128

        now = datetime.now(timezone.utc)

        # Total fund equity (real MT5 accounts only)
        total_equity = 0
        for acc_id in MONITORED_ACCOUNTS:
            doc = await db.mt5_accounts.find_one({"account": acc_id}, {"_id": 0, "equity": 1})
            total_equity += float(doc.get("equity", 0) or 0) if doc else 0

        # Net Fund Position = Equity - Client Capital (what we owe back)
        # This is the TRUE available surplus/deficit
        net_position = total_equity - TOTAL_INITIAL

        # Get all active investments for monthly obligation calculation
        investments = await db.investments.find(
            {"status": {"$in": ["active", "incubation"]}},
            {"_id": 0, "principal_amount": 1, "amount": 1, "interest_rate": 1, "fund_type": 1}
        ).to_list(500)

        def to_float(v):
            if isinstance(v, Decimal128):
                return float(v.to_decimal())
            return float(v) if v else 0

        # Running balance starts from net position (negative = already underfunded)
        running = net_position
        months = []
        for i in range(14):
            month_date = now + relativedelta(months=i)
            month_key = month_date.strftime("%Y-%m")

            # Monthly interest obligations
            month_obligations = 0
            for inv in investments:
                amt = to_float(inv.get("principal_amount") or inv.get("amount", 0))
                rate = to_float(inv.get("interest_rate", 0.015))
                month_obligations += amt * rate

            running -= month_obligations
            months.append({
                "month": month_key,
                "funded": running >= 0,
                "status": "green" if running >= 0 else "red"
            })

        return {"success": True, "months": months, "as_of": now.isoformat()}

    except Exception as e:
        logger.error(f"Fund health calendar error: {e}", exc_info=True)
        return {"success": True, "months": [], "as_of": datetime.now(timezone.utc).isoformat()}
