# MT4 Bridge Setup Script for FIDUS Platform
# Run as Administrator

param(
    [switch]$Install,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Logs
)

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "MT4 BRIDGE SERVICE MANAGER" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Configuration
$baseDir = "C:\mt4_bridge_service"
$logsDir = "$baseDir\logs"
$taskName = "MT4 Bridge Service"
$mt4ExpertsPath = "C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Experts"
$mt4LibrariesPath = "C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Libraries"

function Install-MT4Bridge {
    Write-Host "`nINSTALLING MT4 BRIDGE..." -ForegroundColor Yellow
    
    # Create directory structure
    Write-Host "Creating directories..." -ForegroundColor Gray
    New-Item -ItemType Directory -Force -Path $baseDir | Out-Null
    New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
    
    # Install Python requirements
    Write-Host "Installing Python requirements..." -ForegroundColor Gray
    
    $requirements = @(
        "pyzmq==25.1.1",
        "pymongo[srv]==4.6.0", 
        "python-dotenv==1.0.0"
    )
    
    foreach ($package in $requirements) {
        Write-Host "  Installing $package..." -ForegroundColor DarkGray
        pip install $package --upgrade --quiet
    }
    
    # Download MT4 ZeroMQ library
    Write-Host "Setting up MT4 ZeroMQ library..." -ForegroundColor Gray
    
    $zmqLibUrl = "https://github.com/dingmaotu/mql-zmq/releases/download/v1.0.0/mql-zmq-1.0.0.zip"
    $zmqLibPath = "$baseDir\mql-zmq.zip"
    
    try {
        Invoke-WebRequest -Uri $zmqLibUrl -OutFile $zmqLibPath -UseBasicParsing
        
        # Extract to MT4 directories
        Expand-Archive -Path $zmqLibPath -DestinationPath "$baseDir\zmq-temp" -Force
        
        # Copy files to MT4
        if (Test-Path $mt4ExpertsPath) {
            Copy-Item -Path "$baseDir\zmq-temp\MQL4\Include\Zmq" -Destination "$mt4ExpertsPath\..\Include" -Recurse -Force
            Copy-Item -Path "$baseDir\zmq-temp\MQL4\Libraries\*" -Destination $mt4LibrariesPath -Recurse -Force
            Write-Host "  ZeroMQ library installed" -ForegroundColor Green
        } else {
            Write-Host "  ERROR: MT4 installation not found" -ForegroundColor Red
        }
        
        # Cleanup
        Remove-Item -Path $zmqLibPath -Force -ErrorAction SilentlyContinue
        Remove-Item -Path "$baseDir\zmq-temp" -Recurse -Force -ErrorAction SilentlyContinue
        
    } catch {
        Write-Host "  Warning: Could not download ZeroMQ library. Manual installation required." -ForegroundColor Yellow
    }
    
    # Copy MT4 EA to Experts folder
    Write-Host "Installing MT4 Expert Advisor..." -ForegroundColor Gray
    
    if (Test-Path $mt4ExpertsPath) {
        # Assuming the EA file is in the same directory as this script
        $eaSource = Join-Path $PSScriptRoot "MT4_Python_Bridge.mq4"
        if (Test-Path $eaSource) {
            Copy-Item -Path $eaSource -Destination $mt4ExpertsPath -Force
            Write-Host "  EA copied to MT4 Experts folder" -ForegroundColor Green
        } else {
            Write-Host "  Warning: EA source file not found" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ERROR: MT4 Experts folder not found at $mt4ExpertsPath" -ForegroundColor Red
    }
    
    # Copy Python service
    Write-Host "Installing Python service..." -ForegroundColor Gray
    $pythonSource = Join-Path $PSScriptRoot "mt4_bridge_api_service.py"
    if (Test-Path $pythonSource) {
        Copy-Item -Path $pythonSource -Destination $baseDir -Force
        Write-Host "  Python service installed" -ForegroundColor Green
    }
    
    # Create startup batch file
    Write-Host "Creating startup script..." -ForegroundColor Gray
    
    $startupScript = @"
@echo off
title MT4 Bridge Service
cd /d C:\mt4_bridge_service
echo Starting MT4 Bridge Service...
echo Account: 33200931
echo Server: MEXAtlantic-Real
echo.
python mt4_bridge_api_service.py
pause
"@
    
    Set-Content -Path "$baseDir\start_mt4_bridge.bat" -Value $startupScript
    
    # Create Task Scheduler task
    Write-Host "Setting up Windows Task Scheduler..." -ForegroundColor Gray
    
    $taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if ($taskExists) {
        Write-Host "  Task already exists. Updating..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    
    $action = New-ScheduledTaskAction -Execute "python.exe" -Argument "mt4_bridge_api_service.py" -WorkingDirectory $baseDir
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "Administrator" -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Hours 0)
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings
    
    Write-Host "  Task Scheduler configured" -ForegroundColor Green
    
    Write-Host "`nINSTALLATION COMPLETE!" -ForegroundColor Green
    Write-Host "`nMANUAL STEPS REQUIRED:" -ForegroundColor Yellow
    Write-Host "1. Open MT4 Terminal" -ForegroundColor White
    Write-Host "2. Login to account 33200931 with password Fidus13!" -ForegroundColor White
    Write-Host "3. Open MetaEditor (F4)" -ForegroundColor White
    Write-Host "4. Open Experts\MT4_Python_Bridge.mq4" -ForegroundColor White
    Write-Host "5. Click Compile (F7)" -ForegroundColor White
    Write-Host "6. Attach the EA to any chart (drag & drop from Navigator)" -ForegroundColor White
    Write-Host "7. Enable Expert Advisors (AutoTrading button)" -ForegroundColor White
    Write-Host "8. Run: .\setup_mt4_bridge.ps1 -Start" -ForegroundColor Cyan
}

function Start-MT4Bridge {
    Write-Host "`nSTARTING MT4 BRIDGE SERVICE..." -ForegroundColor Yellow
    
    try {
        Start-ScheduledTask -TaskName $taskName
        Write-Host "Task started successfully" -ForegroundColor Green
        
        Start-Sleep -Seconds 3
        Get-MT4BridgeStatus
        
    } catch {
        Write-Host "Error starting task: $_" -ForegroundColor Red
        Write-Host "`nAlternatively, run manually:" -ForegroundColor Yellow
        Write-Host "  $baseDir\start_mt4_bridge.bat" -ForegroundColor Cyan
    }
}

function Stop-MT4Bridge {
    Write-Host "`nSTOPPING MT4 BRIDGE SERVICE..." -ForegroundColor Yellow
    
    try {
        # Stop scheduled task
        Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        
        # Kill any running Python processes
        Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.MainWindowTitle -like "*mt4_bridge*"} | Stop-Process -Force -ErrorAction SilentlyContinue
        
        Write-Host "Service stopped" -ForegroundColor Green
        
    } catch {
        Write-Host "Error stopping service: $_" -ForegroundColor Red
    }
}

