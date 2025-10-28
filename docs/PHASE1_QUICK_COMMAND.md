# 🚀 PHASE 1: Unicode Fix - Windows VPS (RDP Method)

## ⚡ FASTEST METHOD - Copy/Paste This One Command

**RDP to VPS** (92.118.45.135) and **run this in PowerShell (Admin)**:

```powershell
# MT5 Bridge Unicode Fix - One Command
cd C:\mt5_bridge_service
Stop-ScheduledTask -TaskName "MT5 Bridge Service" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*mt5_bridge_service*" } | Stop-Process -Force
Write-Host "[OK] Bridge stopped, running fix..." -ForegroundColor Green
python fix_unicode_logging.py
Start-Sleep -Seconds 3
Start-ScheduledTask -TaskName "MT5 Bridge Service"
Write-Host "[OK] Bridge restarted, waiting 15 seconds..." -ForegroundColor Green
Start-Sleep -Seconds 15
Invoke-WebRequest -Uri "http://localhost:8000/api/mt5/bridge/health" | Select-Object -ExpandProperty Content
Write-Host "[SUCCESS] PHASE 1 COMPLETE! Check output above." -ForegroundColor Green
```

**That's it!** The fix script (`fix_unicode_logging.py`) already exists on your VPS from previous deployments.

---

## 📋 What This Does

1. **Stops Bridge** - Gracefully stops the service
2. **Runs Fix** - Executes `fix_unicode_logging.py` (removes Unicode characters)
3. **Restarts Bridge** - Starts service with cleaned code
4. **Tests Health** - Verifies Bridge is running
5. **Reports Status** - Shows success/failure

**Time**: ~30 seconds

---

## ✅ Success Looks Like This

```json
{
  "status": "healthy",
  "mt5": {
    "available": true or false,  ← Both OK at Phase 1!
    "terminal_info": {...}
  },
  "mongodb": {
    "connected": true
  }
}
```

**Key Point**: `"available": false` is **NORMAL** after Phase 1. You need Phase 2 to enable MT5 connection.

---

## ❌ If You Get Errors

### Error: "File not found"

**Fix**: Download the script first:
```powershell
cd C:\mt5_bridge_service
$url = "https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/main/vps-scripts/fix_unicode_logging.py"
Invoke-WebRequest -Uri $url -OutFile "fix_unicode_logging.py"
# Then run the one-command fix above
```

### Error: "Task not found"

**Fix**: Bridge service name might be different:
```powershell
# Check actual task name
Get-ScheduledTask | Where-Object { $_.TaskName -like "*MT5*" }
# Use the correct name in commands above
```

### Error: "Cannot connect to health endpoint"

**Check**:
```powershell
# Is Bridge running?
Get-Process -Name python | Where-Object { $_.Path -like "*mt5_bridge_service*" }

# Check Task Scheduler status
Get-ScheduledTask -TaskName "MT5 Bridge Service" | Select-Object State
```

---

## 🎯 After Phase 1 Succeeds

**Report to me**:
- ✅ "Phase 1 done! Status: healthy, MT5 available: [true/false]"

**I'll provide**:
- Phase 2 commands (Task Scheduler fix)
- This enables real MT5 connection
- Dashboard will show real balances

---

## 📖 Detailed Guide

For step-by-step instructions with explanations, see:
→ `/docs/PHASE1_MANUAL_FIX.md`

---

**Ready? RDP to VPS and run the one command above!** 🚀

**VPS**: 92.118.45.135  
**User**: Administrator  
**Time**: 30 seconds  
**Risk**: Very low (automatic backup)
