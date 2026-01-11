# MT5 Bridge Magic Number Fix - Manual Deployment

## Issue Fixed
Added missing `magic` field to trade data extraction in MT5 Bridge.

## File Changed
`/vps-scripts/mt5_bridge_multi_account_fixed.py`

## Change Made
```python
# BEFORE (missing magic):
account_deals.append({
    "ticket": deal.ticket,
    "order": deal.order,
    ...
    "account_number": account_number
})

# AFTER (with magic):
account_deals.append({
    "ticket": deal.ticket,
    "order": deal.order,
    ...
    "magic": deal.magic,  # ADDED: Identifies manager/EA
    ...
    "position_id": deal.position_id,
    "account_number": account_number
})
```

## Deployment Instructions

### Option 1: Via GitHub Actions (Recommended)
1. Go to: https://github.com/chavapalmarubin-lab/FIDUS/actions
2. Select workflow: "Deploy MT5 Bridge Multi-Account Fix"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"
6. Wait 2-3 minutes for completion

### Option 2: Manual VPS Deployment
1. SSH to VPS: `ssh trader@92.118.45.135`
2. Navigate: `cd C:\mt5_bridge_service`
3. Copy fixed file from repository
4. Restart service: `Restart-Service "MT5 Bridge"`
5. Verify: Check http://92.118.45.135:8000/api/mt5/bridge/health

## Verification Steps

After deployment, verify magic numbers are now populated:

```bash
# Check a sample trade from VPS:
curl http://92.118.45.135:8000/api/mt5/account/886602/trades?limit=1

# Expected output should include:
{
  "ticket": 123456,
  "magic": 100234,  # <-- Should be a number, not null
  ...
}
```

## Impact
- ✅ Money Managers Compare tab will show data
- ✅ Manager performance metrics will be accurate
- ✅ Trade attribution by manager will work
- ✅ All 22,000+ existing deals will need re-sync to get magic numbers

## Re-sync Command
After deployment, trigger re-sync of all trade history:
```bash
curl -X POST https://fintech-dashboard-60.preview.emergentagent.com/api/admin/mt5-deals/sync-all \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This will pull fresh data with magic numbers from VPS.
