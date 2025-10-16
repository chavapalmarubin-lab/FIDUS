# FIDUS PLATFORM - FIELD STANDARDIZATION AUDIT
**Date:** October 16, 2025  
**Status:** IN PROGRESS  
**Agent:** Emergent AI Engineer  

## 🎯 EXECUTIVE SUMMARY

This audit documents field naming inconsistencies across the FIDUS platform that led to the October 16, 2025 refactoring disaster. The goal is to establish a single, standardized naming convention for all data fields across:
- MongoDB database collections
- Backend API responses
- Frontend component variables

---

## SECTION 1: MongoDB Collections

### Collection: `mt5_accounts`

**Purpose:** Stores MetaTrader 5 account data synchronized from VPS bridge

| Field Name | Type | Example Value | Notes |
|------------|------|---------------|-------|
| `account` | int | `886557` | Account number (PRIMARY KEY) |
| `balance` | float | `80000.00` | Account balance |
| `equity` | float | `79538.56` | Current equity |
| `profit` | float | `-461.44` | Floating P&L |
| `margin` | float | `0.00` | Used margin |
| `margin_free` | float | `79538.56` | Free margin |
| `leverage` | int | `500` | Leverage ratio |
| `fund_type` | string | `"BALANCE"` | CORE/BALANCE/DYNAMIC |
| `currency` | string | `"USD"` | Account currency |
| `server` | string | `"MEXAtlantic-Real"` | MT5 server |
| `company` | string | `"FD UNO14 GLOBAL"` | Broker name |
| `updated_at` | datetime | `2025-10-16...` | Last sync time |
| `name` | string | `"Main Balance"` | Account friendly name |
| `target_amount` | float | `100000.00` | Target balance |
| `is_active` | boolean | `true` | Active status |

**Database Location:** MongoDB collection `mt5_accounts`

---

### Collection: `investments`

**Purpose:** Stores client investment records

| Field Name | Type | Example Value | Notes |
|------------|------|---------------|-------|
| `investment_id` | string | `"inv_abc123"` | Investment ID (PRIMARY KEY) |
| `client_id` | string | `"client_003"` | Client reference |
| `fund_code` | string | `"BALANCE"` | Fund type |
| `principal_amount` | Decimal | `50000.00` | Initial investment |
| `current_value` | Decimal | `52500.00` | Current value |
| `profit_loss` | Decimal | `2500.00` | Calculated P&L |
| `profit_loss_percentage` | Decimal | `5.00` | P&L percentage |
| `currency` | string | `"USD"` | Currency |
| `status` | string | `"active"` | Investment status |
| `investment_date` | datetime | `2025-01-15...` | Start date |
| `mt5_account_id` | string | `"mt5_886557"` | Linked MT5 account |
| `created_at` | datetime | `2025-01-15...` | Record creation |
| `updated_at` | datetime | `2025-10-16...` | Last update |

**Database Location:** MongoDB collection `investments`

---

### Collection: `clients` (users)

**Purpose:** Stores client/user information

| Field Name | Type | Example Value | Notes |
|------------|------|---------------|-------|
| `id` | string | `"client_003"` | User ID (PRIMARY KEY) |
| `username` | string | `"chava"` | Login username |
| `name` | string | `"SALVADOR PALMA"` | Full name |
| `email` | string | `"chava@..."` | Email address |
| `phone` | string | `"+1-555-..."` | Phone number |
| `type` | string | `"client"` | User type |
| `status` | string | `"active"` | Account status |
| `profile_picture` | string | `"https://..."` | Avatar URL |
| `created_at` | datetime | `2025-01-01...` | Account creation |
| `notes` | string | `"VIP client"` | Admin notes |

**Database Location:** MongoDB collection `users` (stores both clients and admins)

---

### Collection: `mt5_deals_history`

**Purpose:** Stores historical MT5 trading deals from VPS bridge

