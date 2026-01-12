# VIKING MT4 Bridge Setup (JSON File Method)

This guide sets up the VIKING data sync using the **JSON file method** (same as FIDUS).

## Architecture
```
MT4 EA (VIKING_MT4_Bridge_JSON.mq4)
    ↓ writes JSON every 30 seconds
C:\Users\Administrator\AppData\...\MQL4\Files\viking_account_data.json
    ↓ Python service monitors file
viking_json_sync_service.py
    ↓ updates MongoDB
MongoDB Atlas (fidus_production.viking_accounts)
    ↓ Emergent app reads
VIKING Dashboard displays real-time data
```

---

## Step 1: Install the EA

1. **Copy** `VIKING_MT4_Bridge_JSON.mq4` to your MT4 terminal:
   ```
   C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\[TERMINAL_ID]\MQL4\Experts\
   ```

2. **Open MetaEditor** (F4 in MT4) and compile the EA

3. **Attach EA** to any chart on account **33627673**:
   - Drag EA from Navigator → Expert Advisors
   - In settings, confirm:
     - `SyncIntervalSeconds = 30`
     - `OutputFileName = viking_account_data.json`

4. **Enable AutoTrading** (green button in toolbar)

5. **Verify** in Experts tab you see:
   ```
   VIKING MT4 Bridge (JSON) initialized
   Account: 33627673
   VIKING Sync successful - Balance: $XXXXX Equity: $XXXXX
   ```

---

## Step 2: Install Python Service

1. **Open PowerShell as Administrator**

2. **Install dependencies:**
   ```powershell
   pip install pymongo watchdog python-dotenv
   ```

3. **Copy** `viking_json_sync_service.py` to:
   ```
   C:\VIKING_Bridge\viking_json_sync_service.py
   ```

4. **Edit the file** - Update `MT4_FILES_PATH` if needed:
   ```python
   MT4_FILES_PATH = r'C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\[YOUR_TERMINAL_ID]\MQL4\Files'
   ```
   
   Find your Terminal ID:
   - Open MT4 → File → Open Data Folder
   - Copy the path

5. **Test run:**
   ```powershell
   cd C:\VIKING_Bridge
   python viking_json_sync_service.py
   ```

   You should see:
   ```
   VIKING MT4 JSON Sync Service Starting
   MongoDB connected successfully
   File watcher started (watchdog mode)
   Synced account 33627673: Balance=$XXXXX, Equity=$XXXXX
   ```

---

## Step 3: Auto-Start on Boot

### Option A: Task Scheduler (Recommended)

1. Open **Task Scheduler**
2. Create Basic Task:
   - Name: `VIKING MT4 Sync Service`
   - Trigger: `When the computer starts`
   - Action: `Start a program`
   - Program: `python`
   - Arguments: `C:\VIKING_Bridge\viking_json_sync_service.py`
   - Start in: `C:\VIKING_Bridge`

3. In Properties:
   - Check "Run whether user is logged on or not"
   - Check "Run with highest privileges"

### Option B: Batch File

Create `C:\VIKING_Bridge\start_viking_sync.bat`:
```batch
@echo off
cd /d C:\VIKING_Bridge
python viking_json_sync_service.py
```

Add to Windows Startup folder.

---

## Step 4: Verify Data Flow

1. **Check JSON file is being created:**
   ```powershell
   type "C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\[TERMINAL_ID]\MQL4\Files\viking_account_data.json"
   ```

2. **Check MongoDB has data:**
   - Open VIKING dashboard
   - Balance should show real values
   - Status should show "Active"

3. **Check sync log:**
   ```powershell
   type C:\VIKING_Bridge\viking_sync.log
   ```

---

## Troubleshooting

### EA not writing JSON file
- Check MT4 Experts tab for errors
- Ensure AutoTrading is ON (green button)
- Verify EA is attached to chart

### Python service not syncing
- Check `MT4_FILES_PATH` is correct
- Verify MongoDB connection string
- Check `viking_sync.log` for errors

### Dashboard still shows $0
- Verify `last_sync` field in MongoDB is updating
- Check browser console for API errors
- Try clicking "Refresh" button on dashboard

---

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| `VIKING_MT4_Bridge_JSON.mq4` | MT4 Experts folder | EA that writes JSON |
| `viking_json_sync_service.py` | C:\VIKING_Bridge\ | Syncs JSON to MongoDB |
| `viking_account_data.json` | MT4 Files folder | Account data (auto-created) |
| `viking_sync.log` | C:\VIKING_Bridge\ | Service log file |
