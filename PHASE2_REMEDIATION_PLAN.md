# FIDUS — PHASE 2: RISK CONTROLS REMEDIATION PLAN
**Date:** March 18, 2026
**Status:** AWAITING APPROVAL
**Priority:** ALL ITEMS CRITICAL OR HIGH — No feature work until resolved

---

## REMEDIATION OVERVIEW

11 findings from the forensic report. 0 enforcement mechanisms exist today.
This plan builds the ENTIRE risk enforcement layer from scratch.

---

## A. BREAK SWITCH — End-to-End Implementation
**Finding:** F1 — Break switch does not exist
**Classification:** [MISSING FEATURE] | **CRITICAL**

### What Is Broken
No mechanism exists to halt trading when an account or the portfolio exceeds its drawdown limit. When 2208 hit -18.91%, nothing happened. When the portfolio hit -14.68%, nothing happened. New trades continued opening during the breach.

### Exact Fix

**Backend (Python/FastAPI):**
- New service: `/app/backend/services/risk_enforcement_service.py`
- APScheduler cron job running **every 60 seconds**
- For each active MAM/copy account:
  1. Read current equity from `mt5_accounts` collection (synced by VPS bridge every 2 min)
  2. Compare against `initial_allocation` from same collection
  3. Calculate drawdown %: `(equity - initial_allocation) / initial_allocation * 100`
  4. If drawdown exceeds configured threshold (default 10%):
     - Set `halt_status: "halted"` on the account in MongoDB
     - Set `halted_at: datetime`, `halt_reason: "drawdown_breach_X%"`
     - Attempt to close all open positions via MT5 bridge API (`POST /api/mt5/close-all/{account}`)
     - Send admin email alert via SMTP (already configured in .env)
     - Log to new `risk_events` collection
  5. If drawdown exceeds WARNING threshold (default 5%):
     - Send warning email
     - Log warning event
     - Set `risk_warning: true` on account

**Database (MongoDB):**
- New fields on `mt5_accounts`: `halt_status` ('active'|'halted'|'disabled'), `halted_at`, `halt_reason`, `risk_warning`, `break_switch_pct` (configurable per account, default 10)
- New collection: `risk_events` { account, event_type, triggered_at, equity, threshold, initial_allocation, drawdown_pct, action_taken, resolved }

**Frontend (React):**
- Halted account shows **full-width red banner** on Money Managers card: "TRADING HALTED — Drawdown limit reached at X%"
- Break switch status badge on each manager card: `[ACTIVE]` green / `[HALTED]` red / `[DISABLED]` grey
- Admin can "Resume" a halted account (with confirmation modal)

**Effort:** 8-10 hours
**Broker API Required:** YES — needs MT5 bridge `close-all` endpoint (already exists at VPS)
**Internal components:** Scheduler job, MongoDB schema, email alerts, frontend badges

---

## B. RISK LIMITS ENFORCEMENT ENGINE
**Finding:** F2 — Intraday/weekly/monthly limits are display-only
**Classification:** [MISSING FEATURE] | **CRITICAL**

### What Is Broken
`risk_policies` collection stores: max_intraday_loss_pct: 3%, max_weekly_loss_pct: 6%, max_monthly_drawdown_pct: 10%. These values are read by the frontend for display ONLY. No backend code checks them. No action is ever taken.

### Exact Fix

**Integrated into the same 60-second enforcement cron from Item A.**

For each active account, each cycle:
1. **Intraday loss check:** Compare current equity to equity at 00:00 UTC today (stored in new `daily_equity_snapshots` collection, populated by a midnight cron)
2. **Weekly loss check:** Compare current equity to Monday 00:00 UTC snapshot
3. **Monthly drawdown check:** Compare current equity to `initial_allocation` (this IS the break switch — same logic)

Each breach level triggers:
- **Intraday 3%:** WARNING alert + log event + set `risk_warning: true`
- **Weekly 6%:** CRITICAL alert + attempt position close + halt account
- **Monthly 10%:** CRITICAL alert + close all positions + halt + cascade halt (Item C)

