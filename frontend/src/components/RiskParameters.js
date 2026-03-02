import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { 
  Shield, 
  Save, 
  RefreshCw, 
  AlertTriangle,
  CheckCircle,
  Settings,
  Percent,
  TrendingDown,
  Clock,
  DollarSign,
  Zap,
  Info,
  Edit2,
  X
} from 'lucide-react';
import './RiskParameters.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const RiskParameters = () => {
  const [policy, setPolicy] = useState({
    max_risk_per_trade_pct: 1.0,
    max_intraday_loss_pct: 3.0,
    max_weekly_loss_pct: 6.0,
    max_monthly_drawdown_pct: 10.0,
    max_margin_usage_pct: 25.0,
    leverage: 200,
    force_flat_time: "16:50",
    force_flat_timezone: "America/New_York"
  });
  
  const [originalPolicy, setOriginalPolicy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [leverageByClass, setLeverageByClass] = useState({});

  useEffect(() => {
    fetchRiskPolicy();
    fetchLeverageSettings();
  }, []);

  const fetchRiskPolicy = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('fidus_token');
      const response = await fetch(`${BACKEND_URL}/api/admin/risk-engine/policy`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      if (data.success && data.policy) {
        setPolicy(data.policy);
        setOriginalPolicy(data.policy);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchLeverageSettings = async () => {
    try {
      const token = localStorage.getItem('fidus_token');
      const response = await fetch(`${BACKEND_URL}/api/admin/risk-engine/instrument-specs`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      if (data.success && data.instruments) {
        // Group by asset class to show leverage
        const byClass = {};
        data.instruments.forEach(inst => {
          if (!byClass[inst.asset_class]) {
            byClass[inst.asset_class] = {
              leverage: inst.pro_leverage,
              margin: inst.margin_pct,
              count: 0
            };
          }
          byClass[inst.asset_class].count++;
        });
        setLeverageByClass(byClass);
      }
    } catch (err) {
      console.error('Error fetching leverage:', err);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      
      const token = localStorage.getItem('fidus_token');
      const response = await fetch(`${BACKEND_URL}/api/admin/risk-engine/policy`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(policy)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuccess('Risk parameters saved successfully');
        setOriginalPolicy(policy);
        setEditMode(false);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(data.error || 'Failed to save');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setPolicy(originalPolicy);
    setEditMode(false);
    setError(null);
  };

  const handleChange = (field, value) => {
    setPolicy(prev => ({
      ...prev,
      [field]: parseFloat(value) || value
    }));
  };

  const hasChanges = JSON.stringify(policy) !== JSON.stringify(originalPolicy);

  // Calculate risk budget example
  const exampleEquity = 100000;
  const riskBudget = exampleEquity * (policy.max_risk_per_trade_pct / 100);
  const dailyLossLimit = exampleEquity * (policy.max_intraday_loss_pct / 100);
  const weeklyLossLimit = exampleEquity * (policy.max_weekly_loss_pct / 100);
  const monthlyDrawdownLimit = exampleEquity * (policy.max_monthly_drawdown_pct / 100);

  if (loading) {
    return (
      <div className="risk-params-loading">
        <RefreshCw className="spin" size={32} />
        <p>Loading risk parameters...</p>
      </div>
    );
  }

  return (
    <div className="risk-params-container" data-testid="risk-parameters">
      {/* Header */}
      <div className="risk-params-header">
        <div className="risk-params-title">
          <Shield size={28} />
          <div>
            <h1>Risk Parameters</h1>
            <p>Hull-style risk management configuration</p>
          </div>
        </div>
        <div className="risk-params-actions">
          {!editMode ? (
            <Button onClick={() => setEditMode(true)} className="risk-edit-btn">
              <Edit2 size={16} />
              Edit Parameters
            </Button>
          ) : (
            <>
              <Button onClick={handleCancel} variant="outline" className="risk-cancel-btn">
                <X size={16} />
                Cancel
              </Button>
              <Button 
                onClick={handleSave} 
                disabled={saving || !hasChanges}
                className="risk-save-btn"
              >
                {saving ? <RefreshCw size={16} className="spin" /> : <Save size={16} />}
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="risk-alert error">
          <AlertTriangle size={18} />
          {error}
        </div>
      )}
      {success && (
        <div className="risk-alert success">
          <CheckCircle size={18} />
          {success}
        </div>
      )}

      {/* Main Content Grid */}
      <div className="risk-params-grid">
        {/* Trade Risk Limits */}
        <Card className="risk-card">
          <CardHeader className="risk-card-header">
            <CardTitle className="risk-card-title">
              <Percent size={20} />
              Trade Risk Limits
            </CardTitle>
          </CardHeader>
          <CardContent className="risk-card-content">
            <div className="risk-param-group">
              <div className="risk-param-item">
                <Label>Max Risk Per Trade</Label>
                <div className="risk-input-wrapper">
                  <Input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="5"
                    value={policy.max_risk_per_trade_pct}
                    onChange={(e) => handleChange('max_risk_per_trade_pct', e.target.value)}
                    disabled={!editMode}
                    className="risk-input"
                  />
                  <span className="risk-input-suffix">%</span>
                </div>
                <p className="risk-param-hint">
                  @ $100k = ${riskBudget.toLocaleString()} max loss per trade
                </p>
              </div>

              <div className="risk-param-item">
                <Label>Max Margin Usage</Label>
                <div className="risk-input-wrapper">
                  <Input
                    type="number"
                    step="1"
                    min="5"
                    max="100"
                    value={policy.max_margin_usage_pct}
                    onChange={(e) => handleChange('max_margin_usage_pct', e.target.value)}
                    disabled={!editMode}
                    className="risk-input"
                  />
                  <span className="risk-input-suffix">%</span>
                </div>
                <p className="risk-param-hint">Maximum equity to use as margin</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Loss Limits */}
        <Card className="risk-card">
          <CardHeader className="risk-card-header">
            <CardTitle className="risk-card-title">
              <TrendingDown size={20} />
              Loss Limits
            </CardTitle>
          </CardHeader>
          <CardContent className="risk-card-content">
            <div className="risk-param-group">
              <div className="risk-param-item">
                <Label>Max Intraday Loss</Label>
                <div className="risk-input-wrapper">
                  <Input
                    type="number"
                    step="0.5"
                    min="1"
                    max="10"
                    value={policy.max_intraday_loss_pct}
                    onChange={(e) => handleChange('max_intraday_loss_pct', e.target.value)}
                    disabled={!editMode}
                    className="risk-input"
                  />
                  <span className="risk-input-suffix">%</span>
                </div>
                <p className="risk-param-hint">
                  @ $100k = ${dailyLossLimit.toLocaleString()} daily limit
                </p>
              </div>

              <div className="risk-param-item">
                <Label>Max Weekly Loss</Label>
                <div className="risk-input-wrapper">
                  <Input
                    type="number"
                    step="0.5"
                    min="1"
                    max="20"
                    value={policy.max_weekly_loss_pct}
                    onChange={(e) => handleChange('max_weekly_loss_pct', e.target.value)}
                    disabled={!editMode}
                    className="risk-input"
                  />
                  <span className="risk-input-suffix">%</span>
                </div>
                <p className="risk-param-hint">
                  @ $100k = ${weeklyLossLimit.toLocaleString()} weekly limit
                </p>
              </div>

              <div className="risk-param-item">
                <Label>Max Monthly Drawdown</Label>
                <div className="risk-input-wrapper">
                  <Input
                    type="number"
                    step="1"
                    min="5"
                    max="30"
                    value={policy.max_monthly_drawdown_pct}
                    onChange={(e) => handleChange('max_monthly_drawdown_pct', e.target.value)}
                    disabled={!editMode}
                    className="risk-input"
                  />
                  <span className="risk-input-suffix">%</span>
                </div>
                <p className="risk-param-hint">
                  @ $100k = ${monthlyDrawdownLimit.toLocaleString()} max drawdown
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Force Flat Settings */}
        <Card className="risk-card">
          <CardHeader className="risk-card-header">
            <CardTitle className="risk-card-title">
              <Clock size={20} />
              Force Flat (EOD)
            </CardTitle>
          </CardHeader>
          <CardContent className="risk-card-content">
            <div className="risk-param-group">
              <div className="risk-param-item">
                <Label>Force Flat Time</Label>
                <div className="risk-input-wrapper">
                  <Input
                    type="time"
                    value={policy.force_flat_time}
                    onChange={(e) => handleChange('force_flat_time', e.target.value)}
                    disabled={!editMode}
                    className="risk-input"
                  />
                </div>
                <p className="risk-param-hint">Close all positions at this time</p>
              </div>

              <div className="risk-param-item">
                <Label>Timezone</Label>
                <div className="risk-input-wrapper">
                  <Input
                    type="text"
                    value={policy.force_flat_timezone}
                    onChange={(e) => handleChange('force_flat_timezone', e.target.value)}
                    disabled={!editMode}
                    className="risk-input"
                  />
                </div>
                <p className="risk-param-hint">e.g., America/New_York</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Leverage by Asset Class */}
        <Card className="risk-card leverage-card">
          <CardHeader className="risk-card-header">
            <CardTitle className="risk-card-title">
              <Zap size={20} />
              Leverage by Asset Class
            </CardTitle>
          </CardHeader>
          <CardContent className="risk-card-content">
            <div className="leverage-table-wrapper">
              <table className="leverage-table">
                <thead>
                  <tr>
                    <th>Asset Class</th>
                    <th>Leverage</th>
                    <th>Margin</th>
                    <th>Instruments</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(leverageByClass).map(([cls, data]) => (
                    <tr key={cls}>
                      <td>
                        <span className={`class-badge ${cls.toLowerCase().replace('_', '-')}`}>
                          {cls.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="leverage-value">{data.leverage}:1</td>
                      <td className="margin-value">{data.margin}%</td>
                      <td className="count-value">{data.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="leverage-note">
              <Info size={14} />
              Leverage settings are managed per instrument in the Instruments Specifications tab
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Risk Score Penalties Reference */}
      <Card className="risk-card penalties-card">
        <CardHeader className="risk-card-header">
          <CardTitle className="risk-card-title">
            <AlertTriangle size={20} />
            Risk Score Penalty Structure
          </CardTitle>
        </CardHeader>
        <CardContent className="risk-card-content">
          <div className="penalties-grid">
            <div className="penalty-item">
              <span className="penalty-type">Lot Size Breach</span>
              <span className="penalty-value">-6 pts</span>
              <span className="penalty-cap">Cap: -30</span>
            </div>
            <div className="penalty-item">
              <span className="penalty-type">Risk Per Trade Breach</span>
              <span className="penalty-value">-8 pts</span>
              <span className="penalty-cap">Cap: -40</span>
            </div>
            <div className="penalty-item">
              <span className="penalty-type">Margin Breach (first day)</span>
              <span className="penalty-value">-10 pts</span>
              <span className="penalty-cap">Cap: -25</span>
            </div>
            <div className="penalty-item">
              <span className="penalty-type">Daily Loss Breach</span>
              <span className="penalty-value">-20 pts</span>
              <span className="penalty-cap">Cap: -40</span>
            </div>
            <div className="penalty-item">
              <span className="penalty-type">Weekly Loss Breach</span>
              <span className="penalty-value">-25 pts</span>
              <span className="penalty-cap">Cap: -50</span>
            </div>
            <div className="penalty-item">
              <span className="penalty-type">Monthly Drawdown Breach</span>
              <span className="penalty-value">-40 pts</span>
              <span className="penalty-cap">One-time</span>
            </div>
            <div className="penalty-item">
              <span className="penalty-type">Overnight Position</span>
              <span className="penalty-value">-15 pts</span>
              <span className="penalty-cap">Cap: -45</span>
            </div>
          </div>
          <div className="score-labels">
            <span className="score-label strong">80-100: Strong</span>
            <span className="score-label moderate">60-79: Moderate</span>
            <span className="score-label weak">40-59: Weak</span>
            <span className="score-label critical">0-39: Critical</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RiskParameters;
