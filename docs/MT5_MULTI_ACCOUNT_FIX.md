# MT5 MULTI-ACCOUNT BALANCE FIX

**Date:** October 29, 2025  
**Issue:** Only master account (886557) showing balance, other 6 accounts showing $0.00  
**Root Cause:** MT5 Bridge only caching whichever account the Terminal happened to be logged into  
**Fix:** Implemented proper multi-account login cycle to fetch ALL balances

---

## 🔴 THE PROBLEM

### What Was Broken
The previous MT5 Bridge (`mt5_bridge_complete.py` v3.0) had a critical flaw:

```python
# OLD CODE - BROKEN
async def refresh_account_cache():
    """Only cached the CURRENT account"""
    while True:
        if MT5_INITIALIZED:
            # Get current account info
            account_info = mt5.account_info()  # ❌ Only gets current account
            if account_info:
                current_account = account_info.login
                ACCOUNT_CACHE[current_account] = {...}  # Only 1 account cached
```

**Result:** 
- Only the account that MT5 Terminal was logged into got cached
- All other 6 accounts returned `$0.00` balances
- No actual login attempts to other accounts

---

## ✅ THE FIX

### What Changed

**New file:** `/app/vps-scripts/mt5_bridge_multi_account_fixed.py` (v4.0)

**Key improvements:**

1. **Proper Multi-Account Login Cycle**
```python
async def refresh_all_accounts():
    """Cycle through ALL 7 accounts"""
    for account_number in MANAGED_ACCOUNTS.keys():
        # Login to each account
        if login_to_account(account_number, MT5_INVESTOR_PASSWORD):
            # Get real data
            data = get_account_data(account_number)
            # Cache it
            ACCOUNT_CACHE[account_number] = data
        await asyncio.sleep(2)  # Small delay between logins
```

2. **Dedicated Login Function**
```python
def login_to_account(account_number: int, password: str) -> bool:
    """
    Explicitly login to a specific MT5 account
    Uses investor password: Fidus13!
    """
    authorized = mt5.login(
        login=account_number, 
        password=password, 
        server="MEXAtlantic-Real"
    )
    return authorized
```

3. **Background Refresh Loop**
```python
async def account_refresh_loop():
    """Run every 5 minutes"""
    while True:
        await refresh_all_accounts()  # Login to all 7 accounts
        await asyncio.sleep(300)  # 5 minutes
```

4. **Session Isolation Fix**
```powershell
# Task Scheduler now uses -LogonType Interactive
$principal = New-ScheduledTaskPrincipal `
    -UserId "trader" `
    -LogonType Interactive `  # ← Runs in Session 1 with MT5 Terminal
    -RunLevel Highest
```

---

## 🚀 DEPLOYMENT

### How to Deploy

**Option 1: GitHub Actions (Recommended)**
```bash
# Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
# Select: "Deploy MT5 Bridge - Multi-Account Fixed"
# Click: "Run workflow"
# Wait: ~2 minutes for deployment
```

**Option 2: Manual Deployment**
```bash
# From your local machine
cd /app
.github/workflows/deploy-mt5-bridge-multi-account-fix.yml
```

### What the Deployment Does

1. ✅ Copies new `mt5_bridge_multi_account_fixed.py` to VPS as `mt5_bridge_api_service.py`
2. ✅ Stops any existing MT5 Bridge processes
3. ✅ Deletes old Task Scheduler task
4. ✅ Creates new task with `-LogonType Interactive` (Session 1)
5. ✅ Starts the service immediately
6. ✅ Tests health endpoint

---

## ✅ VERIFICATION

### Step 1: Check Service is Running

**RDP into VPS:**
```powershell
mstsc /v:92.118.45.135:42014
# Username: trader
# Password: 4p1We0OHh3LKgm6
```

**Check Task Scheduler:**
```powershell
Get-ScheduledTask -TaskName "MT5_Bridge_Service"
# Should show "Ready" or "Running"
```

**Check Process:**
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python"}
# Should show python.exe running
```

