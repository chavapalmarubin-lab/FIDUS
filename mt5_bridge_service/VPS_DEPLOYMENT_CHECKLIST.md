# VPS MT5 Bridge Service - Complete Deployment Checklist

## 🎯 OBJECTIVE
Set up automatic MT5 → MongoDB sync every 5 minutes using `mt5_bridge_service_dynamic.py`

---

## ✅ PRE-DEPLOYMENT CHECKLIST

### 1. Verify MongoDB Connection
```powershell
# Test MongoDB connection from VPS
$MONGODB_URI = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

# Using Python to test
python -c "from pymongo import MongoClient; client = MongoClient('$MONGODB_URI'); print('Connected:', client.admin.command('ping')); client.close()"
```

**Expected Output:**
```
Connected: {'ok': 1.0}
```

### 2. Verify MT5 Accounts in MongoDB
```powershell
# Check mt5_account_config collection
python -c "from pymongo import MongoClient; client = MongoClient('$MONGODB_URI'); db = client.fidus_production; count = db.mt5_account_config.count_documents({}); print(f'MT5 Configs: {count}'); client.close()"
```

**Expected Output:**
```
MT5 Configs: 7
```

### 3. Check MT5 Terminal
- ✅ MT5 Terminal is installed at: `C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe`
- ✅ MT5 Terminal can login to accounts manually
- ✅ "Algo Trading" is ENABLED in MT5 Tools → Options → Expert Advisors
- ✅ "Allow DLL imports" is CHECKED

---

## 📁 STEP 1: Create Service Directory

```powershell
# Create service directory
New-Item -ItemType Directory -Path "C:\mt5_bridge_service" -Force

# Navigate to directory
cd C:\mt5_bridge_service
```

---

## 📝 STEP 2: Create .env File

Create `C:\mt5_bridge_service\.env` with this content:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority

# MT5 Configuration
MT5_PATH=C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe
UPDATE_INTERVAL=300

# Master Password (if required)
MT5_MASTER_PASSWORD=
```

---

## 📥 STEP 3: Copy Service File

Copy `mt5_bridge_service_dynamic.py` to `C:\mt5_bridge_service\mt5_bridge_service_dynamic.py`

**File location in repo:** `/app/mt5_bridge_service/mt5_bridge_service_dynamic.py`

---

## 🔧 STEP 4: Install Dependencies

```powershell
# Install required packages
pip install MetaTrader5 pymongo python-dotenv

# Verify installations
pip list | Select-String -Pattern "MetaTrader5|pymongo|python-dotenv"
```

**Expected Output:**
```
MetaTrader5     5.0.4511
pymongo         4.10.1
python-dotenv   1.0.1
```

---

## 🧪 STEP 5: Test Service Manually (CRITICAL)

```powershell
cd C:\mt5_bridge_service

# Run service in test mode (will stop after 1 cycle)
python mt5_bridge_service_dynamic.py
```

**Expected Output:**
```
🚀 MT5 Bridge Service - Dynamic Configuration Mode Starting...
⏱️  Update interval: 300.0 seconds (5.0 minutes)
🔌 Connecting to MongoDB...
✅ MongoDB connected successfully
📥 Loading MT5 accounts from mt5_account_config collection...
✅ Loaded 7 active accounts from MongoDB:
   - 886557: Main Balance Account (BALANCE)
   - 886066: Secondary Balance Account (BALANCE)
   - 886602: Tertiary Balance Account (BALANCE)
   - 885822: Core Account (CORE)
   - 886528: Separation Account (SEPARATION)
   - 891215: Account 891215 - Interest Earnings Trading (SEPARATION)
   - 891234: Account 891234 - CORE Fund (CORE)
✅ MT5 Terminal initialized: v5.0.4511
✅ Service initialized successfully - starting sync loop
================================================================================
📊 SYNC CYCLE #1
🔄 Starting sync cycle at 2025-10-15 03:00:00
📊 Accounts to sync: 7
✅ Synced 886557: Balance=$80000.00, Equity=$84973.66, P&L=$4973.66
✅ Synced 886066: Balance=$10000.00, Equity=$10692.22, P&L=$692.22
✅ Synced 886602: Balance=$10000.00, Equity=$11136.10, P&L=$1136.10
✅ Synced 885822: Balance=$18151.41, Equity=$18038.47, P&L=$-112.94
✅ Synced 886528: Balance=$0.00, Equity=$0.00, P&L=$0.00
✅ Synced 891215: Balance=$9000.00, Equity=$9037.41, P&L=$37.41
✅ Synced 891234: Balance=$8000.00, Equity=$8000.00, P&L=$0.00
✅ Sync complete: 7 successful, 0 failed
⏳ Next sync in 300 seconds...
```

**If you see errors:**
- ❌ MongoDB connection error → Check .env file, verify MONGODB_URI
- ❌ MT5 login failed → Check passwords in mt5_account_config collection
- ❌ MT5 initialize failed → Check MT5_PATH, enable Algo Trading

Press `Ctrl+C` to stop after verifying first successful sync.

---

## 📅 STEP 6: Setup Windows Task Scheduler

### Create Scheduled Task:

```powershell
# Create scheduled task XML
$taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>MT5 Bridge Service - Syncs MT5 data to MongoDB every 5 minutes</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <UserId>$(whoami)</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT5M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions>
    <Exec>
      <Command>python</Command>
      <Arguments>C:\mt5_bridge_service\mt5_bridge_service_dynamic.py</Arguments>
      <WorkingDirectory>C:\mt5_bridge_service</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

