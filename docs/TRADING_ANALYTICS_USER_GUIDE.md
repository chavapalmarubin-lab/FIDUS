# Trading Analytics - User Guide

## 📊 Overview

Trading Analytics provides comprehensive manager-level performance analysis for the FIDUS Investment Platform. This system helps you make data-driven capital allocation decisions by analyzing risk-adjusted returns, manager performance, and fund metrics.

---

## 🎯 Key Features

### 1. **Portfolio View** - Overall Performance
View aggregate performance across all your funds and managers.

### 2. **Funds View** - Fund-Specific Analysis
Analyze individual fund performance (BALANCE vs CORE).

### 3. **Managers View** - Manager Rankings ⭐ PRIMARY
Compare manager performance with risk-adjusted metrics for allocation decisions.

### 4. **Accounts View** - Detailed Account Data
Deep-dive into individual account trading activity.

---

## 🚀 Getting Started

### Accessing Trading Analytics

1. Log in to the FIDUS Admin Portal
2. Navigate to **Trading Analytics** in the main menu
3. The Managers View opens by default (most important view)

### Selecting Time Period

Use the period selector dropdown to analyze different timeframes:
- **Last 7 Days** - Recent performance
- **Last 30 Days** - Default, balanced view
- **Last 90 Days** - Quarterly performance
- **Last 6 Months** - Mid-term trends
- **Last Year** - Annual performance

---

## 📈 Portfolio View

**Purpose:** High-level overview of your entire investment portfolio.

### What You'll See:

**Key Metrics Cards:**
- **Total AUM** - Assets Under Management across all funds
- **Total P&L** - Combined profit/loss with blended return percentage
- **Active Managers** - Number of managers currently trading
- **Current Equity** - Real-time portfolio value

**Fund Breakdown:**
- BALANCE Fund performance
- CORE Fund performance
- Asset allocation percentages
- Fund-level metrics

### How to Use:

1. Review total portfolio performance at a glance
2. Compare BALANCE vs CORE fund contributions
3. Check asset allocation balance
4. Identify which fund is driving returns
5. Use for reporting and high-level decision making

---

## 💼 Funds View

**Purpose:** Detailed analysis of individual fund performance.

### Fund Selector:

Click **BALANCE Fund** or **CORE Fund** buttons to switch between funds.

### Fund Summary Metrics:

- **AUM** - Fund's total assets
- **Current Equity** - Real-time value
- **Total P&L** - Fund profit/loss
- **Weighted Return** - Return percentage
- **Managers Count** - Active managers in fund

### Performance Attribution:

- **Best Performer** - Top manager in the fund
- **Needs Attention** - Underperforming manager

### Managers in Fund:

Displays all managers assigned to the selected fund with:
- Manager name and strategy
- Account number
- Allocation and current equity
- P&L and return percentage
- Contribution to fund performance
- Sharpe ratio
- Risk level

### How to Use:

1. Select fund to analyze (BALANCE or CORE)
2. Review fund-level metrics
3. Identify which managers are contributing most
4. Check if fund is meeting performance targets
5. Compare manager performance within the fund
6. Make rebalancing decisions

---

## 👥 Managers View ⭐ PRIMARY VIEW

**Purpose:** Compare all managers to make capital allocation decisions.

This is the **most important view** for fund management!

### Top Performer Banner

Highlights your #1 performing manager with:
- Manager name
- Return percentage
- Total P&L
- Sharpe ratio

### Manager Rankings Table

**Columns Explained:**

| Column | What It Means | Good Value |
|--------|---------------|------------|
| **Rank** | Performance ranking (🥇🥈🥉 for top 3) | Higher is better |
| **Manager** | Manager/strategy name | - |
| **Strategy** | Trading approach | - |
| **Fund** | BALANCE or CORE | - |
| **Account** | MT5 account number | - |
| **P&L** | Total profit/loss | Positive (green) |
| **Return %** | Percentage return | >5% is good |
| **Sharpe** | Risk-adjusted return | >1.0 good, >2.0 excellent |
| **Sortino** | Downside risk-adjusted return | >1.0 good |
| **Max DD** | Maximum drawdown % | <20% is good |
| **Win Rate** | % of winning trades | >50% is good |
| **Profit Factor** | Wins / Losses ratio | >1.5 is good |
| **Risk** | Risk level | Low/Medium preferred |
| **Status** | Performance assessment | Green badges are best |

