# MT4 Bridge Deployment Guide

## ✅ Current Status

- **Python Version**: 3.12 installed on VPS ✓
- **Empty Folder**: C:\mt4_bridge_service created ✓
- **GitHub Workflow**: Ready to populate folder

## 🚀 DEPLOYMENT STEPS

### Step 1: Run GitHub Workflow

1. Go to GitHub → Actions tab
2. Select "Deploy MT4 Bridge Complete with DLLs"
3. Click "Run workflow"
4. Select action: **deploy_all**
5. Click green "Run workflow" button

**This will create:**
- C:\mt4_bridge_service\logs\
- C:\mt4_bridge_service\mt4_bridge_api_service.py
- C:\mt4_bridge_service\start_mt4_bridge.bat
- C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Experts\MT4_Python_Bridge.mq4
- C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Include\Zmq\*.mqh
- C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Libraries\*.dll

### Step 2: Verify Files Created

After workflow completes, RDP to VPS and check:

```powershell
# Check service folder
dir C:\mt4_bridge_service

# Check MT4 EA
dir "C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Experts\MT4_Python_Bridge.mq4"

# Check ZeroMQ library
dir "C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Include\Zmq\"

# Check DLLs
dir "C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Libraries\*.dll"
```

### Step 3: Compile MT4 Expert Advisor

1. Open MT4 Terminal on VPS
2. Press **F4** (opens MetaEditor)
3. In Navigator panel, expand "Experts"
4. Find and open "MT4_Python_Bridge.mq4"
5. Press **F7** to compile
6. Check "Errors" tab at bottom - should show "0 error(s)"
7. Close MetaEditor

### Step 4: Attach EA to Chart

1. In MT4 Terminal, open any chart (e.g., EURUSD)
2. In Navigator panel, find "MT4_Python_Bridge" under Expert Advisors
3. Drag and drop it onto the chart
4. In the dialog that appears:
   - ✓ Check "Allow DLL imports"
   - ✓ Check "Allow live trading" (if needed)
   - Click "OK"
5. You should see a smiley face icon in top-right of chart

### Step 5: Start Python Service

**Option A: Manual Start (for testing)**
```
Double-click: C:\mt4_bridge_service\start_mt4_bridge.bat
```

**Option B: Start from Command Line**
```powershell
cd C:\mt4_bridge_service
python mt4_bridge_api_service.py
```

### Step 6: Verify Data Flow

#### Check Python Service Logs
```powershell
# View log file
notepad C:\mt4_bridge_service\logs\mt4_bridge.log
```

**Expected log entries:**
```
MT4 BRIDGE SERVICE STARTING
Connecting to MongoDB...
MongoDB connected successfully
Setting up ZeroMQ...
ZeroMQ server bound to tcp://localhost:32768
MT4 Bridge Service running...
Waiting for data from MT4...
```

#### Check MT4 Experts Tab

In MT4 Terminal:
1. Click "Experts" tab at bottom
2. Look for messages like:
   - "MT4 Bridge initialized, connecting to tcp://localhost:32768"
   - "Account data sent - Balance: XXXX, Equity: YYYY"

#### Check MongoDB

1. Open MongoDB Compass
2. Connect to: `mongodb+srv://emergent-ops:***SANITIZED***@fidus.ylp9be2.mongodb.net/`
3. Navigate to `fidus_production` → `mt5_accounts`
4. Look for document with `_id: "MT4_33200931"`

**Expected document structure:**
```json
{
  "_id": "MT4_33200931",
  "account": 33200931,
  "name": "Money Manager MT4 Account",
  "server": "MEXAtlantic-Real",
  "balance": 0.00,
  "equity": 0.00,
  "margin": 0.00,
  "free_margin": 0.00,
  "profit": 0.00,
  "currency": "USD",
  "leverage": 100,
  "credit": 0.00,
  "fund_type": "MONEY_MANAGER",
  "platform": "MT4",
  "updated_at": "2025-11-19T..."
}
```

---

## 🔧 TROUBLESHOOTING

### Issue 1: "Python service file missing"

**Cause:** Workflow hasn't run yet or failed

