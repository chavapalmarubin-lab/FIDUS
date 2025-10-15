import * as XLSX from 'xlsx';

/**
 * PHASE 4: Export utilities for dashboard data
 */

/**
 * Export data to Excel file
 * @param {Array} data - Array of objects to export
 * @param {String} filename - Name of the file (without extension)
 * @param {String} sheetName - Name of the worksheet
 */
export const exportToExcel = (data, filename = 'Export', sheetName = 'Data') => {
  try {
    // Create worksheet from data
    const worksheet = XLSX.utils.json_to_sheet(data);
    
    // Create workbook
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
    
    // Generate filename with timestamp
    const timestamp = new Date().toISOString().split('T')[0];
    const fullFilename = `${filename}_${timestamp}.xlsx`;
    
    // Write file
    XLSX.writeFile(workbook, fullFilename);
    
    return { success: true, filename: fullFilename };
  } catch (error) {
    console.error('Export error:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Export multiple sheets to single Excel file
 * @param {Array} sheets - Array of {name, data} objects
 * @param {String} filename - Name of the file
 */
export const exportMultipleSheets = (sheets, filename = 'Export') => {
  try {
    const workbook = XLSX.utils.book_new();
    
    sheets.forEach(sheet => {
      const worksheet = XLSX.utils.json_to_sheet(sheet.data);
      XLSX.utils.book_append_sheet(workbook, worksheet, sheet.name);
    });
    
    const timestamp = new Date().toISOString().split('T')[0];
    const fullFilename = `${filename}_${timestamp}.xlsx`;
    
    XLSX.writeFile(workbook, fullFilename);
    
    return { success: true, filename: fullFilename };
  } catch (error) {
    console.error('Export error:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Format currency for export
 */
export const formatCurrencyForExport = (value) => {
  return typeof value === 'number' ? `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : value;
};

/**
 * Format percentage for export
 */
export const formatPercentageForExport = (value) => {
  return typeof value === 'number' ? `${value.toFixed(2)}%` : value;
};

/**
 * Format date for export
 */
export const formatDateForExport = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('en-US');
};

/**
 * Export Trading Analytics data
 */
export const exportTradingAnalytics = (analyticsData, dailyPerformance, trades) => {
  const sheets = [
    {
      name: 'Overview',
      data: [
        { Metric: 'Total P&L', Value: formatCurrencyForExport(analyticsData?.overview?.total_pnl) },
        { Metric: 'Win Rate', Value: formatPercentageForExport(analyticsData?.overview?.win_rate) },
        { Metric: 'Total Trades', Value: analyticsData?.overview?.total_trades },
        { Metric: 'Winning Trades', Value: analyticsData?.overview?.winning_trades },
        { Metric: 'Losing Trades', Value: analyticsData?.overview?.losing_trades },
        { Metric: 'Average Win', Value: formatCurrencyForExport(analyticsData?.overview?.avg_win) },
        { Metric: 'Average Loss', Value: formatCurrencyForExport(analyticsData?.overview?.avg_loss) },
      ]
    },
    {
      name: 'Daily Performance',
      data: dailyPerformance.map(day => ({
        Date: formatDateForExport(day.date),
        'P&L': formatCurrencyForExport(day.pnl),
        Trades: day.trades,
        'Win Rate': formatPercentageForExport(day.win_rate)
      }))
    },
    {
      name: 'Recent Trades',
      data: trades.map(trade => ({
        Date: formatDateForExport(trade.date),
        Symbol: trade.symbol,
        Type: trade.type,
        'P&L': formatCurrencyForExport(trade.pnl),
        Volume: trade.volume,
        'Entry Price': trade.entry_price,
        'Exit Price': trade.exit_price
      }))
    }
  ];
  
  return exportMultipleSheets(sheets, 'TradingAnalytics');
};

/**
 * Export Fund Portfolio data
 */
export const exportFundPortfolio = (fundData, portfolioStats) => {
  const sheets = [
    {
      name: 'Portfolio Summary',
      data: [
        { Metric: 'Total AUM', Value: formatCurrencyForExport(portfolioStats?.aum) },
        { Metric: 'Number of Investors', Value: portfolioStats?.investors },
        { Metric: 'Weighted Return', Value: formatPercentageForExport(portfolioStats?.weighted_return) }
      ]
    },
    {
      name: 'Fund Details',
      data: Object.entries(fundData || {}).map(([fundCode, fund]) => ({
        'Fund Code': fundCode,
        'Fund Type': fund.fund_type,
        'Current AUM': formatCurrencyForExport(fund.current_aum),
        'Target AUM': formatCurrencyForExport(fund.target_aum),
        'NAV per Share': formatCurrencyForExport(fund.nav_per_share),
        'Return %': formatPercentageForExport(fund.return_pct),
        'Number of Investors': fund.num_investors
      }))
    }
  ];
  
  return exportMultipleSheets(sheets, 'FundPortfolio');
};

/**
 * Export Cash Flow data
 */
export const exportCashFlow = (fundAccounting, monthlyData) => {
  const sheets = [
    {
      name: 'Fund Accounting',
      data: [
        { Category: 'Assets', Item: 'MT5 Trading Profits', Amount: formatCurrencyForExport(fundAccounting?.assets?.mt5_trading_profits) },
        { Category: 'Assets', Item: 'Broker Rebates', Amount: formatCurrencyForExport(fundAccounting?.assets?.broker_rebates) },
        { Category: 'Assets', Item: 'Broker Interest', Amount: formatCurrencyForExport(fundAccounting?.assets?.broker_interest) },
        { Category: 'Assets', Item: 'Total Inflows', Amount: formatCurrencyForExport(fundAccounting?.assets?.total_inflows) },
        { Category: 'Liabilities', Item: 'Client Obligations', Amount: formatCurrencyForExport(fundAccounting?.liabilities?.client_obligations) },
        { Category: 'Liabilities', Item: 'Fund Obligations', Amount: formatCurrencyForExport(fundAccounting?.liabilities?.fund_obligations) },
        { Category: 'Liabilities', Item: 'Total Outflows', Amount: formatCurrencyForExport(fundAccounting?.liabilities?.total_outflows) },
        { Category: 'Net', Item: 'Net Fund Profitability', Amount: formatCurrencyForExport(fundAccounting?.net_fund_profitability) }
      ]
    },
    {
      name: 'Monthly Trends',
      data: monthlyData.map(month => ({
        Month: month.month,
        'Trading Profits': formatCurrencyForExport(month.trading_profits),
        'Withdrawals': formatCurrencyForExport(month.withdrawals),
        'Net Position': formatCurrencyForExport(month.net_position)
      }))
    }
  ];
  
  return exportMultipleSheets(sheets, 'CashFlow');
};

/**
 * Export Money Managers data
 */
export const exportMoneyManagers = (managers) => {
  const data = managers.map(manager => ({
    'Manager Name': manager.manager_name,
    'Strategy': manager.strategy,
    'Risk Level': manager.risk_level,
    'TRUE P&L': formatCurrencyForExport(manager.performance?.true_pnl),
    'Return %': formatPercentageForExport(manager.performance?.return_pct),
    'Win Rate': formatPercentageForExport(manager.performance?.win_rate),
    'Total Trades': manager.performance?.total_trades,
    'Active Accounts': manager.accounts?.length || 0
  }));
  
  return exportToExcel(data, 'MoneyManagers', 'Managers');
};
