# ⚡ QUICK START - MT4 Bridge Deployment

## 🎯 FASTEST WAY - Direct VPS Script (Recommended)

**Skip GitHub Actions entirely and run this directly on the VPS:**

### Step 1: RDP to VPS
- IP: `92.118.45.135`
- Username: `trader`
- Password: `9qvMclgO1El58W4`

### Step 2: Open PowerShell as Administrator
- Right-click PowerShell icon
- Select "Run as Administrator"

### Step 3: Download and Run Script
```powershell
# Download script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/DIRECT_VPS_DEPLOY.ps1" -OutFile "C:\DIRECT_VPS_DEPLOY.ps1"

# Run script
C:\DIRECT_VPS_DEPLOY.ps1
```

**OR** Copy the entire contents of `/app/DIRECT_VPS_DEPLOY.ps1` and paste directly into PowerShell.

### Step 4: After Script Completes

1. **Compile MT4 EA:**
   - Open MT4 Terminal
   - Press `F4` (MetaEditor)
   - Find `MT4_Python_Bridge.mq4`
   - Press `F7` to compile

2. **Attach EA:**
   - Drag EA onto any chart
   - ✓ Check "Allow DLL imports"
   - Click OK

3. **Start Service:**
   - Double-click: `C:\mt4_bridge_service\start_mt4_bridge.bat`

4. **Verify:**
   - Check MongoDB for document `_id: "MT4_33200931"`

---

## 🔄 Alternative - GitHub Actions (If Workflow Appears)

If you see "MT4 Bridge - Simple Deploy" in GitHub Actions:

1. Click "Run workflow"
2. Select "main" branch
3. Click green "Run workflow" button
4. Wait 5-10 minutes
5. Follow steps 1-4 above

---

## ✅ Success Criteria

- [ ] All files created in `C:\mt4_bridge_service\`
- [ ] MT4 EA compiles without errors
- [ ] Python service connects to MongoDB
- [ ] MT4 EA sends data every 5 minutes
- [ ] MongoDB document created with correct structure

---

## 🆘 If Issues Occur

Run this in PowerShell to verify installation:
```powershell
Write-Host "Checking installation..."
if (Test-Path "C:\mt4_bridge_service\mt4_bridge_api_service.py") { Write-Host "[OK] Python service" } else { Write-Host "[MISSING] Python service" }
if (Test-Path "C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Experts\MT4_Python_Bridge.mq4") { Write-Host "[OK] MT4 EA" } else { Write-Host "[MISSING] MT4 EA" }
if (Test-Path "C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Include\Zmq\Zmq.mqh") { Write-Host "[OK] ZeroMQ" } else { Write-Host "[MISSING] ZeroMQ" }
```

---

**This bypasses ALL GitHub Actions issues and deploys directly to VPS.**
