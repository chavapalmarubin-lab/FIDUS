# 🚀 NEW VPS SETUP GUIDE - QUICK START

## 📋 **FILES READY FOR YOU:**

✅ **Batch File Created:** `/app/start_mt5_bridge.bat`

---

## 🎯 **STEP-BY-STEP VPS SETUP (10 MINUTES)**

### **Step 1: Access VPS via RDP (1 min)**

```
Host: 92.118.45.135:3389
User: trader
Password: 4p1We0OHh3LKgm6
```

---

### **Step 2: Create Directory Structure (1 min)**

Open PowerShell as Administrator and run:

```powershell
# Create directories
New-Item -Path "C:\mt5_bridge_service" -ItemType Directory -Force
New-Item -Path "C:\mt5_bridge_service\logs" -ItemType Directory -Force

Write-Host "✅ Directories created" -ForegroundColor Green
```

---

### **Step 3: Copy Files to VPS (2 min)**

Copy these files from your local machine to `C:\mt5_bridge_service\`:

1. **`start_mt5_bridge.bat`** (from `/app/start_mt5_bridge.bat`)
2. **`mt5_bridge_api_service.py`** (from `/app/vps/mt5_bridge_api_service.py`)

**Quick Copy Method:**
- Open File Explorer on VPS
- Navigate to `C:\mt5_bridge_service\`
- Drag and drop the files

---

### **Step 4: Configure Firewall (2 min)**

In PowerShell (as Administrator):

```powershell
# Allow MT5 Bridge API on port 8000
New-NetFirewallRule -DisplayName "MT5 Bridge API" `
    -Direction Inbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow

# Allow SSH on port 42014 (for future remote access)
New-NetFirewallRule -DisplayName "SSH Custom Port" `
    -Direction Inbound `
    -LocalPort 42014 `
    -Protocol TCP `
    -Action Allow

Write-Host "✅ Firewall rules configured" -ForegroundColor Green
```

---

### **Step 5: Verify Python Installation (1 min)**

Check Python path:

```powershell
# Check if Python exists
Test-Path "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"

# If returns False, find Python:
Get-ChildItem -Path "C:\Users\Administrator\AppData\Local\Programs\Python\" -Recurse -Filter "python.exe" | Select-Object FullName
```

**If Python path is different:**
- Edit `start_mt5_bridge.bat`
- Update the `PYTHON_PATH` line with correct path

---

### **Step 6: Create Task Scheduler Task (3 min)**

**Option A: Using GUI (Recommended)**

1. Open **Task Scheduler** (search in Start menu)
2. Click **"Create Task"** (not "Create Basic Task")
3. **General Tab:**
   - Name: `MT5BridgeService`
   - Description: `MT5 Bridge API Service`
   - Select: **"Run whether user is logged on or not"**
   - Check: **"Run with highest privileges"**
   - Configure for: **Windows Server 2022**

4. **Triggers Tab:**
   - Click **"New..."**
   - Begin the task: **At startup**
   - Check: **Enabled**
   - Click **OK**

5. **Actions Tab:**
   - Click **"New..."**
   - Action: **Start a program**
   - Program/script: `C:\mt5_bridge_service\start_mt5_bridge.bat`
   - Start in: `C:\mt5_bridge_service`
   - Click **OK**

6. **Settings Tab:**
   - Check: **"Allow task to be run on demand"**
   - Check: **"Run task as soon as possible after a scheduled start is missed"**
   - Uncheck: **"Stop the task if it runs longer than"**
   - If the task fails, restart every: **5 minutes**
   - Attempt to restart up to: **3 times**
   - Click **OK**

7. Enter your password when prompted
8. Click **OK** to save

**Option B: Using PowerShell (Advanced)**

```powershell
# Create task
$action = New-ScheduledTaskAction -Execute "C:\mt5_bridge_service\start_mt5_bridge.bat" -WorkingDirectory "C:\mt5_bridge_service"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "trader" -LogonType Password -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartInterval (New-TimeSpan -Minutes 5) -RestartCount 3

Register-ScheduledTask -TaskName "MT5BridgeService" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "MT5 Bridge API Service" `
    -Force

Write-Host "✅ Task Scheduler configured" -ForegroundColor Green
```

---

### **Step 7: Start the Service (1 min)**

**Start manually to test:**

```powershell
# Start the task
Start-ScheduledTask -TaskName "MT5BridgeService"

Write-Host "⏳ Waiting 10 seconds for service to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test the service
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ SERVICE IS RUNNING!" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️ Service not responding yet" -ForegroundColor Yellow
    Write-Host "Check logs: C:\mt5_bridge_service\logs\service_error.log" -ForegroundColor Yellow
}
```

---

### **Step 8: Verify from External (1 min)**

**From Emergent's system (or your local machine):**

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

---

## 🔍 **TROUBLESHOOTING**

### **If Service Doesn't Start:**

1. **Check Error Logs:**
   ```powershell
   Get-Content "C:\mt5_bridge_service\logs\service_error.log" -Tail 50
   ```

2. **Verify Python Path:**
   ```powershell
   & "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" --version
   ```

3. **Test Script Manually:**
   ```powershell
   cd C:\mt5_bridge_service
   & "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" mt5_bridge_api_service.py
   ```

4. **Check Task Scheduler:**
   - Open Task Scheduler
   - Find `MT5BridgeService`
   - Check "Last Run Result" (should be 0x0 for success)
   - View "History" tab for errors

---

## 📊 **VERIFICATION CHECKLIST**

After setup, verify:

- [ ] Service responds: `http://localhost:8000/api/mt5/bridge/health`
- [ ] External access: `http://92.118.45.135:8000/api/mt5/bridge/health`
- [ ] Task Scheduler shows task running
- [ ] Backend can reach VPS: Test via Render backend
- [ ] MT5 accounts syncing to MongoDB

---

## 🎯 **QUICK COMMANDS REFERENCE**

```powershell
# Start service
Start-ScheduledTask -TaskName "MT5BridgeService"

# Stop service
Stop-ScheduledTask -TaskName "MT5BridgeService"

# Check if running
Get-ScheduledTask -TaskName "MT5BridgeService" | Select-Object State

# View logs
Get-Content "C:\mt5_bridge_service\logs\service_output.log" -Tail 50
Get-Content "C:\mt5_bridge_service\logs\service_error.log" -Tail 50

# Test service
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing

# Restart service
Stop-ScheduledTask -TaskName "MT5BridgeService"
Start-Sleep -Seconds 2
Start-ScheduledTask -TaskName "MT5BridgeService"
```

---

## 🎉 **AFTER SUCCESSFUL SETUP**

Once the service is running, notify Emergent to run final verification:

1. Test MT5 Bridge health
2. Verify backend proxy
3. Check MongoDB sync
4. Confirm MT5 Watchdog monitoring new VPS
5. Validate end-to-end data flow

**Estimated Setup Time:** 10 minutes  
**Estimated Total Migration Time:** ~45 minutes (Infrastructure + VPS Setup)

---

## 📝 **NOTES**

- Batch file path: `/app/start_mt5_bridge.bat` (ready to copy)
- Python script: `/app/vps/mt5_bridge_api_service.py` (ready to copy)
- This VPS is clean - no legacy services or conflicts
- Task Scheduler will auto-start service on reboot
- Firewall configured for ports 8000 (API) and 42014 (SSH)

---

**Good luck with the setup! Let Emergent know when service is running!** 🚀
