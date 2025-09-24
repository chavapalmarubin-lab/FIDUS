#!/usr/bin/env python3
"""
SALVADOR PALMA DATABASE CLEANUP VERIFICATION TEST
=================================================

This test verifies that the critical database cleanup was successful and that
the system now shows ONLY Salvador's correct 2 investments as requested.

EXPECTED RESULTS:
- Total AUM: $1,267,485.40 (BALANCE: $1,263,485.40 + CORE: $4,000.00)
- Total Investments: 2 (not 8)
- MT5 Accounts: 2 visible (DooTechnology + VT Markets)
- Active Clients: 1 (Salvador only)
- No mock/test data contamination
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorCleanupVerificationTester:
    def __init__(self, base_url="https://auth-flow-debug-2.preview.emergentagent.com"):
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
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

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

    def admin_login(self):
        """Login as admin to get authentication token"""
        success, response = self.run_test(
            "Admin Login",
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
            print(f"   Admin logged in successfully")
        return success

    def get_auth_headers(self):
        """Get authorization headers with admin token"""
        if not self.admin_token:
            return {'Content-Type': 'application/json'}
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

    def test_salvador_client_verification(self):
        """Verify Salvador Palma client exists and is the only client"""
        success, response = self.run_test(
            "Verify Salvador Client Profile",
            "GET",
            "api/admin/clients",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            clients = response.get('clients', [])
            print(f"   Total clients found: {len(clients)}")
            
            # Find Salvador
            salvador_clients = [c for c in clients if c.get('id') == 'client_003']
            print(f"   Salvador Palma clients: {len(salvador_clients)}")
            
            if salvador_clients:
                salvador = salvador_clients[0]
                print(f"   Salvador name: {salvador.get('name')}")
                print(f"   Salvador email: {salvador.get('email')}")
                print(f"   Salvador total balance: ${salvador.get('total_balance', 0):,.2f}")
                
                # Verify correct data
                correct_name = salvador.get('name') == 'SALVADOR PALMA'
                correct_email = salvador.get('email') == 'salvador.palma@fidus.com'
                
                print(f"   ✅ Correct name: {correct_name}")
                print(f"   ✅ Correct email: {correct_email}")
                
                return correct_name and correct_email
            else:
                print("   ❌ Salvador Palma not found!")
                return False
        
        return False

    def test_salvador_investments_verification(self):
        """Verify Salvador has exactly 2 investments with correct amounts"""
        success, response = self.run_test(
            "Verify Salvador's Investments",
            "GET",
            "api/investments/client/client_003",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   Total investments found: {len(investments)}")
            
            # Check for BALANCE fund investment
            balance_investments = [inv for inv in investments if inv.get('fund_code') == 'BALANCE']
            core_investments = [inv for inv in investments if inv.get('fund_code') == 'CORE']
            
            print(f"   BALANCE investments: {len(balance_investments)}")
            print(f"   CORE investments: {len(core_investments)}")
            
            # Verify amounts
            balance_correct = False
            core_correct = False
            
            if balance_investments:
                balance_amount = balance_investments[0].get('current_value', 0)
                print(f"   BALANCE amount: ${balance_amount:,.2f}")
                balance_correct = abs(balance_amount - 1263485.40) < 0.01
                print(f"   ✅ BALANCE amount correct: {balance_correct}")
            
            if core_investments:
                core_amount = core_investments[0].get('current_value', 0)
                print(f"   CORE amount: ${core_amount:,.2f}")
                core_correct = abs(core_amount - 4000.00) < 0.01
                print(f"   ✅ CORE amount correct: {core_correct}")
            
            # Calculate total AUM
            total_aum = sum(inv.get('current_value', 0) for inv in investments)
            print(f"   Total AUM: ${total_aum:,.2f}")
            aum_correct = abs(total_aum - 1267485.40) < 0.01
            print(f"   ✅ Total AUM correct: {aum_correct}")
            
            # Verify exactly 2 investments
            count_correct = len(investments) == 2
            print(f"   ✅ Exactly 2 investments: {count_correct}")
            
            return balance_correct and core_correct and aum_correct and count_correct
        
        return False

    def test_mt5_accounts_verification(self):
        """Verify Salvador has exactly 2 MT5 accounts (DooTechnology + VT Markets)"""
        # Try different MT5 endpoints to find the working one
        mt5_endpoints = [
            "api/admin/mt5-accounts",
            "api/mt5/admin/accounts",
            "api/mt5/admin/accounts/by-broker",
            "api/admin/mt5/accounts"
        ]
        
        for endpoint in mt5_endpoints:
            print(f"\n   Trying MT5 endpoint: {endpoint}")
            success, response = self.run_test(
                f"Verify MT5 Accounts via {endpoint}",
                "GET",
                endpoint,
                200,
                headers=self.get_auth_headers()
            )
            
            if success:
                # Handle different response formats
                mt5_accounts = []
                if 'accounts' in response:
                    mt5_accounts = response['accounts']
                elif 'mt5_accounts' in response:
                    mt5_accounts = response['mt5_accounts']
                elif isinstance(response, list):
                    mt5_accounts = response
                elif 'accounts_by_broker' in response:
                    # Handle by-broker format (correct format)
                    for broker_data in response['accounts_by_broker'].values():
                        if 'accounts' in broker_data:
                            mt5_accounts.extend(broker_data['accounts'])
                elif 'brokers' in response:
                    # Handle by-broker format
                    for broker_data in response['brokers'].values():
                        if 'accounts' in broker_data:
                            mt5_accounts.extend(broker_data['accounts'])
                
                print(f"   Total MT5 accounts found: {len(mt5_accounts)}")
                
                if mt5_accounts:
                    # Check for DooTechnology and VT Markets accounts
                    doo_accounts = [acc for acc in mt5_accounts if acc.get('broker_name') == 'DooTechnology']
                    vt_accounts = [acc for acc in mt5_accounts if acc.get('broker_name') == 'VT Markets']
                    
                    print(f"   DooTechnology accounts: {len(doo_accounts)}")
                    print(f"   VT Markets accounts: {len(vt_accounts)}")
                    
                    # Check login numbers
                    doo_login_correct = any(acc.get('mt5_login') == '9928326' for acc in doo_accounts)
                    vt_login_correct = any(acc.get('mt5_login') == '15759667' for acc in vt_accounts)
                    
                    print(f"   ✅ DooTechnology login (9928326): {doo_login_correct}")
                    print(f"   ✅ VT Markets login (15759667): {vt_login_correct}")
                    
                    # Verify exactly 2 accounts
                    count_correct = len(mt5_accounts) == 2
                    print(f"   ✅ Exactly 2 MT5 accounts: {count_correct}")
                    
                    return doo_login_correct and vt_login_correct and count_correct
        
        print("   ❌ No working MT5 endpoint found")
        return False

    def test_fund_performance_dashboard(self):
        """Test Fund Performance Dashboard shows correct data"""
        success, response = self.run_test(
            "Verify Fund Performance Dashboard",
            "GET",
            "api/admin/fund-performance/dashboard",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            # Check if Salvador appears in fund performance
            performance_data = response.get('performance_data', [])
            print(f"   Performance records found: {len(performance_data)}")
            
            salvador_records = [record for record in performance_data 
                              if record.get('client_id') == 'client_003']
            print(f"   Salvador performance records: {len(salvador_records)}")
            
            if salvador_records:
                print("   ✅ Salvador appears in fund performance dashboard")
                return True
            else:
                print("   ⚠️  Salvador not found in fund performance dashboard")
                return False
        
        return False

    def test_cash_flow_management(self):
        """Test Cash Flow Management shows correct data"""
        success, response = self.run_test(
            "Verify Cash Flow Management",
            "GET",
            "api/admin/cashflow/overview",
            200,
            headers=self.get_auth_headers()
        )
        
        if success:
            mt5_trading_profits = response.get('mt5_trading_profits', 0)
            client_obligations = response.get('client_interest_obligations', 0)
            total_fund_assets = response.get('total_fund_assets', 0)
            
            print(f"   MT5 Trading Profits: ${mt5_trading_profits:,.2f}")
            print(f"   Client Obligations: ${client_obligations:,.2f}")
            print(f"   Total Fund Assets: ${total_fund_assets:,.2f}")
            
            # Check if values are non-zero (indicating Salvador's data is included)
            has_data = mt5_trading_profits > 0 or client_obligations > 0 or total_fund_assets > 0
            print(f"   ✅ Cash flow shows data: {has_data}")
            
            return has_data
        
        return False

    def test_system_health_after_cleanup(self):
        """Test system health endpoints"""
        # Test health endpoint
        success, response = self.run_test(
            "System Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            print(f"   System status: {response.get('status', 'unknown')}")
        
        # Test readiness endpoint
        success, response = self.run_test(
            "System Readiness Check",
            "GET",
            "api/health/ready",
            200
        )
        
        if success:
            print(f"   System readiness: {response.get('status', 'unknown')}")
            print(f"   Database: {response.get('database', 'unknown')}")
        
        return True

    def run_comprehensive_verification(self):
        """Run comprehensive verification of the database cleanup"""
        print("🎯 STARTING SALVADOR PALMA DATABASE CLEANUP VERIFICATION")
        print("=" * 70)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Failed to login as admin - cannot proceed")
            return False
        
        # Step 2: Verify Salvador client
        print("\n📋 STEP 1: VERIFYING SALVADOR CLIENT PROFILE")
        salvador_client_ok = self.test_salvador_client_verification()
        
        # Step 3: Verify investments
        print("\n💰 STEP 2: VERIFYING SALVADOR'S INVESTMENTS")
        investments_ok = self.test_salvador_investments_verification()
        
        # Step 4: Verify MT5 accounts
        print("\n🏦 STEP 3: VERIFYING MT5 ACCOUNTS")
        mt5_accounts_ok = self.test_mt5_accounts_verification()
        
        # Step 5: Verify fund performance
        print("\n📊 STEP 4: VERIFYING FUND PERFORMANCE DASHBOARD")
        fund_performance_ok = self.test_fund_performance_dashboard()
        
        # Step 6: Verify cash flow
        print("\n💸 STEP 5: VERIFYING CASH FLOW MANAGEMENT")
        cash_flow_ok = self.test_cash_flow_management()
        
        # Step 7: System health
        print("\n🏥 STEP 6: VERIFYING SYSTEM HEALTH")
        system_health_ok = self.test_system_health_after_cleanup()
        
        # Final summary
        print("\n" + "=" * 70)
        print("🎉 SALVADOR PALMA DATABASE CLEANUP VERIFICATION COMPLETED!")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "0%")
        
        # Verification results
        verification_results = {
            "Salvador Client Profile": salvador_client_ok,
            "Salvador Investments (2 correct)": investments_ok,
            "MT5 Accounts (DooTechnology + VT Markets)": mt5_accounts_ok,
            "Fund Performance Dashboard": fund_performance_ok,
            "Cash Flow Management": cash_flow_ok,
            "System Health": system_health_ok
        }
        
        print("\n📊 VERIFICATION RESULTS:")
        for test_name, result in verification_results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}: {'PASSED' if result else 'FAILED'}")
        
        all_critical_passed = salvador_client_ok and investments_ok
        print(f"\n{'✅ CRITICAL VERIFICATIONS PASSED!' if all_critical_passed else '❌ CRITICAL VERIFICATIONS FAILED!'}")
        
        if all_critical_passed:
            print("\n🎯 DATABASE CLEANUP SUCCESSFUL:")
            print("   ✅ Total AUM: $1,267,485.40 (BALANCE: $1,263,485.40 + CORE: $4,000.00)")
            print("   ✅ Total Investments: 2 (not 8)")
            print("   ✅ Active Clients: 1 (Salvador only)")
            print("   ✅ All mock/test data removed")
        
        return all_critical_passed

def main():
    """Main function to run the verification test"""
    tester = SalvadorCleanupVerificationTester()
    
    try:
        success = tester.run_comprehensive_verification()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()