# MT5 Bridge Stabilization - Complete Implementation Guide

## 🎯 Overview

This guide implements a complete fix for the MT5 Bridge stability issues that prevent real-time account data from reaching the FIDUS dashboard.

**Current State**: Dashboard shows $0 balances despite MT5 terminals running  
**Target State**: Dashboard shows real-time balances, auto-healing works, full automation

---

## 🚨 The Three Critical Issues

### Issue #1: Unicode Logging Crash (HIGHEST PRIORITY)
- **Problem**: Bridge crashes on startup with Unicode encoding errors
- **Impact**: Service cannot start at all
- **Symptom**: Task Scheduler shows "Running" but no Python process exists
- **Fix**: Phase 1 - Remove emojis and special characters from logs

### Issue #2: Task Scheduler Session Conflict
- **Problem**: Bridge runs in SYSTEM session, MT5 Terminal in user session
- **Impact**: Bridge starts but can't connect to terminal → $0 balances
- **Symptom**: `IPC timeout (-10005)` errors, `available: false` in health check
- **Fix**: Phase 2 - Reconfigure to run as Administrator in user session

### Issue #3: MT5 "Allow Algorithmic Trading" Setting
- **Problem**: Setting may not persist across terminal restarts
- **Impact**: Bridge can't read data even when connected
- **Symptom**: Connection works but no data flows
- **Fix**: Phase 3 - Verify persistence, add startup checks

---

## 📋 Implementation Phases

### Phase 1: Unicode Logging Fix (30 seconds) ⚡ START HERE

**Status**: ✅ Ready to deploy  
**Method**: RDP + PowerShell (VPS is Windows, not Linux)  
**Risk**: Low (automatic backup created)

**What it does**:
- Replaces 45+ Unicode characters (✅→[OK], 🚀→[START], etc.)
- Creates backup of original file
- Restarts Bridge service
- Verifies Bridge can start without crashes

**Instructions**:
→ See: [PHASE1_QUICK_COMMAND.md](/docs/PHASE1_QUICK_COMMAND.md) ← **FASTEST**  
→ See: [PHASE1_MANUAL_FIX.md](/docs/PHASE1_MANUAL_FIX.md) ← Detailed guide

**Quick Start** (One Command):
```powershell
# RDP to VPS (92.118.45.135), open PowerShell (Admin), run:
cd C:\mt5_bridge_service && Stop-ScheduledTask -TaskName "MT5 Bridge Service" -ErrorAction SilentlyContinue && Start-Sleep -Seconds 5 && Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*mt5_bridge_service*" } | Stop-Process -Force && python fix_unicode_logging.py && Start-Sleep -Seconds 3 && Start-ScheduledTask -TaskName "MT5 Bridge Service" && Start-Sleep -Seconds 15 && Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health"
```

**Success Criteria**:
- ✅ Workflow completes without errors
- ✅ Bridge service starts (no crashes)
- ✅ No Unicode errors in logs
- ⚠️ Dashboard may still show $0 (expected - proceed to Phase 2)

---

### Phase 2: Task Scheduler Configuration (2 minutes)

**Status**: ✅ Ready to deploy  
**Method**: VPS PowerShell commands (via RDP or existing workflow)  
**Risk**: Low (can revert easily)

**What it does**:
- Changes Bridge to run as "Administrator" (not SYSTEM)
- Sets "Run only when user is logged on" (Interactive session)
- Enables "Run with highest privileges"
- Restarts Bridge in correct session

**Instructions**:
→ See: [FIX_BRIDGE_USER_SESSION.md](/docs/FIX_BRIDGE_USER_SESSION.md)

**Quick Start**:
```powershell
# Option A: Use existing workflow
# Run workflow: "Fix MT5 Bridge User Session"

# Option B: Manual PowerShell (on VPS)
$taskName = "MT5 Bridge Service"
$principal = New-ScheduledTaskPrincipal -UserId "Administrator" -LogonType Interactive -RunLevel Highest
Set-ScheduledTask -TaskName $taskName -Principal $principal
Stop-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 5
Start-ScheduledTask -TaskName $taskName
```

**Success Criteria**:
- ✅ Health check shows `"available": true`
- ✅ Dashboard shows real balances (not $0)
- ✅ All 7 accounts syncing

---

### Phase 3: MT5 Settings & Health Checks (5 minutes)

**Status**: 🔧 Implementation ready  
**Method**: VPS verification + documentation  
**Risk**: None (verification only)

**What it does**:
- Verifies "Allow algorithmic trading" setting persistence
- Documents MT5 configuration requirements
- Adds startup health check to Bridge
- Creates verification checklist

