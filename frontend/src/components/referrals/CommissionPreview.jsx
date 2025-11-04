import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';

const CommissionPreview = ({ salesperson, investment }) => {
  if (!salesperson || !investment) return null;

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(value);
  };

  const calculateCommission = () => {
    const amount = parseFloat(investment.amount || 0);
    const rate = parseFloat(investment.monthlyRate || 0);
    const months = parseInt(investment.term || 12);
    const frequency = investment.frequency || 'monthly'; // monthly or quarterly
    
    // Calculate total interest client will earn
    let totalInterest;
    if (frequency === 'quarterly') {
      const quarters = months / 3;
      const quarterlyInterest = amount * rate * 3;
      totalInterest = quarterlyInterest * quarters;
    } else {
      totalInterest = amount * rate * months;
    }

    // Commission is 10% of interest
    const commission = totalInterest * 0.10;
    const paymentCount = frequency === 'quarterly' ? months / 3 : months;

    return {
      total: commission,
      perPayment: commission / paymentCount,
      paymentCount: paymentCount,
      frequency: frequency
    };
  };

  const commission = calculateCommission();

  return (
    <Card className="border-2 border-blue-200 bg-blue-50">
      <CardContent className="pt-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Your Financial Advisor</p>
            <p className="text-lg font-bold text-blue-900">{salesperson.name}</p>
          </div>
          <Badge className="bg-blue-600 text-white">Verified</Badge>
        </div>

        {/* Commission Info */}
        <div className="bg-white rounded-lg p-4 space-y-3">
          <div className="flex items-start gap-2">
            <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-sm text-gray-700">
              Your advisor earns a commission on the interest payments you receive. 
              This helps them provide you with ongoing support and service.
            </p>
          </div>

          <div className="border-t pt-3 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Commission</span>
              <span className="text-lg font-bold text-blue-900">
                {formatCurrency(commission.total)}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">
                {commission.paymentCount} {commission.frequency} payments
              </span>
              <span className="text-sm text-gray-700">
                {formatCurrency(commission.perPayment)} each
              </span>
            </div>
          </div>

          {/* Transparency Note */}
          <div className="bg-blue-50 rounded p-3 border border-blue-200">
            <p className="text-xs text-blue-800">
              <strong>💡 Transparency:</strong> Commissions are paid by FIDUS, not deducted 
              from your returns. Your projected earnings remain {formatCurrency(investment.totalInterest || 0)}.
            </p>
          </div>
        </div>

        {/* Contact Info */}
        {(salesperson.phone || salesperson.email) && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-xs text-gray-600 mb-2">Contact Your Advisor:</p>
            <div className="flex flex-col gap-1">
              {salesperson.email && (
                <a 
                  href={`mailto:${salesperson.email}`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  {salesperson.email}
                </a>
              )}
              {salesperson.phone && (
                <a 
                  href={`tel:${salesperson.phone}`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  {salesperson.phone}
                </a>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CommissionPreview;
