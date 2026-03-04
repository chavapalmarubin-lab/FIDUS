import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  ChevronUp, 
  ChevronDown,
  TrendingUp,
  DollarSign,
  Percent,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import './InstrumentSpecifications.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const InstrumentSpecifications = () => {
  const [instruments, setInstruments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClass, setSelectedClass] = useState('ALL');
  const [sortField, setSortField] = useState('symbol');
  const [sortDirection, setSortDirection] = useState('asc');

  const assetClasses = ['ALL', 'FX_MAJOR', 'FX_CROSS', 'INDEX_CFD', 'Metals', 'Commodities', 'Crypto'];

  useEffect(() => {
    fetchInstruments();
  }, []);

  const fetchInstruments = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('fidus_token');
      const response = await fetch(`${BACKEND_URL}/api/admin/risk-engine/instrument-specs`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      if (data.success && data.instruments) {
        setInstruments(data.instruments);
      } else {
        setError('Failed to load instruments');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredInstruments = useMemo(() => {
    let filtered = instruments;
    
    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(inst => 
        inst.symbol?.toLowerCase().includes(term) ||
        inst.name?.toLowerCase().includes(term)
      );
    }
    
    // Filter by asset class
    if (selectedClass !== 'ALL') {
      filtered = filtered.filter(inst => inst.asset_class === selectedClass);
    }
    
    // Sort
    filtered.sort((a, b) => {
      let aVal = a[sortField] || '';
      let bVal = b[sortField] || '';
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      aVal = String(aVal).toLowerCase();
      bVal = String(bVal).toLowerCase();
      
      if (sortDirection === 'asc') {
        return aVal.localeCompare(bVal);
      }
      return bVal.localeCompare(aVal);
    });
    
    return filtered;
  }, [instruments, searchTerm, selectedClass, sortField, sortDirection]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const SortIcon = ({ field }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />;
  };

  const exportToCSV = () => {
    const headers = ['Symbol', 'Name', 'Asset Class', 'Leverage', 'Margin %', 'Contract Size', 'Pip Value', 'Spread', 'Trading Hours'];
    const rows = filteredInstruments.map(inst => [
      inst.symbol,
      inst.name,
      inst.asset_class,
      `${inst.pro_leverage}:1`,
      `${inst.margin_pct}%`,
      inst.contract_size,
      inst.pip_value_per_lot,
      inst.typical_spread,
      inst.trading_hours || 'N/A'
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'instrument_specifications.csv';
    a.click();
  };

  // Summary stats
  const stats = useMemo(() => {
    const byClass = {};
    instruments.forEach(inst => {
      byClass[inst.asset_class] = (byClass[inst.asset_class] || 0) + 1;
    });
    return {
      total: instruments.length,
      byClass
    };
  }, [instruments]);

  if (loading) {
    return (
      <div className="inst-specs-loading">
        <RefreshCw className="spin" size={32} />
        <p>Loading instrument specifications...</p>
      </div>
    );
  }

  return (
    <div className="inst-specs-container" data-testid="instrument-specifications">
      {/* Header */}
      <div className="inst-specs-header">
        <div className="inst-specs-title">
          <TrendingUp size={28} />
          <div>
            <h1>Instrument Specifications</h1>
            <p>Contract specifications for all tradeable instruments</p>
          </div>
        </div>
        <div className="inst-specs-actions">
          <Button onClick={fetchInstruments} variant="outline" className="inst-refresh-btn">
            <RefreshCw size={16} />
            Refresh
          </Button>
          <Button onClick={exportToCSV} className="inst-export-btn">
            <Download size={16} />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="inst-specs-stats">
        <Card className="inst-stat-card">
          <CardContent className="inst-stat-content">
            <div className="inst-stat-icon total">
              <TrendingUp size={24} />
            </div>
            <div className="inst-stat-info">
              <span className="inst-stat-value">{stats.total}</span>
              <span className="inst-stat-label">Total Instruments</span>
            </div>
          </CardContent>
        </Card>
        {Object.entries(stats.byClass).map(([cls, count]) => (
          <Card key={cls} className="inst-stat-card">
            <CardContent className="inst-stat-content">
              <div className={`inst-stat-icon ${cls.toLowerCase().replace('_', '-')}`}>
                <DollarSign size={20} />
              </div>
              <div className="inst-stat-info">
                <span className="inst-stat-value">{count}</span>
                <span className="inst-stat-label">{cls.replace('_', ' ')}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="inst-specs-filters">
        <div className="inst-search-box">
          <Search size={18} />
          <Input
            placeholder="Search by symbol or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="inst-search-input"
          />
        </div>
        <div className="inst-class-filters">
          {assetClasses.map(cls => (
            <button
              key={cls}
              className={`inst-class-btn ${selectedClass === cls ? 'active' : ''}`}
              onClick={() => setSelectedClass(cls)}
            >
              {cls === 'ALL' ? 'All' : cls.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <Card className="inst-specs-table-card">
        <CardContent className="inst-specs-table-content">
          <div className="inst-specs-table-wrapper">
            <table className="inst-specs-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('symbol')} className="sortable">
                    Symbol <SortIcon field="symbol" />
                  </th>
                  <th onClick={() => handleSort('name')} className="sortable">
                    Name <SortIcon field="name" />
                  </th>
                  <th onClick={() => handleSort('asset_class')} className="sortable">
                    Class <SortIcon field="asset_class" />
                  </th>
                  <th onClick={() => handleSort('lucrum_leverage')} className="sortable">
                    Leverage <SortIcon field="lucrum_leverage" />
                  </th>
                  <th onClick={() => handleSort('margin_pct')} className="sortable">
                    Margin <SortIcon field="margin_pct" />
                  </th>
                  <th onClick={() => handleSort('contract_size')} className="sortable">
                    Contract Size <SortIcon field="contract_size" />
                  </th>
                  <th onClick={() => handleSort('pip_value_per_lot')} className="sortable">
                    Pip Value <SortIcon field="pip_value_per_lot" />
                  </th>
                  <th onClick={() => handleSort('typical_spread')} className="sortable">
                    Spread <SortIcon field="typical_spread" />
                  </th>
                  <th>Trading Hours</th>
                </tr>
              </thead>
              <tbody>
                {filteredInstruments.map((inst, idx) => (
                  <tr key={inst.symbol || idx} className={idx % 2 === 0 ? 'even' : 'odd'}>
                    <td className="inst-symbol">
                      <span className="symbol-badge">{inst.symbol}</span>
                    </td>
                    <td className="inst-name">{inst.name}</td>
                    <td>
                      <span className={`inst-class-badge ${inst.asset_class?.toLowerCase().replace('_', '-')}`}>
                        {inst.asset_class?.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="inst-leverage">
                      <span className="leverage-value">{inst.lucrum_leverage || inst.pro_leverage || 'N/A'}:1</span>
                    </td>
                    <td className="inst-margin">{(inst.margin_pct * 100).toFixed(2) || 'N/A'}%</td>
                    <td className="inst-contract">{inst.contract_size?.toLocaleString()}</td>
                    <td className="inst-pip">${inst.pip_value_per_lot}</td>
                    <td className="inst-spread">{inst.typical_spread}</td>
                    <td className="inst-hours">{inst.trading_hours || '24/5'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="inst-table-footer">
            Showing {filteredInstruments.length} of {instruments.length} instruments
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default InstrumentSpecifications;
