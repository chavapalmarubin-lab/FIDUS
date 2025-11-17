import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import './InvestmentCommittee.css';

const MANAGERS = [
  'aleflorextrader',
  'UNO14',
  'Provider1-Assev JC',
  'CP Strategy',
  'TradingHub Gold',
  'Golden Trade Norman',
  'BOT',
  'Spaniard Equity CFDs',
  'JOSE - LUCRUM',
  'JARED'
];

function ManagerDropZone({ manager, accounts, onRemoveAccount }) {
  const { setNodeRef, isOver } = useDroppable({
    id: `manager-${manager}`,
    data: { 
      type: 'manager', 
      manager 
    }
  });

  const totalBalance = accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0);

  return (
    <div
      ref={setNodeRef}
      className={`manager-drop-zone ${isOver ? 'drag-over' : ''} ${accounts.length > 0 ? 'has-accounts' : ''}`}
    >
      <div className="drop-zone-header">
        <h4>📊 {manager}</h4>
        {accounts.length > 0 && (
          <span className="account-count-badge">{accounts.length}</span>
        )}
      </div>
      
      <div className="assigned-accounts">
        {accounts.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">👇</span>
            <p>Drop MT5 accounts here</p>
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
                  onClick={() => onRemoveAccount(account, manager, 'manager')}
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
        <div className="manager-total">
          <strong>Total Allocated:</strong>
          <span>${totalBalance.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          })}</span>
        </div>
      )}
    </div>
  );
}

export default function ManagerDropZones({ allocations, onRemoveAccount }) {
  return (
    <div className="manager-drop-zones">
      <div className="section-header">
        <h3>MONEY MANAGERS</h3>
        <p className="subtitle">(10 Active Managers)</p>
      </div>
      
      <div className="managers-grid">
        {MANAGERS.map(manager => (
          <ManagerDropZone
            key={manager}
            manager={manager}
            accounts={allocations[manager] || []}
            onRemoveAccount={onRemoveAccount}
          />
        ))}
      </div>
    </div>
  );
}
