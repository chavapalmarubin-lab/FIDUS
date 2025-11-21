# FIDUS PLATFORM - DATABASE FIELD NAMING STANDARDS

**⚠️ CRITICAL: This file must be in Emergent's environment and committed to GitHub**

**Last Updated:** November 6, 2025 - 11:30 AM PST  
**Version:** 1.1  
**Maintained By:** Chava Palma (Founder & CEO)

---

## 📋 PURPOSE

This document defines the EXACT field names used in:
1. **MongoDB Collections** (database)
2. **API Responses** (JSON)
3. **Frontend Code** (React/JavaScript)

**Rule:** Database uses `snake_case`, API/Frontend uses `camelCase`

**Conversion happens in backend:** Python converts snake_case to camelCase before sending to frontend

---

## 🗄️ COLLECTION 1: investments

### Database Fields (MongoDB - snake_case):

```javascript
{
  _id: ObjectId,                      // MongoDB auto-generated
  client_id: ObjectId,                // Reference to users collection
  client_name: String,                // "Alejandro Mariscal Romero"
  client_email: String,               // "alejandro.mariscal@email.com"
  fund_type: String,                  // "CORE", "BALANCE", "DYNAMIC", "UNLIMITED"
  principal_amount: Number,           // Initial investment amount
  interest_rate: Number,              // Decimal: 0.015 = 1.5%, 0.025 = 2.5%
  payment_frequency: String,          // "monthly", "quarterly", "semi-annual"
  start_date: Date,                   // ISO date: "2025-10-01T00:00:00Z"
  incubation_end_date: Date,          // 60 days after start_date
  first_payment_date: Date,           // When first interest payment is due
  contract_end_date: Date,            // 426 days after start_date
  status: String,                     // "incubation", "active", "completed", "cancelled"
  salesperson_id: String,             // Reference to salespeople collection
  salesperson_name: String,           // "Salvador Palma"
  referral_code: String,              // "SP-2025"
  referral_salesperson_id: String,    // Used for commission tracking (same as salesperson_id)
  mt5_accounts: Array,                // List of MT5 account numbers allocated
  created_at: Date,                   // When investment was created
  updated_at: Date                    // Last modification timestamp
}
```

### API Response (JSON - camelCase):

```javascript
{
  id: "string",                       // Converted from _id
  clientId: "string",
  clientName: "string",
  clientEmail: "string",
  fundType: "string",
  principalAmount: number,
  interestRate: number,
  paymentFrequency: "string",
  startDate: "string",
  incubationEndDate: "string",
  firstPaymentDate: "string",
  contractEndDate: "string",
  status: "string",
  salespersonId: "string",
  salespersonName: "string",
  referralCode: "string",
  referralSalespersonId: "string",    // Used for commission tracking
  mt5Accounts: array,
  createdAt: "string",
  updatedAt: "string"
}
```

### Example Record:

**Database (snake_case):**
```javascript
{
  _id: ObjectId("67890abcdef"),
  client_id: ObjectId("12345abcdef"),
  client_name: "Alejandro Mariscal Romero",
  client_email: "alejandro.mariscal@email.com",
  fund_type: "CORE",
  principal_amount: 18151.41,
  interest_rate: 0.015,
  payment_frequency: "monthly",
  start_date: ISODate("2025-10-01T00:00:00Z"),
  incubation_end_date: ISODate("2025-11-30T00:00:00Z"),
  first_payment_date: ISODate("2025-12-30T00:00:00Z"),
  contract_end_date: ISODate("2026-12-01T00:00:00Z"),
  status: "active",
  salesperson_id: "sp_6909e8eaaaf69606babea151",
  salesperson_name: "Salvador Palma",
  referral_code: "SP-2025",
  mt5_accounts: [885822, 891234],
  created_at: ISODate("2025-10-01T00:00:00Z"),
  updated_at: ISODate("2025-11-06T00:00:00Z")
}
```

