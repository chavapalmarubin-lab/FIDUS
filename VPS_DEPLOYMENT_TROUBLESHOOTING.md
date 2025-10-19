# 🚨 VPS Bridge Deployment Issue - OLD Service Still Running

## 📊 Current Status (Just Verified)

**VPS Port 8000 Status:**
- ✅ Service responding
- ❌ OLD service still running (not new API service)
- ❌ Health endpoint: 404
- ❌ Status endpoint: Invalid API key
- ❌ All account endpoints: 404

**Frontend Errors (from screenshots):**
1. ❌ "Failed to load cash flow data"
2. ❌ "Error loading managers: Failed to fetch"
3. ❌ "No money manager data available"

**Backend Errors:**
```
ERROR: Failed to fetch MT5 data after 3 attempts
ERROR: Direct broker API not implemented yet
CRITICAL: MT5 sync success rate low: 0.0%
```

---

## 🔍 Root Cause

**The new `mt5_bridge_api_service.py` was NOT deployed or started.**

Even though you:
- ✅ Pushed to GitHub
- ✅ Ran PowerShell commands on VPS

The OLD service is still running, which means either:
1. The new file wasn't copied to VPS
2. The old process wasn't killed
3. The new service wasn't started
4. The new service crashed and old one restarted

---

## 🛠️ Fix Steps (Run on VPS via RDP/PowerShell)

### Step 1: Check What's Running

```powershell
# Check which Python script is running
Get-Process python | Select-Object Id, Path, CommandLine | Format-List

# Check what's listening on port 8000
netstat -ano | findstr :8000
```

**Expected to see:**
- ❌ BAD: `mt5_bridge_service_production.py` (old service)
- ✅ GOOD: `mt5_bridge_api_service.py` (new service)

---

### Step 2: Check if New File Exists

```powershell
# Check if new file was copied
Test-Path C:\mt5_bridge_service\mt5_bridge_api_service.py

# If it doesn't exist, list what files are there
Get-ChildItem C:\mt5_bridge_service\*.py | Select-Object Name
```

**If file doesn't exist:**
- GitHub Actions deployment failed or didn't run
- Need to copy file manually

---

### Step 3: Stop ALL Python Processes

```powershell
# Force kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Verify nothing running
Get-Process python -ErrorAction SilentlyContinue
# Should return nothing

# Verify port 8000 is free
netstat -ano | findstr :8000
# Should return nothing
```

---

### Step 4: Start NEW Service

```powershell
cd C:\mt5_bridge_service

# Make sure we have the new file
if (Test-Path .\mt5_bridge_api_service.py) {
    Write-Host "✅ New service file found" -ForegroundColor Green
    
    # Install/update dependencies
    pip install -r requirements.txt
    
    # Start the NEW API service
    Write-Host "🚀 Starting new MT5 Bridge API service..." -ForegroundColor Yellow
    python mt5_bridge_api_service.py
} else {
    Write-Host "❌ mt5_bridge_api_service.py NOT FOUND!" -ForegroundColor Red
    Write-Host "Available files:" -ForegroundColor Yellow
    Get-ChildItem *.py | Select-Object Name
}
```

---

### Step 5: Verify NEW Service Started

**In a NEW PowerShell window (keep service running in first):**

```powershell
# Test health endpoint (should NOT be 404)
curl http://localhost:8000/api/mt5/bridge/health

# Test status endpoint (should NOT require API key)
curl http://localhost:8000/api/mt5/status

# Test account endpoint (should NOT be 404)
curl http://localhost:8000/api/mt5/account/886602/info
```

**Expected Results:**
- ✅ Health: `{"status":"healthy",...}`
- ✅ Status: `{"status":"online","accounts":{"total":7},...}`
- ✅ Account: `{"account_id":886602,...}`

---

## 🔧 If New File Doesn't Exist on VPS

The file needs to be copied manually:

### Option A: Copy from GitHub

