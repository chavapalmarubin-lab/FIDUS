import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Calendar } from "./ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";  
import { LogOut, Search, Calendar as CalendarIcon, DollarSign, TrendingUp, TrendingDown, Filter, FileText, ArrowDownCircle, Wallet, Globe, Mail } from "lucide-react";
import { format } from "date-fns";
import apiAxios from "../utils/apiAxios";
import DocumentPortal from "./DocumentPortal";
import CurrencySelector from "./CurrencySelector";
import useCurrency from "../hooks/useCurrency";
import ClientGoogleWorkspace from "./ClientGoogleWorkspace";

import RedemptionManagement from "./RedemptionManagement";
import InvestmentCalendar from "./InvestmentCalendar";
import ClientWallet from "./ClientWallet";
import InvestmentCalculator from "./InvestmentCalculator";
import EnhancedFundCard from "./EnhancedFundCard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Fund information configuration
const FUND_INFO = {
  CORE: {
    icon: '🛡️',
    interestRate: 1.5,
    annualReturn: 18,
    riskLevel: 'Conservative',
    description: 'Core strategy focused on capital preservation with steady, reliable returns',
    minInvestment: 10000,
    maxSuggested: 50000,
    lockPeriod: 'None',
    highlight: 'Safe and steady growth'
  },
  BALANCE: {
    icon: '⚖️',
    interestRate: 2.5,
    annualReturn: 30,
    riskLevel: 'Moderate',
    description: 'Balanced risk/reward with monthly guaranteed returns',
    minInvestment: 25000,
    maxSuggested: 100000,
    lockPeriod: 'None',
    highlight: 'Best balance of safety and returns'
  },
  DYNAMIC: {
    icon: '🎯',
    interestRate: 3.5,
    annualReturn: 42,
    riskLevel: 'Moderate-High',
    description: 'Dynamic allocation based on market conditions and opportunities',
    minInvestment: 50000,
    maxSuggested: 150000,
    lockPeriod: '3 months',
    highlight: 'Higher returns for active traders'
  },
  UNLIMITED: {
    icon: '🚀',
    interestRate: 4.0,
    annualReturn: 48,
    riskLevel: 'High',
    description: 'Maximum returns for experienced investors with higher risk tolerance',
    minInvestment: 100000,
    maxSuggested: 250000,
    lockPeriod: '6 months',
    highlight: 'Premium returns for serious investors'
  }
};

