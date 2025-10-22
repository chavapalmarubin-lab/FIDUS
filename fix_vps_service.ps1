# VPS Service Fix Script
# Run this on the VPS via RDP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VPS SERVICE FIX SCRIPT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Navigate to directory
Write-Host "Step 1: Navigate to service directory" -ForegroundColor Yellow
cd C:\mt5_bridge_service
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Step 2: Check current git status
Write-Host "Step 2: Check git status" -ForegroundColor Yellow
git status
Write-Host ""

# Step 3: Stop ALL Python processes
Write-Host "Step 3: Stop all Python processes" -ForegroundColor Yellow
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "Found $($pythonProcs.Count) Python process(es). Stopping..." -ForegroundColor Red
    Get-Process python | Stop-Process -Force
    Start-Sleep -Seconds 3
    Write-Host "✅ All Python processes stopped" -ForegroundColor Green
} else {
    Write-Host "✅ No Python processes running" -ForegroundColor Green
}
Write-Host ""

# Step 4: Verify port 8000 is free
Write-Host "Step 4: Verify port 8000 is free" -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "Port 8000 is occupied. Killing process..." -ForegroundColor Red
    $port8000 | ForEach-Object {
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "✅ Port 8000 freed" -ForegroundColor Green
} else {
    Write-Host "✅ Port 8000 is free" -ForegroundColor Green
}
Write-Host ""

# Step 5: Pull latest code
Write-Host "Step 5: Pull latest code from GitHub" -ForegroundColor Yellow
git pull origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Git pull had issues but continuing..." -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Check if new endpoints exist in code
Write-Host "Step 6: Verify new code has required endpoints" -ForegroundColor Yellow
$content = Get-Content vps\mt5_bridge_api_service.py -Raw
if ($content -match "one_time_setup") {
    Write-Host "✅ Found one_time_setup endpoint in code" -ForegroundColor Green
} else {
    Write-Host "❌ one_time_setup endpoint NOT found in code!" -ForegroundColor Red
    Write-Host "This means the git pull didn't get the latest code." -ForegroundColor Red
}

if ($content -match "emergency_restart") {
    Write-Host "✅ Found emergency_restart endpoint in code" -ForegroundColor Green
} else {
    Write-Host "❌ emergency_restart endpoint NOT found in code!" -ForegroundColor Red
}
Write-Host ""

# Step 7: Check for the correct file
Write-Host "Step 7: Check which file to run" -ForegroundColor Yellow
if (Test-Path "vps\mt5_bridge_api_service.py") {
    Write-Host "✅ vps\mt5_bridge_api_service.py exists" -ForegroundColor Green
    Write-Host "NOTE: Service should run from vps\ subdirectory!" -ForegroundColor Yellow
    $serviceFile = "vps\mt5_bridge_api_service.py"
} elseif (Test-Path "mt5_bridge_api_service.py") {
    Write-Host "✅ mt5_bridge_api_service.py exists (root)" -ForegroundColor Green
    $serviceFile = "mt5_bridge_api_service.py"
} else {
    Write-Host "❌ No service file found!" -ForegroundColor Red
    Write-Host "Listing files:" -ForegroundColor Yellow
    Get-ChildItem -Recurse -Filter "*.py" | Select-Object FullName
    Exit 1
}
Write-Host ""

# Step 8: Install/update dependencies
Write-Host "Step 8: Check dependencies" -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt --break-system-packages 2>&1 | Select-String "Successfully|Requirement|ERROR" | ForEach-Object { Write-Host $_ }
    Write-Host "✅ Dependencies checked" -ForegroundColor Green
} else {
    Write-Host "⚠️ No requirements.txt found" -ForegroundColor Yellow
}
Write-Host ""

# Step 9: Start the service
Write-Host "Step 9: Start MT5 Bridge service" -ForegroundColor Yellow
Write-Host "Starting: python $serviceFile" -ForegroundColor Cyan

# Create logs directory if needed
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}

# Start service in background
$process = Start-Process python -ArgumentList $serviceFile `
    -RedirectStandardOutput "logs\service_startup.log" `
    -RedirectStandardError "logs\error_startup.log" `
    -PassThru -WindowStyle Hidden

Write-Host "✅ Service started with PID: $($process.Id)" -ForegroundColor Green
Write-Host "Waiting 15 seconds for service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15
Write-Host ""

# Step 10: Verify service is running
Write-Host "Step 10: Verify service health" -ForegroundColor Yellow

# Check if process is still running
$stillRunning = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
if (-not $stillRunning) {
    Write-Host "❌ Service process died! Check error log:" -ForegroundColor Red
    Get-Content logs\error_startup.log -Tail 30
    Exit 1
}

# Check health endpoint
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -Method Get -TimeoutSec 10 -UseBasicParsing
    Write-Host "✅ Health endpoint responding: HTTP $($response.StatusCode)" -ForegroundColor Green
    $health = $response.Content | ConvertFrom-Json
    Write-Host "   Status: $($health.status)" -ForegroundColor Green
    Write-Host "   MT5 Available: $($health.mt5.available)" -ForegroundColor Green
    Write-Host "   MongoDB Connected: $($health.mongodb.connected)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health endpoint not responding!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Service log (last 30 lines):" -ForegroundColor Yellow
    Get-Content logs\service_startup.log -Tail 30 -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "Error log (last 30 lines):" -ForegroundColor Yellow
    Get-Content logs\error_startup.log -Tail 30 -ErrorAction SilentlyContinue
    Exit 1
}
Write-Host ""

# Step 11: Check new endpoints
Write-Host "Step 11: Check new endpoints" -ForegroundColor Yellow
try {
    $setupTest = Invoke-WebRequest -Uri "http://localhost:8000/api/admin/one-time-setup?setup_key=test" -Method Post -ErrorAction Stop
    Write-Host "⚠️ Setup endpoint exists (got response)" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ Setup endpoint exists (401 = endpoint found, auth required)" -ForegroundColor Green
    } elseif ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "❌ Setup endpoint NOT FOUND" -ForegroundColor Red
        Write-Host "The new code is NOT running. Old version still active." -ForegroundColor Red
    } else {
        Write-Host "⚠️ Setup endpoint status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

try {
    $restartTest = Invoke-WebRequest -Uri "http://localhost:8000/api/admin/emergency-restart?token=test" -Method Post -ErrorAction Stop
    Write-Host "⚠️ Emergency restart endpoint exists" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ Emergency restart endpoint exists (401 = endpoint found, auth required)" -ForegroundColor Green
    } elseif ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "❌ Emergency restart endpoint NOT FOUND" -ForegroundColor Red
    } else {
        Write-Host "⚠️ Emergency restart endpoint status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}
Write-Host ""

# Final summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FIX COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service Status: RUNNING" -ForegroundColor Green
Write-Host "Process ID: $($process.Id)" -ForegroundColor Green
Write-Host "Health: VERIFIED" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If new endpoints are missing, the git pull may not have worked correctly" -ForegroundColor Yellow
Write-Host "2. Check that you're running the file from vps\ subdirectory if that's where the new code is" -ForegroundColor Yellow
Write-Host "3. Report back to Emergent with the results" -ForegroundColor Yellow
Write-Host ""