### Sorting Options

Use the "Sort by" dropdown to rank managers by:
- **Return %** (default) - Best overall returns
- **Sharpe Ratio** - Best risk-adjusted returns
- **Sortino Ratio** - Best downside-protected returns
- **Profit Factor** - Best win/loss ratio
- **Total P&L** - Highest dollar profits

### Capital Allocation Recommendations 💰

The system automatically suggests:

**"Increase Allocation" (Green):**
- Managers with excellent risk-adjusted returns
- High Sharpe ratios (>1.5)
- Consistent performance
- **Action:** Consider allocating more capital

**"Decrease Allocation" (Red):**
- Managers with poor metrics
- Low Sharpe ratios (<0.5)
- High drawdowns
- Low profit factors
- **Action:** Consider reducing or removing allocation

### Risk Alerts ⚠️

Automatic warnings for:
- **Low Win Rate** (<30%) - Monitor closely
- **High Drawdown** (>20%) - Risk assessment needed
- **Low Profit Factor** (<1.0) - Not profitable
- **Other concerns** - Review performance

### How to Use:

1. **Review the rankings table** - See who's performing best
2. **Sort by Sharpe Ratio** - Find best risk-adjusted returns
3. **Read capital allocation suggestions** - System recommendations
4. **Check risk alerts** - Identify problem areas
5. **Make decisions:**
   - Allocate more to top performers (high Sharpe)
   - Reduce allocation to underperformers
   - Monitor managers with warnings
6. **Re-check regularly** - Weekly or monthly

---

## 📊 Understanding Key Metrics

### Risk-Adjusted Returns

**Sharpe Ratio:**
- Measures return per unit of risk
- Formula: `(Return - Risk-Free Rate) / Standard Deviation`
- **Interpretation:**
  - < 0.5: Poor
  - 0.5 - 1.0: Fair
  - 1.0 - 2.0: Good
  - \> 2.0: Excellent
- **Use:** Primary metric for comparing managers

**Sortino Ratio:**
- Like Sharpe but only considers downside risk
- Focuses on negative returns only
- **Higher is better** - Shows downside protection
- **Use:** Identify managers who protect capital in losses

**Calmar Ratio:**
- Return divided by maximum drawdown
- Formula: `Annualized Return / Max Drawdown`
- **Higher is better**
- **Use:** Evaluate return vs worst-case scenario

### Risk Metrics

**Maximum Drawdown:**
- Largest peak-to-trough decline
- Percentage from highest point to lowest
- **Lower is better** - Shows worst losses
- **Warning:** >20% indicates high risk
- **Use:** Assess downside risk potential

**Win Rate:**
- Percentage of profitable trades
- Formula: `Winning Trades / Total Trades × 100`
- **Good:** >50%
- **Caution:** <40% needs investigation
- **Use:** Gauge consistency, but consider with profit factor

**Profit Factor:**
- Ratio of gross profit to gross loss
- Formula: `Total Wins / Total Losses`
- **Interpretation:**
  - < 1.0: Losing money
  - 1.0 - 1.5: Break-even to moderate
  - 1.5 - 2.0: Good
  - \> 2.0: Excellent
- **Use:** Determine if wins outweigh losses

---

## 💡 Best Practices

### Capital Allocation Strategy

**DO:**
- ✅ **Prioritize Sharpe Ratio** - Allocate more to managers with Sharpe >1.5
- ✅ **Monitor Drawdown** - Reduce allocation if drawdown exceeds 20%
- ✅ **Diversify** - Don't put all capital with one manager
- ✅ **Consider Win Rate + Profit Factor together** - Both tell the full story
- ✅ **Review regularly** - Check rankings weekly or monthly
- ✅ **Follow system recommendations** - Review capital allocation suggestions

**DON'T:**
- ❌ **Chase returns alone** - High returns with high risk aren't sustainable
- ❌ **Ignore risk metrics** - Sharpe/Sortino are crucial
- ❌ **Overtrade** - Let managers do their work
- ❌ **React to short-term noise** - Use 30-90 day views for decisions
- ❌ **Ignore warnings** - Risk alerts indicate real problems

### When to Increase Allocation

Increase capital when a manager has:
- Sharpe Ratio >1.5
- Consistent positive returns (3+ months)
- Maximum drawdown <15%
- Win rate >50%
- Profit factor >1.5
- No active risk alerts

