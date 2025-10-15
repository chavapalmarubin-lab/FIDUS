# Task 2: VPS Setup - Step-by-Step Guide

**Time Required**: 45 minutes  
**Difficulty**: Medium  
**Prerequisites**: Task 1 (GitHub Secrets) complete

---

## Before You Start

**You'll Need**:
- ✅ RDP access to VPS (217.197.163.11)
- ✅ Administrator password (2170Tenoch!)
- ✅ Task 1 (GitHub Secrets) completed

**What We'll Do**:
1. Check if Git is installed (5 min)
2. Initialize Git repository (10 min)
3. Pull code from GitHub (5 min)
4. Deploy new files (10 min)
5. Update Task Scheduler (10 min)
6. Test deployment (5 min)

---

## Step 1: Connect to VPS (2 minutes)

### 1.1 Open Remote Desktop
**Windows**:
1. Press `Windows Key + R`
2. Type: `mstsc`
3. Press Enter

**Mac**:
1. Open "Microsoft Remote Desktop" app
2. Click "Add PC"

### 1.2 Connect to VPS
1. In "Computer" field, type: `217.197.163.11`
2. Click "Connect"
3. Username: `Administrator`
4. Password: `2170Tenoch!`
5. Click OK

### 1.3 You're In!
You should now see the Windows desktop of the VPS.

---

## Step 2: Check/Install Git (5 minutes)

### 2.1 Open PowerShell as Administrator
1. Click Start menu
2. Type: `PowerShell`
3. Right-click "Windows PowerShell"
4. Click "Run as Administrator"
5. Click "Yes" if prompted

### 2.2 Check if Git is Installed
In PowerShell, type:
```powershell
git --version
```

**If you see**: `git version 2.x.x`
- ✅ Git is installed! **Skip to Step 3**

**If you see**: `git : The term 'git' is not recognized...`
- ⚠️ Git not installed, continue with Step 2.3

### 2.3 Install Git (if needed)
In PowerShell, type:
```powershell
winget install Git.Git
```

Wait for installation (takes 2-3 minutes).

**Alternative if winget fails**:
1. Download Git from: https://git-scm.com/download/win
2. Run the installer
3. Accept all default options
4. Restart PowerShell after installation

### 2.4 Verify Installation
Close and reopen PowerShell as Administrator, then type:
```powershell
git --version
```

Should now show: `git version 2.x.x` ✅

---

## Step 3: Navigate to MT5 Bridge Directory (1 minute)

In PowerShell, type:
```powershell
cd C:\mt5_bridge_service
```

Press Enter.

Your prompt should now show: `PS C:\mt5_bridge_service>`

---

## Step 4: Configure Git (2 minutes)

### 4.1 Set Git User Name
```powershell
git config --global user.name "FIDUS VPS"
```

### 4.2 Set Git Email
```powershell
git config --global user.email "vps@fidus.com"
```

### 4.3 Verify Configuration
```powershell
git config --list
```

Should see:
```
user.name=FIDUS VPS
user.email=vps@fidus.com
```

---

## Step 5: Initialize Git Repository (3 minutes)

### 5.1 Check if Git is Already Initialized
```powershell
Test-Path .git
```

**If result is `True`**: Git already initialized, skip to 5.3  
**If result is `False`**: Continue with 5.2

### 5.2 Initialize Git (if needed)
```powershell
git init
```

Should see: `Initialized empty Git repository...`

### 5.3 Add GitHub Remote
```powershell
git remote add origin https://github.com/chavany2025/fidus-investment-platform.git
```

**If you see error** "remote origin already exists":
```powershell
git remote set-url origin https://github.com/chavany2025/fidus-investment-platform.git
```

### 5.4 Verify Remote
```powershell
git remote -v
```

Should see:
```
origin  https://github.com/chavany2025/fidus-investment-platform.git (fetch)
origin  https://github.com/chavany2025/fidus-investment-platform.git (push)
```

---

## Step 6: Pull Code from GitHub (5 minutes)

### 6.1 Fetch All Branches
```powershell
git fetch origin
```

Wait for download to complete (1-2 minutes).

### 6.2 Checkout Main Branch
```powershell
git checkout main
```

**If you see error** about untracked files:
```powershell
git stash
git checkout main
```

### 6.3 Pull Latest Code
```powershell
git pull origin main
```

Should see files being updated.

### 6.4 Verify Files Downloaded
```powershell
ls vps
```

