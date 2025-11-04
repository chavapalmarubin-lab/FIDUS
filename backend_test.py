#!/usr/bin/env python3
"""
MT5 SYSTEM BACKEND TESTING - Complete System Verification After Adding 4 New Accounts
Testing Date: December 18, 2025
Backend URL: https://referral-tracker-8.preview.emergentagent.com/api
Auth: Admin token (username: admin, password: password123)

Test Objectives:
1. Verify MT5 Account Config in MongoDB - All 11 accounts should be present
2. Test MT5 Admin Accounts API - GET /api/mt5/admin/accounts should return all 11 accounts  
3. Test Money Managers API - GET /api/admin/money-managers should return 6 managers
4. Verify Fund Allocations - Check fund totals for CORE, BALANCE, SEPARATION
5. Test VPS Sync - Verify VPS sync service can handle new accounts

Expected Results:
- MongoDB should have all 11 accounts configured
- APIs should return all accounts and managers correctly
- All new accounts should have proper manager assignments
- Initial allocations should match the real MT5 balances from screenshot

New Accounts Added: 897590, 897589, 897591, 897599
New Managers Added: MEXAtlantic Provider 5201, alefloreztrader
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class BackendTester:
    def __init__(self):
        self.base_url = "https://referral-tracker-8.preview.emergentagent.com/api"
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
    
    def test_mt5_admin_accounts_api(self) -> bool:
        """Test 1: MT5 Admin Accounts API - should return all 11 accounts"""
        try:
            print("\n📊 Testing MT5 Admin Accounts API...")
            
            response = self.session.get(f"{self.base_url}/mt5/admin/accounts")
            
            if response.status_code != 200:
                self.log_test("MT5 Admin Accounts API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            accounts = data.get("accounts", [])
            
            # Expected MT5 accounts (11 total: 7 original + 4 new)
            expected_accounts = [
                {"account": "885822", "fund_code": "CORE"},
                {"account": "886557", "fund_code": "BALANCE"}, 
                {"account": "886066", "fund_code": "BALANCE"},
                {"account": "886602", "fund_code": "BALANCE"},
                {"account": "886528", "fund_code": "SEPARATION"},
                {"account": "891215", "fund_code": "SEPARATION"},
                {"account": "891234", "fund_code": "CORE"},
                # New accounts
                {"account": "897590", "fund_code": "CORE"},
                {"account": "897589", "fund_code": "BALANCE"},
                {"account": "897591", "fund_code": "SEPARATION"},
                {"account": "897599", "fund_code": "SEPARATION"}
            ]
            
            # Check total count
            if len(accounts) == 11:
                self.log_test("MT5 Account Count", "PASS", f"Found expected 11 MT5 accounts")
            else:
                self.log_test("MT5 Account Count", "FAIL", f"Expected 11 accounts, found {len(accounts)}")
                return False
            
            # Check specific accounts exist
            found_accounts = {acc.get("account"): acc.get("fund_code") for acc in accounts}
            missing_accounts = []
            wrong_fund_codes = []
            
            for expected in expected_accounts:
                account_num = expected["account"]
                expected_fund = expected["fund_code"]
                
                if account_num not in found_accounts:
                    missing_accounts.append(account_num)
                elif found_accounts[account_num] != expected_fund:
                    wrong_fund_codes.append({
                        "account": account_num,
                        "expected": expected_fund,
                        "actual": found_accounts[account_num]
                    })
            
            if missing_accounts:
                self.log_test("MT5 Account Verification", "FAIL", f"Missing accounts: {missing_accounts}")
                return False
                
            if wrong_fund_codes:
                self.log_test("MT5 Fund Code Verification", "FAIL", f"Wrong fund codes: {wrong_fund_codes}")
                return False
            
            # Check new accounts specifically
            new_accounts = ["897590", "897589", "897591", "897599"]
            found_new = [acc for acc in found_accounts.keys() if acc in new_accounts]
            
            if len(found_new) == 4:
                self.log_test("New MT5 Accounts", "PASS", f"All 4 new accounts found: {found_new}")
            else:
                self.log_test("New MT5 Accounts", "FAIL", f"Expected 4 new accounts, found {len(found_new)}: {found_new}")
                return False
            
            self.log_test("MT5 Admin Accounts API", "PASS", "All MT5 accounts verified successfully")
            return True
            
        except Exception as e:
            self.log_test("Fund Portfolio Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_money_managers_api(self) -> bool:
        """Test 2: Money Managers API - should return 6 managers including 2 new ones"""
        try:
            print("\n👥 Testing Money Managers API...")
            
            response = self.session.get(f"{self.base_url}/admin/money-managers")
            
            if response.status_code != 200:
                self.log_test("Money Managers API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            managers = data.get("managers", [])
            
            # Expected managers (6 total including 2 new ones)
            expected_managers = [
                "CP Strategy",
                "TradingHub Gold", 
                "GoldenTrade",
                "UNO14 MAM Manager",
                "MEXAtlantic Provider 5201",  # New manager
                "alefloreztrader"  # New manager
            ]
            
            # Check total count
            if len(managers) == 6:
                self.log_test("Money Managers Count", "PASS", f"Found expected 6 money managers")
            else:
                self.log_test("Money Managers Count", "FAIL", f"Expected 6 managers, found {len(managers)}")
                return False
            
            # Check specific managers exist
            found_managers = [mgr.get("name") or mgr.get("manager_name") for mgr in managers]
            missing_managers = []
            
            for expected_manager in expected_managers:
                # Allow partial matching for manager names
                found = any(expected_manager in found_name for found_name in found_managers if found_name)
                if not found:
                    missing_managers.append(expected_manager)
            
            if missing_managers:
                self.log_test("Money Managers Verification", "FAIL", f"Missing managers: {missing_managers}")
                return False
            
            # Check new managers specifically
            new_managers = ["MEXAtlantic Provider 5201", "alefloreztrader"]
            found_new_managers = []
            for new_mgr in new_managers:
                found = any(new_mgr in found_name for found_name in found_managers if found_name)
                if found:
                    found_new_managers.append(new_mgr)
            
            if len(found_new_managers) == 2:
                self.log_test("New Money Managers", "PASS", f"Both new managers found: {found_new_managers}")
            else:
                self.log_test("New Money Managers", "FAIL", f"Expected 2 new managers, found {len(found_new_managers)}")
                return False
            
            self.log_test("Money Managers API", "PASS", "All money managers verified successfully")
            return True
            
        except Exception as e:
            self.log_test("Cash Flow Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_fund_allocations(self) -> bool:
        """Test 3: Fund Allocations - verify fund totals are correct"""
        try:
            print("\n💰 Testing Fund Allocations...")
            
            response = self.session.get(f"{self.base_url}/fund-portfolio/overview")
            
            if response.status_code != 200:
                self.log_test("Fund Portfolio API", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            funds = data.get("funds", [])
            
            # Expected fund totals
            expected_totals = {
                "CORE": 18151.41,  # accounts: 885822, 897590, 891234
                "BALANCE": 100979,  # accounts: 886557, 886602, 886066, 891215, 897589 (approx)
                "SEPARATION": 20653  # accounts: 886528, 897591, 897599
            }
            
            fund_totals = {}
            for fund in funds:
                fund_code = fund.get("fund_code")
                total_allocated = fund.get("total_allocated", 0)
                fund_totals[fund_code] = total_allocated
            
            success = True
            
            # Check CORE fund
            core_total = fund_totals.get("CORE", 0)
            expected_core = expected_totals["CORE"]
            if abs(core_total - expected_core) < 100:  # Allow small variance
                self.log_test("CORE Fund Allocation", "PASS", f"CORE fund total: ${core_total:,.2f}")
            else:
                self.log_test("CORE Fund Allocation", "FAIL", f"CORE fund total: ${core_total:,.2f}, expected: ${expected_core:,.2f}")
                success = False
            
            # Check BALANCE fund (approximate)
            balance_total = fund_totals.get("BALANCE", 0)
            expected_balance = expected_totals["BALANCE"]
            if abs(balance_total - expected_balance) < 5000:  # Allow larger variance for BALANCE
                self.log_test("BALANCE Fund Allocation", "PASS", f"BALANCE fund total: ${balance_total:,.2f}")
            else:
                self.log_test("BALANCE Fund Allocation", "FAIL", f"BALANCE fund total: ${balance_total:,.2f}, expected: ~${expected_balance:,.2f}")
                success = False
            
            # Check SEPARATION fund
            separation_total = fund_totals.get("SEPARATION", 0)
            expected_separation = expected_totals["SEPARATION"]
            if abs(separation_total - expected_separation) < 1000:  # Allow moderate variance
                self.log_test("SEPARATION Fund Allocation", "PASS", f"SEPARATION fund total: ${separation_total:,.2f}")
            else:
                self.log_test("SEPARATION Fund Allocation", "FAIL", f"SEPARATION fund total: ${separation_total:,.2f}, expected: ${expected_separation:,.2f}")
                success = False
            
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