# FIDUS Investment Platform - Product Requirements Document

## Original Problem Statement
Build a standalone "VIKING" trading analytics dashboard alongside a comprehensive FIDUS investment platform with:
- Public, no-login VIKING dashboard and private admin dashboard
- Correct calculation and display of total portfolio values, P&L, and cash flow projections
- Creation of referral links for new FIDUS agents
- Reliable mechanism to sync live data from MT5 accounts into MongoDB database

## Core Architecture
- **Frontend:** React with Tailwind CSS
- **Backend:** FastAPI with Python
- **Database:** MongoDB Atlas
- **Deployment:** Render (production), Emergent (preview)

## What's Been Implemented

### Completed Features (Dec 2025 - Mar 2026)

#### Final March 2026 Capital Allocation (Mar 9, 2026) ✅
- **Task:** Complete reallocation of all capital to trading accounts
- **Total Capital:** $407,316.36
- **Final Allocations:**
  1. **Account 2206 (JC PROVIDER):** $179,316.36 - Copies MEX Atlantic 86511 at 0.5 ratio
  2. **Account 20043 (JARED COPIA):** $178,000.00 - Copies LUCRUM 2122 at 0.3 ratio
  3. **Account 2208:** $50,000.00 - Copies LUCRUM 2210 at 0.5 ratio
- **Lucrum Wallet:** $0.00 (all capital now deployed)
- **Previous allocations zeroed:** Account 2209 (JARED) reset to $0
- **Status:** COMPLETE - All capital allocated to trading accounts

#### Drawdown as Paramount Risk Metric (Mar 6, 2026) ✅
- **Feature:** Complete overhaul of risk scoring to make drawdown the PRIMARY risk metric for day trading with leverage
- **Thresholds Implemented:**
  - **5% Drawdown = WARNING** (-30 points, reduce risk)
  - **10% Drawdown = CRITICAL/STOP** (-60 points, review strategy immediately)
- **CRITICAL FIX - Proper Drawdown Calculation:**
  - **Problem:** Previous implementation showed 0% drawdown for all strategies (incorrect)
  - **Root Cause:** Was comparing `current equity` to `max(initial, current)` which always = 0 when profitable
  - **Solution:** Now builds EQUITY CURVE from deal history and calculates:
    - **Maximum Historical Drawdown:** Largest peak-to-trough decline ever recorded
    - **Current Drawdown:** Current equity vs the highest equity ever reached
    - Uses the WORSE of the two for risk scoring
- **Backend Changes:**
  1. Updated `DEFAULT_RISK_POLICY` to include `drawdown_warning_pct` (5%) and `drawdown_critical_pct` (10%)
  2. Redesigned `RISK_SCORE_PENALTIES` to heavily weight drawdown breaches
  3. Refactored `calculate_risk_control_score()` to build equity curve and calculate true max drawdown
  4. Updated `_calculate_drawdown_compliance()` with new status levels: healthy/caution/warning/critical
  5. Added `max_pct`, `current_pct`, and `effective_pct` to drawdown API response
  6. Fixed `live_demo_analytics_service.py` to calculate max drawdown from equity curve
- **Frontend Changes:**
  1. Added prominent **Drawdown Alert Banner** showing MAX drawdown prominently
  2. Shows "(Current: X%)" below the max drawdown value
  3. Updated **Risk Policy card** to show DD Warning (5%) and DD Critical (10%) first
  4. Added **DRAWDOWN (Primary Risk Metric)** as first card in Compliance Summary
  5. Shows both Current and Max drawdown values with appropriate coloring
  6. Status correctly shows CRITICAL when max drawdown exceeds threshold
- **Files Modified:**
  - `/app/backend/services/hull_risk_engine.py` - Equity curve drawdown calculation
  - `/app/backend/services/live_demo_analytics_service.py` - Equity curve drawdown calculation
  - `/app/frontend/src/components/LiveDemoAnalytics.js` - UI components
- **Verified Results:**
  - GOLD DAY TRADING: Max 11.65% (CRITICAL), Current 2.15%
  - CRYPTO BITCOIN: Max 0.05% (HEALTHY)
  - JOEL ALVES NASDAQ: Max 2.03% (HEALTHY)
  - JOEL ALVES GOLD: Max 10.42% (CRITICAL), Current 6.6%
  - UNO14: Max 2.26% (HEALTHY), Current 4.88%
- **Status:** COMPLETE - Verified via API and screenshots

