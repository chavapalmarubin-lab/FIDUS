import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../ui/LoadingSpinner';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { formatCurrency } from '../../constants/styles';
import './FundsView.css';

export default function FundsView({ period }) {
  const [selectedFund, setSelectedFund] = useState('BALANCE');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFundData();
  }, [selectedFund, period]);

  const fetchFundData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const token = localStorage.getItem('fidus_token');
      
      const response = await fetch(
        `${backendUrl}/api/admin/trading-analytics/funds/${selectedFund}?period_days=${period}`,
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
      
      if (result.success && result.fund) {
        setData(result.fund);
      } else {
        throw new Error(result.error || 'Failed to fetch fund data');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching fund data:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  // Using imported formatCurrency from shared constants

  if (loading) {
    return <LoadingSpinner size="lg" text="Loading fund data..." />;
  }

  if (error) {
    return (
      <div className="funds-view-error">
        <p>❌ Error loading fund: {error}</p>
        <Button variant="primary" onClick={fetchFundData} className="mt-4">
          Retry
        </Button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="funds-view-empty">
        <p>No fund data available</p>
      </div>
    );
  }

  return (
    <div className="funds-view">
      {/* Fund Selector */}
      <div className="fund-selector">
        <button
          className={`fund-btn ${selectedFund === 'BALANCE' ? 'active fund-balance' : ''}`}
          onClick={() => setSelectedFund('BALANCE')}
        >
          💼 BALANCE Fund
        </button>
        <button
          className={`fund-btn ${selectedFund === 'CORE' ? 'active fund-core' : ''}`}
          onClick={() => setSelectedFund('CORE')}
        >
          🎯 CORE Fund
        </button>
      </div>

      {/* Fund Summary */}
      <div className="fund-summary">
        <div className="fund-title">
          <h2>{data.fund_name} Fund</h2>
          <span className={`fund-status ${data.total_pnl >= 0 ? 'status-positive' : 'status-negative'}`}>
            {data.total_pnl >= 0 ? '✓ Profitable' : '⚠️ Loss'}
          </span>
        </div>

        <div className="metrics-row">
          <div className="metric-item">
            <div className="metric-label">AUM</div>
            <div className="metric-value">{formatCurrency(data.aum)}</div>
          </div>
          <div className="metric-item">
            <div className="metric-label">Current Equity</div>
            <div className="metric-value">{formatCurrency(data.total_equity)}</div>
          </div>
          <div className="metric-item">
            <div className="metric-label">Total P&L</div>
            <div className={`metric-value ${data.total_pnl >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(data.total_pnl)}
            </div>
          </div>
          <div className="metric-item">
            <div className="metric-label">Weighted Return</div>
            <div className={`metric-value ${data.weighted_return >= 0 ? 'positive' : 'negative'}`}>
              {data.weighted_return >= 0 ? '+' : ''}{data.weighted_return?.toFixed(2)}%
            </div>
          </div>
          <div className="metric-item">
            <div className="metric-label">Managers</div>
            <div className="metric-value">{data.managers_count}</div>
          </div>
        </div>
      </div>

      {/* Performance Attribution */}
      {data.best_performer && data.worst_performer && (
        <div className="performance-attribution">
          <div className="attribution-item best">
            <div className="attribution-icon">🏆</div>
            <div className="attribution-content">
              <div className="attribution-label">Best Performer</div>
              <div className="attribution-manager">{data.best_performer}</div>
            </div>
          </div>
          <div className="attribution-item worst">
            <div className="attribution-icon">📉</div>
            <div className="attribution-content">
              <div className="attribution-label">Needs Attention</div>
              <div className="attribution-manager">{data.worst_performer}</div>
            </div>
          </div>
        </div>
      )}

      {/* Managers in Fund */}
      <div className="managers-in-fund">
        <h3>Managers in {data.fund_name} Fund</h3>
        
        {data.managers && data.managers.length > 0 ? (
          <div className="manager-cards-grid">
            {data.managers.map((manager) => (
              <div key={manager.manager_id} className="manager-card">
                <div className="manager-card-header">
                  <div className="manager-name">{manager.manager_name}</div>
                  <span className={`status-indicator ${manager.status === 'active' ? 'status-active' : 'status-inactive'}`}>
                    {manager.status === 'active' ? '🟢' : '🔴'}
                  </span>
                </div>
                
                <div className="manager-card-body">
                  <div className="manager-detail">
                    <span className="detail-label">Strategy:</span>
                    <span className="detail-value">{manager.strategy}</span>
                  </div>
                  <div className="manager-detail">
                    <span className="detail-label">Account:</span>
                    <span className="detail-value">{manager.account}</span>
                  </div>
                  <div className="manager-detail">
                    <span className="detail-label">Allocation:</span>
                    <span className="detail-value">{formatCurrency(manager.initial_allocation)}</span>
                  </div>
                  <div className="manager-detail">
                    <span className="detail-label">Current Equity:</span>
                    <span className="detail-value">{formatCurrency(manager.current_equity)}</span>
                  </div>
                </div>

                <div className="manager-card-footer">
                  <div className="manager-metric">
                    <div className="metric-label">P&L</div>
                    <div className={`metric-value ${manager.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrency(manager.total_pnl)}
                    </div>
                  </div>
                  <div className="manager-metric">
                    <div className="metric-label">Return</div>
                    <div className={`metric-value ${manager.return_percentage >= 0 ? 'positive' : 'negative'}`}>
                      {manager.return_percentage >= 0 ? '+' : ''}{manager.return_percentage?.toFixed(2)}%
                    </div>
                  </div>
                  <div className="manager-metric">
                    <div className="metric-label">Contribution</div>
                    <div className="metric-value">
                      {manager.contribution_to_fund?.toFixed(2)}%
                    </div>
                  </div>
                  <div className="manager-metric">
                    <div className="metric-label">Sharpe</div>
                    <div className="metric-value">
                      {manager.sharpe_ratio?.toFixed(2) || 'N/A'}
                    </div>
                  </div>
                </div>

                <div className="manager-risk">
                  <span className={`risk-badge risk-${manager.risk_level}`}>
                    Risk: {manager.risk_level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-managers">
            <p>No managers assigned to this fund</p>
          </div>
        )}
      </div>

      {/* Period Information */}
      <div className="period-info">
        <p>📅 Analysis Period: Last {period} days</p>
      </div>
    </div>
  );
}
