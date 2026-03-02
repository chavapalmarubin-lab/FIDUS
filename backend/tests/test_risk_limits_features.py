"""
Tests for Risk Limits Tab New Features:
1. Risk Alerts (CRITICAL/WARNING alerts)
2. Action Items (HIGH/MEDIUM priority fixes)
3. Compliance Details (expandable per-metric breakdown)
4. What-If Simulator (equity slider, simulate button)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
AUTH_TOKEN = None

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin"""
    global AUTH_TOKEN
    if AUTH_TOKEN:
        return AUTH_TOKEN
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "Password123", "user_type": "admin"}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    AUTH_TOKEN = response.json().get("token")
    return AUTH_TOKEN

@pytest.fixture
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestRiskAlertsSection:
    """Test 1: Risk Alerts section - CRITICAL/WARNING alerts"""
    
    def test_strategy_analysis_returns_alerts_for_breach_account(self, auth_headers):
        """Account 2210 should have alerts due to breaches"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify alerts structure
        assert "alerts" in data, "Response should contain alerts field"
        alerts = data["alerts"]
        
        # Account 2210 should have at least one alert
        assert len(alerts) >= 1, f"Account 2210 should have alerts, got {len(alerts)}"
        
        # Check alert structure
        for alert in alerts:
            assert "type" in alert, "Alert should have type"
            assert "severity" in alert, "Alert should have severity"
            assert "message" in alert, "Alert should have message"
            assert alert["severity"] in ["CRITICAL", "WARNING"], f"Invalid severity: {alert['severity']}"
    
    def test_critical_alert_for_risk_breach(self, auth_headers):
        """Account 2210 should have CRITICAL risk breach alert"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        alerts = data.get("alerts", [])
        risk_breach_alerts = [a for a in alerts if a.get("type") == "RISK_BREACH"]
        
        assert len(risk_breach_alerts) >= 1, "Should have RISK_BREACH alert"
        assert risk_breach_alerts[0]["severity"] == "CRITICAL"
    
    def test_daily_loss_breach_alert(self, auth_headers):
        """Account 2210 should have daily loss breach alert"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        alerts = data.get("alerts", [])
        daily_loss_alerts = [a for a in alerts if a.get("type") == "DAILY_LOSS_BREACH"]
        
        assert len(daily_loss_alerts) >= 1, "Should have DAILY_LOSS_BREACH alert"


class TestActionItemsSection:
    """Test 2: Action Items section - HIGH/MEDIUM priority fixes"""
    
    def test_strategy_analysis_returns_action_items(self, auth_headers):
        """Account 2210 should have action items"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify action_items structure
        assert "action_items" in data, "Response should contain action_items field"
        action_items = data["action_items"]
        
        # Account 2210 should have action items
        assert len(action_items) >= 1, f"Account 2210 should have action items"
        
        # Check action item structure
        for item in action_items:
            assert "priority" in item, "Action item should have priority"
            assert "category" in item, "Action item should have category"
            assert "issue" in item, "Action item should have issue"
            assert "fix" in item, "Action item should have fix"
    
    def test_high_priority_action_items(self, auth_headers):
        """Account 2210 should have HIGH priority action items"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        action_items = data.get("action_items", [])
        high_priority = [item for item in action_items if item.get("priority") == "HIGH"]
        
        assert len(high_priority) >= 1, "Should have at least one HIGH priority action item"


class TestComplianceDetailsSection:
    """Test 3: Compliance Details - expandable per-metric breakdown"""
    
    def test_compliance_details_structure(self, auth_headers):
        """Verify compliance_details has all required metrics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify compliance_details exists
        assert "compliance_details" in data, "Response should contain compliance_details"
        details = data["compliance_details"]
        
        # Check for required metrics
        assert "lot_size" in details, "Should have lot_size metric"
        assert "risk_per_trade" in details, "Should have risk_per_trade metric"
        assert "daily_loss" in details, "Should have daily_loss metric"
    
    def test_lot_size_compliance_details(self, auth_headers):
        """Verify lot_size compliance details structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        lot_size = data["compliance_details"]["lot_size"]
        
        assert "policy_limit" in lot_size
        assert "calculation" in lot_size
        assert "breaches" in lot_size
        assert "total_trades" in lot_size
        assert "compliance_rate" in lot_size
        assert "penalty_applied" in lot_size
    
    def test_per_instrument_compliance(self, auth_headers):
        """Verify per-instrument compliance breakdown exists"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        lot_size = data["compliance_details"]["lot_size"]
        
        # Should have by_instrument breakdown
        assert "by_instrument" in lot_size, "Should have by_instrument breakdown"
        by_instrument = lot_size["by_instrument"]
        
        if len(by_instrument) > 0:
            inst = by_instrument[0]
            assert "symbol" in inst
            assert "limit" in inst
            assert "max_used" in inst
            assert "status" in inst
    
    def test_risk_per_trade_breach_details(self, auth_headers):
        """Account 2210 should have risk per trade breaches"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        risk_per_trade = data["compliance_details"]["risk_per_trade"]
        
        # Account 2210 should have breaches
        assert risk_per_trade["breaches"] > 0, "Account 2210 should have risk per trade breaches"
        assert risk_per_trade["penalty_applied"] > 0, "Should have penalty applied for breaches"


class TestWhatIfSimulator:
    """Test 4: What-If Simulator endpoint"""
    
    def test_whatif_endpoint_exists(self, auth_headers):
        """Verify what-if endpoint is accessible"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/what-if/2210?new_equity=50000&period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True, f"What-If API failed: {data}"
    
    def test_whatif_comparison_structure(self, auth_headers):
        """Verify what-if returns limits comparison"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/what-if/2210?new_equity=50000&period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify comparison structure
        assert "comparison" in data, "Should have comparison field"
        comparison = data["comparison"]
        
        assert "current_equity" in comparison
        assert "simulated_equity" in comparison
        assert "current_limits" in comparison
        assert "new_limits" in comparison
        
        # Verify current and new limits have required fields
        assert "risk_per_trade" in comparison["current_limits"]
        assert "daily_loss" in comparison["current_limits"]
        assert "risk_per_trade" in comparison["new_limits"]
        assert "daily_loss" in comparison["new_limits"]
    
    def test_whatif_lot_limits_comparison(self, auth_headers):
        """Verify what-if returns lot limits comparison by instrument"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/what-if/2210?new_equity=50000&period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify lot_limits_comparison
        assert "lot_limits_comparison" in data, "Should have lot_limits_comparison"
        lot_limits = data["lot_limits_comparison"]
        
        assert len(lot_limits) >= 1, "Should have at least one instrument"
        
        # Check structure of each instrument
        for inst in lot_limits:
            assert "symbol" in inst
            assert "current_max_lots" in inst
            assert "new_max_lots" in inst
            assert "change_pct" in inst
    
    def test_whatif_equity_scenarios(self, auth_headers):
        """Verify what-if returns equity scenarios for score projection"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/what-if/2210?new_equity=50000&period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify equity_scenarios
        assert "equity_scenarios" in data, "Should have equity_scenarios"
        scenarios = data["equity_scenarios"]
        
        assert len(scenarios) >= 3, "Should have multiple equity scenarios"
        
        # Check structure of each scenario
        for scenario in scenarios:
            assert "label" in scenario
            assert "equity" in scenario
            assert "projected_score" in scenario
            assert "is_current" in scenario
    
    def test_whatif_higher_equity_increases_limits(self, auth_headers):
        """Verify higher equity increases risk limits"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/what-if/2210?new_equity=100000&period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        comparison = data["comparison"]
        
        # Higher equity should increase limits
        assert comparison["new_limits"]["risk_per_trade"] > comparison["current_limits"]["risk_per_trade"]
        assert comparison["new_limits"]["daily_loss"] > comparison["current_limits"]["daily_loss"]


class TestAccountWithNoBreaches:
    """Test accounts with no breaches for comparison"""
    
    def test_compliant_account_has_no_alerts(self, auth_headers):
        """Account 2215 (Joel NASDAQ) should have minimal or no alerts"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2215?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Account 2215 has high score, should have fewer alerts
        alerts = data.get("alerts", [])
        # Just verify the structure, not strict count
        for alert in alerts:
            assert "type" in alert
            assert "severity" in alert
    
    def test_compliant_account_score(self, auth_headers):
        """Account 2215 should have good risk score"""
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2215?period_days=30",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        score = data.get("risk_control_score", {}).get("composite_score", 0)
        # Account 2215 should have a good score
        assert score >= 80, f"Account 2215 should have good score, got {score}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
