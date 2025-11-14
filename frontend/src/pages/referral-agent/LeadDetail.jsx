import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../../components/referral-agent/Layout';
import StatusBadge from '../../components/referral-agent/StatusBadge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Textarea } from '../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { ArrowLeft, Mail, Phone, Calendar, MapPin, Plus } from 'lucide-react';
import referralAgentApi from '../../services/referralAgentApi';
import { format } from 'date-fns';

const LeadDetail = () => {
  const { leadId } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Note form
  const [noteText, setNoteText] = useState('');
  const [addingNote, setAddingNote] = useState(false);
  
  // Status update form
  const [newStatus, setNewStatus] = useState('');
  const [nextFollowUp, setNextFollowUp] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => {
    fetchLeadDetail();
  }, [leadId]);

  const fetchLeadDetail = async () => {
    try {
      setLoading(true);
      const response = await referralAgentApi.getLeadDetail(leadId);
      if (response.success) {
        setLead(response.lead);
        setNewStatus(response.lead.crmStatus);
      } else {
        setError('Failed to load lead details');
      }
    } catch (err) {
      console.error('Lead detail error:', err);
      setError('An error occurred loading lead details');
    } finally {
      setLoading(false);
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!noteText.trim()) return;

    try {
      setAddingNote(true);
      setError('');
      setSuccess('');
      
      const response = await referralAgentApi.addLeadNote(leadId, noteText);
      if (response.success) {
        setSuccess('Note added successfully');
        setNoteText('');
        fetchLeadDetail();
      } else {
        setError('Failed to add note');
      }
    } catch (err) {
      console.error('Add note error:', err);
      setError('An error occurred adding note');
    } finally {
      setAddingNote(false);
    }
  };

  const handleUpdateStatus = async (e) => {
    e.preventDefault();
    
    try {
      setUpdatingStatus(true);
      setError('');
      setSuccess('');
      
      const response = await referralAgentApi.updateLeadStatus(
        leadId, 
        newStatus, 
        nextFollowUp || null
      );
      
      if (response.success) {
        setSuccess('Status updated successfully');
        fetchLeadDetail();
      } else {
        setError('Failed to update status');
      }
    } catch (err) {
      console.error('Update status error:', err);
      setError('An error occurred updating status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </Layout>
    );
  }

  if (!lead) {
    return (
      <Layout>
        <Alert variant="destructive">
          <AlertDescription>Lead not found</AlertDescription>
        </Alert>
      </Layout>
    );
  }

  return (
    <Layout>
      <Button
        variant="ghost"
        onClick={() => navigate('/referral-agent/leads')}
        className="mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Leads
      </Button>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="mb-6 bg-green-50 text-green-800 border-green-200">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lead Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-2xl">{lead.name || lead.email}</CardTitle>
                <StatusBadge status={lead.crmStatus} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {lead.email && (
                  <div className="flex items-center text-gray-600">
                    <Mail className="h-5 w-5 mr-3 text-gray-400" />
                    <span>{lead.email}</span>
                  </div>
                )}
                {lead.phone && (
                  <div className="flex items-center text-gray-600">
                    <Phone className="h-5 w-5 mr-3 text-gray-400" />
                    <span>{lead.phone}</span>
                  </div>
                )}
                {lead.registrationDate && (
                  <div className="flex items-center text-gray-600">
                    <Calendar className="h-5 w-5 mr-3 text-gray-400" />
                    <span>Registered: {format(new Date(lead.registrationDate), 'MMM d, yyyy')}</span>
                  </div>
                )}
                {lead.lastContacted && (
                  <div className="flex items-center text-gray-600">
                    <Calendar className="h-5 w-5 mr-3 text-gray-400" />
                    <span>Last contacted: {format(new Date(lead.lastContacted), 'MMM d, yyyy')}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Notes */}
          <Card>
            <CardHeader>
              <CardTitle>Notes & Activity</CardTitle>
              <CardDescription>Track your interactions with this lead</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Add Note Form */}
              <form onSubmit={handleAddNote} className="mb-6">
                <div className="space-y-2">
                  <Label htmlFor="note">Add New Note</Label>
                  <Textarea
                    id="note"
                    placeholder="Enter your note here..."
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    rows={3}
                    disabled={addingNote}
                  />
                </div>
                <Button
                  type="submit"
                  className="mt-2"
                  disabled={addingNote || !noteText.trim()}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {addingNote ? 'Adding...' : 'Add Note'}
                </Button>
              </form>

              {/* Notes List */}
              <div className="space-y-4">
                {lead.agentNotes && lead.agentNotes.length > 0 ? (
                  lead.agentNotes.map((note, index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                      <p className="text-sm text-gray-600 mb-1">
                        {note.timestamp && format(new Date(note.timestamp), 'MMM d, yyyy h:mm a')}
                      </p>
                      <p className="text-gray-900">{note.noteText}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-500 text-center py-8">No notes yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Update Status */}
          <Card>
            <CardHeader>
              <CardTitle>Update Status</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateStatus} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select value={newStatus} onValueChange={setNewStatus}>
                    <SelectTrigger id="status">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="contacted">Contacted</SelectItem>
                      <SelectItem value="qualified">Qualified</SelectItem>
                      <SelectItem value="interested">Interested</SelectItem>
                      <SelectItem value="not_interested">Not Interested</SelectItem>
                      <SelectItem value="lost">Lost</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="followup">Next Follow-up (Optional)</Label>
                  <Input
                    id="followup"
                    type="date"
                    value={nextFollowUp}
                    onChange={(e) => setNextFollowUp(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={updatingStatus}
                >
                  {updatingStatus ? 'Updating...' : 'Update Status'}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Lead Priority */}
          {lead.priority && (
            <Card>
              <CardHeader>
                <CardTitle>Priority</CardTitle>
              </CardHeader>
              <CardContent>
                <span className={`inline-flex items-center px-3 py-2 rounded font-medium ${
                  lead.priority === 'high' ? 'bg-red-100 text-red-800' :
                  lead.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {lead.priority.toUpperCase()}
                </span>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default LeadDetail;
