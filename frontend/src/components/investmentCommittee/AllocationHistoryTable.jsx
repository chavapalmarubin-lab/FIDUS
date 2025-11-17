import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '../ui/alert';
import { getAuthHeaders } from '../../utils/auth';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function AllocationHistoryTable({ fundType }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadHistory();
  }, [fundType]);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/investment-committee/funds/${fundType}/history?limit=10`
      );
      
      if (!response.ok) {
        throw new Error('Failed to load history');
      }
      
      const data = await response.json();
      if (data.success) {
        setHistory(data.data.history || []);
      }
    } catch (err) {
      console.error('Error loading history:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getActionBadge = (actionType) => {
    const badges = {
      'manager_added': { color: 'bg-green-900/20 text-green-400 border-green-500/30', icon: '➕' },
      'manager_removed': { color: 'bg-red-900/20 text-red-400 border-red-500/30', icon: '➖' },
      'allocation_increased': { color: 'bg-blue-900/20 text-blue-400 border-blue-500/30', icon: '⬆️' },
      'allocation_decreased': { color: 'bg-yellow-900/20 text-yellow-400 border-yellow-500/30', icon: '⬇️' },
      'add_capital': { color: 'bg-cyan-900/20 text-cyan-400 border-cyan-500/30', icon: '💰' },
      'absorb_loss': { color: 'bg-orange-900/20 text-orange-400 border-orange-500/30', icon: '📉' }
    };

    const badge = badges[actionType] || { color: 'bg-slate-700 text-slate-300', icon: '•' };
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${badge.color}`}>
        {badge.icon} {actionType.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  if (loading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8">
          <div className="flex items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-cyan-500 mr-2" />
            <span className="text-slate-300">Loading history...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Error loading history: {error}</AlertDescription>
      </Alert>
    );
  }

  if (history.length === 0) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8">
          <div className="text-center text-slate-400">
            No allocation history available.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Recent Changes</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {history.map((record, idx) => {
            const impact = record.financialImpact || {};
            const hasLoss = impact.lossAmount > 0;
            const hasGain = impact.gainAmount > 0;
            const hasAllocationChange = impact.allocationChange !== 0;

            return (
              <div 
                key={idx}
                className="bg-slate-900 rounded-lg p-4 border border-slate-700 hover:border-cyan-500/50 transition-colors"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getActionBadge(record.actionType)}
                      <span className="text-sm text-slate-400">{formatDate(record.timestamp)}</span>
                    </div>
                    <div className="text-white font-medium">
                      {record.affectedManager !== 'N/A' && (
                        <span className="text-cyan-400">{record.affectedManager}</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Financial Impact */}
                {(hasLoss || hasGain || hasAllocationChange) && (
                  <div className="grid grid-cols-3 gap-4 mt-3 pt-3 border-t border-slate-700">
                    {hasLoss && (
                      <div className="text-center">
                        <div className="text-xs text-red-400 mb-1">Loss</div>
                        <div className="text-red-400 font-semibold">
                          -${impact.lossAmount.toLocaleString()}
                        </div>
                      </div>
                    )}
                    {hasGain && (
                      <div className="text-center">
                        <div className="text-xs text-green-400 mb-1">Gain</div>
                        <div className="text-green-400 font-semibold">
                          +${impact.gainAmount.toLocaleString()}
                        </div>
                      </div>
                    )}
                    {hasAllocationChange && (
                      <div className="text-center">
                        <div className="text-xs text-slate-400 mb-1">Allocation</div>
                        <div className={`font-semibold ${
                          impact.allocationChange > 0 ? 'text-blue-400' : 'text-yellow-400'
                        }`}>
                          {impact.allocationChange > 0 && '+'}
                          ${Math.abs(impact.allocationChange).toLocaleString()}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Notes */}
                {record.notes && (
                  <div className="mt-3 text-sm text-slate-400 italic">
                    "{record.notes}"
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}