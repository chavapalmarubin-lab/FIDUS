# 🚀 MANUAL DEPLOYMENT INSTRUCTIONS - MT5 Multi-Account Fix

**Date:** October 29, 2025  
**Issue:** Multi-account balance synchronization fix  
**Deployment Time:** ~5 minutes

---

## 📋 QUICK DEPLOYMENT (Copy & Paste)

### Step 1: Connect to VPS via RDP

```
Host: 92.118.45.135:42014
Username: trader
Password: 4p1We0OHh3LKgm6
```

**Windows:** Press `Win+R`, type `mstsc`, paste: `92.118.45.135:42014`  
**Mac:** Use Microsoft Remote Desktop app

---

### Step 2: Open PowerShell as Administrator

1. Right-click Start Menu → **Windows PowerShell (Admin)**
2. Copy and paste the entire command below:

```powershell
# MT5 Bridge Multi-Account Fix - One-Line Deployment
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/scripts/deploy_mt5_fix_via_powershell.ps1" -OutFile "$env:TEMP\deploy_mt5_fix.ps1" -UseBasicParsing; & "$env:TEMP\deploy_mt5_fix.ps1"
```

**This will:**
- ✅ Download the fixed MT5 Bridge script
- ✅ Stop old processes
- ✅ Configure Task Scheduler (Interactive Session)
- ✅ Start the new service
- ✅ Show logs

---

### Step 3: Verify Deployment

**Wait 2-3 minutes**, then test the health endpoint:

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected output:**
```json
{
  "status": "healthy",
  "cache": {
    "accounts_cached": 7,
    "cache_complete": true
  }
}
```

---

### Step 4: Check All Account Balances

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/accounts/summary" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Expected:** All 7 accounts showing real balances (not $0.00)

---

## 🔍 TROUBLESHOOTING

### If service doesn't start:

```powershell
# Check Task Scheduler
Get-ScheduledTask -TaskName "MT5_Bridge_Service"

# Check logs
Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 50

# Manually start
Start-ScheduledTask -TaskName "MT5_Bridge_Service"
```

### If balances still $0.00:

**Force immediate refresh:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/refresh" -Method POST -UseBasicParsing
```

**Wait 5-10 minutes** for the background task to cycle through all 7 accounts.

---

## 📊 VERIFICATION CHECKLIST

- [ ] Service is running (check Task Scheduler)
- [ ] Health endpoint returns "healthy"
- [ ] Cache shows 7/7 accounts
- [ ] `/api/mt5/accounts/summary` shows real balances
- [ ] Dashboard displays all 7 account balances
- [ ] Logs show successful logins to all accounts

---

## 🎯 SUCCESS CRITERIA

**After 10 minutes, you should see:**

1. **Account 885822**: ~$10,151 (CORE-CP)
2. **Account 886066**: ~$10,000 (BALANCE-GoldenTrade)
3. **Account 886528**: ~$6,590 (SEPARATION-Reserve)
4. **Account 886557**: ~$80,000 (BALANCE-Master) ✅
5. **Account 886602**: ~$10,000 (BALANCE-Tertiary)
6. **Account 891215**: ~$6,590 (SEPARATION-Trading)
7. **Account 891234**: ~$8,000 (CORE-GoldenTrade)

---

## 📞 IF YOU NEED HELP

**Logs location:**
```
C:\mt5_bridge_service\logs\api_service.log
```

**Service status:**
```powershell
Get-ScheduledTask -TaskName "MT5_Bridge_Service" | Get-ScheduledTaskInfo
```

**Process check:**
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

---

## 🔄 ALTERNATIVE: Manual Script Execution

If the one-liner doesn't work, manually download and run:

```powershell
# Download script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/scripts/deploy_mt5_fix_via_powershell.ps1" -OutFile "C:\mt5_bridge_service\deploy_fix.ps1"

# Run script
& "C:\mt5_bridge_service\deploy_fix.ps1"
```

---

**Ready to deploy!** Just copy the one-line command from Step 2 into PowerShell on the VPS. 🚀
