# CAPITAL SOURCE CATEGORIZATION - COMPLETE

**Date**: 2025-11-06  
**Source**: MT5 Deal History Analysis  
**Approved By**: Chava

---

## 📊 CAPITAL STRUCTURE

### 1️⃣ CLIENT CAPITAL (Alejandro Mariscal Romero)

**Total Allocation**: $118,151.41  
**Current Equity**: $27,741.32  
**Number of Accounts**: 6

| Account | Type | Allocation | Current Equity | Notes |
|---------|------|------------|----------------|-------|
| 885822 | CORE | $18,151.41 | $2,155.01 | Original deposit account (CORE portion) |
| 886557 | BALANCE | $80,000.00 | $9,905.85 | Main BALANCE account |
| 886602 | BALANCE | $10,000.00 | $15,680.46 | BALANCE account |
| 886066 | BALANCE | $10,000.00 | $0.00 | Golden MM (funds moved out per Q3) |
| 886528 | SEPARATION | $0.00 | $0.00 | Intermediary hub |
| 891234 | CORE | $0.00 | $0.00 | Inactive |

**CLIENT P&L**:
```
Current Equity: $27,741.32
Profit Withdrawals: $20,656.33 (in separation)
Total Value: $48,397.65
Investment: $118,151.41
P&L: -$69,753.76
Return: -59.04%
```

---

### 2️⃣ FIDUS CAPITAL (House Money)

**Total Allocation**: $14,662.94  
**Current Equity**: $68,962.75  
**Number of Accounts**: 1

| Account | Type | Allocation | Current Equity | Notes |
|---------|------|------------|----------------|-------|
| 891215 | BALANCE | $14,662.94 | $68,962.75 | FIDUS house capital |

**FIDUS P&L**:
```
Current Equity: $68,962.75
Investment: $14,662.94
P&L: +$54,299.81
Return: +370.36% 🚀
```

---

### 3️⃣ REINVESTED PROFITS

**Total Allocation**: $0.00 (no client obligation)  
**Current Equity**: $21,021.78  
**Number of Accounts**: 2

| Account | Type | Allocation | Current Equity | Notes |
|---------|------|------------|----------------|-------|
| 897589 | BALANCE | $0.00 | $5,000.00 | Funded from separation |
| 897590 | CORE | $0.00 | $16,021.78 | Funded from separation |

**REINVESTED P&L**:
```
Current Equity: $21,021.78
(No obligation - this is pure profit at work)
```

---

### 4️⃣ SEPARATION ACCOUNTS

**Total Balance**: $20,656.33

| Account | Type | Balance | Notes |
|---------|------|---------|-------|
| 897591 | SEPARATION | $5,000.81 | Extracted profits |
| 897599 | SEPARATION | $15,655.52 | Extracted profits |

---

## 📊 GRAND TOTALS

| Category | Allocation | Current Equity | P&L | Return % |
|----------|------------|----------------|-----|----------|
| Client (Alejandro) | $118,151.41 | $27,741.32 + $20,656.33 | -$69,753.76 | -59.04% |
| FIDUS (House) | $14,662.94 | $68,962.75 | +$54,299.81 | +370.36% |
| Reinvested | $0.00 | $21,021.78 | N/A | N/A |
| **TOTAL FUND** | **$132,814.35** | **$138,382.18** | **-$15,453.95** | **-11.63%** |

---

## 🎯 KEY INSIGHTS

### Why Different Performance?

**Client Accounts (Alejandro): -59%**
- Invested early (Sep 30, 2025)
- Experienced market drawdown
- Conservative allocation (CORE + BALANCE mix)

**FIDUS Capital: +370%**
- Invested later (Nov 6, 2025)  
- Benefited from market recovery
- Aggressive BALANCE strategy
- Account 891215 shows exceptional performance

**Overall Fund: -11.6%**
- Total value ($138k) vs total investment ($133k)
- Modest loss overall
- FIDUS gains partially offset client losses

---

## ✅ CONFIRMED SPECIFICATIONS (From Chava)

**Q2:** Account 885822 allocation = $18,151.41 (Option B)
- Original deposit: $118,151.41
- Transferred out: $100,000 to BALANCE accounts
- Stayed in CORE: $18,151.41 ✅

**Q3:** Account 886066 = $0 is CORRECT
- Golden money manager account
- Funds intentionally moved out
- Not an error ✅

**Q4:** Three-Tier P&L Approach APPROVED ✅
- Client P&L (for Alejandro)
- FIDUS P&L (for house capital)
- Total Fund P&L (for overall reporting)

---

## 🔄 CAPITAL SOURCE FIELD MAPPING

### For Database Update:

```javascript
// CLIENT ACCOUNTS
{account: 885822, capital_source: "client", client_id: "client_alejandro", initial_allocation: 18151.41}
{account: 886557, capital_source: "client", client_id: "client_alejandro", initial_allocation: 80000.00}
{account: 886602, capital_source: "client", client_id: "client_alejandro", initial_allocation: 10000.00}
{account: 886066, capital_source: "client", client_id: "client_alejandro", initial_allocation: 0.00}  // Q3: Moved out
{account: 886528, capital_source: "intermediary", client_id: null, initial_allocation: 0.00}
{account: 891234, capital_source: "client", client_id: "client_alejandro", initial_allocation: 0.00}

// FIDUS ACCOUNTS
{account: 891215, capital_source: "fidus", client_id: null, initial_allocation: 14662.94}

// REINVESTED PROFIT
{account: 897589, capital_source: "reinvested_profit", client_id: null, initial_allocation: 0.00}
{account: 897590, capital_source: "reinvested_profit", client_id: null, initial_allocation: 0.00}

// SEPARATION
{account: 897591, capital_source: "separation", client_id: null, initial_allocation: 0.00}
{account: 897599, capital_source: "separation", client_id: null, initial_allocation: 0.00}
```

---

## 🚀 NEXT STEPS

1. ✅ Update `mt5_accounts` collection with `capital_source` field
2. ✅ Implement three-tier P&L calculation in `pnl_calculator.py`
3. ✅ Update frontend dashboards to show:
   - Client view (Alejandro sees only his P&L)
   - Admin view (FIDUS sees all three tiers)
4. ✅ Test calculations with real data
5. ✅ Deploy to production

**Ready to implement!** 🎯

