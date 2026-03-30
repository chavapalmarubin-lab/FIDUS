"""
FIDUS Risk Monitoring & Alert Service (Layer 2)
March 2026 — Post-Incident Rebuild

ARCHITECTURE BOUNDARY:
This is a MONITORING AND ALERT LAYER ONLY.
DETECT → ALERT → LOG. No trade execution.

Items Implemented:
- Item A: Alert rules on existing polling job
- Item B: Alert delivery service (SMTP email)
- Item C: Equity snapshot storage (90-day retention)
- Item D: Exposure aggregation engine
- Item H: Data health per account
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════

# Default thresholds (overridden per account in MongoDB)
DEFAULT_WARNING_THRESHOLD = 3.0    # 3% drawdown → WARNING
DEFAULT_HALT_THRESHOLD = 5.0       # 5% drawdown → CRITICAL
DEDUP_WINDOW_MINUTES = 60          # Don't re-send same alert within 60 min
SNAPSHOT_RETENTION_DAYS = 90

# SMTP config from .env
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "")
ALERT_RECIPIENT = os.environ.get("ALERT_RECIPIENT_EMAIL", "")

# Telegram config from .env
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Monitored accounts (real capital + live demo)
MONITORED_ACCOUNTS = [2206, 20043, 2208, 2210, 2215, 2216, 2217, 2218, 2219, 20062, 939702]

# Initial allocations (March 27, 2026 — consolidated to 2208)
INITIAL_ALLOCATIONS = {
    2206: 0, 20043: 0,
    2208: 300961.07,  # Full client capital — copies 2210 1:1
    # Live Demo accounts
    2210: 300961.0, 2215: 100000.0, 2216: 100000.0,
    2217: 100000.0, 2218: 100000.0, 2219: 100000.0,
    20062: 200000.0, 939702: 10000.0,
}
TOTAL_INITIAL = sum(INITIAL_ALLOCATIONS.values())


# ═══════════════════════════════════════════
# ITEM B — ALERT DELIVERY SERVICE (Email + Telegram)
# ═══════════════════════════════════════════

import requests as http_requests

def send_telegram_alert(message: str) -> bool:
    """Send alert via Telegram bot. Returns True if sent."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("[ALERT] Telegram not configured")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        resp = http_requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info(f"[ALERT] Telegram sent")
            return True
        else:
            logger.error(f"[ALERT] Telegram failed: {resp.status_code} {resp.text[:100]}")
            return False
    except Exception as e:
        logger.error(f"[ALERT] Telegram error: {e}")
        return False


def send_alert_email(subject: str, body: str) -> bool:
    """Send alert email via SMTP. Returns True if sent."""
    if not SMTP_USERNAME or not SMTP_APP_PASSWORD or not ALERT_RECIPIENT:
        logger.error("[ALERT] SMTP not configured — cannot send email")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = ALERT_RECIPIENT
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_USERNAME, SMTP_APP_PASSWORD)
            server.sendmail(SMTP_USERNAME, ALERT_RECIPIENT, msg.as_string())

        logger.info(f"[ALERT] Email sent: {subject}")
        return True
    except Exception as e:
        logger.error(f"[ALERT] Email send failed: {e}")
        return False


