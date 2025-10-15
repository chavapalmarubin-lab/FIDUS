# Phase 4A: Backend API Documentation - Deal History Endpoints

## Overview
Phase 4A adds 6 new API endpoints for MT5 deal history, rebates, analytics, and cash flow tracking.

All endpoints are prefixed with `/api/mt5/` and return JSON responses.

---

## Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/mt5/deals` | Get deal history with filters |
| GET | `/api/mt5/deals/summary` | Get aggregated deal statistics |
| GET | `/api/mt5/rebates` | Calculate broker rebates |
| GET | `/api/mt5/analytics/performance` | Get manager performance attribution |
| GET | `/api/mt5/balance-operations` | Get balance operations for cash flow |
| GET | `/api/mt5/daily-pnl` | Get daily P&L for equity curves |

---

## 1. GET /api/mt5/deals

Get MT5 deal history with optional filters.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_number` | int | No | Filter by MT5 account (e.g., 886557) |
| `start_date` | string | No | Filter from date (ISO format: 2025-01-01) |
| `end_date` | string | No | Filter to date (ISO format: 2025-01-31) |
| `symbol` | string | No | Filter by trading symbol (e.g., EURUSD) |
| `deal_type` | int | No | Filter by type (0=buy, 1=sell, 2=balance) |
| `limit` | int | No | Maximum deals to return (default: 1000) |

### Response

```json
{
  "success": true,
  "count": 245,
  "deals": [
    {
      "ticket": 12345678,
      "order": 87654321,
      "time": "2025-01-15T14:30:00+00:00",
      "type": 0,
      "entry": 1,
      "symbol": "EURUSD",
      "volume": 1.5,
      "price": 1.0850,
      "profit": 125.50,
      "commission": -7.50,
      "swap": -2.30,
      "position_id": 45678,
      "magic": 100234,
      "comment": "",
      "external_id": "EXT12345",
      "account_number": 886557,
      "account_name": "Main Balance Account",
      "fund_type": "BALANCE"
    }
  ],
  "filters": {
    "account_number": 886557,
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "symbol": "EURUSD",
    "deal_type": 0
  }
}
```

### Example Usage

```bash
# Get all deals for account 886557 in January 2025
curl "https://fidus-api.onrender.com/api/mt5/deals?account_number=886557&start_date=2025-01-01&end_date=2025-01-31"

# Get buy deals only for EURUSD
curl "https://fidus-api.onrender.com/api/mt5/deals?symbol=EURUSD&deal_type=0"

# Get balance operations for all accounts
curl "https://fidus-api.onrender.com/api/mt5/deals?deal_type=2"
```

---

## 2. GET /api/mt5/deals/summary

Get aggregated deal statistics.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_number` | int | No | Filter by MT5 account |
| `start_date` | string | No | Filter from date (ISO format) |
| `end_date` | string | No | Filter to date (ISO format) |

### Response

```json
{
  "success": true,
  "summary": {
    "total_deals": 1234,
    "total_volume": 156.5,
    "total_profit": 5432.10,
    "total_commission": -234.50,
    "total_swap": -45.30,
    "buy_deals": 567,
    "sell_deals": 645,
    "balance_operations": 22,
    "symbols_traded": ["EURUSD", "GBPUSD", "USDJPY", "GOLD"],
    "earliest_deal": "2024-10-15T08:30:00+00:00",
    "latest_deal": "2025-01-15T16:45:00+00:00",
    "date_range": {
      "start": "2024-10-15T08:30:00+00:00",
      "end": "2025-01-15T16:45:00+00:00"
    }
  }
}
```

### Example Usage

```bash
# Get summary for all accounts
curl "https://fidus-api.onrender.com/api/mt5/deals/summary"

# Get summary for specific account
curl "https://fidus-api.onrender.com/api/mt5/deals/summary?account_number=886557"

# Get summary for date range
curl "https://fidus-api.onrender.com/api/mt5/deals/summary?start_date=2025-01-01&end_date=2025-01-31"
```

---

## 3. GET /api/mt5/rebates

Calculate broker rebates based on trading volume.

**Formula**: `total_volume (lots) × rebate_per_lot ($5.05)`

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Calculate from date (ISO format) |
| `end_date` | string | No | Calculate to date (ISO format) |
| `account_number` | int | No | Filter by MT5 account |
| `rebate_per_lot` | float | No | Rebate per lot (default: $5.05) |

### Response

