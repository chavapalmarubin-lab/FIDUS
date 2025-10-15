# Phase 2: Backend API Documentation

## Overview

Phase 2 implements a single unified backend API that serves as the bridge between VPS MT5 Bridge Service and the frontend. All data comes from MongoDB `mt5_accounts` collection, which is automatically synced every 5 minutes by the VPS service.

---

## API Endpoints

### 1. Get All MT5 Accounts (Admin)

**Endpoint:** `GET /api/mt5/admin/accounts`

**Authentication:** Required (Admin JWT token)

**Description:** Returns all 7 MT5 trading accounts with real-time data from VPS Bridge.

**Response Structure:**
```json
{
  "success": true,
  "accounts": [
    {
      "mt5_login": 886557,
      "fund_code": "BALANCE",
      "broker_name": "Main Balance Account",
      "current_equity": 84973.66,
      "profit_loss": 4973.66,
      "profit_loss_percentage": 4.97,
      "balance": 80000.00,
      "margin": 1000.00,
      "free_margin": 83973.66,
      "margin_level": 8497.37,
      "connection_status": "active",
      "is_fresh": true,
      "data_age_minutes": 2.3,
      "last_updated": "2025-10-15T11:28:00Z",
      "currency": "USD",
      "leverage": 500
    }
  ],
  "summary": {
    "total_accounts": 7,
    "total_allocated": 134741.72,
    "total_equity": 132840.45,
    "total_profit_loss": 6689.04,
    "overall_performance_percentage": 4.96,
    "fresh_accounts": 7,
    "stale_accounts": 0
  },
  "timestamp": "2025-10-15T11:30:00Z",
  "data_source": "MongoDB mt5_accounts (VPS Bridge - every 5 min)"
}
```

**Data Freshness Indicators:**
- `is_fresh`: Boolean - true if data is less than 10 minutes old
- `data_age_minutes`: Number - exact age of data in minutes
- `connection_status`: String - "active" (fresh), "stale" (>10 min), "disconnected" (never synced)

**Summary Fields:**
- `fresh_accounts`: Count of accounts with data <10 minutes old
- `stale_accounts`: Count of accounts with data >10 minutes old

---

### 2. Public Health Check

**Endpoint:** `GET /api/mt5/health/public`

**Authentication:** None required (public endpoint)

**Description:** Quick health check for monitoring. Returns sync status without exposing sensitive data.

**Response Structure:**
```json
{
  "status": "healthy",
  "healthy": true,
  "message": "7/7 accounts have fresh data",
  "accounts_count": 7,
  "fresh_accounts": 7,
  "stale_accounts_count": 0,
  "stale_accounts": null,
  "timestamp": "2025-10-15T11:30:00Z"
}
```

**Status Values:**
- `"healthy"`: All accounts have fresh data (<10 minutes)
- `"degraded"`: Some accounts have stale data (>10 minutes)
- `"error"`: No accounts found or system error

**Use Cases:**
- Monitoring dashboards
- Uptime checks
- Status pages
- Automated alerts

---

### 3. Detailed Health Check (Admin)

**Endpoint:** `GET /api/mt5/sync/health`

**Authentication:** Required (Admin JWT token)

**Description:** Comprehensive health check with detailed account-level information.

**Response Structure:**
```json
{
  "success": true,
  "health": {
    "status": "healthy",
    "message": "All 7 accounts syncing properly",
    "service_running": true,
    "timestamp": "2025-10-15T11:30:00Z",
    "accounts": {
      "total": 7,
      "expected": 7,
      "fresh": 7,
      "stale": 0,
      "never_synced": 0
    },
    "fresh_accounts": [
      {
        "account": 886557,
        "minutes_since_sync": 2.3,
        "last_sync": "2025-10-15T11:28:00Z",
        "equity": 84973.66,
        "profit": 4973.66
      }
    ],
    "stale_accounts": null,
    "missing_accounts": null,
    "sync_threshold_minutes": 10
  },
  "timestamp": "2025-10-15T11:30:00Z"
}
```

---

## Data Flow Architecture

```
MT5 Terminal (VPS)
    ↓ (Python Bridge - every 5 minutes)
MongoDB Atlas (mt5_accounts collection)
    ↓ (Backend API - on request)
Frontend (React Dashboard)
```

**Single Source of Truth:** MT5 Terminal on VPS

**Update Frequency:** Every 5 minutes (300 seconds)

**Stale Threshold:** 10 minutes (after 2 missed sync cycles)

---

## MongoDB Schema

**Collection:** `mt5_accounts`