### When to Reduce Allocation

Reduce capital when a manager has:
- Sharpe Ratio <0.5
- Consistent negative returns
- Maximum drawdown >20%
- Win rate <40%
- Profit factor <1.0
- Multiple risk alerts

### Periodic Review Schedule

**Weekly:**
- Quick check of manager rankings
- Review any new risk alerts
- Note significant changes

**Monthly:**
- Comprehensive performance review
- Implement capital allocation changes
- Document decisions and rationale

**Quarterly:**
- Strategic review of fund structure
- Assess overall portfolio performance
- Consider adding/removing managers

---

## 🔧 Tips & Shortcuts

### Efficient Workflow

1. **Start with Managers View** - It's the default for a reason
2. **Sort by Sharpe** - Quickly find best risk-adjusted performers
3. **Check Top Performer Banner** - See best manager instantly
4. **Read Recommendations** - System suggestions are data-driven
5. **Review Alerts** - Address warnings promptly
6. **Export Data** - Use export button for reports

### Understanding Status Badges

- **⭐ BEST PERFORMER** (Green) - Excellent metrics, increase allocation
- **✓ SOLID** (Blue) - Good performance, maintain or increase
- **⚠️ HIGH RISK** (Red) - Concerning metrics, monitor or reduce
- **MONITOR** (Gray) - Average performance, watch closely

### Time Period Selection

- **7 Days** - Too short for decisions, check recent changes only
- **30 Days** - Default, good for monthly reviews
- **90 Days** - Best for allocation decisions (balances recent + trend)
- **6 Months+** - Long-term trends, strategic planning

---

## ❓ Troubleshooting

### Issue: No Data Displaying

**Possible causes:**
- Period selector set incorrectly
- No trading activity in selected timeframe
- Data sync issue from MT5

**Solutions:**
1. Try different time period (e.g., 90 days instead of 7)
2. Check if MT5 accounts are connected
3. Refresh the page
4. Verify with admin that data sync is working

### Issue: Metrics Seem Incorrect

**Possible causes:**
- Time period confusion (30d vs all-time)
- Recent allocation changes not reflected
- Deal data sync delay

**Solutions:**
1. Verify selected time period
2. Check "Last Updated" timestamp
3. Wait 5 minutes and refresh (data caches for performance)
4. Compare with MT5 terminal for verification

### Issue: Manager Not Showing

**Possible causes:**
- Manager inactive in selected period
- No trades in timeframe
- Manager recently added

**Solutions:**
1. Try longer time period (90 days or 6 months)
2. Verify manager is "active" status
3. Check if account has trading history
4. Contact admin to verify manager setup

### Issue: Slow Performance

**Possible causes:**
- Large time period selected
- Multiple tabs open
- Network issues

**Solutions:**
1. Use 30 or 90 day periods (avoid "all time")
2. Close unused browser tabs
3. Refresh the page
4. Data is cached for 5 minutes - subsequent loads faster

---

## 📞 Support & Further Reading

### Getting Help

- **Technical issues:** Contact admin support
- **Metric questions:** Review this guide's "Understanding Key Metrics" section
- **Strategy questions:** Consult with your investment advisor

### Additional Resources

- Technical Documentation: `/docs/TECHNICAL_DOCUMENTATION.md`
- System Architecture: Technical Documentation → Architecture tab
- API Documentation: Technical Documentation → API Documentation tab

---

## 📝 Quick Reference Card

**Manager Rankings - Quick Decision Guide:**

| Sharpe Ratio | Max Drawdown | Win Rate | Profit Factor | Decision |
|--------------|--------------|----------|---------------|----------|
| >1.5 | <15% | >50% | >1.5 | ✅ Increase allocation |
| 1.0-1.5 | 15-20% | 40-50% | 1.2-1.5 | ✓ Maintain allocation |
| 0.5-1.0 | 20-25% | 30-40% | 1.0-1.2 | ⚠️ Monitor closely |
| <0.5 | >25% | <30% | <1.0 | ❌ Reduce/remove allocation |

**Color Coding:**
- 🟢 Green = Positive, Good, Increase
- 🔵 Blue = Neutral, Solid, Maintain
- 🟡 Yellow = Warning, Monitor
- 🔴 Red = Negative, Poor, Reduce

---

*Last Updated: [Current Date]*
*Version: 1.0*
*FIDUS Investment Platform - Trading Analytics*
