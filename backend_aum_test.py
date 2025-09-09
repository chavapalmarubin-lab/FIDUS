#!/usr/bin/env python3

import requests
import json
from datetime import datetime

class BackendAUMTester:
    def __init__(self, base_url="https://mt5-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, test_func):
        """Run a single test"""
        print(f"\n🔍 Testing {name}...")
        self.tests_run += 1
        
        try:
            success = test_func()
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED: {name}")
            else:
                print(f"❌ FAILED: {name}")
            return success
        except Exception as e:
            print(f"❌ ERROR in {name}: {str(e)}")
            return False

    def test_admin_portfolio_summary_aum_field(self):
        """Test that admin portfolio summary returns correct AUM field names"""
        try:
            url = f"{self.base_url}/api/admin/portfolio-summary"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"   Status code: {response.status_code}")
                return False
            
            data = response.json()
            
            # Check both field names exist
            has_aum = 'aum' in data
            has_total_aum = 'total_aum' in data
            
            if not has_aum:
                print("   Missing 'aum' field (required by frontend)")
                return False
                
            if not has_total_aum:
                print("   Missing 'total_aum' field (backend consistency)")
                return False
            
            aum_value = data['aum']
            total_aum_value = data['total_aum']
            
            # Values should match
            if aum_value != total_aum_value:
                print(f"   Field values don't match: aum={aum_value}, total_aum={total_aum_value}")
                return False
            
            # Should be the expected amount
            expected_aum = 161825.0
            if abs(aum_value - expected_aum) > 0.01:
                print(f"   AUM value incorrect: expected {expected_aum}, got {aum_value}")
                return False
            
            print(f"   ✅ Both 'aum' and 'total_aum' fields present with correct value: ${aum_value:,.2f}")
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False

    def test_aum_calculation_accuracy(self):
        """Test that AUM calculation matches expected CORE + BALANCE amounts"""
        try:
            url = f"{self.base_url}/api/admin/portfolio-summary"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            # Check fund breakdown
            fund_breakdown = data.get('fund_breakdown', {})
            
            core_amount = fund_breakdown.get('CORE', {}).get('amount', 0)
            balance_amount = fund_breakdown.get('BALANCE', {}).get('amount', 0)
            
            expected_core = 86825.0
            expected_balance = 75000.0
            
            if abs(core_amount - expected_core) > 0.01:
                print(f"   CORE amount incorrect: expected {expected_core}, got {core_amount}")
                return False
                
            if abs(balance_amount - expected_balance) > 0.01:
                print(f"   BALANCE amount incorrect: expected {expected_balance}, got {balance_amount}")
                return False
            
            total_calculated = core_amount + balance_amount
            aum_value = data.get('aum', 0)
            
            if abs(total_calculated - aum_value) > 0.01:
                print(f"   Calculation mismatch: breakdown total={total_calculated}, aum={aum_value}")
                return False
            
            print(f"   ✅ AUM calculation correct: CORE ${core_amount:,.2f} + BALANCE ${balance_amount:,.2f} = ${aum_value:,.2f}")
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False

    def test_allocation_percentages(self):
        """Test that allocation percentages are calculated correctly"""
        try:
            url = f"{self.base_url}/api/admin/portfolio-summary"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            allocation = data.get('allocation', {})
            fund_breakdown = data.get('fund_breakdown', {})
            total_aum = data.get('aum', 0)
            
            if total_aum == 0:
                print("   Total AUM is zero, cannot test percentages")
                return False
            
            # Check CORE percentage
            core_amount = fund_breakdown.get('CORE', {}).get('amount', 0)
            core_percentage = allocation.get('CORE', 0)
            expected_core_percentage = (core_amount / total_aum) * 100
            
            if abs(core_percentage - expected_core_percentage) > 0.1:
                print(f"   CORE percentage incorrect: expected {expected_core_percentage:.2f}%, got {core_percentage}%")
                return False
            
            # Check BALANCE percentage
            balance_amount = fund_breakdown.get('BALANCE', {}).get('amount', 0)
            balance_percentage = allocation.get('BALANCE', 0)
            expected_balance_percentage = (balance_amount / total_aum) * 100
            
            if abs(balance_percentage - expected_balance_percentage) > 0.1:
                print(f"   BALANCE percentage incorrect: expected {expected_balance_percentage:.2f}%, got {balance_percentage}%")
                return False
            
            print(f"   ✅ Allocation percentages correct: CORE {core_percentage}%, BALANCE {balance_percentage}%")
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False

    def test_client_count_accuracy(self):
        """Test that client count reflects actual clients with investments"""
        try:
            url = f"{self.base_url}/api/admin/portfolio-summary"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            client_count = data.get('client_count', 0)
            
            # Should be 2 clients (Gerardo and Salvador based on the expected AUM)
            expected_client_count = 2
            
            if client_count != expected_client_count:
                print(f"   Client count incorrect: expected {expected_client_count}, got {client_count}")
                return False
            
            print(f"   ✅ Client count correct: {client_count} clients with investments")
            return True
            
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all AUM-related tests"""
        print("🎯 BACKEND AUM TESTING - ADMIN PORTFOLIO SUMMARY ENDPOINT")
        print("=" * 70)
        
        tests = [
            ("AUM Field Names Compatibility", self.test_admin_portfolio_summary_aum_field),
            ("AUM Calculation Accuracy", self.test_aum_calculation_accuracy),
            ("Allocation Percentages", self.test_allocation_percentages),
            ("Client Count Accuracy", self.test_client_count_accuracy),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        print("\n" + "=" * 70)
        print(f"🎯 RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Admin portfolio summary endpoint working correctly!")
            print("✅ Frontend should now display correct AUM value of $161,825")
            return True
        else:
            print("❌ Some tests failed - issues remain with portfolio summary endpoint")
            return False

def main():
    tester = BackendAUMTester()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    main()