#### Quantitative Drawdown Trigger Analysis (Mar 6, 2026) ✅
- **Feature:** Algorithm-driven analysis identifying exactly which trades triggered drawdowns, enabling bot optimization
- **Purpose:** Allow money managers to reprogram bots based on data-driven insights
- **Backend Implementation:**
  1. New function `analyze_drawdown_triggers()` in hull_risk_engine.py
  2. Builds equity curve from deal history to identify drawdown events
  3. Pattern analysis: worst symbols, worst trading hours, position sizing, direction bias, losing streaks
  4. Generates actionable bot recommendations with specific parameter suggestions
  5. New API endpoint: `/api/admin/risk-engine/drawdown-analysis/{account}`
- **Analysis Components:**
  - **Drawdown Events:** Identifies when DD crossed warning/critical thresholds
  - **Triggering Trades:** Lists exact trades that caused each drawdown (ticket, symbol, time, P&L)
  - **Worst Symbols:** Ranks symbols by total losses (e.g., XAUUSD: 102 trades, $13,998 loss)
  - **Dangerous Hours:** Identifies worst trading hours in UTC (e.g., 20:00 UTC: $3,105 loss)
  - **Position Size Analysis:** Compares DD trade sizes to average sizes
  - **Direction Bias:** BUY vs SELL loss analysis
  - **Streak Analysis:** Consecutive loss detection
- **Bot Recommendations Generated:**
  - CRITICAL: `auto_close_dd_threshold: 5.0`
  - HIGH: `max_position_xauusd: reduce by 50%`
  - HIGH: `blocked_hours: [20, 14, 18]`
  - HIGH: `max_consecutive_losses_before_pause: 3`
  - MEDIUM: `sell_size_multiplier: 0.5`
- **Frontend Display:**
  - Summary stats (Critical/Warning events, trades analyzed)
  - Bot optimization recommendations with parameter suggestions
  - Pattern analysis grids (worst symbols, dangerous hours)
  - Drawdown events timeline with triggering trade details
- **Files Modified:**
  - `/app/backend/services/hull_risk_engine.py` - Analysis functions
  - `/app/backend/server.py` - New API endpoint
  - `/app/frontend/src/components/LiveDemoAnalytics.js` - UI components
- **Status:** COMPLETE - Fully functional quantitative analysis for bot optimization

#### Money Manager Allocation Start Date Feature (Mar 6, 2026) ✅
- **Feature:** Track allocation start dates for money managers to evaluate PnL from time of funding
- **Components Built:**
  1. **Backend API:**
     - Updated `/api/v2/derived/money-managers` to include `allocation_start_date` field
     - New endpoint: `POST /api/v2/accounts/allocation-date` - Update single account's date
     - New endpoint: `POST /api/v2/managers/allocation-date` - Update all accounts for a manager
  2. **Frontend Display:**
     - Added "Allocation Date" field on Money Manager cards with calendar icon
     - Added "Alloc Date" column in Manager Comparison Table
     - Added edit functionality in manager details modal with date picker
- **Files Modified:**
  - `/app/backend/routes/single_source_api.py` - API endpoints and aggregation pipeline
  - `/app/frontend/src/components/MoneyManagersDashboard.js` - UI components
- **Status:** COMPLETE - UI displays correctly, edit functionality working

#### Trading Statistics Fix - Demo Analytics (Mar 6, 2026) ✅
- **Bug:** "Trading Statistics" section in Deep Dive tab was showing all zeros
- **Root Cause:** `live_demo_analytics_service.py` only checked `mt5_deals` collection, but demo accounts may have deals in `mt5_deals_history`
- **Fix:** Updated service to check both collections and filter out non-trading operations
- **Files Modified:**
  - `/app/backend/services/live_demo_analytics_service.py` - Added fallback to mt5_deals_history
- **Status:** COMPLETE - Trading statistics now showing correct data (500 total trades, 174 wins, etc.)

#### Trading Hours Compliance - Day Trading Rules (Mar 4, 2026) ✅
- **Feature:** Strict day-trading-only compliance enforcement with full penalty integration
- **FIDUS Rule:** NO overnight positions allowed - all trades must be closed by force_flat_time
- **Bug Fixes Applied:**
  1. Fixed FIFO matching - deals now sorted by time for accurate entry/exit pairing
  2. Fixed risk policy merge - defaults now properly applied when DB values missing
  3. Fixed overnight detection in `_count_overnight_breaches` - now uses FIFO matching
  4. Fixed date filtering - fallback to historical data when no recent trades
