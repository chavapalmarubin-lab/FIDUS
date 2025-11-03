# MT5 Alert Management - Capital Reallocation Guide

## 🎯 Problem Solved
**Issue**: During monthly capital reallocation (when moving funds between accounts), the system was triggering false-positive alerts for "$0 balance" and "low sync success rate", resulting in spam emails.

**Solution**: Intelligent alert system that distinguishes between:
- ✅ **Legitimate $0 balances** (capital reallocation)  
- ❌ **Real disconnections** (MT5 terminal offline)

---

## 🚀 How It Works Now

### Smart Detection Logic
The system now checks **3 conditions** before alerting:

1. **Terminal Connection Status** - Is MT5 reporting as disconnected?
2. **Zero Balance Percentage** - Are >80% of accounts showing $0?
3. **Sync Activity** - Are accounts still syncing successfully?

**Example Scenarios:**

| Scenario | Terminal | $0 Accounts | Syncing? | Alert? | Reason |
|----------|----------|-------------|----------|--------|--------|
| **Capital Reallocation** | Connected | 5/5 (100%) | ✅ Yes | ❌ NO | Accounts syncing - normal reallocation |
| **Partial Reallocation** | Connected | 2/5 (40%) | ✅ Yes | ❌ NO | Only some accounts at $0 - normal |
| **Real Disconnect** | Disconnected | 5/5 (100%) | ❌ NO | ✅ YES | Terminal offline AND not syncing |
| **Sync Issue** | Connected | 1/5 (20%) | ❌ NO | ✅ YES | Real sync failure on account |

---

## 🛠️ Manual Control (During Maintenance)

### Option 1: Disable Alerts Temporarily
When performing monthly capital reallocation or maintenance:

```bash
# Edit .env file
nano /app/backend/.env

# Change this line:
MT5_ALERTS_ENABLED=false

# Restart backend
sudo supervisorctl restart backend

# After reallocation is complete, re-enable:
MT5_ALERTS_ENABLED=true
sudo supervisorctl restart backend
```

### Option 2: Use the Environment Variable
```bash
# Quick disable (lasts until restart)
export MT5_ALERTS_ENABLED=false

# Quick enable
export MT5_ALERTS_ENABLED=true
```

---

## 📊 New Alert Thresholds

### Before (OLD - Too Sensitive)
- ❌ Alert on ANY account with $0 balance
- ❌ Alert if sync rate < 80%
- ❌ Alert cooldown: 5-15 minutes
- ❌ Auto-restart on terminal disconnect

### After (NEW - Intelligent)
- ✅ Alert only if >80% accounts at $0 AND not syncing
- ✅ Alert if sync rate < 50% AND real failures
- ✅ Alert cooldown: 30 minutes
- ✅ Auto-restart requires: disconnection + no sync activity

---

## 📧 Email Alert Reduction

**Expected reduction**: ~80-90% fewer emails

**You'll still receive alerts for:**
- ✅ Real MT5 terminal disconnections (>80% accounts $0 + not syncing)
- ✅ Actual sync failures (<50% success rate)
- ✅ Multiple consecutive failures

**You'll NO LONGER receive alerts for:**
- ❌ Individual accounts with $0 (normal during reallocation)
- ❌ Temporary sync delays (40-50% success)
- ❌ Duplicate alerts within 30 minutes

---

## 🔍 Log Messages Guide

### Normal Operations (INFO)
```
ℹ️ 2/5 active accounts showing $0 balance (normal, SEPARATION excluded)
ℹ️ Low success rate (30%) but syncs are working - 3 accounts with $0 (likely capital reallocation)
```
**Action**: None - this is expected during reallocation

### Warning (WARNING)
```
⚠️ Terminal reports disconnected but only 2/5 accounts at $0 - not triggering restart
⚠️ Low sync rate: 3/7 accounts (42.9%)
```
**Action**: Monitor - may resolve automatically

### Critical (CRITICAL)
```
🚨 MT5 Terminal NOT CONNECTED to broker - initiating auto-restart
   5/5 accounts showing $0 balance
   0/5 accounts recently synced
```
**Action**: Real issue - system is auto-restarting

---

## 🗓️ Monthly Maintenance Workflow

**Recommended process for end-of-month capital reallocation:**

### Before Reallocation
```bash
# 1. Disable alerts
echo "MT5_ALERTS_ENABLED=false" >> /app/backend/.env
sudo supervisorctl restart backend

# 2. Perform capital movements
# (move funds between accounts as needed)

# 3. Wait for all transfers to complete
# (typically 15-30 minutes)
```

### After Reallocation
```bash
# 1. Verify all accounts are syncing
curl http://localhost:8001/api/health

# 2. Re-enable alerts
echo "MT5_ALERTS_ENABLED=true" >> /app/backend/.env
sudo supervisorctl restart backend

# 3. Confirm no spam emails
# (check inbox - should be clean)
```

---

## 📈 Monitoring Dashboard

Check system status at: `/api/health`

Key metrics to watch:
- `mt5_sync_status` - Should be "healthy"
- `accounts_synced` - Number of recently synced accounts
- `zero_balance_count` - How many accounts at $0

---

## 🚨 Troubleshooting

### "Still receiving too many emails"
1. Check if `MT5_ALERTS_ENABLED=true` in `.env`
2. Set to `false` during reallocation periods
3. Increase cooldown in code if needed

### "Not receiving alerts for real issues"
1. Check logs: `tail -f /var/log/supervisor/backend.out.log`
2. Verify `MT5_ALERTS_ENABLED=true`
3. Check email service is working

### "Accounts showing $0 but no alert"
1. ✅ This is CORRECT behavior if accounts are syncing
2. System knows this is reallocation, not a problem
3. Alert will trigger if syncs STOP working

---

## 📝 Technical Details

### Alert Cooldown Configuration
```python
# In mt5_auto_sync_service.py
self.alert_cooldown = 1800  # 30 minutes

# In mt5_watchdog.py  
self.healing_cooldown = 900  # 15 minutes
```

### Sync Success Thresholds
```python
# Alert only if <50% success AND real failures
if success_rate < 50 and actual_failures > total_accounts * 0.5:
    send_alert()
```

### Zero Balance Detection
```python
# Only alert if >80% accounts at $0 AND not syncing
if zero_balance_pct > 0.8 and recently_synced == 0:
    trigger_restart()
```

---

## 📞 Support

For issues with the alert system:
1. Check this documentation
2. Review logs in `/var/log/supervisor/backend.out.log`
3. Temporarily disable with `MT5_ALERTS_ENABLED=false`
4. Contact DevOps team if persistent issues

---

**Last Updated**: 2025-11-03  
**System Version**: FIDUS MT5 v2.0 (Intelligent Alerts)
