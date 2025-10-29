# COMPLETE MT5 BRIDGE DEPLOYMENT - READY TO DEPLOY

## CURRENT STATUS ✅

**Bridge Script Ready**: `/app/vps-scripts/mt5_bridge_complete.py`
- ✅ All endpoints implemented
- ✅ Single-connection method (no account switching)
- ✅ Proper caching mechanism
- ✅ Background refresh task

**Deployment Workflow Ready**: `/app/.github/workflows/deploy-complete-bridge.yml`
- ✅ SSH-based deployment (no PowerShell needed)
- ✅ Automatic service stop/start
- ✅ File backup before deployment
- ✅ Comprehensive endpoint testing
- ✅ Detailed logging

## ENDPOINTS TO BE DEPLOYED

### Currently Missing (404):
- ❌ `GET /api/mt5/accounts/summary` - Returns all 7 account summaries
- ❌ `GET /api/mt5/account/{id}/trades?limit=100` - Returns historical trades

### Already Working:
- ✅ `GET /api/mt5/bridge/health` - Health check
- ✅ `GET /api/mt5/account/{id}/info` - Single account info

### After Deployment (ALL will work):
- ✅ `GET /api/mt5/bridge/health`
- ✅ `GET /api/mt5/accounts/summary` (NEW)
- ✅ `GET /api/mt5/account/{id}/info`  
- ✅ `GET /api/mt5/account/{id}/trades?limit=100` (NEW)

## HOW TO DEPLOY (3 OPTIONS)

### Option 1: GitHub Actions Web UI (RECOMMENDED)
1. Go to: `https://github.com/<your-repo>/actions/workflows/deploy-complete-bridge.yml`
2. Click "Run workflow" button
3. Leave "test_endpoints" as `true`
4. Click "Run workflow" 
5. Wait ~60 seconds for completion
6. Check logs for success messages

### Option 2: GitHub CLI (if installed)
```bash
gh workflow run deploy-complete-bridge.yml
```

### Option 3: GitHub API (curl)
```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR_GITHUB_TOKEN>" \
  https://api.github.com/repos/<OWNER>/<REPO>/actions/workflows/deploy-complete-bridge.yml/dispatches \
  -d '{"ref":"main","inputs":{"test_endpoints":"true"}}'
```

## WHAT THE WORKFLOW DOES

### Phase 1: Preparation
1. ✅ Checks out repository code
2. ✅ Sets up SSH key from GitHub Secret `VPS_SSH_KEY`
3. ✅ Tests SSH connection to VPS (92.118.45.135:22)

### Phase 2: Deployment
4. ✅ Stops MT5 Bridge service via Task Scheduler
5. ✅ Creates backup of current script
6. ✅ Uploads `mt5_bridge_complete.py` → `C:\mt5_bridge_service\mt5_bridge_api_service.py`
7. ✅ Verifies file was uploaded successfully
8. ✅ Starts MT5 Bridge service via Task Scheduler
9. ✅ Waits 15 seconds for service startup

### Phase 3: Verification
10. ✅ Tests `/api/mt5/bridge/health` endpoint
11. ✅ Tests `/api/mt5/accounts/summary` endpoint (NEW)
12. ✅ Tests `/api/mt5/account/886557/info` endpoint
13. ✅ Tests `/api/mt5/account/886557/trades?limit=100` endpoint (NEW)
14. ✅ Displays deployment summary

## EXPECTED RESULTS

### Before Deployment:
```bash
$ curl http://92.118.45.135:8000/api/mt5/accounts/summary
{"detail":"Not Found"}

$ curl http://92.118.45.135:8000/api/mt5/account/886557/trades
{"detail":"Not Found"}
```

### After Deployment:
```bash
$ curl http://92.118.45.135:8000/api/mt5/accounts/summary
{
  "success": true,
  "accounts": [
    {"account": 886557, "name": "BALANCE Master", "fund_type": "BALANCE", "balance": 79824.4, "equity": 79824.4},
    {"account": 886066, "name": "BALANCE-01", "fund_type": "BALANCE", ...},
    ... (all 7 accounts)
  ],
  "count": 7,
  "timestamp": "2025-10-29T..."
}

$ curl http://92.118.45.135:8000/api/mt5/account/886557/trades?limit=5
{
  "success": true,
  "trades": [
    {"ticket": 123456, "time": "2025-10-29T...", "volume": 0.1, "profit": 15.50, "symbol": "EURUSD", ...},
    ...
  ],
  "count": 5,
  "account_number": 886557,
  "timestamp": "2025-10-29T..."
}
```

## SUCCESS CRITERIA

✅ **Deployment Successful** when:
1. Workflow completes without errors (green checkmark in Actions tab)
2. All 4 endpoint tests pass
3. Bridge version shows `"version": "3.0-complete"`
4. Backend `vps_sync_service` successfully syncs historical trades
5. MongoDB `mt5_deals_history` collection gets populated
6. Broker rebates calculation shows correct values

## TROUBLESHOOTING

### If SSH connection fails:
- Verify `VPS_SSH_KEY` secret contains the private key
- Check VPS is accessible: `ping 92.118.45.135`
- Verify SSH port 22 is open

### If service won't start:
- Check VPS logs: `C:\mt5_bridge_service\logs\api_service.log`
- Verify MT5 Terminal is running on VPS
- Check Task Scheduler has MT5BridgeService task configured

### If endpoints return errors:
- Wait 30 seconds after deployment (service needs initialization time)
- Check MT5 Terminal is logged in to an account
- Verify Python packages are installed on VPS

## NEXT STEPS AFTER DEPLOYMENT

1. ✅ Verify backend sync succeeds
2. ✅ Check `mt5_deals_history` MongoDB collection is populated
3. ✅ Test broker rebates calculation endpoint
4. ✅ Verify watchdog alerts stop (90% reduction expected)
5. ✅ Monitor for 24 hours to ensure stability

## FILES IN THIS DEPLOYMENT

| File | Purpose |
|------|---------|
| `/app/vps-scripts/mt5_bridge_complete.py` | Complete Bridge script with all endpoints |
| `/app/.github/workflows/deploy-complete-bridge.yml` | Automated deployment workflow |
| `/app/docs/MT5_BRIDGE_DEPLOYMENT.md` | This documentation |

---

**READY TO DEPLOY** ✅

The complete MT5 Bridge script is ready. All that's needed is to trigger the GitHub Actions workflow.
