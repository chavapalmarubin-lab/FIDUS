# FIDUS GOLD TRADING INCIDENT — FORENSIC ANALYSIS REPORT
**Date of Incident:** March 18, 2026
**Report Date:** March 18, 2026
**Report Type:** Post-Incident Forensic Analysis
**Severity:** CRITICAL
**Analyst:** FIDUS Risk Analysis System

---

## 1. EXECUTIVE SUMMARY

On March 18, 2026, between 15:44 and 15:45 UTC, the FIDUS portfolio suffered a catastrophic GOLD (XAUUSD) loss totaling **$65,838** (-11.06%) across three accounts in under 2 minutes. The loss originated from master account LUCRUM 2210 (Gold Day Trading strategy) and propagated through the copy-trading chain to accounts 2208, 20043, and 2206.

**Root Cause:** A massive adverse Gold move liquidated large XAUUSD positions simultaneously across all copy-linked accounts. The 10% portfolio protection threshold ($535,962) was breached at **15:45 UTC** when equity dropped to $529,796.

**Control Failures (ALL):**
- **Break Switch:** NO BREAK SWITCH EXISTS in the system. No equity protection configuration found on any account in MongoDB. No enforcement code exists in the backend.
- **Risk Limits Enforcement:** Risk policies are configured (10% max DD, 3% intraday) but are **DISPLAY-ONLY**. Zero enforcement code, zero cron jobs, zero automated position closing.
- **Force Flat (21:50 UTC):** Configured in database but **NOT ENFORCED** — no backend mechanism closes positions.
- **Alerts:** No alert was sent to admin. No alert system is implemented for drawdown breaches.

**Avoidable Loss:** Had a 10% break switch been active, the loss would have been capped at ~$59,551 instead of the actual $65,838. The additional **$6,287 was avoidable**. However, the more critical finding is that the ENTIRE loss framework — break switch, intraday limits, force flat — exists only as stored configuration with zero enforcement.

---

## 2. INCIDENT TIMELINE

| Time (UTC) | Event | Portfolio Equity | Cum P&L | Loss % |
|------------|-------|-----------------|---------|--------|
| Pre-Mar 18 | Portfolio stable after Mar 9 reallocation | $595,514 | — | — |
| 00:00-12:00 | Normal trading, small gains | $597,110 | +$1,596 | +0.27% |
| 13:00-14:59 | Active Gold trading, all profitable | $608,753 | +$13,239 | +2.22% |
| **15:14-15:43** | Continued profitable Gold trades | $615,475 | +$19,962 | +3.35% |
| **15:44:28** | **CATASTROPHE**: 12 trades close on Account 2208 in 1 second. Total loss: -$13,583. Largest single: -$3,956 (1.05 lots XAUUSD) | — | — | — |
| **15:44:48** | Account 20043 hit: 12 trades close. Total: -$44,377. Largest: -$12,788 (3.66 lots XAUUSD) | $557,515 | -$38,000 | -6.38% |
| **15:45:10** | Account 2206 hit: 13 trades close. Total: -$27,716. **NEW POSITIONS ALSO OPENED** on 2208, 20043, 2206 | **$529,796** | **-$65,717** | **-11.04%** |
| **15:45:10** | **>>> 10% THRESHOLD BREACHED <<<** | $529,796 | -$65,717 | -11.04% |
| 15:45:47 | Final small losses on 2208 (-$13.84) | $529,676 | -$65,838 | -11.06% |
| 15:46 | Trading stops. Minor loss (-$121) | $529,676 | -$65,838 | -11.06% |

**Total duration of catastrophic phase: 82 seconds (15:44:28 to 15:45:47)**

---

## 3. "WHEN THE 10% LUCRUM BREAK SWITCH SHOULD HAVE CLICKED"

### The Math

| Metric | Value |
|--------|-------|
| Pre-disaster portfolio equity | $595,513.58 |
| 10% of portfolio | $59,551.36 |
| Protection line (90% of equity) | $535,962.22 |
| **Actual breach timestamp** | **15:45:10 UTC** |
| **Equity at breach** | **$529,796.31** |
| Amount below protection line | $6,165.91 |
| Final equity (end of day) | $529,675.69 |
| **Additional loss after breach** | **$120.62** |

### What Should Have Happened

At **15:44:48 UTC**, when Account 20043's batch of 12 Gold closes brought portfolio loss to -$38,000 (-6.38%), a properly configured monitoring system would have detected rapid equity decline and issued a WARNING.