**API Response (camelCase):**
```javascript
{
  id: "67890abcdef",
  clientId: "12345abcdef",
  clientName: "Alejandro Mariscal Romero",
  clientEmail: "alejandro.mariscal@email.com",
  fundType: "CORE",
  principalAmount: 18151.41,
  interestRate: 0.015,
  paymentFrequency: "monthly",
  startDate: "2025-10-01T00:00:00.000Z",
  incubationEndDate: "2025-11-30T00:00:00.000Z",
  firstPaymentDate: "2025-12-30T00:00:00.000Z",
  contractEndDate: "2026-12-01T00:00:00.000Z",
  status: "active",
  salespersonId: "sp_6909e8eaaaf69606babea151",
  salespersonName: "Salvador Palma",
  referralCode: "SP-2025",
  mt5Accounts: [885822, 891234],
  createdAt: "2025-10-01T00:00:00.000Z",
  updatedAt: "2025-11-06T00:00:00.000Z"
}
```

---

## 🗄️ COLLECTION 2: mt5_accounts

### Database Fields (MongoDB - snake_case):

```javascript
{
  _id: ObjectId,
  account: Number,                    // MT5 account number (e.g., 885822)
  fund_type: String,                  // "CORE", "BALANCE", "SEPARATION", "INTERMEDIARY"
  manager_name: String,               // "CP Strategy Provider", "UNO14 Manager"
  manager_profile_url: String,        // URL to manager's profile
  execution_method: String,           // "MAM", "Copy Trade"
  capital_source: String,             // "client", "fidus", "reinvested", "separation"
  client_id: ObjectId,                // Reference if capital_source = "client"
  initial_allocation: Number,         // Original amount allocated to this account
  equity: Number,                     // Current account balance
  balance: Number,                    // Account balance (not including open trades)
  profit: Number,                     // Total profit/loss
  margin: Number,                     // Used margin
  free_margin: Number,                // Available margin
  margin_level: Number,               // Margin level percentage
  leverage: Number,                   // Account leverage (e.g., 100 = 1:100)
  currency: String,                   // "USD"
  server: String,                     // "MEXAtlantic-Live", "Lucrumcapital-Live"
  broker: String,                     // "MEXAtlantic", "Lucrum Capital"
  status: String,                     // "active", "inactive"
  last_sync: Date,                    // Last time data was synced from MT5
  created_at: Date,
  updated_at: Date
}
```

### API Response (JSON - camelCase):

```javascript
{
  id: "string",
  account: number,
  fundType: "string",
  managerName: "string",
  managerProfileUrl: "string",
  executionMethod: "string",
  capitalSource: "string",
  clientId: "string",
  initialAllocation: number,
  equity: number,
  balance: number,
  profit: number,
  margin: number,
  freeMargin: number,
  marginLevel: number,
  leverage: number,
  currency: "string",
  server: "string",
  status: "string",
  lastSync: "string",
  createdAt: "string",
  updatedAt: "string"
}
```

### Example Record:

