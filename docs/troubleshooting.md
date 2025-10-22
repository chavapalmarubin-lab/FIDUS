# FIDUS Troubleshooting Guide

**Last Updated:** October 21, 2025  
**Infrastructure:** Post-VPS Migration (NEW VPS: 92.118.45.135)

---

## 🚨 Common Issues & Solutions

### 1. MT5 Data Not Syncing

**Symptoms:**
- Dashboard shows stale data (timestamps > 15 minutes old)
- MT5 accounts not updating
- "Data freshness" warnings in logs

**Solution Steps:**

#### Check 1: VPS Service Status
```powershell
# RDP to NEW VPS: 92.118.45.135:42014
# Check if Python service is running:
Get-Process python

# Expected: At least one python.exe process running
```

#### Check 2: MT5 Bridge API Health
```bash
# From your local machine or backend:
curl http://92.118.45.135:8000/api/mt5/bridge/health

# Expected response:
{
  "status": "healthy",
  "mongodb": {
    "connected": true,
    "database": "fidus_production"
  },
  "mt5": {
    "connected": true,
    "accounts_count": 7
  }
}
```

#### Check 3: Backend to Bridge Connection
```bash
# Check backend logs:
sudo tail -100 /var/log/supervisor/backend.err.log | grep "MT5 WATCHDOG"

# Look for:
# - "✅ MT5 Bridge recovered"
# - "⚠️ MT5 Bridge unhealthy"
```

#### Check 4: MongoDB Connection
```bash
# Verify cluster name is correct (common typo: y1p9be2 not ylp9be2)
grep "MONGO_URL" /app/backend/.env

# Should show: fidus.y1p9be2.mongodb.net
```

#### Check 5: MT5 Terminal Status
```powershell
# On VPS, check if MT5 is logged in:
# Open MT5 Terminal → Check if accounts show "Connected" status
# Common issue: MT5 needs re-login after Windows updates
```

---

### 2. Auto-Healing Not Working

**Symptoms:**
- Watchdog detects failures but doesn't trigger recovery
- No GitHub Actions workflow runs
- Email alerts say "auto-healing failed"

**Solution Steps:**

#### Check 1: GitHub Token Configuration
```bash
# Verify token is set in backend:
grep "GITHUB_TOKEN" /app/backend/.env

# Should show: GITHUB_TOKEN="ghp_..."
# If empty, watchdog cannot trigger workflows
```

#### Check 2: GitHub Workflow Permissions
1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/settings/secrets/actions
2. Verify these secrets exist:
   - `VPS_HOST` = 92.118.45.135
   - `VPS_USERNAME` = trader
   - `VPS_PASSWORD` = [your VPS password]
   - `VPS_PORT` = 42014

#### Check 3: Manual Workflow Test
1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
2. Select "MT5 Bridge Emergency Restart (NEW VPS)"
3. Click "Run workflow"
4. Check if it completes successfully

#### Check 4: Watchdog Status
```bash
# Call watchdog status API:
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://fidus-api.onrender.com/api/system/mt5-watchdog/status

# Check:
# - github_token_configured: true
# - consecutive_failures: should reset to 0 after healing
```

---

### 3. Backend API Returning 404 Errors

**Symptoms:**
- Specific MT5 endpoints return 404
- "Not Found" errors in frontend
- Postman shows 404 for valid endpoints

**Solution Steps:**

#### Check 1: Verify Endpoint Exists
```bash
# Check if route is registered:
grep "mt5-watchdog" /app/backend/server.py

# All MT5 endpoints should have /api prefix
```

#### Check 2: Backend Service Running
```bash
sudo supervisorctl status backend

# Should show: RUNNING
# If not, restart:
sudo supervisorctl restart backend
```

#### Check 3: Check Recent Code Changes
```bash
# If 404 appeared after deployment:
git log --oneline -10

# Rollback if needed:
git checkout <previous-commit-hash>
sudo supervisorctl restart backend
```

---

### 4. MongoDB Connection Failures

**Symptoms:**
- "MongoDB connection error" in logs
- Backend health check fails
- Data not persisting

**Solution Steps:**

#### Check 1: Network Access (MongoDB Atlas)
1. Go to MongoDB Atlas → Network Access
2. Verify these IPs are whitelisted:
   - **NEW VPS:** 92.118.45.135/32 (FIDUS VPS)
   - **Render Backend:** Check current IP in Render dashboard
3. Remove old IP if present:
   - ❌ **OLD VPS:** 217.197.163.11/32 (deprecated)

#### Check 2: Connection String
```bash
# Verify cluster name in connection string:
grep "MONGO_URL" /app/backend/.env

# CORRECT: mongodb+srv://...@fidus.y1p9be2.mongodb.net/...
# WRONG: mongodb+srv://...@fidus.ylp9be2.mongodb.net/... (note: y1p9be2 not ylp9be2)
```

#### Check 3: Test Connection
```python
# From backend container:
python3 -c "
from pymongo import MongoClient
import os
url = os.getenv('MONGO_URL')
client = MongoClient(url)
print(client.server_info())
"
```

---

### 5. Email Alerts Not Sending

**Symptoms:**
- No critical alerts received
- Watchdog logs say "alert sent" but email doesn't arrive
- SMTP errors in logs

**Solution Steps:**

