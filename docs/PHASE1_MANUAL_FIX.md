# PHASE 1: Manual Unicode Fix (Windows RDP Method)

## 🎯 Why Manual?

The VPS uses **Windows with RDP** (not Linux with SSH), so GitHub Actions workflows requiring SSH won't work. This manual method is actually **faster and more reliable** for Windows servers.

---

## ⚡ Quick Fix (5 minutes)

### Step 1: RDP to VPS

**Connection Details**:
- **Server**: 92.118.45.135
- **Username**: Administrator
- **Password**: [your VPS password]
- **Port**: 3389 (default RDP)

### Step 2: Download Fix Script

**Open PowerShell as Administrator** on the VPS:
1. Press `Win + X`
2. Select **"Windows PowerShell (Admin)"**

**Run this command** to download the fix script:
```powershell
# Create directory if it doesn't exist
New-Item -Path "C:\mt5_bridge_service" -ItemType Directory -Force

# Navigate to directory
cd C:\mt5_bridge_service

# Download the fix script from your repo
$scriptUrl = "https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/main/vps-scripts/fix_unicode_logging.py"
$scriptPath = "C:\mt5_bridge_service\fix_unicode_logging.py"

Invoke-WebRequest -Uri $scriptUrl -OutFile $scriptPath -UseBasicParsing

Write-Host "[OK] Fix script downloaded successfully" -ForegroundColor Green
```

**Replace in the URL above**:
- `YOUR_ORG` - Your GitHub username or organization
- `YOUR_REPO` - Your repository name

---

### Step 3: Stop MT5 Bridge Service

```powershell
Write-Host "[INFO] Stopping MT5 Bridge service..." -ForegroundColor Yellow

# Stop via Task Scheduler
Stop-ScheduledTask -TaskName "MT5 Bridge Service" -ErrorAction SilentlyContinue

# Wait for graceful shutdown
Start-Sleep -Seconds 5

# Force kill any remaining Python processes
Get-Process -Name python -ErrorAction SilentlyContinue | 
  Where-Object { $_.Path -like "*mt5_bridge_service*" } | 
  Stop-Process -Force

Write-Host "[OK] Bridge service stopped" -ForegroundColor Green
Start-Sleep -Seconds 3
```

---

### Step 4: Run Unicode Fix

```powershell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RUNNING UNICODE FIX" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the fix script
python fix_unicode_logging.py

Write-Host ""
Write-Host "[INFO] Unicode fix completed" -ForegroundColor Green
Write-Host ""
```

**Expected Output**:
```
========================================
MT5 BRIDGE UNICODE LOG FIX
========================================

Target file: C:\mt5_bridge_service\mt5_bridge_api_service.py

Processing: C:\mt5_bridge_service\mt5_bridge_api_service.py
  Replaced 12 instances of '✅' with '[OK]'
  Replaced 8 instances of '❌' with '[FAIL]'
  Replaced 5 instances of '🚀' with '[START]'
  ... (more replacements)
  Backup saved to: C:\mt5_bridge_service\mt5_bridge_api_service.py.backup
  [OK] File cleaned and saved

========================================
UNICODE FIX COMPLETE
========================================
```

---

### Step 5: Restart MT5 Bridge Service

```powershell
Write-Host "[INFO] Starting MT5 Bridge service..." -ForegroundColor Yellow

# Start via Task Scheduler
Start-ScheduledTask -TaskName "MT5 Bridge Service"

Write-Host "[OK] Bridge service started" -ForegroundColor Green
Write-Host "[INFO] Waiting 15 seconds for initialization..." -ForegroundColor Yellow

Start-Sleep -Seconds 15
```

---

### Step 6: Verify Success

```powershell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTING BRIDGE HEALTH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing -TimeoutSec 10
    $health = $response.Content | ConvertFrom-Json
    
    Write-Host "Status: $($health.status)" -ForegroundColor White
    Write-Host "MT5 Available: $($health.mt5.available)" -ForegroundColor $(if ($health.mt5.available) { "Green" } else { "Yellow" })
    Write-Host "MongoDB Connected: $($health.mongodb.connected)" -ForegroundColor $(if ($health.mongodb.connected) { "Green" } else { "Red" })
    Write-Host ""
    
    if ($health.status -eq "healthy") {
        Write-Host "[SUCCESS] Bridge is running without crashes!" -ForegroundColor Green
        Write-Host ""
        
        if ($health.mt5.available) {
            Write-Host "[EXCELLENT] MT5 connection is working!" -ForegroundColor Green
            Write-Host "Dashboard should show real balances now." -ForegroundColor Green
        } else {
            Write-Host "[INFO] Bridge runs but MT5 connection not yet established" -ForegroundColor Yellow
            Write-Host "This is expected - you need Phase 2 (Task Scheduler fix) next" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[WARN] Bridge is responding but may have issues" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "[ERROR] Failed to connect to Bridge health endpoint" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Bridge may not have started correctly." -ForegroundColor Yellow
    Write-Host "Check Task Scheduler and Windows Event Viewer for errors." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 1 COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
```

