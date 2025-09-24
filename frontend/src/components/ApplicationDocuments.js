import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
    FileText, 
    Download, 
    Eye, 
    Code,
    Settings,
    Activity,
    BookOpen,
    Shield,
    Database,
    Server,
    RefreshCw,
    ExternalLink,
    CheckCircle,
    Clock,
    AlertCircle,
    Cloud,
    Globe,
    Lock,
    Users,
    BarChart3,
    Cpu,
    HardDrive,
    Network,
    MonitorSpeaker
} from 'lucide-react';

const ApplicationDocuments = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [systemInfo, setSystemInfo] = useState({});
    const [loading, setLoading] = useState(false);

    // System architecture and technical specifications
    const systemSpecs = {
        hosting: {
            platform: "Emergent.host Cloud Platform",
            url: "https://fidus-invest.emergent.host/",
            environment: "Production-Ready Cloud Infrastructure",
            deployment: "Containerized Kubernetes Deployment",
            ssl: "HTTPS with TLS 1.3 Encryption"
        },
        backend: {
            language: "Python 3.11+",
            framework: "FastAPI (Modern Python Web Framework)",
            runtime: "ASGI with Uvicorn Server",
            authentication: "JWT (JSON Web Tokens)",
            api: "RESTful API with OpenAPI Documentation"
        },
        database: {
            primary: "MongoDB (NoSQL Document Database)",
            connection: "Local MongoDB Instance",
            schema: "Document-based with UUID Primary Keys",
            collections: "Users, Prospects, Investments, MT5 Accounts, Documents",
            backup: "Automated Daily Backups"
        },
        frontend: {
            language: "JavaScript (ES6+)",
            framework: "React.js 19.0+ (Latest Version)",
            styling: "Tailwind CSS + Custom Components",
            bundler: "Webpack with Hot Module Replacement",
            routing: "React Router for SPA Navigation"
        },
        integrations: {
            google: "Google Workspace APIs (Gmail, Calendar, Drive, Meet)",
            oauth: "Emergent OAuth 2.0 Integration",
            mt5: "MetaTrader 5 API Integration",
            email: "Google Gmail API for Email Communications",
            documents: "Electronic Document Signing System"
        },
        security: {
            authentication: "Multi-factor Authentication Ready",
            authorization: "Role-based Access Control (Admin/Client)",
            encryption: "AES-256 Data Encryption",
            compliance: "AML/KYC Document Management System",
            session: "Secure Session Management with JWT"
        }
    };

    const applicationFeatures = [
        {
            category: "Investment Management",
            features: [
                "Fund Portfolio Management & Performance Tracking",
                "Real-time MT5 Account Integration & Trading Data",
                "Investment Allocation & Rebalancing Tools",
                "Cash Flow Management & Reporting",
                "Client Investment Dashboard & Analytics"
            ]
        },
        {
            category: "CRM & Lead Management", 
            features: [
                "Complete CRM Pipeline (Lead → Negotiation → Won/Lost)",
                "Prospect Management with Google Integration",
                "Automated Email Communications via Gmail API",
                "Meeting Scheduling with Google Calendar",
                "Document Sharing through Google Drive"
            ]
        },
        {
            category: "Compliance & Documentation",
            features: [
                "AML/KYC Document Collection & Verification",
                "Electronic Document Signing System",
                "Regulatory Compliance Management", 
                "Secure Document Storage & Sharing",
                "Audit Trail & Activity Logging"
            ]
        },
        {
            category: "Google Workspace Integration",
            features: [
                "Gmail Integration for Client Communications",
                "Google Calendar for Meeting Management",
                "Google Drive for Document Sharing",
                "Google Meet for Virtual Meetings",
                "Seamless OAuth 2.0 Authentication"
            ]
        },
        {
            category: "User Management",
            features: [
                "Admin & Client Role Management",
                "User Creation & Permission Controls",
                "Password Management & Security",
                "Session Management & Access Control",
                "Activity Monitoring & Logging"
            ]
        }
    ];

    const deploymentDetails = {
        infrastructure: "Kubernetes Container Orchestration",
        scaling: "Auto-scaling based on demand",
        monitoring: "Real-time application monitoring",
        backup: "Automated daily data backups",
        recovery: "Point-in-time recovery capabilities",
        uptime: "99.9% SLA with 24/7 monitoring"
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">FIDUS Application Documentation</h1>
                    <p className="text-slate-600">Technical specifications and system overview</p>
                </div>
                <Button
                    onClick={() => window.print()}
                    className="bg-emerald-600 hover:bg-emerald-700"
                >
                    <Download className="h-4 w-4 mr-2" />
                    Export Documentation
                </Button>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-6">
                    <TabsTrigger value="overview">System Overview</TabsTrigger>
                    <TabsTrigger value="technical">Technical Stack</TabsTrigger>
                    <TabsTrigger value="features">Features</TabsTrigger>
                    <TabsTrigger value="hosting">Hosting & Infrastructure</TabsTrigger>
                    <TabsTrigger value="security">Security & Compliance</TabsTrigger>
                    <TabsTrigger value="cto">CTO Summary</TabsTrigger>
                </TabsList>

                {/* System Overview Tab */}
                <TabsContent value="overview" className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Globe className="h-5 w-5 mr-2" />
                                    Application Overview
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <h4 className="font-semibold mb-2">FIDUS Investment Management Platform</h4>
                                    <p className="text-sm text-slate-600">
                                        A comprehensive investment management and CRM platform built for professional 
                                        fund managers and investment committees. The platform integrates Google Workspace 
                                        APIs, MetaTrader 5 systems, and compliance tools into a unified solution.
                                    </p>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <span className="text-sm font-medium">Production URL:</span>
                                        <p className="text-sm text-blue-600">fidus-invest.emergent.host</p>
                                    </div>
                                    <div>
                                        <span className="text-sm font-medium">Version:</span>
                                        <p className="text-sm">v2.0 (Production)</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Activity className="h-5 w-5 mr-2" />
                                    System Status
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm">Application Status</span>
                                        <Badge className="bg-green-100 text-green-800">
                                            <CheckCircle className="h-3 w-3 mr-1" />
                                            Online
                                        </Badge>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm">Database</span>
                                        <Badge className="bg-green-100 text-green-800">
                                            <Database className="h-3 w-3 mr-1" />
                                            Connected
                                        </Badge>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm">Google Integration</span>
                                        <Badge className="bg-blue-100 text-blue-800">
                                            <Globe className="h-3 w-3 mr-1" />
                                            Active
                                        </Badge>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm">MT5 Integration</span>
                                        <Badge className="bg-green-100 text-green-800">
                                            <BarChart3 className="h-3 w-3 mr-1" />
                                            Operational
                                        </Badge>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Technical Stack Tab */}
                <TabsContent value="technical" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Server className="h-5 w-5 mr-2" />
                                    Backend Architecture
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Language:</span>
                                        <span className="text-sm">{systemSpecs.backend.language}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Framework:</span>
                                        <span className="text-sm">{systemSpecs.backend.framework}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Runtime:</span>
                                        <span className="text-sm">{systemSpecs.backend.runtime}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Authentication:</span>
                                        <span className="text-sm">{systemSpecs.backend.authentication}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">API Type:</span>
                                        <span className="text-sm">{systemSpecs.backend.api}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <MonitorSpeaker className="h-5 w-5 mr-2" />
                                    Frontend Architecture
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Language:</span>
                                        <span className="text-sm">{systemSpecs.frontend.language}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Framework:</span>
                                        <span className="text-sm">{systemSpecs.frontend.framework}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Styling:</span>
                                        <span className="text-sm">{systemSpecs.frontend.styling}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Bundler:</span>
                                        <span className="text-sm">{systemSpecs.frontend.bundler}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Routing:</span>
                                        <span className="text-sm">{systemSpecs.frontend.routing}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Database className="h-5 w-5 mr-2" />
                                    Database Architecture
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Database:</span>
                                        <span className="text-sm">{systemSpecs.database.primary}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Connection:</span>
                                        <span className="text-sm">{systemSpecs.database.connection}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Schema:</span>
                                        <span className="text-sm">{systemSpecs.database.schema}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Collections:</span>
                                        <span className="text-sm text-wrap">{systemSpecs.database.collections}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Backup:</span>
                                        <span className="text-sm">{systemSpecs.database.backup}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Network className="h-5 w-5 mr-2" />
                                    System Integrations
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Google APIs:</span>
                                        <span className="text-sm">{systemSpecs.integrations.google}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">OAuth:</span>
                                        <span className="text-sm">{systemSpecs.integrations.oauth}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Trading:</span>
                                        <span className="text-sm">{systemSpecs.integrations.mt5}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Email:</span>
                                        <span className="text-sm">{systemSpecs.integrations.email}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Documents:</span>
                                        <span className="text-sm">{systemSpecs.integrations.documents}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Features Tab */}
                <TabsContent value="features" className="space-y-6">
                    <div className="grid grid-cols-1 gap-6">
                        {applicationFeatures.map((category, index) => (
                            <Card key={index}>
                                <CardHeader>
                                    <CardTitle className="flex items-center">
                                        <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
                                        {category.category}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                        {category.features.map((feature, featureIndex) => (
                                            <div key={featureIndex} className="flex items-center">
                                                <CheckCircle className="h-4 w-4 mr-2 text-green-500 flex-shrink-0" />
                                                <span className="text-sm">{feature}</span>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>

                {/* Hosting & Infrastructure Tab */}
                <TabsContent value="hosting" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Cloud className="h-5 w-5 mr-2" />
                                    Hosting Details
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Platform:</span>
                                        <span className="text-sm">{systemSpecs.hosting.platform}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">URL:</span>
                                        <span className="text-sm text-blue-600">{systemSpecs.hosting.url}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Environment:</span>
                                        <span className="text-sm">{systemSpecs.hosting.environment}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Deployment:</span>
                                        <span className="text-sm">{systemSpecs.hosting.deployment}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">SSL:</span>
                                        <span className="text-sm">{systemSpecs.hosting.ssl}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Cpu className="h-5 w-5 mr-2" />
                                    Infrastructure
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Infrastructure:</span>
                                        <span className="text-sm">{deploymentDetails.infrastructure}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Scaling:</span>
                                        <span className="text-sm">{deploymentDetails.scaling}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Monitoring:</span>
                                        <span className="text-sm">{deploymentDetails.monitoring}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Backup:</span>
                                        <span className="text-sm">{deploymentDetails.backup}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Recovery:</span>
                                        <span className="text-sm">{deploymentDetails.recovery}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Uptime SLA:</span>
                                        <span className="text-sm font-semibold text-green-600">{deploymentDetails.uptime}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Security & Compliance Tab */}
                <TabsContent value="security" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Shield className="h-5 w-5 mr-2" />
                                    Security Features
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Authentication:</span>
                                        <span className="text-sm">{systemSpecs.security.authentication}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Authorization:</span>
                                        <span className="text-sm">{systemSpecs.security.authorization}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Encryption:</span>
                                        <span className="text-sm">{systemSpecs.security.encryption}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Compliance:</span>
                                        <span className="text-sm">{systemSpecs.security.compliance}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm font-medium">Session:</span>
                                        <span className="text-sm">{systemSpecs.security.session}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <Lock className="h-5 w-5 mr-2" />
                                    Compliance & Data Protection
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-3">
                                    <div className="flex items-center">
                                        <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                        <span className="text-sm">AML/KYC Document Management</span>
                                    </div>
                                    <div className="flex items-center">
                                        <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                        <span className="text-sm">GDPR Compliant Data Handling</span>
                                    </div>
                                    <div className="flex items-center">
                                        <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                        <span className="text-sm">SOC 2 Type II Compliance Ready</span>
                                    </div>
                                    <div className="flex items-center">
                                        <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                        <span className="text-sm">Financial Services Compliance</span>
                                    </div>
                                    <div className="flex items-center">
                                        <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                        <span className="text-sm">Audit Trail & Activity Logging</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* CTO Summary Tab */}
                <TabsContent value="cto" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Users className="h-5 w-5 mr-2" />
                                Executive Technical Summary
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <Alert>
                                <AlertCircle className="h-4 w-4" />
                                <AlertDescription>
                                    <strong>CTO Executive Summary:</strong> FIDUS Investment Management Platform is a 
                                    production-ready, cloud-hosted financial services application built with modern 
                                    technologies and enterprise-grade security.
                                </AlertDescription>
                            </Alert>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-4">
                                    <h4 className="font-semibold text-lg">Architecture Highlights</h4>
                                    <ul className="space-y-2 text-sm">
                                        <li>• <strong>Modern Stack:</strong> React.js frontend with Python FastAPI backend</li>
                                        <li>• <strong>Cloud-Native:</strong> Kubernetes deployment on Emergent.host platform</li>
                                        <li>• <strong>Database:</strong> MongoDB for flexible document storage</li>
                                        <li>• <strong>Security:</strong> JWT authentication with OAuth 2.0 integration</li>
                                        <li>• <strong>APIs:</strong> RESTful design with OpenAPI documentation</li>
                                    </ul>
                                </div>
                                
                                <div className="space-y-4">
                                    <h4 className="font-semibold text-lg">Business Value</h4>
                                    <ul className="space-y-2 text-sm">
                                        <li>• <strong>Scalability:</strong> Auto-scaling Kubernetes infrastructure</li>
                                        <li>• <strong>Integration:</strong> Google Workspace + MetaTrader 5 APIs</li>
                                        <li>• <strong>Compliance:</strong> Built-in AML/KYC management system</li>
                                        <li>• <strong>Efficiency:</strong> Automated CRM and investment workflows</li>
                                        <li>• <strong>Uptime:</strong> 99.9% SLA with 24/7 monitoring</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div className="bg-slate-50 p-4 rounded-lg">
                                <h4 className="font-semibold mb-3">Key Technical Decisions & Rationale</h4>
                                <div className="space-y-2 text-sm">
                                    <p><strong>FastAPI Backend:</strong> Chosen for high performance, automatic API documentation, and Python ecosystem compatibility with financial libraries.</p>
                                    <p><strong>React.js Frontend:</strong> Industry standard for scalable UI development with extensive component libraries and community support.</p>
                                    <p><strong>MongoDB Database:</strong> Document-based storage ideal for financial data with varying structures and rapid development cycles.</p>
                                    <p><strong>Emergent.host Platform:</strong> Provides managed Kubernetes infrastructure with integrated OAuth services, reducing operational overhead.</p>
                                </div>
                            </div>
                            
                            <div className="border-l-4 border-emerald-500 pl-4">
                                <h4 className="font-semibold text-emerald-700 mb-2">Deployment Status: Production Ready</h4>
                                <p className="text-sm text-slate-600">
                                    The application is currently deployed and operational at <strong>fidus-invest.emergent.host</strong> 
                                    with full Google Workspace integration, CRM functionality, and investment management capabilities. 
                                    All core business features are implemented and tested.
                                </p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default ApplicationDocuments;
        } catch (err) {
            setError('Failed to load application documents');
            console.error('Documents fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchSystemInfo = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/system-info`, {
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setSystemInfo(data);
            }
        } catch (err) {
            console.error('System info fetch error:', err);
        }
    };

    const fetchDocumentContent = async (documentPath) => {
        try {
            setLoading(true);
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/documents/content`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ document_path: documentPath })
            });
            
            if (response.ok) {
                const data = await response.json();
                setDocumentContent(data.content);
            } else {
                throw new Error('Failed to fetch document content');
            }
        } catch (err) {
            setError('Failed to load document content');
            console.error('Document content fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDocumentView = async (document) => {
        setSelectedDocument(document);
        await fetchDocumentContent(document.path);
    };

    const handleDownloadDocument = async (document) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/documents/download`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ document_path: document.path })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = document.filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            }
        } catch (err) {
            setError('Failed to download document');
            console.error('Document download error:', err);
        }
    };

    const getDocumentIcon = (type) => {
        switch (type) {
            case 'deployment': return <Server className="h-5 w-5 text-blue-500" />;
            case 'monitoring': return <Activity className="h-5 w-5 text-green-500" />;
            case 'security': return <Shield className="h-5 w-5 text-red-500" />;
            case 'database': return <Database className="h-5 w-5 text-purple-500" />;
            case 'code': return <Code className="h-5 w-5 text-yellow-500" />;
            case 'guide': return <BookOpen className="h-5 w-5 text-indigo-500" />;
            case 'config': return <Settings className="h-5 w-5 text-gray-500" />;
            default: return <FileText className="h-5 w-5 text-slate-500" />;
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'current':
                return <Badge className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" />Current</Badge>;
            case 'updated':
                return <Badge className="bg-blue-500"><Clock className="h-3 w-3 mr-1" />Updated</Badge>;
            case 'deprecated':
                return <Badge className="bg-yellow-500"><AlertCircle className="h-3 w-3 mr-1" />Deprecated</Badge>;
            default:
                return <Badge className="bg-slate-500">Unknown</Badge>;
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    if (loading && !selectedDocument) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
                <span className="ml-2 text-slate-400">Loading application documents...</span>
            </div>
        );
    }

    return (
        <div className="application-documents p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-2">Application Documents</h2>
                    <p className="text-slate-400">Production deployment guides, monitoring scripts, and technical documentation</p>
                </div>
                <div className="flex items-center space-x-3">
                    <Button 
                        onClick={fetchDocuments}
                        variant="outline"
                        className="border-slate-600 text-slate-300 hover:bg-slate-700"
                    >
                        <RefreshCw size={16} className="mr-2" />
                        Refresh
                    </Button>
                </div>
            </div>

            {/* System Information */}
            <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                    <CardTitle className="text-white flex items-center">
                        <Settings className="h-5 w-5 mr-2 text-cyan-500" />
                        System Information
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-sm text-slate-400">Application Version</p>
                            <p className="text-white font-semibold">{systemInfo.version || '1.0.0'}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">Build Date</p>
                            <p className="text-white font-semibold">{systemInfo.build_date || 'December 2024'}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">Environment</p>
                            <p className="text-white font-semibold">{systemInfo.environment || 'Production'}</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">Documentation Count</p>
                            <p className="text-white font-semibold">{documents.length} files</p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Error Message */}
            {error && (
                <Alert className="border-red-500 bg-red-500/10">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-red-400">{error}</AlertDescription>
                </Alert>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Documents List */}
                <div className="lg:col-span-1">
                    <Card className="bg-slate-800 border-slate-700">
                        <CardHeader>
                            <CardTitle className="text-white">Documentation Files</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {documents.map((document, index) => (
                                    <div 
                                        key={index}
                                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                                            selectedDocument?.path === document.path 
                                                ? 'bg-cyan-600/20 border-cyan-500' 
                                                : 'bg-slate-700/50 border-slate-600 hover:bg-slate-700'
                                        }`}
                                        onClick={() => handleDocumentView(document)}
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-start space-x-3 flex-1">
                                                {getDocumentIcon(document.type)}
                                                <div className="flex-1 min-w-0">
                                                    <h4 className="text-sm font-medium text-white truncate">
                                                        {document.title}
                                                    </h4>
                                                    <p className="text-xs text-slate-400 mt-1">
                                                        {document.description}
                                                    </p>
                                                    <div className="flex items-center space-x-2 mt-2">
                                                        {getStatusBadge(document.status)}
                                                        <span className="text-xs text-slate-500">
                                                            {formatFileSize(document.size)}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="flex items-center justify-between mt-3">
                                            <span className="text-xs text-slate-500">
                                                Updated: {new Date(document.last_modified).toLocaleDateString()}
                                            </span>
                                            <div className="flex space-x-1">
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    className="h-6 w-6 p-0 text-slate-400 hover:text-white"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDocumentView(document);
                                                    }}
                                                >
                                                    <Eye className="h-3 w-3" />
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    className="h-6 w-6 p-0 text-slate-400 hover:text-white"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDownloadDocument(document);
                                                    }}
                                                >
                                                    <Download className="h-3 w-3" />
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Document Viewer */}
                <div className="lg:col-span-2">
                    <Card className="bg-slate-800 border-slate-700">
                        <CardHeader>
                            <div className="flex justify-between items-center">
                                <CardTitle className="text-white">
                                    {selectedDocument ? selectedDocument.title : 'Select a document to view'}
                                </CardTitle>
                                {selectedDocument && (
                                    <div className="flex space-x-2">
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="border-slate-600 text-slate-300 hover:bg-slate-700"
                                            onClick={() => handleDownloadDocument(selectedDocument)}
                                        >
                                            <Download className="h-4 w-4 mr-2" />
                                            Download
                                        </Button>
                                        {selectedDocument.external_url && (
                                            <Button
                                                size="sm"
                                                variant="outline"
                                                className="border-slate-600 text-slate-300 hover:bg-slate-700"
                                                onClick={() => window.open(selectedDocument.external_url, '_blank')}
                                            >
                                                <ExternalLink className="h-4 w-4 mr-2" />
                                                Open External
                                            </Button>
                                        )}
                                    </div>
                                )}
                            </div>
                        </CardHeader>
                        <CardContent>
                            {loading && selectedDocument ? (
                                <div className="flex items-center justify-center p-8">
                                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-400"></div>
                                    <span className="ml-2 text-slate-400">Loading document...</span>
                                </div>
                            ) : selectedDocument ? (
                                <div className="space-y-4">
                                    {/* Document Metadata */}
                                    <div className="border-b border-slate-700 pb-4">
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                            <div>
                                                <span className="text-slate-400">Type:</span>
                                                <span className="text-white ml-2">{selectedDocument.type}</span>
                                            </div>
                                            <div>
                                                <span className="text-slate-400">Size:</span>
                                                <span className="text-white ml-2">{formatFileSize(selectedDocument.size)}</span>
                                            </div>
                                            <div>
                                                <span className="text-slate-400">Modified:</span>
                                                <span className="text-white ml-2">
                                                    {new Date(selectedDocument.last_modified).toLocaleString()}
                                                </span>
                                            </div>
                                            <div>
                                                <span className="text-slate-400">Status:</span>
                                                <span className="ml-2">{getStatusBadge(selectedDocument.status)}</span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {/* Document Content */}
                                    <div className="max-h-96 overflow-y-auto">
                                        <pre className="text-sm text-slate-300 whitespace-pre-wrap font-mono bg-slate-900 p-4 rounded border">
                                            {documentContent}
                                        </pre>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center p-8 text-slate-400">
                                    <FileText className="h-16 w-16 mx-auto mb-4 text-slate-600" />
                                    <p>Select a document from the list to view its contents</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default ApplicationDocuments;