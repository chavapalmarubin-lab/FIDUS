import React, { useState, useEffect } from 'react';
import { X, AlertTriangle, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function RemoveManagerModal({
  isOpen,
  onClose,
  allocation,
  fundType,
  onSubmit
}) {
  const [actualBalance, setActualBalance] = useState(0);
  const [lossHandling, setLossHandling] = useState('absorb_loss');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    if (allocation) {
      fetchActualBalance();
    }
  }, [allocation]);

  const fetchActualBalance = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/admin/investment-committee/managers/${encodeURIComponent(allocation.managerName)}/actual-balance`
      );
      const data = await response.json();
      if (data.success) {
        setActualBalance(data.data.actualBalance || allocation.allocatedAmount);
      } else {
        // Fallback to allocated amount if can't fetch actual
        setActualBalance(allocation.allocatedAmount);
      }
    } catch (error) {
      console.error('Error fetching actual balance:', error);
      setActualBalance(allocation.allocatedAmount);
    }
    setLoading(false);
  };

  if (!isOpen || !allocation) return null;

  const difference = actualBalance - allocation.allocatedAmount;
  const isLoss = difference < 0;
  const isGain = difference > 0;
  const lossAmount = Math.abs(difference);

  const handleSubmit = async () => {
    const errs = [];

    if (!notes.trim()) {
      errs.push('Please provide a reason for removal');
    }

    if (errs.length > 0) {
      setErrors(errs);
      return;
    }

    setSubmitting(true);
    const result = await onSubmit({
      managerName: allocation.managerName,
      expectedAllocation: allocation.allocatedAmount,
      actualBalance: actualBalance,
      lossHandling: lossHandling,
      notes: notes
    });

    setSubmitting(false);

    if (result.success) {
      onClose();
    } else {
      setErrors([result.error || 'Failed to remove manager']);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-slate-700">
          <h2 className="text-2xl font-bold text-white">
            Remove {allocation.managerName}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {errors.length > 0 && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {errors.map((err, i) => <div key={i}>{err}</div>)}
              </AlertDescription>
            </Alert>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-cyan-500" />
              <span className="ml-2 text-slate-300">Loading actual balance...</span>
            </div>
          ) : (
            <>
              {/* Balance Comparison */}
              <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Allocated Amount:</span>
                  <span className="text-white font-semibold">
                    ${allocation.allocatedAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Actual Balance:</span>
                  <span className="text-white font-semibold">
                    ${actualBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className={`flex justify-between items-center border-t border-slate-700 pt-3 ${
                  isLoss ? 'text-red-400' : isGain ? 'text-green-400' : 'text-slate-400'
                }`}>
                  <span className="font-semibold">
                    {isLoss ? 'Loss:' : isGain ? 'Gain:' : 'Difference:'}
                  </span>
                  <span className="text-xl font-bold">
                    {isLoss && '-'}
                    {isGain && '+'}
                    ${lossAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>

              {/* Loss Handling Options */}
              {isLoss && (
                <>
                  <Alert className="bg-yellow-900/20 border-yellow-500/50">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    <AlertDescription className="text-yellow-100">
                      ⚠️ This manager has a loss of ${lossAmount.toLocaleString()}. 
                      How should this loss be handled?
                    </AlertDescription>
                  </Alert>

                  <div className="space-y-3">
                    <Label className="text-white font-semibold">Loss Handling</Label>
                    
                    <label className="flex items-start space-x-3 p-3 bg-slate-700 rounded cursor-pointer hover:bg-slate-600">
                      <input
                        type="radio"
                        name="lossHandling"
                        value="absorb_loss"
                        checked={lossHandling === 'absorb_loss'}
                        onChange={(e) => setLossHandling(e.target.value)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="text-white font-medium">Absorb loss</div>
                        <div className="text-sm text-slate-400">
                          Reduce fund total capital by ${lossAmount.toLocaleString()}
                        </div>
                      </div>
                    </label>

                    <label className="flex items-start space-x-3 p-3 bg-slate-700 rounded cursor-pointer hover:bg-slate-600">
                      <input
                        type="radio"
                        name="lossHandling"
                        value="cover_from_reserves"
                        checked={lossHandling === 'cover_from_reserves'}
                        onChange={(e) => setLossHandling(e.target.value)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="text-white font-medium">Cover from reserves</div>
                        <div className="text-sm text-slate-400">
                          Keep fund total same, reduce reserves by ${lossAmount.toLocaleString()}
                        </div>
                      </div>
                    </label>

                    <label className="flex items-start space-x-3 p-3 bg-slate-700 rounded cursor-pointer hover:bg-slate-600">
                      <input
                        type="radio"
                        name="lossHandling"
                        value="mark_receivable"
                        checked={lossHandling === 'mark_receivable'}
                        onChange={(e) => setLossHandling(e.target.value)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="text-white font-medium">Mark as receivable</div>
                        <div className="text-sm text-slate-400">
                          Track loss as future recovery (not recommended)
                        </div>
                      </div>
                    </label>
                  </div>
                </>
              )}

              {/* Gain Message */}
              {isGain && (
                <Alert className="bg-green-900/20 border-green-500/50">
                  <AlertDescription className="text-green-100">
                    ✅ This manager has a gain of ${lossAmount.toLocaleString()}.
                    The gain will be added to the fund's unallocated capital.
                  </AlertDescription>
                </Alert>
              )}

              {/* Notes */}
              <div className="space-y-2">
                <Label htmlFor="notes" className="text-white">
                  Reason for Removal <span className="text-red-400">*</span>
                </Label>
                <textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Committee decision notes..."
                  rows={4}
                  required
                  className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
                />
              </div>

              {/* Impact Preview */}
              <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                <h3 className="text-white font-semibold mb-3">Impact Preview</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Capital to Return:</span>
                    <span className="text-white font-medium">
                      ${actualBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  {isLoss && lossHandling === 'absorb_loss' && (
                    <div className="flex justify-between text-red-400 border-t border-slate-700 pt-2">
                      <span className="font-medium">Fund Total Change:</span>
                      <span className="font-semibold">
                        -${lossAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  )}
                  {isGain && (
                    <div className="flex justify-between text-green-400 border-t border-slate-700 pt-2">
                      <span className="font-medium">Fund Total Change:</span>
                      <span className="font-semibold">
                        +${lossAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-slate-700">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={submitting}
            className="bg-slate-700 hover:bg-slate-600"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitting || !notes.trim() || loading}
            className="bg-red-600 hover:bg-red-700"
          >
            {submitting ? 'Removing...' : 'Remove Manager'}
          </Button>
        </div>
      </div>
    </div>
  );
}
