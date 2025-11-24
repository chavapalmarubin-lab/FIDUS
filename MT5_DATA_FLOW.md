# MT5 Data Flow Architecture

**Last Updated:** October 24, 2025  
**Status:** Production - Active  
**Purpose:** Document the complete MT5 data flow from terminal to frontend

---

## 🎯 Core Principle

**MT5 Terminal is the SINGLE SOURCE OF TRUTH.**

MongoDB NEVER generates data. Backend NEVER calculates balances. VPS API ONLY reads from MT5.

---

## 1. Components Overview

### 1.1 MT5 Terminal (Source of Truth)
- **Location:** VPS (92.118.45.135)
- **Platform:** MetaTrader 5 Terminal (MEXAtlantic-Real server)
- **Accounts:** 7 live trading accounts
  ```
  886557 - Main Balance Account ($80,000.00)
  886066 - Secondary Balance Account ($10,000.00)
  886602 - Tertiary Balance Account ($9,960.68)
  885822 - Core Account ($10,014.57)
  886528 - Separation Account ($0.00)
  891215 - Interest Earnings Trading ($27,047.52)
  891234 - Account 891234 ($8,000.00)
  ```
- **Role:** Executes trades, maintains account balances, generates deal history
- **Updates:** Real-time as trades execute and settle
- **Access:** Via MetaQuotes Python API (mt5 library)

### 1.2 VPS MT5 Bridge API (Gateway)
- **Location:** `http://92.118.45.135:8000`
- **Technology:** Python 3.12 + FastAPI 0.115.0
- **Service File:** `C:\mt5_bridge_service\mt5_bridge_api_service.py`
- **Role:** Provides REST API access to MT5 Terminal data
- **Authentication:** Master account login (886557) with password
- **Port:** 8000 (HTTP)

