import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Phone, Calendar, MessageSquare, Plus, Save } from 'lucide-react';
import Layout from '../../components/referral-agent/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Textarea } from '../../components/ui/textarea';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import referralAgentApi from '../../services/referralAgentApi';
import StatusBadge from '../../components/referral-agent/StatusBadge';
import { format } from 'date-fns';

const LeadDetail = () => {
  const { leadId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [lead, setLead] = useState(null);
  const [newNote, setNewNote] = useState('');
  const [addingNote, setAddingNote] = useState(false);
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

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    try {
      setAddingNote(true);
      setError('');
      const response = await referralAgentApi.addLeadNote(leadId, newNote);
      if (response.success) {
        setSuccess('Note added successfully');
        setNewNote('');
        await fetchLeadDetail();
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError('Failed to add note');
      }
    } catch (err) {
      console.error('Add note error:', err);
      setError('An error occurred adding the note');
    } finally {
      setAddingNote(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      setUpdatingStatus(true);
      setError('');
      const response = await referralAgentApi.updateLeadStatus(leadId, newStatus);
      if (response.success) {
        setSuccess('Status updated successfully');
        await fetchLeadDetail();
        setTimeout(() => setSuccess(''), 3000);
      } else {
        setError('Failed to update status');
      }
    } catch (err) {
      console.error('Status update error:', err);
      setError('An error occurred updating status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6">
          <div className="animate-pulse">
            <div className="h-8 w-48 bg-slate-800 rounded mb-4"></div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-4">
                <div className="h-64 bg-slate-800 rounded"></div>
                <div className="h-96 bg-slate-800 rounded"></div>
              </div>
              <div className="h-96 bg-slate-800 rounded"></div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (!lead) {
    return (
      <Layout>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-12 text-center">
            <p className="text-white text-xl">Lead not found</p>
            <Button
              onClick={() => navigate('/referral-agent/leads')}
              className="mt-4 bg-cyan-600 hover:bg-cyan-700"
            >
              Back to Leads
            </Button>
          </CardContent>
        </Card>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <Button
            onClick={() => navigate('/referral-agent/leads')}
            variant="ghost"
            className="text-slate-400 hover:text-white mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Leads
          </Button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{lead.email || 'Lead Details'}</h1>
              <p className="text-slate-400">Manage lead information and interactions</p>
            </div>
            <StatusBadge status={lead.crmStatus || 'pending'} />
          </div>
        </div>

        {error && (
          <Alert variant="destructive" className="bg-red-950 border-red-900 text-red-200">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="bg-green-950 border-green-900 text-green-200">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Lead Information */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white">Lead Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                    <Mail className="h-5 w-5 text-slate-400 mt-0.5" />
                    <div>
                      <div className="text-sm text-slate-400">Email</div>
                      <div className="text-white font-medium">{lead.email || 'Not provided'}</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                    <Phone className="h-5 w-5 text-slate-400 mt-0.5" />
                    <div>
                      <div className="text-sm text-slate-400">Phone</div>
                      <div className="text-white font-medium">{lead.phone || 'Not provided'}</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                    <Calendar className="h-5 w-5 text-slate-400 mt-0.5" />
                    <div>
                      <div className="text-sm text-slate-400">Registered</div>
                      <div className="text-white font-medium">
                        {lead.registrationDate ? format(new Date(lead.registrationDate), 'MMM dd, yyyy') : 'Unknown'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                    <Calendar className="h-5 w-5 text-slate-400 mt-0.5" />
                    <div>
                      <div className="text-sm text-slate-400">Last Contacted</div>
                      <div className="text-white font-medium">
                        {lead.lastContacted ? format(new Date(lead.lastContacted), 'MMM dd, yyyy') : 'Never'}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Notes */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-cyan-400" />
                  Notes & Activity
                </CardTitle>
                <CardDescription className="text-slate-400">Track your interactions with this lead</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Add Note */}
                <div className="space-y-2">
                  <Textarea
                    placeholder="Add a note about this lead..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    className="bg-slate-800 border-slate-700 text-white placeholder-slate-500 min-h-[100px]"
                  />
                  <Button
                    onClick={handleAddNote}
                    disabled={addingNote || !newNote.trim()}
                    className="bg-cyan-600 hover:bg-cyan-700 text-white"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Note
                  </Button>
                </div>

                {/* Notes List */}
                <div className="space-y-3 mt-6">
                  {lead.agentNotes && lead.agentNotes.length > 0 ? (
                    lead.agentNotes.map((note, idx) => (
                      <div key={idx} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                        <div className="text-white mb-2">{note.noteText || note.note_text}</div>
                        <div className="text-xs text-slate-400">
                          {note.timestamp ? format(new Date(note.timestamp), 'MMM dd, yyyy HH:mm') : 'Unknown time'}
                          {note.addedBy && ` • ${note.addedBy}`}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-slate-400">
                      <MessageSquare className="h-12 w-12 mx-auto mb-2 text-slate-600" />
                      <p>No notes yet. Add your first note above.</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Status Update */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white">Update Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Select
                  value={lead.crmStatus || 'pending'}
                  onValueChange={handleStatusChange}
                  disabled={updatingStatus}
                >
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="contacted">Contacted</SelectItem>
                    <SelectItem value="qualified">Qualified</SelectItem>
                    <SelectItem value="proposal_sent">Proposal Sent</SelectItem>
                    <SelectItem value="negotiating">Negotiating</SelectItem>
                    <SelectItem value="converted">Converted</SelectItem>
                    <SelectItem value="lost">Lost</SelectItem>
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {lead.email && (
                  <Button
                    onClick={() => window.location.href = `mailto:${lead.email}`}
                    variant="outline"
                    className="w-full justify-start border-slate-700 text-slate-300 hover:bg-slate-800"
                  >
                    <Mail className="h-4 w-4 mr-2" />
                    Send Email
                  </Button>
                )}
                {lead.phone && (
                  <Button
                    onClick={() => window.location.href = `tel:${lead.phone}`}
                    variant="outline"
                    className="w-full justify-start border-slate-700 text-slate-300 hover:bg-slate-800"
                  >
                    <Phone className="h-4 w-4 mr-2" />
                    Call Lead
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default LeadDetail;