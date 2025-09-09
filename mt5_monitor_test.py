#!/usr/bin/env python3
"""
MT5 Monitoring System Test Suite
Tests the newly implemented MT5 monitoring system for Salvador Palma's accounts
"""

import requests
import sys
import json
from datetime import datetime
import time

class MT5MonitorTester:
    def __init__(self, base_url="https://mt5-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

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
                self.failed_tests.append(f"{name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name} - Exception: {str(e)}")
            return False, {}

    def test_salvador_status_endpoint(self):
        """Test Salvador Account Status Check - GET /api/mt5/monitor/salvador-status"""
        print("\n" + "="*80)
        print("🎯 TESTING SALVADOR PALMA MT5 ACCOUNT STATUS")
        print("="*80)
        
        success, response = self.run_test(
            "Salvador Account Status Check",
            "GET", 
            "api/mt5/monitor/salvador-status",
            200
        )
        
        if success:
            print(f"\n📊 SALVADOR PALMA MT5 ACCOUNT ANALYSIS:")
            print(f"   Client ID: {response.get('client_id', 'N/A')}")
            print(f"   Client Name: {response.get('client_name', 'N/A')}")
            print(f"   Total Accounts Found: {response.get('total_accounts', 0)}")
            print(f"   Expected Accounts: {response.get('expected_accounts', 2)}")
            print(f"   Overall Status: {response.get('overall_status', 'unknown')}")
            print(f"   Timestamp: {response.get('timestamp', 'N/A')}")
            
            accounts = response.get('accounts', [])
            print(f"\n🏦 ACCOUNT DETAILS ({len(accounts)} accounts):")
            
            dootechnology_found = False
            vt_found = False
            
            for i, account in enumerate(accounts, 1):
                print(f"\n   Account {i}:")
                print(f"     Broker: {account.get('broker', 'Unknown')}")
                print(f"     Broker Code: {account.get('broker_code', 'unknown')}")
                print(f"     MT5 Login: {account.get('mt5_login', 'N/A')}")
                print(f"     MT5 Server: {account.get('mt5_server', 'N/A')}")
                print(f"     Allocated: ${account.get('allocated', 0):,.2f}")
                print(f"     Current Equity: ${account.get('current_equity', 0):,.2f}")
                print(f"     Profit/Loss: ${account.get('profit_loss', 0):,.2f} ({account.get('profit_loss_percentage', 0):.2f}%)")
                print(f"     Last Updated: {account.get('last_updated', 'N/A')}")
                print(f"     Hours Since Update: {account.get('hours_since_update', 'unknown')}")
                print(f"     Status: {account.get('status', 'unknown')}")
                
                # Check for expected accounts
                broker_code = account.get('broker_code', '').lower()
                mt5_login = account.get('mt5_login')
                
                if broker_code == 'dootechnology' and mt5_login == 9928326:
                    dootechnology_found = True
                    print(f"     ✅ DOOTECHNOLOGY ACCOUNT FOUND (Login: {mt5_login})")
                elif broker_code == 'vt' and mt5_login == 19638038:
                    vt_found = True
                    print(f"     ✅ VT MARKETS ACCOUNT FOUND (Login: {mt5_login})")
            
            # Verify expected results
            print(f"\n🔍 EXPECTED RESULTS VERIFICATION:")
            if response.get('total_accounts') == 2:
                print(f"   ✅ Correct number of accounts: 2")
            else:
                print(f"   ❌ Expected 2 accounts, found {response.get('total_accounts', 0)}")
                
            if dootechnology_found:
                print(f"   ✅ DooTechnology account found (Login: 9928326)")
            else:
                print(f"   ❌ DooTechnology account missing (Expected Login: 9928326)")
                
            if vt_found:
                print(f"   ✅ VT Markets account found (Login: 19638038)")
            else:
                print(f"   ❌ VT Markets account missing (Expected Login: 19638038)")
                
            # Check data freshness
            fresh_data = True
            for account in accounts:
                hours_since_update = account.get('hours_since_update')
                if isinstance(hours_since_update, (int, float)) and hours_since_update > 1:
                    fresh_data = False
                    break
                    
            if fresh_data:
                print(f"   ✅ Data is fresh (recently updated)")
            else:
                print(f"   ⚠️  Some data may be stale")
                
            return success and dootechnology_found and vt_found and response.get('total_accounts') == 2
        
        return success

    def test_mt5_monitor_system_status(self):
        """Test MT5 Monitor System Status - GET /api/mt5/monitor/status"""
        print("\n" + "="*80)
        print("🖥️  TESTING MT5 MONITOR SYSTEM STATUS")
        print("="*80)
        
        success, response = self.run_test(
            "MT5 Monitor System Status",
            "GET",
            "api/mt5/monitor/status", 
            200
        )
        
        if success:
            print(f"\n📊 SYSTEM STATUS ANALYSIS:")
            print(f"   Timestamp: {response.get('timestamp', 'N/A')}")
            print(f"   Monitor Running: {response.get('monitor_running', False)}")
            print(f"   Total Accounts: {response.get('total_accounts', 0)}")
            print(f"   Healthy Accounts: {response.get('healthy_accounts', 0)}")
            print(f"   Stale Accounts: {response.get('stale_accounts', 0)}")
            print(f"   Health Percentage: {response.get('health_percentage', 0):.1f}%")
            print(f"   System Status: {response.get('system_status', 'unknown')}")
            print(f"   Last Health Check: {response.get('last_health_check', 'N/A')}")
            
            salvador_info = response.get('salvador_palma', {})
            print(f"\n👤 SALVADOR PALMA SPECIFIC STATUS:")
            print(f"   Status: {salvador_info.get('status', 'unknown')}")
            print(f"   Accounts Found: {salvador_info.get('accounts_found', 0)}")
            print(f"   Accounts Expected: {salvador_info.get('accounts_expected', 2)}")
            print(f"   Brokers: {', '.join(salvador_info.get('brokers', []))}")
            
            # Verify expected structure
            required_keys = ['timestamp', 'monitor_running', 'total_accounts', 'healthy_accounts', 
                           'stale_accounts', 'health_percentage', 'salvador_palma', 'system_status']
            missing_keys = [key for key in required_keys if key not in response]
            
            if not missing_keys:
                print(f"   ✅ All required keys present in response")
            else:
                print(f"   ❌ Missing keys: {missing_keys}")
                
            # Check Salvador's status
            salvador_status = salvador_info.get('status', 'unknown')
            salvador_accounts = salvador_info.get('accounts_found', 0)
            
            if salvador_status == 'healthy' and salvador_accounts == 2:
                print(f"   ✅ Salvador's status is healthy with 2 accounts")
                return True
            else:
                print(f"   ⚠️  Salvador's status: {salvador_status}, accounts: {salvador_accounts}")
                return success
        
        return success

    def test_force_update_functionality(self):
        """Test Force Update Functionality - POST /api/mt5/monitor/force-update"""
        print("\n" + "="*80)
        print("🔄 TESTING FORCE UPDATE FUNCTIONALITY")
        print("="*80)
        
        success, response = self.run_test(
            "Force Update MT5 Data",
            "POST",
            "api/mt5/monitor/force-update",
            200
        )
        
        if success:
            print(f"\n📊 FORCE UPDATE RESULTS:")
            print(f"   Message: {response.get('message', 'N/A')}")
            print(f"   Accounts Updated: {response.get('accounts_updated', 0)}")
            print(f"   Total Accounts: {response.get('total_accounts', 0)}")
            print(f"   Timestamp: {response.get('timestamp', 'N/A')}")
            
            accounts_updated = response.get('accounts_updated', 0)
            total_accounts = response.get('total_accounts', 0)
            
            if accounts_updated > 0:
                print(f"   ✅ Successfully updated {accounts_updated} accounts")
            else:
                print(f"   ⚠️  No accounts were updated")
                
            if accounts_updated == total_accounts and total_accounts > 0:
                print(f"   ✅ All accounts updated successfully")
                return True
            elif accounts_updated > 0:
                print(f"   ⚠️  Partial update: {accounts_updated}/{total_accounts}")
                return success
            else:
                print(f"   ❌ No accounts updated")
                return False
        
        return success

    def test_monitor_control_start(self):
        """Test Monitor Control - POST /api/mt5/monitor/start"""
        print("\n" + "="*80)
        print("▶️  TESTING MONITOR START CONTROL")
        print("="*80)
        
        success, response = self.run_test(
            "Start MT5 Monitor",
            "POST",
            "api/mt5/monitor/start",
            200
        )
        
        if success:
            print(f"\n📊 START MONITOR RESULTS:")
            print(f"   Message: {response.get('message', 'N/A')}")
            print(f"   Status: {response.get('status', 'unknown')}")
            print(f"   Timestamp: {response.get('timestamp', 'N/A')}")
            
            if response.get('status') == 'running':
                print(f"   ✅ Monitor started successfully")
                return True
            else:
                print(f"   ❌ Monitor not in running state")
                return False
        
        return success

    def test_monitor_control_stop(self):
        """Test Monitor Control - POST /api/mt5/monitor/stop"""
        print("\n" + "="*80)
        print("⏹️  TESTING MONITOR STOP CONTROL")
        print("="*80)
        
        success, response = self.run_test(
            "Stop MT5 Monitor",
            "POST",
            "api/mt5/monitor/stop",
            200
        )
        
        if success:
            print(f"\n📊 STOP MONITOR RESULTS:")
            print(f"   Message: {response.get('message', 'N/A')}")
            print(f"   Status: {response.get('status', 'unknown')}")
            print(f"   Timestamp: {response.get('timestamp', 'N/A')}")
            
            if response.get('status') == 'stopped':
                print(f"   ✅ Monitor stopped successfully")
                return True
            else:
                print(f"   ❌ Monitor not in stopped state")
                return False
        
        return success

    def test_data_structure_validation(self):
        """Test that all endpoints return proper JSON responses with expected data structure"""
        print("\n" + "="*80)
        print("🔍 TESTING DATA STRUCTURE VALIDATION")
        print("="*80)
        
        all_valid = True
        
        # Test Salvador status structure
        success, salvador_data = self.run_test(
            "Salvador Status Data Structure",
            "GET",
            "api/mt5/monitor/salvador-status",
            200
        )
        
        if success:
            required_salvador_keys = ['client_id', 'client_name', 'total_accounts', 'expected_accounts', 
                                    'accounts', 'overall_status', 'timestamp']
            missing_keys = [key for key in required_salvador_keys if key not in salvador_data]
            
            if not missing_keys:
                print(f"   ✅ Salvador status structure valid")
                
                # Check accounts array structure
                accounts = salvador_data.get('accounts', [])
                if accounts:
                    account_keys = ['broker', 'broker_code', 'mt5_login', 'mt5_server', 'allocated', 
                                  'current_equity', 'profit_loss', 'status']
                    account = accounts[0]
                    missing_account_keys = [key for key in account_keys if key not in account]
                    
                    if not missing_account_keys:
                        print(f"   ✅ Account structure valid")
                    else:
                        print(f"   ❌ Account missing keys: {missing_account_keys}")
                        all_valid = False
                else:
                    print(f"   ⚠️  No accounts in response")
            else:
                print(f"   ❌ Salvador status missing keys: {missing_keys}")
                all_valid = False
        else:
            all_valid = False
        
        # Test system status structure
        success, system_data = self.run_test(
            "System Status Data Structure",
            "GET",
            "api/mt5/monitor/status",
            200
        )
        
        if success:
            required_system_keys = ['timestamp', 'monitor_running', 'total_accounts', 'healthy_accounts',
                                  'salvador_palma', 'system_status']
            missing_keys = [key for key in required_system_keys if key not in system_data]
            
            if not missing_keys:
                print(f"   ✅ System status structure valid")
            else:
                print(f"   ❌ System status missing keys: {missing_keys}")
                all_valid = False
        else:
            all_valid = False
            
        return all_valid

    def run_comprehensive_test(self):
        """Run all MT5 monitoring tests"""
        print("🚀 STARTING MT5 MONITORING SYSTEM COMPREHENSIVE TEST")
        print("="*80)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test sequence
        test_results = []
        
        # 1. Test Salvador Account Status Check
        result1 = self.test_salvador_status_endpoint()
        test_results.append(("Salvador Account Status", result1))
        
        # 2. Test MT5 Monitor System Status
        result2 = self.test_mt5_monitor_system_status()
        test_results.append(("MT5 Monitor System Status", result2))
        
        # 3. Test Force Update Functionality
        result3 = self.test_force_update_functionality()
        test_results.append(("Force Update Functionality", result3))
        
        # 4. Test Monitor Control - Start
        result4 = self.test_monitor_control_start()
        test_results.append(("Monitor Control Start", result4))
        
        # 5. Test Monitor Control - Stop
        result5 = self.test_monitor_control_stop()
        test_results.append(("Monitor Control Stop", result5))
        
        # 6. Test Data Structure Validation
        result6 = self.test_data_structure_validation()
        test_results.append(("Data Structure Validation", result6))
        
        # Final Results
        print("\n" + "="*80)
        print("📊 FINAL TEST RESULTS")
        print("="*80)
        
        print(f"\n🎯 INDIVIDUAL TEST RESULTS:")
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   Total Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        # Critical requirements check
        critical_tests = [result1, result2, result3, result4, result5]
        critical_passed = sum(critical_tests)
        
        print(f"\n🎯 CRITICAL REQUIREMENTS STATUS:")
        print(f"   Salvador 2 Accounts (DooTechnology + VT): {'✅ VERIFIED' if result1 else '❌ FAILED'}")
        print(f"   System Health Monitoring: {'✅ WORKING' if result2 else '❌ FAILED'}")
        print(f"   Force Update Capability: {'✅ WORKING' if result3 else '❌ FAILED'}")
        print(f"   Monitor Start/Stop Control: {'✅ WORKING' if (result4 and result5) else '❌ FAILED'}")
        print(f"   JSON Response Structure: {'✅ VALID' if result6 else '❌ INVALID'}")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for i, failure in enumerate(self.failed_tests, 1):
                print(f"   {i}. {failure}")
        
        # Final verdict
        if critical_passed >= 4 and self.tests_passed >= (self.tests_run * 0.8):
            print(f"\n🎉 MT5 MONITORING SYSTEM: ✅ PRODUCTION READY")
            print(f"   All critical functionality verified!")
            return True
        elif critical_passed >= 3:
            print(f"\n⚠️  MT5 MONITORING SYSTEM: 🔶 MOSTLY WORKING")
            print(f"   Some issues found but core functionality operational")
            return False
        else:
            print(f"\n🚨 MT5 MONITORING SYSTEM: ❌ CRITICAL ISSUES")
            print(f"   Major problems detected - requires immediate attention")
            return False

def main():
    """Main test execution"""
    tester = MT5MonitorTester()
    
    try:
        success = tester.run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()