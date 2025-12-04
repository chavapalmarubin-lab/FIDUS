# Quick Deployment Guide - Exact Changes Needed

## 🎯 What to Change in Your Production Code

### Change 1: backend/server.py (Line ~16282)

**Find this:**
```python
CLIENT_MONEY = 118151.41  # Total client investment (from investments collection)
```

**Replace with:**
```python
# Calculate CLIENT_MONEY from investments collection (SSOT)
active_investments = await db.investments.find({'status': 'active'}).to_list(length=None)
CLIENT_MONEY = sum(float(inv.get('principal_amount', 0)) for inv in active_investments)
```

---

### Change 2: backend/server.py (Line ~16629)

**Find this:**
```python
client_money = 118151.41  # Total client investment (from investments collection)
```

**Replace with:**
```python
# Get active investments to calculate total client money
active_investments_for_revenue = await db.investments.find({'status': 'active'}).to_list(length=None)
client_money = sum(float(inv.get('principal_amount', 0)) for inv in active_investments_for_revenue)
```

---

### Change 3: backend/routes/single_source_api.py

The entire `@router.get("/derived/fund-portfolio")` function needs to be replaced.

**This is a larger change - would you like me to provide the complete new function?**

The key change is adding this at the beginning of the function:
```python
# SSOT: Get client obligations from investments collection
active_investments = await db.investments.find({"status": "active"}).to_list(length=None)

# Calculate total allocation per fund from investments (SSOT)
client_obligations_by_fund = {}
total_client_obligations = 0

for inv in active_investments:
    principal_raw = inv.get('principal_amount', 0)
    # Handle Decimal128 objects
    if hasattr(principal_raw, 'to_decimal'):
        principal = float(principal_raw.to_decimal())
    else:
        principal = float(principal_raw)
    
    fund_type = inv.get('fund_type', 'UNKNOWN')
    
    if fund_type not in client_obligations_by_fund:
        client_obligations_by_fund[fund_type] = 0
    client_obligations_by_fund[fund_type] += principal
    total_client_obligations += principal
```

---

## ⚡ Quick Fix for Production

If you want the FASTEST fix, just apply Changes 1 and 2 above to your server.py file. These two changes alone will fix the Cash Flow tab to show $134,145.41.

The other changes (Change 3, frontend changes) are improvements but not critical for the immediate issue.

---

## 🔧 Alternative: Git Patch

Would you like me to create a `.patch` file that you can apply with `git apply`? This would be the cleanest way to transfer the changes.

---

Let me know which format works best for you!
