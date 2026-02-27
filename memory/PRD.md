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

### Completed Features (Dec 2025 - Feb 2026)

#### Next-Generation Trading Analytics Dashboard (Feb 27, 2026) ✅
- **Feature:** Complete replacement of the old Trading Analytics tab with an institutional-grade dashboard
- **Design:** Dark luxury fintech aesthetic (deep navy #0A0F1C, gold #FFB800, cyan #00D4AA accents)
- **Typography:** DM Mono for data, Sora/Plus Jakarta Sans for headings (Google Fonts CDN)
- **Components Built:**
  1. **Top Header Bar:** Time-period selector (7/30/90/180/365 days), Refresh/Export buttons, live UTC clock
  2. **Summary KPI Strip:** 7 metrics (Total AUM, Total P&L, Avg Return, Active Strategies, Avg Sharpe, Avg Win Rate, Total Trades)
  3. **Portfolio Overview Tab:** Fund Allocation pie chart, Portfolio Risk Profile radar chart, Strategy Performance bar chart, Risk vs Return scatter chart
  4. **Manager Rankings Tab:** Strategy Leaderboard table with sortable columns, fund badges (CORE/BALANCE/SEPARATION), risk badges (LOW/MEDIUM/HIGH), head-to-head comparison panel, risk alerts section
  5. **Deep Dive Tab:** Strategy selector (defaults to TradingHub Gold #886557), strategy header with performance badge, key metrics grid, equity curve area chart, risk metrics (Sharpe/Sortino/Max Drawdown) with progress bars, trading statistics grid, allocation insight recommendation card
  6. **AI Advisor Tab:** Placeholder with "Coming Soon" badge (Phase 3)
- **Data Source:** Live data from `/api/admin/trading-analytics/managers` endpoint
- **Tech Stack:** React, Recharts, Tailwind CSS, lucide-react
- **Files Created:**
  - `/app/frontend/src/components/NextGenTradingAnalytics.js` - Main component (~1000 lines)
  - `/app/frontend/src/components/NextGenTradingAnalytics.css` - Dark luxury styling (~800 lines)
- **Status:** COMPLETE - Phase 1 & 2 implemented, tested, and verified

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

### P2
- [ ] Enable live data sync for VIKING CORE & PRO strategies
- [ ] Verify pagination on VIKING "Orders" tab with large datasets
- [ ] Refactor VikingDashboard.js into smaller components
- [ ] Address Lucrum MT5 Bridge duplicate key errors

## Key Files Reference
- `/app/backend/server.py` - Main backend with login endpoint and Live Demo API
- `/app/backend/routes/referrals.py` - Agent portal routes
- `/app/backend/services/calculations.py` - Financial calculations
- `/app/.github/workflows/sync-lucrum-accounts-to-mongodb.yml` - Data sync workflow (updated with demo accounts)
- `/app/.github/workflows/diagnose-lucrum-vps-api.yml` - VPS diagnostic workflow
- `/app/.github/workflows/deploy-mt5-bridge-api-lucrum.yml` - MT5 Bridge API deployment workflow
- `/app/.github/workflows/emergency-restart-mt5-bridge-lucrum.yml` - Emergency restart workflow (uses VPS_PORT secret)
- `/app/vps/mt5_bridge_api_service.py` - FastAPI MT5 Bridge service to deploy to VPS
- `/app/frontend/src/components/LiveDemoDashboard.js` - NEW Live Demo dashboard component
- `/app/frontend/src/components/AdminDashboard.js` - Admin dashboard with LIVE DEMO tab

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
