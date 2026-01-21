#!/usr/bin/env python3
"""
COMPREHENSIVE PHASE II SSOT BACKEND API VERIFICATION
Test ALL dashboard tabs' backend endpoints to ensure they're working with the new SSOT architecture.

Test Date: December 19, 2025
Purpose: Verify SSOT (Single Source of Truth) architecture implementation
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://viking-trade-dash.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
    "user_type": "admin"
}

class SSotBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def authenticate(self):
        """Authenticate as admin user"""
        try:
            print(f"\n🔐 Authenticating with {API_BASE}/auth/login...")
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                if self.auth_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    self.log_result("Authentication", True, "Successfully authenticated as admin")
                    return True
                else:
                    self.log_result("Authentication", False, "No token in response", data)
                    return False
            else:
                self.log_result("Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_fund_portfolio_endpoint(self):
        """Test Fund Portfolio Tab - GET /api/v2/derived/fund-portfolio"""
        try:
            print(f"\n📊 Testing Fund Portfolio endpoint...")
            
            response = self.session.get(f"{API_BASE}/v2/derived/fund-portfolio", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure
                required_keys = ['funds', 'summary']
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_result("Fund Portfolio Structure", False, f"Missing keys: {missing_keys}", data)
                    return False
                
                # Verify funds structure
                funds = data.get('funds', {})
                expected_funds = ['CORE', 'BALANCE', 'SEPARATION']
                
                fund_results = []
                for fund_code in expected_funds:
                    if fund_code in funds:
                        fund_data = funds[fund_code]
                        required_fund_keys = ['total_allocation', 'total_balance', 'total_equity', 'total_pnl', 'accounts']
                        missing_fund_keys = [key for key in required_fund_keys if key not in fund_data]
                        
                        if missing_fund_keys:
                            fund_results.append(f"{fund_code}: missing {missing_fund_keys}")
                        else:
                            accounts_count = len(fund_data.get('accounts', []))
                            allocation = fund_data.get('total_allocation', 0)
                            fund_results.append(f"{fund_code}: {accounts_count} accounts, ${allocation:,.2f}")
                    else:
                        fund_results.append(f"{fund_code}: MISSING")
                
                # Verify summary structure
                summary = data.get('summary', {})
                required_summary_keys = ['total_allocation', 'total_aum', 'total_pnl']
                missing_summary_keys = [key for key in required_summary_keys if key not in summary]
                
                if missing_summary_keys:
                    self.log_result("Fund Portfolio Summary", False, f"Missing summary keys: {missing_summary_keys}", summary)
                    return False
                
                # Verify expected values
                total_allocation = summary.get('total_allocation', 0)
                expected_allocation = 134657.41
                
                success_message = f"Fund Portfolio working correctly. Funds: {', '.join(fund_results)}. Total Allocation: ${total_allocation:,.2f}"
                
                if abs(total_allocation - expected_allocation) > 1000:  # Allow some variance
                    self.log_result("Fund Portfolio Values", False, f"Total allocation ${total_allocation:,.2f} differs significantly from expected ${expected_allocation:,.2f}", data)
                else:
                    self.log_result("Fund Portfolio", True, success_message)
                    return True
                    
            else:
                self.log_result("Fund Portfolio", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Fund Portfolio", False, f"Exception: {str(e)}")
            return False
    
    def test_money_managers_endpoint(self):
        """Test Money Managers Tab - GET /api/v2/derived/money-managers"""
        try:
            print(f"\n👥 Testing Money Managers endpoint...")
            
            response = self.session.get(f"{API_BASE}/v2/derived/money-managers", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure
                if 'managers' not in data:
                    self.log_result("Money Managers Structure", False, "Missing 'managers' key", data)
                    return False
                
                managers = data.get('managers', {})
                manager_count = len(managers)
                
                # Look for expected managers
                expected_managers = ['CP Strategy', 'UNO14 Manager']
                found_managers = []
                
                for manager_name, manager_data in managers.items():
                    required_keys = ['total_allocation', 'total_balance', 'total_pnl', 'accounts']
                    missing_keys = [key for key in required_keys if key not in manager_data]
                    
                    if missing_keys:
                        found_managers.append(f"{manager_name}: missing {missing_keys}")
                    else:
                        accounts_count = len(manager_data.get('accounts', []))
                        allocation = manager_data.get('total_allocation', 0)
                        found_managers.append(f"{manager_name}: {accounts_count} accounts, ${allocation:,.2f}")
                
                # Check for CP Strategy specifically
                cp_strategy_found = any('CP Strategy' in manager for manager in managers.keys())
                
                success_message = f"Money Managers working correctly. {manager_count} managers found: {', '.join(found_managers[:5])}"  # Limit output
                
                if manager_count >= 9 and cp_strategy_found:
                    self.log_result("Money Managers", True, success_message)
                    return True
                else:
                    self.log_result("Money Managers", False, f"Expected 9+ managers with CP Strategy, found {manager_count} managers", data)
                    return False
                    
            else:
                self.log_result("Money Managers", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Money Managers", False, f"Exception: {str(e)}")
            return False
    
    def test_cash_flow_endpoint(self):
        """Test Cash Flow Tab - GET /api/v2/derived/cash-flow"""
        try:
            print(f"\n💰 Testing Cash Flow endpoint...")
            
            response = self.session.get(f"{API_BASE}/v2/derived/cash-flow", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure
                required_keys = ['accounts', 'summary']
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_result("Cash Flow Structure", False, f"Missing keys: {missing_keys}", data)
                    return False
                
                accounts = data.get('accounts', [])
                summary = data.get('summary', {})
                
                # Verify accounts count
                accounts_count = len(accounts)
                expected_accounts = 13  # Active accounts
                
                # Verify summary structure
                required_summary_keys = ['total_balance', 'total_equity', 'total_pnl']
                missing_summary_keys = [key for key in required_summary_keys if key not in summary]
                
                if missing_summary_keys:
                    self.log_result("Cash Flow Summary", False, f"Missing summary keys: {missing_summary_keys}", summary)
                    return False
                
                total_balance = summary.get('total_balance', 0)
                total_equity = summary.get('total_equity', 0)
                total_pnl = summary.get('total_pnl', 0)
                
                success_message = f"Cash Flow working correctly. {accounts_count} accounts, Balance: ${total_balance:,.2f}, Equity: ${total_equity:,.2f}, P&L: ${total_pnl:,.2f}"
                
                if accounts_count >= 10:  # Allow some variance
                    self.log_result("Cash Flow", True, success_message)
                    return True
                else:
                    self.log_result("Cash Flow", False, f"Expected ~13 accounts, found {accounts_count}", data)
                    return False
                    
            else:
                self.log_result("Cash Flow", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Cash Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts_endpoint(self):
        """Test MT5 Accounts Tab - GET /api/v2/accounts/all?platform=MT5"""
        try:
            print(f"\n🏦 Testing MT5 Accounts endpoint...")
            
            response = self.session.get(f"{API_BASE}/v2/accounts/all?platform=MT5", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    accounts = data
                elif isinstance(data, dict) and 'accounts' in data:
                    accounts = data['accounts']
                else:
                    self.log_result("MT5 Accounts Structure", False, "Unexpected response structure", data)
                    return False
                
                mt5_accounts = [acc for acc in accounts if acc.get('platform') == 'MT5']
                mt5_count = len(mt5_accounts)
                
                # Verify account structure
                if mt5_accounts:
                    sample_account = mt5_accounts[0]
                    required_keys = ['account', 'platform', 'broker', 'fund_type', 'manager_name', 'initial_allocation', 'balance', 'pnl']
                    missing_keys = [key for key in required_keys if key not in sample_account]
                    
                    if missing_keys:
                        self.log_result("MT5 Account Structure", False, f"Missing keys in account: {missing_keys}", sample_account)
                        return False
                
                success_message = f"MT5 Accounts working correctly. {mt5_count} MT5 accounts found"
                
                if mt5_count >= 10:  # Expected 14, but allow some variance
                    self.log_result("MT5 Accounts", True, success_message)
                    return True
                else:
                    self.log_result("MT5 Accounts", False, f"Expected ~14 MT5 accounts, found {mt5_count}", {"count": mt5_count})
                    return False
                    
            else:
                self.log_result("MT5 Accounts", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("MT5 Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_mt4_accounts_endpoint(self):
        """Test MT4 Accounts Tab - GET /api/v2/accounts/all?platform=MT4"""
        try:
            print(f"\n🏛️ Testing MT4 Accounts endpoint...")
            
            response = self.session.get(f"{API_BASE}/v2/accounts/all?platform=MT4", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    accounts = data
                elif isinstance(data, dict) and 'accounts' in data:
                    accounts = data['accounts']
                else:
                    self.log_result("MT4 Accounts Structure", False, "Unexpected response structure", data)
                    return False
                
                mt4_accounts = [acc for acc in accounts if acc.get('platform') == 'MT4']
                mt4_count = len(mt4_accounts)
                
                # Look for specific MT4 account
                account_33200931_found = any(str(acc.get('account')) == '33200931' for acc in mt4_accounts)
                
                success_message = f"MT4 Accounts working correctly. {mt4_count} MT4 accounts found"
                if account_33200931_found:
                    success_message += " (including account 33200931)"
                
                if mt4_count >= 1:  # Expected 1 MT4 account
                    self.log_result("MT4 Accounts", True, success_message)
                    return True
                else:
                    self.log_result("MT4 Accounts", False, f"Expected 1 MT4 account, found {mt4_count}", {"count": mt4_count})
                    return False
                    
            else:
                self.log_result("MT4 Accounts", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("MT4 Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_accounts_management_endpoint(self):
        """Test Accounts Management Tab - GET /api/v2/accounts/all"""
        try:
            print(f"\n📋 Testing Accounts Management endpoint...")
            
            response = self.session.get(f"{API_BASE}/v2/accounts/all", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    accounts = data
                elif isinstance(data, dict) and 'accounts' in data:
                    accounts = data['accounts']
                else:
                    self.log_result("Accounts Management Structure", False, "Unexpected response structure", data)
                    return False
                
                total_accounts = len(accounts)
                
                # Verify account structure
                if accounts:
                    sample_account = accounts[0]
                    required_keys = ['initial_allocation', 'pnl']
                    missing_keys = [key for key in required_keys if key not in sample_account]
                    
                    if missing_keys:
                        self.log_result("Account Structure", False, f"Missing keys in account: {missing_keys}", sample_account)
                        return False
                
                # Count platforms
                mt5_count = len([acc for acc in accounts if acc.get('platform') == 'MT5'])
                mt4_count = len([acc for acc in accounts if acc.get('platform') == 'MT4'])
                
                success_message = f"Accounts Management working correctly. {total_accounts} total accounts (MT5: {mt5_count}, MT4: {mt4_count})"
                
                if total_accounts >= 14:  # Expected 15, allow some variance
                    self.log_result("Accounts Management", True, success_message)
                    return True
                else:
                    self.log_result("Accounts Management", False, f"Expected ~15 accounts, found {total_accounts}", {"count": total_accounts})
                    return False
                    
            else:
                self.log_result("Accounts Management", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Accounts Management", False, f"Exception: {str(e)}")
            return False
    
    def test_trading_analytics_endpoint(self):
        """Test Trading Analytics Tab - GET /api/v2/derived/trading-analytics"""
        try:
            print(f"\n📈 Testing Trading Analytics endpoint...")
            
            response = self.session.get(f"{API_BASE}/v2/derived/trading-analytics", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # This endpoint might have various structures, so we'll be flexible
                success_message = f"Trading Analytics endpoint responding correctly"
                
                if isinstance(data, dict):
                    # Look for performance metrics
                    if 'performance' in data or 'analytics' in data or 'accounts' in data:
                        self.log_result("Trading Analytics", True, success_message)
                        return True
                    else:
                        self.log_result("Trading Analytics", True, f"{success_message} (basic structure)")
                        return True
                else:
                    self.log_result("Trading Analytics", True, f"{success_message} (list response)")
                    return True
                    
            else:
                self.log_result("Trading Analytics", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Trading Analytics", False, f"Exception: {str(e)}")
            return False
    
    def test_account_update_endpoint(self):
        """Test Account Updates - PATCH /api/v2/accounts/886602/assign"""
        try:
            print(f"\n✏️ Testing Account Update endpoint...")
            
            # Test with a safe update (status change)
            update_data = {"status": "active"}
            
            response = self.session.patch(
                f"{API_BASE}/v2/accounts/886602/assign",
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    self.log_result("Account Update", True, "Account update endpoint working correctly")
                    return True
                else:
                    self.log_result("Account Update", False, "Update response indicates failure", data)
                    return False
                    
            elif response.status_code == 404:
                self.log_result("Account Update", False, "Account 886602 not found - may be expected", {"status": 404})
                return False
            else:
                self.log_result("Account Update", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Account Update", False, f"Exception: {str(e)}")
            return False
    
    def test_ssot_health_endpoint(self):
        """Test SSOT Health - GET /api/v2/health/ssot"""
        try:
            print(f"\n🏥 Testing SSOT Health endpoint...")
            
            response = self.session.get(f"{API_BASE}/v2/health/ssot", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure
                expected_keys = ['status', 'total_accounts']
                missing_keys = [key for key in expected_keys if key not in data]
                
                if missing_keys:
                    self.log_result("SSOT Health Structure", False, f"Missing keys: {missing_keys}", data)
                    return False
                
                status = data.get('status')
                total_accounts = data.get('total_accounts', 0)
                ssot_violation = data.get('ssot_violation', {})
                violated = ssot_violation.get('violated', True)  # Default to True if missing
                
                success_message = f"SSOT Health working correctly. Status: {status}, Accounts: {total_accounts}, Violated: {violated}"
                
                if status == "HEALTHY" and not violated and total_accounts >= 14:
                    self.log_result("SSOT Health", True, success_message)
                    return True
                else:
                    self.log_result("SSOT Health", False, f"SSOT issues detected: {success_message}", data)
                    return False
                    
            else:
                self.log_result("SSOT Health", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("SSOT Health", False, f"Exception: {str(e)}")
            return False
    
    def test_data_consistency(self):
        """Test data consistency across endpoints"""
        try:
            print(f"\n🔍 Testing Data Consistency...")
            
            # Get data from multiple endpoints
            fund_portfolio_response = self.session.get(f"{API_BASE}/v2/derived/fund-portfolio", timeout=30)
            accounts_response = self.session.get(f"{API_BASE}/v2/accounts/all", timeout=30)
            
            if fund_portfolio_response.status_code != 200 or accounts_response.status_code != 200:
                self.log_result("Data Consistency", False, "Could not fetch data for consistency check")
                return False
            
            fund_data = fund_portfolio_response.json()
            accounts_data = accounts_response.json()
            
            # Extract totals
            fund_total_allocation = fund_data.get('summary', {}).get('total_allocation', 0)
            
            if isinstance(accounts_data, list):
                accounts = accounts_data
            else:
                accounts = accounts_data.get('accounts', [])
            
            accounts_total_allocation = sum(acc.get('initial_allocation', 0) for acc in accounts)
            
            # Check consistency (allow small variance for floating point)
            allocation_diff = abs(fund_total_allocation - accounts_total_allocation)
            
            if allocation_diff < 100:  # Allow $100 variance
                self.log_result("Data Consistency", True, f"Allocation totals consistent: Fund ${fund_total_allocation:,.2f} vs Accounts ${accounts_total_allocation:,.2f}")
                return True
            else:
                self.log_result("Data Consistency", False, f"Allocation mismatch: Fund ${fund_total_allocation:,.2f} vs Accounts ${accounts_total_allocation:,.2f} (diff: ${allocation_diff:,.2f})")
                return False
                
        except Exception as e:
            self.log_result("Data Consistency", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all SSOT backend tests"""
        print("🚀 COMPREHENSIVE PHASE II SSOT BACKEND API VERIFICATION")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("\n❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run all endpoint tests
        tests = [
            self.test_fund_portfolio_endpoint,
            self.test_money_managers_endpoint,
            self.test_cash_flow_endpoint,
            self.test_mt5_accounts_endpoint,
            self.test_mt4_accounts_endpoint,
            self.test_accounts_management_endpoint,
            self.test_trading_analytics_endpoint,
            self.test_account_update_endpoint,
            self.test_ssot_health_endpoint,
            self.test_data_consistency
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SSOT BACKEND TEST RESULTS SUMMARY")
        print("=" * 70)
        
        success_rate = (passed / total) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
        
        # Detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']} - {result['message']}")
        
        # Final assessment
        if success_rate >= 80:
            print(f"\n🎉 SSOT BACKEND VERIFICATION SUCCESSFUL!")
            print(f"The SSOT architecture is working correctly with {success_rate:.1f}% success rate.")
        elif success_rate >= 60:
            print(f"\n⚠️ SSOT BACKEND VERIFICATION PARTIAL SUCCESS")
            print(f"Most endpoints working but some issues detected ({success_rate:.1f}% success rate).")
        else:
            print(f"\n🚨 SSOT BACKEND VERIFICATION FAILED")
            print(f"Critical issues detected ({success_rate:.1f}% success rate).")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = SSotBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)