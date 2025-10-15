# Task 1: Add GitHub Secrets - Step-by-Step Guide

**Time Required**: 5 minutes  
**Difficulty**: Easy

---

## Step 1: Get Render Deploy Hook (2 minutes)

### 1.1 Login to Render Dashboard
1. Go to: https://dashboard.render.com
2. Sign in with your account

### 1.2 Find Your Backend Service
1. Click on your `fidus-api` service (or whatever it's named)
2. Should see your backend service details

### 1.3 Get Deploy Hook URL
1. Click on **"Settings"** in the left sidebar
2. Scroll down to **"Deploy Hook"** section
3. You'll see a URL that looks like:
   ```
   https://api.render.com/deploy/srv-XXXXXXXXXXXXX?key=YYYYYYYYYYYYYYYY
   ```
4. Click **"Copy"** or select and copy this entire URL
5. Save it in a notepad - you'll need it in Step 2

**Important**: Keep this URL secret! It allows anyone to trigger deployments.

---

## Step 2: Add GitHub Secrets (3 minutes)

### 2.1 Go to Repository Settings
1. Go to: https://github.com/chavany2025/fidus-investment-platform
2. Click **"Settings"** tab (top right)
3. In left sidebar, click **"Secrets and variables"**
4. Click **"Actions"**

### 2.2 Add Secret #1: VPS_HOST
1. Click **"New repository secret"** (green button)
2. In "Name" field, type: `VPS_HOST`
3. In "Secret" field, type: `217.197.163.11`
4. Click **"Add secret"**

### 2.3 Add Secret #2: VPS_USERNAME
1. Click **"New repository secret"** again
2. In "Name" field, type: `VPS_USERNAME`
3. In "Secret" field, type: `Administrator`
4. Click **"Add secret"**

### 2.4 Add Secret #3: VPS_PASSWORD
1. Click **"New repository secret"** again
2. In "Name" field, type: `VPS_PASSWORD`
3. In "Secret" field, type: `2170Tenoch!`
4. Click **"Add secret"**

### 2.5 Add Secret #4: RENDER_DEPLOY_HOOK
1. Click **"New repository secret"** again
2. In "Name" field, type: `RENDER_DEPLOY_HOOK`
3. In "Secret" field, **paste** the URL you copied from Render (Step 1)
4. Click **"Add secret"**

### 2.6 Add Secret #5: EMERGENT_WEBHOOK_URL (Optional)
1. If Emergent provided a webhook URL, add it:
2. Click **"New repository secret"**
3. In "Name" field, type: `EMERGENT_WEBHOOK_URL`
4. In "Secret" field, paste the Emergent webhook URL
5. Click **"Add secret"**

**If you don't have an Emergent webhook, skip this step - it's optional!**

---

## Step 3: Verify Secrets

### 3.1 Check All Secrets Are Added
You should now see these secrets in your list:
- ✅ VPS_HOST
- ✅ VPS_USERNAME
- ✅ VPS_PASSWORD
- ✅ RENDER_DEPLOY_HOOK
- ⚠️ EMERGENT_WEBHOOK_URL (optional)

### 3.2 Secrets Are Encrypted
- You'll see `********` instead of actual values
- This is normal - secrets are encrypted
- You can't view them again, but you can update them

---

## ✅ Task 1 Complete!

**What you've accomplished**:
- ✅ GitHub Actions can now deploy to Render
- ✅ GitHub Actions can now SSH into VPS
- ✅ All credentials securely stored

**Next**: Move to Task 2 (VPS Setup)

---

## 🔍 Troubleshooting

**Problem**: Can't find "Settings" tab
- **Solution**: Make sure you're the repository owner or have admin access

**Problem**: "New repository secret" button is grayed out
- **Solution**: You need admin permissions on the repository

**Problem**: Lost the Render deploy hook URL
- **Solution**: Go back to Render dashboard → Settings → Deploy Hook → Copy again

**Problem**: Made a typo in a secret
- **Solution**: Click the secret name → "Update secret" → Fix the value → "Update secret"

---

**Ready for Task 2?** See `TASK2_VPS_SETUP_INSTRUCTIONS.md`
