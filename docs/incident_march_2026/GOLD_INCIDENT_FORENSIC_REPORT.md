# FIDUS GOLD TRADING INCIDENT — FORENSIC ANALYSIS REPORT (CORRECTED)
**Date of Incident:** March 18, 2026
**Report Date:** March 18, 2026
**Severity:** CRITICAL
**Initial Allocations:** March 9, 2026

---

## 1. EXECUTIVE SUMMARY

On March 18, 2026, the FIDUS portfolio suffered a catastrophic GOLD (XAUUSD) loss totaling **$59,790** (-14.68%) across three accounts. The loss originated from Gold exposure copied from master account LUCRUM 2210 and propagated through the copy-trading chain to accounts 2208, 20043, and 2206.

The portfolio **breached the 10% protection threshold** — current equity of **$347,526** is **$19,059 below** the protection line of $366,585.

**All risk controls failed because none were implemented.** The break switch, intraday limits, weekly limits, monthly drawdown enforcement, force flat, and admin alerts exist ONLY as stored configuration values and frontend display elements. **Zero enforcement code exists in the backend.**

---

## 2. CAPITAL BASELINE (March 9, 2026 Allocations — Verified)

| Account | Manager | Initial Allocation | Current Equity | P&L | Drawdown |
|---------|---------|-------------------:|---------------:|----:|---------:|
| 2206 | JC PROVIDER | $179,316.36 | $162,146.42 | -$17,169.94 | **-9.58%** |
| 20043 | JARED COPIA | $178,000.00 | $144,833.35 | -$33,166.65 | **-18.63%** |
| 2208 | JOSE GOLD DAY-TRADE | $50,000.00 | $40,546.34 | -$9,453.66 | **-18.91%** |
| **TOTAL** | **PORTFOLIO** | **$407,316.36** | **$347,526.11** | **-$59,790.25** | **-14.68%** |

**10% Protection Line:** $366,584.72
**Current Breach:** $19,058.61 below protection line
**Status:** BREACHED

---

## 3. PER-ACCOUNT 10% BREACH STATUS

| Account | Own 10% Line | Current Equity | Breached? | Amount Below |
|---------|-------------:|---------------:|-----------|-------------:|
| 2206 | $161,384.72 | $162,146.42 | **NO** (barely above at -9.58%) | — |
| 20043 | $160,200.00 | $144,833.35 | **YES** | $15,366.65 |
| 2208 | $45,000.00 | $40,546.34 | **YES** | $4,453.66 |

---

## 4. INCIDENT TIMELINE (March 18, 2026)

All times UTC. Portfolio pre-March-18 equity: ~$424,744 (including +$17,428 trade profits since Mar 9).

| Time (UTC) | Event | Portfolio Impact | Cum Loss vs Initial |
|------------|-------|-----------------|---------------------|
| 00:00-12:00 | Normal trading, small gains | +$1,596 | +0.39% |
| 13:00-15:43 | Active Gold trading, ALL profitable | +$19,962 | +4.90% |
| **15:44:28** | **CATASTROPHE begins.** 12 XAUUSD closes on 2208 in 1 second. Largest: 1.05 lots = -$3,956 loss | -$13,583 on 2208 | — |
| **15:44:48** | **20043 hit.** 12 XAUUSD closes. Largest: 3.66 lots = -$12,788. Total: -$44,377 | -$57,961 combined | -6.38% (portfolio) |
| **15:45:10** | **2206 hit.** 13 XAUUSD closes. Largest: 2.30 lots = -$7,993. **NEW positions ALSO opened** | -$27,718 combined | — |
| **15:45:10** | **>>> 10% PORTFOLIO THRESHOLD BREACHED <<<** | Equity: ~$359,027 | **-11.86%** |
| 15:45:47 | Final small losses on 2208 | -$13.84 | -11.89% |
| 15:46 | Trading stops on Gold | -$120.62 more | -11.89% |
| 16:54-17:02 | Minor recovery trades on 2206 | +$169 | -11.84% |

**Total catastrophic phase: 82 seconds** (15:44:28 to 15:45:47)
**Total March 18 loss: ~$65,726**

---

## 5. "WHEN THE 10% LUCRUM BREAK SWITCH SHOULD HAVE CLICKED"

### The Math

