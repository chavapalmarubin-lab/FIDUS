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

### Next Steps (Phase 2 - VPS Configuration)
1. Configure MT4 bridge on VPS to sync VIKING CORE account (33627673) data
2. Set up Traders Trust MT4 terminal for PRO account (1309411)
3. Attach MT4 EA to sync data to MongoDB `viking_*` collections

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
