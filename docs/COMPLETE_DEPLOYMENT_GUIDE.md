# 🚀 MT5 BRIDGE COMPLETE DEPLOYMENT GUIDE

**Date:** October 29, 2025  
**Version:** 4.0-multi-account with Task Scheduler automation  
**Status:** Ready for production deployment

---

## 📋 WHAT THIS DEPLOYMENT DOES

This deployment fully automates the MT5 Bridge setup with:

1. ✅ **Deploy MT5 Bridge v4.0** - Fixed script that logs into all 7 accounts
2. ✅ **Configure Windows Task Scheduler** - Auto-start, auto-restart, background operation
3. ✅ **Verify deployment** - Automated health checks and status reporting
4. ✅ **Production-ready** - No manual intervention needed after deployment

---

## 🎯 FILES CREATED

### 1. MT5 Bridge Script (v4.0)
**Location:** `/app/vps-scripts/mt5_bridge_multi_account_fixed.py`

**Features:**
- Logs into all 7 MT5 accounts using investor password `Fidus13!`
- Background task refreshes account data every 5 minutes
- Proper session handling (Interactive session for MT5 compatibility)
- Comprehensive logging and error handling

### 2. Task Scheduler Setup Script
**Location:** `/app/vps-scripts/setup_mt5_task_scheduler.ps1`

**Features:**
- Creates Windows Scheduled Task for MT5 Bridge
- Configures auto-start on system boot
- Auto-restart on failure (up to 999 retries)
- Runs in background (no console window)
- Interactive session (Session 1) for MT5 Terminal compatibility

### 3. GitHub Actions Workflow
**Location:** `/app/.github/workflows/deploy-mt5-with-task-scheduler.yml`

**Features:**
- Automated deployment via GitHub Actions
- Deploys both scripts to VPS
- Executes Task Scheduler setup remotely
- Verifies deployment success
- Tests API endpoints

---

## 🚀 DEPLOYMENT METHODS

### **METHOD 1: GitHub Actions (Recommended)**

1. **Navigate to GitHub Actions:**
   ```
   https://github.com/chavapalmarubin-lab/FIDUS/actions
   ```

2. **Select workflow:** `Deploy MT5 Bridge with Task Scheduler Setup`

3. **Click:** `Run workflow` button

4. **Select branch:** `main`

5. **Click:** `Run workflow` (green button)

6. **Wait:** ~2-3 minutes for deployment to complete

7. **Verify:** Check workflow logs for success messages

---

### **METHOD 2: Manual PowerShell (Alternative)**

If GitHub Actions fails, run manually on VPS:

1. **RDP to VPS:**
   ```
   mstsc /v:92.118.45.135:42014
   Username: trader
   Password: 4p1We0OHh3LKgm6
   ```

2. **Open PowerShell as Administrator**

3. **Download and execute deployment:**
   ```powershell
   # Download MT5 Bridge script
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps-scripts/mt5_bridge_multi_account_fixed.py" -OutFile "C:\mt5_bridge_service\mt5_bridge_api_service.py" -UseBasicParsing
   
   # Download Task Scheduler setup script
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps-scripts/setup_mt5_task_scheduler.ps1" -OutFile "C:\mt5_bridge_service\setup_task_scheduler.ps1" -UseBasicParsing
   
   # Execute setup
   & "C:\mt5_bridge_service\setup_task_scheduler.ps1"
   ```

4. **Verify deployment:** (see verification section below)

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify each layer:

### **1. Task Scheduler (VPS)**

```powershell
# Check task exists
Get-ScheduledTask -TaskName "MT5_Bridge_Service"

# Check task info
Get-ScheduledTaskInfo -TaskName "MT5_Bridge_Service"

# Expected output:
#   State: Running or Ready
#   LastRunTime: Recent timestamp
#   NextRunTime: At next system startup
```

### **2. Process Running (VPS)**

```powershell
# Check if Python process is running
Get-Process python | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmdLine -like "*mt5_bridge*"
}

# Expected: Shows process with PID
```

### **3. API Health Check (VPS)**

```powershell
# Test API endpoint
Invoke-RestMethod http://localhost:8000/api/mt5/bridge/health

# Expected output:
# {
#   "status": "healthy",
#   "version": "4.0-multi-account",
#   "mt5": {
#     "initialized": true,
#     "available": true
#   },
#   "cache": {
#     "accounts_cached": 7,
#     "total_accounts": 7,
#     "cache_complete": true
#   }
# }
```

### **4. All Accounts Endpoint (VPS)**

```powershell
# Check all 7 accounts
Invoke-RestMethod http://localhost:8000/api/mt5/accounts/summary

# Expected: All 7 accounts with real balances (not $0.00)
```

### **5. External Access Test (Any Machine)**

```bash
# Test from external network
curl http://92.118.45.135:8000/api/mt5/bridge/health

# Expected: HTTP 200 with health status JSON
```

### **6. MongoDB Verification**

```python
from pymongo import MongoClient

client = MongoClient("mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.y1p9be2.mongodb.net/fidus_production")
db = client['fidus_production']

accounts = list(db.mt5_accounts.find({}, {"account_number": 1, "balance": 1, "last_sync": 1}))
for acc in accounts:
    print(f"Account {acc['account_number']}: ${acc['balance']:,.2f} (synced: {acc['last_sync']})")

# Expected:
#   - All 7 accounts present
#   - Real balances (not $0.00)
#   - Recent sync timestamps (within last 10 minutes)
```

### **7. Frontend Dashboard Verification**

