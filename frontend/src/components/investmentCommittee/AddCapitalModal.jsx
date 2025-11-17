import React, { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';

export default function AddCapitalModal({
  isOpen,
  onClose,
  fundState,
  onSubmit
}) {
  const [newTotal, setNewTotal] = useState(fundState?.totalCapital || 0);
  const [reason, setReason] = useState('add_capital');
  const [notes, setNotes] = useState('');
  const [errors, setErrors] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen || !fundState) return null;

  const capitalChange = newTotal - fundState.totalCapital;
  const isIncrease = capitalChange > 0;
  const isDecrease = capitalChange < 0;

  const validate = () => {
    const errs = [];

    if (newTotal < fundState.allocatedCapital) {
      errs.push(`New total ($${newTotal.toLocaleString()}) cannot be less than allocated capital ($${fundState.allocatedCapital.toLocaleString()})`);
    }

    if (capitalChange === 0) {
      errs.push('New total must be different from current total');
    }

    setErrors(errs);
    return errs.length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setSubmitting(true);
    const result = await onSubmit({
      newTotalCapital: newTotal,
      reason: reason,
      notes: notes
    });

    setSubmitting(false);

    if (result.success) {
      onClose();
    } else {
      setErrors([result.error || 'Failed to adjust capital']);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg shadow-xl max-w-xl w-full">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-slate-700">
          <h2 className="text-2xl font-bold text-white">Adjust Fund Capital</h2>
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

          {/* Current Total */}
          <div className="bg-slate-900 rounded-lg p-4">
            <div className="text-sm text-slate-400 mb-1">Current Total Capital</div>
            <div className="text-3xl font-bold text-white">
              ${fundState.totalCapital.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-sm text-slate-400 mt-2">
              Allocated: ${fundState.allocatedCapital.toLocaleString()} | 
              Unallocated: ${fundState.unallocatedCapital.toLocaleString()}
            </div>
          </div>

          {/* New Total Input */}
          <div className="space-y-2">
            <Label htmlFor="newTotal" className="text-white">New Total Capital</Label>
            <Input
              id="newTotal"
              type="number"
              value={newTotal}
              onChange={(e) => setNewTotal(parseFloat(e.target.value) || 0)}
              step={1000}
              className="bg-slate-700 border-slate-600 text-white text-xl font-semibold"
            />
          </div>

          {/* Reason */}
          <div className="space-y-2">
            <Label htmlFor="reason" className="text-white">Reason</Label>
            <select
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
            >
              <option value="add_capital">Add Capital</option>
              <option value="withdraw_capital">Withdraw Capital</option>
              <option value="absorb_loss">Absorb Loss</option>
              <option value="recognize_gain">Recognize Gain</option>
            </select>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes" className="text-white">Notes (Optional)</Label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Additional context for this adjustment..."
              rows={3}
              className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
            />
          </div>

          {/* Impact Preview */}
          {capitalChange !== 0 && (
            <div className={`rounded-lg p-4 border ${isIncrease ? 'bg-green-900/20 border-green-500/50' : 'bg-red-900/20 border-red-500/50'}`}>
              <h3 className="text-white font-semibold mb-3">Impact Preview</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-300">Total Capital Change:</span>
                  <span className={`font-bold ${isIncrease ? 'text-green-400' : 'text-red-400'}`}>
                    {isIncrease && '+'}
                    ${Math.abs(capitalChange).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-300">Unallocated Before:</span>
                  <span className="text-white">${fundState.unallocatedCapital.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-300">Unallocated After:</span>
                  <span className="text-white font-semibold">
                    ${(fundState.unallocatedCapital + capitalChange).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            </div>
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
            disabled={submitting || capitalChange === 0}
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            {submitting ? 'Adjusting...' : `Adjust to $${newTotal.toLocaleString()}`}
          </Button>
        </div>
      </div>
    </div>
  );
}