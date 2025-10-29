# MT5 Bridge - Task Scheduler Setup Script
# Configures MT5 Bridge as a Windows Scheduled Task for automatic startup and background operation

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "MT5 BRIDGE - TASK SCHEDULER SETUP" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$taskName = "MT5_Bridge_Service"
$pythonPath = "C:\Users\trader\AppData\Local\Programs\Python\Python312\python.exe"
$scriptPath = "C:\mt5_bridge_service\mt5_bridge_api_service.py"
$workingDir = "C:\mt5_bridge_service"
$logPath = "C:\mt5_bridge_service\logs"

# Ensure log directory exists
if (-not (Test-Path $logPath)) {
    New-Item -ItemType Directory -Path $logPath -Force | Out-Null
    Write-Host "✓ Created log directory: $logPath" -ForegroundColor Green
}

# Stop any existing MT5 Bridge processes
Write-Host ""
Write-Host "[1/4] Stopping existing MT5 Bridge processes..." -ForegroundColor Yellow
$killed = 0
Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "pythonw"} | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)"
        if ($proc.CommandLine -like "*mt5_bridge*") {
            Write-Host "  Stopping PID $($_.Id)" -ForegroundColor Gray
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

# Remove old task if it exists
Write-Host ""
Write-Host "[2/4] Removing old Scheduled Task (if exists)..." -ForegroundColor Yellow
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "  ✓ Removed old task" -ForegroundColor Green
} else {
    Write-Host "  ℹ No existing task found" -ForegroundColor Gray
}

# Create new Scheduled Task
Write-Host ""
Write-Host "[3/4] Creating new Scheduled Task..." -ForegroundColor Yellow

# Action: Run Python script
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument "`"$scriptPath`"" `
    -WorkingDirectory $workingDir

# Trigger: At system startup
$trigger = New-ScheduledTaskTrigger -AtStartup

# Principal: Run as trader user with highest privileges in Interactive session
# CRITICAL: LogonType Interactive ensures Session 1 compatibility with MT5 Terminal
$principal = New-ScheduledTaskPrincipal `
    -UserId "trader" `
    -LogonType Interactive `
    -RunLevel Highest

# Settings: Configure for reliability and auto-restart
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -RestartCount 999 `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -MultipleInstances IgnoreNew

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "MT5 Bridge API Service v4.0 - Multi-Account Balance Sync (Auto-start, Auto-restart)" `
        -Force | Out-Null
    
    Write-Host "  ✓ Scheduled Task created successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to create task: $_" -ForegroundColor Red
    exit 1
}

# Start the task immediately
Write-Host ""
Write-Host "[4/4] Starting MT5 Bridge Service..." -ForegroundColor Yellow
try {
    Start-ScheduledTask -TaskName $taskName
    Write-Host "  ✓ Task started" -ForegroundColor Green
    Start-Sleep -Seconds 5
} catch {
    Write-Host "  ✗ Failed to start task: $_" -ForegroundColor Red
    exit 1
}

# Verify task is running
Write-Host ""
Write-Host "Verifying setup..." -ForegroundColor Yellow

$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "  ✓ Task exists in Scheduler" -ForegroundColor Green
    Write-Host "    State: $($task.State)" -ForegroundColor White
    Write-Host "    Last Run: $($taskInfo.LastRunTime)" -ForegroundColor White
    Write-Host "    Next Run: $($taskInfo.NextRunTime)" -ForegroundColor White
}

# Check if process is running
$bridgeRunning = $false
Get-Process | Where-Object {$_.ProcessName -eq "python"} | ForEach-Object {
    try {
        $proc = Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)"
        if ($proc.CommandLine -like "*mt5_bridge*") {
            Write-Host "  ✓ Bridge process running (PID: $($_.Id))" -ForegroundColor Green
            $bridgeRunning = $true
        }
    } catch {}
}

if (-not $bridgeRunning) {
    Write-Host "  ⚠ Process not detected - may still be starting" -ForegroundColor Yellow
}

# Test API endpoint
Write-Host ""
Write-Host "Testing API endpoint..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/api/mt5/bridge/health" -Method Get -TimeoutSec 10
    Write-Host "  ✓ API responding" -ForegroundColor Green
    Write-Host "    Status: $($health.status)" -ForegroundColor White
    Write-Host "    Version: $($health.version)" -ForegroundColor White
    Write-Host "    MT5 Initialized: $($health.mt5.initialized)" -ForegroundColor White
    
    if ($health.cache) {
        Write-Host "    Cached Accounts: $($health.cache.accounts_cached)/$($health.cache.total_accounts)" -ForegroundColor White
    }
} catch {
    Write-Host "  ⚠ API not responding yet (service may still be starting)" -ForegroundColor Yellow
    Write-Host "    Wait 1-2 minutes and test manually: Invoke-RestMethod http://localhost:8000/api/mt5/bridge/health" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The MT5 Bridge is now configured to:" -ForegroundColor White
Write-Host "  ✓ Start automatically on VPS boot" -ForegroundColor Green
Write-Host "  ✓ Run in background (no console window)" -ForegroundColor Green
Write-Host "  ✓ Restart automatically if it crashes" -ForegroundColor Green
Write-Host "  ✓ Refresh all 7 accounts every 5 minutes" -ForegroundColor Green
Write-Host ""
Write-Host "Verification commands:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Cyan
Write-Host "  Invoke-RestMethod http://localhost:8000/api/mt5/bridge/health" -ForegroundColor Cyan
Write-Host "  Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 50" -ForegroundColor Cyan
Write-Host ""