**Key Endpoints:**

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/mt5/bridge/health` | GET | Health check | Service status, MT5 connection, MongoDB status |
| `/api/mt5/account/{id}/info` | GET | Get account info | Account details + `live_data` from MT5 + stored MongoDB data |
| `/api/mt5/accounts/summary` | GET | Get all accounts | List of all accounts with balances (from MongoDB) |
| `/api/mt5/account/{id}/balance` | GET | Get account balance | Current balance, equity, profit |
| `/api/mt5/account/{id}/trades` | GET | Get account trades | Recent trade history |

**Critical Note:** 
- `/api/mt5/account/{id}/info` returns `live_data` field with LIVE MT5 terminal data
- `/api/mt5/accounts/summary` returns MongoDB cached data (may be stale)
- **Backend MUST use individual account endpoints to get fresh data**

### 1.3 Backend VPS Sync Service (Fetcher)
- **Location:** Render.com (FIDUS Backend)
- **File:** `/app/backend/vps_sync_service.py`
- **Role:** Fetch live MT5 data from VPS and cache in MongoDB
- **Technology:** Python AsyncIO + httpx + Motor (MongoDB async driver)
- **Schedule:** Automated via APScheduler

**Configuration:**
```python
MT5_BRIDGE_URL = "http://92.118.45.135:8000"
MT5_BRIDGE_TIMEOUT = 30 seconds
SYNC_INTERVAL = 5 minutes
```

**Sync Process:**
1. Check VPS Bridge health (`/api/mt5/bridge/health`)
2. Get list of accounts (`/api/mt5/accounts/summary`)
3. For EACH account:
   - Call `/api/mt5/account/{id}/info`
   - Extract `live_data` field (direct from MT5)
   - Update MongoDB with fresh balance/equity/profit
4. Log sync results
5. Update cache collection

**Schedule:**
- **Frequency:** Every 5 minutes
- **Times:** :01, :06, :11, :16, :21, :26, :31, :36, :41, :46, :51, :56
- **Trigger:** APScheduler cron job
- **Function:** `automatic_vps_sync()` in `server.py`

**Error Handling:**
- VPS unreachable: Retry 3 times, log error, skip cycle
- Single account fails: Continue with other accounts
- MongoDB unavailable: Log error, retry next cycle

### 1.4 MongoDB (Cache)
- **Location:** MongoDB Atlas (cloud)
- **Database:** `fidus_production`
- **Collection:** `mt5_accounts`
- **Role:** READ-ONLY cache of MT5 data
- **Update Source:** ONLY from VPS Sync Service

**Schema:**
```javascript
{
  account: 891215,                          // MT5 account number
  name: "Interest Earnings Trading",        // Account name
  fund_type: "SEPARATION",                  // Fund classification
  balance: 27047.52,                        // Current balance (from MT5)
  equity: 27047.52,                         // Current equity (from MT5)
  profit: 0.0,                              // Current profit (from MT5)
  margin: 0,                                // Used margin
  margin_free: 27047.52,                    // Free margin
  margin_level: 0,                          // Margin level %
  leverage: 100,                            // Account leverage
  currency: "USD",                          // Account currency
  trade_allowed: true,                      // Trading enabled
  updated_at: ISODate("2025-10-24T15:53:19.571Z"), // Last sync timestamp
  synced_from_vps: true,                    // Sync status flag
  vps_sync_timestamp: ISODate("2025-10-24T15:53:19.571Z"), // VPS sync time
  data_source: "VPS_LIVE_MT5",              // Data origin (VPS_LIVE_MT5 or VPS_STORED)
  
  // Additional fields (not updated by sync)
  client_id: "client_alejandro",
  password: "***SANITIZED***",                     // Encrypted in production
  server: "MEXAtlantic-Real",
  target_amount: 6590.31,
  broker: "MEXAtlantic"
}
```

**Fields Updated by Sync:**
- `balance`, `equity`, `profit` (from MT5)
- `margin`, `margin_free`, `margin_level` (from MT5)
- `leverage`, `currency`, `trade_allowed` (from MT5)
- `updated_at` (sync timestamp)
- `synced_from_vps` (always true)
- `vps_sync_timestamp` (sync time)
- `data_source` (VPS_LIVE_MT5 or VPS_STORED)

**What MongoDB Should NEVER Do:**
- ❌ Generate account balances
- ❌ Calculate P&L
- ❌ Create MT5 data
- ❌ Modify synced balances
- ✅ ONLY store what VPS API provides

### 1.5 Backend API (Data Provider)
- **Location:** Render.com
- **Technology:** FastAPI
- **Role:** Provide MT5 data to frontend from MongoDB cache
- **Endpoints:** Various client/admin endpoints

**Example Endpoints:**
```
GET /api/client/{client_id}/mt5-accounts
GET /api/client/{client_id}/portfolio
GET /api/admin/mt5/accounts
POST /api/admin/sync-from-vps (manual sync trigger)
```

### 1.6 Frontend (Display)
- **Location:** Render.com
- **Technology:** React.js / Next.js
- **Role:** Display MT5 account data to users
- **Data Source:** Backend API (reads from MongoDB cache)
- **Refresh:** On page load / user action

**Key Pages:**
- Client Portfolio Dashboard
- MT5 Accounts Management
- Cash Flow & Performance
- Admin Dashboard

---

## 2. Complete Data Flow Sequence

### Scenario: User trades on MT5, balance changes

**Step-by-Step:**

1. **Trade Execution (MT5 Terminal)**
   - User places trade in MT5 terminal
   - Trade executes on MEXAtlantic-Real server
   - MT5 updates account balance immediately
   - Balance: $24,638.97 → $27,047.52

2. **Waiting Period**
   - New balance exists in MT5 terminal
   - VPS Bridge can read it (via mt5.login() + mt5.account_info())
   - MongoDB still has old data ($24,638.97)
   - Frontend still shows old data

3. **Scheduled Sync Triggers (Every 5 minutes)**
   - Time: XX:01 (e.g., 15:51:00)
   - APScheduler calls `automatic_vps_sync()`
   - Backend VPS Sync Service starts

4. **Health Check**
   ```
   GET http://92.118.45.135:8000/api/mt5/bridge/health
   Response: {"status": "healthy", "mt5": {"available": true}}
   ```

5. **Fetch Account List**
   ```
   GET http://92.118.45.135:8000/api/mt5/accounts/summary
   Response: {"accounts": [{"account": 891215, ...}, ...]}
   ```

6. **Fetch Live Data for Each Account**
   ```
   For account 891215:
   GET http://92.118.45.135:8000/api/mt5/account/891215/info
   
   Response:
   {
     "account_id": 891215,
     "live_data": {
       "balance": 27047.52,      ← LIVE from MT5 terminal
       "equity": 27047.52,
       "profit": 0.0,
       "margin": 0,
       "margin_free": 27047.52,
       "currency": "USD"
     },
     "stored_data": {
       "balance": 24638.97       ← OLD MongoDB data
     }
   }
   ```

7. **Update MongoDB**
   ```python
   await db.mt5_accounts.update_one(
       {'account': 891215},
       {'$set': {
           'balance': 27047.52,      # Updated!
           'equity': 27047.52,
           'profit': 0.0,
           'updated_at': datetime.now(timezone.utc),
           'synced_from_vps': True,
           'data_source': 'VPS_LIVE_MT5'
       }}
   )
   ```

8. **Sync Complete**
   - Duration: ~8 seconds
   - Accounts synced: 7/7
   - Status: Success
   - Log: "✅ VPS sync complete: 7/7 accounts synced in 7.99s"

9. **User Loads Portfolio Page**
   - Frontend calls: `GET /api/client/alejandro/mt5-accounts`
   - Backend reads from MongoDB
   - Returns: `[{account: 891215, balance: 27047.52, ...}]`
   - Frontend displays: **$27,047.52** ✅

10. **Next Sync**
    - 5 minutes later (XX:06)
    - Process repeats
    - Keeps data fresh

---

## 3. Sync Schedule Details

### Frequency
- **Interval:** Every 5 minutes (12 times per hour, 288 times per day)
- **Offset:** 1 minute after the hour mark (to avoid conflict with VPS internal processes)

### Execution Times
```
:01, :06, :11, :16, :21, :26, :31, :36, :41, :46, :51, :56
```

**Example timeline:**
```
15:01:00 - Sync starts
15:01:08 - Sync complete (7/7 accounts)
15:05:00 - (no sync)
15:06:00 - Sync starts
15:06:08 - Sync complete
...
```

### Configuration (server.py)
```python
scheduler.add_job(
    automatic_vps_sync,
    'cron',
    minute='1,6,11,16,21,26,31,36,41,46,51,56',
    id='auto_vps_sync',
    replace_existing=True
)
```

### Performance Metrics
- **Average duration:** 7-8 seconds
- **Success rate:** 100% (7/7 accounts)
- **Network calls:** 9 per sync (1 health + 1 summary + 7 accounts)
- **MongoDB updates:** 7 per sync

---

## 4. Error Handling & Recovery

### 4.1 VPS API Unreachable

**Scenario:** VPS is down or network issue

**Detection:**
```python
health = await vps_sync.check_vps_health()
if not health.get('healthy'):
    logger.error(f"❌ VPS Bridge unhealthy: {health.get('error')}")
    return  # Skip this sync cycle