```powershell
cd C:\mt5_bridge_service

# If Git is configured
git pull origin main

# Or download directly
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/YOUR-REPO/main/vps/mt5_bridge_api_service.py" -OutFile "mt5_bridge_api_service.py"
```

### Option B: Copy from Workspace

1. Get file from workspace: `/app/vps/mt5_bridge_api_service.py`
2. Copy to VPS via:
   - RDP file transfer
   - SCP/SFTP
   - Paste content manually

---

## 📋 Complete Restart Script

**Save this as `restart_bridge_api.ps1` and run it:**

```powershell
# MT5 Bridge API Service Restart Script
Write-Host "=" -rep 60 -ForegroundColor Cyan
Write-Host "MT5 Bridge API Service Restart" -ForegroundColor Cyan
Write-Host "=" -rep 60 -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop old service
Write-Host "Step 1: Stopping old service..." -ForegroundColor Yellow
$processes = Get-Process python -ErrorAction SilentlyContinue
if ($processes) {
    $processes | Stop-Process -Force
    Write-Host "✅ Stopped $($processes.Count) Python process(es)" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "⚠️ No Python processes running" -ForegroundColor Yellow
}

# Step 2: Verify port is free
Write-Host ""
Write-Host "Step 2: Checking port 8000..." -ForegroundColor Yellow
$port = netstat -ano | findstr :8000
if ($port) {
    Write-Host "⚠️ Port 8000 still in use:" -ForegroundColor Yellow
    Write-Host $port
    Write-Host "Waiting 5 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "✅ Port 8000 is free" -ForegroundColor Green
}

# Step 3: Check for new service file
Write-Host ""
Write-Host "Step 3: Checking for new service file..." -ForegroundColor Yellow
cd C:\mt5_bridge_service

if (Test-Path .\mt5_bridge_api_service.py) {
    Write-Host "✅ mt5_bridge_api_service.py found" -ForegroundColor Green
    
    # Step 4: Update dependencies
    Write-Host ""
    Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
    pip install -q -r requirements.txt
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    
    # Step 5: Start new service
    Write-Host ""
    Write-Host "Step 5: Starting NEW API service..." -ForegroundColor Yellow
    Write-Host "Service will run in this window. Keep it open!" -ForegroundColor Cyan
    Write-Host ""
    python mt5_bridge_api_service.py
    
} else {
    Write-Host "❌ ERROR: mt5_bridge_api_service.py NOT FOUND!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available Python files:" -ForegroundColor Yellow
    Get-ChildItem *.py | Format-Table Name, Length, LastWriteTime
    Write-Host ""
    Write-Host "ACTION REQUIRED:" -ForegroundColor Red
    Write-Host "1. Copy mt5_bridge_api_service.py to this directory" -ForegroundColor Yellow
    Write-Host "2. Run this script again" -ForegroundColor Yellow
}
```

---

## ✅ Success Indicators

Once properly deployed, you should see:

**VPS Console Output:**
```
==========================================================
FIDUS MT5 BRIDGE API SERVICE STARTING
==========================================================
✅ MongoDB connected successfully
✅ MT5 Terminal initialized
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Endpoint Tests:**
```bash
✅ Health: {"status":"healthy"}
✅ Status: {"status":"online","accounts":{"total":7}}
✅ Account info: {"account_id":886602,"name":"FIDUS A"}
```

**Frontend:**
- ✅ Cash Flow page loads data
- ✅ Trading Analytics Manager Rankings loads
- ✅ Money Managers shows data

**Backend Logs:**
```
✅ MT5 sync completed: 7/7 accounts synced successfully
```

---

## 🆘 If Still Not Working

1. **Take screenshot of PowerShell window** showing service output
2. **Check logs:** `Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 50`
3. **Share error messages**
4. **Verify .env file has correct MongoDB connection string**

---

**Current Status:** ❌ OLD service running, NEW service NOT deployed  
**Action Required:** Run restart script above on VPS  
**ETA:** 5-10 minutes to fix
