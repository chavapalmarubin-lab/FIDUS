# VPS MT5 Terminal Configuration Required

**Date:** November 3, 2025  
**Status:** 🟡 VPS Bridge Deployed, MT5 Terminal Login Required

---

## ✅ WHAT'S WORKING:

1. **MongoDB:** All 11 accounts configured ✅
2. **Backend Code:** Updated for 11 accounts ✅  
3. **VPS Bridge Python Script:** Deployed with 11 accounts ✅
4. **VPS Bridge API:** Recognizes all 11 accounts ✅

---

## ⚠️ CURRENT ISSUE:

**The VPS Bridge recognizes 11 accounts but only 7 have data:**

```
VPS Bridge Status:
  886557: $10,054.27 - OK ✅
  886066: $0.00 - No cached data ⚠️
  886602: $15,933.99 - OK ✅
  885822: $0.00 - No cached data ⚠️
  886528: $0.00 - No cached data ⚠️
  891215: $0.00 - No cached data ⚠️
  891234: $0.00 - No cached data ⚠️
  897590: $0.00 - No cached data ⚠️ (NEW)
  897589: $0.00 - No cached data ⚠️ (NEW)
  897591: $0.00 - No cached data ⚠️ (NEW)
  897599: $0.00 - No cached data ⚠️ (NEW)
```

**MongoDB mt5_accounts Collection:**
- Only 7 accounts have synced data
- Missing: 897590, 897589, 897591, 897599

---

## 🔍 ROOT CAUSE:

The VPS Bridge Python script is updated and running, but **the MetaTrader 5 terminal software on the Windows VPS needs to be configured to log into the new accounts**.

**What's happening:**
1. ✅ VPS Bridge script knows about 11 accounts
2. ✅ VPS Bridge API accepts requests for all 11 accounts
3. ❌ MT5 Terminal is NOT logged into the 4 new accounts
4. ❌ Without MT5 login, there's no live data to fetch
5. ❌ Backend can't sync accounts that have no data

---

## 🛠️ SOLUTION: Configure MT5 Terminals on VPS

**Required: Access to Windows VPS (RDP or Remote Desktop)**

### Option 1: Add Accounts to Existing MT5 Terminal

If using a single MT5 terminal with multiple accounts:

1. **RDP into VPS** at http://92.118.45.135
2. **Open MetaTrader 5** terminal
3. **For each new account:**
   - Account: 897590, Password: Fidus13!, Server: MEXAtlantic-Real
   - Account: 897589, Password: Fidus13!, Server: MEXAtlantic-Real
   - Account: 897591, Password: Fidus13!, Server: MultibankFX-Real
   - Account: 897599, Password: Fidus13!, Server: MultibankFX-Real

4. **Add accounts:**
   - File → Login to Trade Account
   - Enter account number and password
   - Select server
   - Enable "Save account info"
   - Click "OK"

5. **Verify connections:**
   - Check that all accounts show green "Connected" status
   - Verify balance shows correctly in each account

### Option 2: Automated MT5 Login Script

If the VPS has automated login scripts:

1. **Locate the MT5 auto-login script**
   - Usually in `C:\mt5_service\` or similar
   - File name might be: `setup_mt5_accounts.ps1` or `mt5_login.py`

2. **Add new accounts to the script:**
   ```powershell
   # Add these to the accounts list:
   @{Account=897590; Password="Fidus13!"; Server="MEXAtlantic-Real"},
   @{Account=897589; Password="Fidus13!"; Server="MEXAtlantic-Real"},
   @{Account=897591; Password="Fidus13!"; Server="MultibankFX-Real"},
   @{Account=897599; Password="Fidus13!"; Server="MultibankFX-Real"}
   ```

3. **Run the script:**
   ```powershell
   .\setup_mt5_accounts.ps1
   ```

### Option 3: Restart MT5 Bridge Service (if auto-configured)

Some setups automatically detect new accounts on restart:

```powershell
# Stop the bridge service
schtasks /End /TN MT5BridgeService

# Wait a moment
Start-Sleep -Seconds 5

# Start the bridge service
schtasks /Run /TN MT5BridgeService

# Wait for initialization
Start-Sleep -Seconds 30

# Check status
curl http://localhost:8000/api/mt5/accounts/summary
```

---

## 📊 VERIFICATION STEPS:

After configuring MT5 terminals, verify success:

### 1. Check VPS Bridge (from VPS):
```powershell
curl http://localhost:8000/api/mt5/accounts/summary
```

Should show all 11 accounts with real balances (no "No cached data").

### 2. Check Render Backend Logs:
Within 5 minutes, you should see:
```
✅ MT5 sync completed: 11/11 accounts synced successfully
✅ VPS sync complete: 11/11 accounts synced
```

### 3. Check MongoDB:
```python
# mt5_accounts collection should have 11 accounts
db.mt5_accounts.count_documents({})  # Should return 11
```

### 4. Check Frontend:
- Go to Admin → MT5 Accounts
- Should display all 11 accounts
- All should show current balances

---

## 🔄 AUTOMATIC SYNC AFTER CONFIGURATION:

Once MT5 terminals are logged in:

1. **VPS Bridge** will immediately fetch live data from MT5
2. **VPS Sync Service** (runs every 5 minutes) will sync to MongoDB
3. **Backend Auto-Sync** (runs every 2 minutes) will update from MongoDB
4. **Frontend** will display all accounts in real-time

**No code changes needed** - everything else is already configured!

---

## 📝 ACCOUNT DETAILS FOR VPS CONFIGURATION:

| Account | Password | Server | Fund | Manager |
|---------|----------|--------|------|---------|
| 897590 | Fidus13! | MEXAtlantic-Real | CORE | CP Strategy |
| 897589 | Fidus13! | MEXAtlantic-Real | BALANCE | MEXAtlantic Provider 5201 |
| 897591 | Fidus13! | MultibankFX-Real | SEPARATION | alefloreztrader |
| 897599 | Fidus13! | MultibankFX-Real | SEPARATION | alefloreztrader |

---

## ✅ SUMMARY:

**Status:** Backend and database fully configured. VPS Bridge deployed. **Action required:** Configure MT5 terminals on Windows VPS to log into the 4 new trading accounts.

**ETA:** Once MT5 terminals are configured, full sync happens automatically within 5 minutes.

**Who can do this:** Anyone with RDP/admin access to the Windows VPS at http://92.118.45.135

---

**Last Updated:** November 3, 2025  
**Next Step:** Configure MT5 terminals on VPS