Should see these files in the `vps` folder:
- auto_update.ps1
- run_mt5_bridge.bat
- mt5_bridge_service_production.py
- VPS_SETUP_GUIDE.md

✅ **Success!** Code is downloaded from GitHub.

---

## Step 7: Create Backup (2 minutes)

### 7.1 Create Backups Directory
```powershell
if (-not (Test-Path backups)) {
    New-Item -ItemType Directory -Path backups
}
```

### 7.2 Backup Current Script
```powershell
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
Copy-Item mt5_bridge_service_production.py "backups\backup_$timestamp.py"
```

### 7.3 Verify Backup Created
```powershell
ls backups
```

Should see your backup file listed.

---

## Step 8: Deploy New Files (5 minutes)

### 8.1 Deploy Enhanced Bridge Script
```powershell
Copy-Item vps\mt5_bridge_service_production.py . -Force
```

### 8.2 Deploy Auto-Update Script
```powershell
Copy-Item vps\auto_update.ps1 . -Force
```

### 8.3 Deploy Run Script
```powershell
Copy-Item vps\run_mt5_bridge.bat run_bridge_with_update.bat -Force
```

**Alternative** (copy all at once):
```powershell
Copy-Item vps\mt5_bridge_service_production.py . -Force
Copy-Item vps\auto_update.ps1 . -Force
Copy-Item vps\run_mt5_bridge.bat run_bridge_with_update.bat -Force
```

### 8.4 Verify Files Copied
```powershell
ls *.py, *.ps1, *.bat
```

