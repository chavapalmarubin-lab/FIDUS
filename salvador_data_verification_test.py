#!/usr/bin/env python3
"""
SALVADOR PALMA DATA VERIFICATION TEST
====================================

This test specifically verifies Salvador Palma's data as requested in the review:
1. GET /api/admin/clients on CURRENT backend instance
2. GET /api/investments/client/client_003 on CURRENT backend instance  
3. GET /api/mt5/admin/accounts on CURRENT backend instance

Expected to find Salvador's data and verify database consistency.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://mockdb-cleanup.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class SalvadorDataVerificationTest:
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
            print(f"   Details: {json.dumps(details, indent=2)}")
    
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
    
    def test_admin_clients_endpoint(self):
        """Test GET /api/admin/clients on CURRENT backend instance"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 200:
                clients_data = response.json()
                
                # Parse clients data
                if isinstance(clients_data, dict) and 'clients' in clients_data:
                    clients = clients_data['clients']
                elif isinstance(clients_data, list):
                    clients = clients_data
                else:
                    clients = []
                
                # Find Salvador
                salvador_client = None
                for client in clients:
                    if client.get('id') == 'client_003':
                        salvador_client = client
                        break
                
                if salvador_client:
                    self.log_result("GET /api/admin/clients", True, 
                                  f"Salvador Palma found with balance: ${salvador_client.get('total_balance', 0):,.2f}",
                                  {
                                      "salvador_data": salvador_client,
                                      "total_clients": len(clients)
                                  })
                else:
                    self.log_result("GET /api/admin/clients", False, 
                                  "Salvador Palma (client_003) not found",
                                  {"all_clients": clients})
            else:
                self.log_result("GET /api/admin/clients", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("GET /api/admin/clients", False, f"Exception: {str(e)}")
    
    def test_salvador_investments_endpoint(self):
        """Test GET /api/investments/client/client_003 on CURRENT backend instance"""
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_003")
            
            if response.status_code == 200:
                investments_data = response.json()
                
                # Parse investments data
                if isinstance(investments_data, dict) and 'investments' in investments_data:
                    investments = investments_data['investments']
                    portfolio_stats = investments_data.get('portfolio_stats', {})
                elif isinstance(investments_data, list):
                    investments = investments_data
                    portfolio_stats = {}
                else:
                    investments = []
                    portfolio_stats = {}
                
                if len(investments) > 0:
                    # Analyze investments
                    balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
                    core_investments = [inv for inv in investments if inv.get('fund_code') == 'CORE']
                    
                    total_balance_amount = sum(inv.get('principal_amount', 0) for inv in balance_investments)
                    total_core_amount = sum(inv.get('principal_amount', 0) for inv in core_investments)
                    total_amount = sum(inv.get('principal_amount', 0) for inv in investments)
                    
                    self.log_result("GET /api/investments/client/client_003", True, 
                                  f"Found {len(investments)} investments, Total: ${total_amount:,.2f}",
                                  {
                                      "investments_summary": {
                                          "total_investments": len(investments),
                                          "balance_investments": len(balance_investments),
                                          "core_investments": len(core_investments),
                                          "total_balance_amount": total_balance_amount,
                                          "total_core_amount": total_core_amount,
                                          "total_amount": total_amount
                                      },
                                      "portfolio_stats": portfolio_stats,
                                      "investments_detail": investments
                                  })
                    
                    # Check for expected amounts
                    expected_balance = 1263485.40
                    expected_core = 4000.00
                    
                    balance_match = any(abs(inv.get('principal_amount', 0) - expected_balance) < 1.0 
                                      for inv in balance_investments)
                    core_match = any(abs(inv.get('principal_amount', 0) - expected_core) < 1.0 
                                   for inv in core_investments)
                    
                    if balance_match and core_match:
                        self.log_result("Expected Investment Amounts", True, 
                                      f"Found expected BALANCE (${expected_balance:,.2f}) and CORE (${expected_core:,.2f}) investments")
                    else:
                        self.log_result("Expected Investment Amounts", False, 
                                      f"Expected amounts not found - BALANCE: {balance_match}, CORE: {core_match}")
                else:
                    self.log_result("GET /api/investments/client/client_003", False, 
                                  "No investments found for Salvador")
            else:
                self.log_result("GET /api/investments/client/client_003", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("GET /api/investments/client/client_003", False, f"Exception: {str(e)}")
    
    def test_mt5_admin_accounts_endpoint(self):
        """Test GET /api/mt5/admin/accounts on CURRENT backend instance"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            
            if response.status_code == 200:
                mt5_data = response.json()
                
                # Parse MT5 data
                if isinstance(mt5_data, dict) and 'accounts' in mt5_data:
                    mt5_accounts = mt5_data['accounts']
                elif isinstance(mt5_data, list):
                    mt5_accounts = mt5_data
                else:
                    mt5_accounts = []
                
                # Find Salvador's MT5 accounts
                salvador_mt5_accounts = [acc for acc in mt5_accounts if acc.get('client_id') == 'client_003']
                
                if len(salvador_mt5_accounts) > 0:
                    # Analyze MT5 accounts
                    doo_accounts = [acc for acc in salvador_mt5_accounts if 'DooTechnology' in str(acc.get('broker', ''))]
                    vt_accounts = [acc for acc in salvador_mt5_accounts if 'VT Markets' in str(acc.get('broker', ''))]
                    
                    # Check for expected logins
                    expected_doo_login = '9928326'
                    expected_vt_login = '15759667'
                    
                    doo_login_found = any(acc.get('login') == expected_doo_login for acc in doo_accounts)
                    vt_login_found = any(acc.get('login') == expected_vt_login for acc in vt_accounts)
                    
                    self.log_result("GET /api/mt5/admin/accounts", True, 
                                  f"Found {len(salvador_mt5_accounts)} MT5 accounts for Salvador",
                                  {
                                      "mt5_summary": {
                                          "total_salvador_accounts": len(salvador_mt5_accounts),
                                          "doo_accounts": len(doo_accounts),
                                          "vt_accounts": len(vt_accounts),
                                          "doo_login_9928326_found": doo_login_found,
                                          "vt_login_15759667_found": vt_login_found
                                      },
                                      "salvador_mt5_accounts": salvador_mt5_accounts
                                  })
                    
                    if doo_login_found and vt_login_found:
                        self.log_result("Expected MT5 Logins", True, 
                                      f"Found expected DooTechnology (9928326) and VT Markets (15759667) accounts")
                    else:
                        self.log_result("Expected MT5 Logins", False, 
                                      f"Expected logins not found - DooTechnology: {doo_login_found}, VT Markets: {vt_login_found}")
                else:
                    self.log_result("GET /api/mt5/admin/accounts", False, 
                                  f"No MT5 accounts found for Salvador (Total MT5 accounts: {len(mt5_accounts)})")
            else:
                self.log_result("GET /api/mt5/admin/accounts", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("GET /api/mt5/admin/accounts", False, f"Exception: {str(e)}")
    
    def test_database_environment_info(self):
        """Test database and environment information"""
        try:
            # Get backend environment info
            response = self.session.get(f"{BACKEND_URL}/health/metrics")
            if response.status_code == 200:
                metrics = response.json()
                db_info = metrics.get('database', {})
                
                self.log_result("Database Environment Info", True, 
                              "Database metrics retrieved",
                              {
                                  "database_status": db_info.get('status'),
                                  "collections": db_info.get('collections'),
                                  "data_size": db_info.get('data_size'),
                                  "backend_url": BACKEND_URL
                              })
            else:
                self.log_result("Database Environment Info", False, 
                              f"Metrics unavailable: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Database Environment Info", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Salvador data verification tests"""
        print("🎯 SALVADOR PALMA DATA VERIFICATION TEST")
        print("=" * 50)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Salvador Data Verification Tests...")
        print("-" * 50)
        
        # Run all verification tests as requested in review
        self.test_admin_clients_endpoint()
        self.test_salvador_investments_endpoint()
        self.test_mt5_admin_accounts_endpoint()
        self.test_database_environment_info()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 50)
        print("🎯 SALVADOR DATA VERIFICATION SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Backend Tested: {BACKEND_URL}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show results for each requested endpoint
        print("📋 REQUESTED ENDPOINT RESULTS:")
        endpoint_tests = [
            ("GET /api/admin/clients", "Admin clients endpoint"),
            ("GET /api/investments/client/client_003", "Salvador investments endpoint"),
            ("GET /api/mt5/admin/accounts", "MT5 accounts endpoint")
        ]
        
        for test_name, description in endpoint_tests:
            test_result = next((r for r in self.test_results if r['test'] == test_name), None)
            if test_result:
                status = "✅" if test_result['success'] else "❌"
                print(f"   {status} {description}: {test_result['message']}")
        
        print()
        
        # Show failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        critical_endpoints_passed = sum(1 for result in self.test_results 
                                      if result['success'] and any(endpoint in result['test'] 
                                      for endpoint, _ in endpoint_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_endpoints_passed >= 3:  # All 3 requested endpoints
            print("✅ SALVADOR DATA VERIFICATION: SUCCESSFUL")
            print("   All requested endpoints contain Salvador's data.")
            print("   Database connection and data consistency confirmed.")
        else:
            print("❌ SALVADOR DATA VERIFICATION: ISSUES FOUND")
            print("   Some requested endpoints have issues.")
            print("   Further investigation required.")
        
        print("\n" + "=" * 50)

def main():
    """Main test execution"""
    test_runner = SalvadorDataVerificationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()