| Field Name | Type | Example Value | Notes |
|------------|------|---------------|-------|
| `account` | int | `886557` | MT5 account number |
| `ticket` | int | `123456789` | Deal ticket |
| `order` | int | `123456788` | Order ticket |
| `position` | int | `123456700` | Position ID |
| `symbol` | string | `"EURUSD"` | Trading pair |
| `type` | int | `0` | Deal type (0=buy, 1=sell) |
| `entry` | int | `0` | Entry type |
| `volume` | float | `0.01` | Lot size |
| `price` | float | `1.0850` | Execution price |
| `profit` | float | `15.00` | Deal profit |
| `commission` | float | `-0.50` | Commission charged |
| `swap` | float | `0.00` | Swap/rollover |
| `magic` | int | `123456` | Magic number (strategy ID) |
| `time` | datetime | `2025-10-16...` | Execution time |
| `comment` | string | `"Trade #1"` | Deal comment |

**Database Location:** MongoDB collection `mt5_deals_history`

---

## SECTION 2: Backend API Endpoints

### Endpoint: `GET /api/mt5/accounts`

**Purpose:** Returns all MT5 accounts with current data

**Response Structure:**
```json
{
  "success": true,
  "accounts": [
    {
      "account": 886557,              // FROM: db.account
      "balance": 80000.00,            // FROM: db.balance
      "equity": 79538.56,             // FROM: db.equity
      "profit": -461.44,              // FROM: db.profit
      "margin": 0.00,                 // FROM: db.margin
      "margin_free": 79538.56,        // FROM: db.margin_free
      "leverage": 500,                // FROM: db.leverage
      "fund_type": "BALANCE",         // FROM: db.fund_type
      "currency": "USD",              // FROM: db.currency
      "server": "MEXAtlantic-Real",   // FROM: db.server
      "company": "FD UNO14 GLOBAL",   // FROM: db.company
      "updated_at": "2025-10-16...",  // FROM: db.updated_at
      "name": "Main Balance",         // FROM: db.name
      "target_amount": 100000.00,     // FROM: db.target_amount
      "is_active": true               // FROM: db.is_active
    }
  ],
  "count": 7
}
```

**Field Transformations:**
- ✅ NO transformations - returns fields with same names as database
- ⚠️ **INCONSISTENCY:** Frontend sometimes expects `accountNumber` but API returns `account`

---

### Endpoint: `GET /api/investments`

**Purpose:** Returns all investments for a client

**Response Structure:**
```json
{
  "success": true,
  "investments": [
    {
      "investment_id": "inv_abc123",        // FROM: db.investment_id
      "client_id": "client_003",            // FROM: db.client_id
      "fund_code": "BALANCE",               // FROM: db.fund_code
      "principal_amount": 50000.00,         // FROM: db.principal_amount
      "current_value": 52500.00,            // FROM: db.current_value
      "profit_loss": 2500.00,               // FROM: db.profit_loss
      "profit_loss_percentage": 5.00,       // FROM: db.profit_loss_percentage
      "currency": "USD",                    // FROM: db.currency
      "status": "active",                   // FROM: db.status
      "investment_date": "2025-01-15...",   // FROM: db.investment_date
      "mt5_account_id": "mt5_886557",       // FROM: db.mt5_account_id
      "created_at": "2025-01-15...",        // FROM: db.created_at
      "updated_at": "2025-10-16..."         // FROM: db.updated_at
    }
  ]
}
```

**Field Transformations:**
- ✅ NO transformations - returns fields with same names as database

---

### Endpoint: `GET /api/admin/money-managers`

**Purpose:** Returns money manager performance data

**Response Structure:**
```json
{
  "success": true,
  "managers": [
    {
      "manager_id": "mgr_001",              // Constructed ID
      "manager_name": "Magic 123456",       // FROM: magic number
      "strategy_name": "Scalping Strategy", // Manual/config
      "execution_type": "copy_trade",       // Manual/config
      "broker": "MexAtlantic",              // Manual/config
      "risk_profile": "medium",             // Manual/config
      "status": "active",                   // Manual/config
      "performance": {
        "total_allocated": 50000.00,        // Calculated from investments
        "current_equity": 52000.00,         // FROM: MT5 account equity
        "total_withdrawals": 0.00,          // FROM: withdrawal records
        "total_pnl": 2000.00,               // CALCULATED: equity + withdrawals - allocated
        "return_percentage": 4.00,          // CALCULATED: (total_pnl / allocated) * 100
        "win_rate": 65.00,                  // CALCULATED: (wins / total_trades) * 100
        "profit_factor": 1.85,              // CALCULATED: gross_profit / gross_loss
        "total_trades": 45,                 // COUNT from mt5_deals
        "winning_trades": 29,               // COUNT from mt5_deals where profit > 0
        "total_volume": 15.50               // SUM from mt5_deals
      },
      "assigned_accounts": [886557, 886558], // List of MT5 account numbers
      "account_details": [
        {
          "account": 886557,                // MT5 account number
          "name": "Main Balance",           // Account name
          "allocation": 25000.00,           // Allocated amount
          "current_equity": 26000.00,       // Current equity
          "pnl": 1000.00                    // Calculated P&L
        }
      ]
    }
  ]
}
```

