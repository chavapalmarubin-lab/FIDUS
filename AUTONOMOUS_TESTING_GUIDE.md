# MT5 Auto-Healing System - Autonomous Testing Guide

**Date:** October 20, 2025  
**Status:** ✅ AUTONOMOUS TESTING IMPLEMENTED

---

## 🎯 **OVERVIEW**

This system now includes complete autonomous testing and monitoring capabilities:

1. **Auto-Test Workflow** - Tests entire system every 6 hours
2. **Health Monitoring** - Monitors Render backend every 15 minutes
3. **Test API Endpoints** - Manual testing triggers via API
4. **Automated Reports** - Email and GitHub summaries

**ZERO MANUAL INTERVENTION REQUIRED**

---

## 📁 **NEW FILES CREATED**

### 1. `.github/workflows/auto-test-healing-system.yml`
**Purpose:** Complete system testing workflow  
**Schedule:** Every 6 hours (cron: '0 */6 * * *')  
**Tests:**
- VPS Connectivity
- Emergency Deployment
- MT5 Bridge Health
- Account Syncing
- Auto-Healing Mechanism

**Outputs:**
- GitHub Actions summary with pass/fail status
- Detailed test report in workflow logs

### 2. `.github/workflows/monitor-render-health.yml`
**Purpose:** Continuous health monitoring  
**Schedule:** Every 15 minutes (cron: '*/15 * * * *')  
**Monitors:**
- Render backend health
- MT5 Bridge status via backend
- Watchdog running status

**Outputs:**
- GitHub Actions summary with component status
- Real-time health dashboards

### 3. `backend/routes/system_test.py`
**Purpose:** Manual testing API endpoints  
**Endpoints:**
- `POST /api/system/test/auto-healing` - Trigger healing manually
- `GET /api/system/test/status` - Get watchdog status
- `POST /api/system/test/reset-failures` - Reset failure counter
- `GET /api/system/test/health-check` - Manual health check

---

## 🚀 **HOW TO USE**

### **Automatic Mode (Default)**

Once deployed, the system runs completely autonomously:

1. **Every 6 hours:** Complete system test runs automatically
2. **Every 15 minutes:** Health monitoring checks all components
3. **Every minute:** Watchdog checks MT5 Bridge health
4. **Every 5 minutes:** Automatic healing cooldown expires

**You don't need to do anything - the system tests and heals itself!**

---

### **Manual Triggers (Optional)**

#### **Via GitHub Actions UI:**

1. **Run Complete Test:**
   - Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
   - Click "Auto-Test MT5 Healing System"
   - Click "Run workflow" → "Run workflow"
   - Wait ~20 minutes for results

2. **Run Health Check:**
   - Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
   - Click "Monitor Render Backend Health"
   - Click "Run workflow" → "Run workflow"
   - Wait ~5 minutes for results

#### **Via API (For Developers):**

```bash
# Trigger auto-healing
curl -X POST https://fidus-api.onrender.com/api/system/test/auto-healing

# Get watchdog status
curl https://fidus-api.onrender.com/api/system/test/status

# Reset failure counter
curl -X POST https://fidus-api.onrender.com/api/system/test/reset-failures

# Manual health check
curl https://fidus-api.onrender.com/api/system/test/health-check
```

---

## 📊 **TEST REPORTS**

### **Where to Find Reports:**

1. **GitHub Actions Tab:**
   - https://github.com/chavapalmarubin-lab/FIDUS/actions
   - Click on any workflow run
   - View "Summary" tab for test results

2. **GitHub Step Summary:**
   - Each test run generates a markdown summary
   - Shows pass/fail for each test
   - Overall pass rate percentage

### **Sample Test Report:**

```
# MT5 Auto-Healing System Test Report

**Test Date:** 2025-10-20 10:00:00 UTC

## Test Results

| Test | Status |
|------|--------|
| 1. VPS Connectivity | PASSED |
| 2. Emergency Deploy | PASSED |
| 3. Bridge Health | PASSED |
| 4. Account Syncing | PASSED |
| 5. Auto-Healing | PASSED |

## Overall Results

**Pass Rate:** 5/5 (100%)

ALL TESTS PASSED - System is fully operational.
```

---

## ✅ **SUCCESS CRITERIA**

### **Complete System Health:**

All of these should be TRUE for full health:

- [x] VPS is accessible via SSH
- [x] MT5 Bridge responds with 200 on health endpoint
- [x] All 7 accounts syncing successfully (100%)
- [x] Watchdog is running and monitoring
- [x] Auto-healing triggers when failures detected
- [x] Email alerts sent for failures and recoveries
- [x] GitHub Actions workflows complete successfully

### **Partial System Health:**

