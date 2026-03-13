# FIDUS Investment Platform - Product Requirements Document

## Original Problem Statement
Build a comprehensive FIDUS investment platform with VIKING trading analytics, MT5 integration, and White Label Franchise System for third-party companies.

## Core Architecture
- **Frontend:** React + Tailwind CSS + Shadcn/UI
- **Backend:** FastAPI + Python
- **Database:** MongoDB Atlas (fidus_production)
- **Deployment:** Render (prod), Emergent (preview)

## White Label Franchise System (Complete)

### Phase 1 - Admin Management (Mar 12, 2026)
- `franchise_companies` collection + CRUD API
- White Label tab in FIDUS Admin Dashboard

### Phase 2 - Franchise Admin Portal (Mar 13, 2026)
- JWT auth at `/api/franchise/auth/`
- 9-tab portal at `/franchise/login` (Overview, Portfolio, Cash Flow, Instruments, Risk, Gap Analysis, Clients, Referrals, Commissions)

### Phase 3 - Client & Agent Portals (Mar 13, 2026)
- **Client Portal** `/franchise/client/login` — investment overview, returns, contract timeline
- **Agent Portal** `/franchise/agent/login` — referred clients, AUM, commissions, tier display

### Phase 4 - Self-Service Onboarding + CSV (Mar 13, 2026)
- **Add Client modal** with referral agent dropdown, auto-generates `Fidus2026!` password
- **Add Agent modal** with commission tier (30/40/50%), auto-generates `Fidus2026!` password
- **CSV download** on all data tabs (Clients, Agents, Commissions, Instruments)
- Created client/agent can immediately login to their respective portals
- Backend: `POST /api/franchise/dashboard/onboard-client` and `POST /api/franchise/dashboard/onboard-agent`

### P1 Bug Fix - Blank Page (Mar 13, 2026)
- Catch-all `*` route prevents blank pages on unmatched URLs
- JWT expiry validation clears stale tokens gracefully

## Prioritized Backlog

### P1
- Deploy MT5 Bridge API to LUCRUM VPS
- Create backend regression tests

### P2
- Bulk copy ratio API performance fix
- Lucrum MT5 Bridge duplicate key errors
- Risk Alerts notification system
- VIKING CORE & PRO live data sync

### P3 (Refactoring)
- Split `single_source_api.py`, `server.py` (29K+ lines)
- Break down `MoneyManagersDashboard.js`

## Test Credentials
| Portal | Email/Username | Password |
|--------|---------------|----------|
| FIDUS Admin | admin | Password123 |
| Franchise Admin | admin@testco.com | FranchiseTest123 |
| Franchise Client | maria@example.com | ClientTest123 |
| Franchise Agent | carlos@example.com | AgentTest123 |
| New onboarded users | (their email) | Fidus2026! |

## Key Files
- `/app/backend/routes/franchise_auth.py` - All franchise auth (admin/client/agent)
- `/app/backend/routes/franchise_dashboard.py` - Dashboard + onboarding endpoints
- `/app/backend/routes/franchise_api.py` - Company CRUD
- `/app/frontend/src/components/FranchisePortal.js` - Admin portal (9 tabs + modals + CSV)
- `/app/frontend/src/components/FranchiseClientPortal.js` - Client portal
- `/app/frontend/src/components/FranchiseAgentPortal.js` - Agent portal
- `/app/frontend/src/components/FranchiseLogin.js` - Admin login