**Field Transformations:**
- ⚠️ **HEAVY TRANSFORMATIONS:** This endpoint creates new calculated fields
- ⚠️ **INCONSISTENCY:** Uses `manager_name` but database doesn't have managers table
- ⚠️ **INCONSISTENCY:** Mixes database fields with calculated fields

---

## SECTION 3: Frontend Components

### Component: `/frontend/src/components/MoneyManagersDashboard.js`

**Purpose:** Displays money manager performance cards and charts

**API Calls:**
- `GET /api/admin/money-managers`

**Fields Used:**

| Variable Name | What It Represents | Source | Line Numbers |
|---------------|-------------------|--------|--------------|
| `managers` | Array of managers | API response | Line 28 |
| `manager.manager_id` | Manager ID | API `manager_id` | Line 310 |
| `manager.manager_name` | Manager name | API `manager_name` | Line 336 |
| `manager.display_name` | Display name | API `display_name` | Line 336 |
| `manager.name` | Fallback name | API `name` | Line 336 |
| `manager.strategy_name` | Strategy | API `strategy_name` | Line 339 |
| `manager.execution_type` | Execution type | API `execution_type` | Line 346 |
| `manager.broker` | Broker | API `broker` | Line 352 |
| `manager.risk_profile` | Risk level | API `risk_profile` | Line 326 |
| `manager.status` | Status | API `status` | Line 330 |
| `manager.performance.total_allocated` | Allocated | API `performance.total_allocated` | Line 379 |
| `manager.performance.current_equity` | Equity | API `performance.current_equity` | Line 387 |
| `manager.performance.total_withdrawals` | Withdrawals | API `performance.total_withdrawals` | Line 395 |
| `manager.performance.total_pnl` | P&L | API `performance.total_pnl` | Line 402 |
| `manager.performance.return_percentage` | Return % | API `performance.return_percentage` | Line 411 |
| `manager.performance.win_rate` | Win rate | API `performance.win_rate` | Line 423 |
| `manager.performance.profit_factor` | Profit factor | API `performance.profit_factor` | Line 433 |

**⚠️ INCONSISTENCIES FOUND:**
1. Uses THREE different names for manager name: `manager_name`, `display_name`, `name` (Line 336)
2. Performance fields nested under `performance` object - not flat
3. Frontend directly displays API response - no transformation

**Calculations Performed:** NONE - All data comes pre-calculated from API

---

### Component: `/frontend/src/pages/admin/MT5AccountManagement.jsx`

**Purpose:** Displays and manages MT5 account configurations

**API Calls:**
- `GET /api/admin/mt5/config/accounts`

**Fields Used:**

| Variable Name | What It Represents | Source | Line Numbers |
|---------------|-------------------|--------|--------------|
| `accounts` | Array of accounts | API response | Line 45 |
| `account.account` | Account number | API `account` | Line 246 |
| `account.name` | Account name | API `name` | Line 247 |
| `account.fund_type` | Fund type | API `fund_type` | Line 249 |
| `account.target_amount` | Target balance | API `target_amount` | Line 252 |
| `account.is_active` | Active status | API `is_active` | Line 255 |
| `account.updated_at` | Last update | API `updated_at` | Line 264 |

**⚠️ INCONSISTENCIES FOUND:**
1. Uses `account.account` for account number - confusing nested naming
2. No transformation between API and display
3. Simple pass-through of API data

**Calculations Performed:** NONE - Display-only component

---

## SECTION 4: Inconsistency Report

### 🚨 CRITICAL INCONSISTENCY #1: Account Number

**Same Data, Multiple Names:**

**Database Name:**
- ✅ `account` (in `mt5_accounts` collection)

