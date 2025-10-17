import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../ui/LoadingSpinner';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { formatCurrency } from '../../constants/styles';
import './PortfolioView.css';
import './TradingAnalytics-responsive.css';

export default function PortfolioView({ period }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPortfolioData();
  }, [period]);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(
        `${backendUrl}/api/admin/trading-analytics/portfolio?period_days=${period}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.portfolio) {
        setData(result.portfolio);
      } else {
        throw new Error(result.error || 'Failed to fetch portfolio data');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching portfolio data:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Using imported formatCurrency from shared constants

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading portfolio data..." />;
  }

  if (error) {
    return (
      <div className="portfolio-view-error">
        <p>❌ Error loading portfolio: {error}</p>
        <Button variant="primary" onClick={fetchPortfolioData} className="mt-4">
          Retry
        </Button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="portfolio-view-empty">
        <p>No portfolio data available</p>
      </div>
    );
  }

  return (
    <div className="portfolio-view">
      {/* Page Header */}
      <div className="page-header">
        <h2>Portfolio Overview</h2>
        <p className="subtitle">Complete fund performance across all investments</p>
      </div>

      {/* Key Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card metric-blue">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-label">Total AUM</div>
            <div className="metric-value">{formatCurrency(data.total_aum)}</div>
            <div className="metric-subtitle">{data.total_managers} active managers</div>
          </div>
        </div>

        <div className={`metric-card ${data.total_pnl >= 0 ? 'metric-green' : 'metric-red'}`}>
          <div className="metric-icon">{data.total_pnl >= 0 ? '📈' : '📉'}</div>
          <div className="metric-content">
            <div className="metric-label">Total P&L</div>
            <div className="metric-value">{formatCurrency(data.total_pnl)}</div>
            <div className="metric-subtitle">
              {data.blended_return >= 0 ? '+' : ''}{data.blended_return?.toFixed(2)}% blended return
            </div>
          </div>
        </div>

        <div className="metric-card metric-purple">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <div className="metric-label">Active Managers</div>
            <div className="metric-value">{data.active_managers}</div>
            <div className="metric-subtitle">of {data.total_managers} total</div>
          </div>
        </div>

        <div className="metric-card metric-orange">
          <div className="metric-icon">⚖️</div>
          <div className="metric-content">
            <div className="metric-label">Current Equity</div>
            <div className="metric-value">{formatCurrency(data.total_equity)}</div>
            <div className="metric-subtitle">
              {((data.total_equity / data.total_aum) * 100).toFixed(2)}% of AUM
            </div>
          </div>
        </div>
      </div>

      {/* Asset Allocation Section */}
      <div className="allocation-section">
        <h3>Asset Allocation by Fund</h3>
        <div className="allocation-visual">
          {data.funds && Object.entries(data.funds).map(([fundName, fundData]) => {
            const percentage = (fundData.aum / data.total_aum) * 100;
            
            return (
              <div key={fundName} className="fund-allocation-item">
                <div className="fund-header">
                  <Badge type="fund" variant={fundName}>
                    {fundName}
                  </Badge>
                  <span className="fund-percentage">{percentage.toFixed(1)}%</span>
                </div>
                <div className="fund-bar">
                  <div 
                    className={`fund-bar-fill fund-${fundName.toLowerCase()}-fill`}
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
                <div className="fund-details">
                  <span>AUM: {formatCurrency(fundData.aum)}</span>
                  <span className={fundData.pnl >= 0 ? 'positive' : 'negative'}>
                    P&L: {formatCurrency(fundData.pnl)}
                  </span>
                  <span>Return: {fundData.return_pct?.toFixed(2)}%</span>
                  <span>{fundData.managers_count} managers</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Fund Breakdown Table */}
      <div className="fund-breakdown-section">
        <h3>Fund Performance Breakdown</h3>
        <table className="fund-breakdown-table">
          <thead>
            <tr>
              <th>Fund</th>
              <th>AUM</th>
              <th>Current Equity</th>
              <th>P&L</th>
              <th>Return %</th>
              <th>Managers</th>
              <th>Weight</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.funds && Object.entries(data.funds).map(([fundName, fundData]) => {
              const weight = (fundData.aum / data.total_aum) * 100;
              const isPerforming = fundData.return_pct >= 0;
              
              return (
                <tr key={fundName}>
                  <td>
                    <Badge type="fund" variant={fundName}>
                      {fundName}
                    </Badge>
                  </td>
                  <td>{formatCurrency(fundData.aum)}</td>
                  <td>{formatCurrency(fundData.aum + fundData.pnl)}</td>
                  <td className={fundData.pnl >= 0 ? 'positive' : 'negative'}>
                    <strong>{formatCurrency(fundData.pnl)}</strong>
                  </td>
                  <td className={fundData.return_pct >= 0 ? 'positive' : 'negative'}>
                    <strong>
                      {fundData.return_pct >= 0 ? '+' : ''}
                      {fundData.return_pct?.toFixed(2)}%
                    </strong>
                  </td>
                  <td>{fundData.managers_count}</td>
                  <td>{weight.toFixed(1)}%</td>
                  <td>
                    <Badge variant={isPerforming ? 'success' : 'warning'}>
                      {isPerforming ? '✓ Performing' : '⚠️ Underperforming'}
                    </Badge>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Period Information */}
      <div className="period-info">
        <p>📅 Analysis Period: Last {period} days</p>
        <p>🕐 Last Updated: {new Date(data.generated_at).toLocaleString()}</p>
      </div>
    </div>
  );
}
