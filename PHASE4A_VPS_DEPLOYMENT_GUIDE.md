# Phase 4A: Deal History Collection - MongoDB Schema & Deployment Guide

## MongoDB Schema: mt5_deals_history Collection

### Collection Purpose
Stores historical deal data from MT5 accounts for analytics, rebate calculations, and cash flow tracking.

### Document Structure

```javascript
{
  // Deal Identification
  "ticket": 12345678,              // INT - Unique deal ID (PRIMARY KEY)
  "order": 87654321,               // INT - Related order ticket
  "position_id": 45678,            // INT - Related position ID
  "external_id": "EXT12345",       // STRING - External reference ID
  
  // Timing
  "time": ISODate("2025-01-15T14:30:00Z"),  // DATETIME - Deal execution time (UTC)
  "synced_at": ISODate("2025-01-15T14:35:00Z"),  // DATETIME - When synced to MongoDB
  
  // Deal Classification
  "type": 0,                       // INT - Deal type (0=buy, 1=sell, 2=balance operation)
  "entry": 0,                      // INT - Entry type (0=in, 1=out)
  "symbol": "EURUSD",              // STRING - Trading symbol
  
  // Financial Data (CRITICAL)
  "volume": 1.5,                   // FLOAT - Volume in lots (CRITICAL for rebates)
  "price": 1.0850,                 // FLOAT - Deal execution price
  "profit": 125.50,                // FLOAT - Profit/loss (CRITICAL for analytics)
  "commission": -7.50,             // FLOAT - Commission paid (CRITICAL for rebates)
  "swap": -2.30,                   // FLOAT - Swap/overnight fee
  
  // Attribution & Classification
  "magic": 100234,                 // INT - Magic number (for manager attribution)
  "comment": "Profit withdrawal",  // STRING - Comment (for transfer classification)
  
  // Account Context
  "account_number": 886557,        // INT - MT5 account number
  "account_name": "Main Balance Account",  // STRING - Account friendly name
  "fund_type": "BALANCE"           // STRING - Fund type (CORE/BALANCE/SEPARATION)
}
```

### Deal Type Classification

| Type | Description | Purpose |
|------|-------------|---------|
| 0 | Buy | Trading activity |
| 1 | Sell | Trading activity |
| 2 | Balance Operation | Cash flow events (deposits, withdrawals, transfers) |

### Entry Type Classification

| Entry | Description | Purpose |
|-------|-------------|---------|
| 0 | In | Entry into position |
| 1 | Out | Exit from position |

### Required Indexes

```javascript
// Single field indexes
db.mt5_deals_history.createIndex({ "account_number": 1 })
db.mt5_deals_history.createIndex({ "time": -1 })
db.mt5_deals_history.createIndex({ "type": 1 })
db.mt5_deals_history.createIndex({ "symbol": 1 })

// Compound indexes (for optimal query performance)
db.mt5_deals_history.createIndex({ "account_number": 1, "time": -1 })

// Unique index (prevent duplicate deals)
db.mt5_deals_history.createIndex({ "ticket": 1 }, { unique: true })
```

### Indexes Created Automatically by Script
The `mt5_bridge_service_with_deals.py` script automatically creates all required indexes on startup via the `ensure_deal_indexes()` method.

---

## VPS Deployment Instructions

### Prerequisites
✅ Windows VPS with MetaTrader5 installed
✅ Python 3.12 installed
✅ MT5 Python API (`pip install MetaTrader5`)
✅ pymongo 4.x (`pip install pymongo`)
✅ python-dotenv (`pip install python-dotenv`)

### Step-by-Step Deployment

#### 1. Stop Current MT5 Bridge Service

```bash
# Open Task Scheduler
# Navigate to: Task Scheduler Library
# Find: "MT5 Bridge Service"
# Right-click → Disable
# Wait 30 seconds to ensure clean shutdown
```

#### 2. Backup Current Script

```bash
# In C:\mt5_bridge_service\
copy mt5_bridge_service_dynamic.py mt5_bridge_service_dynamic.backup
```