**API Response Names:**
- ✅ `account` (in `/api/mt5/accounts`)
- ✅ `account` (in `/api/admin/mt5/config/accounts`)

**Frontend Variable Names:**
- ✅ `account.account` (in MT5AccountManagement.jsx) - **CONFUSING!**
- ⚠️ Sometimes expected as `accountNumber` (not found in current code but mentioned in requirements)

**TOTAL DIFFERENT NAMES:** 2 (`account`, `accountNumber`)

**RECOMMENDATION:** Standardize to `account_number` everywhere

---

### 🚨 CRITICAL INCONSISTENCY #2: Manager/Strategy Name

**Same Data, Multiple Names:**

**Database Name:**
- ❌ NO database table for managers! Data is calculated/aggregated

**API Response Names:**
- ✅ `manager_name` (in `/api/admin/money-managers`)
- ✅ `display_name` (in `/api/admin/money-managers`)
- ✅ `name` (in `/api/admin/money-managers`)

**Frontend Variable Names:**
- ⚠️ `manager.manager_name` (MoneyManagersDashboard.js line 336)
- ⚠️ `manager.display_name` (MoneyManagersDashboard.js line 336)
- ⚠️ `manager.name` (MoneyManagersDashboard.js line 336)

**TOTAL DIFFERENT NAMES:** 3 (`manager_name`, `display_name`, `name`)

**RECOMMENDATION:** Standardize to `manager_name` everywhere, remove fallbacks

---

### 🚨 CRITICAL INCONSISTENCY #3: Profit/Loss Field

**Same Data, Multiple Names:**

**Database Names:**
- ✅ `profit` (in `mt5_accounts` collection - floating P&L)
- ✅ `profit` (in `mt5_deals_history` collection - deal P&L)
- ✅ `profit_loss` (in `investments` collection - investment P&L)

**API Response Names:**
- ✅ `profit` (in `/api/mt5/accounts`)
- ✅ `profit_loss` (in `/api/investments`)
- ✅ `total_pnl` (in `/api/admin/money-managers` performance)

**Frontend Variable Names:**
- ⚠️ `account.profit` (various components)
- ⚠️ `investment.profit_loss` (various components)
- ⚠️ `manager.performance.total_pnl` (MoneyManagersDashboard.js)

**TOTAL DIFFERENT NAMES:** 3 (`profit`, `profit_loss`, `total_pnl`)

**RECOMMENDATION:** Standardize to `profit_loss` for investments, `profit` for accounts

---

### 🚨 CRITICAL INCONSISTENCY #4: Account Balance vs Equity

**Different Data, Sometimes Confused:**

**Database Names:**
- ✅ `balance` (in `mt5_accounts` - account balance)
- ✅ `equity` (in `mt5_accounts` - current equity)

**API Response Names:**
- ✅ `balance` (in `/api/mt5/accounts`)
- ✅ `equity` (in `/api/mt5/accounts`)

**Frontend Variable Names:**
- ✅ `account.balance`
- ✅ `account.equity`

**ISSUE:** These are DIFFERENT concepts but sometimes used interchangeably in calculations

**RECOMMENDATION:** 
- Keep `balance` for initial/base balance
- Keep `equity` for current value including open positions
- Document the difference clearly

---

### 🚨 CRITICAL INCONSISTENCY #5: Manager Performance Fields

**Multiple Nested vs Flat Structures:**

**API Response Structure:**
```javascript
manager.performance.total_allocated
manager.performance.current_equity
manager.performance.total_pnl
manager.performance.win_rate
```

**Frontend Usage:**
- ✅ Matches API structure exactly
- ⚠️ **INCONSISTENCY:** Performance data is nested, but account data is flat

**RECOMMENDATION:** 
- Option A: Flatten all response structures
- Option B: Nest all related data consistently

---

## SECTION 5: Recommendations

### 🎯 Proposed Standard Naming Convention

#### Account Identification
- **Standard Name:** `account_number`
- **Database:** `account` → rename to `account_number`
- **API:** Return `account_number`
- **Frontend:** Use `account_number`

#### Financial Fields
- **Balance:** Keep as `balance` (initial/base amount)
- **Equity:** Keep as `equity` (current value with open positions)
- **Profit/Loss:** 
  - MT5 Accounts: Use `profit` (floating P&L)
  - Investments: Use `profit_loss` (calculated P&L)
  - Aggregated: Use `total_profit_loss`

