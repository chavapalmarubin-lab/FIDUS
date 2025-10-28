# Remote VPS Diagnostics & Fix Workflow

## Overview

This GitHub Actions workflow allows you to diagnose and fix VPS issues remotely without manual access.

**Workflow File**: `.github/workflows/remote-vps-diagnostics-fix.yml`

---

## How to Use

### 1. Go to GitHub Actions
Navigate to: https://github.com/chavapalmarubin-lab/FIDUS/actions/workflows/remote-vps-diagnostics-fix.yml

### 2. Click "Run workflow"

### 3. Choose an Action:

#### **Option 1: Diagnose** (Start Here)
- **When to use**: First step when VPS has issues
- **What it does**: Tests if ports 8000 and 8001 are accessible
- **Safe**: Yes, read-only operation
- **Example output**:
  ```
  ✅ Port 8000 is accessible
  ✅ Port 8001 is accessible
  ```

#### **Option 2: Fix Port 8000** (MT5 Bridge)
- **When to use**: Port 8000 (MT5 Bridge) is not responding
- **What it does**: Attempts HTTP API restart of MT5 Bridge service
- **Safe**: Yes, restarts only MT5 Bridge
- **Fallback**: If this fails, suggests running emergency workflow

#### **Option 3: Fix Port 8001** (Full Restart Service)
- **When to use**: Port 8001 (Restart Service) is not responding
- **What it does**: Provides guidance for manual restart via Task Scheduler
- **Safe**: Yes, read-only (suggests manual steps)
- **Note**: Requires brief RDP access OR VPS reboot

#### **Option 4: Restart Services** (Both Ports)
- **When to use**: Both services need restart
- **What it does**: 
  1. Restarts MT5 Bridge (port 8000)
  2. Triggers full system restart (port 8001)
  3. Waits 60 seconds
  4. Verifies both services are healthy
- **Safe**: Yes, orchestrated restart sequence

#### **Option 5: Full Recovery** (Nuclear Option)
- **When to use**: Everything is broken, nothing responding
- **What it does**: Runs ALL recovery methods in sequence:
  1. Emergency HTTP restart
  2. Triggers GitHub emergency workflow
  3. Full system restart via port 8001
  4. Comprehensive verification
- **Safe**: Yes, but most aggressive
- **Duration**: ~2 minutes

---

## Troubleshooting Guide

### Problem: Port 8000 not responding
**Solution**:
1. Run workflow with `diagnose` action
2. If confirmed down, run `fix-port-8000`
3. If still down, run `full-recovery`
4. If still down after full recovery:
   - Check if VPS is powered on
   - RDP to VPS and check Task Manager for Python processes
   - Restart VPS if needed

### Problem: Port 8001 not responding
**Solution**:
1. Run workflow with `diagnose` action
2. Run `fix-port-8001` for guidance
3. Quick fix: RDP to VPS → Task Scheduler → Run "MT5 Full Restart Service"
4. OR: Reboot VPS (service auto-starts)

### Problem: Both ports not responding
**Solution**:
1. Run `full-recovery` action
2. Wait 2-3 minutes
3. Check results in workflow logs
4. If still down: VPS may be offline or frozen
   - Check VPS provider dashboard
   - Reboot VPS from provider control panel

### Problem: Services keep dying
**Solution**:
1. Check VPS resources (CPU, RAM, disk)
2. Check Windows Event Viewer for crashes
3. Review Python service logs on VPS
4. May need to investigate root cause

---

## Required GitHub Secrets

Make sure these secrets are configured:

1. **MT5_BRIDGE_API_KEY**
   - Used for port 8001 full restart service
   - Value: `fidus_admin_restart_2025_secure_key_xyz123`

2. **ADMIN_SECRET_TOKEN**
   - Used for port 8000 emergency restart
   - Value: (your admin token)

3. **GITHUB_TOKEN**
   - Auto-provided by GitHub Actions
   - Used for triggering other workflows

---

## Workflow Outputs

### Success Example:
```
🔍 Running VPS Diagnostics...

📡 Testing VPS connectivity...
✅ Port 8000 is accessible
Response: {"status":"healthy","timestamp":"2025-10-28..."}
✅ Port 8001 is accessible
Response: {"status":"healthy","timestamp":"2025-10-28..."}

📊 Diagnosis Complete
```

### Failure Example:
```
🔍 Running VPS Diagnostics...

📡 Testing VPS connectivity...
❌ Port 8000 is NOT accessible
Error: Unable to connect to the remote server
❌ Port 8001 is NOT accessible
Error: Unable to connect to the remote server

📊 Diagnosis Complete
If ports are not accessible, run 'fix-port-8000' or 'fix-port-8001' action
```

---

## When to Use Each Action

| Situation | Recommended Action | Estimated Time |
|-----------|-------------------|----------------|
| Not sure what's wrong | `diagnose` | 10 seconds |
| MT5 Bridge down | `fix-port-8000` | 30 seconds |
| Restart service down | `fix-port-8001` | Manual (5 min) |
| Both services acting up | `restart-services` | 2 minutes |
| Total system failure | `full-recovery` | 3-4 minutes |
| VPS completely unresponsive | Manual reboot | 5-10 minutes |

---

## Best Practices

1. **Always start with `diagnose`**
   - Confirms what's actually broken
   - Provides baseline for comparison

2. **Try targeted fixes first**
   - `fix-port-8000` for Bridge issues
   - `fix-port-8001` for restart service issues

3. **Use `full-recovery` sparingly**
   - Nuclear option, tries everything
   - Use when targeted fixes fail

4. **Monitor after fix**
   - Wait 2-3 minutes after running fix
   - Check dashboard: https://fidus-invest.emergent.host
   - Verify accounts syncing

5. **Document issues**
   - Note what action was used
   - Record if it worked
   - Helps identify patterns

---

## Limitations

**What this workflow CAN do:**
- ✅ Diagnose connectivity issues
- ✅ Trigger HTTP API restarts
- ✅ Trigger GitHub workflow restarts
- ✅ Verify service health

**What this workflow CANNOT do:**
- ❌ Access VPS filesystem directly (no WinRM/SSH)
- ❌ Kill specific processes on VPS
- ❌ Modify VPS configuration
- ❌ Restart VPS itself
- ❌ Fix Windows-level issues

**For deeper issues**, you'll need:
- RDP access to VPS
- VPS provider control panel access
- Manual intervention

---

## Emergency Contacts

**If this workflow doesn't resolve issues:**

1. **Check VPS provider dashboard**
   - Verify VPS is powered on
   - Check for alerts or maintenance

2. **Quick RDP check** (2 minutes)
   - RDP to `92.118.45.135`
   - Check Task Manager for Python processes
   - Restart any crashed services

3. **Last resort: Reboot VPS**
   - All services configured to auto-start
   - System will self-recover in 3-5 minutes

---

## Success Indicators

After running a fix, verify:

- [ ] Port 8000 health check returns 200
- [ ] Port 8001 health check returns 200
- [ ] FIDUS dashboard loads
- [ ] MT5 accounts showing real balances (not $0)
- [ ] No errors in backend logs

**All checks passed? System is healthy!** ✅

---

## Version History

- **v1.0** (2025-10-28): Initial release
  - Diagnose functionality
  - Port 8000 fix
  - Port 8001 fix
  - Full recovery mode
  - Comprehensive verification

---

**Questions?** Check workflow run logs for detailed output and error messages.
