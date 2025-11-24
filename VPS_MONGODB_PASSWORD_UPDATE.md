# VPS Bridge Scripts - MongoDB Password Update Guide
**Date:** November 24, 2025  
**Status:** 🔴 CRITICAL - Requires VPS Update

---

## 🔒 New MongoDB Credentials

**Username:** `chavapalmarubin_db_user`  
**New Password:** `***SANITIZED***`  
**Connection String:**
```
mongodb+srv://chavapalmarubin_db_user:***SANITIZED***.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority
```

**Note:** The `@` symbol in the password must be URL-encoded as `%40` in the connection string.

---

## 📋 VPS Update Instructions

You need to update the MongoDB connection string in **3 bridge scripts** on your VPS at `217.197.163.11`:

### Script Locations
```
C:\mt5_bridge_service\mt5_bridge_mexatlantic.py
C:\mt5_bridge_service\mt5_bridge_lucrum.py
C:\mt5_bridge_service\mt4_bridge_mexatlantic.py
```

---

## 🔧 Step-by-Step Update Process

### Step 1: RDP into VPS
```
IP: 217.197.163.11
Username: Administrator
```

### Step 2: Stop All Bridge Services

Open PowerShell as Administrator and run:
```powershell
# Stop all bridge scheduled tasks
Stop-ScheduledTask -TaskName "MEXAtlanticBridge"
Stop-ScheduledTask -TaskName "LucrumBridge"
Stop-ScheduledTask -TaskName "MT4Bridge"

# Verify they're stopped
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Bridge"} | Format-Table TaskName, State
```

### Step 3: Update Each Bridge Script

For **EACH** of the 3 files, find this line:
```python
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:OLD_PASSWORD@fidus.y1p9be2.mongodb.net/fidus_production"
```

Replace with:
```python
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:***SANITIZED***.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"
```

**Files to update:**

#### 1. MEXAtlantic MT5 Bridge
**File:** `C:\mt5_bridge_service\mt5_bridge_mexatlantic.py`

Find and replace the MONGO_URL line (typically near the top of the file).

#### 2. Lucrum MT5 Bridge
**File:** `C:\mt5_bridge_service\mt5_bridge_lucrum.py`

Find and replace the MONGO_URL line.

#### 3. MEXAtlantic MT4 Bridge
**File:** `C:\mt5_bridge_service\mt4_bridge_mexatlantic.py`

Find and replace the MONGO_URL line.

### Step 4: Test Connection (Optional but Recommended)

Before restarting services, test the connection:
```powershell
cd C:\mt5_bridge_service

# Test one of the scripts
python mt5_bridge_mexatlantic.py
```

You should see:
```
✅ MongoDB connected successfully
```

Press `Ctrl+C` to stop the test.

### Step 5: Restart All Bridge Services

```powershell
# Start all bridge scheduled tasks
Start-ScheduledTask -TaskName "MEXAtlanticBridge"
Start-ScheduledTask -TaskName "LucrumBridge"
Start-ScheduledTask -TaskName "MT4Bridge"

# Verify they're running
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Bridge"} | Format-Table TaskName, State
```

### Step 6: Verify Logs

Check the log files to ensure successful connection:
```powershell
# Check last 20 lines of each log
Get-Content C:\mt5_bridge_service\logs\mexatlantic.log -Tail 20
Get-Content C:\mt5_bridge_service\logs\lucrum.log -Tail 20
Get-Content C:\mt5_bridge_service\logs\mt4_mexatlantic.log -Tail 20
```

Look for:
```
✅ MongoDB connected successfully
✅ Syncing 13 accounts (MEXAtlantic)
✅ Syncing 1 account (Lucrum)
✅ Syncing 1 account (MT4)
```

---

## ✅ Verification Checklist

After updating:

- [ ] All 3 bridge scripts updated with new password
- [ ] All 3 scheduled tasks restarted
- [ ] All 3 log files show successful MongoDB connection
- [ ] No authentication errors in logs
- [ ] Lucrum bridge alert cleared in monitoring dashboard

---

## 🚨 If You Encounter Issues

### Authentication Error
```
pymongo.errors.OperationFailure: bad auth : authentication failed
```

**Solutions:**
1. Double-check password is exactly: `***SANITIZED***`
2. Ensure `@` is encoded as `%40` in connection string
3. Verify username is: `chavapalmarubin_db_user`
4. Wait 1-2 minutes after changing password in MongoDB Atlas

### Connection Timeout
```
ServerSelectionTimeoutError
```

**Solutions:**
1. Check internet connection on VPS
2. Verify firewall allows MongoDB Atlas connections
3. Test connection: `ping fidus.y1p9be2.mongodb.net`

### Script Won't Start
```powershell
# Check Python path
where python

# Test script manually
cd C:\mt5_bridge_service
python mt5_bridge_mexatlantic.py
```

---

## 📞 Need Help?

If you encounter any issues:
1. Check logs in `C:\mt5_bridge_service\logs\`
2. Test connection manually with one script
3. Verify MongoDB Atlas shows the password was changed
4. Contact Emergent support if needed

---

## 🔐 Security Notes

- ✅ Password changed in MongoDB Atlas
- ✅ Backend .env updated and tested
- ✅ Backend service restarted successfully
- ⏳ VPS scripts need manual update (this document)
- ⏳ Render environment variables need update
- ⏳ GitHub workflow files need cleanup

---

**Status:** Backend secured ✅ | VPS update pending ⏳