**Database:**
- New collection: `daily_equity_snapshots` { account, date, equity_open, equity_close, populated_at }
- Midnight cron job stores equity snapshot for each account

**Effort:** 4-6 hours (integrated with Item A scheduler)
**Broker API Required:** YES (same close-all endpoint)

---

## C. COPY CHAIN CASCADE HALT
**Finding:** F6 — No cascade halt when downstream account halted
**Classification:** [MISSING FEATURE] | **HIGH**

### What Is Broken
When Account 2208 was in drawdown, its copy relationship to upstream 2206 continued. When 2208 breached, 2206 kept copying from it. No mechanism suspends the copy chain.

### Exact Fix

When any account is halted (Item A/B):
1. Query `mt5_accounts` for all accounts where `copy_sources` contains the halted account
2. For each upstream account: set `copy_halted_sources: [halted_account_id]` 
3. Frontend shows which copy sources are halted with orange warning on the copy config display
4. Admin can manually resume individual copy sources

**Note:** FIDUS cannot programmatically disable the actual LUCRUM MAM copy — that requires broker action. This halt flag is an INTERNAL marker that triggers:
- Admin notification
- Dashboard warning
- Documented recommendation to contact LUCRUM to suspend copy

**Effort:** 2-3 hours
**Broker API Required:** NO (internal tracking only — broker action is manual)

---

## D. FORCE FLAT ENFORCEMENT (21:50 UTC)
**Finding:** F3 — Force flat configured but never enforced
**Classification:** [MISSING FEATURE] | **HIGH**

### What Is Broken
`risk_policy` collection stores `force_flat_time_utc: "21:50"`. No cron job fires at 21:50. No positions are closed. The Hull Risk Engine scores overnight violations after the fact, but takes no preventive action.

### Exact Fix

- New scheduler job: fires at **21:45 UTC** (5 min warning) and **21:50 UTC** (execute)
- At 21:45: Check all accounts for open positions. If any exist, send WARNING email to admin.
- At 21:50: For each account with open positions:
  1. Call MT5 bridge API to close all positions
  2. Log force flat event to `risk_events` collection
  3. If close fails (bridge offline): send CRITICAL alert, log failure
- Skip accounts with `skip_force_flat_penalty: true` (e.g., crypto strategies)

**Effort:** 3-4 hours
**Broker API Required:** YES — MT5 bridge close endpoint

---

## E. RISK SCORE — MAKE IT ACTIONABLE
**Finding:** F8 — Risk Score computed on-demand for display only
**Classification:** [MISSING FEATURE] | **MEDIUM → HIGH**

### What Is Broken
Hull Risk Engine computes Risk Control Score (0-100) when the frontend requests it. The score is never stored, never tracked over time, and never triggers any action.

### Exact Fix

- Daily cron job (02:00 UTC): compute Risk Control Score for each active money manager account
- Store in `risk_score_history` collection: { account, score, date, penalties_applied, label }
- If score < 60 (Weak): auto-flag manager → set `risk_flag: "weak"` on account + send admin email
- If score < 40 (Critical): auto-suspend → set `risk_flag: "critical"` + halt account (same as Item A halt)
- Frontend: Risk Score badge on Money Manager cards, color-coded (green/yellow/orange/red)

**Effort:** 3-4 hours
**Broker API Required:** NO

---

## F. TRADE DATA PIPELINE FIX (Win Rate 0%)
**Finding:** F9 — Win Rate shows 0% despite 80%+ actual in MongoDB
**Classification:** [CONFIRMED BUG] | **MEDIUM**

### What Is Broken
The Money Managers dashboard and Trading Analytics show Win Rate: 0.00% (0W/0T) for all three accounts (2206, 20043, 2208) despite MongoDB `mt5_deals_history` containing hundreds of trades with real P&L data.

### Exact Fix

Debug the frontend trading analytics computation:
- Check if it's filtering by `entry` type incorrectly (only counting `entry: 0` as trades)
- Check if it's filtering by date range that excludes data
- Check if the API endpoint is returning deal counts or just balance operations
- Add data health endpoint: `GET /api/accounts/{id}/data-health` → returns `{ lastTradeSync, tradeCount, winRate, lastEquitySync, dataGapHours }`

