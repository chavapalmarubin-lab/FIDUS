import React, { useState, useEffect } from 'react';
import { DndContext } from '@dnd-kit/core';
import MT5AccountList from './MT5AccountList';
import ManagerDropZones from './ManagerDropZones';
import FundDropZones from './FundDropZones';
import BrokerPlatformZones from './BrokerPlatformZones';
import ReassignmentDialog from './ReassignmentDialog';
import { getAuthHeaders } from '../../utils/auth';
import './InvestmentCommittee.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Define fund types mapping
const FUND_TYPE_NAMES = {
  'SEPARATION': 'Separation Account',
  'REBATES': 'Rebate Account', 
  'CORE': 'FIDUS Core',
  'BALANCE': 'FIDUS Balance',
  'DYNAMIC': 'FIDUS Dynamic'
};

export default function InvestmentCommitteeDragDrop() {
  const [accounts, setAccounts] = useState([]);
  const [managerAllocations, setManagerAllocations] = useState({});
  const [fundAllocations, setFundAllocations] = useState({});
  const [brokerAllocations, setBrokerAllocations] = useState({});
  const [platformAllocations, setPlatformAllocations] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // Confirmation dialog state
  const [showReassignDialog, setShowReassignDialog] = useState(false);
  const [pendingAssignment, setPendingAssignment] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);

      // Debug logging
      console.log('🔍 Investment Committee - API_BASE_URL:', API_BASE_URL);
      console.log('🔍 Investment Committee - Full URL:', `${API_BASE_URL}/api/admin/investment-committee/mt5-accounts`);

      // Fetch all accounts
      const accountsRes = await fetch(
        `${API_BASE_URL}/api/admin/investment-committee/mt5-accounts`,
        { headers: getAuthHeaders() }
      );

      if (!accountsRes.ok) {
        throw new Error(`Failed to fetch accounts: ${accountsRes.statusText}`);
      }

      const accountsData = await accountsRes.json();
      
      if (accountsData.success && accountsData.data) {
        setAccounts(accountsData.data.accounts || []);
      }

      // Fetch allocations
      const allocRes = await fetch(
        `${API_BASE_URL}/api/admin/investment-committee/allocations`,
        { headers: getAuthHeaders() }
      );

      if (!allocRes.ok) {
        throw new Error(`Failed to fetch allocations: ${allocRes.statusText}`);
      }

      const allocData = await allocRes.json();
      
      if (allocData.success && allocData.data) {
        // Process managers
        const managers = {};
        Object.keys(allocData.data.managers || {}).forEach(managerName => {
          managers[managerName] = allocData.data.managers[managerName].accounts || [];
        });
        setManagerAllocations(managers);

        // Process funds
        const funds = {};
        Object.keys(allocData.data.funds || {}).forEach(fundName => {
          funds[fundName] = allocData.data.funds[fundName].accounts || [];
        });
        setFundAllocations(funds);

        // Process brokers
        const brokers = {};
        Object.keys(allocData.data.brokers || {}).forEach(brokerName => {
          brokers[brokerName] = allocData.data.brokers[brokerName].accounts || [];
        });
        setBrokerAllocations(brokers);

        // Process platforms
        const platforms = {};
        Object.keys(allocData.data.platforms || {}).forEach(platformName => {
          platforms[platformName] = allocData.data.platforms[platformName].accounts || [];
        });
        setPlatformAllocations(platforms);
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to load data:', error);
      setError(error.message);
      setLoading(false);
    }
  }

  async function handleDragEnd(event) {
    const { active, over } = event;
    
    if (!over) return;

    const draggedItem = active.data.current;
    const dropTarget = over.data.current;

    if (!draggedItem || !dropTarget) return;

    // Confirm with user
    const account = draggedItem.account;
    let confirmMessage = '';
    let assignmentType = '';
    let assignmentValue = '';

    if (dropTarget.type === 'manager') {
      assignmentType = 'manager';
      assignmentValue = dropTarget.manager;
      confirmMessage = `Assign account ${account.account} to manager "${dropTarget.manager}"?`;
    } else if (dropTarget.type === 'fund') {
      assignmentType = 'fund';
      assignmentValue = dropTarget.fund;
      confirmMessage = `Assign account ${account.account} to fund "${dropTarget.fund}"?`;
    } else if (dropTarget.type === 'broker') {
      assignmentType = 'broker';
      assignmentValue = dropTarget.value;
      confirmMessage = `Assign account ${account.account} to broker "${dropTarget.value}"?`;
    } else if (dropTarget.type === 'platform') {
      assignmentType = 'platform';
      assignmentValue = dropTarget.value;
      confirmMessage = `Assign account ${account.account} to platform "${dropTarget.value}"?`;
    }

    if (!window.confirm(confirmMessage)) {
      return;
    }

    await performAssignment(account.account, assignmentType, assignmentValue);
  }

  async function performAssignment(accountNumber, assignmentType, assignmentValue) {
    try {
      let endpoint = '';
      let payload = { account_number: accountNumber };

      if (assignmentType === 'manager') {
        endpoint = '/api/admin/investment-committee/assign-to-manager';
        payload.manager_name = assignmentValue;
      } else if (assignmentType === 'fund') {
        endpoint = '/api/admin/investment-committee/assign-to-fund';
        payload.fund_type = assignmentValue;
      } else if (assignmentType === 'broker') {
        endpoint = '/api/admin/investment-committee/assign-to-broker';
        payload.broker = assignmentValue;
      } else if (assignmentType === 'platform') {
        endpoint = '/api/admin/investment-committee/assign-to-platform';
        payload.trading_platform = assignmentValue;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Assignment failed');
      }

      const result = await response.json();
      
      if (result.success) {
        // Reload data to reflect changes
        await loadData();
      } else {
        alert('Assignment failed: ' + (result.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to assign account:', error);
      alert('Error: ' + error.message);
    }
  }

  async function handleRemoveAccount(accountOrNumber, assignmentValue, assignmentType) {
    // Handle both account object and account number
    const accountNumber = typeof accountOrNumber === 'object' ? accountOrNumber.account : accountOrNumber;
    
    if (!window.confirm(`Remove account ${accountNumber} from ${assignmentValue}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/investment-committee/remove-assignment`,
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            account_number: accountNumber,
            assignment_type: assignmentType
          })
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Removal failed');
      }

      const result = await response.json();
      
      if (result.success) {
        // Reload data
        await loadData();
      } else {
        alert('Removal failed: ' + (result.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to remove account:', error);
      alert('Error: ' + error.message);
    }
  }

  if (loading) {
    return (
      <div className="investment-committee-loading">
        <div className="spinner"></div>
        <p>Loading Investment Committee...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="investment-committee-error">
        <h3>Error Loading Data</h3>
        <p>{error}</p>
        <button onClick={loadData} className="retry-btn">Retry</button>
      </div>
    );
  }

  function handleApplySuccess(result) {
    // Reload data after successful application
    loadData();
  }

  return (
    <DndContext onDragEnd={handleDragEnd}>
      <div className="investment-committee-container">
        <div className="page-header">
          <h1>Investment Committee - Drag & Drop Assignment</h1>
          <p className="page-description">
            Assign MT5 accounts to managers, funds, brokers, and platforms by dragging and dropping
          </p>
          <button onClick={loadData} className="refresh-btn">
            🔄 Refresh Data
          </button>
        </div>

        {/* Apply Allocations Button - TODO: Uncomment after Render redeploy */}
        {/* <ApplyAllocationsButton onSuccess={handleApplySuccess} /> */}

        <div className="investment-committee-layout">
          {/* Left Sidebar: MT5 Accounts */}
          <div className="left-sidebar">
            <MT5AccountList accounts={accounts} />
          </div>

          {/* Main Content Area */}
          <div className="main-content">
            {/* Top: Managers */}
            <div className="managers-section">
              <ManagerDropZones 
                allocations={managerAllocations}
                onRemoveAccount={handleRemoveAccount}
              />
            </div>

            {/* Bottom Row: Funds, Brokers, Platforms */}
            <div className="bottom-row">
              <div className="funds-column">
                <FundDropZones 
                  allocations={fundAllocations}
                  onRemoveAccount={handleRemoveAccount}
                />
              </div>
              
              <div className="broker-platform-column">
                <BrokerPlatformZones 
                  brokerAllocations={brokerAllocations}
                  platformAllocations={platformAllocations}
                  onRemoveAccount={handleRemoveAccount}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </DndContext>
  );
}
