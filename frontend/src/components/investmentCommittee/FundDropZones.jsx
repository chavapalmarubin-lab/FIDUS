import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import './InvestmentCommittee.css';

const FUNDS = [
  'FIDUS CORE',
  'FIDUS BALANCE',
  'FIDUS DYNAMIC',
  'SEPARATION INTEREST',
  'REBATES ACCOUNT'
];

function FundDropZone({ fund, accounts, onRemoveAccount }) {
  const { setNodeRef, isOver } = useDroppable({
    id: `fund-${fund}`,
    data: { 
      type: 'fund', 
      fund 
    }
  });

  const totalBalance = accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);

  return (
    <div
      ref={setNodeRef}
      className={`fund-drop-zone ${isOver ? 'drag-over' : ''} ${accounts.length > 0 ? 'has-accounts' : ''}`}
    >
      <div className="drop-zone-header">
        <h4>💰 {fund}</h4>
        {accounts.length > 0 && (
          <span className="account-count-badge">{accounts.length}</span>
        )}
      </div>
      
      <div className="assigned-accounts">
        {accounts.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">👇</span>
            <p>Drop accounts here</p>
          </div>
        ) : (
          <div className="account-list">
            {accounts.map(account => (
              <div key={account.account} className="assigned-account-item">
                <div className="account-info">
                  <span className="account-num">🏦 {account.account}</span>
                  <span className="account-bal">
                    ${(account.balance || 0).toLocaleString('en-US', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2
                    })}
                  </span>
                </div>
                <button 
                  className="remove-btn"
                  onClick={() => onRemoveAccount(account, fund, 'fund')}
                  title="Remove assignment"
                >
                  ❌
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {accounts.length > 0 && (
        <div className="fund-total">
          <strong>Total:</strong>
          <span>${totalBalance.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          })}</span>
        </div>
      )}
    </div>
  );
}

export default function FundDropZones({ allocations, onRemoveAccount }) {
  return (
    <div className="fund-drop-zones">
      <div className="section-header">
        <h3>FUND CATEGORIES</h3>
        <p className="subtitle">(5 Fund Types)</p>
      </div>
      
      <div className="funds-grid">
        {FUNDS.map(fund => (
          <FundDropZone
            key={fund}
            fund={fund}
            accounts={allocations[fund] || []}
            onRemoveAccount={onRemoveAccount}
          />
        ))}
      </div>
    </div>
  );
}
