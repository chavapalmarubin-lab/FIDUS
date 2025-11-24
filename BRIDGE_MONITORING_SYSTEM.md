# Bridge Monitoring System Documentation
**Created:** November 24, 2025  
**Version:** 1.0

## Overview

Complete monitoring system for the 3-bridge architecture that syncs 15 trading accounts to the FIDUS platform.

---

## Architecture

### Three Independent Bridges

| Bridge | Script | Accounts | Platform | Server |
|--------|--------|----------|----------|--------|
| **MEXAtlantic MT5** | `mt5_bridge_mexatlantic.py` | 13 | MT5 | MEXAtlantic-Real |
| **Lucrum MT5** | `mt5_bridge_lucrum.py` | 1 (2198) | MT5 | LucrumCapital-Trade |
| **MEXAtlantic MT4** | `mt4_bridge_mexatlantic.py` | 1 (33200931) | MT4 | MEXAtlantic-Real |

**Total:** 15 accounts syncing every 120 seconds

---

## Monitoring Features

### 1. Health Check API

**Endpoint:** `GET /api/bridges/health`

Returns comprehensive status for all 3 bridges:

```json
{
  "status": "healthy",
  "bridges": {
    "mexatlantic_mt5": {
      "status": "running",
      "accounts": 13,
      "expected_accounts": 13,
      "last_sync": "2025-11-24T19:02:31.751000",
      "healthy": true,
      "broker": "MEXAtlantic",
      "platform": "MT5",
      "server": "MEXAtlantic-Real"
    },
    "lucrum_mt5": {
      "status": "running",
      "accounts": 1,
      "expected_accounts": 1,
      "last_sync": "2025-11-24T19:02:25.321000",
      "healthy": true,
      "broker": "Lucrum Capital",
      "platform": "MT5",
      "server": "LucrumCapital-Trade"
    },
    "mexatlantic_mt4": {
      "status": "running",
      "accounts": 1,
      "expected_accounts": 1,
      "last_sync": "2025-11-24T19:02:21.911000",
      "healthy": true,
      "broker": "MEXAtlantic",
      "platform": "MT4",
      "server": "MEXAtlantic-Real"
    }
  },
  "total_accounts": 15,
  "expected_total": 15,
  "timestamp": "2025-11-24T19:04:17.002844+00:00"
}
```

### 2. Accounts List API

**Endpoint:** `GET /api/bridges/accounts`

Returns all 15 accounts with platform and broker information:

```json
{
  "success": true,
  "accounts": [
    {
      "account": 886557,
      "broker": "MEXAtlantic",
      "platform": "MT5",
      "bridge": "mexatlantic_mt5",
      "server": "MEXAtlantic-Real",
      "balance": 50000.00,
      "equity": 51500.00,
      "positions_count": 2,
      "last_sync": "2025-11-24T19:02:31Z"
    }
  ],
  "total_accounts": 15,
  "by_bridge": {
    "mexatlantic_mt5": 13,
    "lucrum_mt5": 1,
    "mexatlantic_mt4": 1
  }
}
```

### 3. Real-Time Alerts API

**Endpoint:** `GET /api/bridges/alerts`

Returns current alerts for any bridge issues:

```json
{
  "alerts": [
    {
      "bridge": "lucrum_mt5",
      "severity": "warning",
      "message": "Data not synced in >5 minutes for lucrum_mt5",
      "timestamp": "2025-11-24T19:04:30Z",
      "details": {
        "status": "stale_data",
        "accounts": 1,
        "last_sync": "2025-11-24T17:54:18Z"
      }
    }
  ],
  "total_alerts": 1
}
```

### 4. Alert History API

**Endpoint:** `GET /api/bridges/alerts/history?hours=24&bridge_id=lucrum_mt5`

Returns historical alerts from the database:

```json
{
  "alerts": [
    {
      "bridge_id": "lucrum_mt5",
      "bridge_name": "Lucrum MT5",
      "severity": "warning",
      "status": "stale_data",
      "issues": ["Data not synced in 12 minutes"],
      "timestamp": "2025-11-24T18:56:30Z",
      "acknowledged": false
    }
  ],
  "total_alerts": 5,
  "period_hours": 24
}
```

### 5. Monitoring Service Status

**Endpoint:** `GET /api/bridges/monitoring/status`

Returns the status of the background monitoring service:

```json
{
  "service_running": true,
  "check_interval_seconds": 60,
  "alert_threshold_minutes": 5,
  "bridges_monitored": 3,
  "bridge_list": ["mexatlantic_mt5", "lucrum_mt5", "mexatlantic_mt4"]
}
```

---

## Frontend Dashboard

### Bridge Health Monitor Component

**Location:** `/app/frontend/src/components/BridgeHealthMonitor.jsx`

**Features:**
- Real-time bridge status cards with health indicators
- Overall system status with metrics (15 accounts, bridge count, alerts)
- Active alerts section with severity badges
- Complete accounts table with Platform (MT4/MT5) and Broker columns
- Last sync timestamps with human-readable format
- Auto-refresh every 30 seconds
- Manual refresh button

**Access:** Admin Dashboard → "🔌 Bridge Monitor" tab

---

## Background Monitoring Service

### Automatic Health Checks

**Service:** `BridgeMonitoringService`  
**Location:** `/app/backend/services/bridge_monitoring_service.py`

**Features:**
- Runs every 60 seconds in the background
- Checks all 3 bridges for:
  - Stale data (>5 minutes since last sync)
  - Missing accounts (expected vs actual count)
  - Connection failures
- Automatically logs warnings and errors
- Stores alert history in MongoDB (`bridge_alerts` collection)

**Startup:** Automatically initialized when FastAPI server starts

---

## Alert Types and Severity

### Severity Levels

1. **Critical** (Red)
   - No accounts found for a bridge
   - Bridge completely offline

2. **Warning** (Orange)
   - Stale data (no sync in >5 minutes)
   - Account count mismatch (expected ≠ actual)

### Alert Conditions

- **Stale Data:** Last sync timestamp > 5 minutes ago
- **Missing Accounts:** Actual account count ≠ expected count
- **No Accounts:** Zero accounts found for a bridge

---

## MongoDB Collections

### mt5_accounts

Contains all 15 accounts with:
- Account number, broker, platform (MT4/MT5)
- Balance, equity, margin, positions
- `last_sync_timestamp` - Used for health monitoring
- `platform` field - "MT4" or "MT5" (default: MT5 for legacy accounts)
- `data_source` field - "MT4_FILE_BRIDGE" for MT4 accounts

### bridge_alerts

Stores historical alerts:
- `bridge_id` - Bridge identifier
- `bridge_name` - Human-readable name
- `severity` - "critical" or "warning"
- `status` - "stale_data", "no_accounts", "error"
- `issues` - Array of issue descriptions
- `timestamp` - When alert was created
- `acknowledged` - Boolean flag for alert acknowledgment

---

## Testing Endpoints

### Test Health Check
```bash
curl http://localhost:8001/api/bridges/health | jq
```

### Test Accounts List
```bash
curl http://localhost:8001/api/bridges/accounts | jq
```

### Test Current Alerts
```bash
curl http://localhost:8001/api/bridges/alerts | jq
```

### Test Alert History (Last 24 Hours)
```bash
curl "http://localhost:8001/api/bridges/alerts/history?hours=24" | jq
```

### Test Monitoring Status
```bash
curl http://localhost:8001/api/bridges/monitoring/status | jq
```

---

## Configuration

### Alert Threshold

Default: **5 minutes**

To change, modify `alert_threshold_minutes` in:
- `/app/backend/services/bridge_monitoring_service.py`

### Check Interval

Default: **60 seconds**

To change, modify `check_interval_seconds` in:
- `/app/backend/services/bridge_monitoring_service.py`

### Bridge Configuration

To add/modify bridges, update `bridges_config` in:
- `/app/backend/services/bridge_monitoring_service.py`
- `/app/backend/routes/bridge_health.py`

---

## Complete Account List (15 Accounts)

