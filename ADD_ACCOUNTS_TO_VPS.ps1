# PowerShell Script to Add Accounts 901351 and 901353 to VPS
# RUN THIS DIRECTLY ON THE VPS

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "MT5 ACCOUNTS ADDITION SCRIPT" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Try to find the correct configuration file
$possibleFiles = @(
    "C:\mt5_bridge_service\mt5_bridge_api_service.py",
    "C:\mt5_bridge_service\mt5_bridge_service_production.py",
    "C:\mt5_bridge_service\config.py",
    "C:\mt5_bridge_service\accounts.py"
)

Write-Host "Searching for configuration file..." -ForegroundColor Yellow
$configFile = $null
foreach ($file in $possibleFiles) {
    if (Test-Path $file) {
        Write-Host "  Found: $file" -ForegroundColor Green
        $content = Get-Content $file -Raw
        if ($content -match "885822|886066|886528") {
            $configFile = $file
            Write-Host "  ✅ This file contains MT5 accounts!" -ForegroundColor Green
            break
        }
    }
}

if (-not $configFile) {
    Write-Host "ERROR: Could not find configuration file with accounts!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please manually locate the file that contains:" -ForegroundColor Yellow
    Write-Host "- Account numbers like 885822, 886066, etc." -ForegroundColor White
    Write-Host "- And run this script with the file path" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Using configuration file: $configFile" -ForegroundColor Cyan
Write-Host ""

# Read file
$content = Get-Content $configFile -Raw

# Check if accounts already exist
if ($content -match "901351" -and $content -match "901353") {
    Write-Host "✅ Accounts 901351 and 901353 already exist in the file!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The file is correct. Try restarting the service:" -ForegroundColor Yellow
    Write-Host "  Get-Process python | Stop-Process -Force" -ForegroundColor White
    Write-Host "  cd C:\mt5_bridge_service" -ForegroundColor White
    Write-Host "  python mt5_bridge_api_service.py" -ForegroundColor White
    exit 0
}

# Show sample of file structure
Write-Host "File structure preview:" -ForegroundColor Yellow
Write-Host ($content.Substring(0, [Math]::Min(500, $content.Length))) -ForegroundColor Gray
Write-Host "..." -ForegroundColor Gray
Write-Host ""

# Create backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$configFile.backup_$timestamp"
Write-Host "Creating backup: $backupFile" -ForegroundColor Yellow
Copy-Item $configFile $backupFile
Write-Host "✅ Backup created" -ForegroundColor Green
Write-Host ""

# Manual instructions
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "MANUAL EDIT REQUIRED" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "I've created a backup of your configuration file." -ForegroundColor White
Write-Host ""
Write-Host "Please follow these steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open the file in Notepad:" -ForegroundColor White
Write-Host "   notepad $configFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Find where the accounts are listed" -ForegroundColor White
Write-Host "   (Search for account numbers like 885822)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Add these two entries in the same format:" -ForegroundColor White
Write-Host ""
Write-Host "   For account 901351:" -ForegroundColor Cyan
Write-Host '   {' -ForegroundColor Yellow
Write-Host '       "login": 901351,' -ForegroundColor Yellow
Write-Host '       "password": "Fidus13!",' -ForegroundColor Yellow
Write-Host '       "fund_type": "UNASSIGNED",' -ForegroundColor Yellow
Write-Host '       "target_amount": 0,' -ForegroundColor Yellow
Write-Host '       "client_name": "Account 901351 - Unassigned"' -ForegroundColor Yellow
Write-Host '   }' -ForegroundColor Yellow
Write-Host ""
Write-Host "   For account 901353:" -ForegroundColor Cyan
Write-Host '   {' -ForegroundColor Yellow
Write-Host '       "login": 901353,' -ForegroundColor Yellow
Write-Host '       "password": "Fidus13!",' -ForegroundColor Yellow
Write-Host '       "fund_type": "UNASSIGNED",' -ForegroundColor Yellow
Write-Host '       "target_amount": 0,' -ForegroundColor Yellow
Write-Host '       "client_name": "Account 901353 - Unassigned"' -ForegroundColor Yellow
Write-Host '   }' -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Save and close Notepad" -ForegroundColor White
Write-Host ""
Write-Host "5. Restart the service:" -ForegroundColor White
Write-Host "   Get-Process python | Stop-Process -Force" -ForegroundColor Yellow
Write-Host "   cd C:\mt5_bridge_service" -ForegroundColor Yellow
Write-Host "   python mt5_bridge_api_service.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "If you make a mistake, restore from backup:" -ForegroundColor Cyan
Write-Host "   Copy-Item $backupFile $configFile" -ForegroundColor Yellow
Write-Host ""
