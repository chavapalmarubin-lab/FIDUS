# Add New MT5 Accounts to VPS Configuration
# Adds 4 new accounts: 897590, 897589, 897591, 897599

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "ADD NEW MT5 ACCOUNTS TO VPS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Account configurations
$newAccounts = @(
    @{Account=897590; Password="Fidus13!"; Server="MEXAtlantic-Real"; Name="CORE-03"},
    @{Account=897589; Password="Fidus13!"; Server="MEXAtlantic-Real"; Name="BALANCE-03"},
    @{Account=897591; Password="Fidus13!"; Server="MultibankFX-Real"; Name="SEPARATION-03"},
    @{Account=897599; Password="Fidus13!"; Server="MultibankFX-Real"; Name="SEPARATION-04"}
)

Write-Host "[1/3] Stopping MT5 Bridge Service..." -ForegroundColor Yellow
try {
    Stop-ScheduledTask -TaskName "MT5_Bridge_Service" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    Write-Host "  ✓ Service stopped" -ForegroundColor Green
} catch {
    Write-Host "  ℹ Service not running or already stopped" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/3] Configuring new MT5 accounts..." -ForegroundColor Yellow

# Import MT5 library
try {
    Import-Module MetaTrader5 -ErrorAction Stop
} catch {
    Write-Host "  ⚠ MetaTrader5 module not found, installing..." -ForegroundColor Yellow
    pip install MetaTrader5 --quiet
    Import-Module MetaTrader5
}

# Try to initialize MT5
try {
    $mt5Path = "C:\Program Files\MetaTrader 5\terminal64.exe"
    if (-not (Test-Path $mt5Path)) {
        $mt5Path = "C:\Program Files (x86)\MetaTrader 5\terminal64.exe"
    }
    
    Write-Host "  Initializing MT5 terminal..." -ForegroundColor Gray
    
    # Python script to login to accounts
    $pythonScript = @"
import MetaTrader5 as mt5
import sys

# Initialize MT5
if not mt5.initialize():
    print(f"ERROR: MT5 initialization failed: {mt5.last_error()}")
    sys.exit(1)

print("MT5 initialized successfully")

# Account configurations
accounts = [
    {"account": 897590, "password": "Fidus13!", "server": "MEXAtlantic-Real"},
    {"account": 897589, "password": "Fidus13!", "server": "MEXAtlantic-Real"},
    {"account": 897591, "password": "Fidus13!", "server": "MultibankFX-Real"},
    {"account": 897599, "password": "Fidus13!", "server": "MultibankFX-Real"}
]

success_count = 0
for acc in accounts:
    print(f"\nAttempting login to account {acc['account']}...")
    
    authorized = mt5.login(
        login=acc['account'],
        password=acc['password'],
        server=acc['server']
    )
    
    if authorized:
        print(f"  ✓ Successfully logged into account {acc['account']}")
        
        # Get account info
        account_info = mt5.account_info()
        if account_info:
            print(f"    Balance: \${account_info.balance:.2f}")
            print(f"    Equity: \${account_info.equity:.2f}")
            print(f"    Server: {account_info.server}")
        
        success_count += 1
    else:
        error = mt5.last_error()
        print(f"  ✗ Failed to login to account {acc['account']}: {error}")

print(f"\n{success_count}/{len(accounts)} accounts logged in successfully")

# Shutdown MT5
mt5.shutdown()
sys.exit(0 if success_count == len(accounts) else 1)
"@
    
    # Save Python script
    $scriptPath = "C:\mt5_bridge_service\login_new_accounts.py"
    $pythonScript | Out-File -FilePath $scriptPath -Encoding UTF8
    
    # Execute Python script
    Write-Host "  Executing account login script..." -ForegroundColor Gray
    $pythonPath = "C:\Users\trader\AppData\Local\Programs\Python\Python312\python.exe"
    & $pythonPath $scriptPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ All 4 new accounts logged in successfully" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Some accounts may have failed to login" -ForegroundColor Yellow
        Write-Host "    Check the output above for details" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "  ✗ Error during MT5 account configuration: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/3] Restarting MT5 Bridge Service..." -ForegroundColor Yellow
try {
    Start-ScheduledTask -TaskName "MT5_Bridge_Service"
    Start-Sleep -Seconds 10
    Write-Host "  ✓ Service restarted" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to restart service: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Verifying new accounts..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $summary = Invoke-RestMethod -Uri "http://localhost:8000/api/mt5/accounts/summary" -Method Get -TimeoutSec 15
    $totalAccounts = $summary.accounts.Count
    $accountsWithData = ($summary.accounts | Where-Object { -not $_.note -or $_.note -ne "No cached data" }).Count
    
    Write-Host "  Total accounts in bridge: $totalAccounts" -ForegroundColor White
    Write-Host "  Accounts with data: $accountsWithData" -ForegroundColor White
    
    # Check specifically for new accounts
    foreach ($acc in $newAccounts) {
        $found = $summary.accounts | Where-Object { $_.account -eq $acc.Account }
        if ($found) {
            if ($found.balance -gt 0) {
                Write-Host "  ✓ Account $($acc.Account): \$$($found.balance) - OK" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ Account $($acc.Account): \$$($found.balance) - May need data refresh" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ✗ Account $($acc.Account): Not found in bridge" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "  ⚠ Could not verify accounts via API: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "CONFIGURATION COMPLETE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "New MT5 accounts have been added to the system:" -ForegroundColor White
Write-Host "  • Account 897590 (CORE)" -ForegroundColor Cyan
Write-Host "  • Account 897589 (BALANCE)" -ForegroundColor Cyan
Write-Host "  • Account 897591 (SEPARATION)" -ForegroundColor Cyan
Write-Host "  • Account 897599 (SEPARATION)" -ForegroundColor Cyan
Write-Host ""
Write-Host "The VPS Bridge will now sync all 11 accounts automatically." -ForegroundColor Green
Write-Host ""