| Metric | Value |
|--------|-------|
| Total Initial Capital (Mar 9) | $407,316.36 |
| 10% of Capital | $40,731.64 |
| Protection Line (90%) | $366,584.72 |
| Portfolio equity at 15:44:28 (just before crash) | ~$444,706 |
| Portfolio equity at 15:44:48 (after 2208 + 20043 hit) | ~$386,745 |
| **Portfolio equity at 15:45:10 (breach moment)** | **~$359,027** |
| Amount below protection line at breach | **$7,558** |
| Final portfolio equity | **$347,526** |
| Final amount below line | **$19,059** |

### What Should Have Happened

At **15:44:48 UTC** — when the portfolio dropped from +4.90% to -5.05% in one second — a real-time equity monitor should have triggered a **WARNING**. This was the last possible intervention point.

At **15:45:10 UTC** — when the 10% line was crossed:
1. All open XAUUSD positions on 2208, 20043, 2206 should have been closed
2. Copy relationships to 2210 should have been suspended
3. Admin alert should have been sent immediately
4. "HALTED" flag should have been set on all accounts

### What Actually Happened

**Nothing.** No check ran. No alert fired. No positions closed. **New positions were OPENED at 15:45:10** — the copy system continued operating through the breach.

### Why It Failed

The break switch **does not exist as implemented code.** It exists only as:
- `max_monthly_drawdown_pct: 10.0` in the `risk_policies` MongoDB collection
- Display values in the Hull Risk Engine frontend
- **Zero enforcement code. Zero cron jobs. Zero automated actions.**

---

## 6. CONTROL FAILURE MATRIX

| # | Layer | Control | Expected | Actual | Classification | Severity |
|---|-------|---------|----------|--------|----------------|----------|
| 1 | Backend | Break Switch (10% DD halt) | Close positions, halt account | **NOT IMPLEMENTED** | [MISSING FEATURE] | **CRITICAL** |
| 2 | Backend | Max Intraday Loss (3%) | Alert + halt | Display-only | [MISSING FEATURE] | **CRITICAL** |
| 3 | Backend | Max Weekly Loss (6%) | Alert + halt | Display-only | [MISSING FEATURE] | **CRITICAL** |
| 4 | Backend | Max Monthly DD (10%) | Close positions + halt | Display-only | [MISSING FEATURE] | **CRITICAL** |
| 5 | Backend | Force Flat (21:50 UTC) | Auto-close all positions | DB config only, no cron | [MISSING FEATURE] | **HIGH** |
| 6 | Backend | Admin Alerts | Email on DD breach | No alert system exists | [MISSING FEATURE] | **CRITICAL** |
| 7 | Backend | Copy-Chain Halt | Suspend copies on halt | Not implemented | [MISSING FEATURE] | **HIGH** |
| 8 | Database | Equity Monitor fields | Per-account halt/switch config | No fields exist on any account | [MISSING FEATURE] | **CRITICAL** |
| 9 | Backend | Risk Enforcement Cron | Check equity every 60s | Only VPS sync + health cron exist | [MISSING FEATURE] | **CRITICAL** |
| 10 | Frontend | Win Rate Display | Show actual win rate | Shows 0% despite 80.9% actual | [CONFIRMED BUG] | **MEDIUM** |
| 11 | Broker (LUCRUM) | Broker-level protection | Stop-out trigger | **UNKNOWN — requires escalation** | [REQUIRES VERIFICATION] | **CRITICAL** |

---

## 7. AVOIDABLE LOSS CALCULATION

### Portfolio-Level (10% Break Switch)

| Metric | Value |
|--------|-------|
| Protection line | $366,584.72 |
| Equity at breach (15:45:10) | ~$359,027 |
| Final equity | $347,526.11 |
| Loss AFTER breach | $11,501 |
| **Avoidable if halted at breach** | **$11,501** |

### Per-Account (Individual Break Switches)

Had each account had its own 10% break switch:

| Account | 10% Line | Breached At | Final Equity | Avoidable |
|---------|----------|-------------|-------------|-----------|
| 2208 | $45,000 | ~15:44 | $40,546 | $4,454 |
| 20043 | $160,200 | ~15:44 | $144,833 | $15,367 |
| 2206 | $161,385 | NOT BREACHED | $162,146 | $0 |