def build_alert_email(alert_type: str, account: int, manager_name: str,
                      equity: float, drawdown_pct: float, threshold: float,
                      initial_alloc: float) -> tuple:
    """Build email subject and HTML body for an alert."""
    severity = "CRITICAL" if alert_type == "halt" else "WARNING"
    color = "#cc0000" if severity == "CRITICAL" else "#e6a800"

    subject = f"[FIDUS {severity}] Account {account} ({manager_name}) — Drawdown {drawdown_pct:+.2f}%"

    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: {color}; color: white; padding: 15px 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">FIDUS {severity} ALERT</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Layer 2 Monitoring System</p>
        </div>
        <div style="background: #1a1a2e; color: #e0e0e0; padding: 20px; border-radius: 0 0 8px 8px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px 0; color: #888;">Account</td><td style="padding: 8px 0; text-align: right; font-weight: bold;">{account}</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Manager</td><td style="padding: 8px 0; text-align: right; font-weight: bold;">{manager_name}</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Current Equity</td><td style="padding: 8px 0; text-align: right; font-weight: bold; color: #ef4444;">${equity:,.2f}</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Initial Allocation</td><td style="padding: 8px 0; text-align: right;">${initial_alloc:,.2f}</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Drawdown</td><td style="padding: 8px 0; text-align: right; font-weight: bold; color: {color};">{drawdown_pct:+.2f}%</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Threshold Breached</td><td style="padding: 8px 0; text-align: right;">{threshold}%</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Timestamp (UTC)</td><td style="padding: 8px 0; text-align: right;">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            </table>
            <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 4px; font-size: 12px; color: #888;">
                This is a monitoring alert from FIDUS Layer 2. No automated trade action is taken.
                Check the Social Trading platform (Layer 1) to verify equity monitors are active.
            </div>
        </div>
    </div>
    """
    return subject, body


def build_portfolio_alert_email(total_equity: float, drawdown_pct: float,
                                 account_details: list) -> tuple:
    """Build portfolio-level breach alert."""
    severity = "CRITICAL" if drawdown_pct <= -10.0 else "WARNING"
    color = "#cc0000" if severity == "CRITICAL" else "#e6a800"

    subject = f"[FIDUS {severity}] Portfolio Drawdown {drawdown_pct:+.2f}% — Total Equity ${total_equity:,.0f}"

    rows = ""
    for a in account_details:
        rows += f"""<tr>
            <td style="padding: 6px 8px;">{a['account']}</td>
            <td style="padding: 6px 8px;">{a['manager']}</td>
            <td style="padding: 6px 8px; text-align: right;">${a['equity']:,.2f}</td>
            <td style="padding: 6px 8px; text-align: right; color: #ef4444;">{a['drawdown']:+.2f}%</td>
        </tr>"""

    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: {color}; color: white; padding: 15px 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">FIDUS PORTFOLIO {severity}</h2>
        </div>
        <div style="background: #1a1a2e; color: #e0e0e0; padding: 20px; border-radius: 0 0 8px 8px;">
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                <tr><td style="padding: 8px 0; color: #888;">Total Initial Capital</td><td style="text-align: right; font-weight: bold;">${TOTAL_INITIAL:,.2f}</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Current Portfolio Equity</td><td style="text-align: right; font-weight: bold; color: #ef4444;">${total_equity:,.2f}</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Portfolio Drawdown</td><td style="text-align: right; font-weight: bold; color: {color};">{drawdown_pct:+.2f}%</td></tr>
                <tr><td style="padding: 8px 0; color: #888;">Protection Line (10%)</td><td style="text-align: right;">${TOTAL_INITIAL * 0.90:,.2f}</td></tr>
            </table>
            <h3 style="color: #ccc; margin: 15px 0 8px 0; font-size: 14px;">Account Breakdown</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <tr style="color: #888;"><th style="text-align:left; padding:6px 8px;">Account</th><th style="text-align:left; padding:6px 8px;">Manager</th><th style="text-align:right; padding:6px 8px;">Equity</th><th style="text-align:right; padding:6px 8px;">DD%</th></tr>
                {rows}
            </table>
            <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 4px; font-size: 12px; color: #888;">
                FIDUS Layer 2 monitoring alert. Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
            </div>
        </div>
    </div>
    """
    return subject, body


# ═══════════════════════════════════════════
# ITEM A — ALERT RULES ON POLLING JOB
# ITEM C — EQUITY SNAPSHOT STORAGE
# ═══════════════════════════════════════════

