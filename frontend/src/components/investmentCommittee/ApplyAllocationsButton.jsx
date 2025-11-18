import React, { useState, useEffect } from 'react';
import './ApplyAllocations.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return token ? { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  } : {
    'Content-Type': 'application/json'
  };
}

export default function ApplyAllocationsButton({ onSuccess }) {
  const [validation, setValidation] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [progress, setProgress] = useState(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  
  // Validate allocations on mount and periodically
  useEffect(() => {
    validateAllocations();
    
    // Re-validate every 3 seconds while on page
    const interval = setInterval(validateAllocations, 3000);
    return () => clearInterval(interval);
  }, []);
  
  async function validateAllocations() {
    try {
      setIsValidating(true);
      
      const response = await fetch(
        `${API_BASE_URL}/api/admin/investment-committee/validate-allocations`,
        { headers: getAuthHeaders() }
      );
      
      if (!response.ok) {
        throw new Error('Validation failed');
      }
      
      const data = await response.json();
      setValidation(data);
    } catch (error) {
      console.error('Validation error:', error);
      setValidation({
        canApply: false,
        reason: 'Validation service unavailable',
        unassignedAccounts: [],
        incompleteAccounts: [],
        pendingChanges: []
      });
    } finally {
      setIsValidating(false);
    }
  }
  
  function handleApplyClick() {
    if (!validation || !validation.canApply) {
      return;
    }
    
    // Show confirmation dialog
    setShowConfirmDialog(true);
  }
  
  function handleCancelConfirm() {
    setShowConfirmDialog(false);
  }
  
  async function handleConfirmApply() {
    setShowConfirmDialog(false);
    setIsApplying(true);
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/investment-committee/apply-allocations`,
        {
          method: 'POST',
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to apply allocations');
      }
      
      const result = await response.json();
      
      // Show success message
      alert(
        `✅ Allocations Applied Successfully!\n\n` +
        `• ${result.accounts_updated} accounts allocated\n` +
        `• ${result.calculations_run} calculations completed\n` +
        `• All dashboards updated`
      );
      
      // Call success callback
      if (onSuccess) {
        onSuccess(result);
      }
      
      // Refresh validation
      await validateAllocations();
      
    } catch (error) {
      console.error('Apply error:', error);
      alert(`❌ Error applying allocations:\n\n${error.message}`);
    } finally {
      setIsApplying(false);
      setProgress(null);
    }
  }
  
  // Render loading state
  if (isValidating && !validation) {
    return (
      <div className="apply-allocations-container">
        <button className="btn-apply-loading" disabled>
          ⏳ Validating...
        </button>
      </div>
    );
  }
  
  // Render disabled state (validation failed)
  if (!validation || !validation.canApply) {
    const reason = validation?.reason || 'Validation in progress';
    const unassignedCount = validation?.unassignedAccounts?.length || 0;
    const incompleteCount = validation?.incompleteAccounts?.length || 0;
    
    return (
      <div className="apply-allocations-container">
        <div className="validation-warnings">
          {unassignedCount > 0 && (
            <div className="warning-badge unassigned">
              ⚠️ {unassignedCount} unassigned account{unassignedCount > 1 ? 's' : ''}
            </div>
          )}
          {incompleteCount > 0 && (
            <div className="warning-badge incomplete">
              ⚠️ {incompleteCount} incomplete allocation{incompleteCount > 1 ? 's' : ''}
            </div>
          )}
        </div>
        
        <button 
          className="btn-apply-disabled"
          disabled
          title={reason}
        >
          ❌ APPLY ALLOCATIONS
        </button>
        
        <p className="error-text">{reason}</p>
        
        {validation?.incompleteAccounts && validation.incompleteAccounts.length > 0 && (
          <div className="incomplete-details">
            <p className="details-header">Incomplete Accounts:</p>
            <ul>
              {validation.incompleteAccounts.map((acc) => (
                <li key={acc.account}>
                  Account {acc.account}: Missing {acc.missing.join(', ')}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }
  
  // Render enabled state (validation passed)
  const pendingCount = validation.pendingChanges?.length || 0;
  
  return (
    <>
      <div className="apply-allocations-container">
        <div className="validation-success">
          ✅ All accounts fully allocated
        </div>
        
        <button 
          className="btn-apply-enabled"
          onClick={handleApplyClick}
          disabled={isApplying}
        >
          {isApplying ? '⏳ APPLYING...' : '✅ APPLY ALLOCATIONS'}
        </button>
        
        {pendingCount > 0 && (
          <p className="pending-count">
            {pendingCount} pending change{pendingCount > 1 ? 's' : ''}
          </p>
        )}
        
        {isApplying && progress && (
          <div className="progress-indicator">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress.percent}%` }}
              />
            </div>
            <span className="progress-text">{progress.step}</span>
          </div>
        )}
      </div>
      
      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="confirmation-overlay" onClick={handleCancelConfirm}>
          <div className="confirmation-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="dialog-header">
              <h3>⚠️ Confirm Allocation Changes</h3>
            </div>
            
            <div className="dialog-body">
              <p>You are about to apply these changes:</p>
              
              <div className="changes-summary">
                <div className="summary-item">
                  📦 <strong>{pendingCount}</strong> account{pendingCount > 1 ? 's' : ''} will be allocated
                </div>
              </div>
              
              <p className="recalculations-header">System will recalculate:</p>
              <ul className="recalculations-list">
                <li>Cash flow projections</li>
                <li>Commission calculations</li>
                <li>Performance metrics</li>
                <li>P&L updates</li>
                <li>Manager assignments</li>
                <li>Fund distributions</li>
              </ul>
              
              <div className="warning-box">
                ⚠️ This action will update the system. Changes will be logged.
              </div>
            </div>
            
            <div className="dialog-footer">
              <button 
                className="btn-cancel" 
                onClick={handleCancelConfirm}
              >
                Cancel
              </button>
              <button 
                className="btn-confirm" 
                onClick={handleConfirmApply}
              >
                Apply Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
