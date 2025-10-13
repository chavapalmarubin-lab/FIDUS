# Broker Rebates - Quick Reference Guide

## 🚀 Quick Start (5 Minutes)

### 1. Calculate This Month's Rebates
```bash
curl -X POST https://your-backend-url/api/admin/rebates/calculate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "auto_approve": true
  }'
```

### 2. View Summary
```bash
curl -X GET "https://your-backend-url/api/admin/rebates/summary?month=10&year=2025" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Check Cash Flow Dashboard
Navigate to: **Investment Committee → Cash Flow & Performance**

Look for: **Broker Rebates** line item in Fund Assets section

---

## 📊 Quick Formula

```
Rebate = Trading Volume (lots) × Rebate Rate (per lot)

Example:
57.7 lots × $5.05/lot = $291.44
```

---

## 🏢 Add New Broker (2 Minutes)

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

---

## 📅 Monthly Process (3 Steps)

### Step 1: Calculate
```bash
POST /api/admin/rebates/calculate
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "auto_approve": false
}
```

### Step 2: Verify
Compare with broker statement, then approve:
```bash
PUT /api/admin/rebates/transactions/{id}/status
{
  "verification_status": "verified"
}
```

### Step 3: Mark Paid
When payment received:
```bash
PUT /api/admin/rebates/transactions/{id}/status
{
  "payment_status": "paid"
}
```

---

## 🔧 6 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/admin/rebates/calculate` | POST | Calculate rebates for period |
| `/api/admin/rebates/summary` | GET | Get rebate summary |
| `/api/admin/rebates/transactions` | GET | List all transactions |
| `/api/admin/rebates/config` | GET | Get broker configs |
| `/api/admin/rebates/config/{code}` | PUT | Update broker config |
| `/api/admin/rebates/transactions/{id}/status` | PUT | Update transaction status |

---

## 💾 3 Database Collections

1. **broker_rebate_config**: Broker rates
2. **rebate_transactions**: Transaction history
3. **mt5_accounts**: Trading volume source

---

## 📊 Current Status

- ✅ Active Brokers: 1 (MEX-Atlantic @ $5.05/lot)
- ✅ Current Rebates: $291.44
- ✅ Trading Volume: 57.7 lots
- ✅ Status: Production Ready

---

## 🎯 Key Features

✅ Automated calculation from MT5 volume  
✅ Multi-broker support  
✅ Real-time Cash Flow integration  
✅ Transaction history & audit trail  
✅ Status tracking (verified, paid)  
✅ Monthly reconciliation workflow  

---

## 🔍 Troubleshooting

**Rebates = $0?**
→ Check MT5 has trades in date range

**Broker not found?**
→ Add via POST /api/admin/rebates/config

**Not in Cash Flow?**
→ Verify transaction status = "verified"

---

## 📞 Need Help?

1. Check main documentation: `BROKER_REBATES_DOCUMENTATION.md`
2. Review backend logs for errors
3. Test API endpoints directly
4. Verify broker & MT5 account configs

---

**Version**: 1.0  
**Last Updated**: October 13, 2025
