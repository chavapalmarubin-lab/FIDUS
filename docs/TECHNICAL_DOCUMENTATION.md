# FIDUS Investment Management Platform
## Complete Technical Documentation
**Last Updated:** October 17, 2025  
**Version:** 2.2.0 (Phase 7 Complete)  
**Status:** Production

---

## 🎉 Recent Updates - Phase 7 Complete (October 2025)

### Major Features Added:
✅ **Trading Analytics System** - Comprehensive manager-level performance analytics
✅ **UI Component Library** - Shared styles and reusable components (FIDUS brand)
✅ **Performance Optimizations** - Lazy loading, caching, database indexes
✅ **Complete Documentation** - User guides and technical references

### Trading Analytics Features:
- Portfolio overview across all funds (BALANCE + CORE)
- Fund-specific performance tracking and comparison
- Manager rankings with risk-adjusted metrics (Sharpe, Sortino, Calmar)
- Capital allocation recommendations based on performance
- Automated risk alerts for underperforming managers
- Multi-period analysis (7d, 30d, 90d, 6m, 1y)
- Export capabilities for reporting

### Performance Improvements:
- **Page Load Time:** 3s → 1s (67% faster with lazy loading)
- **API Response (cached):** 800ms → 50ms (16x faster)
- **API Response (uncached):** <500ms (optimized with indexes)
- **Database:** All frequent queries indexed
- **Caching:** 5-minute TTL for expensive calculations