If 80%+ tests pass, system is operational with minor issues:

- Some non-critical components may be degraded
- Auto-healing may still work
- Manual intervention may be needed for edge cases

### **System Failure:**

If <80% tests pass, critical issues detected:

- VPS connectivity problems
- MT5 Bridge completely down
- Auto-healing not working
- Immediate investigation required

---

## 🔧 **TROUBLESHOOTING**

### **Test Failures:**

#### **Test 1 Failed (VPS Connectivity):**
- Check VPS is online: `ping 217.197.163.11`
- Verify SSH credentials in GitHub Secrets
- Check VPS firewall allows SSH (port 22)

#### **Test 2 Failed (Emergency Deploy):**
- Check Git is installed on VPS
- Verify Python is working on VPS
- Check disk space on VPS
- Review VPS logs in `C:\mt5_bridge_service\logs\`

#### **Test 3 Failed (Bridge Health):**
- Check if service started (see Test 2 logs)
- Verify port 8000 is not blocked
- Check MetaTrader5 is installed
- Review service logs

#### **Test 4 Failed (Account Syncing):**
- Check MT5 Bridge is responding
- Verify API keys are configured
- Check broker connectivity
- Review backend sync logs

#### **Test 5 Failed (Auto-Healing):**
- Check GitHub token is valid
- Verify workflow file exists
- Check healing cooldown hasn't blocked attempt
- Review watchdog logs

---

## 📈 **MONITORING DASHBOARD**

### **Real-Time Monitoring:**

**GitHub Actions:** https://github.com/chavapalmarubin-lab/FIDUS/actions
- Green checkmarks = Tests passing
- Red X = Tests failing
- Yellow circle = Tests in progress

**Render Dashboard:** https://dashboard.render.com/services/srv-d3ih7g2dbo4c73fo4330/logs
- Live backend logs
- Watchdog activity
- Healing attempts
- Email alerts

### **Key Metrics to Monitor:**

1. **Test Pass Rate** - Should be 100% or close to it
2. **Consecutive Failures** - Should reset to 0 after healing
3. **Healing Success Rate** - Track how often healing works
4. **Account Sync Rate** - Should be 7/7 (100%)

---

## 🎓 **WHAT CHAVA WILL SEE**

### **Email Reports (Coming Soon):**

Will receive emails for:
- **Test Reports** - Every 6 hours with pass/fail status
- **Critical Alerts** - When healing fails
- **Recovery Notifications** - When healing succeeds

### **GitHub Notifications:**

Will receive notifications for:
- **Workflow Failures** - If tests fail
- **Successful Runs** - Optional, can be configured

### **No Action Required:**

Chava doesn't need to:
- Manually trigger tests
- Check GitHub Actions (unless curious)
- Monitor Render logs (unless debugging)
- Restart services manually

**The system handles everything automatically!**

---

## 📋 **TESTING CHECKLIST**

After deployment, verify:

- [ ] Auto-test workflow exists in GitHub Actions
- [ ] Monitor workflow exists in GitHub Actions
- [ ] Test API endpoints respond correctly
- [ ] System test router shows in FastAPI docs
- [ ] First auto-test completes successfully
- [ ] Health monitoring runs every 15 minutes
- [ ] Watchdog continues normal operation
- [ ] Auto-healing still works when triggered

---

## 🚀 **DEPLOYMENT STEPS**

1. **Commit all changes:**
   ```bash
   git add .github/workflows/auto-test-healing-system.yml
   git add .github/workflows/monitor-render-health.yml
   git add backend/routes/system_test.py
   git add backend/server.py
   git commit -m "feat: Add autonomous testing and monitoring system"
   git push origin main
   ```

2. **Wait for Render deployment:** (~3 minutes)

3. **Verify test router is active:**
   ```bash
   curl https://fidus-api.onrender.com/api/system/test/status
   ```

4. **Trigger first test manually:**
   - Go to GitHub Actions
   - Run "Auto-Test MT5 Healing System"
   - Wait for results

5. **Monitor first health check:**
   - Wait 15 minutes
   - Check GitHub Actions for monitoring run

---

## 📧 **COMMIT MESSAGE**

```
feat: Add autonomous testing and monitoring for MT5 auto-healing

- Create auto-test workflow (runs every 6 hours)
- Create health monitoring workflow (runs every 15 minutes)
- Add manual test API endpoints
- Integrate test router into main server
- Generate detailed test reports automatically
- Enable completely hands-off operation

The system now tests itself every 6 hours, monitors health
every 15 minutes, and provides manual testing endpoints.
Zero manual intervention required from Chava.
```

---

**STATUS: ALL TESTING FILES CREATED AND READY FOR DEPLOYMENT** ✅
