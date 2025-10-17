# FIDUS Field Naming Conventions

## Standard Field Names - Phase 2 Complete

This document defines the standardized field naming conventions implemented across the FIDUS platform.

---

## 1. Account Fields

**Standard:** `account_number`
- ✅ Use: `account_number`
- ❌ Avoid: `account`, `mt5_login`, `login`

**Context:**
- All MT5 account identifiers use `account_number`
- Database may store as `account`, but APIs return `account_number`

---

## 2. Fund Fields

**Standard:** `fund_code`
- ✅ Use: `fund_code`
- ❌ Avoid: `fund_type`

**Values:** `BALANCE`, `CORE`, `SEPARATION`

**Context:**
- Database stores as `fund_type`
- Backend translates to `fund_code` in API responses
- Frontend only uses `fund_code`

---

## 3. Profit/Loss Fields

**Standards:**
- `profit` - Raw profit from MT5 deal data (unchanged)
- `account_profit_loss` - Individual account P&L
- `total_profit_loss` - Aggregated P&L across accounts
- `corrected_profit_loss` - Adjusted/true P&L values

**Deprecated:**
- ❌ `mt5_trading_pnl` → Use `total_profit_loss`
- ❌ `true_pnl` → Use `corrected_profit_loss`
- ❌ `total_pnl` → Use `total_profit_loss`

---

## 4. Date/Time Fields

**Standards:** ISO 8601 format
- `created_at` - When record was created ("2025-10-17T10:30:00Z")
- `updated_at` - When record was last modified
- `synced_at` - When data was synced from external source

**Format:** Always ISO 8601 with UTC timezone

**Deprecated:**
- ❌ `last_update` → Use `updated_at`
- ❌ `last_sync` → Use `synced_at`
- ❌ Unix timestamps → Use ISO 8601 strings

---

## 5. API Response Structure

**Standard:** Flat structure (Phase 2 Task #3)

**✅ Preferred:**
```json
{
  "total_profit_loss": 36893.50,
  "broker_rebates": 441.0,
  "client_interest_obligations": 33000.00
}
```

**❌ Deprecated (nested):**
```json
{
  "fund_assets": {
    "total_profit_loss": 36893.50
  },
  "liabilities": {
    "client_interest_obligations": 33000.00
  }
}
```

**Note:** Nested structures maintained for backward compatibility but marked as deprecated.

---

## 6. Aggregate Fields

**Standard:** Always use `total_` prefix

**✅ Use:**
- `total_profit_loss`
- `total_equity`
- `total_accounts`
- `total_deals`

**❌ Avoid:**
- `aggregated_*`
- `sum_*`
- `combined_*`

---

## 7. Interest Fields

**Standards:**
- `client_earned_interest` - Interest earned by clients
- `broker_interest` - Interest from broker
- `separation_interest` - Separation account interest
- `accrued_interest` - Interest accrued but not yet paid
- `interest_earned` - General interest earned (context-dependent)

**Context:** Already well-standardized

---

## 8. Manager/Strategy Fields

**Standard:** `manager` terminology

**✅ Use:**
- `manager_name`
- `manager_id`
- `manager_code`

**❌ Avoid:**
- `strategy_name`
- `strategy_id`

---

## 9. Balance/Value Fields

**Context-specific naming:**
- `account_balance` - Bank or account balance
- `current_equity` - Trading account equity
- `portfolio_value` - Total investment value
- `available_balance` - Available for withdrawal

---

## Implementation Status

- ✅ Phase 1: All calculations moved to backend
- ✅ Phase 2: All field names standardized
- ✅ Backend: 20+ files updated
- ✅ Frontend: 10+ components updated
- ✅ Total instances: 100+ field references updated

---

## Migration Notes

**Backend Translation Layer:**
- Backend reads legacy field names from MongoDB
- Backend returns standardized names in API responses
- No database migration required

**Frontend Compatibility:**
- Frontend uses standardized names with fallback to legacy
- Gradual migration ensures zero downtime

---

**Last Updated:** October 17, 2025
**Phase:** Phase 2 Complete
**Status:** Production Ready ✅
