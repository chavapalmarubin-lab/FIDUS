# Broker Rebates System - Complete Documentation

## 📋 Overview

The Broker Rebates System automatically calculates and tracks commission rebates earned from MT5 trading volume. The system integrates with the Cash Flow & Performance dashboard to provide real-time visibility into this revenue stream.

**Current Status**: ✅ Production Ready  
**Current Rebates Tracked**: $291.44 (57.7 lots @ $5.05/lot)

---

## 🔧 API Endpoints

### 1. Calculate Rebates for Period
Automatically calculates rebates based on MT5 trading volume for a specified date range.

**Endpoint**: `POST /api/admin/rebates/calculate`

**Request Body**:
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-13",
  "auto_approve": true
}
```

**Response**:
```json
{
  "success": true,
  "period": "2025-10-01 to 2025-10-13",
  "transactions_created": 1,
  "total_rebates": 291.44,
  "total_volume": 57.7,
  "transactions": [
    {
      "transaction_id": "rebate_xxx",
      "mt5_account": "8885089",
      "broker": "MEX-Atlantic",
      "lots_traded": 57.7,
      "rebate_per_lot": 5.05,
      "total_rebate": 291.44,
      "calculation_date": "2025-10-13",
      "verification_status": "verified"
    }
  ]
}
```

**Usage Example**:
```bash
curl -X POST https://your-backend-url/api/admin/rebates/calculate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-13",
    "auto_approve": true
  }'
```

---

### 2. Get Rebate Summary
Retrieves summary of rebates for a specific month or all-time.

**Endpoint**: `GET /api/admin/rebates/summary`

**Query Parameters**:
- `month` (optional): Month number (1-12)
- `year` (optional): Year (e.g., 2025)

**Response**:
```json
{
  "success": true,
  "summary": {
    "total_rebates": 291.44,
    "total_volume": 57.7,
    "transaction_count": 1,
    "verified_rebates": 291.44,
    "pending_rebates": 0,
    "paid_rebates": 0
  },
  "breakdown_by_broker": {
    "MEX-Atlantic": {
      "total_rebates": 291.44,
      "total_volume": 57.7,
      "transaction_count": 1
    }
  }
}
```

**Usage Example**:
```bash
# Get summary for October 2025
curl -X GET "https://your-backend-url/api/admin/rebates/summary?month=10&year=2025" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get all-time summary
curl -X GET "https://your-backend-url/api/admin/rebates/summary" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 3. Get Rebate Transactions
Retrieves detailed list of all rebate transactions.

**Endpoint**: `GET /api/admin/rebates/transactions`

**Query Parameters**:
- `status` (optional): Filter by verification status (verified, pending, disputed)
- `broker` (optional): Filter by broker name

**Response**:
```json
{
  "success": true,
  "transactions": [
    {
      "transaction_id": "rebate_xxx",
      "mt5_account": "8885089",
      "broker_name": "MEX-Atlantic",
      "fund_code": "BALANCE",
      "lots_traded": 57.7,
      "rebate_per_lot": 5.05,
      "total_rebate": 291.44,
      "calculation_date": "2025-10-13T00:00:00Z",
      "period_start": "2025-10-01T00:00:00Z",
      "period_end": "2025-10-13T23:59:59Z",
      "verification_status": "verified",
      "payment_status": "unpaid",
      "created_at": "2025-10-13T12:00:00Z"
    }
  ]
}
```

**Usage Example**:
```bash
# Get all transactions
curl -X GET "https://your-backend-url/api/admin/rebates/transactions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get verified transactions only
curl -X GET "https://your-backend-url/api/admin/rebates/transactions?status=verified" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 4. Get Broker Configurations
Retrieves rebate configuration for all brokers.

**Endpoint**: `GET /api/admin/rebates/config`

**Response**:
```json
{
  "success": true,
  "brokers": [
    {
      "broker_code": "MEX",
      "broker_name": "MEX-Atlantic",
      "rebate_per_lot": 5.05,
      "currency": "USD",
      "active": true,
      "created_at": "2025-10-13T12:00:00Z"
    }
  ]
}
```

**Usage Example**:
```bash
curl -X GET "https://your-backend-url/api/admin/rebates/config" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 5. Update Broker Configuration
Updates rebate rate for a specific broker.

