# Fix MongoDB Connection on NEW VPS
# Run this on VPS: 92.118.45.135

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔧 FIXING MONGODB CONNECTION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Navigate to service directory
Set-Location "C:\mt5_bridge_service"

# Backup existing .env
if (Test-Path ".env") {
    Copy-Item ".env" ".env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "✅ Existing .env backed up" -ForegroundColor Green
}

# Create correct .env with proper MongoDB credentials
$envContent = @'
MONGODB_URI=mongodb+srv://chavapalmarubin_db_user:2170Tenoch%21@fidus.ylp9be2.mongodb.net/fidus_production?retryWrites=true&w=majority&appName=FIDUS
MT5_PATH=C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe
MT5_SERVER=MEXAtlantic-Real
MT5_ACCOUNT=886557
MT5_PASSWORD=Fidus13!
'@

Set-Content -Path ".env" -Value $envContent -Force -NoNewline
Write-Host "✅ .env file updated with correct MongoDB credentials" -ForegroundColor Green
Write-Host ""

# Display the new .env (hide password)
Write-Host "📄 New .env content:" -ForegroundColor Yellow
Get-Content ".env" | ForEach-Object {
    if ($_ -match "PASSWORD") {
        Write-Host ($_ -replace '=.*', '=***HIDDEN***') -ForegroundColor White
    } else {
        Write-Host $_ -ForegroundColor White
    }
}
Write-Host ""

# Stop the service
Write-Host "🛑 Stopping MT5 Bridge Service..." -ForegroundColor Yellow
Stop-ScheduledTask -TaskName "MT5BridgeService" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "✅ Service stopped" -ForegroundColor Green
Write-Host ""

# Start the service
Write-Host "🚀 Starting MT5 Bridge Service..." -ForegroundColor Yellow
Start-ScheduledTask -TaskName "MT5BridgeService"
Write-Host "✅ Service started" -ForegroundColor Green
Write-Host ""

# Wait for service to initialize
Write-Host "⏳ Waiting 15 seconds for service to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Test the service
Write-Host "🔍 Testing service health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing -TimeoutSec 10
    $json = $response.Content | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
    Write-Host "✅ SERVICE HEALTH CHECK RESULT" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "Status: $($json.status)" -ForegroundColor $(if ($json.status -eq "healthy") { "Green" } else { "Yellow" })
    Write-Host "MT5 Available: $($json.mt5.available)" -ForegroundColor $(if ($json.mt5.available) { "Green" } else { "Red" })
    Write-Host "MT5 Connected: $($json.mt5.terminal_info.connected)" -ForegroundColor $(if ($json.mt5.terminal_info.connected) { "Green" } else { "Red" })
    Write-Host "MongoDB Connected: $($json.mongodb.connected)" -ForegroundColor $(if ($json.mongodb.connected) { "Green" } else { "Red" })
    Write-Host ""
    
    if ($json.mongodb.connected -eq $true) {
        Write-Host "🎉 SUCCESS! MongoDB connection fixed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ MongoDB still not connected - check logs" -ForegroundColor Yellow
        Write-Host "Checking error logs..." -ForegroundColor Cyan
        if (Test-Path "logs\service_error.log") {
            Write-Host ""
            Write-Host "=== Last 20 lines of error log ===" -ForegroundColor Yellow
            Get-Content "logs\service_error.log" -Tail 20
        }
    }
    
} catch {
    Write-Host "❌ Service not responding" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Checking logs..." -ForegroundColor Cyan
    if (Test-Path "logs\service_error.log") {
        Write-Host ""
        Write-Host "=== Last 30 lines of error log ===" -ForegroundColor Yellow
        Get-Content "logs\service_error.log" -Tail 30
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ .env file updated" -ForegroundColor White
Write-Host "✅ Service restarted" -ForegroundColor White
Write-Host "🔗 Test externally: curl http://92.118.45.135:8000/api/mt5/bridge/health" -ForegroundColor White
Write-Host ""