**Instructions**:
→ See: [PHASE3_MT5_SETTINGS.md](/docs/PHASE3_MT5_SETTINGS.md)

**Success Criteria**:
- ✅ Setting persists after MT5 restart
- ✅ Documented as critical startup check
- ✅ Health check validates MT5 connection on startup

---

### Phase 4: End-to-End Testing (10 minutes)

**Status**: 🧪 Ready after Phase 1-3  
**Method**: Automated testing + manual verification  
**Risk**: None (testing only)

**What it does**:
- Tests complete auto-start sequence
- Simulates VPS reboot
- Verifies auto-healing triggers
- Confirms dashboard updates

**Instructions**:
→ See: [PHASE4_TESTING.md](/docs/PHASE4_TESTING.md)

**Success Criteria**:
- ✅ Bridge auto-starts after VPS reboot
- ✅ Dashboard shows real balances within 1 minute
- ✅ Auto-healing detects failures and triggers restart
- ✅ Email alerts sent for critical issues

---

## 🎯 Recommended Execution Order

### Immediate (Today)

**1. Phase 1: Unicode Fix** (2 minutes)
   - Run GitHub Actions workflow
   - Verify Bridge can start
   - **DO NOT expect real data yet**

**2. Phase 2: Task Scheduler** (2 minutes)
   - Run PowerShell commands on VPS
   - Verify real balances appear
   - **Dashboard should work after this**

**3. Quick Verification** (1 minute)
   - Check dashboard shows real balances
   - Test one manual restart
   - Confirm auto-sync works

### Follow-Up (Within 24 hours)

**4. Phase 3: MT5 Settings** (5 minutes)
   - Verify algorithmic trading setting
   - Document persistence behavior
   - Add to startup checklist

**5. Phase 4: Full Testing** (10 minutes)
   - Test VPS reboot scenario
   - Verify auto-healing
   - Validate alerts

---

## 📊 Progress Tracking

### Current Status

| Phase | Status | Completion | Blockers |
|-------|--------|------------|----------|
| Phase 1: Unicode Fix | 🟡 Ready | 0% | None - ready to deploy |
| Phase 2: Task Scheduler | 🟡 Ready | 0% | Requires Phase 1 |
| Phase 3: MT5 Settings | 🟡 Ready | 0% | Requires Phase 2 |
| Phase 4: Testing | ⚪ Waiting | 0% | Requires Phase 1-3 |

**Legend**:
- 🟢 Complete
- 🟡 Ready to start
- 🔵 In progress
- ⚪ Waiting on dependencies
- 🔴 Blocked

---

## 🚀 Quick Start Commands

### For You (User)

**Step 1: Run Phase 1 Workflow**
```
1. Go to: https://github.com/YOUR_ORG/YOUR_REPO/actions
2. Click: "Fix MT5 Bridge Unicode Logging"
3. Click: "Run workflow" button
4. Enable: "auto_restart" checkbox
5. Click: "Run workflow"
6. Wait: ~2 minutes for completion
```

**Step 2: Pull Results & Run Phase 2**
```bash
# I'll prepare the commands for you after Phase 1 completes
```

### For Me (AI Agent) - After Your Confirmation

**After Phase 1 succeeds**:
```bash
# Create Phase 2 workflow or provide PowerShell commands
# Document results
# Update progress tracking
```

---

## ✅ Verification Checklist

### After Phase 1 (Unicode Fix)

- [ ] GitHub Actions workflow completed successfully
- [ ] No "UnicodeEncodeError" in workflow logs
- [ ] Bridge process running in Task Manager (even if not connected)
- [ ] Health endpoint responds: `http://localhost:8000/api/mt5/bridge/health`
- [ ] No more startup crashes in Task Scheduler History

**Expected**: Bridge RUNS but may show `available: false` (normal at this stage)

### After Phase 2 (Task Scheduler)

- [ ] Task shows "Run only when user is logged on"
- [ ] Task shows user: "Administrator" (not SYSTEM)
- [ ] Health check shows: `"available": true`
- [ ] Dashboard displays real balances (not $0)
- [ ] All 7 accounts syncing

**Expected**: Dashboard shows real data, auto-sync works

### After Phase 3 (MT5 Settings)

- [ ] "Allow algorithmic trading" is checked in MT5
- [ ] Setting persists after terminal restart
- [ ] Documented in startup checklist
- [ ] Health check validates setting on Bridge startup

**Expected**: Confidence in configuration persistence

### After Phase 4 (Testing)

- [ ] VPS reboot → Bridge auto-starts correctly
- [ ] Dashboard recovers within 1 minute
- [ ] Auto-healing detects $0 balance failure
- [ ] Auto-healing triggers full restart
- [ ] Email alerts sent for critical failures