---

## ✅ Success Criteria

Phase 1 is **COMPLETE** when:

- ✅ Fix script runs without errors
- ✅ Backup file created: `mt5_bridge_api_service.py.backup`
- ✅ Bridge service starts (no crashes)
- ✅ Health endpoint responds
- ⚠️ `MT5 Available: false` is **OK** at this stage (need Phase 2)

---

## 🚀 One-Command Fix (All Steps Combined)

**Copy and paste this entire script** into PowerShell (Admin):

```powershell
# ============================================================================
# MT5 BRIDGE PHASE 1: UNICODE FIX - ONE COMMAND
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MT5 BRIDGE UNICODE FIX - PHASE 1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Download fix script
Write-Host "[1/5] Downloading fix script..." -ForegroundColor Yellow
New-Item -Path "C:\mt5_bridge_service" -ItemType Directory -Force | Out-Null
cd C:\mt5_bridge_service

$scriptUrl = "https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/main/vps-scripts/fix_unicode_logging.py"
Invoke-WebRequest -Uri $scriptUrl -OutFile "fix_unicode_logging.py" -UseBasicParsing
Write-Host "[OK] Script downloaded" -ForegroundColor Green
Write-Host ""

# Step 2: Stop Bridge
Write-Host "[2/5] Stopping MT5 Bridge..." -ForegroundColor Yellow
Stop-ScheduledTask -TaskName "MT5 Bridge Service" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
Get-Process -Name python -ErrorAction SilentlyContinue | 
  Where-Object { $_.Path -like "*mt5_bridge_service*" } | 
  Stop-Process -Force
Write-Host "[OK] Bridge stopped" -ForegroundColor Green
Start-Sleep -Seconds 3
Write-Host ""

# Step 3: Run fix
Write-Host "[3/5] Running Unicode fix..." -ForegroundColor Yellow
python fix_unicode_logging.py
Write-Host ""

# Step 4: Start Bridge
Write-Host "[4/5] Starting MT5 Bridge..." -ForegroundColor Yellow
Start-ScheduledTask -TaskName "MT5 Bridge Service"
Write-Host "[OK] Bridge started" -ForegroundColor Green
Write-Host "[INFO] Waiting 15 seconds for initialization..." -ForegroundColor Yellow
Start-Sleep -Seconds 15
Write-Host ""

# Step 5: Test health
Write-Host "[5/5] Testing Bridge health..." -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing -TimeoutSec 10
    $health = $response.Content | ConvertFrom-Json
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "HEALTH CHECK RESULTS" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Status: $($health.status)" -ForegroundColor White
    Write-Host "MT5 Available: $($health.mt5.available)" -ForegroundColor $(if ($health.mt5.available) { "Green" } else { "Yellow" })
    Write-Host "MongoDB Connected: $($health.mongodb.connected)" -ForegroundColor $(if ($health.mongodb.connected) { "Green" } else { "Red" })
    Write-Host ""
    
    if ($health.status -eq "healthy") {
        Write-Host "[SUCCESS] PHASE 1 COMPLETE!" -ForegroundColor Green
        Write-Host ""
        
        if ($health.mt5.available) {
            Write-Host "[EXCELLENT] MT5 is connected! Check dashboard." -ForegroundColor Green
        } else {
            Write-Host "[NEXT STEP] Run Phase 2 to enable MT5 connection" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "[ERROR] Health check failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Bridge may not have started. Check Task Scheduler." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 1 COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
```

**Don't forget to replace**:
- `YOUR_ORG/YOUR_REPO` with your actual GitHub repository path

---

## 🔄 If Fix Script Download Fails

If the GitHub download doesn't work, the fix script already exists on your VPS:

```powershell
# Check if script exists locally
if (Test-Path "C:\mt5_bridge_service\fix_unicode_logging.py") {
    Write-Host "[OK] Fix script already exists locally" -ForegroundColor Green
    
    # Run it directly
    cd C:\mt5_bridge_service
    python fix_unicode_logging.py
} else {
    Write-Host "[INFO] Script not found locally, needs download" -ForegroundColor Yellow
}
```

---

## 📞 Report Back

After running the fix, tell me:

**Option A: SUCCESS**
```
"Phase 1 complete! 
Status: healthy
MT5 Available: true (or false)
Ready for Phase 2?"
```

**Option B: ERROR**
```
"Phase 1 failed with error: [paste error message]"
```

---

**Next**: After Phase 1 succeeds, I'll provide Phase 2 PowerShell commands for the Task Scheduler fix!

**Estimated Time**: 5 minutes  
**Risk**: Very low (automatic backup created)