```

**Action:**
- Log error
- Skip sync cycle
- Keep old data in MongoDB
- Retry on next cycle (5 minutes)

**Alert:** If VPS down >10 minutes (2 consecutive failed syncs)

**Recovery:** Automatic on next successful health check

### 4.2 Single Account Fails

**Scenario:** One account's data fetch fails (network timeout, MT5 login issue)

**Detection:**
```python
try:
    result = await vps_sync.fetch_from_vps(f'/api/mt5/account/{account_id}/info')
    if 'error' in result:
        logger.error(f"❌ Failed to fetch account {account_id}")
        failed_accounts.append(account_id)
        continue  # Move to next account
except Exception as e:
    logger.error(f"❌ Error syncing account {account_id}: {e}")
    failed_accounts.append(account_id)
```

**Action:**
- Log specific account error
- Continue syncing other accounts
- Retry failed account on next cycle

**Alert:** If same account fails 3 times in a row

### 4.3 MongoDB Unavailable

**Scenario:** MongoDB Atlas connection issue

**Detection:**
```python
try:
    await db.mt5_accounts.update_one(...)
except Exception as e:
    logger.error(f"❌ MongoDB error: {e}")
```

**Action:**
- Log error
- VPS data not lost (will re-fetch on next cycle)
- Retry on next sync

**Alert:** If MongoDB down >5 minutes

### 4.4 Network Timeout

**Scenario:** VPS API response too slow

**Configuration:**
```python
async with httpx.AsyncClient(timeout=30) as client:
    response = await client.get(url)
