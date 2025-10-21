# 🔄 GitHub Workflow Sync Instructions

## Issue: Security Protection Blocking GitHub Push

GitHub's secret scanning detected sensitive data and blocked the automatic sync. The sensitive file has been removed, and you can now proceed with syncing your workflow changes.

---

## ✅ **IMMEDIATE SOLUTION: Manual Workflow File Updates**

Since we cannot use "Save to GitHub" due to security restrictions, here are **3 alternative methods** to sync the updated workflow files:

---

### **Method 1: Direct GitHub Web UI Edit (Recommended - Fastest)**

Update each workflow file directly on GitHub:

1. **Go to your repository:** https://github.com/chavapalmarubin-lab/FIDUS

2. **Navigate to each workflow file** in `.github/workflows/` and update:

**Files to Update (17 total):**

#### **Critical Files (Update These First):**

1. **`deploy-fresh-vps.yml`**
   - Line 14: Change `217.197.163.11` → `92.118.45.135`
   - All SSH/deployment lines: Use `${{ secrets.VPS_HOST }}`

2. **`deploy-vps.yml`**
   - Replace all `217.197.163.11` → `92.118.45.135`

3. **`deploy-autonomous-system.yml`**
   - Replace all `217.197.163.11` → `92.118.45.135`

4. **`diagnose-vps.yml`**
   - Replace all `217.197.163.11` → `92.118.45.135`

5. **`deploy-mt5-bridge-emergency-ps.yml`**
   - Replace all `217.197.163.11` → `92.118.45.135`

#### **Additional Files (Update When Possible):**

6. `nuclear-reset-mt5-bridge.yml`
7. `direct-file-deploy-mt5-bridge.yml`
8. `final-fix-mt5-bridge.yml`
9. `complete-diagnostic-fix.yml`
10. `auto-test-healing-system.yml`
11. `fresh-install-mt5-bridge.yml`
12. `deploy-mt5-bridge-emergency.yml`
13. `diagnose-mt5-bridge.yml`
14. `setup-mt5-auto-login.yml`
15. `monitor-render-health.yml`
16. `diagnose-vps-auto-restart.yml`
17. `deploy-backend.yml`

**How to Edit on GitHub:**
```
1. Click on the file
2. Click the pencil icon (Edit)
3. Find and replace: 217.197.163.11 → 92.118.45.135
4. Ensure any hardcoded credentials use: ${{ secrets.VPS_HOST }}
5. Commit directly to main branch
```

---

### **Method 2: GitHub CLI (If Installed)**

If you have GitHub CLI installed locally:

```bash
# 1. Clone the repository (if not already cloned)
git clone https://github.com/chavapalmarubin-lab/FIDUS.git
cd FIDUS

# 2. Create a new branch
git checkout -b update-vps-workflows

# 3. Copy updated workflow files from /app to your local repo
cp /app/.github/workflows/*.yml .github/workflows/

# 4. Commit and push
git add .github/workflows/
git commit -m "Update all workflows to use new VPS (92.118.45.135)"
git push origin update-vps-workflows

# 5. Create PR on GitHub and merge
gh pr create --title "Update VPS endpoints to 92.118.45.135" --body "Migration from old VPS to new clean VPS"
gh pr merge
```

---

### **Method 3: Quick Find & Replace Script (GitHub Web)**

Use GitHub's web editor search/replace:

1. Go to repository on GitHub
2. Press `.` (dot) to open web-based VS Code editor
3. Press `Ctrl+Shift+F` (or `Cmd+Shift+F` on Mac) to open global search
4. Search for: `217.197.163.11`
5. Replace all with: `92.118.45.135`
6. Review changes in `.github/workflows/` directory
7. Commit to main branch

---

## 🎯 **SIMPLIFIED 2-MINUTE FIX**

**If you only want to fix the most critical workflow:**

1. Go to: `https://github.com/chavapalmarubin-lab/FIDUS/edit/main/.github/workflows/deploy-fresh-vps.yml`

2. Find this section:
```yaml
VPS_IP: "217.197.163.11"
```

3. Change to:
```yaml
VPS_IP: "${{ secrets.VPS_HOST }}"
```

4. Commit changes

**Done!** Your main deployment workflow now uses the new VPS.

---

## 🔐 **VERIFY GITHUB SECRETS (Already Done)**

Confirm these secrets are set correctly:

```bash
# Go to: https://github.com/chavapalmarubin-lab/FIDUS/settings/secrets/actions

✅ VPS_HOST = 92.118.45.135
✅ VPS_PORT = 42014
✅ VPS_USERNAME = trader
✅ VPS_PASSWORD = [encrypted]
```

---

## ✅ **VERIFICATION AFTER SYNC**

After updating the workflow files, verify the migration:

### **1. Test New VPS MT5 Bridge**
```bash
curl http://92.118.45.135:8000/api/mt5/bridge/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "mt5_available": true,
  "mt5_initialized": true,
  "accounts_connected": 7
}
```

### **2. Test Backend Proxy**
```bash
curl https://fidus-api.onrender.com/api/mt5/bridge/health
```

### **3. Trigger a Test Workflow**
```bash
# Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
# Click on "deploy-fresh-vps" workflow
# Click "Run workflow" dropdown
# Select "main" branch
# Click "Run workflow" button
```

### **4. Monitor Deployment**
- Watch the workflow run logs
- Verify it connects to `92.118.45.135` (not old IP)
- Check for successful completion

---

## 📊 **CURRENT STATUS**

### ✅ **Completed:**
- GitHub Secrets updated (VPS_HOST, VPS_PORT, VPS_USERNAME, VPS_PASSWORD)
- All backend code updated (15 files)
- Frontend code updated (1 file)
- Zero old VPS references in active code

### ⏳ **Pending:**
- Sync 17 workflow files to GitHub repository
- Verify end-to-end MT5 Bridge connectivity
- Test automated deployments

---

## 🚀 **RECOMMENDED ACTION**

**For fastest completion:**

1. **Use Method 1 (GitHub Web UI)** - Edit top 5 critical workflows directly
2. **Total time:** ~10 minutes
3. **Test immediately** with curl commands above

**OR**

**Use Method 3 (GitHub web editor)** - One global find/replace operation
- **Total time:** ~2 minutes
- **Most efficient for bulk changes**

---

## 📝 **WHY SAVE TO GITHUB FAILED**

The "Save to GitHub" feature detected the temporary Python script (`update_github_secrets.py`) that contained a GitHub token in plain text. This triggered GitHub's secret scanning protection.

**Resolution:**
- ✅ Sensitive file removed
- ✅ No secrets in codebase
- ✅ Safe to proceed with manual sync methods above

---

## ❓ **NEED HELP?**

If you encounter issues:

1. **Check GitHub Secrets:** Ensure all 4 secrets are properly set
2. **Verify Workflow Syntax:** Use GitHub Actions workflow validator
3. **Test VPS Connectivity:** Ensure `92.118.45.135:8000` is accessible
4. **Review Logs:** Check GitHub Actions logs for deployment errors

---

**Migration Status:** ✅ Code Ready | ⏳ Workflow Sync Pending | 🎯 Choose Method Above

**Estimated Time to Complete:** 2-10 minutes (depending on method chosen)
