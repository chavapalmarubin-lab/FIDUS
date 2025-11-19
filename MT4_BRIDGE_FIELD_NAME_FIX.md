# MT4 Bridge Field Name Correction

## 🐛 Critical Bug Fixed

**File:** `/app/vps-scripts/mt4_bridge_api_service.py`
**Line:** 201
**Issue:** Attempting to access `document['fundType']` (camelCase) instead of `document['fund_type']` (snake_case)

### Before (INCORRECT):
```python
config_doc = {
    'account_number': account_data['account'],
    'server': account_data['server'],
    'fund_type': document['fundType'],  # ❌ KeyError - 'fundType' doesn't exist
    'platform': 'MT4',
    'enabled': True,
    'updated_at': current_time.isoformat()
}
```

### After (CORRECT):
```python
config_doc = {
    'account_number': account_data['account'],
    'server': account_data['server'],
    'fund_type': document['fund_type'],  # ✅ Correct - matches snake_case
    'platform': 'MT4',
    'enabled': True,
    'updated_at': current_time.isoformat()
}
```

## ✅ Verified Field Names Compliance

All field names in both MT4 bridge files now comply with **Python MetaTrader5 API Standards** (snake_case):

### Python Service (`mt4_bridge_api_service.py`)
| Field | Status |
|-------|--------|
| `account` | ✅ Correct |
| `name` | ✅ Correct |
| `server` | ✅ Correct |
| `balance` | ✅ Correct |
| `equity` | ✅ Correct |
| `margin` | ✅ Correct |
| `free_margin` | ✅ Correct (NOT freeMargin) |
| `profit` | ✅ Correct |
| `currency` | ✅ Correct |
| `leverage` | ✅ Correct |
| `credit` | ✅ Correct |
| `fund_type` | ✅ Correct (NOT fundType) |
| `platform` | ✅ Correct |
| `updated_at` | ✅ Correct |

### MQL4 Expert Advisor (`MT4_Python_Bridge.mq4`)
The EA already sends correct JSON field names:
- Line 122: `"free_margin"` ✅
- Line 129: `"fund_type"` ✅
- All other fields match Python MT5 API standards ✅

## 📊 Document Structure in MongoDB

### Collection: `mt5_accounts`
Document ID Format: `"MT4_33200931"`

```json
{
  "_id": "MT4_33200931",
  "account": 33200931,
  "name": "Money Manager MT4 Account",
  "server": "MEXAtlantic-Real",
  "balance": 0.0,
  "equity": 0.0,
  "margin": 0.0,
  "free_margin": 0.0,
  "profit": 0.0,
  "currency": "USD",
  "leverage": 100,
  "credit": 0.0,
  "fund_type": "MONEY_MANAGER",
  "platform": "MT4",
  "updated_at": "2025-01-XX..."
}
```

## 🎯 Success Criteria (from User Spec)

- [x] All field names match Python MetaTrader5 API
- [x] Document _id format is "MT4_33200931"
- [x] Platform field is "MT4"
- [x] Uses upsert to prevent duplicates
- [ ] **PENDING:** Backend testing to verify MongoDB writes
- [ ] **PENDING:** VPS deployment for live MT4 integration

## 📝 Next Steps

1. ✅ **COMPLETED:** Fix field name bug in Python service
2. 🔄 **IN PROGRESS:** Backend testing to verify data flow
3. ⏳ **UPCOMING:** VPS deployment and MT4 EA attachment
4. ⏳ **UPCOMING:** Update SYSTEM_MASTER.md documentation

---

**Fixed by:** E1 Fork Agent
**Date:** 2025-01-XX
**Status:** Ready for Testing