- **Components Built:**
  1. **Overnight Breach Detection:**
     - Detects positions held past midnight (different calendar days)
     - Uses FIFO matching by symbol when position_id not available
     - Penalty: -15 points per breach (cap -45)
     - Logged in compliance_details.trading_hours.overnight_violations
     - **Now properly included in Risk Control Score**
  2. **Late Trade Detection:**
     - Detects trades closed after 21:50 UTC (force_flat_time)
     - Shows in Active Risk Alerts as WARNING severity
     - Listed in compliance_details.trading_hours.late_trade_violations
  3. **Trade Duration Analysis:**
     - Average, longest, shortest trade durations
     - Day trades percentage (trades < 16 hours)
     - Top 5 longest trades table
  4. **Trading Session Analysis:**
     - Entry/Exit hour distribution (UTC)
     - Peak trading hours identification
     - Trades after force flat count
  5. **UI Display (Risk Limits Tab):**
     - Day Trading row in Detailed Compliance Breakdown table
     - Shows 21:50 UTC (16:50 NY) force flat time
     - Breaches count and COMPLIANT/NON-COMPLIANT status
     - Overnight Violations table (if any)
- **Verified Results:**
  - Account 2210: 332 trades, 213 overnight, Score 0 (Critical), -45 penalty
  - Account 2217: 693 trades, 0 overnight, Score 100 (Strong), COMPLIANT
  - Account 886557: 79 trades, 18 overnight, Score 55 (Weak), -45 penalty
- **API Response Structure:**
  - `compliance_details.trading_hours.overnight_positions_found`
  - `compliance_details.trading_hours.late_trades_found`
  - `compliance_details.trading_hours.force_flat_time`
  - `compliance_details.trading_hours.status` (COMPLIANT/NON-COMPLIANT)
  - `compliance_details.trading_hours.penalty_applied`
  - `risk_control_score.breach_summary` now includes "Overnight breaches: X (-Y)"
- **Test Coverage:**
  - `/app/backend/tests/test_trading_hours_compliance.py` - 11 tests (all passing)
- **Files Modified:**
  - `/app/backend/services/hull_risk_engine.py` - get_deals_for_account, get_risk_policy, _count_overnight_breaches, FIFO matching
- **Status:** COMPLETE - 100% test pass rate, both Trading Analytics and Demo Analytics verified

#### Lucrum Wallet & Capital Allocation Management (Mar 3, 2026) ✅
- **Feature:** Track unallocated capital during high volatility periods
- **Use Case:** When market volatility is high, money can be moved from trading accounts to the Lucrum wallet for safety
- **Components Built:**
  1. **Lucrum Wallet Section (Cash Flow Tab):**
     - Displays current wallet balance ($407,316.36 as of Mar 2, 2026)
     - Shows total allocated to managers ($0 after reset)
     - Shows total capital (wallet + allocated)
     - Notes field for context (e.g., "High volatility - all funds moved to wallet")
     - Last updated timestamp
  2. **Update Wallet Modal:**
     - Input field for balance
     - Notes field for context
     - Save/Cancel buttons
  3. **Reset All Allocations Button:**
     - One-click reset of all money manager allocations to $0
     - Confirmation dialog
     - Logs previous allocations for audit
  4. **Anti-Duplication Validation:**
     - Rule: If wallet balance ≈ total allocated, show warning (money may be double-counted)
     - $100 tolerance threshold
- **API Endpoints:**
  - GET `/api/admin/lucrum-wallet` - Get wallet balance and validation status
  - PUT `/api/admin/lucrum-wallet` - Update wallet balance with notes
  - POST `/api/admin/reset-allocations` - Reset all manager allocations to $0
  - POST `/api/admin/set-allocation/{account_id}` - Set individual account allocation
- **Database Collections:**
  - `lucrum_wallet` - Stores current wallet balance, notes, timestamps
  - `allocation_history` - Audit log of allocation resets
- **Files Modified:**
  - `/app/backend/server.py` - Added wallet endpoints and updated cashflow/complete
  - `/app/frontend/src/components/CashFlowManagement.js` - Added wallet UI section
- **Initial Setup Done:**
  - Set Lucrum Wallet to $407,316.36
  - Reset all 5 manager allocations to $0 (previously totaled $369,900.01)
