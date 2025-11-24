# MT4 Account Integration Guide - Account 33200931

**Date:** November 24, 2025  
**Account:** 33200931  
**Platform:** MT4  
**Server:** MEXAtlantic-Real  
**Status:** Ready to deploy  

---

## 📋 What This Does:

Integrates MT4 account 33200931 into your FIDUS platform using a file-based bridge:

```
MT4 Terminal (33200931)
    ↓
MT4 Expert Advisor (writes JSON every 120s)
    ↓
account_33200931_data.json
    ↓
Python Bridge (reads JSON, updates MongoDB)
    ↓
MongoDB (mt5_accounts collection)
    ↓
FIDUS Dashboard
```

---

## 🚀 Deployment Steps:

### **Step 1: Install MT4 Expert Advisor**

**1.1 Copy EA File:**
- File: `MT4_Account_Data_Writer.mq4`
- Copy to: `C:\Program Files (x86)\MEX Atlantic MT4 Terminal\MQL4\Experts\`

**1.2 Compile EA:**
1. Open MT4 Terminal
2. Press `F4` or click Tools → MetaEditor
3. In MetaEditor, click File → Open
4. Navigate to: `Experts\MT4_Account_Data_Writer.mq4`
5. Click "Compile" button (or press F7)
6. Check for "0 errors" in bottom panel
7. Close MetaEditor

**1.3 Attach EA to Chart:**
1. In MT4, open any chart (e.g., EURUSD M1)
2. In Navigator panel (Ctrl+N), expand "Expert Advisors"
3. Find "MT4_Account_Data_Writer"
4. Drag it onto the chart
5. In settings dialog:
   - Inputs tab: Verify `SyncIntervalSeconds = 120`
   - Common tab: Check "Allow DLL imports" ✅
   - Common tab: Check "Allow live trading" ✅
6. Click OK
7. Look for smiley face icon in top-right corner ☺

**Verification:**
```
// Check MT4 terminal "Experts" tab for:
MT4 Account Data Writer EA Started
Account: 33200931
Server: MEXAtlantic-Real
Data File: account_33200931_data.json
Sync Interval: 120 seconds
Data written: Balance=XXXXX.XX, Equity=XXXXX.XX, Positions=X, Orders=X
```

---

### **Step 2: Verify Data File Created**

**Check file exists:**
```powershell
Get-Item "C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\account_33200931_data.json"
```

**View file contents:**
```powershell
Get-Content "C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\account_33200931_data.json"
```

**Expected content:**
```json
{
  "account": 33200931,
  "server": "MEXAtlantic-Real",
  "balance": 50000.00,
  "equity": 50123.45,
  "margin": 1234.56,
  "free_margin": 48888.89,
  "margin_level": 4057.23,
  "profit": 123.45,
  "leverage": 100,
  "currency": "USD",
  "timestamp": "2025.11.24 18:00:00",
  "positions": [...],
  "orders": [...],
  "positions_count": 2,
  "orders_count": 0
}
```

---

### **Step 3: Deploy Python MT4 Bridge**

**3.1 Copy Bridge Script:**
```powershell
# The script is: mt4_bridge_mexatlantic.py
# Copy to: C:\mt5_bridge_service\
```

**3.2 Test Bridge Manually:**
```powershell
cd C:\mt5_bridge_service\
python mt4_bridge_mexatlantic.py
```

**Expected output:**
```
🚀 MT4 Bridge Service Started
Account: 33200931
Server: MEXAtlantic-Real
Broker: MEXAtlantic
Data File: C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\account_33200931_data.json
Sync Interval: 120 seconds
MongoDB: Connected to fidus_production

🔄 MT4 Sync Cycle Started
📄 Read MT4 data file
✅ Updated MT4 account 33200931: Balance=$50,000.00, Equity=$50,123.45
✅ MT4 sync completed successfully

⏳ Waiting 120 seconds until next sync...
```

**Press Ctrl+C to stop test**

---

### **Step 4: Create Windows Scheduled Task**

**4.1 Create Task:**
```powershell
$action = New-ScheduledTaskAction -Execute "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" -Argument "C:\mt5_bridge_service\mt4_bridge_mexatlantic.py" -WorkingDirectory "C:\mt5_bridge_service\"