async def run_risk_monitoring_cycle(db: AsyncIOMotorDatabase):
    """
    Called AFTER each VPS sync cycle (every 5 minutes).
    1. Reads current equity for all monitored accounts
    2. Computes drawdown vs initial allocation
    3. Stores equity snapshot (Item C)
    4. Checks alert thresholds and sends alerts (Item A)
    """
    try:
        now = datetime.now(timezone.utc)
        account_details = []
        total_equity = 0

        for account_id in MONITORED_ACCOUNTS:
            # Read current equity from mt5_accounts (source of truth, updated by VPS sync)
            acc_doc = await db.mt5_accounts.find_one(
                {"account": account_id},
                {"_id": 0, "equity": 1, "balance": 1, "manager_name": 1,
                 "open_positions_count": 1, "open_positions": 1,
                 "warning_threshold": 1, "halt_threshold": 1,
                 "alert_status": 1, "last_sync_timestamp": 1}
            )
            if not acc_doc:
                continue

            equity = acc_doc.get("equity", 0) or 0
            balance = acc_doc.get("balance", 0) or 0
            manager_name = acc_doc.get("manager_name", f"Account {account_id}")
            initial_alloc = INITIAL_ALLOCATIONS.get(account_id, 0)
            open_positions = acc_doc.get("open_positions_count", 0) or 0

            if initial_alloc == 0:
                continue

            drawdown_pct = ((equity - initial_alloc) / initial_alloc) * 100
            total_equity += equity

            # Per-account thresholds (configurable, fall back to defaults)
            warn_thresh = acc_doc.get("warning_threshold", DEFAULT_WARNING_THRESHOLD)
            halt_thresh = acc_doc.get("halt_threshold", DEFAULT_HALT_THRESHOLD)

            # ── Item C: Store equity snapshot ──
            snapshot = {
                "account": account_id,
                "timestamp": now,
                "equity": equity,
                "balance": balance,
                "initial_allocation": initial_alloc,
                "drawdown_pct": round(drawdown_pct, 4),
                "open_positions": open_positions,
                "breach_flags": []
            }

            # ── Item A: Check thresholds ──
            if drawdown_pct <= -halt_thresh:
                snapshot["breach_flags"].append("CRITICAL")
                await _maybe_send_alert(
                    db, account_id, "halt", manager_name, equity,
                    drawdown_pct, halt_thresh, initial_alloc, now
                )
                # Set alert status on account
                await db.mt5_accounts.update_one(
                    {"account": account_id},
                    {"$set": {"alert_status": "CRITICAL", "alert_status_updated": now}}
                )

            elif drawdown_pct <= -warn_thresh:
                snapshot["breach_flags"].append("WARNING")
                await _maybe_send_alert(
                    db, account_id, "warning", manager_name, equity,
                    drawdown_pct, warn_thresh, initial_alloc, now
                )
                await db.mt5_accounts.update_one(
                    {"account": account_id},
                    {"$set": {"alert_status": "WARNING", "alert_status_updated": now}}
                )
            else:
                # Clear alert status if equity recovered
                if acc_doc.get("alert_status") in ("WARNING", "CRITICAL"):
                    await db.mt5_accounts.update_one(
                        {"account": account_id},
                        {"$set": {"alert_status": "OK", "alert_status_updated": now}}
                    )

            await db.equity_snapshots.insert_one(snapshot)

            account_details.append({
                "account": account_id,
                "manager": manager_name,
                "equity": equity,
                "drawdown": drawdown_pct,
                "initial": initial_alloc,
                "alert_status": "CRITICAL" if drawdown_pct <= -halt_thresh else "WARNING" if drawdown_pct <= -warn_thresh else "OK"
            })

        # ── Portfolio-level check ──
        if total_equity > 0:
            portfolio_dd = ((total_equity - TOTAL_INITIAL) / TOTAL_INITIAL) * 100

            # Store portfolio snapshot
            await db.equity_snapshots.insert_one({
                "account": "PORTFOLIO",
                "timestamp": now,
                "equity": total_equity,
                "balance": total_equity,
                "initial_allocation": TOTAL_INITIAL,
                "drawdown_pct": round(portfolio_dd, 4),
                "open_positions": sum(a.get("open_positions", 0) for a in account_details if isinstance(a.get("open_positions"), (int, float))),
                "breach_flags": ["CRITICAL" if portfolio_dd <= -10 else "WARNING" if portfolio_dd <= -5 else "OK"],
                "account_details": account_details
            })

            # Portfolio alert
            if portfolio_dd <= -10:
                await _maybe_send_portfolio_alert(db, total_equity, portfolio_dd, account_details, now)
            elif portfolio_dd <= -5:
                await _maybe_send_portfolio_alert(db, total_equity, portfolio_dd, account_details, now)

        # ── Cleanup old snapshots (Item C: 90-day retention) ──
        cutoff = now - timedelta(days=SNAPSHOT_RETENTION_DAYS)
        deleted = await db.equity_snapshots.delete_many({"timestamp": {"$lt": cutoff}})
        if deleted.deleted_count > 0:
            logger.info(f"[RISK] Cleaned {deleted.deleted_count} old snapshots")

        logger.info(f"[RISK] Monitoring cycle complete: {len(account_details)} accounts checked, portfolio DD: {portfolio_dd:+.2f}%")

    except Exception as e:
        logger.error(f"[RISK] Monitoring cycle error: {e}", exc_info=True)


