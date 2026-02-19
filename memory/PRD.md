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

### P1
- [ ] Fix root cause in agent creation script to properly hash passwords
- [ ] Fix login for other affected referral agents

### P2
- [ ] Enable live data sync for VIKING CORE & PRO strategies
- [ ] Verify pagination on VIKING "Orders" tab with large datasets
- [ ] Refactor VikingDashboard.js into smaller components
- [ ] Address Lucrum MT5 Bridge duplicate key errors

## Key Files Reference
- `/app/backend/server.py` - Main backend with login endpoint
- `/app/backend/routes/referrals.py` - Agent portal routes
- `/app/backend/services/calculations.py` - Financial calculations
- `/app/.github/workflows/sync-lucrum-accounts-to-mongodb.yml` - Data sync workflow
