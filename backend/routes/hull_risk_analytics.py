"""
FIDUS Hull Risk Analytics Engine
Per-trade risk analysis, VaR/CVaR, session analysis, drawdown events.
Based on John C. Hull institutional risk management methodology.
"""

from fastapi import APIRouter, HTTPException, Header
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import Optional
import os, logging, jwt, math
import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/manager", tags=["Hull Risk Analytics"])

JWT_SECRET = os.environ.get("JWT_SECRET", "fidus-manager-secret-2026")
JWT_ALGORITHM = "HS256"
ADMIN_JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "fidus-production-secret-2025-secure-key")


async def get_db():
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    return client.fidus_production


def _auth(authorization: str, account_id: int):
    """Validate manager or admin token and account access."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Auth required")
    token = authorization.replace("Bearer ", "")
    # Try manager token
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") == "manager":
            if account_id not in payload.get("allowed_accounts", []):
                raise HTTPException(status_code=403, detail="Access denied")
            return payload
    except jwt.InvalidTokenError:
        pass
    # Try admin token
    try:
        payload = jwt.decode(token, ADMIN_JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ═══════════════════════════════════════════════════════
# 1. PER-TRADE RISK ANALYSIS
# ═══════════════════════════════════════════════════════

@router.get("/trade-risk-analysis/{account_id}")
async def get_per_trade_risk_analysis(account_id: int, days: int = 14, authorization: str = Header(None)):
    """
    Per-trade risk breakdown: risk % of equity, drawdown contribution,
    position sizing vs Hull limits, flagged violations.
    """
    _auth(authorization, account_id)
    db = await get_db()

    acc = await db.mt5_accounts.find_one({"account": account_id}, {"_id": 0, "equity": 1, "initial_allocation": 1, "manager_name": 1})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    equity = float(acc.get("equity", 0) or 0)
    initial = float(acc.get("initial_allocation", 0) or 0)
    if initial == 0:
        initial = equity

    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Get all closed trades (entry=1 means close, or profit != 0)
    trades = await db.mt5_deals_history.find(
        {"account": account_id, "type": {"$ne": 2}, "time": {"$gte": since}, "profit": {"$ne": 0}},
        {"_id": 0, "symbol": 1, "profit": 1, "volume": 1, "time": 1, "price": 1, "entry": 1}
    ).sort("time", 1).to_list(2000)

    # Hull risk limits
    MAX_RISK_PER_TRADE = 0.01  # 1% of equity
    risk_budget = equity * MAX_RISK_PER_TRADE

    # Build per-trade analysis
    running_equity = initial
    peak_equity = initial
    analyzed = []

    for t in trades:
        profit = float(t.get("profit", 0))
        volume = float(t.get("volume", 0) or 0)
        symbol = t.get("symbol", "UNKNOWN")
        price = float(t.get("price", 0) or 0)
        tm = t.get("time")

        running_equity += profit
        peak_equity = max(peak_equity, running_equity)

        # Risk calculations
        risk_pct = (abs(profit) / running_equity * 100) if running_equity > 0 else 0
        dd_contribution = (profit / peak_equity * 100) if peak_equity > 0 and profit < 0 else 0
        dd_from_peak = ((running_equity - peak_equity) / peak_equity * 100) if peak_equity > 0 else 0

        # Position sizing: notional exposure
        notional = volume * price * 100  # Approximate for CFDs
        margin_used_pct = (notional / running_equity * 100) if running_equity > 0 else 0

        # Violations
        violations = []
        if abs(profit) > risk_budget:
            violations.append({"rule": "Risk Per Trade > 1%", "actual": f"{risk_pct:.2f}%", "limit": "1.00%", "severity": "HIGH"})
        if profit < 0 and abs(profit) > equity * 0.02:
            violations.append({"rule": "Single Loss > 2%", "actual": f"{risk_pct:.2f}%", "limit": "2.00%", "severity": "CRITICAL"})
        if margin_used_pct > 25:
            violations.append({"rule": "Margin > 25%", "actual": f"{margin_used_pct:.1f}%", "limit": "25%", "severity": "WARNING"})

        analyzed.append({
            "time": tm.isoformat() if tm else None,
            "symbol": symbol,
            "volume": volume,
            "price": round(price, 2),
            "profit": round(profit, 2),
            "risk_pct": round(risk_pct, 4),
            "dd_contribution": round(dd_contribution, 4),
            "dd_from_peak": round(dd_from_peak, 4),
            "running_equity": round(running_equity, 2),
            "notional": round(notional, 2),
            "margin_used_pct": round(margin_used_pct, 2),
            "compliant": len(violations) == 0,
            "violations": violations
        })

    # Summary
    violation_trades = [t for t in analyzed if not t["compliant"]]
    max_single_risk = max((t["risk_pct"] for t in analyzed), default=0)
    max_dd_contribution = min((t["dd_contribution"] for t in analyzed), default=0)
    avg_risk = sum(t["risk_pct"] for t in analyzed) / len(analyzed) if analyzed else 0

    return {
        "success": True,
        "account": account_id,
        "manager_name": acc.get("manager_name", ""),
        "period_days": days,
        "total_trades": len(analyzed),
        "compliant_trades": len(analyzed) - len(violation_trades),
        "violation_trades": len(violation_trades),
        "compliance_rate": round((len(analyzed) - len(violation_trades)) / len(analyzed) * 100, 1) if analyzed else 100,
        "max_single_risk_pct": round(max_single_risk, 4),
        "max_dd_contribution_pct": round(max_dd_contribution, 4),
        "avg_risk_per_trade": round(avg_risk, 4),
        "risk_budget": round(risk_budget, 2),
        "trades": analyzed[-200:],  # Last 200 for display
        "violations_summary": _summarize_violations(violation_trades)
    }


def _summarize_violations(violation_trades):
    """Group violations by rule."""
    rules = {}
    for t in violation_trades:
        for v in t.get("violations", []):
            r = v["rule"]
            if r not in rules:
                rules[r] = {"rule": r, "count": 0, "severity": v["severity"], "worst": 0}
            rules[r]["count"] += 1
            actual_val = float(v["actual"].replace("%", ""))
            rules[r]["worst"] = max(rules[r]["worst"], actual_val)
    return sorted(rules.values(), key=lambda x: x["count"], reverse=True)


# ═══════════════════════════════════════════════════════
# 2. HULL VaR / CVaR ENGINE
# ═══════════════════════════════════════════════════════

@router.get("/var-analysis/{account_id}")
async def get_var_cvar_analysis(account_id: int, days: int = 30, authorization: str = Header(None)):
    """
    Value at Risk (VaR) and Conditional VaR (Expected Shortfall)
    using historical simulation — Hull methodology.
    Includes per-session risk breakdown and Monte Carlo projections.
    """
    _auth(authorization, account_id)
    db = await get_db()

    acc = await db.mt5_accounts.find_one({"account": account_id}, {"_id": 0, "equity": 1, "initial_allocation": 1, "manager_name": 1})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    equity = float(acc.get("equity", 0) or 0)

    # Get daily P&L
    pipeline = [
        {"$match": {"account": account_id, "type": {"$ne": 2}, "profit": {"$ne": 0}}},
        {"$addFields": {"day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$time"}},
                         "hour": {"$hour": "$time"}}},
        {"$group": {
            "_id": "$day",
            "daily_pnl": {"$sum": "$profit"},
            "trade_count": {"$sum": 1},
        }},
        {"$sort": {"_id": -1}},
        {"$limit": days}
    ]
    daily = list(await db.mt5_deals_history.aggregate(pipeline).to_list(days))
    daily_returns = [float(d["daily_pnl"]) for d in daily if d["daily_pnl"] != 0]

    if len(daily_returns) < 5:
        return {"success": True, "message": "Insufficient data for VaR calculation", "min_days_needed": 5}

    returns_array = np.array(daily_returns)

    # Historical VaR (95% and 99%)
    var_95 = float(np.percentile(returns_array, 5))
    var_99 = float(np.percentile(returns_array, 1))

    # CVaR (Expected Shortfall) — average of losses beyond VaR
    losses_beyond_95 = returns_array[returns_array <= var_95]
    cvar_95 = float(np.mean(losses_beyond_95)) if len(losses_beyond_95) > 0 else var_95

    losses_beyond_99 = returns_array[returns_array <= var_99]
    cvar_99 = float(np.mean(losses_beyond_99)) if len(losses_beyond_99) > 0 else var_99

    # Parametric VaR (assuming normal — Hull comparison)
    mean_ret = float(np.mean(returns_array))
    std_ret = float(np.std(returns_array))
    parametric_var_95 = mean_ret - 1.645 * std_ret
    parametric_var_99 = mean_ret - 2.326 * std_ret

    # Per-session analysis
    session_pipeline = [
        {"$match": {"account": account_id, "type": {"$ne": 2}, "profit": {"$ne": 0}}},
        {"$addFields": {"hour": {"$hour": "$time"}}},
        {"$addFields": {"session": {"$switch": {
            "branches": [
                {"case": {"$and": [{"$gte": ["$hour", 0]}, {"$lt": ["$hour", 8]}]}, "then": "Asian"},
                {"case": {"$and": [{"$gte": ["$hour", 8]}, {"$lt": ["$hour", 13]}]}, "then": "London"},
                {"case": {"$and": [{"$gte": ["$hour", 13]}, {"$lt": ["$hour", 21]}]}, "then": "New York"},
            ],
            "default": "After Hours"
        }}}},
        {"$group": {
            "_id": "$session",
            "total_pnl": {"$sum": "$profit"},
            "trade_count": {"$sum": 1},
            "wins": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, 1, 0]}},
            "avg_profit": {"$avg": "$profit"},
            "max_loss": {"$min": "$profit"},
            "max_win": {"$max": "$profit"},
            "loss_sum": {"$sum": {"$cond": [{"$lt": ["$profit", 0]}, "$profit", 0]}},
            "win_sum": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, "$profit", 0]}},
        }}
    ]
    sessions = list(await db.mt5_deals_history.aggregate(session_pipeline).to_list(10))

    session_data = []
    for s in sessions:
        tc = s["trade_count"]
        wr = (s["wins"] / tc * 100) if tc > 0 else 0
        pf = abs(s["win_sum"] / s["loss_sum"]) if s["loss_sum"] != 0 else 0
        session_data.append({
            "session": s["_id"],
            "total_pnl": round(float(s["total_pnl"]), 2),
            "trade_count": tc,
            "win_rate": round(wr, 1),
            "profit_factor": round(pf, 2),
            "avg_profit": round(float(s["avg_profit"]), 2),
            "max_loss": round(float(s["max_loss"]), 2),
            "max_win": round(float(s["max_win"]), 2),
            "risk_concentration": round(abs(float(s["loss_sum"])) / abs(sum(float(ss["loss_sum"]) for ss in sessions)) * 100, 1) if sum(abs(float(ss["loss_sum"])) for ss in sessions) > 0 else 0
        })

    # Monte Carlo: project 5-day drawdown paths (100 simulations)
    mc_paths = []
    n_sims = 100
    n_days_forward = 5
    for _ in range(n_sims):
        path = [equity]
        for d in range(n_days_forward):
            daily_change = float(np.random.choice(returns_array))
            path.append(path[-1] + daily_change)
        mc_paths.append(path)

    mc_array = np.array(mc_paths)
    mc_worst_case = [round(float(np.percentile(mc_array[:, d], 5)), 2) for d in range(n_days_forward + 1)]
    mc_best_case = [round(float(np.percentile(mc_array[:, d], 95)), 2) for d in range(n_days_forward + 1)]
    mc_median = [round(float(np.percentile(mc_array[:, d], 50)), 2) for d in range(n_days_forward + 1)]
    mc_max_dd = float(min(mc_array[:, -1]) - equity)

    # Risk metrics
    sharpe = (mean_ret / std_ret * math.sqrt(252)) if std_ret > 0 else 0
    sortino_downside = returns_array[returns_array < 0]
    downside_std = float(np.std(sortino_downside)) if len(sortino_downside) > 0 else std_ret
    sortino = (mean_ret / downside_std * math.sqrt(252)) if downside_std > 0 else 0

    # Max consecutive losses
    max_consec = 0
    current_consec = 0
    for r in returns_array:
        if r < 0:
            current_consec += 1
            max_consec = max(max_consec, current_consec)
        else:
            current_consec = 0

    return {
        "success": True,
        "account": account_id,
        "manager_name": acc.get("manager_name", ""),
        "equity": equity,
        "period_days": len(daily_returns),
        "var": {
            "historical_95": round(var_95, 2),
            "historical_99": round(var_99, 2),
            "parametric_95": round(parametric_var_95, 2),
            "parametric_99": round(parametric_var_99, 2),
            "as_pct_equity_95": round(var_95 / equity * 100, 2) if equity > 0 else 0,
            "as_pct_equity_99": round(var_99 / equity * 100, 2) if equity > 0 else 0,
        },
        "cvar": {
            "expected_shortfall_95": round(cvar_95, 2),
            "expected_shortfall_99": round(cvar_99, 2),
            "as_pct_equity_95": round(cvar_95 / equity * 100, 2) if equity > 0 else 0,
            "as_pct_equity_99": round(cvar_99 / equity * 100, 2) if equity > 0 else 0,
        },
        "statistics": {
            "mean_daily_pnl": round(mean_ret, 2),
            "std_daily_pnl": round(std_ret, 2),
            "sharpe_annualized": round(sharpe, 2),
            "sortino_annualized": round(sortino, 2),
            "max_consecutive_losses": max_consec,
            "positive_days": int(np.sum(returns_array > 0)),
            "negative_days": int(np.sum(returns_array < 0)),
            "best_day": round(float(np.max(returns_array)), 2),
            "worst_day": round(float(np.min(returns_array)), 2),
            "skewness": round(float(np.mean(((returns_array - mean_ret) / std_ret) ** 3)) if std_ret > 0 else 0, 2),
            "kurtosis": round(float(np.mean(((returns_array - mean_ret) / std_ret) ** 4) - 3) if std_ret > 0 else 0, 2),
        },
        "sessions": sorted(session_data, key=lambda x: x["total_pnl"], reverse=True),
        "monte_carlo": {
            "simulations": n_sims,
            "days_forward": n_days_forward,
            "worst_case_5pct": mc_worst_case,
            "best_case_95pct": mc_best_case,
            "median": mc_median,
            "projected_max_dd": round(mc_max_dd, 2),
            "prob_below_initial": round(float(np.sum(mc_array[:, -1] < (equity * 0.95)) / n_sims * 100), 1),
        }
    }


# ═══════════════════════════════════════════════════════
# 3. DRAWDOWN EVENTS + ALERTS FOR MANAGER
# ═══════════════════════════════════════════════════════

@router.get("/risk-alerts/{account_id}")
async def get_manager_risk_alerts(account_id: int, authorization: str = Header(None)):
    """Active risk alerts filtered to this manager's account."""
    _auth(authorization, account_id)
    db = await get_db()

    alerts = await db.alerts.find(
        {"account": account_id},
        {"_id": 0}
    ).sort("sent_at", -1).to_list(20)

    # Serialize datetimes
    for a in alerts:
        for k in list(a.keys()):
            if isinstance(a[k], datetime):
                a[k] = a[k].isoformat()

    return {"success": True, "alerts": alerts, "count": len(alerts)}



