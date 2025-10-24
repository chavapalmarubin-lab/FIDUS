# 🎯 Quick Deployment Guide - MT5 Bridge Fix

## Problem Summary
Master account password is in `mt5_account_config` collection but code was only checking `mt5_accounts` first.

## Solution
Updated code to check BOTH collections for password.

---

## 🚀 Deploy in 3 Steps

### Step 1: Set GitHub Secrets
Go to: `GitHub → Settings → Secrets → Actions`

Add these secrets:
```
VPS_HOST = 92.118.45.135
VPS_USERNAME = Administrator
VPS_PASSWORD = [Your VPS password]
```

### Step 2: Push to GitHub
```bash
git add .github/workflows/deploy-mt5-bridge-fix.yml
git add mt5_bridge_api_service_FIXED.py
git add EMERGENT_DEPLOY_INSTRUCTIONS.md
git commit -m "Add MT5 Bridge automated deployment"
git push origin main
```

### Step 3: Run Workflow
1. GitHub → **Actions** tab
2. Select: **"Deploy MT5 Bridge Fix to VPS"**
3. Click: **"Run workflow"**
4. Type: `DEPLOY`
5. Click: **"Run workflow"**

⏱️ **Duration:** 3-5 minutes

---

## ✅ Success Indicators

After deployment, check VPS logs for:
```
[LOGIN] Found password in mt5_account_config
[OK] ✅ Master account 886557 logged in successfully
[OK] Master account balance: $XXX,XXX.XX
```

Then verify:
- Client portal shows live balances (not $0.00)
- Account 891215 displays ~$27,047.52
- Health endpoint returns "healthy"

---

## 📋 Files Created

1. `.github/workflows/deploy-mt5-bridge-fix.yml` - Automated deployment workflow
2. `mt5_bridge_api_service_FIXED.py` - Fixed service code (checks both collections)
3. `EMERGENT_DEPLOY_INSTRUCTIONS.md` - Detailed instructions with troubleshooting
4. `DEPLOY_QUICK_REFERENCE.md` - This file

---

## 🔧 Manual Deployment (Alternative)

If GitHub Actions is not available:

1. Copy `mt5_bridge_api_service_FIXED.py` to VPS:
   ```
   C:\mt5_bridge_service\mt5_bridge_api_service.py
   ```

2. Restart Python service on VPS:
   ```powershell
   Get-Process python | Where-Object { $_.CommandLine -like "*mt5_bridge*" } | Stop-Process -Force
   cd C:\mt5_bridge_service
   python mt5_bridge_api_service.py
   ```

3. Check logs:
   ```
   C:\mt5_bridge_service\logs\api_service.log
   ```

---

## 📞 Need Help?

See full documentation: `EMERGENT_DEPLOY_INSTRUCTIONS.md`
