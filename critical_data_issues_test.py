#!/usr/bin/env python3
"""
CRITICAL DATA DISPLAY ISSUES INVESTIGATION TEST
==============================================

This test investigates the specific critical issues reported by user:

1. **Salvador Palma Missing from Clients List**: 
   - Check `/api/admin/clients` vs `/api/clients/all` endpoints
   - Verify why Salvador (client_003) isn't appearing in admin client management

2. **Investment Values All Zero**:
   - Check `/api/fund-portfolio/overview` endpoint 
   - Verify why $1,371,485.40 in Salvador's investments isn't showing

3. **Lilian Limon AML/KYC Conversion**:
   - Find/create AML/KYC approval endpoint 
   - Check for manual review approval functionality

4. **MT5 Accounts Empty**:
   - Check `/api/mt5/admin/accounts` endpoint
   - Verify DooTechnology (9928326) and VT Markets (15759667) accounts

Expected Results:
- Salvador Palma appears in clients list
- Fund portfolio shows $1.37M total
- MT5 accounts show both brokers
- Way to approve Lilian's AML/KYC status
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://auth-troubleshoot-14.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CriticalDataIssuesTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.critical_issues = []
        
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
        
        # Track critical issues
        if not success and any(keyword in test_name.lower() for keyword in ['salvador', 'investment', 'mt5', 'aml']):
            self.critical_issues.append(result)
    
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
    
    def test_salvador_clients_list_issue(self):
        """ISSUE 1: Salvador Palma Missing from Clients List"""
        print("\n🔍 INVESTIGATING ISSUE 1: Salvador Palma Missing from Clients List")
        print("-" * 60)
        
        # Test multiple client endpoints
        endpoints_to_test = [
            ("/admin/clients", "Admin Clients Endpoint"),
            ("/clients/all", "All Clients Endpoint"),
            ("/admin/clients/client_003", "Specific Salvador Client"),
            ("/clients/client_003", "Direct Client Access")
        ]
        
        salvador_found_in = []
        salvador_missing_from = []
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    salvador_found = False
                    
                    # Check if Salvador is in the response
                    if isinstance(data, list):
                        for item in data:
                            if (item.get('id') == 'client_003' or 
                                'SALVADOR' in str(item.get('name', '')).upper() or
                                'salvador.palma' in str(item.get('email', '')).lower() or
                                'chava@alyarglobal.com' in str(item.get('email', '')).lower()):
                                salvador_found = True
                                salvador_found_in.append(name)
                                self.log_result(f"Salvador Found - {name}", True, 
                                              f"Salvador found in {endpoint}", {"client_data": item})
                                break
                    elif isinstance(data, dict):
                        if (data.get('id') == 'client_003' or 
                            'SALVADOR' in str(data.get('name', '')).upper() or
                            'salvador.palma' in str(data.get('email', '')).lower() or
                            'chava@alyarglobal.com' in str(data.get('email', '')).lower()):
                            salvador_found = True
                            salvador_found_in.append(name)
                            self.log_result(f"Salvador Found - {name}", True, 
                                          f"Salvador found in {endpoint}", {"client_data": data})
                    
                    if not salvador_found:
                        salvador_missing_from.append(name)
                        self.log_result(f"Salvador Missing - {name}", False, 
                                      f"Salvador NOT found in {endpoint}", 
                                      {"endpoint": endpoint, "response_type": type(data).__name__, 
                                       "response_length": len(data) if isinstance(data, (list, dict)) else "unknown"})
                else:
                    self.log_result(f"Endpoint Error - {name}", False, 
                                  f"HTTP {response.status_code} for {endpoint}", 
                                  {"status_code": response.status_code, "response": response.text[:500]})
                    
            except Exception as e:
                self.log_result(f"Endpoint Exception - {name}", False, 
                              f"Exception testing {endpoint}: {str(e)}")
        
        # Summary for Issue 1
        if salvador_found_in:
            print(f"\n✅ Salvador found in: {', '.join(salvador_found_in)}")
        if salvador_missing_from:
            print(f"❌ Salvador missing from: {', '.join(salvador_missing_from)}")
    
    def test_investment_values_zero_issue(self):
        """ISSUE 2: Investment Values All Zero"""
        print("\n🔍 INVESTIGATING ISSUE 2: Investment Values All Zero")
        print("-" * 60)
        
        # Test fund portfolio and investment endpoints
        investment_endpoints = [
            ("/fund-portfolio/overview", "Fund Portfolio Overview"),
            ("/admin/fund-portfolio/overview", "Admin Fund Portfolio"),
            ("/investments/client/client_003", "Salvador's Investments"),
            ("/admin/investments", "All Admin Investments"),
            ("/admin/fund-performance/dashboard", "Fund Performance Dashboard"),
            ("/admin/cashflow/overview", "Cash Flow Overview")
        ]
        
        total_investment_value = 0
        investment_data_found = False
        
        for endpoint, name in investment_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Look for investment values
                    values_found = []
                    
                    if isinstance(data, list):
                        for item in data:
                            # Check for various value fields
                            for field in ['current_value', 'principal_amount', 'total_value', 'amount', 'balance']:
                                if field in item and item[field] > 0:
                                    values_found.append(f"{field}: ${item[field]:,.2f}")
                                    total_investment_value += item[field]
                                    investment_data_found = True
                    
                    elif isinstance(data, dict):
                        # Check for aggregate values
                        for field in ['total_aum', 'total_investments', 'total_value', 'total_assets', 'total_balance']:
                            if field in data and data[field] > 0:
                                values_found.append(f"{field}: ${data[field]:,.2f}")
                                total_investment_value += data[field]
                                investment_data_found = True
                    
                    if values_found:
                        self.log_result(f"Investment Values - {name}", True, 
                                      f"Found values in {endpoint}: {', '.join(values_found)}")
                    else:
                        self.log_result(f"Investment Values - {name}", False, 
                                      f"No investment values found in {endpoint}", 
                                      {"data_sample": str(data)[:500] if data else "empty"})
                else:
                    self.log_result(f"Investment Endpoint - {name}", False, 
                                  f"HTTP {response.status_code} for {endpoint}")
                    
            except Exception as e:
                self.log_result(f"Investment Exception - {name}", False, 
                              f"Exception testing {endpoint}: {str(e)}")
        
        # Check if we found the expected $1,371,485.40
        expected_value = 1371485.40
        if investment_data_found:
            if abs(total_investment_value - expected_value) < 1000:  # Allow some variance
                self.log_result("Expected Investment Value", True, 
                              f"Total investment value close to expected: ${total_investment_value:,.2f}")
            else:
                self.log_result("Expected Investment Value", False, 
                              f"Total investment value mismatch: found ${total_investment_value:,.2f}, expected ${expected_value:,.2f}")
        else:
            self.log_result("Investment Data", False, "No investment data found in any endpoint")
    
    def test_lilian_limon_aml_kyc_issue(self):
        """ISSUE 3: Lilian Limon AML/KYC Conversion"""
        print("\n🔍 INVESTIGATING ISSUE 3: Lilian Limon AML/KYC Conversion")
        print("-" * 60)
        
        # Look for AML/KYC related endpoints
        aml_endpoints = [
            ("/admin/aml-kyc", "AML/KYC Management"),
            ("/admin/clients/pending", "Pending Clients"),
            ("/admin/registration/applications", "Registration Applications"),
            ("/admin/prospects", "Prospects Management"),
            ("/aml-kyc/status", "AML/KYC Status"),
            ("/admin/clients/approval", "Client Approval")
        ]
        
        lilian_found = False
        aml_endpoints_available = []
        
        for endpoint, name in aml_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    aml_endpoints_available.append(name)
                    
                    # Look for Lilian Limon
                    if isinstance(data, list):
                        for item in data:
                            if ('LILIAN' in str(item.get('name', '')).upper() or 
                                'LIMON' in str(item.get('name', '')).upper() or
                                'lilian' in str(item.get('email', '')).lower()):
                                lilian_found = True
                                self.log_result(f"Lilian Found - {name}", True, 
                                              f"Lilian found in {endpoint}", {"client_data": item})
                    
                    self.log_result(f"AML/KYC Endpoint - {name}", True, 
                                  f"Endpoint available: {endpoint}")
                elif response.status_code == 404:
                    self.log_result(f"AML/KYC Endpoint - {name}", False, 
                                  f"Endpoint not found: {endpoint}")
                else:
                    self.log_result(f"AML/KYC Endpoint - {name}", False, 
                                  f"HTTP {response.status_code} for {endpoint}")
                    
            except Exception as e:
                self.log_result(f"AML/KYC Exception - {name}", False, 
                              f"Exception testing {endpoint}: {str(e)}")
        
        # Test for approval endpoints
        approval_endpoints = [
            ("/admin/clients/approve", "POST", "Client Approval"),
            ("/admin/aml-kyc/approve", "POST", "AML/KYC Approval"),
            ("/admin/registration/finalize", "POST", "Registration Finalization")
        ]
        
        for endpoint, method, name in approval_endpoints:
            try:
                # Test if endpoint exists (without actually posting)
                if method == "POST":
                    response = self.session.post(f"{BACKEND_URL}{endpoint}", json={})
                    # We expect 400 or 422 for missing data, not 404 for missing endpoint
                    if response.status_code in [400, 422, 200]:
                        self.log_result(f"Approval Endpoint - {name}", True, 
                                      f"Approval endpoint available: {endpoint}")
                    elif response.status_code == 404:
                        self.log_result(f"Approval Endpoint - {name}", False, 
                                      f"Approval endpoint not found: {endpoint}")
                    else:
                        self.log_result(f"Approval Endpoint - {name}", False, 
                                      f"Unexpected response {response.status_code} for {endpoint}")
                        
            except Exception as e:
                self.log_result(f"Approval Exception - {name}", False, 
                              f"Exception testing {endpoint}: {str(e)}")
        
        if not lilian_found:
            self.log_result("Lilian Limon Search", False, "Lilian Limon not found in any AML/KYC endpoint")
    
    def test_mt5_accounts_empty_issue(self):
        """ISSUE 4: MT5 Accounts Empty"""
        print("\n🔍 INVESTIGATING ISSUE 4: MT5 Accounts Empty")
        print("-" * 60)
        
        # Test MT5 related endpoints
        mt5_endpoints = [
            ("/mt5/admin/accounts", "MT5 Admin Accounts"),
            ("/admin/mt5/accounts", "Admin MT5 Accounts"),
            ("/mt5/accounts", "MT5 Accounts"),
            ("/admin/mt5/client/client_003", "Salvador's MT5 Accounts"),
            ("/mt5/performance", "MT5 Performance"),
            ("/admin/mt5/overview", "MT5 Overview")
        ]
        
        mt5_accounts_found = []
        doo_technology_found = False
        vt_markets_found = False
        
        for endpoint, name in mt5_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        mt5_accounts_found.extend(data)
                        
                        # Look for specific accounts
                        for account in data:
                            login = str(account.get('login', ''))
                            broker = str(account.get('broker', ''))
                            
                            if login == '9928326' or 'DooTechnology' in broker:
                                doo_technology_found = True
                                self.log_result("DooTechnology Account", True, 
                                              f"DooTechnology account found: Login {login}")
                            
                            if login == '15759667' or 'VT Markets' in broker:
                                vt_markets_found = True
                                self.log_result("VT Markets Account", True, 
                                              f"VT Markets account found: Login {login}")
                        
                        self.log_result(f"MT5 Data - {name}", True, 
                                      f"Found {len(data)} MT5 accounts in {endpoint}")
                    else:
                        self.log_result(f"MT5 Data - {name}", False, 
                                      f"No MT5 accounts found in {endpoint}", 
                                      {"data": data})
                else:
                    self.log_result(f"MT5 Endpoint - {name}", False, 
                                  f"HTTP {response.status_code} for {endpoint}")
                    
            except Exception as e:
                self.log_result(f"MT5 Exception - {name}", False, 
                              f"Exception testing {endpoint}: {str(e)}")
        
        # Summary for MT5 accounts
        if mt5_accounts_found:
            self.log_result("MT5 Accounts Summary", True, 
                          f"Total MT5 accounts found: {len(mt5_accounts_found)}")
        else:
            self.log_result("MT5 Accounts Summary", False, "No MT5 accounts found in any endpoint")
        
        if not doo_technology_found:
            self.log_result("DooTechnology Missing", False, "DooTechnology account (9928326) not found")
        
        if not vt_markets_found:
            self.log_result("VT Markets Missing", False, "VT Markets account (15759667) not found")
    
    def test_system_health_check(self):
        """Test basic system health and connectivity"""
        print("\n🔍 SYSTEM HEALTH CHECK")
        print("-" * 30)
        
        health_endpoints = [
            ("/health", "Basic Health"),
            ("/health/ready", "Readiness Check"),
            ("/health/metrics", "Health Metrics")
        ]
        
        for endpoint, name in health_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    self.log_result(f"Health - {name}", True, f"System healthy: {endpoint}")
                else:
                    self.log_result(f"Health - {name}", False, f"Health issue: HTTP {response.status_code}")
            except Exception as e:
                self.log_result(f"Health - {name}", False, f"Health check failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all critical data issues investigation tests"""
        print("🚨 CRITICAL DATA DISPLAY ISSUES INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Run system health check first
        self.test_system_health_check()
        
        # Run all critical issue investigations
        self.test_salvador_clients_list_issue()
        self.test_investment_values_zero_issue()
        self.test_lilian_limon_aml_kyc_issue()
        self.test_mt5_accounts_empty_issue()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🚨 CRITICAL DATA ISSUES INVESTIGATION SUMMARY")
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
        
        # Critical Issues Summary
        print("🚨 CRITICAL ISSUES FOUND:")
        if self.critical_issues:
            for issue in self.critical_issues:
                print(f"   ❌ {issue['test']}: {issue['message']}")
        else:
            print("   ✅ No critical issues detected")
        print()
        
        # Issue-by-issue assessment
        print("📋 ISSUE-BY-ISSUE ASSESSMENT:")
        
        # Issue 1: Salvador Palma
        salvador_tests = [r for r in self.test_results if 'salvador' in r['test'].lower()]
        salvador_passed = sum(1 for r in salvador_tests if r['success'])
        print(f"   1. Salvador Palma Missing: {salvador_passed}/{len(salvador_tests)} tests passed")
        
        # Issue 2: Investment Values
        investment_tests = [r for r in self.test_results if 'investment' in r['test'].lower()]
        investment_passed = sum(1 for r in investment_tests if r['success'])
        print(f"   2. Investment Values Zero: {investment_passed}/{len(investment_tests)} tests passed")
        
        # Issue 3: Lilian AML/KYC
        aml_tests = [r for r in self.test_results if 'aml' in r['test'].lower() or 'lilian' in r['test'].lower()]
        aml_passed = sum(1 for r in aml_tests if r['success'])
        print(f"   3. Lilian AML/KYC: {aml_passed}/{len(aml_tests)} tests passed")
        
        # Issue 4: MT5 Accounts
        mt5_tests = [r for r in self.test_results if 'mt5' in r['test'].lower()]
        mt5_passed = sum(1 for r in mt5_tests if r['success'])
        print(f"   4. MT5 Accounts Empty: {mt5_passed}/{len(mt5_tests)} tests passed")
        
        print()
        
        # Overall assessment
        critical_issues_resolved = (
            salvador_passed >= len(salvador_tests) * 0.5 and
            investment_passed >= len(investment_tests) * 0.5 and
            mt5_passed >= len(mt5_tests) * 0.5
        )
        
        print("🎯 OVERALL ASSESSMENT:")
        if critical_issues_resolved:
            print("✅ CRITICAL ISSUES: MOSTLY RESOLVED")
            print("   Most reported issues appear to be working correctly.")
            print("   System may be ready for user verification.")
        else:
            print("❌ CRITICAL ISSUES: REQUIRE IMMEDIATE ATTENTION")
            print("   Multiple critical issues confirmed.")
            print("   Main agent action required before user verification.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = CriticalDataIssuesTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()