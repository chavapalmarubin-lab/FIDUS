# Emergency Fix - MT5 Bridge Showing Zeros

## Current Situation

**Problem**: Task Scheduler task "MT5 Bridge Service" does not exist on VPS
**Impact**: Cannot restart Bridge via Task Scheduler
**Need**: Find how Bridge is actually running and restart it properly

---

## Diagnostic Commands - Run on VPS

```powershell
# 1. Find how Bridge is running
Write-Host "=== FINDING MT5 BRIDGE PROCESS ===" -ForegroundColor Cyan
Get-Process python | Select-Object Id, ProcessName, Path, StartTime

# 2. Check if it's a Windows Service
Get-Service | Where-Object { $_.Name -like "*mt5*" -or $_.Name -like "*bridge*" }

# 3. Check Task Scheduler tasks
Get-ScheduledTask | Where-Object { $_.TaskName -like "*mt5*" -or $_.TaskName -like "*bridge*" }

# 4. Check what's listening on port 8000
netstat -ano | findstr ":8000"

# 5. Check Bridge health
curl http://localhost:8000/api/mt5/bridge/health
```

---

## Quick Restart (Based on Process)

```powershell
Write-Host "=== RESTARTING MT5 TERMINAL AND BRIDGE ===" -ForegroundColor Cyan

# 1. Restart MT5 Terminal
Write-Host "Stopping MT5 Terminal..." -ForegroundColor Yellow
Get-Process -Name terminal64 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 5

Write-Host "Starting MT5 Terminal..." -ForegroundColor Yellow
Start-Process "C:\Program Files\MetaTrader 5\terminal64.exe"
Start-Sleep -Seconds 30

# 2. Restart Bridge (by killing and restarting Python process)
Write-Host "Stopping Bridge..." -ForegroundColor Yellow
Get-Process python | Where-Object { $_.Path -like "*mt5*" } | Stop-Process -Force
Start-Sleep -Seconds 5

# 3. Find and restart Bridge
Write-Host "Starting Bridge..." -ForegroundColor Yellow

# Check common locations
$bridgePaths = @(
    "C:\mt5_bridge_service\mt5_bridge_api_service.py",
    "C:\mt5-bridge\mt5_bridge_api_service.py",
    "C:\mt5_bridge\mt5_bridge_api_service.py"
)

foreach ($path in $bridgePaths) {
    if (Test-Path $path) {
        Write-Host "Found Bridge at: $path" -ForegroundColor Green
        $bridgeDir = Split-Path $path
        cd $bridgeDir
        Start-Process python -ArgumentList "mt5_bridge_api_service.py" -WindowStyle Hidden
        Write-Host "Bridge started!" -ForegroundColor Green
        break
    }
}

Start-Sleep -Seconds 15

# 4. Verify
Write-Host "`n=== VERIFICATION ===" -ForegroundColor Cyan
curl http://localhost:8000/api/mt5/bridge/health

Write-Host "`nDone! Wait 1-2 minutes and refresh dashboard." -ForegroundColor Green
```

---

## If Bridge Doesn't Auto-Start

The Bridge needs to be configured to start automatically. After we fix the zero balance issue, we'll set up proper auto-start.

**For now, just restart it manually as shown above.**
