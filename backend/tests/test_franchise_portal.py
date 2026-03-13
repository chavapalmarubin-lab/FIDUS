"""
Test Suite for FIDUS Franchise Portal - Phase 2
Tests franchise authentication, dashboard APIs, and multi-tenant filtering.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test Credentials
FRANCHISE_ADMIN_EMAIL = "admin@testco.com"
FRANCHISE_ADMIN_PASSWORD = "FranchiseTest123"
EXPECTED_COMPANY_NAME = "Test Franchise Co"


class TestFranchiseAuthEndpoints:
    """Tests for franchise authentication API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_franchise_login_endpoint_exists(self):
        """Test that the franchise login endpoint exists"""
        response = self.session.post(f"{BASE_URL}/api/franchise/auth/login", json={})
        # Should return 422 (validation error) or 401, not 404
        assert response.status_code != 404, "Franchise login endpoint not found"
        print(f"Login endpoint exists, status: {response.status_code}")
    
    def test_franchise_login_missing_credentials(self):
        """Test login with missing credentials returns validation error"""
        response = self.session.post(f"{BASE_URL}/api/franchise/auth/login", json={
            "email": "",
            "password": ""
        })
        # Should return 422 or 401, not 500
        assert response.status_code in [401, 422], f"Unexpected status: {response.status_code}"
        print(f"Missing credentials returns: {response.status_code}")
    
    def test_franchise_login_invalid_credentials(self):
        """Test login with wrong credentials returns 401"""
        response = self.session.post(f"{BASE_URL}/api/franchise/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Invalid credentials correctly returns 401")
    
    def test_franchise_login_success(self):
        """Test successful franchise admin login"""
        response = self.session.post(f"{BASE_URL}/api/franchise/auth/login", json={
            "email": FRANCHISE_ADMIN_EMAIL,
            "password": FRANCHISE_ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Validate response structure
        assert data.get("success") == True, "Login should return success: true"
        assert "token" in data, "Response should include token"
        assert "admin" in data, "Response should include admin data"
        assert "company" in data, "Response should include company data"
        
        # Validate admin data
        admin = data["admin"]
        assert admin.get("email") == FRANCHISE_ADMIN_EMAIL, "Admin email should match"
        assert "first_name" in admin, "Admin should have first_name"
        assert "last_name" in admin, "Admin should have last_name"
        
        # Validate company data
        company = data["company"]
        assert company.get("company_name") == EXPECTED_COMPANY_NAME, f"Company name should be '{EXPECTED_COMPANY_NAME}'"
        assert "company_id" in company, "Company should have company_id"
        assert "company_code" in company, "Company should have company_code"
        
        print(f"Login successful for {admin['email']} at {company['company_name']}")
    
    def test_franchise_token_verification(self):
        """Test token verification endpoint"""
        # First login to get token
        login_response = self.session.post(f"{BASE_URL}/api/franchise/auth/login", json={
            "email": FRANCHISE_ADMIN_EMAIL,
            "password": FRANCHISE_ADMIN_PASSWORD
        })
        
        assert login_response.status_code == 200, "Login failed"
        token = login_response.json().get("token")
        assert token, "No token received from login"
        
        # Verify token
        verify_response = self.session.get(f"{BASE_URL}/api/franchise/auth/verify", params={"token": token})
        
        assert verify_response.status_code == 200, f"Token verification failed: {verify_response.status_code}"
        data = verify_response.json()
        
        assert data.get("success") == True, "Verification should return success"
        assert data.get("valid") == True, "Token should be valid"
        assert "admin" in data, "Verification should return admin data"
        assert "company" in data, "Verification should return company data"
        
        print("Token verification successful")
    
    def test_franchise_token_verification_invalid_token(self):
        """Test token verification with invalid token"""
        verify_response = self.session.get(f"{BASE_URL}/api/franchise/auth/verify", params={"token": "invalid-token"})
        
        assert verify_response.status_code == 401, f"Expected 401, got {verify_response.status_code}"
        print("Invalid token correctly rejected")


class TestFranchiseDashboardEndpoints:
    """Tests for franchise dashboard API endpoints (require authentication)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login and get token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/franchise/auth/login", json={
            "email": FRANCHISE_ADMIN_EMAIL,
            "password": FRANCHISE_ADMIN_PASSWORD
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.company = login_response.json().get("company", {})
        else:
            pytest.skip("Could not login - skipping dashboard tests")
    
    def test_dashboard_overview_endpoint(self):
        """Test dashboard overview endpoint"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/overview")
        
        assert response.status_code == 200, f"Overview failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Overview should return success"
        assert "overview" in data, "Should return overview data"
        
        overview = data["overview"]
        assert "company" in overview, "Overview should include company info"
        assert "stats" in overview, "Overview should include stats"
        assert "monthly_projections" in overview, "Overview should include projections"
        
        # Validate stats structure
        stats = overview["stats"]
        assert "total_clients" in stats, "Stats should include total_clients"
        assert "total_agents" in stats, "Stats should include total_agents"
        assert "total_aum" in stats, "Stats should include total_aum"
        
        print(f"Overview: {stats['total_clients']} clients, {stats['total_agents']} agents, ${stats['total_aum']} AUM")
    
    def test_dashboard_portfolio_endpoint(self):
        """Test fund portfolio endpoint"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/portfolio")
        
        assert response.status_code == 200, f"Portfolio failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Portfolio should return success"
        assert "portfolio" in data, "Should return portfolio data"
        
        portfolio = data["portfolio"]
        assert "fund_type" in portfolio, "Portfolio should include fund_type"
        assert portfolio["fund_type"] == "BALANCE", "Fund type should be BALANCE"
        assert "total_aum" in portfolio, "Portfolio should include total_aum"
        assert "returns" in portfolio, "Portfolio should include returns breakdown"
        
        # Validate returns structure
        returns = portfolio["returns"]
        assert returns.get("gross_return_pct") == 2.5, "Gross return should be 2.5%"
        assert returns.get("client_return_pct") == 2.0, "Client return should be 2.0%"
        assert returns.get("commission_pool_pct") == 0.5, "Commission pool should be 0.5%"
        
        print(f"Portfolio: Fund type {portfolio['fund_type']}, AUM ${portfolio['total_aum']}")
    
    def test_dashboard_cashflow_endpoint(self):
        """Test cash flow endpoint"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/cashflow")
        
        assert response.status_code == 200, f"Cashflow failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Cashflow should return success"
        assert "cashflow" in data, "Should return cashflow data"
        
        cashflow = data["cashflow"]
        assert "summary" in cashflow, "Cashflow should include summary"
        assert "monthly_projection" in cashflow, "Cashflow should include monthly_projection"
        
        print(f"Cashflow: {cashflow.get('investment_count', 0)} investments")
    
    def test_dashboard_clients_endpoint(self):
        """Test clients list endpoint"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/clients")
        
        assert response.status_code == 200, f"Clients failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Clients should return success"
        assert "clients" in data, "Should return clients list"
        assert "summary" in data, "Should return clients summary"
        assert isinstance(data["clients"], list), "Clients should be a list"
        
        summary = data["summary"]
        assert "total_clients" in summary, "Summary should include total_clients"
        
        print(f"Clients: {summary['total_clients']} total clients")
    
    def test_dashboard_agents_endpoint(self):
        """Test referral agents list endpoint"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/agents")
        
        assert response.status_code == 200, f"Agents failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Agents should return success"
        assert "agents" in data, "Should return agents list"
        assert isinstance(data["agents"], list), "Agents should be a list"
        
        print(f"Agents: {len(data['agents'])} referral agents")
    
    def test_dashboard_commissions_endpoint(self):
        """Test commissions endpoint"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/commissions")
        
        assert response.status_code == 200, f"Commissions failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Commissions should return success"
        assert "commissions" in data, "Should return commissions data"
        
        commissions = data["commissions"]
        assert "split" in commissions, "Commissions should include split"
        assert "totals" in commissions, "Commissions should include totals"
        
        # Validate commission split structure
        split = commissions["split"]
        assert "company" in split, "Split should include company percentage"
        assert "agent" in split, "Split should include agent percentage"
        
        print(f"Commission split: {split['company']}% company / {split['agent']}% agent")
    
    def test_dashboard_instruments_endpoint(self):
        """Test instruments specifications endpoint"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/instruments")
        
        assert response.status_code == 200, f"Instruments failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Instruments should return success"
        assert "instruments" in data, "Should return instruments list"
        assert isinstance(data["instruments"], list), "Instruments should be a list"
        
        # Should have multiple instruments
        assert len(data["instruments"]) > 0, "Should have at least some instruments"
        
        # Validate instrument structure (if any exist)
        if data["instruments"]:
            inst = data["instruments"][0]
            assert "symbol" in inst, "Instrument should have symbol"
            # Note: API returns "description" for instrument name
            assert "description" in inst or "name" in inst, "Instrument should have description or name"
        
        print(f"Instruments: {len(data['instruments'])} instrument specifications")
    
    def test_dashboard_risk_policy_endpoint(self):
        """Test risk policy endpoint"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/risk-policy")
        
        assert response.status_code == 200, f"Risk policy failed: {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Risk policy should return success"
        assert "policy" in data, "Should return policy data"
        
        policy = data["policy"]
        
        # Validate expected risk parameters
        assert policy.get("max_risk_per_trade_pct") == 1.0, "Max risk per trade should be 1%"
        assert policy.get("max_intraday_loss_pct") == 3.0, "Max intraday loss should be 3%"
        assert policy.get("max_weekly_loss_pct") == 6.0, "Max weekly loss should be 6%"
        assert policy.get("max_monthly_dd_pct") == 10.0, "Max monthly drawdown should be 10%"
        assert policy.get("max_margin_usage_pct") == 25.0, "Max margin usage should be 25%"
        assert policy.get("leverage") == 200, "Leverage should be 200:1"
        
        print(f"Risk Policy: {policy['leverage']}:1 leverage, {policy['max_risk_per_trade_pct']}% max risk per trade")
    
    def test_dashboard_endpoints_require_auth(self):
        """Test that dashboard endpoints require authentication"""
        # Create new session without auth token
        unauthenticated_session = requests.Session()
        unauthenticated_session.headers.update({"Content-Type": "application/json"})
        
        endpoints = [
            "/api/franchise/dashboard/overview",
            "/api/franchise/dashboard/portfolio",
            "/api/franchise/dashboard/cashflow",
            "/api/franchise/dashboard/clients",
            "/api/franchise/dashboard/agents",
            "/api/franchise/dashboard/commissions",
            "/api/franchise/dashboard/instruments",
            "/api/franchise/dashboard/risk-policy"
        ]
        
        for endpoint in endpoints:
            response = unauthenticated_session.get(f"{BASE_URL}{endpoint}")
            assert response.status_code in [401, 403, 422], f"{endpoint} should require auth, got {response.status_code}"
        
        print("All dashboard endpoints correctly require authentication")


class TestFranchiseMultiTenantFiltering:
    """Tests for multi-tenant data filtering by company_id"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login and get token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/franchise/auth/login", json={
            "email": FRANCHISE_ADMIN_EMAIL,
            "password": FRANCHISE_ADMIN_PASSWORD
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self.company = login_response.json().get("company", {})
        else:
            pytest.skip("Could not login - skipping multi-tenant tests")
    
    def test_overview_returns_company_specific_data(self):
        """Test that overview returns data specific to the logged-in company"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        # Company info should match logged-in company
        overview = data.get("overview", {})
        company_info = overview.get("company", {})
        
        assert company_info.get("name") == EXPECTED_COMPANY_NAME, "Overview should show correct company name"
        
        print(f"Multi-tenant: Overview correctly shows data for '{company_info.get('name')}'")
    
    def test_portfolio_filtered_by_company(self):
        """Test that portfolio data is filtered by company_id"""
        response = self.session.get(f"{BASE_URL}/api/franchise/dashboard/portfolio")
        
        assert response.status_code == 200
        data = response.json()
        
        portfolio = data.get("portfolio", {})
        assert portfolio.get("company_name") == EXPECTED_COMPANY_NAME, "Portfolio should show correct company"
        
        print(f"Multi-tenant: Portfolio correctly filtered for '{portfolio.get('company_name')}'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
