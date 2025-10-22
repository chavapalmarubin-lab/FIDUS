# MT5 Connection Troubleshooting Guide

**Generated:** 2025-10-22 22:50 UTC  
**Issue:** MT5 Terminal running but service can't connect (IPC timeout -10005)

---

## 🔍 CURRENT STATUS

### What's Working: ✅
- VPS service running on port 8000
- MongoDB connected
- Emergency restart API functional (token auth working)
- Health endpoint responding

### What's Not Working: ⚠️
- MT5 Terminal connection
- Error: `IPC timeout (-10005)`
- MT5 available: `false`

---

## 🐛 IPC TIMEOUT ERROR ANALYSIS

### Error Code: -10005 (IPC timeout)

**What it means:**
The MetaTrader5 Python library cannot communicate with the MT5 Terminal application.

**Common Causes:**

1. **MT5 Terminal not fully initialized** (needs 30-60 seconds)
2. **MT5 Terminal not running with correct permissions**
3. **Service and MT5 running under different user accounts**
4. **MT5 path incorrect in configuration**
5. **Windows firewall blocking IPC communication**
6. **MT5 Terminal version incompatible with MetaTrader5 library**

---

## 🔧 TROUBLESHOOTING STEPS

### Step 1: Verify MT5 Terminal is Running

**On VPS:**
```powershell
# Check if terminal64.exe is running
Get-Process | Where-Object {$_.ProcessName -like "*terminal*"}

# Should show:
# ProcessName: terminal64
# Status: Running
```

**If not running:**
```powershell
Start-Process "C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"
```

### Step 2: Check MT5 Terminal is Fully Initialized

**Wait time:** 30-60 seconds after starting MT5 Terminal

**Visual check on VPS:**
- MT5 Terminal window should be open
- Should show connection status (connected/disconnected)
- Should show account information

### Step 3: Verify Both Processes Run as Same User

**Issue:** If MT5 Terminal runs as Administrator but Python service runs as regular user (or vice versa), they can't communicate.

**Solution:**
```powershell
# Check who owns terminal64.exe process
Get-Process terminal64 | Select-Object ProcessName, UserName

# Check who owns python.exe process
Get-Process python | Select-Object ProcessName, UserName

# Both should be same user (e.g., trader or Administrator)
```

**If different:**
- Stop both processes
- Start MT5 Terminal as the same user running the Python service
- Restart Python service

### Step 4: Restart VPS Service After MT5 is Running

**Important:** The VPS service should start AFTER MT5 Terminal is fully initialized.

```powershell
# Stop VPS service
taskkill /F /IM python.exe

# Verify MT5 Terminal is running
Get-Process terminal64

# Wait 5 seconds
timeout /t 5

# Start VPS service
cd C:\mt5_bridge_service
python mt5_bridge_api_service.py
```

### Step 5: Check MT5 Path Configuration

**Verify the path in .env file:**
```powershell
cd C:\mt5_bridge_service
Get-Content .env | Select-String "MT5_PATH"

# Should show:
# MT5_PATH=C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe
```

**Verify the file exists:**
```powershell
Test-Path "C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"

# Should return: True
```

**If path is wrong, update .env:**
```powershell
# Find correct path
Get-ChildItem "C:\Program Files" -Recurse -Filter "terminal64.exe" -ErrorAction SilentlyContinue

# Update .env with correct path
```

### Step 6: Run MT5 Terminal as Administrator

**Sometimes MT5 needs elevated privileges:**

```powershell
# Stop current MT5 Terminal
Stop-Process -Name terminal64 -Force

# Start as Administrator
Start-Process "C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe" -Verb RunAs

# Wait 30 seconds
timeout /t 30

# Restart VPS service
taskkill /F /IM python.exe
cd C:\mt5_bridge_service
python mt5_bridge_api_service.py
```

### Step 7: Check VPS Service Logs

**On VPS:**
```powershell
cd C:\mt5_bridge_service\logs
Get-Content api_service.log -Tail 50

# Look for:
# [ERROR] MT5 initialize() failed, error code: ...
# [OK] MT5 Terminal initialized: v(...)
```

**Common log messages:**

**Success:**
```
[OK] MT5 Terminal initialized: v(500, 5370, '17 Oct 2025')
```

**Failure:**
```
[ERROR] MT5 initialize() failed, error code: (-10005, 'IPC timeout')
```

---

## 🚀 RECOMMENDED FIX (MOST LIKELY TO WORK)

### Complete Service Restart Sequence:

```powershell
# 1. Stop VPS service
Write-Host "Stopping VPS service..." -ForegroundColor Yellow
taskkill /F /IM python.exe
timeout /t 3

# 2. Verify MT5 Terminal is running
Write-Host "Checking MT5 Terminal..." -ForegroundColor Yellow
$mt5Process = Get-Process terminal64 -ErrorAction SilentlyContinue

if ($mt5Process) {
    Write-Host "MT5 Terminal is running" -ForegroundColor Green
} else {
    Write-Host "Starting MT5 Terminal..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"
    Write-Host "Waiting 30 seconds for MT5 initialization..." -ForegroundColor Cyan
    timeout /t 30
}

# 3. Start VPS service
Write-Host "Starting VPS service..." -ForegroundColor Yellow
cd C:\mt5_bridge_service
Start-Process python -ArgumentList "mt5_bridge_api_service.py" -NoNewWindow

# 4. Wait for service startup
Write-Host "Waiting 15 seconds for service startup..." -ForegroundColor Cyan
timeout /t 15

# 5. Test health
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing | Select-Object -ExpandProperty Content

Write-Host "Done!" -ForegroundColor Green
```

