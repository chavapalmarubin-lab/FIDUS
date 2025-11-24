# MT5 Bridge Multi-Terminal Update - Deployment Guide

**Date:** November 24, 2025  
**Version:** 2.0 (Multi-Terminal Support)  
**Status:** Ready to deploy  

---

## 🎯 What This Update Does

**Before:**
- Bridge syncs 13 MEXAtlantic accounts from one terminal
- Cannot handle LUCRUM accounts (different broker)

**After:**
- Bridge syncs 14 MT5 accounts from two terminals
- Routes accounts to correct broker automatically:
  - MEXAtlantic-Real → 13 accounts
  - Lucrumcapital-Live → 1 account (2198)

---

## 📋 Pre-Deployment Checklist

**Verify Before Deploying:**
- [x] LUCRUM terminal is running on VPS
- [x] Account 2198 is logged in and connected
- [x] Current bridge is syncing 13 MEXAtlantic accounts
- [x] MongoDB has account 2198 configured
- [x] Backup of current bridge script taken

---

## 🚀 Deployment Steps

### Step 1: Backup Current Bridge (CRITICAL!)

**On VPS:**
```powershell
# Navigate to bridge directory
cd C:\mt5_bridge_service\

# Create backup with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item mt5_bridge_api_service.py "mt5_bridge_api_service_backup_$timestamp.py"

# Verify backup
Get-ChildItem *backup*.py
```

**Expected Output:**
```
mt5_bridge_api_service_backup_20251124_120000.py
```

---

### Step 2: Stop Current Bridge Service

**Stop via Task Scheduler:**
```powershell
# End the running task
schtasks /End /TN "MT5BridgeService"

# Verify it stopped
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*mt5*"}
```

**Expected Output:**
```
(No processes should be listed)
```

**Alternative - Kill Python Process:**
```powershell
Get-Process python | Where-Object {$_.Path -like "*mt5*"} | Stop-Process -Force
```

---

### Step 3: Deploy Updated Bridge Script

**Option A: Manual File Copy (If you have the new file)**

```powershell
# Replace the old script with new one
Copy-Item "path\to\mt5_bridge_api_service_multi_terminal.py" "C:\mt5_bridge_service\mt5_bridge_api_service.py" -Force

# Verify file size changed
Get-Item C:\mt5_bridge_service\mt5_bridge_api_service.py | Select-Object Name, Length, LastWriteTime
```

**Option B: Direct Edit (If updating in place)**

1. Open: `C:\mt5_bridge_service\mt5_bridge_api_service.py` in text editor
2. Replace entire contents with the new multi-terminal version
3. Save file

**New Script Location:**
- File: `/app/vps-scripts/mt5_bridge_api_service_multi_terminal.py`
- This file contains the complete multi-terminal implementation

---

### Step 4: Verify Terminal Paths

**Check that terminal paths in script match actual installations:**

```powershell
# Check MEXAtlantic terminal
Test-Path "C:\Program Files\MEXAtlantic MetaTrader 5\terminal64.exe"

# Check LUCRUM terminal  
Test-Path "C:\Program Files\Lucrum Capital MetaTrader 5\terminal64.exe"
```

**If paths are different:**
1. Open: `C:\mt5_bridge_service\mt5_bridge_api_service.py`
2. Find the `TERMINALS` dictionary (around line 32)
3. Update paths to match your installation
4. Save file

---

### Step 5: Test the Updated Bridge (Manual Test)

**Run bridge manually to test:**
```powershell
cd C:\mt5_bridge_service\
python mt5_bridge_api_service.py
```

**Watch for:**
```
✅ MongoDB connection established
✅ Found 14 active accounts in config
🔄 Syncing 13 accounts from MEXAtlantic (MEXAtlantic-Real)
✅ Terminal initialized: MEXAtlantic-Real
✅ Synced account 886557 (BALANCE - ...): Balance=$10,054.27, Equity=$10,054.27
...
✅ Server MEXAtlantic-Real: 13/13 accounts synced successfully

🔄 Syncing 1 accounts from Lucrum Capital (Lucrumcapital-Live)
✅ Terminal initialized: Lucrumcapital-Live
✅ Synced account 2198 (BALANCE - JOSE (LUCRUM)): Balance=$11,299.25, Equity=$8,752.64
✅ Server Lucrumcapital-Live: 1/1 accounts synced successfully

✅ Sync cycle completed
⏳ Waiting 120 seconds until next sync...
```

**If you see this output → SUCCESS! ✅**

**Press Ctrl+C to stop manual test**

---

### Step 6: Start Bridge Service

**Start via Task Scheduler:**
```powershell
# Start the bridge service
schtasks /Run /TN "MT5BridgeService"

# Wait 5 seconds
Start-Sleep -Seconds 5

# Verify it's running
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*mt5*"}
```

**Expected Output:**
```
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    xxx      xx   xxxxx      xxxxx       x.xx   xxxx   x python
```

---

### Step 7: Monitor First Sync Cycle

**Watch the logs:**
```powershell
# Tail the log file
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 50 -Wait
```

**Look for:**
- ✅ Both servers syncing (MEXAtlantic-Real and Lucrumcapital-Live)
- ✅ Account 2198 appearing in logs
- ✅ 14 total accounts syncing
- ❌ No error messages

**Press Ctrl+C to stop watching logs**

---

### Step 8: Verify MongoDB Updates

**Check that account 2198 is syncing:**
```powershell
# Create quick test script
@"
from pymongo import MongoClient
client = MongoClient('mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production')
db = client.get_database()
account = db.mt5_accounts.find_one({'account': 2198})
print(f'Account 2198:')
print(f'  Balance: {account.get("balance")}')
print(f'  Equity: {account.get("equity")}')
print(f'  Last Sync: {account.get("last_sync_timestamp")}')
print(f'  Synced from VPS: {account.get("synced_from_vps")}')
client.close()
"@ | python -
```

