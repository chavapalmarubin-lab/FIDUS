# GitHub Actions Workflows Guide - LUCRUM Integration

**Created:** November 21, 2025  
**Purpose:** Step-by-step guide to run GitHub Actions workflows for LUCRUM broker VPS integration  

---

## 📋 Overview

Three GitHub Actions workflows have been created to complete the LUCRUM broker integration on your VPS. These workflows will:

1. **Verify** if account 2198 is syncing
2. **Restart** the MT5 sync service to pick up the new LUCRUM account
3. **Update** MongoDB connection credentials (if needed)

---

## 🚀 Quick Start - Run These Workflows in Order

### Step 1: Verify Current Sync Status

**Workflow:** `Verify LUCRUM Account Sync`  
**File:** `.github/workflows/verify-lucrum-sync.yml`  
**Purpose:** Check if account 2198 is already syncing

**How to Run:**
1. Go to your GitHub repository: `https://github.com/chavapalmarubin-lab/FIDUS`
2. Click on **Actions** tab
3. Find workflow: **"Verify LUCRUM Account Sync"**
4. Click **"Run workflow"** button
5. Select branch: `main`
6. Click green **"Run workflow"** button

**What It Checks:**
- ✅ MT5 sync process status
- ✅ Task Scheduler configuration
- ✅ LUCRUM MT5 Terminal status  
- ✅ MongoDB account 2198 configuration
- ✅ MT5 Bridge API response
- ✅ Sync logs for LUCRUM entries

**Expected Result:**
- If account 2198 appears in API response → ✅ **Sync is working!**
- If account 2198 is NOT in API → ⏩ **Proceed to Step 2**

---

### Step 2: Restart MT5 Sync Service

**Workflow:** `Restart MT5 Sync Service (Include LUCRUM)`  
**File:** `.github/workflows/restart-mt5-sync-lucrum.yml`  
**Purpose:** Restart the sync service to pick up account 2198

**How to Run:**
1. Go to **Actions** tab in GitHub
2. Find workflow: **"Restart MT5 Sync Service (Include LUCRUM)"**
3. Click **"Run workflow"** button
4. Select branch: `main`
5. Click green **"Run workflow"** button

**What It Does:**
1. ✅ Stops existing MT5 sync service
2. ✅ Verifies MongoDB configuration for account 2198
3. ✅ Checks LUCRUM MT5 terminal is running
4. ✅ Restarts MT5 sync service
5. ✅ Waits 30 seconds for initial sync
6. ✅ Verifies account 2198 in API response
7. ✅ Checks sync logs for LUCRUM

**Expected Result:**
- Service restarts successfully
- Account 2198 appears in API response with balance/equity data
- Total accounts changes from 13 to **14** (13 MEXAtlantic + 1 LUCRUM)

**Time:** ~3-5 minutes

---

### Step 3: Update MongoDB Credentials (Optional)

**Workflow:** `Update VPS MongoDB Connection (LUCRUM Support)`  
**File:** `.github/workflows/update-vps-mongodb-url.yml`  
**Purpose:** Update MongoDB connection if using wrong credentials

**When to Run:**
- Only if Step 2 shows MongoDB connection errors
- Only if logs show "connection refused" or "authentication failed"
- **NOT needed if Step 2 works correctly**

**How to Run:**
1. Go to **Actions** tab in GitHub
2. Find workflow: **"Update VPS MongoDB Connection (LUCRUM Support)"**
3. Click **"Run workflow"** button
4. Select branch: `main`
5. Click green **"Run workflow"** button

**What It Does:**
1. ✅ Tests MongoDB connection with emergent-ops credentials
2. ✅ Updates sync script with correct MongoDB URL
3. ✅ Sets MONGO_URL system environment variable
4. ✅ Verifies account 2198 exists in database

**After Running:**
- Must run Step 2 again to restart service with new credentials

---

## 📊 How to View Workflow Results

### During Workflow Execution:

1. Click on the workflow run (shows as "in progress" with yellow spinner)
2. Watch real-time logs for each step
3. Look for:
   - ✅ Green checkmarks = Success
   - ❌ Red X = Failed
   - 🎯 Account 2198 specifically mentioned

### After Workflow Completes:

1. Click on completed workflow run
2. Scroll to **Summary** section at top
3. Read detailed report with:
   - What was checked
   - Current status
   - Next steps
   - Troubleshooting tips

