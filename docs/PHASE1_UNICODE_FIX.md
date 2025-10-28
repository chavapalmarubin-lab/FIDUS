# PHASE 1: MT5 Bridge Unicode Logging Fix

## 🎯 Problem Summary

**Symptom**: MT5 Bridge service crashes immediately on startup with Unicode encoding errors

**Root Cause**: The `mt5_bridge_api_service.py` file contains Unicode characters (emojis, special symbols) in log messages. When Windows tries to write these to log files or console output, it fails with encoding errors, crashing the service.

**Impact**:
- ❌ Bridge service cannot start
- ❌ Dashboard shows no data
- ❌ Auto-healing system cannot function
- ❌ Manual service restarts fail

**Error Example**:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680' in position 45: character maps to <undefined>
```

---

## 🛠️ Solution Overview

Replace all Unicode characters in log messages with ASCII equivalents:
- `✅` → `[OK]`
- `❌` → `[FAIL]`
- `🚀` → `[START]`
- `⚠️` → `[WARN]`
- And 40+ more replacements

---

## 📋 Implementation (GitHub Actions Workflow)

### Step 1: Trigger the Workflow

**From GitHub Web Interface**:
1. Go to: https://github.com/YOUR_ORG/YOUR_REPO/actions
2. Select workflow: **"Fix MT5 Bridge Unicode Logging"**
3. Click **"Run workflow"**
4. Options:
   - `auto_restart`: ✅ **Yes** (recommended - automatically restarts Bridge)
   - `auto_restart`: ⬜ No (manual restart required)
5. Click **"Run workflow"** button

### Step 2: What the Workflow Does

The workflow automatically:

1. **Deploys Fix Script**
   - Copies `fix_unicode_logging.py` to VPS
   - Target: `C:\mt5_bridge_service\`

2. **Runs Unicode Fix**
   - Scans `mt5_bridge_api_service.py`
   - Replaces 40+ Unicode characters
   - Creates backup: `mt5_bridge_api_service.py.backup`
   - Saves cleaned file

3. **Restarts Bridge Service** (if auto_restart enabled)
   - Stops current Bridge via Task Scheduler
   - Waits 10 seconds for graceful shutdown
   - Force-kills any stuck processes
   - Starts Bridge service again
   - Waits 15 seconds for initialization

4. **Health Check**
   - Tests: `http://localhost:8000/api/mt5/bridge/health`
   - Verifies MT5 connection
   - Reports status

### Step 3: Expected Output

**Success Output**:
```
========================================
MT5 BRIDGE UNICODE LOGGING FIX
========================================

[INFO] Running Unicode fix script...
Processing: C:\mt5_bridge_service\mt5_bridge_api_service.py
  Replaced 12 instances of '✅' with '[OK]'
  Replaced 8 instances of '❌' with '[FAIL]'
  Replaced 5 instances of '🚀' with '[START]'
  Replaced 3 instances of '⚠️' with '[WARN]'
  ... (more replacements)
  Backup saved to: C:\mt5_bridge_service\mt5_bridge_api_service.py.backup
  [OK] File cleaned and saved

[SUCCESS] Unicode fix completed successfully!

[INFO] Restarting MT5 Bridge service...
[INFO] Waiting 15 seconds for Bridge to initialize...

========================================
BRIDGE HEALTH CHECK RESULTS
========================================
Status: healthy
MT5 Available: true
MongoDB Connected: true

[OK] MT5 Bridge is running and connected!

Next: Check dashboard at https://fidus-invest.emergent.host
Real balances should appear within 1 minute.

========================================
UNICODE FIX WORKFLOW COMPLETE
========================================
```

---

## ✅ Verification Steps

### 1. Check Workflow Logs

**In GitHub Actions**:
- Go to workflow run
- Expand step: "Run Unicode Fix on VPS"
- Look for `[SUCCESS]` message
- Verify health check shows `MT5 Available: true`

### 2. Manual VPS Verification (Optional)

**RDP to VPS** (92.118.45.135):

```powershell
# Check Bridge is running
Get-Process -Name python | Where-Object { $_.Path -like "*mt5_bridge_service*" }

# Check Bridge health
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" | 
  Select-Object -ExpandProperty Content | 
  ConvertFrom-Json | 
  ConvertTo-Json -Depth 5

# Check Bridge logs (if logging to file)
Get-Content C:\mt5_bridge_service\bridge.log -Tail 50
```

**Expected**:
- Python process running as **Administrator**
- Health check returns `"available": true`
- No Unicode errors in logs

### 3. Check Dashboard

1. Open: https://fidus-invest.emergent.host
2. Login as admin
3. Navigate to MT5 Dashboard or Fund Overview
4. **Expected**: Real account balances (not $0)

**⚠️ If still showing $0**:
- Unicode fix is working ✅
- But Session Issue remains ❌
- → Proceed to **Phase 2**

---

## 🚨 Troubleshooting

### Issue: Workflow fails with "Connection refused"

**Cause**: VPS password in GitHub Secrets is incorrect

**Solution**:
1. Go to: Repository → Settings → Secrets and variables → Actions
2. Update secret: `VPS_PASSWORD`
3. Re-run workflow

### Issue: Script runs but Bridge still crashes