**Document Structure:**
```javascript
{
  account: 886557,                    // MT5 account number
  name: "Main Balance Account",       // Account name
  fund_type: "BALANCE",               // BALANCE, CORE, or SEPARATION
  target_amount: 100000.00,           // Target allocation
  server: "MEXAtlantic-Real",         // MT5 server
  broker: "MEXAtlantic",              // Broker name
  balance: 80000.00,                  // Current balance
  equity: 84973.66,                   // Current equity
  margin: 1000.00,                    // Used margin
  free_margin: 83973.66,              // Free margin
  margin_level: 8497.37,              // Margin level %
  profit: 4973.66,                    // Current P&L
  num_positions: 3,                   // Open positions count
  currency: "USD",                    // Account currency
  leverage: 500,                      // Leverage ratio
  connection_status: "active",        // Sync status
  last_sync: ISODate("2025-10-15T11:28:00Z"),    // Last sync timestamp
  updated_at: ISODate("2025-10-15T11:28:00Z")    // Last update timestamp
}
```

---

## Phase 2 Changes Summary

### ✅ Completed

1. **MT5 Admin Accounts Endpoint Enhanced**
   - Added data freshness validation
   - Added `is_fresh`, `data_age_minutes`, `connection_status` fields
   - Added summary with `fresh_accounts` and `stale_accounts` counts
   - Added `data_source` field for transparency

2. **Public Health Endpoint Created**
   - No authentication required
   - Returns sync status for monitoring
   - Shows account counts and freshness

3. **MockMT5Service Deprecated**
   - Added warning comments
   - Documented that it should NOT be used for new endpoints
   - All MT5 endpoints now use real MongoDB data

4. **Backend Restart & Testing**
   - Backend restarted successfully
   - Endpoints tested and verified
   - Response structure validated

### 🔄 Pending VPS Sync

**Current Status:** Backend is ready, but data is stale (9+ hours old)

**Waiting For:** VPS MT5 Bridge Service to start syncing fresh data

**Once VPS Syncs:**
- All endpoints will return fresh data (<10 minutes old)
- `is_fresh` will be `true`
- `connection_status` will be `"active"`
- Frontend can safely consume real-time data

---

## Testing Instructions

### Test 1: Check MT5 Admin Accounts (requires auth)
```bash
# Get JWT token first (login as admin)
TOKEN="your_jwt_token_here"

# Test endpoint
curl -X GET "https://fidus-invest.emergent.host/api/mt5/admin/accounts" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected:** Returns all 7 accounts with data

### Test 2: Check Public Health (no auth)
```bash
curl -X GET "https://fidus-invest.emergent.host/api/mt5/health/public" \
  | python3 -m json.tool
```

**Expected:**
- When VPS is syncing: `"healthy": true`, `"fresh_accounts": 7`
- When VPS is down: `"healthy": false`, `"stale_accounts_count": 7`

### Test 3: Monitor Data Freshness
```bash
# Check every minute to see when data becomes fresh
watch -n 60 'curl -s https://fidus-invest.emergent.host/api/mt5/health/public | python3 -m json.tool'
```

---

## Success Criteria

### ✅ Phase 2 Complete When:

1. **Backend Endpoints Ready**
   - ✅ `/api/mt5/admin/accounts` returns all 7 accounts
   - ✅ `/api/mt5/health/public` returns health status
   - ✅ Data freshness validation working
   - ✅ No mock data used

2. **Data Flow Verified**
   - ⏳ VPS Bridge syncing every 5 minutes (Chava verifying)
   - ⏳ MongoDB receiving fresh data
   - ⏳ Backend serving fresh data (<10 min old)

3. **Documentation Complete**
   - ✅ API endpoints documented
   - ✅ Response structures defined
   - ✅ Testing instructions provided
   - ✅ Success criteria listed

---

## Next Steps (Phase 3)

Once VPS is confirmed syncing:

1. **Frontend Integration**
   - Create `useMT5Data` hook
   - Replace all mock data in frontend
   - Add data freshness indicators in UI
   - Show stale data warnings

2. **Testing**
   - End-to-end data flow testing
   - Frontend displays match backend data
   - Auto-refresh working

3. **Monitoring**
   - Health widget on admin dashboard
   - Alerts for stale data
   - Service status indicators

---

## Troubleshooting

### Backend Returns Stale Data

**Symptom:** `is_fresh: false`, `data_age_minutes > 10`

**Cause:** VPS Bridge Service not syncing

**Solution:**
1. Check VPS service status
2. Verify MongoDB connection string
3. Check VPS logs
4. Restart VPS service if needed

### Backend Returns 404

**Symptom:** "No MT5 accounts found"

**Cause:** MongoDB collection empty

**Solution:**
1. Run VPS bridge at least once
2. Verify MongoDB URI correct
3. Check database name: `fidus_production`
4. Check collection name: `mt5_accounts`

### Health Check Shows All Stale

**Symptom:** `stale_accounts: 7`, `fresh_accounts: 0`

**Cause:** VPS Bridge not running or not writing

**Solution:**
1. Verify Windows Service running on VPS
2. Check VPS logs for errors
3. Verify MT5 Terminal is running
4. Check MongoDB network access

---

**Phase 2 Backend: COMPLETE ✅**

**Waiting on:** VPS Bridge sync confirmation from Chava

**Ready for:** Phase 3 (Frontend) once data is fresh