async def _maybe_send_alert(db, account_id, alert_type, manager_name,
                             equity, drawdown_pct, threshold, initial_alloc, now):
    """Send alert with deduplication (1 per account per type per 60 min)."""
    # Check for recent duplicate
    recent = await db.alerts.find_one({
        "account": account_id,
        "alert_type": alert_type,
        "sent_at": {"$gte": now - timedelta(minutes=DEDUP_WINDOW_MINUTES)}
    })
    if recent:
        return  # Already alerted recently

    # Build and send email
    subject, body = build_alert_email(
        alert_type, account_id, manager_name,
        equity, drawdown_pct, threshold, initial_alloc
    )
    email_sent = send_alert_email(subject, body)

    # Send Telegram
    severity = "🔴 CRITICAL" if alert_type == "halt" else "⚠️ WARNING"
    tg_msg = (
        f"{severity} <b>FIDUS Risk Alert</b>\n\n"
        f"<b>Account:</b> {account_id} ({manager_name})\n"
        f"<b>Drawdown:</b> {drawdown_pct:+.2f}%\n"
        f"<b>Equity:</b> ${equity:,.2f}\n"
        f"<b>Threshold:</b> {threshold}%\n"
        f"<b>Time:</b> {now.strftime('%Y-%m-%d %H:%M UTC')}"
    )
    telegram_sent = send_telegram_alert(tg_msg)

    # Write alert record to MongoDB
    await db.alerts.insert_one({
        "account": account_id,
        "alert_type": alert_type,
        "manager_name": manager_name,
        "threshold": threshold,
        "actual_value": equity,
        "drawdown_pct": round(drawdown_pct, 4),
        "initial_allocation": initial_alloc,
        "sent_at": now,
        "email_sent": email_sent,
        "telegram_sent": telegram_sent,
        "resolved_at": None,
        "resolved_by": None
    })

    logger.warning(f"[ALERT] {alert_type.upper()} for account {account_id} ({manager_name}): DD {drawdown_pct:+.2f}%, equity ${equity:,.2f}")


async def _maybe_send_portfolio_alert(db, total_equity, drawdown_pct, account_details, now):
    """Send portfolio-level alert with dedup."""
    alert_type = "portfolio_critical" if drawdown_pct <= -10 else "portfolio_warning"

    recent = await db.alerts.find_one({
        "account": "PORTFOLIO",
        "alert_type": alert_type,
        "sent_at": {"$gte": now - timedelta(minutes=DEDUP_WINDOW_MINUTES)}
    })
    if recent:
        return

    subject, body = build_portfolio_alert_email(total_equity, drawdown_pct, account_details)
    email_sent = send_alert_email(subject, body)

    # Send Telegram
    severity = "🔴" if "critical" in alert_type else "⚠️"
    acct_lines = "\n".join([f"  • {a['manager']} ({a['account']}): {a['drawdown']:+.2f}%" for a in account_details])
    tg_msg = (
        f"{severity} <b>FIDUS Portfolio Alert</b>\n\n"
        f"<b>Portfolio DD:</b> {drawdown_pct:+.2f}%\n"
        f"<b>Equity:</b> ${total_equity:,.2f}\n\n"
        f"<b>Accounts:</b>\n{acct_lines}\n\n"
        f"<b>Time:</b> {now.strftime('%Y-%m-%d %H:%M UTC')}"
    )
    telegram_sent = send_telegram_alert(tg_msg)

    await db.alerts.insert_one({
        "account": "PORTFOLIO",
        "alert_type": alert_type,
        "threshold": 10.0 if "critical" in alert_type else 5.0,
        "actual_value": total_equity,
        "drawdown_pct": round(drawdown_pct, 4),
        "initial_allocation": TOTAL_INITIAL,
        "sent_at": now,
        "email_sent": email_sent,
        "telegram_sent": telegram_sent,
        "account_breakdown": account_details,
        "resolved_at": None,
        "resolved_by": None
    })


