import React from 'react';
import { Badge } from '../ui/badge';

const StatusBadge = ({ status }) => {
  const statusConfig = {
    pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100' },
    contacted: { label: 'Contacted', className: 'bg-blue-100 text-blue-800 hover:bg-blue-100' },
    qualified: { label: 'Qualified', className: 'bg-purple-100 text-purple-800 hover:bg-purple-100' },
    interested: { label: 'Interested', className: 'bg-green-100 text-green-800 hover:bg-green-100' },
    converted: { label: 'Converted', className: 'bg-emerald-100 text-emerald-800 hover:bg-emerald-100' },
    not_interested: { label: 'Not Interested', className: 'bg-gray-100 text-gray-800 hover:bg-gray-100' },
    lost: { label: 'Lost', className: 'bg-red-100 text-red-800 hover:bg-red-100' },
  };

  const config = statusConfig[status] || statusConfig.pending;

  return (
    <Badge className={config.className} variant="secondary">
      {config.label}
    </Badge>
  );
};

export default StatusBadge;