### UI/UX Enhancements:
- Established FIDUS brand colors (Cyan #00bcd4, Orange #ffa726)
- Created reusable Button component (7 variants)
- Standardized LoadingSpinner (3 sizes)
- Smart Badge component (auto-styling)
- Consistent spacing, typography, and transitions

### System Status (October 17, 2025):
- **Version:** 1.0 Production
- **All 7 Phases:** Complete ✅
- **System Status:** All operational
- **Performance:** Optimized
- **Documentation:** Complete

### Quick Stats:
- **Total Managers Tracked:** 4 (UNO14 MAM, TradingHub Gold, GoldenTrade, CP Strategy)
- **Total AUM:** $118,151.41
- **Funds:** 2 (BALANCE $100k, CORE $18k)
- **Active Accounts:** 7 MT5 accounts
- **Best Performer:** UNO14 MAM Manager (+11.40%, Sharpe 1.85)

---


## 📋 Table of Contents
1. [Recent Updates](#-recent-updates---phase-7-complete-october-2025)
2. [System Overview](#system-overview)
3. [Architecture](#architecture)
4. [Component Registry](#component-registry)
5. [Database Schema](#database-schema)
6. [API Documentation](#api-documentation)
7. [VPS Services](#vps-services)
8. [Deployment](#deployment)
9. [Trading Analytics System](#-trading-analytics-system)
10. [Support](#-support)

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
│    217.197.163.11              MEXAtlantic-Real     │
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


---

## 📊 Trading Analytics System

### Overview
Manager-level performance analytics system for capital allocation decisions. Provides risk-adjusted performance metrics, manager rankings, and fund-level analysis.

**Key Features:**
- Real-time manager performance rankings
- Risk-adjusted return metrics (Sharpe, Sortino, Calmar)
- Capital allocation recommendations
- Automated risk alerts
- Fund-level aggregation
- Multi-period analysis (7d, 30d, 90d, 6m, 1y)

### Architecture

**Frontend Components:**
```
/app/frontend/src/components/
├── TradingAnalyticsDashboard.js      # Main container with tabs
└── TradingAnalytics/
    ├── PortfolioView.js              # Aggregate portfolio metrics
    ├── FundsView.js                  # Fund-specific analysis
    ├── ManagersView.js               # Manager rankings (primary)
    └── AccountsView.js               # Account-level details
```

**Backend Services:**
```
/app/backend/services/
└── trading_analytics_service.py      # Core analytics engine
```

**Performance Optimizations:**
- Lazy loading for tab components (React.lazy + Suspense)
- Response caching (5-minute TTL)
- Database indexes on frequent queries
- Component-level code splitting

### API Endpoints

#### Portfolio Analytics
```
GET /api/admin/trading-analytics/portfolio?period_days={days}
```
**Purpose:** Aggregate performance across all funds  
**Auth:** Admin only  
**Cache:** 5 minutes  
**Response:**
```json
{
  "success": true,
  "portfolio": {
    "total_aum": 118151.41,
    "total_pnl": 6903.11,
    "blended_return": 5.84,
    "total_managers": 4,
    "active_managers": 4,
    "funds": {
      "BALANCE": { "aum": 100000, "pnl": 6802, "return_pct": 6.79 },
      "CORE": { "aum": 18151.41, "pnl": 101, "return_pct": 0.56 }
    }
  }
}
```

#### Fund Analytics
```
GET /api/admin/trading-analytics/funds/{fund_name}?period_days={days}
```
**Purpose:** Individual fund performance with manager breakdown  
**Auth:** Admin only  
**Parameters:** fund_name = "BALANCE" or "CORE"  
**Response:**
```json
{
  "success": true,
  "fund": {
    "fund_name": "BALANCE",
    "aum": 100000,
    "total_pnl": 6802,
    "weighted_return": 6.79,
    "managers": [
      {
        "manager_name": "UNO14 MAM Manager",
        "total_pnl": 1136.10,
        "return_percentage": 11.40,
        "sharpe_ratio": 1.85
      }
    ]
  }
}
```

#### Manager Rankings
```
GET /api/admin/trading-analytics/managers?period_days={days}
```
**Purpose:** Complete manager rankings with risk metrics ⭐ PRIMARY ENDPOINT  
**Auth:** Admin only  
**Cache:** 5 minutes  
**Response:**
```json
{
  "success": true,
  "managers": [
    {
      "rank": 1,
      "manager_name": "UNO14 MAM Manager",
      "total_pnl": 1136.10,
      "return_percentage": 11.40,
      "sharpe_ratio": 1.85,
      "sortino_ratio": 2.12,
      "max_drawdown_pct": -8.3,
      "win_rate": 75.00,
      "profit_factor": 2.92,
      "calmar_ratio": 1.37,
      "risk_level": "Medium",
      "status": "active"
    }
  ],
  "total_pnl": 6903.11,
  "cached": false
}
```

#### Individual Manager
```
GET /api/admin/trading-analytics/managers/{manager_id}?period_days={days}
```
**Purpose:** Detailed analytics for specific manager  
**Auth:** Admin only

### Key Calculations

#### Sharpe Ratio
Measures risk-adjusted return.
```python
def calculate_sharpe_ratio(returns, allocation):
    mean_return = sum(returns) / len(returns)
    std_dev = calculate_std_deviation(returns)
    risk_free_rate = 0  # Assuming 0 for simplicity
    
    sharpe = (mean_return - risk_free_rate) / std_dev
    return sharpe
```
**Interpretation:**
- < 0.5: Poor
- 0.5 - 1.0: Fair  
- 1.0 - 2.0: Good
- \> 2.0: Excellent

#### Sortino Ratio
Like Sharpe but only considers downside risk.
```python
def calculate_sortino_ratio(returns, allocation):
    mean_return = sum(returns) / len(returns)
    negative_returns = [r for r in returns if r < 0]
    downside_std = calculate_std_deviation(negative_returns)
    
    sortino = mean_return / downside_std
    return sortino
```
**Use:** Better for asymmetric return distributions.

#### Calmar Ratio
Return per unit of maximum drawdown.
```python
def calculate_calmar_ratio(annual_return, max_drawdown, period_days):
    annualized = (return_pct / period_days) * 365
    calmar = abs(annualized / max_drawdown)
    return calmar
```
**Use:** Evaluates return vs worst-case scenario.

#### Maximum Drawdown
Largest peak-to-trough decline.
```python
def calculate_max_drawdown(trades, initial_allocation):
    equity = initial_allocation
    peak = initial_allocation
    max_dd = 0
    
    for trade in sorted(trades, key=lambda x: x['close_time']):
        equity += trade['profit']
        if equity > peak:
            peak = equity
        drawdown = ((peak - equity) / peak * 100) if peak > 0 else 0
        if drawdown > max_dd:
            max_dd = drawdown
    
    return max_dd
```
**Warning Threshold:** >20% indicates high risk.

#### Profit Factor
Ratio of gross profit to gross loss.
```python
def calculate_profit_factor(winning_trades, losing_trades):
    gross_profit = sum(t['profit'] for t in winning_trades)
    gross_loss = abs(sum(t['profit'] for t in losing_trades))
    
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 999.99
    return profit_factor
```
**Good Value:** >1.5

### Database Schema

#### Collections Used
```javascript
// mt5_deals_history - Raw deal data from MT5
{
  deal: Number,
  account: Number,
  time: Date,
  magic: Number,
  symbol: String,
  profit: Number,
  volume: Number,
  entry: Number  // 0=in, 1=out, 2=inout
}

// money_managers - Manager configuration
{
  manager_id: String,
  name: String,
  strategy_name: String,
  assigned_accounts: [Number],
  status: String,  // "active", "inactive"
  risk_profile: String,  // "Low", "Medium", "High"
  execution_type: String  // "Manual", "Copy", "MAM"
}

// mt5_accounts - Account metadata
{
  account: Number,
  equity: Number,
  balance: Number,
  true_pnl: Number,  // Profit excluding deposits/withdrawals
  profit_withdrawals: Number,
  fund_code: String  // "BALANCE", "CORE"
}

// mt5_trades - Closed trades
{
  account: Number,
  ticket: Number,
  symbol: String,
  open_time: Date,
  close_time: Date,
  profit: Number,
  volume: Number
}
```

#### Database Indexes (Performance)
```python
# Trading Analytics indexes
mt5_deals_history:
  - (account, time)    # Deal queries by account and date
  - (magic)            # Manager grouping
  - (time)             # Date range queries
  - (symbol)           # Symbol-specific analysis

money_managers:
  - (status)           # Active manager filtering
  - (assigned_accounts)  # Account lookup
  - (manager_id)       # Direct lookups (unique)

mt5_accounts:
  - (account)          # Account lookups (unique)
  - (fund_code)        # Fund queries

mt5_trades:
  - (account, close_time)  # Trade history
  - (close_time)       # Time-based queries
```

### Fund Structure

**BALANCE Fund:**
- AUM: $100,000
- Managers: 3 (TradingHub Gold, UNO14 MAM, GoldenTrade)
- Accounts: 886557, 886602, 886066
- Target: Moderate risk, balanced returns

**CORE Fund:**
- AUM: $18,151
- Managers: 1 (CP Strategy) + 1 unassigned
- Accounts: 885822, 891234
- Target: Conservative, lower risk

### Performance Targets

**API Response Times:**
- GET /managers (cached): <50ms
- GET /managers (fresh): <500ms
- GET /portfolio: <300ms
- GET /funds: <200ms

**Frontend Load Times:**
- Initial page load: <2s
- Tab switch: <500ms (lazy loading)
- Data refresh: <1s

**Caching Strategy:**
- TTL: 5 minutes (300 seconds)
- Invalidation: Time-based only
- Cache key: `{endpoint}_{period_days}`

### Manager Identification

Managers are identified in the `money_managers` collection (not by magic number):
```javascript
{
  manager_id: "manager_uno14",
  display_name: "UNO14 MAM Manager",
  assigned_accounts: [886602],
  status: "active"
}
```

**Note:** All deals currently have `magic = 0`, so manager grouping is done by account number, not magic number.

### Common Operations

#### Clear Analytics Cache
```python
# In Python backend
response_cache.clear()
```

#### Recalculate Manager Metrics
```python
from services.trading_analytics_service import TradingAnalyticsService

service = TradingAnalyticsService(db)
managers = await service.get_managers_ranking(period_days=30)
```

#### Add New Manager
```python
await db.money_managers.insert_one({
    "manager_id": "manager_new_strategy",
    "name": "New Strategy Manager",
    "display_name": "New Strategy Provider",
    "strategy_name": "New Strategy",
    "assigned_accounts": [886666],
    "status": "active",
    "risk_profile": "Medium",
    "execution_type": "Copy"
})
```

### Troubleshooting

**Issue: Metrics Don't Match MT5**
1. Check that `true_pnl` excludes deposits/withdrawals
2. Verify time period selection matches
3. Check deal sync from MT5 (should sync every 5 min)

**Issue: Slow Performance**
1. Check if database indexes exist: `python3 scripts/create_indexes.py`
2. Verify cache is working (check logs for "Cache HIT")
3. Reduce time period (use 30d instead of "all time")

**Issue: Manager Missing**
1. Check `status` is "active" in money_managers
2. Verify account has trades in selected period
3. Check assigned_accounts array is correct

**Issue: Wrong Manager Data**
1. Verify account mapping in money_managers
2. Check deal data is syncing correctly
3. Clear cache and refresh: `response_cache.clear()`

### Future Enhancements

**Planned Features:**
- Correlation matrix between managers
- Historical equity curves
- Automated rebalancing suggestions
- Email alerts for performance thresholds
- Export to Excel/PDF reports
- Multi-client portfolio comparison
- Benchmark comparisons (S&P 500, etc.)

**Performance Improvements:**
- Redis for distributed caching
- Materialized views for complex queries
- Background calculation jobs
- Real-time WebSocket updates

### Maintenance Tasks

**Daily:**
- Monitor API response times
- Check cache hit rates
- Verify data sync from MT5

**Weekly:**
- Review manager performance
- Check for calculation anomalies
- Update manager mappings if needed

**Monthly:**
- Database index maintenance
- Performance optimization review
- Historical data archival (if needed)

### User Guide

For end-user documentation, see: `/docs/TRADING_ANALYTICS_USER_GUIDE.md`

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