```json
{
  "success": true,
  "rebates": {
    "total_volume": 156.5,
    "total_commission": -234.50,
    "rebate_per_lot": 5.05,
    "total_rebates": 790.83,
    "by_account": [
      {
        "account": 886557,
        "account_name": "Main Balance Account",
        "fund_type": "BALANCE",
        "volume": 80.5,
        "commission": -120.25,
        "rebates": 406.53
      },
      {
        "account": 886066,
        "account_name": "Secondary Balance Account",
        "fund_type": "BALANCE",
        "volume": 45.0,
        "commission": -67.50,
        "rebates": 227.25
      }
    ],
    "by_symbol": [
      {
        "symbol": "EURUSD",
        "volume": 80.0,
        "deals": 234,
        "rebates": 404.00
      },
      {
        "symbol": "GBPUSD",
        "volume": 45.5,
        "deals": 156,
        "rebates": 229.78
      }
    ],
    "date_range": {
      "start": "2025-01-01T00:00:00+00:00",
      "end": "2025-01-31T23:59:59+00:00"
    }
  }
}
```

### Example Usage

```bash
# Calculate rebates for January 2025
curl "https://fidus-api.onrender.com/api/mt5/rebates?start_date=2025-01-01&end_date=2025-01-31"

# Calculate rebates for specific account
curl "https://fidus-api.onrender.com/api/mt5/rebates?account_number=886557"

# Calculate with custom rebate rate
curl "https://fidus-api.onrender.com/api/mt5/rebates?rebate_per_lot=6.00"
```

---

## 4. GET /api/mt5/analytics/performance

Get money manager performance attribution by magic number.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Filter from date (ISO format) |
| `end_date` | string | No | Filter to date (ISO format) |

### Response

```json
{
  "success": true,
  "count": 4,
  "managers": [
    {
      "magic": 100234,
      "manager_name": "TradingHub Gold",
      "total_deals": 234,
      "total_volume": 45.5,
      "total_profit": 2345.67,
      "total_commission": -68.25,
      "win_deals": 156,
      "loss_deals": 78,
      "win_rate": 66.67,
      "avg_profit_per_deal": 10.02,
      "accounts_used": [886557, 886066]
    },
    {
      "magic": 100235,
      "manager_name": "GoldenTrade",
      "total_deals": 189,
      "total_volume": 34.2,
      "total_profit": 1234.56,
      "total_commission": -51.30,
      "win_deals": 120,
      "loss_deals": 69,
      "win_rate": 63.49,
      "avg_profit_per_deal": 6.53,
      "accounts_used": [886602]
    }
  ]
}
```

### Manager Magic Number Mapping

| Magic | Manager Name |
|-------|--------------|
| 0 | Manual Trading |
| 100234 | TradingHub Gold |
| 100235 | GoldenTrade |
| 100236 | UNO14 MAM |
| 100237 | CP Strategy |

### Example Usage

```bash
# Get all manager performance
curl "https://fidus-api.onrender.com/api/mt5/analytics/performance"

# Get performance for date range
curl "https://fidus-api.onrender.com/api/mt5/analytics/performance?start_date=2025-01-01&end_date=2025-01-31"
```

---

## 5. GET /api/mt5/balance-operations

Get balance operations (type=2 deals) for cash flow tracking.

Identifies:
- Profit withdrawals
- Deposits
- Inter-account transfers
- Interest payments

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_number` | int | No | Filter by MT5 account |
| `start_date` | string | No | Filter from date (ISO format) |
| `end_date` | string | No | Filter to date (ISO format) |

### Response

```json
{
  "success": true,
  "count": 15,
  "operations": [
    {
      "ticket": 12345678,
      "time": "2025-01-15T14:30:00+00:00",
      "account_number": 886557,
      "account_name": "Main Balance Account",
      "profit": 5000.00,
      "comment": "Profit withdrawal",
      "operation_type": "withdrawal"
    },
    {
      "ticket": 12345679,
      "time": "2025-01-14T10:00:00+00:00",
      "account_number": 886528,
      "profit": 450.00,
      "comment": "Interest payment",
      "operation_type": "interest"
    },
    {
      "ticket": 12345680,
      "time": "2025-01-10T09:00:00+00:00",
      "account_number": 886557,
      "profit": -2000.00,
      "comment": "Transfer to 886066",
      "operation_type": "transfer"
    }
  ]
}
```

### Operation Types

| Type | Description | Typical Comment |
|------|-------------|-----------------|
| `withdrawal` | Profit withdrawn from account | "Profit withdrawal" |
| `deposit` | Funds added to account | "Deposit" |
| `transfer` | Inter-account transfer | "Transfer to XXXXX" |
| `interest` | Interest/separation account payment | "Interest payment" |
| `credit` | Generic credit operation | Various |
| `debit` | Generic debit operation | Various |
| `other` | Unclassified operation | Various |

### Example Usage

```bash
# Get all balance operations
curl "https://fidus-api.onrender.com/api/mt5/balance-operations"

