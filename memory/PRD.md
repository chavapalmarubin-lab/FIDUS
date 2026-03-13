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
- **Franchise Admin Authentication:** JWT-based auth at `/api/franchise/auth/`
- **Franchise Dashboard API:** Multi-tenant endpoints at `/api/franchise/dashboard/`
- **Franchise Admin Portal UI:** 9-tab portal at `/franchise/login`
  - Overview, Fund Portfolio, Cash Flow, Instruments, Risk Parameters, Gap Analysis, Clients, Referrals, Commissions

#### Phase 3 (Completed - Mar 13, 2026)
- **Franchise Client Portal** at `/franchise/client/login`
  - Client login/auth (JWT with type=franchise_client)
  - Investment overview: total invested, returns earned/paid, pending returns
  - Account status: incubation/active, KYC status, return rate
  - Contract timeline: investment date, incubation end, contract start/end
  - Investment table with fund type, amount, returns, status
  - Company-branded header with logo support
- **Franchise Agent Portal** at `/franchise/agent/login`
  - Agent login/auth (JWT with type=franchise_agent)
  - KPI dashboard: clients referred, AUM referred, commission earned, active clients
  - Referred clients table with investment amounts and status
  - Commission history/transactions table
  - Commission tier display (e.g., Tier 40%)
- **New Backend Endpoints:**
  - `POST /api/franchise/auth/client/register` & `POST /api/franchise/auth/client/login`
  - `POST /api/franchise/auth/agent/register` & `POST /api/franchise/auth/agent/login`
  - `GET /api/franchise/dashboard/client/overview` (filtered by client JWT)
  - `GET /api/franchise/dashboard/agent/overview` (filtered by agent JWT)
- **New DB Collections:** `franchise_client_logins`, `franchise_agent_logins`

#### P1 Bug Fix: Blank Page / Session Loss (Mar 13, 2026)
- Added catch-all `*` route in React Router to prevent blank pages on unmatched URLs
- Added JWT token expiry validation in App.js auth check - clears stale tokens
- Enhanced `clearAuth()` to remove all auth-related localStorage keys
- Unmatched URLs now show login page instead of blank screen

### Other Completed Features (Dec 2025 - Mar 2026)
- Final Capital Allocation ($407K across trading accounts)
- Drawdown as Paramount Risk Metric (Hull-Style Risk Engine)
- Multi-Source Copy Trading, LUCRUM MT5 Account Integration
- AI Strategy Advisor (Claude Sonnet 4.5)
- Complete Trading Analytics & Live Demo Analytics dashboards
- Investment Committee Allocation Workflow
- Client Management, CRM, Referral System
- MT5 Auto-Healing & Bridge Monitoring

## Prioritized Backlog

### P1 (High Priority)
- Deploy MT5 Bridge API service to LUCRUM VPS
- Create backend regression tests

### P2 (Medium Priority)
- Fix bulk copy ratio API performance
- Fix Lucrum MT5 Bridge duplicate key errors
- Implement backend notification system for "Risk Alerts"
- Enable live data sync for VIKING CORE & PRO strategies

### P3 (Low Priority / Refactoring)
- Refactor `single_source_api.py` into domain-specific route files
- Break down `MoneyManagersDashboard.js` into smaller components
- Refactor `server.py` (29K+ lines) into modular structure

## Test Credentials
- **FIDUS Admin:** username=admin, password=Password123, user_type=admin
- **Franchise Admin:** email=admin@testco.com, password=FranchiseTest123
- **Franchise Client:** email=maria@example.com, password=ClientTest123
- **Franchise Agent:** email=carlos@example.com, password=AgentTest123
- **Test Company:** Test Franchise Co (code: testco, 60/40 commission split)