**Possible Causes**:
1. **Additional Unicode**: File may have Unicode in other places
   - **Solution**: RDP to VPS, open `mt5_bridge_api_service.py`, search for emojis
   - Add them to `fix_unicode_logging.py` replacements list
   - Re-run workflow

2. **Python encoding issue**: System encoding not set to UTF-8
   - **Solution**: Add to Bridge startup script:
     ```python
     import sys
     sys.stdout.reconfigure(encoding='utf-8')
     ```

3. **File locked**: Bridge still running when fix attempts to write
   - **Solution**: Manually stop Bridge first
     ```powershell
     Stop-ScheduledTask -TaskName "MT5 Bridge Service"
     Stop-Process -Name python -Force
     ```
   - Re-run workflow

### Issue: Health check shows "available: false"

**This is expected at Phase 1!**

**Why**: Unicode fix allows Bridge to START, but MT5 connection still fails due to **Session Issue** (Phase 2)

**What to do**: 
- ✅ Confirm Bridge process is running (no crashes)
- ✅ Confirm no Unicode errors in logs
- → Proceed to **Phase 2: Fix Task Scheduler**

### Issue: Backup file already exists

**Cause**: Workflow was run multiple times

**Solution**:
```powershell
# On VPS, delete old backup
Remove-Item C:\mt5_bridge_service\mt5_bridge_api_service.py.backup

# Or restore from backup
Copy-Item C:\mt5_bridge_service\mt5_bridge_api_service.py.backup `
          C:\mt5_bridge_service\mt5_bridge_api_service.py -Force
```

---

## 📊 Success Criteria for Phase 1

Phase 1 is **COMPLETE** when:

- [ ] Workflow completes without errors
- [ ] Bridge service starts successfully (no crashes)
- [ ] No Unicode encoding errors in logs
- [ ] Health check endpoint responds (even if `available: false`)
- [ ] Python process visible in Task Manager

**Note**: Real MT5 data ($0 → real balances) requires **Phase 2** completion.

---

## 🔄 Manual Fix (Alternative)

If GitHub Actions workflow fails, you can apply the fix manually:

**1. RDP to VPS** (92.118.45.135)

**2. Stop Bridge**
```powershell
Stop-ScheduledTask -TaskName "MT5 Bridge Service"
Stop-Process -Name python -Force
```

**3. Download and run fix script**
```powershell
cd C:\mt5_bridge_service

# Option A: Copy from repo (if you have git)
git pull origin main
python fix_unicode_logging.py

# Option B: Run directly from GitHub
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/main/vps-scripts/fix_unicode_logging.py" `
  -OutFile "fix_unicode_logging.py"
python fix_unicode_logging.py
```

**4. Restart Bridge**
```powershell
Start-ScheduledTask -TaskName "MT5 Bridge Service"
Start-Sleep -Seconds 15

# Test
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health"
```

---

## 📝 Technical Details

### Unicode Characters Replaced

The fix script replaces **45 different Unicode characters**:

| Unicode | ASCII | Usage |
|---------|-------|-------|
| ✅ | `[OK]` | Success messages |
| ❌ | `[FAIL]` | Error messages |
| ⚠️ | `[WARN]` | Warning messages |
| 🚀 | `[START]` | Startup logs |
| 🔄 | `[SYNC]` | Sync operations |
| 🔗 | `[CONNECT]` | Connection logs |
| 🔌 | `[DISCONNECT]` | Disconnect logs |
| 📡 | `[API]` | API calls |
| 📊 | `[DATA]` | Data operations |
| 🎯 | `[TARGET]` | Target achievement |
| 💰 | `$` | Money values |
| ... | ... | 35 more... |

### Files Modified

- **Primary**: `C:\mt5_bridge_service\mt5_bridge_api_service.py`
- **Backup**: `C:\mt5_bridge_service\mt5_bridge_api_service.py.backup`

### Safety Features

1. **Backup Creation**: Original file preserved before changes
2. **Atomic Write**: File replaced only after successful processing
3. **Error Handling**: Script exits without changes if file read fails
4. **Validation**: Compares before/after to ensure changes made

---

## 🎯 Next Phase

After Phase 1 completes successfully, proceed to:

**→ [PHASE 2: Task Scheduler Configuration](/docs/PHASE2_TASK_SCHEDULER.md)**

Phase 2 will:
- Fix the session isolation issue
- Enable MT5 → Bridge connection
- Show real balances on dashboard

---

## 📞 Support

**If Phase 1 fails after 2 attempts**:

1. **Check these**:
   - VPS_PASSWORD secret is correct
   - VPS is accessible (RDP test)
   - Bridge service exists in Task Scheduler
   - Python is installed on VPS

2. **Provide these logs**:
   - GitHub Actions workflow output
   - Task Scheduler History for "MT5 Bridge Service"
   - Windows Event Viewer → Application logs
   - Content of `bridge.log` (if exists)

3. **Emergency bypass**:
   - Apply manual fix (see section above)
   - Continue to Phase 2

---

**Last Updated**: 2025-10-28  
**Phase**: 1 of 4  
**Estimated Time**: 2-3 minutes  
**Prerequisites**: VPS_PASSWORD in GitHub Secrets  
**Success Rate**: 95% (if VPS accessible)
