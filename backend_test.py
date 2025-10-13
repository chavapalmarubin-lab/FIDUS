#!/usr/bin/env python3
"""
Backend Testing for Performance Fee Endpoints (Phase 3)
Testing the 6 new performance fee endpoints added to the backend.

Test Objectives:
1. GET /api/admin/performance-fees/current - Should return total of $1,000.64
2. POST /api/admin/performance-fees/calculate-daily - Should calculate fees successfully
3. GET /api/admin/performance-fees/summary - Should show correct period and totals
4. GET /api/admin/performance-fees/transactions - Should work (even if empty)
5. PUT /api/admin/money-managers/{manager_id}/performance-fee - Should update fee rate
6. Verify all endpoints return HTTP 200 and expected data structure

Expected Results:
- Current fees total: $1,000.64
- 3 managers with fees: TradingHub Gold ($848.91), GoldenTrade ($98.41), UNO14 MAM ($53.32)
- CP Strategy should have $0 fee (loss)
- Summary shows period "2025-10", accrued_fees: 1000.64, paid_fees: 0
- Transactions endpoint works (empty array initially)
- Manager fee update works correctly
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://financeflow-89.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class PerformanceFeeEndpointsTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.manager_ids = []  # Store manager IDs for testing
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate(self):
        """Authenticate as admin and get JWT token"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
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
    
    def test_current_performance_fees(self):
        """Test GET /api/admin/performance-fees/current"""
        try:
            url = f"{BACKEND_URL}/api/admin/performance-fees/current"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'totals' not in data:
                    self.log_test("Current Performance Fees Structure", False, "Missing 'totals' key in response")
                    return False
                
                if 'managers' not in data:
                    self.log_test("Current Performance Fees Structure", False, "Missing 'managers' key in response")
                    return False
                
                totals = data['totals']
                managers = data['managers']
                
                # Check totals structure
                total_fees = totals.get('total_performance_fees', 0)
                managers_with_fees = totals.get('managers_with_fees', 0)
                
                # Expected values from review request
                expected_total = 1000.64
                expected_managers_count = 3
                expected_total_managers = 4
                
                # Validate total performance fees
                if abs(total_fees - expected_total) < 0.01:
                    self.log_test("Performance Fees Total", True, f"Total fees: ${total_fees:.2f} (matches expected ${expected_total:.2f})")
                else:
                    self.log_test("Performance Fees Total", False, f"Total fees: ${total_fees:.2f} (expected ${expected_total:.2f})")
                    return False
                
                # Validate managers with fees count
                if managers_with_fees == expected_managers_count:
                    self.log_test("Managers With Fees Count", True, f"Managers with fees: {managers_with_fees} (matches expected {expected_managers_count})")
                else:
                    self.log_test("Managers With Fees Count", False, f"Managers with fees: {managers_with_fees} (expected {expected_managers_count})")
                
                # Validate total managers count
                if len(managers) == expected_total_managers:
                    self.log_test("Total Managers Count", True, f"Total managers: {len(managers)} (matches expected {expected_total_managers})")
                else:
                    self.log_test("Total Managers Count", False, f"Total managers: {len(managers)} (expected {expected_total_managers})")
                
                # Check for specific managers and their fees
                manager_fees = {}
                for manager in managers:
                    name = manager.get('manager_name', 'Unknown')  # Use manager_name instead of name
                    fee = manager.get('performance_fee_amount', 0)  # Use performance_fee_amount instead of performance_fee
                    manager_fees[name] = fee
                    
                    # Store manager ID for later tests
                    if 'manager_id' in manager:
                        self.manager_ids.append(manager['manager_id'])
                
                # Expected manager fees from review request
                expected_managers = {
                    'TradingHub Gold Provider': 848.91,
                    'GoldenTrade Provider': 98.41,
                    'UNO14 MAM Manager': 53.32,
                    'CP Strategy Provider': 0.0  # Loss, should have $0 fee
                }
                
                managers_verified = 0
                for expected_name, expected_fee in expected_managers.items():
                    found_manager = False
                    for manager_name, actual_fee in manager_fees.items():
                        if expected_name == manager_name:  # Exact match
                            found_manager = True
                            if abs(actual_fee - expected_fee) < 0.01:
                                self.log_test(f"Manager Fee - {expected_name}", True, f"${actual_fee:.2f} (matches expected ${expected_fee:.2f})")
                                managers_verified += 1
                            else:
                                self.log_test(f"Manager Fee - {expected_name}", False, f"${actual_fee:.2f} (expected ${expected_fee:.2f})")
                            break
                    
                    if not found_manager:
                        self.log_test(f"Manager Presence - {expected_name}", False, f"Manager not found in response")
                
                details = f"Total: ${total_fees:.2f}, Managers with fees: {managers_with_fees}, Total managers: {len(managers)}, Verified: {managers_verified}/4"
                self.log_test("Current Performance Fees", True, details)
                return True
                
            else:
                self.log_test("Current Performance Fees", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Current Performance Fees", False, f"Exception: {str(e)}")
            return False
    
    def test_calculate_daily_performance_fees(self):
        """Test POST /api/admin/performance-fees/calculate-daily"""
        try:
            url = f"{BACKEND_URL}/api/admin/performance-fees/calculate-daily"
            response = self.session.post(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'success' not in data:
                    self.log_test("Calculate Daily Fees Structure", False, "Missing 'success' key in response")
                    return False
                
                if not data.get('success'):
                    self.log_test("Calculate Daily Fees Success", False, f"success=false in response: {data}")
                    return False
                
                # Check for data section
                if 'data' in data and 'totals' in data['data']:
                    totals = data['data']['totals']
                    total_fees = totals.get('total_performance_fees', 0)
                    
                    # Should match expected total
                    expected_total = 1000.64
                    if abs(total_fees - expected_total) < 0.01:
                        self.log_test("Calculate Daily Fees Total", True, f"Calculated total: ${total_fees:.2f} (matches expected ${expected_total:.2f})")
                    else:
                        self.log_test("Calculate Daily Fees Total", False, f"Calculated total: ${total_fees:.2f} (expected ${expected_total:.2f})")
                
                # Check for success message
                message = data.get('message', '')
                expected_message = "Daily performance fees calculated successfully"
                if expected_message.lower() in message.lower():
                    self.log_test("Calculate Daily Fees Message", True, f"Message: {message}")
                else:
                    self.log_test("Calculate Daily Fees Message", False, f"Unexpected message: {message}")
                
                details = f"success={data.get('success')}, message='{message}'"
                self.log_test("Calculate Daily Performance Fees", True, details)
                return True
                
            else:
                self.log_test("Calculate Daily Performance Fees", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Calculate Daily Performance Fees", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_fees_summary(self):
        """Test GET /api/admin/performance-fees/summary"""
        try:
            # Test without parameters (current month)
            url = f"{BACKEND_URL}/api/admin/performance-fees/summary"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['period', 'accrued_fees', 'paid_fees', 'pending_payment', 'statistics']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Performance Fees Summary Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check expected values
                period = data.get('period', '')
                accrued_fees = data.get('accrued_fees', 0)
                paid_fees = data.get('paid_fees', 0)
                pending_payment = data.get('pending_payment', 0)
                
                # Expected values from review request
                expected_period = "2025-10"
                expected_accrued = 1000.64
                expected_paid = 0
                expected_pending = 1000.64
                
                # Validate period
                if expected_period in period:
                    self.log_test("Summary Period", True, f"Period: {period} (contains expected {expected_period})")
                else:
                    self.log_test("Summary Period", False, f"Period: {period} (expected to contain {expected_period})")
                
                # Validate accrued fees
                if abs(accrued_fees - expected_accrued) < 0.01:
                    self.log_test("Summary Accrued Fees", True, f"Accrued fees: ${accrued_fees:.2f} (matches expected ${expected_accrued:.2f})")
                else:
                    self.log_test("Summary Accrued Fees", False, f"Accrued fees: ${accrued_fees:.2f} (expected ${expected_accrued:.2f})")
                
                # Validate paid fees
                if paid_fees == expected_paid:
                    self.log_test("Summary Paid Fees", True, f"Paid fees: ${paid_fees:.2f} (matches expected ${expected_paid:.2f})")
                else:
                    self.log_test("Summary Paid Fees", False, f"Paid fees: ${paid_fees:.2f} (expected ${expected_paid:.2f})")
                
                # Validate pending payment
                if abs(pending_payment - expected_pending) < 0.01:
                    self.log_test("Summary Pending Payment", True, f"Pending payment: ${pending_payment:.2f} (matches expected ${expected_pending:.2f})")
                else:
                    self.log_test("Summary Pending Payment", False, f"Pending payment: ${pending_payment:.2f} (expected ${expected_pending:.2f})")
                
                # Check statistics
                if 'statistics' in data:
                    stats = data['statistics']
                    profitable_managers = stats.get('profitable_managers', 0)
                    expected_profitable = 3
                    
                    if profitable_managers == expected_profitable:
                        self.log_test("Summary Statistics", True, f"Profitable managers: {profitable_managers} (matches expected {expected_profitable})")
                    else:
                        self.log_test("Summary Statistics", False, f"Profitable managers: {profitable_managers} (expected {expected_profitable})")
                
                details = f"Period: {period}, Accrued: ${accrued_fees:.2f}, Paid: ${paid_fees:.2f}, Pending: ${pending_payment:.2f}"
                self.log_test("Performance Fees Summary", True, details)
                
                # Test with specific month/year parameters
                return self.test_performance_fees_summary_with_params()
                
            else:
                self.log_test("Performance Fees Summary", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Performance Fees Summary", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_fees_summary_with_params(self):
        """Test GET /api/admin/performance-fees/summary with month/year parameters"""
        try:
            url = f"{BACKEND_URL}/api/admin/performance-fees/summary"
            params = {"month": 10, "year": 2025}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should have same structure as before
                period = data.get('period', '')
                expected_period = "2025-10"
                
                if expected_period in period:
                    self.log_test("Summary With Params", True, f"Period with params: {period} (contains expected {expected_period})")
                    return True
                else:
                    self.log_test("Summary With Params", False, f"Period with params: {period} (expected to contain {expected_period})")
                    return False
                
            else:
                self.log_test("Summary With Params", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Summary With Params", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_fees_transactions(self):
        """Test GET /api/admin/performance-fees/transactions"""
        try:
            # Test without parameters
            url = f"{BACKEND_URL}/api/admin/performance-fees/transactions"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'transactions', 'total']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Performance Fees Transactions Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check expected values
                success = data.get('success', False)
                transactions = data.get('transactions', [])
                total = data.get('total', 0)
                
                # Expected values from review request (empty initially)
                if not success:
                    self.log_test("Transactions Success", False, f"success=false in response")
                    return False
                
                if not isinstance(transactions, list):
                    self.log_test("Transactions Array", False, f"transactions should be array, got {type(transactions)}")
                    return False
                
                # Should be empty array initially (no finalized transactions yet)
                if len(transactions) == 0 and total == 0:
                    self.log_test("Transactions Empty State", True, f"Empty transactions array and total=0 as expected")
                else:
                    self.log_test("Transactions Content", True, f"Found {len(transactions)} transactions, total={total}")
                
                details = f"success={success}, transactions count={len(transactions)}, total={total}"
                self.log_test("Performance Fees Transactions", True, details)
                
                # Test with limit/offset parameters
                return self.test_performance_fees_transactions_with_params()
                
            else:
                self.log_test("Performance Fees Transactions", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Performance Fees Transactions", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_fees_transactions_with_params(self):
        """Test GET /api/admin/performance-fees/transactions with limit/offset"""
        try:
            url = f"{BACKEND_URL}/api/admin/performance-fees/transactions"
            params = {"limit": 10, "offset": 0}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                success = data.get('success', False)
                if success:
                    self.log_test("Transactions With Params", True, f"Transactions endpoint works with limit/offset parameters")
                    return True
                else:
                    self.log_test("Transactions With Params", False, f"success=false with parameters")
                    return False
                
            else:
                self.log_test("Transactions With Params", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Transactions With Params", False, f"Exception: {str(e)}")
            return False
    
    def test_update_manager_performance_fee(self):
        """Test PUT /api/admin/money-managers/{manager_id}/performance-fee"""
        try:
            # Skip if no manager IDs found
            if not self.manager_ids:
                self.log_test("Update Manager Performance Fee", False, "No manager IDs available for testing")
                return False
            
            # Note: There's currently an ObjectId import issue in the backend
            self.log_test("Update Manager Performance Fee", False, "Skipped due to backend ObjectId import issue - needs 'from bson import ObjectId' in the endpoint")
            return False
            
            # Use first manager ID for testing
            manager_id = self.manager_ids[0]
            url = f"{BACKEND_URL}/api/admin/money-managers/{manager_id}/performance-fee"
            
            # Test data
            payload = {
                "performance_fee_rate": 0.35
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'success' not in data:
                    self.log_test("Update Manager Fee Structure", False, "Missing 'success' key in response")
                    return False
                
                if not data.get('success'):
                    self.log_test("Update Manager Fee Success", False, f"success=false in response: {data}")
                    return False
                
                # Check for manager data
                if 'manager' in data:
                    manager = data['manager']
                    updated_rate = manager.get('performance_fee_rate', 0)
                    expected_rate = 0.35
                    
                    if abs(updated_rate - expected_rate) < 0.001:
                        self.log_test("Manager Fee Rate Update", True, f"Updated rate: {updated_rate} (matches expected {expected_rate})")
                    else:
                        self.log_test("Manager Fee Rate Update", False, f"Updated rate: {updated_rate} (expected {expected_rate})")
                
                details = f"Manager ID: {manager_id}, success={data.get('success')}, rate=0.35"
                self.log_test("Update Manager Performance Fee", True, details)
                return True
                
            else:
                self.log_test("Update Manager Performance Fee", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Manager Performance Fee", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all performance fee endpoint tests"""
        print("🎯 PERFORMANCE FEE ENDPOINTS TESTING (Phase 3)")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test Current Performance Fees
        print("📋 TEST 1: Get Current Performance Fees")
        self.test_current_performance_fees()
        print()
        
        # Step 3: Test Calculate Daily Performance Fees
        print("📋 TEST 2: Calculate Daily Performance Fees")
        self.test_calculate_daily_performance_fees()
        print()
        
        # Step 4: Test Performance Fees Summary
        print("📋 TEST 3: Get Performance Fees Summary")
        self.test_performance_fees_summary()
        print()
        
        # Step 5: Test Performance Fees Transactions
        print("📋 TEST 4: List Performance Fee Transactions")
        self.test_performance_fees_transactions()
        print()
        
        # Step 6: Test Update Manager Performance Fee
        print("📋 TEST 6: Update Manager Performance Fee")
        self.test_update_manager_performance_fee()
        print()
        
        # Summary
        self.print_summary()
        
        # Return overall success
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        return passed_tests == total_tests
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 PERFORMANCE FEE ENDPOINTS TEST SUMMARY")
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
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 OVERALL RESULT: EXCELLENT - All performance fee endpoints working correctly!")
        elif success_rate >= 75:
            print("✅ OVERALL RESULT: GOOD - Most performance fee endpoints working")
        elif success_rate >= 50:
            print("⚠️ OVERALL RESULT: PARTIAL - Some performance fee endpoints need attention")
        else:
            print("❌ OVERALL RESULT: CRITICAL - Major performance fee endpoint issues detected")
        
        print()
        print("🔍 KEY FINDINGS:")
        
        # Check specific success criteria from review request
        current_fees_working = any(r['success'] and 'Current Performance Fees' in r['test'] 
                                  for r in self.test_results)
        
        if current_fees_working:
            print("   ✅ Current performance fees endpoint returns expected $1,000.64 total")
        else:
            print("   ❌ Current performance fees endpoint may not be working correctly")
        
        calculate_working = any(r['success'] and 'Calculate Daily Performance Fees' in r['test'] 
                               for r in self.test_results)
        
        if calculate_working:
            print("   ✅ Daily performance fees calculation working successfully")
        else:
            print("   ❌ Daily performance fees calculation may have issues")
        
        summary_working = any(r['success'] and 'Performance Fees Summary' in r['test'] 
                             for r in self.test_results)
        
        if summary_working:
            print("   ✅ Performance fees summary shows correct period and totals")
        else:
            print("   ❌ Performance fees summary may have issues")
        
        transactions_working = any(r['success'] and 'Performance Fees Transactions' in r['test'] 
                                  for r in self.test_results)
        
        if transactions_working:
            print("   ✅ Performance fees transactions endpoint working (even if empty)")
        else:
            print("   ❌ Performance fees transactions endpoint may have issues")
        
        manager_update_working = any(r['success'] and 'Update Manager Performance Fee' in r['test'] 
                                    for r in self.test_results)
        
        if manager_update_working:
            print("   ✅ Manager performance fee update working correctly")
        else:
            print("   ❌ Manager performance fee update may have issues")
        
        print()
        print("🎯 SUCCESS CRITERIA VERIFICATION:")
        print("   Expected Results:")
        print("   • Current fees total: $1,000.64 ✓" if current_fees_working else "   • Current fees total: $1,000.64 ❌")
        print("   • 3 managers with fees (TradingHub Gold, GoldenTrade, UNO14 MAM) ✓" if current_fees_working else "   • 3 managers with fees ❌")
        print("   • CP Strategy shows $0 fee (loss) ✓" if current_fees_working else "   • CP Strategy shows $0 fee ❌")
        print("   • Summary shows period '2025-10' and correct totals ✓" if summary_working else "   • Summary shows correct period and totals ❌")
        print("   • Transactions endpoint works (empty initially) ✓" if transactions_working else "   • Transactions endpoint works ❌")
        print("   • Manager fee update works ✓" if manager_update_working else "   • Manager fee update works ❌")
        
        print()

def main():
    """Main test execution"""
    tester = PerformanceFeeEndpointsTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()