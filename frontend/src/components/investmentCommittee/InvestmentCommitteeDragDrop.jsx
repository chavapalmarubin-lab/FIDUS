import React, { useState, useEffect } from 'react';
import { DndContext } from '@dnd-kit/core';
import MT5AccountList from './MT5AccountList';
import ManagerDropZones from './ManagerDropZones';
import FundDropZones from './FundDropZones';
import FundTypesRow from './FundTypesRow';
import BrokerPlatformZones from './BrokerPlatformZones';
import ReassignmentDialog from './ReassignmentDialog';
import { getAuthHeaders } from '../../utils/auth';
import './InvestmentCommittee.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Define fund types mapping - MUST MATCH BACKEND EXACTLY
const FUND_TYPE_NAMES = {
  'SEPARATION': 'SEPARATION INTEREST',
  'REBATES': 'REBATES ACCOUNT', 
  'CORE': 'FIDUS CORE',
  'BALANCE': 'FIDUS BALANCE',
  'DYNAMIC': 'FIDUS DYNAMIC'
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

    console.log('Dragged:', draggedItem);
    console.log('Drop target:', dropTarget);

    // Extract account info
    const accountNumber = draggedItem.account;
    const accountData = accounts.find(acc => acc.account === accountNumber);
    
    if (!accountNumber || !accountData) {
      alert('Invalid account data');
      return;
    }

    // Check if this is a reassignment (account already has allocation of this type)
    let needsConfirmation = false;
    let currentAllocation = null;
    let newAllocation = null;

    if (dropTarget.type === 'fund' && accountData.fundType) {
      needsConfirmation = true;
      currentAllocation = FUND_TYPE_NAMES[accountData.fundType] || accountData.fundType;
      newAllocation = FUND_TYPE_NAMES[dropTarget.fundType] || dropTarget.fundType;
    } else if (dropTarget.type === 'manager' && accountData.manager_assigned) {
      needsConfirmation = true;
      currentAllocation = accountData.manager_assigned;
      newAllocation = dropTarget.managerName;
    }

    // If needs confirmation, show dialog
    if (needsConfirmation) {
      setPendingAssignment({
        accountNumber,
        type: dropTarget.type,
        value: dropTarget.type === 'fund' ? FUND_TYPE_NAMES[dropTarget.fundType] : dropTarget.managerName,
        currentAllocation,
        newAllocation
      });
      setShowReassignDialog(true);
    } else {
      // Direct assignment for new allocations
      if (dropTarget.type === 'manager') {
        await performAssignment(accountNumber, 'manager', dropTarget.managerName);
      } else if (dropTarget.type === 'fund') {
        await performAssignment(accountNumber, 'fund', FUND_TYPE_NAMES[dropTarget.fundType]);
      } else if (dropTarget.type === 'broker') {
        await performAssignment(accountNumber, 'broker', dropTarget.brokerName);
      } else if (dropTarget.type === 'platform') {
        await performAssignment(accountNumber, 'platform', dropTarget.platformName);
      }
    }
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
        setHasUnsavedChanges(true);
        await loadData();
      } else {
        alert('Assignment failed: ' + (result.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to assign account:', error);
      alert('Error: ' + error.message);
    }
  }

  // Handle reassignment dialog confirmation
  async function handleReassignConfirm() {
    if (!pendingAssignment) return;
    
    await performAssignment(
      pendingAssignment.accountNumber,
      pendingAssignment.type,
      pendingAssignment.value
    );
    
    setShowReassignDialog(false);
    setPendingAssignment(null);
  }

  // Handle reassignment dialog cancellation
  function handleReassignCancel() {
    setShowReassignDialog(false);
    setPendingAssignment(null);
  }

  // Handle reassignment dialog confirmation
  async function handleReassignConfirm() {
    if (!pendingAssignment) return;
    
    await performAssignment(
      pendingAssignment.accountNumber,
      pendingAssignment.type,
      pendingAssignment.value
    );
    
    setShowReassignDialog(false);
    setPendingAssignment(null);
  }

  // Handle reassignment dialog cancellation
  function handleReassignCancel() {
    setShowReassignDialog(false);
    setPendingAssignment(null);
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
          <h1>Investment Committee - Fund Allocation</h1>
          <p className="page-description">
            Assign MT5 accounts to fund types and managers by dragging and dropping
          </p>
          <div className="header-actions">
            <button onClick={loadData} className="refresh-btn">
              🔄 Refresh Data
            </button>
            {hasUnsavedChanges && (
              <button 
                onClick={() => setHasUnsavedChanges(false)} 
                className="apply-btn"
                title="Apply changes and recalculate fund portfolios"
              >
                ✅ Apply Changes
              </button>
            )}
          </div>
        </div>

        <div className="investment-committee-layout">
          {/* Top: Fund Types Row - 5 fund categories */}
          <FundTypesRow 
            allocations={fundAllocations}
            onRemoveAccount={handleRemoveAccount}
          />

          {/* Main Content */}
          <div className="main-content-row">
            {/* Left: MT5 Accounts List */}
            <div className="accounts-sidebar">
              <MT5AccountList accounts={accounts} />
            </div>

            {/* Right: Managers Section */}
            <div className="managers-section">
              <ManagerDropZones 
                allocations={managerAllocations}
                onRemoveAccount={handleRemoveAccount}
              />
            </div>
          </div>
        </div>

        {/* Reassignment Confirmation Dialog */}
        <ReassignmentDialog
          isOpen={showReassignDialog}
          accountNumber={pendingAssignment?.accountNumber}
          currentAllocation={pendingAssignment?.currentAllocation}
          newAllocation={pendingAssignment?.newAllocation}
          onConfirm={handleReassignConfirm}
          onCancel={handleReassignCancel}
        />
      </div>
    </DndContext>
  );
}