# Save XML to file
$taskXml | Out-File -FilePath "C:\mt5_bridge_service\mt5_bridge_task.xml" -Encoding UTF8

# Import task
schtasks /create /tn "MT5BridgeService" /xml "C:\mt5_bridge_service\mt5_bridge_task.xml" /f
```

### Start the Task:

```powershell
schtasks /run /tn "MT5BridgeService"
```

### Verify Task is Running:

```powershell
schtasks /query /tn "MT5BridgeService" /v /fo list
```

---

## 🔍 STEP 7: Monitor Service (15 minutes)

### Check Log File:

```powershell
# Watch log file in real-time
Get-Content C:\mt5_bridge_service\mt5_bridge_dynamic.log -Tail 50 -Wait
```

### Verify MongoDB Updates:

After 5 minutes, check if data is syncing:

```powershell
# Check last update time
python -c "from pymongo import MongoClient; from datetime import datetime; client = MongoClient('$MONGODB_URI'); db = client.fidus_production; accounts = list(db.mt5_accounts.find()); print(f'Accounts in DB: {len(accounts)}'); for acc in accounts: print(f'{acc[\"account\"]}: Last sync: {acc.get(\"last_sync\")}'); client.close()"
```

**Expected Output:**
```
Accounts in DB: 7
886557: Last sync: 2025-10-15 03:05:23.456789+00:00
886066: Last sync: 2025-10-15 03:05:24.123456+00:00
...
```

### Wait for 3 Sync Cycles (15 minutes):

- Cycle 1: 03:00 ✅
- Cycle 2: 03:05 ✅  
- Cycle 3: 03:10 ✅

**SUCCESS CRITERIA:**
- ✅ All 7 accounts updated in MongoDB
- ✅ last_sync timestamp updates every 5 minutes
- ✅ No errors in log file
- ✅ Balance, equity, profit values are accurate

---

## 🎯 STEP 8: Verify Complete Data Flow

### 1. Check MongoDB (Source):

```powershell
python -c "from pymongo import MongoClient; client = MongoClient('$MONGODB_URI'); db = client.fidus_production; acc = db.mt5_accounts.find_one({'account': 886557}); print(f'Account 886557: Equity=${acc[\"equity\"]}, P&L=${acc[\"profit\"]}'); client.close()"
```

### 2. Check Backend API:

```bash
# From development machine
curl https://fidus-invest.emergent.host/api/mt5/admin/accounts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" | jq '.accounts[] | select(.mt5_login==886557) | {account, equity, profit}'
```

### 3. Check Frontend:

- Login to admin dashboard
- Navigate to "MT5 Accounts" page
- Verify all 7 accounts display
- Verify values match MongoDB

---

## 🚨 TROUBLESHOOTING

### Issue: MongoDB Connection Failed

**Error:** `bad auth : authentication failed`

**Solution:**
1. Verify MONGODB_URI in .env
2. Check MongoDB Atlas Network Access whitelist
3. Verify user permissions in MongoDB Atlas

### Issue: MT5 Login Failed

**Error:** `Login failed for [account]: (1, 'Unauthorized')`

**Solution:**
1. Verify password in mt5_account_config collection
2. Check if account is logged in elsewhere
3. Verify server name: "MEXAtlantic-Real"
4. Enable "Algo Trading" in MT5

### Issue: Service Stops After Running

**Check:**
```powershell
# Check task status
schtasks /query /tn "MT5BridgeService"

# Check if process is running
Get-Process python
```

**Restart:**
```powershell
schtasks /run /tn "MT5BridgeService"
```

---

## ✅ DEPLOYMENT COMPLETE CHECKLIST

Before declaring success:

- [ ] mt5_account_config collection has 7 accounts
- [ ] Service runs without errors for 30+ minutes
- [ ] mt5_accounts collection updates every 5 minutes
- [ ] All 7 accounts sync successfully
- [ ] last_sync timestamp is current (< 6 minutes old)
- [ ] Backend API returns correct data
- [ ] Frontend displays live data
- [ ] Task Scheduler shows task running
- [ ] Log file shows successful sync cycles

---

## 📞 SUPPORT

**If deployment fails:**
1. Share log file: `C:\mt5_bridge_service\mt5_bridge_dynamic.log`
2. Share error messages
3. Share output of verification commands

**Expected Service Uptime:** 24/7 with automatic restarts on failure