const ClientDashboard = ({ user, onLogout }) => {
  const [clientData, setClientData] = useState(null);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({ from: null, to: null });
  const [fundFilter, setFundFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCurrency, setSelectedCurrency] = useState('USD');

  // Profile editing state
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || ''
  });
  const [profileLoading, setProfileLoading] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current: '',
    new: '',
    confirm: ''
  });
  const [passwordLoading, setPasswordLoading] = useState(false);

  // Currency conversion hook
  const { 
    convertAmount: convertCurrencyAmount, 
    formatCurrency: formatCurrencyAmount 
  } = useCurrency();

  useEffect(() => {
    fetchClientData();
  }, [user.id]);

  const fetchClientData = async () => {
    try {
      const response = await apiAxios.get(`/client/${user.id}/data`);
      setClientData(response.data);
      setFilteredTransactions(response.data.transactions);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching client data:", error);
      setLoading(false);
    }
  };

  // Profile management functions
  const handlePhotoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setProfileLoading(true);
    try {
      const formData = new FormData();
      formData.append('photo', file);

      const response = await apiAxios.post('/client/profile/photo', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        // Update user profile picture in local state
        user.profile_picture = response.data.photo_url;
        alert('Profile photo updated successfully!');
      }
    } catch (error) {
      console.error('Photo upload error:', error);
      alert('Failed to update profile photo: ' + (error.response?.data?.detail || error.message));
    } finally {
      setProfileLoading(false);
    }
  };

  const handleProfileUpdate = async () => {
    setProfileLoading(true);
    try {
      const response = await apiAxios.put('/client/profile', profileData);

      if (response.data.success) {
        // Update user data in local state
        Object.assign(user, response.data.user);
        alert('Profile updated successfully!');
      }
    } catch (error) {
      console.error('Profile update error:', error);
      alert('Failed to update profile: ' + (error.response?.data?.detail || error.message));
    } finally {
      setProfileLoading(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordData.new !== passwordData.confirm) {
      alert('New passwords do not match');
      return;
    }
    
    if (passwordData.new.length < 6) {
      alert('New password must be at least 6 characters long');
      return;
    }

    setPasswordLoading(true);
    try {
      const response = await apiAxios.post('/auth/change-password', {
        username: user.username,
        current_password: passwordData.current,
        new_password: passwordData.new
      });

      if (response.data.success) {
        alert('Password changed successfully!');
        setShowPasswordChange(false);
        setPasswordData({ current: '', new: '', confirm: '' });
      }
    } catch (error) {
      console.error('Password change error:', error);
      alert('Failed to change password: ' + (error.response?.data?.detail || error.message));
    } finally {
      setPasswordLoading(false);
    }
  };

  // Initialize profile data when user data loads - fetch fresh from backend
  useEffect(() => {
    const fetchCurrentProfile = async () => {
      try {
        // Get fresh user data from backend instead of using cached session data
        const response = await apiAxios.get('/client/profile');
        if (response.data.success && response.data.user) {
          setProfileData({
            name: response.data.user.name || '',
            email: response.data.user.email || '',
            phone: response.data.user.phone || ''
          });
        }
      } catch (error) {
        // Fallback to session user data if API call fails
        if (user) {
          setProfileData({
            name: user.name || '',
            email: user.email || '',
            phone: user.phone || ''
          });
        }
      }
    };
    
    fetchCurrentProfile();
  }, [user]);

  const applyFilters = () => {
    if (!clientData) return;

    let filtered = [...clientData.transactions];

    // Date range filter
    if (dateRange.from) {
      filtered = filtered.filter(t => new Date(t.date) >= dateRange.from);
    }
    if (dateRange.to) {
      filtered = filtered.filter(t => new Date(t.date) <= dateRange.to);
    }

    // Fund type filter
    if (fundFilter !== "all") {
      filtered = filtered.filter(t => t.fund_type === fundFilter);
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(t => 
        t.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredTransactions(filtered);
  };

  useEffect(() => {
    applyFilters();
  }, [dateRange, fundFilter, searchTerm, clientData]);

  const formatCurrency = (amount) => {
    if (selectedCurrency === 'USD') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
      }).format(Math.abs(amount));
    } else {
      // Convert to selected currency and format
      const convertedAmount = convertCurrencyAmount(Math.abs(amount), 'USD', selectedCurrency);
      return formatCurrencyAmount(convertedAmount, selectedCurrency);
    }
  };

  const formatCurrencyWithConversion = (amount) => {
    const primaryAmount = formatCurrency(amount);
    if (selectedCurrency !== 'USD') {
      const usdAmount = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
      }).format(Math.abs(amount));
      return { primary: primaryAmount, secondary: usdAmount };
    }
    return { primary: primaryAmount, secondary: null };
  };

  const formatDate = (dateString) => {
    return format(new Date(dateString), 'MMM dd, yyyy');
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <div className="header-logo flex items-center p-4">
            <img 
              src="/fidus-logo.png"
              alt="FIDUS Logo"
              style={{ 
                height: '48px', 
                width: 'auto',
                maxWidth: '180px',
                objectFit: 'contain'
              }}
            />
          </div>
        </div>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-white text-xl">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">

        <div className="flex items-center gap-4">
          <span className="text-slate-300">{user.name}</span>
          <Button onClick={onLogout} className="logout-btn">
            <LogOut size={16} className="mr-2" />
            Logout
          </Button>
        </div>
      </div>

      <div className="p-6 max-w-7xl mx-auto">
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-5 bg-slate-800 border-slate-600 mb-6">
            <TabsTrigger value="overview" className="text-white data-[state=active]:bg-cyan-600">
              <DollarSign size={16} className="mr-2" />
              Account Overview
            </TabsTrigger>
            <TabsTrigger value="wallet" className="text-white data-[state=active]:bg-cyan-600">
              <Wallet size={16} className="mr-2" />
              Wallet
            </TabsTrigger>
            <TabsTrigger value="redemptions" className="text-white data-[state=active]:bg-cyan-600">
              <ArrowDownCircle size={16} className="mr-2" />
              Redemptions
            </TabsTrigger>
            <TabsTrigger value="calendar" className="text-white data-[state=active]:bg-cyan-600">
              <CalendarIcon size={16} className="mr-2" />
              Calendar
            </TabsTrigger>
            <TabsTrigger value="google-workspace" className="text-white data-[state=active]:bg-cyan-600">
              <Globe size={16} className="mr-2" />
              My FIDUS Workspace
            </TabsTrigger>
            <TabsTrigger value="profile" className="text-white data-[state=active]:bg-cyan-600">
              <img src={user.profile_picture || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"} 
                   alt="Profile" className="w-4 h-4 rounded-full mr-2" />
              My Profile
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
        {/* Profile Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8"
        >
          {/* Profile Card */}
          <Card className="dashboard-card lg:col-span-1">
            <CardContent className="p-6 text-center">
              <motion.img
                src={user.profile_picture}
                alt={user.name}
                className="w-24 h-24 rounded-full mx-auto mb-4 object-cover"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              />
              <h2 className="text-xl font-bold text-white mb-2">{user.name}</h2>
              <p className="text-slate-400 text-sm">{user.email}</p>
              <div className="mt-4 space-y-2 text-sm text-slate-300">
                <div>FIDUS Account: <span className="text-cyan-400 font-semibold">124567</span></div>
                <div>Start Contract: 04-2020</div>
                <div>Renew Contract: 04-2025</div>
              </div>
              
              {/* TradingHub Gold Provider Link */}
              <div className="mt-4 pt-4 border-t border-slate-700">
                <a 
                  href="https://ratings.multibankfx.com/widgets/ratings/1359?widgetKey=social_platform_ratings"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-700 hover:to-yellow-600 text-white text-sm font-semibold rounded-lg transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-yellow-500/50"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  TradingHub-Gold
                </a>
              </div>
            </CardContent>
          </Card>

          {/* Account Balance */}
          <Card className="dashboard-card lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <div className="flex items-center">
                  <DollarSign className="mr-2" size={20} />
                  Account Balance
                </div>
                <div className="flex-shrink-0">
                  <CurrencySelector
                    selectedCurrency={selectedCurrency}
                    onCurrencyChange={setSelectedCurrency}
                    showRates={false}
                    showSummary={false}
                    size="sm"
                  />
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center">
                  <div className="balance-amount">
                    {clientData && formatCurrency(clientData.balance.total_balance)}
                  </div>
                  {selectedCurrency !== 'USD' && clientData && (
                    <div className="text-slate-400 text-sm mt-1">
                      {new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        minimumFractionDigits: 2
                      }).format(clientData.balance.total_balance)} USD
                    </div>
                  )}
                </div>
                
                {/* All 4 Fund Balances */}
                <div className="grid grid-cols-2 gap-4">
                  {/* CORE Fund */}
                  <div>
                    <div className="balance-label">CORE Fund</div>
                    <div className="text-2xl font-bold text-orange-400">
                      {clientData && formatCurrency(clientData.balance.core_balance)}
                    </div>
                    {selectedCurrency !== 'USD' && clientData && clientData.balance.core_balance > 0 && (
                      <div className="text-xs text-gray-500">
                        {new Intl.NumberFormat('en-US', {
                          style: 'currency',
                          currency: 'USD'
                        }).format(clientData.balance.core_balance)} USD
                      </div>
                    )}
                    <div className="text-xs text-gray-400">
                      {clientData && clientData.balance.core_balance > 0 ? 'ACTIVE' : 'NO INVESTMENT'}
                    </div>
                  </div>
                  
                  {/* BALANCE Fund */}
                  <div>
                    <div className="balance-label">BALANCE Fund</div>
                    <div className="text-2xl font-bold text-cyan-400">
                      {clientData && formatCurrency(clientData.balance.balance_balance)}
                    </div>
                    {selectedCurrency !== 'USD' && clientData && clientData.balance.balance_balance > 0 && (
                      <div className="text-xs text-gray-500">
                        {new Intl.NumberFormat('en-US', {
                          style: 'currency',
                          currency: 'USD'
                        }).format(clientData.balance.balance_balance)} USD
                      </div>
                    )}
                    <div className="text-xs text-gray-400">
                      {clientData && clientData.balance.balance_balance > 0 ? 'ACTIVE' : 'NO INVESTMENT'}
                    </div>
                  </div>
                  
                  {/* DYNAMIC Fund */}
                  <div>
                    <div className="balance-label">DYNAMIC Fund</div>
                    <div className="text-2xl font-bold text-green-400">
                      {clientData && formatCurrency(clientData.balance.dynamic_balance)}
                    </div>
                    {selectedCurrency !== 'USD' && clientData && clientData.balance.dynamic_balance > 0 && (
                      <div className="text-xs text-gray-500">
                        {new Intl.NumberFormat('en-US', {
                          style: 'currency',
                          currency: 'USD'
                        }).format(clientData.balance.dynamic_balance)} USD
                      </div>
                    )}
                    <div className="text-xs text-gray-400">
                      {clientData && clientData.balance.dynamic_balance > 0 ? 'ACTIVE' : 'NO INVESTMENT'}
                    </div>
                  </div>
                  
                  {/* UNLIMITED Fund */}
                  <div>
                    <div className="balance-label">UNLIMITED Fund</div>
                    <div className="text-2xl font-bold text-purple-400">
                      {clientData && formatCurrency(clientData.balance.unlimited_balance)}
                    </div>
                    {selectedCurrency !== 'USD' && clientData && clientData.balance.unlimited_balance > 0 && (
                      <div className="text-xs text-gray-500">
                        {new Intl.NumberFormat('en-US', {
                          style: 'currency',
                          currency: 'USD'
                        }).format(clientData.balance.unlimited_balance)} USD
                      </div>
                    )}
                    <div className="text-xs text-gray-400">
                      {clientData && clientData.balance.unlimited_balance > 0 ? 'ACTIVE' : 'NO INVESTMENT'}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Monthly Statement */}
          <Card className="dashboard-card lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-white text-sm">Month Statement</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {clientData && (
                <>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Initial Balance</span>
                    <span className="text-white">{formatCurrency(clientData.monthly_statement.initial_balance)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Profit</span>
                    <span className="text-green-400 flex items-center">
                      <TrendingUp size={14} className="mr-1" />
                      {clientData.monthly_statement.profit_percentage}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm font-semibold">
                    <span className="text-slate-400">Final Balance</span>
                    <span className="text-cyan-400">{formatCurrency(clientData.monthly_statement.final_balance)}</span>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Enhanced Fund Cards Section */}
        {clientData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mb-8"
          >
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
              <DollarSign className="mr-2" size={24} />
              Your Investment Funds
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* CORE Fund Card */}
              <EnhancedFundCard
                fundName="CORE FUND"
                fundInfo={FUND_INFO.CORE}
                balance={clientData.balance.core_balance}
                isActive={clientData.balance.core_balance > 0}
                monthlyEarnings={clientData.balance.core_balance * FUND_INFO.CORE.interestRate / 100}
                formatCurrency={formatCurrency}
                selectedCurrency={selectedCurrency}
              />
              
              {/* BALANCE Fund Card */}
              <EnhancedFundCard
                fundName="BALANCE FUND"
                fundInfo={FUND_INFO.BALANCE}
                balance={clientData.balance.balance_balance}
                isActive={clientData.balance.balance_balance > 0}
                monthlyEarnings={clientData.balance.balance_balance * FUND_INFO.BALANCE.interestRate / 100}
                formatCurrency={formatCurrency}
                selectedCurrency={selectedCurrency}
              />
              
              {/* DYNAMIC Fund Card */}
              <EnhancedFundCard
                fundName="DYNAMIC FUND"
                fundInfo={FUND_INFO.DYNAMIC}
                balance={clientData.balance.dynamic_balance}
                isActive={clientData.balance.dynamic_balance > 0}
                monthlyEarnings={clientData.balance.dynamic_balance * FUND_INFO.DYNAMIC.interestRate / 100}
                formatCurrency={formatCurrency}
                selectedCurrency={selectedCurrency}
              />
              
              {/* UNLIMITED Fund Card */}
              <EnhancedFundCard
                fundName="UNLIMITED FUND"
                fundInfo={FUND_INFO.UNLIMITED}
                balance={clientData.balance.unlimited_balance}
                isActive={clientData.balance.unlimited_balance > 0}
                monthlyEarnings={clientData.balance.unlimited_balance * FUND_INFO.UNLIMITED.interestRate / 100}
                formatCurrency={formatCurrency}
                selectedCurrency={selectedCurrency}
              />
            </div>
          </motion.div>
        )}

        {/* Investment Opportunities Section - Show calculators for inactive funds */}
        {clientData && (() => {
          // Calculate current monthly earnings from active funds
          const currentMonthlyEarnings = (
            (clientData.balance.core_balance * FUND_INFO.CORE.interestRate / 100) +
            (clientData.balance.balance_balance * FUND_INFO.BALANCE.interestRate / 100) +
            (clientData.balance.dynamic_balance * FUND_INFO.DYNAMIC.interestRate / 100) +
            (clientData.balance.unlimited_balance * FUND_INFO.UNLIMITED.interestRate / 100)
          );
          
          // Get inactive funds (with zero balance)
          const inactiveFunds = [];
          if (clientData.balance.core_balance === 0) inactiveFunds.push({ type: 'CORE', info: FUND_INFO.CORE, name: 'CORE FUND' });
          if (clientData.balance.balance_balance === 0) inactiveFunds.push({ type: 'BALANCE', info: FUND_INFO.BALANCE, name: 'BALANCE FUND' });
          if (clientData.balance.dynamic_balance === 0) inactiveFunds.push({ type: 'DYNAMIC', info: FUND_INFO.DYNAMIC, name: 'DYNAMIC FUND' });
          if (clientData.balance.unlimited_balance === 0) inactiveFunds.push({ type: 'UNLIMITED', info: FUND_INFO.UNLIMITED, name: 'UNLIMITED FUND' });
          
          if (inactiveFunds.length > 0) {
            return (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="investment-opportunities bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-8 mb-8"
              >
                <div className="section-header text-center mb-8">
                  <h2 className="text-3xl font-bold mb-3">
                    <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                      💰 Grow Your Earnings - Investment Opportunities
                    </span>
                  </h2>
                  <p className="text-slate-400 text-base max-w-2xl mx-auto">
                    See how much more you could earn by diversifying your investments across our other funds
                  </p>
                </div>
                
                <div className="space-y-6">
                  {inactiveFunds.map(fund => (
                    <InvestmentCalculator
                      key={fund.type}
                      fundName={fund.name}
                      fundInfo={fund.info}
                      currentMonthlyEarnings={currentMonthlyEarnings}
                      userBalance={clientData.balance.total_balance}
                    />
                  ))}
                </div>
                
                {/* Pro Tip */}
                <div className="pro-tip flex items-start gap-4 p-5 bg-gradient-to-br from-yellow-900/30 to-orange-900/30 border border-yellow-500/40 rounded-xl mt-8">
                  <span className="icon text-3xl flex-shrink-0">💡</span>
                  <div>
                    <p className="text-sm text-slate-300 leading-relaxed">
                      <strong className="text-yellow-400">Pro Tip:</strong> Diversifying across multiple funds 
                      reduces risk while maximizing returns. Our investment experts 
                      can help you create the optimal portfolio mix.
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          }
          return null;
        })()}

        {/* Filters Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="dashboard-card mb-6">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Filter className="mr-2" size={20} />
                Search & Filter Transactions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Search */}
                <div className="space-y-2">
                  <Label htmlFor="search" className="text-slate-300">Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={16} />
                    <Input
                      id="search"
                      type="text"
                      placeholder="Search transactions..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 bg-slate-800 border-slate-600 text-white"
                    />
                  </div>
                </div>

                {/* Date From */}
                <div className="space-y-2">
                  <Label className="text-slate-300">From Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start bg-slate-800 border-slate-600 text-white">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange.from ? format(dateRange.from, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0 bg-slate-800 border-slate-600">
                      <Calendar
                        mode="single"
                        selected={dateRange.from}
                        onSelect={(date) => setDateRange({ ...dateRange, from: date })}
                        initialFocus
                        className="text-white"
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                {/* Date To */}
                <div className="space-y-2">
                  <Label className="text-slate-300">To Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start bg-slate-800 border-slate-600 text-white">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange.to ? format(dateRange.to, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0 bg-slate-800 border-slate-600">
                      <Calendar
                        mode="single"
                        selected={dateRange.to}
                        onSelect={(date) => setDateRange({ ...dateRange, to: date })}
                        initialFocus
                        className="text-white"
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                {/* Fund Filter */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Fund Type</Label>
                  <Select value={fundFilter} onValueChange={setFundFilter}>
                    <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-600">
                      <SelectItem value="all" className="text-white">All Funds</SelectItem>
                      <SelectItem value="fidus" className="text-white">FIDUS</SelectItem>
                      <SelectItem value="core" className="text-white">Core</SelectItem>
                      <SelectItem value="dynamic" className="text-white">Dynamic</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setDateRange({ from: null, to: null });
                    setFundFilter("all");
                    setSearchTerm("");
                  }}
                  className="text-white border-slate-600 hover:bg-slate-700"
                >
                  Clear Filters
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Transaction History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="dashboard-card">
            <CardHeader>
              <CardTitle className="text-white">
                Transaction History ({filteredTransactions.length} transactions)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {(filteredTransactions || []).map((transaction, index) => (
                  <motion.div
                    key={transaction.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.02 }}
                    className="transaction-item"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <Badge 
                          variant={transaction.fund_type === 'fidus' ? 'default' : 
                                   transaction.fund_type === 'core' ? 'secondary' : 'outline'}
                          className="text-xs"
                        >
                          {transaction.fund_type.toUpperCase()}
                        </Badge>
                        <span className="text-white font-medium">{transaction.description}</span>
                      </div>
                      <div className="text-sm text-slate-400 mt-1">
                        {formatDate(transaction.date)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`transaction-amount font-bold ${
                        transaction.amount >= 0 ? 'positive' : 'negative'
                      }`}>
                        {transaction.amount >= 0 ? (
                          <TrendingUp size={16} className="inline mr-1" />
                        ) : (
                          <TrendingDown size={16} className="inline mr-1" />
                        )}
                        {formatCurrency(transaction.amount)}
                      </div>
                    </div>
                  </motion.div>
                ))}
                {filteredTransactions.length === 0 && (
                  <div className="text-center text-slate-400 py-8">
                    No transactions found matching your criteria.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
          </TabsContent>

          <TabsContent value="wallet" className="mt-6">
            <ClientWallet user={user} />
          </TabsContent>

          <TabsContent value="redemptions" className="mt-6">
            <RedemptionManagement user={user} />
          </TabsContent>

          <TabsContent value="calendar" className="mt-6">
            <InvestmentCalendar user={user} userType="client" />
          </TabsContent>

          <TabsContent value="google-workspace" className="mt-6">
            <ClientGoogleWorkspace user={user} />
          </TabsContent>

          <TabsContent value="profile" className="mt-6">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <img src={user.profile_picture || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"} 
                         alt="Profile" className="w-8 h-8 rounded-full" />
                    My Profile Settings
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  
                  {/* Profile Photo Section */}
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <img 
                        src={user.profile_picture || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"}
                        alt="Profile"
                        className="w-20 h-20 rounded-full object-cover border-4 border-cyan-500"
                      />
                    </div>
                    <div className="space-y-2">
                      <h3 className="font-medium">Profile Photo</h3>
                      <input
                        id="photo-upload"
                        type="file"
                        accept="image/*"
                        style={{ display: 'none' }}
                        onChange={handlePhotoUpload}
                      />
                      <Button 
                        onClick={() => document.getElementById('photo-upload').click()}
                        variant="outline"
                        size="sm"
                      >
                        Change Photo
                      </Button>
                    </div>
                  </div>

                  {/* Profile Information Form */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        value={profileData.name}
                        onChange={(e) => setProfileData({...profileData, name: e.target.value})}
                        placeholder="Enter your full name"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={profileData.email}
                        onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                        placeholder="Enter your email"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input
                        id="phone"
                        value={profileData.phone}
                        onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                        placeholder="Enter your phone number"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="username">Username</Label>
                      <Input
                        id="username"
                        value={user.username}
                        disabled
                        className="bg-gray-100"
                        placeholder="Username (cannot be changed)"
                      />
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-4 pt-4">
                    <Button 
                      onClick={handleProfileUpdate}
                      className="bg-cyan-600 hover:bg-cyan-700"
                      disabled={profileLoading}
                    >
                      {profileLoading ? "Updating..." : "Update Profile"}
                    </Button>
                    
                    <Button 
                      onClick={() => setShowPasswordChange(true)}
                      variant="outline"
                    >
                      Change Password
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Password Change Modal */}
              {showPasswordChange && (
                <Card>
                  <CardHeader>
                    <CardTitle>Change Password</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="current-password">Current Password</Label>
                      <Input
                        id="current-password"
                        type="password"
                        value={passwordData.current}
                        onChange={(e) => setPasswordData({...passwordData, current: e.target.value})}
                        placeholder="Enter current password"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="new-password">New Password</Label>
                      <Input
                        id="new-password"
                        type="password"
                        value={passwordData.new}
                        onChange={(e) => setPasswordData({...passwordData, new: e.target.value})}
                        placeholder="Enter new password"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="confirm-password">Confirm New Password</Label>
                      <Input
                        id="confirm-password"
                        type="password"
                        value={passwordData.confirm}
                        onChange={(e) => setPasswordData({...passwordData, confirm: e.target.value})}
                        placeholder="Confirm new password"
                      />
                    </div>
                    
                    <div className="flex gap-4 pt-4">
                      <Button 
                        onClick={handlePasswordChange}
                        className="bg-cyan-600 hover:bg-cyan-700"
                        disabled={passwordLoading}
                      >
                        {passwordLoading ? "Changing..." : "Change Password"}
                      </Button>
                      
                      <Button 
                        onClick={() => setShowPasswordChange(false)}
                        variant="outline"
                      >
                        Cancel
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ClientDashboard;