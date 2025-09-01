import React, { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Switch } from "./ui/switch";
import { LogOut, Upload, Download, Plus, Trash2, Users, FileText, TrendingUp } from "lucide-react";
import ClientManagement from "./ClientManagement";
import DocumentPortal from "./DocumentPortal";
import CRMDashboard from "./CRMDashboard";
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
import axios from "axios";

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

  const fields = ["CORE", "BALANCE", "DYNAMIC"];

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      const response = await axios.get(`${API}/admin/portfolio-summary`);
      setPortfolioData(response.data);
      // Update allocation with fetched data
      setAlloc({
        aum: response.data.aum,
        ...response.data.allocation
      });
      // Update weekly data with fetched performance
      setRows(response.data.weekly_performance);
    } catch (error) {
      console.error("Error fetching portfolio data:", error);
    }
  };

  const effectiveRows = useMemo(() => {
    if (!sim.enabled) return rows;
    if (rows.length === 0) return rows;
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
    return effectiveRows.map((r) => {
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
    return effectiveRows.map((r) => {
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
    return weightedWeekly.map((r) => {
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

  function onExport(kind) {
    if (kind === "csv") {
      download("fidus_ic_weeks.csv", exportCSV(rows));
    } else if (kind === "json") {
      download("fidus_ic_weeks.json", JSON.stringify(rows, null, 2));
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
        <div className="header-logo">
          <span className="header-logo-text">
            <span className="header-logo-f">F</span>IDUS
          </span>
          <span className="text-slate-400 ml-4 text-sm">Investment Committee</span>
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

        <Tabs defaultValue="portfolio" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-slate-800 border-slate-600">
            <TabsTrigger value="portfolio" className="text-white data-[state=active]:bg-cyan-600">
              Fund Portfolio
            </TabsTrigger>
            <TabsTrigger value="clients" className="text-white data-[state=active]:bg-cyan-600">
              <Users size={16} className="mr-2" />
              Client Management
            </TabsTrigger>
            <TabsTrigger value="documents" className="text-white data-[state=active]:bg-cyan-600">
              <FileText size={16} className="mr-2" />
              Document Portal
            </TabsTrigger>
          </TabsList>

          <TabsContent value="portfolio" className="mt-6">
            <div className="flex justify-end mb-4">
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => onExport("csv")} className="text-white border-slate-600">
                  <Download size={16} className="mr-2" />
                  Export CSV
                </Button>
                <Button variant="outline" onClick={() => onExport("json")} className="text-white border-slate-600">
                  <Download size={16} className="mr-2" />
                  Export JSON
                </Button>
              </div>
            </div>

        {/* Top row: Allocation + Upload */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3 mb-6">
          <Card className="dashboard-card md:col-span-2">
            <CardHeader>
              <CardTitle className="text-white">AUM & Allocation</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-3">
                <div>
                  <Label htmlFor="aum" className="text-slate-300">AUM (USD)</Label>
                  <Input
                    id="aum"
                    type="number"
                    value={alloc.aum}
                    onChange={(e) => setAlloc({ ...alloc, aum: parseNumber(e.target.value) })}
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
                <div className="grid grid-cols-3 gap-3">
                  {fields.map((f) => (
                    <div key={f}>
                      <Label htmlFor={`alloc-${f}`} className="text-slate-300">{f} %</Label>
                      <Input
                        id={`alloc-${f}`}
                        type="number"
                        step="0.01"
                        value={alloc[f]}
                        onChange={(e) => setAlloc({ ...alloc, [f]: parseNumber(e.target.value) })}
                        className="bg-slate-800 border-slate-600 text-white"
                      />
                    </div>
                  ))}
                </div>
                <div className="text-xs text-slate-400">
                  Allocation Sum: <span className={allocOk ? "text-emerald-400" : "text-rose-400"}>{toFixedPct(allocSum)}%</span> (should be 100%)
                </div>
                <div className="text-sm text-slate-300">
                  Est. P&L: <strong className="text-cyan-400">{currencyFormatter(totalPnL)}</strong>
                </div>
              </div>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie 
                      data={pieAlloc} 
                      dataKey="value" 
                      nameKey="name" 
                      outerRadius={80} 
                      innerRadius={40}
                    >
                      {pieAlloc.map((_, idx) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(val) => `${Number(val).toFixed(2)}%`}
                      contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="dashboard-card">
            <CardHeader>
              <CardTitle className="text-white">Data Import</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input 
                type="file" 
                accept=".xlsx,.xls,.csv" 
                ref={fileInputRef} 
                onChange={onUploadFile}
                className="bg-slate-800 border-slate-600 text-white"
              />
              <div className="text-xs text-slate-400">
                Expected columns in sheet <strong>"FIDUS Investment Committee"</strong>: 
                <code className="bg-slate-700 px-1 rounded ml-1">Week</code>, 
                <code className="bg-slate-700 px-1 rounded ml-1">CORE</code>, 
                <code className="bg-slate-700 px-1 rounded ml-1">BALANCE</code>, 
                <code className="bg-slate-700 px-1 rounded ml-1">DYNAMIC</code>
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => fileInputRef.current?.click()}
                  className="text-white border-slate-600"
                >
                  <Upload size={16} className="mr-2" />
                  Choose File
                </Button>
                <Button 
                  variant="ghost" 
                  onClick={resetData}
                  className="text-white hover:bg-slate-700"
                >
                  Reset
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Simulation + Charts */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3 mb-6">
          <Card className="dashboard-card md:col-span-1">
            <CardHeader>
              <CardTitle className="text-white">Simulation (this week)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="sim-enabled" className="text-slate-300">Enable Simulation</Label>
                <Switch 
                  id="sim-enabled" 
                  checked={sim.enabled} 
                  onCheckedChange={(v) => setSim({ ...sim, enabled: v })} 
                />
              </div>
              <div className={`grid grid-cols-3 gap-3 ${!sim.enabled ? "opacity-50" : ""}`}>
                {fields.map((f) => (
                  <div key={`sim-${f}`}>
                    <Label htmlFor={`sim-${f}`} className="text-slate-300">{f} %</Label>
                    <Input
                      id={`sim-${f}`}
                      type="number"
                      step="0.01"
                      disabled={!sim.enabled}
                      value={sim[f]}
                      onChange={(e) => setSim({ ...sim, [f]: e.target.value })}
                      className="bg-slate-800 border-slate-600 text-white"
                    />
                  </div>
                ))}
              </div>
              <div className="text-xs text-slate-400">
                Simulation temporarily overrides the last row's weekly returns without saving changes.
              </div>
            </CardContent>
          </Card>

          <Card className="dashboard-card md:col-span-2">
            <CardHeader>
              <CardTitle className="text-white">Weekly vs. Cumulative</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={effectiveRows}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                    <XAxis dataKey="week" stroke="#94a3b8" />
                    <YAxis tickFormatter={(v) => `${v}%`} stroke="#94a3b8" />
                    <Tooltip 
                      formatter={(v) => `${Number(v).toFixed(2)}%`}
                      contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                    />
                    <Legend />
                    <Bar dataKey="CORE" name="CORE %" fill="#00bcd4" />
                    <Bar dataKey="BALANCE" name="BALANCE %" fill="#ffa726" />
                    <Bar dataKey="DYNAMIC" name="DYNAMIC %" fill="#4caf50" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={mergedCum}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                    <XAxis dataKey="week" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                    <Legend />
                    <Line type="monotone" dataKey="CORE" name="CORE NAV" dot={false} stroke="#00bcd4" />
                    <Line type="monotone" dataKey="BALANCE" name="BALANCE NAV" dot={false} stroke="#ffa726" />
                    <Line type="monotone" dataKey="DYNAMIC" name="DYNAMIC NAV" dot={false} stroke="#4caf50" />
                    <Line type="monotone" dataKey="TOTAL" name="TOTAL NAV (weighted)" strokeDasharray="4 2" dot={false} stroke="#ffffff" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Data Table */}
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white">Week-by-Week Input</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] table-auto border-collapse">
                <thead>
                  <tr className="bg-slate-700 text-left text-sm">
                    <th className="p-3 text-slate-300">#</th>
                    <th className="p-3 text-slate-300">Week</th>
                    {fields.map((f) => (
                      <th className="p-3 text-slate-300" key={`th-${f}`}>{f} %</th>
                    ))}
                    <th className="p-3 text-slate-300"></th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => (
                    <tr key={i} className="border-b border-slate-600">
                      <td className="p-3 text-slate-400">{i + 1}</td>
                      <td className="p-3">
                        <Input
                          value={r.week}
                          onChange={(e) => handleCellChange(i, "week", e.target.value)}
                          className="bg-slate-800 border-slate-600 text-white"
                        />
                      </td>
                      {fields.map((f) => (
                        <td className="p-3" key={`cell-${i}-${f}`}>
                          <Input
                            type="number"
                            step="0.01"
                            value={r[f]}
                            onChange={(e) => handleCellChange(i, f, e.target.value)}
                            className="bg-slate-800 border-slate-600 text-white"
                          />
                        </td>
                      ))}
                      <td className="p-3 text-right">
                        <Button 
                          variant="ghost" 
                          onClick={() => removeRow(i)}
                          className="text-red-400 hover:bg-red-900/20"
                        >
                          <Trash2 size={16} />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex gap-2">
              <Button onClick={addRow} className="bg-cyan-600 hover:bg-cyan-700">
                <Plus size={16} className="mr-2" />
                Add Week
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setRows(rows.map((r) => ({ ...r, CORE: 0, BALANCE: 0, DYNAMIC: 0 })))}
                className="text-white border-slate-600"
              >
                Clear Returns
              </Button>
            </div>
          </CardContent>
        </Card>

            {/* Notes */}
            <div className="mt-6 text-xs text-slate-400 bg-slate-800/50 p-4 rounded-lg">
              <p>
                <strong>Tip:</strong> Use the <strong>Simulation</strong> toggle to preview this week's hypothetical returns without saving. 
                Upload your <em>FIDUS Projections.xlsx</em> (sheet <em>FIDUS Investment Committee</em>) to auto-populate the table. 
                All edits persist to your browser's local storage.
              </p>
            </div>
          </TabsContent>

          <TabsContent value="clients" className="mt-6">
            <ClientManagement />
          </TabsContent>

          <TabsContent value="documents" className="mt-6">
            <DocumentPortal user={user} userType="admin" />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;