**Database (snake_case):**
```javascript
{
  _id: ObjectId("abc123def456"),
  account: 885822,
  fund_type: "CORE",
  manager_name: "CP Strategy Provider",
  manager_profile_url: "https://ratings.mexatlantic.com/widgets/ratings/3157",
  execution_method: "Copy Trade",
  capital_source: "client",
  client_id: ObjectId("12345abcdef"),
  initial_allocation: 18151.41,
  equity: 2165.55,
  balance: 2165.55,
  profit: -15985.86,
  margin: 0,
  free_margin: 2165.55,
  margin_level: 0,
  leverage: 100,
  currency: "USD",
  server: "MEXAtlantic-Live",
  broker: "MEXAtlantic",
  status: "active",
  last_sync: ISODate("2025-11-06T10:00:00Z"),
  created_at: ISODate("2025-10-01T00:00:00Z"),
  updated_at: ISODate("2025-11-06T10:00:00Z")
}

**Example 2 - Lucrum Capital Account (snake_case):**
```javascript
{
  _id: ObjectId("abc123def457"),
  account: 2198,
  fund_type: "BALANCE",
  manager_name: "JOSE",
  manager_profile_url: null,
  execution_method: "Copy Trade",
  capital_source: "client",
  initial_allocation: 10000.00,
  equity: 10000.00,
  balance: 10000.00,
  profit: 0.00,
  margin: 0,
  free_margin: 10000.00,
  margin_level: 0,
  leverage: 100,
  currency: "USD",
  server: "Lucrumcapital-Live",
  broker: "Lucrum Capital",
  phase: "Phase 2",
  status: "active",
  sync_enabled: true,
  last_sync: ISODate("2025-11-21T18:00:00Z"),
  created_at: ISODate("2025-11-21T18:00:00Z"),
  updated_at: ISODate("2025-11-21T18:44:00Z")
}
```

---

## 🗄️ COLLECTION 3: salespeople

### Database Fields (MongoDB - snake_case):

```javascript
{
  _id: ObjectId,
  salesperson_id: String,             // Unique ID: "sp_6909e8eaaaf69606babea151"
  name: String,                       // "Salvador Palma"
  code: String,                       // "SP-2025"
  email: String,
  phone: String,
  referral_link: String,              // Unique referral URL
  commission_rate: Number,            // 0.10 = 10%
  total_sales: Number,                // Sum of all client investments referred
  total_commissions: Number,          // Total earned commissions
  pending_commissions: Number,        // Unpaid commissions
  paid_commissions: Number,           // Already paid commissions
  active_clients: Number,             // Count of active clients
  status: String,                     // "active", "inactive"
  joined_date: Date,
  created_at: Date,
  updated_at: Date
}
```

### API Response (JSON - camelCase):

```javascript
{
  id: "string",
  salespersonId: "string",
  name: "string",
  code: "string",
  email: "string",
  phone: "string",
  referralLink: "string",
  commissionRate: number,
  totalSales: number,
  totalCommissions: number,
  pendingCommissions: number,
  paidCommissions: number,
  activeClients: number,
  status: "string",
  joinedDate: "string",
  createdAt: "string",
  updatedAt: "string"
}
```

---

## 🗄️ COLLECTION 4: referral_commissions

### Database Fields (MongoDB - snake_case):

```javascript
{
  _id: ObjectId,
  salesperson_id: String,             // "sp_6909e8eaaaf69606babea151"
  salesperson_name: String,           // "Salvador Palma"
  client_id: ObjectId,
  client_name: String,
  investment_id: ObjectId,
  fund_type: String,                  // "CORE", "BALANCE"
  payment_date: Date,                 // When commission is due
  client_payment_amount: Number,      // Client's interest payment
  commission_amount: Number,          // 10% of client payment
  commission_type: String,            // "monthly", "quarterly"
  payment_number: Number,             // Which payment in sequence (1-16)
  status: String,                     // "pending", "approved", "paid"
  approved_by: String,
  approved_date: Date,
  paid_date: Date,
  created_at: Date,
  updated_at: Date
}
```

### API Response (JSON - camelCase):

```javascript
{
  id: "string",
  salespersonId: "string",
  salespersonName: "string",
  clientId: "string",
  clientName: "string",
  investmentId: "string",
  fundType: "string",
  paymentDate: "string",
  clientPaymentAmount: number,
  commissionAmount: number,
  commissionType: "string",
  paymentNumber: number,
  status: "string",
  approvedBy: "string",
  approvedDate: "string",
  paidDate: "string",
  createdAt: "string",
  updatedAt: "string"
}
```

---

## 🗄️ COLLECTION 5: money_managers

### Database Fields (MongoDB - snake_case):

```javascript
{
  _id: ObjectId,
  manager_id: String,                 // Unique ID
  name: String,                       // "UNO14 Manager", "CP Strategy Provider"
  strategy_name: String,              // "UNO14 MAM Strategy", "CP Strategy"
  execution_method: String,           // "MAM", "Copy Trade"
  profile_url: String,                // Link to performance profile
  broker: String,                     // "MultibankFX", "MEXAtlantic"
  accounts_assigned: Array,           // List of MT5 account numbers
  total_allocation: Number,           // Total $ allocated to this manager
  current_equity: Number,             // Current value across all accounts
  total_pnl: Number,                  // Total profit/loss
  return_percentage: Number,          // Overall return %
  sharpe_ratio: Number,
  max_drawdown: Number,
  win_rate: Number,
  profit_factor: Number,
  risk_level: String,                 // "Conservative", "Moderate", "Aggressive"
  status: String,                     // "active", "inactive"
  start_date: Date,
  last_updated: Date,
  created_at: Date,
  updated_at: Date
}
```

### API Response (JSON - camelCase):

```javascript
{
  id: "string",
  managerId: "string",
  name: "string",
  strategyName: "string",
  executionMethod: "string",
  profileUrl: "string",
  broker: "string",
  accountsAssigned: array,
  totalAllocation: number,
  currentEquity: number,
  totalPnl: number,
  returnPercentage: number,
  sharpeRatio: number,
  maxDrawdown: number,
  winRate: number,
  profitFactor: number,
  riskLevel: "string",
  status: "string",
  startDate: "string",
  lastUpdated: "string",
  createdAt: "string",
  updatedAt: "string"
}
```

---

## 🔄 FIELD NAME CONVERSION RULES

### Python Backend Conversion Function:

```python
def snake_to_camel(snake_str):
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake(camel_str):
    """Convert camelCase to snake_case"""
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

