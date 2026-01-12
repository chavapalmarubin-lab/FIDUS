/**
 * VIKING Trading Operations - Standalone Application
 * 
 * Completely separate from FIDUS
 * Access at: /viking
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { 
  Shield, 
  Eye, 
  EyeOff, 
  Loader2,
  AlertCircle,
  Sword
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Viking-specific credentials (can be configured)
const VIKING_CREDENTIALS = {
  username: 'viking_admin',
  password: 'viking2026'
};

const VikingLogin = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Simple authentication for VIKING
    if (username === VIKING_CREDENTIALS.username && password === VIKING_CREDENTIALS.password) {
      // Store VIKING session
      localStorage.setItem('viking_authenticated', 'true');
      localStorage.setItem('viking_user', username);
      onLogin(true);
    } else {
      setError('Invalid credentials. Contact administrator.');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 flex items-center justify-center p-4">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMyMDIwMjAiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRoLTJ2LTRoMnY0em0wLTZ2LTRoLTJ2NGgyem0tNiA2di00aC00djRoNHptMC02aC00di00aDR2NHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20"></div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10"
      >
        <Card className="w-[420px] bg-gray-900/90 border-gray-800 backdrop-blur-xl shadow-2xl">
          <CardHeader className="text-center pb-2">
            {/* Viking Logo */}
            <div className="mx-auto mb-4 relative">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
                <span className="text-4xl">⚔️</span>
              </div>
              <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-green-500 border-2 border-gray-900 flex items-center justify-center">
                <Shield className="w-3 h-3 text-white" />
              </div>
            </div>
            
            <CardTitle className="text-2xl font-bold text-white">
              VIKING Trading
            </CardTitle>
            <p className="text-gray-400 text-sm mt-1">
              Trading Operations Portal
            </p>
            <p className="text-amber-500/80 text-xs mt-2">
              Account 33627673 • MEXAtlantic
            </p>
          </CardHeader>
          
          <CardContent className="pt-4">
            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 flex items-center gap-2"
                >
                  <AlertCircle className="w-4 h-4 text-red-400" />
                  <span className="text-red-400 text-sm">{error}</span>
                </motion.div>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="username" className="text-gray-300">Username</Label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="bg-gray-800/50 border-gray-700 text-white focus:border-amber-500 focus:ring-amber-500/20"
                  placeholder="Enter username"
                  required
                  data-testid="viking-username-input"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-300">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-gray-800/50 border-gray-700 text-white pr-10 focus:border-amber-500 focus:ring-amber-500/20"
                    placeholder="Enter password"
                    required
                    data-testid="viking-password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white font-semibold py-2.5 mt-2"
                data-testid="viking-login-btn"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Authenticating...
                  </>
                ) : (
                  <>
                    <Sword className="w-4 h-4 mr-2" />
                    Access VIKING Portal
                  </>
                )}
              </Button>
            </form>
            
            <div className="mt-6 pt-4 border-t border-gray-800">
              <p className="text-center text-gray-500 text-xs">
                VIKING Trading Operations • Separate from FIDUS
              </p>
              <p className="text-center text-gray-600 text-xs mt-1">
                Real-time MT4 Performance Analytics
              </p>
            </div>
          </CardContent>
        </Card>
        
        {/* Demo credentials hint */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-4 text-center"
        >
          <p className="text-gray-600 text-xs">
            Demo: viking_admin / viking2026
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default VikingLogin;
