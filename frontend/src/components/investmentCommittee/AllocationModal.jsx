import React, { useState, useEffect } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';

export default function AllocationModal({
  isOpen,
  onClose,
  manager,
  availableCapital,
  fundType,
  onSubmit
}) {
  const [amount, setAmount] = useState(0);
  const [distribution, setDistribution] = useState([]);
  const [notes, setNotes] = useState('');
  const [errors, setErrors] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (manager) {
      // If editing existing allocation
      if (manager.existingAllocation) {
        setAmount(manager.existingAllocation.allocatedAmount);
        setDistribution(manager.existingAllocation.accounts.map(acc => ({
          accountNumber: acc.accountNumber,
          amount: acc.amount,
          type: acc.type
        })));
      } else {
        // Auto-distribute across accounts for new allocation
        const accounts = manager.assignedAccounts || [];
        if (accounts.length > 0) {
          const perAccount = amount / accounts.length;
          setDistribution(accounts.map(accNum => ({
            accountNumber: accNum,
            amount: perAccount,
            type: 'master'
          })));
        }
      }
    }
  }, [manager]);

  useEffect(() => {
    // Auto-redistribute when amount changes
    if (distribution.length > 0) {
      const perAccount = amount / distribution.length;
      setDistribution(dist => dist.map(d => ({
        ...d,
        amount: perAccount
      })));
    }
  }, [amount]);

  const validate = () => {
    const errs = [];

    if (amount <= 0) {
      errs.push('Amount must be greater than 0');
    }

    if (amount > availableCapital + (manager?.existingAllocation?.allocatedAmount || 0)) {
      errs.push(`Insufficient capital. Available: $${availableCapital.toLocaleString()}`);
    }

    const totalDist = distribution.reduce((sum, d) => sum + d.amount, 0);
    if (Math.abs(totalDist - amount) > 0.01) {
      errs.push(`Account distribution ($${totalDist.toLocaleString()}) must equal total amount ($${amount.toLocaleString()})`);
    }

    setErrors(errs);
    return errs.length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setSubmitting(true);
    const result = await onSubmit({
      managerName: manager.name,
      amount: amount,
      accountDistribution: distribution,
      notes: notes
    });

    setSubmitting(false);

    if (result.success) {
      onClose();
    } else {
      setErrors([result.error || 'Failed to apply allocation']);
    }
  };

  if (!isOpen || !manager) return null;

  const existingAmount = manager.existingAllocation?.allocatedAmount || 0;
  const requiredCapital = amount - existingAmount;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-slate-700">
          <h2 className="text-2xl font-bold text-white">
            {existingAmount > 0 ? 'Edit' : 'Allocate to'} {manager.displayName || manager.name}
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

          {/* Amount Input */}
          <div className="space-y-2">
            <Label htmlFor="amount" className="text-white">Allocation Amount</Label>
            <Input
              id="amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
              step={1000}
              className="bg-slate-700 border-slate-600 text-white"
            />
            <div className="text-sm text-slate-400">
              Available: ${availableCapital.toLocaleString()}
              {existingAmount > 0 && (
                <span className="ml-2">
                  (Currently: ${existingAmount.toLocaleString()})
                </span>
              )}
            </div>
          </div>

          {/* Account Distribution */}
          <div className="space-y-2">
            <Label className="text-white">Account Distribution</Label>
            <div className="space-y-2">
              {distribution.map((dist, idx) => (
                <div key={idx} className="flex items-center gap-3 bg-slate-700 rounded p-3">
                  <span className="text-white flex-shrink-0 w-24">
                    Account {dist.accountNumber}
                  </span>
                  <Input
                    type="number"
                    value={dist.amount}
                    onChange={(e) => {
                      const newDist = [...distribution];
                      newDist[idx].amount = parseFloat(e.target.value) || 0;
                      setDistribution(newDist);
                    }}
                    className="bg-slate-600 border-slate-500 text-white"
                  />
                  <select
                    value={dist.type}
                    onChange={(e) => {
                      const newDist = [...distribution];
                      newDist[idx].type = e.target.value;
                      setDistribution(newDist);
                    }}
                    className="bg-slate-600 border-slate-500 text-white rounded px-2 py-1"
                  >
                    <option value="master">Master</option>
                    <option value="copy">Copy</option>
                    <option value="MAM">MAM</option>
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes" className="text-white">Notes (Optional)</Label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Reason for this allocation..."
              rows={3}
              className="w-full bg-slate-700 border-slate-600 text-white rounded px-3 py-2"
            />
          </div>

          {/* Impact Preview */}
          <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
            <h3 className="text-white font-semibold mb-3">Impact Preview</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Unallocated Before:</span>
                <span className="text-white font-medium">${availableCapital.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Unallocated After:</span>
                <span className="text-white font-medium">
                  ${(availableCapital - requiredCapital).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between border-t border-slate-700 pt-2">
                <span className="text-slate-400">Manager Allocation:</span>
                <span className="text-cyan-400 font-semibold">${amount.toLocaleString()}</span>
              </div>
            </div>
          </div>
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
            disabled={submitting}
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            {submitting ? 'Applying...' : `Allocate $${amount.toLocaleString()}`}
          </Button>
        </div>
      </div>
    </div>
  );
}