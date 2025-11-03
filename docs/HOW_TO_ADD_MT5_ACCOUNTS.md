# How to Add New MT5 Accounts - Easy Guide

## Overview
Adding new MT5 accounts requires updates to **3 locations**:
1. MongoDB - `mt5_account_config` collection (configuration)
2. MongoDB - `mt5_accounts` collection (live data)
3. VPS Bridge - Python script (account monitoring)

---

## Step 1: Add to MongoDB Collections

Run this Python script on the backend:

```python
import os
from pymongo import MongoClient
from datetime import datetime, timezone

mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['fidus_production']

# NEW ACCOUNT DETAILS
NEW_ACCOUNT = 897999  # <-- Change this
ACCOUNT_PASSWORD = "Fidus13!"  # <-- Change this  
ACCOUNT_SERVER = "MEXAtlantic-Real"  # <-- Change this
ACCOUNT_NAME = "CORE-04"  # <-- Change this
FUND_TYPE = "CORE"  # Options: CORE, BALANCE, SEPARATION
MANAGER_NAME = "CP Strategy"  # <-- Change this
INITIAL_BALANCE = 10000.00  # <-- Change this

# Add to mt5_account_config (configuration)
config_doc = {
    "account": NEW_ACCOUNT,
    "password": ACCOUNT_PASSWORD,
    "name": ACCOUNT_NAME,
    "fund_type": FUND_TYPE,
    "fund_code": FUND_TYPE,
    "server": ACCOUNT_SERVER,
    "broker_name": ACCOUNT_SERVER.split('-')[0],
    "manager_name": MANAGER_NAME,
    "target_amount": INITIAL_BALANCE,
    "initial_allocation": INITIAL_BALANCE,
    "is_active": True,
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
}

db.mt5_account_config.insert_one(config_doc)
print(f"✅ Added {NEW_ACCOUNT} to mt5_account_config")

# Add to mt5_accounts (live data)
live_doc = {
    "account": NEW_ACCOUNT,
    "balance": INITIAL_BALANCE,
    "equity": INITIAL_BALANCE,
    "profit": 0.0,
    "margin": 0.0,
    "margin_free": INITIAL_BALANCE,
    "margin_level": 0.0,
    "leverage": 100,
    "currency": "USD",
    "trade_allowed": True,
    "updated_at": datetime.now(timezone.utc),
    "synced_from_vps": False,
    "data_source": "INITIAL_SETUP"
}

db.mt5_accounts.insert_one(live_doc)
print(f"✅ Added {NEW_ACCOUNT} to mt5_accounts")

print(f"\n✅ Account {NEW_ACCOUNT} added to both MongoDB collections!")
```

---

## Step 2: Update VPS Bridge Script

### Edit File: `/app/vps-scripts/mt5_bridge_complete.py`

Find the `MANAGED_ACCOUNTS` dictionary (around line 39) and add your new account:

```python
MANAGED_ACCOUNTS = {
    886557: {"name": "BALANCE Master", "fund_type": "BALANCE"},
    886066: {"name": "BALANCE-01", "fund_type": "BALANCE"},
    886602: {"name": "BALANCE-02", "fund_type": "BALANCE"},
    885822: {"name": "CORE-01", "fund_type": "CORE"},
    886528: {"name": "CORE-02", "fund_type": "CORE"},
    891215: {"name": "SEPARATION-01", "fund_type": "SEPARATION"},
    891234: {"name": "SEPARATION-02", "fund_type": "SEPARATION"},
    897590: {"name": "CORE-03", "fund_type": "CORE"},
    897589: {"name": "BALANCE-03", "fund_type": "BALANCE"},
    897591: {"name": "SEPARATION-03", "fund_type": "SEPARATION"},
    897599: {"name": "SEPARATION-04", "fund_type": "SEPARATION"},
    # ADD NEW ACCOUNT HERE:
    897999: {"name": "CORE-04", "fund_type": "CORE"}  # <-- Your new account
}
```

---

## Step 3: Deploy VPS Bridge Update

### Option A: GitHub Actions (Recommended)

1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
2. Select: **"Deploy Complete MT5 Bridge"** workflow
3. Click **"Run workflow"**
4. Wait 2-3 minutes for deployment