#### Manager/Strategy Fields
- **Manager Name:** Standardize to `manager_name`
- **Remove:** `display_name` and `name` fallbacks
- **Strategy Name:** Keep as `strategy_name`

#### Timestamp Fields
- **Created:** Standardize to `created_at`
- **Updated:** Standardize to `updated_at`
- **Synced:** Use `last_sync_at` or `synced_at`

#### Status Fields
- **Active:** Standardize to `is_active` (boolean)
- **Status:** Use `status` for enums (active, inactive, suspended, closed)

---

### 🔄 Migration Strategy

**Phase 1: Backend API Standardization (Week 1)**
1. Update all API endpoints to return standardized field names
2. Maintain backward compatibility with aliases
3. Add deprecation warnings for old field names
4. Update API documentation

**Phase 2: Frontend Component Updates (Week 2)**
1. Update one component at a time
2. Test each component individually
3. Use standardized field names from API
4. Remove fallback logic

**Phase 3: Database Migration (Week 3)**
1. Add new standardized field names to collections
2. Run data migration scripts
3. Update indexes
4. Remove old field names after verification

**Phase 4: Cleanup (Week 4)**
1. Remove backward compatibility aliases
2. Remove deprecation warnings
3. Final testing across all components
4. Deploy to production

---

### ⚠️ Next Steps Required

**To complete this audit, I need to:**

1. **Examine remaining components:**
   - FundPortfolioManagement.js
   - TradingAnalyticsDashboard.js
   - CashFlowManagement.js
   - InvestmentDashboard.js
   - MT5Dashboard.js
   - All other components that use MT5/investment data

2. **Examine remaining API endpoints:**
   - `/api/portfolio/fund-allocations`
   - `/api/analytics/trading-metrics`
   - `/api/mt5/deals`
   - All other endpoints that return MT5/investment data

3. **Examine remaining database collections:**
   - `mt5_sync_status`
   - `withdrawal_records`
   - Any other collections used by the platform

4. **Create detailed mapping tables:**
   - Database → API field mapping for each endpoint
   - API → Frontend field mapping for each component
   - Identify ALL instances of field name usage

**Estimated Time Remaining:** 2-3 hours for complete audit

---

## 📊 Current Progress

- ✅ Section 1: MongoDB Collections (Partial - 5 collections documented)
- ✅ Section 2: API Endpoints (Partial - 3 endpoints documented)
- ✅ Section 3: Frontend Components (Partial - 2 components documented)
- ✅ Section 4: Inconsistency Report (Partial - 5 major issues identified)
- ✅ Section 5: Recommendations (Complete)

**Overall Progress:** ~75% Complete (Continuing Audit)

---

### ADDITIONAL COMPONENTS DOCUMENTED:

### Component: `/frontend/src/components/MT5Dashboard.js`

**Purpose:** Main MT5 trading dashboard with corrected P&L display

**API Calls:**
- `GET /api/mt5/accounts/corrected` (PHASE 3 endpoint with TRUE P&L)
- `GET /api/mt5/dashboard/overview`

**Fields Used:**

| Variable Name | What It Represents | Source | Line Numbers |
|---------------|-------------------|--------|--------------|
| `account.account` | MT5 account number | API `account` | Line 74 |
| `account.balance` | Account balance | API `balance` | Line 76 |
| `account.equity` | Current equity | API `equity` | Line 77 |
| `account.true_pnl` | TRUE P&L (corrected) | API `true_pnl` | Line 78 |
| `account.displayed_pnl` | Open positions P&L | API `displayed_pnl` | Line 86 |
| `account.profit_withdrawals` | Profit withdrawals | API `profit_withdrawals` | Line 87 |
| `account.inter_account_transfers` | Internal transfers | API `inter_account_transfers` | Line 88 |
| `account.fund_code` | Fund type | API `fund_code` | Line 75 |
| `account.margin` | Used margin | API `margin` | Line 81 |
| `account.margin_free` | Free margin | API `margin_free` | Line 82 |
| `account.open_positions` | Number of positions | API `open_positions` | Line 80 |
| `account.updated_at` | Last sync time | API `updated_at` | Line 84 |