$trigger = New-ScheduledTaskTrigger -AtStartup

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "MT4BridgeService" -Action $action -Trigger $trigger -Settings $settings -User "Administrator" -RunLevel Highest -Description "MT4 Bridge Service for account 33200931"
```

**4.2 Start Task:**
```powershell
Start-ScheduledTask -TaskName "MT4BridgeService"
```

**4.3 Verify Running:**
```powershell
Get-ScheduledTask -TaskName "MT4BridgeService"
Get-Process python | Where-Object {$_.Path -like "*python*"}
```

---

### **Step 5: Add to MongoDB**

**Add account to mt5_accounts collection:**
```javascript
db.mt5_accounts.insertOne({
  _id: "MT4_MEXATLANTIC_33200931",
  account: 33200931,
  broker: "MEXAtlantic",
  server: "MEXAtlantic-Real",
  platform: "MT4",
  manager_name: "Money Manager",
  fund_type: "MONEY_MANAGER",
  phase: "Phase 2",
  status: "active",
  sync_enabled: true,
  connection_status: "ready_for_sync",
  data_source: "MT4_FILE_BRIDGE",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
})
```

**Or add to mt5_account_config:**
```javascript
db.mt5_account_config.insertOne({
  account: 33200931,
  name: "MONEY_MANAGER - MT4",
  server: "MEXAtlantic-Real",
  platform: "MT4",
  fund_type: "MONEY_MANAGER",
  is_active: true,
  broker: "MEXAtlantic",
  phase: "Phase 2",
  created_at: new Date().toISOString()
})
```

---

### **Step 6: Verify End-to-End**

**6.1 Check MT4 EA is writing:**
```powershell
# Watch file updates
while($true) {
  $file = Get-Item "C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\account_33200931_data.json"
  Write-Host "Last modified: $($file.LastWriteTime)"
  Start-Sleep -Seconds 30
}
```

**6.2 Check Python bridge is reading:**
```powershell
Get-Content "C:\mt5_bridge_service\logs\mt4_mexatlantic.log" -Tail 20 -Wait
```

**6.3 Check MongoDB is updating:**
```powershell
python -c "from pymongo import MongoClient; db=MongoClient('mongodb+srv://chavapalmarubin_db_user:***SANITIZED***.y1p9be2.mongodb.net/fidus_production').get_database(); acc=db.mt5_accounts.find_one({'account':33200931}); print(f'Balance: {acc[\"balance\"]}, Last Sync: {acc.get(\"last_sync_timestamp\")}')"
```

---

## 📊 Expected System State After Integration:

**Running Processes:**
- MEXAtlantic MT5 Bridge (13 accounts)
- LUCRUM MT5 Bridge (1 account)
- MEXAtlantic MT4 Bridge (1 account)

**Total Accounts:** 15 (13 MT5 MEX + 1 MT5 LUCRUM + 1 MT4 MEX)

**Log Files:**
- `C:\mt5_bridge_service\logs\mexatlantic.log` (MT5)
- `C:\mt5_bridge_service\logs\lucrum.log` (MT5)
- `C:\mt5_bridge_service\logs\mt4_mexatlantic.log` (MT4)

---

## 🔧 Troubleshooting:

### Issue 1: EA Not Writing Data File

**Symptoms:**
- No file created in Common/Files
- No output in MT4 Experts tab

**Solutions:**
1. Check "Allow live trading" is enabled
2. Check EA has smiley face ☺ icon
3. Check MT4 Experts tab for errors
4. Recompile EA (no errors)
5. Restart MT4 terminal

---

### Issue 2: Python Can't Find Data File

**Error:** "MT4 data file not found"

**Solutions:**
```powershell
# Find the file
Get-ChildItem "C:\Users\Administrator\AppData\Roaming\MetaQuotes\" -Recurse -Filter "account_33200931_data.json"

# Update path in mt4_bridge_mexatlantic.py if needed
```

---

### Issue 3: MongoDB Not Updating

**Check connection:**
```python
from pymongo import MongoClient
client = MongoClient('mongodb+srv://chavapalmarubin_db_user:***SANITIZED***.y1p9be2.mongodb.net/fidus_production')
client.admin.command('ping')
print("MongoDB OK")
```

**Check account exists:**
```python
db = client.get_database()
account = db.mt5_accounts.find_one({'account': 33200931})
print(account)
```

---

## 📝 File Locations:

**MT4 EA:**
- Source: `MT4_Account_Data_Writer.mq4`
- Install to: `C:\Program Files (x86)\MEX Atlantic MT4 Terminal\MQL4\Experts\`

**Data File:**
- Location: `C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\account_33200931_data.json`
- Updates: Every 120 seconds

**Python Bridge:**
- Script: `mt4_bridge_mexatlantic.py`
- Location: `C:\mt5_bridge_service\`
- Log: `C:\mt5_bridge_service\logs\mt4_mexatlantic.log`

---

## ✅ Verification Checklist:

- [ ] MT4 Terminal logged into account 33200931
- [ ] MT4 EA installed and compiled
- [ ] EA attached to chart with smiley face ☺
- [ ] Data file created and updating every 120s
- [ ] Python bridge script deployed
- [ ] Scheduled task created and running
- [ ] MongoDB account document exists
- [ ] MongoDB updating every 120s
- [ ] Dashboard shows 15 total accounts
- [ ] Account 33200931 visible with MT4 platform label

---

**Deployment Time:** 15-20 minutes  
**Complexity:** Medium (requires MT4 EA installation)  
**Reliability:** High (file-based approach is stable)
