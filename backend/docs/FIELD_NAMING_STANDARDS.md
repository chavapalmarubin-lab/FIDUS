# FIDUS PLATFORM FIELD NAMING STANDARDS

**Date:** October 31, 2025  
**Version:** 1.0  
**Author:** FIDUS Investment Management  

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## NAMING CONVENTION RULES

### Layer-Specific Conventions

**1. MongoDB (Database Layer)**
- Convention: `snake_case`
- Example: `account_number`, `account_balance`, `profit_loss`
- Rationale: MongoDB standard, Python compatibility

**2. Backend API (JSON Responses)**
- Convention: `camelCase`
- Example: `accountNumber`, `accountBalance`, `profitLoss`
- Rationale: JavaScript/JSON standard, frontend compatibility

**3. Frontend (React/JavaScript)**
- Convention: `camelCase` (match API)
- Example: `accountNumber`, `accountBalance`, `profitLoss`
- Rationale: JavaScript standard, consistency with API

**4. Transformation Location**
- Location: Backend API layer
- Method: Use `field_transformers.py` utility functions
- Example: `balance` → `accountBalance`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## STANDARD FIELD NAMES

### MT5 Account Data

| Data                 | MongoDB        | API/Frontend        |
|----------------------|----------------|---------------------|
| Account Number       | `account`      | `accountNumber`     |
| Account Balance      | `balance`      | `accountBalance`    |
| Account Equity       | `equity`       | `accountEquity`     |
| Profit/Loss          | `profit`       | `profitLoss`        |
| Used Margin          | `margin`       | `usedMargin`        |
| Free Margin          | `margin_free`  | `freeMargin`        |
| Margin Level         | `margin_level` | `marginLevel`       |
| Leverage             | `leverage`     | `accountLeverage`   |
| Currency             | `currency`     | `currency`          |
| Server               | `server`       | `serverName`        |
| Broker               | `company`      | `brokerName`        |
| Fund Type            | `fund_type`    | `fundType`          |
| Manager Name         | `manager_name` | `managerName`       |
| Target Amount        | `target_amount`| `targetAmount`      |
| Last Update          | `updated_at`   | `lastUpdate`        |
| TRUE P&L             | (calculated)   | `truePnl`           |
| Return %             | (calculated)   | `returnPercentage`  |

### Investment Data

| Data              | MongoDB            | API/Frontend         |
|-------------------|--------------------|----------------------|
| Investment ID     | `_id`              | `investmentId`       |
| Client ID         | `client_id`        | `clientId`           |
| Principal Amount  | `principal_amount` | `principalAmount`    |
| Current Value     | `current_value`    | `currentValue`       |
| Interest Rate     | `interest_rate`    | `interestRate`       |
| Interest Earned   | `interest_earned`  | `interestEarned`     |
| Investment Date   | `investment_date`  | `investmentDate`     |
| Maturity Date     | `maturity_date`    | `maturityDate`       |
| Fund Type         | `fund_type`        | `fundType`           |
| Status            | `status`           | `status`             |

### Client Data

| Data                  | MongoDB                | API/Frontend           |
|-----------------------|------------------------|------------------------|
| Client ID             | `_id`                  | `clientId`             |
| Email                 | `email`                | `email`                |
| First Name            | `first_name`           | `firstName`            |
| Last Name             | `last_name`            | `lastName`             |
| Full Name             | `full_name`            | `fullName`             |
| Phone                 | `phone_number`         | `phoneNumber`          |
| Total Invested        | `total_invested`       | `totalInvested`        |
| Interest Earned       | `total_interest_earned`| `totalInterestEarned`  |
| Withdrawals           | `total_withdrawals`    | `totalWithdrawals`     |

### Manager Data

| Data              | MongoDB           | API/Frontend       |
|-------------------|-------------------|--------------------|
| Manager ID        | `manager_id`      | `managerId`        |
| Manager Name      | `manager_name`    | `managerName`      |
| Strategy          | `strategy`        | `strategy`         |
| Risk Level        | `risk_level`      | `riskLevel`        |
| TRUE P&L          | (calculated)      | `managerTruePnl`   |
| Return %          | (calculated)      | `managerReturnPercentage` |
| Assigned Accounts | `assigned_accounts`| `assignedAccounts` |

### P&L Calculation Fields

| Data              | Calculator Output      | API/Frontend           |
|-------------------|------------------------|------------------------|
| Initial Allocation| `initial_allocation`   | `initialAllocation`    |
| Total Deposits    | `total_deposits`       | `totalDeposits`        |
| Total Withdrawals | `total_withdrawals`    | `totalWithdrawals`     |
| Current Equity    | `current_equity`       | `currentEquity`        |
| TRUE P&L          | `true_pnl`             | `truePnl`              |
| Return %          | `return_percentage`    | `returnPercentage`     |
| Is Profitable     | `is_profitable`        | `isProfitable`         |
| Capital In        | `total_capital_in`     | `totalCapitalIn`       |
| Capital Out       | `total_capital_out`    | `totalCapitalOut`      |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## USAGE GUIDELINES

