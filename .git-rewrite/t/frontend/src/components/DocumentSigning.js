import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Upload, FileText, Eye, Download, PenTool, Send, 
  CheckCircle, AlertCircle, RefreshCw, X, Mail
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';

const DocumentSigning = () => {
  const [documents, setDocuments] = useState([]);
  const [currentDocument, setCurrentDocument] = useState(null);
  const [pdfData, setPdfData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Signature state
  const [isSigningMode, setIsSigningMode] = useState(false);
  const [signaturePosition, setSignaturePosition] = useState({ x: 0, y: 0, page: 1 });
  const [signatureText, setSignatureText] = useState('');
  const [notificationEmail, setNotificationEmail] = useState('');
  const [sendNotification, setSendNotification] = useState(false);
  
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const signatureCanvasRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setLoading(true);
      setError('');

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/documents/upload`, {
        method: 'POST',
        credentials: 'include',
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setSuccess('Document uploaded successfully!');
        setDocuments(prev => [...prev, data.document]);
        
        // Auto-load the document for viewing
        await viewDocument(data.document.document_id);
      } else {
        throw new Error(data.error || 'Failed to upload document');
      }

    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const viewDocument = async (documentId) => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/documents/${documentId}/pdf`, {
        credentials: 'include'
      });

      const data = await response.json();

      if (data.success) {
        setCurrentDocument(documentId);
        setPdfData(data);
        setIsSigningMode(false);
        
        // Load PDF in viewer
        setTimeout(() => {
          displayPDF(data.pdf_data);
        }, 100);
      } else {
        throw new Error(data.error || 'Failed to load document');
      }

    } catch (err) {
      console.error('View document error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const displayPDF = (base64Data) => {
    try {
      // Create PDF blob
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);

      // Display in iframe
      const iframe = document.getElementById('pdf-viewer');
      if (iframe) {
        iframe.src = url;
      }
    } catch (err) {
      console.error('PDF display error:', err);
      setError('Failed to display PDF');
    }
  };

  const startSigning = () => {
    setIsSigningMode(true);
    setError('');
    setSuccess('');
  };

  const handleCanvasClick = (event) => {
    if (!isSigningMode) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    setSignaturePosition({ x, y, page: 1 });
    
    // Draw signature preview
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'rgba(255, 0, 0, 0.7)';
    ctx.fillRect(x, y, 120, 40);
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.fillText('Signature Here', x + 5, y + 25);
  };

  const drawSignature = () => {
    const canvas = signatureCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Simple signature drawing
    ctx.strokeStyle = '#1e40af';
    ctx.lineWidth = 2;
    ctx.font = '16px cursive';
    ctx.fillStyle = '#1e40af';
    
    if (signatureText) {
      ctx.fillText(signatureText, 10, 30);
    }
  };

  const signDocument = async () => {
    if (!currentDocument || !signatureText.trim()) {
      setError('Please enter your signature text');
      return;
    }

    try {
      setLoading(true);
      setError('');

      // Get signature image data
      const canvas = signatureCanvasRef.current;
      const signatureImageData = canvas ? canvas.toDataURL().split(',')[1] : null;

      const signatureData = {
        x: signaturePosition.x,
        y: signaturePosition.y,
        page: signaturePosition.page,
        text: signatureText,
        image_data: signatureImageData,
        send_notification: sendNotification,
        notification_email: notificationEmail
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/documents/${currentDocument}/sign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(signatureData)
      });

      const data = await response.json();

      if (data.success) {
        setSuccess('Document signed successfully!');
        setIsSigningMode(false);
        setSignatureText('');
        
        // Optional: Reload document to show signed version
        if (data.signed_document_url) {
          setTimeout(() => {
            window.open(data.signed_document_url, '_blank');
          }, 1000);
        }
      } else {
        throw new Error(data.error || 'Failed to sign document');
      }

    } catch (err) {
      console.error('Sign document error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (signatureText) {
      drawSignature();
    }
  }, [signatureText]);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Document Signing
        </h1>
        <p className="text-gray-600">
          Upload, view, and electronically sign documents
        </p>
      </div>

      {error && (
        <Alert className="bg-red-50 border-red-200 mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200 mb-4">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Documents
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileUpload}
                className="hidden"
              />

              <div className="space-y-2">
                {documents.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No documents uploaded</p>
                    <p className="text-sm">Click Upload to add documents</p>
                  </div>
                ) : (
                  documents.map((doc) => (
                    <Card
                      key={doc.document_id}
                      className={`cursor-pointer transition-all ${
                        currentDocument === doc.document_id
                          ? 'ring-2 ring-blue-500 bg-blue-50'
                          : 'hover:shadow-md'
                      }`}
                      onClick={() => viewDocument(doc.document_id)}
                    >
                      <CardContent className="p-3">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-8 w-8 text-blue-600" />
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm truncate">
                              {doc.filename}
                            </p>
                            <p className="text-xs text-gray-500">
                              {doc.page_count > 0 && `${doc.page_count} pages • `}
                              {Math.round(doc.file_size / 1024)} KB
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Document Viewer */}
        <div className="lg:col-span-2">
          <Card className="h-[600px]">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Document Viewer</span>
                {currentDocument && (
                  <div className="space-x-2">
                    {!isSigningMode ? (
                      <Button
                        onClick={startSigning}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <PenTool className="h-4 w-4 mr-2" />
                        Sign Document
                      </Button>
                    ) : (
                      <Button
                        onClick={() => setIsSigningMode(false)}
                        variant="outline"
                      >
                        <X className="h-4 w-4 mr-2" />
                        Cancel Signing
                      </Button>
                    )}
                  </div>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="h-full p-0">
              {currentDocument ? (
                <div className="relative h-full">
                  <iframe
                    id="pdf-viewer"
                    className="w-full h-full border-0"
                    title="PDF Viewer"
                  />
                  
                  {isSigningMode && (
                    <canvas
                      ref={canvasRef}
                      onClick={handleCanvasClick}
                      className="absolute inset-0 w-full h-full cursor-crosshair bg-transparent"
                      style={{ pointerEvents: 'auto', zIndex: 10 }}
                    />
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <Eye className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">Select a document to view</p>
                    <p className="text-sm">Upload a document or select from the list</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Signature Modal */}
      {isSigningMode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-md mx-4">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Add Electronic Signature</h3>
                <button
                  onClick={() => setIsSigningMode(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Signature Text
                  </label>
                  <input
                    type="text"
                    value={signatureText}
                    onChange={(e) => setSignatureText(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your full name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Signature Preview
                  </label>
                  <canvas
                    ref={signatureCanvasRef}
                    width={300}
                    height={50}
                    className="border border-gray-300 rounded-md bg-gray-50"
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="sendNotification"
                    checked={sendNotification}
                    onChange={(e) => setSendNotification(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor="sendNotification" className="text-sm text-gray-700">
                    Send email notification
                  </label>
                </div>

                {sendNotification && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notification Email
                    </label>
                    <input
                      type="email"
                      value={notificationEmail}
                      onChange={(e) => setNotificationEmail(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="recipient@example.com"
                    />
                  </div>
                )}

                <div className="text-sm text-gray-600">
                  Click on the document above to position your signature, then click "Sign Document" to complete the process.
                </div>

                <div className="flex justify-end space-x-3">
                  <Button
                    onClick={() => setIsSigningMode(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={signDocument}
                    disabled={loading || !signatureText.trim()}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Signing...
                      </>
                    ) : (
                      <>
                        <PenTool className="h-4 w-4 mr-2" />
                        Sign Document
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentSigning;