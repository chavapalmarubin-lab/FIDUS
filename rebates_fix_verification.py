#!/usr/bin/env python3
"""
REBATES FIX VERIFICATION - Quick Test

Test that Cash Flow now shows correct rebate amount of $363.60:

1. **Login as Admin**:
   - POST /api/auth/login
   - Credentials: admin/password123

2. **Check Cash Flow Rebates**:
   - GET /api/admin/cashflow/overview?timeframe=3_months
   - Extract broker_rebates value
   - **Expected**: Should be $363.60 (or very close)
   - **Previous (broken)**: Was $291

3. **Verify Client Alejandro**:
   - Login as alejandro_mariscal (password: password123 or TempPass123!)
   - GET /api/client/{client_id}/data
   - **Expected**: Should show non-zero balances for CORE ($18,151.41) and BALANCE ($100,000)

Please report:
- Broker rebates amount from Cash Flow
- Alejandro's total_balance from client data endpoint
- HTTP status codes
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://alloc-refresh.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Alejandro credentials
ALEJANDRO_USERNAME = "alejandro_mariscal"
ALEJANDRO_PASSWORDS = ["password123", "TempPass123!"]

class RebatesFixVerification:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.alejandro_token = None
        self.alejandro_client_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, http_status=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        status_info = f" (HTTP {http_status})" if http_status else ""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "http_status": http_status,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}{status_info}: {test_name}")
        if details:
            print(f"   Details: {details}")
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
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}", response.status_code)
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", response.status_code)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Authentication failed: {response.text}", response.status_code)
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
                    self.alejandro_client_id = data.get('id')  # Get client_id from login response
                    
                    if self.alejandro_token and self.alejandro_client_id:
                        self.log_test("Alejandro Authentication", True, f"Successfully authenticated as {ALEJANDRO_USERNAME} with password: {password}, client_id: {self.alejandro_client_id}", response.status_code)
                        return True
                    else:
                        self.log_test("Alejandro Authentication", False, f"Missing token or client_id in response with password: {password}", response.status_code)
                        continue
                else:
                    print(f"   Tried password '{password}': HTTP {response.status_code}")
                    continue
            
            # If we get here, all passwords failed
            self.log_test("Alejandro Authentication", False, f"All passwords failed for {ALEJANDRO_USERNAME}")
            return False
                
        except Exception as e:
            self.log_test("Alejandro Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_cash_flow_rebates(self):
        """Test Cash Flow Rebates - GET /api/admin/cashflow/overview?timeframe=3_months"""
        try:
            url = f"{BACKEND_URL}/api/admin/cashflow/overview?timeframe=3_months"
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract broker_rebates value
                summary = data.get('summary', {})
                broker_rebates = summary.get('broker_rebates', 0)
                
                # Expected: Should be $363.60 (or very close)
                expected_rebates = 363.60
                tolerance = 5.0  # Allow $5 tolerance
                
                if abs(broker_rebates - expected_rebates) <= tolerance:
                    self.log_test("Cash Flow Broker Rebates", True, f"Broker rebates: ${broker_rebates:.2f} (expected: ${expected_rebates:.2f})", response.status_code)
                    return True, broker_rebates
                else:
                    self.log_test("Cash Flow Broker Rebates", False, f"Broker rebates: ${broker_rebates:.2f} (expected: ${expected_rebates:.2f}) - difference: ${abs(broker_rebates - expected_rebates):.2f}", response.status_code)
                    return False, broker_rebates
                
            else:
                self.log_test("Cash Flow Rebates Endpoint", False, f"Failed to get cash flow data: {response.text}", response.status_code)
                return False, 0
                
        except Exception as e:
            self.log_test("Cash Flow Rebates Endpoint", False, f"Exception: {str(e)}")
            return False, 0
    
    def test_alejandro_client_data(self):
        """Test Alejandro's Client Data - GET /api/client/{client_id}/data"""
        try:
            if not self.alejandro_client_id:
                self.log_test("Alejandro Client Data", False, "No client_id available - authentication may have failed")
                return False, 0
            
            url = f"{BACKEND_URL}/api/client/{self.alejandro_client_id}/data"
            headers = {'Authorization': f'Bearer {self.alejandro_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract balance information
                balance = data.get('balance', {})
                core_balance = balance.get('core_balance', 0)
                balance_balance = balance.get('balance_balance', 0)  # BALANCE fund
                total_balance = balance.get('total_balance', 0)
                
                # Expected: CORE ($18,151.41) and BALANCE ($100,000)
                expected_core = 18151.41
                expected_balance = 100000.0
                tolerance = 1000.0  # Allow $1000 tolerance
                
                core_success = abs(core_balance - expected_core) <= tolerance
                balance_success = abs(balance_balance - expected_balance) <= tolerance
                
                details = f"CORE: ${core_balance:.2f} (expected: ${expected_core:.2f}), BALANCE: ${balance_balance:.2f} (expected: ${expected_balance:.2f}), Total: ${total_balance:.2f}"
                
                if core_success and balance_success and total_balance > 0:
                    self.log_test("Alejandro Client Balances", True, details, response.status_code)
                    return True, total_balance
                else:
                    failure_reasons = []
                    if not core_success:
                        failure_reasons.append(f"CORE balance off by ${abs(core_balance - expected_core):.2f}")
                    if not balance_success:
                        failure_reasons.append(f"BALANCE balance off by ${abs(balance_balance - expected_balance):.2f}")
                    if total_balance == 0:
                        failure_reasons.append("Total balance is zero")
                    
                    self.log_test("Alejandro Client Balances", False, f"{details} - Issues: {', '.join(failure_reasons)}", response.status_code)
                    return False, total_balance
                
            else:
                self.log_test("Alejandro Client Data Endpoint", False, f"Failed to get client data: {response.text}", response.status_code)
                return False, 0
                
        except Exception as e:
            self.log_test("Alejandro Client Data Endpoint", False, f"Exception: {str(e)}")
            return False, 0
    
    def run_verification(self):
        """Run complete rebates fix verification"""
        print("🔍 REBATES FIX VERIFICATION - Quick Test")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate as Admin
        print("📋 STEP 1: Login as Admin")
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot test cash flow.")
            return False
        print()
        
        # Step 2: Check Cash Flow Rebates
        print("📋 STEP 2: Check Cash Flow Rebates")
        rebates_success, broker_rebates = self.test_cash_flow_rebates()
        print()
        
        # Step 3: Authenticate as Alejandro
        print("📋 STEP 3: Login as Alejandro")
        if not self.authenticate_alejandro():
            print("❌ Alejandro authentication failed. Cannot test client data.")
            alejandro_success = False
            total_balance = 0
        else:
            print()
            
            # Step 4: Check Alejandro's Client Data
            print("📋 STEP 4: Verify Alejandro's Client Data")
            alejandro_success, total_balance = self.test_alejandro_client_data()
            print()
        
        # Summary
        self.print_verification_summary(rebates_success, broker_rebates, alejandro_success, total_balance)
        
        # Return overall success
        return rebates_success and alejandro_success
    
    def print_verification_summary(self, rebates_success, broker_rebates, alejandro_success, total_balance):
        """Print verification summary"""
        print("=" * 60)
        print("📊 REBATES FIX VERIFICATION SUMMARY")
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
        
        # Key Results
        print("🎯 KEY VERIFICATION RESULTS:")
        print(f"   {'✅' if rebates_success else '❌'} Broker Rebates Amount: ${broker_rebates:.2f}")
        print(f"   {'✅' if alejandro_success else '❌'} Alejandro's Total Balance: ${total_balance:.2f}")
        print()
        
        # HTTP Status Codes
        print("🌐 HTTP STATUS CODES:")
        for result in self.test_results:
            if result.get('http_status'):
                print(f"   {result['test']}: HTTP {result['http_status']}")
        print()
        
        # Detailed Results
        if failed_tests > 0:
            print("❌ FAILED VERIFICATIONS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ SUCCESSFUL VERIFICATIONS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        print()
        
        # Final Assessment
        print("🔍 FINAL ASSESSMENT:")
        if rebates_success and alejandro_success:
            print("   ✅ REBATES FIX VERIFICATION SUCCESSFUL")
            print("   🎉 Cash Flow shows correct rebate amount and Alejandro's balances are correct")
        else:
            print("   ❌ REBATES FIX VERIFICATION FAILED")
            if not rebates_success:
                print("   🔧 Cash Flow rebates amount needs attention")
            if not alejandro_success:
                print("   🔧 Alejandro's client data needs attention")
        
        print()

def main():
    """Main verification execution"""
    verifier = RebatesFixVerification()
    success = verifier.run_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()