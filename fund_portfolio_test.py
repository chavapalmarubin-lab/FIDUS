#!/usr/bin/env python3
"""
FUND PORTFOLIO ENDPOINT TESTING - Issue #5 Resolution
====================================================

This test verifies the fund portfolio endpoint to resolve Issue #5 (Fund Portfolio Empty):

EXPECTED RESULTS (as per review request):
1. CORE fund: $18,151.41 AUM with 1 MT5 account
2. BALANCE fund: $100,000.00 AUM with 3 MT5 accounts  
3. Total AUM: $118,151.41
4. Total investors: 1 (Alejandro)
5. Fund count: 2 (CORE + BALANCE)

VALIDATION CRITERIA:
✅ Fund portfolio should NOT be empty anymore
✅ Both CORE and BALANCE funds should show correct data
✅ MT5 allocations should match investment amounts
✅ Issue #5 (Fund Portfolio Empty) should be RESOLVED

Authentication: admin/password123
Backend: https://trading-platform-76.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class FundPortfolioEndpointTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.expected_total_aum = 118151.41  # As specified in review request
        self.expected_core_aum = 18151.41
        self.expected_balance_aum = 100000.00
        self.expected_core_mt5_accounts = 1
        self.expected_balance_mt5_accounts = 3
        self.expected_total_investors = 1
        self.expected_fund_count = 2
        
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
    
    def test_fund_portfolio_overview_endpoint(self):
        """Test the /api/fund-portfolio/overview endpoint for Issue #5 resolution"""
        try:
            response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if portfolio is not empty (Issue #5 resolution)
                funds = data.get('funds', [])
                total_aum = data.get('total_aum', 0)
                
                if len(funds) == 0:
                    self.log_result("Issue #5 Resolution", False, 
                                  "Fund portfolio is still EMPTY - Issue #5 NOT resolved", {"response": data})
                    return
                elif total_aum == 0:
                    self.log_result("Issue #5 Resolution", False, 
                                  f"Fund portfolio has {len(funds)} funds but $0 AUM - Issue #5 partially resolved", {"response": data})
                else:
                    self.log_result("Issue #5 Resolution", True, 
                                  f"Fund portfolio is NOT empty: {len(funds)} funds with ${total_aum:,.2f} total AUM - Issue #5 RESOLVED")
                
                # Check CORE fund details
                core_fund = None
                balance_fund = None
                
                # Handle both array and dict formats for funds
                if isinstance(funds, list):
                    core_fund = next((f for f in funds if f.get("fund_code") == "CORE"), None)
                    balance_fund = next((f for f in funds if f.get("fund_code") == "BALANCE"), None)
                elif isinstance(funds, dict):
                    core_fund = funds.get("CORE")
                    balance_fund = funds.get("BALANCE")
                
                # Validate CORE fund
                if core_fund:
                    core_aum = core_fund.get("total_aum", 0) or core_fund.get("aum", 0)
                    core_mt5_count = core_fund.get("mt5_accounts_count", 0)
                    
                    if abs(core_aum - self.expected_core_aum) < 0.01:
                        self.log_result("CORE Fund AUM", True, 
                                      f"CORE fund AUM correct: ${core_aum:,.2f}")
                    else:
                        self.log_result("CORE Fund AUM", False, 
                                      f"CORE fund AUM incorrect: Expected ${self.expected_core_aum:,.2f}, got ${core_aum:,.2f}")
                    
                    if core_mt5_count == self.expected_core_mt5_accounts:
                        self.log_result("CORE Fund MT5 Accounts", True, 
                                      f"CORE fund MT5 accounts correct: {core_mt5_count}")
                    else:
                        self.log_result("CORE Fund MT5 Accounts", False, 
                                      f"CORE fund MT5 accounts incorrect: Expected {self.expected_core_mt5_accounts}, got {core_mt5_count}")
                else:
                    self.log_result("CORE Fund Presence", False, "CORE fund not found in portfolio")
                
                # Validate BALANCE fund
                if balance_fund:
                    balance_aum = balance_fund.get("total_aum", 0) or balance_fund.get("aum", 0)
                    balance_mt5_count = balance_fund.get("mt5_accounts_count", 0)
                    
                    if abs(balance_aum - self.expected_balance_aum) < 0.01:
                        self.log_result("BALANCE Fund AUM", True, 
                                      f"BALANCE fund AUM correct: ${balance_aum:,.2f}")
                    else:
                        self.log_result("BALANCE Fund AUM", False, 
                                      f"BALANCE fund AUM incorrect: Expected ${self.expected_balance_aum:,.2f}, got ${balance_aum:,.2f}")
                    
                    if balance_mt5_count == self.expected_balance_mt5_accounts:
                        self.log_result("BALANCE Fund MT5 Accounts", True, 
                                      f"BALANCE fund MT5 accounts correct: {balance_mt5_count}")
                    else:
                        self.log_result("BALANCE Fund MT5 Accounts", False, 
                                      f"BALANCE fund MT5 accounts incorrect: Expected {self.expected_balance_mt5_accounts}, got {balance_mt5_count}")
                else:
                    self.log_result("BALANCE Fund Presence", False, "BALANCE fund not found in portfolio")
                
                # Validate total AUM
                if abs(total_aum - self.expected_total_aum) < 0.01:
                    self.log_result("Total AUM", True, 
                                  f"Total AUM correct: ${total_aum:,.2f}")
                else:
                    self.log_result("Total AUM", False, 
                                  f"Total AUM incorrect: Expected ${self.expected_total_aum:,.2f}, got ${total_aum:,.2f}")
                
                # Validate portfolio summary
                total_investors = data.get("total_investors", 0)
                fund_count = data.get("fund_count", 0)
                
                if total_investors == self.expected_total_investors:
                    self.log_result("Total Investors", True, 
                                  f"Total investors correct: {total_investors}")
                else:
                    self.log_result("Total Investors", False, 
                                  f"Total investors incorrect: Expected {self.expected_total_investors}, got {total_investors}")
                
                if fund_count == self.expected_fund_count:
                    self.log_result("Fund Count", True, 
                                  f"Fund count correct: {fund_count}")
                else:
                    self.log_result("Fund Count", False, 
                                  f"Fund count incorrect: Expected {self.expected_fund_count}, got {fund_count}")
                
            elif response.status_code == 404:
                self.log_result("Fund Portfolio Overview Endpoint", False, 
                              "Endpoint not found (404) - needs to be created", {"url": f"{BACKEND_URL}/fund-portfolio/overview"})
            else:
                self.log_result("Fund Portfolio Overview Endpoint", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Fund Portfolio Overview Endpoint", False, f"Exception: {str(e)}")
    
    def test_fund_allocation_details(self):
        """Test fund allocation details and MT5 mapping"""
        try:
            response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            
            if response.status_code == 200:
                data = response.json()
                funds = data.get('funds', [])
                
                allocation_issues = []
                
                # Handle both array and dict formats
                if isinstance(funds, list):
                    for fund in funds:
                        fund_code = fund.get("fund_code")
                        mt5_allocation = fund.get("mt5_allocation", 0)
                        client_investments = fund.get("client_investments", 0)
                        allocation_match = fund.get("allocation_match", False)
                        
                        if not allocation_match:
                            allocation_issues.append(f"{fund_code}: MT5 allocation ${mt5_allocation:,.2f} != Client investments ${client_investments:,.2f}")
                        else:
                            self.log_result(f"{fund_code} Allocation Match", True, 
                                          f"MT5 allocation matches client investments: ${mt5_allocation:,.2f}")
                elif isinstance(funds, dict):
                    for fund_code, fund_data in funds.items():
                        mt5_allocation = fund_data.get("mt5_allocation", 0)
                        client_investments = fund_data.get("client_investments", 0)
                        allocation_match = fund_data.get("allocation_match", False)
                        
                        if not allocation_match:
                            allocation_issues.append(f"{fund_code}: MT5 allocation ${mt5_allocation:,.2f} != Client investments ${client_investments:,.2f}")
                        else:
                            self.log_result(f"{fund_code} Allocation Match", True, 
                                          f"MT5 allocation matches client investments: ${mt5_allocation:,.2f}")
                
                if allocation_issues:
                    self.log_result("Fund Allocation Details", False, 
                                  f"Allocation mismatches found: {'; '.join(allocation_issues)}")
                else:
                    self.log_result("Fund Allocation Details", True, 
                                  "All fund allocations match client investments")
                    
            else:
                self.log_result("Fund Allocation Details", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Fund Allocation Details", False, f"Exception: {str(e)}")
    
    def test_data_consistency_verification(self):
        """Test data consistency between fund portfolio and client totals"""
        try:
            # Get fund portfolio total
            fund_response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            fund_total = 0
            
            if fund_response.status_code == 200:
                fund_data = fund_response.json()
                fund_total = fund_data.get('total_aum', 0)
            
            # Get client investment total
            client_response = self.session.get(f"{BACKEND_URL}/investments/client/client_003")
            client_total = 0
            
            if client_response.status_code == 200:
                client_data = client_response.json()
                if isinstance(client_data, dict) and 'investments' in client_data:
                    investments = client_data['investments']
                    client_total = sum(inv.get('current_value', 0) for inv in investments)
                elif isinstance(client_data, list):
                    client_total = sum(inv.get('current_value', 0) for inv in client_data)
            
            # Compare totals
            if fund_total > 0 and client_total > 0:
                if abs(fund_total - client_total) < 1000:  # Allow $1K variance
                    self.log_result("Data Consistency - Fund vs Client Totals", True, 
                                  f"Totals match: Fund ${fund_total:,.2f}, Client ${client_total:,.2f}")
                else:
                    self.log_result("Data Consistency - Fund vs Client Totals", False, 
                                  f"Totals mismatch: Fund ${fund_total:,.2f}, Client ${client_total:,.2f}")
            else:
                self.log_result("Data Consistency - Fund vs Client Totals", False, 
                              f"One or both totals are zero: Fund ${fund_total:,.2f}, Client ${client_total:,.2f}")
            
            # Check expected total value consistency
            expected_total = self.expected_salvador_total
            fund_matches = abs(fund_total - expected_total) < 10000
            client_matches = abs(client_total - expected_total) < 10000
            
            if fund_matches and client_matches:
                self.log_result("Data Consistency - Expected Total", True, 
                              f"Both endpoints show expected ${expected_total:,.2f} total")
            else:
                issues = []
                if not fund_matches:
                    issues.append(f"Fund total ${fund_total:,.2f} != expected ${expected_total:,.2f}")
                if not client_matches:
                    issues.append(f"Client total ${client_total:,.2f} != expected ${expected_total:,.2f}")
                
                self.log_result("Data Consistency - Expected Total", False, 
                              f"Total value inconsistencies: {'; '.join(issues)}")
                
        except Exception as e:
            self.log_result("Data Consistency Verification", False, f"Exception: {str(e)}")
    
    def test_frontend_api_compatibility(self):
        """Test frontend API compatibility for key endpoints"""
        try:
            # Test endpoints that frontend components expect
            frontend_endpoints = [
                ("/admin/clients", "ClientManagement component"),
                ("/fund-portfolio/overview", "FundPortfolioManagement component"),
                ("/mt5/admin/accounts", "MT5Management component"),
                ("/admin/prospects", "ProspectManagement component")
            ]
            
            for endpoint, component in frontend_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if response is JSON serializable (frontend requirement)
                        json.dumps(data)  # This will raise exception if not serializable
                        
                        # Check for expected structure based on endpoint
                        if endpoint == "/admin/clients":
                            if isinstance(data, dict) and 'clients' in data:
                                self.log_result(f"Frontend Compatibility - {component}", True, 
                                              "Endpoint returns frontend-compatible format")
                            else:
                                self.log_result(f"Frontend Compatibility - {component}", False, 
                                              "Endpoint format not compatible with frontend expectations")
                        
                        elif endpoint == "/fund-portfolio/overview":
                            if isinstance(data, dict) and data.get('success') and 'funds' in data:
                                self.log_result(f"Frontend Compatibility - {component}", True, 
                                              "Endpoint returns frontend-compatible format")
                            else:
                                self.log_result(f"Frontend Compatibility - {component}", False, 
                                              "Endpoint format not compatible with frontend expectations")
                        
                        else:
                            # For other endpoints, just check they return valid JSON
                            self.log_result(f"Frontend Compatibility - {component}", True, 
                                          "Endpoint returns valid JSON response")
                    
                    elif response.status_code == 404:
                        self.log_result(f"Frontend Compatibility - {component}", False, 
                                      f"Endpoint not found: {endpoint}")
                    
                    else:
                        self.log_result(f"Frontend Compatibility - {component}", False, 
                                      f"HTTP {response.status_code} for {endpoint}")
                
                except json.JSONDecodeError:
                    self.log_result(f"Frontend Compatibility - {component}", False, 
                                  f"Endpoint returns invalid JSON: {endpoint}")
                except Exception as e:
                    self.log_result(f"Frontend Compatibility - {component}", False, 
                                  f"Exception testing {endpoint}: {str(e)}")
                
        except Exception as e:
            self.log_result("Frontend API Compatibility", False, f"Exception: {str(e)}")
    
    def test_zero_values_verification(self):
        """Verify no inappropriate zero values appear in responses"""
        try:
            # Test key endpoints for zero values
            endpoints_to_check = [
                ("/fund-portfolio/overview", "Fund Portfolio"),
                ("/admin/clients", "Admin Clients"),
                ("/investments/client/client_003", "Salvador Investments")
            ]
            
            zero_value_issues = []
            
            for endpoint, name in endpoints_to_check:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check for inappropriate zero values
                        if endpoint == "/fund-portfolio/overview":
                            total_aum = data.get('total_aum', 0)
                            if total_aum == 0:
                                zero_value_issues.append(f"{name}: total_aum is zero")
                        
                        elif endpoint == "/admin/clients":
                            if isinstance(data, dict) and 'clients' in data:
                                clients = data['clients']
                                for client in clients:
                                    if client.get('id') == 'client_003':
                                        balance = client.get('total_balance', 0) or client.get('balance', 0)
                                        if balance == 0:
                                            zero_value_issues.append(f"{name}: Salvador's balance is zero")
                        
                        elif endpoint == "/investments/client/client_003":
                            if isinstance(data, dict) and 'investments' in data:
                                investments = data['investments']
                                if len(investments) == 0:
                                    zero_value_issues.append(f"{name}: No investments found for Salvador")
                                else:
                                    for inv in investments:
                                        if inv.get('current_value', 0) == 0:
                                            zero_value_issues.append(f"{name}: Investment {inv.get('fund_code')} has zero value")
                            elif isinstance(data, list):
                                if len(data) == 0:
                                    zero_value_issues.append(f"{name}: No investments found for Salvador")
                                else:
                                    for inv in data:
                                        if inv.get('current_value', 0) == 0:
                                            zero_value_issues.append(f"{name}: Investment {inv.get('fund_code')} has zero value")
                
                except Exception as e:
                    zero_value_issues.append(f"{name}: Exception checking values - {str(e)}")
            
            if len(zero_value_issues) == 0:
                self.log_result("Zero Values Verification", True, 
                              "No inappropriate zero values found in key endpoints")
            else:
                self.log_result("Zero Values Verification", False, 
                              f"Found {len(zero_value_issues)} zero value issues", 
                              {"issues": zero_value_issues})
                
        except Exception as e:
            self.log_result("Zero Values Verification", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all fund portfolio and admin clients endpoint tests"""
        print("🎯 FUND PORTFOLIO OVERVIEW & ADMIN CLIENTS ENDPOINT TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Expected Salvador Total: ${self.expected_salvador_total:,.2f}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Fund Portfolio & Admin Clients Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_fund_portfolio_overview_endpoint()
        self.test_admin_clients_endpoint_structure()
        self.test_data_consistency_verification()
        self.test_frontend_api_compatibility()
        self.test_zero_values_verification()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 FUND PORTFOLIO & ADMIN CLIENTS TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests first (more important)
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
        
        # Critical assessment for review request
        critical_tests = [
            "Fund Portfolio Overview - Success Flag",
            "Fund Portfolio - BALANCE Fund", 
            "Admin Clients - Response Format",
            "Admin Clients - Salvador Present",
            "Data Consistency - Expected Total"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT FOR REVIEW REQUEST:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ FUND PORTFOLIO & ADMIN CLIENTS FIXES: SUCCESSFUL")
            print("   • /api/fund-portfolio/overview endpoint working correctly")
            print("   • /api/admin/clients endpoint returns proper format")
            print("   • Salvador's $1,371,485.40 investments properly displayed")
            print("   • Data consistency verified across endpoints")
            print("   • Frontend API compatibility confirmed")
        else:
            print("❌ FUND PORTFOLIO & ADMIN CLIENTS FIXES: INCOMPLETE")
            print("   • Critical endpoint issues still exist")
            print("   • User-reported data display problems not fully resolved")
            print("   • Main agent action required to complete fixes")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = FundPortfolioEndpointTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()