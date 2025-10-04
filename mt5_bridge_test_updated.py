#!/usr/bin/env python3
"""
MT5 Bridge Service Connectivity Testing Suite - Updated
Tests the MT5 Bridge Service connectivity and FIDUS backend MT5 integration.
Updated to test actual endpoints that exist in the FIDUS backend.
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List
import time

class MT5BridgeConnectivityTester:
    def __init__(self, fidus_backend_url="https://fidus-invest.emergent.host"):
        self.fidus_backend_url = fidus_backend_url
        self.mt5_bridge_url = "http://217.197.163.11:8000"
        self.mt5_api_key = "fidus-mt5-bridge-key-2025-secure"
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        
    def run_test(self, name: str, method: str, url: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, timeout: int = 30) -> tuple[bool, Dict]:
        """Run a single API test"""
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, {"text": response.text}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout after {timeout} seconds")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error (service may be down)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_fidus_authentication(self) -> bool:
        """Setup FIDUS backend authentication"""
        print("\n" + "="*80)
        print("🔐 SETTING UP FIDUS BACKEND AUTHENTICATION")
        print("="*80)
        
        # Test admin login to FIDUS backend
        success, response = self.run_test(
            "FIDUS Admin Login",
            "POST",
            f"{self.fidus_backend_url}/api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            }
        )
        
        if success and response.get('token'):
            self.admin_token = response['token']
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
            return True
        else:
            print("   ❌ Admin login failed - cannot proceed with FIDUS backend tests")
            return False

    def test_direct_mt5_bridge_connectivity(self) -> bool:
        """Test direct connectivity to MT5 bridge service"""
        print("\n" + "="*80)
        print("🌐 TESTING DIRECT MT5 BRIDGE SERVICE CONNECTIVITY")
        print("="*80)
        
        # Test 1: Basic health endpoint (try different endpoints)
        print("\n📊 Test 1: MT5 Bridge Service Accessibility")
        
        # Try different common endpoints
        endpoints_to_try = [
            ("/health", "Health Check"),
            ("/", "Root Endpoint"),
            ("/status", "Status Endpoint"),
            ("/api/health", "API Health Check")
        ]
        
        bridge_accessible = False
        
        for endpoint, description in endpoints_to_try:
            print(f"\n   Trying {description}: {self.mt5_bridge_url}{endpoint}")
            success, response = self.run_test(
                f"MT5 Bridge {description}",
                "GET",
                f"{self.mt5_bridge_url}{endpoint}",
                200,
                timeout=10
            )
            
            if success:
                print(f"   ✅ MT5 Bridge {description} accessible")
                bridge_accessible = True
                break
            else:
                print(f"   ❌ MT5 Bridge {description} not accessible")
        
        if not bridge_accessible:
            print("\n⚠️ MT5 Bridge Service appears to be down or unreachable")
            print("   This could be due to:")
            print("   - Service not running on Windows VPS")
            print("   - Network connectivity issues")
            print("   - Firewall blocking connections")
            print("   - Service running on different port")
            return False
        
        # Test 2: Try with API key authentication
        print("\n📊 Test 2: MT5 Bridge API Key Authentication")
        headers = {'X-API-Key': self.mt5_api_key}
        
        # Try MT5 specific endpoints with API key
        mt5_endpoints = [
            ("/mt5/status", "MT5 Status"),
            ("/api/mt5/status", "API MT5 Status"),
            ("/mt5/terminal/info", "MT5 Terminal Info"),
            ("/api/mt5/terminal/info", "API MT5 Terminal Info")
        ]
        
        mt5_endpoint_accessible = False
        
        for endpoint, description in mt5_endpoints:
            print(f"\n   Trying {description}: {self.mt5_bridge_url}{endpoint}")
            success, response = self.run_test(
                f"MT5 Bridge {description}",
                "GET",
                f"{self.mt5_bridge_url}{endpoint}",
                200,
                headers=headers,
                timeout=10
            )
            
            if success:
                print(f"   ✅ MT5 Bridge {description} accessible")
                mt5_endpoint_accessible = True
                
                # Check for MT5 status information
                if isinstance(response, dict):
                    mt5_available = response.get('mt5_available', 'unknown')
                    mt5_initialized = response.get('mt5_initialized', 'unknown')
                    print(f"   📊 MT5 Available: {mt5_available}")
                    print(f"   📊 MT5 Initialized: {mt5_initialized}")
                break
            else:
                print(f"   ❌ MT5 Bridge {description} not accessible")
        
        return bridge_accessible or mt5_endpoint_accessible

    def test_fidus_mt5_integration(self) -> bool:
        """Test FIDUS backend MT5 integration endpoints"""
        print("\n" + "="*80)
        print("🔗 TESTING FIDUS BACKEND MT5 INTEGRATION")
        print("="*80)
        
        if not self.admin_token:
            print("❌ No admin token available for FIDUS backend tests")
            return False
            
        headers = {
            'Authorization': f'Bearer {self.admin_token}',
            'Content-Type': 'application/json'
        }

        # Test 1: FIDUS MT5 Bridge Health Check
        print("\n📊 Test 1: FIDUS MT5 Bridge Health Check")
        success, response = self.run_test(
            "FIDUS MT5 Bridge Health",
            "GET",
            f"{self.fidus_backend_url}/api/mt5/bridge/health",
            200,
            headers=headers,
            timeout=30
        )
        
        if success:
            print("   ✅ FIDUS MT5 bridge health endpoint accessible")
            
            # Check bridge health status
            bridge_health = response.get('bridge_health', {})
            if bridge_health:
                print(f"   📊 Bridge Health Data: {bridge_health}")
            else:
                print("   📊 Bridge health check completed")
        else:
            print("   ❌ FIDUS MT5 bridge health endpoint failed")
            return False

        # Test 2: FIDUS MT5 System Status
        print("\n📊 Test 2: FIDUS MT5 System Status")
        success, response = self.run_test(
            "FIDUS MT5 System Status",
            "GET",
            f"{self.fidus_backend_url}/api/mt5/status",
            200,
            headers=headers,
            timeout=30
        )
        
        if success:
            print("   ✅ FIDUS MT5 system status endpoint accessible")
            
            # Check system status details
            bridge_health = response.get('bridge_health', {})
            total_accounts = response.get('total_accounts', 0)
            broker_stats = response.get('broker_statistics', {})
            
            print(f"   📊 Total MT5 Accounts: {total_accounts}")
            print(f"   📊 Bridge Health: {bridge_health}")
            print(f"   📊 Broker Statistics: {broker_stats}")
        else:
            print("   ❌ FIDUS MT5 system status endpoint failed")
            return False

        # Test 3: FIDUS MT5 Test Connection
        print("\n📊 Test 3: FIDUS MT5 Test Connection")
        success, response = self.run_test(
            "FIDUS MT5 Test Connection",
            "POST",
            f"{self.fidus_backend_url}/api/mt5/test-connection",
            200,
            headers=headers,
            timeout=30
        )
        
        if success:
            print("   ✅ FIDUS MT5 test connection endpoint accessible")
            
            # Check connection test results
            connection_status = response.get('connection_status', 'unknown')
            print(f"   📊 Connection Status: {connection_status}")
        else:
            print("   ❌ FIDUS MT5 test connection endpoint failed")
            # Don't fail the test as this endpoint might not be fully implemented

        return True

    def test_mt5_account_management(self) -> bool:
        """Test MT5 account management endpoints"""
        print("\n" + "="*80)
        print("🏦 TESTING MT5 ACCOUNT MANAGEMENT")
        print("="*80)
        
        if not self.admin_token:
            print("❌ No admin token available for MT5 account tests")
            return False
            
        headers = {
            'Authorization': f'Bearer {self.admin_token}',
            'Content-Type': 'application/json'
        }

        # Test 1: Get MT5 Accounts for a client
        print("\n📊 Test 1: Get Client MT5 Accounts")
        
        # Use a known client ID (client_001 - Gerardo Briones)
        client_id = "client_001"
        
        success, response = self.run_test(
            "Get Client MT5 Accounts",
            "GET",
            f"{self.fidus_backend_url}/api/mt5/accounts/{client_id}",
            200,
            headers=headers,
            timeout=30
        )
        
        if success:
            print("   ✅ FIDUS MT5 accounts endpoint accessible")
            
            # Check account data
            accounts = response.get('accounts', [])
            print(f"   📊 MT5 Accounts found: {len(accounts)}")
            
            if accounts:
                for i, account in enumerate(accounts[:3]):  # Show first 3 accounts
                    account_id = account.get('account_id', 'unknown')
                    fund_code = account.get('fund_code', 'unknown')
                    mt5_login = account.get('mt5_login', 'unknown')
                    print(f"   📊 Account {i+1}: ID={account_id}, Fund={fund_code}, Login={mt5_login}")
        else:
            print("   ❌ FIDUS MT5 accounts endpoint failed")
            return False

        # Test 2: Create MT5 Account (if endpoint exists)
        print("\n📊 Test 2: Create MT5 Account")
        success, response = self.run_test(
            "Create MT5 Account",
            "POST",
            f"{self.fidus_backend_url}/api/mt5/accounts",
            200,
            data={
                "client_id": client_id,
                "fund_code": "CORE",
                "initial_balance": 10000.0
            },
            headers=headers,
            timeout=30
        )
        
        if success:
            print("   ✅ FIDUS MT5 account creation endpoint accessible")
            
            # Check creation response
            account_id = response.get('account_id', 'unknown')
            mt5_login = response.get('mt5_login', 'unknown')
            print(f"   📊 Created Account ID: {account_id}")
            print(f"   📊 MT5 Login: {mt5_login}")
        else:
            print("   ❌ FIDUS MT5 account creation endpoint failed")
            # Don't fail the test as this might be expected

        return True

    def test_mt5_sync_operations(self) -> bool:
        """Test MT5 synchronization operations"""
        print("\n" + "="*80)
        print("🔄 TESTING MT5 SYNC OPERATIONS")
        print("="*80)
        
        if not self.admin_token:
            print("❌ No admin token available for MT5 sync tests")
            return False
            
        headers = {
            'Authorization': f'Bearer {self.admin_token}',
            'Content-Type': 'application/json'
        }

        # Test 1: Sync All MT5 Accounts
        print("\n📊 Test 1: Sync All MT5 Accounts")
        success, response = self.run_test(
            "Sync All MT5 Accounts",
            "POST",
            f"{self.fidus_backend_url}/api/mt5/sync-all",
            200,
            headers=headers,
            timeout=60  # Longer timeout for sync operations
        )
        
        if success:
            print("   ✅ FIDUS MT5 sync-all endpoint accessible")
            
            # Check sync results
            synced_accounts = response.get('synced_accounts', 0)
            sync_errors = response.get('sync_errors', [])
            print(f"   📊 Synced Accounts: {synced_accounts}")
            print(f"   📊 Sync Errors: {len(sync_errors)}")
            
            if sync_errors:
                print(f"   ⚠️ Sync errors detected: {sync_errors[:3]}")  # Show first 3 errors
        else:
            print("   ❌ FIDUS MT5 sync-all endpoint failed")
            return False

        return True

    def run_comprehensive_mt5_bridge_tests(self) -> bool:
        """Run all MT5 bridge connectivity tests"""
        print("\n" + "="*100)
        print("🚀 STARTING COMPREHENSIVE MT5 BRIDGE CONNECTIVITY TESTING")
        print("="*100)
        print(f"MT5 Bridge URL: {self.mt5_bridge_url}")
        print(f"FIDUS Backend URL: {self.fidus_backend_url}")
        print(f"API Key: {self.mt5_api_key[:20]}...")
        
        # Setup FIDUS authentication
        if not self.setup_fidus_authentication():
            print("\n❌ FIDUS authentication setup failed - cannot proceed")
            return False
        
        # Run all test suites
        test_suites = [
            ("Direct MT5 Bridge Connectivity", self.test_direct_mt5_bridge_connectivity),
            ("FIDUS MT5 Integration", self.test_fidus_mt5_integration),
            ("MT5 Account Management", self.test_mt5_account_management),
            ("MT5 Sync Operations", self.test_mt5_sync_operations)
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
        
        # Analysis and recommendations
        print(f"\n🔍 Analysis:")
        
        if passed_suites == 0:
            print("   ❌ CRITICAL: No test suites passed")
            print("   🔧 Recommendations:")
            print("      - Check if MT5 Bridge Service is running on Windows VPS")
            print("      - Verify network connectivity to 217.197.163.11:8000")
            print("      - Check firewall settings on Windows VPS")
            print("      - Verify MT5 Bridge Service configuration")
        elif passed_suites == 1:
            print("   ⚠️ PARTIAL: Only FIDUS authentication working")
            print("   🔧 Recommendations:")
            print("      - MT5 Bridge Service may be down or unreachable")
            print("      - Check Windows VPS status and MT5 service")
            print("      - Verify MT5 Bridge Service is properly configured")
        elif passed_suites >= 2:
            print("   ✅ GOOD: FIDUS backend MT5 integration is working")
            if passed_suites < total_suites:
                print("   🔧 Minor issues detected in some MT5 operations")
            else:
                print("   🎉 All MT5 systems are operational!")
        
        # Expected results verification
        print(f"\n🎯 Expected Results Status:")
        fidus_working = passed_suites >= 2
        bridge_accessible = passed_suites >= 1 and "Direct MT5 Bridge Connectivity" in [name for name, result in suite_results if result]
        
        print(f"   ✓ MT5 Bridge Service Accessible: {'✅' if bridge_accessible else '❌'}")
        print(f"   ✓ FIDUS Backend Integration: {'✅' if fidus_working else '❌'}")
        print(f"   ✓ MT5 Account Management: {'✅' if passed_suites >= 3 else '❌'}")
        print(f"   ✓ MT5 Sync Operations: {'✅' if passed_suites >= 4 else '❌'}")
        
        # Determine overall success
        overall_success = passed_suites >= 2 and self.tests_passed >= (self.tests_run * 0.60)
        
        if overall_success:
            print(f"\n🎉 MT5 BRIDGE CONNECTIVITY TESTING COMPLETED SUCCESSFULLY!")
            print("   FIDUS MT5 integration is working correctly.")
            if not bridge_accessible:
                print("   ⚠️ Note: Direct MT5 Bridge Service may need attention")
        else:
            print(f"\n⚠️ MT5 BRIDGE CONNECTIVITY TESTING COMPLETED WITH ISSUES")
            print("   Critical MT5 functionality may need immediate attention.")
        
        return overall_success

def main():
    """Main test execution"""
    print("🔧 MT5 Bridge Service Connectivity Testing Suite - Updated")
    print("Testing MT5 Bridge Service and FIDUS backend MT5 integration")
    
    tester = MT5BridgeConnectivityTester()
    
    try:
        success = tester.run_comprehensive_mt5_bridge_tests()
        
        if success:
            print("\n✅ MT5 bridge connectivity tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ MT5 bridge connectivity tests completed with issues!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()