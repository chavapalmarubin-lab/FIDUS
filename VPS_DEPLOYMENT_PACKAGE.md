# 🚀 COMPLETE VPS DEPLOYMENT PACKAGE

## 📦 **ALL FILES YOU NEED TO COPY TO VPS**

---

## **FILE 1: mt5_bridge_api_service.py**

**Location:** `C:\mt5_bridge_service\mt5_bridge_api_service.py`

**Content:** See below (547 lines)

---

## **FILE 2: requirements.txt**

**Location:** `C:\mt5_bridge_service\requirements.txt`

**Content:**
```
fastapi==0.115.0
uvicorn==0.30.6
pydantic==2.9.0
MetaTrader5==5.0.4508
pymongo==4.8.0
python-dotenv==1.0.1
cryptography==43.0.1
httpx==0.27.0
python-dateutil==2.8.2
```

---

## **FILE 3: .env**

**Location:** `C:\mt5_bridge_service\.env`

**Content:**
```
MONGODB_URI=mongodb+srv://fidus_admin:***SANITIZED***@fiduscluster.qscrf.mongodb.net/fidus_production?retryWrites=true&w=majority
MT5_PATH=C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe
MT5_SERVER=MEXAtlantic-Real
MT5_ACCOUNT=886557
MT5_PASSWORD=***SANITIZED***
```

---

## **FILE 4: start_mt5_bridge.bat** (Already created)

**Location:** `C:\mt5_bridge_service\start_mt5_bridge.bat`

**Content:**
```batch
@echo off
cd /d C:\mt5_bridge_service
SET PYTHON_PATH=C:\Users\Administrator\AppData\Local\Programs\Python\Python312
"%PYTHON_PATH%\python.exe" mt5_bridge_api_service.py >> logs\service_output.log 2>> logs\service_error.log
exit /b %ERRORLEVEL%
```

---

## 🎯 **STEP-BY-STEP DEPLOYMENT**

### **Step 1: Install Python Dependencies (5 min)**

Open PowerShell as Administrator on VPS:

```powershell
cd C:\mt5_bridge_service

# Install all required packages
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip install --upgrade pip
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe -m pip install -r requirements.txt
```

---

### **Step 2: Create .env File (2 min)**

1. Open Notepad on VPS
2. Copy the `.env` content from FILE 3 above
3. Save as: `C:\mt5_bridge_service\.env`
   - **IMPORTANT:** Save as type: "All Files"
   - File name must be exactly: `.env` (with the dot at the start)

---

### **Step 3: Create mt5_bridge_api_service.py (3 min)**

**OPTION A: Download from GitHub**
```powershell
cd C:\mt5_bridge_service
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/chavapalmarubin-lab/FIDUS/main/vps/mt5_bridge_api_service.py" -OutFile "mt5_bridge_api_service.py"
```

**OPTION B: Copy-Paste (if GitHub fails)**
1. I'll provide the full content in next message
2. Create file in Notepad
3. Save as: `C:\mt5_bridge_service\mt5_bridge_api_service.py`

---

### **Step 4: Test Service Manually (2 min)**

```powershell
cd C:\mt5_bridge_service
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe mt5_bridge_api_service.py
```

**Expected output:**
```
============================================================
FIDUS MT5 BRIDGE API SERVICE STARTING
============================================================
Time: 2025-10-21...
MT5 Path: C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe
MT5 Server: MEXAtlantic-Real
MongoDB: Connected
Port: 8000
============================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If running successfully, press Ctrl+C to stop, then continue to Step 5**

---

### **Step 5: Start Service via Task Scheduler**

```powershell
# Start the service
Start-ScheduledTask -TaskName "MT5BridgeService"

# Wait 10 seconds
Start-Sleep -Seconds 10

# Test the service
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing
```

**Expected response:**
```json
{
  "status": "healthy",
  "mt5": {
    "available": true
  },
  "mongodb": {
    "connected": true
  }
}
```

---

### **Step 6: Test from External**

From your local machine or Emergent's system:

```bash
curl http://92.118.45.135:8000/api/mt5/bridge/health
```

**Should return the same healthy response!**

---

## 🔍 **TROUBLESHOOTING**

### **If service doesn't start:**

**Check logs:**
```powershell
Get-Content C:\mt5_bridge_service\logs\service_error.log -Tail 50
```

**Common issues:**

1. **Python not found:**
   - Verify Python path: `Test-Path "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"`
   - If False, find Python: `Get-ChildItem -Path "C:\" -Recurse -Filter "python.exe" | Select-Object FullName`
   - Update `start_mt5_bridge.bat` with correct path

2. **Missing dependencies:**
   - Run: `pip install -r requirements.txt` again
   - Check for errors in pip install output

3. **MongoDB connection failed:**
   - Verify `.env` file exists and has correct MONGODB_URI
   - Test MongoDB: The service will show "MongoDB: Not Connected" if it fails

4. **MT5 not initializing:**
   - Ensure MT5 Terminal is installed
   - Verify path in `.env` file
   - MT5 account must be logged in (you confirmed: 886557 is logged in)

---

## ✅ **VERIFICATION CHECKLIST**

After deployment:

- [ ] Python dependencies installed
- [ ] `.env` file created with MongoDB URI
- [ ] `mt5_bridge_api_service.py` file present
- [ ] Service starts manually without errors
- [ ] Service accessible on localhost:8000
- [ ] Service accessible externally on 92.118.45.135:8000
- [ ] Health check returns "healthy" status
- [ ] Task Scheduler auto-starts service

---

## 📋 **QUICK REFERENCE**

**Service Files Location:** `C:\mt5_bridge_service\`

**Start Service:**
```powershell
Start-ScheduledTask -TaskName "MT5BridgeService"
```

**Stop Service:**
```powershell
Stop-ScheduledTask -TaskName "MT5BridgeService"
```

**View Logs:**
```powershell
Get-Content C:\mt5_bridge_service\logs\service_error.log -Tail 50
Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 50
```

**Test Service:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" -UseBasicParsing
```

---

## 🎉 **NEXT MESSAGE**

I'll provide the complete `mt5_bridge_api_service.py` file content in the next message for copy-paste!
