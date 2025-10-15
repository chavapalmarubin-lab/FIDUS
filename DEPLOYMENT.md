# FIDUS Deployment Guide

## Overview
This document describes the automated deployment pipeline for the FIDUS Investment Platform, including backend, frontend, and VPS MT5 bridge components.

---

## Architecture

```
GitHub Repository (main branch)
    |
    ├─→ Backend Changes → GitHub Actions → Render.com → https://fidus-api.onrender.com
    |
    ├─→ Frontend Changes → GitHub Actions → Emergent.host → https://fidus-invest.emergent.host
    |
    └─→ VPS Changes → GitHub Actions → VPS Auto-Update → C:\mt5_bridge_service
```

---

## Automated Deployments

### Backend (FastAPI)
- **Trigger**: Push to `main` branch with changes in `backend/` directory
- **Target**: Render.com
- **URL**: https://fidus-api.onrender.com
- **Workflow**: `.github/workflows/deploy-backend.yml`
- **Duration**: ~2 minutes
- **Health Check**: https://fidus-api.onrender.com/api/health

**Process:**
1. Detect changes in `backend/` directory
2. Trigger Render deployment via webhook
3. Wait 60 seconds for deployment
4. Verify health endpoint returns 200 OK
5. Test Phase 4A endpoints (`/api/mt5/deals`, `/api/mt5/rebates`)

### Frontend (React)
- **Trigger**: Push to `main` branch with changes in `frontend/` directory
- **Target**: Emergent.host
- **URL**: https://fidus-invest.emergent.host
- **Workflow**: `.github/workflows/deploy-frontend.yml`
- **Duration**: ~3-5 minutes

**Process:**
1. Detect changes in `frontend/` directory
2. Trigger Emergent.host deployment (auto-detected)
3. Wait 90 seconds for build
4. Verify homepage is accessible

### VPS MT5 Bridge
- **Trigger**: Push to `main` branch with changes in `vps/` or `mt5_bridge_service/` directories
- **Target**: VPS 217.197.163.11
- **Auto-updates**: Every 5 minutes before sync
- **Workflow**: `.github/workflows/deploy-vps.yml`
- **Duration**: <1 minute (update detection), 5 minutes max (next sync)

**Process:**
1. Detect changes in VPS-related directories
2. VPS auto-update script checks GitHub every 5 minutes
3. If new commit detected:
   - Backup current script
   - Pull latest code
   - Use new code on next run
4. Clean up old backups (keep last 5)

---

## Manual Deployment

### Trigger Specific Workflow

**Via GitHub UI:**
1. Go to: https://github.com/chavany2025/fidus-investment-platform/actions
2. Select desired workflow:
   - "Deploy Backend to Render"
   - "Deploy Frontend to Emergent.host"
   - "Update VPS MT5 Bridge"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow" button

**Via GitHub CLI:**
```bash
# Install GitHub CLI: https://cli.github.com/

# Trigger backend deployment
gh workflow run deploy-backend.yml

# Trigger frontend deployment
gh workflow run deploy-frontend.yml

# Trigger VPS update
gh workflow run deploy-vps.yml
```

### Manual Backend Deployment (Render)
```bash
# Option 1: Via webhook
curl -X POST "$RENDER_DEPLOY_HOOK"

# Option 2: Via Render dashboard
# Go to: https://dashboard.render.com
# Select: fidus-api service
# Click: "Manual Deploy" → Deploy latest commit
```

### Manual Frontend Deployment (Emergent.host)
```bash
# Frontend auto-deploys on Git push
# No manual intervention needed

# To verify deployment:
curl -I https://fidus-invest.emergent.host
# Should return: HTTP/2 200
```

### Manual VPS Update
```powershell
# RDP to VPS: 217.197.163.11
# Username: Administrator
# Password: 2170Tenoch!

# Navigate to bridge directory
cd C:\mt5_bridge_service

# Pull latest code
git pull origin main

# Verify update
git log -1

# Manual restart (if needed)
# Open Task Scheduler → Find bridge task → Right-click → Run
```

---

## Rollback Procedures