- **Status:** COMPLETE - Tested via API and UI screenshots

#### Data Contamination Bug Fix - Demo Account Isolation (Mar 2, 2026) ✅
- **Bug:** Demo accounts (account_type='live_demo') were appearing in real fund dashboards
- **Impact:** Money Managers and Cash Flow tabs showed inflated/incorrect data
- **Root Cause:** Backend endpoints not filtering by account_type
- **Fix Applied:**
  - Added `{"account_type": {"$ne": "live_demo"}}` filter to:
    - `/api/v2/derived/fund-portfolio` (line 136)
    - `/api/v2/derived/money-managers` (line 260)
    - `/api/v2/derived/positions-overview` (lines 412, 450)
    - `/api/admin/fund-performance/dashboard` (line 22781)
- **Files Modified:**
  - `/app/backend/routes/single_source_api.py`
  - `/app/backend/server.py`
- **Verification:**
  - API returns 5 real managers, 0 demo accounts
  - Demo accounts correctly isolated to LIVE DEMO tab
- **Status:** COMPLETE - Verified via curl and screenshots

#### Instruments & Risk Parameters Admin Tabs (Mar 2, 2026) ✅
- **Feature:** Two new tabs in FIDUS Admin Dashboard for managing risk configurations
- **Instruments Specifications Tab:**
  - Displays all 61 tradeable instruments with full contract specs
  - Columns: Symbol, Name, Class, Leverage, Margin, Contract Size, Pip Value, Spread, Trading Hours
  - Filter by asset class (ALL, FX Major, FX Cross, Index CFD, Metals, Commodities, Crypto)
  - Search by symbol/name
  - Export to CSV functionality
  - Sortable columns
- **Risk Parameters Tab:**
  - Trade Risk Limits: Max Risk Per Trade (1%), Max Margin Usage (25%)
  - Loss Limits: Max Intraday (3%), Max Weekly (6%), Max Monthly Drawdown (10%)
  - Force Flat (EOD): Time and Timezone settings
  - Leverage by Asset Class table with live data
  - Risk Score Penalty Structure reference
  - Edit mode with Save/Cancel buttons
- **Files Created:**
  - `/app/frontend/src/components/InstrumentSpecifications.js`
  - `/app/frontend/src/components/InstrumentSpecifications.css`
  - `/app/frontend/src/components/RiskParameters.js`
  - `/app/frontend/src/components/RiskParameters.css`
- **Status:** COMPLETE - 100% test pass rate (11/11 backend + all frontend tests)

#### Contract Specifications Database & Risk Engine Update (Mar 2, 2026) ✅
- **Task:** Import all MultiBank contract specifications and ensure risk calculations use proper specs
- **Database Update:**
  - Added 60 instruments total (53 new, 7 updated)
  - Forex Majors: 7 pairs (EURUSD, GBPUSD, USDJPY, etc.)
  - Forex Crosses: 21 pairs (EURGBP, GBPJPY, etc.)
  - Indices: 14 (DE40, NAS100, US30, UK100, HK50, JP225, etc.)
  - Metals: 4 (XAUUSD, XAGUSD, XPTUSD, XPDUSD)
  - Commodities: 5 (USOUSD, UKOUSD, NATGAS, CLxx, LCOxx)
  - Crypto: 9 (BTCUSD, ETHUSD, XRPUSD, ADAUSD, etc.)
- **Risk Engine Fixes:**
  - Updated `calculate_max_lots()` to use `margin_pct` from specs (not hardcoded leverage)
  - Fixed FX stop distance handling (pips vs price format)
  - Added asset class-specific loss calculations for each instrument type
  - Included `contract_size`, `margin_pct`, `effective_leverage` in calculation results
- **Each instrument includes:**
  - Symbol, Name, Asset Class
  - Margin % (0.2% to 10% based on MultiBank specs)
  - Contract Size (100 oz gold, 100,000 FX, etc.)
  - Quote Currency
  - Pip Value Per Lot
  - Default Stop Distance
- **Status:** COMPLETE - All 60 instruments tested with accurate calculations

#### Risk Limits Bug Fix - Demo Account Deal Data (Mar 2, 2026) ✅
- **Bug:** Risk Limits tab showed 0 trades analyzed and 100% compliance for ALL demo strategies
- **Root Cause:** Demo account deals stored in `mt5_deals_history` collection, not `mt5_deals`
- **Fix Applied:**
  1. Added `get_deals_for_account()` method to Hull Risk Engine
  2. Method queries BOTH `mt5_deals` AND `mt5_deals_history` collections
  3. Filters out deposits/withdrawals (non-trading operations)
  4. Optimized performance with symbol-based caching (reduced from 96s to <1s)
