#!/usr/bin/env python3
"""
FOCUSED SYSTEM VERIFICATION - Available Endpoints Only
Testing Date: December 18, 2025
Backend URL: https://fidusrefs.preview.emergentagent.com/api
Auth: Admin (username: admin, password: password123)

Available Test Suite:
1. MT5 Status and Bridge Health
2. MT5 Accounts Verification (7 accounts with real balances)
3. Fund Portfolio Status
4. Cash Flow Analysis
5. Trading Analytics Dashboard
6. Money Managers Verification

Focus: Test what's actually implemented and working
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class FocusedSystemVerifier:
    def __init__(self):
        self.base_url = "https://fidusrefs.preview.emergentagent.com/api"
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
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating as admin...")
            
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    self.log_test("Admin Authentication", "PASS", "Successfully authenticated as admin")
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
    
    def test_mt5_status_and_bridge(self) -> bool:
        """Test 1: MT5 Status and Bridge Health"""
        try:
            print("\n🔌 Testing MT5 Status and Bridge Health...")
            
            success = True
            
            # Test MT5 Status endpoint
            response = self.session.get(f"{self.base_url}/mt5/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("MT5 Status API", "PASS", "MT5 status endpoint accessible")
                
                # Check connection status
                connection_status = data.get('connection_status', 'unknown')
                if connection_status == 'connected':
                    self.log_test("MT5 Connection Status", "PASS", f"Status: {connection_status}")
                else:
                    self.log_test("MT5 Connection Status", "FAIL", f"Status: {connection_status}")
                    success = False
                    
            else:
                self.log_test("MT5 Status API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                success = False
            
            # Test MT5 Bridge Health endpoint
            response = self.session.get(f"{self.base_url}/mt5/bridge/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("MT5 Bridge Health API", "PASS", "MT5 bridge health endpoint accessible")
                
                # Check bridge status
                bridge_status = data.get('status', 'unknown')
                if bridge_status in ['healthy', 'connected', 'operational']:
                    self.log_test("MT5 Bridge Status", "PASS", f"Bridge status: {bridge_status}")
                else:
                    self.log_test("MT5 Bridge Status", "FAIL", f"Bridge status: {bridge_status}")
                    success = False
                    
            else:
                self.log_test("MT5 Bridge Health API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                success = False
            
            return success
                
        except Exception as e:
            self.log_test("MT5 Status Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts_verification(self) -> bool:
        """Test 2: MT5 Accounts Verification (7 accounts with real balances)"""
        try:
            print("\n💰 Testing MT5 Accounts Verification...")
            
            response = self.session.get(f"{self.base_url}/mt5/accounts/all")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("MT5 Accounts API", "PASS", "MT5 accounts endpoint accessible")
                
                # Check account count
                accounts = data.get('accounts', [])
                account_count = len(accounts)
                
                if account_count == 7:
                    self.log_test("MT5 Account Count", "PASS", f"Found {account_count} accounts (expected 7)")
                else:
                    self.log_test("MT5 Account Count", "FAIL", f"Found {account_count} accounts (expected 7)")
                
                # Check for real balances (not $0)
                real_balance_accounts = 0
                total_equity = 0
                account_details = []
                
                for account in accounts:
                    if isinstance(account, dict):
                        account_id = account.get('account', 'Unknown')
                        equity = account.get('equity', 0)
                        balance = account.get('balance', 0)
                        
                        if equity > 0 or balance > 0:
                            real_balance_accounts += 1
                            total_equity += equity
                            
                        account_details.append(f"Account {account_id}: ${equity:.2f}")
                
                if real_balance_accounts >= 5:  # Allow some accounts to be $0
                    self.log_test("MT5 Real Balances", "PASS", 
                                f"{real_balance_accounts}/{account_count} accounts have real balances")
                else:
                    self.log_test("MT5 Real Balances", "FAIL", 
                                f"Only {real_balance_accounts}/{account_count} accounts have real balances")
                
                # Log account details
                for detail in account_details[:5]:  # Show first 5 accounts
                    print(f"   {detail}")
                
                self.log_test("Total MT5 Equity", "PASS" if total_equity > 0 else "FAIL", 
                            f"Total equity across all accounts: ${total_equity:,.2f}")
                
                return account_count == 7 and real_balance_accounts >= 5
            else:
                self.log_test("MT5 Accounts API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MT5 Accounts Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_fund_portfolio_status(self) -> bool:
        """Test 3: Fund Portfolio Status"""
        try:
            print("\n📊 Testing Fund Portfolio Status...")
            
            response = self.session.get(f"{self.base_url}/fund-portfolio/overview")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Fund Portfolio API", "PASS", "Fund portfolio endpoint accessible")
                
                # Check fund structure
                funds = data.get('funds', {})
                fund_count = len(funds)
                
                if fund_count >= 4:  # CORE, BALANCE, DYNAMIC, UNLIMITED
                    self.log_test("Fund Count", "PASS", f"Found {fund_count} funds")
                else:
                    self.log_test("Fund Count", "FAIL", f"Found {fund_count} funds (expected ≥4)")
                
                # Check specific funds
                expected_funds = ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']
                found_funds = []
                total_aum = 0
                
                for fund_code in expected_funds:
                    if fund_code in funds:
                        found_funds.append(fund_code)
                        fund_data = funds[fund_code]
                        aum = fund_data.get('aum', 0)
                        total_aum += aum
                        
                        self.log_test(f"{fund_code} Fund", "PASS", f"AUM: ${aum:,.2f}")
                
                if len(found_funds) == 4:
                    self.log_test("Expected Funds", "PASS", f"All expected funds found: {found_funds}")
                else:
                    missing = [f for f in expected_funds if f not in found_funds]
                    self.log_test("Expected Funds", "FAIL", f"Missing funds: {missing}")
                
                self.log_test("Total Portfolio AUM", "PASS" if total_aum > 0 else "FAIL", 
                            f"Total AUM: ${total_aum:,.2f}")
                
                return len(found_funds) == 4 and total_aum > 0
            else:
                self.log_test("Fund Portfolio API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Fund Portfolio Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_cash_flow_analysis(self) -> bool:
        """Test 4: Cash Flow Analysis"""
        try:
            print("\n💸 Testing Cash Flow Analysis...")
            
            response = self.session.get(f"{self.base_url}/admin/cashflow/overview")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Cash Flow API", "PASS", "Cash flow endpoint accessible")
                
                # Check summary data
                summary = data.get('summary', {})
                
                # Key cash flow metrics
                fund_revenue = summary.get('fund_revenue', 0)
                net_profit = summary.get('net_profit', 0)
                separation_interest = summary.get('separation_interest', 0)
                
                if fund_revenue != 0:
                    self.log_test("Fund Revenue", "PASS", f"Fund revenue: ${fund_revenue:,.2f}")
                else:
                    self.log_test("Fund Revenue", "FAIL", "Fund revenue is $0")
                
                if separation_interest != 0:
                    self.log_test("Separation Interest", "PASS", f"Separation interest: ${separation_interest:,.2f}")
                else:
                    self.log_test("Separation Interest", "FAIL", "Separation interest is $0")
                
                # Net profit can be negative, so just check it's not null
                if net_profit is not None:
                    self.log_test("Net Profit Calculation", "PASS", f"Net profit: ${net_profit:,.2f}")
                else:
                    self.log_test("Net Profit Calculation", "FAIL", "Net profit calculation missing")
                
                # Check for fund breakdown
                fund_breakdown = data.get('fund_breakdown', {})
                if fund_breakdown:
                    self.log_test("Fund Breakdown", "PASS", f"Fund breakdown available with {len(fund_breakdown)} entries")
                else:
                    self.log_test("Fund Breakdown", "FAIL", "Fund breakdown missing")
                
                return fund_revenue != 0 and separation_interest != 0 and net_profit is not None
            else:
                self.log_test("Cash Flow API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Cash Flow Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_trading_analytics_dashboard(self) -> bool:
        """Test 5: Trading Analytics Dashboard"""
        try:
            print("\n📈 Testing Trading Analytics Dashboard...")
            
            response = self.session.get(f"{self.base_url}/admin/fund-performance/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Trading Analytics API", "PASS", "Trading analytics endpoint accessible")
                
                # Check dashboard structure
                dashboard = data.get('dashboard', {})
                
                # Check by_fund breakdown
                by_fund = dashboard.get('by_fund', {})
                if by_fund:
                    self.log_test("Fund Performance Breakdown", "PASS", f"Performance data for {len(by_fund)} funds")
                    
                    # Specifically check CORE fund (should have 2 accounts)
                    core_fund = by_fund.get('CORE', {})
                    if core_fund:
                        account_count = core_fund.get('account_count', 0)
                        if account_count == 2:
                            self.log_test("CORE Fund Account Count", "PASS", f"CORE fund has {account_count} accounts")
                        else:
                            self.log_test("CORE Fund Account Count", "FAIL", f"CORE fund has {account_count} accounts (expected 2)")
                    else:
                        self.log_test("CORE Fund Data", "FAIL", "CORE fund data missing")
                else:
                    self.log_test("Fund Performance Breakdown", "FAIL", "Fund performance breakdown missing")
                
                # Check summary metrics
                summary = dashboard.get('summary', {})
                total_equity = summary.get('total_equity', 0)
                total_pnl = summary.get('total_pnl', 0)
                
                if total_equity > 0:
                    self.log_test("Total Equity", "PASS", f"Total equity: ${total_equity:,.2f}")
                else:
                    self.log_test("Total Equity", "FAIL", "Total equity is $0")
                
                # P&L can be negative, so just check it's not null
                if total_pnl is not None:
                    self.log_test("Total P&L", "PASS", f"Total P&L: ${total_pnl:,.2f}")
                else:
                    self.log_test("Total P&L", "FAIL", "Total P&L calculation missing")
                
                return len(by_fund) > 0 and total_equity > 0
            else:
                self.log_test("Trading Analytics API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Trading Analytics Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_money_managers_verification(self) -> bool:
        """Test 6: Money Managers Verification"""
        try:
            print("\n👥 Testing Money Managers Verification...")
            
            response = self.session.get(f"{self.base_url}/admin/trading-analytics/managers")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Money Managers API", "PASS", "Money managers endpoint accessible")
                
                # Check managers list
                managers = data.get('managers', [])
                manager_count = len(managers)
                
                if manager_count == 4:
                    self.log_test("Manager Count", "PASS", f"Found {manager_count} managers (expected 4)")
                else:
                    self.log_test("Manager Count", "FAIL", f"Found {manager_count} managers (expected 4)")
                
                # Check manager details
                manager_names = []
                total_pnl = 0
                
                for manager in managers:
                    if isinstance(manager, dict):
                        name = manager.get('manager_name', manager.get('name', 'Unknown'))
                        pnl = manager.get('total_pnl', 0)
                        
                        manager_names.append(name)
                        total_pnl += pnl
                        
                        # Check for real manager names (not "Unknown" or "Manual Trading")
                        if name not in ['Unknown', 'Manual Trading', 'Manager None']:
                            self.log_test(f"Manager: {name}", "PASS", f"P&L: ${pnl:,.2f}")
                        else:
                            self.log_test(f"Manager: {name}", "FAIL", "Invalid/placeholder manager name")
                
                # Check for expected managers
                expected_managers = ["CP Strategy", "TradingHub Gold", "GoldenTrade", "UNO14"]
                found_expected = 0
                
                for expected in expected_managers:
                    for found in manager_names:
                        if expected in found:
                            found_expected += 1
                            break
                
                if found_expected == 4:
                    self.log_test("Expected Managers", "PASS", f"All {found_expected} expected managers found")
                else:
                    self.log_test("Expected Managers", "FAIL", f"Only {found_expected}/4 expected managers found")
                
                self.log_test("Total Manager P&L", "PASS" if total_pnl != 0 else "FAIL", 
                            f"Combined P&L: ${total_pnl:,.2f}")
                
                return manager_count == 4 and found_expected == 4
            else:
                self.log_test("Money Managers API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Money Managers Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_focused_verification(self) -> Dict[str, Any]:
        """Run focused system verification"""
        print("🚀 Starting Focused System Verification - Available Endpoints")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # Run all available tests
        test_results = {
            "mt5_status_and_bridge": self.test_mt5_status_and_bridge(),
            "mt5_accounts_verification": self.test_mt5_accounts_verification(),
            "fund_portfolio_status": self.test_fund_portfolio_status(),
            "cash_flow_analysis": self.test_cash_flow_analysis(),
            "trading_analytics_dashboard": self.test_trading_analytics_dashboard(),
            "money_managers_verification": self.test_money_managers_verification()
        }
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 70)
        print("📊 FOCUSED VERIFICATION SUMMARY")
        print("=" * 70)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 ALL AVAILABLE SYSTEMS VERIFIED - Focused verification successful!")
        elif success_rate >= 80:
            print("⚠️  Most systems verified - Minor issues remain")
        elif success_rate >= 60:
            print("⚠️  Partial verification - Some systems working")
        else:
            print("🚨 CRITICAL SYSTEM ISSUES - Multiple verification failures")
        
        return {
            "success": success_rate >= 80,  # 80% threshold for success
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "detailed_results": self.test_results
        }

def main():
    """Main verification execution"""
    verifier = FocusedSystemVerifier()
    results = verifier.run_focused_verification()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()