function Get-MT4BridgeStatus {
    Write-Host "`nMT4 BRIDGE SERVICE STATUS:" -ForegroundColor Cyan
    
    # Check scheduled task
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) {
        $taskState = $task.State
        $lastRun = (Get-ScheduledTaskInfo -TaskName $taskName).LastRunTime
        Write-Host "Scheduled Task: $taskState" -ForegroundColor $(if($taskState -eq "Running") {"Green"} else {"Yellow"})
        Write-Host "Last Run: $lastRun"
    } else {
        Write-Host "Scheduled Task: Not found" -ForegroundColor Red
    }
    
    # Check Python process
    $pythonProcess = Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.Path -like "*mt4_bridge*"}
    if ($pythonProcess) {
        Write-Host "Python Process: Running (PID: $($pythonProcess.Id))" -ForegroundColor Green
        Write-Host "Start Time: $($pythonProcess.StartTime)"
        Write-Host "CPU Time: $($pythonProcess.TotalProcessorTime)"
    } else {
        Write-Host "Python Process: Not running" -ForegroundColor Red
    }
    
    # Check log file
    $logFile = "$logsDir\mt4_bridge.log"
    if (Test-Path $logFile) {
        $logInfo = Get-Item $logFile
        Write-Host "Log File: $($logInfo.Length) bytes, modified $($logInfo.LastWriteTime)" -ForegroundColor Green
        
        # Show last few lines
        Write-Host "`nLast 5 log entries:" -ForegroundColor Gray
        Get-Content $logFile -Tail 5 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "Log File: Not found" -ForegroundColor Red
    }
    
    # Check MT4 EA status
    Write-Host "`nMT4 EA Status:" -ForegroundColor Cyan
    Write-Host "Check MT4 Terminal for EA status on chart" -ForegroundColor Yellow
    Write-Host "EA should show 'MT4 Python Bridge Initialized' in Journal" -ForegroundColor White
}

function Show-MT4BridgeLogs {
    $logFile = "$logsDir\mt4_bridge.log"
    
    if (Test-Path $logFile) {
        Write-Host "`nMT4 BRIDGE LOGS (Last 50 lines):" -ForegroundColor Cyan
        Write-Host "Log file: $logFile" -ForegroundColor Gray
        Write-Host ("-" * 60) -ForegroundColor Gray
        
        Get-Content $logFile -Tail 50 | ForEach-Object {
            $color = "White"
            if ($_.Contains("ERROR")) { $color = "Red" }
            elseif ($_.Contains("WARNING")) { $color = "Yellow" }
            elseif ($_.Contains("SUCCESS") -or $_.Contains("✅")) { $color = "Green" }
            
            Write-Host $_ -ForegroundColor $color
        }
    } else {
        Write-Host "Log file not found: $logFile" -ForegroundColor Red
    }
}

# Main execution
if ($Install) {
    Install-MT4Bridge
}
elseif ($Start) {
    Start-MT4Bridge
}
elseif ($Stop) {
    Stop-MT4Bridge
}
elseif ($Status) {
    Get-MT4BridgeStatus
}
elseif ($Logs) {
    Show-MT4BridgeLogs
}
else {
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  .\setup_mt4_bridge.ps1 -Install    # Install MT4 bridge" -ForegroundColor Cyan
    Write-Host "  .\setup_mt4_bridge.ps1 -Start      # Start service" -ForegroundColor Cyan
    Write-Host "  .\setup_mt4_bridge.ps1 -Stop       # Stop service" -ForegroundColor Cyan
    Write-Host "  .\setup_mt4_bridge.ps1 -Status     # Check status" -ForegroundColor Cyan
    Write-Host "  .\setup_mt4_bridge.ps1 -Logs       # Show logs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Account: 33200931" -ForegroundColor Yellow
    Write-Host "Server: MEXAtlantic-Real" -ForegroundColor Yellow
    Write-Host "Platform: MT4" -ForegroundColor Yellow
}