**Endpoint**: `PUT /api/admin/rebates/config/{broker_code}`

**Request Body**:
```json
{
  "rebate_per_lot": 5.50,
  "active": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Broker configuration updated successfully",
  "config": {
    "broker_code": "MEX",
    "broker_name": "MEX-Atlantic",
    "rebate_per_lot": 5.50,
    "active": true,
    "updated_at": "2025-10-13T12:00:00Z"
  }
}
```

---

### 6. Update Transaction Status
Updates verification or payment status of a rebate transaction.

**Endpoint**: `PUT /api/admin/rebates/transactions/{transaction_id}/status`

**Request Body**:
```json
{
  "verification_status": "verified",
  "payment_status": "paid",
  "notes": "Confirmed payment received from MEX-Atlantic"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Transaction status updated successfully",
  "transaction": {
    "transaction_id": "rebate_xxx",
    "verification_status": "verified",
    "payment_status": "paid",
    "updated_at": "2025-10-13T12:00:00Z"
  }
}
```

---

## 📊 Rebate Calculation Logic

### Formula
```
Rebate Earned = Trading Volume (lots) × Rebate Rate (per lot)
```

### Example Calculation
```
Account: 8885089 (BALANCE Fund)
Broker: MEX-Atlantic
Period: October 1-13, 2025

Trading Volume: 57.7 lots
Rebate Rate: $5.05 per lot
Rebate Earned: 57.7 × $5.05 = $291.44
```

### Volume Calculation
The system queries MT5 trading history for all accounts linked to a broker during the specified period and sums the lot sizes of all closed trades.

### Automatic Approval
When `auto_approve: true` is set, the system automatically:
1. Calculates rebates from MT5 trading data
2. Creates rebate transactions
3. Sets verification_status to "verified"
4. Integrates with Cash Flow calculations

---

## 🏢 Adding New Brokers

### Step 1: Create Broker Configuration

Use the POST endpoint to add a new broker:

```bash
curl -X POST https://your-backend-url/api/admin/rebates/config \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "broker_code": "ICM",
    "broker_name": "IC Markets",
    "rebate_per_lot": 4.50,
    "currency": "USD",
    "active": true
  }'
```

### Step 2: Update MT5 Accounts

Ensure MT5 accounts are properly configured:
1. Go to MT5 Accounts management
2. Assign accounts to the new broker
3. Verify broker_name field matches configuration
4. Ensure accounts are active and trading

### Step 3: Verify Configuration

```bash
# Verify broker was added
curl -X GET "https://your-backend-url/api/admin/rebates/config" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Step 4: Test Calculation

Run a test calculation for the new broker:
```bash
curl -X POST https://your-backend-url/api/admin/rebates/calculate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-13",
    "auto_approve": false
  }'
```

Review the results before approving.

---

## 📅 Monthly Reconciliation Process

### Step 1: Calculate Monthly Rebates
At the end of each month, run the calculation:

```bash
curl -X POST https://your-backend-url/api/admin/rebates/calculate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "auto_approve": false
  }'
```

### Step 2: Compare with Broker Statements
1. Download broker rebate statements
2. Compare total volume and rebate amounts
3. Investigate any discrepancies

### Step 3: Approve Transactions
For each verified transaction:

```bash
curl -X PUT https://your-backend-url/api/admin/rebates/transactions/{transaction_id}/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "verification_status": "verified",
    "notes": "Confirmed with broker statement"
  }'
```

### Step 4: Mark as Paid
When broker pays rebates:

```bash
curl -X PUT https://your-backend-url/api/admin/rebates/transactions/{transaction_id}/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_status": "paid",
    "notes": "Payment received on 2025-11-05"
  }'
```

### Step 5: Generate Reports
Use the summary endpoint to generate monthly reports:

```bash
curl -X GET "https://your-backend-url/api/admin/rebates/summary?month=10&year=2025" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 💾 Database Collections

