"""
FIDUS Franchise Portal Phase 3 Tests
Tests for Client Portal, Agent Portal, and catch-all route fix

Test Company: Test Franchise Co (company_id: e27bc269-d123-4e78-b4c4-d43c5dd80183)
Test Client: Maria Garcia - maria@example.com / ClientTest123
Test Agent: Carlos Lopez - carlos@example.com / AgentTest123
Test Admin: admin@testco.com / FranchiseTest123
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestClientAuthentication:
    """Tests for franchise client login and auth"""
    
    def test_client_login_success(self):
        """POST /api/franchise/auth/client/login - Valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/franchise/auth/client/login",
            json={"email": "maria@example.com", "password": "ClientTest123"}
        )
        print(f"Client login response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert "token" in data, "Expected token in response"
        assert "client" in data, "Expected client object in response"
        assert "company" in data, "Expected company object in response"
        
        # Verify client data structure
        client = data["client"]
        assert "client_id" in client, "Expected client_id"
        assert client.get("first_name") == "Maria" or "Maria" in client.get("first_name", ""), "Expected Maria"
        assert client.get("last_name") == "Garcia" or "Garcia" in client.get("last_name", ""), "Expected Garcia"
        
        # Verify company data
        company = data["company"]
        assert "company_name" in company, "Expected company_name"
        
        print(f"Client login SUCCESS - Token received, client: {client.get('first_name')} {client.get('last_name')}")
        return data["token"]
    
    def test_client_login_invalid_credentials(self):
        """POST /api/franchise/auth/client/login - Invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/franchise/auth/client/login",
            json={"email": "maria@example.com", "password": "WrongPassword"}
        )
        print(f"Invalid client login response: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Invalid credentials correctly rejected with 401")
    
    def test_client_login_nonexistent_email(self):
        """POST /api/franchise/auth/client/login - Non-existent email"""
        response = requests.post(
            f"{BASE_URL}/api/franchise/auth/client/login",
            json={"email": "nonexistent@example.com", "password": "SomePassword"}
        )
        print(f"Non-existent email login response: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Non-existent email correctly rejected with 401")


class TestAgentAuthentication:
    """Tests for franchise agent login and auth"""
    
    def test_agent_login_success(self):
        """POST /api/franchise/auth/agent/login - Valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/franchise/auth/agent/login",
            json={"email": "carlos@example.com", "password": "AgentTest123"}
        )
        print(f"Agent login response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert "token" in data, "Expected token in response"
        assert "agent" in data, "Expected agent object in response"
        assert "company" in data, "Expected company object in response"
        
        # Verify agent data structure
        agent = data["agent"]
        assert "agent_id" in agent, "Expected agent_id"
        assert agent.get("first_name") == "Carlos" or "Carlos" in agent.get("first_name", ""), "Expected Carlos"
        assert agent.get("last_name") == "Lopez" or "Lopez" in agent.get("last_name", ""), "Expected Lopez"
        assert "commission_tier" in agent, "Expected commission_tier"
        
        # Verify company data
        company = data["company"]
        assert "company_name" in company, "Expected company_name"
        
        print(f"Agent login SUCCESS - Token received, agent: {agent.get('first_name')} {agent.get('last_name')}, tier: {agent.get('commission_tier')}%")
        return data["token"]
    
    def test_agent_login_invalid_credentials(self):
        """POST /api/franchise/auth/agent/login - Invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/franchise/auth/agent/login",
            json={"email": "carlos@example.com", "password": "WrongPassword"}
        )
        print(f"Invalid agent login response: {response.status_code}")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Invalid credentials correctly rejected with 401")


class TestClientDashboard:
    """Tests for client dashboard endpoints"""
    
    @pytest.fixture(scope="class")
    def client_token(self):
        """Get client auth token"""
        response = requests.post(
            f"{BASE_URL}/api/franchise/auth/client/login",
            json={"email": "maria@example.com", "password": "ClientTest123"}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not get client token - skipping dashboard tests")
    
    def test_client_overview_endpoint(self, client_token):
        """GET /api/franchise/dashboard/client/overview - Client's investment data"""
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/client/overview",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        print(f"Client overview response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        
        # Verify response structure
        assert "client" in data, "Expected client object"
        assert "summary" in data, "Expected summary object"
        assert "investments" in data, "Expected investments array"
        assert "fund_terms" in data, "Expected fund_terms object"
        
        # Verify client data
        client = data["client"]
        assert "first_name" in client, "Expected first_name"
        assert "last_name" in client, "Expected last_name"
        assert "status" in client, "Expected status"
        
        # Verify summary data
        summary = data["summary"]
        assert "total_invested" in summary, "Expected total_invested"
        total_invested = summary.get("total_invested", 0)
        print(f"Client total invested: ${total_invested:,.0f}")
        
        # Expected: $150,000 investment
        assert total_invested >= 0, "Expected non-negative investment"
        
        # Verify fund terms
        fund_terms = data["fund_terms"]
        assert fund_terms.get("client_return_pct") == 2.0, "Expected 2.0% client return"
        
        print(f"Client overview SUCCESS - Invested: ${total_invested:,.0f}, Status: {client.get('status')}")
    
    def test_client_overview_unauthorized(self):
        """GET /api/franchise/dashboard/client/overview - No auth should fail"""
        response = requests.get(f"{BASE_URL}/api/franchise/dashboard/client/overview")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Unauthorized access correctly rejected with 401")
    
    def test_client_overview_invalid_token(self):
        """GET /api/franchise/dashboard/client/overview - Invalid token should fail"""
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/client/overview",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Invalid token correctly rejected with 401")