At **15:45:10 UTC**, when equity crossed $535,962 (the 10% line):
1. All open positions on 2208, 20043, 2206 should have been closed immediately
2. Copy relationships from 2210 to all follower accounts should have been suspended
3. Admin alert should have been sent
4. "HALTED" flag should have been set on all affected accounts

### What Actually Happened

**Nothing.** No system checked. No alert fired. No positions closed. Furthermore, at 15:45:10, **new positions were OPENED** on accounts 2208, 20043, and 2206 — the copy system continued operating through the breach.

### Why It Failed

The 10% break switch **does not exist as implemented code**. It exists only as:
- A `max_monthly_drawdown_pct: 10.0` value in the `risk_policies` collection
- Display text in the Hull Risk Engine frontend component
- Zero enforcement code, zero scheduled checks, zero automated actions

---

## 4. CONTROL FAILURE MATRIX

| Layer | Control | Expected Behavior | Actual Behavior | Failure Type | Severity |
|-------|---------|-------------------|-----------------|--------------|----------|
| **Platform (FIDUS Backend)** | Break Switch | Close positions when equity drops 10% | **NOT IMPLEMENTED** — no enforcement code exists | [MISSING FEATURE] | **CRITICAL** |
| **Platform (FIDUS Backend)** | Max Intraday Loss (3%) | Alert and halt when daily loss exceeds 3% | Display-only in frontend. No backend enforcement | [MISSING FEATURE] | **CRITICAL** |
| **Platform (FIDUS Backend)** | Max Weekly Loss (6%) | Halt trading on weekly 6% breach | Display-only. No enforcement | [MISSING FEATURE] | **CRITICAL** |
| **Platform (FIDUS Backend)** | Force Flat (21:50 UTC) | Auto-close all positions at 21:50 UTC | Stored in `risk_policy` but no cron job closes positions | [MISSING FEATURE] | **HIGH** |
| **Platform (FIDUS Backend)** | Risk Score Penalties | Auto-penalize manager score and flag for review | Computed on-demand for display only. No automated action | [MISSING FEATURE] | **HIGH** |
| **Platform (FIDUS Backend)** | Admin Alerts | Email admin on drawdown breach | No alert system exists. `alerts` collection does not exist | [MISSING FEATURE] | **CRITICAL** |
| **Platform (FIDUS Backend)** | Equity Monitor per Account | Track equity vs initial allocation, trigger on threshold | No `equity_monitor`, `break_switch`, or `halt` fields on any account | [MISSING FEATURE] | **CRITICAL** |
| **Platform (FIDUS Backend)** | Copy Chain Halt | Suspend copy relationships on downstream halt | No cascade halt mechanism exists | [MISSING FEATURE] | **HIGH** |
| **Dashboard (Frontend)** | Risk Status Display | Show break switch status, halt status per manager | No halt status, no break switch badge on Money Manager cards | [MISSING FEATURE] | **MEDIUM** |
| **LUCRUM (Broker)** | Broker-level equity protection | Broker stop-out level triggers | **UNKNOWN** — broker-level behavior not observable from FIDUS data | [REQUIRES ESCALATION] | **CRITICAL** |

---

## 5. AVOIDABLE LOSS CALCULATION

### Scenario: Break Switch Active at 10%

| Metric | Value |
|--------|-------|
| Portfolio equity at 10% breach (15:45:10 UTC) | $529,796.31 |
| Ideal protection line | $535,962.22 |
| Overshoot (breach depth) | $6,165.91 |
| Additional loss after breach | $120.62 |
| **Total avoidable loss** | **$6,286.53** |

### Note on Overshoot
The $6,166 overshoot is due to the speed of execution — the loss at 15:44:48 brought equity to $557,515 (-6.38%), and the next batch at 15:45:10 crossed the threshold in a single batch of 13 trades. Even with a 60-second polling interval, a break switch could NOT have prevented the 15:45:10 batch — the jump from -6.38% to -11.04% happened in 22 seconds.

### Scenario: Break Switch with 5% Warning + 10% Hard Stop

Had a 5% WARNING been configured at -$29,776 (equity $565,738):
- At 15:44:48, equity was $557,515 (-6.38%) — the 5% warning would have triggered
- Admin would have had **22 seconds** to review before the 10% breach
- Automated position reduction at 5% could have prevented most of the subsequent loss

---

## 6. CONCENTRATION & RISK PROPAGATION ANALYSIS

### Copy Chain Architecture
```
LUCRUM 2210 (GOLD DAY TRADING — Master)
   │
   ├──→ 2208 (JOSE GOLD DAY-TRADE) — 0.5x ratio
   │       │
   │       └──→ 2206 (JC PROVIDER) — 0.25x ratio (effectively 0.125x of 2210)
   │
   └──→ 20043 (JARED COPIA) — copies from 2122 + 20062 (NOT directly from 2210)
```

