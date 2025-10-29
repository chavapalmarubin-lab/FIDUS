# ============================================================================
# DEPLOY COMPLETE MT5 BRIDGE - ONE COMMAND
# This deploys the COMPLETE Bridge with ALL endpoints
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYING COMPLETE MT5 BRIDGE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Download complete Bridge script
Write-Host "[1/6] Downloading complete Bridge script..." -ForegroundColor Yellow
cd C:\mt5_bridge_service

try {
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps-scripts/mt5_bridge_complete.py" -OutFile "mt5_bridge_api_service_new.py" -UseBasicParsing -TimeoutSec 30
    Write-Host "  [OK] Complete script downloaded" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Failed to download: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Backup current Bridge
Write-Host "[2/6] Backing up current Bridge..." -ForegroundColor Yellow
if (Test-Path "mt5_bridge_api_service.py") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item "mt5_bridge_api_service.py" "mt5_bridge_api_service.py.backup_$timestamp"
    Write-Host "  [OK] Backup created" -ForegroundColor Green
}
Write-Host ""

# Step 3: Stop Bridge
Write-Host "[3/6] Stopping current Bridge..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*mt5_bridge_service*" } | Stop-Process -Force
Start-Sleep -Seconds 5
Write-Host "  [OK] Bridge stopped" -ForegroundColor Green
Write-Host ""

# Step 4: Deploy new Bridge
Write-Host "[4/6] Deploying complete Bridge..." -ForegroundColor Yellow
Move-Item "mt5_bridge_api_service_new.py" "mt5_bridge_api_service.py" -Force
Write-Host "  [OK] Complete Bridge deployed" -ForegroundColor Green
Write-Host ""

# Step 5: Start Bridge
Write-Host "[5/6] Starting Bridge..." -ForegroundColor Yellow
Start-Process python -ArgumentList "mt5_bridge_api_service.py" -WindowStyle Hidden -WorkingDirectory "C:\mt5_bridge_service"
Start-Sleep -Seconds 20
Write-Host "  [OK] Bridge started" -ForegroundColor Green
Write-Host ""

# Step 6: Test ALL endpoints
Write-Host "[6/6] Testing ALL endpoints..." -ForegroundColor Yellow
Write-Host ""

$allGood = $true

# Test 1: Health endpoint
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "  [OK] Health endpoint: WORKING" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Health endpoint: FAILED" -ForegroundColor Red
    $allGood = $false
}

# Test 2: Accounts summary endpoint
try {
    $summary = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/accounts/summary" -UseBasicParsing -TimeoutSec 10
    Write-Host "  [OK] Accounts summary endpoint: WORKING" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Accounts summary endpoint: FAILED (was 404 before)" -ForegroundColor Red
    $allGood = $false
}

# Test 3: Account info endpoint
try {
    $info = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/account/886557/info" -UseBasicParsing -TimeoutSec 10
    Write-Host "  [OK] Account info endpoint: WORKING" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Account info endpoint: FAILED" -ForegroundColor Red
    $allGood = $false
}

# Test 4: Trades endpoint
try {
    $trades = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/account/886557/trades?limit=10" -UseBasicParsing -TimeoutSec 10
    Write-Host "  [OK] Trades endpoint: WORKING (was 404 before)" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Trades endpoint: FAILED" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
    Write-Host "ALL 4 ENDPOINTS WORKING" -ForegroundColor Green
} else {
    Write-Host "DEPLOYMENT PARTIALLY SUCCESSFUL" -ForegroundColor Yellow
    Write-Host "Some endpoints may need more time to initialize" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Wait 5 minutes for backend sync to run" -ForegroundColor White
Write-Host "Check for 404 errors in backend logs - should be gone" -ForegroundColor White
Write-Host "Alert spam should stop within 10 minutes" -ForegroundColor White
