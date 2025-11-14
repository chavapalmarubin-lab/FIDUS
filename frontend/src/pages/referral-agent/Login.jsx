import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { Label } from '../../components/ui/label';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Mail, Lock, AlertCircle } from 'lucide-react';
import referralAgentApi from '../../services/referralAgentApi';
import { setAuthToken, setCurrentAgent, isAuthenticated } from '../../utils/referralAgentAuth';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/referral-agent/dashboard');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await referralAgentApi.login(email, password);
      
      if (response.success && response.token) {
        setAuthToken(response.token);
        setCurrentAgent(response.agent);
        navigate('/referral-agent/dashboard');
      } else {
        setError(response.message || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      console.error('Login error:', err);
      if (err.response?.status === 401) {
        setError('Invalid email or password');
      } else if (err.response?.status === 403) {
        setError('Access denied. Please contact administrator.');
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <img
            src="/fidus-logo.png"
            alt="FIDUS"
            className="h-16 w-auto mx-auto mb-4"
          />
          <h1 className="text-3xl font-bold text-gray-900">Referral Agent Portal</h1>
          <p className="text-gray-600 mt-2">Sign in to manage your leads and commissions</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Welcome Back</CardTitle>
            <CardDescription>Enter your credentials to access your portal</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="agent@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <span className="animate-spin mr-2">⏳</span>
                    Signing in...
                  </span>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-gray-600">
              <p>Need help? Contact your administrator</p>
            </div>
          </CardContent>
        </Card>

        <div className="mt-6 text-center text-xs text-gray-500">
          <p>&copy; 2025 FIDUS. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
