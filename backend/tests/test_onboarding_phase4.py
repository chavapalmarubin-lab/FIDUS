"""
Test: Franchise Portal Phase 4 - Self-Service Onboarding
Tests: Add Client modal, Add Agent modal, CSV download, credential generation
Date: Jan 2026
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@testco.com"
ADMIN_PASSWORD = "FranchiseTest123"
COMPANY_ID = "e27bc269-d123-4e78-b4c4-d43c5dd80183"

# Existing agent for client onboarding
EXISTING_AGENT_ID = "b74e1fc0-902f-4bf5-8b88-d0da03c37161"  # Carlos Lopez

# Generate unique emails for each test run
TEST_RUN_ID = str(int(time.time()))[-6:]


@pytest.fixture(scope="module")
def admin_token():
    """Get franchise admin auth token"""
    response = requests.post(
        f"{BASE_URL}/api/franchise/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    assert data.get("success"), "Login response missing success flag"
    assert "token" in data, "Login response missing token"
    return data["token"]


@pytest.fixture
def auth_headers(admin_token):
    """Get authorization headers with token"""
    return {"Authorization": f"Bearer {admin_token}"}


# =============================================================================
# TEST: Get Agents for Dropdown
# =============================================================================

class TestAgentsDropdown:
    """Verify agents endpoint returns data for dropdown"""
    
    def test_get_agents_list(self, auth_headers):
        """GET /api/franchise/dashboard/agents - should return agents for dropdown"""
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/agents",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get agents: {response.text}"
        data = response.json()
        assert data.get("success"), "Response missing success flag"
        assert "agents" in data, "Response missing agents list"
        
        # Verify Carlos Lopez is in the list
        agents = data["agents"]
        assert len(agents) >= 1, "Expected at least 1 agent (Carlos Lopez)"
        
        # Find Carlos Lopez
        carlos = next((a for a in agents if a.get("agent_id") == EXISTING_AGENT_ID), None)
        assert carlos is not None, "Carlos Lopez (existing agent) not found"
        assert carlos.get("first_name") == "Carlos", f"Expected first_name 'Carlos', got {carlos.get('first_name')}"
        print(f"PASS: Found {len(agents)} agents, including Carlos Lopez")


# =============================================================================
# TEST: Onboard Client (Add Client Modal)
# =============================================================================

class TestOnboardClient:
    """Test POST /api/franchise/dashboard/onboard-client"""
    
    def test_onboard_client_success(self, auth_headers):
        """Create a new client with investment and credentials"""
        unique_email = f"test_client_{TEST_RUN_ID}@example.com"
        
        payload = {
            "first_name": "Test",
            "last_name": "Client",
            "email": unique_email,
            "phone": "+1234567890",
            "country": "USA",
            "investment_amount": 100000,
            "referral_agent_id": EXISTING_AGENT_ID
        }
        
        response = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-client",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Client onboarding failed: {response.text}"
        data = response.json()
        
        # Verify success
        assert data.get("success"), f"Response not successful: {data}"
        assert "client_id" in data, "Response missing client_id"
        
        # Verify credentials returned
        assert "credentials" in data, "Response missing credentials"
        creds = data["credentials"]
        assert creds.get("email") == unique_email.lower(), f"Email mismatch"
        assert creds.get("temp_password") == "Fidus2026!", f"Expected temp_password 'Fidus2026!', got {creds.get('temp_password')}"
        assert "/franchise/client/login" in creds.get("login_url", ""), "Login URL missing or incorrect"
        
        print(f"PASS: Client onboarded successfully with credentials: {creds}")
        return data["client_id"], unique_email
    
    def test_onboard_client_missing_fields(self, auth_headers):
        """Empty/missing required fields should fail validation"""
        payload = {
            "first_name": "",
            "last_name": "",
            "email": "",
            "investment_amount": 0,
            "referral_agent_id": ""
        }
        
        response = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-client",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail - either 400/422 validation error
        # Note: Pydantic will reject empty strings for required fields
        assert response.status_code in [400, 422, 500], f"Expected validation error, got {response.status_code}"
        print(f"PASS: Empty fields rejected with status {response.status_code}")
    
    def test_onboard_client_duplicate_email(self, auth_headers):
        """Duplicate email should fail"""
        unique_email = f"test_dup_{TEST_RUN_ID}@example.com"
        
        payload = {
            "first_name": "Dup",
            "last_name": "Client",
            "email": unique_email,
            "phone": "",
            "country": "",
            "investment_amount": 50000,
            "referral_agent_id": EXISTING_AGENT_ID
        }
        
        # First create should succeed
        response1 = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-client",
            json=payload,
            headers=auth_headers
        )
        assert response1.status_code == 200, f"First client creation failed: {response1.text}"
        
        # Second create with same email should fail
        response2 = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-client",
            json=payload,
            headers=auth_headers
        )
        assert response2.status_code == 400, f"Expected 400 for duplicate email, got {response2.status_code}"
        
        data2 = response2.json()
        assert "already exists" in data2.get("detail", "").lower(), f"Expected 'already exists' error, got: {data2}"
        print(f"PASS: Duplicate email rejected correctly")
    
    def test_onboard_client_invalid_agent(self, auth_headers):
        """Invalid referral agent ID should fail"""
        payload = {
            "first_name": "Invalid",
            "last_name": "Agent",
            "email": f"test_invalid_agent_{TEST_RUN_ID}@example.com",
            "phone": "",
            "country": "",
            "investment_amount": 50000,
            "referral_agent_id": "nonexistent-agent-id"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-client",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid agent, got {response.status_code}"
        data = response.json()
        assert "not found" in data.get("detail", "").lower(), f"Expected 'not found' error, got: {data}"
        print("PASS: Invalid agent ID rejected correctly")


# =============================================================================
# TEST: Onboard Agent (Add Agent Modal)
# =============================================================================

class TestOnboardAgent:
    """Test POST /api/franchise/dashboard/onboard-agent"""
    
    def test_onboard_agent_success(self, auth_headers):
        """Create a new referral agent with credentials"""
        unique_email = f"test_agent_{TEST_RUN_ID}@example.com"
        
        payload = {
            "first_name": "Test",
            "last_name": "Agent",
            "email": unique_email,
            "phone": "+9876543210",
            "commission_tier": 40
        }
        
        response = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-agent",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Agent onboarding failed: {response.text}"
        data = response.json()
        
        # Verify success
        assert data.get("success"), f"Response not successful: {data}"
        assert "agent_id" in data, "Response missing agent_id"
        
        # Verify credentials returned
        assert "credentials" in data, "Response missing credentials"
        creds = data["credentials"]
        assert creds.get("email") == unique_email.lower(), f"Email mismatch"
        assert creds.get("temp_password") == "Fidus2026!", f"Expected temp_password 'Fidus2026!', got {creds.get('temp_password')}"
        assert "/franchise/agent/login" in creds.get("login_url", ""), "Login URL missing or incorrect"
        
        print(f"PASS: Agent onboarded successfully with credentials: {creds}")
        return data["agent_id"], unique_email
    
    def test_onboard_agent_duplicate_email(self, auth_headers):
        """Duplicate email should fail"""
        unique_email = f"test_dup_agent_{TEST_RUN_ID}@example.com"
        
        payload = {
            "first_name": "Dup",
            "last_name": "Agent",
            "email": unique_email,
            "phone": "",
            "commission_tier": 50
        }
        
        # First create should succeed
        response1 = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-agent",
            json=payload,
            headers=auth_headers
        )
        assert response1.status_code == 200, f"First agent creation failed: {response1.text}"
        
        # Second create with same email should fail
        response2 = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-agent",
            json=payload,
            headers=auth_headers
        )
        assert response2.status_code == 400, f"Expected 400 for duplicate email, got {response2.status_code}"
        
        data2 = response2.json()
        assert "already exists" in data2.get("detail", "").lower(), f"Expected 'already exists' error, got: {data2}"
        print("PASS: Duplicate agent email rejected correctly")
    
    def test_onboard_agent_commission_tiers(self, auth_headers):
        """Test different commission tiers"""
        for tier in [30, 40, 50]:
            unique_email = f"test_tier{tier}_{TEST_RUN_ID}@example.com"
            
            payload = {
                "first_name": f"Tier{tier}",
                "last_name": "Agent",
                "email": unique_email,
                "phone": "",
                "commission_tier": tier
            }
            
            response = requests.post(
                f"{BASE_URL}/api/franchise/dashboard/onboard-agent",
                json=payload,
                headers=auth_headers
            )
            
            assert response.status_code == 200, f"Agent with tier {tier} failed: {response.text}"
            print(f"PASS: Agent with tier {tier}% created successfully")


# =============================================================================
# TEST: Created Client Can Login
# =============================================================================

class TestCreatedClientLogin:
    """Test that newly created client can login with Fidus2026!"""
    
    def test_created_client_can_login(self, auth_headers):
        """Create client and verify login works"""
        unique_email = f"test_login_client_{TEST_RUN_ID}@example.com"
        
        # Create the client
        payload = {
            "first_name": "Login",
            "last_name": "TestClient",
            "email": unique_email,
            "phone": "",
            "country": "",
            "investment_amount": 75000,
            "referral_agent_id": EXISTING_AGENT_ID
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-client",
            json=payload,
            headers=auth_headers
        )
        assert create_response.status_code == 200, f"Client creation failed: {create_response.text}"
        
        # Now try to login as the client
        login_response = requests.post(
            f"{BASE_URL}/api/franchise/auth/client/login",
            json={"email": unique_email, "password": "Fidus2026!"}
        )
        
        assert login_response.status_code == 200, f"Client login failed: {login_response.text}"
        login_data = login_response.json()
        assert login_data.get("success"), f"Login not successful: {login_data}"
        assert "token" in login_data, "Login response missing token"
        assert login_data.get("client", {}).get("first_name") == "Login", "Client name mismatch"
        
        print(f"PASS: Created client can login with Fidus2026! password")


# =============================================================================
# TEST: Created Agent Can Login
# =============================================================================

class TestCreatedAgentLogin:
    """Test that newly created agent can login with Fidus2026!"""
    
    def test_created_agent_can_login(self, auth_headers):
        """Create agent and verify login works"""
        unique_email = f"test_login_agent_{TEST_RUN_ID}@example.com"
        
        # Create the agent
        payload = {
            "first_name": "Login",
            "last_name": "TestAgent",
            "email": unique_email,
            "phone": "",
            "commission_tier": 50
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/franchise/dashboard/onboard-agent",
            json=payload,
            headers=auth_headers
        )
        assert create_response.status_code == 200, f"Agent creation failed: {create_response.text}"
        
        # Now try to login as the agent
        login_response = requests.post(
            f"{BASE_URL}/api/franchise/auth/agent/login",
            json={"email": unique_email, "password": "Fidus2026!"}
        )
        
        assert login_response.status_code == 200, f"Agent login failed: {login_response.text}"
        login_data = login_response.json()
        assert login_data.get("success"), f"Login not successful: {login_data}"
        assert "token" in login_data, "Login response missing token"
        assert login_data.get("agent", {}).get("first_name") == "Login", "Agent name mismatch"
        
        print(f"PASS: Created agent can login with Fidus2026! password")


# =============================================================================
# TEST: Dashboard Data Endpoints (for CSV download data)
# =============================================================================

class TestCSVDataEndpoints:
    """Verify endpoints return data needed for CSV download"""
    
    def test_clients_endpoint_for_csv(self, auth_headers):
        """GET /api/franchise/dashboard/clients returns data for CSV"""
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/clients",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Clients endpoint failed: {response.text}"
        data = response.json()
        assert data.get("success"), "Response not successful"
        assert "clients" in data, "Missing clients array"
        print(f"PASS: Clients endpoint returns {len(data['clients'])} clients for CSV")
    
    def test_agents_endpoint_for_csv(self, auth_headers):
        """GET /api/franchise/dashboard/agents returns data for CSV"""
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/agents",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Agents endpoint failed: {response.text}"
        data = response.json()
        assert data.get("success"), "Response not successful"
        assert "agents" in data, "Missing agents array"
        print(f"PASS: Agents endpoint returns {len(data['agents'])} agents for CSV")
    
    def test_commissions_endpoint_for_csv(self, auth_headers):
        """GET /api/franchise/dashboard/commissions returns data for CSV"""
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/commissions",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Commissions endpoint failed: {response.text}"
        data = response.json()
        assert data.get("success"), "Response not successful"
        assert "commissions" in data, "Missing commissions object"
        print("PASS: Commissions endpoint returns data for CSV")
    
    def test_instruments_endpoint_for_csv(self, auth_headers):
        """GET /api/franchise/dashboard/instruments returns data for CSV"""
        response = requests.get(
            f"{BASE_URL}/api/franchise/dashboard/instruments",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Instruments endpoint failed: {response.text}"
        data = response.json()
        assert data.get("success"), "Response not successful"
        assert "instruments" in data, "Missing instruments array"
        print(f"PASS: Instruments endpoint returns {len(data['instruments'])} instruments for CSV")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