---

## ✅ VERIFICATION

### After Running the Fix:

**Test 1: Local Health Check (on VPS)**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing | ConvertFrom-Json
```

**Expected:**
```json
{
  "status": "healthy",
  "mt5": {
    "available": true,
    "terminal_info": {
      "connected": true,
      "name": "MEX Atlantic MT5 Terminal"
    }
  },
  "mongodb": {"connected": true}
}
```

**Test 2: External Health Check**
```bash
curl http://92.118.45.135:8000/api/mt5/bridge/health
```

**Expected:** Same as above

**Test 3: Emergency Restart**
```bash
curl -X POST "http://92.118.45.135:8000/api/admin/emergency-restart?token=fidus_admin_restart_2025_secure_key_xyz123"
```

**Expected:**
```json
{
  "success": true,
  "message": "MT5 Bridge service restarted successfully",
  "mt5_reinitialized": true,
  "mongodb_connected": true
}
```

---

## 🔍 ALTERNATIVE: CHECK MT5 TERMINAL VERSION

### Verify Python MetaTrader5 Library Version

**On VPS:**
```powershell
python -c "import MetaTrader5 as mt5; print(mt5.__version__)"

# Should show: 5.0.45 or similar
```

### Check MT5 Terminal Build

**On VPS (in Python):**
```powershell
python -c "import MetaTrader5 as mt5; mt5.initialize(); print(mt5.version()); mt5.shutdown()"

# Should show: (500, 5370, '17 Oct 2025') or similar
# If this fails with IPC timeout, proceed with troubleshooting steps
```

---

## 🎯 SUCCESS CRITERIA

MT5 connection is working when:

1. ✅ MT5 Terminal window is open and showing account data
2. ✅ Health endpoint shows `"mt5": {"available": true}`
3. ✅ Terminal info is populated (not null)
4. ✅ Emergency restart returns `"success": true`
5. ✅ VPS service logs show `[OK] MT5 Terminal initialized`

---

## 📧 NEED MORE HELP?

If MT5 still won't connect after all these steps:

1. **Check VPS logs:**
   - `C:\mt5_bridge_service\logs\api_service.log`
   - Look for specific error messages

2. **Check Windows Event Viewer:**
   - Look for application errors related to Python or terminal64.exe

3. **Verify MetaTrader5 library installation:**
   ```powershell
   pip show MetaTrader5
   # Should show version 5.0.45 or higher
   ```

4. **Reinstall MetaTrader5 library:**
   ```powershell
   pip uninstall MetaTrader5
   pip install MetaTrader5
   ```

5. **Check if MT5 Terminal is trial version:**
   - Some MT5 features may be restricted in trial versions
   - Verify it's a full installation

---

## 🚨 KNOWN ISSUES

### Issue 1: User Permission Mismatch
**Symptom:** IPC timeout even though MT5 is running  
**Cause:** MT5 and Python service run as different users  
**Fix:** Run both as same user

### Issue 2: MT5 Terminal Not Responding
**Symptom:** MT5 window frozen or not showing data  
**Cause:** MT5 crashed or hung  
**Fix:** Restart MT5 Terminal

### Issue 3: Multiple MT5 Instances
**Symptom:** Inconsistent connection  
**Cause:** Multiple terminal64.exe processes  
**Fix:** Kill all and start one instance

### Issue 4: Windows Defender Blocking
**Symptom:** IPC timeout, firewall logs  
**Cause:** Windows Defender blocking IPC  
**Fix:** Add exception for terminal64.exe and python.exe

---

## 📊 QUICK DIAGNOSTIC CHECKLIST

Run this on VPS to get full diagnostic info:

```powershell
Write-Host "=== MT5 CONNECTION DIAGNOSTIC ===" -ForegroundColor Cyan
Write-Host ""

# Check processes
Write-Host "1. Process Status:" -ForegroundColor Yellow
Get-Process terminal64 -ErrorAction SilentlyContinue | Select-Object ProcessName, Id, UserName
Get-Process python -ErrorAction SilentlyContinue | Select-Object ProcessName, Id, UserName

# Check MT5 path
Write-Host ""
Write-Host "2. MT5 Path Check:" -ForegroundColor Yellow
Test-Path "C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"

# Check .env configuration
Write-Host ""
Write-Host "3. Environment Configuration:" -ForegroundColor Yellow
Get-Content C:\mt5_bridge_service\.env | Select-String "MT5"

# Check service logs
Write-Host ""
Write-Host "4. Recent Service Logs:" -ForegroundColor Yellow
Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 10

# Test local health
Write-Host ""
Write-Host "5. Local Health Check:" -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing | Select-Object -ExpandProperty Content
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== DIAGNOSTIC COMPLETE ===" -ForegroundColor Cyan
```

---

**RUN THE RECOMMENDED FIX ABOVE TO RESOLVE THE IPC TIMEOUT ISSUE** 🚀
