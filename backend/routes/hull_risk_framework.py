"""
FIDUS Hull Risk Framework — Backend API
Prohibited trading calendar, position sizing calculator, stress testing.
"""

from fastapi import APIRouter, HTTPException, Header
from datetime import datetime, timezone, timedelta
from typing import Optional
import os, logging, math

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/risk-framework", tags=["Hull Risk Framework"])

# ═══════════════════════════════════════════
# PROHIBITED TRADING CALENDAR 2026
# FOMC, NFP, CPI, Fed Speeches, Holidays
# ═══════════════════════════════════════════

PROHIBITED_EVENTS_2026 = [
    # FOMC Meetings (2-day, announce day 2)
    {"date": "2026-01-28", "type": "FOMC", "name": "FOMC Rate Decision", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    {"date": "2026-03-18", "type": "FOMC", "name": "FOMC Rate Decision + Dot Plot", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    {"date": "2026-05-06", "type": "FOMC", "name": "FOMC Rate Decision", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    {"date": "2026-06-17", "type": "FOMC", "name": "FOMC Rate Decision + Dot Plot", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    {"date": "2026-07-29", "type": "FOMC", "name": "FOMC Rate Decision", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    {"date": "2026-09-16", "type": "FOMC", "name": "FOMC Rate Decision + Dot Plot", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    {"date": "2026-11-04", "type": "FOMC", "name": "FOMC Rate Decision", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    {"date": "2026-12-16", "type": "FOMC", "name": "FOMC Rate Decision + Dot Plot", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    # NFP (First Friday of each month)
    {"date": "2026-01-09", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-02-06", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-03-06", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-04-03", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-05-08", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-06-05", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-07-02", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-08-07", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-09-04", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-10-02", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-11-06", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    {"date": "2026-12-04", "type": "NFP", "name": "Non-Farm Payrolls", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, INDICES"},
    # CPI (mid-month)
    {"date": "2026-01-14", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-02-11", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-03-11", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-04-14", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-05-13", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-06-10", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-07-14", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-08-12", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-09-15", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-10-13", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-11-10", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    {"date": "2026-12-09", "type": "CPI", "name": "CPI Inflation Report", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "FOREX, GOLD, BONDS"},
    # US Market Holidays (CLOSED)
    {"date": "2026-01-01", "type": "HOLIDAY", "name": "New Year's Day", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-01-19", "type": "HOLIDAY", "name": "Martin Luther King Jr Day", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-02-16", "type": "HOLIDAY", "name": "Presidents Day", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-04-03", "type": "HOLIDAY", "name": "Good Friday", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-05-25", "type": "HOLIDAY", "name": "Memorial Day", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-06-19", "type": "HOLIDAY", "name": "Juneteenth", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-07-03", "type": "HOLIDAY", "name": "Independence Day (Observed)", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-09-07", "type": "HOLIDAY", "name": "Labor Day", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-11-26", "type": "HOLIDAY", "name": "Thanksgiving", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-11-27", "type": "HOLIDAY", "name": "Black Friday (Early Close)", "impact": "REDUCED", "action": "EARLY CLOSE 1PM ET", "instruments": "US EQUITIES, INDICES"},
    {"date": "2026-12-25", "type": "HOLIDAY", "name": "Christmas Day", "impact": "CLOSED", "action": "MARKETS CLOSED", "instruments": "ALL"},
    # Jackson Hole + Other Major
    {"date": "2026-08-27", "type": "FED_SPEECH", "name": "Jackson Hole Symposium", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    {"date": "2026-08-28", "type": "FED_SPEECH", "name": "Jackson Hole Day 2", "impact": "CRITICAL", "action": "NO TRADING", "instruments": "ALL"},
    # Quarterly Options Expiry (Triple Witching)
    {"date": "2026-03-20", "type": "OPEX", "name": "Quad Witching", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "INDICES, OPTIONS"},
    {"date": "2026-06-19", "type": "OPEX", "name": "Quad Witching", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "INDICES, OPTIONS"},
    {"date": "2026-09-18", "type": "OPEX", "name": "Quad Witching", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "INDICES, OPTIONS"},
    {"date": "2026-12-18", "type": "OPEX", "name": "Quad Witching", "impact": "HIGH", "action": "REDUCE SIZE 50%", "instruments": "INDICES, OPTIONS"},
]


@router.get("/prohibited-calendar")
async def get_prohibited_calendar():
    """Full 2026 prohibited trading calendar with countdown to next event."""
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    events = []
    next_event = None
    active_today = []

    for ev in sorted(PROHIBITED_EVENTS_2026, key=lambda x: x["date"]):
        evt_date = datetime.strptime(ev["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_away = (evt_date - now).days
        is_past = days_away < 0
        is_today = ev["date"] == today

        event = {**ev, "days_away": days_away, "is_past": is_past, "is_today": is_today}
        events.append(event)

        if is_today:
            active_today.append(event)
        if not is_past and next_event is None:
            next_event = event

    # Group by month
    by_month = {}
    for ev in events:
        mk = ev["date"][:7]
        if mk not in by_month:
            by_month[mk] = []
        by_month[mk].append(ev)

    return {
        "success": True,
        "events": events,
        "by_month": by_month,
        "total_events": len(events),
        "next_event": next_event,
        "active_today": active_today,
        "today_is_prohibited": len(active_today) > 0,
    }


# ═══════════════════════════════════════════
# POSITION SIZING CALCULATOR (Hull Method)
# ═══════════════════════════════════════════

INSTRUMENTS = {
    "XAUUSD": {"name": "Gold", "class": "COMMODITIES", "contract_size": 100, "pip_value": 10, "avg_atr": 30, "stop_mult": 0.60, "max_lots_per_100k": 0.30},
    "NAS100": {"name": "NASDAQ 100", "class": "INDICES", "contract_size": 1, "pip_value": 1, "avg_atr": 250, "stop_mult": 0.80, "max_lots_per_100k": 3.0},
    "US30": {"name": "Dow Jones 30", "class": "INDICES", "contract_size": 1, "pip_value": 1, "avg_atr": 300, "stop_mult": 0.80, "max_lots_per_100k": 3.0},
    "EURUSD": {"name": "EUR/USD", "class": "FOREX_MAJOR", "contract_size": 100000, "pip_value": 10, "avg_atr": 0.0080, "stop_mult": 0.75, "max_lots_per_100k": 1.0},
    "GBPUSD": {"name": "GBP/USD", "class": "FOREX_MAJOR", "contract_size": 100000, "pip_value": 10, "avg_atr": 0.0100, "stop_mult": 0.75, "max_lots_per_100k": 1.0},
    "USDJPY": {"name": "USD/JPY", "class": "FOREX_MAJOR", "contract_size": 100000, "pip_value": 7.5, "avg_atr": 1.20, "stop_mult": 0.75, "max_lots_per_100k": 1.0},
    "USOIL": {"name": "WTI Crude Oil", "class": "COMMODITIES", "contract_size": 1000, "pip_value": 10, "avg_atr": 1.50, "stop_mult": 0.70, "max_lots_per_100k": 0.30},
    "BTCUSD": {"name": "Bitcoin", "class": "CRYPTO", "contract_size": 1, "pip_value": 1, "avg_atr": 2500, "stop_mult": 0.50, "max_lots_per_100k": 0.30},
    "ETHUSD": {"name": "Ethereum", "class": "CRYPTO", "contract_size": 1, "pip_value": 1, "avg_atr": 150, "stop_mult": 0.55, "max_lots_per_100k": 0.50},
}


@router.get("/position-calculator")
async def get_position_sizing(equity: float = 100000, risk_pct: float = 0.5):
    """Hull position sizing for all instruments at given equity and risk%."""
    risk_budget = equity * (risk_pct / 100)
    results = []

    for symbol, spec in INSTRUMENTS.items():
        atr = spec["avg_atr"]
        stop = atr * spec["stop_mult"]
        pip_val = spec["pip_value"]

        # Hull formula: Lots = Risk Budget / (Stop Distance × Pip Value)
        if stop > 0 and pip_val > 0:
            lots = risk_budget / (stop * pip_val)
        else:
            lots = 0

        max_lots = spec["max_lots_per_100k"] * (equity / 100000)
        recommended = min(lots, max_lots)
        notional = recommended * spec["contract_size"] * (atr * 100 if spec["class"] == "FOREX_MAJOR" else 1)

        results.append({
            "symbol": symbol,
            "name": spec["name"],
            "asset_class": spec["class"],
            "hull_lots": round(lots, 3),
            "max_lots": round(max_lots, 3),
            "recommended_lots": round(recommended, 3),
            "stop_distance": round(stop, 4),
            "stop_multiplier": spec["stop_mult"],
            "avg_atr": atr,
            "risk_per_trade": round(risk_budget, 2),
            "max_loss_at_stop": round(recommended * stop * pip_val, 2),
        })

    return {
        "success": True,
        "equity": equity,
        "risk_pct": risk_pct,
        "risk_budget": round(risk_budget, 2),
        "instruments": results,
    }


# ═══════════════════════════════════════════
# STRESS TESTING
# ═══════════════════════════════════════════

@router.get("/stress-test")
async def get_stress_test(equity: float = 407316):
    """Stress test: what-if scenarios at given equity."""
    scenarios = [
        {"name": "March 18 Gold Incident", "description": "Gold reversal -82 seconds, $65K loss across 3 accounts", "loss_pct": 14.68, "duration": "82 seconds", "trigger": "XAUUSD reversal"},
        {"name": "Flash Crash (2010-style)", "description": "Market drops 9% in minutes, recovers partially", "loss_pct": 9.0, "duration": "36 minutes", "trigger": "Liquidity vacuum"},
        {"name": "NFP Surprise", "description": "NFP misses by 200K jobs, USD drops 150 pips", "loss_pct": 3.5, "duration": "5 minutes", "trigger": "NFP release"},
        {"name": "FOMC Surprise Rate Hike", "description": "Unexpected 50bp hike, all assets reprice", "loss_pct": 8.0, "duration": "2 hours", "trigger": "FOMC statement"},
        {"name": "Black Swan (COVID-style)", "description": "Multi-day 30% market crash", "loss_pct": 30.0, "duration": "5 days", "trigger": "Pandemic/geopolitical"},
        {"name": "Broker Failure", "description": "Broker platform down during volatile market", "loss_pct": 15.0, "duration": "4 hours", "trigger": "Technical failure"},
        {"name": "Overnight Gap (Weekend)", "description": "Sunday open gaps 3% against positions", "loss_pct": 3.0, "duration": "Instant", "trigger": "Weekend event"},
        {"name": "Correlation Breakdown", "description": "All hedges fail simultaneously", "loss_pct": 12.0, "duration": "1 day", "trigger": "Systemic risk"},
    ]

    results = []
    for sc in scenarios:
        loss = equity * (sc["loss_pct"] / 100)
        surviving_equity = equity - loss
        recovery_needed = (loss / surviving_equity * 100) if surviving_equity > 0 else 999
        months_to_recover = (recovery_needed / 2.5) if surviving_equity > 0 else 999  # At 2.5% monthly

        results.append({
            **sc,
            "loss_amount": round(loss, 2),
            "surviving_equity": round(surviving_equity, 2),
            "recovery_pct_needed": round(recovery_needed, 2),
            "months_to_recover": round(months_to_recover, 1),
            "breaches_10pct": sc["loss_pct"] > 10,
            "severity": "CRITICAL" if sc["loss_pct"] > 10 else "HIGH" if sc["loss_pct"] > 5 else "MEDIUM",
        })

    return {"success": True, "equity": equity, "scenarios": results}