1. Open FIDUS dashboard
2. Navigate to MT5 accounts / portfolio section
3. **Verify:** All 7 accounts show real balances
4. **Expected total:** ~$138,460 across all accounts

---

## 🔍 TROUBLESHOOTING

### **Issue: Task Scheduler task not found**

```powershell
# Re-run setup script
& "C:\mt5_bridge_service\setup_task_scheduler.ps1"
```

### **Issue: Service not starting**

```powershell
# Check logs
Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 50

# Look for errors related to:
#   - Python path
#   - MT5 Terminal connection
#   - Port 8000 already in use
```

### **Issue: MT5 not initialized**

```powershell
# Ensure MT5 Terminal is running
Get-Process | Where-Object {$_.ProcessName -like "*terminal*"}

# If not running, start it:
Start-Process "C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"

# Then restart the bridge task:
Stop-ScheduledTask -TaskName "MT5_Bridge_Service"
Start-ScheduledTask -TaskName "MT5_Bridge_Service"
```

### **Issue: Accounts still showing $0.00**

```powershell
# Force immediate account refresh
Invoke-RestMethod -Uri http://localhost:8000/api/mt5/refresh -Method POST

# Wait 2-3 minutes and check again
Invoke-RestMethod http://localhost:8000/api/mt5/accounts/summary
```

### **Issue: GitHub Actions deployment fails**

**Check GitHub Secrets:**
1. Go to repository Settings → Secrets → Actions
2. Verify these secrets exist:
   - `VPS_HOST`: 92.118.45.135
   - `VPS_PORT`: 42014
   - `VPS_USERNAME`: trader
   - `VPS_PASSWORD`: 4p1We0OHh3LKgm6

**If secrets are missing:**
```bash
# Add secrets via GitHub CLI
gh secret set VPS_HOST --body "92.118.45.135" --repo chavapalmarubin-lab/FIDUS
gh secret set VPS_PORT --body "42014" --repo chavapalmarubin-lab/FIDUS
gh secret set VPS_USERNAME --body "trader" --repo chavapalmarubin-lab/FIDUS
gh secret set VPS_PASSWORD --body "4p1We0OHh3LKgm6" --repo chavapalmarubin-lab/FIDUS
```

---

## 🎯 SUCCESS CRITERIA

Deployment is **COMPLETE** when:

- ✅ Windows Scheduled Task exists and is running
- ✅ MT5 Bridge process is running (no console window needed)
- ✅ API health check returns `"status": "healthy"`
- ✅ API health check shows `"version": "4.0-multi-account"`
- ✅ API health check shows `"cache_complete": true`
- ✅ All 7 accounts return real balances via API
- ✅ MongoDB has real balances with recent timestamps
- ✅ Render backend serves correct data
- ✅ Frontend dashboard displays all 7 account balances
- ✅ Service survives VPS reboot (auto-starts)

---

## 📊 EXPECTED ACCOUNT BALANCES

Based on screenshot provided:

| Account | Fund Type | Expected Balance |
|---------|-----------|------------------|
| 885822 | CORE-CP | ~$10,002 |
| 886066 | BALANCE-GoldenTrade | ~$2,752 |
| 886528 | SEPARATION-Reserve | ~$0 (correct) |
| 886557 | BALANCE-Master | ~$79,425 |
| 886602 | BALANCE-Tertiary | ~$10,100 |
| 891215 | SEPARATION-Trading | ~$28,700 |
| 891234 | CORE-GoldenTrade | ~$7,479 |
| **TOTAL** | **All Funds** | **~$138,460** |

---

## 🔄 POST-DEPLOYMENT TESTING

### **Test 1: VPS Reboot Test**

```powershell
# Restart VPS
Restart-Computer -Force

# Wait for VPS to come back online (2-3 minutes)
# RDP back in and verify:
Get-ScheduledTask -TaskName "MT5_Bridge_Service"  # Should show "Running"
Invoke-RestMethod http://localhost:8000/api/mt5/bridge/health  # Should return healthy
```

### **Test 2: Service Crash Recovery**

```powershell
# Kill the bridge process
Get-Process python | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmdLine -like "*mt5_bridge*"
} | Stop-Process -Force

# Wait 1 minute - Task Scheduler should auto-restart it
Start-Sleep -Seconds 60

# Verify it restarted
Get-Process python | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmdLine -like "*mt5_bridge*"
}  # Should show new process

Invoke-RestMethod http://localhost:8000/api/mt5/bridge/health  # Should return healthy
```

---

## 📞 SUPPORT

**Logs Location:**
```
C:\mt5_bridge_service\logs\api_service.log
```

**View Logs:**
```powershell
Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 100 -Wait
```

**Service Control:**
```powershell
# Start service
Start-ScheduledTask -TaskName "MT5_Bridge_Service"

# Stop service
Stop-ScheduledTask -TaskName "MT5_Bridge_Service"

# Check status
Get-ScheduledTaskInfo -TaskName "MT5_Bridge_Service"
```

---

## ✅ DEPLOYMENT STATUS

**Created:**
- ✅ MT5 Bridge v4.0 script
- ✅ Task Scheduler setup script
- ✅ GitHub Actions workflow
- ✅ Complete documentation

**Ready for:**
- ✅ GitHub Actions deployment
- ✅ Manual PowerShell deployment
- ✅ Production use

**Next Action:**
- 🚀 Trigger GitHub Actions workflow OR run manual deployment
- ✅ Verify using checklist above
- ✅ Confirm all 7 accounts showing real balances

---

**Version:** 1.0  
**Last Updated:** October 29, 2025  
**Status:** READY FOR DEPLOYMENT 🚀
