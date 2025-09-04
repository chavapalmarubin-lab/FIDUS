import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Users, 
  Plus, 
  Edit2, 
  Trash2, 
  UserCheck, 
  Send,
  Eye,
  ArrowRight,
  TrendingUp,
  Calendar,
  Phone,
  Mail,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Target,
  DollarSign
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const STAGE_CONFIG = {
  lead: { 
    label: "Lead", 
    color: "bg-blue-500", 
    textColor: "text-blue-700", 
    bgColor: "bg-blue-50",
    icon: Target 
  },
  qualified: { 
    label: "Qualified", 
    color: "bg-green-500", 
    textColor: "text-green-700", 
    bgColor: "bg-green-50",
    icon: CheckCircle 
  },
  proposal: { 
    label: "Proposal", 
    color: "bg-yellow-500", 
    textColor: "text-yellow-700", 
    bgColor: "bg-yellow-50",
    icon: FileText 
  },
  negotiation: { 
    label: "Negotiation", 
    color: "bg-orange-500", 
    textColor: "text-orange-700", 
    bgColor: "bg-orange-50",
    icon: TrendingUp 
  },
  won: { 
    label: "Won", 
    color: "bg-emerald-600", 
    textColor: "text-emerald-700", 
    bgColor: "bg-emerald-50",
    icon: UserCheck 
  },
  lost: { 
    label: "Lost", 
    color: "bg-red-500", 
    textColor: "text-red-700", 
    bgColor: "bg-red-50",
    icon: XCircle 
  }
};