Should see:
- mt5_bridge_service_production.py (today's date)
- auto_update.ps1 (today's date)
- run_bridge_with_update.bat (today's date)

✅ **Success!** New files deployed.

---

## Step 9: Update Task Scheduler (10 minutes)

### 9.1 Open Task Scheduler
1. Press `Windows Key + R`
2. Type: `taskschd.msc`
3. Press Enter

### 9.2 Find Your MT5 Bridge Task
1. In left panel, click "Task Scheduler Library"
2. Look for your MT5 bridge task (might be named):
   - "MT5BridgeSync"
   - "MT5 Bridge Service"
   - "FIDUS MT5 Bridge"
   - Or similar name

### 9.3 Edit the Task
1. Right-click your bridge task
2. Click "Properties"
3. Go to "Actions" tab

### 9.4 Update the Action
1. Select the action (should be only one)
2. Click "Edit" button
3. In "Program/script" field, change to:
   ```
   C:\mt5_bridge_service\run_bridge_with_update.bat
   ```
4. In "Start in" field, verify it shows:
   ```
   C:\mt5_bridge_service
   ```
5. Click "OK"
6. Click "OK" again to close Properties

### 9.5 Test the Task
1. Right-click your bridge task
2. Click "Run"
3. Wait 10-15 seconds
4. Check "Last Run Result" column
5. Should show: `0x0` (means success)

**If you see error code**:
- Go to Step 10 (Troubleshooting) below

---

## Step 10: Test Auto-Update Script (5 minutes)

### 10.1 Test Manually
In PowerShell (still in C:\mt5_bridge_service), type:
```powershell
powershell -ExecutionPolicy Bypass -File auto_update.ps1
```

### 10.2 Watch the Output
You should see colorful output like:
```
========================================
VPS AUTO-UPDATE STARTING
========================================
Working directory: C:\mt5_bridge_service
Fetching latest changes from GitHub...
Current commit: abc123...
Remote commit: abc123...
✅ No updates available. System is up to date.
========================================
```

### 10.3 Check the Log
```powershell
Get-Content logs\auto_update.log -Tail 20
```

Should show recent log entries with timestamps.

✅ **Success!** Auto-update is working.

---

## Step 11: Verify Everything (5 minutes)

### 11.1 Check Git Status
```powershell
git status
```

Should show you're on branch `main` and up to date.

### 11.2 Check Task Scheduler
1. Open Task Scheduler (if closed)
2. Find your bridge task
3. Verify "Next Run Time" shows a future time
4. Verify "Last Run Result" is `0x0`

### 11.3 Check Service Logs
```powershell
Get-Content logs\service_output.log -Tail 30
```

Look for recent entries showing:
- MT5 initialization
- Account sync messages
- Deal collection (if Phase 4A is active)

---

## ✅ Task 2 Complete!

**What you've accomplished**:
- ✅ Git installed and configured
- ✅ Repository connected to GitHub
- ✅ Latest code pulled from GitHub
- ✅ New files deployed
- ✅ Task Scheduler updated
- ✅ Auto-update tested and working

**VPS is now connected to GitHub!**

---

## Step 12: Test GitHub Auto-Deployment (Next Step)

Now let's test that pushing code to GitHub automatically deploys to VPS!

### 12.1 Make a Small Test Change
On your development machine (not VPS), create a test file:

```bash
# On your local machine
cd /path/to/fidus-investment-platform
echo "# Test auto-deployment" >> vps/TEST.txt
git add vps/TEST.txt
git commit -m "test: VPS auto-deployment"
git push origin main
```

### 12.2 Check GitHub Actions
1. Go to: https://github.com/chavany2025/fidus-investment-platform/actions
2. You should see "Deploy to VPS" workflow running
3. Wait for it to complete (takes ~30 seconds)
4. Should show green checkmark ✅

### 12.3 Verify on VPS
Back on the VPS, in PowerShell:
```powershell
# Check auto-update log
Get-Content logs\auto_update.log -Tail 30

# Check if test file exists
Test-Path vps\TEST.txt
```

Should return: `True` ✅

**Congratulations! GitHub auto-deployment is working!** 🎉

---

## 🔍 Troubleshooting

### Problem: Git not found after installation
**Solution**:
```powershell
# Add Git to PATH
$env:Path += ";C:\Program Files\Git\bin"
# Restart PowerShell
```

### Problem: "Permission denied" when pulling code
**Solution**:
```powershell
# If repository is private, you may need authentication
# Option 1: Use GitHub Personal Access Token
git config --global credential.helper store
# Then try git pull again - it will ask for credentials once
```

### Problem: Task Scheduler shows error code
**Common error codes**:
- `0x1`: File not found - Check path in Task Scheduler
- `0x2`: Access denied - Run task as Administrator
- `0xFF`: Task still running - Wait and try again

**Solution**:
1. Open Task Scheduler
2. Right-click task → Properties
3. "General" tab:
   - Check "Run with highest privileges"
   - "Configure for": Windows Server 2022
4. "Actions" tab:
   - Verify path is correct
   - Verify "Start in" is set
5. Click OK and test again

### Problem: Auto-update script doesn't run
**Solution**:
```powershell
# Check PowerShell execution policy
Get-ExecutionPolicy

# If it's Restricted:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try running script again
```

### Problem: Can't find MT5 Bridge task in Task Scheduler
**Solution**:
1. You may need to create the task first
2. Or it might be in a subfolder
3. Use search: Click "Task Scheduler Library" → Press Ctrl+F → Search for "MT5"

### Problem: Files not deploying from GitHub
**Solution**:
```powershell
# Ensure you're on main branch
git checkout main

# Force pull latest
git fetch origin
git reset --hard origin/main

# Try deploy again
Copy-Item vps\* . -Force
```

---

## 📋 Quick Reference Commands

**Check Git Status**:
```powershell
cd C:\mt5_bridge_service
git status
```

**Pull Latest Code**:
```powershell
cd C:\mt5_bridge_service
git pull origin main
```

**Test Auto-Update**:
```powershell
cd C:\mt5_bridge_service
powershell -ExecutionPolicy Bypass -File auto_update.ps1
```

**Check Logs**:
```powershell
cd C:\mt5_bridge_service
Get-Content logs\auto_update.log -Tail 30
Get-Content logs\service_output.log -Tail 30
```

**Run Bridge Manually (for testing)**:
```powershell
cd C:\mt5_bridge_service
python mt5_bridge_service_production.py
```
(Press Ctrl+C to stop)

---

## ✅ Success Checklist

Before moving to Task 3 (Testing), verify:

- [ ] Git is installed (`git --version` works)
- [ ] Git repository initialized (`.git` folder exists)
- [ ] Connected to GitHub (`git remote -v` shows origin)
- [ ] Latest code pulled (`git pull` succeeded)
- [ ] New files deployed (`ls *.py, *.ps1, *.bat` shows today's dates)
- [ ] Task Scheduler updated (action points to new .bat file)
- [ ] Auto-update script tested (runs without errors)
- [ ] Logs show successful operation
- [ ] Test deployment from GitHub worked (TEST.txt appeared)

**All checked?** You're ready for Task 3! 🚀

---

**Next**: Test everything end-to-end and verify dashboards show real data!
