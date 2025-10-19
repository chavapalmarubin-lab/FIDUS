# VPS Setup Guide

**Last Updated:** 2025-01-19 - Automated deployment configured via GitHub Actions - GitHub Auto-Update Integration

## Overview
This guide walks Chava through setting up Git on the VPS so that the MT5 bridge automatically pulls latest code from GitHub before each sync.

---

## Prerequisites
✅ Windows VPS access (RDP)  
✅ MT5 bridge currently running via Task Scheduler  
✅ GitHub repository: `chavany2025/fidus-investment-platform`  

---

## Step 1: Install Git on Windows VPS

### Option A: Using winget (Recommended)
```powershell
# Open PowerShell as Administrator
winget install Git.Git

# Verify installation
git --version
# Should output: git version 2.x.x
```

### Option B: Manual Download
1. Download Git from: https://git-scm.com/download/win
2. Run installer (accept all defaults)
3. Restart PowerShell after installation

---

## Step 2: Configure Git

```powershell
# Set Git user (for commits if needed)
git config --global user.name "FIDUS VPS"
git config --global user.email "vps@fidus.com"

# Verify configuration
git config --list
```

---

## Step 3: Initialize Git Repository

```powershell
# Navigate to bridge directory
cd C:\mt5_bridge_service

# Initialize Git (if not already initialized)
git init

# Add GitHub remote
git remote add origin https://github.com/chavany2025/fidus-investment-platform.git

# Verify remote
git remote -v
# Should show:
# origin  https://github.com/chavany2025/fidus-investment-platform.git (fetch)
# origin  https://github.com/chavany2025/fidus-investment-platform.git (push)
```

---

## Step 4: Create .gitignore

```powershell
# Create .gitignore file
@"
# Ignore sensitive files
.env
*.env

# Ignore logs
logs/
*.log

# Ignore backups
*.backup.*

# Ignore Python cache
*.pyc
__pycache__/
.pytest_cache/
"@ | Out-File -FilePath .gitignore -Encoding UTF8

# Add and commit .gitignore
git add .gitignore
git commit -m "Add .gitignore"
```

---

## Step 5: Pull Latest Code from GitHub

```powershell
# Fetch all branches
git fetch origin

# Checkout main branch
git checkout main

# Pull latest code
git pull origin main

# Verify you have the latest files
git log -1
# Should show the most recent commit
```

---

## Step 6: Deploy New Files

```powershell
# The GitHub repo has these new files in /vps/ directory:
# - mt5_bridge_service_production.py (enhanced with deal history)
# - auto_update.ps1 (auto-update script)
# - run_bridge_with_update.bat (enhanced run script)

# Copy from repo to bridge directory
Copy-Item vps\mt5_bridge_service_production.py . -Force
Copy-Item vps\auto_update.ps1 . -Force
Copy-Item vps\run_bridge_with_update.bat . -Force

# Verify files exist
ls *.py, *.ps1, *.bat
```

---

## Step 7: Update Windows Task Scheduler

### 7.1 Open Task Scheduler
```powershell
# Open Task Scheduler
taskschd.msc
```

### 7.2 Find Your Bridge Task
- Navigate to: Task Scheduler Library
- Find task: "MT5BridgeSync" or "MT5 Bridge Service"

### 7.3 Edit Task Action
1. Select the task
2. Right-click → Properties
3. Go to "Actions" tab
4. Select the action → Click "Edit"
5. Update "Program/script" to:
   ```
   C:\mt5_bridge_service\run_bridge_with_update.bat
   ```
6. Ensure "Start in" is:
   ```
   C:\mt5_bridge_service
   ```
7. Click OK → OK

### 7.4 Test the Task
1. Right-click the task → "Run"
2. Check Task History for any errors
3. Check logs:
   ```powershell
   Get-Content C:\mt5_bridge_service\logs\auto_update.log -Tail 20
   Get-Content C:\mt5_bridge_service\logs\service_output.log -Tail 20
   ```

---

## Step 8: Verify Auto-Update Works

### 8.1 Check Auto-Update Log
```powershell
cd C:\mt5_bridge_service

# View auto-update log
Get-Content logs\auto_update.log

# You should see entries like:
# 2025-01-15 14:30:00 - Starting auto-update check...
# 2025-01-15 14:30:01 - Code is up to date (commit: abc123...)
# 2025-01-15 14:30:01 - Auto-update check complete
```

