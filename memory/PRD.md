# FIDUS Investment Platform - Product Requirements Document

## Three-Layer Risk Architecture (Post-Incident March 2026)

### Layer 1 — Social Trading Platform (PRIMARY enforcement)
### Layer 2 — FIDUS Platform (MONITORING & ALERTING) ← This system
### Layer 3 — LUCRUM Broker (Last resort)

## Layer 2 Implementation — ALL ITEMS COMPLETE

| Item | Description | Status |
|------|-------------|--------|
| A | Alert rules on 5-min polling (3% warn / 5% critical) | COMPLETE |
| B | Alert delivery service (SMTP email, MongoDB alerts) | COMPLETE |
| C | Equity snapshots (every 5 min, 90-day retention) | COMPLETE |
| D | Exposure aggregation engine | COMPLETE |
| E | Dashboard: Risk Alerts tab + drawdown bars on MM cards | COMPLETE |
| F | Social trading monitor tracking per account | COMPLETE |
| G | Risk score auto-computation (100pt scale) | COMPLETE |
| H | Data health endpoint per account | COMPLETE |

## Key Files
- `/app/backend/services/risk_monitoring_service.py` — Core monitoring service
- `/app/backend/routes/risk_monitoring.py` — All risk API endpoints
- `/app/frontend/src/components/RiskAlertsDashboard.js` — Risk Alerts tab
- `/app/docs/incident_march_2026/` — All incident documents (7 files)

## API Endpoints (Layer 2)
- `GET /api/admin/risk/status` — Portfolio + per-account risk status
- `GET /api/admin/risk/alerts` — Alert list with lifecycle
- `GET /api/admin/risk/alerts/unresolved-count` — Badge count
- `POST /api/admin/risk/alerts/{id}/resolve` — Resolve alert
- `GET /api/admin/risk/snapshots/{id}` — Equity history
- `GET /api/admin/risk/exposure` — Instrument concentration
- `GET /api/admin/risk/data-health/{id}` — Sync status
- `GET /api/admin/risk/risk-scores` — Computed risk scores
- `GET /api/admin/risk/social-monitors` — Monitor config status
- `POST /api/admin/risk/social-monitors/{id}` — Add monitor config
- `POST /api/admin/risk/test-alert` — Test SMTP delivery

## Test Credentials
| Portal | Email/Username | Password |
|--------|---------------|----------|
| FIDUS Admin | admin | Password123 |
