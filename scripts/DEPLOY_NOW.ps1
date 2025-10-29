# ============================================
# MT5 BRIDGE MULTI-ACCOUNT FIX - DEPLOY NOW
# ============================================
# Copy this ENTIRE script and run in PowerShell on VPS

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "MT5 BRIDGE MULTI-ACCOUNT FIX DEPLOYMENT" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Download fixed script
Write-Host "[1/5] Downloading fixed MT5 Bridge script..." -ForegroundColor Yellow
$scriptUrl = "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps-scripts/mt5_bridge_multi_account_fixed.py"
$destination = "C:\mt5_bridge_service\mt5_bridge_api_service.py"
$backupPath = "C:\mt5_bridge_service\mt5_bridge_api_service_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').py"

try {
    # Backup current script
    if (Test-Path $destination) {
        Copy-Item $destination $backupPath
        Write-Host "  ✓ Backed up current script to: $backupPath" -ForegroundColor Green
    }
    
    # Download new script
    Invoke-WebRequest -Uri $scriptUrl -OutFile $destination -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✓ Downloaded fixed script successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to download: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "MANUAL FALLBACK:" -ForegroundColor Yellow
    Write-Host "1. Open browser and go to:" -ForegroundColor White
    Write-Host "   https://github.com/chavapalmarubin-lab/FIDUS/blob/main/vps-scripts/mt5_bridge_multi_account_fixed.py" -ForegroundColor Cyan
    Write-Host "2. Click 'Raw' button" -ForegroundColor White
    Write-Host "3. Save file as: C:\mt5_bridge_service\mt5_bridge_api_service.py" -ForegroundColor White
    exit 1
}

Write-Host ""

# Step 2: Stop existing processes
Write-Host "[2/5] Stopping existing MT5 Bridge processes..." -ForegroundColor Yellow
$killed = 0
Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "pythonw"} | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)"
        if ($proc.CommandLine -like "*mt5_bridge*") {
            Write-Host "  Killing PID $($_.Id)" -ForegroundColor Gray
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            $killed++
        }
    } catch {}
}
if ($killed -gt 0) {
    Write-Host "  ✓ Stopped $killed process(es)" -ForegroundColor Green
} else {
    Write-Host "  ℹ No existing processes found" -ForegroundColor Gray
}

Write-Host ""

# Step 3: Configure Task Scheduler
Write-Host "[3/5] Configuring Task Scheduler (Interactive Session)..." -ForegroundColor Yellow

# Remove old task
$taskName = "MT5_Bridge_Service"
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "  Removed old task" -ForegroundColor Gray
}

# Create new task
$action = New-ScheduledTaskAction `
    -Execute "C:\Users\trader\AppData\Local\Programs\Python\Python312\python.exe" `
    -Argument "C:\mt5_bridge_service\mt5_bridge_api_service.py" `
    -WorkingDirectory "C:\mt5_bridge_service"

$trigger = New-ScheduledTaskTrigger -AtStartup

# CRITICAL: Interactive session
$principal = New-ScheduledTaskPrincipal `
    -UserId "trader" `
    -LogonType Interactive `
    -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -RestartCount 999 `
    -ExecutionTimeLimit (New-TimeSpan -Days 365)

try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "MT5 Bridge v4.0 - Multi-Account Fixed (Interactive Session)" `
        -Force | Out-Null
    Write-Host "  ✓ Task Scheduler configured successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to create task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Start service
Write-Host "[4/5] Starting MT5 Bridge Service..." -ForegroundColor Yellow
try {
    Start-ScheduledTask -TaskName $taskName
    Write-Host "  ✓ Service started" -ForegroundColor Green
    Start-Sleep -Seconds 5
} catch {
    Write-Host "  ✗ Failed to start: $_" -ForegroundColor Red
}

# Check if running
$bridgeRunning = $false
Get-Process | Where-Object {$_.ProcessName -eq "python"} | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)"
        if ($proc.CommandLine -like "*mt5_bridge*") {
            Write-Host "  ✓ Bridge running (PID: $($_.Id))" -ForegroundColor Green
            $bridgeRunning = $true
        }
    } catch {}
}

if (-not $bridgeRunning) {
    Write-Host "  ⚠ Process not detected - checking logs..." -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Verify deployment
Write-Host "[5/5] Verifying deployment..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/mt5/bridge/health" -Method Get -TimeoutSec 10
    Write-Host "  ✓ Bridge responding" -ForegroundColor Green
    Write-Host "    Status: $($health.status)" -ForegroundColor White
    Write-Host "    Version: $($health.version)" -ForegroundColor White
    Write-Host "    MT5 Initialized: $($health.mt5.initialized)" -ForegroundColor White
    
    if ($health.cache) {
        Write-Host "    Accounts Cached: $($health.cache.accounts_cached)/$($health.cache.total_accounts)" -ForegroundColor White
    }
} catch {
    Write-Host "  ⚠ Bridge not responding yet (may still be starting)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Show recent logs
if (Test-Path "C:\mt5_bridge_service\logs\api_service.log") {
    Write-Host "Recent logs (last 30 lines):" -ForegroundColor Yellow
    Write-Host "--------------------------------------------" -ForegroundColor Gray
    Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 30
} else {
    Write-Host "Log file not created yet" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Wait 5-10 minutes for account refresh cycle" -ForegroundColor White
Write-Host "2. Test: Invoke-RestMethod http://localhost:8000/api/mt5/accounts/summary" -ForegroundColor White
Write-Host "3. Check logs: Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 50" -ForegroundColor White
Write-Host "4. Monitor dashboard for all 7 account balances" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