### Step 2: Check Logs

```powershell
Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 50
```

**What to look for:**
```
[INIT] MT5 initialized successfully
[LOGIN] Attempting to login to account 885822...
[OK] Successfully logged into account 885822
[DATA] Account 885822: Balance=$10151.41, Equity=$10151.41
[CACHE] ✅ Cached account 885822: $10151.41
[LOGIN] Attempting to login to account 886066...
[OK] Successfully logged into account 886066
[DATA] Account 886066: Balance=$10000.00, Equity=$10000.00
...
[CACHE] Refresh cycle complete. Cached accounts: 7/7
```

### Step 3: Test API Endpoint

**From any machine:**
```bash
curl http://92.118.45.135:8000/api/mt5/bridge/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "mt5": {
    "initialized": true,
    "available": true,
    "current_account": 886557
  },
  "cache": {
    "accounts_cached": 7,
    "total_accounts": 7,
    "cache_complete": true
  },
  "version": "4.0-multi-account"
}
```

**Check all accounts:**
```bash
curl http://92.118.45.135:8000/api/mt5/accounts/summary
```

**Expected response:**
```json
{
  "success": true,
  "accounts": [
    {
      "account": 885822,
      "name": "CORE-CP",
      "fund_type": "CORE",
      "balance": 10151.41,  # ✅ REAL balance, not $0.00
      "equity": 10151.41,
      "data_source": "cached"
    },
    {
      "account": 886066,
      "name": "BALANCE-GoldenTrade",
      "fund_type": "BALANCE",
      "balance": 10000.00,  # ✅ REAL balance
      "equity": 10000.00,
      "data_source": "cached"
    }
    // ... all 7 accounts with REAL balances
  ],
  "count": 7,
  "cached_count": 7
}
```

### Step 4: Check Frontend Dashboard

1. Open FIDUS dashboard
2. Navigate to "MT5 Accounts" or "Portfolio" section
3. **Verify:** All 7 accounts show real balances (not $0.00)

**Expected balances (approximate):**
- 885822: ~$10,151
- 886066: ~$10,000
- 886528: ~$6,590
- 886557: ~$80,000
- 886602: ~$10,000
- 891215: ~$6,590
- 891234: ~$8,000

---

## 🔍 TROUBLESHOOTING

### Issue: Service starts but crashes immediately

**Check:**
```powershell
# View error log
Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 100
```

**Common causes:**
- Python not in PATH
- MT5 Terminal not running
- Incorrect server name (should be "MEXAtlantic-Real")

**Fix:**
```powershell
# Ensure MT5 Terminal is running
Get-Process | Where-Object {$_.ProcessName -eq "terminal64"}

# If not running, start it
Start-Process "C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"
```

### Issue: "MT5 not initialized" error

**Check session:**
```powershell
# Check which session the task is running in
Get-ScheduledTask -TaskName "MT5_Bridge_Service" | Get-ScheduledTaskInfo
```

**Should show:**
```
LogonType: Interactive  # ← Must be Interactive, not ServiceAccount
```

**Fix:**
```powershell
# Re-run deployment workflow to recreate task with correct session type
```

### Issue: Some accounts still showing $0.00

**Possible causes:**
1. First cache cycle hasn't completed yet (wait 5-10 minutes)
2. Login failed for those accounts (wrong password)
3. Accounts don't exist or are inactive

**Check logs:**
```powershell
Get-Content C:\mt5_bridge_service\logs\api_service.log | Select-String "FAIL"
```

**Look for:**
```
[FAIL] Login failed for account 885822: (error code, message)
```

**Fix:**
- Verify account numbers are correct in `MANAGED_ACCOUNTS`
- Verify investor password is correct (`Fidus13!`)
- Check if account is active in MT5

### Issue: Bridge responds but balances still $0.00

