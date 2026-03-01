"""
Hull Risk Engine Backend API Tests
Tests for the institutional-grade risk management features

Test Coverage:
- Admin login with Password123 credentials
- /api/admin/risk-engine/instrument-specs - Get all instrument specifications
- /api/admin/risk-engine/calculate-max-lots - Position sizing calculation
- /api/admin/risk-engine/policy - Risk policy retrieval
- /api/admin/risk-engine/narrative - Risk profile interpretation
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://hull-risk-preview.preview.emergentagent.com')


class TestHullRiskEngine:
    """Hull Risk Engine API Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - Login and get token"""
        # Login with admin credentials
        login_resp = requests.post(
            f'{BASE_URL}/api/auth/login',
            json={
                'username': 'admin',
                'password': 'Password123',
                'user_type': 'admin'
            },
            timeout=30
        )
        
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        data = login_resp.json()
        assert 'token' in data, "No token in login response"
        
        self.token = data['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    def test_admin_login(self):
        """Test admin login with Password123 credentials"""
        login_resp = requests.post(
            f'{BASE_URL}/api/auth/login',
            json={
                'username': 'admin',
                'password': 'Password123',
                'user_type': 'admin'
            },
            timeout=30
        )
        
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert 'token' in data
        assert data.get('type') == 'admin' or data.get('user_type') == 'admin'
        print(f"✅ Admin login successful")
    
    def test_get_instrument_specs(self):
        """Test /api/admin/risk-engine/instrument-specs returns 7+ instruments"""
        resp = requests.get(
            f'{BASE_URL}/api/admin/risk-engine/instrument-specs',
            headers=self.headers,
            timeout=30
        )
        
        assert resp.status_code == 200
        data = resp.json()
        
        assert data.get('success') == True
        instruments = data.get('instruments', [])
        
        # Should have at least 7 instruments
        assert len(instruments) >= 7, f"Expected at least 7 instruments, got {len(instruments)}"
        
        # Check for required FIDUS Tier-1 instruments
        symbols = [inst.get('symbol') for inst in instruments]
        required_instruments = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'US30', 'DE40']
        
        for required in required_instruments:
            assert required in symbols, f"Missing required instrument: {required}"
        
        print(f"✅ Found {len(instruments)} instruments: {symbols}")
    
    def test_get_xauusd_specs(self):
        """Test getting XAUUSD (Gold) specific instrument specs"""
        resp = requests.get(
            f'{BASE_URL}/api/admin/risk-engine/instrument-specs/XAUUSD',
            headers=self.headers,
            timeout=30
        )
        
        assert resp.status_code == 200
        data = resp.json()
        
        assert data.get('success') == True
        specs = data.get('specs', {})
        
        assert specs.get('symbol') == 'XAUUSD'
        assert specs.get('name') == 'Gold'
        assert specs.get('contract_size') == 100  # 100 oz per lot
        
        print(f"✅ XAUUSD specs: contract_size={specs.get('contract_size')}, pip_value_per_lot={specs.get('pip_value_per_lot')}")
    
    def test_calculate_max_lots_xauusd(self):
        """
        Test MaxLotsAllowed calculation for XAUUSD
        
        Expected: $100k equity, XAUUSD, $10 stop = 1.0 lots (RISK bound)
        
        Calculation:
        - Risk Budget = $100,000 * 1% = $1,000
        - Loss per lot at $10 stop = 100 oz * $10 = $1,000
        - MaxLotsRisk = $1,000 / $1,000 = 1.0 lots
        - MaxLotsMargin = much higher (200:1 leverage)
        - MaxLotsAllowed = min(1.0, margin_lots) = 1.0 (RISK binds)
        """
        resp = requests.post(
            f'{BASE_URL}/api/admin/risk-engine/calculate-max-lots',
            headers=self.headers,
            json={
                'equity': 100000,
                'symbol': 'XAUUSD',
                'stop_distance': 10
            },
            timeout=30
        )
        
        assert resp.status_code == 200
        data = resp.json()
        
        assert data.get('success') == True
        
        # Verify calculation components
        assert data.get('equity') == 100000
        assert data.get('symbol') == 'XAUUSD'
        assert data.get('risk_budget') == 1000.0  # 1% of 100k
        assert data.get('stop_distance') == 10
        assert data.get('loss_per_lot_at_stop') == 1000.0  # 100 oz * $10
        
        # Verify MaxLotsRisk calculation: RiskBudget / LossPerLotAtStop
        assert data.get('max_lots_risk') == 1.0  # 1000 / 1000 = 1.0
        
        # Verify MaxLotsAllowed = min(MaxLotsRisk, MaxLotsMargin)
        assert data.get('max_lots_allowed') == 1.0
        
        # Verify RISK is the binding constraint (not MARGIN)
        assert data.get('binding_constraint') == 'RISK'
        
        print(f"✅ MaxLotsAllowed calculation correct: {data.get('max_lots_allowed')} lots (RISK bound)")
        print(f"   Risk Budget: ${data.get('risk_budget')}")
        print(f"   Loss per Lot at Stop: ${data.get('loss_per_lot_at_stop')}")
        print(f"   Max Lots Risk: {data.get('max_lots_risk')}")
        print(f"   Max Lots Margin: {data.get('max_lots_margin')}")
    
    def test_calculate_max_lots_eurusd(self):
        """Test MaxLotsAllowed calculation for EURUSD"""
        resp = requests.post(
            f'{BASE_URL}/api/admin/risk-engine/calculate-max-lots',
            headers=self.headers,
            json={
                'equity': 50000,
                'symbol': 'EURUSD',
                'stop_distance': 0.0050  # 50 pips
            },
            timeout=30
        )
        
        assert resp.status_code == 200
        data = resp.json()
        
        assert data.get('success') == True
        assert data.get('symbol') == 'EURUSD'
        assert data.get('max_lots_allowed') > 0
        
        print(f"✅ EURUSD MaxLotsAllowed: {data.get('max_lots_allowed')} lots ({data.get('binding_constraint')} bound)")
    
    def test_get_risk_policy(self):
        """
        Test /api/admin/risk-engine/policy returns default risk parameters
        
        Expected defaults:
        - 1% risk per trade
        - 3% daily loss
        - 25% max margin
        - 200:1 leverage
        """
        resp = requests.get(
            f'{BASE_URL}/api/admin/risk-engine/policy',
            headers=self.headers,
            timeout=30
        )
        
        assert resp.status_code == 200
        data = resp.json()
        
        assert data.get('success') == True
        policy = data.get('policy', {})
        
        # Verify default risk parameters
        assert policy.get('max_risk_per_trade_pct') == 1.0, "Expected 1% risk per trade"
        assert policy.get('max_intraday_loss_pct') == 3.0, "Expected 3% daily loss"
        assert policy.get('max_margin_usage_pct') == 25.0, "Expected 25% max margin"
        assert policy.get('leverage') == 200, "Expected 200:1 leverage"
        
        print(f"✅ Risk Policy verified:")
        print(f"   Max Risk Per Trade: {policy.get('max_risk_per_trade_pct')}%")
        print(f"   Max Intraday Loss: {policy.get('max_intraday_loss_pct')}%")
        print(f"   Max Margin Usage: {policy.get('max_margin_usage_pct')}%")
        print(f"   Leverage: {policy.get('leverage')}:1")
    
    def test_get_risk_narrative(self):
        """
        Test /api/admin/risk-engine/narrative returns Risk Profile Interpretation
        
        Should include:
        - Executive Read/Summary
        - Metric interpretations
        - Red flags (if any)
        - Actionable fixes (if any)
        """
        resp = requests.get(
            f'{BASE_URL}/api/admin/risk-engine/narrative',
            headers=self.headers,
            params={'period_days': 30},
            timeout=30
        )
        
        assert resp.status_code == 200
        data = resp.json()
        
        assert data.get('success') == True
        
        # Check for narrative components
        assert 'executive_read' in data, "Missing executive_read in narrative"
        assert 'metric_interpretations' in data, "Missing metric_interpretations in narrative"
        
        # Executive read should be a list of bullet points
        executive_read = data.get('executive_read', [])
        assert isinstance(executive_read, list), "executive_read should be a list"
        
        # Metric interpretations should be a list of objects
        interpretations = data.get('metric_interpretations', [])
        assert isinstance(interpretations, list), "metric_interpretations should be a list"
        
        if interpretations:
            # Check structure of metric interpretation
            first_interp = interpretations[0]
            assert 'metric' in first_interp, "Metric interpretation missing 'metric' field"
            assert 'value' in first_interp, "Metric interpretation missing 'value' field"
            assert 'interpretation' in first_interp, "Metric interpretation missing 'interpretation' field"
        
        print(f"✅ Risk Narrative returned:")
        print(f"   Executive Summary items: {len(executive_read)}")
        print(f"   Metric interpretations: {len(interpretations)}")
        print(f"   Red flags: {len(data.get('red_flags', []))}")
        print(f"   Actionable fixes: {len(data.get('actionable_fixes', []))}")


class TestTradingAnalyticsIntegration:
    """Integration tests for Trading Analytics with Risk Engine"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - Login and get token"""
        login_resp = requests.post(
            f'{BASE_URL}/api/auth/login',
            json={
                'username': 'admin',
                'password': 'Password123',
                'user_type': 'admin'
            },
            timeout=30
        )
        
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert 'token' in data
        
        self.token = data['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    def test_trading_analytics_managers(self):
        """Test /api/admin/trading-analytics/managers returns strategy data"""
        resp = requests.get(
            f'{BASE_URL}/api/admin/trading-analytics/managers',
            headers=self.headers,
            params={'period_days': 30},
            timeout=30
        )
        
        assert resp.status_code == 200
        data = resp.json()
        
        assert data.get('success') == True
        managers = data.get('managers', [])
        
        # Should have at least some managers
        assert len(managers) > 0, "No managers found in trading analytics"
        
        # Check manager structure
        if managers:
            first_manager = managers[0]
            assert 'manager_name' in first_manager
            assert 'account' in first_manager
            
        print(f"✅ Found {len(managers)} managers in trading analytics")
        for m in managers[:3]:
            print(f"   - {m.get('manager_name')} (#{m.get('account')})")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
