#!/usr/bin/env python3
"""
FIDUS Backend Testing Suite - Client Portal Redemptions Endpoint Fix
Testing the specific fix for Alejandro's account redemptions endpoint
"""

import requests
import json
import sys
from datetime import datetime, timezone
import time

# Configuration
BACKEND_URL = "https://vps-bridge-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}")
    print(f"🎯 {title}")
    print(f"{'='*80}{Colors.END}")

def print_test(test_name):
    print(f"\n{Colors.BLUE}🧪 Testing: {test_name}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.WHITE}ℹ️ {message}{Colors.END}")

class RedemptionsTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        
    def add_result(self, test_name, passed, message="", details=None):
        """Add test result to tracking"""
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'details': details,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        if passed:
            print_success(f"{test_name}: {message}")
        else:
            print_error(f"{test_name}: {message}")
            if details:
                print_info(f"Details: {details}")

    def login_as_admin(self):
        """Login as admin to get JWT token"""
        print_test("Admin Authentication")
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.add_result("Admin Login", True, f"Successfully authenticated as {data.get('name', 'admin')}")
                return True
            else:
                self.add_result("Admin Login", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.add_result("Admin Login", False, f"Request failed: {str(e)}")
            return False

    def login_as_alejandro(self):
        """Login as Alejandro (client) to get JWT token"""
        print_test("Alejandro Client Authentication")
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "username": "alejandro_mariscal",
                "password": "password123",
                "user_type": "client"
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.client_token = data.get('token')
                user_id = data.get('id', 'unknown')
                self.add_result("Alejandro Login", True, f"Successfully authenticated as {data.get('name', 'Alejandro')} (ID: {user_id})")
                return True
            else:
                self.add_result("Alejandro Login", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.add_result("Alejandro Login", False, f"Request failed: {str(e)}")
            return False

    def test_redemptions_endpoint(self):
        """Test the main redemptions endpoint for Alejandro"""
        print_test("GET /api/redemptions/client/client_alejandro")
        
        if not self.client_token:
            self.add_result("Redemptions Endpoint", False, "No client token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = requests.get(f"{API_BASE}/redemptions/client/client_alejandro", 
                                  headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic response structure
                if not data.get('success'):
                    self.add_result("Redemptions Endpoint", False, "Response success=false", data)
                    return False
                
                available_redemptions = data.get('available_redemptions', [])
                if not available_redemptions:
                    self.add_result("Redemptions Endpoint", False, "No available_redemptions found", data)
                    return False
                
                self.add_result("Redemptions Endpoint", True, 
                              f"Successfully retrieved {len(available_redemptions)} investments")
                return data
                
            else:
                self.add_result("Redemptions Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.add_result("Redemptions Endpoint", False, f"Request failed: {str(e)}")
            return False

    def verify_investment_data(self, redemptions_data):
        """Verify the structure and content of investment data"""
        print_test("Investment Data Verification")
        
        if not redemptions_data:
            self.add_result("Investment Data", False, "No redemptions data provided")
            return False
            
        available_redemptions = redemptions_data.get('available_redemptions', [])
        
        # Look for CORE and BALANCE investments
        core_investment = None
        balance_investment = None
        
        for investment in available_redemptions:
            fund_code = investment.get('fund_code', '').upper()
            if fund_code == 'CORE':
                core_investment = investment
            elif fund_code == 'BALANCE':
                balance_investment = investment
        
        # Verify CORE Fund Investment
        if core_investment:
            self.verify_core_investment(core_investment)
        else:
            self.add_result("CORE Investment", False, "CORE fund investment not found")
        
        # Verify BALANCE Fund Investment  
        if balance_investment:
            self.verify_balance_investment(balance_investment)
        else:
            self.add_result("BALANCE Investment", False, "BALANCE fund investment not found")
            
        return core_investment and balance_investment

    def verify_core_investment(self, investment):
        """Verify CORE fund investment data"""
        print_test("CORE Fund Investment Verification")
        
        required_fields = [
            'principal_amount', 'deposit_date', 'interest_start_date', 
            'status', 'fund_code', 'fund_name', 'redemption_frequency', 
            'redemption_schedule'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in investment:
                missing_fields.append(field)
        
        if missing_fields:
            self.add_result("CORE Required Fields", False, f"Missing fields: {missing_fields}")
        else:
            self.add_result("CORE Required Fields", True, "All required fields present")
        
        # Verify specific values
        principal = investment.get('principal_amount')
        if principal == 18151.41:
            self.add_result("CORE Principal Amount", True, f"${principal}")
        else:
            self.add_result("CORE Principal Amount", False, f"Expected $18,151.41, got ${principal}")
        
        # Verify fund details
        fund_code = investment.get('fund_code')
        if fund_code == 'CORE':
            self.add_result("CORE Fund Code", True, fund_code)
        else:
            self.add_result("CORE Fund Code", False, f"Expected 'CORE', got '{fund_code}'")
        
        redemption_freq = investment.get('redemption_frequency')
        if redemption_freq == 'monthly':
            self.add_result("CORE Redemption Frequency", True, redemption_freq)
        else:
            self.add_result("CORE Redemption Frequency", False, f"Expected 'monthly', got '{redemption_freq}'")
        
        # Verify redemption schedule
        schedule = investment.get('redemption_schedule', [])
        if len(schedule) >= 10:  # Should have ~14 monthly payments
            self.add_result("CORE Redemption Schedule", True, f"{len(schedule)} payments scheduled")
            self.verify_redemption_schedule(schedule, "CORE")
        else:
            self.add_result("CORE Redemption Schedule", False, f"Expected ~14 payments, got {len(schedule)}")

    def verify_balance_investment(self, investment):
        """Verify BALANCE fund investment data"""
        print_test("BALANCE Fund Investment Verification")
        
        required_fields = [
            'principal_amount', 'deposit_date', 'interest_start_date', 
            'status', 'fund_code', 'fund_name', 'redemption_frequency', 
            'redemption_schedule'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in investment:
                missing_fields.append(field)
        
        if missing_fields:
            self.add_result("BALANCE Required Fields", False, f"Missing fields: {missing_fields}")
        else:
            self.add_result("BALANCE Required Fields", True, "All required fields present")
        
        # Verify specific values
        principal = investment.get('principal_amount')
        if principal == 100000:
            self.add_result("BALANCE Principal Amount", True, f"${principal}")
        else:
            self.add_result("BALANCE Principal Amount", False, f"Expected $100,000, got ${principal}")
        
        # Verify fund details
        fund_code = investment.get('fund_code')
        if fund_code == 'BALANCE':
            self.add_result("BALANCE Fund Code", True, fund_code)
        else:
            self.add_result("BALANCE Fund Code", False, f"Expected 'BALANCE', got '{fund_code}'")
        
        redemption_freq = investment.get('redemption_frequency')
        if redemption_freq == 'quarterly':
            self.add_result("BALANCE Redemption Frequency", True, redemption_freq)
        else:
            self.add_result("BALANCE Redemption Frequency", False, f"Expected 'quarterly', got '{redemption_freq}'")
        
        # Verify redemption schedule
        schedule = investment.get('redemption_schedule', [])
        if len(schedule) >= 3:  # Should have ~4 quarterly payments
            self.add_result("BALANCE Redemption Schedule", True, f"{len(schedule)} payments scheduled")
            self.verify_redemption_schedule(schedule, "BALANCE")
        else:
            self.add_result("BALANCE Redemption Schedule", False, f"Expected ~4 payments, got {len(schedule)}")

    def verify_redemption_schedule(self, schedule, fund_type):
        """Verify redemption schedule structure and data integrity"""
        print_test(f"{fund_type} Redemption Schedule Structure")
        
        nan_amounts = []
        invalid_dates = []
        missing_fields = []
        
        required_payment_fields = [
            'payment_number', 'date', 'amount', 'type', 'status', 'can_redeem', 'days_until'
        ]
        
        for i, payment in enumerate(schedule):
            # Check for required fields
            for field in required_payment_fields:
                if field not in payment:
                    missing_fields.append(f"Payment {i+1}: {field}")
            
            # Check for NaN amounts
            amount = payment.get('amount')
            if amount is None or (isinstance(amount, float) and str(amount).lower() == 'nan'):
                nan_amounts.append(f"Payment {i+1}")
            elif isinstance(amount, (int, float)) and amount <= 0:
                nan_amounts.append(f"Payment {i+1}: ${amount}")
            
            # Check for invalid dates
            date_str = payment.get('date')
            if not date_str or date_str == 'Invalid Date':
                invalid_dates.append(f"Payment {i+1}")
            else:
                try:
                    datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    invalid_dates.append(f"Payment {i+1}: {date_str}")
        
        # Report results
        if not nan_amounts:
            self.add_result(f"{fund_type} No NaN Amounts", True, "All amounts are valid numbers")
        else:
            self.add_result(f"{fund_type} No NaN Amounts", False, f"NaN amounts found: {nan_amounts}")
        
        if not invalid_dates:
            self.add_result(f"{fund_type} Valid Dates", True, "All dates are valid ISO strings")
        else:
            self.add_result(f"{fund_type} Valid Dates", False, f"Invalid dates found: {invalid_dates}")
        
        if not missing_fields:
            self.add_result(f"{fund_type} Complete Fields", True, "All required fields present")
        else:
            self.add_result(f"{fund_type} Complete Fields", False, f"Missing fields: {missing_fields}")
        
        # Check for final payment
        final_payments = [p for p in schedule if p.get('type') == 'final']
        if final_payments:
            self.add_result(f"{fund_type} Final Payment", True, f"Final payment found with type='final'")
        else:
            self.add_result(f"{fund_type} Final Payment", False, "No final payment with type='final' found")

    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print_header("FIDUS Client Portal Redemptions Endpoint Testing")
        print_info(f"Backend URL: {BACKEND_URL}")
        print_info(f"Testing Alejandro's redemptions endpoint fix")
        print_info(f"Started at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Step 1: Login as Alejandro
        if not self.login_as_alejandro():
            print_error("Cannot proceed without client authentication")
            return False
        
        # Step 2: Test redemptions endpoint
        redemptions_data = self.test_redemptions_endpoint()
        if not redemptions_data:
            print_error("Cannot proceed without redemptions data")
            return False
        
        # Step 3: Verify investment data structure
        self.verify_investment_data(redemptions_data)
        
        # Print summary
        self.print_test_summary()
        
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print_header("TEST SUMMARY")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['passed']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Colors.BOLD}📊 OVERALL RESULTS:{Colors.END}")
        print(f"   Total Tests: {total_tests}")
        print(f"   {Colors.GREEN}✅ Passed: {passed_tests}{Colors.END}")
        print(f"   {Colors.RED}❌ Failed: {failed_tests}{Colors.END}")
        print(f"   {Colors.CYAN}📈 Success Rate: {success_rate:.1f}%{Colors.END}")
        
        if failed_tests > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ FAILED TESTS:{Colors.END}")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   • {result['test']}: {result['message']}")
        
        print(f"\n{Colors.BOLD}🎯 CRITICAL SUCCESS CRITERIA:{Colors.END}")
        
        # Check critical criteria
        critical_tests = [
            "Alejandro Login",
            "Redemptions Endpoint", 
            "CORE Required Fields",
            "BALANCE Required Fields",
            "CORE No NaN Amounts",
            "BALANCE No NaN Amounts",
            "CORE Valid Dates",
            "BALANCE Valid Dates"
        ]
        
        critical_passed = 0
        for test_name in critical_tests:
            test_result = next((r for r in self.test_results if r['test'] == test_name), None)
            if test_result and test_result['passed']:
                print(f"   {Colors.GREEN}✅ {test_name}{Colors.END}")
                critical_passed += 1
            else:
                print(f"   {Colors.RED}❌ {test_name}{Colors.END}")
        
        critical_success_rate = (critical_passed / len(critical_tests) * 100)
        
        print(f"\n{Colors.BOLD}🎯 CRITICAL SUCCESS RATE: {critical_success_rate:.1f}% ({critical_passed}/{len(critical_tests)}){Colors.END}")
        
        if critical_success_rate >= 90:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 REDEMPTIONS ENDPOINT FIX VERIFICATION: SUCCESS!{Colors.END}")
            print(f"{Colors.GREEN}   The Client Portal Redemptions endpoint fix is working correctly.{Colors.END}")
            print(f"{Colors.GREEN}   Alejandro can access his investment data without $NaN or Invalid Date issues.{Colors.END}")
        elif critical_success_rate >= 70:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ REDEMPTIONS ENDPOINT FIX VERIFICATION: PARTIAL SUCCESS{Colors.END}")
            print(f"{Colors.YELLOW}   Most functionality is working but some issues remain.{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ REDEMPTIONS ENDPOINT FIX VERIFICATION: FAILED{Colors.END}")
            print(f"{Colors.RED}   Critical issues prevent proper redemptions functionality.{Colors.END}")

def main():
    """Main execution function"""
    tester = RedemptionsTester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Testing interrupted by user{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {str(e)}{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())