import React from 'react';
import './ReassignmentDialog.css';

export default function ReassignmentDialog({ 
  isOpen, 
  accountNumber, 
  currentAllocation, 
  newAllocation,
  onConfirm, 
  onCancel 
}) {
  if (!isOpen) return null;

  return (
    <div className="dialog-overlay" onClick={onCancel}>
      <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-header">
          <h3>⚠️ Reassign Account?</h3>
        </div>
        
        <div className="dialog-body">
          <p className="dialog-message">
            Account <strong>#{accountNumber}</strong> is currently allocated to:
          </p>
          
          <div className="allocation-change">
            <div className="allocation-box current">
              <span className="label">Current</span>
              <span className="value">{currentAllocation}</span>
            </div>
            
            <div className="arrow">→</div>
            
            <div className="allocation-box new">
              <span className="label">New</span>
              <span className="value">{newAllocation}</span>
            </div>
          </div>
          
          <p className="dialog-warning">
            Are you sure you want to change this allocation? This action will update the account's fund assignment.
          </p>
        </div>
        
        <div className="dialog-actions">
          <button className="btn-cancel" onClick={onCancel}>
            Cancel
          </button>
          <button className="btn-confirm" onClick={onConfirm}>
            Yes, Reassign
          </button>
        </div>
      </div>
    </div>
  );
}