const ProspectManagement = () => {
  const [prospects, setProspects] = useState([]);
  const [pipeline, setPipeline] = useState({});
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProspect, setSelectedProspect] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  // Form states
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    notes: ""
  });

  useEffect(() => {
    fetchProspects();
    fetchPipeline();
  }, []);

  const fetchProspects = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/crm/prospects`);
      setProspects(response.data.prospects);
      setStats(response.data);
    } catch (err) {
      setError("Failed to fetch prospects");
      console.error("Error fetching prospects:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPipeline = async () => {
    try {
      const response = await axios.get(`${API}/crm/prospects/pipeline`);
      setPipeline(response.data.pipeline);
      setStats(prev => ({ ...prev, ...response.data.stats }));
    } catch (err) {
      console.error("Error fetching pipeline:", err);
    }
  };

  const handleAddProspect = async () => {
    try {
      if (!formData.name || !formData.email || !formData.phone) {
        setError("Please fill in all required fields");
        return;
      }

      const response = await axios.post(`${API}/crm/prospects`, formData);
      
      if (response.data.success) {
        setSuccess("Prospect added successfully");
        setShowAddModal(false);
        resetForm();
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add prospect");
    }
  };

  const handleUpdateProspect = async () => {
    try {
      if (!selectedProspect) return;

      const response = await axios.put(`${API}/crm/prospects/${selectedProspect.id}`, formData);
      
      if (response.data.success) {
        setSuccess("Prospect updated successfully");
        setShowEditModal(false);
        setSelectedProspect(null);
        resetForm();
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update prospect");
    }
  };

  const handleStageChange = async (prospectId, newStage) => {
    try {
      const response = await axios.put(`${API}/crm/prospects/${prospectId}`, {
        stage: newStage
      });
      
      if (response.data.success) {
        setSuccess(`Prospect moved to ${STAGE_CONFIG[newStage].label} stage`);
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update prospect stage");
    }
  };

  const handleDeleteProspect = async (prospectId, prospectName) => {
    if (!window.confirm(`Are you sure you want to delete prospect "${prospectName}"?`)) {
      return;
    }

    try {
      const response = await axios.delete(`${API}/crm/prospects/${prospectId}`);
      
      if (response.data.success) {
        setSuccess("Prospect deleted successfully");
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete prospect");
    }
  };

  const handleConvertProspect = async (prospectId) => {
    try {
      const response = await axios.post(`${API}/crm/prospects/${prospectId}/convert`, {
        prospect_id: prospectId,
        send_agreement: true
      });
      
      if (response.data.success) {
        setSuccess(`Prospect converted to client successfully! ${response.data.message}`);
        fetchProspects();
        fetchPipeline();
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to convert prospect");
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      email: "",
      phone: "",
      notes: ""
    });
  };

  const openEditModal = (prospect) => {
    setSelectedProspect(prospect);
    setFormData({
      name: prospect.name,
      email: prospect.email,
      phone: prospect.phone,
      notes: prospect.notes || ""
    });
    setShowEditModal(true);
  };

  const renderProspectCard = (prospect) => {
    const stageConfig = STAGE_CONFIG[prospect.stage] || STAGE_CONFIG.lead;
    const IconComponent = stageConfig.icon;

    return (
      <motion.div
        key={prospect.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg border border-slate-200 p-4 hover:shadow-md transition-shadow"
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${stageConfig.bgColor}`}>
              <IconComponent className={`h-4 w-4 ${stageConfig.textColor}`} />
            </div>
            <div>
              <h3 className="font-medium text-slate-900">{prospect.name}</h3>
              <p className="text-sm text-slate-600">{prospect.email}</p>
            </div>
          </div>
          <Badge className={`${stageConfig.color} text-white text-xs`}>
            {stageConfig.label}
          </Badge>
        </div>

        <div className="space-y-2 text-sm text-slate-600 mb-4">
          <div className="flex items-center gap-2">
            <Phone className="h-3 w-3" />
            <span>{prospect.phone}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-3 w-3" />
            <span>Created: {new Date(prospect.created_at).toLocaleDateString()}</span>
          </div>
          {prospect.notes && (
            <div className="flex items-start gap-2">
              <FileText className="h-3 w-3 mt-0.5" />
              <span className="text-xs">{prospect.notes.substring(0, 100)}...</span>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => openEditModal(prospect)}
            className="flex-1"
          >
            <Edit2 size={14} className="mr-1" />
            Edit
          </Button>
          
          {prospect.stage === 'won' && !prospect.converted_to_client && (
            <Button
              size="sm"
              onClick={() => handleConvertProspect(prospect.id)}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              <UserCheck size={14} className="mr-1" />
              Convert
            </Button>
          )}
          
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleDeleteProspect(prospect.id, prospect.name)}
            className="text-red-500 hover:text-red-700"
          >
            <Trash2 size={14} />
          </Button>
        </div>
      </motion.div>
    );
  };

  const renderStageColumn = (stage, prospects) => {
    const stageConfig = STAGE_CONFIG[stage];
    const IconComponent = stageConfig.icon;

    return (
      <div key={stage} className="min-w-80 bg-slate-50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <IconComponent className={`h-5 w-5 ${stageConfig.textColor}`} />
            <h3 className="font-medium text-slate-900">{stageConfig.label}</h3>
            <Badge variant="outline" className="text-xs">
              {prospects.length}
            </Badge>
          </div>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {(prospects || []).map(prospect => (
            <div key={prospect.id} className="bg-white rounded-lg border p-3 shadow-sm">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-medium text-sm text-slate-900">{prospect.name}</h4>
                  <p className="text-xs text-slate-600">{prospect.email}</p>
                </div>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => openEditModal(prospect)}
                    className="h-6 w-6 p-0"
                  >
                    <Edit2 size={12} />
                  </Button>
                </div>
              </div>
              
              <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
                <Phone className="h-3 w-3" />
                <span>{prospect.phone}</span>
              </div>

              {/* Stage progression buttons */}
              <div className="flex gap-1 flex-wrap">
                {Object.keys(STAGE_CONFIG).map(nextStage => {
                  if (nextStage === stage) return null;
                  const nextConfig = STAGE_CONFIG[nextStage];
                  
                  return (
                    <Button
                      key={nextStage}
                      size="sm"
                      variant="outline"
                      onClick={() => handleStageChange(prospect.id, nextStage)}
                      className="text-xs h-6 px-2"
                    >
                      {nextConfig.label}
                    </Button>
                  );
                })}
              </div>
            </div>
          ))}
          
          {(prospects || []).length === 0 && (
            <div className="text-center py-8 text-slate-500">
              <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No prospects in this stage</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-slate-600 text-xl">Loading prospects...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Prospect Management</h2>
          <p className="text-slate-600">Manage leads and track conversion pipeline</p>
        </div>
        
        <Button
          onClick={() => setShowAddModal(true)}
          className="bg-cyan-600 hover:bg-cyan-700"
        >
          <Plus size={16} className="mr-2" />
          Add Prospect
        </Button>
      </div>

      {/* Success/Error Messages */}
      {error && (
        <Alert className="bg-red-50 border-red-200">
          <AlertDescription className="text-red-800">{error}</AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setError("")}
            className="ml-auto text-red-600"
          >
            ×
          </Button>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <AlertDescription className="text-green-800">{success}</AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSuccess("")}
            className="ml-auto text-green-600"
          >
            ×
          </Button>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-50 rounded-full">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Total Prospects</p>
                <p className="text-xl font-semibold text-slate-900">{stats.total_prospects || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-50 rounded-full">
                <Target className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Active Prospects</p>
                <p className="text-xl font-semibold text-slate-900">{stats.active_prospects || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-full">
                <UserCheck className="h-5 w-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Won Prospects</p>
                <p className="text-xl font-semibold text-slate-900">{stats.won_prospects || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-50 rounded-full">
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-slate-600">Conversion Rate</p>
                <p className="text-xl font-semibold text-slate-900">{stats.conversion_rate || 0}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(prospects || []).map(renderProspectCard)}
          </div>
          
          {prospects.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <Users size={48} className="mx-auto mb-4 text-slate-400" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">No Prospects Yet</h3>
                <p className="text-slate-600 mb-4">Start building your sales pipeline by adding prospects</p>
                <Button
                  onClick={() => setShowAddModal(true)}
                  className="bg-cyan-600 hover:bg-cyan-700"
                >
                  <Plus size={16} className="mr-2" />
                  Add First Prospect
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="pipeline" className="space-y-4">
          <div className="overflow-x-auto">
            <div className="flex gap-4 pb-4" style={{ minWidth: 'fit-content' }}>
              {Object.entries(pipeline).map(([stage, prospects]) => 
                renderStageColumn(stage, prospects)
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* Add Prospect Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Add New Prospect</h3>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name" className="text-slate-700">Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="Full name"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="email" className="text-slate-700">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="email@example.com"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="phone" className="text-slate-700">Phone *</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    placeholder="+1 (555) 123-4567"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="notes" className="text-slate-700">Notes</Label>
                  <textarea
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    placeholder="Additional notes about this prospect..."
                    className="mt-1 w-full min-h-20 px-3 py-2 border border-slate-300 rounded-md resize-none"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddModal(false);
                    resetForm();
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAddProspect}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                >
                  Add Prospect
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Edit Prospect Modal */}
      <AnimatePresence>
        {showEditModal && selectedProspect && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setShowEditModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Edit Prospect</h3>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="edit-name" className="text-slate-700">Name *</Label>
                  <Input
                    id="edit-name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="Full name"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="edit-email" className="text-slate-700">Email *</Label>
                  <Input
                    id="edit-email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="email@example.com"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="edit-phone" className="text-slate-700">Phone *</Label>
                  <Input
                    id="edit-phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    placeholder="+1 (555) 123-4567"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="edit-notes" className="text-slate-700">Notes</Label>
                  <textarea
                    id="edit-notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    placeholder="Additional notes about this prospect..."
                    className="mt-1 w-full min-h-20 px-3 py-2 border border-slate-300 rounded-md resize-none"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedProspect(null);
                    resetForm();
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleUpdateProspect}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                >
                  Update Prospect
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProspectManagement;