# MT5 AUTO-LOGIN SYSTEM - COMPLETE GUIDE

**Status:** Ready to deploy via GitHub Actions  
**Date:** October 20, 2024  
**Purpose:** Automatically login to MT5 account 886557 on VPS startup

---

## 🎯 WHAT THIS SOLVES:

When your Windows VPS restarts:
- MT5 Terminal starts but accounts are NOT logged in automatically
- Without account 886557 logged in, the MT5 Bridge API cannot access data
- This causes the entire MT5 integration to fail
- **Solution:** Auto-login script runs on every VPS startup

---

## 📋 HOW IT WORKS:

### **1. Auto-Login Script (`auto_login_mt5.ps1`):**
- PowerShell script that uses MetaTrader5 Python library
- Reads credentials from `MT5_MASTER_PASSWORD` environment variable
- Logs into account 886557 on MEXAtlantic-Real server
- Logs all actions to `C:\mt5_bridge_service\logs\auto_login.log`

### **2. Windows Task Scheduler:**
- Scheduled task runs auto-login script on system startup
- Runs with SYSTEM privileges (highest level)
- Triggers automatically when VPS boots

### **3. Emergency Deployment Integration:**
- Emergency deployment workflows now include auto-login step
- Before starting MT5 Bridge service, script attempts to login
- Ensures account is always logged in before API starts

---

## 🚀 DEPLOYMENT INSTRUCTIONS (VIA GITHUB ACTIONS):

### **STEP 1: Set MT5 Master Password as GitHub Secret**

This is the ONLY manual step required:

1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `MT5_MASTER_PASSWORD`
4. Value: [Your MT5 account 886557 password]
5. Click **"Add secret"**

### **STEP 2: Run Setup Workflow on GitHub**

1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
2. Click **"Setup MT5 Auto-Login on VPS"** in the left sidebar
3. Click **"Run workflow"** button (top right)
4. Select branch: **main**
5. Click **"Run workflow"** button

### **STEP 3: Wait for Setup to Complete (5 minutes)**

The workflow will:
- Download auto-login script to VPS
- Install MetaTrader5 Python package
- Create Windows Task Scheduler task
- Set MT5_MASTER_PASSWORD as system environment variable
- Test the login immediately
- Generate detailed setup report

### **STEP 4: Verify Setup**

Check the workflow logs for:
```
✅ AUTO-LOGIN TEST: SUCCESS
✅ Task verification: SUCCESS
✅ MT5 AUTO-LOGIN SETUP COMPLETED
```

---

## 🧪 TESTING:

### **Test Without Restarting VPS:**

After the setup workflow completes, the script runs automatically. To test again manually:

1. VPS will have the script already deployed
2. The GitHub Actions workflow tests it during setup
3. Check logs at: `C:\mt5_bridge_service\logs\auto_login.log`

### **Test With VPS Restart:**

The ultimate test:

1. Restart your VPS
2. Wait 2 minutes
3. Check if MT5 account 886557 is logged in
4. Check logs at: `C:\mt5_bridge_service\logs\auto_login.log`

---

## 📊 MONITORING:

### **Check if Auto-Login is Working:**

**Method 1: Check MT5 Terminal**
- Look at MT5 Terminal on VPS
- Account 886557 should show "Connected" status
- Balance and equity should be visible

**Method 2: Check Logs**
```powershell
# On VPS, open PowerShell:
Get-Content C:\mt5_bridge_service\logs\auto_login.log -Tail 50
```

**Method 3: Test MT5 Bridge Health**
```bash
curl http://217.197.163.11:8000/api/mt5/bridge/health
```

Should return:
```json
{
  "status": "healthy",
  "accounts_synced": 7,
  "master_account": "886557",
  "master_status": "connected"
}
```

---

## 🔄 INTEGRATION WITH AUTONOMOUS SYSTEM:

### **How Auto-Login Works with Auto-Healing:**

1. **VPS Restart Scenario:**
   - VPS restarts (power loss, Windows update, etc.)
   - Windows Task Scheduler runs auto-login script
   - MT5 account 886557 logs in automatically
   - MT5 Bridge service starts (via startup script or emergency deployment)
   - System is fully operational

2. **Auto-Healing Scenario:**
   - MT5 Watchdog detects stale data (no updates for 5 minutes)
   - Triggers emergency deployment via GitHub Actions
   - Emergency deployment runs auto-login script first
   - Then restarts MT5 Bridge service
   - System recovers automatically