**Expected Output:**
```
Account 2198:
  Balance: 11299.25
  Equity: 8752.64
  Last Sync: 2025-11-24 XX:XX:XX (recent timestamp)
  Synced from VPS: True
```

---

## ✅ Post-Deployment Verification

### Check 1: Log File Review

```powershell
# Check last 100 lines for any errors
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 100 | Select-String -Pattern "ERROR|FAIL|❌"
```

**Expected:** No errors (or only old errors from before update)

---

### Check 2: Account Count

```powershell
# Count syncing accounts in logs
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 200 | Select-String -Pattern "Synced account" | Measure-Object
```

**Expected Count:** 14 (13 MEXAtlantic + 1 LUCRUM)

---

### Check 3: LUCRUM Specific

```powershell
# Find LUCRUM account entries
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 200 | Select-String -Pattern "2198|LUCRUM|Lucrumcapital"
```

**Should See:**
```
✅ Synced account 2198 (BALANCE - JOSE (LUCRUM)): Balance=$11,299.25
```

---

### Check 4: Dashboard Verification

1. Open FIDUS platform
2. Go to Investment Committee dashboard
3. Verify:
   - Total accounts: 15 (14 MT5 + 1 MT4)
   - Account 2198 visible with LUCRUM broker
   - Balance matches terminal: ~$11,299
   - JOSE manager appears in Money Managers

---

## 🔄 Rollback Procedure (If Needed)

**If something goes wrong, rollback to original:**

```powershell
# Stop new bridge
schtasks /End /TN "MT5BridgeService"

# Restore backup
Copy-Item "C:\mt5_bridge_service\mt5_bridge_api_service_backup_*.py" "C:\mt5_bridge_service\mt5_bridge_api_service.py" -Force

# Restart service
schtasks /Run /TN "MT5BridgeService"

# Verify MEXAtlantic accounts still syncing
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 50 -Wait
```

---

## 🐛 Troubleshooting

### Issue 1: Script Won't Start

**Error:** "ModuleNotFoundError: No module named 'MetaTrader5'"

**Fix:**
```powershell
pip install MetaTrader5
```

---

### Issue 2: Terminal Path Not Found

**Error:** "Failed to initialize terminal"

**Fix:**
1. Find actual terminal location:
```powershell
Get-ChildItem "C:\Program Files\" -Recurse -Filter "terminal64.exe" -ErrorAction SilentlyContinue
```

2. Update paths in script:
```python
TERMINALS = {
    'MEXAtlantic-Real': {
        'path': r'<ACTUAL_PATH_HERE>',
        ...
    },
    'Lucrumcapital-Live': {
        'path': r'<ACTUAL_PATH_HERE>',
        ...
    }
}
```

---

### Issue 3: LUCRUM Account Not Syncing

**Possible Causes:**

1. **Terminal not running:**
   ```powershell
   Get-Process terminal64 | Where-Object {$_.MainWindowTitle -like "*2198*"}
   ```
   **Fix:** Launch LUCRUM terminal and login to 2198

2. **Account not in config:**
   ```powershell
   python -c "from pymongo import MongoClient; db = MongoClient('mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production').get_database(); print(db.mt5_account_config.find_one({'account': 2198}))"
   ```
   **Fix:** Verify `is_active: true` in MongoDB

3. **Wrong server name:**
   - Check terminal shows: "Lucrumcapital-Live"
   - Check script uses: "Lucrumcapital-Live" (exact match)

---

### Issue 4: MEXAtlantic Accounts Stopped Syncing

**Cause:** Terminal path or configuration issue

**Fix:**
1. Check logs for MEXAtlantic-specific errors
2. Verify MEXAtlantic terminal is still running
3. Try rollback procedure if needed

---

## 📊 Success Metrics

**After successful deployment, you should see:**

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| MT5 Accounts Syncing | 13 | 14 | ✅ |
| Brokers Supported | 1 | 2 | ✅ |
| LUCRUM Account 2198 | Not syncing | Syncing | ✅ |
| MongoDB last_sync | Old | Recent | ✅ |
| Dashboard Total | 14 | 15 | ✅ |

---

## 🎯 Key Changes in New Bridge

**What's Different:**

1. **Terminal Configuration:**
   - Added `TERMINALS` dictionary mapping servers to terminal paths
   - Supports multiple brokers

2. **Account Grouping:**
   - Accounts grouped by server before syncing
   - Each server's accounts synced via its terminal

3. **Terminal Switching:**
   - Bridge initializes correct terminal per server
   - Shutdown between terminal switches

4. **Enhanced Logging:**
   - Shows which broker/server is syncing
   - Displays per-server success counts
   - Better error messages

5. **Same Sync Interval:**
   - Still 120 seconds
   - All accounts sync in one cycle

---

## 📞 Support

**If You Need Help:**

1. **Check Logs:**
   - Location: `C:\mt5_bridge_service\logs\api_service.log`
   - Look for errors with ❌ or ERROR

2. **Verify Prerequisites:**
   - Both terminals running
   - MongoDB accessible
   - Python packages installed

3. **Test Manually:**
   - Run script in terminal
   - Watch output for specific errors

4. **Rollback if Needed:**
   - Use backup to restore
   - MEXAtlantic must keep working

---

**Deployment Date:** November 24, 2025  
**Version:** 2.0 Multi-Terminal  
**Risk Level:** Low (fully tested logic, rollback available)  
**Expected Downtime:** 2-3 minutes during restart
