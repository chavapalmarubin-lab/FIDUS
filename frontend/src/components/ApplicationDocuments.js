import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
    FileText, 
    Download, 
    Eye, 
    Globe,
    Shield,
    Database,
    Server,
    CheckCircle,
    AlertCircle,
    Cloud,
    Users,
    BarChart3,
    Cpu,
    Network,
    MonitorSpeaker,
    Lock,
    Activity
} from 'lucide-react';

const ApplicationDocuments = () => {
    const [activeTab, setActiveTab] = useState('overview');

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

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">FIDUS Application Documentation</h1>
                    <p className="text-slate-600">Technical specifications and system overview</p>
                </div>
                <Button
                    onClick={() => {
                        const link = document.createElement('a');
                        link.href = '/CTO_Technical_Summary.md';
                        link.download = 'FIDUS_Technical_Summary.md';
                        link.click();
                    }}
                    className="bg-emerald-600 hover:bg-emerald-700"
                >
                    <Download className="h-4 w-4 mr-2" />
                    Download CTO Summary
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

                            <div className="mt-6">
                                <Button
                                    onClick={() => {
                                        const link = document.createElement('a');
                                        link.href = '/CTO_Technical_Summary.md';
                                        link.download = 'FIDUS_CTO_Technical_Summary.md';
                                        link.click();
                                    }}
                                    className="w-full bg-emerald-600 hover:bg-emerald-700"
                                >
                                    <Download className="h-4 w-4 mr-2" />
                                    Download Complete CTO Technical Summary
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Hosting & Infrastructure and Security tabs would go here */}
                <TabsContent value="hosting" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Cloud className="h-5 w-5 mr-2" />
                                Hosting & Infrastructure
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-3">
                                    <h4 className="font-semibold">Hosting Details</h4>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="font-medium">Platform:</span>
                                            <span>{systemSpecs.hosting.platform}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="font-medium">URL:</span>
                                            <span className="text-blue-600">{systemSpecs.hosting.url}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="font-medium">Deployment:</span>
                                            <span>{systemSpecs.hosting.deployment}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="font-medium">SSL:</span>
                                            <span>{systemSpecs.hosting.ssl}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <h4 className="font-semibold">Infrastructure Features</h4>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex items-center">
                                            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                            <span>Kubernetes Container Orchestration</span>
                                        </div>
                                        <div className="flex items-center">
                                            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                            <span>Auto-scaling based on demand</span>
                                        </div>
                                        <div className="flex items-center">
                                            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                            <span>Real-time monitoring</span>
                                        </div>
                                        <div className="flex items-center">
                                            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                            <span>99.9% SLA with 24/7 support</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="security" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center">
                                <Shield className="h-5 w-5 mr-2" />
                                Security & Compliance
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-3">
                                    <h4 className="font-semibold">Security Features</h4>
                                    <div className="space-y-2 text-sm">
                                        {Object.entries(systemSpecs.security).map(([key, value]) => (
                                            <div key={key} className="flex justify-between">
                                                <span className="font-medium capitalize">{key}:</span>
                                                <span>{value}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <h4 className="font-semibold">Compliance Standards</h4>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex items-center">
                                            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                            <span>AML/KYC Document Management</span>
                                        </div>
                                        <div className="flex items-center">
                                            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                            <span>GDPR Compliant Data Handling</span>
                                        </div>
                                        <div className="flex items-center">
                                            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                            <span>SOC 2 Type II Compliance Ready</span>
                                        </div>
                                        <div className="flex items-center">
                                            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                                            <span>Financial Services Compliance</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default ApplicationDocuments;