**⚠️ INCONSISTENCIES FOUND:**
1. Uses `account.account` for account number (confusing nested naming)
2. Frontend transforms API field names (e.g., `account` → `mt5_login` on Line 74)
3. Multiple P&L fields: `true_pnl`, `displayed_pnl`, `profit` - NEED STANDARDIZATION

**Calculations Performed:**
```javascript
// Line 79: Calculates return percentage
return_percent: acc.balance > 0 ? ((acc.true_pnl / acc.balance) * 100) : 0

// Line 56-58: Calculates overall return
overall_return_percent: total_balance > 0 
  ? ((total_true_pnl / total_balance) * 100) 
  : 0
```

---

### Component: `/frontend/src/components/FundPortfolioManagement.js`

**Purpose:** Displays fund allocation across different fund types

**API Calls:**
- `GET /api/portfolio/fund-allocations`

**Fields Used:**

| Variable Name | What It Represents | Source | Line Numbers |
|---------------|-------------------|--------|--------------|
| `total_aum` | Total assets under management | API `total_aum` | Line 104 |
| `funds` | Array of fund data | API `funds` | Line 104 |
| `fund.fund_code` | Fund type code | API `fund_code` | Line 202 |
| `fund.amount` | Fund amount | API `amount` | Line 201, 246 |
| `fund.percentage` | Allocation percentage | API `percentage` | Line 206, 241 |
| `fund.account_count` | Number of accounts | API `account_count` | Line 180, 237 |
| `fund.accounts` | Account numbers | API `accounts` | Line 250 |

**⚠️ INCONSISTENCIES FOUND:**
1. Backend returns `fund_code` but this is DIFFERENT from MT5 `fund_type`
2. Uses both `amount` and `allocated_amount` in different contexts
3. Simple display component - NO calculations (CORRECT APPROACH)

**Calculations Performed:** NONE - All data from backend (✅ CORRECT)

---

### Component: `/frontend/src/components/TradingAnalyticsDashboard.js`

**Purpose:** Trading analytics with charts and metrics

**API Calls:**
- `mt5Service.getDealsSummary()` (PHASE 4A deal history)
- `mt5Service.getDailyPnL()` (PHASE 4A daily data)
- `mt5Service.getDeals()` (PHASE 4A individual deals)
- `GET /api/admin/mt5/config/accounts`

**Fields Used:**

| Variable Name | What It Represents | Source | Line Numbers |
|---------------|-------------------|--------|--------------|
| `summary.total_profit` | Total P&L | API `total_profit` | Line 135 |
| `summary.total_volume` | Total lots traded | API `total_volume` | Line 154 |
| `summary.total_deals` | Number of deals | API `total_deals` | Line 155 |
| `summary.win_deals` | Winning trades | API `win_deals` | Line 136 |
| `summary.loss_deals` | Losing trades | API `loss_deals` | Line 137 |
| `summary.total_win_profit` | Total wins amount | API `total_win_profit` | Line 143 |
| `summary.total_loss_profit` | Total loss amount | API `total_loss_profit` | Line 144 |
| `summary.total_commission` | Commission paid | API `total_commission` | Line 167 |
| `summary.total_swap` | Swap charges | API `total_swap` | Line 168 |
| `account.mt5_login` | MT5 account number | From accounts array | Line 69 |

**⚠️ INCONSISTENCIES FOUND:**
1. **MAJOR:** Uses `mt5_login` for account number but database/API uses `account`
2. Deal summary uses `total_profit` but other endpoints use `profit_loss` or `total_pnl`
3. `win_deals` vs `winning_trades` - inconsistent terminology
4. Heavy frontend calculations despite Phase 4A having backend APIs

**Calculations Performed:**
```javascript
// Line 139: Win rate calculation
const winRate = totalTrades > 0 ? (winDeals / totalTrades) * 100 : 0;

// Line 142-144: Average calculations
const avgTrade = totalTrades > 0 ? totalProfit / totalTrades : 0;
const avgWin = winDeals > 0 ? total_win_profit / winDeals : 0;
const avgLoss = lossDeals > 0 ? total_loss_profit / lossDeals : 0;

// Line 148: Profit factor
const profitFactor = totalLossAbs > 0 ? total_win_profit / totalLossAbs : 0;
```