def convert_dict_keys(data, to_camel=True):
    """Recursively convert dictionary keys"""
    if isinstance(data, dict):
        converter = snake_to_camel if to_camel else camel_to_snake
        return {converter(k): convert_dict_keys(v, to_camel) 
                for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dict_keys(item, to_camel) for item in data]
    else:
        return data
```

### Usage in API Endpoints:

```python
# When fetching from MongoDB (snake_case) and returning to frontend
@app.route('/api/investments/<investment_id>')
def get_investment(investment_id):
    # Get from MongoDB (snake_case)
    investment = db.investments.find_one({'_id': ObjectId(investment_id)})
    
    # Convert _id to id
    if investment:
        investment['id'] = str(investment.pop('_id'))
    
    # Convert snake_case to camelCase
    investment_camel = convert_dict_keys(investment, to_camel=True)
    
    return jsonify(investment_camel)

# When receiving from frontend (camelCase) and saving to MongoDB
@app.route('/api/investments', methods=['POST'])
def create_investment():
    # Get data from frontend (camelCase)
    data = request.get_json()
    
    # Convert camelCase to snake_case for MongoDB
    data_snake = convert_dict_keys(data, to_camel=False)
    
    # Save to MongoDB (snake_case)
    result = db.investments.insert_one(data_snake)
    
    return jsonify({'id': str(result.inserted_id)})
```

---

## ❌ COMMON MISTAKES TO AVOID

### Mistake 1: Mixing Case Styles

**Wrong:**
```javascript
// MongoDB query mixing cases
db.investments.find({ fundType: "CORE" })  // ❌ fundType is camelCase
```

**Correct:**
```javascript
// MongoDB uses snake_case
db.investments.find({ fund_type: "CORE" })  // ✅
```

### Mistake 2: Not Converting Before API Response

**Wrong:**
```python
# Returning MongoDB document directly to frontend
investment = db.investments.find_one({'_id': id})
return jsonify(investment)  # ❌ Frontend gets snake_case
```

**Correct:**
```python
# Convert to camelCase first
investment = db.investments.find_one({'_id': id})
investment['id'] = str(investment.pop('_id'))
investment_camel = convert_dict_keys(investment, to_camel=True)
return jsonify(investment_camel)  # ✅ Frontend gets camelCase
```

### Mistake 3: Using Wrong Field Names in Queries

**Wrong:**
```python
# Looking for camelCase in MongoDB
accounts = db.mt5_accounts.find({ 'fundType': 'CORE' })  # ❌
```

**Correct:**
```python
# Use snake_case in MongoDB queries
accounts = db.mt5_accounts.find({ 'fund_type': 'CORE' })  # ✅
```

---

## ✅ TESTING CHECKLIST

Before deploying any code that touches database fields:

- [ ] All MongoDB queries use snake_case field names
- [ ] All API responses convert to camelCase
- [ ] All API requests convert from camelCase to snake_case
- [ ] Frontend code expects camelCase
- [ ] No hardcoded field names without conversion
- [ ] Test with actual data to verify field names match

---

## 📝 MAINTENANCE

When adding new fields:

1. Add to this document in both sections (snake_case and camelCase)
2. Update conversion functions if needed
3. Update TypeScript interfaces in frontend
4. Test thoroughly before deploying

**Last Updated:** November 6, 2025  
**Next Review:** When adding new collections or fields

---

**END OF DATABASE_FIELD_STANDARDS.MD**

**This file must be in Emergent's environment and committed to GitHub.**
