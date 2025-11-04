import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import referralService from '../../services/referralService';

const ApproveModal = ({ commission, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleApprove = async () => {
    try {
      setLoading(true);
      setError(null);
      await referralService.approveCommission(commission.id);
      onSuccess();
    } catch (err) {
      console.error('Failed to approve commission:', err);
      setError(err.response?.data?.message || 'Failed to approve commission. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Approve Commission Payment</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Commission Details */}
          <div className="bg-gray-50 p-4 rounded-lg space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Salesperson</span>
              <span className="font-medium">{commission.salesperson_name}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Client</span>
              <span className="font-medium">{commission.client_name}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Product</span>
              <Badge variant="outline">{commission.product_type?.replace('FIDUS_', '')}</Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Payment Number</span>
              <span className="font-medium">#{commission.payment_number}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Due Date</span>
              <span className="font-medium">{formatDate(commission.commission_due_date)}</span>
            </div>

            <div className="border-t pt-3 mt-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Client Interest</span>
                <span className="font-medium">{formatCurrency(commission.client_interest_amount)}</span>
              </div>
              <div className="flex items-center justify-between mt-2">
                <span className="text-sm text-gray-600">Commission (10%)</span>
                <span className="text-lg font-bold text-green-600">{formatCurrency(commission.commission_amount)}</span>
              </div>
            </div>
          </div>

          {/* Warning Message */}
          <Alert>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <AlertDescription>
              Approving this commission will change its status to "approved" and make it ready for payment processing.
            </AlertDescription>
          </Alert>

          {/* Error Message */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleApprove} disabled={loading}>
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Approving...
              </>
            ) : (
              'Approve Commission'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ApproveModal;