# PowerShell script to deploy the account-switching MT5 Bridge to VPS
# Run this on the VPS directly

Write-Host "=" * 80
Write-Host "DEPLOYING MT5 BRIDGE WITH ACCOUNT SWITCHING"
Write-Host "=" * 80

# Stop existing service
Write-Host "`nStopping any running MT5 Bridge..."
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*MT5_Bridge*"} | Stop-Process -Force
Start-Sleep -Seconds 2

# Create directory
$bridgeDir = "C:\MT5_Bridge"
if (!(Test-Path $bridgeDir)) {
    New-Item -Path $bridgeDir -ItemType Directory
    Write-Host "Created directory: $bridgeDir"
}

# Download the script from GitHub
Write-Host "`nDownloading MT5 Bridge script from GitHub..."
$scriptUrl = "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps-scripts/mt5_bridge_account_switching.py"
$scriptPath = "$bridgeDir\mt5_bridge_service.py"

try {
    Invoke-WebRequest -Uri $scriptUrl -OutFile $scriptPath
    Write-Host "✅ Script downloaded successfully"
} catch {
    Write-Host "❌ Failed to download script: $_"
    Write-Host "`nManual installation required:"
    Write-Host "1. Copy mt5_bridge_account_switching.py to $scriptPath"
    Write-Host "2. Run: python $scriptPath"
    exit 1
}

# Install Python packages
Write-Host "`nInstalling required Python packages..."
pip install fastapi uvicorn MetaTrader5 pymongo python-multipart

# Start the service
Write-Host "`nStarting MT5 Bridge service..."
Start-Process python -ArgumentList $scriptPath -WorkingDirectory $bridgeDir -WindowStyle Normal

Start-Sleep -Seconds 5

# Check if running
$process = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*python*"}
if ($process) {
    Write-Host "✅ MT5 Bridge is running (PID: $($process.Id))"
    Write-Host "`nService URL: http://localhost:8000"
    Write-Host "Health check: http://localhost:8000/api/mt5/bridge/health"
} else {
    Write-Host "❌ MT5 Bridge failed to start"
    Write-Host "Check logs in: $bridgeDir"
}

Write-Host "`n" + ("=" * 80)
Write-Host "DEPLOYMENT COMPLETE"
Write-Host ("=" * 80)