**Expected**: Fully automated, self-healing system

---

## 🚨 Troubleshooting Decision Tree

```
START: Dashboard shows $0 balances
│
├─ Is Bridge process running?
│  ├─ NO → Phase 1 incomplete (Unicode fix needed)
│  │      → Run "Fix MT5 Bridge Unicode Logging" workflow
│  │
│  └─ YES → Continue to next check
│
├─ Does health check show "available: true"?
│  ├─ NO → Phase 2 incomplete (Session issue)
│  │      → Run Task Scheduler reconfiguration
│  │      → See: FIX_BRIDGE_USER_SESSION.md
│  │
│  └─ YES → Continue to next check
│
├─ Is MT5 Terminal running and connected?
│  ├─ NO → MT5 Terminal issue
│  │      → Check terminal status
│  │      → Verify internet connection
│  │      → Check broker credentials
│  │
│  └─ YES → Continue to next check
│
├─ Is "Allow algorithmic trading" enabled?
│  ├─ NO → Phase 3 incomplete
│  │      → Enable in MT5: Tools → Options → Expert Advisors
│  │      → Check "Allow algorithmic trading"
│  │      → Restart MT5
│  │
│  └─ YES → Advanced troubleshooting needed
│           → Check Windows Event Viewer
│           → Check Bridge logs
│           → Verify MongoDB connection
│           → Contact support with diagnostic logs
```

---

## 📞 Support & Next Steps

### If Phase 1 Fails

**Collect**:
- GitHub Actions workflow output (full log)
- VPS Task Scheduler history
- Windows Event Viewer → Application logs

**Try**:
- Manual fix (see PHASE1_UNICODE_FIX.md → Manual Fix section)
- Verify VPS_PASSWORD secret is correct
- Test VPS connectivity via RDP

### If Phase 2 Fails

**Collect**:
- Health check response: `Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health"`
- Task Manager screenshot (Python process details)
- Task Scheduler task configuration screenshot

**Try**:
- Task Scheduler GUI method (see FIX_BRIDGE_USER_SESSION.md → Option B)
- Verify Administrator user is logged in
- Check if MT5 Terminal is running first

### If Phases 1-2 Work But Data Still $0

**Check**:
1. MT5 Terminal connection status (bottom-right corner)
2. "Allow algorithmic trading" setting
3. Bridge logs for specific error messages
4. MongoDB connection status
5. VPS internet connectivity

---

## 🎯 Success Definition

**Full success** means:

1. **Stability**:
   - Bridge runs 24/7 without crashes
   - Auto-starts after VPS reboot
   - Recovers from MT5 terminal restarts

2. **Data Accuracy**:
   - Dashboard shows real-time balances (not $0)
   - All 7 accounts sync within 1 minute
   - P&L updates reflect actual trading

3. **Auto-Healing**:
   - Detects $0 balance failures
   - Triggers automatic restart
   - Sends email alerts
   - Recovers without manual intervention

4. **Monitoring**:
   - Health checks pass
   - Logs are clean (no Unicode errors)
   - Sync rate = 100%

---

## 📁 Related Documentation

- [PHASE1_UNICODE_FIX.md](/docs/PHASE1_UNICODE_FIX.md) - Unicode logging fix
- [FIX_BRIDGE_USER_SESSION.md](/docs/FIX_BRIDGE_USER_SESSION.md) - Task Scheduler configuration
- [REMOTE_VPS_DIAGNOSTICS.md](/docs/REMOTE_VPS_DIAGNOSTICS.md) - Remote diagnostics workflow
- [vps-scripts/DEPLOYMENT.md](/vps-scripts/DEPLOYMENT.md) - VPS deployment guide

---

## 🔄 Workflow Files

- `fix-unicode-logging.yml` - Phase 1 automation
- `fix-bridge-user-session.yml` - Phase 2 reference (manual execution)
- `remote-vps-diagnostics-fix.yml` - Diagnostic tools
- `mt5-full-restart.yml` - Emergency restart automation

---

**Last Updated**: 2025-10-28  
**Status**: Phase 1 ready for deployment  
**Estimated Total Time**: 20 minutes (all phases)  
**Risk Level**: Low (all changes reversible)

---

## 🎬 Ready to Start?

**Your next action**:

1. **Confirm this plan** by responding with: "Confirmed, start Phase 1"
2. **I will run** the GitHub Actions workflow for you (or provide instructions)
3. **You will test** on your VPS after deployment
4. **Report results** so I can proceed to Phase 2

**Let's fix this! 🚀**
