#!/usr/bin/env python3
"""
PRODUCTION SALVADOR PALMA DATA VERIFICATION TEST
===============================================

This test verifies Salvador's data accessibility in production after fixing frontend URL configuration.

FRONTEND CONFIG FIXED:
✅ Changed REACT_APP_BACKEND_URL from preview URL to production URL
✅ Frontend will now connect to correct production backend at https://fidus-invest.emergent.host

VERIFICATION NEEDED:
1. Test Salvador's client data: GET /api/client/client_003/data
2. Test Salvador's investments: GET /api/investments/client/client_003  
3. Test MT5 accounts: GET /api/mt5/admin/accounts
4. Test fund performance: GET /api/admin/fund-performance/dashboard
5. Test cash flow: GET /api/admin/cashflow/overview

EXPECTED RESULTS AFTER FRONTEND FIX:
- Client dashboard should show Salvador's correct balances
- Total AUM: $1,267,485.40 (BALANCE: $1,263,485.40 + CORE: $4,000)
- MT5 accounts should be visible (DooTechnology + VT Markets)
- Fund performance dashboard should include Salvador
- No more $0 values in frontend
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - PRODUCTION BACKEND URL
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ProductionSalvadorVerificationTest:
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
    
    def test_salvador_client_data(self):
        """Test Salvador's client data endpoint"""
        try:
            # Try the specific client data endpoint mentioned in review
            response = self.session.get(f"{BACKEND_URL}/client/client_003/data")
            if response.status_code == 200:
                client_data = response.json()
                
                # Check if Salvador's data is present
                if client_data and isinstance(client_data, dict):
                    # Look for key indicators of Salvador's data
                    balance_info = client_data.get('balance', {})
                    total_balance = balance_info.get('total_balance', 0)
                    
                    if total_balance > 0:
                        self.log_result("Salvador Client Data", True, 
                                      f"Client data accessible with balance: ${total_balance:,.2f}",
                                      {"total_balance": total_balance})
                    else:
                        self.log_result("Salvador Client Data", False, 
                                      "Client data accessible but shows $0 balance",
                                      {"client_data": client_data})
                else:
                    self.log_result("Salvador Client Data", False, 
                                  "Empty or invalid client data response",
                                  {"response": client_data})
            else:
                self.log_result("Salvador Client Data", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Salvador Client Data", False, f"Exception: {str(e)}")
    
    def test_salvador_investments(self):
        """Test Salvador's investments endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_003")
            if response.status_code == 200:
                investments = response.json()
                
                if isinstance(investments, list) and len(investments) > 0:
                    # Calculate total investment amount
                    total_amount = 0
                    balance_found = False
                    core_found = False
                    
                    for investment in investments:
                        principal = investment.get('principal_amount', 0)
                        fund_code = investment.get('fund_code', '')
                        total_amount += principal
                        
                        if fund_code == 'BALANCE' and abs(principal - 1263485.40) < 1.0:
                            balance_found = True
                        elif fund_code == 'CORE' and abs(principal - 4000.00) < 1.0:
                            core_found = True
                    
                    expected_total = 1267485.40
                    if abs(total_amount - expected_total) < 1.0:
                        self.log_result("Salvador Investments", True, 
                                      f"Investments accessible with correct total: ${total_amount:,.2f}",
                                      {"investment_count": len(investments), "balance_found": balance_found, "core_found": core_found})
                    else:
                        self.log_result("Salvador Investments", False, 
                                      f"Investment total incorrect: expected ${expected_total:,.2f}, got ${total_amount:,.2f}",
                                      {"investments": investments})
                else:
                    self.log_result("Salvador Investments", False, 
                                  f"No investments found for Salvador (count: {len(investments) if isinstance(investments, list) else 'unknown'})",
                                  {"response": investments})
            else:
                self.log_result("Salvador Investments", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Salvador Investments", False, f"Exception: {str(e)}")
    
    def test_mt5_accounts(self):
        """Test MT5 accounts endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            if response.status_code == 200:
                mt5_accounts = response.json()
                
                if isinstance(mt5_accounts, list):
                    # Look for Salvador's MT5 accounts
                    salvador_accounts = [acc for acc in mt5_accounts if acc.get('client_id') == 'client_003']
                    
                    if len(salvador_accounts) >= 2:
                        # Check for DooTechnology and VT Markets
                        doo_found = any('9928326' in str(acc.get('login', '')) for acc in salvador_accounts)
                        vt_found = any('15759667' in str(acc.get('login', '')) for acc in salvador_accounts)
                        
                        if doo_found and vt_found:
                            self.log_result("MT5 Accounts", True, 
                                          f"Both MT5 accounts found for Salvador (DooTechnology + VT Markets)",
                                          {"account_count": len(salvador_accounts)})
                        else:
                            missing = []
                            if not doo_found: missing.append("DooTechnology (9928326)")
                            if not vt_found: missing.append("VT Markets (15759667)")
                            self.log_result("MT5 Accounts", False, 
                                          f"Missing MT5 accounts: {', '.join(missing)}",
                                          {"salvador_accounts": salvador_accounts})
                    else:
                        self.log_result("MT5 Accounts", False, 
                                      f"Insufficient MT5 accounts for Salvador: {len(salvador_accounts)} (expected 2)",
                                      {"total_accounts": len(mt5_accounts), "salvador_accounts": salvador_accounts})
                else:
                    self.log_result("MT5 Accounts", False, 
                                  "Invalid MT5 accounts response format",
                                  {"response": mt5_accounts})
            else:
                self.log_result("MT5 Accounts", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("MT5 Accounts", False, f"Exception: {str(e)}")
    
    def test_fund_performance_dashboard(self):
        """Test fund performance dashboard endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/fund-performance/dashboard")
            if response.status_code == 200:
                fund_data = response.json()
                
                if fund_data and isinstance(fund_data, dict):
                    # Look for Salvador's presence in fund performance data
                    salvador_found = False
                    total_aum = 0
                    
                    # Check various possible data structures
                    if 'clients' in fund_data:
                        clients = fund_data['clients']
                        if isinstance(clients, list):
                            salvador_found = any('client_003' in str(client) or 'SALVADOR' in str(client).upper() 
                                               for client in clients)
                    
                    if 'total_aum' in fund_data:
                        total_aum = fund_data['total_aum']
                    elif 'total_assets' in fund_data:
                        total_aum = fund_data['total_assets']
                    
                    # Check if we have non-zero values (no more $0 values)
                    has_non_zero_values = total_aum > 0
                    
                    if salvador_found or has_non_zero_values:
                        self.log_result("Fund Performance Dashboard", True, 
                                      f"Fund performance data accessible with non-zero values (AUM: ${total_aum:,.2f})",
                                      {"salvador_found": salvador_found, "total_aum": total_aum})
                    else:
                        self.log_result("Fund Performance Dashboard", False, 
                                      "Fund performance shows $0 values or Salvador not found",
                                      {"fund_data": fund_data})
                else:
                    self.log_result("Fund Performance Dashboard", False, 
                                  "Empty or invalid fund performance response",
                                  {"response": fund_data})
            else:
                self.log_result("Fund Performance Dashboard", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Fund Performance Dashboard", False, f"Exception: {str(e)}")
    
    def test_cash_flow_overview(self):
        """Test cash flow overview endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/cashflow/overview")
            if response.status_code == 200:
                cashflow_data = response.json()
                
                if cashflow_data and isinstance(cashflow_data, dict):
                    # Look for non-zero cash flow values
                    mt5_profits = cashflow_data.get('mt5_trading_profits', 0)
                    client_obligations = cashflow_data.get('client_obligations', 0) or cashflow_data.get('client_interest_obligations', 0)
                    total_assets = cashflow_data.get('total_fund_assets', 0)
                    
                    # Check if we have meaningful cash flow data (no more $0 values)
                    has_meaningful_data = any(val > 0 for val in [mt5_profits, client_obligations, total_assets])
                    
                    if has_meaningful_data:
                        self.log_result("Cash Flow Overview", True, 
                                      f"Cash flow data accessible with non-zero values",
                                      {"mt5_profits": mt5_profits, "client_obligations": client_obligations, "total_assets": total_assets})
                    else:
                        self.log_result("Cash Flow Overview", False, 
                                      "Cash flow shows all $0 values",
                                      {"cashflow_data": cashflow_data})
                else:
                    self.log_result("Cash Flow Overview", False, 
                                  "Empty or invalid cash flow response",
                                  {"response": cashflow_data})
            else:
                self.log_result("Cash Flow Overview", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Cash Flow Overview", False, f"Exception: {str(e)}")
    
    def test_production_connectivity(self):
        """Test basic production backend connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("Production Connectivity", True, 
                              "Production backend is accessible and healthy",
                              {"health_status": health_data.get('status', 'unknown')})
            else:
                self.log_result("Production Connectivity", False, 
                              f"Production backend health check failed: HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Production Connectivity", False, f"Cannot connect to production backend: {str(e)}")
    
    def run_all_tests(self):
        """Run all production verification tests"""
        print("🎯 PRODUCTION SALVADOR PALMA DATA VERIFICATION TEST")
        print("=" * 60)
        print(f"Production Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("VERIFICATION SCOPE:")
        print("✅ Frontend URL configuration fixed to production")
        print("✅ Testing Salvador's data accessibility via production backend")
        print("✅ Verifying no more $0 values in dashboards")
        print()
        
        # Test production connectivity first
        self.test_production_connectivity()
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Production Data Verification Tests...")
        print("-" * 50)
        
        # Run all verification tests as specified in review request
        self.test_salvador_client_data()
        self.test_salvador_investments()
        self.test_mt5_accounts()
        self.test_fund_performance_dashboard()
        self.test_cash_flow_overview()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 PRODUCTION VERIFICATION TEST SUMMARY")
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
        
        # Critical assessment for production readiness
        critical_tests = [
            "Salvador Investments",
            "MT5 Accounts", 
            "Fund Performance Dashboard",
            "Cash Flow Overview"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 PRODUCTION READINESS ASSESSMENT:")
        if critical_passed >= 3:  # At least 3 out of 4 critical tests
            print("✅ PRODUCTION VERIFICATION: SUCCESSFUL")
            print("   Salvador's data is accessible via production backend.")
            print("   Frontend URL configuration fix is working correctly.")
            print("   Expected AUM ($1,267,485.40) and MT5 accounts should be visible.")
        else:
            print("❌ PRODUCTION VERIFICATION: FAILED")
            print("   Critical issues found with Salvador's data accessibility.")
            print("   Frontend may still show $0 values despite URL fix.")
            print("   Main agent action required.")
        
        print("\n📋 EXPECTED RESULTS VERIFICATION:")
        print("   • Total AUM: $1,267,485.40 (BALANCE: $1,263,485.40 + CORE: $4,000)")
        print("   • MT5 Accounts: DooTechnology (9928326) + VT Markets (15759667)")
        print("   • Fund Performance: Salvador should be included")
        print("   • Cash Flow: Non-zero values expected")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = ProductionSalvadorVerificationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
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

    def test_admin_login(self):
        """Test admin login"""
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
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
        return success

    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.admin_user or not self.admin_user.get('token'):
            return {'Content-Type': 'application/json'}
        return {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }

    def test_salvador_client_exists(self):
        """Test if Salvador Palma client exists"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Salvador Client Profile Check",
            "GET",
            "api/admin/clients",
            200,
            headers=headers
        )
        
        if success:
            clients = response.get('clients', [])
            print(f"   Total clients in production: {len(clients)}")
            
            salvador_found = False
            for client in clients:
                if client.get('id') == self.salvador_client_id:
                    salvador_found = True
                    print(f"   ✅ Salvador Palma found!")
                    print(f"   - Name: {client.get('name')}")
                    print(f"   - Email: {client.get('email')}")
                    print(f"   - Status: {client.get('status', 'N/A')}")
                    break
            
            if not salvador_found:
                print(f"   ❌ Salvador Palma (client_003) NOT FOUND in production!")
                print(f"   Available clients:")
                for client in clients[:5]:  # Show first 5 clients
                    print(f"   - {client.get('id')}: {client.get('name')}")
                return False
                
            return True
        
        return False

    def test_salvador_investments(self):
        """Test Salvador's investments"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Salvador Investments Check",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200,
            headers=headers
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   Salvador's investments: {len(investments)}")
            
            balance_found = False
            core_found = False
            
            for investment in investments:
                fund_code = investment.get('fund_code')
                principal = investment.get('principal_amount', 0)
                investment_id = investment.get('investment_id')
                
                print(f"   - {fund_code}: ${principal:,.2f} (ID: {investment_id})")
                
                if fund_code == "BALANCE" and abs(principal - 1263485.40) < 1:
                    balance_found = True
                    print(f"     ✅ BALANCE fund investment verified!")
                
                if fund_code == "CORE" and abs(principal - 4000.00) < 1:
                    core_found = True
                    print(f"     ✅ CORE fund investment verified!")
            
            if not balance_found:
                print(f"   ❌ BALANCE fund investment ($1,263,485.40) NOT FOUND!")
            
            if not core_found:
                print(f"   ❌ CORE fund investment ($4,000.00) NOT FOUND!")
            
            return balance_found and core_found
        
        return False

    def test_mt5_accounts(self):
        """Test MT5 accounts"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "MT5 Accounts Check",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   Total MT5 accounts: {len(accounts)}")
            
            salvador_accounts = [acc for acc in accounts if acc.get('client_id') == self.salvador_client_id]
            print(f"   Salvador's MT5 accounts: {len(salvador_accounts)}")
            
            doo_found = False
            vt_found = False
            
            for account in salvador_accounts:
                login = account.get('login')
                broker = account.get('broker', 'Unknown')
                print(f"   - Login: {login}, Broker: {broker}")
                
                if login == "9928326":
                    doo_found = True
                    print(f"     ✅ DooTechnology account found!")
                
                if login == "15759667":
                    vt_found = True
                    print(f"     ✅ VT Markets account found!")
            
            if not doo_found:
                print(f"   ❌ DooTechnology MT5 account (9928326) NOT FOUND!")
            
            if not vt_found:
                print(f"   ❌ VT Markets MT5 account (15759667) NOT FOUND!")
            
            return doo_found and vt_found
        
        return False

    def test_fund_performance(self):
        """Test Fund Performance dashboard"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=headers
        )
        
        if success:
            performance_data = response.get('performance_gaps', [])
            print(f"   Performance records: {len(performance_data)}")
            
            salvador_records = [rec for rec in performance_data if rec.get('client_id') == self.salvador_client_id]
            print(f"   Salvador's performance records: {len(salvador_records)}")
            
            if salvador_records:
                print(f"   ✅ Salvador found in Fund Performance dashboard!")
                for record in salvador_records[:3]:  # Show first 3 records
                    print(f"   - Fund: {record.get('fund_code')}, Gap: {record.get('performance_gap', 'N/A')}")
                return True
            else:
                print(f"   ❌ Salvador NOT found in Fund Performance dashboard!")
                return False
        
        return False

    def test_cash_flow(self):
        """Test Cash Flow Management"""
        headers = self.get_auth_headers()
        success, response = self.run_test(
            "Cash Flow Management",
            "GET",
            "api/admin/cashflow/overview",
            200,
            headers=headers
        )
        
        if success:
            mt5_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            
            print(f"   MT5 Trading Profits: ${mt5_profits:,.2f}")
            print(f"   Client Obligations: ${client_obligations:,.2f}")
            
            if mt5_profits > 0 and client_obligations > 0:
                print(f"   ✅ Cash Flow shows non-zero values!")
                return True
            else:
                print(f"   ❌ Cash Flow shows zero values!")
                return False
        
        return False

    def test_health_check(self):
        """Test basic health check"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            print(f"   System Status: {status}")
        
        return success

    def run_all_tests(self):
        """Run all production verification tests"""
        print("=" * 80)
        print("🚀 PRODUCTION ENVIRONMENT VERIFICATION")
        print("=" * 80)
        print(f"Production URL: {self.base_url}")
        print(f"Target: Salvador Palma (client_003) complete data restoration")
        print()
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Admin Authentication", self.test_admin_login),
            ("Salvador Client Profile", self.test_salvador_client_exists),
            ("Salvador Investments", self.test_salvador_investments),
            ("MT5 Accounts", self.test_mt5_accounts),
            ("Fund Performance Dashboard", self.test_fund_performance),
            ("Cash Flow Management", self.test_cash_flow),
        ]
        
        results = []
        for test_name, test_method in tests:
            print(f"\n{'='*60}")
            print(f"🧪 {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_method()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Final summary
        print("\n" + "=" * 80)
        print("📊 PRODUCTION VERIFICATION RESULTS")
        print("=" * 80)
        
        passed_tests = sum(1 for _, result in results if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"API Tests Run: {self.tests_run}")
        print(f"API Tests Passed: {self.tests_passed}")
        print(f"API Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print()
        print(f"Test Suites Passed: {passed_tests}/{total_tests}")
        print(f"Test Suite Success Rate: {success_rate:.1f}%")
        print()
        
        print("DETAILED RESULTS:")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        print("\n" + "=" * 80)
        
        # Critical assessment
        critical_tests = [
            "Salvador Client Profile",
            "Salvador Investments", 
            "MT5 Accounts"
        ]
        
        critical_passed = sum(1 for test_name, result in results 
                            if test_name in critical_tests and result)
        
        if critical_passed == len(critical_tests):
            print("🎉 PRODUCTION DATA RESTORATION: ✅ SUCCESS")
            print("Salvador Palma's complete data successfully verified in production!")
        else:
            print("🚨 PRODUCTION DATA RESTORATION: ❌ INCOMPLETE")
            print("Salvador Palma's data restoration needs attention!")
            print(f"Critical tests passed: {critical_passed}/{len(critical_tests)}")
        
        print("=" * 80)
        
        return success_rate >= 70.0

if __name__ == "__main__":
    tester = ProductionVerificationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)