```

**Action:**
- Wait up to 30 seconds
- If timeout, log error
- Skip account
- Retry next cycle

### 4.5 Partial Data (live_data missing)

**Scenario:** VPS returns success but no live_data field

**Detection:**
```python
live_data = account_result.get('live_data', {})
if not live_data:
    logger.warning(f"⚠️  No live data for account {account_id}, using stored data")
    stored_data = account_result.get('stored_data', {})
    balance = stored_data.get('balance', 0)
```

**Action:**
- Use stored_data as fallback
- Mark data_source as "VPS_STORED" (not "VPS_LIVE_MT5")
- Log warning
- Retry on next cycle

---

## 5. Data Freshness & Staleness

### Freshness Metrics

**Ideal State:**
- Data age: <5 minutes
- Last sync: Within last 5 minutes
- All accounts updated

**Acceptable State:**
- Data age: 5-10 minutes
- Last sync: 1 missed cycle
- >5 accounts updated

**Degraded State:**
- Data age: 10-15 minutes
- Last sync: 2 missed cycles
- <5 accounts updated

**Critical State:**
- Data age: >15 minutes
- Last sync: 3+ missed cycles
- <3 accounts updated

### Staleness Detection

**In MongoDB:**
```python
account = await db.mt5_accounts.find_one({'account': 891215})
age = (datetime.now(timezone.utc) - account['updated_at']).total_seconds() / 60

if age > 10:
    logger.warning(f"⚠️ Account {account_id} data is {age:.1f} minutes old")
if age > 15:
    logger.error(f"❌ Account {account_id} data is STALE ({age:.1f} minutes)")
```

**Frontend Indicator:**
```javascript
const lastUpdated = new Date(account.updated_at);
const ageMinutes = (Date.now() - lastUpdated) / 1000 / 60;

if (ageMinutes > 10) {
  showWarning("Account data may be outdated");
}
```

---

## 6. Monitoring & Health Checks

### 6.1 VPS Bridge Health

**Endpoint:** `GET /api/mt5/bridge/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T15:53:19Z",
  "mt5": {
    "available": true,
    "terminal_info": {
      "connected": true,
      "trade_allowed": true,
      "name": "MEXAtlantic-Real",
      "company": "MEX Atlantic",
      "build": 3770
    }
  },
  "mongodb": {
    "connected": true
  }
}
```

**What it checks:**
- MT5 terminal initialized
- MT5 terminal connected to broker
- Trading allowed
- MongoDB connection

### 6.2 Sync Status Monitoring

**Logs to check:**
```bash
# Backend sync logs
tail -f /var/log/supervisor/backend.err.log | grep "VPS sync"