- **Verified Results:**
  - Account 2217 (UNO14): 1015 trades, Score 70 (Moderate) ✅
  - Account 2210 (GOLD DAY TRADING): 625 trades, Score 40 (Weak) ✅
  - Account 2215 (JOEL NASDAQ): 407 trades, Score 100 (Strong) ✅
  - Account 2216 (JOEL GOLD): Score 72 (Moderate) ✅
  - Account 20062 (CRYPTO BITCOIN): Score 100 (Strong) ✅
- **Files Modified:**
  - `/app/backend/services/hull_risk_engine.py` - Added get_deals_for_account(), optimized caching
- **Status:** COMPLETE - 100% test pass rate (backend + frontend)

#### Risk Limits Tab Enhanced Features (Mar 2, 2026) ✅
- **Feature:** Three new features for comprehensive risk analysis and improvement guidance
- **Components Built:**
  1. **Active Risk Alerts Section:**
     - CRITICAL/WARNING severity badges
     - Alert types: RISK_BREACH, LOT_BREACH, DAILY_LOSS_BREACH
     - Real-time notification of compliance issues
  2. **Action Items to Improve Score:**
     - HIGH/MEDIUM/LOW priority badges
     - Category labels (risk_per_trade, lot_size, daily_loss)
     - Issue description + specific fix recommendations
  3. **Detailed Compliance Breakdown (Expandable):**
     - Policy limit, calculation formula, breaches, compliance rate, penalty applied
     - Per-instrument lot size limits table with breach percentages
  4. **What-If Simulator:**
     - Equity slider (25% to 300% of current)
     - "Simulate" button to recalculate
     - Limits Comparison (Risk Per Trade, Daily Loss)
     - Max Lots by Instrument comparison (XAUUSD, GER40, US30, NAS100, BTCUSD)
     - Score Projection by Equity Level chart (6 scenarios: 50%, 75%, Current, 125%, 150%, 200%)
- **API Endpoints:**
  - GET `/api/admin/risk-engine/what-if/{account}` - Returns simulation data
  - GET `/api/admin/risk-engine/strategy-analysis/{account}` - Now includes alerts, action_items, compliance_details
- **Files Modified:**
  - `/app/backend/services/hull_risk_engine.py` - Added alerts, action_items, compliance_details, what_if_scenarios
  - `/app/backend/server.py` - Added What-If simulator endpoint
  - `/app/frontend/src/components/LiveDemoAnalytics.js` - Added UI components
  - `/app/frontend/src/components/LiveDemoAnalytics.css` - Added styles for new sections
- **Status:** COMPLETE - 100% test pass rate (16/16 backend + 7/7 frontend tests)

#### Hull-Style Risk Engine & Trading Analytics Enhancements (Mar 1, 2026) ✅
- **Feature:** Institutional-grade risk management aligned with John C. Hull discipline
- **Design:** Dark luxury fintech aesthetic with new Risk Limits tab
- **Components Built:**
  1. **Position Sizing Calculator:** Hull-style MaxLotsAllowed calculation
     - MaxLotsAllowed = min(MaxLotsRisk, MaxLotsMargin)
     - Risk-bound formula: MaxLotsRisk = RiskBudget / LossPerLotAtStop
  2. **Strategy Allocation Chart:** Horizontal bar chart showing capital allocation per money manager
     - Replaced incorrect "Fund Allocation" pie chart
     - Toggle between Allocated, Equity, and P&L views
  3. **Risk Profile Interpretation Panel:** Deterministic AI-style narrative
     - Executive Summary with bullet points
     - Metric analysis (Sharpe, Win Rate, Profit Factor, Risk Control)
     - LOW CONFIDENCE warning when insufficient data
  4. **Risk Limits Tab (NEW):** 
     - Active Risk Policy header (1%, 3%, 25%, 200:1)
     - Position Sizing Calculator with instrument dropdown
     - XAUUSD calculation examples
     - Key insight: "Risk limit (not margin) is binding constraint"