**Effort:** 2-3 hours
**Broker API Required:** NO

---

## G. ADMIN ALERTS SYSTEM
**Finding:** F4 — No alert system exists
**Classification:** [MISSING FEATURE] | **CRITICAL**

### What Is Broken
No email or notification is sent to admin for ANY event — drawdown breach, break switch activation, force flat execution, data sync gap, risk score drop.

### Exact Fix

- Alert service: `/app/backend/services/alert_service_v2.py`
- Uses existing SMTP config from `.env` (`SMTP_USERNAME`, `SMTP_APP_PASSWORD`, `ALERT_RECIPIENT_EMAIL`)
- Alert types: `drawdown_warning`, `drawdown_breach`, `halt_activated`, `force_flat_executed`, `force_flat_failed`, `risk_score_critical`, `data_sync_gap`
- All alerts logged to new `admin_alerts` collection: { alert_type, account, timestamp, value, threshold, message, email_sent, resolved }
- Deduplication: don't re-send same alert within 1 hour

**Effort:** 3-4 hours (integrated with Items A, B, D, E)
**Broker API Required:** NO

---

## H. DASHBOARD RISK INDICATORS
**Finding:** Multiple — no risk status visible on Money Manager cards
**Classification:** [MISSING FEATURE] | **MEDIUM**

### What Is Broken
Money Manager cards show no risk status, no halt status, no drawdown warning, no data sync info.

### Exact Fix

Each Money Manager card gets:
- **RISK STATUS banner:** Current drawdown % vs limit, color-coded (green <5%, yellow 5-8%, orange 8-10%, red >10%)
- **Break switch badge:** `[ACTIVE]` / `[HALTED]` / `[DISABLED]`
- **Last data sync timestamp** with freshness indicator
- **Active violations count** (overnight, intraday breach, etc.)
- Risk Score badge (0-100) with color

**Effort:** 3-4 hours
**Broker API Required:** NO

---

## IMPLEMENTATION PRIORITY & SEQUENCE

| Priority | Item | Description | Effort | Dependencies |
|----------|------|-------------|--------|--------------|
| **1** | **A** | Break Switch (end-to-end) | 8-10h | None — build first |
| **2** | **G** | Admin Alerts System | 3-4h | Build with A |
| **3** | **B** | Risk Limits Enforcement | 4-6h | Requires A scheduler |
| **4** | **C** | Copy Chain Cascade Halt | 2-3h | Requires A halt logic |
| **5** | **D** | Force Flat Enforcement | 3-4h | Requires A scheduler + G alerts |
| **6** | **H** | Dashboard Risk Indicators | 3-4h | Requires A/B fields in DB |
| **7** | **E** | Risk Score Actionable | 3-4h | Requires A halt + G alerts |
| **8** | **F** | Win Rate Display Fix | 2-3h | Independent |

**Total estimated effort: 28-38 hours**
**Items 1-4 are CRITICAL and should be deployed together as Risk Enforcement v1.**

---

## WHAT REQUIRES BROKER (LUCRUM) ACCESS

| Item | Broker Action Needed |
|------|---------------------|
| A (Break Switch) | MT5 bridge API `close-all` endpoint — already exists on VPS |
| B (Risk Limits) | Same close-all endpoint |
| D (Force Flat) | Same close-all endpoint |
| C (Copy Chain) | Manual — FIDUS flags internally, admin contacts LUCRUM to suspend copy |
| F10 finding | Verify: does master 2122 also trade XAUUSD? How did 20043 get Gold exposure? |

---

## DO NOT DEPLOY WITHOUT APPROVAL

Each item requires Chava's explicit approval before implementation begins.
No item should be marked complete without:
1. MongoDB record proof (risk_event document)
2. API response proof (endpoint returning halt status)
3. Email proof (alert received)
4. Frontend screenshot (halt banner, risk badges)

---

*Awaiting approval to proceed with implementation, starting with Items A + G (Break Switch + Alerts).*