#### Check 1: SMTP Configuration
```bash
grep "SMTP" /app/backend/.env

# Should show:
# SMTP_USERNAME=chavapalmarubin@gmail.com
# SMTP_APP_PASSWORD=[app-specific password]
# ALERT_RECIPIENT_EMAIL=chavapalmarubin@gmail.com
```

#### Check 2: Gmail App Password
1. The password should be an "App Password", not your regular Gmail password
2. Generate new one: https://myaccount.google.com/apppasswords
3. Update in .env if needed

#### Check 3: Test Email Manually
```python
# From backend:
python3 /app/backend/test_email_alert.py
```

#### Check 4: Check Spam Folder
- Critical alerts might be marked as spam
- Add "no-reply@fidus-platform.com" to contacts

---

### 6. Frontend Shows Old Data or Broken UI

**Symptoms:**
- Dashboard displays outdated information
- UI components not loading
- "Cannot connect to backend" errors

**Solution Steps:**

#### Check 1: Hard Refresh Frontend
- Chrome/Edge: Ctrl + Shift + R
- Safari: Cmd + Shift + R
- This clears cached JavaScript/CSS

#### Check 2: Verify Backend URL
```javascript
// In browser console (F12):
console.log(process.env.REACT_APP_BACKEND_URL);

// Should show: https://fidus-api.onrender.com
```

#### Check 3: Check CORS Configuration
```bash
# In backend server.py, verify CORS allows frontend domain:
grep "allow_origins" /app/backend/server.py

# Should include: "https://fidus-investment-platform.onrender.com"
```

#### Check 4: Backend Health
```bash
curl https://fidus-api.onrender.com/health

# Should return 200 OK with system status
```

---

## 🛠️ Emergency Procedures

### Emergency 1: Complete MT5 Bridge Failure

**When to use:** Auto-healing has failed 3+ times, manual intervention needed

**Steps:**
1. **RDP to VPS:** 92.118.45.135:42014
2. **Stop all Python processes:**
   ```powershell
   Get-Process python | Stop-Process -Force
   ```
3. **Check port 8000:**
   ```powershell
   Get-NetTCPConnection -LocalPort 8000
   # If occupied, kill the process
   ```
4. **Restart service manually:**
   ```powershell
   cd C:\mt5_bridge_service
   python mt5_bridge_api_service.py
   ```
5. **Verify health:**
   ```powershell
   Invoke-WebRequest http://localhost:8000/api/mt5/bridge/health
   ```

### Emergency 2: Database Completely Inaccessible

**When to use:** MongoDB Atlas down or connection impossible

**Steps:**
1. **Check MongoDB Atlas Status:** https://status.mongodb.com/
2. **Verify network access in Atlas:** Add current IPs
3. **Test from VPS:**
   ```powershell
   # On VPS, test MongoDB connection
   python -c "from pymongo import MongoClient; print(MongoClient('YOUR_MONGO_URL').server_info())"
   ```
4. **Fallback:** Backend has cached data for 15 minutes

### Emergency 3: Backend API Completely Down

**When to use:** Render.com backend service crashed or unresponsive

**Steps:**
1. **Check Render Dashboard:** https://dashboard.render.com/
2. **View Recent Logs:** Check for Python exceptions
3. **Manual Redeploy:**
   - Go to Render dashboard
   - Click "Manual Deploy" → Deploy latest commit
4. **Rollback if needed:**
   - Select previous successful deployment
   - Click "Rollback to this version"

---

## 📞 Support Contacts

### Primary Contact
- **Email:** chavapalmarubin@gmail.com
- **For:** All technical issues, infrastructure problems

### Service Providers
- **Render.com Support:** support@render.com
- **MongoDB Atlas Support:** https://support.mongodb.com/
- **ForexVPS Support:** support@forexvps.com

---

## 📝 Logging & Debugging

### Backend Logs
```bash
# View live logs:
sudo tail -f /var/log/supervisor/backend.err.log

# Search for specific errors:
sudo grep "ERROR" /var/log/supervisor/backend.err.log | tail -50

# Watchdog-specific logs:
sudo grep "MT5 WATCHDOG" /var/log/supervisor/backend.err.log | tail -20
```

### VPS Logs
```powershell
# On VPS (C:\mt5_bridge_service):
Get-Content logs\service.log -Tail 50
Get-Content logs\error.log -Tail 50

# Real-time monitoring:
Get-Content logs\service.log -Wait
```

### Frontend (Browser Console)
```javascript
// Open Developer Tools (F12) → Console
// Look for:
// - Network errors (failed API calls)
// - JavaScript exceptions
// - CORS errors
```

---

## 🔍 Health Check URLs

Use these to quickly verify system status:

| Component | Health Check URL | Expected Response |
|-----------|------------------|-------------------|
| Backend API | https://fidus-api.onrender.com/health | HTTP 200, {"status":"healthy"} |
| MT5 Bridge | http://92.118.45.135:8000/api/mt5/bridge/health | HTTP 200, {"status":"healthy"} |
| Watchdog | https://fidus-api.onrender.com/api/system/mt5-watchdog/status | HTTP 200, {"watchdog_enabled":true} |
| MongoDB | N/A (internal) | Check via backend /health endpoint |

---

**Last Resort:** If all troubleshooting fails, contact chavapalmarubin@gmail.com with:
- Description of the issue
- Screenshots of errors
- Recent logs (backend.err.log, VPS service.log)
- Steps already attempted
