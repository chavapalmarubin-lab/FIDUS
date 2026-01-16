# FIDUS Investment Management Platform - PRD

## Original Problem Statement
Full-stack financial dashboard (React + FastAPI + MongoDB) for FIDUS Investment Committee managing:
- Fund portfolio tracking (MT5 accounts)
- Client investments and obligations
- Referral system
- Cash flow management
- Trading analytics

## Recent Major Addition: VIKING Trading Operations (Jan 11, 2026)

### What is VIKING?
VIKING is a **completely separate trading operation** from FIDUS Funds. It manages two trading strategies:

| Strategy | Account | Broker | Server | Platform | Status |
|----------|---------|--------|--------|----------|--------|
| **CORE** | 33627673 | MEXAtlantic | MEXAtlantic-Real-2 | MT4 | ✅ Pending Sync |
| **PRO** | 1309411 | Traders Trust | TTCM | MT4 | ⚠️ Pending Setup |

### Architecture
- **VIKING is NOT part of FIDUS funds** (CORE, BALANCE, DYNAMIC)
- Uses separate MongoDB collections: `viking_accounts`, `viking_deals_history`, `viking_analytics`
- Has its own API endpoints under `/api/viking/*`
- Has its own navigation tab in the Admin Dashboard

### Implementation Status (Phase 1 Complete)

#### Backend (✅ Complete)
- Created `/app/backend/routes/viking.py` with all API endpoints:
  - `GET /api/viking/accounts` - Get all VIKING accounts
  - `GET /api/viking/accounts/{account_number}` - Get specific account
  - `POST /api/viking/accounts` - Create new account
  - `PUT /api/viking/accounts/{account_number}` - Update account (for MT4 bridge sync)
  - `GET /api/viking/analytics/{strategy}` - Get analytics for CORE or PRO
  - `POST /api/viking/analytics/{account_number}` - Save calculated analytics
  - `GET /api/viking/deals/{strategy}` - Get deal history
  - `POST /api/viking/deals/batch` - Batch insert deals from MT4 bridge
  - `GET /api/viking/orders/{strategy}` - Get open orders
  - `GET /api/viking/summary` - Combined summary
  - `GET /api/viking/symbols/{strategy}` - Symbol distribution for charts
  - `GET /api/viking/balance-history/{strategy}` - Balance history for charts
  - `GET /api/viking/risk/{strategy}` - Risk analysis data
  - `POST /api/viking/sync` - Trigger manual sync

#### Frontend (✅ Complete)
- Created `/app/frontend/src/components/VikingDashboard.js`
- Added VIKING tab to AdminDashboard navigation
- Following FXBlue format with 5 sub-tabs:
  - **Overview**: Strategy cards, stats summary, balance chart, symbol distribution
  - **Analysis**: Balance+deposits chart, profit analysis, market breakdown
  - **Stats**: Detailed metrics, deposits/profit/loss tables, returns breakdown
  - **Risk**: Risk of ruin table, balance metrics, equity metrics
  - **Orders**: Trade history table

#### Database Collections (✅ Created)
- `viking_accounts` - Account data with unique index on account number
- `viking_deals_history` - Trade history with compound index (account, ticket)
- `viking_analytics` - Calculated performance metrics

### Phase 2 - VPS Configuration ✅ COMPLETE (Jan 11, 2026)
1. ✅ Deploy VIKING MT4 Bridge service to VPS (port 8001)
2. ✅ Copy EA to MEXAtlantic MT4 terminal MQL4/Experts folder
3. ✅ Compile EA in MetaEditor
4. ✅ Enable WebRequest for `http://localhost:8001` in MT4 Options
5. ✅ Attach EA to any chart on account 33627673
6. ✅ MongoDB connected - viking_accounts collection active
7. ✅ Set up Windows Task Scheduler for auto-start on reboot

### Phase 3 - Analytics & Visualization ✅ COMPLETE (Jan 12, 2026)
1. ✅ Balance Charts - Added AreaChart with balance/equity visualization
2. ✅ Analytics Calculations Endpoint - `/api/viking/calculate-analytics/{strategy}`
   - Total Return %, Monthly/Weekly/Daily Return %
   - Profit Factor, Win Rate %, Risk/Reward Ratio
   - Peak Drawdown, Trade Statistics
3. ✅ Balance Snapshots - `/api/viking/snapshot-balance/{strategy}` and `/api/viking/balance-snapshots/{strategy}`
4. ✅ Profit Analysis Chart - Best/Worst/Average trade visualization
5. ✅ Symbol Distribution - Pie chart from `/api/viking/symbols/{strategy}`
6. ✅ "Calculate Analytics" button added to dashboard header