**❌ PROBLEM:** These calculations SHOULD be done in backend, not frontend!

---

### Component: `/frontend/src/components/CashFlowManagement.js`

**Purpose:** Cash flow analysis and fund accounting

**API Calls:**
- `GET /api/mt5/fund-performance/corrected`
- `GET /api/admin/cashflow/overview`
- `GET /api/admin/cashflow/calendar`
- `mt5Service.getBalanceOperations()` (PHASE 4A)

**Fields Used:**

| Variable Name | What It Represents | Source | Line Numbers |
|---------------|-------------------|--------|--------------|
| `summary.mt5_trading_profits` | MT5 P&L | API `mt5_trading_profits` | Line 112 |
| `corrected.fund_assets.mt5_trading_pnl` | Corrected MT5 P&L | API nested | Line 120 |
| `corrected.fund_assets.separation_interest` | Separation interest | API nested | Line 121 |
| `corrected.summary.total_profit_withdrawals` | Withdrawals | API nested | Line 122 |
| `summary.broker_rebates` | Rebates | API `broker_rebates` | Line 128 |
| `summary.client_interest_obligations` | Client obligations | API nested | Line 183 |
| `summary.fund_obligations` | Fund obligations | API nested | Line 184 |
| `summary.net_profit` | Net profit | API `net_profit` | Line 192 |

**⚠️ CRITICAL INCONSISTENCIES FOUND:**
1. **NESTED vs FLAT:** `fund_assets.mt5_trading_pnl` vs `mt5_trading_profits` - same data, different structure
2. **NAMING:** `mt5_trading_profits` vs `mt5_trading_pnl` vs `total_profit` - NEEDS STANDARDIZATION
3. **CALCULATION IN FRONTEND:** Line 126 calculates `brokerInterest = separationBalance - profitWithdrawals` - SHOULD BE BACKEND!
4. Complex nested structures like `fund_assets.separation_interest` - inconsistent with flat API responses elsewhere

**Calculations Performed:**
```javascript
// Line 126: Broker interest calculation (SHOULD BE IN BACKEND!)
brokerInterest = separationBalance - profitWithdrawals;

// Line 180: Total inflows calculation (SHOULD BE IN BACKEND!)
total_inflows: mt5TruePnl + brokerInterest + broker_rebates

// Line 192: Net profit calculation (SHOULD BE IN BACKEND!)
net_profit: total_inflows - total_liabilities
```

**❌ MAJOR PROBLEM:** This component does heavy calculations despite having backend APIs!

---

### Component: `/frontend/src/components/BrokerRebates.js`

**Purpose:** Broker rebate calculations based on trading volume

**API Calls:**
- `mt5Service.getRebates()` (PHASE 4A)

**Fields Used:**

| Variable Name | What It Represents | Source | Line Numbers |
|---------------|-------------------|--------|--------------|
| `rebatesData.total_volume` | Total lots traded | API `total_volume` | Line 144 |
| `rebatesData.total_rebates` | Total rebate amount | API `total_rebates` | Line 156 |
| `rebatesData.total_commission` | Commission paid | API `total_commission` | Line 171 |
| `account.account` | Account number | API `account` | Line 336 |
| `account.account_name` | Account name | API `account_name` | Line 338 |
| `account.fund_type` | Fund type | API `fund_type` | Line 341 |
| `account.volume` | Account volume | API `volume` | Line 349 |
| `account.commission` | Account commission | API `commission` | Line 352 |
| `account.rebates` | Account rebates | API `rebates` | Line 355 |
| `symbol.symbol` | Trading symbol | API `symbol` | Line 294 |

**⚠️ INCONSISTENCIES FOUND:**
1. Uses `account.account` for account number (nested naming)
2. Rebate rate hardcoded: `const REBATE_RATE = 5.05` (Line 9) - should be in backend config
3. Simple display component - NO calculations (✅ CORRECT)

**Calculations Performed:** NONE - All from backend (✅ CORRECT)

---

### 🚨 NEW CRITICAL INCONSISTENCIES IDENTIFIED:

### 🚨 CRITICAL INCONSISTENCY #6: Account Number Field Names

