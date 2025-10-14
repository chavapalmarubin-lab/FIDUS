# MT5 Bridge Service - Dynamic Configuration Deployment Guide

## 📋 Overview

This guide will help you deploy the **dynamic configuration version** of the MT5 Bridge Service to your VPS. This version loads MT5 accounts from the MongoDB `mt5_account_config` collection instead of hardcoded values.

## ✅ Prerequisites

**Current VPS Setup (Already Configured):**
- ✅ Python 3.12 installed
- ✅ MT5 Terminal installed at: `C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe`
- ✅ Service directory: `C:\mt5_bridge_service\`
- ✅ `.env` file configured with MongoDB URI
- ✅ Production script (`mt5_bridge_service_production.py`) working perfectly
- ✅ Task Scheduler configured to run service every 5 minutes

## 🔧 What Changed?

**Dynamic Script vs Production Script:**

| Feature | Production Script | Dynamic Script |
|---------|------------------|----------------|
| Account Source | Hardcoded in script | MongoDB `mt5_account_config` |
| Adding Accounts | Edit script + restart service | Add via admin dashboard |
| Removing Accounts | Edit script + restart service | Deactivate via admin dashboard |
| Password Changes | Edit script + restart service | Update via admin dashboard |
| Fallback | N/A | Uses hardcoded accounts if MongoDB fails |
| Pymongo 4.x Fix | N/A | ✅ Fixed "truth value testing" error |

## 📥 Deployment Steps

### Step 1: Download the New Script

Copy the new `mt5_bridge_service_dynamic.py` file to your VPS at:
```
C:\mt5_bridge_service\mt5_bridge_service_dynamic.py
```

**How to transfer the file:**
1. **Option A (Recommended):** Use Remote Desktop and copy/paste the file
2. **Option B:** Upload to Google Drive, download on VPS
3. **Option C:** Use SFTP/WinSCP to transfer the file

### Step 2: Verify Prerequisites

Open PowerShell on the VPS and verify:

```powershell
# Check Python version
python --version
# Should show: Python 3.12.x

# Check pymongo is installed
pip show pymongo
# Should show pymongo version 4.x

# Verify .env file exists
Test-Path C:\mt5_bridge_service\.env
# Should return: True

# Check .env content has MongoDB URI
Get-Content C:\mt5_bridge_service\.env
# Should show MONGODB_URI=mongodb+srv://...
```

### Step 3: Test the Dynamic Script (Manual Run)

**IMPORTANT:** Don't stop the production script yet! Test the dynamic script first.

```powershell
cd C:\mt5_bridge_service
python mt5_bridge_service_dynamic.py
```

**Expected Output:**
```
🚀 MT5 Bridge Service - Dynamic Configuration Mode Starting...
⏱️  Update interval: 300 seconds (5.0 minutes)
🔌 Connecting to MongoDB...
✅ MongoDB connected successfully
📥 Loading MT5 accounts from mt5_account_config collection...
✅ Loaded 7 active accounts from MongoDB:
   - 886557: Main Balance Account (BALANCE)
   - 886066: Secondary Balance Account (BALANCE)
   - 886602: Tertiary Balance Account (BALANCE)
   - 885822: Core Account (CORE)
   - 886528: Separation Account (SEPARATION)
   - 888520: Profit Share Account (BALANCE)
   - 888521: Growth Balance Account (BALANCE)