### Rollback Backend
```bash
# Via Render dashboard:
# 1. Go to: https://dashboard.render.com
# 2. Select: fidus-api service
# 3. Click: "Rollback" next to a previous deployment
# 4. Confirm rollback

# Via Git revert:
git revert <commit-hash>
git push origin main
# Automatically triggers new deployment
```

### Rollback Frontend
```bash
# Via Git revert:
git revert <commit-hash>
git push origin main
# Automatically triggers new build

# Via Emergent dashboard:
# Contact Emergent support for rollback options
```

### Rollback VPS
```powershell
# RDP to VPS

# Option 1: Use automatic backup
cd C:\mt5_bridge_service
Get-ChildItem *.backup.* | Sort-Object LastWriteTime -Descending | Select-Object -First 5
Copy-Item "mt5_bridge_service_production.py.backup.YYYYMMDD_HHMMSS" mt5_bridge_service_production.py

# Option 2: Git checkout previous commit
git log --oneline -10
git checkout <commit-hash> vps/mt5_bridge_service_production.py
Copy-Item vps\mt5_bridge_service_production.py . -Force

# Verify rollback
git log -1
```

---

## Monitoring

### GitHub Actions
- **URL**: https://github.com/chavany2025/fidus-investment-platform/actions
- **Check**: All workflows should show green checkmarks ✅
- **Alerts**: Email notifications on workflow failures

### Backend Health
```bash
# Health check endpoint
curl https://fidus-api.onrender.com/api/health

# Expected response:
{
  "status": "healthy",
  "mongodb": "connected",
  "timestamp": "2025-01-15T14:30:00Z"
}

# Phase 4A endpoints
curl https://fidus-api.onrender.com/api/mt5/deals?limit=1
curl https://fidus-api.onrender.com/api/mt5/rebates
curl https://fidus-api.onrender.com/api/mt5/analytics/performance
```

### Frontend Health
```bash
# Check homepage
curl -I https://fidus-invest.emergent.host

# Should return: HTTP/2 200

# Check in browser:
# https://fidus-invest.emergent.host
# Should load dashboard without errors
```

### VPS Health
```powershell
# RDP to VPS

# Check auto-update log
Get-Content C:\mt5_bridge_service\logs\auto_update.log -Tail 20

# Check service output
Get-Content C:\mt5_bridge_service\logs\service_output.log -Tail 50

# Check service errors
Get-Content C:\mt5_bridge_service\logs\service_error.log -Tail 20

# Check Task Scheduler
taskschd.msc
# Find bridge task → Check "Last Run Result" (should be 0x0 = success)

# Expected log entries:
# ✅ MongoDB connected successfully
# ✅ Collected XXX deals for account XXXXXX
# ✅ Deal sync complete: XXXX deals processed
```

### MongoDB Data
```javascript
// Connect to MongoDB Atlas
// https://cloud.mongodb.com

// Check deal history
use fidus_production
db.mt5_deals_history.countDocuments()
// Should have 500-5000+ deals

// Check recent deals
db.mt5_deals_history.find().sort({time: -1}).limit(10)

// Check deals per account
db.mt5_deals_history.aggregate([
  { $group: { _id: "$account_number", count: { $sum: 1 } } }
])
// Should show all 7 accounts
```

---

## Configuration

### GitHub Secrets
**Location**: https://github.com/chavany2025/fidus-investment-platform/settings/secrets/actions

**Required Secrets:**
- `RENDER_DEPLOY_HOOK` - Backend deployment webhook URL
- `RENDER_DEPLOY_HOOK_FRONTEND` - Frontend deployment webhook URL
- `VPS_HOST` - VPS IP address (217.197.163.11)
- `VPS_USERNAME` - VPS username (Administrator)
- `VPS_PASSWORD` - VPS password
- `MONGODB_URI` - MongoDB connection string

**How to Add Secret:**
1. Go to repository Settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Enter name and value
5. Click "Add secret"

### Environment Variables

**Backend (.env):**
```bash
MONGO_URL=mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.ylp9be2.mongodb.net/fidus_production
PORT=8001
```

**Frontend (.env):**
```bash
REACT_APP_BACKEND_URL=https://fidus-api.onrender.com
```

