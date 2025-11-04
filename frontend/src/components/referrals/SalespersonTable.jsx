import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';

const SalespersonTable = ({ salespeople, onEdit, onToggleActive, onRefresh }) => {
  const [copiedId, setCopiedId] = useState(null);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  const formatCompact = (value) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return formatCurrency(value);
  };

  const copyReferralLink = (salesperson) => {
    const link = `${window.location.origin}/prospects?ref=${salesperson.referral_code}`;
    
    navigator.clipboard.writeText(link).then(() => {
      setCopiedId(salesperson.id || salesperson._id);
      
      // Show success message
      const message = document.createElement('div');
      message.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
      message.innerHTML = `
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <div>
            <p class="font-semibold">Referral link copied!</p>
            <p class="text-sm">${salesperson.name}'s link is ready to share</p>
          </div>
        </div>
      `;
      document.body.appendChild(message);
      setTimeout(() => message.remove(), 3000);
      
      setTimeout(() => setCopiedId(null), 2000);
    }).catch(err => {
      alert('Failed to copy link');
      console.error('Copy failed:', err);
    });
  };

  const handleToggleActive = async (salesperson) => {
    const newStatus = !salesperson.active;
    const action = newStatus ? 'activate' : 'deactivate';
    
    if (window.confirm(`Are you sure you want to ${action} ${salesperson.name}?`)) {
      await onToggleActive(salesperson.id || salesperson._id, newStatus);
    }
  };

  if (salespeople.length === 0) {
    return (
      <div className="text-center py-12 border rounded-lg bg-gray-50">
        <p className="text-gray-600">No salespeople found</p>
        <p className="text-sm text-gray-500 mt-2">Add your first salesperson to get started</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-gray-50">
            <TableHead className="w-[250px]">Salesperson</TableHead>
            <TableHead className="w-[120px]">Referral Code</TableHead>
            <TableHead className="text-right w-[100px]">Clients</TableHead>
            <TableHead className="text-right w-[120px]">Sales Volume</TableHead>
            <TableHead className="text-right w-[120px]">Commissions</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="text-right w-[200px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {salespeople.map((salesperson) => {
            const spId = salesperson.id || salesperson._id;
            const isCopied = copiedId === spId;
            
            return (
              <TableRow key={spId} className="hover:bg-gray-50">
                {/* Name & Contact */}
                <TableCell>
                  <div>
                    <p className="font-medium text-gray-900">{salesperson.name}</p>
                    <p className="text-xs text-gray-500">{salesperson.email}</p>
                    {salesperson.phone && (
                      <p className="text-xs text-gray-500">{salesperson.phone}</p>
                    )}
                  </div>
                </TableCell>

                {/* Referral Code */}
                <TableCell>
                  <Badge variant="outline" className="font-mono">
                    {salesperson.referral_code}
                  </Badge>
                </TableCell>

                {/* Clients */}
                <TableCell className="text-right font-medium">
                  {salesperson.total_clients_referred || 0}
                </TableCell>

                {/* Sales Volume */}
                <TableCell className="text-right font-medium text-green-600">
                  {formatCompact(salesperson.total_sales_volume)}
                </TableCell>

                {/* Commissions */}
                <TableCell className="text-right font-medium text-blue-600">
                  {formatCompact(salesperson.total_commissions_earned)}
                </TableCell>

                {/* Status */}
                <TableCell>
                  {salesperson.active ? (
                    <Badge className="bg-green-100 text-green-800 border-green-200">
                      Active
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="text-gray-500">
                      Inactive
                    </Badge>
                  )}
                </TableCell>

                {/* Actions */}
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    {/* Copy Link */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyReferralLink(salesperson)}
                      className="h-8 w-8 p-0"
                      title="Copy referral link"
                    >
                      {isCopied ? (
                        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      )}
                    </Button>

                    {/* Edit */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onEdit(salesperson)}
                      className="h-8 w-8 p-0"
                      title="Edit salesperson"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </Button>

                    {/* Open Link */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const link = `${window.location.origin}/prospects?ref=${salesperson.referral_code}`;
                        window.open(link, '_blank');
                      }}
                      className="h-8 w-8 p-0"
                      title="Open referral link"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </Button>

                    {/* Activate/Deactivate */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleActive(salesperson)}
                      className={`h-8 w-8 p-0 ${
                        salesperson.active 
                          ? 'text-red-600 hover:text-red-700' 
                          : 'text-green-600 hover:text-green-700'
                      }`}
                      title={salesperson.active ? 'Deactivate' : 'Activate'}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
                      </svg>
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

export default SalespersonTable;
