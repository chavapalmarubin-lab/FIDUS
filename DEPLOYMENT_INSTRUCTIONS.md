# 🚀 VPS MT5 BRIDGE DEPLOYMENT - LIVE DEALS ENDPOINTS

**Date:** October 24, 2025  
**Priority:** CRITICAL  
**Status:** READY TO DEPLOY

---

## 📋 WHAT'S BEING DEPLOYED

**New Endpoints on VPS MT5 Bridge:**
1. `GET /api/mt5/account/{id}/deals/live?days=30` - Get live deals for single account
2. `GET /api/mt5/accounts/deals/live?days=30` - Get live deals for all accounts

**Why:** These endpoints fetch deal history directly from MT5 terminal using `mt5.history_deals_get()`, not from stale MongoDB cache.

**Impact:** Rebates will calculate from current trading volume, not 5-day-old data.

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Run GitHub Actions Workflow

1. Go to GitHub → **Actions** tab
2. Select workflow: **"Deploy VPS MT5 Bridge - Add Live Deals Endpoints"**
3. Click **"Run workflow"**
4. Type: `DEPLOY`
5. Click **"Run workflow"** to start

**Expected Duration:** ~5 minutes

**What it does:**
- ✅ Connects to VPS via WinRM
- ✅ Backs up current service file
- ✅ Uploads updated file with live deals endpoints
- ✅ Restarts MT5 Bridge service
- ✅ Verifies new endpoints work

---

### Step 2: Verify VPS Deployment

**Test new endpoint:**
```bash
curl "http://92.118.45.135:8000/api/mt5/account/891215/deals/live?days=7"
```

**Expected response:**
```json
{
  "account_id": 891215,
  "deals_count": 150,
  "total_volume_lots": 45.30,
  "date_from": "2025-10-17T...",
  "date_to": "2025-10-24T...",
  "data_source": "MT5_TERMINAL_LIVE",  ← CRITICAL: Must be "MT5_TERMINAL_LIVE"
  "deals": [...]
}
```

---

### Step 3: Update Backend to Use New Endpoint

**File:** `/app/backend/vps_sync_service.py`

**Change in `sync_account_trades()` method:**

```python
# OLD (line ~265):
result = await self.fetch_from_vps(f'/api/mt5/account/{account_id}/trades?limit={limit}')

# NEW:
result = await self.fetch_from_vps(f'/api/mt5/account/{account_id}/deals/live?days=30')
```

**Full updated method:**
```python
async def sync_account_trades(self, account_id: int, days: int = 30) -> Dict[str, Any]:
    """
    Sync deals for a single account from VPS LIVE endpoint
    Updated Oct 24, 2025: Now uses /deals/live for real-time MT5 data
    """
    try:
        logger.info(f"🔄 Syncing LIVE deals for account {account_id}")
        
        # Fetch LIVE deals from VPS (not cached data)
        result = await self.fetch_from_vps(f'/api/mt5/account/{account_id}/deals/live?days={days}')
        
        if 'error' in result:
            logger.error(f"❌ Failed to fetch live deals for {account_id}: {result['error']}")
            return {
                "success": False,
                "account_id": account_id,
                "error": result['error'],
                "trades_synced": 0
            }
        
        # Verify we're getting LIVE data
        if result.get('data_source') != 'MT5_TERMINAL_LIVE':
            logger.error(f"❌ Not getting live data! Source: {result.get('data_source')}")
            return {
                "success": False,
                "account_id": account_id,
                "error": f"Data source is {result.get('data_source')}, expected MT5_TERMINAL_LIVE",
                "trades_synced": 0
            }
        
        deals = result.get('deals', [])
        
        if not deals:
            logger.info(f"📭 No deals found for account {account_id}")
            return {
                "success": True,
                "account_id": account_id,
                "trades_synced": 0,
                "message": "No deals to sync"
            }
        
        # Store deals in mt5_deals_history collection
        deals_synced = 0
        sync_time = datetime.now(timezone.utc)
        
        for deal in deals:
            try:
                # Prepare deal document
                deal_doc = {
                    'account_number': account_id,
                    'ticket': deal.get('ticket'),
                    'order': deal.get('order'),
                    'time': deal.get('time'),  # Already in ISO format from VPS
                    'type': deal.get('type'),
                    'entry': deal.get('entry'),
                    'magic': deal.get('magic'),
                    'position_id': deal.get('position_id'),
                    'symbol': deal.get('symbol'),
                    'volume': deal.get('volume', 0),
                    'price': deal.get('price'),
                    'commission': deal.get('commission', 0),
                    'swap': deal.get('swap', 0),
                    'profit': deal.get('profit', 0),
                    'comment': deal.get('comment', ''),
                    'external_id': deal.get('external_id', ''),
                    'synced_at': sync_time,
                    'synced_from_vps': True,
                    'data_source': 'MT5_TERMINAL_LIVE'
                }
                
                # Upsert deal (ticket + time as unique identifier)
                await self.db.mt5_deals_history.update_one(
                    {
                        'account_number': account_id,
                        'ticket': deal_doc['ticket'],
                        'time': deal_doc['time']
                    },
                    {'$set': deal_doc},
                    upsert=True
                )
                
                deals_synced += 1
            
            except Exception as e:
                logger.error(f"❌ Error storing deal {deal.get('ticket')}: {str(e)}")
                continue
        
        logger.info(f"✅ Synced {deals_synced}/{len(deals)} LIVE deals for account {account_id}")
        
        return {
            "success": True,
            "account_id": account_id,
            "trades_synced": deals_synced,
            "total_trades": len(deals),
            "total_volume": result.get('total_volume_lots', 0),
            "sync_time": sync_time.isoformat(),
            "data_source": "MT5_TERMINAL_LIVE"
        }
    
    except Exception as e:
        logger.error(f"❌ Error syncing live deals for {account_id}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "account_id": account_id,
            "error": str(e),
            "trades_synced": 0
        }
```

