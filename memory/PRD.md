# FIDUS Investment Platform - Product Requirements Document

## Architecture: Three-Layer Risk Control

### Layer 1 — Social Trading Platform (PRIMARY enforcement)
- Equity monitors on the social trading platform
- Can disable copiers, close trades, send alerts
- Configured per account by FIDUS admin

### Layer 2 — FIDUS Platform (MONITORING & ALERTING)
- Render API + MongoDB + React dashboard
- DETECT → ALERT → LOG only. No trade execution.
- 5-minute equity polling with alert rules
- Email alerts on drawdown breaches

### Layer 3 — LUCRUM Broker (Last resort)
- Broker-level equity protection / stop-out
- Break switch at broker level

## Layer 2 Implementation Status (March 2026)

### Items A+B+C — Alert Rules + Service + Snapshots [COMPLETE]
- Risk monitoring service runs after every VPS sync (5 min)
- Per-account drawdown check: 3% WARNING, 5% CRITICAL (configurable per account)
- Portfolio-level drawdown check: 5% WARNING, 10% CRITICAL
- Email alerts via SMTP with deduplication (60 min window)
- Equity snapshots stored every 5 min (90-day retention)
- Alert status set on mt5_accounts: OK / WARNING / CRITICAL
- Files: `/app/backend/services/risk_monitoring_service.py`, `/app/backend/routes/risk_monitoring.py`

### API Endpoints
- `GET /api/admin/risk/status` — Current risk status for all accounts + portfolio
- `GET /api/admin/risk/alerts?status=unresolved` — Alert list with lifecycle
- `GET /api/admin/risk/alerts/unresolved-count` — Badge count (poll 30s)
- `POST /api/admin/risk/alerts/{id}/resolve` — Mark alert resolved
- `GET /api/admin/risk/snapshots/{account_id}?hours=24` — Equity history
- `GET /api/admin/risk/exposure` — Cross-account instrument concentration
- `GET /api/admin/risk/data-health/{account_id}` — Sync health status
- `POST /api/admin/risk/test-alert` — Test email delivery

### Remaining Layer 2 Items
- Item D: Exposure aggregation dashboard view (backend done, frontend pending)
- Item E: Dashboard alert panel + risk status on Money Manager cards (frontend)
- Item F: Social trading monitor tracking per account (backend + frontend)
- Item G: Risk score auto-computation daily (backend)

## Incident Archive
All documents at `/app/docs/incident_march_2026/`

## Test Credentials
| Portal | Email/Username | Password |
|--------|---------------|----------|
| FIDUS Admin | admin | Password123 |
| Franchise Admin | admin@testco.com | FranchiseTest123 |