### Option B: Manual Deployment

If you have VPS access:

```powershell
# Stop service
schtasks /End /TN MT5BridgeService
Start-Sleep -Seconds 3

# Download updated script
$url = "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps-scripts/mt5_bridge_complete.py"
$output = "C:\mt5_bridge_service\mt5_bridge_api_service.py"
Invoke-WebRequest -Uri $url -OutFile $output

# Restart service
schtasks /Run /TN MT5BridgeService
Start-Sleep -Seconds 10

# Verify
curl http://localhost:8000/api/mt5/accounts/summary
```

---

## Step 4: Update Backend Sync Service

### Edit File: `/app/backend/services/mt5_deals_sync_service.py`

Find the `managed_accounts` list (around line 39) and add your account:

```python
self.managed_accounts = [
    885822, 886066, 886528, 886557, 886602, 
    891215, 891234, 897590, 897589, 897591, 897599,
    897999  # <-- Your new account
]
```

Then restart backend:
```bash
sudo supervisorctl restart backend
```

---

## Step 5: Verification

After all steps, verify the account appears:

```python
# Check MongoDB
from pymongo import MongoClient
import os

mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['fidus_production']

# Should show your new account
print("mt5_accounts:", db.mt5_accounts.count_documents({}))
print("mt5_account_config:", db.mt5_account_config.count_documents({}))

# List all accounts
accounts = list(db.mt5_accounts.find({}, {"account": 1, "_id": 0}).sort("account", 1))
print("Accounts:", [a['account'] for a in accounts])
```

### Check Render Logs

Within 5 minutes, you should see:
```
✅ VPS sync complete: 12/12 accounts synced successfully
✅ MT5 sync completed: 12/12 accounts synced successfully
```

### Check Frontend

- Go to Admin → MT5 Accounts
- Your new account should appear in the list

---

## Step 6: Add New Money Manager (If Needed)

If the account uses a new manager:

```python
new_manager = {
    "manager_id": "new_manager_id",
    "manager_name": "New Manager Name",
    "profile_type": "copy_trade",
    "profile_url": "https://profile-url.com",
    "true_pnl": 0.0,
    "performance_fee_rate": 0.2,
    "stats": {
        "total_trades": 0,
        "win_rate": 0,
        "sharpe_ratio": 0
    },
    "is_active": True,
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
}

db.money_managers.insert_one(new_manager)
print(f"✅ Added manager: {new_manager['manager_name']}")
```

---

## Quick Checklist

- [ ] Added account to `mt5_account_config` collection
- [ ] Added account to `mt5_accounts` collection  
- [ ] Updated VPS Bridge script `MANAGED_ACCOUNTS`
- [ ] Deployed VPS Bridge via GitHub Actions
- [ ] Updated backend `mt5_deals_sync_service.py`
- [ ] Restarted backend service
- [ ] Verified in MongoDB (both collections)
- [ ] Checked Render logs for 11/11 → 12/12 sync
- [ ] Confirmed account appears in frontend
- [ ] Added new manager (if applicable)

---

## Common Issues

**Issue:** "Account not found in database" warnings in logs  
**Solution:** Account missing from `mt5_accounts` collection. Add it using Step 1.

**Issue:** Backend still shows old count (e.g., 7/11)  
**Solution:** Restart backend: `sudo supervisorctl restart backend`

**Issue:** Frontend doesn't show new account  
**Solution:** Wait 5 minutes for sync, then clear browser cache

**Issue:** VPS Bridge returns "No cached data"  
**Solution:** MT5 terminal on VPS needs to login to the account. Restart VPS Bridge service.

---

## Notes

- MongoDB Atlas and local MongoDB are both used (check MONGO_URL)
- VPS sync runs every 5 minutes (at :01, :06, :11, :16, :21, :26, etc.)
- Backend auto-sync runs every 2 minutes
- Initial setup shows `data_source: "INITIAL_SETUP"`
- After first VPS sync, shows `data_source: "VPS_LIVE_MT5"`

---

**Last Updated:** November 3, 2025  
**Tested With:** 11 accounts successfully added
