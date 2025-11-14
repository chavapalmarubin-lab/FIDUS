import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Mail, Phone, Calendar, ChevronRight } from 'lucide-react';
import StatusBadge from './StatusBadge';
import { format } from 'date-fns';

const LeadCard = ({ lead }) => {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                {lead.name || lead.email}
              </h3>
              <StatusBadge status={lead.crmStatus} />
            </div>
            {lead.priority && (
              <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                lead.priority === 'high' ? 'bg-red-100 text-red-800' :
                lead.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {lead.priority.toUpperCase()} Priority
              </span>
            )}
          </div>
          <Link to={`/referral-agent/leads/${lead.id}`}>
            <Button variant="ghost" size="sm">
              <ChevronRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>

        <div className="space-y-2 text-sm text-gray-600">
          {lead.email && (
            <div className="flex items-center">
              <Mail className="h-4 w-4 mr-2 text-gray-400" />
              <span>{lead.email}</span>
            </div>
          )}
          {lead.phone && (
            <div className="flex items-center">
              <Phone className="h-4 w-4 mr-2 text-gray-400" />
              <span>{lead.phone}</span>
            </div>
          )}
          {lead.lastContacted && (
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-2 text-gray-400" />
              <span>Last contact: {format(new Date(lead.lastContacted), 'MMM d, yyyy')}</span>
            </div>
          )}
          {lead.nextFollowUp && (
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-2 text-blue-500" />
              <span className="text-blue-600 font-medium">
                Follow up: {format(new Date(lead.nextFollowUp), 'MMM d, yyyy')}
              </span>
            </div>
          )}
        </div>

        {lead.agentNotes && lead.agentNotes.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-gray-600 line-clamp-2">
              Latest: {lead.agentNotes[lead.agentNotes.length - 1].noteText}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default LeadCard;