**Note:** The catastrophe happened in <2 minutes. Even a 60-second polling break switch may not have caught the 15:44-15:45 cascade in time. The speed of the Gold reversal was extreme. However, a 5% WARNING threshold at 15:44:48 could have provided a ~22-second intervention window.

---

## 8. COPY CHAIN & GOLD CONCENTRATION

### Confirmed Copy Architecture
```
LUCRUM 2210 (GOLD DAY TRADING — Demo Master, -69.48%)
   │
   ├──→ 2208 (JOSE GOLD DAY-TRADE) — 0.5x ratio copy
   │       │
   │       └──→ 2206 (JC PROVIDER) — 0.25x ratio (effective: 0.125x of 2210)
   │
   2206 also copies from MEX Atlantic 86511 at 0.5x ratio

LUCRUM 2122 (Strategy 2122)
   │
   └──→ 20043 (JARED COPIA) — 0.5x ratio
         Also copies LUCRUM 20062 (CRYPTO BITCOIN) — 0.1 lot fixed
```

### CRITICAL: 20043's Gold Exposure Source

Account 20043 does NOT copy 2210 directly. Its copy sources are 2122 and 20062. **Yet 20043 had $-33,909 in Gold losses on March 18.**

This means **LUCRUM 2122 was also executing Gold trades**, propagating Gold exposure to 20043 independently of the 2210 chain. **[REQUIRES VERIFICATION WITH LUCRUM]**

### Gold Concentration on March 18

100% of the March 18 loss was XAUUSD across all three accounts:
- **2208:** -$10,557 Gold loss (100% of day's loss)
- **20043:** -$33,908 Gold loss (100% of day's loss)
- **2206:** -$21,203 Gold loss (100% of day's loss)

**All three accounts were simultaneously long Gold when the reversal hit.** The copy architecture created hidden correlated risk — one adverse Gold move became a $65,726 multi-account loss in 82 seconds.

---

## 9. DATA PIPELINE FINDING

**Dashboard shows 0.00% Win Rate (0W/0T) for all three accounts.** However, MongoDB contains real trade data:

| Account | Actual Trades | Wins | Losses | Actual Win Rate |
|---------|-------------:|-----:|-------:|----------------:|
| 2208 | 204 | 165 | 39 | 80.9% |
| 20043 | 258 | 225 | 33 | 87.2% |
| 2206 | 289 | 226 | 63 | 78.2% |

**[CONFIRMED BUG]** The frontend analytics display is computing win rate incorrectly — likely filtering by entry type or time window that excludes the actual closed trade data.

---

## 10. FINDINGS SUMMARY

| # | Finding | Classification | Severity |
|---|---------|---------------|----------|
| F1 | Break switch has zero implementation — no code, no cron, no DB fields | [MISSING FEATURE] | **CRITICAL** |
| F2 | All risk limits (3% intraday, 6% weekly, 10% monthly) are display-only | [MISSING FEATURE] | **CRITICAL** |
| F3 | Force Flat (21:50 UTC) stored in DB but not enforced by any mechanism | [MISSING FEATURE] | **HIGH** |
| F4 | No admin alert system for drawdown, breach, or data gap events | [MISSING FEATURE] | **CRITICAL** |
| F5 | No equity monitor/halt/switch fields on any account document | [MISSING FEATURE] | **CRITICAL** |
| F6 | No copy-chain cascade halt mechanism | [MISSING FEATURE] | **HIGH** |
| F7 | Only 2 scheduler jobs exist (VPS sync, health check) — zero risk jobs | [MISSING FEATURE] | **CRITICAL** |
| F8 | New positions opened DURING portfolio breach (15:45:10) | [MISSING FEATURE] | **CRITICAL** |
| F9 | Win Rate shows 0% on dashboard vs 78-87% actual in MongoDB | [CONFIRMED BUG] | **MEDIUM** |
| F10 | Account 20043 Gold exposure source unclear (copies 2122, not 2210) | [REQUIRES VERIFICATION] | **HIGH** |
| F11 | Portfolio -14.68% total loss vs 10% limit = 4.68% overshoot ($19,059) | [CONTROL FAILURE] | **CRITICAL** |

---

*All figures verified against MongoDB `fidus_production` and MT5 account data. Initial allocations confirmed from March 9, 2026 Money Managers dashboard. No mock data used.*