### VIKING MT4 Bridge Files (Created Jan 11, 2026)
| File | Location | Description |
|------|----------|-------------|
| `VIKING_MT4_Bridge.mq4` | `/app/backend/mt4_bridge/` | MT4 Expert Advisor |
| `viking_mt4_bridge_service.py` | `/app/backend/mt4_bridge/` | Python service (port 8001) |
| `start_viking_bridge.bat` | `/app/backend/mt4_bridge/` | Windows startup script |
| `start_viking_bridge.sh` | `/app/backend/mt4_bridge/` | Linux startup script |
| `requirements_viking.txt` | `/app/backend/mt4_bridge/` | Python dependencies |
| `deploy-viking-mt4-bridge.yml` | `/.github/workflows/` | GitHub Actions deployment |

### Phase 4 - Standalone VIKING Application ✅ COMPLETE (Jan 12, 2026)
1. ✅ Created `/viking` route - completely separate from FIDUS
2. ✅ VikingLogin.js - Separate login page with VIKING branding
3. ✅ VikingApp.js - Standalone wrapper with header, logout, footer
4. ✅ Own credentials: `viking_admin` / `viking2026`
5. ✅ All 5 tabs accessible: Overview, Analysis, Stats, Risk, Orders

### Phase 5 - VKNG AI Branding ✅ COMPLETE (Jan 12, 2026)
Applied official getvkng.com branding to entire VIKING portal:
- ✅ Downloaded official VKNG AI logo (purple "V" icon)
- ✅ Color scheme: Dark navy (#0A112B), Purple (#9B27FF), Pink/Magenta gradient (#E621A4 → #CC00FF)
- ✅ Login page: Purple gradient background, magenta button, logo with purple glow
- ✅ Dashboard header: Logo, LIVE indicator, Account badge, purple accents
- ✅ Tabs: Pink-to-magenta gradient on active tab
- ✅ Cards: Purple borders and accent icons
- ✅ Charts: Updated to use VKNG purple color scheme

### Phase 6 - MT4 Trade History Integration ✅ COMPLETE (Jan 12, 2026)
- ✅ Created `VIKING_Account_Data_Writer.mq4` v2.0 with closed trades export (MODE_HISTORY)
- ✅ Updated `viking_file_monitor.py` to sync closed trades to `viking_deals_history` collection
- ✅ 77 closed trades synced from MT4 account 33627673
- ✅ Backend analytics calculation from real trade data
- ✅ Real metrics: 97.4% win rate, $801.74 profit, 844.94 profit factor
- ✅ Removed all placeholder/template data from dashboard
- ✅ Fixed routing - VIKING app completely separate from FIDUS at `/viking`

### Phase 7 - Complete Dashboard Tabs ✅ COMPLETE (Jan 12, 2026)
- ✅ **Orders Tab**: Displays 77 closed trades with ticket, close time, type, lots, symbol, open/close prices, commission, swap, profit
- ✅ **Overview Tab**: Real balance/equity, calculated analytics (win rate, profit factor, drawdown, etc.)
- ✅ **Analysis Tab**: Balance chart, Profit analysis bar chart, Market/Return analysis with XAUUSD.ecn data
- ✅ **Stats Tab**: Returns, Currency, Equity, Balance, Floating P/L, Deposits/Profit/Loss table
- ✅ **Risk Tab**: Risk of Ruin probability table, Balance Metrics, Equity Metrics
- ✅ All data is real, calculated from 77 closed trades in `viking_deals_history`

### Phase 8 - Multi-Strategy Support ✅ COMPLETE (Jan 13, 2026)
- ✅ Added Strategy Selector (ALL | CORE | PRO) to dashboard header
- ✅ Combined Portfolio summary showing total balance/equity across all accounts
- ✅ VIKING CORE card (blue accent) - Active, connected to MEXAtlantic
- ✅ VIKING PRO card (purple accent) - Pending Setup, for Traders Trust account
- ✅ Created PRO account EA: `VIKING_PRO_Account_Data_Writer.mq4`
- ✅ Created PRO account Python service: `viking_pro_file_monitor.py`
- ✅ Created comprehensive GitHub Action: `deploy-viking-pro-bridge.yml`
  - Full deployment (EA + Python service + batch files + scheduled task)
  - Separate options: deploy EA only, deploy Python only, restart, status, logs, test sync
- ⏳ **Pending User Action**: Deploy EA and Python service on VPS for account 1309411
  - User can trigger via GitHub Actions → "Deploy VIKING PRO MT4 Bridge" workflow

### Phase 9 - Orders Tab Pagination ✅ COMPLETE (Jan 13, 2026)
- ✅ Added pagination controls to Orders tab header
- ✅ "Show" dropdown: 10, 25, 50, 100 items per page
- ✅ Page navigation: First, Prev, Next, Last buttons
- ✅ Page indicator: "Page X of Y"
- ✅ Bottom pagination summary: "Showing X - Y of Z trades"
- ✅ "Jump to page" input for direct navigation
- ✅ Backend pagination API already supported (`skip` and `limit` params)

### Phase 10 - Accurate Monthly Returns (Deposits/Withdrawals) ✅ IMPLEMENTED (Dec 2025)
**Problem:** Monthly return percentages were inaccurate because deposits/withdrawals were counted as trading profit.

**Solution:** Updated the complete data pipeline:
1. ✅ **MQL4 EAs Updated** (v3.0) - Now export `balance_operations` array with deposits/withdrawals
   - `VIKING_Account_Data_Writer.mq4` - Added balance operations export (OrderType() == 6)
   - `VIKING_PRO_Account_Data_Writer.mq4` - Already had balance operations, version bumped
2. ✅ **Python File Monitors Updated** - Process `balance_operations` array from JSON
   - `viking_file_monitor.py` - Added `upload_balance_operations()` function
   - `viking_pro_file_monitor.py` - Added `upload_balance_operations()` function
3. ✅ **Backend Analytics Updated** - Separates trading P&L from balance operations
   - `/api/viking/monthly-returns/{strategy}` - Excludes deposits from profit calculations
   - `/api/viking/calculate-analytics/{strategy}` - Properly tracks deposits vs trading profit
   - Returns `deposits_info` object with: `total_deposits`, `total_withdrawals`, `net_deposits`, `total_trading_profit`

**Formula Used:**
```
Monthly Return % = Trading Profit / Total Deposits × 100
Where: Trading Profit = Sum of actual trade profits (BUY/SELL only, no DEPOSIT/WITHDRAWAL)
```

**⏳ PENDING USER ACTION:** 
- Deploy updated EAs to VPS (both CORE and PRO accounts)
- Restart MT4 terminals to load v3.0 EAs
- Wait for next sync cycle to import balance operations
- Verify balance operations appear in MongoDB

**PRO Account Credentials:**
- Account: 1309411
- Broker: Traders Trust
- Password: `eM@54f*M4PB1`

**Access VIKING Portal at:** `/viking`
**Login:** `admin` / `Password123`

---

## Core Architecture

### Single Source of Truth (SSOT)
- **MT5 Accounts** = "THE FUND" (one pool of money)
- **Client Products** (CORE, BALANCE, DYNAMIC) = OBLIGATIONS only
- Fund Portfolio correctly separates "Fund Assets" from "Client Obligations"

### Technology Stack
- **Frontend**: React 18, Tailwind CSS, shadcn/ui, Recharts
- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas
- **Deployment**: Render

## Files of Reference

### VIKING Implementation
- `/app/backend/routes/viking.py` - VIKING API routes
- `/app/frontend/src/components/VikingDashboard.js` - VIKING UI component

### Core Platform
- `/app/backend/server.py` - Main FastAPI application
- `/app/backend/services/calculations.py` - SSOT calculations
- `/app/frontend/src/components/AdminDashboard.js` - Main admin UI
- `/app/frontend/src/components/FundPortfolioManagement.js` - Fund Portfolio

---

## Completed Work

### January 11, 2026
- ✅ Created VIKING Trading Operations tab (completely separate from FIDUS)
- ✅ Backend: All API endpoints for VIKING accounts, analytics, deals, orders
- ✅ Frontend: FXBlue-style dashboard with 5 sub-tabs
- ✅ Database: Collections with proper indexes

### Previous Sessions
- ✅ Architectural overhaul (Fund Assets vs Client Obligations)
- ✅ Fixed Investments Tab 500 error (ObjectId serialization)
- ✅ Fixed Referrals Tab sorting/filtering
- ✅ Created Wealth Calendar component
- ✅ GitHub Action for MT5 password updates
- ✅ Removed marketing section from ProspectsPortal

---

## Pending Issues

### P1 - High Priority
- Configure `GITHUB_TOKEN` for MT5 bridge auto-healing

### P2 - Medium Priority
- Remove obsolete V1 API code and backup files
- Implement Referral Link Analytics Backend
- Lucrum MT5 Bridge duplicate key errors
- Failing logins for three specific referral agents

---

## Test Credentials
- **Admin Username**: `emergent_admin`
- **Admin Password**: `password123`
