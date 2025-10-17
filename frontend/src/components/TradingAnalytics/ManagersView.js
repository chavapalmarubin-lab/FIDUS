import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../ui/LoadingSpinner';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { formatCurrency, formatPercentage } from '../../constants/styles';
import './ManagersView.css';

export default function ManagersView({ period }) {
  const [managers, setManagers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('return_percentage'); // Default sort by return

  useEffect(() => {
    fetchManagers();
  }, [period]);

  const fetchManagers = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(
        `${backendUrl}/api/admin/trading-analytics/managers?period_days=${period}`,
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

      const data = await response.json();
      
      if (data.success && data.managers) {
        setManagers(data.managers);
      } else {
        throw new Error(data.error || 'Failed to fetch managers');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching managers:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Sort managers
  const sortedManagers = [...managers].sort((a, b) => {
    const aVal = a[sortBy] || 0;
    const bVal = b[sortBy] || 0;
    return bVal - aVal; // Descending order
  });

  // Helper Functions moved to shared constants
  // Using imported formatCurrency and formatPercentage

  const getRankEmoji = (index) => {
    if (index === 0) return '🥇';
    if (index === 1) return '🥈';
    if (index === 2) return '🥉';
    return `#${index + 1}`;
  };

  const getSharpeClass = (sharpe) => {
    if (sharpe >= 2) return 'excellent';
    if (sharpe >= 1) return 'good';
    if (sharpe >= 0.5) return 'fair';
    return 'poor';
  };

  const getSharpeLabel = (sharpe) => {
    if (sharpe >= 2) return 'Excellent';
    if (sharpe >= 1) return 'Good';
    if (sharpe >= 0.5) return 'Fair';
    return 'Poor';
  };

  const getProfitFactorClass = (pf) => {
    if (pf >= 2) return 'excellent';
    if (pf >= 1.5) return 'good';
    if (pf >= 1) return 'breakeven';
    return 'poor';
  };

  const getStatusBadge = (manager) => {
    if (manager.sharpe_ratio >= 1.5 && manager.profit_factor >= 2) {
      return { label: '⭐ BEST PERFORMER', class: 'status-best' };
    }
    if (manager.sharpe_ratio >= 1) {
      return { label: '✓ SOLID', class: 'status-solid' };
    }
    if (manager.win_rate < 30 || manager.profit_factor < 1) {
      return { label: '⚠️ HIGH RISK', class: 'status-risk' };
    }
    return { label: 'MONITOR', class: 'status-monitor' };
  };

  const generateAllocationSuggestions = () => {
    const suggestions = [];
    
    // Best performer - allocate more
    const best = sortedManagers[0];
    if (best && best.sharpe_ratio > 1.5) {
      suggestions.push({
        type: 'increase',
        manager: best.manager_name,
        message: `Consider allocating more capital to ${best.manager_name} (Sharpe: ${best.sharpe_ratio.toFixed(2)}, Return: +${best.return_percentage.toFixed(2)}%)`,
        priority: 'high'
      });
    }
    
    // Poor performers - reduce allocation
    const poor = sortedManagers.filter(m => (m.sharpe_ratio && m.sharpe_ratio < 0.5) || (m.profit_factor && m.profit_factor < 1));
    poor.forEach(manager => {
      suggestions.push({
        type: 'decrease',
        manager: manager.manager_name,
        message: `Consider reducing ${manager.manager_name} allocation (Sharpe: ${manager.sharpe_ratio?.toFixed(2) || 'N/A'}, PF: ${manager.profit_factor?.toFixed(2) || 'N/A'})`,
        priority: 'medium'
      });
    });
    
    return suggestions;
  };

  const generateRiskAlerts = () => {
    const alerts = [];
    
    sortedManagers.forEach(manager => {
      // Low win rate alert
      if (manager.win_rate && manager.win_rate < 30) {
        alerts.push({
          type: 'warning',
          message: `${manager.manager_name} has low win rate (${manager.win_rate.toFixed(1)}%) - Monitor closely`
        });
      }
      
      // High drawdown alert
      if (manager.max_drawdown_pct && Math.abs(manager.max_drawdown_pct) > 20) {
        alerts.push({
          type: 'danger',
          message: `${manager.manager_name} has high drawdown (${manager.max_drawdown_pct.toFixed(1)}%) - Risk assessment needed`
        });
      }
      
      // Low profit factor
      if (manager.profit_factor && manager.profit_factor < 1) {
        alerts.push({
          type: 'warning',
          message: `${manager.manager_name} profit factor below 1.0 (${manager.profit_factor.toFixed(2)}) - Not profitable`
        });
      }
    });
    
    return alerts;
  };

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading manager rankings..." />;
  }

  if (error) {
    return (
      <div className="managers-view-error">
        <p>❌ Error loading managers: {error}</p>
        <Button variant="primary" onClick={fetchManagers} className="mt-4">
          Retry
        </Button>
      </div>
    );
  }

  if (!managers || managers.length === 0) {
    return (
      <div className="managers-view-empty">
        <p>No managers data available</p>
      </div>
    );
  }

  const suggestions = generateAllocationSuggestions();
  const alerts = generateRiskAlerts();

  return (
    <div className="managers-view">
      {/* Page Header */}
      <div className="page-header">
        <h2>Manager Performance Rankings</h2>
        <p className="subtitle">
          Risk-adjusted performance analysis for capital allocation decisions
        </p>
      </div>

      {/* Top Performers Banner */}
      {sortedManagers[0] && (
        <div className="top-performers-banner">
          <div className="top-performer">
            <span className="rank-emoji">🏆</span>
            <div className="performer-info">
              <div className="performer-name">{sortedManagers[0].manager_name}</div>
              <div className="performer-stats">
                <span className="return-value positive">
                  +{sortedManagers[0].return_percentage?.toFixed(2)}%
                </span>
                <span className="pnl-value">{formatCurrency(sortedManagers[0].total_pnl)}</span>
                <span className="sharpe-value">Sharpe: {sortedManagers[0].sharpe_ratio?.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manager Rankings Table */}
      <div className="rankings-section">
        <div className="section-header">
          <h3>📊 Complete Rankings</h3>
          <div className="table-controls">
            <label>Sort by:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-selector">
              <option value="return_percentage">Return %</option>
              <option value="sharpe_ratio">Sharpe Ratio</option>
              <option value="sortino_ratio">Sortino Ratio</option>
              <option value="profit_factor">Profit Factor</option>
              <option value="total_pnl">Total P&L</option>
              <option value="win_rate">Win Rate</option>
            </select>
          </div>
        </div>

        {/* Desktop Table View - Hidden on Mobile/Tablet */}
        <div className="table-container desktop-only">
          <table className="manager-rankings-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Manager</th>
                <th>Strategy</th>
                <th>Fund</th>
                <th>Account</th>
                <th>P&L</th>
                <th>Return %</th>
                <th>Sharpe</th>
                <th>Sortino</th>
                <th>Max DD</th>
                <th>Win Rate</th>
                <th>Profit Factor</th>
                <th>Risk</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {sortedManagers.map((manager, index) => {
                const status = getStatusBadge(manager);
                
                return (
                  <tr key={manager.manager_id} className={`rank-row rank-${index + 1}`}>
                    {/* Rank */}
                    <td className="rank-cell">
                      <span className="rank-badge">{getRankEmoji(index)}</span>
                    </td>

                    {/* Manager Name */}
                    <td className="manager-name-cell">
                      <strong>{manager.manager_name}</strong>
                    </td>

                    {/* Strategy */}
                    <td>{manager.strategy}</td>

                    {/* Fund */}
                    <td>
                      <Badge type="fund" variant={manager.fund}>
                        {manager.fund}
                      </Badge>
                    </td>

                    {/* Account */}
                    <td className="account-cell">{manager.account}</td>

                    {/* P&L */}
                    <td className={`pnl-cell ${manager.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                      <strong>{formatCurrency(manager.total_pnl)}</strong>
                    </td>

                    {/* Return % */}
                    <td className={`return-cell ${manager.return_percentage >= 0 ? 'positive' : 'negative'}`}>
                      <strong>
                        {manager.return_percentage >= 0 ? '+' : ''}
                        {manager.return_percentage?.toFixed(2)}%
                      </strong>
                    </td>

                    {/* Sharpe Ratio */}
                    <td>
                      <div className={`sharpe-indicator ${getSharpeClass(manager.sharpe_ratio)}`}>
                        <span className="value">{manager.sharpe_ratio?.toFixed(2) || 'N/A'}</span>
                        <span className="label">{getSharpeLabel(manager.sharpe_ratio)}</span>
                      </div>
                    </td>

                    {/* Sortino Ratio */}
                    <td>
                      <span className={`ratio-value ${getSharpeClass(manager.sortino_ratio)}`}>
                        {manager.sortino_ratio?.toFixed(2) || 'N/A'}
                      </span>
                    </td>

                    {/* Max Drawdown */}
                    <td>
                      <div className={`drawdown-cell ${Math.abs(manager.max_drawdown_pct) > 20 ? 'warning' : 'ok'}`}>
                        {manager.max_drawdown_pct?.toFixed(2)}%
                        {Math.abs(manager.max_drawdown_pct) > 20 && <span className="warning-icon">⚠️</span>}
                      </div>
                    </td>

                    {/* Win Rate */}
                    <td>
                      <div className="win-rate-bar">
                        <div className="bar-fill" style={{ width: `${manager.win_rate}%` }}></div>
                        <span className="bar-label">{manager.win_rate?.toFixed(1)}%</span>
                      </div>
                    </td>

                    {/* Profit Factor */}
                    <td>
                      <span className={`profit-factor ${getProfitFactorClass(manager.profit_factor)}`}>
                        {manager.profit_factor?.toFixed(2) || 'N/A'}
                      </span>
                    </td>

                    {/* Risk Level */}
                    <td>
                      <Badge type="risk" variant={manager.risk_level}>
                        {manager.risk_level}
                      </Badge>
                    </td>

                    {/* Status */}
                    <td>
                      <span className={`status-badge ${status.class}`}>
                        {status.label}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Mobile/Tablet Card View - Hidden on Desktop */}
        <div className="manager-cards-container mobile-tablet-only">
          {sortedManagers.map((manager, index) => {
            const status = getStatusBadge(manager);
            
            return (
              <div key={manager.manager_id} className={`manager-card rank-${index + 1}`}>
                {/* Card Header */}
                <div className="manager-card-header">
                  <div className="manager-card-rank">
                    <span className="rank-badge-mobile">{getRankEmoji(index)}</span>
                  </div>
                  <div className="manager-card-title">
                    <h4 className="manager-name">{manager.manager_name}</h4>
                    <div className="manager-meta">
                      <Badge type="fund" variant={manager.fund}>{manager.fund}</Badge>
                      <span className="account-number">#{manager.account}</span>
                    </div>
                  </div>
                  <div className="manager-card-status">
                    <span className={`status-badge-mobile ${status.class}`}>
                      {status.label}
                    </span>
                  </div>
                </div>

                {/* Key Metrics - Prominent Display */}
                <div className="manager-card-key-metrics">
                  <div className="metric-primary">
                    <div className="metric-label">P&L</div>
                    <div className={`metric-value ${manager.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrency(manager.total_pnl)}
                    </div>
                  </div>
                  <div className="metric-primary">
                    <div className="metric-label">Return</div>
                    <div className={`metric-value ${manager.return_percentage >= 0 ? 'positive' : 'negative'}`}>
                      {manager.return_percentage >= 0 ? '+' : ''}
                      {manager.return_percentage?.toFixed(2)}%
                    </div>
                  </div>
                  <div className="metric-primary">
                    <div className="metric-label">Sharpe</div>
                    <div className={`metric-value sharpe-${getSharpeClass(manager.sharpe_ratio)}`}>
                      {manager.sharpe_ratio?.toFixed(2) || 'N/A'}
                      <span className="metric-sublabel">{getSharpeLabel(manager.sharpe_ratio)}</span>
                    </div>
                  </div>
                </div>

                {/* Collapsible Details */}
                <details className="manager-card-details">
                  <summary className="details-toggle">
                    <span>View All Metrics</span>
                    <span className="toggle-icon">▼</span>
                  </summary>
                  
                  <div className="manager-card-expanded">
                    {/* Risk Metrics Row */}
                    <div className="metrics-grid">
                      <div className="metric-item">
                        <div className="metric-label">Sortino</div>
                        <div className="metric-value">
                          {manager.sortino_ratio?.toFixed(2) || 'N/A'}
                        </div>
                      </div>
                      <div className="metric-item">
                        <div className="metric-label">Max DD</div>
                        <div className={`metric-value ${Math.abs(manager.max_drawdown_pct) > 20 ? 'warning' : ''}`}>
                          {manager.max_drawdown_pct?.toFixed(2)}%
                          {Math.abs(manager.max_drawdown_pct) > 20 && <span> ⚠️</span>}
                        </div>
                      </div>
                      <div className="metric-item">
                        <div className="metric-label">Profit Factor</div>
                        <div className={`metric-value pf-${getProfitFactorClass(manager.profit_factor)}`}>
                          {manager.profit_factor?.toFixed(2) || 'N/A'}
                        </div>
                      </div>
                    </div>

                    {/* Win Rate Bar */}
                    <div className="metric-item full-width">
                      <div className="metric-label">Win Rate</div>
                      <div className="win-rate-bar-mobile">
                        <div className="bar-fill" style={{ width: `${manager.win_rate}%` }}></div>
                        <span className="bar-label">{manager.win_rate?.toFixed(1)}%</span>
                      </div>
                    </div>

                    {/* Additional Info */}
                    <div className="metrics-grid">
                      <div className="metric-item">
                        <div className="metric-label">Strategy</div>
                        <div className="metric-value small">{manager.strategy}</div>
                      </div>
                      <div className="metric-item">
                        <div className="metric-label">Risk Level</div>
                        <div className="metric-value">
                          <Badge type="risk" variant={manager.risk_level}>
                            {manager.risk_level}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </details>
              </div>
            );
          })}
        </div>
      </div>

      {/* Capital Allocation Suggestions */}
      {suggestions.length > 0 && (
        <div className="allocation-suggestions">
          <h3>💰 Capital Allocation Recommendations</h3>
          <div className="suggestions-grid">
            {suggestions.map((suggestion, i) => (
              <div key={i} className={`suggestion-card suggestion-${suggestion.type} priority-${suggestion.priority}`}>
                <div className="suggestion-icon">
                  {suggestion.type === 'increase' ? '📈' : '📉'}
                </div>
                <div className="suggestion-content">
                  <div className="suggestion-manager">{suggestion.manager}</div>
                  <div className="suggestion-message">{suggestion.message}</div>
                </div>
                <div className="suggestion-priority">
                  {suggestion.priority === 'high' && <span className="badge-high">HIGH PRIORITY</span>}
                  {suggestion.priority === 'medium' && <span className="badge-medium">MEDIUM</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Alerts */}
      {alerts.length > 0 && (
        <div className="risk-alerts">
          <h3>⚠️ Risk Alerts & Warnings</h3>
          <div className="alerts-list">
            {alerts.map((alert, i) => (
              <div key={i} className={`alert alert-${alert.type}`}>
                <span className="alert-icon">
                  {alert.type === 'danger' ? '🚨' : '⚠️'}
                </span>
                <span className="alert-message">{alert.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="summary-stats">
        <div className="stat-card">
          <div className="stat-label">Total Managers</div>
          <div className="stat-value">{managers.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total P&L</div>
          <div className="stat-value positive">
            {formatCurrency(managers.reduce((sum, m) => sum + (m.total_pnl || 0), 0))}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Return</div>
          <div className="stat-value">
            {(managers.reduce((sum, m) => sum + (m.return_percentage || 0), 0) / managers.length).toFixed(2)}%
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Sharpe</div>
          <div className="stat-value">
            {(managers.reduce((sum, m) => sum + (m.sharpe_ratio || 0), 0) / managers.length).toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
}
