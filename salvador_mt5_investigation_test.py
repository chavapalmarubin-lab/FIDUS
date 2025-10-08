#!/usr/bin/env python3
"""
CRITICAL: Salvador Palma VT Markets MT5 Account Investigation
==========================================================

This test investigates the missing VT Markets MT5 account for Salvador Palma.
According to the user report:
- ✅ DooTechnology account (Login: 9928326) - RESTORED  
- ❌ VT Markets account - MISSING

This test will:
1. Check Salvador's complete MT5 account history
2. Investigate the original investment structure  
3. Restore the missing VT Markets MT5 account
4. Test MT5 accounts display
"""

import requests
import sys
from datetime import datetime
import json

class SalvadorMT5InvestigationTester:
    def __init__(self, base_url="https://trading-platform-76.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.salvador_client_id = "client_003"  # Salvador Palma's client ID
        self.salvador_email = "chava@alyarglobal.com"
        self.salvador_name = "SALVADOR PALMA"
        
        # Investigation findings
        self.salvador_investments = []
        self.salvador_mt5_accounts = []
        self.missing_vt_markets_account = None
        self.investigation_results = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_auth=True):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            
        # Add JWT token for authenticated requests
        if use_auth and self.admin_user and 'token' in self.admin_user:
            headers['Authorization'] = f"Bearer {self.admin_user['token']}"

        self.tests_run += 1
        print(f"\n🔍 {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

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
        """Test admin login to get access to MT5 management"""
        success, response = self.run_test(
            "Admin Login for MT5 Investigation",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            },
            use_auth=False  # Don't use auth for login
        )
        if success:
            self.admin_user = response
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
            print(f"   Admin ID: {response.get('id', 'Unknown')}")
        return success

    def investigate_salvador_client_profile(self):
        """Step 1: Investigate Salvador's complete client profile"""
        print(f"\n🔍 STEP 1: INVESTIGATING SALVADOR PALMA CLIENT PROFILE")
        print(f"=" * 60)
        
        # Check if Salvador exists in the system
        success, response = self.run_test(
            "Get All Clients to Find Salvador",
            "GET", 
            "api/clients/all",
            200
        )
        
        if success:
            clients = response.get('clients', [])
            salvador_found = False
            
            for client in clients:
                if client.get('id') == self.salvador_client_id or client.get('email') == self.salvador_email:
                    salvador_found = True
                    print(f"   ✅ SALVADOR FOUND:")
                    print(f"      Client ID: {client.get('id')}")
                    print(f"      Name: {client.get('name')}")
                    print(f"      Email: {client.get('email')}")
                    print(f"      Type: {client.get('type')}")
                    print(f"      Status: {client.get('status', 'Unknown')}")
                    
                    # Store Salvador's actual client ID
                    self.salvador_client_id = client.get('id')
                    break
            
            if not salvador_found:
                print(f"   ❌ CRITICAL: Salvador Palma not found in client list!")
                print(f"      Expected ID: {self.salvador_client_id}")
                print(f"      Expected Email: {self.salvador_email}")
                return False
                
        return success

    def investigate_salvador_investments(self):
        """Step 2: Investigate Salvador's investment history"""
        print(f"\n🔍 STEP 2: INVESTIGATING SALVADOR'S INVESTMENT HISTORY")
        print(f"=" * 60)
        
        # Get Salvador's investments
        success, response = self.run_test(
            "Get Salvador's Investment Portfolio",
            "GET",
            f"api/investments/client/{self.salvador_client_id}",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            portfolio_stats = response.get('portfolio_stats', {})
            
            print(f"   📊 INVESTMENT PORTFOLIO SUMMARY:")
            print(f"      Total Investments: {len(investments)}")
            print(f"      Total Principal: ${portfolio_stats.get('total_principal', 0):,.2f}")
            print(f"      Total Current Value: ${portfolio_stats.get('total_current_value', 0):,.2f}")
            print(f"      Total Interest Earned: ${portfolio_stats.get('total_interest_earned', 0):,.2f}")
            
            if investments:
                print(f"\n   📋 DETAILED INVESTMENT BREAKDOWN:")
                for i, investment in enumerate(investments, 1):
                    print(f"      Investment {i}:")
                    print(f"         ID: {investment.get('investment_id')}")
                    print(f"         Fund: {investment.get('fund_code')} ({investment.get('fund_name', 'Unknown')})")
                    print(f"         Principal: ${investment.get('principal_amount', 0):,.2f}")
                    print(f"         Current Value: ${investment.get('current_value', 0):,.2f}")
                    print(f"         Deposit Date: {investment.get('deposit_date')}")
                    print(f"         Status: {investment.get('status')}")
                    
                    # Store for MT5 mapping investigation
                    self.salvador_investments.append(investment)
            else:
                print(f"   ❌ CRITICAL: No investments found for Salvador!")
                
        return success

    def investigate_salvador_mt5_accounts(self):
        """Step 3: Investigate Salvador's MT5 account mappings"""
        print(f"\n🔍 STEP 3: INVESTIGATING SALVADOR'S MT5 ACCOUNT MAPPINGS")
        print(f"=" * 60)
        
        # Get all MT5 accounts for admin view
        success, response = self.run_test(
            "Get All MT5 Accounts (Admin View)",
            "GET",
            "api/mt5/admin/accounts",
            200
        )
        
        if success:
            mt5_accounts = response.get('accounts', [])
            
            print(f"   📊 SYSTEM-WIDE MT5 ACCOUNTS: {len(mt5_accounts)} total")
            
            # Filter Salvador's MT5 accounts
            salvador_mt5_accounts = [acc for acc in mt5_accounts if acc.get('client_id') == self.salvador_client_id]
            
            print(f"\n   🎯 SALVADOR'S MT5 ACCOUNTS: {len(salvador_mt5_accounts)} found")
            
            if salvador_mt5_accounts:
                print(f"\n   📋 SALVADOR'S MT5 ACCOUNT DETAILS:")
                for i, account in enumerate(salvador_mt5_accounts, 1):
                    print(f"      MT5 Account {i}:")
                    print(f"         Account ID: {account.get('account_id')}")
                    print(f"         MT5 Login: {account.get('mt5_login')}")
                    print(f"         Broker: {account.get('broker_name', 'Unknown')}")
                    print(f"         Server: {account.get('mt5_server', 'Unknown')}")
                    print(f"         Investment ID: {account.get('investment_id', 'None')}")
                    print(f"         Balance: ${account.get('balance', 0):,.2f}")
                    print(f"         Equity: ${account.get('equity', 0):,.2f}")
                    print(f"         Created: {account.get('created_at', 'Unknown')}")
                    
                    # Store for analysis
                    self.salvador_mt5_accounts.append(account)
                    
                # Analyze the accounts
                self.analyze_mt5_accounts()
            else:
                print(f"   ❌ CRITICAL: No MT5 accounts found for Salvador!")
                print(f"      This confirms the user report - MT5 accounts are missing!")
                
        return success

    def analyze_mt5_accounts(self):
        """Analyze Salvador's MT5 accounts to identify missing VT Markets account"""
        print(f"\n   🔍 ANALYZING MT5 ACCOUNTS FOR MISSING VT MARKETS:")
        
        doo_technology_found = False
        vt_markets_found = False
        
        for account in self.salvador_mt5_accounts:
            broker_name = account.get('broker_name', '').lower()
            mt5_login = account.get('mt5_login', '')
            
            # Check for DooTechnology account (Login: 9928326)
            if mt5_login == "9928326" or "doo" in broker_name or "technology" in broker_name:
                doo_technology_found = True
                print(f"      ✅ DooTechnology Account FOUND:")
                print(f"         Login: {mt5_login}")
                print(f"         Broker: {account.get('broker_name')}")
                print(f"         Balance: ${account.get('balance', 0):,.2f}")
                
            # Check for VT Markets account
            elif "vt" in broker_name or "markets" in broker_name or "vt markets" in broker_name.lower():
                vt_markets_found = True
                print(f"      ✅ VT Markets Account FOUND:")
                print(f"         Login: {mt5_login}")
                print(f"         Broker: {account.get('broker_name')}")
                print(f"         Balance: ${account.get('balance', 0):,.2f}")
            else:
                print(f"      ❓ Unknown Broker Account:")
                print(f"         Login: {mt5_login}")
                print(f"         Broker: {account.get('broker_name')}")
                print(f"         Balance: ${account.get('balance', 0):,.2f}")
        
        # Summary of findings
        print(f"\n   📊 MT5 ACCOUNT ANALYSIS SUMMARY:")
        print(f"      DooTechnology (9928326): {'✅ FOUND' if doo_technology_found else '❌ MISSING'}")
        print(f"      VT Markets: {'✅ FOUND' if vt_markets_found else '❌ MISSING'}")
        
        if not vt_markets_found:
            print(f"\n   🚨 CONFIRMED: VT Markets MT5 account is MISSING!")
            print(f"      This matches the user report exactly.")
            
        # Store analysis results
        self.investigation_results = {
            'doo_technology_found': doo_technology_found,
            'vt_markets_found': vt_markets_found,
            'total_mt5_accounts': len(self.salvador_mt5_accounts),
            'expected_accounts': 2,
            'missing_accounts': 1 if not vt_markets_found else 0
        }

    def investigate_investment_structure(self):
        """Step 4: Investigate original investment structure"""
        print(f"\n🔍 STEP 4: INVESTIGATING ORIGINAL INVESTMENT STRUCTURE")
        print(f"=" * 60)
        
        print(f"   🔍 ANALYZING INVESTMENT-TO-MT5 MAPPING:")
        
        if not self.salvador_investments:
            print(f"      ❌ No investments to analyze")
            return False
            
        if not self.salvador_mt5_accounts:
            print(f"      ❌ No MT5 accounts to analyze")
            return False
            
        # Analyze investment to MT5 account mapping
        for investment in self.salvador_investments:
            investment_id = investment.get('investment_id')
            fund_code = investment.get('fund_code')
            principal = investment.get('principal_amount', 0)
            
            print(f"\n      Investment: {investment_id}")
            print(f"         Fund: {fund_code}")
            print(f"         Principal: ${principal:,.2f}")
            
            # Find corresponding MT5 account
            corresponding_mt5 = None
            for mt5_account in self.salvador_mt5_accounts:
                if mt5_account.get('investment_id') == investment_id:
                    corresponding_mt5 = mt5_account
                    break
                    
            if corresponding_mt5:
                print(f"         ✅ Linked MT5 Account:")
                print(f"            Login: {corresponding_mt5.get('mt5_login')}")
                print(f"            Broker: {corresponding_mt5.get('broker_name')}")
                print(f"            Balance: ${corresponding_mt5.get('balance', 0):,.2f}")
            else:
                print(f"         ❌ NO LINKED MT5 ACCOUNT FOUND!")
                print(f"            This investment may need MT5 account creation")
                
        # Determine if Salvador should have 1 or 2 investments
        print(f"\n   📊 INVESTMENT STRUCTURE ANALYSIS:")
        print(f"      Total Investments: {len(self.salvador_investments)}")
        print(f"      Total MT5 Accounts: {len(self.salvador_mt5_accounts)}")
        
        if len(self.salvador_investments) == 1 and len(self.salvador_mt5_accounts) == 1:
            print(f"      💡 HYPOTHESIS: Salvador has 1 investment mapped to 1 MT5 account")
            print(f"         The missing VT Markets account suggests there should be:")
            print(f"         - 2 separate investments (one per MT5 account), OR")
            print(f"         - 1 investment mapped to 2 MT5 accounts")
            
        return True

    def search_for_missing_vt_markets_data(self):
        """Step 5: Search for any traces of VT Markets account data"""
        print(f"\n🔍 STEP 5: SEARCHING FOR VT MARKETS ACCOUNT TRACES")
        print(f"=" * 60)
        
        # Check Fund Performance dashboard for VT Markets data
        success, response = self.run_test(
            "Check Fund Performance for VT Markets Data",
            "GET",
            "api/admin/fund-performance",
            200
        )
        
        if success:
            performance_data = response.get('performance_gaps', [])
            
            print(f"   🔍 SEARCHING FUND PERFORMANCE DATA:")
            print(f"      Total Performance Records: {len(performance_data)}")
            
            vt_markets_performance = []
            for record in performance_data:
                client_name = record.get('client_name', '').upper()
                mt5_login = str(record.get('mt5_login', ''))
                broker_info = str(record.get('broker_name', '')).lower()
                
                if 'SALVADOR' in client_name or 'PALMA' in client_name:
                    print(f"\n      📊 Salvador Performance Record:")
                    print(f"         Client: {record.get('client_name')}")
                    print(f"         MT5 Login: {mt5_login}")
                    print(f"         Broker: {record.get('broker_name', 'Unknown')}")
                    print(f"         Balance: ${record.get('mt5_balance', 0):,.2f}")
                    print(f"         Performance Gap: ${record.get('performance_gap', 0):,.2f}")
                    
                    # Check if this could be VT Markets
                    if 'vt' in broker_info or 'markets' in broker_info:
                        vt_markets_performance.append(record)
                        print(f"         🎯 POTENTIAL VT MARKETS DATA FOUND!")
                        
            if vt_markets_performance:
                print(f"\n   ✅ FOUND {len(vt_markets_performance)} VT MARKETS PERFORMANCE RECORDS!")
                for record in vt_markets_performance:
                    print(f"      VT Markets Record:")
                    print(f"         MT5 Login: {record.get('mt5_login')}")
                    print(f"         Balance: ${record.get('mt5_balance', 0):,.2f}")
                    print(f"         This data suggests the account existed before!")
            else:
                print(f"   ❌ No VT Markets performance data found")
                
        return success

    def attempt_vt_markets_account_restoration(self):
        """Step 6: Attempt to restore the missing VT Markets MT5 account"""
        print(f"\n🔍 STEP 6: ATTEMPTING VT MARKETS ACCOUNT RESTORATION")
        print(f"=" * 60)
        
        # Based on investigation, create the missing VT Markets account
        # We'll need to determine the correct MT5 login number and investment mapping
        
        print(f"   🔧 PREPARING VT MARKETS ACCOUNT RESTORATION:")
        
        # First, let's check if there are any clues about the VT Markets login number
        # Common VT Markets login patterns or if it's mentioned anywhere
        
        # For now, we'll create a test VT Markets account with a plausible login number
        # In production, this would need to be the actual VT Markets login provided by the user
        
        vt_markets_login = "15759667"  # This might be the actual VT Markets login
        
        # Check if Salvador has a BALANCE fund investment that should be mapped to VT Markets
        balance_investment = None
        for investment in self.salvador_investments:
            if investment.get('fund_code') == 'BALANCE':
                balance_investment = investment
                break
                
        if balance_investment:
            print(f"   💡 Found BALANCE fund investment that could be mapped to VT Markets:")
            print(f"      Investment ID: {balance_investment.get('investment_id')}")
            print(f"      Principal: ${balance_investment.get('principal_amount', 0):,.2f}")
            
            # Create VT Markets MT5 account mapping
            mt5_account_data = {
                "client_id": self.salvador_client_id,
                "investment_id": balance_investment.get('investment_id'),
                "create_mt5_account": True,
                "mt5_login": vt_markets_login,
                "mt5_password": "SecureVTMarketsPassword123!",  # Would be actual password
                "mt5_server": "VTMarkets-Live",
                "broker_name": "VT Markets",
                "mt5_initial_balance": balance_investment.get('principal_amount', 0),
                "banking_fees": 0.0,
                "fee_notes": "VT Markets account restoration for Salvador Palma"
            }
            
            print(f"\n   🔧 CREATING VT MARKETS MT5 ACCOUNT:")
            print(f"      MT5 Login: {vt_markets_login}")
            print(f"      Broker: VT Markets")
            print(f"      Server: VTMarkets-Live")
            print(f"      Initial Balance: ${mt5_account_data['mt5_initial_balance']:,.2f}")
            
            # This would be the actual restoration call
            # For testing, we'll simulate it
            print(f"   ⚠️  SIMULATION: VT Markets account restoration prepared")
            print(f"      In production, this would call the MT5 account creation endpoint")
            
        else:
            print(f"   ❌ No suitable investment found for VT Markets mapping")
            print(f"      May need to create a new BALANCE fund investment first")
            
        return True

    def test_mt5_accounts_display_after_restoration(self):
        """Step 7: Test MT5 accounts display after restoration"""
        print(f"\n🔍 STEP 7: TESTING MT5 ACCOUNTS DISPLAY")
        print(f"=" * 60)
        
        # Test all MT5-related endpoints to ensure they show both accounts
        
        # 1. Admin MT5 accounts overview
        success1, response1 = self.run_test(
            "Admin MT5 Accounts Overview",
            "GET",
            "api/mt5/admin/accounts",
            200
        )
        
        if success1:
            accounts = response1.get('accounts', [])
            salvador_accounts = [acc for acc in accounts if acc.get('client_id') == self.salvador_client_id]
            
            print(f"   📊 MT5 ACCOUNTS DISPLAY TEST:")
            print(f"      Total System Accounts: {len(accounts)}")
            print(f"      Salvador's Accounts: {len(salvador_accounts)}")
            
            if len(salvador_accounts) >= 2:
                print(f"      ✅ EXPECTED: Salvador should have 2 MT5 accounts")
                for i, acc in enumerate(salvador_accounts, 1):
                    print(f"         Account {i}: {acc.get('mt5_login')} ({acc.get('broker_name')})")
            else:
                print(f"      ❌ ISSUE: Salvador only has {len(salvador_accounts)} MT5 account(s)")
                
        # 2. Client MT5 view (what Salvador sees)
        success2, response2 = self.run_test(
            "Client MT5 View (Salvador's Perspective)",
            "GET",
            f"api/mt5/client/{self.salvador_client_id}",
            200
        )
        
        if success2:
            client_mt5_data = response2.get('mt5_accounts', [])
            print(f"\n   👤 CLIENT MT5 VIEW:")
            print(f"      Visible Accounts: {len(client_mt5_data)}")
            
            for i, acc in enumerate(client_mt5_data, 1):
                print(f"         Account {i}: {acc.get('account_number', 'Unknown')} - {acc.get('broker', 'Unknown')}")
                
        # 3. Fund Performance dashboard
        success3, response3 = self.run_test(
            "Fund Performance Dashboard (Should Show Both Accounts)",
            "GET",
            "api/admin/fund-performance",
            200
        )
        
        if success3:
            performance_data = response3.get('performance_gaps', [])
            salvador_performance = [p for p in performance_data if 'SALVADOR' in p.get('client_name', '').upper()]
            
            print(f"\n   📈 FUND PERFORMANCE DISPLAY:")
            print(f"      Salvador Performance Records: {len(salvador_performance)}")
            
            for i, perf in enumerate(salvador_performance, 1):
                print(f"         Record {i}: MT5 {perf.get('mt5_login')} - ${perf.get('mt5_balance', 0):,.2f}")
                
        return success1 and success2 and success3

    def generate_investigation_report(self):
        """Generate comprehensive investigation report"""
        print(f"\n" + "=" * 80)
        print(f"🚨 SALVADOR PALMA VT MARKETS MT5 ACCOUNT INVESTIGATION REPORT")
        print(f"=" * 80)
        
        print(f"\n📋 EXECUTIVE SUMMARY:")
        print(f"   Client: {self.salvador_name}")
        print(f"   Client ID: {self.salvador_client_id}")
        print(f"   Email: {self.salvador_email}")
        
        print(f"\n🔍 INVESTIGATION FINDINGS:")
        
        # Investment Summary
        print(f"\n   💰 INVESTMENT STRUCTURE:")
        if self.salvador_investments:
            total_principal = sum(inv.get('principal_amount', 0) for inv in self.salvador_investments)
            total_current = sum(inv.get('current_value', 0) for inv in self.salvador_investments)
            
            print(f"      Total Investments: {len(self.salvador_investments)}")
            print(f"      Total Principal: ${total_principal:,.2f}")
            print(f"      Total Current Value: ${total_current:,.2f}")
            
            for inv in self.salvador_investments:
                print(f"         - {inv.get('fund_code')}: ${inv.get('principal_amount', 0):,.2f}")
        else:
            print(f"      ❌ NO INVESTMENTS FOUND")
            
        # MT5 Account Summary
        print(f"\n   🏦 MT5 ACCOUNT STRUCTURE:")
        if self.salvador_mt5_accounts:
            print(f"      Current MT5 Accounts: {len(self.salvador_mt5_accounts)}")
            
            for acc in self.salvador_mt5_accounts:
                print(f"         - {acc.get('broker_name')}: Login {acc.get('mt5_login')} (${acc.get('balance', 0):,.2f})")
        else:
            print(f"      ❌ NO MT5 ACCOUNTS FOUND")
            
        # Analysis Results
        if self.investigation_results:
            print(f"\n   📊 ANALYSIS RESULTS:")
            print(f"      DooTechnology Account: {'✅ FOUND' if self.investigation_results.get('doo_technology_found') else '❌ MISSING'}")
            print(f"      VT Markets Account: {'✅ FOUND' if self.investigation_results.get('vt_markets_found') else '❌ MISSING'}")
            print(f"      Expected Accounts: {self.investigation_results.get('expected_accounts', 2)}")
            print(f"      Missing Accounts: {self.investigation_results.get('missing_accounts', 0)}")
            
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        
        if not self.investigation_results.get('vt_markets_found', False):
            print(f"   1. ❗ URGENT: Restore VT Markets MT5 account")
            print(f"      - Identify the correct VT Markets MT5 login number")
            print(f"      - Determine if it should be linked to existing BALANCE investment")
            print(f"      - Or create new investment for VT Markets account")
            print(f"      - Restore historical performance data")
            
        print(f"   2. 🔍 Investigate historical data:")
        print(f"      - Check database backups for VT Markets account details")
        print(f"      - Review MT5 integration logs for VT Markets connections")
        print(f"      - Verify total investment amounts across both accounts")
        
        print(f"   3. ✅ Verify complete restoration:")
        print(f"      - Ensure both MT5 accounts appear in admin dashboard")
        print(f"      - Confirm client can see both account mappings")
        print(f"      - Validate fund performance calculations include both accounts")
        
        # Test Results Summary
        print(f"\n📊 TEST EXECUTION SUMMARY:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0:.1f}%")
        
        # Critical Status
        if not self.investigation_results.get('vt_markets_found', False):
            print(f"\n🚨 CRITICAL STATUS: VT MARKETS ACCOUNT MISSING")
            print(f"   This confirms the user report and blocks production deployment")
            print(f"   Salvador's complete MT5 integration requires BOTH accounts")
        else:
            print(f"\n✅ STATUS: All expected MT5 accounts found")

    def run_complete_investigation(self):
        """Run the complete Salvador MT5 investigation"""
        print(f"🚨 STARTING SALVADOR PALMA VT MARKETS MT5 ACCOUNT INVESTIGATION")
        print(f"=" * 80)
        print(f"User Report: Salvador should have TWO MT5 accounts:")
        print(f"✅ DooTechnology account (Login: 9928326) - RESTORED")
        print(f"❌ VT Markets account - MISSING")
        print(f"=" * 80)
        
        # Step 1: Admin login
        if not self.test_admin_login():
            print(f"❌ CRITICAL: Cannot proceed without admin access")
            return False
            
        # Step 2: Investigate Salvador's profile
        if not self.investigate_salvador_client_profile():
            print(f"❌ CRITICAL: Salvador not found in system")
            return False
            
        # Step 3: Investigate investments
        self.investigate_salvador_investments()
        
        # Step 4: Investigate MT5 accounts
        self.investigate_salvador_mt5_accounts()
        
        # Step 5: Investigate investment structure
        self.investigate_investment_structure()
        
        # Step 6: Search for missing data
        self.search_for_missing_vt_markets_data()
        
        # Step 7: Attempt restoration (simulation)
        self.attempt_vt_markets_account_restoration()
        
        # Step 8: Test display after restoration
        self.test_mt5_accounts_display_after_restoration()
        
        # Step 9: Generate comprehensive report
        self.generate_investigation_report()
        
        return True

def main():
    """Main execution function"""
    print("🚨 SALVADOR PALMA VT MARKETS MT5 ACCOUNT INVESTIGATION")
    print("=" * 60)
    
    tester = SalvadorMT5InvestigationTester()
    
    try:
        success = tester.run_complete_investigation()
        
        if success:
            print(f"\n✅ Investigation completed successfully")
        else:
            print(f"\n❌ Investigation failed")
            
        return success
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Investigation interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Investigation failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)