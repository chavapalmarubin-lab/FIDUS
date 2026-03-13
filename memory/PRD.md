# FIDUS Investment Platform - Product Requirements Document

## Original Problem Statement
Build a standalone "VIKING" trading analytics dashboard alongside a comprehensive FIDUS investment platform with:
- Public, no-login VIKING dashboard and private admin dashboard
- Correct calculation and display of total portfolio values, P&L, and cash flow projections
- Creation of referral links for new FIDUS agents
- Reliable mechanism to sync live data from MT5 accounts into MongoDB database
- White Label Franchise System for third-party companies to manage their own clients

## Core Architecture
- **Frontend:** React with Tailwind CSS + Shadcn/UI
- **Backend:** FastAPI with Python
- **Database:** MongoDB Atlas (fidus_production)
- **Deployment:** Render (production), Emergent (preview)

## What's Been Implemented

### White Label Franchise System

#### Phase 1 (Completed - Mar 12, 2026)
- Multi-tenant database schema with `franchise_companies` collection
- CRUD API endpoints for franchise management at `/api/franchise/`
- "White Label" management tab in FIDUS Admin Dashboard
- Company creation with commission split structure, subdomain, branding

#### Phase 2 (Completed - Mar 13, 2026)
- **Franchise Admin Authentication:** Separate JWT-based auth system at `/api/franchise/auth/`
  - Register, Login, Verify, Change Password endpoints
  - JWT tokens carry company_id for multi-tenant data filtering
- **Franchise Dashboard API:** Full suite of multi-tenant endpoints at `/api/franchise/dashboard/`
  - Overview, Portfolio, Cash Flow, Clients, Agents, Commissions, Instruments, Risk Policy
  - All data filtered by company_id from JWT token
- **Franchise Admin Portal UI:** Complete React portal at `/franchise/login`
  - 9 tabs: Overview, Fund Portfolio, Cash Flow, Instruments, Risk Parameters, Gap Analysis, Clients, Referrals, Commissions
  - Company branding support (logo, colors)
  - Sandboxed view showing only company-specific data
- **Files:**
  - `/app/backend/routes/franchise_auth.py` - Auth endpoints
  - `/app/backend/routes/franchise_dashboard.py` - Dashboard endpoints
  - `/app/backend/routes/franchise_api.py` - Company CRUD
  - `/app/frontend/src/components/FranchiseLogin.js` - Login page
  - `/app/frontend/src/components/FranchisePortal.js` - Portal with all tabs
- **Test Franchise:** Test Franchise Co (code: testco, admin: admin@testco.com / FranchiseTest123)

### Other Completed Features (Dec 2025 - Mar 2026)
- Final Capital Allocation ($407K across trading accounts)
- Drawdown as Paramount Risk Metric (Hull-Style Risk Engine)
- Quantitative Drawdown Trigger Analysis
- Multi-Source Copy Trading
- LUCRUM MT5 Account Integration (accounts 2218, 2219)
- Money Managers Dashboard editing (profiles, copy configs)
- Dashboard filtering (hide zero-allocation managers)
- AI Strategy Advisor (Claude Sonnet 4.5)
- Complete Trading Analytics & Live Demo Analytics dashboards
- Investment Committee Allocation Workflow
- Client Management, CRM, Referral System
- MT5 Auto-Healing & Bridge Monitoring

## Prioritized Backlog

### P0 (Next)
- **Phase 3: White Label Client & Referral Agent Portals** - Build client-facing portal for franchise clients to view their investments, and agent portal for referral tracking

### P1 (High Priority)
- Fix intermittent frontend blank page / session loss bug (recurring P1)
- Deploy MT5 Bridge API service to LUCRUM VPS
- Create backend regression tests

### P2 (Medium Priority)
- Fix bulk copy ratio API performance (`/api/admin/risk-engine/copy-ratio-all`)
- Fix Lucrum MT5 Bridge duplicate key errors
- Implement backend notification system for "Risk Alerts"
- Enable live data sync for VIKING CORE & PRO strategies

### P3 (Low Priority / Refactoring)
- Refactor `single_source_api.py` into domain-specific route files
- Break down `MoneyManagersDashboard.js` into smaller components
- Refactor `server.py` (29K+ lines) into modular structure

## Key Technical Concepts
- **SSOT Architecture:** mt5_accounts is the single source of truth for all account data
- **Multi-Tenant Franchise:** company_id in JWT tokens filters all data per franchise
- **Dynamic MT5 Sync:** VPS bridge reads from mt5_account_config collection
- **Hull-Style Risk Engine:** Institutional risk management with deterministic scoring

## Test Credentials
- **FIDUS Admin:** username=admin, password=Password123, user_type=admin
- **Franchise Admin:** email=admin@testco.com, password=FranchiseTest123