### 1. broker_rebate_config
Stores broker-specific rebate configurations.

**Schema**:
```javascript
{
  broker_code: "MEX",
  broker_name: "MEX-Atlantic",
  rebate_per_lot: 5.05,
  currency: "USD",
  active: true,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes**:
- `broker_code` (unique)
- `active`

### 2. rebate_transactions
Stores individual rebate transactions.

**Schema**:
```javascript
{
  transaction_id: "rebate_xxx",
  mt5_account: "8885089",
  broker_name: "MEX-Atlantic",
  broker_code: "MEX",
  fund_code: "BALANCE",
  lots_traded: 57.7,
  rebate_per_lot: 5.05,
  total_rebate: 291.44,
  calculation_date: ISODate,
  period_start: ISODate,
  period_end: ISODate,
  verification_status: "verified",
  payment_status: "unpaid",
  notes: "",
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes**:
- `transaction_id` (unique)
- `mt5_account`
- `broker_code`
- `verification_status`
- `calculation_date`

### 3. mt5_accounts (Updated)
Existing collection updated with broker information.

**New Fields**:
```javascript
{
  broker_name: "MEX-Atlantic",
  track_rebates: true
}
```

---

## 🔗 Integration with Cash Flow

### Automatic Integration
The rebate system automatically integrates with the Cash Flow & Performance dashboard through the `/api/admin/cashflow/overview` endpoint.

**Integration Points**:
1. **Fund Assets**: Broker rebates appear as a separate line item
2. **Fund Revenue**: Includes rebates in total revenue calculation
3. **Net Profitability**: Factors rebates into net profit analysis
4. **Fund Accounting Table**: Shows rebates per fund

### Data Flow
```
MT5 Trading Volume
    ↓
RebateCalculator.calculate_rebates()
    ↓
rebate_transactions collection
    ↓
RebateCalculator.get_rebates_for_cash_flow()
    ↓
/api/admin/cashflow/overview
    ↓
Cash Flow & Performance UI
```

---

## 🎯 Future Enhancements

### Phase 2 (Planned)
- **Client Rebate Sharing**: Share rebates with clients based on their trading volume
- **Multi-Currency Support**: Handle rebates in different currencies
- **Automated Broker Reconciliation**: API integration with broker statements
- **Performance Reports**: Detailed analytics on rebate trends
- **Email Notifications**: Alert when rebates are calculated/paid
- **Export Functionality**: Export rebate data to Excel/PDF

### Phase 3 (Future)
- **Rebate Forecasting**: Predict future rebates based on trading patterns
- **Broker Comparison**: Compare rebate rates across brokers
- **Client Portal**: Allow clients to view their rebate share
- **Automated Payments**: Trigger payments when rebates are verified

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue**: Rebates showing $0
- **Cause**: No trading volume in the specified period
- **Solution**: Verify MT5 accounts have closed trades in the date range

**Issue**: Broker not found
- **Cause**: Broker configuration missing
- **Solution**: Add broker using POST /api/admin/rebates/config

**Issue**: Volume mismatch with broker statement
- **Cause**: Different calculation period or closed trades only
- **Solution**: Verify date ranges match and only closed trades are counted

**Issue**: Transaction not appearing in Cash Flow
- **Cause**: Transaction not verified
- **Solution**: Update verification_status to "verified"

### Debug Mode
Enable detailed logging in backend:
```python
logging.info(f"💰 Broker Rebates: ${broker_rebates:,.2f} from {total_volume} lots")
```

---

## 📊 System Status

**Current Configuration**:
- **Active Brokers**: 1 (MEX-Atlantic)
- **Current Rebates**: $291.44
- **Trading Volume**: 57.7 lots
- **Status**: ✅ Production Ready

**Last Updated**: October 13, 2025

---

## 📧 Contact

For questions or issues related to the Broker Rebates System:
- Review this documentation first
- Check backend logs for detailed error messages
- Verify broker configurations and MT5 account settings
- Test API endpoints directly with curl/Postman

---

**System Version**: 1.0  
**Documentation Version**: 1.0  
**Last Updated**: October 13, 2025