#### 3. Deploy New Script

```bash
# Copy the new script to VPS
# Save as: C:\mt5_bridge_service\mt5_bridge_service_with_deals.py

# Verify file exists
dir C:\mt5_bridge_service\
```

#### 4. Update .env File

```bash
# C:\mt5_bridge_service\.env

MONGODB_URI=mongodb+srv://chavapalmarubin_db_user:***SANITIZED***.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority
MT5_PATH=C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe

# Account sync (every 5 minutes)
UPDATE_INTERVAL=300

# Deal sync (every 24 hours)
DEAL_SYNC_INTERVAL=86400

# Initial backfill (90 days)
INITIAL_BACKFILL_DAYS=90
```

#### 5. Update run_bridge.bat

```batch
@echo off
REM MT5 Bridge Service - Deal History Collection
REM Batch file wrapper for Windows Task Scheduler

echo Starting MT5 Bridge Service with Deal History...
cd /d C:\mt5_bridge_service

REM Activate Python virtual environment (if using venv)
REM call venv\Scripts\activate.bat

REM Run the enhanced bridge service
python mt5_bridge_service_with_deals.py

REM If script exits, log the event
echo MT5 Bridge Service stopped at %date% %time% >> service_stop.log
pause
```

#### 6. Test Script Manually (Before Scheduling)

```bash
# Open Command Prompt as Administrator
cd C:\mt5_bridge_service

# Run manually to test
python mt5_bridge_service_with_deals.py

# Expected output:
# 🚀 MT5 Bridge Service - Deal History Collection (Phase 4A) Starting...
# ✅ MongoDB connected successfully
# ✅ Deal history indexes created/verified
# ✅ Loaded 7 active accounts from MongoDB
# ✅ MT5 Terminal initialized: v5.0.XXXX
# 🎯 Performing initial deal history sync...
# 📦 Starting 90-day backfill for account 886557
# ✅ Collected XXX deals for 886557
# 💾 Stored XXX new deals, updated 0 existing deals
# [... repeat for all 7 accounts ...]
# ✅ Deal sync complete: XXXX deals processed

# Press Ctrl+C to stop after verifying it works
```

#### 7. Update Windows Task Scheduler

```bash
# Open Task Scheduler
# Find: "MT5 Bridge Service"
# Right-click → Properties

# In "Actions" tab:
#   Program/script: C:\mt5_bridge_service\run_bridge.bat
#   Start in: C:\mt5_bridge_service

# Save changes
# Right-click → Enable
# Right-click → Run (to test)
```

#### 8. Verify Deployment

##### Check Logs

```bash
# View log file
type C:\mt5_bridge_service\mt5_bridge_with_deals.log

# Expected entries:
# - MongoDB connection successful
# - Indexes created
# - 7 accounts loaded
# - Initial backfill completed
# - Daily sync running
```

##### Verify MongoDB Data

```javascript
// Connect to MongoDB Atlas
// Database: fidus_production

// Check deal count
db.mt5_deals_history.countDocuments()
// Expected: 500-5000+ deals (depending on trading activity over 90 days)

// Check recent deals
db.mt5_deals_history.find().sort({time: -1}).limit(10).pretty()

// Check deals per account
db.mt5_deals_history.aggregate([
  { $group: { _id: "$account_number", count: { $sum: 1 } } }
])

// Verify indexes
db.mt5_deals_history.getIndexes()
```

##### Test Backend API (Next Step)

```bash
# After backend API is deployed (Day 2)
curl https://fidus-api.onrender.com/api/mt5/deals?account_number=886557

# Should return deal history for account 886557
```

