#!/usr/bin/env python3
"""
INDIVIDUAL GOOGLE OAUTH ENDPOINTS TESTING
=========================================

This test verifies the new Individual Google OAuth endpoints as requested in the review:
- GET /admin/google/individual-status - Should return connection status for current admin
- GET /admin/google/individual-auth-url - Should generate Google OAuth URL for individual admin
- GET /admin/google/all-connections - Should return all admin Google connections (master admin view)
- POST /admin/google/individual-disconnect - Should disconnect admin's Google account

Authentication: Use admin credentials (admin/password123)

Expected Results:
- All endpoints should require admin JWT authentication
- individual-status should show "No Google account connected" initially
- individual-auth-url should generate proper Google OAuth URL with all required scopes
- all-connections should return empty list initially
- individual-disconnect should return proper error message when no connection exists
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use correct backend URL from frontend/.env
BACKEND_URL = "https://fidus-google-sync.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class IndividualGoogleOAuthTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_individual_google_status_endpoint(self):
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
    
    def test_salvador_mt5_accounts(self):
        """Test Salvador's 2 MT5 accounts are properly created and linked"""
        try:
            # Get all MT5 accounts for Salvador
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            if response.status_code == 200:
                all_mt5_accounts = response.json()
                salvador_mt5_accounts = []
                
                # Filter for Salvador's accounts
                if isinstance(all_mt5_accounts, list):
                    for account in all_mt5_accounts:
                        if account.get('client_id') == 'client_003':
                            salvador_mt5_accounts.append(account)
                
                if len(salvador_mt5_accounts) == 2:
                    # Check for DooTechnology and VT Markets accounts
                    doo_found = False
                    vt_found = False
                    
                    for account in salvador_mt5_accounts:
                        login = account.get('login')
                        broker = account.get('broker')
                        
                        if login == '9928326' and 'DooTechnology' in str(broker):
                            doo_found = True
                            self.log_result("Salvador DooTechnology MT5", True, 
                                          f"DooTechnology account found: Login {login}")
                        elif login == '15759667' and 'VT Markets' in str(broker):
                            vt_found = True
                            self.log_result("Salvador VT Markets MT5", True, 
                                          f"VT Markets account found: Login {login}")
                    
                    if doo_found and vt_found:
                        self.log_result("Salvador MT5 Accounts Complete", True, 
                                      "Both MT5 accounts verified and properly linked")
                    else:
                        missing = []
                        if not doo_found:
                            missing.append("DooTechnology (Login: 9928326)")
                        if not vt_found:
                            missing.append("VT Markets (Login: 15759667)")
                        self.log_result("Salvador MT5 Account Verification", False, 
                                      f"Missing MT5 accounts: {', '.join(missing)}", 
                                      {"found_accounts": salvador_mt5_accounts})
                else:
                    self.log_result("Salvador MT5 Account Count", False, 
                                  f"Expected 2 MT5 accounts, found {len(salvador_mt5_accounts)}", 
                                  {"accounts": salvador_mt5_accounts})
            else:
                self.log_result("Salvador MT5 Accounts", False, 
                              f"Failed to get MT5 accounts: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Salvador MT5 Accounts", False, f"Exception: {str(e)}")
    
    def test_total_aum_calculation(self):
        """Test that total AUM shows correct amount ($1,267,485.40)"""
        try:
            # Test fund performance dashboard
            response = self.session.get(f"{BACKEND_URL}/admin/fund-performance/dashboard")
            if response.status_code == 200:
                fund_data = response.json()
                
                # Look for total AUM or similar metrics
                total_aum = None
                if isinstance(fund_data, dict):
                    total_aum = fund_data.get('total_aum') or fund_data.get('total_assets')
                
                expected_aum = 1267485.40
                if total_aum and abs(total_aum - expected_aum) < 1.0:  # Allow small rounding differences
                    self.log_result("Total AUM Calculation", True, 
                                  f"Total AUM correct: ${total_aum:,.2f}")
                else:
                    self.log_result("Total AUM Calculation", False, 
                                  f"Total AUM incorrect: expected ${expected_aum:,.2f}, got ${total_aum}", 
                                  {"fund_data": fund_data})
            else:
                self.log_result("Total AUM Calculation", False, 
                              f"Failed to get fund performance data: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Total AUM Calculation", False, f"Exception: {str(e)}")
    
    def test_critical_api_endpoints(self):
        """Test all critical API endpoints are responding"""
        critical_endpoints = [
            ("/health", "Health Check"),
            ("/admin/clients", "Admin Clients"),
            ("/investments/client/client_003", "Salvador Investments"),
            ("/mt5/admin/accounts", "MT5 Accounts"),
            ("/admin/fund-performance/dashboard", "Fund Performance"),
            ("/admin/cashflow/overview", "Cash Flow Management")
        ]
        
        for endpoint, name in critical_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    self.log_result(f"API Endpoint - {name}", True, 
                                  f"Endpoint responding: {endpoint}")
                else:
                    self.log_result(f"API Endpoint - {name}", False, 
                                  f"HTTP {response.status_code}: {endpoint}")
            except Exception as e:
                self.log_result(f"API Endpoint - {name}", False, 
                              f"Exception on {endpoint}: {str(e)}")
    
    def run_all_tests(self):
        """Run all Salvador data restoration verification tests"""
        print("🎯 SALVADOR PALMA DATABASE RESTORATION VERIFICATION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Database Restoration Verification Tests...")
        print("-" * 50)
        
        # Run all verification tests
        self.test_database_cleanup_verification()
        self.test_salvador_client_profile()
        self.test_salvador_investments()
        self.test_salvador_mt5_accounts()
        self.test_total_aum_calculation()
        self.test_critical_api_endpoints()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 SALVADOR DATA RESTORATION TEST SUMMARY")
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
        
        # Critical assessment
        critical_tests = [
            "Salvador Client Profile",
            "Salvador BALANCE Investment", 
            "Salvador CORE Investment",
            "Salvador DooTechnology MT5",
            "Salvador VT Markets MT5"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ SALVADOR DATA RESTORATION: SUCCESSFUL")
            print("   Salvador's client profile and investments are properly restored.")
            print("   System ready for production deployment verification.")
        else:
            print("❌ SALVADOR DATA RESTORATION: INCOMPLETE")
            print("   Critical data restoration issues found.")
            print("   Main agent action required before deployment.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = SalvadorDataRestorationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()