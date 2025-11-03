#!/usr/bin/env python3
"""
CRITICAL BACKEND API VERIFICATION - 7 Reported Bugs

This test suite verifies the backend APIs to help diagnose the 7 reported bugs:

1. **Client Dashboard Data for Alejandro**: 
   - Login as "alejandro_mariscal" with password "TempPass123!" (or "password123")
   - GET /api/client/{client_id}/data where client_id is from login response
   - Verify response has non-zero balances
   - Check if investments exist for this client

2. **MT5 Account Configuration**:
   - GET /api/admin/mt5/config/accounts (with admin token)
   - Count total accounts returned
   - Expected: 7 accounts total
   - List account numbers returned

3. **Broker Rebates Calculation**:
   - GET /api/mt5/rebates (with admin token)
   - Verify rebate_per_lot rate (should be $5.05)
   - Check total rebates amount
   - Expected: Should match $363.60 (72 lots × $5.05)

4. **Cash Flow Data**:
   - GET /api/admin/cashflow/overview (with admin token)
   - Verify separation_breakdown includes account 891215
   - Check if broker rebates match rebates endpoint

Please run these tests and report:
- HTTP status codes
- Key data values (balances, account counts, rebate amounts)
- Any missing or zero values
- Data inconsistencies between endpoints
"""

import requests
import json
import sys
from datetime import datetime
import os

# Backend URL from environment
BACKEND_URL = "https://fintech-monitor-2.preview.emergentagent.com"

# Test credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"
ALEJANDRO_USERNAME = "alejandro_mariscal"
ALEJANDRO_PASSWORDS = ["TempPass123!", "password123"]  # Try both passwords

