# MT5 Bridge Service - Quick Reference

## 🚀 Quick Deploy (TL;DR)

```powershell
# 1. Copy mt5_bridge_service_dynamic.py to VPS
# 2. Test it manually
cd C:\mt5_bridge_service
python mt5_bridge_service_dynamic.py
# Press Ctrl+C after successful sync

# 3. Update Task Scheduler
# Change: mt5_bridge_service_production.py
# To:     mt5_bridge_service_dynamic.py

# 4. Monitor
Get-Content C:\mt5_bridge_service\mt5_bridge_dynamic.log -Wait -Tail 50
```

## 📁 Files on VPS

```
C:\mt5_bridge_service\
├── .env                                    (existing - MongoDB URI)
├── mt5_bridge_service_production.py       (existing - KEEP as backup!)
├── mt5_bridge_service_dynamic.py          (new - deploy this)
├── mt5_bridge_production.log              (existing log)
└── mt5_bridge_dynamic.log                 (new log - will be created)
```

## 🔑 Key Fix in Dynamic Script

**The Problem:**
```python
# ❌ This fails in pymongo 4.x on Python 3.12
if db:  # NotImplementedError: Database objects do not implement truth value testing
    accounts = db.mt5_account_config.find()
```

**The Solution:**
```python
# ✅ This works in pymongo 4.x
if self.db is not None:
    accounts = self.db.mt5_account_config.find()
```

## 📊 Comparison Table

| Feature | Production (Current) | Dynamic (New) |
|---------|---------------------|---------------|
| **Accounts Source** | Hardcoded in script | MongoDB database |
| **Add Account** | Edit script + VPS access | Admin dashboard only |
| **Remove Account** | Edit script + VPS access | Admin dashboard only |
| **Update Password** | Edit script + VPS access | Admin dashboard only |
| **Sync Time** | Immediate (after restart) | Within 50 minutes |
| **Rollback** | N/A | Switch back in Task Scheduler |
| **VPS Access Needed** | Every change | Only for initial setup |
| **Pymongo 4.x Bug** | May exist | ✅ Fixed |
| **Fallback** | N/A | Uses hardcoded accounts |
| **Audit Trail** | None | Full (who, when, what) |

## 🎯 When to Use Which Script

### Use Production Script If:
- You want accounts hardcoded and unchangeable
- You don't mind editing the script for changes
- You have easy VPS access
- You want to avoid any MongoDB dependencies

### Use Dynamic Script If:
- You want to manage accounts via admin dashboard
- You don't want to access VPS for account changes
- You want full audit trail of changes
- You want the system to be fully data-driven
- **You're experiencing the pymongo "truth value testing" error**

## ⚡ Testing Commands

### Test MongoDB Connection
```powershell
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGODB_URI')); print(client.admin.command('ping'))"
```

### Test Dynamic Script (One Cycle)
```powershell
cd C:\mt5_bridge_service
python mt5_bridge_service_dynamic.py
# Wait for sync to complete, then Ctrl+C
```

### View Logs
```powershell
# Production log
Get-Content C:\mt5_bridge_service\mt5_bridge_production.log -Tail 50

# Dynamic log
Get-Content C:\mt5_bridge_service\mt5_bridge_dynamic.log -Tail 50
```

### Check Active Accounts in MongoDB
```powershell
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGODB_URI')); db = client.get_database(); accounts = list(db.mt5_account_config.find({'is_active': True}, {'account': 1, 'name': 1})); print(f'Found {len(accounts)} active accounts:'); [print(f\"  - {a['account']}: {a['name']}\") for a in accounts]"
```

## 🔄 Rollback Process (If Needed)

**Instant Rollback - Takes 2 Minutes:**

1. Open Task Scheduler
2. Find task: "MT5 Bridge Service"
3. Edit → Actions tab → Edit action
4. Change script name back to: `mt5_bridge_service_production.py`
5. Save

**That's it!** The service will continue working with the production script.

## ✅ Success Indicators

After deploying dynamic script, look for these in the logs:

```
✅ MongoDB connected successfully
✅ Loaded 7 active accounts from MongoDB:
   - 886557: Main Balance Account (BALANCE)
   - 886066: Secondary Balance Account (BALANCE)
   ...
✅ Synced 886557: Balance=$100000.00, Equity=$100500.00, P&L=$500.00
...
✅ Sync complete: 7 successful, 0 failed
```

**Red Flags (indicates problems):**
```
❌ MongoDB connection error
⚠️ No active accounts found in mt5_account_config, using fallback
❌ Login failed for [account]: [error]
NotImplementedError: Database objects do not implement truth value testing
```

## 📞 Quick Help

### Script Won't Start
- Check Python 3.12 installed: `python --version`
- Check pymongo installed: `pip show pymongo`
- Check .env file exists: `Test-Path C:\mt5_bridge_service\.env`

### MongoDB Connection Failed
- Verify MONGODB_URI in .env file
- Check MongoDB Atlas whitelist includes VPS IP
- Test connection with the MongoDB test command above

### Accounts Not Loading from Database
- Check `is_active: true` in mt5_account_config collection
- Verify MongoDB connection successful in logs
- Run dynamic script manually to see detailed error messages

### Task Scheduler Not Running
- Check task history for errors
- Verify script path is correct
- Run script manually to identify issues

---

## 🎉 Final Checklist

Before going to production with dynamic script:

- [ ] Production script working and saved as backup
- [ ] Dynamic script tested manually with successful sync
- [ ] MongoDB connection verified
- [ ] Accounts loading from database (not using fallback)
- [ ] Task Scheduler updated to use dynamic script
- [ ] Monitored for 2-3 sync cycles (10-15 minutes)
- [ ] No errors in mt5_bridge_dynamic.log
- [ ] Admin dashboard shows updated account data
- [ ] Rollback plan tested and confirmed working

---

**Questions?** Check the full `DEPLOYMENT_INSTRUCTIONS.md` file for detailed troubleshooting and step-by-step guide.
