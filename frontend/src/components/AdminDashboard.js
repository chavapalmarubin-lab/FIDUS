import React, { useEffect, useMemo, useRef, useState } from "react";
import './tab-fix.css';
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Switch } from "./ui/switch";
import { LogOut, Upload, Download, Plus, Trash2, Users, FileText, TrendingUp, ArrowDownCircle, DollarSign, Star } from "lucide-react";
import ClientManagement from "./ClientManagement";
import DocumentPortal from "./DocumentPortal";
import CRMDashboard from "./CRMDashboard";

import AdminInvestmentManagement from "./AdminInvestmentManagement";
import AdminRedemptionManagement from "./AdminRedemptionManagement";
import FundPortfolioManagement from "./FundPortfolioManagement";
import CashFlowManagement from "./CashFlowManagement";
import MT5Management from "./MT5Management";
import FundPerformanceDashboard from "./FundPerformanceDashboard";
import ApplicationDocuments from "./ApplicationDocuments";
import UserAdministration from "./UserAdministration";
// Clean imports - removed unused Google components
import InvestmentDashboard from './InvestmentDashboard';
import ClientDetailModal from './ClientDetailModal';
import InvestmentDetailView from './InvestmentDetailView';
import FullGoogleWorkspace from './FullGoogleWorkspace';
import AlejandroInvestmentDashboard from './AlejandroInvestmentDashboard';
import RealGoogleWorkspace from './RealGoogleWorkspace';
import SimpleIndividualGoogleWorkspace from './SimpleIndividualGoogleWorkspace';
// GoogleConnectionMonitor removed - redundant with Google Workspace integration
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import * as XLSX from "xlsx";
import apiAxios from "../utils/apiAxios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LS_KEY = "fidus_ic_data_v1";
const LS_ALLOC_KEY = "fidus_ic_alloc_v1";

function toFixedPct(n) {
  return (Math.round(n * 10000) / 10000).toFixed(4);
}

function parseNumber(v) {
  if (v === null || v === undefined) return 0;
  if (typeof v === "number") return v;
  const cleaned = String(v).replace(/%/g, "").trim();
  const num = Number(cleaned);
  return isNaN(num) ? 0 : num;
}

const defaultWeeks = Array.from({ length: 8 }).map((_, i) => ({
  week: `Week ${i + 1}`,
  CORE: 0,
  BALANCE: 0,
  DYNAMIC: 0,
}));

const defaultAlloc = {
  aum: 1000000,
  CORE: 33.33,
  BALANCE: 33.33,
  DYNAMIC: 33.34,
};

function useLocalStorage(key, initialValue) {
  const [state, setState] = useState(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : initialValue;
    } catch (e) {
      return initialValue;
    }
  });
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch {}
  }, [key, state]);
  return [state, setState];
}

