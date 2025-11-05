# FIDUS PLATFORM - COMPLETE FIELD REGISTRY

**Version:** 1.0  
**Last Updated:** November 5, 2025  
**Purpose:** Single Source of Truth for all field names across MongoDB, APIs, and Frontend

---

## TABLE OF CONTENTS

1. [Field Naming Standards](#field-naming-standards)
2. [Collection: mt5_accounts](#collection-mt5_accounts)
3. [Collection: money_managers](#collection-money_managers)
4. [Collection: salespeople](#collection-salespeople)
5. [Collection: referral_commissions](#collection-referral_commissions)
6. [Collection: investments](#collection-investments)
7. [Collection: clients](#collection-clients)
8. [Collection: mt5_deals_history](#collection-mt5_deals_history)
9. [Identified Inconsistencies](#identified-inconsistencies)
10. [Migration Required](#migration-required)

---

## FIELD NAMING STANDARDS

### Rule 1: MongoDB Collections
**Standard:** `snake_case` for ALL field names  
**Example:** `account_number`, `manager_name`, `created_at`

### Rule 2: API Responses  
**Standard:** `camelCase` for ALL field names  
**Example:** `accountNumber`, `managerName`, `createdAt`

### Rule 3: Frontend Variables
**Standard:** `camelCase` for ALL variable names  
**Example:** `accountNumber`, `managerName`, `createdAt`

### Rule 4: Transformation Layer
All MongoDB documents MUST be transformed to camelCase before sending to API:

```python
def transform_to_api(mongo_doc):
    """Transform MongoDB snake_case to API camelCase"""
    return {
        "accountNumber": mongo_doc.get("account"),
        "managerName": mongo_doc.get("manager_name"),
        "createdAt": mongo_doc.get("created_at")
    }
```

### Rule 5: Reserved/Forbidden Field Names
**Never use these:**
- `id` (ambiguous - use `_id` in MongoDB or `documentId` in API)
- `type` (Python/JS reserved word - use `record_type`, `fund_type`)
- `class` (reserved word - use `category`, `classification`)

### Rule 6: Enum Values - Manager Names
**Allowed values** (from SYSTEM_MASTER.md Section 5):
```
"UNO14 Manager"
"GoldenTrade Manager"
"Provider1-Assev"
"alefloreztrader"
"TradingHub Gold Provider"
"CP Strategy Provider"
"GoldenTrade" (inactive only)
```

### Rule 7: Enum Values - Fund Types
**Allowed values:**
```
"BALANCE"
"CORE"
"DYNAMIC"
"UNLIMITED"
"SEPARATION"
```

### Rule 8: Enum Values - Status
**Allowed values:**
```
"active"
"inactive"
"pending"
"approved"
"cancelled"
"paid"
```

---

## COLLECTION: mt5_accounts

**Purpose:** Real-time MT5 trading account data from broker

**Document Count:** 11

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| account | Number | Yes | accountNumber | accountNumber | Unique identifier |
| balance | Number | Yes | balance | balance | Current balance |
| equity | Number | Yes | equity | equity | Current equity |
| manager | String | Yes | managerName | managerName | Must be from allowed list |
| manager_name | String | No | managerName | managerName | **DUPLICATE - use manager** |
| fund_type | String | Yes | fundType | fundType | BALANCE\|CORE\|DYNAMIC\|UNLIMITED\|SEPARATION |
| fund_code | String | Yes | fundCode | fundCode | Short code for fund |
| broker | String | Yes | broker | broker | Always "MEXAtlantic" |
| currency | String | Yes | currency | currency | Always "USD" |
| leverage | Number | Yes | leverage | leverage | Account leverage |
| profit | Number | Yes | profit | profit | Realized profit |
| free_margin | Number | Yes | freeMargin | freeMargin | Available margin |
| margin | Number | Yes | margin | margin | Used margin |
| margin_level | Number | Yes | marginLevel | marginLevel | Margin level % |
| num_positions | Number | Yes | numPositions | numPositions | Open positions count |
| client_id | String | Yes | clientId | clientId | Reference to clients collection |
| client_name | String | No | clientName | clientName | Display name |
| initial_allocation | Number | No | initialAllocation | initialAllocation | Starting capital |
| true_pnl | Number | Yes | truePnl | truePnl | Corrected P&L |
| displayed_pnl | Number | Yes | displayedPnl | displayedPnl | Shown P&L |
| profit_withdrawals | Number | No | profitWithdrawals | profitWithdrawals | Withdrawn profits |
| inter_account_transfers | Number | No | interAccountTransfers | interAccountTransfers | Internal transfers |
| connection_status | String | Yes | connectionStatus | connectionStatus | Sync status |
| last_sync | String | No | lastSync | lastSync | **DEPRECATED - use last_sync_timestamp** |
| last_sync_timestamp | DateTime | Yes | lastSyncTimestamp | lastSyncTimestamp | Last sync time |
| created_at | String/DateTime | Yes | createdAt | createdAt | Creation timestamp |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update timestamp |
| data_source | String | Yes | dataSource | dataSource | VPS_LIVE_MT5 |
| synced_from_vps | Boolean | Yes | syncedFromVps | syncedFromVps | VPS sync flag |

**Indexes:**
- `{ "account": 1 }` (unique)
- `{ "fund_type": 1 }`
- `{ "manager": 1 }`

---

## COLLECTION: money_managers

**Purpose:** Money manager profiles and performance tracking

**Document Count:** 7

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| manager_id | String | Yes | managerId | managerId | Unique identifier |
| name | String | Yes | name | name | Must be from allowed manager list |
| manager_name | String | No | managerName | managerName | **DUPLICATE - use name** |
| display_name | String | No | displayName | displayName | Frontend display |
| status | String | Yes | status | status | active\|inactive |
| assigned_accounts | Array | Yes | assignedAccounts | assignedAccounts | MT5 account numbers |
| strategy_name | String | Yes | strategyName | strategyName | Strategy description |
| strategy_description | String | No | strategyDescription | strategyDescription | Detailed description |
| performance_fee_rate | Number | Yes | performanceFeeRate | performanceFeeRate | Decimal (0.15 = 15%) |
| performance_fee_type | String | Yes | performanceFeeType | performanceFeeType | monthly\|quarterly |
| risk_profile | String | Yes | riskProfile | riskProfile | low\|medium\|high |
| broker | String | Yes | broker | broker | Always "MEXAtlantic" |
| profile_type | String | Yes | profileType | profileType | copy_trade\|manual |
| execution_type | String | Yes | executionType | executionType | copy_trade\|manual |
| current_month_profit | Number | Yes | currentMonthProfit | currentMonthProfit | MTD profit |
| current_month_fee_accrued | Number | Yes | currentMonthFeeAccrued | currentMonthFeeAccrued | MTD fees |
| ytd_fees_paid | Number | Yes | ytdFeesPaid | ytdFeesPaid | Year-to-date fees |
| true_pnl | Number | Yes | truePnl | truePnl | Lifetime P&L |
| start_date | DateTime | Yes | startDate | startDate | Manager start date |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update |

**Indexes:**
- `{ "manager_id": 1 }` (unique)
- `{ "status": 1 }`
- `{ "name": 1 }`

---

## COLLECTION: salespeople

**Purpose:** Referral system salespeople/affiliates

**Document Count:** 3

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| salesperson_id | String | Yes | salespersonId | salespersonId | sp_[mongodb_id] |
| name | String | Yes | name | name | Full name |
| email | String | Yes | email | email | Contact email |
| phone | String | No | phone | phone | Contact phone |
| referral_code | String | Yes | referralCode | referralCode | Unique code |
| referral_link | String | Yes | referralLink | referralLink | Full URL with code |
| active | Boolean | Yes | active | active | Active status |
| total_sales_volume | Decimal128 | Yes | totalSalesVolume | totalSalesVolume | Total referred investment amount |
| total_commissions_earned | Decimal128 | Yes | totalCommissionsEarned | totalCommissionsEarned | Total commissions |
| commissions_pending | Decimal128 | Yes | commissionsPending | commissionsPending | Unpaid commissions |
| commissions_paid_to_date | Decimal128 | Yes | commissionsPaidToDate | commissionsPaidToDate | Paid commissions |
| total_clients_referred | Number | Yes | totalClientsReferred | totalClientsReferred | Client count |
| active_clients | Number | Yes | activeClients | activeClients | Active client count |
| active_investments | Number | Yes | activeInvestments | activeInvestments | Active investment count |
| next_commission_date | DateTime | No | nextCommissionDate | nextCommissionDate | Next payment date |
| next_commission_amount | Number | No | nextCommissionAmount | nextCommissionAmount | Next payment amount |
| joined_date | DateTime | Yes | joinedDate | joinedDate | Signup date |
| preferred_payment_method | String | No | preferredPaymentMethod | preferredPaymentMethod | Payment method |
| wallet_details | Object | No | walletDetails | walletDetails | Payment info |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update |

**Indexes:**
- `{ "salesperson_id": 1 }` (unique)
- `{ "referral_code": 1 }` (unique)
- `{ "active": 1 }`

---

## COLLECTION: referral_commissions

**Purpose:** Commission payment tracking for referrals

**Document Count:** 16

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| commission_id | String | Yes | commissionId | commissionId | Unique identifier |
| salesperson_id | String | Yes | salespersonId | salespersonId | Reference to salespeople |
| investment_id | String | Yes | investmentId | investmentId | Reference to investments |
| client_id | String | Yes | clientId | clientId | Reference to clients |
| fund_type | String | Yes | fundType | fundType | FIDUS_CORE\|FIDUS_BALANCE\|etc |
| principal_amount | Decimal128 | Yes | principalAmount | principalAmount | Investment principal |
| interest_amount | Decimal128 | Yes | interestAmount | interestAmount | Interest earned |
| commission_amount | Decimal128 | Yes | commissionAmount | commissionAmount | 10% of interest |
| payment_month | String | Yes | paymentMonth | paymentMonth | Month 1\|Quarter 1\|etc |
| payment_date | DateTime | Yes | paymentDate | paymentDate | Scheduled payment date |
| status | String | Yes | status | status | pending\|approved\|paid\|cancelled |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update |

**Indexes:**
- `{ "salesperson_id": 1, "payment_date": 1 }`
- `{ "status": 1 }`
- `{ "investment_id": 1 }`

---

## COLLECTION: investments

**Purpose:** Client investment records

**Document Count:** 3

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| investment_id | String | Yes | investmentId | investmentId | Unique identifier |
| client_id | String | Yes | clientId | clientId | Reference to clients |
| fund_type | String | Yes | fundType | fundType | FIDUS_CORE\|FIDUS_BALANCE\|etc |
| fund_code | String | Yes | fundCode | fundCode | CORE\|BALANCE\|etc |
| product | String | Yes | product | product | Product name |
| amount | Number | Yes | amount | amount | **DUPLICATE - use principal_amount** |
| principal_amount | Number | Yes | principalAmount | principalAmount | Investment amount |
| current_value | Number | Yes | currentValue | currentValue | Current value |
| status | String | Yes | status | status | active\|inactive\|closed |
| start_date | DateTime | Yes | startDate | startDate | Investment start |
| deposit_date | DateTime | Yes | depositDate | depositDate | Deposit date |
| investment_date | DateTime | Yes | investmentDate | investmentDate | **DUPLICATE - use start_date** |
| interest_start_date | DateTime | Yes | interestStartDate | interestStartDate | Interest accrual start |
| referral_salesperson_id | String | No | referralSalespersonId | referralSalespersonId | Referring salesperson |
| referred_by | String | No | referredBy | referredBy | **DUPLICATE - use referral_salesperson_id** |
| referred_by_name | String | No | referredByName | referredByName | Display name |
| total_interest_earned | Number | Yes | totalInterestEarned | totalInterestEarned | Lifetime interest |
| total_commissions_due | Number | No | totalCommissionsDue | totalCommissionsDue | Total commissions |
| commissions_pending | Number | No | commissionsPending | commissionsPending | Unpaid commissions |
| next_commission_date | DateTime | No | nextCommissionDate | nextCommissionDate | Next payment |
| next_commission_amount | Number | No | nextCommissionAmount | nextCommissionAmount | Next amount |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |
| updated_at | DateTime | Yes | updatedAt | updatedAt | Last update |

**Indexes:**
- `{ "investment_id": 1 }` (unique)
- `{ "client_id": 1 }`
- `{ "referral_salesperson_id": 1 }`
- `{ "fund_type": 1 }`

---

## COLLECTION: clients

**Purpose:** Client profile and contact information

**Document Count:** 1

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| name | String | Yes | name | name | Full name |
| email | String | Yes | email | email | Contact email |
| phone | String | No | phone | phone | Contact phone |
| status | String | Yes | status | status | active\|inactive |
| referral_code | String | No | referralCode | referralCode | Code used |
| referred_by | ObjectId | No | referredBy | referredBy | Salesperson ObjectId |
| referred_by_name | String | No | referredByName | referredByName | Display name |
| referral_date | DateTime | No | referralDate | referralDate | Referral date |
| total_commissions_generated | Number | No | totalCommissionsGenerated | totalCommissionsGenerated | Total commissions |
| commissions_pending | Number | No | commissionsPending | commissionsPending | Unpaid commissions |
| next_commission_date | DateTime | No | nextCommissionDate | nextCommissionDate | Next payment |
| next_commission_amount | Number | No | nextCommissionAmount | nextCommissionAmount | Next amount |
| created_at | DateTime | Yes | createdAt | createdAt | Record creation |

**Indexes:**
- `{ "email": 1 }` (unique)
- `{ "referred_by": 1 }`
- `{ "status": 1 }`

---

## COLLECTION: mt5_deals_history

**Purpose:** Complete trading history from MT5

**Document Count:** 81,127

| MongoDB Field | Type | Required | API Field | Frontend Field | Enum/Notes |
|--------------|------|----------|-----------|----------------|------------|
| _id | ObjectId | Yes | id | id | Auto-generated |
| ticket | Number | Yes | ticket | ticket | Deal ticket number |
| account_number | Number | Yes | accountNumber | accountNumber | MT5 account |
| time | Number | Yes | time | time | Unix timestamp |
| type | Number | Yes | type | type | Deal type code |
| entry | Number | Yes | entry | entry | Entry type |
| symbol | String | No | symbol | symbol | Trading symbol |
| volume | Number | Yes | volume | volume | Lot size |
| price | Number | Yes | price | price | Execution price |
| profit | Number | Yes | profit | profit | Deal profit |
| commission | Number | Yes | commission | commission | Broker commission |
| swap | Number | Yes | swap | swap | Swap/rollover |
| fee | Number | Yes | fee | fee | Additional fees |
| comment | String | No | comment | comment | Deal comment |
| fund_type | String | No | fundType | fundType | Associated fund |
| synced_at | DateTime | Yes | syncedAt | syncedAt | Sync timestamp |
| synced_from_vps | Boolean | Yes | syncedFromVps | syncedFromVps | VPS source flag |

**Indexes:**
- `{ "account_number": 1, "time": -1 }`
- `{ "ticket": 1 }` (unique)
- `{ "synced_at": -1 }`

---

## IDENTIFIED INCONSISTENCIES

### 1. Manager Name Fields
**Issue:** Multiple field names for the same data
- mt5_accounts: `manager` (String)
- mt5_accounts: `manager_name` (String) - **DUPLICATE**
- money_managers: `name` (String)
- money_managers: `manager_name` (String) - **DUPLICATE**

**Standard:**
- MongoDB: `manager_name` (for MT5 accounts), `name` (for money_managers collection)
- API: `managerName`

### 2. Investment Amount Fields
**Issue:** Duplicate fields for principal
- investments: `amount` (Number)
- investments: `principal_amount` (Number) - **DUPLICATE**

**Standard:**
- MongoDB: `principal_amount`
- API: `principalAmount`

### 3. Referral Fields
**Issue:** Multiple ways to store referral link
- investments: `referral_salesperson_id` (String)
- investments: `referred_by` (String) - **DUPLICATE**
- clients: `referred_by` (ObjectId) - **DIFFERENT TYPE**

**Standard:**
- MongoDB: `referral_salesperson_id` (String) for referencing salesperson_id
- API: `referralSalespersonId`

### 4. Timestamp Fields
**Issue:** Inconsistent timestamp field types
- Some collections: `created_at` (String)
- Some collections: `created_at` (DateTime)
- mt5_accounts: `last_sync` (String) vs `last_sync_timestamp` (DateTime)

**Standard:**
- MongoDB: Always use DateTime type for timestamps
- API: Always return ISO 8601 strings

### 5. Account Number Fields
**Issue:** Different field names for MT5 account number
- mt5_accounts: `account` (Number)
- mt5_deals_history: `account_number` (Number)

**Standard:**
- MongoDB: `account` for mt5_accounts collection, `account_number` for related collections
- API: Always `accountNumber`

---

## MIGRATION REQUIRED

### Priority 1: Remove Duplicate Fields (CRITICAL)

**mt5_accounts collection:**
```javascript
// Remove duplicate manager_name field, keep manager
db.mt5_accounts.updateMany(
  {},
  { $unset: { "manager_name": "" } }
)
```

**money_managers collection:**
```javascript
// Remove duplicate manager_name field, keep name
db.money_managers.updateMany(
  {},
  { $unset: { "manager_name": "" } }
)
```

**investments collection:**
```javascript
// Remove duplicate fields
db.investments.updateMany(
  {},
  { 
    $unset: { 
      "amount": "",
      "referred_by": "",
      "investment_date": ""
    }
  }
)
```

### Priority 2: Standardize Timestamp Fields

**Convert all string timestamps to DateTime:**
```javascript
// Example for mt5_accounts
db.mt5_accounts.find({ created_at: { $type: "string" } }).forEach(doc => {
  db.mt5_accounts.updateOne(
    { _id: doc._id },
    { $set: { created_at: new Date(doc.created_at) } }
  )
})
```

### Priority 3: Add Missing Indexes

**All collections need:**
- `{ "created_at": -1 }`
- `{ "updated_at": -1 }`

---

## VALIDATION REQUIRED

After migration, verify:

1. ✅ No duplicate field names in any collection
2. ✅ All timestamps are DateTime type
3. ✅ All manager names from allowed enum list
4. ✅ All fund_type values from allowed enum list
5. ✅ All API responses use camelCase
6. ✅ All frontend components use camelCase
7. ✅ No data loss during migration

---

**END OF FIELD REGISTRY**
