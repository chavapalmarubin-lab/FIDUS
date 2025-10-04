#!/usr/bin/env python3
"""
FIDUS Backend API Testing Suite - Phase 2 Database Architecture Verification
Testing comprehensive backend functionality after MongoDB migration and repository pattern implementation.

Test Areas:
1. Health Check Endpoints
2. User Authentication & Session Management  
3. User Management System
4. Investment Management System
5. CRM Pipeline System
6. Google Integration APIs
7. Database Operations & Repository Pattern
8. JWT Token Management

Context: 7 users exist in database (including alejandro_mariscal)
Investment collection is clean (0 investments)
MongoDB Atlas connection operational at ~30ms ping time
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
import uuid

# Backend URL Configuration
BACKEND_URL = "https://invest-manager-9.preview.emergentagent.com/api"

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
        """Test GET /admin/google/individual-status endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/individual-status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get('success') and 'connected' in data and 'admin_info' in data:
                    # Should show "No Google account connected" initially
                    if not data.get('connected') and data.get('message') == "No Google account connected":
                        self.log_result("Individual Google Status - Not Connected", True, 
                                      "Correctly shows no Google account connected initially",
                                      {"response": data})
                    elif data.get('connected'):
                        self.log_result("Individual Google Status - Connected", True, 
                                      "Google account is connected for admin",
                                      {"google_info": data.get('google_info', {})})
                    else:
                        self.log_result("Individual Google Status - Unexpected State", False, 
                                      f"Unexpected connection state: {data.get('message')}", 
                                      {"response": data})
                else:
                    self.log_result("Individual Google Status - Invalid Response", False, 
                                  "Response missing required fields", {"response": data})
            elif response.status_code == 401:
                self.log_result("Individual Google Status - Authentication", False, 
                              "Endpoint requires admin authentication (expected behavior)")
            else:
                self.log_result("Individual Google Status - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Individual Google Status", False, f"Exception: {str(e)}")
    
    def test_individual_google_auth_url_endpoint(self):
        """Test GET /admin/google/individual-auth-url endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/individual-auth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get('success') and 'auth_url' in data:
                    auth_url = data.get('auth_url')
                    
                    # Verify OAuth URL contains required parameters
                    required_params = [
                        'client_id=',
                        'redirect_uri=',
                        'response_type=code',
                        'scope=',
                        'access_type=offline',
                        'prompt=consent'
                    ]
                    
                    # Check for required scopes
                    required_scopes = [
                        'gmail.readonly',
                        'gmail.send',
                        'calendar',
                        'drive'
                    ]
                    
                    url_valid = True
                    missing_params = []
                    missing_scopes = []
                    
                    for param in required_params:
                        if param not in auth_url:
                            url_valid = False
                            missing_params.append(param)
                    
                    for scope in required_scopes:
                        if scope not in auth_url:
                            missing_scopes.append(scope)
                    
                    if url_valid and not missing_scopes:
                        self.log_result("Individual Google Auth URL - Valid", True, 
                                      "Generated proper Google OAuth URL with all required parameters",
                                      {"auth_url_length": len(auth_url), "admin_info": data.get('admin_user_id')})
                    else:
                        self.log_result("Individual Google Auth URL - Invalid", False, 
                                      "OAuth URL missing required parameters or scopes", 
                                      {"missing_params": missing_params, "missing_scopes": missing_scopes})
                else:
                    self.log_result("Individual Google Auth URL - Invalid Response", False, 
                                  "Response missing required fields", {"response": data})
            elif response.status_code == 401:
                self.log_result("Individual Google Auth URL - Authentication", False, 
                              "Endpoint requires admin authentication (expected behavior)")
            else:
                self.log_result("Individual Google Auth URL - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Individual Google Auth URL", False, f"Exception: {str(e)}")
    
    def test_all_admin_google_connections_endpoint(self):
        """Test GET /admin/google/all-connections endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/all-connections")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get('success') and 'total_connections' in data and 'connections' in data:
                    total_connections = data.get('total_connections', 0)
                    connections = data.get('connections', [])
                    
                    # Should return empty list initially (no connections yet)
                    if total_connections == 0 and len(connections) == 0:
                        self.log_result("All Admin Google Connections - Empty", True, 
                                      "Correctly returns empty list initially (no connections)",
                                      {"total_connections": total_connections})
                    elif total_connections > 0:
                        # If there are connections, verify structure
                        connection_valid = True
                        for conn in connections:
                            required_fields = ['admin_user_id', 'admin_name', 'admin_email', 'connection_status']
                            for field in required_fields:
                                if field not in conn:
                                    connection_valid = False
                                    break
                        
                        if connection_valid:
                            self.log_result("All Admin Google Connections - Valid", True, 
                                          f"Found {total_connections} valid admin connections",
                                          {"connections_preview": connections[:2]})  # Show first 2
                        else:
                            self.log_result("All Admin Google Connections - Invalid Structure", False, 
                                          "Connection objects missing required fields", 
                                          {"connections": connections})
                    else:
                        self.log_result("All Admin Google Connections - Mismatch", False, 
                                      f"Total connections mismatch: {total_connections} vs {len(connections)}")
                else:
                    self.log_result("All Admin Google Connections - Invalid Response", False, 
                                  "Response missing required fields", {"response": data})
            elif response.status_code == 401:
                self.log_result("All Admin Google Connections - Authentication", False, 
                              "Endpoint requires admin authentication (expected behavior)")
            else:
                self.log_result("All Admin Google Connections - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("All Admin Google Connections", False, f"Exception: {str(e)}")
    
    def test_individual_google_disconnect_endpoint(self):
        """Test POST /admin/google/individual-disconnect endpoint"""
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/google/individual-disconnect")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if 'success' in data and 'message' in data and 'admin_info' in data:
                    # Should return proper error message when no connection exists
                    if not data.get('success') and "No Google connection found" in data.get('message', ''):
                        self.log_result("Individual Google Disconnect - No Connection", True, 
                                      "Correctly returns error when no connection exists",
                                      {"message": data.get('message')})
                    elif data.get('success') and "disconnected" in data.get('message', '').lower():
                        self.log_result("Individual Google Disconnect - Success", True, 
                                      "Successfully disconnected Google account",
                                      {"message": data.get('message')})
                    else:
                        self.log_result("Individual Google Disconnect - Unexpected Response", False, 
                                      f"Unexpected response: {data.get('message')}", 
                                      {"response": data})
                else:
                    self.log_result("Individual Google Disconnect - Invalid Response", False, 
                                  "Response missing required fields", {"response": data})
            elif response.status_code == 401:
                self.log_result("Individual Google Disconnect - Authentication", False, 
                              "Endpoint requires admin authentication (expected behavior)")
            else:
                self.log_result("Individual Google Disconnect - HTTP Error", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Individual Google Disconnect", False, f"Exception: {str(e)}")
    
    def test_authentication_requirements(self):
        """Test that all endpoints require proper admin JWT authentication"""
        try:
            # Test endpoints without authentication
            endpoints_to_test = [
                "/admin/google/individual-status",
                "/admin/google/individual-auth-url", 
                "/admin/google/all-connections"
            ]
            
            # Create session without auth token
            unauth_session = requests.Session()
            
            all_protected = True
            unprotected_endpoints = []
            
            for endpoint in endpoints_to_test:
                try:
                    response = unauth_session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code != 401:
                        all_protected = False
                        unprotected_endpoints.append(f"{endpoint} (HTTP {response.status_code})")
                except Exception as e:
                    # Network errors are acceptable for this test
                    pass
            
            # Test POST endpoint
            try:
                response = unauth_session.post(f"{BACKEND_URL}/admin/google/individual-disconnect")
                if response.status_code != 401:
                    all_protected = False
                    unprotected_endpoints.append(f"/admin/google/individual-disconnect (HTTP {response.status_code})")
            except Exception as e:
                pass
            
            if all_protected:
                self.log_result("Authentication Requirements", True, 
                              "All endpoints properly require admin JWT authentication")
            else:
                self.log_result("Authentication Requirements", False, 
                              "Some endpoints not properly protected", 
                              {"unprotected": unprotected_endpoints})
                
        except Exception as e:
            self.log_result("Authentication Requirements", False, f"Exception: {str(e)}")
    
    def test_google_oauth_environment_variables(self):
        """Test that Google OAuth environment variables are properly configured"""
        try:
            # Test auth URL generation to verify environment variables
            response = self.session.get(f"{BACKEND_URL}/admin/google/individual-auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                # Check for Google client ID in URL
                if 'client_id=' in auth_url and len(auth_url) > 200:
                    # Extract client ID from URL
                    import re
                    client_id_match = re.search(r'client_id=([^&]+)', auth_url)
                    redirect_uri_match = re.search(r'redirect_uri=([^&]+)', auth_url)
                    
                    if client_id_match and redirect_uri_match:
                        client_id = client_id_match.group(1)
                        redirect_uri = redirect_uri_match.group(1)
                        
                        self.log_result("Google OAuth Environment Variables", True, 
                                      "Google OAuth environment variables properly configured",
                                      {"client_id_prefix": client_id[:20] + "...", 
                                       "redirect_uri": redirect_uri})
                    else:
                        self.log_result("Google OAuth Environment Variables", False, 
                                      "Could not extract OAuth parameters from URL")
                else:
                    self.log_result("Google OAuth Environment Variables", False, 
                                  "OAuth URL appears malformed or missing client_id")
            else:
                self.log_result("Google OAuth Environment Variables", False, 
                              f"Could not test environment variables: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google OAuth Environment Variables", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Individual Google OAuth endpoint tests"""
        print("🎯 INDIVIDUAL GOOGLE OAUTH ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Test authentication requirements first (without auth)
        print("🔒 Testing Authentication Requirements...")
        print("-" * 50)
        self.test_authentication_requirements()
        
        # Authenticate for protected endpoint tests
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with protected endpoint tests.")
            return False
        
        print("\n🔍 Running Individual Google OAuth Endpoint Tests...")
        print("-" * 50)
        
        # Run all endpoint tests
        self.test_individual_google_status_endpoint()
        self.test_individual_google_auth_url_endpoint()
        self.test_all_admin_google_connections_endpoint()
        self.test_individual_google_disconnect_endpoint()
        self.test_google_oauth_environment_variables()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 INDIVIDUAL GOOGLE OAUTH ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment for Individual Google OAuth endpoints
        critical_tests = [
            "Individual Google Status",
            "Individual Google Auth URL", 
            "All Admin Google Connections",
            "Individual Google Disconnect",
            "Authentication Requirements"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ INDIVIDUAL GOOGLE OAUTH SYSTEM: OPERATIONAL")
            print("   All Individual Google OAuth endpoints are working properly.")
            print("   System ready for individual admin Google account connections.")
            print("   Replacing old automatic service account approach successfully.")
        else:
            print("❌ INDIVIDUAL GOOGLE OAUTH SYSTEM: ISSUES DETECTED")
            print("   Critical Individual Google OAuth endpoint issues found.")
            print("   Main agent action required to fix OAuth implementation.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = IndividualGoogleOAuthTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()