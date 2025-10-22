# MT5 Auto-Healing System - Next Steps

## ✅ COMPLETED SO FAR

1. **VPS Code Deployment** ✅
   - Updated `mt5_bridge_api_service.py` successfully deployed to VPS (92.118.45.135)
   - Service running on port 8000
   - New endpoints operational:
     - `/api/mt5/bridge/health` - Working (returns healthy status)
     - `/api/admin/emergency-restart` - Working (requires token)
     - `/api/admin/one-time-setup` - Working (ready for configuration)

2. **Backend Watchdog** ✅
   - MT5 Watchdog service configured in backend
   - Monitors health every 60 seconds
   - Auto-healing threshold: 3 consecutive failures
   - Triggers GitHub Actions for recovery

3. **GitHub Actions Workflows** ✅
   - `configure-vps-auto-healing.yml` - Ready to configure ADMIN_SECRET_TOKEN
   - `emergency-restart-hybrid.yml` - Ready to trigger restarts via API

## 🎯 NEXT STEPS TO COMPLETE AUTO-HEALING

### Step 1: Add GitHub Secret (REQUIRED)

The auto-healing system needs a secure token to authenticate restart requests.

**Action Required:**
1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/settings/secrets/actions
2. Click "New repository secret"
3. Name: `ADMIN_SECRET_TOKEN`
4. Value: `fidus_admin_restart_2025_secure_key_xyz123`
5. Click "Add secret"

**Why?** Both the GitHub workflows and VPS need this token to securely communicate.

### Step 2: Run Configuration Workflow

After adding the GitHub secret, run the configuration workflow to set up the VPS:

**Action Required:**
1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions/workflows/configure-vps-auto-healing.yml
2. Click "Run workflow" dropdown
3. Select branch: `main`
4. Click "Run workflow"

**What it does:**
- Adds `ADMIN_SECRET_TOKEN` to VPS .env file
- Attempts service restart to load new token
- Verifies service health

### Step 3: Verify Auto-Healing Works

Test the emergency restart manually:

**Action Required:**
1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions/workflows/emergency-restart-hybrid.yml
2. Click "Run workflow"
3. Enter reason: "Testing auto-healing system"
4. Click "Run workflow"

**Expected outcome:**
- Workflow triggers restart via API
- MT5 Bridge service restarts
- Health check confirms service is healthy

### Step 4: Monitor Watchdog Activity

The backend MT5 Watchdog is automatically monitoring the bridge:

**Check watchdog logs:**
```bash
# On Render.com backend, check logs for:
[MT5 WATCHDOG] 🚀 Starting MT5 Watchdog monitoring loop
[MT5 WATCHDOG] ✅ MT5 Bridge healthy - Consecutive failures: 0
```

**How to verify it's working:**
1. Check backend logs on Render.com
2. Look for "[MT5 WATCHDOG]" messages every 60 seconds
3. Confirm it shows "healthy" status

### Step 5: Security Cleanup (After Testing)

Once auto-healing is verified working, remove the one-time setup endpoint:

**Action Required:**
1. On VPS, open `C:\mt5_bridge_service\mt5_bridge_api_service.py`
2. Remove lines 634-705 (the `/api/admin/one-time-setup` endpoint)
3. Restart the service

**Why?** This endpoint was only needed for initial setup. Removing it improves security.

## 🔍 HOW TO VERIFY EVERYTHING IS WORKING

### Check 1: VPS Health Endpoint
```bash
curl http://92.118.45.135:8000/api/mt5/bridge/health
```
Expected: `{"status": "healthy", ...}`

### Check 2: Backend Watchdog Logs
- Go to Render.com backend logs
- Search for "[MT5 WATCHDOG]"
- Should see checks every 60 seconds

### Check 3: Emergency Restart Works
- Manually trigger workflow (Step 3 above)
- Check workflow succeeds
- Verify service restarts

### Check 4: Auto-Healing Triggers Automatically
Simulate failure and watch auto-healing:
1. Stop MT5 Bridge on VPS manually
2. Wait 3 minutes (3 consecutive failures)
3. Watch watchdog trigger auto-healing workflow
4. Verify service recovers automatically
5. Check email for recovery notification

## 📊 MONITORING & ALERTS

### Email Alerts

Auto-healing sends email notifications:

**Recovery Success:**
- Subject: "✅ MT5 Bridge Recovered"
- Details: Downtime duration, recovery method

**Critical Failure:**
- Subject: "🚨 MT5 Bridge Critical - Auto-Healing Failed"
- Details: Manual intervention required

### GitHub Actions History

Monitor auto-healing activity:
- URL: https://github.com/chavapalmarubin-lab/FIDUS/actions
- Filter: "MT5 Bridge Emergency Restart"
- Shows all auto-healing attempts

## 🛠️ TROUBLESHOOTING

### Issue: "ADMIN_SECRET_TOKEN not configured" error

**Solution:**
1. Verify GitHub secret was added (Step 1)
2. Run configuration workflow (Step 2)
3. Restart VPS service manually

### Issue: Workflow fails with 401 Unauthorized

**Solution:**
1. Token mismatch - verify both places use same token:
   - GitHub Secret: `ADMIN_SECRET_TOKEN`
   - VPS .env: `ADMIN_SECRET_TOKEN`
2. Run configuration workflow again

### Issue: Watchdog not detecting failures

**Solution:**
1. Check backend is running: `sudo supervisorctl status backend`
2. Check watchdog initialized: Search logs for "[MT5 WATCHDOG] 🚀 Starting"
3. Verify VPS URL correct: `http://92.118.45.135:8000`

### Issue: Service won't restart on VPS

**Solution:**
1. Check VPS Task Scheduler is running
2. Verify Python process: `tasklist | findstr python`
3. Manually restart if needed:
   ```powershell
   cd C:\mt5_bridge_service
   python mt5_bridge_api_service.py
   ```

## 🎯 SUCCESS CRITERIA

Auto-healing is fully operational when:

- ✅ GitHub secret `ADMIN_SECRET_TOKEN` added
- ✅ Configuration workflow runs successfully
- ✅ VPS .env contains `ADMIN_SECRET_TOKEN`
- ✅ Emergency restart workflow works
- ✅ Watchdog logs show monitoring every 60s
- ✅ Manual failure test triggers auto-healing
- ✅ Email notifications received
- ✅ One-time setup endpoint removed

## 📚 RELATED DOCUMENTATION

- Infrastructure Overview: `/app/docs/infrastructure-overview.md`
- Troubleshooting Guide: `/app/docs/troubleshooting.md`
- VPS Migration History: `/app/docs/vps-migration-oct-2025.md`
- MT5 Auto-Healing Details: `/app/docs/mt5-auto-healing.md`

---

**Current Status:** Ready for GitHub secret configuration (Step 1)

**Estimated Time to Complete:** 15-20 minutes
