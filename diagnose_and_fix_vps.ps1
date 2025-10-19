# MT5 Bridge Diagnostic & Fix Script
# Save as: C:\mt5_bridge_service\diagnose_and_fix.ps1
# Run as Administrator

Write-Host "=" -rep 70 -ForegroundColor Cyan
Write-Host "MT5 BRIDGE API DIAGNOSTIC & FIX TOOL" -ForegroundColor Cyan
Write-Host "=" -rep 70 -ForegroundColor Cyan
Write-Host ""

$servicePath = "C:\mt5_bridge_service"
cd $servicePath

# DIAGNOSTIC SECTION
Write-Host "[DIAGNOSTIC] Checking current state..." -ForegroundColor Yellow
Write-Host ""

# Check 1: Running processes
Write-Host "CHECK 1: Python processes" -ForegroundColor Cyan
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "✅ Python processes found:" -ForegroundColor Green
    foreach ($proc in $pythonProcesses) {
        Write-Host "  PID: $($proc.Id) | Path: $($proc.Path)" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  No Python processes running" -ForegroundColor Yellow
}
Write-Host ""

# Check 2: Port 8000
Write-Host "CHECK 2: Port 8000 status" -ForegroundColor Cyan
$port8000 = netstat -ano | findstr :8000
if ($port8000) {
    Write-Host "✅ Port 8000 is in use:" -ForegroundColor Green
    Write-Host $port8000 -ForegroundColor Gray
} else {
    Write-Host "⚠️  Port 8000 is NOT listening" -ForegroundColor Yellow
}
Write-Host ""

# Check 3: Service files
Write-Host "CHECK 3: Service files present" -ForegroundColor Cyan
$newServiceExists = Test-Path "$servicePath\mt5_bridge_api_service.py"
$oldServiceExists = Test-Path "$servicePath\mt5_bridge_service_production.py"

if ($newServiceExists) {
    Write-Host "✅ NEW service file exists: mt5_bridge_api_service.py" -ForegroundColor Green
    $newFileInfo = Get-Item "$servicePath\mt5_bridge_api_service.py"
    Write-Host "   Size: $($newFileInfo.Length) bytes | Modified: $($newFileInfo.LastWriteTime)" -ForegroundColor Gray
} else {
    Write-Host "❌ NEW service file MISSING: mt5_bridge_api_service.py" -ForegroundColor Red
}

if ($oldServiceExists) {
    Write-Host "✅ OLD service file exists: mt5_bridge_service_production.py" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  OLD service file not found" -ForegroundColor Gray
}
Write-Host ""

# Check 4: Requirements
Write-Host "CHECK 4: Dependencies" -ForegroundColor Cyan
if (Test-Path "$servicePath\requirements.txt") {
    Write-Host "✅ requirements.txt exists" -ForegroundColor Green
    $reqFileInfo = Get-Item "$servicePath\requirements.txt"
    Write-Host "   Modified: $($reqFileInfo.LastWriteTime)" -ForegroundColor Gray
} else {
    Write-Host "⚠️  requirements.txt not found" -ForegroundColor Yellow
}
Write-Host ""

# Check 5: Environment
Write-Host "CHECK 5: Environment configuration" -ForegroundColor Cyan
if (Test-Path "$servicePath\.env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
}
Write-Host ""

# Check 6: Test endpoint
Write-Host "CHECK 6: Testing current endpoint" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Service responding on port 8000" -ForegroundColor Green
    Write-Host "   Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Service NOT responding on port 8000" -ForegroundColor Red
}
Write-Host ""

# Check 7: Test NEW endpoints
Write-Host "CHECK 7: Testing NEW API endpoints" -ForegroundColor Cyan
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Health endpoint working (NEW service is running!)" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "❌ Health endpoint returns 404 (OLD service is running!)" -ForegroundColor Red
    } else {
        Write-Host "❌ Health endpoint error: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# DECISION POINT
Write-Host "=" -rep 70 -ForegroundColor Cyan
Write-Host "DIAGNOSIS COMPLETE" -ForegroundColor Cyan
Write-Host "=" -rep 70 -ForegroundColor Cyan
Write-Host ""

if (-not $newServiceExists) {
    Write-Host "❌ PROBLEM: NEW service file is MISSING!" -ForegroundColor Red
    Write-Host ""
    Write-Host "SOLUTION:" -ForegroundColor Yellow
    Write-Host "1. The file mt5_bridge_api_service.py needs to be copied to this directory" -ForegroundColor White
    Write-Host "2. Check if GitHub Actions deployment succeeded" -ForegroundColor White
    Write-Host "3. Or copy file manually from workspace/GitHub" -ForegroundColor White
    Write-Host ""
    Write-Host "File should be located at:" -ForegroundColor Yellow
    Write-Host "  Workspace: /app/vps/mt5_bridge_api_service.py" -ForegroundColor Gray
    Write-Host "  GitHub: vps/mt5_bridge_api_service.py" -ForegroundColor Gray
    Write-Host ""
    
    $continue = Read-Host "Do you have the file ready to paste? (y/n)"
    if ($continue -eq 'y') {
        Write-Host ""
        Write-Host "Please paste the full path to the new service file:"
        $sourcePath = Read-Host "Path"
        if (Test-Path $sourcePath) {
            Copy-Item $sourcePath "$servicePath\mt5_bridge_api_service.py"
            Write-Host "✅ File copied!" -ForegroundColor Green
            $newServiceExists = $true
        } else {
            Write-Host "❌ File not found at that path" -ForegroundColor Red
            exit
        }
    } else {
        Write-Host "Please obtain the file and run this script again." -ForegroundColor Yellow
        exit
    }
}

# FIX SECTION
if ($newServiceExists) {
    Write-Host ""
    Write-Host "[FIX] Ready to deploy NEW service" -ForegroundColor Yellow
    Write-Host ""
    
    $deploy = Read-Host "Deploy NEW MT5 Bridge API service now? (y/n)"
    
    if ($deploy -eq 'y') {
        Write-Host ""
        Write-Host "STEP 1: Stopping old service..." -ForegroundColor Yellow
        
        if ($pythonProcesses) {
            foreach ($proc in $pythonProcesses) {
                Stop-Process -Id $proc.Id -Force
                Write-Host "  ✅ Stopped process $($proc.Id)" -ForegroundColor Green
            }
            Start-Sleep -Seconds 3
        }
        
        # Verify stopped
        $stillRunning = Get-Process python -ErrorAction SilentlyContinue
        if ($stillRunning) {
            Write-Host "  ⚠️  Some Python processes still running" -ForegroundColor Yellow
            Get-Process python | Stop-Process -Force
            Start-Sleep -Seconds 3
        }
        Write-Host "  ✅ All Python processes stopped" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "STEP 2: Installing dependencies..." -ForegroundColor Yellow
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        Write-Host "  ✅ Dependencies installed" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "STEP 3: Starting NEW API service..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "=" -rep 70 -ForegroundColor Green
        Write-Host "NEW MT5 BRIDGE API SERVICE STARTING" -ForegroundColor Green
        Write-Host "Keep this window open! Service will run here." -ForegroundColor Cyan
        Write-Host "=" -rep 70 -ForegroundColor Green
        Write-Host ""
        
        # Start service
        python mt5_bridge_api_service.py
    } else {
        Write-Host "Deployment cancelled." -ForegroundColor Yellow
    }
} else {
    Write-Host "Cannot proceed without new service file." -ForegroundColor Red
}
