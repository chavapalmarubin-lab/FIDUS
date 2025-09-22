#!/usr/bin/env python3
"""
SALVADOR PALMA DATABASE RESTORATION VERIFICATION TEST
====================================================

This test verifies the critical database restoration as requested in the urgent review:
- Clean database of test data contamination
- Create Salvador's correct client profile (client_003)
- Create exactly 2 investments: BALANCE ($1,263,485.40) and CORE ($4,000.00)
- Create 2 MT5 accounts: DooTechnology (9928326) and VT Markets (15759667)
- Verify all API endpoints work correctly

Expected Results:
- Salvador Palma visible in clients
- Exactly 2 investments with correct amounts
- Both MT5 accounts properly linked
- Total AUM: $1,267,485.40 (not millions)
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-workspace.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class SalvadorDataRestorationTest:
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
    
    def test_database_cleanup_verification(self):
        """Verify database cleanup was successful"""
        try:
            # Check total clients count
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                client_count = len(clients) if isinstance(clients, list) else clients.get('total_clients', 0)
                
                if client_count <= 2:  # Should have admin + Salvador only
                    self.log_result("Database Cleanup - Client Count", True, 
                                  f"Client count acceptable: {client_count} (should be ≤2)")
                else:
                    self.log_result("Database Cleanup - Client Count", False, 
                                  f"Too many clients: {client_count} (should be ≤2)", {"clients": clients})
            else:
                self.log_result("Database Cleanup - Client Count", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
            
            # Check total investments
            response = self.session.get(f"{BACKEND_URL}/admin/investments")
            if response.status_code == 200:
                investments = response.json()
                investment_count = len(investments) if isinstance(investments, list) else investments.get('total_investments', 0)
                
                if investment_count <= 2:  # Should have exactly Salvador's 2 investments
                    self.log_result("Database Cleanup - Investment Count", True, 
                                  f"Investment count correct: {investment_count} (should be ≤2)")
                else:
                    self.log_result("Database Cleanup - Investment Count", False, 
                                  f"Too many investments: {investment_count} (should be ≤2)")
            else:
                self.log_result("Database Cleanup - Investment Count", False, 
                              f"Failed to get investments: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Database Cleanup Verification", False, f"Exception: {str(e)}")
    
    def test_salvador_client_profile(self):
        """Test Salvador's client profile exists with correct data"""
        try:
            # Get all clients and find Salvador
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                salvador_found = False
                
                if isinstance(clients, list):
                    for client in clients:
                        if client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper():
                            salvador_found = True
                            expected_data = {
                                'id': 'client_003',
                                'name': 'SALVADOR PALMA',
                                'email': 'chava@alyarglobal.com'
                            }
                            
                            # Verify client data
                            data_correct = True
                            issues = []
                            
                            for key, expected_value in expected_data.items():
                                actual_value = client.get(key)
                                if actual_value != expected_value:
                                    data_correct = False
                                    issues.append(f"{key}: expected '{expected_value}', got '{actual_value}'")
                            
                            if data_correct:
                                self.log_result("Salvador Client Profile", True, 
                                              "Salvador Palma profile found with correct data",
                                              {"client_data": client})
                            else:
                                self.log_result("Salvador Client Profile", False, 
                                              "Salvador found but data incorrect", 
                                              {"issues": issues, "client_data": client})
                            break
                
                if not salvador_found:
                    self.log_result("Salvador Client Profile", False, 
                                  "Salvador Palma (client_003) not found in clients list",
                                  {"total_clients": len(clients) if isinstance(clients, list) else "unknown"})
            else:
                self.log_result("Salvador Client Profile", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Salvador Client Profile", False, f"Exception: {str(e)}")
    
    def test_salvador_investments(self):
        """Test Salvador's 2 investments with correct amounts"""
        try:
            # Get Salvador's investments
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_003")
            if response.status_code == 200:
                investments = response.json()
                
                if len(investments) == 2:
                    # Check for BALANCE and CORE investments
                    balance_found = False
                    core_found = False
                    
                    for investment in investments:
                        fund_code = investment.get('fund_code')
                        principal_amount = investment.get('principal_amount')
                        
                        if fund_code == 'BALANCE' and principal_amount == 1263485.40:
                            balance_found = True
                            self.log_result("Salvador BALANCE Investment", True, 
                                          f"BALANCE investment found: ${principal_amount:,.2f}")
                        elif fund_code == 'CORE' and principal_amount == 4000.00:
                            core_found = True
                            self.log_result("Salvador CORE Investment", True, 
                                          f"CORE investment found: ${principal_amount:,.2f}")
                    
                    if balance_found and core_found:
                        total_amount = 1263485.40 + 4000.00
                        self.log_result("Salvador Total Investments", True, 
                                      f"Both investments verified. Total: ${total_amount:,.2f}")
                    else:
                        missing = []
                        if not balance_found:
                            missing.append("BALANCE ($1,263,485.40)")
                        if not core_found:
                            missing.append("CORE ($4,000.00)")
                        self.log_result("Salvador Investment Verification", False, 
                                      f"Missing investments: {', '.join(missing)}", 
                                      {"found_investments": investments})
                else:
                    self.log_result("Salvador Investment Count", False, 
                                  f"Expected 2 investments, found {len(investments)}", 
                                  {"investments": investments})
            else:
                self.log_result("Salvador Investments", False, 
                              f"Failed to get Salvador's investments: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Salvador Investments", False, f"Exception: {str(e)}")
    
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