| # | Account | Broker | Platform | Bridge | Description |
|---|---------|--------|----------|--------|-------------|
| 1 | 886557 | MEXAtlantic | MT5 | mexatlantic_mt5 | Main Balance |
| 2 | 886066 | MEXAtlantic | MT5 | mexatlantic_mt5 | Secondary Balance |
| 3 | 886602 | MEXAtlantic | MT5 | mexatlantic_mt5 | Tertiary Balance |
| 4 | 885822 | MEXAtlantic | MT5 | mexatlantic_mt5 | Core |
| 5 | 886528 | MEXAtlantic | MT5 | mexatlantic_mt5 | Separation |
| 6 | 891215 | MEXAtlantic | MT5 | mexatlantic_mt5 | Interest Earnings |
| 7 | 891234 | MEXAtlantic | MT5 | mexatlantic_mt5 | CORE Fund |
| 8 | 897590 | MEXAtlantic | MT5 | mexatlantic_mt5 | CORE - CP Strategy 2 |
| 9 | 897589 | MEXAtlantic | MT5 | mexatlantic_mt5 | BALANCE - MEXAtlantic |
| 10 | 897591 | MEXAtlantic | MT5 | mexatlantic_mt5 | Interest Segregation 1 |
| 11 | 897599 | MEXAtlantic | MT5 | mexatlantic_mt5 | Interest Segregation 2 |
| 12 | 901351 | MEXAtlantic | MT5 | mexatlantic_mt5 | Unassigned |
| 13 | 901353 | MEXAtlantic | MT5 | mexatlantic_mt5 | Unassigned (Copy) |
| 14 | 2198 | Lucrum Capital | MT5 | lucrum_mt5 | LUCRUM Account |
| 15 | 33200931 | MEXAtlantic | MT4 | mexatlantic_mt4 | Money Manager |

---

## Integration Points

### 1. Admin Dashboard
- New tab: "🔌 Bridge Monitor"
- Shows all bridge statuses and accounts
- Real-time updates every 30 seconds

### 2. API Endpoints
- All endpoints prefixed with `/api/bridges/`
- Public endpoints (no authentication required for monitoring)
- RESTful design

### 3. Background Services
- Automatic startup with FastAPI server
- Runs independently in asyncio task
- Non-blocking, asynchronous health checks

---

## Troubleshooting

### Bridge Shows as "Unhealthy"

1. Check VPS bridge scripts are running:
   - MEXAtlantic MT5: `mt5_bridge_mexatlantic.py`
   - Lucrum MT5: `mt5_bridge_lucrum.py`
   - MEXAtlantic MT4: `mt4_bridge_mexatlantic.py`

2. Check VPS logs:
   - `C:\mt5_bridge_service\logs\mexatlantic.log`
   - `C:\mt5_bridge_service\logs\lucrum.log`
   - `C:\mt5_bridge_service\logs\mt4_mexatlantic.log`

3. Check MongoDB connectivity:
   ```bash
   curl http://localhost:8001/api/bridges/accounts | jq '.total_accounts'
   ```

### Alert Not Clearing

Alerts are based on real-time health checks. If a bridge is fixed:
1. Wait up to 60 seconds for next health check
2. Alert should automatically clear from current alerts
3. Historical alert remains in `bridge_alerts` collection

### Monitoring Service Not Running

Check startup logs:
```bash
tail -n 100 /var/log/supervisor/backend.*.log | grep "Bridge Monitoring"
```

Restart backend if needed:
```bash
sudo supervisorctl restart backend
```

---

## Files Created/Modified

### New Files
1. `/app/backend/routes/bridge_health.py` - Health check API endpoints
2. `/app/backend/services/bridge_monitoring_service.py` - Background monitoring service
3. `/app/frontend/src/components/BridgeHealthMonitor.jsx` - Dashboard component
4. `/app/BRIDGE_MONITORING_SYSTEM.md` - This documentation

### Modified Files
1. `/app/backend/server.py` - Added bridge health router and startup initialization
2. `/app/frontend/src/components/AdminDashboard.js` - Added Bridge Monitor tab

---

## Future Enhancements

1. **Email/SMS Alerts**
   - Send notifications when alerts are triggered
   - Integration with existing alert service

2. **Bridge Restart API**
   - Remote restart capability for bridges
   - Integration with VPS management

3. **Performance Metrics**
   - Track sync duration
   - Account update latency
   - Historical performance graphs

4. **Advanced Filtering**
   - Filter accounts by bridge, platform, broker
   - Search by account number
   - Sort by balance, equity, positions

5. **Alert Acknowledgment UI**
   - Mark alerts as acknowledged from dashboard
   - Add notes to alerts
   - Alert escalation rules

---

## Summary

✅ Complete monitoring system for 3-bridge architecture  
✅ Real-time health checks with 60-second intervals  
✅ Comprehensive API with 5 endpoints  
✅ Frontend dashboard with auto-refresh  
✅ Background alerting service with MongoDB persistence  
✅ All 15 accounts monitored (13 MT5 MEX + 1 MT5 Lucrum + 1 MT4 MEX)  
✅ Platform/Broker labeling for all accounts  
✅ Automatic startup with FastAPI server  

---

**Status:** ✅ COMPLETE AND OPERATIONAL