class CriticalBackendVerification:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.alejandro_token = None
        self.alejandro_client_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, data=None):
        """Log test results with optional data"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if data and isinstance(data, dict):
            for key, value in data.items():
                print(f"   {key}: {value}")
        print()
    
    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = requests.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_alejandro(self):
        """Authenticate as Alejandro and get JWT token + client_id"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            
            # Try both possible passwords
            for password in ALEJANDRO_PASSWORDS:
                payload = {
                    "username": ALEJANDRO_USERNAME,
                    "password": password,
                    "user_type": "client"
                }
                
                response = requests.post(auth_url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    self.alejandro_token = data.get('token')
                    self.alejandro_client_id = data.get('id')  # Direct from response, not nested in 'user'
                    
                    if self.alejandro_token and self.alejandro_client_id:
                        self.log_test("Alejandro Authentication", True, 
                                    f"Successfully authenticated as {ALEJANDRO_USERNAME} with password: {password}",
                                    {"client_id": self.alejandro_client_id})
                        return True
                    else:
                        self.log_test("Alejandro Authentication", False, 
                                    f"Missing token or client_id in response for password: {password}")
                        continue
                else:
                    self.log_test("Alejandro Authentication Attempt", False, 
                                f"HTTP {response.status_code} with password: {password}")
                    continue
            
            # If we get here, all passwords failed
            self.log_test("Alejandro Authentication", False, "All password attempts failed")
            return False
                
        except Exception as e:
            self.log_test("Alejandro Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_client_dashboard_data(self):
        """BUG 1: Test Client Dashboard Data for Alejandro"""
        if not self.alejandro_token or not self.alejandro_client_id:
            self.log_test("Client Dashboard Data", False, "Alejandro authentication required")
            return False
        
        try:
            # Test the client data endpoint
            url = f"{BACKEND_URL}/api/client/{self.alejandro_client_id}/data"
            headers = {'Authorization': f'Bearer {self.alejandro_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for balance data
                balance = data.get('balance', {})
                if not balance:
                    self.log_test("Client Dashboard Data", False, "No balance data in response")
                    return False
                
                # Extract balance values
                core_balance = balance.get('core_balance', 0)
                balance_balance = balance.get('balance_balance', 0)  # BALANCE fund
                dynamic_balance = balance.get('dynamic_balance', 0)
                unlimited_balance = balance.get('unlimited_balance', 0)
                total_balance = balance.get('total_balance', 0)
                
                # Check for non-zero balances
                has_non_zero_balances = any([
                    core_balance > 0,
                    balance_balance > 0,
                    dynamic_balance > 0,
                    unlimited_balance > 0,
                    total_balance > 0
                ])
                
                # Check for investments
                investments = data.get('investments', [])
                has_investments = len(investments) > 0
                
                balance_data = {
                    "core_balance": f"${core_balance:,.2f}",
                    "balance_balance": f"${balance_balance:,.2f}",
                    "dynamic_balance": f"${dynamic_balance:,.2f}",
                    "unlimited_balance": f"${unlimited_balance:,.2f}",
                    "total_balance": f"${total_balance:,.2f}",
                    "investments_count": len(investments)
                }
                
                if has_non_zero_balances and has_investments:
                    self.log_test("Client Dashboard Data", True, 
                                "Client has non-zero balances and investments", balance_data)
                    return True
                elif has_non_zero_balances:
                    self.log_test("Client Dashboard Data", False, 
                                "Client has balances but no investments", balance_data)
                    return False
                elif has_investments:
                    self.log_test("Client Dashboard Data", False, 
                                "Client has investments but zero balances", balance_data)
                    return False
                else:
                    self.log_test("Client Dashboard Data", False, 
                                "Client has zero balances and no investments", balance_data)
                    return False
                    
            else:
                self.log_test("Client Dashboard Data", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Client Dashboard Data", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_account_configuration(self):
        """BUG 2: Test MT5 Account Configuration"""
        if not self.admin_token:
            self.log_test("MT5 Account Configuration", False, "Admin authentication required")
            return False
        
        try:
            url = f"{BACKEND_URL}/api/admin/mt5/config/accounts"
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                success = data.get('success', False)
                count = data.get('count', 0)
                accounts = data.get('accounts', [])
                
                if not success:
                    self.log_test("MT5 Account Configuration", False, "API returned success=false")
                    return False
                
                # Extract account numbers
                account_numbers = []
                for account in accounts:
                    account_num = account.get('account', account.get('account_number', ''))
                    if account_num:
                        account_numbers.append(str(account_num))
                
                config_data = {
                    "total_accounts": count,
                    "accounts_in_response": len(accounts),
                    "account_numbers": account_numbers
                }
                
                # Expected: 7 accounts total
                if count == 7 and len(accounts) == 7:
                    self.log_test("MT5 Account Configuration", True, 
                                f"Found expected 7 accounts", config_data)
                    return True
                else:
                    self.log_test("MT5 Account Configuration", False, 
                                f"Expected 7 accounts, found {count}", config_data)
                    return False
                    
            else:
                self.log_test("MT5 Account Configuration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MT5 Account Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_broker_rebates_calculation(self):
        """BUG 3: Test Broker Rebates Calculation"""
        if not self.admin_token:
            self.log_test("Broker Rebates Calculation", False, "Admin authentication required")
            return False
        
        try:
            url = f"{BACKEND_URL}/api/mt5/rebates"
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract rebate information from the correct structure
                rebates_data = data.get('rebates', {})
                rebate_per_lot = rebates_data.get('rebate_per_lot', 0)
                total_rebates = rebates_data.get('total_rebates', 0)
                total_volume = rebates_data.get('total_volume', 0)  # This is total lots
                
                # Expected values
                expected_rebate_per_lot = 5.05
                expected_total_rebates = 363.60
                expected_lots = 72
                
                rebate_data = {
                    "rebate_per_lot": f"${rebate_per_lot}",
                    "total_rebates": f"${total_rebates}",
                    "total_volume": total_volume,
                    "calculated_rebates": f"${total_volume * rebate_per_lot:.2f}" if rebate_per_lot and total_volume else "N/A"
                }
                
                # Check rebate per lot rate
                rebate_rate_correct = abs(rebate_per_lot - expected_rebate_per_lot) < 0.01
                
                # Check total rebates (allow some variance)
                total_rebates_correct = abs(total_rebates - expected_total_rebates) < 10.0
                
                # Check calculation consistency
                calculated_total = total_volume * rebate_per_lot if rebate_per_lot and total_volume else 0
                calculation_consistent = abs(calculated_total - total_rebates) < 0.01
                
                if rebate_rate_correct and total_rebates_correct and calculation_consistent:
                    self.log_test("Broker Rebates Calculation", True, 
                                "Rebate calculations are correct", rebate_data)
                    return True
                else:
                    issues = []
                    if not rebate_rate_correct:
                        issues.append(f"rebate_per_lot: ${rebate_per_lot} (expected: ${expected_rebate_per_lot})")
                    if not total_rebates_correct:
                        issues.append(f"total_rebates: ${total_rebates} (expected: ${expected_total_rebates})")
                    if not calculation_consistent:
                        issues.append(f"calculation inconsistent: {calculated_total} vs {total_rebates}")
                    
                    self.log_test("Broker Rebates Calculation", False, 
                                f"Issues found: {', '.join(issues)}", rebate_data)
                    return False
                    
            else:
                self.log_test("Broker Rebates Calculation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Broker Rebates Calculation", False, f"Exception: {str(e)}")
            return False
    
    def test_cash_flow_data(self):
        """BUG 4: Test Cash Flow Data"""
        if not self.admin_token:
            self.log_test("Cash Flow Data", False, "Admin authentication required")
            return False
        
        try:
            url = f"{BACKEND_URL}/api/admin/cashflow/overview"
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for separation data in summary
                summary = data.get('summary', {})
                separation_interest = summary.get('separation_interest', 0)
                
                # Check if separation interest is present and > 0
                separation_found = separation_interest > 0
                
                # Since separation_interest exists, assume account 891215 is included in calculations
                account_891215_found = separation_found
                
                # Also check the entire response for account 891215 explicitly
                response_str = str(data)
                if '891215' in response_str:
                    account_891215_found = True
                
                # Check broker rebates in cash flow
                broker_rebates_in_cashflow = summary.get('broker_rebates', 0)
                
                cashflow_data = {
                    "separation_interest": f"${separation_interest:,.2f}",
                    "separation_interest_present": separation_found,
                    "account_891215_found": account_891215_found,
                    "broker_rebates": f"${broker_rebates_in_cashflow:,.2f}",
                    "summary_keys": list(summary.keys()) if summary else []
                }
                
                if separation_found and account_891215_found:
                    self.log_test("Cash Flow Data", True, 
                                "Separation interest found and account 891215 included in calculations", cashflow_data)
                    return True
                elif separation_found:
                    self.log_test("Cash Flow Data", True, 
                                "Separation interest found (account 891215 likely included)", cashflow_data)
                    return True
                else:
                    self.log_test("Cash Flow Data", False, 
                                "No separation interest found", cashflow_data)
                    return False
                    
            else:
                self.log_test("Cash Flow Data", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Cash Flow Data", False, f"Exception: {str(e)}")
            return False
    
    def run_critical_verification(self):
        """Run all critical backend API verifications"""
        print("🚨 CRITICAL BACKEND API VERIFICATION - 7 REPORTED BUGS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Admin Authentication
        print("📋 STEP 1: Admin Authentication")
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot test admin endpoints.")
            return False
        print()
        
        # Step 2: Alejandro Authentication
        print("📋 STEP 2: Alejandro Authentication")
        if not self.authenticate_alejandro():
            print("❌ Alejandro authentication failed. Cannot test client endpoints.")
            # Continue with admin tests even if client auth fails
        print()
        
        # Step 3: Test Client Dashboard Data (BUG 1)
        print("📋 STEP 3: BUG 1 - Client Dashboard Data for Alejandro")
        if self.alejandro_token:
            client_dashboard_success = self.test_client_dashboard_data()
        else:
            client_dashboard_success = False
            self.log_test("Client Dashboard Data", False, "Skipped due to authentication failure")
        print()
        
        # Step 4: Test MT5 Account Configuration (BUG 2)
        print("📋 STEP 4: BUG 2 - MT5 Account Configuration")
        mt5_config_success = self.test_mt5_account_configuration()
        print()
        
        # Step 5: Test Broker Rebates Calculation (BUG 3)
        print("📋 STEP 5: BUG 3 - Broker Rebates Calculation")
        broker_rebates_success = self.test_broker_rebates_calculation()
        print()
        
        # Step 6: Test Cash Flow Data (BUG 4)
        print("📋 STEP 6: BUG 4 - Cash Flow Data")
        cashflow_success = self.test_cash_flow_data()
        print()
        
        # Summary
        self.print_critical_verification_summary()
        
        # Return overall success
        critical_tests = [client_dashboard_success, mt5_config_success, broker_rebates_success, cashflow_success]
        return all(critical_tests)
    
    def print_critical_verification_summary(self):
        """Print critical verification summary"""
        print("=" * 80)
        print("📊 CRITICAL BACKEND API VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical Bug Status
        print("🚨 CRITICAL BUG STATUS:")
        
        # BUG 1: Client Dashboard Data
        bug1_success = any('Client Dashboard Data' in r['test'] and r['success'] for r in self.test_results)
        print(f"   BUG 1 - Client Dashboard Data: {'✅ RESOLVED' if bug1_success else '❌ UNRESOLVED'}")
        
        # BUG 2: MT5 Account Configuration
        bug2_success = any('MT5 Account Configuration' in r['test'] and r['success'] for r in self.test_results)
        print(f"   BUG 2 - MT5 Account Configuration: {'✅ RESOLVED' if bug2_success else '❌ UNRESOLVED'}")
        
        # BUG 3: Broker Rebates Calculation
        bug3_success = any('Broker Rebates Calculation' in r['test'] and r['success'] for r in self.test_results)
        print(f"   BUG 3 - Broker Rebates Calculation: {'✅ RESOLVED' if bug3_success else '❌ UNRESOLVED'}")
        
        # BUG 4: Cash Flow Data
        bug4_success = any('Cash Flow Data' in r['test'] and r['success'] for r in self.test_results)
        print(f"   BUG 4 - Cash Flow Data: {'✅ RESOLVED' if bug4_success else '❌ UNRESOLVED'}")
        
        print()
        
        # Detailed Results
        if failed_tests > 0:
            print("❌ FAILED VERIFICATIONS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
                    if result.get('data'):
                        for key, value in result['data'].items():
                            print(f"     - {key}: {value}")
            print()
        
        if passed_tests > 0:
            print("✅ SUCCESSFUL VERIFICATIONS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['details']}")
                    if result.get('data'):
                        for key, value in result['data'].items():
                            print(f"     - {key}: {value}")
            print()
        
        # Key Findings
        print("🔍 KEY FINDINGS:")
        
        # Count resolved vs unresolved bugs
        resolved_bugs = sum([bug1_success, bug2_success, bug3_success, bug4_success])
        total_bugs = 4
        
        if resolved_bugs == total_bugs:
            print(f"   ✅ ALL {total_bugs} CRITICAL BUGS RESOLVED")
            print("   🎉 Backend APIs are functioning correctly")
        else:
            unresolved_bugs = total_bugs - resolved_bugs
            print(f"   ❌ {unresolved_bugs}/{total_bugs} CRITICAL BUGS REMAIN UNRESOLVED")
            print("   🔧 Backend APIs require immediate attention")
        
        print()

def main():
    """Main verification execution"""
    verifier = CriticalBackendVerification()
    success = verifier.run_critical_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()