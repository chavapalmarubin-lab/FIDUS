# MT4 File Monitor - Setup & Troubleshooting Guide

**Account:** 33200931 (Spain Equities CFD)
**Current Status:** Pending Real-Time Data
**Last Updated:** 2025-11-20

---

## Current Situation

✅ **What's Working:**
- MT4 EA compiled successfully (MT4_Python_Bridge_FileBased.mq4)
- EA shows "Data written" messages in MT4 Journal
- Account 33200931 exists in MongoDB database

❌ **What's NOT Working:**
- account_data.json file location unknown
- Python File Monitor not yet deployed to VPS
- No real-time data flowing to MongoDB

**Data Source:** MANUAL_ENTRY (needs to change to VPS_LIVE_MT4)

---

## Architecture Overview

```
MT4 Terminal → EA writes JSON → account_data.json → Python Monitor → MongoDB
                                      ↓
                        Auto-discovers file location
                        Updates every 30 seconds
```

---

## Step 1: Deploy Python File Monitor to VPS

### Option A: Using GitHub Actions (Recommended)

1. Go to your GitHub repository
2. Navigate to **Actions** tab
3. Find workflow: **"Deploy MT4 File Monitor Service"**
4. Click **"Run workflow"**
5. Wait for completion (approximately 2-3 minutes)

**This will:**
- Create `C:\mt4_bridge_service\mt4_file_monitor.py`
- Install required Python packages (pymongo, python-dotenv)
- Create Windows Task Scheduler job to auto-start service
- Start the service immediately

### Option B: Manual Deployment (If GitHub Actions fails)

Run this PowerShell script on your VPS:

```powershell
# Download the Python script
$serviceDir = "C:\mt4_bridge_service"
New-Item -ItemType Directory -Path $serviceDir -Force | Out-Null

# Copy from repository or use curl to download
# The file mt4_file_monitor.py should be deployed

# Install dependencies
pip install pymongo python-dotenv

# Create .env file with MongoDB connection
$envContent = "MONGO_URL=<your_mongodb_url>"
[System.IO.File]::WriteAllText("$serviceDir\.env", $envContent)

# Test run
cd $serviceDir
python mt4_file_monitor.py
```

---

## Step 2: Verify EA is Writing File

### On Your VPS:

1. **Open MT4 Terminal**
2. **Check Journal Tab:**
   - Look for messages: "MT4 File-Based Bridge initialized"
   - Look for messages: "Account data written - Balance: X"

3. **Search for account_data.json:**

Run this PowerShell command to find the file:

```powershell
Get-ChildItem -Path "C:\" -Recurse -Filter "account_data.json" -ErrorAction SilentlyContinue | 
    Select-Object FullName, Length, LastWriteTime
```

**Common Locations:**
- `C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\account_data.json`
- `C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\<ID>\Files\account_data.json`
- `C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Files\account_data.json`

4. **View the file content:**

```powershell
$file = "C:\path\to\account_data.json"
Get-Content $file | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Expected Content:**
```json
{
  "account": 33200931,
  "name": "Your Name",
  "server": "MEXAtlantic-Real",
  "balance": 10000.00,
  "equity": 10000.00,
  "margin": 0.00,
  "free_margin": 10000.00,
  "profit": 0.00,
  "currency": "USD",
  "leverage": 100,
  "credit": 0.00,
  "platform": "MT4",
  "timestamp": "2025.11.20 20:00:00"
}
```

---

## Step 3: Verify Python Service is Running

### Check Task Scheduler:

```powershell
Get-ScheduledTask -TaskName "MT4 File Monitor" | Select State, LastRunTime, NextRunTime
```

**Expected Output:**
```
State   LastRunTime          NextRunTime
-----   -----------          -----------
Running 11/20/2025 8:00:00 PM
```

### Check Service Logs Manually:

```powershell
cd C:\mt4_bridge_service
python mt4_file_monitor.py
```

**Expected Output:**
```
======================================================================
MT4 FILE MONITOR SERVICE
======================================================================
Account: MT4_33200931
MongoDB: mongodb://...
======================================================================
🔍 Searching for account_data.json...
   Checking: C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files
