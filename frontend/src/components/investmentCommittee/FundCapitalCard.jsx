import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { DollarSign, Plus } from 'lucide-react';

export default function FundCapitalCard({ 
  fundType, 
  totalCapital, 
  allocatedCapital, 
  unallocatedCapital,
  onAddCapital
}) {
  const allocatedPercent = totalCapital > 0 ? (allocatedCapital / totalCapital) * 100 : 0;
  const unallocatedPercent = totalCapital > 0 ? (unallocatedCapital / totalCapital) * 100 : 0;

  return (
    <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="text-2xl text-white">{fundType} Fund</span>
          <Button 
            onClick={onAddCapital}
            size="sm"
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            <Plus size={16} className="mr-2" />
            Adjust Capital
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Total Capital */}
        <div className="text-center">
          <div className="text-sm text-slate-400 mb-1">Total Capital</div>
          <div className="text-4xl font-bold text-white">
            ${totalCapital.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="h-8 bg-slate-700 rounded-full overflow-hidden flex">
            {allocatedPercent > 0 && (
              <div 
                className="bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center text-xs font-semibold text-white"
                style={{ width: `${allocatedPercent}%` }}
              >
                {allocatedPercent > 10 && `${allocatedPercent.toFixed(1)}%`}
              </div>
            )}
            {unallocatedPercent > 0 && (
              <div 
                className="bg-gradient-to-r from-gray-600 to-gray-700 flex items-center justify-center text-xs font-semibold text-white"
                style={{ width: `${unallocatedPercent}%` }}
              >
                {unallocatedPercent > 10 && `${unallocatedPercent.toFixed(1)}%`}
              </div>
            )}
          </div>
        </div>

        {/* Breakdown */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-900/20 rounded-lg p-4 border border-blue-500/30">
            <div className="text-sm text-blue-300 mb-1">Allocated</div>
            <div className="text-2xl font-bold text-blue-100">
              ${allocatedCapital.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-blue-400 mt-1">
              {allocatedPercent.toFixed(1)}%
            </div>
          </div>
          
          <div className="bg-gray-900/20 rounded-lg p-4 border border-gray-500/30">
            <div className="text-sm text-gray-300 mb-1">Unallocated</div>
            <div className="text-2xl font-bold text-gray-100">
              ${unallocatedCapital.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {unallocatedPercent.toFixed(1)}%
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}