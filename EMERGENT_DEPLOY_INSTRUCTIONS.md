# 🚀 MT5 Bridge Fix - Automated Deployment Instructions

## 📋 Problem Identified
- **Root Cause**: Master account password is stored in `mt5_account_config` collection
- **Previous Code**: Only checked `mt5_accounts` first, then fell back to config only if account not found
- **Issue**: Account exists in `mt5_accounts` WITHOUT password, so it never checked `mt5_account_config`
- **Result**: $0.00 balances returned for all accounts

## ✅ Solution Implemented
Updated code to check BOTH collections explicitly:
1. Check `mt5_accounts` for password
2. If not found, check `mt5_account_config` 
3. Use whichever password is found (already exists in `mt5_account_config`)

---

## 🎯 Automated Deployment via GitHub Actions

### Prerequisites
You need to set up GitHub Secrets for VPS access:

1. **Go to GitHub Repository Settings**
   - Navigate to: `Settings` → `Secrets and variables` → `Actions`

2. **Add the following secrets:**
   ```
   VPS_HOST = 92.118.45.135
   VPS_USERNAME = Administrator
   VPS_PASSWORD = [Your VPS Administrator password]
   ```

### Deployment Steps

#### Step 1: Commit the workflow file
The workflow file is already created at:
```
.github/workflows/deploy-mt5-bridge-fix.yml
```

Commit this file to your repository:
```bash
git add .github/workflows/deploy-mt5-bridge-fix.yml
git add mt5_bridge_api_service_FIXED.py
git commit -m "Add automated deployment for MT5 Bridge fix"
git push origin main
```

#### Step 2: Run the workflow
1. Go to GitHub → **Actions** tab
2. Select workflow: **"Deploy MT5 Bridge Fix to VPS"**
3. Click **"Run workflow"** button
4. In the confirmation input, type: `DEPLOY`
5. Click **"Run workflow"** to start

#### Step 3: Monitor deployment
The workflow will:
- ✅ Test VPS connectivity
- ✅ Upload the fixed file to `C:\mt5_bridge_service\mt5_bridge_api_service.py`
- ✅ Restart the MT5 Bridge service
- ✅ Verify the service is healthy
- ✅ Display next steps

**Expected Duration:** ~3-5 minutes

---

## 🔍 Verification Steps

### 1. Check VPS Logs
Connect to VPS and check the service log:
```
C:\mt5_bridge_service\logs\api_service.log
```

**Look for these SUCCESS messages:**
```
[LOGIN] Password not in mt5_accounts, checking mt5_account_config...
[LOGIN] Found password in mt5_account_config
[LOGIN] Attempting login to master account 886557...
[OK] ✅ Master account 886557 logged in successfully
[OK] Master account balance: $XXX,XXX.XX
[OK] Server: MEXAtlantic-Real, Trade allowed: True
```

### 2. Test from Backend
From your FIDUS backend, test the MT5 bridge:

**Test Health Endpoint:**
```bash
curl http://92.118.45.135:8000/api/mt5/bridge/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "mt5": {
    "available": true,
    "terminal_info": {
      "connected": true,
      "trade_allowed": true
    }
  },
  "mongodb": {
    "connected": true
  }
}
```

**Test Account Data:**
```bash
curl http://92.118.45.135:8000/api/mt5/account/891215/info
```

**Expected Response:**
```json
{
  "account_id": 891215,
  "name": "Account Name",
  "fund_type": "CORE",
  "live_data": {
    "balance": 27047.52,
    "equity": 27047.52,
    "profit": 0.0
  }
}
```

### 3. Verify Client Portal
- Login to the client portal
- Navigate to account dashboard
- **All account balances should show live data** (not $0.00)
- Account 891215 should display approximately **$27,047.52**

---

## 🐛 Troubleshooting

### Issue: Workflow fails at "Deploy fixed file to VPS"
**Possible Causes:**
- VPS credentials incorrect
- WinRM not enabled on VPS
- Firewall blocking connection

**Solution:**
1. Verify GitHub Secrets are correct
2. Test VPS connectivity manually:
   ```powershell
   Test-Connection -ComputerName 92.118.45.135
   ```
3. Ensure WinRM is enabled on VPS:
   ```powershell
   Enable-PSRemoting -Force
   ```

### Issue: Service starts but master account login fails
**Check logs for:**
```
[ERROR] ❌ Master account login failed, error code: XXXXX
```

**Solution:**
1. Verify password "Fidus13!" is correct in MongoDB
2. Check MT5 terminal is running on VPS
3. Verify MT5_SERVER is set to "MEXAtlantic-Real"

### Issue: Still seeing $0.00 balances
**Possible Causes:**
- Backend cache not cleared
- Old bridge service still running
- Password still not found in database

**Solution:**
1. Restart backend service:
   ```bash
   sudo supervisorctl restart backend
   ```
2. Check VPS for multiple Python processes:
   ```powershell
   Get-Process python | Where-Object { $_.CommandLine -like "*mt5_bridge*" }
   ```
3. Verify password exists in MongoDB:
   ```python
   db.mt5_account_config.find_one({'account': 886557}, {'password': 1})
   ```

---

## 📊 Expected Results

### Before Fix:
```
Account 886557: Balance = $0.00 ❌
Account 886066: Balance = $0.00 ❌
Account 886602: Balance = $0.00 ❌
Account 885822: Balance = $0.00 ❌
Account 886528: Balance = $0.00 ❌
Account 891115: Balance = $0.00 ❌
Account 891234: Balance = $0.00 ❌
```

### After Fix:
```
Account 886557: Balance = $XXX,XXX.XX ✅
Account 886066: Balance = $XX,XXX.XX ✅
Account 886602: Balance = $XX,XXX.XX ✅
Account 885822: Balance = $XX,XXX.XX ✅
Account 886528: Balance = $XX,XXX.XX ✅
Account 891115: Balance = $XX,XXX.XX ✅
Account 891234: Balance = $27,047.52 ✅
```

---

## 🎉 Success Criteria

✅ Master account (886557) logs in successfully  
✅ All 7 MT5 accounts return live balance data  
✅ Client portal displays current balances (not $0.00)  
✅ Account 891215 shows ~$27,047.52  
✅ No "Suspicious balance change" errors in logs  
✅ MT5 Bridge health endpoint returns "healthy" status  

---

## 📞 Support

If deployment fails or issues persist:
1. Check VPS logs at `C:\mt5_bridge_service\logs\api_service.log`
2. Verify GitHub Secrets are correctly configured
3. Test VPS connectivity and WinRM access
4. Confirm MongoDB contains password in `mt5_account_config` collection

**Timeline:** This automated deployment should complete in ~5 minutes from start to verified fix.