3. **Manual Trigger Scenario:**
   - You can manually trigger "Setup MT5 Auto-Login" workflow anytime
   - Script re-deploys and re-configures everything
   - Useful if settings get changed or corrupted

---

## 📁 FILES CREATED:

### **On GitHub:**
- `vps/auto_login_mt5.ps1` - Auto-login PowerShell script
- `.github/workflows/setup-mt5-auto-login.yml` - Setup workflow

### **On VPS (after deployment):**
- `C:\mt5_bridge_service\auto_login_mt5.ps1` - Auto-login script
- `C:\mt5_bridge_service\mt5_login.py` - Python login helper
- `C:\mt5_bridge_service\logs\auto_login.log` - Auto-login logs
- Windows Task Scheduler task: `MT5_Auto_Login`
- System environment variable: `MT5_MASTER_PASSWORD`

---

## 🛠️ TROUBLESHOOTING:

### **If Auto-Login Fails:**

**Check 1: Environment Variable**
```powershell
# On VPS:
[System.Environment]::GetEnvironmentVariable('MT5_MASTER_PASSWORD', 'Machine')
```
Should return your MT5 password. If empty, the workflow couldn't set it.

**Check 2: Scheduled Task**
```powershell
# On VPS:
Get-ScheduledTask -TaskName "MT5_Auto_Login"
```
Should show task with State = "Ready"

**Check 3: Python and MetaTrader5 Package**
```powershell
# On VPS:
python -c "import MetaTrader5; print('OK')"
```
Should print "OK". If error, package isn't installed.

**Check 4: MT5 Terminal Running**
```powershell
# On VPS:
Get-Process -Name terminal64 -ErrorAction SilentlyContinue
```
Should show MT5 terminal process. If not running, start it manually.

**Check 5: Logs**
```powershell
# On VPS:
Get-Content C:\mt5_bridge_service\logs\auto_login.log -Tail 100
```
Review logs for specific error messages.

---

## 🔐 SECURITY:

### **Password Storage:**
- Password stored as system environment variable on VPS
- Only accessible by administrators and SYSTEM account
- Not visible in GitHub Actions logs
- Not stored in GitHub repository
- Auto-login script reads from environment, never hardcoded

### **Best Practices:**
- Use GitHub Secrets for sensitive data (already implemented)
- Regularly rotate MT5 password and update GitHub secret
- Monitor auto-login logs for unauthorized access attempts
- Keep VPS Windows updated with security patches

---

## ✅ SUCCESS CRITERIA:

Auto-login system is working correctly when:

1. **After VPS Restart:**
   - [ ] MT5 account 886557 automatically logs in within 2 minutes
   - [ ] MT5 Bridge API accessible at http://217.197.163.11:8000
   - [ ] FIDUS dashboard shows live MT5 data
   - [ ] No manual intervention required

2. **After Auto-Healing:**
   - [ ] Emergency deployment triggers auto-login before starting service
   - [ ] Service recovers automatically
   - [ ] You receive email notification of recovery

3. **Monitoring:**
   - [ ] Auto-login logs show successful logins
   - [ ] Windows Task Scheduler shows task runs on startup
   - [ ] No failed login attempts in logs

---

## 📧 NOTIFICATIONS:

You will receive email notifications for:
- Emergency deployment (includes auto-login status)
- Auto-healing failures (if auto-login fails)
- System test reports (includes MT5 connection status)

---

## 🎯 NEXT STEPS:

1. **Set `MT5_MASTER_PASSWORD` as GitHub Secret** (one-time setup)
2. **Run "Setup MT5 Auto-Login on VPS" workflow** (5 minutes)
3. **Verify setup succeeded** (check logs)
4. **Test by restarting VPS** (optional but recommended)
5. **System is now fully autonomous!**

---

## 📞 SUPPORT:

If you encounter issues:
1. Check the logs: `C:\mt5_bridge_service\logs\auto_login.log`
2. Review GitHub Actions workflow logs
3. Verify environment variable is set
4. Ensure MT5 Terminal is installed and working
5. Re-run the setup workflow if needed

---

**REMEMBER: After initial setup, you should NEVER need to manually login to MT5 again. The system handles it automatically on every VPS restart!**