### 8.2 Simulate a Code Update
```powershell
# View current commit
git log -1

# When you push changes to GitHub, the auto-update script will:
# 1. Detect new commits
# 2. Backup current file
# 3. Pull latest code
# 4. Use new code on next run
```

---

## Step 9: Verify Deal History Collection

### 9.1 Check Service Logs
```powershell
# View recent service output
Get-Content logs\service_output.log -Tail 50

# Look for messages like:
# ✅ Collected XXX deals for account 886557
# 💾 Stored XXX new deals, updated 0 existing deals
# ✅ Deal sync complete: XXXX deals processed
```

### 9.2 Check MongoDB
1. Go to: https://cloud.mongodb.com
2. Browse Collections
3. Database: `fidus_production`
4. Collection: `mt5_deals_history`
5. Should see deals from all 7 accounts
6. Should have ~90 days of history (initial backfill)

---

## Step 10: Monitor System Health

### View Task History
```powershell
# Open Task Scheduler
taskschd.msc

# Select your bridge task
# Click "History" tab at bottom
# Check for successful runs every 5 minutes
```

### Check Recent Logs
```powershell
cd C:\mt5_bridge_service

# Auto-update log (last 20 lines)
Get-Content logs\auto_update.log -Tail 20

# Service output (last 50 lines)
Get-Content logs\service_output.log -Tail 50

# Service errors (should be empty or minimal)
Get-Content logs\service_error.log -Tail 20
```

### Monitor GitHub Commits
- GitHub Actions will run on every push to `main`
- VPS will auto-update within 5 minutes of commit
- Check Actions page: https://github.com/chavany2025/fidus-investment-platform/actions

---

## Troubleshooting

### Issue: Git not found
**Solution:**
```powershell
# Add Git to PATH
$env:Path += ";C:\Program Files\Git\bin"
[System.Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)

# Restart PowerShell and try again
```

### Issue: Authentication failed
**Solution:**
```powershell
# Use HTTPS with token (if repo is private)
git remote set-url origin https://YOUR_TOKEN@github.com/chavany2025/fidus-investment-platform.git

# Or use SSH (requires SSH key setup)
```

### Issue: Auto-update script not running
**Solution:**
```powershell
# Check PowerShell execution policy
Get-ExecutionPolicy

# If Restricted, set to RemoteSigned
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Test script manually
cd C:\mt5_bridge_service
powershell.exe -ExecutionPolicy Bypass -File auto_update.ps1
```

### Issue: Merge conflicts
**Solution:**
```powershell
# If you have local changes that conflict:
git stash
git pull origin main
git stash pop

# Or reset to remote version:
git fetch origin
git reset --hard origin/main
```

---

## Backup & Rollback

### Backup Current Script
```powershell
cd C:\mt5_bridge_service
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item mt5_bridge_service_production.py "mt5_bridge_service_production.py.manual_backup.$timestamp"
```

### Rollback to Previous Version
```powershell
# List backups
Get-ChildItem *.backup.* | Sort-Object LastWriteTime -Descending

# Restore a backup
Copy-Item "mt5_bridge_service_production.py.backup.YYYYMMDD_HHMMSS" mt5_bridge_service_production.py

# Or use Git to rollback
git log --oneline -10  # See last 10 commits
git checkout COMMIT_HASH vps/mt5_bridge_service_production.py
Copy-Item vps\mt5_bridge_service_production.py . -Force
```

---

## Success Checklist

- [ ] Git installed and configured
- [ ] Repository initialized and remote added
- [ ] Latest code pulled from GitHub
- [ ] New files deployed to bridge directory
- [ ] Task Scheduler updated with new run script
- [ ] Task tested and runs successfully
- [ ] Auto-update log shows successful checks
- [ ] Service logs show deal collection working
- [ ] MongoDB shows deals in `mt5_deals_history` collection
- [ ] GitHub Actions workflows running (after setup)

---

## Next Steps

After VPS setup is complete:
1. Test GitHub push → VPS auto-update
2. Verify dashboards show real data
3. Take screenshots for documentation
4. Complete Phase 4A testing

---

**Estimated Setup Time:** 30-45 minutes  
**Difficulty:** Medium  
**Support:** Contact if any issues arise