### Backend API Development

**DO:**
- ✅ Always use `field_transformers.py` functions for responses
- ✅ Return `camelCase` fields in all API responses
- ✅ Store data in `snake_case` in MongoDB
- ✅ Add null safety checks before transformations
- ✅ Document transformations in endpoint docstrings

**DON'T:**
- ❌ Return `snake_case` fields from API
- ❌ Mix naming conventions in same response
- ❌ Hardcode field name transformations
- ❌ Skip null checks before accessing nested fields

**Example:**
```python
from app.utils.field_transformers import transform_mt5_account

@router.get("/api/mt5/accounts")
async def get_accounts():
    # Get from database (snake_case)
    db_accounts = await db.mt5_accounts.find().to_list(length=100)
    
    # Transform to API format (camelCase)
    api_accounts = [transform_mt5_account(acc) for acc in db_accounts]
    
    return {
        "success": True,
        "accounts": api_accounts  # camelCase
    }
```

### Frontend Development

**DO:**
- ✅ Use `camelCase` for all variables
- ✅ Match API field names exactly
- ✅ Use optional chaining (`?.`) for null safety
- ✅ Provide default values with nullish coalescing (`??`)
- ✅ Format numbers with `.toLocaleString()` or `.toFixed()`

**DON'T:**
- ❌ Use `snake_case` in frontend code
- ❌ Assume fields are always present
- ❌ Display raw numbers without formatting
- ❌ Use different names than API provides

**Example:**
```javascript
// ✅ CORRECT
const { accountNumber, accountBalance, truePnl } = account;
<div>${accountBalance?.toLocaleString() ?? '0.00'}</div>
<div>{truePnl?.toFixed(2) ?? '0.00'}%</div>

// ❌ WRONG
const { account, balance } = account;  // Wrong field names
<div>${balance.toFixed(2)}</div>  // No null safety
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ADDING NEW FIELDS

### Step-by-Step Process

**1. Define Field in All Layers**
```
MongoDB:     new_field_name
API:         newFieldName
Frontend:    newFieldName
```

**2. Add to Field Transformer**
```python
# In app/utils/field_transformers.py
def transform_mt5_account(db_account: Dict[str, Any]) -> Dict[str, Any]:
    return {
        # ... existing fields ...
        "newFieldName": db_account.get("new_field_name"),
    }
```

**3. Update API Endpoint**
```python
# Use transformer (automatically includes new field)
accounts = [transform_mt5_account(acc) for acc in db_accounts]
```

**4. Update Frontend**
```javascript
// Destructure new field
const { accountNumber, newFieldName } = account;

// Use with null safety
<div>{newFieldName ?? 'N/A'}</div>
```

**5. Test**
- ✅ Check database has field
- ✅ Check API returns field with correct name
- ✅ Check frontend displays field
- ✅ Check null/undefined handling

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## COMMON MISTAKES & FIXES

### Issue #1: Field Name Mismatches

**Problem:**
```javascript
// Frontend expects camelCase but gets snake_case
const { accountNumber } = account;  // undefined!
```

**Cause:** API not using field transformer

**Fix:**
```python
# In backend
return transform_mt5_account(db_account)  # ✅
```

### Issue #2: Null/Undefined Errors

**Problem:**
```javascript
// Crashes if account or balance is undefined
<div>${account.accountBalance.toFixed(2)}</div>
```

**Fix:**
```javascript
<div>${account?.accountBalance?.toFixed(2) ?? '0.00'}</div>  // ✅
```

### Issue #3: Mixed Naming in Same Component

**Problem:**
```javascript
// Component uses both styles
const { account } = data;  // snake_case
const { accountNumber } = otherData;  // camelCase
```

**Fix:** Standardize to camelCase everywhere
```javascript
const { accountNumber } = data;  // ✅
const { accountNumber: otherAccountNumber } = otherData;  // ✅
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## FIELD REFERENCE QUICK LOOKUP

### MT5 Quick Reference
```
account         → accountNumber
balance         → accountBalance
equity          → accountEquity
profit          → profitLoss
margin          → usedMargin
margin_free     → freeMargin
leverage        → accountLeverage
fund_type       → fundType
manager_name    → managerName
updated_at      → lastUpdate
```

### Investment Quick Reference
```
client_id         → clientId
principal_amount  → principalAmount
interest_rate     → interestRate
investment_date   → investmentDate
```

### P&L Quick Reference
```
true_pnl            → truePnl
return_percentage   → returnPercentage
total_withdrawals   → totalWithdrawals
initial_allocation  → initialAllocation
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## VERSION HISTORY

- **v1.0** (October 31, 2025): Initial field naming standards established
  - Defined naming conventions for all layers
  - Created comprehensive field reference
  - Established transformation guidelines
  - Documented common issues and fixes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**IMPORTANT:** This document is the SINGLE SOURCE OF TRUTH for field naming across the FIDUS platform. All new development must follow these standards.
