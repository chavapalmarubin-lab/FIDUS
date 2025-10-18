# MT5 Bridge 404 Fixes - Deployment Guide

## Issue Summary
The MT5 Bridge on VPS (217.197.163.11:8000) was returning 404 errors for all account endpoints because the service was **NOT a REST API** - it was just a data sync script with no HTTP server.

## Root Cause
- ❌ Old service: `mt5_bridge_service_production.py` - sync script only, no API endpoints
- ✅ New service: `mt5_bridge_api_service.py` - FastAPI REST API with all endpoints

## Files Created/Modified

### 1. NEW: MT5 Bridge API Service (VPS)
**File**: `/vps/mt5_bridge_api_service.py`
- ✅ Complete FastAPI REST API service
- ✅ Runs on port 8000
- ✅ All 6 missing endpoints added:
  - `/api/mt5/bridge/health`
  - `/api/mt5/status`
  - `/api/mt5/account/{id}/info`
  - `/api/mt5/account/{id}/balance`
  - `/api/mt5/account/{id}/trades`
  - `/api/mt5/accounts/summary`
  - `/api/mt5/admin/system-status`

### 2. NEW: Startup Script (VPS)
**File**: `/vps/run_api_service.bat`
- Windows batch script to start the FastAPI service
- Sets up venv and installs dependencies
- Runs `mt5_bridge_api_service.py`

### 3. UPDATED: Requirements (VPS)
**File**: `/vps/requirements.txt`
- Updated to latest FastAPI 0.115.0
- Updated to latest uvicorn 0.30.6
- Added httpx 0.27.0
- All required dependencies

### 4. NEW: Backend Proxy Routes
**File**: `/backend/routes/mt5_bridge_proxy.py`
- Proxies all requests from FIDUS backend to VPS MT5 Bridge
- Proper error handling and logging
- Uses httpx for async HTTP requests

### 5. UPDATED: Backend Server
**File**: `/backend/server.py`
- Added import for `mt5_bridge_proxy_router`
- Registered the router with FastAPI

## Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Fix: Add MT5 Bridge REST API service with all missing endpoints"
git push origin main
```

### Step 2: Deploy to VPS (via GitHub Actions or Manual)

#### Option A: Automatic (GitHub Actions)
The `.github/workflows/deploy-vps.yml` will automatically:
1. Pull latest code from GitHub
2. Copy new files to `C:\mt5_bridge_service\`
3. Restart the service

#### Option B: Manual Deployment
On the VPS (217.197.163.11), open PowerShell:

```powershell
# Navigate to service directory
cd C:\mt5_bridge_service

# Pull latest code (if GitHub is set up)
git pull origin main

# Copy new files from vps/ folder
copy mt5_bridge_api_service.py .
copy requirements.txt .
copy run_api_service.bat .

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Stop old service (if running)
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start new API service
.\run_api_service.bat
```

### Step 3: Verify Endpoints on VPS

Test locally on the VPS:
```powershell
# Health check
curl http://localhost:8000/api/mt5/bridge/health

# Status
curl http://localhost:8000/api/mt5/status

# Account info
curl http://localhost:8000/api/mt5/account/886602/info

# Accounts summary
curl http://localhost:8000/api/mt5/accounts/summary
```

### Step 4: Test from Backend

Once VPS service is running, test from backend:
```bash
# From your local machine or backend server
curl https://your-backend-url.com/api/mt5/bridge/health
curl https://your-backend-url.com/api/mt5/status
curl https://your-backend-url.com/api/mt5/account/886602/info
```

### Step 5: Monitor Logs

On VPS, check logs:
```powershell
Get-Content C:\mt5_bridge_service\logs\api_service.log -Tail 50 -Wait
```

## Expected Results

After deployment:
- ✅ All 6 endpoints return 200 OK (instead of 404)
- ✅ Health check shows "healthy" status
- ✅ Account info returns real-time MT5 data
- ✅ 100% endpoint success rate (up from 66.7%)
- ✅ MT5 sync success rate: 7/7 accounts (up from 0/7)

## Verification Checklist

- [ ] VPS: MT5 Bridge API service running on port 8000
- [ ] VPS: `/api/mt5/bridge/health` returns "healthy"
- [ ] VPS: `/api/mt5/status` returns account list
- [ ] VPS: `/api/mt5/account/886602/info` returns account data
- [ ] Backend: All proxy endpoints return 200 OK
- [ ] Backend logs: No more 404 errors for MT5 endpoints
- [ ] MT5 auto-sync: 7/7 accounts syncing successfully

## Troubleshooting

### Issue: Port 8000 already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual ID)
taskkill /PID <PID> /F
```

### Issue: MT5 Terminal not initialized
- Check MT5 Path in `.env`: `MT5_PATH=C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe`
- Verify MT5 Terminal is installed and running
- Check MT5 Terminal logs

### Issue: MongoDB connection failed
- Verify `MONGODB_URI` in `.env` file
- Test MongoDB connection: `mongo "your-connection-string"`
- Check firewall rules

### Issue: Backend can't reach VPS
- Check if port 8000 is open on ForexVPS firewall
- Test connectivity: `curl http://217.197.163.11:8000/api/mt5/bridge/health`
- Contact ForexVPS support to open port 8000

## Service Management

### Start Service
```powershell
cd C:\mt5_bridge_service
.\run_api_service.bat
```

### Stop Service
```powershell
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Restart Service
```powershell
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
.\run_api_service.bat
```

### Auto-Start on Boot (Windows Task Scheduler)
Create a scheduled task:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `C:\mt5_bridge_service\run_api_service.bat`
6. Check "Run with highest privileges"

## Next Steps

1. **Deploy to VPS** - Follow deployment steps above
2. **Test Endpoints** - Verify all endpoints return 200 OK
3. **Monitor Performance** - Check MT5 sync success rate
4. **Update Documentation** - Document any VPS-specific configurations
5. **Set Up Monitoring** - Add health check alerts

## Support

If issues persist after deployment:
1. Check VPS logs: `C:\mt5_bridge_service\logs\api_service.log`
2. Check backend logs for proxy errors
3. Verify MT5 Terminal is running
4. Test MongoDB connectivity
5. Contact ForexVPS support for port 8000 access

---

**Status**: Ready for deployment
**Priority**: HIGH - This fixes critical MT5 data sync issues
**Estimated Time**: 15-30 minutes for deployment and verification
