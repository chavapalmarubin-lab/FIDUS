import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../../utils/referralAgentAuth';
import referralAgentApi from '../../services/referralAgentApi';

const ProtectedRoute = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      if (!isAuthenticated()) {
        setLoading(false);
        setIsValid(false);
        return;
      }

      try {
        await referralAgentApi.getCurrentAgent();
        setIsValid(true);
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsValid(false);
        localStorage.removeItem('referral_agent_token');
        localStorage.removeItem('referral_agent_user');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isValid) {
    return <Navigate to="/referral-agent/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
