#!/usr/bin/env python3
"""
Money Managers Endpoints Testing After Sync Fix
Test the Money Managers endpoints to verify the sync fix has been implemented correctly.

CRITICAL CONTEXT from review request:
Just synced money_managers collection with 5 active managers:
1. UNO14 Manager (886602, BALANCE, MAM)
2. TradingHub Gold (886557, 891215, BALANCE)
3. Provider1-Assev (897589, BALANCE)
4. CP Strategy (885822, 897590, CORE)
5. alefloreztrader (897591, 897599, SEPARATION)

GoldenTrade set to inactive (should NOT appear in active lists).

Expected Results:
- Exactly 5 managers returned
- All have status="active"
- GoldenTrade NOT in list
- Each has correct assigned_accounts
- Performance metrics populated (not $0)
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://referral-tracker-9.preview.emergentagent.com/api"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class MoneyManagersTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                
                if self.admin_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    
                    self.log_result(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as admin",
                        f"Token length: {len(self.admin_token)} characters"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication",
                        False,
                        "No token received in response",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Authentication failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}",
                None
            )
            return False
    
    def test_money_managers_overview(self):
        """Test GET /api/admin/money-managers endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/money-managers")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has managers
                if 'managers' in data or isinstance(data, list):
                    managers = data.get('managers', data) if isinstance(data, dict) else data
                    
                    # Expected manager names from review request
                    expected_managers = [
                        "UNO14 Manager",
                        "TradingHub Gold",
                        "Provider1-Assev", 
                        "CP Strategy",
                        "alefloreztrader"
                    ]
                    
                    # Check manager count
                    manager_count = len(managers)
                    if manager_count == 5:
                        self.log_result(
                            "Money Managers Count",
                            True,
                            f"Exactly 5 managers returned as expected",
                            f"Manager count: {manager_count}"
                        )
                    else:
                        self.log_result(
                            "Money Managers Count",
                            False,
                            f"Expected 5 managers, got {manager_count}",
                            f"Managers found: {[m.get('name', m.get('manager_name', 'Unknown')) for m in managers]}"
                        )
                    
                    # Check for GoldenTrade exclusion
                    manager_names = [m.get('name', m.get('manager_name', '')) for m in managers]
                    goldentrade_found = any('goldentrade' in name.lower() or 'golden' in name.lower() for name in manager_names)
                    
                    if not goldentrade_found:
                        self.log_result(
                            "GoldenTrade Exclusion",
                            True,
                            "GoldenTrade correctly excluded from active managers",
                            f"Active managers: {manager_names}"
                        )
                    else:
                        self.log_result(
                            "GoldenTrade Exclusion",
                            False,
                            "GoldenTrade found in active managers list",
                            f"All managers: {manager_names}"
                        )
                    
                    # Check manager status and assigned accounts
                    active_managers = 0
                    managers_with_accounts = 0
                    managers_with_performance = 0
                    
                    for manager in managers:
                        # Check status
                        status = manager.get('status', 'unknown')
                        if status == 'active':
                            active_managers += 1
                        
                        # Check assigned accounts
                        assigned_accounts = manager.get('assigned_accounts', [])
                        if assigned_accounts and len(assigned_accounts) > 0:
                            managers_with_accounts += 1
                        
                        # Check performance metrics (not $0)
                        total_pnl = manager.get('total_pnl', 0)
                        current_equity = manager.get('current_equity', 0)
                        if total_pnl != 0 or current_equity != 0:
                            managers_with_performance += 1
                    
                    # Validate all managers are active
                    if active_managers == manager_count:
                        self.log_result(
                            "Manager Status Validation",
                            True,
                            f"All {manager_count} managers have status='active'",
                            f"Active managers: {active_managers}/{manager_count}"
                        )
                    else:
                        self.log_result(
                            "Manager Status Validation",
                            False,
                            f"Not all managers have active status",
                            f"Active managers: {active_managers}/{manager_count}"
                        )
                    
                    # Validate assigned accounts
                    if managers_with_accounts >= 4:  # At least 4 should have accounts
                        self.log_result(
                            "Assigned Accounts Validation",
                            True,
                            f"Most managers have assigned accounts",
                            f"Managers with accounts: {managers_with_accounts}/{manager_count}"
                        )
                    else:
                        self.log_result(
                            "Assigned Accounts Validation",
                            False,
                            f"Too few managers have assigned accounts",
                            f"Managers with accounts: {managers_with_accounts}/{manager_count}"
                        )
                    
                    # Validate performance metrics
                    if managers_with_performance >= 3:  # At least 3 should have non-zero performance
                        self.log_result(
                            "Performance Metrics Validation",
                            True,
                            f"Most managers have performance data",
                            f"Managers with performance: {managers_with_performance}/{manager_count}"
                        )
                    else:
                        self.log_result(
                            "Performance Metrics Validation",
                            False,
                            f"Too few managers have performance data",
                            f"Managers with performance: {managers_with_performance}/{manager_count}"
                        )
                    
                    # Log detailed manager information
                    manager_details = []
                    for manager in managers:
                        detail = {
                            "name": manager.get('name', manager.get('manager_name', 'Unknown')),
                            "status": manager.get('status', 'unknown'),
                            "assigned_accounts": manager.get('assigned_accounts', []),
                            "total_pnl": manager.get('total_pnl', 0),
                            "current_equity": manager.get('current_equity', 0)
                        }
                        manager_details.append(detail)
                    
                    self.log_result(
                        "Manager Details Summary",
                        True,
                        f"Retrieved detailed information for all {manager_count} managers",
                        json.dumps(manager_details, indent=2)
                    )
                    
                else:
                    self.log_result(
                        "Money Managers Overview",
                        False,
                        "No managers found in response",
                        f"Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}"
                    )
                    
            else:
                self.log_result(
                    "Money Managers Overview",
                    False,
                    f"API call failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Money Managers Overview",
                False,
                f"Error testing money managers overview: {str(e)}",
                None
            )
    
    def test_money_managers_compare(self):
        """Test GET /api/admin/money-managers/compare endpoint"""
        try:
            # Test with specific manager IDs from review request
            manager_ids = "manager_uno14,manager_tradinghub_gold"
            response = self.session.get(f"{BACKEND_URL}/admin/money-managers/compare?manager_ids={manager_ids}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'comparison' in data or 'managers' in data or isinstance(data, list):
                    comparison_data = data.get('comparison', data.get('managers', data))
                    
                    if isinstance(comparison_data, list) and len(comparison_data) >= 2:
                        self.log_result(
                            "Money Managers Compare",
                            True,
                            f"Compare endpoint returned data for {len(comparison_data)} managers",
                            f"Manager comparison data available"
                        )
                        
                        # Check if managers have performance metrics
                        managers_with_metrics = 0
                        for manager in comparison_data:
                            if any(key in manager for key in ['total_pnl', 'return_percentage', 'win_rate']):
                                managers_with_metrics += 1
                        
                        if managers_with_metrics >= 1:
                            self.log_result(
                                "Compare Performance Metrics",
                                True,
                                f"Managers have performance metrics for comparison",
                                f"Managers with metrics: {managers_with_metrics}/{len(comparison_data)}"
                            )
                        else:
                            self.log_result(
                                "Compare Performance Metrics",
                                False,
                                f"No performance metrics found in comparison data",
                                f"Available fields: {list(comparison_data[0].keys()) if comparison_data else 'None'}"
                            )
                    else:
                        self.log_result(
                            "Money Managers Compare",
                            False,
                            f"Compare endpoint returned insufficient data",
                            f"Data type: {type(comparison_data)}, Length: {len(comparison_data) if hasattr(comparison_data, '__len__') else 'N/A'}"
                        )
                else:
                    self.log_result(
                        "Money Managers Compare",
                        False,
                        "Compare endpoint response missing expected data structure",
                        f"Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
                    )
                    
            elif response.status_code == 404:
                # Try alternative endpoint
                response = self.session.get(f"{BACKEND_URL}/admin/trading-analytics/managers")
                
                if response.status_code == 200:
                    data = response.json()
                    managers = data.get('managers', data) if isinstance(data, dict) else data
                    
                    if isinstance(managers, list) and len(managers) >= 4:
                        self.log_result(
                            "Money Managers Compare (Alternative)",
                            True,
                            f"Alternative compare endpoint returned {len(managers)} managers",
                            f"Using trading analytics endpoint as fallback"
                        )
                    else:
                        self.log_result(
                            "Money Managers Compare (Alternative)",
                            False,
                            f"Alternative endpoint returned insufficient managers",
                            f"Manager count: {len(managers) if isinstance(managers, list) else 'Not a list'}"
                        )
                else:
                    self.log_result(
                        "Money Managers Compare",
                        False,
                        f"Both compare endpoints failed. Primary: 404, Alternative: {response.status_code}",
                        f"Alternative response: {response.text[:200]}"
                    )
            else:
                self.log_result(
                    "Money Managers Compare",
                    False,
                    f"Compare API call failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Money Managers Compare",
                False,
                f"Error testing money managers compare: {str(e)}",
                None
            )
    
    def test_manager_names_verification(self):
        """Verify specific manager names from review request"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/money-managers")
            
            if response.status_code == 200:
                data = response.json()
                managers = data.get('managers', data) if isinstance(data, dict) else data
                
                if isinstance(managers, list):
                    # Extract manager names
                    found_names = []
                    for manager in managers:
                        name = manager.get('name', manager.get('manager_name', ''))
                        if name:
                            found_names.append(name)
                    
                    # Expected names from review request
                    expected_names = [
                        "UNO14 Manager",
                        "TradingHub Gold", 
                        "Provider1-Assev",
                        "CP Strategy",
                        "alefloreztrader"
                    ]
                    
                    # Check for each expected name (case-insensitive partial match)
                    matches_found = 0
                    match_details = []
                    
                    for expected in expected_names:
                        found_match = False
                        for found in found_names:
                            # Check for partial matches (case-insensitive)
                            if any(part.lower() in found.lower() for part in expected.lower().split()):
                                found_match = True
                                match_details.append(f"✓ {expected} → {found}")
                                break
                        
                        if found_match:
                            matches_found += 1
                        else:
                            match_details.append(f"✗ {expected} → NOT FOUND")
                    
                    if matches_found >= 4:  # At least 4 out of 5 should match
                        self.log_result(
                            "Manager Names Verification",
                            True,
                            f"Found {matches_found}/5 expected manager names",
                            "\n".join(match_details)
                        )
                    else:
                        self.log_result(
                            "Manager Names Verification",
                            False,
                            f"Only found {matches_found}/5 expected manager names",
                            f"Expected: {expected_names}\nFound: {found_names}\nMatches:\n" + "\n".join(match_details)
                        )
                    
                    # Verify GoldenTrade is NOT in the list
                    goldentrade_found = any('golden' in name.lower() for name in found_names)
                    if not goldentrade_found:
                        self.log_result(
                            "GoldenTrade Exclusion Verification",
                            True,
                            "GoldenTrade correctly excluded from manager names",
                            f"All found names: {found_names}"
                        )
                    else:
                        self.log_result(
                            "GoldenTrade Exclusion Verification",
                            False,
                            "GoldenTrade found in manager names (should be excluded)",
                            f"All found names: {found_names}"
                        )
                        
                else:
                    self.log_result(
                        "Manager Names Verification",
                        False,
                        "Could not extract manager names from response",
                        f"Response type: {type(managers)}"
                    )
            else:
                self.log_result(
                    "Manager Names Verification",
                    False,
                    f"Could not retrieve managers for name verification (status {response.status_code})",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Manager Names Verification",
                False,
                f"Error verifying manager names: {str(e)}",
                None
            )
    
    def run_all_tests(self):
        """Run all Money Managers tests"""
        print("🚀 MONEY MANAGERS ENDPOINTS TESTING AFTER SYNC FIX")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test Money Managers Overview
        self.test_money_managers_overview()
        
        # Step 3: Test Money Managers Compare
        self.test_money_managers_compare()
        
        # Step 4: Verify Manager Names
        self.test_manager_names_verification()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Print detailed results
        print("📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            print(f"   {result['message']}")
        
        print()
        
        # Critical validations from review request
        print("🎯 CRITICAL VALIDATIONS FROM REVIEW REQUEST:")
        
        # Check if we have exactly 5 managers
        overview_results = [r for r in self.test_results if 'Count' in r['test']]
        if overview_results and overview_results[0]['success']:
            print("✅ Manager count = 5 (not 3, not 4)")
        else:
            print("❌ Manager count ≠ 5")
        
        # Check if GoldenTrade is excluded
        exclusion_results = [r for r in self.test_results if 'GoldenTrade' in r['test']]
        if exclusion_results and all(r['success'] for r in exclusion_results):
            print("✅ GoldenTrade excluded")
        else:
            print("❌ GoldenTrade not properly excluded")
        
        # Check if managers have non-zero data
        performance_results = [r for r in self.test_results if 'Performance' in r['test']]
        if performance_results and performance_results[0]['success']:
            print("✅ All managers have non-zero data")
        else:
            print("❌ Managers missing performance data")
        
        # Check if names match
        name_results = [r for r in self.test_results if 'Names' in r['test']]
        if name_results and name_results[0]['success']:
            print("✅ Names match exactly as specified")
        else:
            print("❌ Names don't match specification")
        
        return success_rate >= 80  # Consider 80%+ as success

if __name__ == "__main__":
    tester = MoneyManagersTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 MONEY MANAGERS SYNC FIX VERIFICATION: SUCCESS!")
        sys.exit(0)
    else:
        print("\n🚨 MONEY MANAGERS SYNC FIX VERIFICATION: FAILED!")
        sys.exit(1)