function download(filename, text) {
  const element = document.createElement("a");
  element.setAttribute(
    "href",
    "data:text/plain;charset=utf-8," + encodeURIComponent(text)
  );
  element.setAttribute("download", filename);
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

function exportCSV(rows) {
  const header = ["Week", "CORE", "BALANCE", "DYNAMIC"]; 
  const lines = [header.join(",")].concat(
    rows.map((r) => [r.week, r.CORE, r.BALANCE, r.DYNAMIC].join(","))
  );
  return lines.join("\n");
}

const COLORS = ['#00bcd4', '#ffa726', '#4caf50'];

const AdminDashboard = ({ user, onLogout }) => {
  const [rows, setRows] = useLocalStorage(LS_KEY, defaultWeeks);
  const [alloc, setAlloc] = useLocalStorage(LS_ALLOC_KEY, defaultAlloc);
  const [sim, setSim] = useState({ enabled: false, CORE: 0, BALANCE: 0, DYNAMIC: 0 });
  const [portfolioData, setPortfolioData] = useState(null);
  const fileInputRef = useRef(null);

  // Detect tab parameter from URL for OAuth callback
  const [activeTab, setActiveTab] = useState(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    
    if (tabParam === 'connection-monitor' || tabParam === 'google-workspace') {
      console.log('🎯 OAuth callback detected - setting Google Workspace as active tab');
      return 'google';
    }
    return 'portfolio';
  });

  const fields = ["CORE", "BALANCE", "DYNAMIC"];

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      const response = await apiAxios.get(`/admin/portfolio-summary`);
      setPortfolioData(response.data);
      // Update allocation with fetched data
      setAlloc({
        aum: response.data.aum,
        ...response.data.allocation
      });
      // Update weekly data with fetched performance
      setRows(response.data.weekly_performance || defaultWeeks);
    } catch (error) {
      console.error("Error fetching portfolio data:", error);
    }
  };

  const effectiveRows = useMemo(() => {
    if (!sim.enabled) return rows || [];
    if (!rows || rows.length === 0) return rows || [];
    const cloned = rows.map((r) => ({ ...r }));
    const lastIdx = cloned.length - 1;
    cloned[lastIdx] = {
      ...cloned[lastIdx],
      CORE: parseNumber(sim.CORE),
      BALANCE: parseNumber(sim.BALANCE),
      DYNAMIC: parseNumber(sim.DYNAMIC),
    };
    return cloned;
  }, [rows, sim]);

  const cumData = useMemo(() => {
    const start = 100;
    const cum = {};
    fields.forEach((f) => (cum[f] = start));
    return (effectiveRows || []).map((r) => {
      const out = { week: r.week };
      fields.forEach((f) => {
        const weeklyPct = parseNumber(r[f]) / 100;
        cum[f] = cum[f] * (1 + weeklyPct);
        out[f] = Number(cum[f].toFixed(4));
      });
      return out;
    });
  }, [effectiveRows]);

  const weightedWeekly = useMemo(() => {
    return (effectiveRows || []).map((r) => {
      const core = parseNumber(r.CORE) / 100;
      const bal = parseNumber(r.BALANCE) / 100;
      const dyn = parseNumber(r.DYNAMIC) / 100;
      const w = (parseNumber(alloc.CORE) + parseNumber(alloc.BALANCE) + parseNumber(alloc.DYNAMIC)) || 0;
      const wc = w === 0 ? 0 : parseNumber(alloc.CORE) / w;
      const wb = w === 0 ? 0 : parseNumber(alloc.BALANCE) / w;
      const wd = w === 0 ? 0 : parseNumber(alloc.DYNAMIC) / w;
      const total = core * wc + bal * wb + dyn * wd;
      return { week: r.week, TOTAL: total * 100 };
    });
  }, [effectiveRows, alloc]);

  const cumTotal = useMemo(() => {
    let nav = 100;
    return (weightedWeekly || []).map((r) => {
      const pct = parseNumber(r.TOTAL) / 100;
      nav = nav * (1 + pct);
      return { week: r.week, TOTAL: Number(nav.toFixed(4)) };
    });
  }, [weightedWeekly]);

  const mergedCum = useMemo(() => {
    const map = new Map();
    [cumData, cumTotal].forEach((series) => {
      series.forEach((row) => {
        const key = row.week;
        if (!map.has(key)) map.set(key, { week: key });
        Object.assign(map.get(key), row);
      });
    });
    return Array.from(map.values());
  }, [cumData, cumTotal]);

  const totalPnL = useMemo(() => {
    const start = alloc.aum || 0;
    const last = cumTotal.length ? cumTotal[cumTotal.length - 1].TOTAL : 100;
    return start * (last / 100 - 1);
  }, [alloc.aum, cumTotal]);

  function handleCellChange(i, key, value) {
    const next = [...rows];
    next[i] = { ...next[i], [key]: value === "" ? 0 : parseNumber(value) };
    setRows(next);
  }

  function addRow() {
    const idx = rows.length + 1;
    setRows([...rows, { week: `Week ${idx}`, CORE: 0, BALANCE: 0, DYNAMIC: 0 }]);
  }

  function removeRow(i) {
    const next = [...rows];
    next.splice(i, 1);
    setRows(next);
  }

  function resetData() {
    if (window.confirm("Reset all data to zeros?")) setRows(defaultWeeks);
  }

  function onUploadFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      const data = new Uint8Array(evt.target.result);
      const wb = XLSX.read(data, { type: "array" });
      const sheetName = wb.SheetNames.includes("FIDUS Investment Committee")
        ? "FIDUS Investment Committee"
        : wb.SheetNames[0];
      const ws = wb.Sheets[sheetName];
      const json = XLSX.utils.sheet_to_json(ws, { defval: "" });
      
      const norm = json
        .map((r, i) => {
          const w = r["Week"] ?? r["week"] ?? r["WEEK"] ?? `Week ${i + 1}`;
          const core = parseNumber(r["CORE"] ?? r["Core"] ?? r["core"] ?? 0);
          const bal = parseNumber(r["BALANCE"] ?? r["Balance"] ?? r["balance"] ?? 0);
          const dyn = parseNumber(r["DYNAMIC"] ?? r["Dynamic"] ?? r["dynamic"] ?? 0);
          return { week: String(w), CORE: core, BALANCE: bal, DYNAMIC: dyn };
        })
        .filter((r) => r.week);
      if (norm.length) setRows(norm);
      else alert("No compatible data found. Expect columns: Week, CORE, BALANCE, DYNAMIC.");
    };
    reader.readAsArrayBuffer(file);
  }

  // Enhanced export functionality for all tabs
  function exportToExcel(data, fileName, sheetName = 'Data') {
    try {
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(data);
      
      // Auto-size columns
      const range = XLSX.utils.decode_range(ws['!ref']);
      const cols = [];
      for (let C = range.s.c; C <= range.e.c; ++C) {
        let maxWidth = 10;
        for (let R = range.s.r; R <= range.e.r; ++R) {
          const cellAddress = XLSX.utils.encode_cell({ r: R, c: C });
          const cell = ws[cellAddress];
          if (cell && cell.v) {
            maxWidth = Math.max(maxWidth, cell.v.toString().length);
          }
        }
        cols.push({ wch: Math.min(maxWidth + 2, 50) });
      }
      ws['!cols'] = cols;
      
      XLSX.utils.book_append_sheet(wb, ws, sheetName);
      XLSX.writeFile(wb, `${fileName}_${new Date().toISOString().split('T')[0]}.xlsx`);
      
      console.log(`✅ Exported ${data.length} records to ${fileName}.xlsx`);
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed. Please try again.');
    }
  }

  // Export functions for each tab
  function exportCurrentTab() {
    const currentDate = new Date().toISOString().split('T')[0];
    
    switch (activeTab) {
      case 'portfolio':
        exportPortfolioData();
        break;
      case 'fund-performance':
        exportFundVsMT5Data();
        break;
      case 'cashflow':
        exportCashFlowData();
        break;
      case 'investments':
        exportInvestmentsData();
        break;
      default:
        alert('Export not available for this tab');
    }
  }

  function exportPortfolioData() {
    const portfolioExportData = investmentCommitteeData.map(fund => ({
      'Fund Code': fund.fund_code || 'N/A',
      'Fund Name': fund.fund_name || 'N/A',
      'Fund Manager': fund.fund_manager || 'N/A',
      'AUM (USD)': fund.aum_current ? `$${fund.aum_current.toLocaleString()}` : '$0',
      'Performance YTD': fund.performance_ytd || '0%',
      'NAV per Unit': fund.nav_per_unit ? `$${fund.nav_per_unit}` : '$0',
      'Management Fee': fund.management_fee || '0%',
      'Inception Date': fund.inception_date || 'N/A',
      'Status': fund.status || 'Active'
    }));
    
    exportToExcel(portfolioExportData, 'FIDUS_Fund_Portfolio', 'Fund Portfolio');
  }

  function exportFundPortfolioData() {
    // Export fund portfolio management data
    const fundData = [{
      'Export Date': new Date().toLocaleDateString(),
      'Total AUM': `$${portfolioData.reduce((sum, fund) => sum + (fund.aum || 0), 0).toLocaleString()}`,
      'Total Funds': portfolioData.length,
      'Note': 'Fund portfolio data as of export date'
    }];
    
    exportToExcel(fundData, 'FIDUS_Fund_Portfolio_Management', 'Portfolio Summary');
  }

  function exportFundVsMT5Data() {
    // Export fund vs MT5 comparison data
    const comparisonData = [{
      'Export Date': new Date().toLocaleDateString(),
      'Fund Performance': 'TBD - Awaiting investment data',
      'MT5 Trading': '$0 (No trading activity)',
      'Variance': '$0',
      'Note': 'Data will populate after investment entry'
    }];
    
    exportToExcel(comparisonData, 'FIDUS_Fund_vs_MT5', 'Fund vs MT5');
  }

  function exportCashFlowData() {
    // Export cash flow management data
    const cashFlowData = [{
      'Export Date': new Date().toLocaleDateString(),
      'MT5 Trading Profits': '$0',
      'Broker Rebates': '$0',
      'Total Inflows': '$0',
      'Client Interest Obligations': '$0',
      'Net Cash Flow': '$0',
      'Note': 'Awaiting Alejandro Mariscal investment entry'
    }];
    
    exportToExcel(cashFlowData, 'FIDUS_Cash_Flow', 'Cash Flow');
  }

  function exportInvestmentsData() {
    // Export investments data - currently only Alejandro Mariscal ready
    const investmentsData = [{
      'Export Date': new Date().toLocaleDateString(),
      'Ready Clients': 'Alejandro Mariscal (AML/KYC Approved)',
      'Pending Investments': 'To be entered',
      'Total Invested': '$0',
      'Active Investments': '0',
      'Note': 'Alejandro Mariscal ready for investment entry'
    }];
    
    exportToExcel(investmentsData, 'FIDUS_Investments', 'Investments');
  }

  function exportRedemptionsData() {
    // Export redemptions data
    const redemptionsData = [{
      'Export Date': new Date().toLocaleDateString(),
      'Total Redemptions': '$0',
      'Pending Redemptions': '0',
      'Processed Redemptions': '0',
      'Note': 'No redemption activity yet'
    }];
    
    exportToExcel(redemptionsData, 'FIDUS_Redemptions', 'Redemptions');
  }

  function onExport(kind) {
    if (kind === "csv") {
      download("fidus_ic_weeks.csv", exportCSV(rows));
    } else if (kind === "json") {
      download("fidus_ic_weeks.json", JSON.stringify(rows, null, 2));
    } else if (kind === "excel") {
      exportCurrentTab();
    }
  }

  const allocSum = parseNumber(alloc.CORE) + parseNumber(alloc.BALANCE) + parseNumber(alloc.DYNAMIC);
  const allocOk = Math.abs(allocSum - 100) < 0.01;

  const pieAlloc = [
    { name: "CORE", value: parseNumber(alloc.CORE) },
    { name: "BALANCE", value: parseNumber(alloc.BALANCE) },
    { name: "DYNAMIC", value: parseNumber(alloc.DYNAMIC) },
  ];

  const currencyFormatter = (value) => {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="flex items-center gap-4" style={{ minHeight: '64px' }}>
          <img 
            src="/fidus-logo.png"
            alt="FIDUS Logo"
            onError={(e) => { 
              console.error('Top left logo failed to load'); 
            }}
            onLoad={() => { 
              console.log('BIG Top left logo loaded successfully at 64px'); 
            }}
            style={{ 
              height: '64px', 
              width: 'auto',
              maxWidth: '200px',
              objectFit: 'contain',
              display: 'block !important',
              visibility: 'visible !important',
              opacity: '1 !important'
            }}
          />
          <span className="text-slate-400 text-base">Investment Committee</span>
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
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.4 }}
        >
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white">
                FIDUS Investment Committee — Admin Dashboard
              </h1>
              <p className="text-sm text-slate-400">
                Manage fund allocations, monitor performance, and oversee client database.
              </p>
            </div>
          </div>
        </motion.div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-12 bg-slate-800 border-slate-600">
            <TabsTrigger value="portfolio" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              Fund Portfolio
            </TabsTrigger>
            <TabsTrigger value="fund-performance" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              📊 Fund vs MT5
            </TabsTrigger>
            <TabsTrigger value="cashflow" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              <DollarSign size={16} className="mr-2" />
              Cash Flow
            </TabsTrigger>
            <TabsTrigger value="investments" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              <TrendingUp size={16} className="mr-2" />
              Investments
            </TabsTrigger>
            <TabsTrigger value="mt5" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              📈 MT5 Accounts
            </TabsTrigger>
            <TabsTrigger value="clients" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              <Users size={16} className="mr-2" />
              Clients
            </TabsTrigger>
            <TabsTrigger value="users" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              <Users size={16} className="mr-2" />
              User Admin
            </TabsTrigger>
            <TabsTrigger value="crm" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              CRM Dashboard
            </TabsTrigger>
            <TabsTrigger value="redemptions" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              <ArrowDownCircle size={16} className="mr-2" />
              Redemptions
            </TabsTrigger>
            <TabsTrigger value="google" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              🌐 Google Workspace
            </TabsTrigger>
            {/* Google Connection Monitor removed - redundant with Google Workspace integration */}
            <TabsTrigger value="documents" className="text-white hover:bg-slate-700 data-[state=active]:bg-cyan-600 data-[state=active]:text-white data-[state=active]:font-bold data-[state=active]:border data-[state=active]:border-cyan-400">
              <FileText size={16} className="mr-2" />
              📄 App Documents
            </TabsTrigger>
          </TabsList>

          <TabsContent value="portfolio" className="mt-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Fund Portfolio Management</h2>
                <Button
                  onClick={() => exportCurrentTab()}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export to Excel
                </Button>
              </div>
              <FundPortfolioManagement />
            </div>
          </TabsContent>

          <TabsContent value="fund-performance" className="mt-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Fund vs MT5 Analysis</h2>
                <Button
                  onClick={() => exportCurrentTab()}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export to Excel
                </Button>
              </div>
              <FundPerformanceDashboard />
            </div>
          </TabsContent>

          <TabsContent value="cashflow" className="mt-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Cash Flow Management</h2>
                <Button
                  onClick={() => exportCurrentTab()}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export to Excel
                </Button>
              </div>
              <CashFlowManagement />
            </div>
          </TabsContent>

          <TabsContent value="investments" className="mt-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Investment Management</h2>
                <Button
                  onClick={() => exportCurrentTab()}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export to Excel
                </Button>
              </div>
              <AdminInvestmentManagement />
            </div>
          </TabsContent>

          <TabsContent value="mt5" className="mt-6">
            <MT5Management />
          </TabsContent>

          <TabsContent value="redemptions" className="mt-6">
            <AdminRedemptionManagement />
          </TabsContent>

          <TabsContent value="crm" className="mt-6">
            <CRMDashboard user={user} />
          </TabsContent>

          <TabsContent value="clients" className="mt-6">
            <ClientManagement />
          </TabsContent>

          <TabsContent value="users" className="mt-6">
            <UserAdministration />
          </TabsContent>

          <TabsContent value="google" className="mt-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-4">🌐 Google Workspace Integration</h2>
              <p className="text-gray-600 mb-4">Testing Google Workspace tab routing...</p>
              <FullGoogleWorkspace />
            </div>
          </TabsContent>

          {/* Google Connection Monitor content removed - redundant with Google Workspace integration */}

          <TabsContent value="documents" className="mt-6">
            <ApplicationDocuments />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;