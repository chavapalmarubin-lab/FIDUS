import React, { useState, lazy, Suspense } from 'react';
import LoadingSpinner from './ui/LoadingSpinner';
import './TradingAnalyticsDashboard.css';

// Lazy load tab components for better performance
const PortfolioView = lazy(() => import('./TradingAnalytics/PortfolioView'));
const FundsView = lazy(() => import('./TradingAnalytics/FundsView'));
const ManagersView = lazy(() => import('./TradingAnalytics/ManagersView'));
const AccountsView = lazy(() => import('./TradingAnalytics/AccountsView'));

export default function TradingAnalyticsDashboard() {
  const [activeTab, setActiveTab] = useState('managers'); // Default to Managers (most important)
  const [period, setPeriod] = useState(30); // Default 30 days

  const handleRefresh = () => {
    window.location.reload();
  };

  const handleExport = () => {
    alert('Export functionality coming soon!');
  };

  return (
    <div className="trading-analytics-dashboard">
      {/* Header */}
      <div className="analytics-header">
        <div className="header-left">
          <h1>📊 Trading Analytics</h1>
          <p className="subtitle">Manager Performance & Capital Allocation</p>
        </div>
        <div className="header-controls">
          <select 
            value={period} 
            onChange={(e) => setPeriod(parseInt(e.target.value))}
            className="period-selector"
          >
            <option value={7}>Last 7 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
            <option value={180}>Last 6 Months</option>
            <option value={365}>Last Year</option>
          </select>
          <button onClick={handleRefresh} className="btn-icon">
            🔄 Refresh
          </button>
          <button onClick={handleExport} className="btn-icon">
            📥 Export
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="analytics-tabs">
        <button
          className={`tab-btn ${activeTab === 'portfolio' ? 'active' : ''}`}
          onClick={() => setActiveTab('portfolio')}
        >
          <span className="tab-icon">🌐</span>
          Portfolio Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'funds' ? 'active' : ''}`}
          onClick={() => setActiveTab('funds')}
        >
          <span className="tab-icon">💼</span>
          Fund Performance
        </button>
        <button
          className={`tab-btn ${activeTab === 'managers' ? 'active' : ''}`}
          onClick={() => setActiveTab('managers')}
        >
          <span className="tab-icon">👥</span>
          Manager Rankings
          <span className="primary-badge">PRIMARY</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'accounts' ? 'active' : ''}`}
          onClick={() => setActiveTab('accounts')}
        >
          <span className="tab-icon">📈</span>
          Account Details
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'portfolio' && <PortfolioView period={period} />}
        {activeTab === 'funds' && <FundsView period={period} />}
        {activeTab === 'managers' && <ManagersView period={period} />}
        {activeTab === 'accounts' && <AccountsView period={period} />}
      </div>
    </div>
  );
}
