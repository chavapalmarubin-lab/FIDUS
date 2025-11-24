# Push to GitHub & Deploy - Instructions

**Date:** November 24, 2025  
**Status:** Files ready, need manual GitHub push  

---

## 📋 Files Ready to Push:

**Bridge Code:**
- ✅ `vps-scripts/mt5_bridge_api_service_multi_terminal.py` (9.6 KB)

**GitHub Workflow:**
- ✅ `.github/workflows/deploy-multi-terminal-bridge.yml` (12.4 KB)

**Documentation:**
- ✅ `BRIDGE_UPDATE_DEPLOYMENT.md` (10.6 KB)
- ✅ `MULTI_TERMINAL_SOLUTION.md`
- ✅ `FINAL_EMERGENT_REQUEST.md`
- ✅ `START_LUCRUM_TERMINAL_GUIDE.md`
- ✅ `VPS_DIAGNOSTIC_REPORT.md`
- ✅ `WORKFLOW_FIXES_APPLIED.md`
- ✅ `SYSTEM_MASTER.md` (updated)

---

## 🚀 Step 1: Push to GitHub

**In Emergent UI:**

1. Look for **"Save to GitHub"** button (usually in top-right or toolbar)
2. Click it to push all committed changes
3. Wait for confirmation that push succeeded
4. Changes will appear in your GitHub repository

**Alternative - If no "Save to GitHub" button:**

If you don't see the button in Emergent, you can use the **"Connect GitHub"** feature to link your repository, then save.

---

## 🎯 Step 2: Run Deployment Workflow

**After files are in GitHub:**

1. **Go to GitHub Actions:**
   - Open: `https://github.com/chavapalmarubin-lab/FIDUS/actions`
   
2. **Find the workflow:**
   - Look for: **"Deploy Multi-Terminal Bridge Update"**
   - It should appear in the workflows list (left sidebar)
   
3. **Run it:**
   - Click on the workflow name
   - Click **"Run workflow"** button (right side)
   - Select branch: `main`
   - Click green **"Run workflow"** button
   
4. **Monitor progress:**
   - Click on the running workflow
   - Watch each step complete
   - Look for success indicators (✅)

---

## ⏱️ Timeline:

```
Now: Click "Save to GitHub" (1 min)
  ↓
+1 min: Changes appear in GitHub
  ↓
+2 min: Go to GitHub Actions
  ↓
+3 min: Run "Deploy Multi-Terminal Bridge Update"
  ↓
+13 min: Deployment completes
  ↓
+15 min: Verify account 2198 syncing
```

**Total Time:** ~15 minutes

---

## ✅ What to Expect After Deployment:

**During Workflow Execution:**

You'll see these steps complete:
1. ✅ Backup Current Bridge
2. ✅ Stop Current Bridge Service
3. ✅ Deploy Updated Bridge Script
4. ✅ Install Updated Bridge
5. ✅ Verify Terminal Paths
6. ✅ Test Bridge Manually
7. ✅ Start Bridge Service
8. ✅ Monitor First Sync Cycle
9. ✅ Verify LUCRUM Account Syncing

**Success Indicators:**

In workflow logs, look for:
```
✅ Backup created: mt5_bridge_api_service_backup_20251124_120000.py
✅ Bridge service stopped
✅ New bridge script installed
✅ MEXAtlantic terminal found
✅ LUCRUM terminal found
✅ LUCRUM terminal is running with account 2198
✅ Bridge service is running (PID: xxxx)

Account 2198 Status:
  Balance: $11,299.25
  Last Sync: 2025-11-24 XX:XX:XX
  Synced from VPS: True
✅ Account is syncing successfully!
```

---

## 🐛 If "Save to GitHub" is Not Available:

**Option 1: Manual Git Push (Advanced)**

If you have Git access, you can push manually:

```bash
# In terminal/command line on your local machine
git clone https://github.com/chavapalmarubin-lab/FIDUS.git
cd FIDUS

# Copy the files from Emergent to your local repo
# Then:
git add .
git commit -m "Add LUCRUM multi-terminal bridge support"
git push origin main
```

**Option 2: Manual File Upload**

Upload files directly via GitHub web interface:
1. Go to your repo: `https://github.com/chavapalmarubin-lab/FIDUS`
2. Navigate to each directory
3. Click "Add file" → "Upload files"
4. Upload the new files:
   - `vps-scripts/mt5_bridge_api_service_multi_terminal.py`
   - `.github/workflows/deploy-multi-terminal-bridge.yml`
   - All the `.md` documentation files

**Option 3: Contact Emergent Support**

Ask Emergent support how to push changes from the platform to GitHub.

---

## 🔄 Alternative: Manual VPS Deployment

**If GitHub Actions doesn't work, deploy manually:**

1. **RDP to VPS:** `217.197.163.11`

2. **Download the new bridge script:**
   - From GitHub after pushing, or
   - Copy from Emergent file browser

3. **Run deployment commands:**
   ```powershell
   # Backup
   cd C:\mt5_bridge_service\
   Copy-Item mt5_bridge_api_service.py "mt5_bridge_api_service_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').py"
   
   # Stop service
   schtasks /End /TN "MT5BridgeService"
   
   # Replace script
   # (Copy mt5_bridge_api_service_multi_terminal.py to this directory)
   # Then:
   Copy-Item mt5_bridge_api_service_multi_terminal.py mt5_bridge_api_service.py -Force
   
   # Start service
   schtasks /Run /TN "MT5BridgeService"
   
   # Monitor
   Get-Content logs\api_service.log -Tail 50 -Wait
   ```

---

## 📞 Quick Reference:

**GitHub Repository:**
`https://github.com/chavapalmarubin-lab/FIDUS`

**GitHub Actions:**
`https://github.com/chavapalmarubin-lab/FIDUS/actions`

**Workflow Name:**
"Deploy Multi-Terminal Bridge Update"

**VPS:**
- IP: `217.197.163.11`
- User: (your username)
- Bridge: `C:\mt5_bridge_service\`

---

## 🎯 Summary:

**What You Need to Do:**

1. **Push to GitHub:**
   - Use "Save to GitHub" button in Emergent UI
   - OR manually push via Git
   - OR upload files via GitHub web interface

2. **Run Deployment:**
   - Go to GitHub Actions
   - Find "Deploy Multi-Terminal Bridge Update" workflow
   - Click "Run workflow"
   - Monitor progress

3. **Verify:**
   - Check workflow completes successfully
   - View dashboard for 15 accounts
   - Confirm account 2198 syncing

**Total Time:** 15-20 minutes

---

**Created:** November 24, 2025  
**Next Step:** Click "Save to GitHub" in Emergent UI
