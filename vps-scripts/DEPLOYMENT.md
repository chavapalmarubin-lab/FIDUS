# MT5 Full Restart System - Deployment Guide

## 🎯 Overview

This system enables **fully automated MT5 terminal restarts** without manual VPS access. Once deployed, the watchdog will detect MT5 disconnections (all accounts showing $0) and automatically restart everything.

---

## 📋 Prerequisites

- Windows VPS with MT5 terminals installed
- Python 3.8+ installed on VPS
- MetaTrader5 Python library installed
- Admin/RDP access to VPS (ONE TIME ONLY)

---

## 🚀 ONE-TIME DEPLOYMENT STEPS

### Step 1: Copy Script to VPS

1. **Connect to VPS via RDP**
2. **Create directory**: `C:\mt5-bridge\`
3. **Copy file**: `vps-scripts/mt5_full_restart.py` → `C:\mt5-bridge\mt5_full_restart.py`

```powershell
# In PowerShell on VPS:
mkdir C:\mt5-bridge
# Then copy the file via RDP
```

---

### Step 2: Configure Environment Variables

Create file: `C:\mt5-bridge\.env`

```env
# API Security
MT5_BRIDGE_API_KEY=your-secure-api-key-here

# MT5 Account Credentials (for reconnection)
MT5_886557_PASSWORD=password1
MT5_886557_SERVER=ICMarkets-Demo02

MT5_886066_PASSWORD=password2
MT5_886066_SERVER=ICMarkets-Demo02

MT5_886602_PASSWORD=password3
MT5_886602_SERVER=ICMarkets-Demo02

MT5_885822_PASSWORD=password4
MT5_885822_SERVER=ICMarkets-Demo02

MT5_886528_PASSWORD=password5
MT5_886528_SERVER=ICMarkets-Demo02

MT5_891215_PASSWORD=password6
MT5_891215_SERVER=ICMarkets-Demo02

MT5_891234_PASSWORD=password7
MT5_891234_SERVER=ICMarkets-Demo02
```

**⚠️ SECURITY NOTE**: Keep this `.env` file secure! It contains account credentials.

---

### Step 3: Update MT5 Terminal Path (if needed)

Open `C:\mt5-bridge\mt5_full_restart.py` and verify the path:

```python
MT5_TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
```

If your MT5 is installed elsewhere, update this path.

---

### Step 4: Install Python Dependencies

```powershell
# In PowerShell on VPS:
cd C:\mt5-bridge

# Install required packages
pip install fastapi uvicorn MetaTrader5 python-dotenv

# Or install from requirements:
pip install -r requirements.txt
```

Create `C:\mt5-bridge\requirements.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
MetaTrader5==5.0.45
python-dotenv==1.0.0
```

---

### Step 5: Test the Script Manually

```powershell
cd C:\mt5-bridge
python mt5_full_restart.py
```

This should start the service on port 8000. Test with:

```powershell
# In another PowerShell window:
curl http://localhost:8000/health
```

You should see: `{"status":"healthy","service":"mt5-full-restart"}`

**Press Ctrl+C to stop the test server.**

---

### Step 6: Create Windows Service (Run at Startup)

Create file: `C:\mt5-bridge\start-restart-service.ps1`

```powershell
# MT5 Full Restart Service Startup Script
cd C:\mt5-bridge

# Load environment variables
$envFile = "C:\mt5-bridge\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Start the service
python C:\mt5-bridge\mt5_full_restart.py
```

**Set to run at startup**:
1. Press `Win + R`, type `taskschd.msc`
2. Click **Create Task**
3. **General Tab**:
   - Name: `MT5 Full Restart Service`
   - Run whether user is logged on or not: ✓
   - Run with highest privileges: ✓
4. **Triggers Tab**:
   - New → At startup
5. **Actions Tab**:
   - New → Start a program
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File C:\mt5-bridge\start-restart-service.ps1`
6. **Click OK** and enter admin password

---

### Step 7: Add GitHub Secret

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `MT5_BRIDGE_API_KEY`
5. Value: (same key you put in `.env` file)
6. Click **Add secret**

---

### Step 8: Test End-to-End

**Manually trigger the workflow**:

1. Go to GitHub Actions
2. Find workflow: **MT5 Full System Restart**
3. Click **Run workflow** → **Run workflow**
4. Watch the logs to verify it works

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Script running as Windows service
- [ ] Service auto-starts on VPS reboot
- [ ] Health endpoint accessible: `http://localhost:8000/health`
- [ ] GitHub Actions can trigger restart successfully
- [ ] MT5 terminals restart and reconnect properly
- [ ] All 7 accounts show real balances after restart

---

## 🔧 Troubleshooting

### Service Won't Start

```powershell
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list | Select-String "fastapi|uvicorn|MetaTrader5"

# Check logs
Get-Content C:\mt5-bridge\mt5_restart.log -Tail 50
```

### MT5 Terminals Not Restarting

1. **Verify MT5 path is correct** in `mt5_full_restart.py`
2. **Check MT5 is not running as different user**
3. **Verify task runs with highest privileges**

### Accounts Still Show $0

1. **Check MT5 login credentials in `.env`**
2. **Verify MT5 server names are correct**
3. **Check MT5 terminals actually started** (look for `terminal64.exe` in Task Manager)

---

## 📊 How It Works After Deployment

```
1. Watchdog detects all accounts = $0
   ↓
2. Watchdog triggers GitHub Actions workflow
   ↓
3. GitHub Actions calls VPS endpoint: POST /api/system/full-restart
   ↓
4. VPS script:
   - Kills all MT5 processes
   - Waits 5 seconds
   - Starts MT5 terminals
   - Waits 15 seconds for initialization
   - Reconnects Bridge to MT5
   - Verifies account balances
   ↓
5. Returns success/failure to GitHub Actions
   ↓
6. GitHub Actions verifies each account
   ↓
7. System fully operational - NO MANUAL INTERVENTION NEEDED!
```

---

## 🎉 What Chava Gets

After this ONE-TIME deployment:

✅ **Never needs RDP access again**  
✅ **Automatic MT5 terminal restarts**  
✅ **Automatic reconnection verification**  
✅ **Email alerts if restart fails**  
✅ **Complete automation - zero manual work**

---

## 📞 Support

If you encounter issues during deployment:

1. Check logs: `C:\mt5-bridge\mt5_restart.log`
2. Verify environment variables are loaded
3. Test manual restart via API first
4. Check GitHub Actions workflow logs

---

## 🔄 Updating the Script

If you need to update the script later:

1. Copy new version to VPS
2. Restart the Windows service:

```powershell
Stop-ScheduledTask -TaskName "MT5 Full Restart Service"
Start-ScheduledTask -TaskName "MT5 Full Restart Service"
```

---

**Deployment complete! System is now fully automated.** 🚀
