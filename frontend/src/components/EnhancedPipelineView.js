import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Target,
  Handshake,
  Trophy,
  X,
  Plus,
  Eye,
  ArrowRight,
  DollarSign,
  Calendar,
  Phone,
  Mail,
  FileText,
  UserCheck,
  ShieldCheck,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ChevronRight,
  TrendingUp,
  Activity,
  RefreshCw,
  Edit,
  Trash2,
  MessageSquare,
  Video
} from 'lucide-react';
import apiAxios from '../utils/apiAxios';
import ClientDetailModal from './ClientDetailModal';

const PIPELINE_STAGES = {
  lead: {
    label: 'Lead',
    icon: Target,
    color: 'bg-blue-500',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-700',
    borderColor: 'border-blue-200',
    description: 'Initial prospects and new leads'
  },
  negotiation: {
    label: 'Negotiation',
    icon: Handshake,
    color: 'bg-orange-500',
    bgColor: 'bg-orange-50',
    textColor: 'text-orange-700',
    borderColor: 'border-orange-200',
    description: 'Active discussions and proposal reviews'
  },
  won: {
    label: 'Won',
    icon: Trophy,
    color: 'bg-green-500',
    bgColor: 'bg-green-50',
    textColor: 'text-green-700',
    borderColor: 'border-green-200',
    description: 'Successfully closed deals'
  },
  lost: {
    label: 'Lost',
    icon: XCircle,
    color: 'bg-red-500',
    bgColor: 'bg-red-50',
    textColor: 'text-red-700',
    borderColor: 'border-red-200',
    description: 'Unsuccessful prospects'
  }
};

