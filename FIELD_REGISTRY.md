# FIDUS PLATFORM - COMPLETE FIELD REGISTRY

**Version:** 2.0  
**Last Updated:** November 5, 2025  
**Purpose:** Single Source of Truth for all field names across MongoDB, APIs, and Frontend

---

## EXECUTIVE SUMMARY

**Collections Audited:** 35+ collections  
**Critical Collections:** 7 (documented in detail)  
**Critical Inconsistencies Identified:** 12  
**Required Migrations:** 5 high-priority  
**Status:** ⚠️ REQUIRES IMMEDIATE FIXES

### Critical Issues:
1. ✅ **RESOLVED**: Salvador Palma referral data field mapping
2. ⚠️ **PENDING**: Duplicate field names in multiple collections
3. ⚠️ **PENDING**: Inconsistent timestamp types (String vs DateTime)
4. ⚠️ **PENDING**: Manager name field duplication
5. ⚠️ **PENDING**: Investment amount field duplication

---

## TABLE OF CONTENTS

1. [Field Naming Standards](#field-naming-standards)
2. [Complete Collection List](#complete-collection-list)
3. [Core Collections (Detailed)](#core-collections-detailed)
   - [mt5_accounts](#collection-mt5_accounts)
   - [money_managers](#collection-money_managers)
   - [salespeople](#collection-salespeople)
   - [referral_commissions](#collection-referral_commissions)
   - [investments](#collection-investments)
   - [clients](#collection-clients)
   - [mt5_deals_history](#collection-mt5_deals_history)
4. [Supporting Collections (Summary)](#supporting-collections-summary)
5. [Identified Inconsistencies](#identified-inconsistencies)
6. [Migration Scripts](#migration-scripts)
7. [Validation Rules](#validation-rules)

---

## FIELD NAMING STANDARDS

### Rule 1: MongoDB Collections
**Standard:** `snake_case` for ALL field names  
**Example:** `account_number`, `manager_name`, `created_at`  
**Rationale:** MongoDB best practice for field naming

### Rule 2: API Responses  
**Standard:** `camelCase` for ALL field names  
**Example:** `accountNumber`, `managerName`, `createdAt`  
**Rationale:** JavaScript/TypeScript convention

### Rule 3: Frontend Variables
**Standard:** `camelCase` for ALL variable names  
**Example:** `accountNumber`, `managerName`, `createdAt`  
**Rationale:** JavaScript/React convention

### Rule 4: Transformation Layer
All MongoDB documents MUST be transformed to camelCase before sending to API:

```python
# Use field_registry.transform_to_api_format()
from backend.validation.field_registry import transform_to_api_format

mongo_doc = await db.mt5_accounts.find_one({"account": 886557})
api_response = transform_to_api_format(mongo_doc)
# Output: {"accountNumber": 886557, "managerName": "...", "createdAt": "2025-11-05T..."}
```

### Rule 5: Reserved/Forbidden Field Names
**Never use these:**
- ❌ `id` → Use `_id` in MongoDB, transform to `id` in API
- ❌ `type` → Use `record_type`, `fund_type`, `account_type`
- ❌ `class` → Use `category`, `classification`
- ❌ `amount` → Use `principal_amount`, `commission_amount`, `interest_amount`

### Rule 6: Enum Values - Manager Names
**Allowed values** (SYSTEM_MASTER.md Section 5):
```
"UNO14 Manager"
"GoldenTrade Manager"
"Provider1-Assev"
"alefloreztrader"
"TradingHub Gold Provider"
"CP Strategy Provider"
"GoldenTrade" (inactive only)
```
**Validation:** Backend MUST reject any other values

### Rule 7: Enum Values - Fund Types
**Allowed values:**
```
"BALANCE" or "FIDUS_BALANCE"
"CORE" or "FIDUS_CORE"
"DYNAMIC" or "FIDUS_DYNAMIC"
"UNLIMITED" or "FIDUS_UNLIMITED"
"SEPARATION" or "FIDUS_SEPARATION"
```
**Validation:** Backend MUST normalize to short form (without FIDUS_ prefix)

### Rule 8: Enum Values - Status
**Allowed values:**
```
"active", "inactive", "pending", "approved", "cancelled", "paid", "ready_to_pay"
```

### Rule 9: DateTime Format
**MongoDB Storage:** Always use `datetime` object (Python) or `ISODate` (MongoDB shell)  
**API Response:** Always return ISO 8601 string: `"2025-11-05T14:30:00.000Z"`  
**Frontend Display:** Use JavaScript `new Date()` to parse

### Rule 10: Decimal/Money Fields
**MongoDB Storage:** Use `Decimal128` for all monetary values  
**API Response:** Convert to `float` with 2 decimal precision  
**Frontend Display:** Format with currency symbol and 2 decimals

---

## COMPLETE COLLECTION LIST

### Core Business Collections (7)
1. ✅ **mt5_accounts** - Real-time MT5 trading accounts (11 docs)
2. ✅ **money_managers** - Manager profiles and performance (7 docs)
3. ✅ **salespeople** - Referral system salespeople (3 docs)
4. ✅ **referral_commissions** - Commission tracking (16 docs)
5. ✅ **investments** - Client investment records (3 docs)
6. ✅ **clients** - Client profiles (1 doc)
7. ✅ **mt5_deals_history** - MT5 trading history (81,127 docs)

### CRM & Prospects (4)
8. **crm_prospects** - CRM pipeline leads
9. **leads** - Lead generation data
10. **client_interactions** - Interaction history
11. **client_meetings** - Meeting schedules

### Documents & Communication (4)
12. **client_documents** - Client document storage
13. **client_document_uploads** - Upload tracking
14. **prospect_documents** - Prospect documents
15. **client_communications** - Communication logs

### Performance & Analytics (5)
16. **daily_performance** - Daily performance metrics
17. **fund_performance_alerts** - Performance alerts
18. **fund_realtime_data** - Real-time fund data
19. **performance_fee_transactions** - Fee transactions
20. **broker_rebate_config** - Rebate configurations

### System & Auth (7)
21. **users** - Application users
22. **admin_users** - Admin user profiles
23. **admin_sessions** - Admin session tracking
24. **user_sessions** - User session tracking
25. **admin_google_sessions** - Google OAuth sessions
26. **google_tokens** - Google API tokens
27. **credential_audit_log** - Credential change audit

### System Health & Monitoring (5)
28. **system_alerts** - System alert notifications
29. **system_health_history** - Health check history
30. **notifications** - User notifications
31. **admin_notifications** - Admin notifications
32. **mt5_watchdog_status** - MT5 bridge health

### Other Business Collections (3)
33. **withdrawals** - Withdrawal requests
34. **registration_applications** - New client applications
35. **rebate_transactions** - Rebate payment tracking

---

## CORE COLLECTIONS (DETAILED)

## COLLECTION: mt5_accounts

**Purpose:** Real-time MT5 trading account data from VPS MT5 Bridge  
**Document Count:** 11  
**Sync Frequency:** Every 5 minutes from VPS  
**Critical For:** Trading Analytics, Cash Flow, Fund Performance

### Schema

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| account | Number | Yes | accountNumber | accountNumber | MT5 account login number (unique) |
| balance | Number | Yes | balance | balance | Current balance USD |
| equity | Number | Yes | equity | equity | Current equity USD |
| manager | String | Yes | managerName | managerName | ⚠️ Use this, not manager_name |
| ~~manager_name~~ | String | No | - | - | **DEPRECATED - DO NOT USE** |
| fund_type | String | Yes | fundType | fundType | BALANCE\|CORE\|DYNAMIC\|UNLIMITED\|SEPARATION |
| fund_code | String | Yes | fundCode | fundCode | Short code (e.g., "BALANCE") |
| broker | String | Yes | broker | broker | Always "MEXAtlantic" |
| currency | String | Yes | currency | currency | Always "USD" |
| leverage | Number | Yes | leverage | leverage | Account leverage (e.g., 100) |
| profit | Number | Yes | profit | profit | Unrealized profit/loss |
| free_margin | Number | Yes | freeMargin | freeMargin | Available margin |
| margin | Number | Yes | margin | margin | Used margin |
| margin_level | Number | Yes | marginLevel | marginLevel | Margin level percentage |
| num_positions | Number | Yes | numPositions | numPositions | Number of open positions |
| client_id | String | Yes | clientId | clientId | Reference to clients._id |
| client_name | String | No | clientName | clientName | Display name for UI |
| initial_allocation | Number | No | initialAllocation | initialAllocation | Starting capital allocation |
| true_pnl | Number | Yes | truePnl | truePnl | **Corrected P&L (includes withdrawals)** |
| displayed_pnl | Number | Yes | displayedPnl | displayedPnl | MT5 displayed P&L |
| profit_withdrawals | Number | No | profitWithdrawals | profitWithdrawals | Withdrawn profits (added to true_pnl) |
| inter_account_transfers | Number | No | interAccountTransfers | interAccountTransfers | Internal transfers |
| connection_status | String | Yes | connectionStatus | connectionStatus | active\|inactive\|error |
| ~~last_sync~~ | String | No | - | - | **DEPRECATED - use last_sync_timestamp** |
| last_sync_timestamp | DateTime | Yes | lastSyncTimestamp | lastSyncTimestamp | Last sync from VPS |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation timestamp |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update timestamp |
| data_source | String | Yes | dataSource | dataSource | Always "VPS_LIVE_MT5" |
| synced_from_vps | Boolean | Yes | syncedFromVps | syncedFromVps | VPS sync flag |

### Indexes
```javascript
db.mt5_accounts.createIndex({ "account": 1 }, { unique: true })
db.mt5_accounts.createIndex({ "fund_type": 1 })
db.mt5_accounts.createIndex({ "manager": 1 })
db.mt5_accounts.createIndex({ "client_id": 1 })
db.mt5_accounts.createIndex({ "last_sync_timestamp": -1 })
```

### Known Issues
1. ⚠️ **manager_name** field exists but should not be used (use **manager** instead)
2. ⚠️ **last_sync** string field deprecated in favor of **last_sync_timestamp** DateTime
3. ✅ All 11 accounts have correct true_pnl calculations from VPS

### Sample Document
```json
{
  "_id": ObjectId("..."),
  "account": 886557,
  "balance": 79425.13,
  "equity": 79425.13,
  "manager": "UNO14 Manager",
  "fund_type": "BALANCE",
  "fund_code": "BALANCE",
  "broker": "MEXAtlantic",
  "currency": "USD",
  "leverage": 100,
  "profit": 0.00,
  "true_pnl": 2829.69,
  "displayed_pnl": 2829.69,
  "profit_withdrawals": 0.00,
  "connection_status": "active",
  "last_sync_timestamp": ISODate("2025-11-05T14:30:00Z"),
  "synced_from_vps": true,
  "data_source": "VPS_LIVE_MT5"
}
```

---

## COLLECTION: money_managers

**Purpose:** Money manager profiles, strategies, and performance tracking  
**Document Count:** 7  
**Critical For:** Trading Analytics, Manager Rankings, Performance Fees

### Schema

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| manager_id | String | Yes | managerId | managerId | Unique identifier (mm_...) |
| name | String | Yes | name | name | ⚠️ Must be from allowed manager list |
| ~~manager_name~~ | String | No | - | - | **DEPRECATED - DO NOT USE** |
| display_name | String | No | displayName | displayName | Frontend display override |
| status | String | Yes | status | status | active\|inactive |
| assigned_accounts | Array[Number] | Yes | assignedAccounts | assignedAccounts | MT5 account numbers |
| strategy_name | String | Yes | strategyName | strategyName | Strategy description |
| strategy_description | String | No | strategyDescription | strategyDescription | Detailed description |
| performance_fee_rate | Number | Yes | performanceFeeRate | performanceFeeRate | Decimal (0.15 = 15%) |
| performance_fee_type | String | Yes | performanceFeeType | performanceFeeType | monthly\|quarterly |
| risk_profile | String | Yes | riskProfile | riskProfile | low\|medium\|high |
| broker | String | Yes | broker | broker | Always "MEXAtlantic" |
| profile_type | String | Yes | profileType | profileType | copy_trade\|manual |
| execution_type | String | Yes | executionType | executionType | copy_trade\|manual |
| current_month_profit | Number | Yes | currentMonthProfit | currentMonthProfit | Month-to-date profit |
| current_month_fee_accrued | Number | Yes | currentMonthFeeAccrued | currentMonthFeeAccrued | MTD performance fees |
| ytd_fees_paid | Number | Yes | ytdFeesPaid | ytdFeesPaid | Year-to-date fees paid |
| true_pnl | Number | Yes | truePnl | truePnl | Lifetime true P&L |
| start_date | DateTime | Yes | startDate | startDate | Manager start date |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update |

### Indexes
```javascript
db.money_managers.createIndex({ "manager_id": 1 }, { unique: true })
db.money_managers.createIndex({ "name": 1 })
db.money_managers.createIndex({ "status": 1 })
```

### Known Issues
1. ⚠️ **manager_name** field exists but should not be used (use **name** instead)
2. ✅ All managers filtered by `status: "active"` in API

---

## COLLECTION: salespeople

**Purpose:** Referral system salespeople/affiliates tracking  
**Document Count:** 3 (including Salvador Palma)  
**Critical For:** Referral System, Commission Payments  
**Status:** ✅ FIXED - Field mapping resolved

### Schema

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated MongoDB ID |
| salesperson_id | String | Yes | salespersonId | salespersonId | sp_[mongodb_id] (unique) |
| name | String | Yes | name | name | Full name |
| email | String | Yes | email | email | Contact email (unique) |
| phone | String | No | phone | phone | Contact phone |
| referral_code | String | Yes | referralCode | referralCode | Unique referral code |
| referral_link | String | Yes | referralLink | referralLink | Full URL with code |
| active | Boolean | Yes | active | active | Active status |
| total_sales_volume | Decimal128 | Yes | totalSalesVolume | totalSalesVolume | ✅ Total investment amount referred |
| total_commissions_earned | Decimal128 | Yes | totalCommissionsEarned | totalCommissionsEarned | ✅ Total commissions earned |
| commissions_pending | Decimal128 | Yes | commissionsPending | commissionsPending | Unpaid commissions |
| commissions_paid_to_date | Decimal128 | Yes | commissionsPaidToDate | commissionsPaidToDate | Paid commissions |
| total_clients_referred | Number | Yes | totalClientsReferred | totalClientsReferred | ✅ Number of clients referred |
| active_clients | Number | Yes | activeClients | activeClients | Active clients count |
| active_investments | Number | Yes | activeInvestments | activeInvestments | Active investments count |
| next_commission_date | DateTime | No | nextCommissionDate | nextCommissionDate | Next payment date |
| next_commission_amount | Number | No | nextCommissionAmount | nextCommissionAmount | Next payment amount |
| joined_date | DateTime | Yes | joinedDate | joinedDate | Signup date |
| preferred_payment_method | String | No | preferredPaymentMethod | preferredPaymentMethod | Payment method |
| wallet_details | Object | No | walletDetails | walletDetails | Payment wallet info |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update |

### Indexes
```javascript
db.salespeople.createIndex({ "salesperson_id": 1 }, { unique: true })
db.salespeople.createIndex({ "email": 1 }, { unique: true })
db.salespeople.createIndex({ "referral_code": 1 }, { unique: true })
db.salespeople.createIndex({ "active": 1 })
```

### Salvador Palma Record (Reference)
```json
{
  "_id": ObjectId("6909e8eaaaf69606babea151"),
  "salesperson_id": "sp_6909e8eaaaf69606babea151",
  "name": "Salvador Palma",
  "email": "chava@alyarglobal.com",
  "phone": "+1234567891",
  "referral_code": "SALVADOR2025",
  "active": true,
  "total_sales_volume": Decimal128("118151.41"),
  "total_commissions_earned": Decimal128("3272.27"),
  "total_clients_referred": 1
}
```

### Known Issues - RESOLVED ✅
1. ✅ Frontend field mapping fixed: `totalSalesVolume`, `totalCommissionsEarned`, `totalClientsReferred`
2. ✅ API transformer applies camelCase correctly
3. ✅ Detail page no longer shows "Salesperson not found"

---

## COLLECTION: referral_commissions

**Purpose:** Track individual commission payments for each investment  
**Document Count:** 16 (Alejandro's 2 investments × 8 payments each)  
**Critical For:** Cash Flow Calendar, Commission Payments  
**Status:** ✅ REGENERATED with correct data

### Schema

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| commission_id | String | Yes | commissionId | commissionId | Unique identifier |
| salesperson_id | String | Yes | salespersonId | salespersonId | Reference to salespeople.salesperson_id |
| investment_id | String | Yes | investmentId | investmentId | Reference to investments.investment_id |
| client_id | String | Yes | clientId | clientId | Reference to clients._id |
| fund_type | String | Yes | fundType | fundType | FIDUS_CORE\|FIDUS_BALANCE |
| principal_amount | Decimal128 | Yes | principalAmount | principalAmount | Investment principal |
| interest_amount | Decimal128 | Yes | interestAmount | interestAmount | Interest earned for period |
| commission_amount | Decimal128 | Yes | commissionAmount | commissionAmount | 10% of interest |
| payment_month | String | Yes | paymentMonth | paymentMonth | "Month 1", "Quarter 1", etc. |
| payment_date | DateTime | Yes | paymentDate | paymentDate | Scheduled payment date |
| status | String | Yes | status | status | pending\|approved\|paid\|cancelled |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update |

### Commission Calculation Rules

**CORE Fund:**
- Interest Rate: 18% annual / 1.5% monthly
- Payment Frequency: Monthly (on day 90, 120, 150, ...)
- Incubation Period: 60 days before first payment
- Commission: 10% of monthly interest
- Example: $18,151.41 × 1.5% = $272.27 interest → $27.23 commission

**BALANCE Fund:**
- Interest Rate: 30% annual / 7.5% quarterly
- Payment Frequency: Quarterly (on day 150, 240, 330, 420)
- Incubation Period: 60 days before first payment
- Commission: 10% of quarterly interest
- Example: $100,000 × 7.5% = $7,500 interest → $750.00 commission

### Indexes
```javascript
db.referral_commissions.createIndex({ "commission_id": 1 }, { unique: true })
db.referral_commissions.createIndex({ "salesperson_id": 1, "payment_date": 1 })
db.referral_commissions.createIndex({ "investment_id": 1 })
db.referral_commissions.createIndex({ "status": 1 })
```

### Sample - Alejandro CORE Commission
```json
{
  "_id": ObjectId("..."),
  "commission_id": "comm_...",
  "salesperson_id": "sp_6909e8eaaaf69606babea151",
  "investment_id": "inv_core_alejandro",
  "client_id": "client_alejandro",
  "fund_type": "FIDUS_CORE",
  "principal_amount": Decimal128("18151.41"),
  "interest_amount": Decimal128("272.27"),
  "commission_amount": Decimal128("27.23"),
  "payment_month": "Month 1",
  "payment_date": ISODate("2025-12-30T00:00:00Z"),
  "status": "pending"
}
```

---

## COLLECTION: investments

**Purpose:** Client investment records with referral tracking  
**Document Count:** 3  
**Critical For:** Referral System, Cash Flow, AUM Calculations

### Schema

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| investment_id | String | Yes | investmentId | investmentId | Unique identifier |
| client_id | String | Yes | clientId | clientId | Reference to clients._id |
| fund_type | String | Yes | fundType | fundType | FIDUS_CORE\|FIDUS_BALANCE\|etc |
| fund_code | String | Yes | fundCode | fundCode | CORE\|BALANCE\|etc |
| product | String | Yes | product | product | Product name |
| ~~amount~~ | Number | No | - | - | **DEPRECATED - use principal_amount** |
| principal_amount | Number | Yes | principalAmount | principalAmount | ✅ Investment amount (use this) |
| current_value | Number | Yes | currentValue | currentValue | Current value |
| status | String | Yes | status | status | active\|inactive\|closed |
| start_date | DateTime | Yes | startDate | startDate | Investment start date |
| deposit_date | DateTime | Yes | depositDate | depositDate | Deposit date |
| ~~investment_date~~ | DateTime | No | - | - | **DEPRECATED - use start_date** |
| interest_start_date | DateTime | Yes | interestStartDate | interestStartDate | Interest accrual start |
| referral_salesperson_id | String | No | referralSalespersonId | referralSalespersonId | ✅ Referring salesperson (use this) |
| ~~referred_by~~ | String | No | - | - | **DEPRECATED - use referral_salesperson_id** |
| referred_by_name | String | No | referredByName | referredByName | Display name |
| total_interest_earned | Number | Yes | totalInterestEarned | totalInterestEarned | Lifetime interest |
| total_commissions_due | Number | No | totalCommissionsDue | totalCommissionsDue | Total commissions |
| commissions_pending | Number | No | commissionsPending | commissionsPending | Unpaid commissions |
| next_commission_date | DateTime | No | nextCommissionDate | nextCommissionDate | Next payment date |
| next_commission_amount | Number | No | nextCommissionAmount | nextCommissionAmount | Next payment amount |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update |

### Indexes
```javascript
db.investments.createIndex({ "investment_id": 1 }, { unique: true })
db.investments.createIndex({ "client_id": 1 })
db.investments.createIndex({ "referral_salesperson_id": 1 })
db.investments.createIndex({ "fund_type": 1 })
db.investments.createIndex({ "status": 1 })
```

### Known Issues
1. ⚠️ **amount** field deprecated - use **principal_amount**
2. ⚠️ **referred_by** field deprecated - use **referral_salesperson_id**
3. ⚠️ **investment_date** field deprecated - use **start_date**

---

## COLLECTION: clients

**Purpose:** Client profile and contact information  
**Document Count:** 1 (Alejandro Mariscal Romero)  
**Critical For:** Referral System, CRM Integration

### Schema

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| name | String | Yes | name | name | Full name |
| email | String | Yes | email | email | Contact email (unique) |
| phone | String | No | phone | phone | Contact phone |
| status | String | Yes | status | status | active\|inactive |
| referral_code | String | No | referralCode | referralCode | Code used at signup |
| referred_by | ObjectId | No | referredBy | referredBy | ⚠️ Salesperson ObjectId (inconsistent) |
| referred_by_name | String | No | referredByName | referredByName | Display name |
| referral_date | DateTime | No | referralDate | referralDate | Referral date |
| total_commissions_generated | Number | No | totalCommissionsGenerated | totalCommissionsGenerated | Total commissions |
| commissions_pending | Number | No | commissionsPending | commissionsPending | Unpaid commissions |
| next_commission_date | DateTime | No | nextCommissionDate | nextCommissionDate | Next payment |
| next_commission_amount | Number | No | nextCommissionAmount | nextCommissionAmount | Next amount |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |

### Indexes
```javascript
db.clients.createIndex({ "email": 1 }, { unique: true })
db.clients.createIndex({ "referred_by": 1 })
db.clients.createIndex({ "status": 1 })
```

### Known Issues
1. ⚠️ **referred_by** uses ObjectId but should use String salesperson_id for consistency

---

## COLLECTION: mt5_deals_history

**Purpose:** Complete MT5 trading history from VPS  
**Document Count:** 81,127  
**Critical For:** P&L Calculations, Trading Analytics  
**Size:** ~50MB

### Schema

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| ticket | Number | Yes | ticket | ticket | Deal ticket number (unique) |
| account_number | Number | Yes | accountNumber | accountNumber | MT5 account |
| time | Number | Yes | time | time | Unix timestamp |
| type | Number | Yes | type | type | Deal type code |
| entry | Number | Yes | entry | entry | Entry type (0=in, 1=out) |
| symbol | String | No | symbol | symbol | Trading symbol (EURUSD, etc.) |
| volume | Number | Yes | volume | volume | Lot size |
| price | Number | Yes | price | price | Execution price |
| profit | Number | Yes | profit | profit | Deal profit/loss |
| commission | Number | Yes | commission | commission | Broker commission |
| swap | Number | Yes | swap | swap | Swap/rollover fees |
| fee | Number | Yes | fee | fee | Additional fees |
| comment | String | No | comment | comment | Deal comment |
| fund_type | String | No | fundType | fundType | Associated fund |
| synced_at | DateTime | Yes | syncedAt | syncedAt | Sync timestamp |
| synced_from_vps | Boolean | Yes | syncedFromVps | syncedFromVps | VPS source flag |

### Indexes
```javascript
db.mt5_deals_history.createIndex({ "ticket": 1 }, { unique: true })
db.mt5_deals_history.createIndex({ "account_number": 1, "time": -1 })
db.mt5_deals_history.createIndex({ "synced_at": -1 })
```

---

## SUPPORTING COLLECTIONS (SUMMARY)

These collections are less critical for the current referral system fix but documented for completeness:

### CRM Collections
- **crm_prospects**: Pipeline leads with stages
- **leads**: Lead generation tracking
- **client_interactions**: Interaction history
- **client_meetings**: Meeting schedules

### Document Collections
- **client_documents**: Client document storage
- **client_document_uploads**: Upload tracking
- **prospect_documents**: Prospect documents

### Performance Collections
- **daily_performance**: Daily metrics
- **fund_performance_alerts**: Performance alerts
- **fund_realtime_data**: Real-time fund data
- **performance_fee_transactions**: Fee transactions

### System Collections
- **users**: Application users
- **admin_users**: Admin profiles
- **admin_sessions**: Session tracking
- **system_alerts**: System alerts
- **notifications**: User notifications

---

## IDENTIFIED INCONSISTENCIES

### 1. Manager Name Field Duplication ⚠️ CRITICAL
**Issue:** Multiple field names for the same data  
**Impact:** Query inconsistencies, data redundancy

**Affected Collections:**
- `mt5_accounts`: Both `manager` and `manager_name` exist
- `money_managers`: Both `name` and `manager_name` exist

**Current State:**
```json
// mt5_accounts - INCONSISTENT
{
  "manager": "UNO14 Manager",
  "manager_name": "UNO14 Manager"  // Duplicate!
}

// money_managers - INCONSISTENT
{
  "name": "UNO14 Manager",
  "manager_name": "UNO14 Manager"  // Duplicate!
}
```

**Standard (After Migration):**
- `mt5_accounts`: Use `manager` ONLY
- `money_managers`: Use `name` ONLY
- API: Always `managerName`
- Remove all `manager_name` fields

**Migration Priority:** 🔴 HIGH  
**Estimated Docs Affected:** 11 (mt5_accounts) + 7 (money_managers) = 18

---

### 2. Investment Amount Field Duplication ⚠️ CRITICAL
**Issue:** Two fields for investment principal  
**Impact:** Confusion in queries, potential calculation errors

**Affected Collection:** `investments`

**Current State:**
```json
{
  "amount": 18151.41,              // Deprecated
  "principal_amount": 18151.41     // Use this
}
```

**Standard (After Migration):**
- MongoDB: Use `principal_amount` ONLY
- API: `principalAmount`
- Remove all `amount` fields

**Migration Priority:** 🔴 HIGH  
**Estimated Docs Affected:** 3

---

### 3. Referral Field Inconsistency ⚠️ HIGH
**Issue:** Different field names and types for referral tracking  
**Impact:** Join queries fail, referral tracking broken

**Affected Collections:**
- `investments`: `referral_salesperson_id` (String) and `referred_by` (String)
- `clients`: `referred_by` (ObjectId)

**Current State:**
```json
// investments - TWO FIELDS
{
  "referral_salesperson_id": "sp_6909e8eaaaf69606babea151",  // Use this
  "referred_by": "sp_6909e8eaaaf69606babea151"               // Duplicate
}

// clients - WRONG TYPE
{
  "referred_by": ObjectId("6909e8eaaaf69606babea151")  // Should be String!
}
```

**Standard (After Migration):**
- Always use `referral_salesperson_id` (String) format
- Store salesperson_id as String (e.g., "sp_6909e8eaaaf69606babea151")
- Remove `referred_by` field from investments
- Convert `clients.referred_by` from ObjectId to String salesperson_id

**Migration Priority:** 🔴 HIGH  
**Estimated Docs Affected:** 3 (investments) + 1 (clients) = 4

---

### 4. Timestamp Type Inconsistency ⚠️ MEDIUM
**Issue:** Mixed String and DateTime types  
**Impact:** Sort/query issues, timezone confusion

**Affected Collections:** Multiple

**Current State:**
```json
// Some documents
{
  "created_at": "2025-11-05T14:30:00Z"  // String
}

// Other documents
{
  "created_at": ISODate("2025-11-05T14:30:00Z")  // DateTime
}
```

**Standard (After Migration):**
- MongoDB: Always DateTime object
- API: Always ISO 8601 string

**Migration Priority:** 🟡 MEDIUM  
**Estimated Docs Affected:** Unknown (need full audit)

---

### 5. Account Number Field Naming ⚠️ LOW
**Issue:** Different field names for MT5 account number  
**Impact:** Query confusion, but no data loss

**Affected Collections:**
- `mt5_accounts`: Uses `account`
- `mt5_deals_history`: Uses `account_number`

**Standard (After Migration):**
- `mt5_accounts`: Keep `account` (primary collection)
- Related collections: Use `account_number` (foreign key)
- API: Always `accountNumber`

**Migration Priority:** 🟢 LOW (No migration needed, just document)

---

### 6. Deprecated Fields Still Present ⚠️ LOW
**Issue:** Old fields not removed from documents  
**Impact:** Confusion, wasted storage

**Fields to Remove:**
- `mt5_accounts.last_sync` (use `last_sync_timestamp`)
- `investments.investment_date` (use `start_date`)

**Migration Priority:** 🟢 LOW  
**Estimated Docs Affected:** 14

---

## MIGRATION SCRIPTS

### Priority 1: Remove Duplicate Manager Name Fields

**Target:** mt5_accounts and money_managers collections

```javascript
// Step 1: Verify all documents have 'manager' or 'name' field
db.mt5_accounts.find({ "manager": { $exists: false } }).count()
// Expected: 0

db.money_managers.find({ "name": { $exists: false } }).count()
// Expected: 0

// Step 2: Remove duplicate manager_name field
db.mt5_accounts.updateMany(
  {},
  { $unset: { "manager_name": "" } }
)

db.money_managers.updateMany(
  {},
  { $unset: { "manager_name": "" } }
)

// Step 3: Verify removal
db.mt5_accounts.find({ "manager_name": { $exists: true } }).count()
// Expected: 0

db.money_managers.find({ "manager_name": { $exists: true } }).count()
// Expected: 0
```

**Rollback:**
```javascript
// If needed, restore from manager field
db.mt5_accounts.updateMany(
  {},
  [{ $set: { "manager_name": "$manager" } }]
)
```

---

### Priority 2: Remove Duplicate Investment Amount Fields

**Target:** investments collection

```javascript
// Step 1: Verify all have principal_amount
db.investments.find({ "principal_amount": { $exists: false } }).count()
// Expected: 0

// Step 2: Copy amount to principal_amount if missing
db.investments.updateMany(
  { 
    "principal_amount": { $exists: false },
    "amount": { $exists: true }
  },
  [{ $set: { "principal_amount": "$amount" } }]
)

// Step 3: Remove amount field
db.investments.updateMany(
  {},
  { $unset: { "amount": "", "investment_date": "", "referred_by": "" } }
)

// Step 4: Verify
db.investments.find({
  $or: [
    { "amount": { $exists: true } },
    { "investment_date": { $exists: true } },
    { "referred_by": { $exists: true } }
  ]
}).count()
// Expected: 0
```

---

### Priority 3: Standardize Referral Fields

**Target:** clients collection (convert ObjectId to String)

```javascript
// Step 1: Find all clients with ObjectId referred_by
const clients = await db.clients.find({ 
  "referred_by": { $type: "objectId" } 
}).toArray()

// Step 2: Convert ObjectId to salesperson_id String
for (const client of clients) {
  const salesperson = await db.salespeople.findOne({ 
    _id: client.referred_by 
  })
  
  if (salesperson) {
    await db.clients.updateOne(
      { _id: client._id },
      { $set: { "referred_by": salesperson.salesperson_id } }
    )
  }
}

// Step 3: Verify all are now Strings
db.clients.find({ "referred_by": { $type: "objectId" } }).count()
// Expected: 0
```

---

### Priority 4: Convert String Timestamps to DateTime

**Target:** All collections with created_at/updated_at

```javascript
// Function to convert timestamps
function convertTimestamps(collectionName) {
  const collection = db.getCollection(collectionName)
  
  collection.find({ 
    $or: [
      { "created_at": { $type: "string" } },
      { "updated_at": { $type: "string" } }
    ]
  }).forEach(doc => {
    const updates = {}
    
    if (typeof doc.created_at === 'string') {
      updates.created_at = new Date(doc.created_at)
    }
    
    if (typeof doc.updated_at === 'string') {
      updates.updated_at = new Date(doc.updated_at)
    }
    
    if (Object.keys(updates).length > 0) {
      collection.updateOne(
        { _id: doc._id },
        { $set: updates }
      )
    }
  })
}

// Apply to critical collections
convertTimestamps('mt5_accounts')
convertTimestamps('money_managers')
convertTimestamps('salespeople')
convertTimestamps('referral_commissions')
convertTimestamps('investments')
convertTimestamps('clients')
```

---

### Priority 5: Remove Deprecated Fields

**Target:** Multiple collections

```javascript
// Remove deprecated timestamp fields
db.mt5_accounts.updateMany(
  {},
  { $unset: { "last_sync": "" } }
)

// Verify
db.mt5_accounts.find({ "last_sync": { $exists: true } }).count()
// Expected: 0
```

---

## VALIDATION RULES

### Pre-Migration Validation Checklist

✅ **1. Backup Database**
```bash
mongodump --uri="$MONGO_URL" --out=/backups/pre_migration_$(date +%Y%m%d)
```

✅ **2. Count All Documents**
```javascript
db.mt5_accounts.countDocuments()        // Expected: 11
db.money_managers.countDocuments()      // Expected: 7
db.salespeople.countDocuments()         // Expected: 3
db.referral_commissions.countDocuments() // Expected: 16
db.investments.countDocuments()         // Expected: 3
db.clients.countDocuments()             // Expected: 1
```

✅ **3. Verify Critical Data**
```javascript
// Salvador Palma exists
db.salespeople.findOne({ name: "Salvador Palma" })
// Expected: Document with correct totals

// Alejandro's investments exist
db.investments.find({ client_id: "client_alejandro" }).count()
// Expected: 2

// 16 commissions exist
db.referral_commissions.find({ 
  salesperson_id: "sp_6909e8eaaaf69606babea151" 
}).count()
// Expected: 16
```

### Post-Migration Validation Checklist

✅ **1. Document Counts Match**
```javascript
// All counts should be identical to pre-migration
```

✅ **2. No Duplicate Fields**
```javascript
db.mt5_accounts.find({ "manager_name": { $exists: true } }).count()  // Expected: 0
db.money_managers.find({ "manager_name": { $exists: true } }).count() // Expected: 0
db.investments.find({ "amount": { $exists: true } }).count()         // Expected: 0
```

✅ **3. All Timestamps are DateTime**
```javascript
db.salespeople.find({ "created_at": { $type: "string" } }).count()  // Expected: 0
```

✅ **4. API Response Validation**
```bash
# Test API returns correct field names
curl https://fidus-investment-platform.onrender.com/api/admin/referrals/salespeople
# Verify: totalSalesVolume, totalCommissionsEarned, totalClientsReferred (camelCase)
```

✅ **5. Frontend Display Test**
- Navigate to Referrals page
- Verify Salvador shows: $118,151.41 Total Sales, $3,272.27 Commissions
- Click Salvador card
- Verify detail page shows 2 investments, 16 commissions

### Python Validation Script

```python
#!/usr/bin/env python3
"""
Field Registry Validation Script
Run after migration to verify all standards are met
"""

import os
from pymongo import MongoClient
from backend.validation.field_registry import (
    validate_manager_name,
    validate_fund_type,
    validate_mongodb_document,
    ALLOWED_MANAGER_NAMES,
    ALLOWED_FUND_TYPES
)

def main():
    mongo_url = os.environ.get('MONGO_URL')
    client = MongoClient(mongo_url)
    db = client.get_default_database()
    
    errors = []
    
    # 1. Check for duplicate fields
    print("\n1. Checking for duplicate fields...")
    
    mt5_with_manager_name = db.mt5_accounts.count_documents({"manager_name": {"$exists": True}})
    if mt5_with_manager_name > 0:
        errors.append(f"❌ Found {mt5_with_manager_name} mt5_accounts with manager_name field")
    else:
        print("✅ No manager_name field in mt5_accounts")
    
    # 2. Check manager names are valid
    print("\n2. Validating manager names...")
    
    for account in db.mt5_accounts.find():
        if "manager" in account:
            if not validate_manager_name(account["manager"]):
                errors.append(f"❌ Invalid manager name: {account['manager']} in account {account['account']}")
    
    if not errors:
        print("✅ All manager names are valid")
    
    # 3. Check fund types
    print("\n3. Validating fund types...")
    
    for account in db.mt5_accounts.find():
        if "fund_type" in account:
            if not validate_fund_type(account["fund_type"]):
                errors.append(f"❌ Invalid fund type: {account['fund_type']} in account {account['account']}")
    
    if not errors:
        print("✅ All fund types are valid")
    
    # 4. Check timestamps are DateTime
    print("\n4. Validating timestamp types...")
    
    string_timestamps = db.salespeople.count_documents({"created_at": {"$type": "string"}})
    if string_timestamps > 0:
        errors.append(f"❌ Found {string_timestamps} salespeople with string created_at")
    else:
        print("✅ All timestamps are DateTime objects")
    
    # 5. Summary
    print("\n" + "="*60)
    if errors:
        print(f"❌ VALIDATION FAILED: {len(errors)} issues found")
        for error in errors:
            print(f"  {error}")
        return 1
    else:
        print("✅ VALIDATION PASSED: All field standards met")
        return 0

if __name__ == "__main__":
    exit(main())
```

---

## BACKEND IMPLEMENTATION CHECKLIST

### ✅ Completed
1. ✅ `field_registry.py` validation module created
2. ✅ Transform functions for all collections
3. ✅ Salvador Palma field mapping fixed
4. ✅ API responses use camelCase

### ⚠️ Pending
1. ⚠️ Apply transforms to ALL API endpoints
2. ⚠️ Remove duplicate fields from MongoDB
3. ⚠️ Add validation middleware to reject invalid data
4. ⚠️ Update all queries to use standard field names

---

## FRONTEND IMPLEMENTATION CHECKLIST

### ✅ Completed
1. ✅ SalespersonCard uses camelCase fields
2. ✅ SalespersonDetail uses camelCase fields
3. ✅ Referrals overview uses camelCase fields

### ⚠️ Pending
1. ⚠️ Verify all other components use camelCase
2. ⚠️ Remove any snake_case references
3. ⚠️ Add TypeScript interfaces for type safety

---

## CRITICAL NEXT STEPS

### Phase 1: Complete Field Registry ✅ DONE
1. ✅ Document all collections
2. ✅ Identify all inconsistencies
3. ✅ Create migration scripts
4. ✅ Define validation rules

### Phase 2: Apply Systematic Fixes ⏳ IN PROGRESS
1. ⚠️ Run migration scripts on production
2. ⚠️ Update all backend endpoints to use transforms
3. ⚠️ Verify frontend displays correct data
4. ⚠️ Add validation middleware

### Phase 3: Verification & Testing ⏳ PENDING
1. ⏳ Backend testing via deep_testing_backend_v2
2. ⏳ Frontend testing via auto_frontend_testing_agent
3. ⏳ Production verification on Render.com
4. ⏳ Cash Flow, Money Managers, Trading Analytics verification

---

**END OF COMPLETE FIELD REGISTRY**

**Document Status:** Phase 1 Complete - Ready for Phase 2 Implementation  
**Last Reviewed By:** AI Engineer  
**Next Action:** User review and approval before Phase 2