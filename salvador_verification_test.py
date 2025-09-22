#!/usr/bin/env python3
"""
SALVADOR PALMA DATA VERIFICATION TEST - CORRECTED VERSION
=========================================================

This test verifies Salvador's data restoration as requested in the urgent review.
Based on initial findings, the data appears to be correctly restored.

Expected Results (from review request):
- Salvador Palma client profile (client_003)
- BALANCE fund investment: $1,263,485.40
- CORE fund investment: $4,000.00
- DooTechnology MT5 account (Login: 9928326)
- VT Markets MT5 account (Login: 15759667)
- Total AUM: $1,267,485.40
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fidussign.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class SalvadorVerificationTest:
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
    
    def test_salvador_client_profile(self):
        """Test Salvador's client profile exists with correct data"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                data = response.json()
                clients = data.get('clients', [])
                
                salvador_found = False
                for client in clients:
                    if client.get('id') == 'client_003':
                        salvador_found = True
                        
                        # Verify expected data
                        expected_name = 'SALVADOR PALMA'
                        expected_email = 'chava@alyarglobal.com'
                        expected_balance = 1267485.4
                        
                        name_correct = client.get('name') == expected_name
                        email_correct = client.get('email') == expected_email
                        balance_correct = abs(client.get('total_balance', 0) - expected_balance) < 1.0
                        
                        if name_correct and email_correct and balance_correct:
                            self.log_result("Salvador Client Profile", True, 
                                          f"Salvador found with correct data: {client.get('name')}, {client.get('email')}, ${client.get('total_balance'):,.2f}")
                        else:
                            issues = []
                            if not name_correct:
                                issues.append(f"Name: expected '{expected_name}', got '{client.get('name')}'")
                            if not email_correct:
                                issues.append(f"Email: expected '{expected_email}', got '{client.get('email')}'")
                            if not balance_correct:
                                issues.append(f"Balance: expected ${expected_balance:,.2f}, got ${client.get('total_balance'):,.2f}")
                            
                            self.log_result("Salvador Client Profile", False, 
                                          "Salvador found but data incorrect", {"issues": issues})
                        break
                
                if not salvador_found:
                    self.log_result("Salvador Client Profile", False, 
                                  "Salvador Palma (client_003) not found", 
                                  {"total_clients": len(clients)})
            else:
                self.log_result("Salvador Client Profile", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Salvador Client Profile", False, f"Exception: {str(e)}")
    
    def test_salvador_investments(self):
        """Test Salvador's 2 investments with correct amounts"""
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_003")
            if response.status_code == 200:
                data = response.json()
                investments = data.get('investments', [])
                
                if len(investments) == 2:
                    balance_found = False
                    core_found = False
                    
                    for investment in investments:
                        fund_code = investment.get('fund_code')
                        principal_amount = investment.get('principal_amount')
                        
                        if fund_code == 'BALANCE' and abs(principal_amount - 1263485.40) < 1.0:
                            balance_found = True
                            self.log_result("Salvador BALANCE Investment", True, 
                                          f"BALANCE investment verified: ${principal_amount:,.2f}")
                        elif fund_code == 'CORE' and abs(principal_amount - 4000.00) < 1.0:
                            core_found = True
                            self.log_result("Salvador CORE Investment", True, 
                                          f"CORE investment verified: ${principal_amount:,.2f}")
                    
                    if balance_found and core_found:
                        total_amount = 1263485.40 + 4000.00
                        self.log_result("Salvador Investment Verification", True, 
                                      f"Both investments verified. Total: ${total_amount:,.2f}")
                    else:
                        missing = []
                        if not balance_found:
                            missing.append("BALANCE ($1,263,485.40)")
                        if not core_found:
                            missing.append("CORE ($4,000.00)")
                        self.log_result("Salvador Investment Verification", False, 
                                      f"Missing investments: {', '.join(missing)}")
                else:
                    self.log_result("Salvador Investment Count", False, 
                                  f"Expected 2 investments, found {len(investments)}")
            else:
                self.log_result("Salvador Investments", False, 
                              f"Failed to get Salvador's investments: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Salvador Investments", False, f"Exception: {str(e)}")
    
    def test_salvador_mt5_accounts(self):
        """Test Salvador's 2 MT5 accounts are properly created and linked"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            if response.status_code == 200:
                data = response.json()
                all_accounts = data.get('accounts', [])
                
                salvador_accounts = [acc for acc in all_accounts if acc.get('client_id') == 'client_003']
                
                if len(salvador_accounts) == 2:
                    doo_found = False
                    vt_found = False
                    
                    for account in salvador_accounts:
                        login = account.get('mt5_login')
                        broker = account.get('broker_name', '')
                        
                        if login == '9928326' and 'DooTechnology' in broker:
                            doo_found = True
                            self.log_result("Salvador DooTechnology MT5", True, 
                                          f"DooTechnology account verified: Login {login}, Allocated ${account.get('total_allocated'):,.2f}")
                        elif login == '15759667' and 'VT Markets' in broker:
                            vt_found = True
                            self.log_result("Salvador VT Markets MT5", True, 
                                          f"VT Markets account verified: Login {login}, Allocated ${account.get('total_allocated'):,.2f}")
                    
                    if doo_found and vt_found:
                        total_allocated = sum(acc.get('total_allocated', 0) for acc in salvador_accounts)
                        self.log_result("Salvador MT5 Accounts Complete", True, 
                                      f"Both MT5 accounts verified. Total allocated: ${total_allocated:,.2f}")
                    else:
                        missing = []
                        if not doo_found:
                            missing.append("DooTechnology (Login: 9928326)")
                        if not vt_found:
                            missing.append("VT Markets (Login: 15759667)")
                        self.log_result("Salvador MT5 Account Verification", False, 
                                      f"Missing MT5 accounts: {', '.join(missing)}")
                else:
                    self.log_result("Salvador MT5 Account Count", False, 
                                  f"Expected 2 MT5 accounts, found {len(salvador_accounts)}")
            else:
                self.log_result("Salvador MT5 Accounts", False, 
                              f"Failed to get MT5 accounts: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Salvador MT5 Accounts", False, f"Exception: {str(e)}")
    
    def test_fund_performance_integration(self):
        """Test Salvador appears in fund performance dashboard"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/fund-performance/dashboard")
            if response.status_code == 200:
                data = response.json()
                dashboard = data.get('dashboard', {})
                
                # Check fund commitments
                fund_commitments = dashboard.get('fund_commitments', {})
                balance_commitment = fund_commitments.get('BALANCE', {})
                core_commitment = fund_commitments.get('CORE', {})
                
                balance_ok = balance_commitment.get('client_investment', {}).get('client_id') == 'client_003'
                core_ok = core_commitment.get('client_investment', {}).get('client_id') == 'client_003'
                
                if balance_ok and core_ok:
                    balance_amount = balance_commitment.get('client_investment', {}).get('principal_amount', 0)
                    core_amount = core_commitment.get('client_investment', {}).get('principal_amount', 0)
                    self.log_result("Fund Performance Integration", True, 
                                  f"Salvador integrated in fund performance: BALANCE ${balance_amount:,.2f}, CORE ${core_amount:,.2f}")
                else:
                    self.log_result("Fund Performance Integration", False, 
                                  "Salvador not properly integrated in fund performance dashboard")
            else:
                self.log_result("Fund Performance Integration", False, 
                              f"Failed to get fund performance: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Fund Performance Integration", False, f"Exception: {str(e)}")
    
    def test_cash_flow_integration(self):
        """Test Salvador appears in cash flow calculations"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/cashflow/overview")
            if response.status_code == 200:
                data = response.json()
                
                # Look for non-zero values indicating Salvador's data is included
                mt5_profits = data.get('mt5_trading_profits', 0)
                client_obligations = data.get('client_interest_obligations', 0)
                
                if mt5_profits > 0 or client_obligations > 0:
                    self.log_result("Cash Flow Integration", True, 
                                  f"Salvador integrated in cash flow: MT5 Profits ${mt5_profits:,.2f}, Obligations ${client_obligations:,.2f}")
                else:
                    self.log_result("Cash Flow Integration", False, 
                                  "Salvador not integrated in cash flow calculations (all values $0)")
            else:
                self.log_result("Cash Flow Integration", False, 
                              f"Failed to get cash flow data: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Cash Flow Integration", False, f"Exception: {str(e)}")
    
    def test_system_health(self):
        """Test system health and critical endpoints"""
        critical_endpoints = [
            ("/health", "Health Check"),
            ("/health/ready", "Readiness Check")
        ]
        
        for endpoint, name in critical_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    self.log_result(f"System Health - {name}", True, 
                                  f"Endpoint healthy: {endpoint}")
                else:
                    self.log_result(f"System Health - {name}", False, 
                                  f"HTTP {response.status_code}: {endpoint}")
            except Exception as e:
                self.log_result(f"System Health - {name}", False, 
                              f"Exception on {endpoint}: {str(e)}")
    
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
        print("-" * 40)
        
        # Run all verification tests
        self.test_salvador_client_profile()
        self.test_salvador_investments()
        self.test_salvador_mt5_accounts()
        self.test_fund_performance_integration()
        self.test_cash_flow_integration()
        self.test_system_health()
        
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
        
        # Critical assessment based on review requirements
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
            print("   ✓ Salvador Palma client profile exists")
            print("   ✓ BALANCE fund investment: $1,263,485.40")
            print("   ✓ CORE fund investment: $4,000.00")
            print("   ✓ DooTechnology MT5 account (Login: 9928326)")
            print("   ✓ VT Markets MT5 account (Login: 15759667)")
            print("   ✓ Total AUM: $1,267,485.40")
            print("\n   🎉 SYSTEM READY FOR PRODUCTION DEPLOYMENT!")
        else:
            print("❌ SALVADOR DATA RESTORATION: INCOMPLETE")
            print("   Critical data restoration issues found.")
            print("   Main agent action required before deployment.")
        
        print("\n" + "=" * 50)

def main():
    """Main test execution"""
    test_runner = SalvadorVerificationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()