✅ MT5 Terminal initialized: v5.0.xxxx
✅ Service initialized successfully - starting sync loop
```

**If you see "⚠️ Using fallback accounts":** The dynamic loading failed, but the script will still work with hardcoded accounts (same as production).

**Stop the test** by pressing `Ctrl+C` after you see successful syncing.

### Step 4: Verify MongoDB Account Loading

Let's verify the dynamic script is actually reading from MongoDB:

1. **Add a test account** via the admin dashboard:
   - Login to FIDUS admin dashboard
   - Go to "⚙️ MT5 Config" tab
   - Click "Add Account"
   - Add test account: `999888` (any number not already in use)
   - Set password: `Fidus13@`
   - Name: "Test Dynamic Loading"
   - Fund Type: BALANCE
   - Target Amount: 5000

2. **Run the dynamic script again:**
   ```powershell
   python mt5_bridge_service_dynamic.py
   ```

3. **Verify** the log shows **8 accounts** (7 original + 1 test):
   ```
   ✅ Loaded 8 active accounts from MongoDB:
   ...
   - 999888: Test Dynamic Loading (BALANCE)
   ```

4. **Success!** If you see 8 accounts, the dynamic loading is working! Press `Ctrl+C` to stop.

5. **Cleanup:** Deactivate or delete the test account via the admin dashboard.

### Step 5: Update Task Scheduler (Switch to Dynamic)

**Only do this after confirming Step 4 works!**

1. Open **Task Scheduler** (search in Windows Start menu)

2. Find the existing task: **"MT5 Bridge Service"** or **"MT5_Sync_Service"**

3. **Don't delete the old task** - we'll modify it:
   - Right-click the task → **Properties**
   - Go to the **Actions** tab
   - **Edit** the existing action

4. **Change the script name:**
   - Old: `C:\mt5_bridge_service\mt5_bridge_service_production.py`
   - New: `C:\mt5_bridge_service\mt5_bridge_service_dynamic.py`

5. **Save** the task

6. **Test** the task:
   - Right-click the task → **Run**
   - Check the log file: `C:\mt5_bridge_service\mt5_bridge_dynamic.log`
   - Should see successful sync messages

### Step 6: Monitor the Service

After switching to the dynamic script, monitor for 1-2 sync cycles (10-20 minutes):

```powershell
# View live log (updates automatically)
Get-Content C:\mt5_bridge_service\mt5_bridge_dynamic.log -Wait -Tail 50
```

**What to look for:**
- ✅ "Loaded X active accounts from MongoDB" (not "using fallback")
- ✅ Successful sync messages for all accounts
- ✅ No pymongo errors or "truth value testing" errors

## 🔄 Rollback Plan (If Something Goes Wrong)

If the dynamic script has issues, you can instantly rollback:

1. Open **Task Scheduler**
2. Edit the task
3. Change script back to: `mt5_bridge_service_production.py`
4. Save

The production script will continue working as before! ✅

## 🎯 Key Differences - Dynamic vs Production

### Production Script (Current):
```python
# Hardcoded in the script
MT5_ACCOUNTS = [
    {"account": 886557, "password": "Fidus13@", ...},
    {"account": 886066, "password": "Fidus13@", ...},
    ...
]
```

**To add an account:** Edit the script file → Restart service

### Dynamic Script (New):
```python
# Loaded from MongoDB
accounts = db.mt5_account_config.find({"is_active": True})
```

**To add an account:** Add via admin dashboard → Wait 50 minutes (automatic)

## ❓ Troubleshooting

### Issue: "Using fallback accounts" message

**Cause:** MongoDB connection failed or no active accounts found

**Fix:**
1. Check `.env` file has correct `MONGODB_URI`
2. Verify MongoDB Atlas allows connections from VPS IP
3. Test MongoDB connection:
   ```powershell
   python -c "from pymongo import MongoClient; client = MongoClient('YOUR_MONGODB_URI'); print(client.admin.command('ping'))"
   ```

### Issue: "Database objects do not implement truth value testing"

**Fix:** This is already fixed in the new dynamic script! It uses `if self.db is not None:` instead of `if self.db:`

### Issue: Script crashes with pymongo error

**Check pymongo version:**
```powershell
pip show pymongo
```

**If version is 3.x, upgrade to 4.x:**
```powershell
pip install --upgrade pymongo
```

### Issue: Accounts not syncing after adding via dashboard

**Expected behavior:** New accounts take up to 50 minutes to start syncing

**Why?** The script reloads accounts from MongoDB at the start of each sync cycle (every 5 minutes), but there may be a delay before the next scheduled run.

**To force immediate sync:** Manually run the script once:
```powershell
python C:\mt5_bridge_service\mt5_bridge_service_dynamic.py
# Press Ctrl+C after one sync cycle
```

## 📊 Monitoring & Maintenance

### View Recent Logs
```powershell
Get-Content C:\mt5_bridge_service\mt5_bridge_dynamic.log -Tail 100
```

### Check Task Scheduler History
1. Open Task Scheduler
2. Right-click task → Properties
3. History tab → View recent runs

### MongoDB Health Check
```powershell
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv('C:\\mt5_bridge_service\\.env'); client = MongoClient(os.getenv('MONGODB_URI')); db = client.get_database(); print(f'Active accounts: {db.mt5_account_config.count_documents({\"is_active\": True})}')"
```

## ✅ Success Criteria

After deployment, you should see:

1. ✅ Task Scheduler shows task running successfully
2. ✅ Log file shows: "Loaded X active accounts from MongoDB"
3. ✅ MongoDB `mt5_accounts` collection updates every 5 minutes
4. ✅ Admin dashboard displays current account data
5. ✅ No "fallback accounts" warnings in logs
6. ✅ No pymongo errors in logs

## 📞 Support

If you encounter issues:

1. **Check the logs first:** `C:\mt5_bridge_service\mt5_bridge_dynamic.log`
2. **Verify MongoDB connection:** Test with the MongoDB health check command above
3. **Rollback if needed:** Switch Task Scheduler back to production script
4. **Keep production script as backup:** Don't delete `mt5_bridge_service_production.py`

## 🎉 Benefits of Dynamic Configuration

Once deployed, you can:

- ✅ Add new MT5 accounts via admin dashboard (no VPS access needed)
- ✅ Update account details (name, fund type, target amount) via dashboard
- ✅ Deactivate accounts without deleting data
- ✅ Change passwords via dashboard
- ✅ All changes sync automatically within 50 minutes
- ✅ No manual script editing required
- ✅ Full audit trail (created_by, last_modified_by, timestamps)

---

**Deployment Completed By:** _____________  
**Date:** _____________  
**Version:** Dynamic Configuration v1.0  
**Status:** ☐ Testing ☐ Production