---

### Step 4: Deploy Backend Update

```bash
# Backend will auto-restart with supervisor hot reload
sudo supervisorctl restart backend

# Or just wait for hot reload (should detect file change)
```

---

### Step 5: Trigger Manual Sync

**Test the complete flow:**

```bash
# Call manual sync endpoint (requires admin auth)
curl -X POST http://localhost:8001/api/admin/sync-from-vps \
  -H "Authorization: Bearer {admin_token}"
```

**Expected result:**
```json
{
  "status": "success",
  "accounts": {
    "synced": 7,
    "total": 7
  },
  "trades": {
    "synced": 500,  ← NEW deals synced
    "accounts_processed": 7
  }
}
```

---

### Step 6: Verify Rebates Update

**Check MongoDB:**
```python
# Latest deal should be recent (today)
latest_deal = await db.mt5_deals_history.find_one(
    {},
    sort=[('time', -1)]
)
print(f"Latest deal: {latest_deal['time']}")
print(f"Data source: {latest_deal.get('data_source')}")
# Should show: data_source: MT5_TERMINAL_LIVE
```

**Check rebates calculation:**
```python
from datetime import datetime, timezone, timedelta

end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=30)

pipeline = [
    {'$match': {
        'time': {'$gte': start_date.isoformat(), '$lte': end_date.isoformat()},
        'type': {'$in': [0, 1]}  # Buy/Sell only
    }},
    {'$group': {
        '_id': None,
        'total_volume': {'$sum': '$volume'}
    }}
]

result = await db.mt5_deals_history.aggregate(pipeline).to_list(length=1)
volume = result[0]['total_volume'] if result else 0
rebates = volume * 5.05

print(f"Total volume (last 30 days): {volume:.2f} lots")
print(f"Rebates at $5.05/lot: ${rebates:.2f}")
```

**Check frontend:**
- Login to client portal
- View cash flow dashboard
- **Rebates should show NEW amount** (not $450)

---

## ✅ SUCCESS CRITERIA

**Deployment successful when:**

1. ✅ VPS has new endpoints responding
2. ✅ Endpoints return `data_source: "MT5_TERMINAL_LIVE"`
3. ✅ Backend syncs fresh deals (not 5 days old)
4. ✅ MongoDB has current deals (today's date)
5. ✅ Rebates calculate from current volume
6. ✅ Frontend shows updated rebates

---

## 🐛 TROUBLESHOOTING

### Issue: VPS deployment fails

**Check:**
- GitHub Secrets configured (VPS_HOST, VPS_USERNAME, VPS_PASSWORD)
- VPS is reachable
- WinRM is enabled on VPS

**Fix:**
- Verify secrets in GitHub Settings → Secrets
- Test connectivity: `Test-Connection -ComputerName 92.118.45.135`

### Issue: New endpoints return 404

**Check:**
- VPS service restarted successfully
- No Python errors in VPS logs

**Fix:**
- Check VPS logs at `C:\mt5_bridge_service\logs\api_service.log`
- Manually restart service on VPS if needed

### Issue: Data source is not "MT5_TERMINAL_LIVE"

**Check:**
- MT5 terminal is running on VPS
- Master account logged in
- Account credentials exist in MongoDB

**Fix:**
- Restart VPS MT5 Bridge service
- Verify master account login in VPS logs

### Issue: Backend still syncs 0 trades

**Check:**
- Backend using new endpoint (`/deals/live`)
- VPS endpoint returns deals (test with curl)

**Fix:**
- Update `vps_sync_service.py` as shown in Step 3
- Restart backend
- Trigger manual sync

---

## 📊 EXPECTED TIMELINE

| Step | Duration | Status |
|------|----------|--------|
| 1. Run GitHub workflow | 5 min | ⏳ Pending |
| 2. Verify VPS | 2 min | ⏳ Pending |
| 3. Update backend code | 5 min | ⏳ Pending |
| 4. Deploy backend | 1 min | ⏳ Pending |
| 5. Trigger sync | 2 min | ⏳ Pending |
| 6. Verify rebates | 3 min | ⏳ Pending |
| **TOTAL** | **~20 min** | ⏳ Ready |

---

## 🎯 DELIVERABLES

- ✅ Updated VPS service file (`mt5_bridge_api_service_FIXED.py`)
- ✅ GitHub Actions deployment workflow
- ✅ Updated backend sync service code
- ✅ Deployment instructions (this document)
- ⏳ VPS deployed (pending workflow run)
- ⏳ Backend updated (pending code change)
- ⏳ Rebates verified (pending sync)

---

## 🚀 READY TO DEPLOY

**All files are ready. Execute Step 1 to begin deployment.**

**Files:**
- `/app/mt5_bridge_api_service_FIXED.py` - Updated VPS service
- `/app/.github/workflows/deploy-vps-live-deals.yml` - Deployment workflow
- `/app/DEPLOYMENT_INSTRUCTIONS.md` - This file

**Next action:** Run GitHub Actions workflow "Deploy VPS MT5 Bridge - Add Live Deals Endpoints"
