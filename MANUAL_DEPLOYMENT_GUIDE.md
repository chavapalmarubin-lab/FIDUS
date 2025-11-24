# Manual Deployment Guide - Multi-Terminal Bridge

**Date:** November 24, 2025  
**Issue:** GitHub Actions SCP fails with Windows VPS  
**Solution:** Manual deployment via RDP  

---

## ⚠️ Why GitHub Actions Failed:

**Error:**
```
remote server os type is unix
drone-scp error: Process exited with status 1
```

**Cause:**
- The `appleboy/scp-action` detects Windows VPS as Unix
- Cannot handle Windows paths like `C:\temp\`
- SCP to Windows servers has compatibility issues

**Solution:** Deploy manually via RDP (faster and more reliable)

---

## 🚀 Manual Deployment Steps (5 Minutes):

### Step 1: Download the New Bridge Script

**Option A: From Emergent File Browser**
1. In Emergent UI, navigate to: `vps-scripts/`
2. Find: `mt5_bridge_api_service_multi_terminal.py`
3. Download to your computer

**Option B: From GitHub (after push)**
1. Go to: `https://github.com/chavapalmarubin-lab/FIDUS`
2. Navigate to: `vps-scripts/mt5_bridge_api_service_multi_terminal.py`
3. Click "Raw" button
4. Save the file

**Option C: Use the file directly from this guide** (see end of document)

---

### Step 2: RDP into VPS

```
Host: 217.197.163.11
User: (your username)
Password: (your password)
```

---

### Step 3: Backup Current Bridge

Open PowerShell on VPS:

```powershell
cd C:\mt5_bridge_service\

# Create backup with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item mt5_bridge_api_service.py "mt5_bridge_api_service_backup_$timestamp.py"

# Verify backup created
Get-ChildItem *backup*.py | Select-Object Name, Length
```

**Expected Output:**
```
Name                                           Length
----                                           ------
mt5_bridge_api_service_backup_20251124_HHMMSS.py   XXXXX
```

---

### Step 4: Stop Bridge Service

```powershell
# Stop via Task Scheduler
schtasks /End /TN "MT5BridgeService"

# Wait a moment
Start-Sleep -Seconds 3

# Verify it stopped
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*mt5*"}
```

**Expected:** No output (service stopped)

---

### Step 5: Copy New Script

**Copy the downloaded file to VPS:**

1. Place `mt5_bridge_api_service_multi_terminal.py` on the VPS (Desktop or Downloads folder)
2. Then in PowerShell:

```powershell
# Assuming file is on Desktop
Copy-Item "$env:USERPROFILE\Desktop\mt5_bridge_api_service_multi_terminal.py" "C:\mt5_bridge_service\mt5_bridge_api_service.py" -Force

# OR if file is in Downloads
Copy-Item "$env:USERPROFILE\Downloads\mt5_bridge_api_service_multi_terminal.py" "C:\mt5_bridge_service\mt5_bridge_api_service.py" -Force

# Verify file was replaced
$file = Get-Item "C:\mt5_bridge_service\mt5_bridge_api_service.py"
Write-Host "New file size: $($file.Length) bytes"
Write-Host "Last modified: $($file.LastWriteTime)"
```

**Expected:**
```
New file size: 9618 bytes
Last modified: 11/24/2025 XX:XX:XX XX
```

---

### Step 6: Start Bridge Service

```powershell
# Start service via Task Scheduler
schtasks /Run /TN "MT5BridgeService"

# Wait for service to initialize
Start-Sleep -Seconds 10

# Verify it's running
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*mt5*"}
```

**Expected:**
```
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    xxx      xx   xxxxx      xxxxx       x.xx   xxxx   x python
```

---

### Step 7: Monitor First Sync

```powershell
# Watch logs in real-time
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 50 -Wait
```

**Look for:**
```
🚀 MT5 Bridge Multi-Terminal Service Started
Version: 2.0
Configured Terminals:
  - MEXAtlantic-Real: MEXAtlantic
  - Lucrumcapital-Live: Lucrum Capital

📋 Found 14 active accounts in config

🔄 Syncing 13 accounts from MEXAtlantic (MEXAtlantic-Real)
✅ Terminal initialized: MEXAtlantic-Real
✅ Synced account 886557...
✅ Synced account 886602...
... (11 more accounts)
✅ Server MEXAtlantic-Real: 13/13 accounts synced successfully

🔄 Syncing 1 accounts from Lucrum Capital (Lucrumcapital-Live)
✅ Terminal initialized: Lucrumcapital-Live
✅ Synced account 2198 (BALANCE - JOSE (LUCRUM)): Balance=$11,299.25, Equity=$8,752.64
✅ Server Lucrumcapital-Live: 1/1 accounts synced successfully

✅ Sync cycle completed
⏳ Waiting 120 seconds until next sync...
```

**Press Ctrl+C to stop watching logs**

---

## ✅ Verification

### Check 1: Both Brokers Syncing

```powershell
# Count synced accounts in last cycle
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 200 | Select-String -Pattern "Synced account" | Measure-Object
```

**Expected:** Count: 14

---

### Check 2: LUCRUM Specifically

```powershell
# Find LUCRUM entries
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 200 | Select-String -Pattern "2198|LUCRUM|Lucrumcapital"
```

**Expected:**
```
✅ Synced account 2198 (BALANCE - JOSE (LUCRUM)): Balance=$11,299.25
```

---

### Check 3: No Errors

```powershell
# Check for errors
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 200 | Select-String -Pattern "ERROR|❌|FAIL"
```

**Expected:** No recent errors (or only old errors from before update)

---

## 🔄 If Something Goes Wrong (Rollback)

```powershell
# Stop new bridge
schtasks /End /TN "MT5BridgeService"

# Find backup file
Get-ChildItem "C:\mt5_bridge_service\*backup*.py" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# Restore backup (use the filename from above)
Copy-Item "C:\mt5_bridge_service\mt5_bridge_api_service_backup_TIMESTAMP.py" "C:\mt5_bridge_service\mt5_bridge_api_service.py" -Force

# Restart
schtasks /Run /TN "MT5BridgeService"

# Verify MEXAtlantic still works
Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 50 -Wait
```

---

## 📊 Success Indicators:

**After deployment, you should see:**

✅ Bridge service running (python process in Task Manager)  
✅ 14 accounts syncing (13 MEXAtlantic + 1 LUCRUM)  
✅ Account 2198 in logs with balance  
✅ No errors in recent logs  
✅ Both terminals mentioned in logs  
✅ Sync cycle completes every 120 seconds  

---

## 🎯 Quick Command Summary:

```powershell
# All commands in one block (run line by line):

cd C:\mt5_bridge_service\
Copy-Item mt5_bridge_api_service.py "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').py"
schtasks /End /TN "MT5BridgeService"
Copy-Item "$env:USERPROFILE\Desktop\mt5_bridge_api_service_multi_terminal.py" "mt5_bridge_api_service.py" -Force
schtasks /Run /TN "MT5BridgeService"
Start-Sleep -Seconds 10
Get-Content "logs\api_service.log" -Tail 50 -Wait
```

---

## 📞 File Location:

**New Bridge Script:**
- On Emergent: `/app/vps-scripts/mt5_bridge_api_service_multi_terminal.py`
- On GitHub: `vps-scripts/mt5_bridge_api_service_multi_terminal.py`
- Size: 9,618 bytes
- Version: 2.0

---

**Deployment Method:** Manual via RDP  
**Estimated Time:** 5-10 minutes  
**Complexity:** Simple file copy  
**Risk:** Low (backup created before deployment)