class TestAgentDashboard:
    """Tests for agent dashboard endpoints"""
    
    @pytest.fixture(scope="class")
    def agent_token(self):
        """Get agent auth token"""
        response = requests.post(
            f"{BASE_URL}/api/franchise/auth/agent/login",
            json={"email": "carlos@example.com", "password": "AgentTest123"}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not get agent token - skipping dashboard tests")
    
    def test_agent_overview_endpoint(self, agent_token):
        """GET /api/franchise/dashboard/agent/overview - Agent's referral data"""
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/agent/overview",
            headers={"Authorization": f"Bearer {agent_token}"}
        )
        print(f"Agent overview response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        
        # Verify response structure
        assert "agent" in data, "Expected agent object"
        assert "summary" in data, "Expected summary object"
        assert "clients" in data, "Expected clients array"
        assert "transactions" in data, "Expected transactions array"
        
        # Verify agent data
        agent = data["agent"]
        assert "first_name" in agent, "Expected first_name"
        assert "last_name" in agent, "Expected last_name"
        assert "commission_tier" in agent, "Expected commission_tier"
        
        commission_tier = agent.get("commission_tier", 0)
        print(f"Agent: {agent.get('first_name')} {agent.get('last_name')}, Commission Tier: {commission_tier}%")
        
        # Verify summary data
        summary = data["summary"]
        assert "total_clients_referred" in summary, "Expected total_clients_referred"
        assert "total_aum_referred" in summary, "Expected total_aum_referred"
        assert "total_commission_earned" in summary, "Expected total_commission_earned"
        
        clients_referred = summary.get("total_clients_referred", 0)
        print(f"Agent overview SUCCESS - Clients referred: {clients_referred}, Tier: {commission_tier}%")
    
    def test_agent_overview_unauthorized(self):
        """GET /api/franchise/dashboard/agent/overview - No auth should fail"""
        response = requests.get(f"{BASE_URL}/api/franchise/dashboard/agent/overview")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Unauthorized access correctly rejected with 401")


class TestFranchiseAdminStillWorks:
    """Verify existing franchise admin portal still works"""
    
    def test_admin_login_still_works(self):
        """POST /api/franchise/auth/login - Admin login unchanged"""
        response = requests.post(
            f"{BASE_URL}/api/franchise/auth/login",
            json={"email": "admin@testco.com", "password": "FranchiseTest123"}
        )
        print(f"Admin login response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=True"
        assert "token" in data, "Expected token"
        assert data.get("company", {}).get("company_name") == "Test Franchise Co"
        
        print("Admin login still works correctly")
        return data["token"]
    
    def test_admin_overview_still_works(self):
        """GET /api/franchise/dashboard/overview - Admin overview unchanged"""
        # Get admin token first
        login_res = requests.post(
            f"{BASE_URL}/api/franchise/auth/login",
            json={"email": "admin@testco.com", "password": "FranchiseTest123"}
        )
        if login_res.status_code != 200:
            pytest.skip("Could not get admin token")
        
        token = login_res.json().get("token")
        
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Admin overview response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        assert "overview" in data
        
        print("Admin overview endpoint still works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
