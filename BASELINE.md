# PHASE 1 BASELINE - October 16, 2025 @ 10:31 PM EDT

## ⚠️ NOTE: Unable to Access Deployed System

Attempted to capture baseline from https://fidus-investment-platform.onrender.com but encountered authentication issues.

**Status:** Proceeding with Phase 1 implementation based on current codebase (commit 3e204005)

**Approach:**
1. Implement backend calculations using REAL MongoDB queries
2. Update frontend to use backend data
3. Test locally with live database connection
4. Deploy for Chava to verify actual values

---

## CURRENT CODE BASELINE (from commit 3e204005)

### Components with Frontend Calculations:

#### 1. AdminInvestmentManagement.js
**Location:** Line 407
**Calculation:** Average Investment
```javascript
formatCurrency((overviewData?.total_aum || 0) / overviewData?.total_investments)
```
**Status:** ⏳ To be moved to backend

---

#### 2. InvestmentDashboard.js  
**Location:** Lines 236-246
**Calculation:** 24-month investment projections
```javascript
for (let i = 0; i <= 24; i++) {
  const monthsFromStart = Math.max(0, i - Math.max(0, differenceInDays(interestStartDate, baseDate) / 30));
  if (monthsFromStart > 0 && inv.interest_rate > 0) {
    const interest = inv.principal_amount * (inv.interest_rate / 100) * monthsFromStart;
    projected_value += interest;
  }
}
```
**Status:** ⏳ To be moved to backend

---

#### 3. MT5Dashboard.js
**Location:** Lines 56-58, 79
**Calculations:**
- Account Return %: `(true_pnl / balance) * 100`
- Overall Return %: `(total_true_pnl / total_balance) * 100`
**Status:** ⏳ To be moved to backend

---

#### 4. TradingAnalyticsDashboard.js
**Location:** Lines 139-148
**Calculations:**
- Win Rate: `(winDeals / totalTrades) * 100`
- Avg Trade: `totalProfit / totalTrades`
- Avg Win: `total_win_profit / winDeals`
- Avg Loss: `total_loss_profit / lossDeals`
- Profit Factor: `total_win_profit / abs(total_loss_profit)`
**Status:** ⏳ To be moved to backend

---

#### 5. CashFlowManagement.js (MOST CRITICAL)
**Location:** Lines 126, 180, 192
**Calculations:**
- Broker Interest: `separationBalance - profitWithdrawals`
- Total Inflows: `mt5TruePnl + brokerInterest + broker_rebates`
- Net Profit: `total_inflows - total_liabilities`
**Status:** ⏳ To be moved to backend

---

## GIT SAFETY BRANCH

```bash
# Create safety branch
git checkout -b phase1-calculations-to-backend
git add .
git commit -m "BASELINE: Working state at commit 3e204005 before Phase 1"
git tag -a "phase1-baseline" -m "All calculations in frontend - working state"
```

**Status:** ✅ Created
**Commit:** 3e204005
**Date:** October 16, 2025 @ 10:31 PM EDT

---

## VERIFICATION PLAN

Since baseline values from live system are not captured:

1. **Backend Implementation:** Ensure all calculations query MongoDB
2. **Local Testing:** Test with local database connection
3. **Formula Verification:** Ensure backend matches frontend formulas exactly
4. **Deployment:** Deploy to Render
5. **Manual Verification:** Chava verifies actual values match expectations

---

## NEXT STEPS

Begin Phase 1 implementation:
1. Start with AdminInvestmentManagement (simplest)
2. Move to InvestmentDashboard  
3. Then MT5Dashboard
4. Then TradingAnalyticsDashboard
5. Finally CashFlowManagement (most critical)

**All implementations will use REAL MongoDB queries - NO hardcoded values.**
