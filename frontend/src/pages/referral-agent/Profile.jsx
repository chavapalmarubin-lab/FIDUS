import React, { useState, useEffect, useRef } from 'react';
import { User, Mail, Phone, Link as LinkIcon, QrCode, Copy, Check, Download, BarChart3, Share2, MessageCircle } from 'lucide-react';
import Layout from '../../components/referral-agent/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import referralAgentApi from '../../services/referralAgentApi';
import QRCode from 'qrcode';

const Profile = () => {
  const [loading, setLoading] = useState(true);
  const [agent, setAgent] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await referralAgentApi.getCurrentAgent();
      setAgent(response);
      
      // Generate QR code for referral link
      if (response.referralLink) {
        const qrDataUrl = await QRCode.toDataURL(response.referralLink, {
          width: 300,
          margin: 2,
          color: {
            dark: '#0891B2',
            light: '#FFFFFF'
          }
        });
        setQrCodeDataUrl(qrDataUrl);
      }
    } catch (err) {
      console.error('Profile error:', err);
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const copyReferralLink = async () => {
    try {
      await navigator.clipboard.writeText(agent.referralLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Copy failed:', err);
    }
  };

  const downloadQRCode = () => {
    const link = document.createElement('a');
    link.download = `referral-qr-${agent.referralCode}.png`;
    link.href = qrCodeDataUrl;
    link.click();
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6">
          <div className="animate-pulse">
            <div className="h-8 w-48 bg-slate-800 rounded mb-2"></div>
            <div className="h-4 w-64 bg-slate-800 rounded"></div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-96 bg-slate-800 rounded"></div>
            <div className="h-96 bg-slate-800 rounded"></div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Agent Toolkit</h1>
          <p className="text-slate-400">Your profile and referral tools</p>
        </div>

        {error && (
          <Alert variant="destructive" className="bg-red-950 border-red-900 text-red-200">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Profile Information */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <User className="h-5 w-5 text-cyan-400" />
                Profile Information
              </CardTitle>
              <CardDescription className="text-slate-400">Your agent account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                <User className="h-5 w-5 text-slate-400 mt-0.5" />
                <div>
                  <div className="text-sm text-slate-400">Full Name</div>
                  <div className="text-white font-medium">{agent?.name || 'N/A'}</div>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                <Mail className="h-5 w-5 text-slate-400 mt-0.5" />
                <div>
                  <div className="text-sm text-slate-400">Email</div>
                  <div className="text-white font-medium">{agent?.email || 'N/A'}</div>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                <Phone className="h-5 w-5 text-slate-400 mt-0.5" />
                <div>
                  <div className="text-sm text-slate-400">Referral Code</div>
                  <div className="text-cyan-400 font-bold text-lg">{agent?.referralCode || 'N/A'}</div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-700">
                <div className="text-sm text-slate-400 mb-2">Account Stats</div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-cyan-900/20 rounded-lg border border-cyan-800/50">
                    <div className="text-2xl font-bold text-cyan-400">{agent?.loginCount || 0}</div>
                    <div className="text-xs text-slate-400">Total Logins</div>
                  </div>
                  <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                    <div className="text-2xl font-bold text-white">{agent?.lastLogin ? 'Active' : 'New'}</div>
                    <div className="text-xs text-slate-400">Status</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Referral Tools */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <LinkIcon className="h-5 w-5 text-cyan-400" />
                Referral Tools
              </CardTitle>
              <CardDescription className="text-slate-400">Share your unique referral link</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Referral Link */}
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Your Referral Link</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={agent?.referralLink || ''}
                    readOnly
                    className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-white text-sm"
                  />
                  <Button
                    onClick={copyReferralLink}
                    className="bg-cyan-600 hover:bg-cyan-700 text-white"
                  >
                    {copied ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              {/* QR Code */}
              {qrCodeDataUrl && (
                <div>
                  <label className="text-sm text-slate-400 mb-2 block">QR Code</label>
                  <div className="bg-white p-4 rounded-lg inline-block">
                    <img src={qrCodeDataUrl} alt="Referral QR Code" className="w-48 h-48" />
                  </div>
                  <Button
                    onClick={downloadQRCode}
                    variant="outline"
                    className="w-full mt-3 border-slate-700 text-slate-300 hover:bg-slate-800"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download QR Code
                  </Button>
                </div>
              )}

              {/* Link Analytics Placeholder */}
              <div className="pt-4 border-t border-slate-700">
                <div className="flex items-center gap-2 text-sm text-slate-400 mb-3">
                  <BarChart3 className="h-4 w-4" />
                  Link Analytics
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-3 bg-slate-800/50 rounded-lg text-center">
                    <div className="text-xl font-bold text-white">-</div>
                    <div className="text-xs text-slate-400">Clicks</div>
                  </div>
                  <div className="p-3 bg-slate-800/50 rounded-lg text-center">
                    <div className="text-xl font-bold text-white">-</div>
                    <div className="text-xs text-slate-400">Leads</div>
                  </div>
                  <div className="p-3 bg-slate-800/50 rounded-lg text-center">
                    <div className="text-xl font-bold text-white">-</div>
                    <div className="text-xs text-slate-400">Rate</div>
                  </div>
                </div>
                <p className="text-xs text-slate-500 mt-3 text-center">Analytics tracking coming soon</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Marketing Materials Section */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Download className="h-5 w-5 text-cyan-400" />
              Marketing Materials
            </CardTitle>
            <CardDescription className="text-slate-400">Downloadable assets for promoting FIDUS investments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 text-center">
                <div className="h-24 bg-gradient-to-br from-cyan-600 to-blue-700 rounded mb-3 flex items-center justify-center">
                  <span className="text-white font-bold">FIDUS</span>
                </div>
                <div className="text-white font-medium mb-1">Investment Brochure</div>
                <div className="text-xs text-slate-400 mb-3">PDF · 2.3 MB</div>
                <Button variant="outline" className="w-full border-slate-700 text-slate-300 hover:bg-slate-800" size="sm" disabled>
                  Coming Soon
                </Button>
              </div>

              <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 text-center">
                <div className="h-24 bg-gradient-to-br from-purple-600 to-pink-700 rounded mb-3 flex items-center justify-center">
                  <span className="text-white font-bold">SOCIAL</span>
                </div>
                <div className="text-white font-medium mb-1">Social Media Kit</div>
                <div className="text-xs text-slate-400 mb-3">ZIP · 5.1 MB</div>
                <Button variant="outline" className="w-full border-slate-700 text-slate-300 hover:bg-slate-800" size="sm" disabled>
                  Coming Soon
                </Button>
              </div>

              <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 text-center">
                <div className="h-24 bg-gradient-to-br from-green-600 to-teal-700 rounded mb-3 flex items-center justify-center">
                  <span className="text-white font-bold">PRESO</span>
                </div>
                <div className="text-white font-medium mb-1">Pitch Deck</div>
                <div className="text-xs text-slate-400 mb-3">PPTX · 3.7 MB</div>
                <Button variant="outline" className="w-full border-slate-700 text-slate-300 hover:bg-slate-800" size="sm" disabled>
                  Coming Soon
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Profile;