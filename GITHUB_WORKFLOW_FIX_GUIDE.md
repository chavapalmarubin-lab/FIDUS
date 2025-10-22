# GitHub Workflow Emergency Fix Guide

**Date:** October 22, 2025  
**Issue:** Auto-Healing GitHub Actions workflow is failing  
**Impact:** Watchdog can't automatically restart MT5 Bridge

---

## 🚨 PROBLEM IDENTIFIED

**Symptoms:**
- GitHub Actions workflow "Emergency Deploy MT5 Bridge (PowerShell)" failing in 15 seconds
- Critical alert email: "MT5 Bridge is offline and automatic recovery failed"
- Auto-healing system detected issue but couldn't fix it

**Root Cause:**
Most likely one of:
1. ❌ GitHub Secrets not configured correctly
2. ❌ SSH not enabled/configured on Windows VPS
3. ❌ Wrong port or credentials
4. ❌ Firewall blocking SSH access

---

## ✅ SOLUTION STEPS

### Step 1: Verify GitHub Secrets

**Go to:** https://github.com/chavapalmarubin-lab/FIDUS/settings/secrets/actions

**Required Secrets:**

| Secret Name | Expected Value | Status |
|------------|----------------|--------|
| `VPS_HOST` | 92.118.45.135 | ❓ Check |
| `VPS_USERNAME` | trader | ❓ Check |
| `VPS_PASSWORD` | [your VPS password] | ❓ Check |
| `VPS_PORT` | 42014 | ❓ Check |

**How to check/add:**
1. Click "New repository secret"
2. Name: `VPS_HOST`, Value: `92.118.45.135`
3. Name: `VPS_USERNAME`, Value: `trader`
4. Name: `VPS_PASSWORD`, Value: [your actual VPS password]
5. Name: `VPS_PORT`, Value: `42014`

⚠️ **CRITICAL:** If these secrets don't exist or are wrong, the workflow CANNOT connect to VPS!

---

### Step 2: Test VPS Connection

**Run the diagnostic workflow:**

1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
2. Select workflow: "Test VPS Connection (Diagnostic)"
3. Click "Run workflow" → "Run workflow"
4. Wait for completion (~30 seconds)
5. View logs

**Expected Success Output:**
```
✅ VPS_HOST is set: 92.118.45.135
✅ VPS_USERNAME is set: trader
✅ VPS_PASSWORD is set: (hidden)
✅ VPS_PORT is set: 42014

SSH CONNECTION SUCCESSFUL!
VPS Information:
Hostname: [hostname]
Current User: trader
PowerShell is available!
✅ C:/mt5_bridge_service exists
```

**If it fails:**
- Check SSH is enabled on Windows VPS
- Verify port 42014 is open
- Test SSH manually: `ssh trader@92.118.45.135 -p 42014`

---

### Step 3: Enable SSH on Windows VPS (If Needed)

**If SSH test fails, SSH may not be configured on Windows:**

#### Option A: Enable OpenSSH Server (Recommended)

**On Windows VPS (via RDP):**

```powershell
# Open PowerShell as Administrator

# 1. Install OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 2. Start SSH service
Start-Service sshd

# 3. Set to auto-start
Set-Service -Name sshd -StartupType 'Automatic'

# 4. Verify it's running
Get-Service sshd

# 5. Allow through firewall
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# 6. For custom port 42014 (if needed):
# Edit: C:\ProgramData\ssh\sshd_config
# Change: Port 22 → Port 42014
# Restart: Restart-Service sshd
```

**Test SSH:**
```bash
# From your local machine:
ssh trader@92.118.45.135 -p 42014
```

#### Option B: Use WinRM Instead (Alternative)

If SSH doesn't work, we can modify the workflow to use WinRM instead.

---

### Step 4: Fix Firewall Rules (If Needed)

**On Windows VPS:**

```powershell
# Allow SSH through Windows Firewall
New-NetFirewallRule -DisplayName "SSH Inbound" -Direction Inbound -LocalPort 42014 -Protocol TCP -Action Allow

# Verify firewall rule
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*SSH*"}
```

**With ForexVPS Provider:**
- Contact ForexVPS support to open port 42014
- Or check their control panel for firewall settings

---

### Step 5: Test Emergency Workflow

**After fixing SSH/secrets:**

1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
2. Select: "MT5 Bridge Emergency Restart (NEW VPS)"
3. Click "Run workflow"
4. Enter reason: "Manual test after fixing SSH"
5. Click "Run workflow"
6. Watch the logs

**Expected Success Output:**
```
MT5 BRIDGE EMERGENCY RESTART - NEW VPS
Reason: Manual test after fixing SSH

=== STEP 1: STOP MT5 BRIDGE SERVICE ===
✅ All Python processes stopped

=== STEP 2: VERIFY SERVICE FILE ===
✅ Service file found

=== STEP 3: START MT5 BRIDGE SERVICE ===
✅ Service started with PID: [number]

=== STEP 4: VERIFY SERVICE HEALTH ===
✅ Bridge Health Check: HTTP 200
   MongoDB Connected: True
   MT5 Connected: True
   Accounts Count: 7

✅✅✅ RESTART SUCCESSFUL! ✅✅✅
```

---

### Step 6: Verify Auto-Healing Works

**After emergency workflow succeeds:**

The watchdog will automatically:
1. Detect MT5 Bridge failures (every 60 seconds)
2. Trigger GitHub Actions after 3 failures (~3 minutes)
3. Workflow will restart the service
4. Verify recovery and send email

**Test it:**
1. Manually stop MT5 Bridge on VPS (stop Python process)
2. Wait 3-4 minutes
3. Watchdog should trigger auto-healing
4. Check GitHub Actions for new workflow run
5. Verify service restarts automatically
6. Check email for recovery notification

---

## 🔧 ALTERNATIVE: WinRM-Based Workflow

**If SSH doesn't work, use this WinRM workflow:**

Create: `.github/workflows/emergency-restart-winrm.yml`

```yaml
name: MT5 Bridge Emergency Restart (WinRM)

on:
  workflow_dispatch:

jobs:
  emergency-restart:
    runs-on: windows-latest
    timeout-minutes: 10
    
    steps:
      - name: Restart MT5 Bridge via WinRM
        shell: powershell
        run: |
          $secPassword = ConvertTo-SecureString "${{ secrets.VPS_PASSWORD }}" -AsPlainText -Force
          $cred = New-Object System.Management.Automation.PSCredential("${{ secrets.VPS_USERNAME }}", $secPassword)
          
          $session = New-PSSession -ComputerName "${{ secrets.VPS_HOST }}" -Credential $cred
          
          Invoke-Command -Session $session -ScriptBlock {
            # Stop Python processes
            Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
            Start-Sleep -Seconds 5
            
            # Start service
            cd C:\mt5_bridge_service
            Start-Process python -ArgumentList "mt5_bridge_api_service.py" -WindowStyle Hidden
            Start-Sleep -Seconds 20
            
            # Test health
            Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -Method Get
          }
          
          Remove-PSSession $session
```

---

## 📊 TROUBLESHOOTING

### Issue 1: "Connection refused"
**Cause:** SSH not running or port blocked  
**Fix:** Enable OpenSSH Server (see Step 3)

### Issue 2: "Authentication failed"
**Cause:** Wrong credentials in GitHub secrets  
**Fix:** Update VPS_USERNAME and VPS_PASSWORD

### Issue 3: "Port 22: Connection refused"
**Cause:** Using wrong port  
**Fix:** Ensure VPS_PORT is set to 42014

### Issue 4: "Timeout"
**Cause:** Firewall blocking connection  
**Fix:** Open port 42014 in Windows Firewall and ForexVPS control panel

### Issue 5: "Permission denied"
**Cause:** User doesn't have permissions  
**Fix:** Ensure 'trader' user has admin rights

---

## ✅ VERIFICATION CHECKLIST

After fixing, verify:

- [ ] GitHub secrets are set correctly (4 secrets)
- [ ] Test VPS Connection workflow succeeds
- [ ] SSH connection works manually
- [ ] Emergency Restart workflow succeeds
- [ ] Can manually trigger restart via GitHub Actions
- [ ] Watchdog detects and triggers auto-healing
- [ ] Recovery email received (success notification)

---

## 📧 EXPECTED EMAIL AFTER FIX

**Success Email:**
```
Subject: ✅ MT5 Auto-Recovery Successful

The MT5 Bridge experienced a temporary issue but has been 
automatically recovered.

Issue: 3 consecutive health check failures
Action Taken: Emergency service restart via GitHub Actions
Result: ✅ Service restored, all accounts syncing normally

Downtime: ~3 minutes
Recovery Method: Automatic
No action required.
```

---

## 🎯 NEXT STEPS

1. **Immediate:** Fix GitHub secrets (5 minutes)
2. **Test:** Run diagnostic workflow (1 minute)
3. **Fix SSH:** If needed, enable OpenSSH (10 minutes)
4. **Test Emergency:** Run emergency restart manually (2 minutes)
5. **Verify Auto-Healing:** Let watchdog trigger automatically (wait 5 minutes)

---

## 📞 SUPPORT

**If still failing after following this guide:**

1. Check GitHub Actions logs for specific error messages
2. Test SSH manually from command line
3. Verify Windows VPS has:
   - OpenSSH Server installed and running
   - Port 42014 open in firewall
   - 'trader' user has permissions
4. Contact ForexVPS support if needed

**ForexVPS Support:**
- Ask them to enable SSH access on port 42014
- Verify no firewall rules blocking GitHub Actions IPs

---

**Last Updated:** October 22, 2025  
**Status:** Awaiting GitHub secrets verification and SSH configuration
