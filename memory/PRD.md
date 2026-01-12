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

**Access VIKING Portal at:** `/viking`

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