✅ Found: C:\Users\...\account_data.json
✅ Connected to MongoDB
🚀 Service started. Monitoring: C:\Users\...\account_data.json
📊 Poll interval: 30 seconds

📄 File updated: 2025-11-20 20:15:30
📄 Read data from file: Balance=$10000.0
✅ Updated: Balance=$10000.00, Equity=$10000.00
```

### If Service Shows Errors:

**Error: "account_data.json not found"**
- EA might not be writing the file yet
- Check MT4 Journal for "Data written" messages
- Verify EA is attached to a chart and running

**Error: "MongoDB connection error"**
- Check .env file has correct MONGO_URL
- Verify MongoDB Atlas IP whitelist includes VPS IP
- Test connection: `python -c "from pymongo import MongoClient; print(MongoClient('your_url').admin.command('ping'))"`

**Error: "Invalid JSON"**
- File might be partially written (race condition)
- Service will retry automatically
- Check file content for corruption

---

## Step 4: Verify Data in MongoDB

### From Your Development Machine:

Run this command to check if MT4 data is flowing:

```bash
curl -X GET "http://localhost:8001/api/mt5/accounts/33200931" \
  -H "Authorization: Bearer <admin_token>"
```

Or run this Python script:

```python
from pymongo import MongoClient
import os

mongo_url = os.getenv('MONGO_URL')
client = MongoClient(mongo_url)
db = client.get_database()

account = db.mt5_accounts.find_one({"account": 33200931})

print(f"Balance: ${account['balance']:,.2f}")
print(f"Equity: ${account['equity']:,.2f}")
print(f"Data Source: {account['data_source']}")
print(f"Last Update: {account['updated_at']}")
print(f"Synced from VPS: {account['synced_from_vps']}")
```

**Success Indicators:**
- ✅ `data_source`: Changes from "MANUAL_ENTRY" to "MT4_FILE_MONITOR"
- ✅ `synced_from_vps`: Changes from `false` to `true`
- ✅ `updated_at`: Updates every 5 minutes (EA update interval)
- ✅ `last_sync_timestamp`: Shows recent timestamp
- ✅ `status`: Changes from "pending_real_time_data" to "active"

---

## Step 5: Update Account Status

Once real-time data is flowing, update the account status:

```python
from pymongo import MongoClient
from datetime import datetime, timezone

mongo_url = "your_mongodb_url"
client = MongoClient(mongo_url)
db = client.get_database()

db.mt5_accounts.update_one(
    {"account": 33200931},
    {"$set": {
        "status": "active",
        "connection_status": "connected",
        "integration_status": "integrated",
        "updated_at": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    }}
)

