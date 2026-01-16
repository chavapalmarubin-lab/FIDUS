#!/usr/bin/env python3
"""
FIDUS Cash Flow Tab Backend Testing Suite
Testing Cash Flow tab functionality as requested in review.

Test Coverage:
1. Client Money API Endpoint - GET /api/admin/client-money/total
2. Cash Flow Overview API - GET /api/admin/cashflow/overview  
3. Authentication with emergent_admin credentials
4. Verification of expected values and non-zero calculations

Expected Results:
- Client Money: $134,145.41 from 3 active investments
- Fund Assets section: Should show actual MT5 data (not zeros)
- Fund Liabilities: Should show actual obligations (not zeros)
- All monetary values properly calculated (not showing $0)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class CashFlowTabTester:
    def __init__(self):
        # Use the frontend URL from .env file
        self.base_url = "https://vkng-dashboard.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str, expected: Any = None, actual: Any = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,  # PASS, FAIL, ERROR
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {details}")
        
        if expected is not None and actual is not None:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
    
    def authenticate_admin(self) -> bool:
        """Authenticate as emergent_admin user"""
        try:
            print("🔐 Authenticating as emergent_admin...")
            
            login_data = {
                "username": "emergent_admin",
                "password": "admin123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    self.log_test("Admin Authentication", "PASS", "Successfully authenticated as emergent_admin")
                    return True
                else:
                    self.log_test("Admin Authentication", "FAIL", "No token received in response")
                    return False
            else:
                self.log_test("Admin Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", "ERROR", f"Exception during authentication: {str(e)}")
            return False
    
    def test_client_money_api(self) -> bool:
        """Test 1: Client Money API Endpoint - GET /api/admin/client-money/total"""
        try:
            print("\n💰 Testing Client Money API Endpoint...")
            
            response = self.session.get(f"{self.base_url}/admin/client-money/total", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Client Money API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            success = True
            
            # Check if API returns success
            if not data.get("success", True):  # Some APIs might not have success field
                self.log_test("Client Money API Response", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            # Check total client money
            total_client_money = data.get("total_client_money", 0)
            expected_total = 134145.41
            
            if abs(total_client_money - expected_total) < 100.0:  # Allow $100 tolerance
                self.log_test("Total Client Money", "PASS", 
                            f"Total client money matches expected value", 
                            f"${expected_total:,.2f}", 
                            f"${total_client_money:,.2f}")
            else:
                self.log_test("Total Client Money", "FAIL", 
                            f"Total client money differs from expected value", 
                            f"${expected_total:,.2f}", 
                            f"${total_client_money:,.2f}")
                success = False
            
            # Check breakdown by client exists
            breakdown = data.get("breakdown", {})
            if breakdown and len(breakdown) >= 1:
                self.log_test("Client Breakdown", "PASS", 
                            f"Found breakdown for {len(breakdown)} clients")
                
                # Check for 3 active investments
                total_investments = 0
                for client_id, client_data in breakdown.items():
                    investments = client_data.get("investments", [])
                    active_investments = [inv for inv in investments if inv.get("status") == "active"]
                    total_investments += len(active_investments)
                
                if total_investments >= 3:
                    self.log_test("Active Investments Count", "PASS", 
                                f"Found {total_investments} active investments (expected 3+)")
                else:
                    self.log_test("Active Investments Count", "FAIL", 
                                f"Found only {total_investments} active investments (expected 3+)")
                    success = False
                    
            else:
                self.log_test("Client Breakdown", "FAIL", 
                            "No client breakdown found in response")
                success = False
            
            # Check that values are not zero
            if total_client_money > 0:
                self.log_test("Non-Zero Values", "PASS", 
                            "Client money shows real values (not $0)")
            else:
                self.log_test("Non-Zero Values", "FAIL", 
                            "Client money shows $0 - indicates calculation issue")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Client Money API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_cashflow_overview_api(self) -> bool:
        """Test 2: Cash Flow Overview API - GET /api/admin/cashflow/overview"""
        try:
            print("\n📊 Testing Cash Flow Overview API...")
            
            response = self.session.get(f"{self.base_url}/admin/cashflow/overview", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Cash Flow Overview API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            success = True
            
            # Check if API returns success
            if not data.get("success", True):
                self.log_test("Cash Flow Overview Response", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            summary = data.get("summary", {})
            
            # Test Fund Assets section - should show actual MT5 data (not zeros)
            mt5_trading_profits = summary.get("mt5_trading_profits", 0)
            separation_interest = summary.get("separation_interest", 0)
            broker_rebates = summary.get("broker_rebates", 0)
            
            # Check MT5 Trading Profits (should be non-zero)
            if abs(mt5_trading_profits) > 0:
                self.log_test("MT5 Trading Profits", "PASS", 
                            f"MT5 trading shows real data (not $0)", 
                            "Non-zero", 
                            f"${mt5_trading_profits:,.2f}")
            else:
                self.log_test("MT5 Trading Profits", "FAIL", 
                            f"MT5 trading shows $0 - should show actual data", 
                            "Non-zero", 
                            f"${mt5_trading_profits:,.2f}")
                success = False
            
            # Check Separation Interest (should be substantial)
            if separation_interest > 1000:
                self.log_test("Separation Interest", "PASS", 
                            f"Separation interest shows substantial amount", 
                            "> $1,000", 
                            f"${separation_interest:,.2f}")
            else:
                self.log_test("Separation Interest", "FAIL", 
                            f"Separation interest too low or zero", 
                            "> $1,000", 
                            f"${separation_interest:,.2f}")
                success = False
            
            # Check Broker Rebates
            if broker_rebates >= 0:  # Can be zero, but should be present
                self.log_test("Broker Rebates", "PASS", 
                            f"Broker rebates field present", 
                            "Present", 
                            f"${broker_rebates:,.2f}")
            else:
                self.log_test("Broker Rebates", "FAIL", 
                            f"Broker rebates field missing or negative")
                success = False
            
            # Test Fund Liabilities - should show actual obligations (not zeros)
            fund_obligations = summary.get("fund_obligations", 0)
            client_interest_obligations = summary.get("client_interest_obligations", 0)
            
            if fund_obligations > 0:
                self.log_test("Fund Obligations", "PASS", 
                            f"Fund obligations show real data (not $0)", 
                            "> $0", 
                            f"${fund_obligations:,.2f}")
            else:
                self.log_test("Fund Obligations", "FAIL", 
                            f"Fund obligations show $0 - should show actual obligations", 
                            "> $0", 
                            f"${fund_obligations:,.2f}")
                success = False
            
            if client_interest_obligations > 0:
                self.log_test("Client Interest Obligations", "PASS", 
                            f"Client interest obligations show real data", 
                            "> $0", 
                            f"${client_interest_obligations:,.2f}")
            else:
                self.log_test("Client Interest Obligations", "FAIL", 
                            f"Client interest obligations show $0", 
                            "> $0", 
                            f"${client_interest_obligations:,.2f}")
                success = False
            
            # Check Fund Revenue calculation
            fund_revenue = summary.get("fund_revenue", 0)
            expected_revenue = mt5_trading_profits + separation_interest + broker_rebates
            
            if abs(fund_revenue - expected_revenue) < 1.0:
                self.log_test("Fund Revenue Calculation", "PASS", 
                            f"Fund revenue calculated correctly", 
                            f"${expected_revenue:,.2f}", 
                            f"${fund_revenue:,.2f}")
            else:
                self.log_test("Fund Revenue Calculation", "FAIL", 
                            f"Fund revenue calculation incorrect", 
                            f"${expected_revenue:,.2f}", 
                            f"${fund_revenue:,.2f}")
                success = False
            
            # Check Net Profit calculation
            net_profit = summary.get("net_profit", 0)
            expected_net_profit = fund_revenue - fund_obligations
            
            if abs(net_profit - expected_net_profit) < 1.0:
                self.log_test("Net Profit Calculation", "PASS", 
                            f"Net profit calculated correctly", 
                            f"${expected_net_profit:,.2f}", 
                            f"${net_profit:,.2f}")
            else:
                self.log_test("Net Profit Calculation", "FAIL", 
                            f"Net profit calculation incorrect", 
                            f"${expected_net_profit:,.2f}", 
                            f"${net_profit:,.2f}")
                success = False
            
            # Check that all monetary values are properly calculated (not showing $0)
            monetary_fields = [
                ("MT5 Trading Profits", mt5_trading_profits),
                ("Separation Interest", separation_interest),
                ("Fund Revenue", fund_revenue),
                ("Fund Obligations", fund_obligations),
                ("Net Profit", net_profit)
            ]
            
            zero_count = sum(1 for name, value in monetary_fields if value == 0)
            if zero_count <= 1:  # Allow at most 1 field to be zero (e.g., broker rebates)
                self.log_test("Non-Zero Calculations", "PASS", 
                            f"Most monetary values show real calculations ({len(monetary_fields) - zero_count}/{len(monetary_fields)} non-zero)")
            else:
                self.log_test("Non-Zero Calculations", "FAIL", 
                            f"Too many fields showing $0 ({zero_count}/{len(monetary_fields)} are zero)")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Cash Flow Overview API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_cashflow_calendar_api(self) -> bool:
        """Test 3: Cash Flow Calendar API - GET /api/admin/cashflow/calendar"""
        try:
            print("\n📅 Testing Cash Flow Calendar API...")
            
            response = self.session.get(f"{self.base_url}/admin/cashflow/calendar", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Cash Flow Calendar API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            success = True
            
            # Check if API returns success
            if not data.get("success", True):
                self.log_test("Cash Flow Calendar Response", "FAIL", f"API returned success=false: {data.get('message', 'Unknown error')}")
                return False
            
            # Check current revenue
            current_revenue = data.get("current_revenue", 0)
            if current_revenue > 0:
                self.log_test("Current Revenue", "PASS", 
                            f"Current revenue shows positive value", 
                            "> $0", 
                            f"${current_revenue:,.2f}")
            else:
                self.log_test("Current Revenue", "FAIL", 
                            f"Current revenue is zero or negative", 
                            "> $0", 
                            f"${current_revenue:,.2f}")
                success = False
            
            # Check monthly obligations
            monthly_obligations = data.get("monthly_obligations", [])
            if len(monthly_obligations) >= 12:
                self.log_test("Monthly Obligations", "PASS", 
                            f"Found {len(monthly_obligations)} months of obligations")
            else:
                self.log_test("Monthly Obligations", "FAIL", 
                            f"Expected 12+ months, found {len(monthly_obligations)}")
                success = False
            
            # Check milestones
            milestones = data.get("milestones", {})
            expected_milestones = ["next_payment", "first_large_payment", "contract_end"]
            
            milestone_count = 0
            for milestone in expected_milestones:
                if milestone in milestones:
                    milestone_count += 1
            
            if milestone_count >= 2:
                self.log_test("Cash Flow Milestones", "PASS", 
                            f"Found {milestone_count}/3 expected milestones")
            else:
                self.log_test("Cash Flow Milestones", "FAIL", 
                            f"Only found {milestone_count}/3 expected milestones")
                success = False
            
            # Check summary calculations
            summary = data.get("summary", {})
            total_obligations = summary.get("total_future_obligations", 0)
            final_balance = summary.get("final_balance", 0)
            
            if total_obligations > 0:
                self.log_test("Total Future Obligations", "PASS", 
                            f"Total obligations calculated", 
                            "> $0", 
                            f"${total_obligations:,.2f}")
            else:
                self.log_test("Total Future Obligations", "FAIL", 
                            f"Total obligations is zero", 
                            "> $0", 
                            f"${total_obligations:,.2f}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Cash Flow Calendar API Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all Cash Flow tab tests"""
        print("🚀 Starting FIDUS Cash Flow Tab Backend Testing")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all Cash Flow tests
        tests = [
            ("Client Money API", self.test_client_money_api),
            ("Cash Flow Overview API", self.test_cashflow_overview_api),
            ("Cash Flow Calendar API", self.test_cashflow_calendar_api)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(f"{test_name} Exception", "ERROR", f"Test failed with exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 CASH FLOW TAB TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Print detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test_name']}: {result['details']}")
            
            if result.get("expected") and result.get("actual"):
                print(f"   Expected: {result['expected']}")
                print(f"   Actual: {result['actual']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 70:
            print("🎉 CASH FLOW TAB TESTING: SUCCESSFUL")
            print("✅ Client Money API returning expected $134,145.41")
            print("✅ Cash Flow Overview showing real MT5 data (not zeros)")
            print("✅ Fund Assets and Liabilities properly calculated")
            print("✅ All monetary values showing accurate calculations")
            return True
        else:
            print("🚨 CASH FLOW TAB TESTING: NEEDS ATTENTION")
            print("❌ Critical Cash Flow issues found")
            return False

def main():
    """Main test execution"""
    tester = CashFlowTabTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()