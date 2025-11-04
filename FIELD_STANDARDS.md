# FIDUS Platform Field Standards

**Last Updated:** November 4, 2025
**Purpose:** Define consistent field naming conventions across the entire platform

---

## 🎯 Core Principle

**Database (MongoDB):** Uses `snake_case` 
**API/Frontend:** Uses `camelCase`

**RULE:** All API responses MUST transform snake_case → camelCase at the API boundary.

---

## 📊 MT5 Accounts Collection

### MongoDB Fields (snake_case):
```python
{
    "account": int,              # MT5 account number
    "balance": float,            # Current balance
    "equity": float,             # Current equity
    "profit": float,             # Current open profit/loss
    "true_pnl": float,           # True P&L (balance - deposits + withdrawals)
    "displayed_pnl": float,      # Displayed P&L
    "fund_type": str,            # CORE, BALANCE, DYNAMIC, etc.
    "fund_code": str,            # Fund identifier
    "initial_allocation": float, # Initial investment amount
    "client_name": str,          # Client name
    "client_id": str,            # Client ID
    "manager": str,              # Money manager name (if applicable)
}
```

### API/Frontend Fields (camelCase):
```javascript
{
    "accountNumber": number,
    "balance": number,
    "equity": number,
    "profit": number,
    "truePnl": number,
    "displayedPnl": number,
    "fundType": string,
    "fundCode": string,
    "initialAllocation": number,
    "clientName": string,
    "clientId": string,
    "manager": string,
}
```

---

## 💰 Investments Collection

### MongoDB Fields (snake_case):
```python
{
    "investment_id": str,
    "client_id": str,
    "principal_amount": float,     # USE THIS for investment amount
    "current_value": float,
    "fund_code": str,
    "status": str,
    "deposit_date": datetime,
    "interest_start_date": datetime,
    "referred_by": str,           # Salesperson ID
    "referred_by_name": str,      # Salesperson name
}
```

### API/Frontend Fields (camelCase):
```javascript
{
    "investmentId": string,
    "clientId": string,
    "principalAmount": number,    // USE THIS for investment amount
    "currentValue": number,
    "fundCode": string,
    "status": string,
    "depositDate": string,
    "interestStartDate": string,
    "referredBy": string,
    "referredByName": string,
}
```

---

## 👔 Money Managers Collection

### MongoDB Fields (snake_case):
```python
{
    "manager_id": str,
    "name": str,
    "display_name": str,
    "status": str,                      # "active" or "inactive"
    "assigned_accounts": list[int],
    "execution_type": str,
    "strategy_name": str,
    "performance_fee_rate": float,
    "current_month_profit": float,
    "current_month_fee_accrued": float,
}
```

### API/Frontend Fields (camelCase):
```javascript
{
    "managerId": string,
    "name": string,
    "displayName": string,
    "status": string,                   // "active" or "inactive"
    "assignedAccounts": number[],
    "executionType": string,
    "strategyName": string,
    "performanceFeeRate": number,
    "currentMonthProfit": number,
    "currentMonthFeeAccrued": number,
}
```

---

## 🤝 Salespeople Collection

### MongoDB Fields (snake_case):
```python
{
    "referral_code": str,
    "name": str,
    "email": str,
    "phone": str,
    "active": bool,
    "total_sales_volume": Decimal128,    # USE THIS for total sales
    "total_clients_referred": int,
    "total_commissions_earned": Decimal128,
    "commissions_paid_to_date": Decimal128,
    "commissions_pending": Decimal128,
}
```

### API/Frontend Fields (camelCase):
```javascript
{
    "referralCode": string,
    "name": string,
    "email": string,
    "phone": string,
    "active": boolean,
    "totalSalesVolume": number,         // USE THIS for total sales
    "totalClientsReferred": number,
    "totalCommissionsEarned": number,
    "commissionsPaidToDate": number,
    "commissionsPending": number,
}
```

---

## 🚫 FORBIDDEN FIELD NAME VARIANTS

### ❌ DO NOT USE:
- `amount` (use `principal_amount` for investments)
- `account_balance` (use `balance`)
- `account_equity` (use `equity`)
- `profit_loss` (use `profit` or `true_pnl`)
- `sales` (use `total_sales_volume`)
- `allocated` (use `initial_allocation`)

---

## ✅ TRANSFORMATION RULES

### Backend API Response Transformation:
1. Convert all `_id` → `id` (string)
2. Convert all Decimal128 → float
3. Convert all datetime → ISO string
4. Convert all snake_case → camelCase
5. Remove MongoDB-specific fields (_id after conversion)

### Example:
```python
# MongoDB document
{
    "_id": ObjectId("..."),
    "total_sales_volume": Decimal128("118151.41"),
    "created_at": datetime(2025, 10, 1)
}

# Transformed API response
{
    "id": "...",
    "totalSalesVolume": 118151.41,
    "createdAt": "2025-10-01T00:00:00Z"
}
```

---

## 📝 USAGE GUIDELINES

### For Backend Developers:
1. Always query MongoDB using snake_case field names
2. Always transform responses before returning from API
3. Use transformation functions from `/app/backend/utils/field_transformers.py`

### For Frontend Developers:
1. Always expect camelCase fields from API
2. Never transform field names in components
3. If API returns snake_case, it's a backend bug - fix the API

---

## 🔄 MIGRATION CHECKLIST

When adding new fields:
- [ ] Add to MongoDB with snake_case
- [ ] Add to this document
- [ ] Add to transformation function
- [ ] Test API response uses camelCase
- [ ] Update TypeScript types (if applicable)
- [ ] Document in API spec

---

**Remember:** Consistency is key. One source of truth. No exceptions.
