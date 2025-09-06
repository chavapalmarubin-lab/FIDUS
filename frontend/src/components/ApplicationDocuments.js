import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
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
    AlertCircle
} from 'lucide-react';

const ApplicationDocuments = () => {
    const [documents, setDocuments] = useState([]);
    const [selectedDocument, setSelectedDocument] = useState(null);
    const [documentContent, setDocumentContent] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [systemInfo, setSystemInfo] = useState({});

    useEffect(() => {
        fetchDocuments();
        fetchSystemInfo();
    }, []);

    const fetchDocuments = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/documents`, {
                headers: {
                    'Authorization': `Bearer ${JSON.parse(localStorage.getItem('fidus_user')).token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setDocuments(data.documents || []);
            } else {
                throw new Error('Failed to fetch documents');
            }
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