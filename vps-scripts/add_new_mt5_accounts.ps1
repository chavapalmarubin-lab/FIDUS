# Add New MT5 Accounts to VPS Configuration
# Adds 4 new accounts: 897590, 897589, 897591, 897599

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "ADD NEW MT5 ACCOUNTS TO VPS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Stopping MT5 Bridge Service..." -ForegroundColor Yellow
try {
    schtasks /End /TN MT5BridgeService 2>$null
    Start-Sleep -Seconds 3
    Write-Host "  Service stopped" -ForegroundColor Green
} catch {
    Write-Host "  Service not running" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/2] Restarting MT5 Bridge Service (will pick up new accounts)..." -ForegroundColor Yellow
try {
    schtasks /Run /TN MT5BridgeService
    Start-Sleep -Seconds 10
    Write-Host "  Service restarted" -ForegroundColor Green
} catch {
    Write-Host "  Failed to restart service" -ForegroundColor Red
}

Write-Host ""
Write-Host "Verifying accounts..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $summary = Invoke-RestMethod -Uri "http://localhost:8000/api/mt5/accounts/summary" -Method Get -TimeoutSec 15
    $totalAccounts = $summary.accounts.Count
    Write-Host "  Total accounts in bridge: $totalAccounts" -ForegroundColor White
    
    if ($totalAccounts -eq 11) {
        Write-Host "  SUCCESS: All 11 accounts in system!" -ForegroundColor Green
    } else {
        Write-Host "  Expected 11, found $totalAccounts" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Could not verify via API" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "CONFIGURATION COMPLETE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The VPS Bridge will now sync all 11 accounts automatically." -ForegroundColor Green
Write-Host ""