# Get operations for specific account
curl "https://fidus-api.onrender.com/api/mt5/balance-operations?account_number=886557"

# Get operations for date range
curl "https://fidus-api.onrender.com/api/mt5/balance-operations?start_date=2025-01-01&end_date=2025-01-31"
```

---

## 6. GET /api/mt5/daily-pnl

Get daily P&L for equity curve charting.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_number` | int | No | Filter by MT5 account |
| `days` | int | No | Number of days to include (default: 30) |

### Response

```json
{
  "success": true,
  "days": 30,
  "data": [
    {
      "date": "2025-01-15",
      "pnl": 234.56,
      "volume": 5.5,
      "deals": 12,
      "commission": -8.25,
      "swap": -1.50
    },
    {
      "date": "2025-01-14",
      "pnl": -45.32,
      "volume": 3.2,
      "deals": 8,
      "commission": -4.80,
      "swap": -0.85
    }
  ]
}
```

### Example Usage

```bash
# Get daily P&L for last 30 days (all accounts)
curl "https://fidus-api.onrender.com/api/mt5/daily-pnl"

# Get daily P&L for specific account
curl "https://fidus-api.onrender.com/api/mt5/daily-pnl?account_number=886557"

# Get daily P&L for last 90 days
curl "https://fidus-api.onrender.com/api/mt5/daily-pnl?days=90"
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Failed to fetch deals: Connection error"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found
- `500`: Internal Server Error

---

## Testing Endpoints

### Using curl

```bash
# Set backend URL
BACKEND_URL="https://fidus-api.onrender.com"

# Test deals endpoint
curl "$BACKEND_URL/api/mt5/deals?account_number=886557&limit=10"

# Test summary endpoint
curl "$BACKEND_URL/api/mt5/deals/summary"

# Test rebates endpoint
curl "$BACKEND_URL/api/mt5/rebates?start_date=2025-01-01&end_date=2025-01-31"

# Test manager performance
curl "$BACKEND_URL/api/mt5/analytics/performance"

# Test balance operations
curl "$BACKEND_URL/api/mt5/balance-operations?account_number=886557"

# Test daily P&L
curl "$BACKEND_URL/api/mt5/daily-pnl?days=30"
```

### Using Python

```python
import requests

BACKEND_URL = "https://fidus-api.onrender.com"

# Get deals
response = requests.get(f"{BACKEND_URL}/api/mt5/deals", params={
    "account_number": 886557,
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
})
deals = response.json()

# Get rebates
response = requests.get(f"{BACKEND_URL}/api/mt5/rebates", params={
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
})
rebates = response.json()

# Get manager performance
response = requests.get(f"{BACKEND_URL}/api/mt5/analytics/performance")
managers = response.json()
```

---

## Integration with Frontend

### Example: Fetch deals for Trading Analytics

```javascript
// frontend/src/services/mt5Service.js

export const getDeals = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `${process.env.REACT_APP_BACKEND_URL}/api/mt5/deals?${params}`
  );
  return response.json();
};

export const getDealsSummary = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `${process.env.REACT_APP_BACKEND_URL}/api/mt5/deals/summary?${params}`
  );
  return response.json();
};

export const getRebates = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `${process.env.REACT_APP_BACKEND_URL}/api/mt5/rebates?${params}`
  );
  return response.json();
};
```

### Example: Display daily P&L chart

```javascript
import { getDailyPnL } from '../services/mt5Service';

const TradingAnalytics = () => {
  const [dailyData, setDailyData] = useState([]);
  
  useEffect(() => {
    const fetchData = async () => {
      const result = await getDailyPnL({ days: 30 });
      setDailyData(result.data);
    };
    fetchData();
  }, []);
  
  return (
    <LineChart data={dailyData}>
      <XAxis dataKey="date" />
      <YAxis />
      <Line dataKey="pnl" stroke="#8884d8" />
    </LineChart>
  );
};
```

---

## Data Flow

```
MT5 Terminal (VPS)
    ↓
mt5_bridge_service_with_deals.py
    ↓
MongoDB (mt5_deals_history collection)
    ↓
Backend API (mt5_deals_service.py)
    ↓
Frontend (React components)
```

---

## Next Steps

1. **Deploy Enhanced VPS Bridge**: Install `mt5_bridge_service_with_deals.py` on VPS to start collecting deal history
2. **Test Endpoints**: Use curl/Postman to verify all endpoints work
3. **Update Frontend**: Integrate new endpoints into Trading Analytics, Cash Flow, Rebates dashboards
4. **Verify Data**: Confirm deal history is being collected and served correctly

---

**Phase 4A Backend API**: Complete ✅
**Next**: Frontend Integration (Day 3)
