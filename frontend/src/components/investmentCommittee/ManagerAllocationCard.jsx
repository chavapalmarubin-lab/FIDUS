import React from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Edit, Trash2 } from 'lucide-react';

export default function ManagerAllocationCard({ 
  allocation,
  onEdit,
  onRemove
}) {
  if (!allocation) return null;
  
  const allocatedAmount = allocation.allocatedAmount || 0;
  const allocationPercentage = allocation.allocationPercentage || 0;
  const accounts = allocation.accounts || [];
  
  return (
    <Card className="bg-slate-800 border-slate-700 hover:border-cyan-500/50 transition-colors">
      <div className="p-4 space-y-3">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-white">{allocation.managerName}</h3>
            <div className="text-2xl font-bold text-cyan-400 mt-1">
              ${allocatedAmount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-slate-400 mt-1">
              {allocationPercentage.toFixed(1)}% of fund
            </div>
          </div>
        </div>

        {/* Account Breakdown */}
        <div className="space-y-1 border-t border-slate-700 pt-3">
          <div className="text-xs text-slate-400 mb-2">Accounts:</div>
          {accounts.map(account => (
            <div 
              key={account.accountNumber} 
              className="flex justify-between items-center text-sm bg-slate-900/50 rounded px-2 py-1"
            >
              <span className="text-slate-300">
                {account.accountNumber}
                <span className="text-slate-500 ml-2">({account.type})</span>
              </span>
              <span className="text-cyan-400 font-medium">
                ${(account.amount || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2 border-t border-slate-700">
          <Button 
            size="sm" 
            variant="outline"
            onClick={onEdit}
            className="flex-1 bg-slate-700 hover:bg-slate-600 border-slate-600"
          >
            <Edit size={14} className="mr-1" />
            Edit
          </Button>
          <Button 
            size="sm" 
            variant="outline"
            onClick={onRemove}
            className="flex-1 bg-red-900/20 hover:bg-red-900/30 border-red-500/30 text-red-400"
          >
            <Trash2 size={14} className="mr-1" />
            Remove
          </Button>
        </div>
      </div>
    </Card>
  );
}