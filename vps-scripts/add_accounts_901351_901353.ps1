# PowerShell Script to Add Accounts 901351 and 901353 to VPS Bridge Service
# Run this on the VPS

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "ADDING ACCOUNTS 901351 AND 901353 TO VPS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$configFile = "C:\mt5_bridge_service\mt5_bridge_service_production.py"

# Check if file exists
if (-not (Test-Path $configFile)) {
    Write-Host "ERROR: Configuration file not found!" -ForegroundColor Red
    Write-Host "Expected: $configFile" -ForegroundColor Yellow
    exit 1
}

Write-Host "Reading configuration file..." -ForegroundColor Yellow
$content = Get-Content $configFile -Raw

# Find ACCOUNTS list
$accountsStart = $content.IndexOf("ACCOUNTS = [")
if ($accountsStart -eq -1) {
    Write-Host "ERROR: Could not find ACCOUNTS list in configuration file!" -ForegroundColor Red
    exit 1
}

# Find closing bracket
$accountsEnd = $content.IndexOf("]", $accountsStart)
if ($accountsEnd -eq -1) {
    Write-Host "ERROR: Could not find end of ACCOUNTS list!" -ForegroundColor Red
    exit 1
}

Write-Host "Found ACCOUNTS list at position $accountsStart" -ForegroundColor Green

# Check if accounts already exist
if ($content -match '"login":\s*901351' -or $content -match "'login':\s*901351") {
    Write-Host "Account 901351 already exists in configuration!" -ForegroundColor Yellow
} else {
    Write-Host "Account 901351 will be added" -ForegroundColor Green
}

if ($content -match '"login":\s*901353' -or $content -match "'login':\s*901353") {
    Write-Host "Account 901353 already exists in configuration!" -ForegroundColor Yellow
} else {
    Write-Host "Account 901353 will be added" -ForegroundColor Green
}

# New account entries
$newAccount1 = @"
    {
        "login": 901351,
        "password": "Fidus13!",
        "fund_type": "UNASSIGNED",
        "target_amount": 0,
        "client_name": "Account 901351 - Unassigned"
    }
"@

$newAccount2 = @"
    {
        "login": 901353,
        "password": "Fidus13!",
        "fund_type": "UNASSIGNED",
        "target_amount": 0,
        "client_name": "Account 901353 - Unassigned"
    }
"@

# Insert accounts before closing bracket
$beforeClosing = $content.Substring(0, $accountsEnd)
$afterClosing = $content.Substring($accountsEnd)

$updatedContent = $beforeClosing + ",`n" + $newAccount1 + ",`n" + $newAccount2 + "`n" + $afterClosing

# Backup original file
$backupFile = "$configFile.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host ""
Write-Host "Creating backup: $backupFile" -ForegroundColor Yellow
Copy-Item $configFile $backupFile

# Write updated content
Write-Host "Writing updated configuration..." -ForegroundColor Yellow
Set-Content $configFile -Value $updatedContent -Encoding UTF8

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "CONFIGURATION UPDATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backup saved to: $backupFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Stop the Python service" -ForegroundColor White
Write-Host "2. Restart the Python service" -ForegroundColor White
Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "  Get-Process python | Stop-Process -Force" -ForegroundColor White
Write-Host "  cd C:\mt5_bridge_service" -ForegroundColor White
Write-Host "  python mt5_bridge_service_production.py" -ForegroundColor White
Write-Host ""