const EnhancedPipelineView = () => {
  const [prospects, setProspects] = useState([]);
  const [pipeline, setPipeline] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [clientDetailOpen, setClientDetailOpen] = useState(false);
  const [stats, setStats] = useState({});
  const [draggedProspect, setDraggedProspect] = useState(null);

  useEffect(() => {
    loadProspects();
    loadPipelineStats();
  }, []);

  const loadProspects = async () => {
    setLoading(true);
    try {
      const response = await apiAxios.get('/crm/prospects');
      if (response.data.success) {
        setProspects(response.data.prospects);
        organizePipeline(response.data.prospects);
      }
    } catch (error) {
      console.error('Failed to load prospects:', error);
    } finally {
      setLoading(false);
    }
  };

  const organizePipeline = (prospectsData) => {
    const organized = {
      lead: [],
      negotiation: [],
      won: [],
      lost: []
    };

    prospectsData.forEach(prospect => {
      const stage = prospect.stage || 'lead';
      if (organized[stage]) {
        organized[stage].push(prospect);
      } else {
        organized.lead.push(prospect);
      }
    });

    setPipeline(organized);
  };

  const loadPipelineStats = async () => {
    try {
      const response = await apiAxios.get('/crm/pipeline-stats');
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Failed to load pipeline stats:', error);
    }
  };

  const moveProspectToStage = async (prospectId, newStage) => {
    setLoading(true);
    try {
      const response = await apiAxios.put(`/crm/prospects/${prospectId}`, {
        stage: newStage,
        stage_changed_at: new Date().toISOString()
      });

      if (response.data.success) {
        // Update local state immediately
        const updatedProspects = prospects.map(p => 
          p.id === prospectId 
            ? { ...p, stage: newStage, stage_changed_at: new Date().toISOString() }
            : p
        );
        setProspects(updatedProspects);
        organizePipeline(updatedProspects);
        loadPipelineStats();
        
        console.log(`✅ Moved prospect to ${newStage} stage`);
      } else {
        throw new Error(response.data.error || 'Failed to update stage');
      }
    } catch (error) {
      console.error('Failed to move prospect:', error);
      alert(`Failed to move prospect: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const convertToClient = async (prospectId) => {
    setLoading(true);
    try {
      const response = await apiAxios.post(`/crm/prospects/${prospectId}/convert-to-client`);
      
      if (response.data.success) {
        alert('🎉 Prospect successfully converted to client! They will now go through the AML/KYC process.');
        loadProspects();
        loadPipelineStats();
      } else {
        throw new Error(response.data.error || 'Failed to convert prospect');
      }
    } catch (error) {
      console.error('Failed to convert prospect:', error);
      alert(`Failed to convert prospect: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const initiateAMLKYC = async (prospectId) => {
    setLoading(true);
    try {
      const response = await apiAxios.post(`/crm/prospects/${prospectId}/aml-kyc`);
      
      if (response.data.success) {
        alert('✅ AML/KYC check initiated successfully!');
        loadProspects();
      } else {
        throw new Error(response.data.error || 'Failed to initiate AML/KYC');
      }
    } catch (error) {
      console.error('Failed to initiate AML/KYC:', error);
      alert(`Failed to initiate AML/KYC: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const openClientDetail = (client) => {
    setSelectedClient(client);
    setClientDetailOpen(true);
  };

  const handleDragStart = (e, prospect) => {
    setDraggedProspect(prospect);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, targetStage) => {
    e.preventDefault();
    if (draggedProspect && draggedProspect.stage !== targetStage) {
      moveProspectToStage(draggedProspect.id, targetStage);
    }
    setDraggedProspect(null);
  };

  const renderProspectCard = (prospect) => {
    const canConvert = prospect.stage === 'won' && 
                      (prospect.aml_kyc_status === 'clear' || prospect.aml_kyc_status === 'approved') && 
                      !prospect.converted_to_client;
    
    const needsAMLKYC = prospect.stage === 'won' && !prospect.aml_kyc_status;

    return (
      <motion.div
        key={prospect.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg border border-gray-200 p-4 mb-3 shadow-sm hover:shadow-md transition-all cursor-pointer"
        draggable
        onDragStart={(e) => handleDragStart(e, prospect)}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900 text-sm mb-1">{prospect.name}</h4>
            <p className="text-xs text-gray-600">{prospect.email}</p>
            <div className="flex items-center gap-2 mt-1">
              <Phone className="w-3 h-3 text-gray-400" />
              <span className="text-xs text-gray-500">{prospect.phone}</span>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => openClientDetail(prospect)}
            className="h-8 w-8 p-0 text-blue-600 hover:text-blue-700"
          >
            <Eye className="w-4 h-4" />
          </Button>
        </div>

        {/* AML/KYC Status */}
        {prospect.aml_kyc_status && (
          <div className="flex items-center gap-1 mb-2">
            <ShieldCheck className="w-3 h-3" />
            <span className={`text-xs font-medium ${
              prospect.aml_kyc_status === 'clear' || prospect.aml_kyc_status === 'approved'
                ? 'text-green-600'
                : prospect.aml_kyc_status === 'manual_review'
                ? 'text-yellow-600'
                : 'text-red-600'
            }`}>
              AML/KYC: {prospect.aml_kyc_status.toUpperCase()}
            </span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-2">
          {/* Stage Movement Buttons */}
          <div className="flex gap-1 flex-wrap">
            {Object.entries(PIPELINE_STAGES).map(([stageKey, stageConfig]) => {
              if (stageKey === prospect.stage) return null;
              
              return (
                <Button
                  key={stageKey}
                  size="sm"
                  variant="outline"
                  onClick={() => moveProspectToStage(prospect.id, stageKey)}
                  className="text-xs h-7 px-2"
                  disabled={loading}
                >
                  <ArrowRight className="w-3 h-3 mr-1" />
                  {stageConfig.label}
                </Button>
              );
            })}
          </div>

          {/* Special Actions for Won Stage */}
          {prospect.stage === 'won' && (
            <div className="border-t pt-2 space-y-2">
              {needsAMLKYC && (
                <Button
                  size="sm"
                  onClick={() => initiateAMLKYC(prospect.id)}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs h-7"
                  disabled={loading}
                >
                  <ShieldCheck className="w-3 h-3 mr-1" />
                  Start AML/KYC
                </Button>
              )}

              {canConvert && (
                <Button
                  size="sm"
                  onClick={() => convertToClient(prospect.id)}
                  className="w-full bg-green-600 hover:bg-green-700 text-white text-xs h-8 font-bold"
                  disabled={loading}
                >
                  <UserCheck className="w-3 h-3 mr-1" />
                  CONVERT TO CLIENT
                </Button>
              )}

              {prospect.aml_kyc_status === 'manual_review' && (
                <div className="text-center">
                  <Badge className="bg-yellow-100 text-yellow-800 text-xs">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    Pending Review
                  </Badge>
                </div>
              )}
            </div>
          )}

          {/* Quick Actions */}
          <div className="flex gap-1 pt-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs text-blue-600 hover:text-blue-700"
            >
              <MessageSquare className="w-3 h-3 mr-1" />
              Email
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs text-green-600 hover:text-green-700"
            >
              <Video className="w-3 h-3 mr-1" />
              Meet
            </Button>
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="mt-2 pt-2 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Last updated: {new Date(prospect.updated_at || prospect.created_at).toLocaleDateString()}</span>
            <div className="flex items-center gap-1">
              {prospect.converted_to_client && (
                <Badge className="bg-purple-100 text-purple-800 text-xs">Client</Badge>
              )}
              {prospect.stage === 'won' && !prospect.converted_to_client && (
                <Badge className="bg-green-100 text-green-800 text-xs">Won Deal</Badge>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  const renderStageColumn = (stageKey, stageConfig, stageProspects) => {
    const IconComponent = stageConfig.icon;
    
    return (
      <div
        key={stageKey}
        className={`min-w-80 rounded-lg p-4 ${stageConfig.bgColor} ${stageConfig.borderColor} border-2`}
        onDragOver={handleDragOver}
        onDrop={(e) => handleDrop(e, stageKey)}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${stageConfig.color}`}>
              <IconComponent className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className={`font-bold ${stageConfig.textColor}`}>{stageConfig.label}</h3>
              <p className="text-xs text-gray-600">{stageConfig.description}</p>
            </div>
          </div>
          <div className="text-center">
            <Badge className={`${stageConfig.color} text-white font-bold`}>
              {stageProspects.length}
            </Badge>
            {stats[`${stageKey}_value`] && (
              <p className="text-xs text-gray-600 mt-1">
                ${stats[`${stageKey}_value`].toLocaleString()}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          <AnimatePresence>
            {stageProspects.map(renderProspectCard)}
          </AnimatePresence>
          
          {stageProspects.length === 0 && (
            <div className="text-center py-8">
              <IconComponent className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm text-gray-500">No prospects in this stage</p>
              <p className="text-xs text-gray-400 mt-1">
                Drag prospects here or use the action buttons
              </p>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Pipeline Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Prospects</p>
                <p className="text-2xl font-bold text-gray-900">
                  {prospects.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Trophy className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Won Deals</p>
                <p className="text-2xl font-bold text-green-600">
                  {pipeline.won?.length || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Conversion Rate</p>
                <p className="text-2xl font-bold text-orange-600">
                  {stats.conversion_rate || 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <DollarSign className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Pipeline Value</p>
                <p className="text-xl font-bold text-purple-600">
                  ${stats.total_pipeline_value?.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pipeline Stages */}
      <div className="bg-gray-50 rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Sales Pipeline</h2>
            <p className="text-gray-600">Drag prospects between stages or use action buttons</p>
          </div>
          <Button
            onClick={loadProspects}
            variant="outline"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            <span className="ml-3 text-gray-600">Loading pipeline...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <div className="flex gap-6 pb-4" style={{ minWidth: 'fit-content' }}>
              {Object.entries(PIPELINE_STAGES).map(([stageKey, stageConfig]) =>
                renderStageColumn(stageKey, stageConfig, pipeline[stageKey] || [])
              )}
            </div>
          </div>
        )}
      </div>

      {/* Success/Error Messages */}
      {loading && (
        <Alert className="bg-blue-50 border-blue-200">
          <Activity className="h-4 w-4" />
          <AlertDescription className="text-blue-800">
            Processing pipeline changes...
          </AlertDescription>
        </Alert>
      )}

      {/* Client Detail Modal */}
      <ClientDetailModal
        client={selectedClient}
        isOpen={clientDetailOpen}
        onClose={() => {
          setClientDetailOpen(false);
          setSelectedClient(null);
        }}
      />
    </div>
  );
};

export default EnhancedPipelineView;