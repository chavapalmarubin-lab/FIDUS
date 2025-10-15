# FIDUS MT5 Bridge Auto-Update Script
# Pulls latest code from GitHub before each sync run
# Location: C:\mt5_bridge_service\auto_update.ps1

$ErrorActionPreference = "Stop"
$LogFile = "C:\mt5_bridge_service\logs\auto_update.log"

# Create logs directory if it doesn't exist
if (-not (Test-Path "C:\mt5_bridge_service\logs")) {
    New-Item -ItemType Directory -Path "C:\mt5_bridge_service\logs" -Force | Out-Null
}

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $LogFile -Append
    Write-Host $Message
}

try {
    Write-Log "=========================================="
    Write-Log "Starting auto-update check..."
    
    # Navigate to bridge directory
    Set-Location C:\mt5_bridge_service
    
    # Check if Git is initialized
    if (-not (Test-Path ".git")) {
        Write-Log "Git repository not initialized. Run setup first."
        exit 0
    }
    
    # Fetch latest changes
    Write-Log "Fetching latest changes from GitHub..."
    git fetch origin main 2>&1 | Out-Null
    
    # Check if updates available
    $localCommit = git rev-parse HEAD
    $remoteCommit = git rev-parse origin/main
    
    if ($localCommit -ne $remoteCommit) {
        Write-Log "🔄 Updates found! Pulling latest code..."
        Write-Log "Current commit: $localCommit"
        Write-Log "New commit: $remoteCommit"
        
        # Backup current version
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = "mt5_bridge_service_production.py.backup.$timestamp"
        
        if (Test-Path "mt5_bridge_service_production.py") {
            Copy-Item mt5_bridge_service_production.py $backupFile
            Write-Log "✅ Backup created: $backupFile"
        }
        
        # Pull latest
        $pullResult = git pull origin main 2>&1
        Write-Log "Pull result: $pullResult"
        Write-Log "✅ Code updated successfully"
        
        # Clean up old backups (keep last 5)
        $backups = Get-ChildItem -Filter "*.backup.*" | Sort-Object LastWriteTime -Descending
        if ($backups.Count -gt 5) {
            $backups | Select-Object -Skip 5 | ForEach-Object {
                Remove-Item $_.FullName -Force
                Write-Log "Removed old backup: $($_.Name)"
            }
        }
        
        Write-Log "🎉 Update complete! New code will be used on next run."
    } else {
        Write-Log "✅ Code is up to date (commit: $localCommit)"
    }
    
    Write-Log "Auto-update check complete"
    Write-Log "=========================================="
    exit 0
    
} catch {
    Write-Log "❌ Error during auto-update: $_"
    Write-Log "Error details: $($_.Exception.Message)"
    # Don't fail the sync if update fails - use existing code
    Write-Log "Continuing with existing code..."
    exit 0
}