### Check Sync Status:

**Look for this in the logs:**
```
🎉 SUCCESS! LUCRUM Account 2198 IS SYNCING!

Account Details:
  Account: 2198
  Balance: $10,000.00
  Equity: $10,000.00
  Server: Lucrumcapital-Live
```

---

## 🔍 Troubleshooting Guide

### Issue 1: Account 2198 Not Found in API

**Symptoms:**
- Restart workflow completes but shows "Account 2198 NOT FOUND"
- API response doesn't include account 2198

**Possible Causes:**
1. LUCRUM MT5 terminal is not running on VPS
2. Terminal is not logged into account 2198
3. Server name mismatch

**Solutions:**

**Solution A: Check MT5 Terminal (Manual)**
1. RDP into VPS: `92.118.45.135` (user: `trader`)
2. Look for LUCRUM MT5 terminal window
3. Check if it shows account 2198 in title bar
4. If not logged in:
   - Click File → Login to Trade Account
   - Enter: 2198
   - Password: `Fidus13!`
   - Server: `Lucrumcapital-Live`
5. After logging in, wait 2 minutes and run Step 1 (Verify) again

**Solution B: Wait for Sync Cycle**
- Sometimes takes 2-3 sync cycles (5-10 minutes)
- Wait 5 minutes and run Step 1 (Verify) again

**Solution C: Check Logs**
- In workflow output, look for "Recent Sync Logs" section
- Look for error messages related to 2198 or Lucrum
- Common errors:
  - "Login failed" → Check password/server name
  - "Terminal not found" → MT5 terminal not running
  - "Connection timeout" → Network issue

---

### Issue 2: Workflow Fails with SSH Error

**Symptoms:**
- Workflow fails immediately
- Error message: "SSH connection failed" or "Authentication failed"

**Cause:**
- GitHub Secrets not configured correctly

**Solution:**
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Verify these secrets exist:
   - `VPS_HOST`: `92.118.45.135`
   - `VPS_USERNAME`: (your VPS username)
   - `VPS_PASSWORD`: (your VPS password)
   - `VPS_SSH_PORT`: `22` (or your custom port)
3. If missing, add them
4. Run workflow again

---

### Issue 3: MongoDB Connection Errors

**Symptoms:**
- Logs show "MongoDB connection FAILED"
- Error: "Authentication failed" or "Connection refused"

**Solution:**
1. Run Step 3: **Update VPS MongoDB Connection**
2. After it completes, run Step 2: **Restart MT5 Sync Service**
3. Run Step 1: **Verify LUCRUM Account Sync**

---

### Issue 4: Service Won't Start

**Symptoms:**
- Restart workflow shows "Service may not have started"
- No Python process found

**Cause:**
- Task Scheduler job not configured or corrupted

**Solution:**
1. RDP into VPS
2. Open Task Scheduler
3. Look for task named "MT5BridgeService"
4. If missing, you'll need to create it (see VPS Setup section below)
5. If exists, right-click → Run
6. Wait 2 minutes and run Step 1 (Verify)

---

## 🖥️ Manual VPS Verification (Alternative)

If workflows are not working, you can verify manually via SSH:

### Check if Sync Script is Running:
```powershell
Get-Process python | Where-Object {$_.Path -like "*mt5*"}
```

### Check MongoDB Connection:
```powershell
python -c "from pymongo import MongoClient; client = MongoClient('mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.y1p9be2.mongodb.net/fidus_production'); print(client.admin.command('ping'))"
```

### Check Account 2198 in MongoDB:
```powershell
python -c "from pymongo import MongoClient; db = MongoClient('mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.y1p9be2.mongodb.net/fidus_production').get_database(); print(db.mt5_account_config.find_one({'account': 2198}))"
```