# ═══════════════════════════════════════════════════════
# COPY CHAIN P&L ATTRIBUTION
# Shows how each sub-strategy contributes to 2208
# ═══════════════════════════════════════════════════════

@router.get("/copy-chain-attribution/{account_id}")
async def get_copy_chain_attribution(account_id: int, days: int = 30, authorization: str = Header(None)):
    """
    P&L attribution by analyzing the MASTER account's (2210) actual trades
    and matching each trade to the sub-account that originated it (by symbol + timing).
    Also includes instrument weight analysis.
    """
    _auth(authorization, account_id)
    db = await get_db()

    acc = await db.mt5_accounts.find_one({"account": account_id}, {"_id": 0, "copy_sources": 1, "manager_name": 1, "equity": 1, "initial_allocation": 1, "allocation_start_date": 1})
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    # Get master account (2210)
    master_acc = None
    master_id = None
    if acc.get("copy_sources"):
        master_id = acc["copy_sources"][0].get("master_account")
        if master_id:
            master_acc = await db.mt5_accounts.find_one({"account": master_id}, {"_id": 0, "copy_sources": 1, "manager_name": 1, "account": 1, "allocation_start_date": 1})

    # Build list of sub-strategies from master
    sub_strategies = []
    sub_account_ids = []
    if master_acc and master_acc.get("copy_sources"):
        for cs in master_acc["copy_sources"]:
            sub_strategies.append({"account": cs["master_account"], "name": cs["master_name"], "ratio": cs.get("ratio", 1.0)})
            sub_account_ids.append(cs["master_account"])

    # Use allocation start date (March 23) or fallback to days
    alloc_date = acc.get("allocation_start_date") or master_acc.get("allocation_start_date") if master_acc else None
    if alloc_date:
        if alloc_date.tzinfo is None:
            alloc_date = alloc_date.replace(tzinfo=timezone.utc)
        since = alloc_date
    else:
        since = datetime.now(timezone.utc) - timedelta(days=days)

    # Get ALL trades from master account (2210) since allocation date
    master_trades = await db.mt5_deals_history.find(
        {"account": master_id, "type": {"$ne": 2}, "profit": {"$ne": 0}, "time": {"$gte": since}},
        {"_id": 0, "symbol": 1, "profit": 1, "time": 1, "volume": 1}
    ).sort("time", 1).to_list(5000)

    # Attribution: match each master trade to the sub-account that originated it
    attribution = {acc_id: {"account": acc_id, "name": "", "pnl": 0, "trades": 0, "wins": 0, "symbols": []} for acc_id in sub_account_ids}
    attribution["unmatched"] = {"account": 0, "name": "Unmatched", "pnl": 0, "trades": 0, "wins": 0, "symbols": []}
    for s in sub_strategies:
        if s["account"] in attribution:
            attribution[s["account"]]["name"] = s["name"]

    for trade in master_trades:
        sym = trade.get("symbol", "")
        tm = trade.get("time")
        profit = float(trade.get("profit", 0))
        if not tm or not sym:
            continue

        # Find matching sub-account trade (same symbol, within 60 seconds)
        best_match = None
        for sub_id in sub_account_ids:
            match = await db.mt5_deals_history.find_one({
                "account": sub_id,
                "symbol": sym,
                "type": {"$ne": 2},
                "time": {"$gte": tm - timedelta(seconds=60), "$lte": tm + timedelta(seconds=60)}
            })
            if match:
                best_match = sub_id
                break

        target = best_match if best_match else "unmatched"
        attribution[target]["pnl"] += profit
        attribution[target]["trades"] += 1
        if profit > 0:
            attribution[target]["wins"] += 1
        if sym not in attribution[target]["symbols"]:
            attribution[target]["symbols"].append(sym)

    # Build result
    total_pnl = sum(a["pnl"] for a in attribution.values())
    result_attribution = []
    for key, a in attribution.items():
        if a["trades"] == 0:
            continue
        wr = (a["wins"] / a["trades"] * 100) if a["trades"] > 0 else 0
        pct = (abs(a["pnl"]) / abs(total_pnl) * 100) if total_pnl != 0 else 0
        result_attribution.append({
            "account": a["account"],
            "name": a["name"],
            "ratio": 1.0,
            "pnl": round(a["pnl"], 2),
            "contributed_pnl": round(a["pnl"], 2),
            "trades": a["trades"],
            "wins": a["wins"],
            "win_rate": round(wr, 1),
            "profit_factor": 0,
            "pct_of_total": round(pct, 1),
            "symbols": a["symbols"],
        })
    result_attribution.sort(key=lambda x: abs(x["contributed_pnl"]), reverse=True)

    # ── INSTRUMENT ANALYSIS from master account's own trades ──
    instrument_pipeline = [
        {"$match": {"account": master_id, "type": {"$ne": 2}, "profit": {"$ne": 0}, "time": {"$gte": since}}},
        {"$group": {
            "_id": "$symbol",
            "total_pnl": {"$sum": "$profit"},
            "trades": {"$sum": 1},
            "wins": {"$sum": {"$cond": [{"$gt": ["$profit", 0]}, 1, 0]}},
            "total_volume": {"$sum": "$volume"},
        }},
        {"$sort": {"total_pnl": -1}}
    ]
    instruments = list(await db.mt5_deals_history.aggregate(instrument_pipeline).to_list(50))

    total_inst_pnl = sum(abs(float(i["total_pnl"])) for i in instruments) or 1
    instrument_data = []
    for inst in instruments:
        sym = inst["_id"] or "UNKNOWN"
        pnl = float(inst["total_pnl"])
        tc = inst["trades"]
        wr = (inst["wins"] / tc * 100) if tc > 0 else 0
        weight = abs(pnl) / total_inst_pnl * 100
        category = "GOLD" if "XAU" in sym.upper() else "FOREX" if any(x in sym.upper() for x in ["EUR","GBP","USD","JPY","AUD","CAD","CHF","NZD"]) and "XAU" not in sym.upper() else "INDICES" if any(x in sym.upper() for x in ["NAS","US30","DAX","DE40","SPX"]) else "CRYPTO" if any(x in sym.upper() for x in ["BTC","ETH"]) else "OTHER"
        instrument_data.append({"symbol": sym, "category": category, "pnl": round(pnl, 2), "trades": tc, "wins": inst["wins"], "win_rate": round(wr, 1), "weight_pct": round(weight, 1), "total_volume": round(float(inst.get("total_volume", 0)), 2)})

    categories = {}
    for i in instrument_data:
        cat = i["category"]
        if cat not in categories:
            categories[cat] = {"category": cat, "pnl": 0, "trades": 0, "instruments": []}
        categories[cat]["pnl"] += i["pnl"]
        categories[cat]["trades"] += i["trades"]
        categories[cat]["instruments"].append(i["symbol"])
    for cat in categories.values():
        cat["weight_pct"] = round(abs(cat["pnl"]) / total_inst_pnl * 100, 1)
        cat["pnl"] = round(cat["pnl"], 2)

    return {
        "success": True,
        "account": account_id,
        "manager_name": acc.get("manager_name"),
        "equity": float(acc.get("equity", 0)),
        "period_start": since.isoformat(),
        "period_days": (datetime.now(timezone.utc) - since).days,
        "total_master_trades": len(master_trades),
        "copy_chain": {
            "master": {"account": master_acc["account"], "name": master_acc["manager_name"]} if master_acc else None,
            "sub_strategies": result_attribution,
            "total_contributed_pnl": round(total_pnl, 2),
        },
        "instruments": instrument_data,
        "categories": sorted(categories.values(), key=lambda x: abs(x["pnl"]), reverse=True),
    }