# Look for:
✅ VPS sync complete: 7/7 accounts synced in 7.99s
❌ VPS sync failed: [error]
⚠️  No live data for account [id]
```

**MongoDB check:**
```python
# Check last sync time
accounts = await db.mt5_accounts.find().to_list(length=None)
latest_sync = max(acc['updated_at'] for acc in accounts)
age = (datetime.now(timezone.utc) - latest_sync).total_seconds() / 60
print(f"Latest sync: {age:.1f} minutes ago")
```

### 6.3 Health Check Endpoint (Backend)

**Coming soon:** `GET /api/admin/mt5-health`

**Will return:**
```json
{
  "status": "healthy",
  "vps_api": {
    "reachable": true,
    "response_time": 0.8,
    "status": "healthy"
  },
  "data_freshness": {
    "oldest_update": "2 minutes ago",
    "staleness": "fresh"
  },
  "last_sync": {
    "time": "2025-10-24T15:53:19Z",
    "success": true,
    "accounts_synced": "7/7",
    "duration": 7.99
  },
  "issues": []
}
```

---

## 7. Reliability Measures

### Automatic Recovery
- Sync runs every 5 minutes automatically
- No manual intervention needed
- Recovers from temporary failures
- Logs all operations

### Retry Logic
- VPS unreachable: Retry next cycle
- Single account fails: Retry next cycle
- Network timeout: Retry next cycle
- MongoDB unavailable: Retry next cycle

### Redundancy
- Multiple sync cycles per hour
- Fallback to stored_data if live_data unavailable
- Continue syncing other accounts if one fails

### Logging
- All syncs logged with results
- All errors logged with details
- Timestamps on every operation
- Success/failure tracking

### Data Integrity
- Never modify synced data
- Never generate fake data
- Only store what VPS provides
- Validate data before storing

---

## 8. Architecture Diagrams

### High-Level Flow
```
┌─────────────────┐
│  MT5 Terminal   │  ← SINGLE SOURCE OF TRUTH
│   (VPS Server)  │
└────────┬────────┘
         │ mt5.account_info()
         ↓
┌─────────────────┐
│ VPS MT5 Bridge  │  ← Gateway (Port 8000)
│   FastAPI API   │
└────────┬────────┘
         │ HTTP GET /api/mt5/account/{id}/info
         ↓
┌─────────────────┐
│  Backend Sync   │  ← Fetcher (Every 5 min)
│    Service      │
└────────┬────────┘
         │ update_one()
         ↓
┌─────────────────┐
│    MongoDB      │  ← Read-Only Cache
│  mt5_accounts   │
└────────┬────────┘
         │ find()
         ↓
┌─────────────────┐
│  Backend API    │  ← Data Provider
│    FastAPI      │
└────────┬────────┘
         │ HTTP GET
         ↓
┌─────────────────┐
│    Frontend     │  ← Display
│   React/Next    │
└─────────────────┘
```

### Sync Process Detail
```
1. TRIGGER (APScheduler - Every 5 min)
   ↓
2. HEALTH CHECK
   GET http://92.118.45.135:8000/api/mt5/bridge/health
   ↓
   Healthy? ──NO──> Skip cycle, log error, retry in 5 min
   │
   YES
   ↓
3. GET ACCOUNT LIST
   GET http://92.118.45.135:8000/api/mt5/accounts/summary
   ↓
4. FOR EACH ACCOUNT (7 accounts)
   ├─> GET http://92.118.45.135:8000/api/mt5/account/886557/info
   ├─> GET http://92.118.45.135:8000/api/mt5/account/886066/info
   ├─> GET http://92.118.45.135:8000/api/mt5/account/886602/info
   ├─> GET http://92.118.45.135:8000/api/mt5/account/885822/info
   ├─> GET http://92.118.45.135:8000/api/mt5/account/886528/info
   ├─> GET http://92.118.45.135:8000/api/mt5/account/891215/info
   └─> GET http://92.118.45.135:8000/api/mt5/account/891234/info
   ↓
5. EXTRACT live_data FROM EACH RESPONSE
   {
     "live_data": {
       "balance": 27047.52,
       "equity": 27047.52,
       "profit": 0.0
     }
   }
   ↓
6. UPDATE MONGODB (7 updates)
   db.mt5_accounts.update_one(
     {'account': 891215},
     {'$set': {'balance': 27047.52, ...}}
   )
   ↓
7. LOG RESULTS
   "✅ VPS sync complete: 7/7 accounts synced in 7.99s"
   ↓
8. WAIT 5 MINUTES
   ↓