### Test API Response:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/mt5/accounts/summary" | ConvertTo-Json
```

### Manually Start Sync Script:
```powershell
cd C:\mt5_bridge_service
python mt5_bridge_account_switching.py
```

---

## 📈 Expected Results After Successful Integration

### On VPS:
- MT5 sync script running (can see in Task Manager)
- LUCRUM MT5 terminal logged into account 2198
- API endpoint shows 14 total accounts (including 2198)

### In MongoDB:
```javascript
db.mt5_accounts.findOne({account: 2198})
// Shows: synced_from_vps: true, last_sync_timestamp: (recent)
```

### On Dashboard:
- Investment Committee: Total accounts = 12 (was 11)
- BALANCE Fund: Increases by ~$10,000
- Money Managers: Shows JOSE manager
- Account 2198 visible with real-time balance/equity

---

## 🔄 Recommended Workflow Sequence

### For First-Time Setup:
1. ✅ Run **Verify LUCRUM Account Sync** (Step 1)
2. ✅ Run **Restart MT5 Sync Service** (Step 2)
3. ✅ Wait 2 minutes
4. ✅ Run **Verify LUCRUM Account Sync** again (Step 1)
5. ✅ Check Investment Committee dashboard

### If Account 2198 Still Not Syncing:
1. ✅ Run **Update VPS MongoDB Connection** (Step 3)
2. ✅ Run **Restart MT5 Sync Service** (Step 2)
3. ✅ RDP into VPS and manually verify LUCRUM terminal is logged in
4. ✅ Wait 5 minutes
5. ✅ Run **Verify LUCRUM Account Sync** (Step 1)

---

## 📞 Support & Additional Resources

### Documentation Files:
- `/app/LUCRUM_INTEGRATION_COMPLETE.md` - Complete integration report
- `/app/LUCRUM_BROKER_INTEGRATION_GUIDE.md` - Integration guide
- `/app/SYSTEM_MASTER.md` - Platform documentation (updated)
- `/app/DATABASE_FIELD_STANDARDS.md` - Field standards (updated)

### VPS Access:
- **Host:** 92.118.45.135
- **Username:** trader
- **RDP:** Use Remote Desktop Connection

### MongoDB Access:
- **Connection String:** `mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.y1p9be2.mongodb.net/fidus_production`
- **Database:** fidus_production
- **Collections:** mt5_accounts, mt5_account_config

### Key Files on VPS:
- **Sync Script:** `C:\mt5_bridge_service\mt5_bridge_account_switching.py`
- **Logs:** `C:\mt5_bridge_service\logs\api_service.log`
- **MT5 Terminal:** Look for LUCRUM window in taskbar

---

## ✅ Success Checklist

After running workflows, verify these items:

- [ ] **Verify workflow** shows account 2198 in API response
- [ ] Account 2198 has real-time balance/equity (not $0)
- [ ] Total accounts in API = 14 (was 13)
- [ ] Investment Committee dashboard shows 12 accounts (was 11)
- [ ] BALANCE fund total increased by ~$10,000
- [ ] JOSE manager appears in Money Managers page
- [ ] MongoDB shows `synced_from_vps: true` for account 2198
- [ ] Sync logs mention account 2198 without errors

---

## 🎯 Quick Reference

| Workflow | When to Use | Expected Time |
|----------|-------------|---------------|
| **Verify LUCRUM Account Sync** | Check if 2198 is syncing | 2-3 min |
| **Restart MT5 Sync Service** | Start syncing 2198 | 3-5 min |
| **Update VPS MongoDB Connection** | Fix connection issues | 2-3 min |

---

## 🚨 Important Notes

1. **Do NOT run multiple workflows simultaneously** - Wait for one to complete before starting another
2. **LUCRUM Terminal Must Be Running** - The VPS must have the LUCRUM MT5 terminal open and logged in
3. **Wait Between Retries** - If sync doesn't work immediately, wait 5 minutes before retrying
4. **Check Logs** - Always review workflow output logs for specific error messages
5. **RDP Access May Be Needed** - Some issues require manual VPS access to resolve

---

## 📝 Workflow Execution Log Template

Use this to track your workflow executions:

```
Date: _______________
Time: _______________

□ Step 1: Verify LUCRUM Account Sync
  - Run Status: □ Success  □ Failed
  - Account 2198 Found: □ Yes  □ No
  - Notes: _________________________________

□ Step 2: Restart MT5 Sync Service  
  - Run Status: □ Success  □ Failed
  - Service Started: □ Yes  □ No
  - Account 2198 Syncing: □ Yes  □ No
  - Notes: _________________________________

□ Step 3: Update MongoDB Connection (if needed)
  - Run Status: □ Success  □ Failed
  - Connection Test: □ Pass  □ Fail
  - Notes: _________________________________

Final Result: □ LUCRUM Integration Complete  □ Needs Troubleshooting

Next Steps: _________________________________
```

---

**End of Guide**

For additional assistance, refer to the comprehensive integration report at `/app/LUCRUM_INTEGRATION_COMPLETE.md`
