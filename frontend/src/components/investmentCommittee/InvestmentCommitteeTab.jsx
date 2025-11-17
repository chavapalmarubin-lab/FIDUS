import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { Card } from '../ui/card';
import { Loader2 } from 'lucide-react';
import FundCapitalCard from './FundCapitalCard';
import ManagerAllocationCard from './ManagerAllocationCard';
import AllocationModal from './AllocationModal';
import RemoveManagerModal from './RemoveManagerModal';
import AddCapitalModal from './AddCapitalModal';
import AllocationHistoryTable from './AllocationHistoryTable';
import { getAuthHeaders } from '../../utils/auth';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function InvestmentCommitteeTab() {
  const [selectedFund, setSelectedFund] = useState('BALANCE');
  const [fundState, setFundState] = useState(null);
  const [availableManagers, setAvailableManagers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Modal states
  const [showAllocationModal, setShowAllocationModal] = useState(false);
  const [showRemoveModal, setShowRemoveModal] = useState(false);
  const [showAddCapitalModal, setShowAddCapitalModal] = useState(false);
  const [selectedManager, setSelectedManager] = useState(null);
  const [selectedAllocation, setSelectedAllocation] = useState(null);

  useEffect(() => {
    loadFundState();
    loadAvailableManagers();
  }, [selectedFund]);

  const loadFundState = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/investment-committee/funds/${selectedFund}/allocation`,
        {
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to load fund state');
      }
      
      const data = await response.json();
      if (data.success) {
        setFundState(data.data);
      } else {
        throw new Error(data.error || 'Failed to load fund state');
      }
    } catch (err) {
      console.error('Error loading fund state:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableManagers = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/investment-committee/managers/available?fundType=${selectedFund}`,
        {
          headers: getAuthHeaders()
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to load managers');
      }
      
      const data = await response.json();
      if (data.success) {
        setAvailableManagers(data.data.managers || []);
      }
    } catch (err) {
      console.error('Error loading managers:', err);
    }
  };

  const handleAllocateToManager = (manager) => {
    setSelectedManager(manager);
    setShowAllocationModal(true);
  };

  const handleEditAllocation = (allocation) => {
    // Find the full manager object
    const manager = availableManagers.find(m => m.name === allocation.managerName);
    if (manager) {
      setSelectedManager({...manager, existingAllocation: allocation});
      setShowAllocationModal(true);
    }
  };

  const handleRemoveManager = (allocation) => {
    setSelectedAllocation(allocation);
    setShowRemoveModal(true);
  };

  const handleAllocationSubmit = async (allocationData) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/investment-committee/funds/${selectedFund}/allocate`,
        {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          },
          body: JSON.stringify(allocationData)
        }
      );
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        await loadFundState();
        await loadAvailableManagers();
        setShowAllocationModal(false);
        return { success: true };
      } else {
        return { success: false, error: data.error || 'Failed to apply allocation' };
      }
    } catch (err) {
      console.error('Error allocating:', err);
      return { success: false, error: err.message };
    }
  };

  const handleRemoveSubmit = async (removeData) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/investment-committee/funds/${selectedFund}/managers/${encodeURIComponent(removeData.managerName)}`,
        {
          method: 'DELETE',
          headers: { 
            'Content-Type': 'application/json',
            ...getAuthHeaders()
          },
          body: JSON.stringify(removeData)
        }
      );
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        await loadFundState();
        await loadAvailableManagers();
        setShowRemoveModal(false);
        return { success: true };
      } else {
        return { success: false, error: data.error || 'Failed to remove manager' };
      }
    } catch (err) {
      console.error('Error removing manager:', err);
      return { success: false, error: err.message };
    }
  };

  const handleAddCapitalSubmit = async (capitalData) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/investment-committee/funds/${selectedFund}/capital`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(capitalData)
        }
      );
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        await loadFundState();
        setShowAddCapitalModal(false);
        return { success: true };
      } else {
        return { success: false, error: data.error || 'Failed to adjust capital' };
      }
    } catch (err) {
      console.error('Error adjusting capital:', err);
      return { success: false, error: err.message };
    }
  };

  // Get unallocated managers
  const unallocatedManagers = availableManagers.filter(m => {
    if (m.status !== 'active') return false;
    if (!fundState) return false;
    return !fundState.managerAllocations.some(alloc => alloc.managerName === m.name);
  });

  if (loading && !fundState) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-cyan-500" />
        <span className="ml-2 text-slate-300">Loading Investment Committee...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-4">
        <AlertDescription>Error: {error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="investment-committee-tab p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Investment Committee - Allocation Manager</h1>
      </div>

      {/* Fund Selector */}
      <Tabs value={selectedFund} onValueChange={setSelectedFund} className="w-full">
        <TabsList className="bg-slate-800">
          <TabsTrigger value="BALANCE">BALANCE Fund</TabsTrigger>
          <TabsTrigger value="CORE">CORE Fund</TabsTrigger>
          <TabsTrigger value="DYNAMIC">DYNAMIC Fund</TabsTrigger>
          <TabsTrigger value="SEPARATION">SEPARATION Fund</TabsTrigger>
        </TabsList>
      </Tabs>

      {fundState && (
        <>
          {/* Capital Overview */}
          <FundCapitalCard
            fundType={fundState.fundType}
            totalCapital={fundState.totalCapital}
            allocatedCapital={fundState.allocatedCapital}
            unallocatedCapital={fundState.unallocatedCapital}
            onAddCapital={() => setShowAddCapitalModal(true)}
          />

          {/* Current Allocations */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-white">Current Allocations</h2>
            {fundState.managerAllocations.length === 0 ? (
              <Alert className="bg-slate-800 border-slate-700">
                <AlertDescription className="text-slate-300">
                  No managers currently allocated to this fund.
                </AlertDescription>
              </Alert>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {fundState.managerAllocations.map(allocation => (
                  <ManagerAllocationCard
                    key={allocation.managerName}
                    allocation={allocation}
                    onEdit={() => handleEditAllocation(allocation)}
                    onRemove={() => handleRemoveManager(allocation)}
                  />
                ))}
              </div>
            )}
          </section>

          {/* Available Capital Banner */}
          {fundState.unallocatedCapital > 0 && (
            <Alert className="bg-cyan-900/20 border-cyan-500/50">
              <AlertDescription className="text-cyan-100">
                💰 <strong>${fundState.unallocatedCapital.toLocaleString()}</strong> available to allocate
              </AlertDescription>
            </Alert>
          )}

          {/* Available Managers */}
          {unallocatedManagers.length > 0 && (
            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-white">Available Managers</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {unallocatedManagers.map(manager => (
                  <Card key={manager.name} className="bg-slate-800 border-slate-700">
                    <div className="p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-semibold text-white">{manager.displayName || manager.name}</h3>
                          <p className="text-sm text-slate-400">{manager.executionMethod}</p>
                        </div>
                        {manager.status === 'active' && (
                          <button
                            onClick={() => handleAllocateToManager(manager)}
                            className="px-3 py-1 bg-cyan-600 hover:bg-cyan-700 text-white rounded text-sm"
                          >
                            Allocate
                          </button>
                        )}
                        {manager.status === 'pending_activation' && (
                          <span className="px-2 py-1 bg-yellow-900/20 text-yellow-500 rounded text-xs">
                            Pending
                          </span>
                        )}
                      </div>
                      {manager.notes && (
                        <p className="text-xs text-slate-500">{manager.notes}</p>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </section>
          )}

          {/* Allocation History */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-white">Allocation History</h2>
            <AllocationHistoryTable fundType={selectedFund} />
          </section>
        </>
      )}

      {/* Modals */}
      {showAllocationModal && (
        <AllocationModal
          isOpen={showAllocationModal}
          onClose={() => {
            setShowAllocationModal(false);
            setSelectedManager(null);
          }}
          manager={selectedManager}
          availableCapital={fundState?.unallocatedCapital || 0}
          fundType={selectedFund}
          onSubmit={handleAllocationSubmit}
        />
      )}

      {showRemoveModal && (
        <RemoveManagerModal
          isOpen={showRemoveModal}
          onClose={() => {
            setShowRemoveModal(false);
            setSelectedAllocation(null);
          }}
          allocation={selectedAllocation}
          fundType={selectedFund}
          onSubmit={handleRemoveSubmit}
        />
      )}

      {showAddCapitalModal && (
        <AddCapitalModal
          isOpen={showAddCapitalModal}
          onClose={() => setShowAddCapitalModal(false)}
          fundState={fundState}
          onSubmit={handleAddCapitalSubmit}
        />
      )}
    </div>
  );
}