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
import { LogOut, Search, Calendar as CalendarIcon, DollarSign, TrendingUp, TrendingDown, Filter, FileText, Target, ArrowDownCircle } from "lucide-react";
import { format } from "date-fns";
import apiAxios from "../utils/apiAxios";
import DocumentPortal from "./DocumentPortal";
import InvestmentDashboard from "./InvestmentDashboard";
import RedemptionManagement from "./RedemptionManagement";
import InvestmentCalendar from "./InvestmentCalendar";
import ClientMT5View from "./ClientMT5View";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ClientDashboard = ({ user, onLogout }) => {
  const [clientData, setClientData] = useState(null);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({ from: null, to: null });
  const [fundFilter, setFundFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

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
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(Math.abs(amount));
  };

  const formatDate = (dateString) => {
    return format(new Date(dateString), 'MMM dd, yyyy');
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <div className="header-logo">
            <span className="header-logo-text">
              <span className="header-logo-f">F</span>IDUS
            </span>
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
        <div className="header-logo">
          <span className="header-logo-text">
            <span className="header-logo-f">F</span>IDUS
          </span>
        </div>
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
          <TabsList className="grid w-full grid-cols-6 bg-slate-800 border-slate-600 mb-6">
            <TabsTrigger value="overview" className="text-white data-[state=active]:bg-cyan-600">
              <DollarSign size={16} className="mr-2" />
              Account Overview
            </TabsTrigger>

            <TabsTrigger value="mt5" className="text-white data-[state=active]:bg-cyan-600">
              📈 Fund Commitments
            </TabsTrigger>
            <TabsTrigger value="redemptions" className="text-white data-[state=active]:bg-cyan-600">
              <ArrowDownCircle size={16} className="mr-2" />
              Redemptions
            </TabsTrigger>
            <TabsTrigger value="calendar" className="text-white data-[state=active]:bg-cyan-600">
              <CalendarIcon size={16} className="mr-2" />
              Calendar
            </TabsTrigger>
            <TabsTrigger value="documents" className="text-white data-[state=active]:bg-cyan-600">
              <FileText size={16} className="mr-2" />
              Documents
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
            </CardContent>
          </Card>

          {/* Account Balance */}
          <Card className="dashboard-card lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <DollarSign className="mr-2" size={20} />
                Account Balance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center">
                  <div className="balance-amount">
                    {clientData && formatCurrency(clientData.balance.total_balance)}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="balance-label">FIDUS Funds</div>
                    <div className="text-2xl font-bold text-cyan-400">
                      {clientData && formatCurrency(clientData.balance.fidus_funds)}
                    </div>
                    <div className="text-xs text-gray-400">BALANCE & UNLIMITED</div>
                  </div>
                  <div>
                    <div className="balance-label">Core Balance</div>
                    <div className="text-2xl font-bold text-orange-400">
                      {clientData && formatCurrency(clientData.balance.core_balance)}
                    </div>
                    <div className="text-xs text-gray-400">CORE Fund</div>
                  </div>
                </div>
                {clientData && clientData.balance.dynamic_balance > 0 && (
                  <div className="mt-4">
                    <div className="balance-label">Dynamic Balance</div>
                    <div className="text-2xl font-bold text-green-400">
                      {formatCurrency(clientData.balance.dynamic_balance)}
                    </div>
                    <div className="text-xs text-gray-400">DYNAMIC Fund</div>
                  </div>
                )}
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

          <TabsContent value="investments" className="mt-6">
            <InvestmentDashboard user={user} userType="client" />
          </TabsContent>

          <TabsContent value="mt5" className="mt-6">
            <ClientMT5View clientId={user.id} />
          </TabsContent>

          <TabsContent value="redemptions" className="mt-6">
            <RedemptionManagement user={user} />
          </TabsContent>

          <TabsContent value="calendar" className="mt-6">
            <InvestmentCalendar user={user} />
          </TabsContent>

          <TabsContent value="documents" className="mt-6">
            <DocumentPortal user={user} userType="client" />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ClientDashboard;