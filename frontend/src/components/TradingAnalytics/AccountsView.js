import React from 'react';
import './AccountsView.css';

export default function AccountsView({ period }) {
  return (
    <div className="accounts-view">
      <div className="page-header">
        <h2>Account Details</h2>
        <p className="subtitle">Detailed trading analytics for individual accounts</p>
      </div>

      <div className="coming-soon">
        <div className="coming-soon-icon">🚧</div>
        <h3>Account-Level Details Coming Soon</h3>
        <p>
          This tab will provide detailed account-level analytics including:
        </p>
        <ul>
          <li>Individual trade history</li>
          <li>Equity curves and drawdown analysis</li>
          <li>Position sizing patterns</li>
          <li>Symbol-specific performance</li>
          <li>Time-based performance analysis</li>
        </ul>
        <p className="note">
          For now, use the <strong>Managers</strong> tab to view performance by manager,
          which includes account-level data.
        </p>
      </div>
    </div>
  );
}