**VPS (.env):**
```bash
MONGODB_URI=mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.ylp9be2.mongodb.net/fidus_production
MT5_PATH=C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe
UPDATE_INTERVAL=300
DEAL_SYNC_INTERVAL=86400
INITIAL_BACKFILL_DAYS=90
```

---

## Troubleshooting

### Backend Deployment Fails
**Symptoms:**
- GitHub Actions workflow shows red ❌
- Health check returns non-200 status

**Solutions:**
1. Check GitHub Actions logs for error details
2. Check Render deployment logs:
   - Go to: https://dashboard.render.com
   - Select: fidus-api service
   - Click: "Logs" tab
3. Common issues:
   - MongoDB connection failure → Check `MONGO_URL` env var
   - Dependencies not installed → Check `requirements.txt`
   - Port binding issue → Check `PORT` env var

### Frontend Deployment Fails
**Symptoms:**
- Website shows old version
- Console errors in browser

**Solutions:**
1. Check Emergent dashboard for build status
2. Hard refresh browser (Ctrl+Shift+R)
3. Check for JavaScript errors in console
4. Verify `REACT_APP_BACKEND_URL` in `.env`

### VPS Update Fails
**Symptoms:**
- Auto-update log shows errors
- Old code still running

**Solutions:**
1. RDP to VPS
2. Check auto-update log:
   ```powershell
   Get-Content C:\mt5_bridge_service\logs\auto_update.log -Tail 50
   ```
3. Common issues:
   - Git not found → Install Git
   - Merge conflict → Reset to remote: `git reset --hard origin/main`
   - Permission denied → Run as Administrator
4. Manual pull:
   ```powershell
   cd C:\mt5_bridge_service
   git pull origin main
   ```

### No Deal Data in Dashboards
**Symptoms:**
- Dashboards show "No data available"
- Charts are empty

**Solutions:**
1. Check VPS bridge is running:
   ```powershell
   # Open Task Scheduler
   # Check bridge task status
   ```
2. Check MongoDB has deal data:
   ```javascript
   db.mt5_deals_history.countDocuments()
   ```
3. Check backend API returns data:
   ```bash
   curl https://fidus-api.onrender.com/api/mt5/deals?limit=1
   ```
4. Check browser console for API errors
5. Verify VPS has completed initial 90-day backfill

---

## Best Practices

### Before Pushing to Main
```bash
# 1. Test changes locally
npm test  # or pytest

# 2. Check code quality
npm run lint  # or flake8

# 3. Review changes
git diff

# 4. Commit with descriptive message
git commit -m "feat: Add broker rebates calculator"

# 5. Push to main
git push origin main

# 6. Monitor GitHub Actions
# Check: https://github.com/.../actions
```

### Code Review
- Create pull requests for major changes
- Review before merging to `main`
- Automated deployments only trigger on `main` branch

### Testing
- Test in development environment first
- Use feature branches for new features
- Merge to `main` only when stable

### Monitoring
- Check GitHub Actions daily
- Monitor backend health endpoint
- Review VPS logs weekly
- Check MongoDB data freshness

---

## Support

### For Deployment Issues:
- **GitHub Actions**: Check workflow logs
- **Render**: https://dashboard.render.com (support chat available)
- **Emergent**: Contact Emergent support
- **VPS**: RDP access for troubleshooting

### For Code Issues:
- Check application logs
- Review recent commits
- Test locally before deploying
- Use rollback if needed

### Emergency Contacts:
- **Chava**: chavapalmarubin@gmail.com
- **Render Support**: support@render.com
- **Emergent Support**: [via dashboard]

---

## Changelog

### 2025-01-15 - Phase 4A Deployment
- ✅ Added GitHub Actions workflows
- ✅ Implemented VPS auto-update
- ✅ Enhanced MT5 bridge with deal history
- ✅ Deployed 6 new backend API endpoints
- ✅ Deployed 4 enhanced frontend components
- ✅ Deployed new Broker Rebates component

---

**Last Updated**: January 15, 2025  
**Version**: 1.0 - Phase 4A Complete