**Solution:**
1. Run the GitHub workflow "Deploy MT4 Bridge Complete with DLLs"
2. Select action: "deploy_all"
3. Wait for completion
4. Check VPS folder: `C:\mt4_bridge_service\`

### Issue 2: MT4 EA compilation errors

**Common errors:**
- `'Zmq.mqh' - cannot open the file`
  - **Solution:** Run workflow with action "install_zeromq_complete"
  
- `DLL function call not allowed`
  - **Solution:** Enable "Allow DLL imports" when attaching EA

### Issue 3: Python service can't connect to MongoDB

**Error:** `MongoDB connection failed`

**Solutions:**
1. Check internet connectivity on VPS
2. Verify MongoDB URI in python file
3. Test connection:
   ```python
   python -c "import pymongo; c=pymongo.MongoClient('mongodb+srv://...'); c.admin.command('ping'); print('OK')"
   ```

### Issue 4: ZeroMQ connection failed

**Error:** `ZeroMQ setup failed: Address already in use`

**Solutions:**
1. Check if port 32768 is already in use:
   ```powershell
   netstat -ano | findstr :32768
   ```
2. If in use, kill the process:
   ```powershell
   taskkill /PID <PID> /F
   ```
3. Restart Python service

### Issue 5: No data flowing from MT4 to Python

**Checklist:**
- [ ] MT4 EA attached to chart (check for smiley face icon)
- [ ] EA shows "connected" in Experts tab
- [ ] Python service is running (check Task Manager)
- [ ] Python service log shows "ZeroMQ server bound"
- [ ] No firewall blocking localhost connections

**Debug commands:**
```powershell
# Check if Python service is running
tasklist | findstr python

# Check if port is listening
netstat -ano | findstr :32768

# Test ZeroMQ manually
python -c "import zmq; ctx=zmq.Context(); s=ctx.socket(zmq.PULL); s.bind('tcp://localhost:32768'); print('OK')"
```

---

## 📋 VERIFICATION CHECKLIST

After deployment, verify these items:

### Files Created
- [ ] C:\mt4_bridge_service\logs\ (folder)
- [ ] C:\mt4_bridge_service\mt4_bridge_api_service.py
- [ ] C:\mt4_bridge_service\start_mt4_bridge.bat
- [ ] C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Experts\MT4_Python_Bridge.mq4
- [ ] C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Include\Zmq\Zmq.mqh
- [ ] C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Libraries\*.dll

### Services Running
- [ ] Python service running in Task Manager
- [ ] MT4 EA attached to chart with smiley face
- [ ] No errors in Python log file
- [ ] MT4 Experts tab shows "Account data sent"

### Data Flow
- [ ] MongoDB document created with _id "MT4_33200931"
- [ ] Document has platform = "MT4"
- [ ] Document has fund_type = "MONEY_MANAGER"
- [ ] All fields use snake_case (free_margin, not freeMargin)
- [ ] Document updates every 5 minutes

---

## 🎯 SUCCESS CRITERIA

✅ **Deployment is successful when:**
1. All files created on VPS
2. MT4 EA compiles without errors
3. Python service connects to MongoDB
4. ZeroMQ socket binds successfully
5. MT4 EA sends data every 5 minutes
6. Python service receives and saves data
7. MongoDB document appears and updates
8. All field names are snake_case
9. No errors in logs

---

## 📞 NEXT STEPS AFTER SUCCESS

Once MT4 bridge is working:

1. **Verify in FIDUS Dashboard**
   - Login to FIDUS admin panel
   - Check if MT4 account 33200931 appears
   - Verify balance/equity values match MT4

2. **Monitor for 24 Hours**
   - Check logs daily
   - Verify continuous data updates
   - Monitor MongoDB document timestamps

3. **Move to Priority 2 Tasks**
   - Fix Investment Committee UI bugs
   - Fix referral agent logins

---

## 🔑 KEY INFORMATION

**MT4 Account Details:**
- Account: 33200931
- Server: MEXAtlantic-Real
- Fund Type: MONEY_MANAGER
- Platform: MT4

**MongoDB Details:**
- Database: fidus_production
- Collection: mt5_accounts
- Document ID: MT4_33200931

**ZeroMQ Configuration:**
- Protocol: tcp
- Host: localhost
- Port: 32768
- Socket Type: PULL (Python) / PUSH (MT4)

**Update Interval:**
- 300 seconds (5 minutes)

---

**Created:** 2025-11-19  
**Status:** Ready for deployment  
**Priority:** P0 (Critical)
