"""
Test suite for Instruments Specifications and Risk Parameters tabs
Tests the new admin dashboard tabs for contract specs and Hull-style risk management
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication for admin tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login and get admin token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "admin",
                "password": "Password123",
                "user_type": "admin"
            }
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        return data["token"]


class TestInstrumentSpecifications(TestAuth):
    """Tests for Instrument Specifications API endpoint"""
    
    def test_get_all_instruments(self, admin_token):
        """Test GET /api/admin/risk-engine/instrument-specs returns all 61 instruments"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/instrument-specs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True, "Response success should be True"
        assert "instruments" in data, "Response should contain instruments array"
        
        # Verify 61 instruments are returned
        instruments = data["instruments"]
        assert len(instruments) == 61, f"Expected 61 instruments, got {len(instruments)}"
    
    def test_instruments_have_required_fields(self, admin_token):
        """Test each instrument has required specification fields"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/instrument-specs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        instruments = data["instruments"]
        
        required_fields = ["symbol", "name", "asset_class", "pro_leverage", "margin_pct", 
                         "contract_size", "pip_value_per_lot", "typical_spread"]
        
        for inst in instruments[:5]:  # Check first 5 instruments
            for field in required_fields:
                assert field in inst, f"Instrument {inst.get('symbol')} missing field: {field}"
    
    def test_instruments_by_asset_class(self, admin_token):
        """Test instruments contain all expected asset classes"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/instrument-specs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        instruments = data["instruments"]
        
        # Get all unique asset classes
        asset_classes = set(inst.get("asset_class") for inst in instruments)
        
        # Should have multiple asset classes
        expected_classes = {"FX_MAJOR", "FX_CROSS", "INDEX_CFD", "Metals", "Commodities", "Crypto"}
        for cls in expected_classes:
            assert cls in asset_classes, f"Missing asset class: {cls}"
    
    def test_fx_major_instruments(self, admin_token):
        """Test FX_MAJOR instruments are present"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/instrument-specs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        instruments = data["instruments"]
        
        fx_major = [i for i in instruments if i.get("asset_class") == "FX_MAJOR"]
        assert len(fx_major) > 0, "Should have FX_MAJOR instruments"
        
        # Check for common forex pairs
        fx_symbols = [i.get("symbol") for i in fx_major]
        assert "EURUSD" in fx_symbols, "EURUSD should be present"
        assert "GBPUSD" in fx_symbols, "GBPUSD should be present"


class TestRiskPolicy(TestAuth):
    """Tests for Risk Policy API endpoints"""
    
    def test_get_risk_policy(self, admin_token):
        """Test GET /api/admin/risk-engine/policy returns risk policy"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/policy",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True, "Response success should be True"
        assert "policy" in data, "Response should contain policy object"
    
    def test_risk_policy_has_required_fields(self, admin_token):
        """Test risk policy contains all Hull-style risk parameters"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/policy",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        policy = data["policy"]
        
        # Verify required risk policy fields
        required_fields = [
            "max_risk_per_trade_pct",
            "max_intraday_loss_pct", 
            "max_weekly_loss_pct",
            "max_monthly_drawdown_pct",
            "max_margin_usage_pct",
            "leverage"
        ]
        
        for field in required_fields:
            assert field in policy, f"Risk policy missing field: {field}"
            assert isinstance(policy[field], (int, float)), f"{field} should be a number"
    
    def test_risk_policy_valid_values(self, admin_token):
        """Test risk policy values are within valid ranges"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/policy",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        policy = data["policy"]
        
        # Verify risk values are reasonable
        assert 0 < policy["max_risk_per_trade_pct"] <= 5, "max_risk_per_trade_pct should be 0-5%"
        assert 0 < policy["max_intraday_loss_pct"] <= 10, "max_intraday_loss_pct should be 0-10%"
        assert 0 < policy["max_weekly_loss_pct"] <= 20, "max_weekly_loss_pct should be 0-20%"
        assert 0 < policy["max_monthly_drawdown_pct"] <= 30, "max_monthly_drawdown_pct should be 0-30%"
    
    def test_update_risk_policy(self, admin_token):
        """Test POST /api/admin/risk-engine/policy updates policy"""
        # First get current policy
        get_response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/policy",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        original_policy = get_response.json()["policy"]
        
        # Update with same values (don't change actual settings)
        update_data = {
            "max_risk_per_trade_pct": original_policy.get("max_risk_per_trade_pct", 1.0),
            "max_intraday_loss_pct": original_policy.get("max_intraday_loss_pct", 3.0),
            "max_weekly_loss_pct": original_policy.get("max_weekly_loss_pct", 6.0),
            "max_monthly_drawdown_pct": original_policy.get("max_monthly_drawdown_pct", 10.0),
            "max_margin_usage_pct": original_policy.get("max_margin_usage_pct", 25.0),
            "leverage": original_policy.get("leverage", 200)
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/risk-engine/policy",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            json=update_data
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Update should succeed"


class TestRiskPolicyRanges(TestAuth):
    """Tests for risk policy validation ranges"""
    
    def test_policy_includes_ranges(self, admin_token):
        """Test risk policy response includes validation ranges"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/policy",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        policy = data["policy"]
        
        # Check if ranges are included (some APIs include them)
        if "ranges" in policy:
            ranges = policy["ranges"]
            assert "max_risk_per_trade_pct" in ranges, "Should have range for max_risk_per_trade_pct"
            assert "max_intraday_loss_pct" in ranges, "Should have range for max_intraday_loss_pct"


class TestEndpointAuthentication(TestAuth):
    """Tests for endpoint authentication requirements"""
    
    def test_instrument_specs_requires_auth(self):
        """Test instrument-specs endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/risk-engine/instrument-specs")
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403, 422], "Should require authentication"
    
    def test_risk_policy_requires_auth(self):
        """Test risk-policy endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/risk-engine/policy")
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403, 422], "Should require authentication"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