print("✅ Account 33200931 marked as active with real-time data")
```

---

## Troubleshooting Common Issues

### Issue 1: EA Not Writing File

**Symptoms:**
- No "Data written" messages in MT4 Journal
- No account_data.json file found

**Solutions:**
1. Verify EA is attached to a chart (should show smiley face icon)
2. Check MT4 allows Expert Advisors: Tools → Options → Expert Advisors → Enable
3. Check EA settings: Right-click chart → Expert Advisors → Properties
4. Restart MT4 terminal
5. Check MT4 Journal for error messages

### Issue 2: Python Service Not Finding File

**Symptoms:**
- Service shows "account_data.json not found"
- Keeps retrying search

**Solutions:**
1. Find file manually using PowerShell (see Step 2)
2. Verify file is being updated (check LastWriteTime)
3. Check file permissions (service needs read access)
4. Add file path to search_paths in mt4_file_monitor.py if in non-standard location

### Issue 3: Data Not Updating in MongoDB

**Symptoms:**
- File exists and updates
- Service shows "File updated"
- But MongoDB shows old data

**Solutions:**
1. Check MongoDB connection in service logs
2. Verify account ID matches: "MT4_33200931"
3. Check MongoDB Atlas IP whitelist
4. Verify .env file has correct MONGO_URL
5. Check for errors in service output

### Issue 4: Service Keeps Crashing

**Symptoms:**
- Task shows "Running" but no output
- Service stops after a while

**Solutions:**
1. Check Task Scheduler Last Run Result (should be 0 for success)
2. Run service manually to see error messages
3. Check Windows Event Viewer for Python errors
4. Verify all dependencies installed: `pip list | grep -E "pymongo|python-dotenv"`
5. Check if MongoDB connection is stable

---

## Testing Checklist

Use this checklist to verify everything is working:

### EA (MT4 Terminal)
- [ ] EA compiled successfully (0 errors)
- [ ] EA attached to chart (smiley face icon visible)
- [ ] MT4 Journal shows "MT4 File-Based Bridge initialized"
- [ ] MT4 Journal shows "Account data written" every 5 minutes
- [ ] account_data.json file exists and updates every 5 minutes

### Python Service
- [ ] Service deployed to C:\mt4_bridge_service
- [ ] Dependencies installed (pymongo, python-dotenv)
- [ ] .env file has correct MONGO_URL
- [ ] Task Scheduler shows service running
- [ ] Service finds account_data.json file
- [ ] Service connects to MongoDB
- [ ] Service shows "File updated" messages every 30 seconds (when file changes)

### MongoDB
- [ ] Account 33200931 exists in mt5_accounts collection
- [ ] data_source changed from "MANUAL_ENTRY" to "MT4_FILE_MONITOR"
- [ ] updated_at timestamp updates every 5 minutes
- [ ] Balance and Equity values update correctly
- [ ] status changed from "pending_real_time_data" to "active"

### Investment Committee UI
- [ ] Account 33200931 appears in dashboard
- [ ] Shows "Spain Equities CFD" manager name
- [ ] Displays current balance: ~$10,000
- [ ] Status shows "Active" (green)
- [ ] Last update timestamp is recent (< 10 minutes)

---

## Quick Start Commands

### Deploy Everything (Run on VPS):

```powershell
# 1. Navigate to service directory
cd C:\mt4_bridge_service

# 2. Run service manually first to test
python mt4_file_monitor.py

# If successful, press Ctrl+C and start as scheduled task:

# 3. Start scheduled task
Start-ScheduledTask -TaskName "MT4 File Monitor"

# 4. Verify it's running
Get-ScheduledTask -TaskName "MT4 File Monitor" | Select State
```

### Monitor Service (Run on VPS):

```powershell
# Check if service is running
Get-Process python | Where-Object {$_.Path -like "*mt4_file_monitor*"}

# View recent Task Scheduler history
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'; ID=200} -MaxEvents 5

# Test MongoDB connection
python -c "from pymongo import MongoClient; print(MongoClient('your_url').admin.command('ping'))"
```

---

## Success Criteria

The MT4 File Monitor is fully operational when:

✅ EA writes account_data.json every 5 minutes
✅ Python service finds and reads the file
✅ MongoDB receives updates every 5 minutes
✅ Account status changes to "active"
✅ Investment Committee shows real-time balance

**Expected Timeline:**
- Setup: 5-10 minutes
- First data point: Within 5 minutes of EA starting
- Full integration: Within 15 minutes

---

## Support

If issues persist after following this guide:

1. Capture EA screenshot showing "Data written" messages
2. Run PowerShell command to find account_data.json and share path
3. Run Python service manually and share full output
4. Check MongoDB account document and share relevant fields
5. Share any error messages from MT4 Journal, Task Scheduler, or Python output

---

**Last Updated:** 2025-11-20
**Status:** Deployment guide created, awaiting VPS execution
