# MT5 Bridge Multi-Account Fix - Direct Deployment Script
# Run this on the VPS to deploy the fixed bridge

Write-Host "========================================"
Write-Host "MT5 BRIDGE MULTI-ACCOUNT FIX DEPLOYMENT"
Write-Host "========================================"
Write-Host ""

# Download the fixed script from GitHub
Write-Host "Step 1: Downloading fixed MT5 Bridge script from GitHub..."
$scriptUrl = "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps-scripts/mt5_bridge_multi_account_fixed.py"
$destination = "C:\mt5_bridge_service\mt5_bridge_api_service.py"

try {
    Invoke-WebRequest -Uri $scriptUrl -OutFile $destination -UseBasicParsing
    Write-Host "✅ Script downloaded successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to download script: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Stopping existing MT5 Bridge processes..."

# Stop any existing Python processes running the bridge
Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "pythonw"} | ForEach-Object {
    try {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
        if ($cmdLine -like "*mt5_bridge*") {
            Write-Host "  Killing process $($_.Id): $($_.ProcessName)"
            Stop-Process -Id $_.Id -Force
        }
    } catch {
        Write-Host "  Could not check process $($_.Id)"
    }
}

Write-Host "✅ Old processes stopped" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Configuring Task Scheduler (Interactive Session)..."

# Delete old task if exists
$taskExists = Get-ScheduledTask -TaskName "MT5_Bridge_Service" -ErrorAction SilentlyContinue
if ($taskExists) {
    Unregister-ScheduledTask -TaskName "MT5_Bridge_Service" -Confirm:$false
    Write-Host "  Old task removed"
}

# Create new task with INTERACTIVE session (Session 1)
$action = New-ScheduledTaskAction `
    -Execute "C:\Users\trader\AppData\Local\Programs\Python\Python312\python.exe" `
    -Argument "C:\mt5_bridge_service\mt5_bridge_api_service.py" `
    -WorkingDirectory "C:\mt5_bridge_service"

$trigger = New-ScheduledTaskTrigger -AtStartup

# CRITICAL: Use Interactive logon type for Session 1
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

Register-ScheduledTask `
    -TaskName "MT5_Bridge_Service" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "MT5 Bridge API Service - Multi-Account Fixed (Interactive Session)" `
    -Force | Out-Null

Write-Host "✅ Task Scheduler configured (Interactive Session)" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Starting MT5 Bridge Service..."

Start-ScheduledTask -TaskName "MT5_Bridge_Service"
Start-Sleep -Seconds 5

# Check if process is running
$bridgeProcess = Get-Process | Where-Object {$_.ProcessName -eq "python"} | Where-Object {
    try {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
        $cmdLine -like "*mt5_bridge*"
    } catch {
        $false
    }
}

if ($bridgeProcess) {
    Write-Host "✅ MT5 Bridge Service is RUNNING (PID: $($bridgeProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "⚠️  Process not detected yet - may still be starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 5: Checking service logs..."
Write-Host "----------------------------------------"

if (Test-Path "C:\mt5_bridge_service\logs\api_service.log") {
    Get-Content "C:\mt5_bridge_service\logs\api_service.log" -Tail 30
} else {
    Write-Host "  Log file not created yet (service still starting)"
}

Write-Host ""
Write-Host "========================================"
Write-Host "DEPLOYMENT COMPLETE"
Write-Host "========================================"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "1. Wait 5-10 minutes for first account refresh cycle"
Write-Host "2. Test health endpoint: http://92.118.45.135:8000/api/mt5/bridge/health"
Write-Host "3. Check all accounts: http://92.118.45.135:8000/api/mt5/accounts/summary"
Write-Host "4. Verify dashboard shows real balances for all 7 accounts"
Write-Host ""
