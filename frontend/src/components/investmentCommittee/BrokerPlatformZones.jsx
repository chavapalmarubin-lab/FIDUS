import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import './InvestmentCommittee.css';

const BROKERS = ['MEXAtlantic', 'LUCRUM'];
const PLATFORMS = ['Broker Platform', 'Biking'];

function DropZone({ id, label, icon, accounts, onRemoveAccount, assignmentType }) {
  const { setNodeRef, isOver } = useDroppable({
    id: `${assignmentType}-${id}`,
    data: { 
      type: assignmentType, 
      value: id 
    }
  });

  return (
    <div
      ref={setNodeRef}
      className={`broker-platform-zone ${isOver ? 'drag-over' : ''} ${accounts.length > 0 ? 'has-accounts' : ''}`}
    >
      <div className="drop-zone-header">
        <h4>{icon} {label}</h4>
        {accounts.length > 0 && (
          <span className="account-count-badge">{accounts.length}</span>
        )}
      </div>
      
      <div className="assigned-accounts-compact">
        {accounts.length === 0 ? (
          <div className="empty-state-small">
            <p>Drop here</p>
          </div>
        ) : (
          <div className="account-chips">
            {accounts.map(account => (
              <div key={account} className="account-chip">
                <span>🏦 {account}</span>
                <button 
                  className="remove-btn-small"
                  onClick={() => onRemoveAccount(account, id, assignmentType)}
                  title="Remove"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function BrokerPlatformZones({ brokerAllocations, platformAllocations, onRemoveAccount }) {
  return (
    <div className="broker-platform-zones">
      <div className="brokers-section">
        <div className="section-header">
          <h3>BROKERS</h3>
          <p className="subtitle">(2 Brokers)</p>
        </div>
        
        <div className="broker-platform-grid">
          {BROKERS.map(broker => (
            <DropZone
              key={broker}
              id={broker}
              label={broker}
              icon="🏛️"
              accounts={brokerAllocations[broker] || []}
              onRemoveAccount={onRemoveAccount}
              assignmentType="broker"
            />
          ))}
        </div>
      </div>
      
      <div className="platforms-section">
        <div className="section-header">
          <h3>TRADING PLATFORMS</h3>
          <p className="subtitle">(2 Platforms)</p>
        </div>
        
        <div className="broker-platform-grid">
          {PLATFORMS.map(platform => (
            <DropZone
              key={platform}
              id={platform}
              label={platform}
              icon="🖥️"
              accounts={platformAllocations[platform] || []}
              onRemoveAccount={onRemoveAccount}
              assignmentType="platform"
            />
          ))}
        </div>
      </div>
    </div>
  );
}
