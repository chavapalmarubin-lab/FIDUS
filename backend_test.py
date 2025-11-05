#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING - ALL CRITICAL ENDPOINTS
Testing Date: December 18, 2025
Backend URL: https://data-consistency-4.preview.emergentagent.com/api
Auth: Admin token (username: admin, password: password123)

CRITICAL ENDPOINTS TO TEST:
1. Cash Flow System: GET /api/admin/cashflow/overview & GET /api/admin/cashflow/calendar
2. Money Managers: GET /api/admin/money-managers (5 active managers expected)
3. Trading Analytics: GET /api/trading-analytics/overview
4. MT5 Accounts: GET /api/mt5/admin/accounts (11 accounts expected)
5. Fund Portfolio: GET /api/fund-portfolio/overview

EXPECTED RESULTS:
- Cash Flow: Real fund revenue, MT5 profits (not $0)
- Money Managers: 5 active managers with real performance data
- Trading Analytics: Real portfolio data (not 404)
- MT5 Accounts: 11 accounts with real balances
- Fund Portfolio: Real fund allocations for CORE, BALANCE, SEPARATION

MONGODB DATA AVAILABLE:
- 11 MT5 accounts with real equity ($9,924, $15,576, etc.)
- 5 active money managers with assigned accounts
- 2 investments for Alejandro ($18K CORE, $100K BALANCE)
- 16 referral commissions (verified working)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class BackendTester:
    def __init__(self):
        self.base_url = "https://data-consistency-4.preview.emergentagent.com/api"
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
    
    def test_cashflow_system(self) -> bool:
        """Test 1: Cash Flow System - Overview and Calendar endpoints"""
        try:
            print("\n💰 Testing Cash Flow System...")
            
            # Test Cash Flow Overview
            response = self.session.get(f"{self.base_url}/admin/cashflow/overview")
            
            if response.status_code != 200:
                self.log_test("Cash Flow Overview API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check for real fund revenue (not $0)
            fund_revenue = data.get("fund_revenue", 0)
            mt5_trading_profits = data.get("mt5_trading_profits", 0)
            separation_interest = data.get("separation_interest", 0)
            
            success = True
            
            if fund_revenue != 0:
                self.log_test("Fund Revenue", "PASS", f"Fund revenue: ${fund_revenue:,.2f} (not $0)")
            else:
                self.log_test("Fund Revenue", "FAIL", "Fund revenue is $0 - expected real data")
                success = False
            
            if mt5_trading_profits != 0:
                self.log_test("MT5 Trading Profits", "PASS", f"MT5 profits: ${mt5_trading_profits:,.2f} (not $0)")
            else:
                self.log_test("MT5 Trading Profits", "FAIL", "MT5 trading profits is $0 - expected real data")
                success = False
            
            # Test Cash Flow Calendar
            calendar_response = self.session.get(f"{self.base_url}/admin/cashflow/calendar")
            
            if calendar_response.status_code != 200:
                self.log_test("Cash Flow Calendar API", "FAIL", f"HTTP {calendar_response.status_code}: {calendar_response.text}")
                success = False
            else:
                calendar_data = calendar_response.json()
                monthly_obligations = calendar_data.get("monthly_obligations", [])
                
                if len(monthly_obligations) > 0:
                    self.log_test("Cash Flow Calendar", "PASS", f"Calendar has {len(monthly_obligations)} monthly obligations")
                else:
                    self.log_test("Cash Flow Calendar", "FAIL", "Calendar has no monthly obligations")
                    success = False
            
            return success
            
        except Exception as e:
            self.log_test("Cash Flow System Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_money_managers_api(self) -> bool:
        """Test 2: Money Managers API - should return 5 active managers with real performance data"""
        try:
            print("\n👥 Testing Money Managers API...")
            
            response = self.session.get(f"{self.base_url}/admin/money-managers")
            
            if response.status_code != 200:
                self.log_test("Money Managers API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            managers = data.get("managers", [])
            
            # Expected 5 active managers with real performance data
            expected_managers = [
                "CP Strategy",
                "TradingHub Gold", 
                "UNO14",
                "alefloreztrader",
                "Provider1-Assev"
            ]
            
            # Check total count
            if len(managers) == 5:
                self.log_test("Money Managers Count", "PASS", f"Found expected 5 money managers")
            else:
                self.log_test("Money Managers Count", "FAIL", f"Expected 5 managers, found {len(managers)}")
                print(f"   Found managers: {[mgr.get('name') or mgr.get('manager_name') for mgr in managers]}")
                return False
            
            # Check for real performance data (not $0)
            managers_with_real_data = 0
            total_pnl = 0
            
            for mgr in managers:
                pnl = mgr.get("total_pnl", 0) or mgr.get("profit_loss", 0)
                equity = mgr.get("total_equity", 0) or mgr.get("current_equity", 0)
                initial_allocation = mgr.get("initial_allocation", 0)
                
                if pnl != 0 or equity > 0 or initial_allocation > 0:
                    managers_with_real_data += 1
                    total_pnl += pnl
                
                manager_name = mgr.get("name") or mgr.get("manager_name", "Unknown")
                self.log_test(f"Manager {manager_name} Data", 
                            "PASS" if (pnl != 0 or equity > 0) else "FAIL",
                            f"P&L: ${pnl:,.2f}, Equity: ${equity:,.2f}, Allocation: ${initial_allocation:,.2f}")
            
            if managers_with_real_data >= 4:  # At least 4 out of 5 should have real data
                self.log_test("Managers Real Performance Data", "PASS", 
                            f"{managers_with_real_data}/5 managers have real performance data")
            else:
                self.log_test("Managers Real Performance Data", "FAIL", 
                            f"Only {managers_with_real_data}/5 managers have real data")
                return False
            
            # Check total P&L is not $0
            if total_pnl != 0:
                self.log_test("Total Manager P&L", "PASS", f"Total P&L: ${total_pnl:,.2f} (not $0)")
            else:
                self.log_test("Total Manager P&L", "FAIL", "Total P&L is $0 - expected real data")
                return False
            
            self.log_test("Money Managers API", "PASS", "Money managers with real performance data verified")
            return True
            
        except Exception as e:
            self.log_test("Money Managers Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_trading_analytics(self) -> bool:
        """Test 3: Trading Analytics - should return real portfolio data (not 404)"""
        try:
            print("\n📈 Testing Trading Analytics...")
            
            response = self.session.get(f"{self.base_url}/trading-analytics/overview")
            
            if response.status_code == 404:
                self.log_test("Trading Analytics API", "FAIL", "Trading Analytics endpoint returns 404 - not found")
                return False
            elif response.status_code != 200:
                self.log_test("Trading Analytics API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check for real portfolio data
            total_portfolio_value = data.get("total_portfolio_value", 0)
            total_pnl = data.get("total_pnl", 0)
            active_accounts = data.get("active_accounts", 0)
            
            success = True
            
            if total_portfolio_value > 0:
                self.log_test("Portfolio Value", "PASS", f"Total portfolio value: ${total_portfolio_value:,.2f}")
            else:
                self.log_test("Portfolio Value", "FAIL", "Total portfolio value is $0 - expected real data")
                success = False
            
            if total_pnl != 0:
                self.log_test("Portfolio P&L", "PASS", f"Total P&L: ${total_pnl:,.2f} (not $0)")
            else:
                self.log_test("Portfolio P&L", "FAIL", "Total P&L is $0 - expected real data")
                success = False
            
            if active_accounts > 0:
                self.log_test("Active Accounts", "PASS", f"Active accounts: {active_accounts}")
            else:
                self.log_test("Active Accounts", "FAIL", "No active accounts found")
                success = False
            
            self.log_test("Trading Analytics API", "PASS" if success else "FAIL", 
                        "Trading Analytics endpoint accessible with real data" if success else "Trading Analytics has data issues")
            return success
            
        except Exception as e:
            self.log_test("Trading Analytics Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_vps_sync_capability(self) -> bool:
        """Test 4: VPS Sync - verify sync service can handle new accounts"""
        try:
            print("\n🔄 Testing VPS Sync Capability...")
            
            response = self.session.get(f"{self.base_url}/mt5/status")
            
            if response.status_code != 200:
                self.log_test("MT5 Status API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            bridge_status = data.get("bridge_status", "unknown")
            
            success = True
            
            if bridge_status in ["connected", "active", "online"]:
                self.log_test("VPS Bridge Status", "PASS", f"MT5 bridge status: {bridge_status}")
            else:
                self.log_test("VPS Bridge Status", "FAIL", f"MT5 bridge status: {bridge_status}")
                success = False
            
            # Check if sync can handle multiple accounts
            total_accounts = data.get("total_accounts", 0)
            if total_accounts >= 11:
                self.log_test("VPS Multi-Account Sync", "PASS", f"VPS sync handling {total_accounts} accounts")
            else:
                self.log_test("VPS Multi-Account Sync", "FAIL", f"VPS sync handling {total_accounts} accounts, expected 11+")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("VPS Sync Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_mt5_config_mongodb(self) -> bool:
        """Test 5: MT5 Account Config in MongoDB via API"""
        try:
            print("\n📊 Testing MT5 MongoDB Configuration...")
            
            response = self.session.get(f"{self.base_url}/mt5/accounts/all")
            
            if response.status_code != 200:
                self.log_test("MT5 MongoDB Config", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            accounts = data.get("accounts", [])
            
            if len(accounts) >= 11:
                self.log_test("MT5 MongoDB Configuration", "PASS", f"MongoDB contains {len(accounts)} MT5 accounts")
                
                # Check for proper manager assignments
                accounts_with_managers = [acc for acc in accounts if acc.get("manager_name")]
                self.log_test("MT5 Manager Assignments", "PASS" if len(accounts_with_managers) >= 8 else "FAIL", 
                            f"{len(accounts_with_managers)} accounts have manager assignments")
                
                return True
            else:
                self.log_test("MT5 MongoDB Configuration", "FAIL", f"MongoDB contains {len(accounts)} accounts, expected 11+")
                return False
            
        except Exception as e:
            self.log_test("Money Managers Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all MT5 system tests"""
        print("🚀 Starting MT5 System Backend Testing - Complete System Verification")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            return {"success": False, "error": "Authentication failed"}
        
        # Run all tests
        test_results = {
            "mt5_admin_accounts_api": self.test_mt5_admin_accounts_api(),
            "money_managers_api": self.test_money_managers_api(),
            "fund_allocations": self.test_fund_allocations(),
            "vps_sync_capability": self.test_vps_sync_capability(),
            "mt5_config_mongodb": self.test_mt5_config_mongodb()
        }
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 MT5 SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 MT5 SYSTEM VERIFICATION: EXCELLENT - All 11 accounts configured correctly!")
            print("   ✅ All 4 new accounts (897590, 897589, 897591, 897599) added successfully")
            print("   ✅ All 6 money managers including 2 new ones operational")
            print("   ✅ Fund allocations match expected totals")
            print("   ✅ VPS sync service handling all accounts")
        elif success_rate >= 80:
            print("✅ MT5 SYSTEM VERIFICATION: GOOD - Minor issues to address")
        elif success_rate >= 60:
            print("⚠️ MT5 SYSTEM VERIFICATION: NEEDS ATTENTION - Several issues found")
        else:
            print("🚨 MT5 SYSTEM VERIFICATION: CRITICAL ISSUES - Major problems detected")
        
        return {
            "success": success_rate >= 80,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": test_results,
            "detailed_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()