# MT4 File Monitor - Automated Deployment

## What This Does

**Automatically finds and monitors the MT4 account data file**, then uploads to MongoDB.

### Features:
✅ **Auto-discovery** - Searches common MT4 locations for account_data.json  
✅ **Auto-restart** - Windows Task Scheduler ensures it runs on boot  
✅ **Auto-recovery** - Retries if file not found or MongoDB disconnects  
✅ **Zero manual config** - Everything deployed via GitHub Actions  

## Deployment Steps

### 1. Run GitHub Action

Go to: **Actions** → **"Deploy MT4 File Monitor Service"** → **Run workflow**

This will:
- Create `C:\mt4_bridge_service\mt4_file_monitor.py`
- Install Python dependencies (pymongo, python-dotenv)
- Create Windows Task Scheduler task
- Start the service immediately

### 2. Verify Service is Running

On your VPS, open PowerShell:

```powershell
# Check Task Scheduler status
Get-ScheduledTask -TaskName "MT4 File Monitor" | Select State

# Should show "Running"
```

### 3. Check if File Was Found

The service searches these locations:
1. `C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\`
2. `C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\*\Files\`
3. `C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Files\`

Check MT4 Journal for "Data written" messages - this confirms EA is working.

## How It Works

```
MT4 EA (every 5 min) → account_data.json → Python Monitor → MongoDB
```

1. **MT4 EA** writes account data to JSON file
2. **Python service** auto-finds and monitors the file
3. **MongoDB** receives updates with `fund_type: "MONEY_MANAGER"`

## MongoDB Document Structure

```javascript
{
  "_id": "MT4_33200931",
  "account_number": 33200931,
  "account_name": "Chava",
  "server": "MEXAtlantic-Real",
  "balance": 50000.00,
  "equity": 50000.00,
  "margin": 0.00,
  "free_margin": 50000.00,
  "profit": 0.00,
  "currency": "USD",
  "leverage": 100,
  "credit": 0.00,
  "platform": "MT4",
  "fund_type": "MONEY_MANAGER",  // Added by service
  "updated_at": "2025-01-19T17:45:00Z",  // Added by service
  "mt4_timestamp": "2025.01.19 17:45:00"
}
```

## Troubleshooting

### Service not running?

```powershell
Start-ScheduledTask -TaskName "MT4 File Monitor"
```

### Check logs (when logging is added):

```powershell
Get-Content C:\mt4_bridge_service\monitor.log -Tail 50
```

### Restart service:

```powershell
Stop-ScheduledTask -TaskName "MT4 File Monitor"
Start-ScheduledTask -TaskName "MT4 File Monitor"
```

### Check MongoDB connection:

Ensure `MONGO_URL` secret is set correctly in GitHub repo settings.

## Manual Test

To test the service manually:

```powershell
cd C:\mt4_bridge_service
python mt4_file_monitor.py
```

You should see:
```
🔍 Searching for account_data.json...
   Checking: C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files
✅ Found: C:\Users\...\account_data.json
✅ Connected to MongoDB
🚀 Service started. Monitoring: C:\Users\...\account_data.json
```

## What If File Still Not Found?

The service will:
1. Print all search paths it checked
2. Wait 60 seconds
3. Search again
4. Repeat until file is found

**Once the MT4 EA writes the file**, the service will find it automatically.

## Advantages Over Previous Approaches

| Feature | File Monitor | ZeroMQ |
|---------|--------------|--------|
| Setup | ✅ Automated | ❌ 14+ hours, failed |
| Dependencies | ✅ Python only | ❌ DLLs, libraries |
| Auto-discovery | ✅ Finds file automatically | ❌ Fixed paths |
| Reliability | ✅ File I/O always works | ❌ Socket errors |
| Debugging | ✅ Clear logs | ❌ Network debugging |

## Next Steps After Deployment

1. **Verify EA is running** - Check MT4 Journal for "Data written" messages
2. **Wait 5 minutes** - EA writes file every 300 seconds
3. **Check MongoDB** - Query `db.mt5_accounts.findOne({_id: "MT4_33200931"})`
4. **Verify data updates** - `updated_at` field should update every 5 minutes

## Files Created

- `C:\mt4_bridge_service\mt4_file_monitor.py` - Main service
- `C:\mt4_bridge_service\.env` - MongoDB connection string
- `C:\mt4_bridge_service\start_monitor.bat` - Startup script
- Windows Task: "MT4 File Monitor" - Auto-starts on boot
