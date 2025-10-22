# FIDUS Infrastructure Overview

**Last Updated:** October 21, 2025  
**Status:** ✅ Production - Post VPS Migration

---

## 🏗️ Current Production Setup

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FIDUS PLATFORM                            │
│                                                               │
│  Frontend (React) ──→ Backend (FastAPI) ──→ MT5 Bridge      │
│        ↓                     ↓                    ↓          │
│   Render.com          Render.com            Windows VPS      │
│                            ↓                                  │
│                      MongoDB Atlas                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 Production Endpoints

### Frontend Application
- **Platform:** Render.com
- **URL:** https://fidus-investment-platform.onrender.com
- **Framework:** React.js
- **Auto-Deploy:** GitHub main branch

### Backend API
- **Platform:** Render.com
- **URL:** https://fidus-api.onrender.com
- **Framework:** Python FastAPI
- **Auto-Deploy:** GitHub main branch
- **Health Check:** https://fidus-api.onrender.com/health

### MT5 Bridge Service (NEW VPS)
- **Provider:** ForexVPS
- **IP Address:** 92.118.45.135
- **Port:** 8000
- **SSH Port:** 42014
- **URL:** http://92.118.45.135:8000
- **Health Endpoint:** http://92.118.45.135:8000/api/mt5/bridge/health
- **Services Running:**
  - MT5 Terminal (7 accounts)
  - MT5 Bridge API (Python FastAPI)
  - Auto-start via Windows Task Scheduler
  - MT5 Watchdog (Auto-Healing System)

---

## 🗄️ Database

### MongoDB Atlas
- **Provider:** MongoDB Atlas
- **Cluster:** fidus.y1p9be2.mongodb.net
- **Database:** fidus_production
- **Connection:** Secured with IP whitelist
- **Collections:**
  - `mt5_accounts` - MT5 account configurations
  - `mt5_deals_history` - Trading history
  - `clients` - Client information
  - `investments` - Investment records
  - `users` - User accounts
  - `mt5_watchdog_status` - Watchdog health monitoring

---

## 📊 MT5 Accounts (7 Total)

### Account Details
- **Broker:** MEXAtlantic-Real
- **Server:** MEXAtlantic-Real
- **Accounts:**
  - 886557 (BALANCE Fund - Main)
  - 886066 (BALANCE Fund - Secondary)
  - 886602 (BALANCE Fund - Tertiary)
  - 885822 (CORE Fund - Main)
  - 886528 (SEPARATION Account)
  - 891215 (SEPARATION - Interest Earnings)
  - 891234 (CORE Fund - Secondary)

### Sync Configuration
- **Sync Interval:** Every 5 minutes
- **Auto-Login:** Enabled (PowerShell script)
- **Password:** Encrypted in environment variables
- **Data Flow:** MT5 → Bridge API → MongoDB → Backend API → Frontend

---

## 🔒 Security & Access

### VPS Access
- **RDP:** 92.118.45.135:42014
- **Username:** trader
- **Authentication:** Password-protected
- **Firewall:** ForexVPS managed

### API Security
- **Backend:** JWT token authentication
- **MT5 Bridge:** API key authentication
- **MongoDB:** Username/password + IP whitelist
- **GitHub:** Personal Access Token for workflows

---

## 🔄 Auto-Healing System

### MT5 Watchdog
- **Status:** ✅ Active and Monitoring
- **Check Interval:** Every 60 seconds
- **Failure Threshold:** 3 consecutive failures
- **Auto-Healing:** Via GitHub Actions workflow
- **Alerting:** Email notifications on critical failures

### Monitoring Checks
1. **Bridge API Availability** - Is MT5 Bridge responding?
2. **Data Freshness** - Last MongoDB update < 15 minutes?
3. **Account Sync** - At least 50% of accounts syncing?

### Auto-Healing Process
1. Watchdog detects 3 consecutive failures
2. Triggers GitHub Actions workflow
3. Workflow SSHs to VPS and restarts MT5 Bridge
4. Verifies service health after restart
5. Sends email notification (success or failure)

---

## 📈 Monitoring & Alerts

### Email Alerts
- **SMTP Provider:** Gmail
- **Sender:** chavapalmarubin@gmail.com
- **Recipient:** chavapalmarubin@gmail.com
- **Alert Types:**
  - 🚨 **CRITICAL** - Auto-healing failed, manual intervention required
  - ⚠️ **WARNING** - Service degraded but operational
  - ✅ **INFO** - Auto-recovery successful

### Watchdog API Endpoints
- `GET /api/system/mt5-watchdog/status` - Current watchdog status
- `POST /api/system/mt5-watchdog/force-sync` - Manual sync trigger
- `POST /api/system/mt5-watchdog/force-healing` - Manual healing trigger

---

## 🔧 Deployment & CI/CD

### GitHub Actions Workflows
- **Backend Deploy:** Automatic on push to main
- **Frontend Deploy:** Automatic on push to main
- **Emergency MT5 Restart:** Manual or auto-triggered by watchdog
- **Repository:** chavapalmarubin-lab/FIDUS

### Environment Variables
**Backend (.env):**
- `MONGO_URL` - MongoDB connection string
- `MT5_BRIDGE_URL` - NEW VPS MT5 Bridge endpoint
- `GITHUB_TOKEN` - For auto-healing workflows
- `SMTP_USERNAME` / `SMTP_APP_PASSWORD` - Email alerts
- `JWT_SECRET_KEY` - Authentication
- `FRONTEND_URL` - Frontend base URL

**VPS (Windows Environment):**
- `MT5_MASTER_PASSWORD` - MT5 terminal password
- `MONGO_URL` - MongoDB connection

---

## 📚 Related Documentation

- [Troubleshooting Guide](./troubleshooting.md)
- [VPS Migration History](./vps-migration-oct-2025.md)
- [MT5 Auto-Healing Documentation](./mt5-auto-healing.md)
- [API Documentation](./api-documentation.md)

---

## ⚠️ Important Notes

### Old VPS (DEPRECATED)
- **IP:** 217.197.163.11
- **Status:** ❌ Shut down and decommissioned
- **DO NOT USE** for any new configurations

### Migration Date
- **Completed:** October 21, 2025
- **Reason:** Old VPS had hidden service conflicts causing 404 errors
- **Downtime:** ~6 hours
- **Success:** All services migrated successfully

---

**For technical support or issues, contact:** chavapalmarubin@gmail.com
