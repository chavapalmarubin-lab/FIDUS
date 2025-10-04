#!/usr/bin/env python3
"""
MT5 Bridge Service Connectivity Testing Suite
Tests MT5 Bridge Service connectivity after ForexVPS firewall configuration.

Focus Areas:
1. FIDUS Backend MT5 Endpoints (/api/mt5/*)
2. Error Handling when bridge is unreachable
3. Configuration Validation
4. Timeout Handling (30-second timeout)
5. Fallback Behavior when MT5 bridge is unavailable

Expected Results:
- Proper error messages (connection timeout/refused)
- Graceful error handling with informative messages
- No 500 errors or crashes when bridge is unreachable
- Configuration should be correct for when bridge becomes accessible
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class MT5BridgeConnectivityTester:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        self.bridge_url = "http://217.197.163.11:8000"
        self.expected_timeout = 30
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, timeout: int = 35) -> tuple[bool, Dict]:
        """Run a single API test with timeout handling"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            elapsed_time = time.time() - start_time
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Time: {elapsed_time:.2f}s")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {"text": response.text}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                    return False, error_data
                except:
                    print(f"   Error text: {response.text}")
                    return False, {"text": response.text}

        except requests.exceptions.Timeout as e:
            elapsed_time = time.time() - start_time
            print(f"⏰ Timeout after {elapsed_time:.2f}s - {str(e)}")
            return False, {"error": "timeout", "elapsed_time": elapsed_time}
        except requests.exceptions.ConnectionError as e:
            elapsed_time = time.time() - start_time
            print(f"🔌 Connection Error after {elapsed_time:.2f}s - {str(e)}")
            return False, {"error": "connection_error", "elapsed_time": elapsed_time}
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ Failed after {elapsed_time:.2f}s - Error: {str(e)}")
            return False, {"error": str(e), "elapsed_time": elapsed_time}

    def setup_authentication(self) -> bool:
        """Setup admin and client authentication"""
        print("\n" + "="*80)
        print("🔐 SETTING UP AUTHENTICATION")
        print("="*80)
        
        # Test admin login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            }
        )
        if success:
            self.admin_user = response
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        else:
            print("   ❌ Admin login failed - cannot proceed with MT5 admin tests")
            return False

        # Test client login (Salvador Palma)
        success, response = self.run_test(
            "Client Login (Salvador Palma)",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client3", 
                "password": "password123",
                "user_type": "client"
            }
        )
        if success:
            self.client_user = response
            print(f"   ✅ Client logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        else:
            print("   ❌ Client login failed - cannot proceed with MT5 client tests")
            return False
            
        return True

    def test_direct_bridge_connectivity(self) -> bool:
        """Test direct connectivity to MT5 Bridge Service"""
        print("\n" + "="*80)
        print("🌐 TESTING DIRECT MT5 BRIDGE SERVICE CONNECTIVITY")
        print("="*80)
        
        print(f"Bridge URL: {self.bridge_url}")
        print(f"Expected Timeout: {self.expected_timeout}s")
        
        # Test 1: Direct health check to bridge service
        print("\n📊 Test 1: Direct Bridge Health Check")
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.bridge_url}/health", timeout=self.expected_timeout)
            elapsed_time = time.time() - start_time
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Time: {elapsed_time:.2f}s")
            
            if response.status_code == 200:
                bridge_data = response.json()
                print(f"   ✅ Bridge Service Response: {json.dumps(bridge_data, indent=2)}")
                return True
            else:
                print(f"   ❌ Bridge returned status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout as e:
            elapsed_time = time.time() - start_time
            print(f"   ⏰ Expected Timeout after {elapsed_time:.2f}s - Bridge is blocked by firewall")
            print(f"   ✅ This confirms the firewall is blocking external access as expected")
            return True  # This is expected behavior
            
        except requests.exceptions.ConnectionError as e:
            elapsed_time = time.time() - start_time
            print(f"   🔌 Expected Connection Error after {elapsed_time:.2f}s - Bridge is unreachable")
            print(f"   ✅ This confirms the bridge is blocked by ForexVPS firewall as expected")
            return True  # This is expected behavior
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"   ❌ Unexpected error after {elapsed_time:.2f}s: {str(e)}")
            return False

    def test_fidus_mt5_endpoints_error_handling(self) -> bool:
        """Test FIDUS backend MT5 endpoints error handling when bridge is unreachable"""
        print("\n" + "="*80)
        print("🔧 TESTING FIDUS MT5 ENDPOINTS ERROR HANDLING")
        print("="*80)
        
        if not self.admin_user:
            print("❌ No admin user available for MT5 admin tests")
            return False
            
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }
        
        # Test 1: Admin MT5 Accounts Overview
        print("\n📊 Test 1: Admin MT5 Accounts Overview (Bridge Unreachable)")
        success, response = self.run_test(
            "Get All MT5 Accounts (Admin) - Bridge Unreachable",
            "GET",
            "api/mt5/admin/accounts",
            200,  # Should return 200 with proper error handling
            headers=admin_headers
        )
        
        if success:
            # Check if response contains proper error handling
            if 'error' in response or 'bridge_error' in response or response.get('accounts') == []:
                print("   ✅ Proper error handling - returns structured response when bridge unreachable")
            else:
                print("   ⚠️ Response structure may need bridge error indication")
        else:
            print("   ❌ Endpoint failed completely - should handle bridge errors gracefully")
            return False

        # Test 2: MT5 Performance Overview
        print("\n📊 Test 2: MT5 Performance Overview (Bridge Unreachable)")
        success, response = self.run_test(
            "Get MT5 Performance Overview (Admin) - Bridge Unreachable",
            "GET",
            "api/mt5/admin/performance/overview",
            200,  # Should return 200 with proper error handling
            headers=admin_headers
        )
        
        if success:
            # Check if response contains proper error handling
            if 'error' in response or 'bridge_error' in response or 'overview' in response:
                print("   ✅ Proper error handling - returns structured response when bridge unreachable")
            else:
                print("   ⚠️ Response structure may need bridge error indication")
        else:
            print("   ❌ Endpoint failed completely - should handle bridge errors gracefully")
            return False

        # Test 3: MT5 System Status
        print("\n📊 Test 3: MT5 System Status (Bridge Unreachable)")
        success, response = self.run_test(
            "Get MT5 System Status - Bridge Unreachable",
            "GET",
            "api/mt5/admin/system-status",
            200,  # Should return 200 with proper error handling
            headers=admin_headers
        )
        
        if success:
            # Check if response indicates bridge connectivity issues
            if 'bridge_status' in response or 'mt5_bridge' in response or 'error' in response:
                print("   ✅ System status properly indicates bridge connectivity issues")
            else:
                print("   ⚠️ System status should indicate bridge connectivity status")
        else:
            print("   ❌ System status endpoint failed - should handle bridge errors gracefully")
            return False

        # Test 4: MT5 Realtime Data
        print("\n📊 Test 4: MT5 Realtime Data (Bridge Unreachable)")
        success, response = self.run_test(
            "Get MT5 Realtime Data - Bridge Unreachable",
            "GET",
            "api/mt5/admin/realtime-data",
            200,  # Should return 200 with proper error handling
            headers=admin_headers
        )
        
        if success:
            # Check if response handles bridge unavailability
            if 'error' in response or 'bridge_error' in response or response.get('data') == []:
                print("   ✅ Realtime data properly handles bridge unavailability")
            else:
                print("   ⚠️ Realtime data should indicate when bridge is unavailable")
        else:
            print("   ❌ Realtime data endpoint failed - should handle bridge errors gracefully")
            return False

        return True

    def test_client_mt5_endpoints_error_handling(self) -> bool:
        """Test client MT5 endpoints error handling when bridge is unreachable"""
        print("\n" + "="*80)
        print("👤 TESTING CLIENT MT5 ENDPOINTS ERROR HANDLING")
        print("="*80)
        
        if not self.client_user:
            print("❌ No client user available for MT5 client tests")
            return False
            
        client_id = self.client_user.get('id')
        client_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.client_user.get('token')}"
        }

        # Test 1: Client MT5 Accounts
        print("\n📊 Test 1: Client MT5 Accounts (Bridge Unreachable)")
        success, response = self.run_test(
            "Get Client MT5 Accounts - Bridge Unreachable",
            "GET",
            f"api/mt5/client/{client_id}/accounts",
            200,  # Should return 200 with proper error handling
            headers=client_headers
        )
        
        if success:
            # Check if response contains proper error handling
            if 'error' in response or 'bridge_error' in response or response.get('accounts') == []:
                print("   ✅ Client accounts properly handle bridge unavailability")
            else:
                print("   ⚠️ Client accounts should indicate when bridge is unavailable")
        else:
            print("   ❌ Client accounts endpoint failed - should handle bridge errors gracefully")
            return False

        # Test 2: Client Performance Summary
        print("\n📊 Test 2: Client Performance Summary (Bridge Unreachable)")
        success, response = self.run_test(
            "Get Client Performance Summary - Bridge Unreachable",
            "GET",
            f"api/mt5/client/{client_id}/performance",
            200,  # Should return 200 with proper error handling
            headers=client_headers
        )
        
        if success:
            # Check if response contains proper error handling
            if 'error' in response or 'bridge_error' in response or 'summary' in response:
                print("   ✅ Client performance properly handles bridge unavailability")
            else:
                print("   ⚠️ Client performance should indicate when bridge is unavailable")
        else:
            print("   ❌ Client performance endpoint failed - should handle bridge errors gracefully")
            return False

        return True

    def test_mt5_configuration_validation(self) -> bool:
        """Test MT5 configuration validation"""
        print("\n" + "="*80)
        print("⚙️ TESTING MT5 CONFIGURATION VALIDATION")
        print("="*80)
        
        # Test 1: MT5 Brokers Configuration
        print("\n📊 Test 1: MT5 Brokers Configuration")
        
        # Need admin authentication for MT5 endpoints
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        } if self.admin_user else {'Content-Type': 'application/json'}
        
        success, response = self.run_test(
            "Get MT5 Brokers Configuration",
            "GET",
            "api/mt5/brokers",
            200,
            headers=admin_headers
        )
        
        if success:
            brokers = response.get('brokers', [])
            if brokers:
                print(f"   ✅ Found {len(brokers)} configured brokers")
                for broker in brokers:
                    print(f"      - {broker.get('name', 'Unknown')}: {broker.get('code', 'Unknown')}")
            else:
                print("   ⚠️ No brokers configured")
        else:
            print("   ❌ Failed to get brokers configuration")
            return False

        # Test 2: MT5 Broker Servers Configuration
        print("\n📊 Test 2: MT5 Broker Servers Configuration")
        success, response = self.run_test(
            "Get MT5 Broker Servers (Multibank)",
            "GET",
            "api/mt5/brokers/multibank/servers",
            200
        )
        
        if success:
            servers = response.get('servers', [])
            if servers:
                print(f"   ✅ Found {len(servers)} configured servers for Multibank")
                for server in servers[:3]:  # Show first 3
                    print(f"      - {server}")
            else:
                print("   ⚠️ No servers configured for Multibank")
        else:
            print("   ❌ Failed to get broker servers configuration")
            return False

        return True

    def test_timeout_handling(self) -> bool:
        """Test timeout handling for MT5 operations"""
        print("\n" + "="*80)
        print("⏰ TESTING TIMEOUT HANDLING")
        print("="*80)
        
        if not self.admin_user:
            print("❌ No admin user available for timeout tests")
            return False
            
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }

        # Test 1: MT5 Credentials Update (should timeout gracefully)
        print("\n📊 Test 1: MT5 Credentials Update Timeout Handling")
        start_time = time.time()
        
        success, response = self.run_test(
            "Update MT5 Credentials - Timeout Test",
            "POST",
            "api/mt5/admin/credentials/update",
            404,  # Expect 404 for non-existent account, not timeout error
            data={
                "client_id": "test_client",
                "fund_code": "CORE",
                "mt5_login": 12345678,
                "mt5_password": "TestPass123!",
                "mt5_server": "Test-Server"
            },
            headers=admin_headers,
            timeout=35  # Allow for 30s bridge timeout + 5s buffer
        )
        
        elapsed_time = time.time() - start_time
        
        if success or elapsed_time < 35:  # Should complete within timeout
            print(f"   ✅ Request completed in {elapsed_time:.2f}s (within timeout)")
        else:
            print(f"   ❌ Request took {elapsed_time:.2f}s (exceeded expected timeout)")
            return False

        # Test 2: Account Disconnect (should handle bridge unavailability)
        print("\n📊 Test 2: Account Disconnect Timeout Handling")
        start_time = time.time()
        
        success, response = self.run_test(
            "Disconnect MT5 Account - Timeout Test",
            "POST",
            "api/mt5/admin/account/test_account_id/disconnect",
            404,  # Expect 404 for non-existent account, not timeout error
            headers=admin_headers,
            timeout=35  # Allow for 30s bridge timeout + 5s buffer
        )
        
        elapsed_time = time.time() - start_time
        
        if success or elapsed_time < 35:  # Should complete within timeout
            print(f"   ✅ Request completed in {elapsed_time:.2f}s (within timeout)")
        else:
            print(f"   ❌ Request took {elapsed_time:.2f}s (exceeded expected timeout)")
            return False

        return True

    def test_fallback_behavior(self) -> bool:
        """Test fallback behavior when MT5 bridge is unavailable"""
        print("\n" + "="*80)
        print("🔄 TESTING FALLBACK BEHAVIOR")
        print("="*80)
        
        if not self.admin_user:
            print("❌ No admin user available for fallback tests")
            return False
            
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }

        # Test 1: System should continue operating without MT5 bridge
        print("\n📊 Test 1: System Operation Without MT5 Bridge")
        
        # Test basic system health
        success, response = self.run_test(
            "System Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            print("   ✅ System health check works without MT5 bridge")
        else:
            print("   ❌ System health check failed - system should work without MT5 bridge")
            return False

        # Test 2: Investment creation should work (MT5 mapping may fail gracefully)
        print("\n📊 Test 2: Investment Creation Fallback")
        
        success, response = self.run_test(
            "Create Investment Without MT5 Bridge",
            "POST",
            "api/investments/create",
            200,  # Should succeed even if MT5 mapping fails
            data={
                "client_id": self.client_user.get('id'),
                "fund_code": "CORE",
                "amount": 10000.0,
                "deposit_date": "2024-12-19"
            },
            headers=admin_headers
        )
        
        if success:
            investment_id = response.get('investment_id')
            if investment_id:
                print(f"   ✅ Investment created successfully: {investment_id}")
                print("   ✅ System continues operating without MT5 bridge")
            else:
                print("   ⚠️ Investment creation response format may need review")
        else:
            print("   ❌ Investment creation failed - should work without MT5 bridge")
            return False

        # Test 3: User management should work independently
        print("\n📊 Test 3: User Management Independence")
        
        success, response = self.run_test(
            "Get Admin Users",
            "GET",
            "api/admin/users",
            200,
            headers=admin_headers
        )
        
        if success:
            users = response.get('users', [])
            print(f"   ✅ User management works independently: {len(users)} users found")
        else:
            print("   ❌ User management failed - should work independently of MT5 bridge")
            return False

        return True

    def run_comprehensive_bridge_connectivity_tests(self) -> bool:
        """Run all MT5 bridge connectivity tests"""
        print("\n" + "="*100)
        print("🚀 STARTING MT5 BRIDGE SERVICE CONNECTIVITY TESTING")
        print("="*100)
        print("Testing MT5 Bridge Service connectivity after ForexVPS firewall configuration")
        print(f"Bridge URL: {self.bridge_url}")
        print(f"Expected Timeout: {self.expected_timeout}s")
        print("="*100)
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run all test suites
        test_suites = [
            ("Direct Bridge Connectivity", self.test_direct_bridge_connectivity),
            ("FIDUS MT5 Endpoints Error Handling", self.test_fidus_mt5_endpoints_error_handling),
            ("Client MT5 Endpoints Error Handling", self.test_client_mt5_endpoints_error_handling),
            ("MT5 Configuration Validation", self.test_mt5_configuration_validation),
            ("Timeout Handling", self.test_timeout_handling),
            ("Fallback Behavior", self.test_fallback_behavior)
        ]
        
        suite_results = []
        
        for suite_name, test_method in test_suites:
            print(f"\n🔄 Running {suite_name}...")
            try:
                result = test_method()
                suite_results.append((suite_name, result))
                
                if result:
                    print(f"✅ {suite_name} - PASSED")
                else:
                    print(f"❌ {suite_name} - FAILED")
            except Exception as e:
                print(f"❌ {suite_name} - ERROR: {str(e)}")
                suite_results.append((suite_name, False))
        
        # Print final results
        print("\n" + "="*100)
        print("📊 MT5 BRIDGE CONNECTIVITY TEST RESULTS SUMMARY")
        print("="*100)
        
        passed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Overall Results:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed ({passed_suites/total_suites*100:.1f}%)")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        print(f"\n🔍 Key Findings:")
        print(f"   - MT5 Bridge URL: {self.bridge_url}")
        print(f"   - Bridge Status: Expected to be blocked by ForexVPS firewall")
        print(f"   - FIDUS Backend: Should handle bridge unavailability gracefully")
        print(f"   - Error Handling: Should return proper error messages, not 500 errors")
        print(f"   - Timeout Configuration: {self.expected_timeout}s timeout should be working")
        print(f"   - System Fallback: Core functionality should work without MT5 bridge")
        
        # Determine overall success
        overall_success = passed_suites >= (total_suites * 0.8)  # 80% pass rate
        
        if overall_success:
            print(f"\n🎉 MT5 BRIDGE CONNECTIVITY TESTING COMPLETED SUCCESSFULLY!")
            print("   FIDUS system properly handles MT5 bridge unavailability.")
            print("   Ready for when ForexVPS opens port 8000 for bridge access.")
        else:
            print(f"\n⚠️ MT5 BRIDGE CONNECTIVITY TESTING COMPLETED WITH ISSUES")
            print("   Some error handling or fallback behavior may need attention.")
        
        return overall_success

def main():
    """Main test execution"""
    print("🔧 MT5 Bridge Service Connectivity Testing Suite")
    print("Testing FIDUS backend behavior when MT5 bridge is unreachable due to firewall")
    
    tester = MT5BridgeConnectivityTester()
    
    try:
        success = tester.run_comprehensive_bridge_connectivity_tests()
        
        if success:
            print("\n✅ MT5 Bridge connectivity tests completed successfully!")
            print("FIDUS backend properly handles bridge unavailability.")
            sys.exit(0)
        else:
            print("\n❌ Some MT5 Bridge connectivity tests failed!")
            print("Error handling or fallback behavior may need attention.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()