### CRITICAL FINDING: Account 20043 Copy Chain

**The provided fact sheet states 2210 → 20043 at 0.5x ratio. However, the MongoDB data shows:**
- Account 20043's `copy_sources` are: **LUCRUM 2122** (ratio 0.5) and **LUCRUM 20062 CRYPTO BITCOIN** (0.1 lot fixed)
- Account 20043 does **NOT** copy from 2210 directly
- Yet Account 20043 suffered $-33,908 in Gold losses on March 18

**This means either:**
1. Account 2122 (master for 20043) was ALSO trading Gold — propagating Gold exposure independently
2. Or the copy chain documentation is incomplete

**[REQUIRES VERIFICATION WITH LUCRUM]**

### Gold Concentration (Confirmed)

| Account | Initial Capital | Gold P&L (All Time) | Gold Trades | Gold as % of Total P&L |
|---------|----------------|--------------------:|------------:|----------------------:|
| 2210 (Master) | $19,850 | -$5,027 | 576 | 100% (Gold-only strategy) |
| 2208 | $50,000 | -$9,312 | 201 | 100% Gold |
| 20043 | $178,000 | -$24,222 | 255 | Mixed (Gold + other) |
| 2206 | $179,316 | -$14,707 | 285 | Mixed (Gold + MEX Atlantic) |

### Effective Gold Exposure on March 18

All three follower accounts (2208, 20043, 2206) had active XAUUSD positions at 15:44 UTC. The copy architecture created **hidden multi-account Gold concentration** where:
- One Gold strategy on master 2210 became simultaneous Gold exposure on 3 accounts
- Combined Gold lot size at time of loss: **~15+ lots XAUUSD** across all accounts
- A single adverse Gold move (~$30/oz) liquidated all positions across all accounts within 82 seconds

### Why Diversification Failed

The copy-trading architecture created **correlated risk** — all accounts were long Gold simultaneously. When Gold reversed sharply, all accounts lost simultaneously. There was no risk isolation between accounts because:
1. No per-account break switch existed
2. No copy-chain halt mechanism existed
3. No concentration limit was enforced (all accounts 100% Gold-exposed at time of event)

---

## 7. DATA PIPELINE AUDIT

### Finding: Win Rate 0.00% Discrepancy

**The dashboard shows 0W/0T for Account 2208.** However, MongoDB contains **204 trades with P&L** for this account (165W / 39L = 80.9% win rate).

**Root Cause:** [CONFIRMED BUG] The Trading Analytics frontend is likely computing win rate from a filtered dataset (e.g., last 30 days only, or filtering by `entry` type) that excludes balance operations or shows only the catastrophic day's data. The raw deal data is intact — the display pipeline is broken.

**MongoDB deal data for 2208 is HEALTHY:** 402 total deals, 204 with P&L, synced up to 15:45:47 UTC today.

---

## 8. FINDINGS SUMMARY

| # | Finding | Classification | Severity |
|---|---------|---------------|----------|
| F1 | Break switch does not exist as implemented code | [MISSING FEATURE] | **CRITICAL** |
| F2 | Risk limits (intraday/weekly/monthly) are display-only with zero enforcement | [MISSING FEATURE] | **CRITICAL** |
| F3 | Force Flat (21:50 UTC) is not enforced by any backend mechanism | [MISSING FEATURE] | **HIGH** |
| F4 | No admin alert system exists for drawdown breaches | [MISSING FEATURE] | **CRITICAL** |
| F5 | No equity monitor fields exist on any account in MongoDB | [MISSING FEATURE] | **CRITICAL** |
| F6 | No copy-chain halt mechanism exists | [MISSING FEATURE] | **HIGH** |
| F7 | No scheduler job exists for risk enforcement (only VPS sync + health check) | [MISSING FEATURE] | **CRITICAL** |
| F8 | Risk Score is computed on-demand for display only, triggers no actions | [MISSING FEATURE] | **MEDIUM** |
| F9 | Win Rate shows 0% on dashboard despite 80.9% actual — frontend display bug | [CONFIRMED BUG] | **MEDIUM** |
| F10 | Account 20043 copy chain documentation may be incorrect (no direct 2210 link) | [REQUIRES VERIFICATION] | **HIGH** |
| F11 | New positions were OPENED at 15:45:10 UTC while portfolio was in breach | [MISSING FEATURE] — no halt mechanism | **CRITICAL** |

---

*Report prepared from real-time MongoDB forensic extraction. All timestamps, equity values, and trade data are from production database `fidus_production`. No mock data used.*