# ═══════════════════════════════════════════
# ITEM D — EXPOSURE AGGREGATION
# ═══════════════════════════════════════════

async def get_exposure_aggregation(db: AsyncIOMotorDatabase) -> dict:
    """
    Cross-account instrument exposure. Read-only.
    For each instrument, aggregate total lots across all monitored accounts.
    """
    exposure = {}
    total_equity = 0

    for account_id in MONITORED_ACCOUNTS:
        acc = await db.mt5_accounts.find_one(
            {"account": account_id},
            {"_id": 0, "equity": 1, "open_positions": 1, "manager_name": 1}
        )
        if not acc:
            continue

        equity = acc.get("equity", 0) or 0
        total_equity += equity
        positions = acc.get("open_positions", []) or []

        for pos in positions:
            symbol = pos.get("symbol", "UNKNOWN")
            volume = abs(pos.get("volume", 0) or 0)
            profit = pos.get("profit", 0) or 0
            notional = abs(pos.get("price", 0) or 0) * volume * 100  # Approximate

            if symbol not in exposure:
                exposure[symbol] = {"symbol": symbol, "total_lots": 0, "accounts": [], "total_profit": 0, "total_notional": 0}

            exposure[symbol]["total_lots"] += volume
            exposure[symbol]["total_profit"] += profit
            exposure[symbol]["total_notional"] += notional
            exposure[symbol]["accounts"].append({
                "account": account_id,
                "manager": acc.get("manager_name", ""),
                "lots": volume,
                "profit": profit
            })

    # Compute % of portfolio for each instrument
    for sym, data in exposure.items():
        data["pct_of_portfolio"] = round((data["total_notional"] / total_equity * 100), 2) if total_equity > 0 else 0
        data["account_count"] = len(data["accounts"])

    return {
        "total_equity": total_equity,
        "instruments": sorted(exposure.values(), key=lambda x: x["total_lots"], reverse=True),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ═══════════════════════════════════════════
# ITEM H — DATA HEALTH PER ACCOUNT
# ═══════════════════════════════════════════

async def get_account_data_health(db: AsyncIOMotorDatabase, account_id: int) -> dict:
    """Returns data health status for an account."""
    now = datetime.now(timezone.utc)

    acc = await db.mt5_accounts.find_one({"account": account_id}, {"_id": 0})
    if not acc:
        return {"error": f"Account {account_id} not found"}

    last_sync = acc.get("last_sync_timestamp")
    if last_sync and isinstance(last_sync, datetime):
        if last_sync.tzinfo is None:
            last_sync = last_sync.replace(tzinfo=timezone.utc)
        data_gap_hours = (now - last_sync).total_seconds() / 3600
    else:
        data_gap_hours = None

    # Trade count
    trade_count = await db.mt5_deals_history.count_documents({"account": account_id, "type": {"$ne": 2}})

    # Last trade
    last_trade = await db.mt5_deals_history.find_one(
        {"account": account_id, "type": {"$ne": 2}},
        {"_id": 0, "time": 1},
        sort=[("time", -1)]
    )

    # Latest snapshot
    latest_snapshot = await db.equity_snapshots.find_one(
        {"account": account_id},
        {"_id": 0, "timestamp": 1, "drawdown_pct": 1},
        sort=[("timestamp", -1)]
    )

    # Determine status
    if data_gap_hours is None:
        bridge_status = "NO_DATA"
    elif data_gap_hours < 0.5:
        bridge_status = "SYNCED"
    elif data_gap_hours < 4:
        bridge_status = "STALE"
    else:
        bridge_status = "OFFLINE"

    return {
        "account": account_id,
        "manager_name": acc.get("manager_name", ""),
        "last_equity_sync": last_sync.isoformat() if last_sync else None,
        "data_gap_hours": round(data_gap_hours, 2) if data_gap_hours else None,
        "trade_count": trade_count,
        "last_trade_sync": last_trade["time"].isoformat() if last_trade and last_trade.get("time") else None,
        "bridge_status": bridge_status,
        "alert_status": acc.get("alert_status", "OK"),
        "equity": acc.get("equity", 0),
        "drawdown_pct": latest_snapshot.get("drawdown_pct") if latest_snapshot else None,
        "timestamp": now.isoformat()
    }
