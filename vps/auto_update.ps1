# FIDUS MT5 Bridge Auto-Update Script
# Pulls latest code from GitHub and restarts service
# Location: C:\mt5_bridge_service\auto_update.ps1

$ErrorActionPreference = "Stop"
$LogFile = "C:\mt5_bridge_service\logs\auto_update.log"

# Create logs directory if it doesn't exist
if (-not (Test-Path "C:\mt5_bridge_service\logs")) {
    New-Item -ItemType Directory -Path "C:\mt5_bridge_service\logs" -Force | Out-Null
}

function Write-Log {
    param($Message, $Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp - $Message"
    $logMessage | Out-File -FilePath $LogFile -Append
    Write-Host $Message -ForegroundColor $Color
}

try {
    Write-Log "========================================" "Cyan"
    Write-Log "VPS AUTO-UPDATE STARTING" "Cyan"
    Write-Log "========================================" "Cyan"
    
    # Navigate to bridge directory
    Set-Location C:\mt5_bridge_service
    Write-Log "Working directory: $(Get-Location)"
    
    # Check if Git is initialized
    if (-not (Test-Path ".git")) {
        Write-Log "Git repository not initialized. Initializing..." "Yellow"
        git init
        git remote add origin https://github.com/chavany2025/fidus-investment-platform.git
        Write-Log "Git repository initialized successfully" "Green"
    }
    
    # Fetch latest changes
    Write-Log "Fetching latest changes from GitHub..." "Yellow"
    git fetch origin main 2>&1 | Out-Null
    
    # Check if updates available
    $localCommit = git rev-parse HEAD
    $remoteCommit = git rev-parse origin/main
    
    Write-Log "Current commit: $localCommit"
    Write-Log "Remote commit: $remoteCommit"
    
    if ($localCommit -eq $remoteCommit) {
        Write-Log "✅ No updates available. System is up to date." "Green"
        Write-Log "========================================" "Cyan"
        exit 0
    }
    
    Write-Log "🔄 Updates detected! Deploying new code..." "Yellow"
    
    # Create backup directory
    $backupDir = "backups"
    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir | Out-Null
        Write-Log "Created backups directory"
    }
    
    # Create backup
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$backupDir\backup_$timestamp.py"
    
    if (Test-Path "mt5_bridge_service_production.py") {
        Copy-Item mt5_bridge_service_production.py $backupFile
        Write-Log "✅ Backup created: $backupFile" "Green"
    }
    
    # Stop the MT5 Bridge service
    Write-Log "Stopping MT5 Bridge Service..." "Yellow"
    try {
        Stop-ScheduledTask -TaskName "MT5BridgeSync" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 5
        Write-Log "Service stopped successfully" "Green"
    } catch {
        Write-Log "Warning: Could not stop service (may not be running)" "Yellow"
    }
    
    # Pull latest code
    Write-Log "Pulling latest code from GitHub..." "Yellow"
    $pullResult = git pull origin main 2>&1
    Write-Log "Pull result: $pullResult"
    Write-Log "✅ Code updated successfully" "Green"
    
    # Copy files from vps directory to root if they exist
    if (Test-Path "vps\mt5_bridge_service_production.py") {
        Copy-Item "vps\mt5_bridge_service_production.py" . -Force
        Write-Log "✅ Deployed enhanced MT5 bridge script"
    }
    
    if (Test-Path "vps\run_mt5_bridge.bat") {
        Copy-Item "vps\run_mt5_bridge.bat" "run_bridge_with_update.bat" -Force
        Write-Log "✅ Deployed enhanced run script"
    }
    
    # Start the MT5 Bridge service
    Write-Log "Starting MT5 Bridge Service..." "Yellow"
    try {
        Start-ScheduledTask -TaskName "MT5BridgeSync"
        Start-Sleep -Seconds 3
        Write-Log "Service started successfully" "Green"
    } catch {
        Write-Log "Warning: Could not start service automatically" "Yellow"
    }
    
    # Verify service status
    try {
        $task = Get-ScheduledTask -TaskName "MT5BridgeSync"
        Write-Log "Service Status: $($task.State)" "Green"
    } catch {
        Write-Log "Warning: Could not verify service status" "Yellow"
    }
    
    # Clean up old backups (keep last 10)
    $backups = Get-ChildItem "$backupDir\backup_*.py" | Sort-Object LastWriteTime -Descending
    if ($backups.Count -gt 10) {
        $backups | Select-Object -Skip 10 | ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Log "Removed old backup: $($_.Name)"
        }
    }
    
    Write-Log "========================================" "Cyan"
    Write-Log "🎉 DEPLOYMENT SUCCESSFUL!" "Green"
    Write-Log "========================================" "Cyan"
    exit 0
    
} catch {
    Write-Log "========================================" "Red"
    Write-Log "❌ DEPLOYMENT FAILED!" "Red"
    Write-Log "Error: $_" "Red"
    Write-Log "Error details: $($_.Exception.Message)" "Red"
    Write-Log "========================================" "Red"
    
    # Attempt to restore from backup
    Write-Log "Attempting to restore from backup..." "Yellow"
    $latestBackup = Get-ChildItem "$backupDir\backup_*.py" -ErrorAction SilentlyContinue | 
                    Sort-Object LastWriteTime -Descending | 
                    Select-Object -First 1
    
    if ($latestBackup) {
        Write-Log "Restoring from backup: $($latestBackup.Name)" "Yellow"
        Copy-Item $latestBackup.FullName "mt5_bridge_service_production.py" -Force
        
        # Try to restart service
        try {
            Start-ScheduledTask -TaskName "MT5BridgeSync"
            Write-Log "Service restarted with backup code" "Green"
        } catch {
            Write-Log "Could not restart service" "Red"
        }
    } else {
        Write-Log "No backup available for restore" "Red"
    }
    
    exit 1
}
