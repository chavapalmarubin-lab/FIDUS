import React, { useState } from 'react';
import './ApplyAllocationsDialog.css';

export default function ApplyAllocationsDialog({ 
  isOpen, 
  allocations, 
  totalCapital,
  onConfirm, 
  onCancel 
}) {
  const [isApplying, setIsApplying] = useState(false);

  if (!isOpen) return null;

  // Calculate fund totals
  const fundTotals = {};
  let totalAllocated = 0;

  // Process fund allocations
  Object.entries(allocations || {}).forEach(([fundType, accounts]) => {
    const total = accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);
    fundTotals[fundType] = total;
    totalAllocated += total;
  });

  const isFullyAllocated = Math.abs(totalAllocated - totalCapital) < 0.01;
  const allocationPercentage = totalCapital > 0 ? (totalAllocated / totalCapital) * 100 : 0;

  const handleConfirm = async () => {
    setIsApplying(true);
    try {
      await onConfirm();
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <div className="dialog-overlay" onClick={onCancel}>
      <div className="allocation-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-header">
          <h2>🎯 Apply Fund Allocations</h2>
          <p className="dialog-subtitle">
            Review and confirm the allocation of MT5 accounts to fund types
          </p>
        </div>

        {/* Allocation Summary */}
        <div className="allocation-overview">
          <div className="overview-header">
            <h3>Allocation Overview</h3>
            <div className={`allocation-status ${isFullyAllocated ? 'complete' : 'incomplete'}`}>
              {isFullyAllocated ? '✅ Fully Allocated' : '⚠️ Partial Allocation'}
            </div>
          </div>

          <div className="total-summary">
            <div className="summary-row">
              <span>Total Capital:</span>
              <span className="amount">${totalCapital.toLocaleString()}</span>
            </div>
            <div className="summary-row">
              <span>Allocated:</span>
              <span className="amount allocated">${totalAllocated.toLocaleString()}</span>
            </div>
            <div className="summary-row">
              <span>Remaining:</span>
              <span className={`amount ${totalCapital - totalAllocated > 0 ? 'remaining' : 'complete'}`}>
                ${Math.max(0, totalCapital - totalAllocated).toLocaleString()}
              </span>
            </div>
          </div>

          <div className="progress-section">
            <div className="progress-label">
              Allocation Progress: {allocationPercentage.toFixed(1)}%
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${Math.min(100, allocationPercentage)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Fund Breakdown */}
        <div className="fund-breakdown">
          <h3>Fund Allocation Breakdown</h3>
          <div className="fund-grid">
            {Object.entries(fundTotals).map(([fundType, amount]) => (
              <div key={fundType} className="fund-item">
                <div className="fund-header">
                  <span className="fund-name">{fundType}</span>
                  <span className="fund-amount">${amount.toLocaleString()}</span>
                </div>
                <div className="fund-percentage">
                  {totalCapital > 0 ? ((amount / totalCapital) * 100).toFixed(1) : 0}% of total
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Warning for incomplete allocation */}
        {!isFullyAllocated && (
          <div className="allocation-warning">
            <div className="warning-icon">⚠️</div>
            <div className="warning-content">
              <strong>Incomplete Allocation</strong>
              <p>
                ${(totalCapital - totalAllocated).toLocaleString()} remains unallocated. 
                You can still proceed, but consider allocating all capital for optimal fund management.
              </p>
            </div>
          </div>
        )}

        {/* System Impact Notice */}
        <div className="system-impact">
          <h4>📊 System Updates</h4>
          <p>Applying these allocations will trigger updates across:</p>
          <ul>
            <li>Fund Portfolio Dashboard</li>
            <li>Cash Flow Analysis</li>
            <li>Performance Metrics</li>
            <li>Risk Management Reports</li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="dialog-actions">
          <button 
            className="btn-cancel" 
            onClick={onCancel}
            disabled={isApplying}
          >
            Cancel
          </button>
          <button 
            className="btn-apply" 
            onClick={handleConfirm}
            disabled={isApplying}
          >
            {isApplying ? (
              <>
                <span className="spinner"></span>
                Applying Changes...
              </>
            ) : (
              <>
                ✅ Apply Allocations
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}