9. REPEAT
```

---

## 9. Critical Success Factors

### What Makes This Work

1. **Simple Architecture**
   - No complex calculations
   - No data transformation
   - Just fetch and store

2. **Single Source of Truth**
   - MT5 terminal is authoritative
   - No conflicting data sources
   - Clear data lineage

3. **Automatic Recovery**
   - Scheduled sync runs automatically
   - Recovers from temporary failures
   - No manual intervention needed

4. **Proper Error Handling**
   - Continues on single failures
   - Logs all errors
   - Retries automatically

5. **Data Integrity**
   - Never modify synced data
   - Never generate fake data
   - Only store what VPS provides

### What Could Break This

1. **VPS Down for Extended Period**
   - Impact: Data becomes stale
   - Mitigation: VPS is stable, auto-healing in place
   - Detection: Health checks alert after 10 min

2. **MongoDB Unavailable**
   - Impact: Can't cache new data
   - Mitigation: MongoDB Atlas is highly available
   - Recovery: Automatic when MongoDB returns

3. **Network Issues**
   - Impact: Can't reach VPS from backend
   - Mitigation: Retry logic, timeout handling
   - Recovery: Automatic when network stable

4. **MT5 Master Account Login Fails**
   - Impact: Can't read MT5 data
   - Mitigation: Password stored securely in MongoDB
   - Recovery: Requires manual intervention to fix password

5. **Backend Crashes**
   - Impact: Sync stops
   - Mitigation: Supervisor auto-restarts backend
   - Recovery: Sync resumes automatically on restart

---

## 10. Validation & Testing

### How to Verify System is Working

**Test 1: Check VPS Health**
```bash
curl http://92.118.45.135:8000/api/mt5/bridge/health
# Should return: {"status": "healthy"}
```

**Test 2: Check Live Data**
```bash
curl http://92.118.45.135:8000/api/mt5/account/891215/info | jq '.live_data.balance'
# Should return current MT5 balance (e.g., 27047.52)
```

**Test 3: Check MongoDB Data**
```python
account = await db.mt5_accounts.find_one({'account': 891215})
print(f"Balance: ${account['balance']:,.2f}")
print(f"Updated: {account['updated_at']}")
print(f"Data source: {account['data_source']}")
# Should show: VPS_LIVE_MT5, recent timestamp
```

**Test 4: Check Backend Logs**
```bash
tail -f /var/log/supervisor/backend.err.log | grep "VPS sync"
# Should see: ✅ VPS sync complete: 7/7 accounts synced
```

**Test 5: Check Frontend**
- Login to client portal
- View MT5 accounts
- Verify balances match VPS
- Check "Last updated" timestamp

### Manual Sync Test
```bash
# Trigger manual sync (requires admin auth)
curl -X POST https://fidus-api.onrender.com/api/admin/sync-from-vps \
  -H "Authorization: Bearer {admin_token}"

# Response should show:
{
  "status": "success",
  "accounts_synced": 7,
  "total_accounts": 7
}
```

---

## 11. Maintenance & Operations

### Daily Operations
- Check backend logs for sync status
- Verify all 7 accounts syncing successfully
- Monitor data freshness (<5 minutes)

### Weekly Tasks
- Review sync success rate (should be >99%)
- Check for any recurring errors
- Verify frontend displays current data

### Monthly Tasks
- Review VPS uptime
- Check MongoDB performance
- Update documentation if needed

### Troubleshooting
See `MT5_TROUBLESHOOTING.md` for common issues and solutions.

---

## 12. Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-24 | 1.0 | Initial documentation - VPS sync service implemented |

---

## 13. References

- **VPS MT5 Bridge:** `http://92.118.45.135:8000`
- **Backend Sync Service:** `/app/backend/vps_sync_service.py`
- **Sync Function:** `/app/backend/server.py` → `automatic_vps_sync()`
- **Fix Summary:** `/app/VPS_SYNC_FIX_SUMMARY.md`

---

**Document Status:** ✅ Complete and Active
