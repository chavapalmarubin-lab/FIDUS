# FIDUS Investment Management Platform
## Complete Technical Documentation
**Last Updated:** October 13, 2025  
**Version:** 2.1.0  
**Status:** Production

---

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Component Registry](#component-registry)
4. [Database Schema](#database-schema)
5. [API Documentation](#api-documentation)
6. [VPS Services](#vps-services)
7. [Deployment](#deployment)
8. [Recent Updates](#recent-updates)

---

## 🏗️ System Overview

### Platform Purpose
FIDUS is a comprehensive hedge fund management platform providing:
- Multi-fund portfolio management (CORE, BALANCE, DYNAMIC)
- Real-time MT5 trading integration
- Client relationship management (CRM)
- KYC/AML compliance processing
- Investment committee dashboard
- Performance analytics and reporting

### Technology Stack
- **Frontend:** React 19.0+, Tailwind CSS, Vite
- **Backend:** Python 3.11+, FastAPI, Pydantic
- **Database:** MongoDB Atlas (fidus_production)
- **Trading:** MetaTrader 5 (MEXAtlantic broker)
- **Infrastructure:** Emergent.host (frontend), Render.com (backend), Windows VPS (trading services)

---

## 🔧 Architecture

### System Architecture Diagram
```
┌─────────────────────────────────────────────────────┐
│                   FIDUS Platform                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [Users/Clients]                                    │
│         ↓                                            │
│  [Frontend - React]                                 │
│    fidus-invest.emergent.host                       │
│         ↓ HTTPS/REST API                            │
│  [Backend - FastAPI]                                │
│    fidus-api.onrender.com                           │
│         ↓ MongoDB Driver                            │
│  [MongoDB Atlas]                                    │
│    fidus_production                                 │
│         ↑                                            │
│         │ Sync every 5 min                          │
│  [VPS MT5 Bridge Service] ←→ [MT5 Terminal]       │
│    92.118.45.135 (NEW)         MEXAtlantic-Real     │
│                                                      │
│  [Integrations]                                     │
│    - Google Workspace (Gmail, Calendar, Drive)     │
│    - Email SMTP (smtp.gmail.com:587)               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Data Flow
1. **Trading Data:**
   - MT5 accounts trade on MEXAtlantic broker
   - VPS Bridge Service syncs data every 5 minutes
   - Data stored in MongoDB Atlas
   - Backend API serves cached data to frontend

2. **User Data:**
   - Frontend captures user input
   - Backend validates and processes
   - MongoDB stores persistent data
   - Real-time updates via REST API

---

## 📦 Component Registry

### 1. Frontend Application
- **URL:** https://fidus-invest.emergent.host
- **Platform:** Emergent.host Kubernetes
- **Tech:** React 19.0+, Tailwind CSS, Vite
- **Dashboard:** https://app.emergent.host
- **Deployment:** Automatic on push to main
- **Status:** ✅ Online

### 2. Backend API
- **URL:** https://fidus-api.onrender.com
- **Platform:** Render.com
- **Tech:** Python 3.11+, FastAPI, Uvicorn
- **Dashboard:** https://dashboard.render.com
- **Deployment:** Automatic on push to main
- **Status:** ✅ Online

### 3. MongoDB Atlas
- **Database:** fidus_production
- **Collections:**
  - users (user accounts)
  - prospects (CRM leads)
  - investments (client investments)
  - mt5_accounts (trading account data)
  - mt5_accounts_cache (backend cache)
  - sessions (user sessions)
  - documents (uploaded files)
- **Status:** ✅ Online

### 4. VPS Services
- **IP:** 217.197.163.11
- **OS:** Windows Server 2022
- **Services:**
  - MT5 Bridge Service (Python, Task Scheduler)
  - MT5 Terminal (terminal64.exe)
- **Status:** ✅ Online

### 5. MT5 Trading System
- **Broker:** MEXAtlantic
- **Server:** MEXAtlantic-Real
- **Accounts:**
  - 886557 (Main Balance) - $100,000
  - 886066 (Secondary Balance) - $210,000
  - 886602 (Tertiary Balance)
  - 885822 (Core Account) - $128,151
  - 886528 (Separation Account) - $6,590
- **Sync Frequency:** Every 5 minutes
- **Status:** ✅ Syncing

---

## 💾 Database Schema

### mt5_accounts Collection
```javascript
{
  _id: ObjectId,
  account: Number (unique, indexed),
  name: String,
  server: String,
  balance: Number,         // Initial deposit
  equity: Number,          // Current value including P&L
  margin: Number,
  free_margin: Number,
  profit: Number,          // Floating P&L
  fund_type: String,       // "BALANCE", "CORE", "SEPARATION"
  updated_at: DateTime
}
```

### users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique, indexed),
  password_hash: String,
  role: String,            // "admin", "user", "client"
  created_at: DateTime,
  updated_at: DateTime
}
```

---

## 🔌 API Documentation

### Base URL
```
Production: https://fidus-api.onrender.com
```

### MT5 Endpoints

#### GET /api/mt5/accounts
**Description:** Get all MT5 account data

**Response:**
```javascript
{
  "success": true,
  "accounts": [
    {
      "account": 886557,
      "name": "Main Balance Account",
      "balance": 100000.00,
      "equity": 100264.87,
      "profit": 264.87,
      "fund_type": "BALANCE"
    }
  ]
}
```

### System Endpoints

#### GET /api/system/status
**Description:** Overall system health check

**Response:**
```javascript
{
  "status": "healthy",
  "components": {
    "frontend": "online",
    "backend": "online",
    "database": "online",
    "vps": "online",
    "mt5_bridge": "online"
  }
}
```

---

## 🖥️ VPS Services

### MT5 Bridge Service

#### Configuration
- **Script:** `C:\mt5_bridge_service\mt5_bridge_service_production.py`
- **Scheduler:** Windows Task Scheduler
- **Frequency:** Every 300 seconds (5 minutes)
- **Logs:** `C:\mt5_bridge_service\logs/`

#### What It Does
```
Every 5 minutes:
1. Connects to MT5 Terminal
2. Logs into each account
3. Retrieves account.equity
4. Stores to MongoDB
5. Creates log entry
```

---

## 🚀 Deployment

### Frontend (Emergent.host)
```bash
git push origin main
# Automatic deployment triggered
```

### Backend (Render.com)
```bash
git push origin main
# Automatic deployment triggered
```

### VPS Services
```bash
# Manual deployment
# RDP into VPS and restart service
```

---

## 📝 Recent Updates

### October 13, 2025

#### ✅ VPS MT5 Bridge - 5 Minute Sync
- Changed sync interval from 15 to 5 minutes
- All 5 accounts syncing successfully
- Data now updates every 5 minutes

#### ✅ Cash Flow Label Correction
- Changed "Broker Interest" to "Last Profits Moved to Separation Balance"
- More accurate financial reporting

---

## 🔐 Security

- ✅ All API endpoints use HTTPS
- ✅ JWT tokens for authentication
- ✅ MongoDB connection uses TLS/SSL
- ✅ VPS accessible only via RDP
- ✅ Sensitive data encrypted at rest

---

## 📞 Support

### Emergency Procedures
1. **Frontend Down:** Check Emergent.host dashboard
2. **Backend Down:** Check Render.com dashboard
3. **MongoDB Issues:** Check MongoDB Atlas console
4. **VPS/MT5 Issues:** RDP into VPS

---

**Document Version:** 2.1.0  
**Last Updated:** October 13, 2025
