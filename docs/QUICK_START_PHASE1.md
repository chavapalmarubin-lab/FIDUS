# 🚀 PHASE 1: Unicode Fix - Quick Start Guide

## What You Need to Do NOW

### Step 1: Run the Workflow (2 minutes)

1. **Go to GitHub Actions**:
   - URL: `https://github.com/YOUR_ORG/YOUR_REPO/actions`
   - (Replace YOUR_ORG and YOUR_REPO with your actual values)

2. **Select the Workflow**:
   - Find: **"Fix MT5 Bridge Unicode Logging"**
   - Click on it

3. **Run the Workflow**:
   - Click: **"Run workflow"** dropdown (top right)
   - Select branch: **main**
   - Enable checkbox: **"Automatically restart Bridge service after fix"** ✅
   - Click: **"Run workflow"** button

4. **Watch Progress** (2-3 minutes):
   - Refresh page to see workflow running
   - Wait for green ✅ checkmark
   - Click on workflow run to see detailed logs

### Step 2: Verify Success

**From Workflow Logs**, look for:
```
[SUCCESS] Unicode fix completed successfully!
[OK] MT5 Bridge is running and connected!
```

**Expected Outcomes**:

✅ **GOOD** - Bridge starts without crashes:
```
Status: healthy
MT5 Available: true (or false - both OK at this stage)
MongoDB Connected: true
```

❌ **BAD** - Workflow fails:
- Check VPS password in Secrets
- Check VPS is accessible (try RDP: 92.118.45.135)
- Report error to me with full logs

### Step 3: Report Back to Me

**Tell me one of these**:

**Option A: SUCCESS**
```
"Phase 1 complete! Bridge is running. Health check shows: [paste result]"
```

**Option B: PARTIAL SUCCESS**
```
"Phase 1 complete! Bridge running but shows 'available: false'. 
Ready for Phase 2?"
```

**Option C: FAILURE**
```
"Phase 1 failed with error: [paste error message]"
```

---

## What Happens Next

### If Phase 1 Succeeds

**Dashboard Status**: Still showing $0 (expected - need Phase 2)

**What I'll do**:
1. Create Phase 2 commands for Task Scheduler fix
2. This will enable real MT5 connection
3. Dashboard will show real balances

**Your next action**: Run Phase 2 commands I provide

### If Phase 1 Fails

**What I'll do**:
1. Analyze error logs
2. Create manual fix script
3. Provide alternative deployment method

**Your next action**: Apply manual fix or troubleshoot connectivity

---

## Emergency: Manual Fix (If Workflow Fails)

**Only use this if GitHub Actions workflow completely fails**

### Manual Steps on VPS

1. **RDP to VPS**: 92.118.45.135

2. **Stop Bridge**:
```powershell
Stop-ScheduledTask -TaskName "MT5 Bridge Service"
Get-Process -Name python | Stop-Process -Force
```

3. **Download and Run Fix**:
```powershell
cd C:\mt5_bridge_service

# Download fix script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/main/vps-scripts/fix_unicode_logging.py" `
  -OutFile "fix_unicode_logging.py"

# Run fix
python fix_unicode_logging.py
```

4. **Restart Bridge**:
```powershell
Start-ScheduledTask -TaskName "MT5 Bridge Service"
Start-Sleep -Seconds 15

# Test
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health"
```

5. **Report Result**:
   - Tell me if Bridge starts successfully
   - Share health check output
   - Ready for Phase 2

---

## Quick Diagnostics

### Check Bridge is Running

```powershell
# On VPS, run:
Get-Process -Name python | Where-Object { $_.Path -like "*mt5_bridge_service*" }
```

**Expected**: Shows python.exe process  
**If empty**: Bridge not running - check Task Scheduler

### Check Health Endpoint

```powershell
# On VPS, run:
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" | 
  Select-Object -ExpandProperty Content
```

**Expected**: JSON response with status  
**If fails**: Bridge not responding - check logs

### Check for Unicode Errors

```powershell
# On VPS, check Task Scheduler History:
# 1. Open Task Scheduler (taskschd.msc)
# 2. Find "MT5 Bridge Service"
# 3. Right-click → View → History
# 4. Look for "Task started" events
# 5. Check for errors
```

**Look for**: No Unicode encoding errors  
**If present**: Manual fix needed

---

## FAQ

### Q: How do I know if Phase 1 worked?

**A**: Bridge service starts and runs without crashing. Health check responds (even if `available: false`).

### Q: Should dashboard show real data after Phase 1?

**A**: NO! Phase 1 only fixes crashes. Real data requires Phase 2 (Task Scheduler fix).

### Q: What if workflow says "Connection refused"?

**A**: VPS password in GitHub Secrets is wrong or VPS is unreachable. Check:
1. Can you RDP to 92.118.45.135?
2. Is VPS_PASSWORD secret set correctly?
3. Is VPS firewall blocking SSH/PowerShell remote?

### Q: Can I skip Phase 1?

**A**: NO! If Bridge crashes on startup due to Unicode, nothing else will work. Phase 1 MUST complete first.

---

## Timeline

**Phase 1**: ~2-3 minutes  
**Phase 2**: ~2 minutes (after Phase 1 success)  
**Phase 3**: ~5 minutes (after Phase 2 success)  
**Phase 4**: ~10 minutes (testing)

**Total**: ~20 minutes to full stability

---

## Contact Me After

Once you've run Phase 1 workflow, report back with:

1. ✅ or ❌ Status
2. Health check output (if available)
3. Any error messages
4. Ready to proceed to Phase 2?

**I'm ready to guide you through Phase 2 immediately after Phase 1 succeeds!** 🚀

---

**Created**: 2025-10-28  
**Phase**: 1 of 4  
**Priority**: CRITICAL - Do this first  
**Estimated Time**: 2-3 minutes
