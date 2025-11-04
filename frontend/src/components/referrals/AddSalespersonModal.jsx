import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';

const AddSalespersonModal = ({ isOpen, onClose, onSave, editData = null }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    referral_code: '',
    wallet_address: '',
    wallet_type: 'crypto_wallet',
    notes: '',
    active: true
  });

  useEffect(() => {
    if (editData) {
      // Editing existing salesperson
      setFormData({
        name: editData.name || '',
        email: editData.email || '',
        phone: editData.phone || '',
        referral_code: editData.referral_code || '',
        wallet_address: editData.payment_info?.wallet_address || '',
        wallet_type: editData.payment_info?.wallet_type || 'crypto_wallet',
        notes: editData.notes || '',
        active: editData.active !== false
      });
    } else if (isOpen) {
      // Reset for new salesperson
      setFormData({
        name: '',
        email: '',
        phone: '',
        referral_code: '',
        wallet_address: '',
        wallet_type: 'crypto_wallet',
        notes: '',
        active: true
      });
    }
  }, [editData, isOpen]);

  const generateReferralCode = (name) => {
    // Generate code from name initials + year
    const year = new Date().getFullYear();
    const initials = name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
    
    return initials.length >= 2 ? `${initials}-${year}` : `SP-${year}`;
  };

  const handleNameChange = (name) => {
    setFormData(prev => ({ ...prev, name }));
    
    // Auto-generate code when name changes (only for new salespeople)
    if (!editData && name.trim()) {
      const code = generateReferralCode(name);
      setFormData(prev => ({ ...prev, referral_code: code }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.name || !formData.email || !formData.referral_code) {
      alert('Please fill in required fields (Name, Email, Referral Code)');
      return;
    }

    setLoading(true);
    
    try {
      await onSave({
        ...formData,
        payment_info: {
          wallet_address: formData.wallet_address,
          wallet_type: formData.wallet_type
        }
      });
      
      // Show success message
      const message = document.createElement('div');
      message.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      message.innerHTML = `
        <p class="font-semibold">${editData ? 'Salesperson updated!' : 'Salesperson added!'}</p>
        <p class="text-sm">${formData.name} is ready to start referring clients</p>
      `;
      document.body.appendChild(message);
      setTimeout(() => message.remove(), 3000);
      
      onClose();
    } catch (error) {
      alert('Failed to save salesperson: ' + error.message);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const isEditing = !!editData;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? 'Edit Salesperson' : 'Add New Salesperson'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h3 className="font-semibold text-sm text-gray-700">Basic Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">
                  Full Name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  placeholder="John Doe"
                  required
                />
              </div>

              <div>
                <Label htmlFor="email">
                  Email <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="john@example.com"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  placeholder="+1234567890"
                />
              </div>

              <div>
                <Label htmlFor="referral_code">
                  Referral Code <span className="text-red-500">*</span>
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="referral_code"
                    value={formData.referral_code}
                    onChange={(e) => setFormData({...formData, referral_code: e.target.value.toUpperCase()})}
                    placeholder="SP-2025"
                    className="font-mono"
                    required
                  />
                  {!isEditing && (
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => setFormData({...formData, referral_code: generateReferralCode(formData.name)})}
                      title="Regenerate code"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </Button>
                  )}
                </div>
                {!isEditing && (
                  <p className="text-xs text-gray-500 mt-1">
                    Auto-generated from name. You can edit it.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Payment Info */}
          <div className="space-y-4">
            <h3 className="font-semibold text-sm text-gray-700">Payment Information</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="wallet_type">Wallet Type</Label>
                <select
                  id="wallet_type"
                  value={formData.wallet_type}
                  onChange={(e) => setFormData({...formData, wallet_type: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md bg-white"
                >
                  <option value="crypto_wallet">Crypto Wallet</option>
                  <option value="bank_account">Bank Account</option>
                  <option value="paypal">PayPal</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <Label htmlFor="wallet_address">Wallet Address / Account</Label>
                <Input
                  id="wallet_address"
                  value={formData.wallet_address}
                  onChange={(e) => setFormData({...formData, wallet_address: e.target.value})}
                  placeholder="0x... or account number"
                  className="font-mono text-sm"
                />
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notes (Optional)</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              placeholder="Any additional notes about this salesperson..."
              rows={3}
            />
          </div>

          {/* Status */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="active"
              checked={formData.active}
              onChange={(e) => setFormData({...formData, active: e.target.checked})}
              className="w-4 h-4"
            />
            <Label htmlFor="active" className="cursor-pointer">
              Active (can accept new referrals)
            </Label>
          </div>

          {/* Preview */}
          {formData.referral_code && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm font-medium text-blue-900 mb-2">
                📋 Referral Link Preview:
              </p>
              <code className="text-xs bg-white px-3 py-2 rounded border block break-all">
                {window.location.origin}/prospects?ref={formData.referral_code}
              </code>
            </div>
          )}

          {/* Actions */}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && (
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              )}
              {isEditing ? 'Save Changes' : 'Add Salesperson'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddSalespersonModal;
