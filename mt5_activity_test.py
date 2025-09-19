#!/usr/bin/env python3
"""
MT5 Account Activity API Testing Suite
Critical test for MT5 activity API as requested in review.

PRIORITY TESTING:
1. GET /api/mt5/admin/account/mt5_client_003_BALANCE_dootechnology_34c231f6/activity
2. Verify 6 trading activities (1 deposit + 5 trades)
3. Check response structure and data format
4. Debug database query for mt5_activity collection
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

class MT5ActivityTester:
    def __init__(self, base_url="https://wealth-portal-17.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.target_account_id = "mt5_client_003_BALANCE_dootechnology_34c231f6"
        self.admin_token = None
        self.client_token = None
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

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
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_authentication(self) -> bool:
        """Setup admin authentication for MT5 API access"""
        print("\n" + "="*80)
        print("🔐 SETTING UP AUTHENTICATION")
        print("="*80)
        
        # Test admin login
        success, response = self.run_test(
            "Admin Login for MT5 Access",
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
            self.admin_token = response.get('token')
            if self.admin_token:
                print(f"   ✅ Admin authenticated successfully")
                print(f"   🔑 Token obtained: {self.admin_token[:20]}...")
                return True
            else:
                print(f"   ❌ No token received in admin login response")
                return False
        else:
            print(f"   ❌ Admin login failed")
            return False

    def get_auth_headers(self) -> Dict:
        """Get authentication headers with JWT token"""
        if self.admin_token:
            return {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.admin_token}'
            }
        else:
            return {'Content-Type': 'application/json'}

    def test_priority_1_mt5_activity_api(self) -> bool:
        """PRIORITY 1: Test MT5 Activity API Endpoint for specific account"""
        print("\n" + "="*80)
        print("🎯 PRIORITY 1: TESTING MT5 ACTIVITY API ENDPOINT")
        print("="*80)
        print(f"Target Account ID: {self.target_account_id}")
        
        # Test the exact endpoint mentioned in the review
        success, response = self.run_test(
            f"MT5 Activity API - Target Account",
            "GET",
            f"api/mt5/admin/account/{self.target_account_id}/activity",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            # Verify response structure
            required_keys = ['success', 'account_id', 'activity', 'total_activities']
            missing_keys = [key for key in required_keys if key not in response]
            
            if missing_keys:
                print(f"   ❌ Missing required keys: {missing_keys}")
                return False
            else:
                print(f"   ✅ All required response keys present")
            
            # Check account ID matches
            returned_account_id = response.get('account_id')
            if returned_account_id == self.target_account_id:
                print(f"   ✅ Account ID matches: {returned_account_id}")
            else:
                print(f"   ❌ Account ID mismatch: Expected {self.target_account_id}, got {returned_account_id}")
                return False
            
            # Check activity data
            activities = response.get('activity', [])
            total_activities = response.get('total_activities', 0)
            
            print(f"   📊 Total activities found: {total_activities}")
            print(f"   📊 Activities array length: {len(activities)}")
            
            # Expected: 6 activities (1 deposit + 5 trades)
            expected_activities = 6
            if total_activities == expected_activities:
                print(f"   ✅ Expected activity count found: {total_activities}")
            else:
                print(f"   ❌ Activity count mismatch: Expected {expected_activities}, got {total_activities}")
                if total_activities == 0:
                    print(f"   🚨 CRITICAL: No activities found - this matches the user-reported issue!")
                    print(f"   🔍 This confirms the frontend 'No activity recorded' problem")
                return False
            
            # Analyze activity structure if activities exist
            if activities:
                print(f"\n   📋 Analyzing activity structure:")
                activity = activities[0]  # Check first activity
                
                # Expected activity fields
                expected_fields = ['activity_id', 'type', 'amount', 'description', 'timestamp', 'status']
                trade_fields = ['symbol', 'trade_type', 'volume', 'opening_price', 'current_price', 'profit_loss']
                
                for field in expected_fields:
                    if field in activity:
                        print(f"   ✅ Activity has {field}: {activity.get(field)}")
                    else:
                        print(f"   ❌ Activity missing {field}")
                
                # Check for trade-specific fields if it's a trade
                if activity.get('type') == 'trade':
                    for field in trade_fields:
                        if field in activity:
                            print(f"   ✅ Trade has {field}: {activity.get(field)}")
                        else:
                            print(f"   ❌ Trade missing {field}")
                
                # Count activity types
                deposits = sum(1 for a in activities if a.get('type') == 'deposit')
                trades = sum(1 for a in activities if a.get('type') == 'trade')
                
                print(f"   📊 Activity breakdown: {deposits} deposits, {trades} trades")
                
                # Expected: 1 deposit + 5 trades
                if deposits == 1 and trades == 5:
                    print(f"   ✅ Expected activity breakdown found")
                else:
                    print(f"   ❌ Activity breakdown mismatch: Expected 1 deposit + 5 trades")
                    return False
                
                # Check for expected trading symbols
                expected_symbols = ['EURUSD', 'USDCHF', 'XAUUSD']
                found_symbols = set()
                
                for activity in activities:
                    if activity.get('type') == 'trade' and activity.get('symbol'):
                        found_symbols.add(activity.get('symbol'))
                
                print(f"   📊 Trading symbols found: {list(found_symbols)}")
                
                # Check if we have the expected symbols
                matching_symbols = found_symbols.intersection(expected_symbols)
                if matching_symbols:
                    print(f"   ✅ Expected trading symbols found: {list(matching_symbols)}")
                else:
                    print(f"   ❌ No expected trading symbols found (EURUSD, USDCHF, XAUUSD)")
                    return False
            else:
                print(f"   🚨 CRITICAL: Activities array is empty!")
                print(f"   🔍 This confirms the user-reported 'No activity recorded' issue")
                return False
                
        else:
            print(f"   ❌ Failed to get MT5 activity for target account")
            return False
        
        return True

    def test_priority_2_database_query_debug(self) -> bool:
        """PRIORITY 2: Debug Database Query for mt5_activity collection"""
        print("\n" + "="*80)
        print("🔍 PRIORITY 2: DEBUG DATABASE QUERY")
        print("="*80)
        
        # Test 1: Check if any MT5 accounts exist
        print("\n📊 Test 1: Check MT5 Accounts Existence")
        success, response = self.run_test(
            "Get All MT5 Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   📊 Total MT5 accounts found: {len(accounts)}")
            
            # Look for our target account
            target_found = False
            for account in accounts:
                account_id = account.get('account_id')
                if account_id == self.target_account_id:
                    target_found = True
                    print(f"   ✅ Target account found: {account_id}")
                    print(f"   📊 Client ID: {account.get('client_id')}")
                    print(f"   📊 Fund Code: {account.get('fund_code')}")
                    print(f"   📊 MT5 Login: {account.get('mt5_login')}")
                    print(f"   📊 Allocated: ${account.get('total_allocated', 0):,.2f}")
                    break
                else:
                    print(f"   📋 Found account: {account_id}")
            
            if not target_found:
                print(f"   ❌ Target account {self.target_account_id} NOT FOUND in MT5 accounts")
                print(f"   🔍 This could be why no activity is returned")
                return False
            else:
                print(f"   ✅ Target account exists in MT5 accounts")
        else:
            print(f"   ❌ Failed to get MT5 accounts list")
            return False
        
        # Test 2: Check client_003 specifically (Salvador Palma)
        print("\n📊 Test 2: Check Client_003 (Salvador Palma) Data")
        success, response = self.run_test(
            "Get Client_003 MT5 Accounts",
            "GET",
            "api/mt5/client/client_003/accounts",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   📊 Client_003 MT5 accounts: {len(accounts)}")
            
            for account in accounts:
                account_id = account.get('account_id')
                fund_code = account.get('fund_code')
                mt5_login = account.get('mt5_login')
                allocated = account.get('total_allocated', 0)
                
                print(f"   📋 Account: {account_id}")
                print(f"      Fund: {fund_code}, Login: {mt5_login}, Allocated: ${allocated:,.2f}")
                
                if account_id == self.target_account_id:
                    print(f"   ✅ Found target account in client_003 accounts")
        else:
            print(f"   ❌ Failed to get client_003 MT5 accounts")
            return False
        
        # Test 3: Test activity endpoint with different account IDs
        print("\n📊 Test 3: Test Activity Endpoint with Different Accounts")
        
        # Get all accounts and test their activity endpoints
        success, response = self.run_test(
            "Get All Accounts for Activity Testing",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            accounts = response.get('accounts', [])
            
            for account in accounts[:3]:  # Test first 3 accounts
                account_id = account.get('account_id')
                
                success_activity, activity_response = self.run_test(
                    f"Test Activity for {account_id[:30]}...",
                    "GET",
                    f"api/mt5/admin/account/{account_id}/activity",
                    200,
                    headers=self.get_auth_headers()
                )
                
                if success_activity:
                    activities = activity_response.get('activity', [])
                    total = activity_response.get('total_activities', 0)
                    print(f"      Activities: {total} found")
                    
                    if total > 0:
                        print(f"      ✅ This account HAS activity data")
                        # Show sample activity
                        sample = activities[0]
                        print(f"      Sample: {sample.get('type')} - {sample.get('description', 'No description')}")
                    else:
                        print(f"      ❌ This account has NO activity data")
                else:
                    print(f"      ❌ Failed to get activity for this account")
        
        return True

    def test_priority_3_api_response_format(self) -> bool:
        """PRIORITY 3: Test API Response Format"""
        print("\n" + "="*80)
        print("📋 PRIORITY 3: TEST API RESPONSE FORMAT")
        print("="*80)
        
        # Test the response format with our target account
        success, response = self.run_test(
            "Verify API Response Format",
            "GET",
            f"api/mt5/admin/account/{self.target_account_id}/activity",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            print(f"\n   📋 Complete Response Structure Analysis:")
            
            # Check top-level structure
            expected_structure = {
                'success': bool,
                'account_id': str,
                'activity': list,
                'total_activities': int
            }
            
            for key, expected_type in expected_structure.items():
                if key in response:
                    actual_value = response[key]
                    actual_type = type(actual_value)
                    
                    if isinstance(actual_value, expected_type):
                        print(f"   ✅ {key}: {actual_type.__name__} = {actual_value if key != 'activity' else f'[{len(actual_value)} items]'}")
                    else:
                        print(f"   ❌ {key}: Expected {expected_type.__name__}, got {actual_type.__name__}")
                        return False
                else:
                    print(f"   ❌ Missing required field: {key}")
                    return False
            
            # Check activity array structure if activities exist
            activities = response.get('activity', [])
            if activities:
                print(f"\n   📋 Activity Object Structure Analysis:")
                activity = activities[0]
                
                # Required fields for all activities
                required_fields = {
                    'activity_id': str,
                    'type': str,
                    'amount': (int, float),
                    'description': str,
                    'timestamp': str,
                    'status': str
                }
                
                for field, expected_type in required_fields.items():
                    if field in activity:
                        actual_value = activity[field]
                        actual_type = type(actual_value)
                        
                        if isinstance(actual_value, expected_type):
                            print(f"   ✅ {field}: {actual_type.__name__} = {actual_value}")
                        else:
                            print(f"   ❌ {field}: Expected {expected_type}, got {actual_type.__name__}")
                            return False
                    else:
                        print(f"   ❌ Missing activity field: {field}")
                        return False
                
                # Check trade-specific fields if it's a trade
                if activity.get('type') == 'trade':
                    print(f"\n   📋 Trade-Specific Fields Analysis:")
                    trade_fields = {
                        'symbol': str,
                        'trade_type': str,
                        'volume': (int, float),
                        'opening_price': (int, float),
                        'current_price': (int, float),
                        'profit_loss': (int, float)
                    }
                    
                    for field, expected_type in trade_fields.items():
                        if field in activity:
                            actual_value = activity[field]
                            actual_type = type(actual_value)
                            
                            if isinstance(actual_value, expected_type):
                                print(f"   ✅ {field}: {actual_type.__name__} = {actual_value}")
                            else:
                                print(f"   ❌ {field}: Expected {expected_type}, got {actual_type.__name__}")
                                return False
                        else:
                            print(f"   ❌ Missing trade field: {field}")
                            return False
                
                # Validate timestamp format
                timestamp = activity.get('timestamp')
                if timestamp:
                    try:
                        # Try to parse the timestamp
                        parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        print(f"   ✅ Timestamp format valid: {parsed_time}")
                    except:
                        print(f"   ❌ Invalid timestamp format: {timestamp}")
                        return False
                
            else:
                print(f"\n   🚨 No activities to analyze structure")
                print(f"   🔍 This confirms the 'No activity recorded' issue")
                return False
                
        else:
            print(f"   ❌ Failed to get response for format analysis")
            return False
        
        return True

    def run_comprehensive_mt5_activity_tests(self) -> bool:
        """Run all MT5 activity tests as requested in review"""
        print("\n" + "="*100)
        print("🎯 CRITICAL MT5 ACCOUNT ACTIVITY API TESTING")
        print("="*100)
        print("User Report: Frontend shows 'No activity recorded' despite stored trading data")
        print(f"Target Account: {self.target_account_id}")
        print("Expected: 6 activities (1 deposit + 5 trades with EURUSD, USDCHF, XAUUSD)")
        
        # Setup authentication first
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed with MT5 tests")
            return False
        
        # Run all priority tests
        test_suites = [
            ("Priority 1: MT5 Activity API Endpoint", self.test_priority_1_mt5_activity_api),
            ("Priority 2: Database Query Debug", self.test_priority_2_database_query_debug),
            ("Priority 3: API Response Format", self.test_priority_3_api_response_format)
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
        print("📊 MT5 ACTIVITY API TEST RESULTS")
        print("="*100)
        
        passed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Overall Results:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed ({passed_suites/total_suites*100:.1f}%)")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Determine overall success and provide diagnosis
        overall_success = passed_suites == total_suites and self.tests_passed >= (self.tests_run * 0.8)
        
        print(f"\n🔍 DIAGNOSIS:")
        if self.tests_passed == 0:
            print("   🚨 CRITICAL: All tests failed - MT5 activity API is completely broken")
            print("   🔧 ACTION: Check backend server status and database connectivity")
        elif passed_suites == 0:
            print("   🚨 CRITICAL: No test suites passed - Major MT5 activity system failure")
            print("   🔧 ACTION: Investigate MT5 activity endpoint implementation")
        elif passed_suites < total_suites:
            print("   ⚠️ PARTIAL: Some tests failed - MT5 activity system has issues")
            print("   🔧 ACTION: Review failed test details and fix specific issues")
        else:
            print("   ✅ SUCCESS: All tests passed - MT5 activity API is working correctly")
            print("   🎉 RESULT: Frontend 'No activity recorded' issue should be resolved")
        
        if overall_success:
            print(f"\n🎉 MT5 ACTIVITY API TESTING COMPLETED SUCCESSFULLY!")
            print("   The MT5 activity system is working correctly.")
            print("   If frontend still shows 'No activity recorded', check frontend code.")
        else:
            print(f"\n⚠️ MT5 ACTIVITY API TESTING FOUND ISSUES")
            print("   The reported 'No activity recorded' issue is confirmed.")
            print("   Backend MT5 activity system needs fixes.")
        
        return overall_success

def main():
    """Main test execution"""
    print("🎯 MT5 Account Activity API Testing Suite")
    print("Critical test for user-reported 'No activity recorded' issue")
    
    tester = MT5ActivityTester()
    
    try:
        success = tester.run_comprehensive_mt5_activity_tests()
        
        if success:
            print("\n✅ MT5 Activity API tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ MT5 Activity API tests found critical issues!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()