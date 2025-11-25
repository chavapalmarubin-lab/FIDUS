# MT5 Watchdog tzinfo Bug Fix

## Problem
After the Cash Flow API simplification, the MT5 watchdog service started failing with:
```
ERROR:mt5_watchdog:[MT5 WATCHDOG] Data freshness check failed: 'str' object has no attribute 'tzinfo'
```

This caused all real-time financial data (balance, equity) to become stale.

## Root Cause
The code in multiple files was attempting to access `.tzinfo` attribute on datetime fields that were **strings** (ISO format) instead of Python `datetime` objects.

When timestamps are retrieved from MongoDB, they can come back as either:
- Python `datetime` objects (when recently set in Python)
- ISO format strings like `"2025-11-25T20:01:59.930518876Z"` (when stored as strings)

The watchdog code didn't handle the string case, causing `AttributeError`.

## Files Fixed

### 1. `/app/backend/services/mt5_watchdog.py` (line 283)
**Before:**
```python
if last_sync.tzinfo is None:
    last_sync = last_sync.replace(tzinfo=timezone.utc)
```

**After:**
```python
# Convert string to datetime if needed
if isinstance(last_sync, str):
    last_sync = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))

if last_sync.tzinfo is None:
    last_sync = last_sync.replace(tzinfo=timezone.utc)
```

### 2. `/app/backend/mt5_watchdog.py` (line 116)
**Before:**
```python
if last_update.tzinfo is None:
    last_update = last_update.replace(tzinfo=timezone.utc)
```

**After:**
```python
# Convert string to datetime if needed
if isinstance(last_update, str):
    last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))

if last_update.tzinfo is None:
    last_update = last_update.replace(tzinfo=timezone.utc)
```

### 3. `/app/backend/health_checks.py` (lines 101 and 200)
Applied the same string-to-datetime conversion before accessing `.tzinfo`.

## Verification
After fixes:
- ✅ No more `'str' object has no attribute 'tzinfo'` errors
- ✅ MT5 watchdog monitoring loop runs successfully
- ✅ All datetime comparisons work correctly

## Current Status
- **Code bug:** FIXED ✅
- **MT5 Bridge connectivity:** Still failing (separate infrastructure issue - VPS unreachable at 92.118.45.135:8000)

The code is now robust and handles both string and datetime objects correctly.
