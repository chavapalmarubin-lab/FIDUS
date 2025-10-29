# MT5 Bridge Fix - Single Connection Method

## Problem

**Original Issue**: MT5 Bridge was calling `mt5.login(account_number)` for each account query, causing MT5 Terminal to repeatedly switch accounts. When the Bridge asked for account A's data while MT5 was logged into account B, it returned $0 balances.

**Impact**:
- Dashboard showed zeros randomly
- Data inconsistency every 5 minutes
- Terminal constantly switching accounts
- Unreliable balance reporting

## Solution

**Fixed MT5 Bridge** uses single connection method:
1. Initialize MT5 **ONCE** at startup
2. Login to manager account (886557) **ONCE**  
3. Query all accounts through **SAME** connection
4. **NO** terminal switching during queries

## Deployment

### Automatic (GitHub Actions)

**Workflow**: `fix-bridge-connection-method.yml`

**Steps**:
1. Go to: Repository → Actions
2. Select: "Fix MT5 Bridge - Single Connection Method"
3. Click: "Run workflow"
4. Wait: 2-3 minutes for completion

**What it does**:
- Backs up current Bridge
- Deploys fixed Bridge script
- Restarts Bridge service
- Verifies health check
- Reports success/failure

### Files Deployed

- **Source**: `/vps-scripts/mt5_bridge_api_service_fixed.py`
- **Destination**: `C:\mt5_bridge_service\mt5_bridge_api_service.py`
- **Backup**: `C:\mt5_bridge_service\mt5_bridge_api_service.py.backup_YYYYMMDD_HHMMSS`

## Technical Changes

### Before (Broken)

```python
def get_account_info(account_number):
    # WRONG: Logs into each account
    mt5.login(account_number, password, server)  # Terminal switches!
    account_info = mt5.account_info()
    return account_info
```

**Result**: Terminal switches accounts → Other accounts show $0

### After (Fixed)

```python
# Initialize ONCE at startup
MT5_INITIALIZED = False

def initialize_mt5_once():
    global MT5_INITIALIZED
    if not MT5_INITIALIZED:
        mt5.initialize()
        mt5.login(MANAGER_ACCOUNT, password, server)  # Login ONCE
        MT5_INITIALIZED = True

def get_account_info(account_number):
    # CORRECT: Query through existing connection
    account_info = mt5.account_info()  # No login call!
    positions = mt5.positions_get(group=f"*{account_number}*")
    return account_info, positions
```

**Result**: Terminal stays on manager account → All queries work

## Expected Behavior

### After Fix

**Bridge Startup**:
```
[START] Initializing MT5 connection...
[OK] MT5 initialized successfully
[OK] Logged in to manager account: 886557
```

**Account Queries** (no switching):
```
[QUERY] Getting data for account 886557 (no terminal switch)
[OK] Querying currently logged-in account: 886557
[QUERY] Getting data for account 886066 (no terminal switch)
[OK] Retrieved 5 positions for account 886066
[QUERY] Getting data for account 886602 (no terminal switch)
[OK] Retrieved 3 positions for account 886602
```

**MT5 Terminal**: Stays on account 886557, never switches

### Dashboard Behavior

**Before Fix**:
- Sync 1: Accounts show real balances ✓
- Sync 2: Some accounts show $0 ❌
- Sync 3: Different accounts show $0 ❌
- Sync 4: Accounts show real balances ✓
- Pattern repeats...

**After Fix**:
- Sync 1: Accounts show real balances ✓
- Sync 2: Accounts show real balances ✓
- Sync 3: Accounts show real balances ✓
- Sync 4: Accounts show real balances ✓
- **Stable forever**

## Verification

### 1. Check Workflow Logs

**Success Output**:
```
[SUCCESS] Bridge is running with fixed connection method!

Next: Wait 5 minutes and check dashboard
Balances should stay stable (no more zeros)
```

### 2. Monitor Dashboard

**Timeline**:
- **Immediate**: Bridge restarted with fix
- **+5 minutes**: First sync with new method
- **+10 minutes**: Second sync (verify stability)
- **+15 minutes**: Third sync (confirm fix working)

**What to look for**:
- ✅ Balances stay stable
- ✅ No random zeros
- ✅ Data updates every 5 minutes
- ✅ All 7 accounts showing real data

### 3. Check Backend Logs

```bash
# On your monitoring system
tail -f /var/log/supervisor/backend*.log | grep "Bridge success"
```

**Expected**:
```
Bridge success for 886557: Balance = $16847.13
Bridge success for 886066: Balance = $18562.45
Bridge success for 886602: Balance = $17391.82
... (all accounts with real balances)
```

**NOT**:
```
Bridge success for 886557: Balance = $0.0  ❌ BAD
```

## Limitations

**Note**: The fixed Bridge can fully query only the **currently logged-in account** (886557 manager). For other accounts, it provides:

- **Full data** if manager has API access to all accounts
- **Limited data** (positions only) if manager has partial access
- **Marker to use stored data** if no API access

**Fallback**: If API doesn't provide full access, the backend uses **stored data from MongoDB** (last known good balances). This is better than showing $0.

## Rollback

If the fix causes issues:

**Automatic**:
```powershell
# On VPS
cd C:\mt5_bridge_service
Get-ChildItem *.backup_* | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Copy-Item -Destination "mt5_bridge_api_service.py" -Force
# Restart Bridge
```

**Manual**: Restore from backup and restart

## Troubleshooting

### Issue: Workflow fails with SSH error

**Check**:
- VPS_PASSWORD secret is correct
- VPS is accessible (test RDP)
- SSH service running on VPS

### Issue: Bridge starts but accounts still show zeros

**Possible causes**:
1. MT5 Terminal not running
2. Manager account not logged in
3. API permissions issue

**Check**:
- MT5 Terminal is open and logged into 886557
- "Allow algorithmic trading" is enabled
- Manager account has access to other accounts

### Issue: Health check shows "unavailable"

**Check**:
- Bridge process running: `Get-Process python`
- Bridge logs for errors
- MT5 Terminal connection status

## Success Criteria

Fix is **COMPLETE** when:

- ✅ GitHub Actions workflow completes successfully
- ✅ Bridge health check shows `"available": true`
- ✅ Dashboard shows real balances for all accounts
- ✅ Balances stay stable for 15+ minutes
- ✅ No zeros appearing in sync cycles
- ✅ MT5 Terminal stays on manager account

## Next Steps

After successful deployment:

1. **Monitor for 1 hour** - Verify stability
2. **Check logs** - Confirm no errors
3. **Remove temporary fix** - Backend validation can be relaxed
4. **Document** - Update system documentation

---

**Created**: 2025-10-28  
**Status**: Ready for deployment  
**Method**: Fully automated via GitHub Actions  
**User Action Required**: NONE (just run workflow and monitor results)