- **Risk Policy Defaults:**
  - Max Risk Per Trade: 1.0% (range 0.25-2.0%)
  - Max Intraday Loss: 3.0%
  - Max Weekly Loss: 6.0%
  - Max Monthly Drawdown: 10.0%
  - Max Margin Usage: 25.0%
  - Leverage: 200:1 (static)
  - No overnight exposure (force-flat 16:50 NY)
- **Risk Control Score (0-100):** Deterministic penalty-based scoring
- **instrument_specs Collection:** 7 FIDUS Tier-1 instruments
  - XAUUSD, EURUSD, GBPUSD, USDJPY, AUDCAD, US30, DE40
- **API Endpoints:**
  - GET `/api/admin/risk-engine/instrument-specs`
  - POST `/api/admin/risk-engine/calculate-max-lots`
  - GET `/api/admin/risk-engine/policy`
  - GET `/api/admin/risk-engine/narrative`
- **Files Created/Modified:**
  - `/app/backend/services/hull_risk_engine.py` (1200+ lines)
  - `/app/backend/seed_instrument_specs.py` - Collection seeder
  - `/app/backend/tests/test_hull_risk_engine.py` - Pytest tests
  - `/app/frontend/src/components/NextGenTradingAnalytics.js` (updated)
- **Status:** COMPLETE - 100% test pass rate (backend + frontend)
- **Documentation:** SYSTEM_MASTER.md updated with Hull Risk Engine section

