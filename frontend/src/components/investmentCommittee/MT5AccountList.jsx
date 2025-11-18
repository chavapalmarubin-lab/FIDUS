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
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  // Calculate totals
  const totalCapital = accounts?.reduce((sum, acc) => sum + (acc.balance || 0), 0) || 0;
  const unassignedCapital = accounts?.filter(acc => !acc.managerAssigned && !acc.fundType)
                                    .reduce((sum, acc) => sum + (acc.balance || 0), 0) || 0;
  const assignedCapital = totalCapital - unassignedCapital;

  // Filter and search accounts
  const filteredAccounts = useMemo(() => {
    let filtered = accounts || [];

    // Filter by assignment status
    if (filterType === 'unassigned') {
      filtered = filtered.filter(account => !account.managerAssigned && !account.fundType);
    } else if (filterType === 'assigned') {
      filtered = filtered.filter(account => account.managerAssigned || account.fundType);
    }

    // Search by account number, client name, or server
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(account => 
        account.account?.toString().includes(term) ||
        account.clientName?.toLowerCase().includes(term) ||
        account.server?.toLowerCase().includes(term)
      );
    }

    return filtered;
  }, [accounts, searchTerm, filterType]);

  const unassignedCount = accounts?.filter(acc => !acc.managerAssigned && !acc.fundType).length || 0;
  const assignedCount = accounts?.filter(acc => acc.managerAssigned || acc.fundType).length || 0;

  return (
    <div className="mt5-accounts-container">
      {/* Search Header */}
      <div className="accounts-header">
        <div className="accounts-title">
          <h3>MT5 Accounts</h3>
          <div className="accounts-stats">
            <span className="stat-badge unassigned">{unassignedCount} Unassigned</span>
            <span className="stat-badge assigned">{assignedCount} Assigned</span>
          </div>
        </div>
        
        {/* Search Bar */}
        <div className="search-container">
          <div className="search-input-wrapper">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search by account number, client, or broker..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            {searchTerm && (
              <button 
                onClick={() => setSearchTerm('')}
                className="clear-search"
                title="Clear search"
              >
                ×
              </button>
            )}
          </div>
        </div>

        {/* Filter Buttons */}
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => setFilterType('all')}
          >
            All ({accounts?.length || 0})
          </button>
          <button 
            className={`filter-btn ${filterType === 'unassigned' ? 'active' : ''}`}
            onClick={() => setFilterType('unassigned')}
          >
            Unassigned ({unassignedCount})
          </button>
          <button 
            className={`filter-btn ${filterType === 'assigned' ? 'active' : ''}`}
            onClick={() => setFilterType('assigned')}
          >
            Assigned ({assignedCount})
          </button>
        </div>
      </div>

      {/* Scrollable Accounts List */}
      <div className="accounts-list-wrapper">
        {filteredAccounts.length === 0 ? (
          <div className="empty-accounts">
            {searchTerm ? (
              <>
                <span className="empty-icon">🔍</span>
                <p>No accounts found for "{searchTerm}"</p>
                <button onClick={() => setSearchTerm('')} className="clear-btn">
                  Clear search
                </button>
              </>
            ) : (
              <>
                <span className="empty-icon">📋</span>
                <p>No {filterType === 'all' ? '' : filterType} accounts available</p>
              </>
            )}
          </div>
        ) : (
          <div className="accounts-list">
            {filteredAccounts.map(account => (
              <MT5AccountCard key={account.account} account={account} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
