import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Building2, Loader2, ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const FranchiseLogin = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({ email: '', password: '', company_code: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!credentials.email || !credentials.password) {
      setError('Please enter email and password');
      return;
    }
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/franchise/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: credentials.email.trim(),
          password: credentials.password.trim(),
          company_code: credentials.company_code.trim() || null
        })
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Login failed');
        return;
      }

      if (data.success) {
        localStorage.setItem('franchise_token', data.token);
        localStorage.setItem('franchise_admin', JSON.stringify(data.admin));
        localStorage.setItem('franchise_company', JSON.stringify(data.company));
        onLogin(data);
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      data-testid="franchise-login-page"
      className="min-h-screen flex items-center justify-center"
      style={{
        background: 'linear-gradient(135deg, #0c1222 0%, #111d35 50%, #0a1628 100%)'
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md mx-4"
      >
        <Card className="border-0 shadow-2xl" style={{ background: 'rgba(15, 23, 42, 0.95)', borderColor: 'rgba(14, 165, 233, 0.2)', border: '1px solid rgba(14, 165, 233, 0.2)' }}>
          <CardHeader className="text-center pb-2">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #0ea5e9, #0284c7)' }}>
                <Building2 className="w-8 h-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-white tracking-tight">Franchise Portal</CardTitle>
            <p className="text-sm text-slate-400 mt-1">Powered by FIDUS Investment Management</p>
          </CardHeader>
          <CardContent className="pt-4">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Email</Label>
                <Input
                  data-testid="franchise-login-email"
                  type="email"
                  placeholder="admin@company.com"
                  value={credentials.email}
                  onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                  className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-sky-500 focus:ring-sky-500/20"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Password</Label>
                <Input
                  data-testid="franchise-login-password"
                  type="password"
                  placeholder="Enter your password"
                  value={credentials.password}
                  onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                  className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-sky-500 focus:ring-sky-500/20"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300 text-sm">Company Code <span className="text-slate-500">(optional)</span></Label>
                <Input
                  data-testid="franchise-login-company-code"
                  type="text"
                  placeholder="e.g. acme"
                  value={credentials.company_code}
                  onChange={(e) => setCredentials({ ...credentials, company_code: e.target.value })}
                  className="bg-slate-800/60 border-slate-700 text-white placeholder:text-slate-500 focus:border-sky-500 focus:ring-sky-500/20"
                />
              </div>

              {error && (
                <div data-testid="franchise-login-error" className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                  {error}
                </div>
              )}

              <Button
                data-testid="franchise-login-submit"
                type="submit"
                disabled={loading}
                className="w-full h-11 font-semibold text-white"
                style={{ background: 'linear-gradient(135deg, #0ea5e9, #0284c7)' }}
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <a href="/" className="text-xs text-slate-500 hover:text-sky-400 transition-colors flex items-center justify-center gap-1">
                <ArrowLeft className="w-3 h-3" />
                Back to FIDUS Platform
              </a>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default FranchiseLogin;
