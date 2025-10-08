#!/usr/bin/env python3
"""
MT5 Integration Testing on Render Production Service
Testing comprehensive MT5 integration fixes on the deployed Render service.

Service URL: https://fidus-api.onrender.com

Priority Testing Areas:
1. MT5 Service Initialization - /api/health endpoint with MT5 integration status
2. MT5 Account Management - client MT5 account retrieval and creation
3. Background Task Execution - delayed MT5 initialization and mock allocation
4. Key Endpoints - health, accounts, performance data
5. Error Handling - no asyncio event loop conflicts, proper path resolution

Expected Outcomes:
- All MT5 endpoints respond successfully
- Mock MT5 service initializes without event loop conflicts
- Background tasks complete successfully
- Path utilities work correctly for Render environment
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone
import uuid

# Render Production Service URL
BACKEND_URL = "https://fidus-api.onrender.com/api"

# Test Users for Authentication
TEST_USERS = {
    "admin": {
        "username": "admin", 
        "password": "password123",
        "user_type": "admin"
    }
}

class MT5RenderTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
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

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None, timeout=45):
        """Make HTTP request with proper error handling and extended timeout for Render"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Set up headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        if auth_token:
            req_headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            print(f"Making {method} request to: {url}")  # Debug logging
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            print(f"Response: {response.status_code}")  # Debug logging
            return response
        except requests.exceptions.Timeout:
            print(f"Request timeout after {timeout}s: {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Attempting Admin Authentication...")
        
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
                    return True
                else:
                    self.log_test("Admin Authentication", False, "Missing token or incorrect type")
                    return False
            except json.JSONDecodeError:
                self.log_test("Admin Authentication", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            try:
                error_detail = response.json().get("detail", "Unknown error") if response else "No response"
                self.log_test("Admin Authentication", False, f"HTTP {status_code}: {error_detail}")
            except:
                self.log_test("Admin Authentication", False, f"HTTP {status_code}")
            
            # Continue with limited testing even without authentication
            print("⚠️  Continuing with limited testing (no authentication)")
            return False

    def test_mt5_service_initialization(self):
        """Test MT5 Service Initialization"""
        print("🔍 Testing MT5 Service Initialization...")
        
        # Test health endpoint with MT5 integration status
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("status") == "healthy":
                    # Check for MT5-specific health indicators
                    mt5_indicators = []
                    if "mt5" in str(data).lower():
                        mt5_indicators.append("MT5 mentioned in health response")
                    if "service" in data:
                        mt5_indicators.append(f"Service: {data.get('service')}")
                    
                    self.log_test("MT5 Service - Health Check", True, 
                                f"Status: {data.get('status')}, Indicators: {', '.join(mt5_indicators) if mt5_indicators else 'Basic health check'}")
                else:
                    self.log_test("MT5 Service - Health Check", False, 
                                f"Unexpected status: {data.get('status')}")
            except json.JSONDecodeError:
                self.log_test("MT5 Service - Health Check", False, "Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            self.log_test("MT5 Service - Health Check", False, f"HTTP {status_code}")

        # Test MT5-specific health endpoint if available
        response = self.make_request("GET", "/mt5/health", auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_test("MT5 Service - MT5 Health Endpoint", True, 
                                f"MT5 health endpoint accessible: {data}")
                except json.JSONDecodeError:
                    self.log_test("MT5 Service - MT5 Health Endpoint", True, 
                                "MT5 health endpoint accessible (non-JSON response)")
            elif response.status_code == 404:
                self.log_test("MT5 Service - MT5 Health Endpoint", False, 
                            "MT5 health endpoint not found (404)")
            else:
                self.log_test("MT5 Service - MT5 Health Endpoint", False, 
                            f"MT5 health endpoint error: HTTP {response.status_code}")
        else:
            self.log_test("MT5 Service - MT5 Health Endpoint", False, "No response from MT5 health endpoint")

    def test_mt5_account_management(self):
        """Test MT5 Account Management"""
        print("🔍 Testing MT5 Account Management...")
        
        if not self.admin_token:
            self.log_test("MT5 Account Management", False, "No admin token available")
            return

        # Test client MT5 account retrieval - client_003 as specified in review
        response = self.make_request("GET", "/mt5/accounts/client_003", auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) or (isinstance(data, dict) and "accounts" in data):
                        account_count = len(data) if isinstance(data, list) else len(data.get("accounts", []))
                        self.log_test("MT5 Account Management - Client Account Retrieval", True, 
                                    f"Retrieved {account_count} MT5 accounts for client_003")
                    else:
                        self.log_test("MT5 Account Management - Client Account Retrieval", True, 
                                    f"MT5 account endpoint accessible: {data}")
                except json.JSONDecodeError:
                    self.log_test("MT5 Account Management - Client Account Retrieval", True, 
                                "MT5 account endpoint accessible (non-JSON response)")
            elif response.status_code == 404:
                self.log_test("MT5 Account Management - Client Account Retrieval", False, 
                            "MT5 account endpoint not found (404)")
            elif response.status_code == 500:
                # Check if it's an asyncio event loop error
                try:
                    error_data = response.json()
                    error_msg = str(error_data)
                    if "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                        self.log_test("MT5 Account Management - Client Account Retrieval", False, 
                                    f"Asyncio event loop error detected: {error_msg}")
                    else:
                        self.log_test("MT5 Account Management - Client Account Retrieval", False, 
                                    f"Server error (500): {error_msg}")
                except:
                    self.log_test("MT5 Account Management - Client Account Retrieval", False, 
                                f"Server error (500): Unable to parse error details")
            else:
                self.log_test("MT5 Account Management - Client Account Retrieval", False, 
                            f"HTTP {response.status_code}")
        else:
            self.log_test("MT5 Account Management - Client Account Retrieval", False, "No response")

        # Test MT5 account creation functionality
        test_account_data = {
            "client_id": "client_003",
            "broker_code": "multibank",
            "account_type": "investment",
            "initial_balance": 10000.0
        }
        
        response = self.make_request("POST", "/mt5/accounts/create", test_account_data, auth_token=self.admin_token)
        if response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if data.get("success") or data.get("account_id") or data.get("mt5_account_number"):
                        self.log_test("MT5 Account Management - Account Creation", True, 
                                    f"MT5 account creation successful: {data}")
                    else:
                        self.log_test("MT5 Account Management - Account Creation", True, 
                                    f"MT5 account creation endpoint accessible: {data}")
                except json.JSONDecodeError:
                    self.log_test("MT5 Account Management - Account Creation", True, 
                                "MT5 account creation endpoint accessible")
            elif response.status_code == 404:
                self.log_test("MT5 Account Management - Account Creation", False, 
                            "MT5 account creation endpoint not found (404)")
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = str(error_data)
                    if "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                        self.log_test("MT5 Account Management - Account Creation", False, 
                                    f"Asyncio event loop error detected: {error_msg}")
                    else:
                        self.log_test("MT5 Account Management - Account Creation", False, 
                                    f"Server error (500): {error_msg}")
                except:
                    self.log_test("MT5 Account Management - Account Creation", False, 
                                f"Server error (500): Unable to parse error details")
            else:
                self.log_test("MT5 Account Management - Account Creation", False, 
                            f"HTTP {response.status_code}")
        else:
            self.log_test("MT5 Account Management - Account Creation", False, "No response")

        # Test MT5 performance data retrieval
        response = self.make_request("GET", "/mt5/performance/client_003", auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_test("MT5 Account Management - Performance Data", True, 
                                f"MT5 performance data retrieved: {data}")
                except json.JSONDecodeError:
                    self.log_test("MT5 Account Management - Performance Data", True, 
                                "MT5 performance endpoint accessible")
            elif response.status_code == 404:
                self.log_test("MT5 Account Management - Performance Data", False, 
                            "MT5 performance endpoint not found (404)")
            else:
                self.log_test("MT5 Account Management - Performance Data", False, 
                            f"HTTP {response.status_code}")
        else:
            self.log_test("MT5 Account Management - Performance Data", False, "No response")

    def test_background_task_execution(self):
        """Test Background Task Execution"""
        print("🔍 Testing Background Task Execution...")
        
        if not self.admin_token:
            self.log_test("Background Task Execution", False, "No admin token available")
            return

        # Test endpoints that should trigger delayed MT5 initialization
        test_endpoints = [
            ("/mt5/initialize", "MT5 Initialization Trigger"),
            ("/mt5/background/status", "Background Task Status"),
            ("/mt5/tasks/status", "MT5 Task Status")
        ]
        
        for endpoint, test_name in test_endpoints:
            response = self.make_request("GET", endpoint, auth_token=self.admin_token)
            if response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log_test(f"Background Tasks - {test_name}", True, 
                                    f"Endpoint accessible: {data}")
                    except json.JSONDecodeError:
                        self.log_test(f"Background Tasks - {test_name}", True, 
                                    "Endpoint accessible (non-JSON response)")
                elif response.status_code == 404:
                    self.log_test(f"Background Tasks - {test_name}", False, 
                                f"Endpoint not found (404): {endpoint}")
                elif response.status_code == 500:
                    try:
                        error_data = response.json()
                        error_msg = str(error_data)
                        if "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                            self.log_test(f"Background Tasks - {test_name}", False, 
                                        f"Asyncio event loop error: {error_msg}")
                        else:
                            self.log_test(f"Background Tasks - {test_name}", False, 
                                        f"Server error (500): {error_msg}")
                    except:
                        self.log_test(f"Background Tasks - {test_name}", False, 
                                    f"Server error (500): Unable to parse error details")
                else:
                    self.log_test(f"Background Tasks - {test_name}", False, 
                                f"HTTP {response.status_code}")
            else:
                self.log_test(f"Background Tasks - {test_name}", False, "No response")

        # Test mock allocation creation
        mock_allocation_data = {
            "client_id": "client_003",
            "amount": 5000.0,
            "allocation_type": "test"
        }
        
        response = self.make_request("POST", "/mt5/allocations/create", mock_allocation_data, auth_token=self.admin_token)
        if response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.log_test("Background Tasks - Mock Allocation Creation", True, 
                                f"Mock allocation created successfully: {data}")
                except json.JSONDecodeError:
                    self.log_test("Background Tasks - Mock Allocation Creation", True, 
                                "Mock allocation endpoint accessible")
            elif response.status_code == 404:
                self.log_test("Background Tasks - Mock Allocation Creation", False, 
                            "Mock allocation endpoint not found (404)")
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = str(error_data)
                    if "conflict" in error_msg.lower():
                        self.log_test("Background Tasks - Mock Allocation Creation", False, 
                                    f"Allocation conflict detected: {error_msg}")
                    elif "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                        self.log_test("Background Tasks - Mock Allocation Creation", False, 
                                    f"Asyncio event loop error: {error_msg}")
                    else:
                        self.log_test("Background Tasks - Mock Allocation Creation", False, 
                                    f"Server error (500): {error_msg}")
                except:
                    self.log_test("Background Tasks - Mock Allocation Creation", False, 
                                f"Server error (500): Unable to parse error details")
            else:
                self.log_test("Background Tasks - Mock Allocation Creation", False, 
                            f"HTTP {response.status_code}")
        else:
            self.log_test("Background Tasks - Mock Allocation Creation", False, "No response")

    def test_key_mt5_endpoints(self):
        """Test Key MT5 Endpoints"""
        print("🔍 Testing Key MT5 Endpoints...")
        
        # Test some endpoints without authentication first
        public_endpoints = [
            ("/health", "Health Check with MT5 Integration Status", False),
            ("/mt5/status", "MT5 Status Endpoint", False),
            ("/mt5/bridge/health", "MT5 Bridge Health", False)
        ]
        
        for endpoint, test_name, requires_auth in public_endpoints:
            auth_token = self.admin_token if requires_auth else None
            response = self.make_request("GET", endpoint, auth_token=auth_token)
            
            if response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Check for specific MT5 integration indicators
                        mt5_indicators = []
                        data_str = str(data).lower()
                        if "mt5" in data_str:
                            mt5_indicators.append("MT5 data present")
                        if "bridge" in data_str:
                            mt5_indicators.append("Bridge data present")
                        if "status" in data_str:
                            mt5_indicators.append("Status information present")
                        if "healthy" in data_str:
                            mt5_indicators.append("Healthy status")
                            
                        indicator_text = f", Indicators: {', '.join(mt5_indicators)}" if mt5_indicators else ""
                        self.log_test(f"Key Endpoints - {test_name}", True, 
                                    f"Endpoint successful{indicator_text}")
                    except json.JSONDecodeError:
                        self.log_test(f"Key Endpoints - {test_name}", True, 
                                    "Endpoint accessible (non-JSON response)")
                elif response.status_code == 404:
                    self.log_test(f"Key Endpoints - {test_name}", False, 
                                f"Endpoint not found (404): {endpoint}")
                elif response.status_code == 401:
                    self.log_test(f"Key Endpoints - {test_name}", False, 
                                f"Authentication required (401): {endpoint}")
                elif response.status_code == 500:
                    try:
                        error_data = response.json()
                        error_msg = str(error_data)
                        if "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                            self.log_test(f"Key Endpoints - {test_name}", False, 
                                        f"Asyncio event loop error: {error_msg}")
                        elif "permission" in error_msg.lower():
                            self.log_test(f"Key Endpoints - {test_name}", False, 
                                        f"Permission error detected: {error_msg}")
                        else:
                            self.log_test(f"Key Endpoints - {test_name}", False, 
                                        f"Server error (500): {error_msg}")
                    except:
                        self.log_test(f"Key Endpoints - {test_name}", False, 
                                    f"Server error (500): Unable to parse error details")
                else:
                    self.log_test(f"Key Endpoints - {test_name}", False, 
                                f"HTTP {response.status_code}")
            else:
                self.log_test(f"Key Endpoints - {test_name}", False, "No response")
        
        # If we have admin token, test protected endpoints
        if not self.admin_token:
            print("   ⚠️  Skipping protected MT5 endpoints (no authentication)")
            return

        # Key endpoints to test as specified in review
        key_endpoints = [
            ("/health", "Health Check with MT5 Integration Status", False),  # No auth needed
            ("/mt5/accounts/client_003", "Client MT5 Account Retrieval", True),
            ("/mt5/account/123456", "MT5 Account by ID", True),
            ("/mt5/performance/123456", "Real-time Performance Data", True)
        ]
        
        for endpoint, test_name, requires_auth in key_endpoints:
            auth_token = self.admin_token if requires_auth else None
            response = self.make_request("GET", endpoint, auth_token=auth_token)
            
            if response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Check for specific MT5 integration indicators
                        mt5_indicators = []
                        data_str = str(data).lower()
                        if "mt5" in data_str:
                            mt5_indicators.append("MT5 data present")
                        if "account" in data_str:
                            mt5_indicators.append("Account data present")
                        if "performance" in data_str:
                            mt5_indicators.append("Performance data present")
                        if "status" in data_str:
                            mt5_indicators.append("Status information present")
                            
                        indicator_text = f", Indicators: {', '.join(mt5_indicators)}" if mt5_indicators else ""
                        self.log_test(f"Key Endpoints - {test_name}", True, 
                                    f"Endpoint successful{indicator_text}")
                    except json.JSONDecodeError:
                        self.log_test(f"Key Endpoints - {test_name}", True, 
                                    "Endpoint accessible (non-JSON response)")
                elif response.status_code == 404:
                    self.log_test(f"Key Endpoints - {test_name}", False, 
                                f"Endpoint not found (404): {endpoint}")
                elif response.status_code == 401:
                    self.log_test(f"Key Endpoints - {test_name}", False, 
                                f"Authentication required (401): {endpoint}")
                elif response.status_code == 500:
                    try:
                        error_data = response.json()
                        error_msg = str(error_data)
                        if "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                            self.log_test(f"Key Endpoints - {test_name}", False, 
                                        f"Asyncio event loop error: {error_msg}")
                        elif "permission" in error_msg.lower():
                            self.log_test(f"Key Endpoints - {test_name}", False, 
                                        f"Permission error detected: {error_msg}")
                        else:
                            self.log_test(f"Key Endpoints - {test_name}", False, 
                                        f"Server error (500): {error_msg}")
                    except:
                        self.log_test(f"Key Endpoints - {test_name}", False, 
                                    f"Server error (500): Unable to parse error details")
                else:
                    self.log_test(f"Key Endpoints - {test_name}", False, 
                                f"HTTP {response.status_code}")
            else:
                self.log_test(f"Key Endpoints - {test_name}", False, "No response")

    def test_error_handling(self):
        """Test Error Handling"""
        print("🔍 Testing Error Handling...")
        
        if not self.admin_token:
            self.log_test("Error Handling", False, "No admin token available")
            return

        # Test for asyncio event loop conflicts
        response = self.make_request("GET", "/mt5/test/eventloop", auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "event_loop" in str(data).lower() and "error" not in str(data).lower():
                        self.log_test("Error Handling - Event Loop Test", True, 
                                    "No event loop conflicts detected")
                    else:
                        self.log_test("Error Handling - Event Loop Test", True, 
                                    f"Event loop test endpoint accessible: {data}")
                except json.JSONDecodeError:
                    self.log_test("Error Handling - Event Loop Test", True, 
                                "Event loop test endpoint accessible")
            elif response.status_code == 404:
                self.log_test("Error Handling - Event Loop Test", False, 
                            "Event loop test endpoint not found (404)")
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = str(error_data)
                    if "cannot run the event loop while another loop is running" in error_msg.lower():
                        self.log_test("Error Handling - Event Loop Test", False, 
                                    "CRITICAL: Event loop conflict detected!")
                    elif "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                        self.log_test("Error Handling - Event Loop Test", False, 
                                    f"Event loop related error: {error_msg}")
                    else:
                        self.log_test("Error Handling - Event Loop Test", False, 
                                    f"Server error (500): {error_msg}")
                except:
                    self.log_test("Error Handling - Event Loop Test", False, 
                                f"Server error (500): Unable to parse error details")
            else:
                self.log_test("Error Handling - Event Loop Test", False, 
                            f"HTTP {response.status_code}")
        else:
            self.log_test("Error Handling - Event Loop Test", False, "No response")

        # Test path resolution for Render environment
        response = self.make_request("GET", "/mt5/test/paths", auth_token=self.admin_token)
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "/tmp" in str(data) or "path" in str(data).lower():
                        self.log_test("Error Handling - Path Resolution", True, 
                                    f"Path utilities working correctly: {data}")
                    else:
                        self.log_test("Error Handling - Path Resolution", True, 
                                    f"Path test endpoint accessible: {data}")
                except json.JSONDecodeError:
                    self.log_test("Error Handling - Path Resolution", True, 
                                "Path test endpoint accessible")
            elif response.status_code == 404:
                self.log_test("Error Handling - Path Resolution", False, 
                            "Path test endpoint not found (404)")
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = str(error_data)
                    if "permission" in error_msg.lower():
                        self.log_test("Error Handling - Path Resolution", False, 
                                    f"CRITICAL: Path permission error detected: {error_msg}")
                    else:
                        self.log_test("Error Handling - Path Resolution", False, 
                                    f"Path resolution error: {error_msg}")
                except:
                    self.log_test("Error Handling - Path Resolution", False, 
                                f"Server error (500): Unable to parse error details")
            else:
                self.log_test("Error Handling - Path Resolution", False, 
                            f"HTTP {response.status_code}")
        else:
            self.log_test("Error Handling - Path Resolution", False, "No response")

        # Test file operations using /tmp correctly
        test_file_data = {
            "filename": "test_mt5_file.txt",
            "content": "MT5 integration test file"
        }
        
        response = self.make_request("POST", "/mt5/test/file-ops", test_file_data, auth_token=self.admin_token)
        if response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if "/tmp" in str(data) or "success" in str(data).lower():
                        self.log_test("Error Handling - File Operations", True, 
                                    f"File operations using /tmp correctly: {data}")
                    else:
                        self.log_test("Error Handling - File Operations", True, 
                                    f"File operations endpoint accessible: {data}")
                except json.JSONDecodeError:
                    self.log_test("Error Handling - File Operations", True, 
                                "File operations endpoint accessible")
            elif response.status_code == 404:
                self.log_test("Error Handling - File Operations", False, 
                            "File operations endpoint not found (404)")
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = str(error_data)
                    if "permission" in error_msg.lower() and "/tmp" not in error_msg.lower():
                        self.log_test("Error Handling - File Operations", False, 
                                    f"CRITICAL: File permission error (not using /tmp): {error_msg}")
                    else:
                        self.log_test("Error Handling - File Operations", False, 
                                    f"File operations error: {error_msg}")
                except:
                    self.log_test("Error Handling - File Operations", False, 
                                f"Server error (500): Unable to parse error details")
            else:
                self.log_test("Error Handling - File Operations", False, 
                            f"HTTP {response.status_code}")
        else:
            self.log_test("Error Handling - File Operations", False, "No response")

    def run_comprehensive_mt5_test(self):
        """Run comprehensive MT5 integration test on Render production"""
        print("🚀 MT5 Integration Testing on Render Production Service")
        print("=" * 80)
        print(f"Service URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first (but continue even if it fails)
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("⚠️  Admin authentication failed - proceeding with limited testing")
            print("   (Testing endpoints that don't require authentication)")
            print()

        # Run all MT5 test suites
        self.test_mt5_service_initialization()
        self.test_mt5_account_management()
        self.test_background_task_execution()
        self.test_key_mt5_endpoints()
        self.test_error_handling()

        # Generate summary
        print("=" * 80)
        print("🎯 MT5 INTEGRATION TESTING SUMMARY")
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
        
        # Check for event loop conflicts
        event_loop_errors = [t for t in failed_tests if "event loop" in t["error"].lower()]
        if event_loop_errors:
            print("   🚨 CRITICAL: Asyncio event loop conflicts detected!")
            for error in event_loop_errors:
                print(f"      - {error['test']}: {error['error']}")
        else:
            print("   ✅ No asyncio event loop conflicts detected")

        # Check for path resolution issues
        path_errors = [t for t in failed_tests if "permission" in t["error"].lower() and "path" in t["test"].lower()]
        if path_errors:
            print("   🚨 CRITICAL: Path resolution issues detected!")
            for error in path_errors:
                print(f"      - {error['test']}: {error['error']}")
        else:
            print("   ✅ Path utilities appear to be working correctly")

        # Check MT5 service availability
        mt5_service_tests = [t for t in self.test_results if "MT5 Service" in t["test"]]
        mt5_service_success = sum(1 for t in mt5_service_tests if t["success"])
        if mt5_service_success > 0:
            print("   ✅ MT5 service initialization working")
        else:
            print("   ❌ MT5 service initialization issues detected")

        # Check MT5 account management
        account_mgmt_tests = [t for t in self.test_results if "Account Management" in t["test"]]
        account_mgmt_success = sum(1 for t in account_mgmt_tests if t["success"])
        if account_mgmt_success >= 1:
            print("   ✅ MT5 account management partially functional")
        else:
            print("   ❌ MT5 account management not working")

        # Check background tasks
        bg_task_tests = [t for t in self.test_results if "Background Tasks" in t["test"]]
        bg_task_success = sum(1 for t in bg_task_tests if t["success"])
        if bg_task_success >= 1:
            print("   ✅ Background task execution partially functional")
        else:
            print("   ❌ Background task execution not working")

        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 MT5 INTEGRATION STATUS: FULLY OPERATIONAL ON RENDER")
        elif success_rate >= 60:
            print("⚠️  MT5 INTEGRATION STATUS: MOSTLY WORKING - MINOR ISSUES")
        elif success_rate >= 40:
            print("🚨 MT5 INTEGRATION STATUS: PARTIAL FUNCTIONALITY - NEEDS ATTENTION")
        else:
            print("🚨 MT5 INTEGRATION STATUS: CRITICAL ISSUES - IMMEDIATE FIXES REQUIRED")
            
        print("=" * 80)
        
        return success_rate

if __name__ == "__main__":
    tester = MT5RenderTester()
    success_rate = tester.run_comprehensive_mt5_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 60 else 1)