import React, { useState, useMemo } from 'react';
import { useDraggable } from '@dnd-kit/core';
import './InvestmentCommittee.css';

function MT5AccountCard({ account }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `account-${account.account}`,
    data: { 
      type: 'account', 
      account: account.account
    }
  });

  const style = {
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
    opacity: isDragging ? 0.5 : 1,
    cursor: 'grab'
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`mt5-account-card ${account.managerAssigned ? 'allocated' : 'available'}`}
    >
      <div className="account-header">
        <span className="account-icon">🏦</span>
        <span className="account-number">{account.account}</span>
      </div>
      
      <div className="account-balance">
        ${(account.balance || 0).toLocaleString('en-US', { 
          minimumFractionDigits: 2, 
          maximumFractionDigits: 2 
        })}
      </div>
      
      <div className="account-details">
        {account.clientName && (
          <div className="account-client">
            <small className="assignment-label">👤 {account.clientName}</small>
          </div>
        )}
        
        {account.server && (
          <div className="account-broker">
            <small className="assignment-label">🏢 {account.server}</small>
          </div>
        )}
        
        {account.managerAssigned && (
          <div className="account-assignment">
            <small className="assignment-label">📊 {account.managerAssigned}</small>
          </div>
        )}
        
        {account.fundType && (
          <div className="account-fund">
            <small className="assignment-label">💰 {account.fundType}</small>
          </div>
        )}
      </div>
      
      <div className="account-status">
        <span className={`status-badge ${account.managerAssigned ? 'assigned' : 'unassigned'}`}>
          {account.managerAssigned ? 'Assigned' : 'Available'}
        </span>
      </div>
    </div>
  );
}

export default function MT5AccountList({ accounts }) {
  // Separate unassigned and assigned accounts
  const unassignedAccounts = accounts.filter(acc => !acc.managerAssigned && !acc.fundType);
  const assignedAccounts = accounts.filter(acc => acc.managerAssigned || acc.fundType);
  
  return (
    <div className="mt5-account-list">
      {/* Unassigned Accounts Section */}
      {unassignedAccounts.length > 0 && (
        <>
          <div className="section-header unassigned-header">
            <h3>🆕 UNASSIGNED ACCOUNTS</h3>
            <p className="subtitle">({unassignedAccounts.length} awaiting assignment)</p>
          </div>
          
          <div className="account-grid unassigned-grid">
            {unassignedAccounts.map(account => (
              <MT5AccountCard key={account.account} account={account} />
            ))}
          </div>
          
          <div className="divider"></div>
        </>
      )}
      
      {/* Assigned Accounts Section */}
      <div className="section-header">
        <h3>MT5 ACCOUNTS</h3>
        <p className="subtitle">({assignedAccounts.length} assigned)</p>
      </div>
      
      <div className="account-grid">
        {assignedAccounts.map(account => (
          <MT5AccountCard key={account.account} account={account} />
        ))}
      </div>
      
      <div className="total-summary">
        <div className="summary-row">
          <strong>Total Accounts:</strong>
          <span>{accounts.length}</span>
        </div>
        <div className="summary-row">
          <strong>Unassigned:</strong>
          <span className="unassigned-count">{unassignedAccounts.length}</span>
        </div>
        <div className="summary-row">
          <strong>Total Capital:</strong>
          <span>
            ${accounts.reduce((sum, acc) => sum + (acc.balance || 0), 0).toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </span>
        </div>
      </div>
    </div>
  );
}