**Force immediate refresh:**
```bash
curl -X POST http://92.118.45.135:8000/api/mt5/refresh
```

**This will:**
- Immediately cycle through all 7 accounts
- Login and fetch fresh data
- Update cache
- Return updated account count

---

## 📊 MONITORING

### Health Check Schedule

The auto-healing system (`monitor-bridge-health.yml`) runs every 15 minutes:
- Checks if bridge is responding
- Verifies MT5 is initialized
- Auto-restarts if service is down

### Manual Health Check

```bash
# Quick check
curl http://92.118.45.135:8000/api/mt5/bridge/health

# Detailed check
curl http://92.118.45.135:8000/api/mt5/accounts/summary | python3 -m json.tool
```

### Log Monitoring

```powershell
# Watch logs in real-time
Get-Content C:\mt5_bridge_service\logs\api_service.log -Wait -Tail 50

# Filter for errors
Get-Content C:\mt5_bridge_service\logs\api_service.log | Select-String "FAIL|ERROR"

# Filter for successful logins
Get-Content C:\mt5_bridge_service\logs\api_service.log | Select-String "Successfully logged"
```

---

## 🎯 SUCCESS CRITERIA

✅ **Service is working correctly when:**

1. Health endpoint returns `"cache_complete": true`
2. All 7 accounts have non-zero balances (unless they're actually zero)
3. Logs show successful login to all accounts every 5 minutes
4. Frontend dashboard displays real balances for all accounts
5. Broker rebates calculate correctly with historical data

---

## 📝 TECHNICAL DETAILS

### Account Configuration

```python
MANAGED_ACCOUNTS = {
    885822: {"name": "CORE-CP", "fund_type": "CORE"},
    886066: {"name": "BALANCE-GoldenTrade", "fund_type": "BALANCE"},
    886528: {"name": "SEPARATION-Reserve", "fund_type": "SEPARATION"},
    886557: {"name": "BALANCE-Master", "fund_type": "BALANCE"},  # Master
    886602: {"name": "BALANCE-Tertiary", "fund_type": "BALANCE"},
    891215: {"name": "SEPARATION-Trading", "fund_type": "SEPARATION_TRADING"},
    891234: {"name": "CORE-GoldenTrade", "fund_type": "CORE"}
}
```

### Refresh Schedule

- **Initial refresh:** 10 seconds after startup
- **Subsequent refreshes:** Every 5 minutes (300 seconds)
- **Time per account:** ~2 seconds (login + data fetch)
- **Total cycle time:** ~14 seconds for all 7 accounts

### Session Configuration

- **Python Service Session:** Session 1 (Interactive)
- **MT5 Terminal Session:** Session 1 (Interactive)
- **Task Scheduler Type:** Interactive (not Service Account)
- **User:** trader (logged in via RDP)

---

## 🔐 SECURITY NOTES

- Investor password (`Fidus13!`) is read-only - cannot place trades
- Password is hardcoded in script (acceptable for investor password)
- Service runs as `trader` user (not Administrator)
- No sensitive data exposed via API endpoints

---

## 📅 NEXT STEPS

After deployment and verification:

1. ✅ Verify `vps_sync_service.py` (backend) correctly syncs data from bridge to MongoDB
2. ✅ Check `mt5_deals_history` collection in MongoDB is populated
3. ✅ Test broker rebates calculation with all 7 accounts
4. ✅ Monitor watchdog alerts (should remain low)

---

## 📞 SUPPORT

If issues persist after following this guide:

1. Collect logs: `C:\mt5_bridge_service\logs\api_service.log`
2. Collect health check output: `curl http://92.118.45.135:8000/api/mt5/bridge/health`
3. Check Task Scheduler task status
4. Verify MT5 Terminal is running
5. RDP into VPS and manually test Python script

---

**Version:** 1.0  
**Last Updated:** October 29, 2025  
**Status:** Ready for deployment
