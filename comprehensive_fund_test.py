#!/usr/bin/env python3
"""
Comprehensive Fund Performance Management System Backend Testing
Testing the corrected system with specific validation criteria from review request
"""

import requests
import sys
from datetime import datetime
import json

class ComprehensiveFundTester:
    def __init__(self, base_url="https://fund-performance.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
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
        """Test admin login with credentials from review request"""
        success, response = self.run_test(
            "Admin Login (admin/password123)",
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
            self.admin_token = response.get('token')
            print(f"   Admin authenticated: {response.get('name', 'Unknown')}")
        return success

    def test_fund_performance_gaps_detailed(self):
        """Test Fund Performance Gaps API with detailed validation"""
        headers = {'Content-Type': 'application/json'}
        if self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
            
        success, response = self.run_test(
            "Fund Performance Gaps API - Detailed Validation",
            "GET",
            "api/admin/fund-performance/gaps",
            200,
            headers=headers
        )
        
        if success:
            gaps = response.get('performance_gaps', [])
            print(f"   Performance gaps found: {len(gaps)}")
            
            # Find Salvador Palma (client_003) BALANCE fund
            salvador_gap = None
            for gap in gaps:
                if gap.get('client_id') == 'client_003' and gap.get('fund_code') == 'BALANCE':
                    salvador_gap = gap
                    break
            
            if salvador_gap:
                print(f"   ✅ SALVADOR PALMA BALANCE FUND FOUND:")
                
                # Extract values
                principal = salvador_gap.get('principal_amount', 0)
                expected_perf = salvador_gap.get('expected_performance', 0)
                actual_mt5 = salvador_gap.get('actual_mt5_performance', 0)
                gap_amount = salvador_gap.get('gap_amount', 0)
                gap_percentage = salvador_gap.get('gap_percentage', 0)
                risk_level = salvador_gap.get('risk_level', 'N/A')
                deposit_date = salvador_gap.get('deposit_date', 'N/A')
                mt5_login = salvador_gap.get('mt5_login', 'N/A')
                
                print(f"      Principal Amount: ${principal:,.2f}")
                print(f"      Expected Performance: ${expected_perf:,.2f}")
                print(f"      Actual MT5 Performance: ${actual_mt5:,.2f}")
                print(f"      Gap Amount: ${gap_amount:,.2f}")
                print(f"      Gap Percentage: {gap_percentage:.1f}%")
                print(f"      Risk Level: {risk_level}")
                print(f"      Deposit Date: {deposit_date}")
                print(f"      MT5 Login: {mt5_login}")
                
                # Validation against review request expectations
                validations = {
                    "MT5 deposit amount": abs(principal - 1263485.40) < 1000,
                    "MT5 equity": abs(actual_mt5 - 638401.51) < 1000,
                    "Negative gap (underperformance)": gap_amount < 0,
                    "Critical risk level": risk_level == "CRITICAL",
                    "MT5 funding date": "2024-12-19" in str(deposit_date),
                    "MT5 login present": mt5_login != 'N/A' and mt5_login != 0
                }
                
                print(f"\n   📋 VALIDATION RESULTS:")
                all_passed = True
                for check, result in validations.items():
                    status = "✅ PASS" if result else "❌ FAIL"
                    print(f"      {status} {check}")
                    if not result:
                        all_passed = False
                
                if all_passed:
                    print(f"\n   🎉 ALL CRITICAL VALIDATIONS PASSED!")
                    return True
                else:
                    print(f"\n   ⚠️  Some validations failed")
                    return False
            else:
                print(f"   ❌ Salvador Palma BALANCE fund gap not found")
                return False
        
        return success

    def test_fund_performance_dashboard_detailed(self):
        """Test Fund Performance Dashboard API with detailed validation"""
        headers = {'Content-Type': 'application/json'}
        if self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
            
        success, response = self.run_test(
            "Fund Performance Dashboard API - Detailed Validation",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=headers
        )
        
        if success:
            dashboard = response.get('dashboard', {})
            fund_commitments = dashboard.get('fund_commitments', [])
            performance_gaps = dashboard.get('performance_gaps', [])
            risk_summary = dashboard.get('risk_summary', {})
            action_items = dashboard.get('action_items', [])
            
            print(f"   📊 DASHBOARD ANALYSIS:")
            print(f"      Fund commitments: {len(fund_commitments)}")
            print(f"      Performance gaps: {len(performance_gaps)}")
            print(f"      Risk summary: {risk_summary}")
            print(f"      Action items: {len(action_items)}")
            
            # Validation against review request expectations
            validations = {
                "BALANCE fund present": any('BALANCE' in str(f) for f in fund_commitments),
                "1 performance gap": len(performance_gaps) == 1,
                "1 critical risk": risk_summary.get('CRITICAL', 0) == 1,
                "Salvador action item": any('client_003' in str(item) or 'BALANCE' in str(item) for item in action_items)
            }
            
            print(f"\n   📋 DASHBOARD VALIDATION:")
            all_passed = True
            for check, result in validations.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"      {status} {check}")
                if not result:
                    all_passed = False
            
            # Show fund commitments details
            print(f"\n   📈 FUND COMMITMENTS DETAILS:")
            for fund in fund_commitments:
                if isinstance(fund, dict):
                    fund_code = fund.get('fund_code', 'N/A')
                    monthly_return = fund.get('monthly_return', 0)
                    print(f"      {fund_code}: {monthly_return}% monthly")
                else:
                    print(f"      {fund}")
            
            return all_passed
        
        return success

    def test_client_fund_performance_detailed(self):
        """Test Client Fund Performance API with detailed validation"""
        headers = {'Content-Type': 'application/json'}
        if self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
            
        success, response = self.run_test(
            "Client Fund Performance API - Salvador Palma Detailed",
            "GET",
            "api/admin/fund-performance/client/client_003",
            200,
            headers=headers
        )
        
        if success:
            client_comparison = response.get('client_comparison', {})
            funds = client_comparison.get('funds', [])
            overall_gap = client_comparison.get('overall_gap', 0)
            risk_level = client_comparison.get('risk_level', 'N/A')
            
            print(f"   👤 CLIENT PERFORMANCE ANALYSIS:")
            print(f"      Funds analyzed: {len(funds)}")
            print(f"      Overall gap: ${overall_gap:,.2f}")
            print(f"      Risk level: {risk_level}")
            
            if funds:
                balance_fund = funds[0] if funds else {}
                principal = balance_fund.get('principal_amount', 0)
                expected_value = balance_fund.get('expected_current_value', 0)
                actual_value = balance_fund.get('actual_current_value', 0)
                
                print(f"\n   💰 BALANCE FUND DETAILS:")
                print(f"      Principal Amount: ${principal:,.2f}")
                print(f"      Expected Current Value: ${expected_value:,.2f}")
                print(f"      Actual Current Value: ${actual_value:,.2f}")
                
                # Validation against review request expectations
                validations = {
                    "Principal matches MT5 deposit": abs(principal - 1263485.40) < 1000,
                    "Actual value matches MT5 equity": abs(actual_value - 638401.51) < 1000,
                    "Expected value ~$1,534,000": abs(expected_value - 1534000) < 100000,
                    "Overall gap negative": overall_gap < 0,
                    "High risk level": risk_level in ["HIGH", "CRITICAL"]
                }
                
                print(f"\n   📋 CLIENT PERFORMANCE VALIDATION:")
                all_passed = True
                for check, result in validations.items():
                    status = "✅ PASS" if result else "❌ FAIL"
                    print(f"      {status} {check}")
                    if not result:
                        all_passed = False
                
                return all_passed
        
        return success

    def test_client_investment_separation(self):
        """Test Client Investment API to verify separation of concerns"""
        success, response = self.run_test(
            "Client Investment API - Separation Verification",
            "GET",
            "api/investments/client/client_003",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"   🔄 CLIENT-ADMIN SEPARATION TEST:")
            print(f"      Client investments: {len(investments)}")
            
            balance_investment = None
            for inv in investments:
                if inv.get('fund_code') == 'BALANCE':
                    balance_investment = inv
                    break
            
            if balance_investment:
                client_current_value = balance_investment.get('current_value', 0)
                principal = balance_investment.get('principal_amount', 0)
                
                print(f"      Principal: ${principal:,.2f}")
                print(f"      Client View Current Value: ${client_current_value:,.2f}")
                
                # This should show FIDUS commitment view, not MT5 reality
                validations = {
                    "Principal matches MT5 deposit": abs(principal - 1263485.40) < 1000,
                    "Client sees FIDUS promises (~$1,547K)": abs(client_current_value - 1547000) < 100000,
                    "Client view != MT5 reality": abs(client_current_value - 638401.51) > 100000
                }
                
                print(f"\n   📋 SEPARATION VALIDATION:")
                all_passed = True
                for check, result in validations.items():
                    status = "✅ PASS" if result else "❌ FAIL"
                    print(f"      {status} {check}")
                    if not result:
                        all_passed = False
                
                if all_passed:
                    print(f"\n   🎉 CLIENT-ADMIN DATA SEPARATION WORKING CORRECTLY!")
                
                return all_passed
        
        return success

    def test_fund_commitments_detailed(self):
        """Test Fund Commitments API with detailed validation"""
        headers = {'Content-Type': 'application/json'}
        if self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
            
        success, response = self.run_test(
            "Fund Commitments API - Detailed Validation",
            "GET",
            "api/admin/fund-commitments",
            200,
            headers=headers
        )
        
        if success:
            commitments = response.get('fund_commitments', [])
            print(f"   📋 FUND COMMITMENTS ANALYSIS:")
            print(f"      Total funds: {len(commitments)}")
            
            expected_specs = {
                'BALANCE': {'rate': 2.5, 'minimum': 50000, 'redemption': 3}
            }
            
            found_funds = {}
            for commitment in commitments:
                if isinstance(commitment, dict):
                    fund_code = commitment.get('fund_code')
                    found_funds[fund_code] = commitment
                    monthly_return = commitment.get('monthly_return', 0)
                    minimum_investment = commitment.get('minimum_investment', 0)
                    redemption_frequency = commitment.get('redemption_frequency', 0)
                    
                    print(f"      {fund_code}: {monthly_return}% monthly, ${minimum_investment:,.0f} min, {redemption_frequency}mo redemption")
                else:
                    print(f"      {commitment}")
            
            # Validate BALANCE fund specifications
            balance_fund = found_funds.get('BALANCE', {})
            validations = {
                "BALANCE fund present": 'BALANCE' in found_funds,
                "BALANCE 2.5% monthly": balance_fund.get('monthly_return') == 2.5,
                "BALANCE $50K minimum": balance_fund.get('minimum_investment') == 50000,
                "BALANCE 3-month redemptions": balance_fund.get('redemption_frequency') == 3,
                "All 4 funds configured": len(found_funds) == 4
            }
            
            print(f"\n   📋 FUND SPECIFICATIONS VALIDATION:")
            all_passed = True
            for check, result in validations.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"      {status} {check}")
                if not result:
                    all_passed = False
            
            return all_passed
        
        return success

    def run_comprehensive_test(self):
        """Run comprehensive Fund Performance Management System test"""
        print("=" * 80)
        print("🚀 CORRECTED FUND PERFORMANCE MANAGEMENT SYSTEM")
        print("   COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print("Testing MT5 data as primary source with corrected investment amounts")
        print("Expected: Salvador Palma $1,263,485.40 → MT5 $638,401.51 (-58.4% gap)")
        print("=" * 80)
        
        # Test sequence based on review request priorities
        test_results = []
        
        # 1. Authentication
        test_results.append(("Admin Authentication", self.test_admin_login()))
        
        # 2. Fund Performance Gaps API (Priority 1)
        test_results.append(("Fund Performance Gaps", self.test_fund_performance_gaps_detailed()))
        
        # 3. Fund Performance Dashboard API (Priority 2)
        test_results.append(("Fund Performance Dashboard", self.test_fund_performance_dashboard_detailed()))
        
        # 4. Client Fund Performance API (Priority 3)
        test_results.append(("Client Fund Performance", self.test_client_fund_performance_detailed()))
        
        # 5. Client Investment API - Separation Verification (Priority 4)
        test_results.append(("Client-Admin Separation", self.test_client_investment_separation()))
        
        # 6. Fund Commitments API (Priority 5)
        test_results.append(("Fund Commitments", self.test_fund_commitments_detailed()))
        
        # Print comprehensive results
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        passed_tests = []
        failed_tests = []
        
        for test_name, result in test_results:
            if result:
                passed_tests.append(test_name)
                print(f"✅ PASS - {test_name}")
            else:
                failed_tests.append(test_name)
                print(f"❌ FAIL - {test_name}")
        
        print(f"\nOverall Results: {len(passed_tests)}/{len(test_results)} tests passed ({(len(passed_tests)/len(test_results)*100):.1f}%)")
        
        # Critical success indicators from review request
        if len(failed_tests) == 0:
            print("\n🎉 ALL CRITICAL SUCCESS INDICATORS ACHIEVED!")
            print("✅ MT5 data now primary source for admin performance analysis")
            print("✅ Correct investment amounts and dates from MT5 ($1,263,485.40)")
            print("✅ Only active funds (BALANCE) displayed in commitments")
            print("✅ Performance gap shows MT5 underperformance vs FIDUS commitments")
            print("✅ Client vs Admin data separation working correctly")
            return True
        else:
            print(f"\n⚠️  {len(failed_tests)} critical tests failed:")
            for test in failed_tests:
                print(f"   - {test}")
            print("\nSystem needs fixes before production readiness")
            return False

if __name__ == "__main__":
    tester = ComprehensiveFundTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)