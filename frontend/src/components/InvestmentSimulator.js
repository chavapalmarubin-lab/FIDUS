import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Calculator, 
  TrendingUp, 
  Calendar,
  DollarSign,
  PieChart,
  BarChart3,
  Download,
  Mail,
  Info,
  Clock,
  Target,
  Wallet,
  LineChart,
  Save,
  Play,
  Plus
} from "lucide-react";
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend
} from 'recharts';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FUND_COLORS = {
  'CORE': '#3B82F6',
  'BALANCE': '#10B981', 
  'DYNAMIC': '#F59E0B',
  'UNLIMITED': '#8B5CF6'
};

const InvestmentSimulator = ({ isPublic = true, leadInfo = null }) => {
  const [funds, setFunds] = useState([]);
  const [investments, setInvestments] = useState([
    { fund_code: 'CORE', amount: 10000 },
    { fund_code: 'BALANCE', amount: 50000 },
    { fund_code: 'DYNAMIC', amount: 250000 }
  ]);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [timeframeMonths, setTimeframeMonths] = useState(24);
  const [simulationName, setSimulationName] = useState("");
  const [leadInfoForm, setLeadInfoForm] = useState({
    name: leadInfo?.name || "",
    email: leadInfo?.email || "",
    phone: leadInfo?.phone || ""
  });
  const [activeTab, setActiveTab] = useState("setup");

  useEffect(() => {
    fetchFundConfigurations();
  }, []);

  const fetchFundConfigurations = async () => {
    try {
      const response = await fetch(`${API}/investments/funds/config`);
      const data = await response.json();
      
      if (data.success) {
        setFunds(data.funds);
      }
    } catch (err) {
      console.error("Failed to fetch fund configurations:", err);
    }
  };

  const addInvestment = () => {
    const availableFunds = funds.filter(fund => 
      !investments.some(inv => inv.fund_code === fund.fund_code)
    );
    
    if (availableFunds.length > 0) {
      setInvestments([...investments, {
        fund_code: availableFunds[0].fund_code,
        amount: availableFunds[0].minimum_investment
      }]);
    }
  };

  const removeInvestment = (index) => {
    setInvestments(investments.filter((_, i) => i !== index));
  };

  const updateInvestment = (index, field, value) => {
    const updated = [...investments];
    updated[index][field] = field === 'amount' ? parseFloat(value) || 0 : value;
    setInvestments(updated);
  };

  const validateInvestments = () => {
    for (const investment of investments) {
      const fund = funds.find(f => f.fund_code === investment.fund_code);
      if (!fund) continue;
      
      if (investment.amount < fund.minimum_investment) {
        throw new Error(`Minimum investment for ${fund.name} is $${fund.minimum_investment.toLocaleString()}`);
      }
      
      if (fund.invitation_only && investment.fund_code === 'UNLIMITED') {
        throw new Error(`${fund.name} is by invitation only. Please contact our team.`);
      }
    }
  };

  const runSimulation = async () => {
    try {
      setLoading(true);
      setError("");
      setSuccess("");

      if (investments.length === 0) {
        throw new Error("Please add at least one investment");
      }

      validateInvestments();

      const requestData = {
        investments: investments.filter(inv => inv.amount > 0),
        timeframe_months: timeframeMonths,
        simulation_name: simulationName || "Investment Simulation",
        lead_info: isPublic ? leadInfoForm : leadInfo
      };

      const response = await fetch(`${API}/investments/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setSimulationResult(data.simulation);
        setActiveTab("results");
        setSuccess("Investment simulation completed successfully!");
      } else {
        throw new Error(data.detail || "Failed to run simulation");
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const exportSimulation = async () => {
    if (!simulationResult) return;
    
    try {
      setLoading(true);
      
      // Create PDF
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 20;
      let yPosition = margin;
      
      // Add FIDUS Logo (you can replace this with actual logo if available)
      pdf.setFontSize(24);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(59, 130, 246); // Blue color
      pdf.text('FIDUS', margin, yPosition);
      
      pdf.setFontSize(12);
      pdf.setFont(undefined, 'normal');
      pdf.setTextColor(100, 116, 139); // Gray color
      pdf.text('Professional Investment Management Platform', margin, yPosition + 8);
      
      yPosition += 30;
      
      // Title
      pdf.setFontSize(20);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(17, 24, 39); // Dark gray
      pdf.text('Investment Portfolio Simulation Report', margin, yPosition);
      
      yPosition += 15;
      
      // Date and Simulation Info
      pdf.setFontSize(10);
      pdf.setFont(undefined, 'normal');
      pdf.setTextColor(75, 85, 99);
      const currentDate = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
      pdf.text(`Generated: ${currentDate}`, margin, yPosition);
      
      if (simulationResult.simulation_name) {
        pdf.text(`Simulation: ${simulationResult.simulation_name}`, margin, yPosition + 5);
        yPosition += 5;
      }
      
      if (simulationResult.lead_info?.name) {
        pdf.text(`Prepared for: ${simulationResult.lead_info.name}`, margin, yPosition + 5);
        yPosition += 5;
      }
      
      yPosition += 20;
      
      // Executive Summary Box
      pdf.setDrawColor(59, 130, 246);
      pdf.setFillColor(239, 246, 255);
      pdf.roundedRect(margin, yPosition, pageWidth - 2*margin, 35, 3, 3, 'FD');
      
      yPosition += 8;
      pdf.setFontSize(14);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(59, 130, 246);
      pdf.text('Executive Summary', margin + 5, yPosition);
      
      yPosition += 8;
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'normal');
      pdf.setTextColor(17, 24, 39);
      
      const summaryStats = [
        `Total Investment: ${formatCurrency(simulationResult.summary.total_investment)}`,
        `Projected Final Value: ${formatCurrency(simulationResult.summary.final_value)}`,
        `Total Interest Earned: ${formatCurrency(simulationResult.summary.total_interest_earned)}`,
        `Return on Investment: ${formatPercentage(simulationResult.summary.total_roi_percentage)}`
      ];
      
      summaryStats.forEach((stat, index) => {
        pdf.text(stat, margin + 5, yPosition);
        yPosition += 5;
      });
      
      yPosition += 15;
      
      // Fund Breakdown
      pdf.setFontSize(16);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(17, 24, 39);
      pdf.text('Investment Fund Breakdown', margin, yPosition);
      yPosition += 10;
      
      simulationResult.fund_breakdown.forEach((fund, index) => {
        // Check if we need a new page
        if (yPosition > pageHeight - 60) {
          pdf.addPage();
          yPosition = margin;
        }
        
        // Fund header
        pdf.setFontSize(12);
        pdf.setFont(undefined, 'bold');
        pdf.setTextColor(17, 24, 39);
        pdf.text(`${fund.fund_name} (${fund.fund_code})`, margin, yPosition);
        
        yPosition += 8;
        pdf.setFontSize(10);
        pdf.setFont(undefined, 'normal');
        pdf.setTextColor(75, 85, 99);
        
        const fundDetails = [
          `Investment Amount: ${formatCurrency(fund.investment_amount)}`,
          `Interest Rate: ${fund.interest_rate}% monthly`,
          `Redemption Frequency: ${fund.redemption_frequency}`,
          `Final Value: ${formatCurrency(fund.final_value)}`,
          `Total Interest: ${formatCurrency(fund.total_interest)}`,
          `ROI: ${formatPercentage(fund.roi_percentage)}`
        ];
        
        fundDetails.forEach(detail => {
          pdf.text(`• ${detail}`, margin + 5, yPosition);
          yPosition += 4;
        });
        
        yPosition += 8;
      });
      
      // Investment Timeline (Key Events)
      if (yPosition > pageHeight - 100) {
        pdf.addPage();
        yPosition = margin;
      }
      
      pdf.setFontSize(16);
      pdf.setFont(undefined, 'bold');
      pdf.setTextColor(17, 24, 39);
      pdf.text('Key Investment Timeline Events', margin, yPosition);
      yPosition += 10;
      
      // Get key events (investment starts, incubation ends, principal redeemable)
      const keyEvents = simulationResult.calendar_events.filter(event => 
        ['investment_start', 'incubation_end', 'principal_redeemable'].includes(event.type)
      ).slice(0, 10); // Limit to first 10 events
      
      keyEvents.forEach(event => {
        if (yPosition > pageHeight - 30) {
          pdf.addPage();
          yPosition = margin;
        }
        
        pdf.setFontSize(10);
        pdf.setFont(undefined, 'bold');
        pdf.setTextColor(17, 24, 39);
        pdf.text(`${new Date(event.date).toLocaleDateString()} - ${event.title}`, margin, yPosition);
        
        yPosition += 4;
        pdf.setFont(undefined, 'normal');
        pdf.setTextColor(75, 85, 99);
        const description = pdf.splitTextToSize(event.description, pageWidth - 2*margin - 10);
        pdf.text(description, margin + 5, yPosition);
        yPosition += description.length * 4 + 5;
      });
      
      // Add disclaimer/footer
      if (yPosition > pageHeight - 40) {
        pdf.addPage();
        yPosition = margin;
      } else {
        yPosition = pageHeight - 35;
      }
      
      pdf.setDrawColor(229, 231, 235);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 8;
      
      pdf.setFontSize(8);
      pdf.setFont(undefined, 'italic');
      pdf.setTextColor(107, 114, 128);
      pdf.text('This simulation is for illustrative purposes only and does not constitute investment advice.', margin, yPosition);
      pdf.text('Past performance does not guarantee future results. Please consult with a financial advisor.', margin, yPosition + 4);
      pdf.text('Generated by FIDUS Investment Management Platform', margin, yPosition + 8);
      
      // Add page numbers
      const pageCount = pdf.internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.setTextColor(107, 114, 128);
        pdf.text(`Page ${i} of ${pageCount}`, pageWidth - margin - 20, pageHeight - 10);
      }
      
      // Save the PDF
      const fileName = `FIDUS_Investment_Simulation_${simulationResult.lead_info?.name?.replace(/\s+/g, '_') || 'Report'}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);
      
      setSuccess("Investment simulation PDF exported successfully!");
      
    } catch (error) {
      console.error('PDF export error:', error);
      setError("Failed to export PDF. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const emailSimulation = async () => {
    // This would integrate with email service
    setSuccess("Email feature will be implemented with email service integration");
  };

  const getFundByCode = (code) => funds.find(f => f.fund_code === code);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value) => `${value.toFixed(2)}%`;

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Calculator className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">
            FIDUS Investment Simulator
          </h1>
        </div>
        <p className="text-gray-600 text-lg max-w-3xl mx-auto">
          Model your investment portfolio across our four fund options and see projected returns with real-time calculations including incubation periods and redemption schedules.
        </p>
      </div>

      {/* Error/Success Messages */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg"
          >
            {error}
          </motion.div>
        )}
        
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg"
          >
            {success}
          </motion.div>
        )}
      </AnimatePresence>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="setup" className="flex items-center gap-2">
            <Calculator size={16} />
            Setup
          </TabsTrigger>
          <TabsTrigger value="results" disabled={!simulationResult} className="flex items-center gap-2">
            <TrendingUp size={16} />
            Results
          </TabsTrigger>
          <TabsTrigger value="charts" disabled={!simulationResult} className="flex items-center gap-2">
            <BarChart3 size={16} />
            Charts
          </TabsTrigger>
          <TabsTrigger value="calendar" disabled={!simulationResult} className="flex items-center gap-2">
            <Calendar size={16} />
            Timeline
          </TabsTrigger>
        </TabsList>

        {/* Setup Tab */}
        <TabsContent value="setup" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Investment Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wallet className="w-5 h-5" />
                  Investment Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {investments.map((investment, index) => {
                  const fund = getFundByCode(investment.fund_code);
                  if (!fund) return null;

                  return (
                    <div key={index} className="p-4 border rounded-lg space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div 
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: FUND_COLORS[fund.fund_code] }}
                          />
                          <h3 className="font-medium">{fund.name}</h3>
                          {fund.invitation_only && (
                            <Badge variant="secondary" className="text-xs">
                              Invitation Only
                            </Badge>
                          )}
                        </div>
                        {investments.length > 1 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeInvestment(index)}
                            className="text-red-600 hover:text-red-700"
                          >
                            Remove
                          </Button>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor={`fund-${index}`}>Fund</Label>
                          <select
                            id={`fund-${index}`}
                            value={investment.fund_code}
                            onChange={(e) => updateInvestment(index, 'fund_code', e.target.value)}
                            className="w-full mt-1 p-2 border rounded-md"
                          >
                            {funds.map(fund => (
                              <option key={fund.fund_code} value={fund.fund_code}>
                                {fund.name} ({fund.interest_rate}%)
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <Label htmlFor={`amount-${index}`}>
                            Investment Amount (Min: {formatCurrency(fund.minimum_investment)})
                          </Label>
                          <Input
                            id={`amount-${index}`}
                            type="number"
                            min={fund.minimum_investment}
                            step="1000"
                            value={investment.amount}
                            onChange={(e) => updateInvestment(index, 'amount', e.target.value)}
                            className="mt-1"
                          />
                        </div>
                      </div>

                      <div className="text-sm text-gray-600 grid grid-cols-2 gap-2">
                        <div>Interest Rate: <span className="font-medium">{fund.interest_rate}% monthly</span></div>
                        <div>Redemption: <span className="font-medium">{fund.redemption_frequency}</span></div>
                        <div>Incubation: <span className="font-medium">{fund.incubation_months} months</span></div>
                        <div>Min Hold: <span className="font-medium">{fund.minimum_hold_months} months</span></div>
                      </div>
                    </div>
                  );
                })}

                <Button 
                  onClick={addInvestment}
                  variant="outline"
                  className="w-full"
                  disabled={investments.length >= funds.length}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Another Fund
                </Button>
              </CardContent>
            </Card>

            {/* Simulation Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Simulation Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="timeframe">Projection Timeframe (Months)</Label>
                  <select
                    id="timeframe"
                    value={timeframeMonths}
                    onChange={(e) => setTimeframeMonths(parseInt(e.target.value))}
                    className="w-full mt-1 p-2 border rounded-md"
                  >
                    <option value={12}>1 Year (12 months)</option>
                    <option value={24}>2 Years (24 months)</option>
                    <option value={36}>3 Years (36 months)</option>
                    <option value={60}>5 Years (60 months)</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="sim-name">Simulation Name (Optional)</Label>
                  <Input
                    id="sim-name"
                    value={simulationName}
                    onChange={(e) => setSimulationName(e.target.value)}
                    placeholder="My Investment Plan"
                    className="mt-1"
                  />
                </div>

                {isPublic && (
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-900">Lead Information</h4>
                    <div>
                      <Label htmlFor="lead-name">Name</Label>
                      <Input
                        id="lead-name"
                        value={leadInfoForm.name}
                        onChange={(e) => setLeadInfoForm({...leadInfoForm, name: e.target.value})}
                        placeholder="Your name"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="lead-email">Email</Label>
                      <Input
                        id="lead-email"
                        type="email"
                        value={leadInfoForm.email}
                        onChange={(e) => setLeadInfoForm({...leadInfoForm, email: e.target.value})}
                        placeholder="your@email.com"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="lead-phone">Phone (Optional)</Label>
                      <Input
                        id="lead-phone"
                        value={leadInfoForm.phone}
                        onChange={(e) => setLeadInfoForm({...leadInfoForm, phone: e.target.value})}
                        placeholder="+1-555-0123"
                        className="mt-1"
                      />
                    </div>
                  </div>
                )}

                <Button 
                  onClick={runSimulation}
                  disabled={loading || investments.length === 0}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                      Running Simulation...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Run Investment Simulation
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Fund Information Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {funds.map(fund => (
              <Card key={fund.fund_code} className="relative overflow-hidden">
                <div 
                  className="absolute top-0 left-0 w-full h-1"
                  style={{ backgroundColor: FUND_COLORS[fund.fund_code] }}
                />
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex items-center justify-between">
                    {fund.name}
                    {fund.invitation_only && (
                      <Badge variant="secondary" className="text-xs">
                        Invitation
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Interest Rate:</span>
                    <span className="font-medium">{fund.interest_rate}%/month</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Minimum:</span>
                    <span className="font-medium">{formatCurrency(fund.minimum_investment)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Redemptions:</span>
                    <span className="font-medium capitalize">{fund.redemption_frequency}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Incubation:</span>
                    <span className="font-medium">{fund.incubation_months} months</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Results Tab */}
        <TabsContent value="results" className="space-y-6">
          {simulationResult && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Investment</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {formatCurrency(simulationResult.summary.total_investment)}
                        </p>
                      </div>
                      <DollarSign className="w-8 h-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Final Value</p>
                        <p className="text-2xl font-bold text-green-600">
                          {formatCurrency(simulationResult.summary.final_value)}
                        </p>
                      </div>
                      <TrendingUp className="w-8 h-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Interest</p>
                        <p className="text-2xl font-bold text-emerald-600">
                          {formatCurrency(simulationResult.summary.total_interest_earned)}
                        </p>
                      </div>
                      <Target className="w-8 h-8 text-emerald-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total ROI</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {formatPercentage(simulationResult.summary.total_roi_percentage)}
                        </p>
                      </div>
                      <LineChart className="w-8 h-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Fund Breakdown */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="w-5 h-5" />
                      Fund Breakdown
                    </CardTitle>
                    <div className="flex gap-2">
                      <Button onClick={exportSimulation} variant="outline" size="sm" disabled={loading}>
                        <Download className="w-4 h-4 mr-2" />
                        {loading ? "Generating PDF..." : "Export PDF"}
                      </Button>
                      <Button onClick={emailSimulation} variant="outline" size="sm">
                        <Mail className="w-4 h-4 mr-2" />
                        Email
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {simulationResult.fund_breakdown.map((fund, index) => (
                      <div key={fund.fund_code} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-4 h-4 rounded-full"
                              style={{ backgroundColor: FUND_COLORS[fund.fund_code] }}
                            />
                            <h3 className="font-medium">{fund.fund_name}</h3>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">{formatCurrency(fund.final_value)}</div>
                            <div className="text-sm text-gray-600">
                              +{formatCurrency(fund.total_interest)} ({formatPercentage(fund.roi_percentage)})
                            </div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Investment:</span>
                            <div className="font-medium">{formatCurrency(fund.investment_amount)}</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Interest Rate:</span>
                            <div className="font-medium">{fund.interest_rate}%/month</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Redemptions:</span>
                            <div className="font-medium capitalize">{fund.redemption_frequency}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* Charts Tab */}
        <TabsContent value="charts" className="space-y-6">
          {simulationResult && (
            <div className="space-y-6">
              {/* Portfolio Growth Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Portfolio Growth Over Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsLineChart data={simulationResult.projected_timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="date" 
                          tickFormatter={(value) => new Date(value).toLocaleDateString()}
                        />
                        <YAxis tickFormatter={(value) => formatCurrency(value)} />
                        <Tooltip 
                          formatter={(value, name) => [formatCurrency(value), name]}
                          labelFormatter={(value) => new Date(value).toLocaleDateString()}
                        />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="total_investment" 
                          stroke="#6B7280" 
                          strokeDasharray="5 5"
                          name="Total Investment"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="total_value" 
                          stroke="#10B981" 
                          strokeWidth={3}
                          name="Portfolio Value"
                        />
                        <Line 
                          type="monotone" 
                          dataKey="total_interest" 
                          stroke="#3B82F6" 
                          name="Total Interest"
                        />
                      </RechartsLineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Fund Allocation Pie Chart */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Investment Allocation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <RechartsPieChart>
                          <Pie
                            data={simulationResult.fund_breakdown.map(fund => ({
                              name: fund.fund_code,
                              value: fund.investment_amount,
                              fill: FUND_COLORS[fund.fund_code]
                            }))}
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            dataKey="value"
                            label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                          >
                            {simulationResult.fund_breakdown.map((fund, index) => (
                              <Cell key={`cell-${index}`} fill={FUND_COLORS[fund.fund_code]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value) => formatCurrency(value)} />
                        </RechartsPieChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>ROI by Fund</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={simulationResult.fund_breakdown}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="fund_code" />
                          <YAxis tickFormatter={(value) => `${value}%`} />
                          <Tooltip 
                            formatter={(value) => [`${value.toFixed(2)}%`, 'ROI']}
                          />
                          <Bar 
                            dataKey="roi_percentage"
                            fill="#8884d8"
                            radius={[4, 4, 0, 0]}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </TabsContent>

        {/* Calendar Timeline Tab */}
        <TabsContent value="calendar" className="space-y-6">
          {simulationResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Investment Timeline & Events
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {simulationResult.calendar_events.map((event, index) => {
                    const eventDate = new Date(event.date);
                    const isUpcoming = eventDate > new Date();
                    
                    return (
                      <div 
                        key={index}
                        className={`flex items-start gap-4 p-4 rounded-lg border ${
                          isUpcoming ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'
                        }`}
                      >
                        <div className="flex-shrink-0">
                          <div 
                            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium"
                            style={{ backgroundColor: FUND_COLORS[event.fund_code] || '#6B7280' }}
                          >
                            {event.fund_code ? event.fund_code.charAt(0) : '•'}
                          </div>
                        </div>
                        
                        <div className="flex-grow">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium text-gray-900">{event.title}</h4>
                            {isUpcoming && (
                              <Badge variant="secondary" className="text-xs">
                                Upcoming
                              </Badge>
                            )}
                          </div>
                          <p className="text-gray-600 text-sm mb-2">{event.description}</p>
                          <div className="flex items-center gap-4 text-sm">
                            <span className="text-gray-500">
                              📅 {eventDate.toLocaleDateString()}
                            </span>
                            {event.amount > 0 && (
                              <span className="text-green-600 font-medium">
                                💰 {formatCurrency(event.amount)}
                              </span>
                            )}
                            <span className="text-blue-600 capitalize">
                              {event.type.replace('_', ' ')}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default InvestmentSimulator;