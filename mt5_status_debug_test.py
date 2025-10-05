#!/usr/bin/env python3
"""
FIDUS MT5 Status Endpoint Debug Test
Specifically tests the /api/mt5/status endpoint that's returning 500 error.

Focus:
1. Test admin authentication
2. Test /api/mt5/status endpoint specifically
3. Check backend logs for specific error messages
4. Test related MT5 endpoints to identify which are working vs broken
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

class MT5StatusDebugTester:
    def __init__(self):
        # Use the correct backend URL from frontend/.env - but should be the live app URL
        self.backend_url = "https://fidus-invest.emergent.host/api"
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
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

    def make_request(self, method, endpoint, data=None, headers=None, timeout=30):
        """Make HTTP request with proper error handling"""
        url = f"{self.backend_url}{endpoint}"
        
        # Set up headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=req_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=req_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
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
            self.log_test("Admin Authentication", False, f"HTTP {status_code}")
            return False

    def test_mt5_status_endpoint(self):
        """Test the specific /api/mt5/status endpoint that's failing"""
        print("🔍 Testing /api/mt5/status endpoint...")
        
        if not self.admin_token:
            self.log_test("MT5 Status Endpoint", False, "No admin token available")
            return False

        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test the specific endpoint that's failing
        response = self.make_request("GET", "/mt5/status", headers=headers)
        
        if response:
            print(f"   Response Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_test("MT5 Status Endpoint", True, 
                                f"Success: {data.get('success')}, Bridge Health: {data.get('bridge_health', {}).get('status', 'N/A')}")
                    return True
                except json.JSONDecodeError:
                    self.log_test("MT5 Status Endpoint", False, "Invalid JSON response")
                    return False
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'No detail provided')
                    self.log_test("MT5 Status Endpoint", False, 
                                f"500 Internal Server Error: {error_detail}")
                    print(f"   Full Error Response: {error_data}")
                except json.JSONDecodeError:
                    error_text = response.text
                    self.log_test("MT5 Status Endpoint", False, 
                                f"500 Internal Server Error: {error_text}")
                return False
            else:
                try:
                    error_data = response.json()
                    self.log_test("MT5 Status Endpoint", False, 
                                f"HTTP {response.status_code}: {error_data}")
                except json.JSONDecodeError:
                    self.log_test("MT5 Status Endpoint", False, 
                                f"HTTP {response.status_code}: {response.text}")
                return False
        else:
            self.log_test("MT5 Status Endpoint", False, "No response received")
            return False

    def test_related_mt5_endpoints(self):
        """Test related MT5 endpoints to see which are working vs broken"""
        print("🔍 Testing related MT5 endpoints...")
        
        if not self.admin_token:
            self.log_test("Related MT5 Endpoints", False, "No admin token available")
            return

        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # List of MT5 endpoints to test
        mt5_endpoints = [
            ("/mt5/admin/system-status", "MT5 Admin System Status"),
            ("/mt5/brokers", "MT5 Brokers List"),
            ("/mt5/admin/accounts", "MT5 Admin Accounts"),
            ("/mt5/admin/performance/overview", "MT5 Admin Performance Overview"),
            ("/mt5/bridge/health", "MT5 Bridge Health Check"),
        ]
        
        working_endpoints = []
        broken_endpoints = []
        
        for endpoint, name in mt5_endpoints:
            print(f"   Testing {name} ({endpoint})...")
            response = self.make_request("GET", endpoint, headers=headers)
            
            if response:
                if response.status_code == 200:
                    working_endpoints.append((endpoint, name))
                    print(f"   ✅ {name}: Working (200)")
                elif response.status_code == 500:
                    broken_endpoints.append((endpoint, name, "500 Internal Server Error"))
                    try:
                        error_data = response.json()
                        print(f"   ❌ {name}: 500 Error - {error_data.get('detail', 'No detail')}")
                    except:
                        print(f"   ❌ {name}: 500 Error - {response.text}")
                else:
                    broken_endpoints.append((endpoint, name, f"HTTP {response.status_code}"))
                    print(f"   ⚠️ {name}: HTTP {response.status_code}")
            else:
                broken_endpoints.append((endpoint, name, "No response"))
                print(f"   ❌ {name}: No response")
        
        # Log summary
        self.log_test("Related MT5 Endpoints Summary", True, 
                    f"Working: {len(working_endpoints)}, Broken: {len(broken_endpoints)}")
        
        if working_endpoints:
            print(f"\n✅ Working MT5 Endpoints ({len(working_endpoints)}):")
            for endpoint, name in working_endpoints:
                print(f"   • {name}: {endpoint}")
        
        if broken_endpoints:
            print(f"\n❌ Broken MT5 Endpoints ({len(broken_endpoints)}):")
            for endpoint, name, error in broken_endpoints:
                print(f"   • {name}: {endpoint} - {error}")

    def check_backend_logs(self):
        """Check backend logs for MT5-related errors"""
        print("📋 Checking backend logs for MT5 errors...")
        
        try:
            import subprocess
            
            # Get recent backend logs
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for MT5-related errors
                mt5_errors = []
                for line in logs.split('\n'):
                    if any(keyword in line.lower() for keyword in ['mt5', 'metatrader', 'bridge']):
                        if any(error_keyword in line.lower() for error_keyword in ['error', 'failed', 'exception']):
                            mt5_errors.append(line.strip())
                
                if mt5_errors:
                    print(f"   Found {len(mt5_errors)} MT5-related errors in logs:")
                    for error in mt5_errors[-10:]:  # Show last 10 errors
                        print(f"   • {error}")
                    
                    self.log_test("Backend Logs Check", True, 
                                f"Found {len(mt5_errors)} MT5-related errors")
                else:
                    print("   No MT5-related errors found in recent logs")
                    self.log_test("Backend Logs Check", True, "No MT5-related errors in recent logs")
            else:
                self.log_test("Backend Logs Check", False, "Failed to read backend logs")
                
        except Exception as e:
            self.log_test("Backend Logs Check", False, f"Error checking logs: {str(e)}")

    def test_mt5_bridge_connectivity(self):
        """Test MT5 bridge connectivity"""
        print("🌐 Testing MT5 bridge connectivity...")
        
        # Test the VPS MT5 bridge service directly
        bridge_url = "http://217.197.163.11:8000"
        
        try:
            print(f"   Testing direct connection to {bridge_url}...")
            response = requests.get(f"{bridge_url}/health", timeout=10)
            
            if response.status_code == 200:
                self.log_test("MT5 Bridge Direct Connection", True, 
                            f"Bridge service responding at {bridge_url}")
            else:
                self.log_test("MT5 Bridge Direct Connection", False, 
                            f"Bridge returned HTTP {response.status_code}")
        except requests.exceptions.ConnectTimeout:
            self.log_test("MT5 Bridge Direct Connection", False, 
                        "Connection timeout - bridge may be blocked by firewall")
        except requests.exceptions.ConnectionError:
            self.log_test("MT5 Bridge Direct Connection", False, 
                        "Connection error - bridge service unreachable")
        except Exception as e:
            self.log_test("MT5 Bridge Direct Connection", False, 
                        f"Unexpected error: {str(e)}")

    def run_debug_test(self):
        """Run the complete debug test suite"""
        print("🚀 FIDUS MT5 Status Endpoint Debug Test")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False

        # Step 2: Test the specific failing endpoint
        self.test_mt5_status_endpoint()

        # Step 3: Test related MT5 endpoints
        self.test_related_mt5_endpoints()

        # Step 4: Check backend logs
        self.check_backend_logs()

        # Step 5: Test MT5 bridge connectivity
        self.test_mt5_bridge_connectivity()

        # Generate summary
        print("=" * 80)
        print("🎯 MT5 STATUS DEBUG TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
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
        
        # Check if MT5 status endpoint is working
        mt5_status_test = next((t for t in self.test_results if "MT5 Status Endpoint" in t["test"]), None)
        if mt5_status_test and mt5_status_test["success"]:
            print("   ✅ /api/mt5/status endpoint is working correctly")
        else:
            print("   ❌ /api/mt5/status endpoint is returning 500 error - CRITICAL ISSUE")
            if mt5_status_test:
                print(f"      Error: {mt5_status_test['error']}")

        # Check bridge connectivity
        bridge_test = next((t for t in self.test_results if "MT5 Bridge Direct Connection" in t["test"]), None)
        if bridge_test and bridge_test["success"]:
            print("   ✅ MT5 bridge service is reachable and working")
        else:
            print("   ⚠️ MT5 bridge service connectivity issues detected")
            if bridge_test:
                print(f"      Issue: {bridge_test['error']}")

        print()
        print("=" * 80)
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = MT5StatusDebugTester()
    success = tester.run_debug_test()
    
    if success:
        print("✅ All debug tests passed - MT5 status endpoint should be working")
        sys.exit(0)
    else:
        print("❌ Debug tests found issues - MT5 status endpoint needs investigation")
        sys.exit(1)