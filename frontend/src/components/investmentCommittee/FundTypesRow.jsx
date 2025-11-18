import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import './FundTypesRow.css';

const FUND_TYPES = [
  { id: 'SEPARATION', name: 'Separation Account', color: '#FF6B35', backendValue: 'SEPARATION INTEREST' },
  { id: 'REBATES', name: 'Rebate Account', color: '#F7931E', backendValue: 'REBATES ACCOUNT' },
  { id: 'CORE', name: 'FIDUS Core', color: '#004E89', backendValue: 'FIDUS CORE' },
  { id: 'BALANCE', name: 'FIDUS Balance', color: '#1B998B', backendValue: 'FIDUS BALANCE' },
  { id: 'DYNAMIC', name: 'FIDUS Dynamic', color: '#C44569', backendValue: 'FIDUS DYNAMIC' }
];

function FundTypeZone({ fundType, accounts, onRemoveAccount }) {
  const { setNodeRef, isOver } = useDroppable({
    id: `fund-${fundType.id}`,
    data: {
      type: 'fund',
      fundType: fundType.id
    }
  });

  const totalBalance = accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);

  return (
    <div 
      ref={setNodeRef}
      className={`fund-type-zone ${isOver ? 'drag-over' : ''}`}
      style={{ borderColor: fundType.color }}
    >
      <div className="fund-type-header" style={{ background: fundType.color }}>
        <h3>{fundType.name}</h3>
        <span className="fund-type-count">{accounts.length} accounts</span>
      </div>
      
      <div className="fund-type-content">
        {accounts.length === 0 ? (
          <div className="empty-state">
            <span className="drop-icon">👇</span>
            <p>Drop accounts here</p>
          </div>
        ) : (
          <div className="accounts-list">
            {accounts.map(account => (
              <div key={account.account} className="account-card-mini">
                <div className="account-info">
                  <span className="account-number">#{account.account}</span>
                  <span className="account-balance">${account.balance?.toLocaleString()}</span>
                </div>
                <button
                  className="remove-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveAccount(account, fundType.id, 'fund');
                  }}
                  title="Remove from fund"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
        
        {accounts.length > 0 && (
          <div className="fund-type-footer">
            <span>Total: ${totalBalance.toLocaleString()}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function FundTypesRow({ allocations, onRemoveAccount }) {
  return (
    <div className="fund-types-row">
      <h2 className="section-title">Fund Allocations</h2>
      <div className="fund-types-grid">
        {FUND_TYPES.map(fundType => (
          <FundTypeZone
            key={fundType.id}
            fundType={fundType}
            accounts={allocations[fundType.id] || []}
            onRemoveAccount={onRemoveAccount}
          />
        ))}
      </div>
    </div>
  );
}