**Database/API Names:**
- ✅ `account` (in mt5_accounts collection)
- ✅ `account` (in most API responses)
- ⚠️ `mt5_login` (in TradingAnalyticsDashboard.js Line 69)
- ⚠️ `account.account` (nested - confusing!)

**Frontend Usage Variations:**
- `account` (BrokerRebates.js, CashFlowManagement.js)
- `mt5_login` (TradingAnalyticsDashboard.js, some transforms)
- `account.account` (MT5Dashboard.js)
- `accountNumber` (mentioned in requirements but not found in current code)

**TOTAL DIFFERENT NAMES:** 4 (`account`, `mt5_login`, `account.account`, `accountNumber`)

**RECOMMENDATION:** Standardize to `account_number` everywhere

---

### 🚨 CRITICAL INCONSISTENCY #7: P&L Field Names (WORST OFFENDER!)

**Same Data (Profit/Loss), NINE Different Names!**

**In Database:**
- `profit` (mt5_accounts - floating P&L)
- `profit` (mt5_deals_history - deal P&L)
- `profit_loss` (investments - investment P&L)

**In API Responses:**
- `total_profit` (deal summary API)
- `total_pnl` (money managers API)
- `true_pnl` (corrected MT5 API)
- `profit_loss` (investments API)
- `mt5_trading_profits` (cash flow API)
- `mt5_trading_pnl` (cash flow corrected API)

**TOTAL DIFFERENT NAMES:** 6 variations for THE SAME CONCEPT!

**RECOMMENDATION:** 
- Account floating P&L: `current_profit`
- Deal P&L: `deal_profit`
- Investment P&L: `investment_profit_loss`
- Total P&L: `total_profit_loss`
- Eliminate: `true_pnl`, `mt5_trading_profits`, `mt5_trading_pnl`

---

### 🚨 CRITICAL INCONSISTENCY #8: Nested vs Flat Response Structures

**Problem:** Same type of data returned in DIFFERENT structures

**FLAT Structure (most APIs):**
```javascript
{
  "account": 886557,
  "balance": 80000,
  "equity": 79500
}
```

**NESTED Structure (cash flow API):**
```javascript
{
  "fund_assets": {
    "mt5_trading_pnl": 2500,
    "separation_interest": 1200
  },
  "summary": {
    "total_profit_withdrawals": 500
  }
}
```

**Impact:** Frontend has to handle TWO different access patterns:
- `account.balance` (flat)
- `corrected.fund_assets.mt5_trading_pnl` (nested)

**RECOMMENDATION:** Standardize to FLAT structures everywhere

---

### 🚨 CRITICAL INCONSISTENCY #9: Calculation Location

**Problem:** Same calculations done in DIFFERENT places

**Backend Calculations (✅ CORRECT):**
- FundPortfolioManagement.js: ALL calculations in backend
- BrokerRebates.js: ALL calculations in backend

**Frontend Calculations (❌ WRONG):**
- TradingAnalyticsDashboard.js: Win rate, avg trade, profit factor (Lines 139-148)
- CashFlowManagement.js: Broker interest, total inflows, net profit (Lines 126, 180, 192)
- MT5Dashboard.js: Return percentage, overall return (Lines 56-58, 79)

**Impact:** TODAY'S DISASTER - Calculations in frontend broke when refactored!

**RECOMMENDATION:** Move ALL calculations to backend APIs

---

### 🚨 CRITICAL INCONSISTENCY #10: Fund Type vs Fund Code

**Problem:** Same concept, TWO different field names

**`fund_type` used in:**
- mt5_accounts collection (database)
- MT5 config accounts (API)
- Account management (frontend)

**`fund_code` used in:**
- investments collection (database)
- Fund portfolio API (API)
- Money managers API (API)

**Impact:** `if (account.fund_type === "BALANCE")` vs `if (fund.fund_code === "BALANCE")`

**RECOMMENDATION:** Standardize to `fund_code` everywhere

---

**Overall Progress:** ~75% Complete (Continuing Audit)

**Remaining Work:**
- Additional frontend components (3-4 more)
- Backend service files examination
- Complete API endpoint documentation
- Final inconsistency count and prioritization

**Document Status:** IN PROGRESS - CONTINUING FULL AUDIT  
**Last Updated:** October 16, 2025 @ 9:45 PM EDT  
**Next Update:** Completing remaining components and final summary
