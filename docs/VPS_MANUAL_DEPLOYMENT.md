# MANUAL DEPLOYMENT INSTRUCTIONS FOR VPS BRIDGE FIX
# Follow these steps on your Windows VPS

## STEP 1: Copy the new script to VPS

1. Download this file from the repository:
   `/app/vps-scripts/mt5_bridge_account_switching.py`

2. Copy it to your VPS at:
   `C:\MT5_Bridge\mt5_bridge_service.py`

## STEP 2: Stop the old service

Open PowerShell as Administrator and run:
```powershell
# Stop any running MT5 Bridge
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*python*"} | Stop-Process -Force
```

## STEP 3: Install required packages

```powershell
pip install fastapi uvicorn MetaTrader5 pymongo python-multipart
```

## STEP 4: Start the new service

```powershell
cd C:\MT5_Bridge
python mt5_bridge_service.py
```

## STEP 5: Verify it's working

Open a new PowerShell window and test:
```powershell
curl http://localhost:8000/api/mt5/bridge/health
```

You should see:
```json
{
  "status": "healthy",
  "mt5": {
    "initialized": true,
    "cached_accounts": 11
  }
}
```

## STEP 6: Check accounts are loading

```powershell
curl http://localhost:8000/api/mt5/accounts/summary
```

Wait 2-3 minutes and check again - you should see all 11 accounts with real balances!

## TROUBLESHOOTING

If you see errors, check the console output. The script will show:
- "[LOAD] Loading account credentials from MongoDB..."
- "[LOGIN] Attempting to login to account 886557..."
- "[DATA] Account 886557: Balance=$10,054.27, Equity=$10,054.27"
- This will repeat for all 11 accounts

## ALTERNATIVE: Direct file content

If you can't access the file, I can provide the complete script content for you to copy-paste directly into a new file on the VPS.