---

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UPDATE_INTERVAL` | 300 | Account sync interval (seconds) |
| `DEAL_SYNC_INTERVAL` | 86400 | Deal sync interval (seconds, 24 hours) |
| `INITIAL_BACKFILL_DAYS` | 90 | Days to backfill on first run |

### Sync Schedule Options

#### Option 1: Integrated (Recommended)
- Account sync: Every 5 minutes (existing)
- Deal sync: Daily check (once per 24 hours)
- **Benefit**: Single service, simple management

#### Option 2: Separate Task
- Create second Windows Task for daily deal sync
- Run at specific time (e.g., 12:00 AM UTC)
- **Benefit**: Predictable deal sync timing

**Current Implementation**: Option 1 (Integrated)

---

## Data Volume Estimates

### Initial Backfill (90 days)
- Light trader: 50-200 deals per account
- Active trader: 500-1000 deals per account
- High-frequency: 2000-5000 deals per account

**7 Accounts × 500 deals avg = ~3500 deals initial**

### Daily Incremental
- 10-50 deals per day across all accounts
- Storage: ~2-10 KB per day

### MongoDB Storage
- Deal document size: ~500 bytes
- 3500 deals = ~1.75 MB initial
- Annual growth: ~3-15 MB

**Conclusion**: Storage impact is minimal, well within free tier limits.

---

## Troubleshooting

### Issue: No Deals Collected

**Symptoms:**
```
📊 Account 886557: No deals in range
```

**Solutions:**
1. Check date range - may be no trading activity
2. Verify MT5 login credentials
3. Check MT5 terminal is running
4. Verify account has historical data in MT5

### Issue: MongoDB Connection Failed

**Symptoms:**
```
❌ MongoDB connection error: ServerSelectionTimeoutError
```

**Solutions:**
1. Check internet connection on VPS
2. Verify MONGODB_URI in .env file
3. Check MongoDB Atlas IP whitelist (allow VPS IP)
4. Test connection: `ping fidus.y1p9be2.mongodb.net`

### Issue: Duplicate Deal Errors

**Symptoms:**
```
❌ Error storing deals to MongoDB: DuplicateKeyError
```

**Solutions:**
1. This is normal - deals already exist
2. Script uses upsert to handle duplicates
3. Check logs for "modified" count instead of "inserted"

### Issue: Service Crashes

**Symptoms:**
- Task Scheduler shows "Last Run Result: (0x1)"
- Service stops unexpectedly

**Solutions:**
1. Check mt5_bridge_with_deals.log for errors
2. Verify all dependencies installed
3. Check MT5 terminal is running
4. Restart VPS if needed

---

## Rollback Procedure

If issues occur, rollback to previous version:

```bash
# 1. Stop current service
# Task Scheduler → Disable "MT5 Bridge Service"

# 2. Restore backup
copy C:\mt5_bridge_service\mt5_bridge_service_dynamic.backup C:\mt5_bridge_service\mt5_bridge_service_dynamic.py

# 3. Update run_bridge.bat to use old script
# Change: python mt5_bridge_service_with_deals.py
# To: python mt5_bridge_service_dynamic.py

# 4. Re-enable service
# Task Scheduler → Enable "MT5 Bridge Service"

# 5. Optional: Delete deal collection
# MongoDB: db.mt5_deals_history.drop()
```

---

## Success Criteria

✅ Script runs without errors for 24 hours
✅ MongoDB contains 500+ deals (initial backfill complete)
✅ New deals added daily (check deal timestamps)
✅ All 7 accounts have deal history
✅ Backend API can query deals (Day 2 implementation)
✅ Frontend dashboards display deal data (Day 3 implementation)

---

## Next Steps

After successful VPS deployment:
1. **Day 2**: Implement backend API endpoints (`/api/mt5/deals`, `/api/mt5/rebates`)
2. **Day 3**: Update frontend components (Trading Analytics, Cash Flow, Rebates)
3. **Day 4**: End-to-end testing and verification

---

## Support

If issues persist after troubleshooting:
1. Share mt5_bridge_with_deals.log (last 100 lines)
2. Share MongoDB deal count: `db.mt5_deals_history.countDocuments()`
3. Share Task Scheduler status screenshot
4. Share any error messages from Command Prompt test run

---

**Phase 4A Implementation**: VPS Bridge Enhancement Complete ✅
**Next**: Backend API Development (Day 2)