#### Live Demo Analytics Dashboard (Feb 27, 2026) ✅
- **Feature:** Complete analytics dashboard for LIVE DEMO accounts (manager candidate evaluation)
- **Design:** Purple/Orange theme (#A855F7, #F97316) to distinguish from real trading analytics
- **Data Separation:** REAL accounts (account_type=null) and DEMO accounts (account_type='live_demo') are completely isolated
- **Components:** Same as Trading Analytics but filtered for demo accounts only
  - DEMO ACCOUNTS badge with orange pulsing indicator
  - KPI Strip showing demo portfolio metrics
  - Portfolio Overview, Manager Rankings, Deep Dive tabs
  - AI Advisor with demo-specific context ("Which managers should receive real capital?")
- **Hull-style Risk Engine (Mar 1, 2026):** Full feature parity with Trading Analytics
  - Strategy Allocation horizontal bar chart (Allocated/Equity/P&L toggle)
  - Portfolio Risk Profile radar chart (5 metrics)
  - Risk Profile Interpretation narrative panel
  - Risk Limits tab with Position Sizing Calculator
  - XAUUSD Example with verified calculations
  - Strategy Risk Analysis dropdown (5 demo accounts)
- **API Endpoints:** 
  - `/api/admin/live-demo-analytics/managers` - Returns only live_demo accounts
  - `/api/admin/live-demo-ai-advisor/*` - AI endpoints with demo context
- **Files Created:**
  - `/app/frontend/src/components/LiveDemoAnalytics.js` - Dashboard component (updated with Risk Engine)
  - `/app/frontend/src/components/LiveDemoAnalytics.css` - Purple/orange theme (updated)
  - `/app/backend/services/live_demo_analytics_service.py` - Backend service
- **Status:** COMPLETE - 100% test pass rate, all Risk Engine features verified

#### Next-Generation Trading Analytics Dashboard (Feb 27, 2026) ✅
- **Feature:** Complete replacement of the old Trading Analytics tab with an institutional-grade dashboard
- **Design:** Dark luxury fintech aesthetic (deep navy #0A0F1C, gold #FFB800, cyan #00D4AA accents)
- **Typography:** DM Mono for data, Sora/Plus Jakarta Sans for headings (Google Fonts CDN)
- **Components Built:**
  1. **Top Header Bar:** Time-period selector (7/30/90/180/365 days), Refresh/Export buttons, live UTC clock, Auto-refresh toggle (30s)
  2. **Summary KPI Strip:** 7 metrics (Total AUM, Total P&L, Avg Return, Active Strategies, Avg Sharpe, Avg Win Rate, Total Trades)
  3. **Portfolio Overview Tab:** Fund Allocation pie chart, Portfolio Risk Profile radar chart, Strategy Performance bar chart, Risk vs Return scatter chart
  4. **Manager Rankings Tab:** Strategy Leaderboard table with sortable columns, fund badges (CORE/BALANCE/SEPARATION), risk badges (LOW/MEDIUM/HIGH), head-to-head comparison panel, risk alerts section
  5. **Deep Dive Tab:** Strategy selector (defaults to TradingHub Gold #886557), strategy header with performance badge, key metrics grid, equity curve area chart, risk metrics (Sharpe/Sortino/Max Drawdown) with progress bars, trading statistics grid, allocation insight recommendation card
  6. **AI Strategy Advisor Tab (Phase 3):** Claude Sonnet 4.5 integration via Emergent LLM key, featuring:
     - **AI Insights:** Auto-generated portfolio analysis with Health Score and rationale
     - **Allocation Advisor:** Capital allocation recommendations based on risk tolerance
     - **Chat Interface:** Interactive Q&A with Claude about trading strategies
- **Auto-refresh:** 30-second silent data refresh with Live/Paused toggle indicator
- **Data Source:** Live data from `/api/admin/trading-analytics/managers` endpoint
- **AI Endpoints:** `/api/admin/ai-advisor/chat`, `/api/admin/ai-advisor/insights`, `/api/admin/ai-advisor/allocation`
- **Tech Stack:** React, Recharts, Tailwind CSS, lucide-react, Claude Sonnet 4.5
- **Files Created:**
  - `/app/frontend/src/components/NextGenTradingAnalytics.js` - Main component (~1500 lines)
  - `/app/frontend/src/components/NextGenTradingAnalytics.css` - Dark luxury styling (~1500 lines)
  - `/app/backend/services/ai_strategy_advisor.py` - AI advisor service (~250 lines)
- **Status:** COMPLETE - All 3 phases implemented, tested, and verified

#### Investment Simulator Currency Fixes (Feb 21, 2026) ✅
- **Live Exchange Rates:** Backend now fetches live rates from exchangerate-api.com (free, no API key)
  - Before: Hardcoded 18.5 MXN
  - After: Live rate ~17.17 MXN (updates hourly)
- **Timeline Tab Currency Fix:** Timeline tab now respects selected currency (MXN/EUR)
  - Before: Always showed amounts in USD
  - After: Shows amounts in selected currency

#### Financial Calculation Fixes
- [x] Fund Portfolio P&L calculation corrected (using only active accounts)
- [x] Account Management totals fixed to filter by `status='active'`
- [x] Wealth Calendar logic corrected (Performance Gap vs Running Balance)
- [x] Core `get_total_equity` function updated to filter by status

#### Data Synchronization
- [x] GitHub Actions workflow for MT5 data sync (`sync-lucrum-accounts-to-mongodb.yml`)
- [x] Live data sync from MT5 VPS bridge
- [x] Zeroing out inactive MEXAtlantic accounts

#### Referral Agent System
- [x] Agent creation endpoint
- [x] Referral code generation
- [x] Agent portal login system

### Bug Fixes (Feb 19, 2026)

#### P0 - Cesar Lambreton Login Fix
- **Issue:** New referral agent `cesar@gacel.llc` could not log in
- **Root Cause:** 
  1. Password stored as plain text instead of bcrypt hash
  2. Missing `id` field in user document
- **Fix Applied:**
  1. Hashed password with bcrypt (`$2b$12$...`)
  2. Added `id` field (`referral_agent_c6d88ca9`)
  3. Added `profile_picture` field
- **Status:** RESOLVED, login working

## Known Issues

### P0 - VPS API Service Not Running (CRITICAL)
- **Issue:** Backend cannot connect to MT5 Bridge API at 92.118.45.135:8000
- **Root Cause:** Nothing is listening on port 8000 - the MT5 bridge service is not running or lacks HTTP server functionality
- **Impact:** Live data sync failures, continuous alert emails about "VPS down"
- **Diagnosis Result:** Connection refused (not timeout) confirms port is reachable but no service listening
- **Fix Required:** Deploy the proper FastAPI MT5 Bridge API service to the VPS
- **Workflows Created:**
  1. `diagnose-lucrum-vps-api.yml` - Diagnose current VPS state
  2. `deploy-mt5-bridge-api-lucrum.yml` - Deploy the MT5 Bridge API service
- **Status:** IN PROGRESS - Workflows created, awaiting GitHub Actions execution

### P1 - Other Referral Agents Login Issues
- Three other referral agents may have the same login issue
- Likely need the same fix (hash password, add id field)

### P2 - Legacy Issues
- Lucrum MT5 Bridge duplicate key errors
- VIKING CORE & PRO strategies data sync not enabled

## Database Schema

### users Collection
```json
{
  "id": "string (required)",
  "username": "string",
  "email": "string",
  "name": "string",
  "type": "admin|client|referral_agent",
  "status": "active|inactive",
  "password": "bcrypt hash (required for login)",
  "temp_password": "plain text (for first login)",
  "profile_picture": "url string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### salespeople Collection
```json
{
  "name": "string",
  "email": "string",
  "referral_code": "string (unique)",
  "referral_link": "url string",
  "password_hash": "bcrypt hash",
  "status": "active|inactive",
  "active": "boolean"
}
```

## Credentials
- **FIDUS Admin:** `admin` / `Password123`
- **Referral Agent (fixed):** `cesar@gacel.llc` / `Fidus2026!`

## Future/Backlog Tasks

### P0
- [ ] Deploy MT5 Bridge API service to LUCRUM VPS (92.118.45.135:8000)

### P1
- [ ] Fix root cause in agent creation script to properly hash passwords
- [ ] Fix login for other affected referral agents
- [ ] Create backend regression tests for data contamination bug

### P2
- [ ] Enable live data sync for VIKING CORE & PRO strategies
- [ ] Verify pagination on VIKING "Orders" tab with large datasets
- [ ] Refactor VikingDashboard.js, CashFlowManagement.js, LiveDemoAnalytics.js into smaller components
- [ ] Address Lucrum MT5 Bridge duplicate key errors
- [ ] Backend notification system for Risk Alerts (email, push)

## Key Files Reference
- `/app/backend/server.py` - Main backend with login endpoint, Live Demo API, Lucrum Wallet endpoints
- `/app/backend/routes/referrals.py` - Agent portal routes
- `/app/backend/routes/single_source_api.py` - Single Source of Truth API (demo account filtering)
- `/app/backend/services/calculations.py` - Financial calculations
- `/app/backend/services/trading_analytics_service.py` - Trading analytics service for manager rankings
- `/app/backend/services/hull_risk_engine.py` - Hull-style Risk Engine (MaxLotsAllowed, Risk Control Score)
- `/app/backend/seed_instrument_specs.py` - FIDUS Tier-1 instrument specs seeder
- `/app/frontend/src/components/NextGenTradingAnalytics.js` - Next-Gen Trading Analytics Dashboard with Risk Limits tab
- `/app/frontend/src/components/CashFlowManagement.js` - Cash Flow tab with Lucrum Wallet section
- `/app/frontend/src/components/NextGenTradingAnalytics.css` - Dark luxury fintech styling
- `/app/frontend/src/components/AdminDashboard.js` - Admin dashboard with Trading Analytics tab
- `/app/frontend/src/components/LiveDemoDashboard.js` - Live Demo dashboard component
- `/app/.github/workflows/sync-lucrum-accounts-to-mongodb.yml` - Data sync workflow (updated with demo accounts)
- `/app/.github/workflows/diagnose-lucrum-vps-api.yml` - VPS diagnostic workflow
- `/app/.github/workflows/deploy-mt5-bridge-api-lucrum.yml` - MT5 Bridge API deployment workflow
- `/app/.github/workflows/emergency-restart-mt5-bridge-lucrum.yml` - Emergency restart workflow (uses VPS_PORT secret)
- `/app/vps/mt5_bridge_api_service.py` - FastAPI MT5 Bridge service to deploy to VPS
- `/app/SYSTEM_MASTER.md` - System documentation (updated with Hull Risk Engine section)

## GitHub Workflows for VPS Management
1. **diagnose-lucrum-vps-api.yml** - Diagnoses VPS state: checks port 8000 listener, Python processes, script contents, Task Scheduler, logs
2. **deploy-mt5-bridge-api-lucrum.yml** - Deploys the full FastAPI MT5 Bridge API service with uvicorn, creates Task Scheduler entry for auto-restart
3. **emergency-restart-mt5-bridge-lucrum.yml** - Emergency restart workflow using VPS_PORT secret
4. **sync-lucrum-accounts-to-mongodb.yml** - Syncs LUCRUM accounts (now includes 20062, 2210 Live Demo accounts)

## Live Demo Accounts (NEW)
- Purpose: Evaluate new money managers with simulated funded accounts
- Account 20062: Demo Manager 1 (password: Fidus2026@)
- Account 2210: Demo Manager 2 (password: YtJ!T7Qi)
- Server: Lucrumcapital-Live
- Status: Configured in mt5_account_config and mt5_accounts collections
- API: `/api/live-demo/accounts`
