# FIDUS Investment Platform - Product Requirements Document

## Original Problem Statement
Build a comprehensive FIDUS investment platform with VIKING trading analytics, MT5 integration, and White Label Franchise System for third-party companies.

## Core Architecture
- **Frontend:** React + Tailwind CSS + Shadcn/UI
- **Backend:** FastAPI + Python
- **Database:** MongoDB Atlas (fidus_production)

## White Label Franchise System (Complete)

### Phase 1-4 Summary
- Phase 1: Admin Management + White Label tab in FIDUS
- Phase 2: Franchise Admin Portal (9 tabs) at `/franchise/login`
- Phase 3: Client Portal (`/franchise/client/login`) + Agent Portal (`/franchise/agent/login`)
- Phase 4: Self-service onboarding (Add Client/Agent), CSV downloads, Bulk CSV Import

### Cash Flow Upgrade (Mar 13, 2026)
- Rebuilt Cash Flow tab to match FIDUS main dashboard quality
- Cash Flow Obligations Calendar with status bar (AUM, Returns, Obligations, Net Position)
- Key Milestones (Next Payment, First Large Payment, Contract End with dates + amounts + days)
- Capital & Revenue Calculation (AUM - Obligations = Net Position, Monthly Revenue Breakdown)
- Monthly Obligations Timeline with per-client breakdowns, referral commissions, running balance
- Export to CSV

### Simulator
- Interactive revenue simulator at `/franchise/simulator` (public, no login)
- AUM slider, client return rate slider (0.5%-2.0%), commission split slider
- MXN/USD toggle with live exchange rate

## Test Credentials
| Portal | Email/Username | Password |
|--------|---------------|----------|
| FIDUS Admin | admin | Password123 |
| Franchise Admin | admin@testco.com | FranchiseTest123 |
| Franchise Client | maria@example.com | ClientTest123 |
| Franchise Agent | carlos@example.com | AgentTest123 |

## Prioritized Backlog
### P1: Deploy MT5 Bridge API to LUCRUM VPS, Backend regression tests
### P2: Bulk copy ratio API perf, Lucrum duplicate keys, Risk Alerts
### P3: Refactor server.py (29K+ lines), single_source_api.py
