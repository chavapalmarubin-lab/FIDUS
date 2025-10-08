#!/usr/bin/env python3
"""
URGENT DEBUG: Frontend Data Visibility Testing
Testing specific endpoints that frontend should be calling but user reports no data visible.

Focus Areas:
1. Admin Authentication 
2. Investment Admin Overview (dashboard totals)
3. Ready Clients (investment dropdown)
4. Client Investments (Alejandro's data)
5. MT5 Accounts (Alejandro's accounts)
6. Google Connection Status

Context: User reports no investments, MT5 accounts, or Google email functionality visible in frontend.
Need to verify these specific endpoints are returning correct data for frontend consumption.
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
import uuid

# Backend URL Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

# Test Users Available
TEST_USERS = {
    "admin": {
        "username": "admin", 
        "password": "password123",
        "user_type": "admin",
        "expected_name": "Investment Committee"
    },
    "alejandro_mariscal": {
        "username": "alejandro_mariscal",
        "password": "password123", 
        "user_type": "client",
        "expected_email": "alejandro.mariscal@email.com"
    },
    "client1": {
        "username": "client1",
        "password": "password123",
        "user_type": "client", 
        "expected_email": "g.b@fidus.com"
    }
}

class FidusBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request with proper error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Set up headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        if auth_token:
            req_headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_health_endpoints(self):
        """Test health check and readiness endpoints"""
        print("🔍 Testing Health Check Endpoints...")
        
        # Test basic health endpoint
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check Endpoint", True, 
                                f"Status: {data.get('status')}, Service: {data.get('service', 'N/A')}")
                else:
                    self.log_test("Health Check Endpoint", False, 
                                f"Unexpected status: {data.get('status')}")
            except json.JSONDecodeError:
                self.log_test("Health Check Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Health Check Endpoint", False, f"HTTP {status_code}")

        # Test readiness endpoint
        response = self.make_request("GET", "/health/ready")
        if response and response.status_code == 200:
            self.log_test("Readiness Check Endpoint", True, "System ready for requests")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Readiness Check Endpoint", False, f"HTTP {status_code}")

        # Test health metrics endpoint
        response = self.make_request("GET", "/health/metrics")
        if response and response.status_code == 200:
            self.log_test("Health Metrics Endpoint", True, "Metrics endpoint accessible")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Health Metrics Endpoint", False, f"HTTP {status_code}")

    def test_user_authentication(self):
        """Test user authentication and JWT token management"""
        print("🔍 Testing User Authentication & JWT Management...")
        
        # Test admin login
        admin_data = TEST_USERS["admin"]
        login_payload = {
            "username": admin_data["username"],
            "password": admin_data["password"], 
            "user_type": admin_data["user_type"]
        }
        
        response = self.make_request("POST", "/auth/login", login_payload)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token") and data.get("type") == "admin":
                    self.admin_token = data["token"]
                    self.log_test("Admin Authentication", True, 
                                f"Admin: {data.get('name')}, Type: {data.get('type')}")
                else:
                    self.log_test("Admin Authentication", False, "Missing token or incorrect type")
            except json.JSONDecodeError:
                self.log_test("Admin Authentication", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Admin Authentication", False, f"HTTP {status_code}")

        # Test client login (alejandro_mariscal)
        client_data = TEST_USERS["alejandro_mariscal"]
        login_payload = {
            "username": client_data["username"],
            "password": client_data["password"],
            "user_type": client_data["user_type"]
        }
        
        response = self.make_request("POST", "/auth/login", login_payload)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token") and data.get("type") == "client":
                    self.client_token = data["token"]
                    self.log_test("Client Authentication (Alejandro)", True,
                                f"Client: {data.get('name')}, Email: {data.get('email')}")
                else:
                    self.log_test("Client Authentication (Alejandro)", False, 
                                "Missing token or incorrect type")
            except json.JSONDecodeError:
                self.log_test("Client Authentication (Alejandro)", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Client Authentication (Alejandro)", False, f"HTTP {status_code}")

        # Test JWT token refresh
        if self.admin_token:
            response = self.make_request("POST", "/auth/refresh-token", 
                                       auth_token=self.admin_token)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success") and data.get("token"):
                        self.log_test("JWT Token Refresh", True, "Token refreshed successfully")
                    else:
                        self.log_test("JWT Token Refresh", False, "Invalid refresh response")
                except json.JSONDecodeError:
                    self.log_test("JWT Token Refresh", False, "Invalid JSON response")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test("JWT Token Refresh", False, f"HTTP {status_code}")

    def test_user_management(self):
        """Test user management endpoints"""
        print("🔍 Testing User Management System...")
        
        if not self.admin_token:
            self.log_test("User Management", False, "No admin token available")
            return

        # Test get all users (admin endpoint)
        response = self.make_request("GET", "/admin/users", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                users = data.get("users", [])
                if len(users) >= 7:  # Expected 7 users including alejandro_mariscal
                    alejandro_found = any(u.get("username") == "alejandro_mariscal" for u in users)
                    if alejandro_found:
                        self.log_test("User Management - Get All Users", True,
                                    f"Found {len(users)} users including alejandro_mariscal")
                    else:
                        self.log_test("User Management - Get All Users", False,
                                    "alejandro_mariscal not found in users list")
                else:
                    self.log_test("User Management - Get All Users", False,
                                f"Expected ≥7 users, found {len(users)}")
            except json.JSONDecodeError:
                self.log_test("User Management - Get All Users", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("User Management - Get All Users", False, f"HTTP {status_code}")

        # Test get all clients
        response = self.make_request("GET", "/admin/clients", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                clients = data.get("clients", [])
                if len(clients) > 0:
                    self.log_test("User Management - Get All Clients", True,
                                f"Found {len(clients)} clients")
                else:
                    self.log_test("User Management - Get All Clients", False, "No clients found")
            except json.JSONDecodeError:
                self.log_test("User Management - Get All Clients", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("User Management - Get All Clients", False, f"HTTP {status_code}")

        # Test user creation
        test_user_data = {
            "username": f"test_user_{int(time.time())}",
            "name": "Test User Phase2",
            "email": f"test.phase2.{int(time.time())}@fidus.com",
            "phone": "+1-555-TEST",
            "temporary_password": "TempPass123!",
            "notes": "Created during Phase 2 backend testing"
        }
        
        response = self.make_request("POST", "/admin/users/create", test_user_data, 
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success") and data.get("user_id"):
                    self.log_test("User Management - Create User", True,
                                f"Created user: {data.get('user_id')}")
                else:
                    self.log_test("User Management - Create User", False, 
                                "Missing success flag or user_id")
            except json.JSONDecodeError:
                self.log_test("User Management - Create User", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("User Management - Create User", False, f"HTTP {status_code}")

    def test_investment_management(self):
        """Test investment management endpoints"""
        print("🔍 Testing Investment Management System...")
        
        if not self.admin_token:
            self.log_test("Investment Management", False, "No admin token available")
            return

        # Test get client investments (should be clean slate - 0 investments)
        response = self.make_request("GET", "/admin/investments", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                investments = data.get("investments", [])
                self.log_test("Investment Management - Get All Investments", True,
                            f"Found {len(investments)} investments (clean slate expected)")
            except json.JSONDecodeError:
                self.log_test("Investment Management - Get All Investments", False, 
                            "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Investment Management - Get All Investments", False, f"HTTP {status_code}")

        # Test investment creation (using alejandro_mariscal as test client)
        if self.client_token:
            investment_data = {
                "client_id": "client_alejandro",  # Alejandro's client ID
                "fund_code": "CORE",
                "amount": 10000.0,
                "deposit_date": "2025-01-01"
            }
            
            response = self.make_request("POST", "/investments/create", investment_data,
                                       auth_token=self.admin_token)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success") and data.get("investment_id"):
                        self.log_test("Investment Management - Create Investment", True,
                                    f"Created investment: {data.get('investment_id')}")
                    else:
                        self.log_test("Investment Management - Create Investment", False,
                                    "Missing success flag or investment_id")
                except json.JSONDecodeError:
                    self.log_test("Investment Management - Create Investment", False, 
                                "Invalid JSON response")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test("Investment Management - Create Investment", False, f"HTTP {status_code}")

        # Test fund configurations
        response = self.make_request("GET", "/investments/fund-configs", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                funds = data.get("funds", {})
                expected_funds = ["CORE", "BALANCE", "DYNAMIC", "UNLIMITED"]
                found_funds = [fund for fund in expected_funds if fund in funds]
                if len(found_funds) == len(expected_funds):
                    self.log_test("Investment Management - Fund Configurations", True,
                                f"All {len(found_funds)} fund configs available")
                else:
                    self.log_test("Investment Management - Fund Configurations", False,
                                f"Expected {len(expected_funds)} funds, found {len(found_funds)}")
            except json.JSONDecodeError:
                self.log_test("Investment Management - Fund Configurations", False, 
                            "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Investment Management - Fund Configurations", False, f"HTTP {status_code}")

    def test_crm_system(self):
        """Test CRM pipeline system"""
        print("🔍 Testing CRM Pipeline System...")
        
        if not self.admin_token:
            self.log_test("CRM System", False, "No admin token available")
            return

        # Test get all prospects
        response = self.make_request("GET", "/crm/prospects", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                prospects = data.get("prospects", [])
                self.log_test("CRM System - Get All Prospects", True,
                            f"Found {len(prospects)} prospects")
            except json.JSONDecodeError:
                self.log_test("CRM System - Get All Prospects", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("CRM System - Get All Prospects", False, f"HTTP {status_code}")

        # Test pipeline statistics
        response = self.make_request("GET", "/crm/pipeline-stats", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "total_prospects" in data or "stats" in data:
                    self.log_test("CRM System - Pipeline Statistics", True,
                                "Pipeline stats endpoint working")
                else:
                    self.log_test("CRM System - Pipeline Statistics", False,
                                "Missing expected stats fields")
            except json.JSONDecodeError:
                self.log_test("CRM System - Pipeline Statistics", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("CRM System - Pipeline Statistics", False, f"HTTP {status_code}")

        # Test prospect creation
        prospect_data = {
            "name": f"Test Prospect Phase2 {int(time.time())}",
            "email": f"test.prospect.{int(time.time())}@example.com",
            "phone": "+1-555-PHASE2",
            "notes": "Created during Phase 2 backend testing"
        }
        
        response = self.make_request("POST", "/crm/prospects", prospect_data,
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success") and data.get("prospect_id"):
                    self.log_test("CRM System - Create Prospect", True,
                                f"Created prospect: {data.get('prospect_id')}")
                else:
                    self.log_test("CRM System - Create Prospect", False,
                                "Missing success flag or prospect_id")
            except json.JSONDecodeError:
                self.log_test("CRM System - Create Prospect", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("CRM System - Create Prospect", False, f"HTTP {status_code}")

    def test_google_integration(self):
        """Test Google integration endpoints"""
        print("🔍 Testing Google Integration APIs...")
        
        if not self.admin_token:
            self.log_test("Google Integration", False, "No admin token available")
            return

        # Test Google OAuth URL generation
        response = self.make_request("GET", "/auth/google/url", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("auth_url") and "accounts.google.com" in data["auth_url"]:
                    self.log_test("Google Integration - OAuth URL Generation", True,
                                "Valid Google OAuth URL generated")
                else:
                    self.log_test("Google Integration - OAuth URL Generation", False,
                                "Invalid or missing OAuth URL")
            except json.JSONDecodeError:
                self.log_test("Google Integration - OAuth URL Generation", False, 
                            "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Google Integration - OAuth URL Generation", False, f"HTTP {status_code}")

        # Test Google connection status
        response = self.make_request("GET", "/google/connection/test-all", 
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "overall_status" in data and "services" in data:
                    services = data.get("services", {})
                    expected_services = ["gmail", "calendar", "drive", "meet"]
                    found_services = [svc for svc in expected_services if svc in services]
                    self.log_test("Google Integration - Connection Monitor", True,
                                f"Connection monitor working, {len(found_services)}/4 services configured")
                else:
                    self.log_test("Google Integration - Connection Monitor", False,
                                "Missing expected connection status fields")
            except json.JSONDecodeError:
                self.log_test("Google Integration - Connection Monitor", False, 
                            "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Google Integration - Connection Monitor", False, f"HTTP {status_code}")

        # Test Gmail API endpoints
        response = self.make_request("GET", "/google/gmail/real-messages", 
                                   auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "messages" in data or "auth_required" in data:
                        self.log_test("Google Integration - Gmail API", True,
                                    "Gmail API endpoint accessible")
                    else:
                        self.log_test("Google Integration - Gmail API", False,
                                    "Unexpected Gmail API response format")
                except json.JSONDecodeError:
                    self.log_test("Google Integration - Gmail API", False, "Invalid JSON response")
            else:
                self.log_test("Google Integration - Gmail API", True,
                            f"Gmail API endpoint exists (HTTP {response.status_code})")
        else:
            self.log_test("Google Integration - Gmail API", False, "No response")

        # Test Calendar API endpoints
        response = self.make_request("GET", "/google/calendar/events", 
                                   auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "events" in data or "auth_required" in data:
                        self.log_test("Google Integration - Calendar API", True,
                                    "Calendar API endpoint accessible")
                    else:
                        self.log_test("Google Integration - Calendar API", False,
                                    "Unexpected Calendar API response format")
                except json.JSONDecodeError:
                    self.log_test("Google Integration - Calendar API", False, "Invalid JSON response")
            else:
                self.log_test("Google Integration - Calendar API", True,
                            f"Calendar API endpoint exists (HTTP {response.status_code})")
        else:
            self.log_test("Google Integration - Calendar API", False, "No response")

    def test_database_operations(self):
        """Test database operations and repository pattern"""
        print("🔍 Testing Database Operations & Repository Pattern...")
        
        if not self.admin_token:
            self.log_test("Database Operations", False, "No admin token available")
            return

        # Test database connectivity through health endpoint
        response = self.make_request("GET", "/health/ready", auth_token=self.admin_token)
        if response and response.status_code == 200:
            self.log_test("Database Operations - Connectivity", True,
                        "Database connectivity verified through readiness check")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Database Operations - Connectivity", False, f"HTTP {status_code}")

        # Test MongoDB user operations (repository pattern)
        response = self.make_request("GET", "/admin/users", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                users = data.get("users", [])
                # Verify expected users exist (Phase 2 migration verification)
                expected_users = ["admin", "alejandro_mariscal", "client1"]
                found_users = []
                for user in users:
                    if user.get("username") in expected_users:
                        found_users.append(user.get("username"))
                
                if len(found_users) >= 3:
                    self.log_test("Database Operations - User Repository", True,
                                f"Repository pattern working, found {len(found_users)} expected users")
                else:
                    self.log_test("Database Operations - User Repository", False,
                                f"Expected ≥3 users, found {len(found_users)}")
            except json.JSONDecodeError:
                self.log_test("Database Operations - User Repository", False, 
                            "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Database Operations - User Repository", False, f"HTTP {status_code}")

        # Test data consistency (user_type field migration)
        if response and response.status_code == 200:
            try:
                data = response.json()
                users = data.get("users", [])
                users_with_type = [u for u in users if u.get("type")]
                if len(users_with_type) == len(users):
                    self.log_test("Database Operations - Schema Migration", True,
                                "All users have 'type' field (Phase 2 migration successful)")
                else:
                    self.log_test("Database Operations - Schema Migration", False,
                                f"{len(users) - len(users_with_type)} users missing 'type' field")
            except json.JSONDecodeError:
                self.log_test("Database Operations - Schema Migration", False, 
                            "Invalid JSON response")

    def test_session_management(self):
        """Test JWT session management and security"""
        print("🔍 Testing Session Management & JWT Security...")
        
        # Test protected endpoint without token
        response = self.make_request("GET", "/admin/users")
        if response and response.status_code == 401:
            self.log_test("Session Management - Unauthorized Access", True,
                        "Protected endpoint correctly returns 401 without token")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Session Management - Unauthorized Access", False,
                        f"Expected 401, got HTTP {status_code}")

        # Test protected endpoint with valid token
        if self.admin_token:
            response = self.make_request("GET", "/admin/users", auth_token=self.admin_token)
            if response and response.status_code == 200:
                self.log_test("Session Management - Authorized Access", True,
                            "Protected endpoint accessible with valid token")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test("Session Management - Authorized Access", False,
                            f"Expected 200, got HTTP {status_code}")

        # Test token validation with invalid token
        invalid_token = "invalid.jwt.token"
        response = self.make_request("GET", "/admin/users", auth_token=invalid_token)
        if response and response.status_code == 401:
            self.log_test("Session Management - Invalid Token", True,
                        "Invalid token correctly rejected")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Session Management - Invalid Token", False,
                        f"Expected 401, got HTTP {status_code}")

        # Test role-based access (client token on admin endpoint)
        if self.client_token:
            response = self.make_request("GET", "/admin/users", auth_token=self.client_token)
            if response and response.status_code == 403:
                self.log_test("Session Management - Role-Based Access", True,
                            "Client token correctly denied admin access")
            else:
                status_code = response.status_code if response else "No response"
                self.log_test("Session Management - Role-Based Access", False,
                            f"Expected 403, got HTTP {status_code}")

    def test_alejandro_production_setup(self):
        """Test Alejandro Mariscal's production setup verification"""
        print("🔍 Testing Alejandro Mariscal Production Setup Verification...")
        
        if not self.admin_token:
            self.log_test("Alejandro Production Setup", False, "No admin token available")
            return

        # 1. Client Record Verification
        response = self.make_request("GET", "/admin/clients/client_alejandro/details", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("email") == "alexmar7609@gmail.com":
                    self.log_test("Client Record Verification", True, 
                                f"Client found: {data.get('name', 'N/A')}, Email: {data.get('email', 'N/A')}")
                else:
                    self.log_test("Client Record Verification", False, 
                                f"Email mismatch. Expected: alexmar7609@gmail.com, Got: {data.get('email', 'N/A')}")
            except json.JSONDecodeError:
                self.log_test("Client Record Verification", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Client Record Verification", False, f"HTTP {status_code}")

        # 2. Ready for Investment Endpoint
        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                alejandro_found = any(client.get("name") == "Alejandro Mariscal Romero" for client in ready_clients)
                if alejandro_found:
                    self.log_test("Ready for Investment Endpoint", True, 
                                f"Alejandro found in ready clients list ({len(ready_clients)} total)")
                else:
                    self.log_test("Ready for Investment Endpoint", False, 
                                f"Alejandro not found in ready clients list ({len(ready_clients)} clients)")
            except json.JSONDecodeError:
                self.log_test("Ready for Investment Endpoint", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Ready for Investment Endpoint", False, f"HTTP {status_code}")

        # 3. Investment Records Verification
        response = self.make_request("GET", "/investments/client/client_alejandro", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                investments = data.get("investments", [])
                if len(investments) == 2:
                    # Check for BALANCE ($100,000) and CORE ($18,151.41)
                    balance_found = any(inv.get("fund_code") == "BALANCE" and inv.get("principal_amount") == 100000 for inv in investments)
                    core_found = any(inv.get("fund_code") == "CORE" and inv.get("principal_amount") == 18151.41 for inv in investments)
                    
                    if balance_found and core_found:
                        total_amount = sum(inv.get("principal_amount", 0) for inv in investments)
                        self.log_test("Investment Records Verification", True, 
                                    f"Found 2 investments: BALANCE ($100,000) + CORE ($18,151.41) = ${total_amount:,.2f}")
                    else:
                        self.log_test("Investment Records Verification", False, 
                                    f"Investment amounts/types incorrect. Expected: BALANCE $100,000 + CORE $18,151.41")
                else:
                    self.log_test("Investment Records Verification", False, 
                                f"Expected 2 investments, found {len(investments)}")
            except json.JSONDecodeError:
                self.log_test("Investment Records Verification", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Investment Records Verification", False, f"HTTP {status_code}")

        # 4. MT5 Accounts Verification
        response = self.make_request("GET", "/mt5/accounts/client_alejandro", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                accounts = data.get("accounts", [])
                if len(accounts) == 4:
                    # Check for expected MT5 accounts: 886557, 886066, 886602, 885822
                    expected_accounts = ["886557", "886066", "886602", "885822"]
                    found_accounts = [acc.get("mt5_account_number") for acc in accounts]
                    
                    # Check if all expected accounts are found
                    all_found = all(acc in found_accounts for acc in expected_accounts)
                    
                    # Check MEXAtlantic broker
                    mexatlantic_accounts = [acc for acc in accounts if acc.get("broker_name") == "MEXAtlantic"]
                    
                    if all_found and len(mexatlantic_accounts) == 4:
                        total_balance = sum(acc.get("balance", 0) for acc in accounts)
                        self.log_test("MT5 Accounts Verification", True, 
                                    f"Found 4 MT5 accounts with MEXAtlantic broker, Total: ${total_balance:,.2f}")
                    else:
                        self.log_test("MT5 Accounts Verification", False, 
                                    f"Account numbers or broker mismatch. Expected: {expected_accounts} with MEXAtlantic")
                else:
                    self.log_test("MT5 Accounts Verification", False, 
                                f"Expected 4 MT5 accounts, found {len(accounts)}")
            except json.JSONDecodeError:
                self.log_test("MT5 Accounts Verification", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("MT5 Accounts Verification", False, f"HTTP {status_code}")

        # 5. Investment Overview
        response = self.make_request("GET", "/investments/admin/overview", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                total_aum = data.get("total_aum", 0)
                expected_aum = 118151.41
                
                if abs(total_aum - expected_aum) < 0.01:  # Allow for small floating point differences
                    self.log_test("Investment Overview", True, 
                                f"Total AUM matches expected: ${total_aum:,.2f}")
                else:
                    self.log_test("Investment Overview", False, 
                                f"AUM mismatch. Expected: ${expected_aum:,.2f}, Got: ${total_aum:,.2f}")
            except json.JSONDecodeError:
                self.log_test("Investment Overview", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("Investment Overview", False, f"HTTP {status_code}")

    def run_comprehensive_test(self):
        """Run all backend tests"""
        print("🚀 FIDUS Backend API Testing Suite - Alejandro Mariscal Production Setup Verification")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Run authentication first
        self.test_user_authentication()
        
        # Run Alejandro production setup verification
        self.test_alejandro_production_setup()
        
        # Run other critical tests
        self.test_health_endpoints()
        self.test_user_management()
        self.test_investment_management()
        self.test_crm_system()
        self.test_google_integration()
        self.test_database_operations()
        self.test_session_management()

        # Generate summary
        print("=" * 80)
        print("🎯 FIDUS BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        # Show failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
            print()

        # Show critical findings
        print("🔍 CRITICAL FINDINGS:")
        
        if self.admin_token:
            print("   ✅ Admin authentication working with JWT tokens")
        else:
            print("   ❌ Admin authentication failed - critical issue")
            
        if self.client_token:
            print("   ✅ Client authentication working (alejandro_mariscal verified)")
        else:
            print("   ❌ Client authentication failed - user access blocked")

        # Database architecture verification
        user_mgmt_tests = [t for t in self.test_results if "User Management" in t["test"]]
        user_mgmt_success = sum(1 for t in user_mgmt_tests if t["success"])
        if user_mgmt_success >= 2:
            print("   ✅ Phase 2 database architecture operational")
        else:
            print("   ❌ Phase 2 database architecture issues detected")

        # Google integration status
        google_tests = [t for t in self.test_results if "Google Integration" in t["test"]]
        google_success = sum(1 for t in google_tests if t["success"])
        if google_success >= 2:
            print("   ✅ Google integration infrastructure ready")
        else:
            print("   ❌ Google integration infrastructure needs attention")

        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 BACKEND STATUS: READY FOR PHASE 3 MT5 INTEGRATION")
        elif success_rate >= 60:
            print("⚠️  BACKEND STATUS: MINOR ISSUES - REVIEW REQUIRED")
        else:
            print("🚨 BACKEND STATUS: CRITICAL ISSUES - IMMEDIATE ATTENTION REQUIRED")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = FidusBackendTester()
    success_rate = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)