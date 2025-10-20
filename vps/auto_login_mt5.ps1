# MT5 Auto-Login Script
# This script automatically logs into MT5 account 886557 on VPS startup
# Deployed and managed via GitHub Actions

Write-Host "=== MT5 AUTO-LOGIN SCRIPT STARTING ===" -ForegroundColor Green
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow

# Configuration
$MT5_ACCOUNT = "886557"
$MT5_SERVER = "MEXAtlantic-Real"
$MT5_PASSWORD_ENV = $env:MT5_MASTER_PASSWORD
$LOG_FILE = "C:\mt5_bridge_service\logs\auto_login.log"

# Create logs directory if it doesn't exist
$LOG_DIR = "C:\mt5_bridge_service\logs"
if (!(Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
    Write-Host "Created logs directory: $LOG_DIR" -ForegroundColor Yellow
}

# Function to log messages
function Write-Log {
    param($Message, $Color = "White")
    $Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LOG_FILE -Value $LogMessage
}

Write-Log "Starting MT5 auto-login process..." "Green"

# Check if Python is installed
Write-Log "Checking Python installation..." "Yellow"
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (!$pythonPath) {
    Write-Log "ERROR: Python not found. Please install Python 3.8+." "Red"
    exit 1
}
Write-Log "Python found at: $($pythonPath.Path)" "Green"

# Check if MetaTrader5 package is installed
Write-Log "Checking MetaTrader5 Python package..." "Yellow"
$mt5Installed = python -c "import MetaTrader5; print('installed')" 2>$null
if ($mt5Installed -ne "installed") {
    Write-Log "MetaTrader5 package not found. Installing..." "Yellow"
    python -m pip install MetaTrader5 --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Log "MetaTrader5 package installed successfully" "Green"
    } else {
        Write-Log "ERROR: Failed to install MetaTrader5 package" "Red"
        exit 1
    }
} else {
    Write-Log "MetaTrader5 package already installed" "Green"
}

# Wait for MT5 terminal to start (if it's starting up)
Write-Log "Waiting for MT5 terminal to be ready..." "Yellow"
Start-Sleep -Seconds 10

# Create Python script for MT5 login
$pythonScript = @"
import MetaTrader5 as mt5
import sys
import os
from datetime import datetime

def log_message(message, level='INFO'):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] [{level}] {message}')

def login_mt5():
    log_message('Initializing MT5 connection...')
    
    # Initialize MT5
    if not mt5.initialize():
        log_message(f'MT5 initialization failed: {mt5.last_error()}', 'ERROR')
        return False
    
    log_message('MT5 initialized successfully')
    
    # Get account credentials from environment
    account = int('$MT5_ACCOUNT')
    password = os.environ.get('MT5_MASTER_PASSWORD', '')
    server = '$MT5_SERVER'
    
    if not password:
        log_message('MT5_MASTER_PASSWORD environment variable not set', 'ERROR')
        mt5.shutdown()
        return False
    
    log_message(f'Attempting to login to account {account} on server {server}...')
    
    # Attempt login
    authorized = mt5.login(account, password=password, server=server)
    
    if authorized:
        account_info = mt5.account_info()
        if account_info:
            log_message(f'Login successful!', 'SUCCESS')
            log_message(f'Account: {account_info.login}')
            log_message(f'Server: {account_info.server}')
            log_message(f'Balance: {account_info.balance}')
            log_message(f'Equity: {account_info.equity}')
            log_message(f'Connection status: {"Connected" if account_info.trade_allowed else "Not trading"}')
            mt5.shutdown()
            return True
        else:
            log_message('Login succeeded but could not retrieve account info', 'WARNING')
            mt5.shutdown()
            return True
    else:
        error = mt5.last_error()
        log_message(f'Login failed: {error}', 'ERROR')
        mt5.shutdown()
        return False

if __name__ == '__main__':
    try:
        success = login_mt5()
        sys.exit(0 if success else 1)
    except Exception as e:
        log_message(f'Exception occurred: {str(e)}', 'ERROR')
        sys.exit(1)
"@

# Save Python script to temp file
$pythonScriptPath = "C:\mt5_bridge_service\mt5_login.py"
$pythonScript | Out-File -FilePath $pythonScriptPath -Encoding UTF8 -Force
Write-Log "Created Python login script at: $pythonScriptPath" "Green"

# Execute Python script
Write-Log "Executing MT5 login..." "Yellow"
$output = python $pythonScriptPath 2>&1
$exitCode = $LASTEXITCODE

# Log output
foreach ($line in $output) {
    Write-Log $line "Cyan"
}

if ($exitCode -eq 0) {
    Write-Log "MT5 auto-login completed successfully!" "Green"
    Write-Log "Account 886557 is now logged in and ready" "Green"
} else {
    Write-Log "MT5 auto-login failed with exit code: $exitCode" "Red"
    Write-Log "Please check the logs and environment variables" "Red"
}

Write-Log "=== MT5 AUTO-LOGIN SCRIPT COMPLETED ===" "Green"
exit $exitCode
