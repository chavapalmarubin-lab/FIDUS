#!/usr/bin/env python3
"""
URGENT: MT5 Manual Account Creation Testing for client_alejandro

Testing the manual MT5 account creation endpoint to create the 4 missing accounts 
for client_alejandro as specified in the review request.

Expected Accounts to Create:
1. BALANCE - $80,000 (mt5_login: 886557)
2. BALANCE - $10,000 (mt5_login: 886066) 
3. BALANCE - $10,000 (mt5_login: 886602)
4. CORE - $18,151.41 (mt5_login: 885822)

All accounts use:
- broker_code: multibank
- mt5_password: FIDUS13@
- mt5_server: MEXAtlantic-Real
"""

import requests
import json
import sys
from datetime import datetime

# Use the correct backend URL from frontend/.env
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class MT5ManualAccountTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.created_accounts = []
        
    def log_test(self, test_name, success, details, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_admin_authentication(self):
        """Test admin login with credentials admin/password123"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        
        try:
            login_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as {data.get('name', 'admin')} with JWT token",
                        {"user_id": data.get("id"), "username": data.get("username"), "type": data.get("type")}
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", data)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_existing_mt5_accounts(self):
        """Check existing MT5 accounts for client_alejandro before creation"""
        print("\n🔍 CHECKING EXISTING MT5 ACCOUNTS")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                
                self.log_test(
                    "Existing MT5 Accounts Check",
                    True,
                    f"Found {len(accounts)} existing MT5 accounts for client_alejandro",
                    {"account_count": len(accounts), "accounts": [{"login": acc.get("mt5_login"), "broker": acc.get("broker_name")} for acc in accounts]}
                )
                return True
            else:
                self.log_test("Existing MT5 Accounts Check", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Existing MT5 Accounts Check", False, f"Exception: {str(e)}")
            return False
    
    def create_mt5_account(self, account_data, account_name):
        """Create a single MT5 account"""
        print(f"\n💳 CREATING MT5 ACCOUNT: {account_name}")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/mt5/admin/add-manual-account", json=account_data)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                
                if data.get("success", False):
                    self.created_accounts.append({
                        "name": account_name,
                        "mt5_login": account_data["mt5_login"],
                        "fund_code": account_data["fund_code"],
                        "response": data
                    })
                    
                    self.log_test(
                        f"MT5 Account Creation - {account_name}",
                        True,
                        f"Successfully created MT5 account {account_data['mt5_login']} for {account_data['fund_code']} fund",
                        {"mt5_login": account_data["mt5_login"], "fund_code": account_data["fund_code"], "broker": account_data["broker_code"]}
                    )
                    return True
                else:
                    self.log_test(
                        f"MT5 Account Creation - {account_name}",
                        False,
                        f"Account creation failed: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    f"MT5 Account Creation - {account_name}",
                    False,
                    f"HTTP {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test(f"MT5 Account Creation - {account_name}", False, f"Exception: {str(e)}")
            return False
    
    def test_create_all_mt5_accounts(self):
        """Create all 4 MT5 accounts for client_alejandro"""
        print("\n🏦 CREATING ALL MT5 ACCOUNTS FOR CLIENT_ALEJANDRO")
        
        # Account definitions from review request
        accounts_to_create = [
            {
                "name": "BALANCE Account 1 ($80,000)",
                "data": {
                    "client_id": "client_alejandro",
                    "fund_code": "BALANCE",
                    "broker_code": "multibank",
                    "mt5_login": "886557",
                    "mt5_password": "FIDUS13@",
                    "mt5_server": "MEXAtlantic-Real"
                }
            },
            {
                "name": "BALANCE Account 2 ($10,000)",
                "data": {
                    "client_id": "client_alejandro",
                    "fund_code": "BALANCE",
                    "broker_code": "multibank",
                    "mt5_login": "886066",
                    "mt5_password": "FIDUS13@",
                    "mt5_server": "MEXAtlantic-Real"
                }
            },
            {
                "name": "BALANCE Account 3 ($10,000)",
                "data": {
                    "client_id": "client_alejandro",
                    "fund_code": "BALANCE",
                    "broker_code": "multibank",
                    "mt5_login": "886602",
                    "mt5_password": "FIDUS13@",
                    "mt5_server": "MEXAtlantic-Real"
                }
            },
            {
                "name": "CORE Account ($18,151.41)",
                "data": {
                    "client_id": "client_alejandro",
                    "fund_code": "CORE",
                    "broker_code": "multibank",
                    "mt5_login": "885822",
                    "mt5_password": "FIDUS13@",
                    "mt5_server": "MEXAtlantic-Real"
                }
            }
        ]
        
        successful_creations = 0
        
        for account in accounts_to_create:
            if self.create_mt5_account(account["data"], account["name"]):
                successful_creations += 1
        
        # Overall result
        if successful_creations == 4:
            self.log_test(
                "All MT5 Accounts Creation",
                True,
                f"Successfully created all 4 MT5 accounts for client_alejandro",
                {"created_count": successful_creations, "total_expected": 4}
            )
            return True
        else:
            self.log_test(
                "All MT5 Accounts Creation",
                False,
                f"Only created {successful_creations}/4 MT5 accounts",
                {"created_count": successful_creations, "total_expected": 4}
            )
            return False
    
    def test_verify_created_accounts(self):
        """Verify that all 4 accounts were created successfully"""
        print("\n✅ VERIFYING CREATED MT5 ACCOUNTS")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                
                # Check for the specific account logins we created
                expected_logins = ["886557", "886066", "886602", "885822"]
                found_logins = [str(int(acc.get("mt5_account_number", 0))) for acc in accounts if str(int(acc.get("mt5_account_number", 0))) in expected_logins]
                
                if len(found_logins) == 4:
                    self.log_test(
                        "MT5 Accounts Verification",
                        True,
                        f"All 4 expected MT5 accounts found: {', '.join(found_logins)}",
                        {"total_accounts": len(accounts), "expected_accounts": found_logins}
                    )
                    return True
                else:
                    missing_logins = [login for login in expected_logins if login not in found_logins]
                    self.log_test(
                        "MT5 Accounts Verification",
                        False,
                        f"Missing {len(missing_logins)} accounts: {', '.join(missing_logins)}. Found: {', '.join(found_logins)}",
                        {"total_accounts": len(accounts), "found_accounts": found_logins, "missing_accounts": missing_logins}
                    )
                    return False
            else:
                self.log_test("MT5 Accounts Verification", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("MT5 Accounts Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_endpoint_availability(self):
        """Test if the MT5 manual account creation endpoint exists"""
        print("\n🔗 TESTING MT5 ENDPOINT AVAILABILITY")
        
        try:
            # Test with invalid data to see if endpoint exists
            test_data = {"test": "endpoint_check"}
            response = self.session.post(f"{BACKEND_URL}/mt5/admin/add-manual-account", json=test_data)
            
            # Any response other than 404 means endpoint exists
            if response.status_code != 404:
                self.log_test(
                    "MT5 Manual Account Endpoint",
                    True,
                    f"Endpoint exists (HTTP {response.status_code})",
                    {"status_code": response.status_code}
                )
                return True
            else:
                self.log_test(
                    "MT5 Manual Account Endpoint",
                    False,
                    "Endpoint not found (HTTP 404)",
                    {"status_code": 404}
                )
                return False
                
        except Exception as e:
            self.log_test("MT5 Manual Account Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all MT5 manual account creation tests"""
        print("🚨 URGENT: MT5 Manual Account Creation Testing")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Client: client_alejandro")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Admin Authentication", self.test_admin_authentication),
            ("MT5 Endpoint Availability", self.test_mt5_endpoint_availability),
            ("Existing MT5 Accounts Check", self.test_existing_mt5_accounts),
            ("Create All MT5 Accounts", self.test_create_all_mt5_accounts),
            ("Verify Created Accounts", self.test_verify_created_accounts)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 MT5 MANUAL ACCOUNT CREATION TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Account creation summary
        if self.created_accounts:
            print(f"\n✅ SUCCESSFULLY CREATED ACCOUNTS:")
            for account in self.created_accounts:
                print(f"   - {account['name']}: MT5 Login {account['mt5_login']} ({account['fund_code']} fund)")
        
        # Critical findings
        critical_issues = []
        for result in self.test_results:
            if not result["success"]:
                critical_issues.append(result["test"])
        
        if critical_issues:
            print(f"\n🚨 ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   - {issue}")
        
        # Final recommendation
        print(f"\n📋 FINAL STATUS:")
        if success_rate == 100:
            print("   ✅ ALL MT5 ACCOUNTS CREATED SUCCESSFULLY - User complaint should be resolved")
        elif success_rate >= 80:
            print("   ⚠️ MOSTLY SUCCESSFUL - Some accounts created, check individual failures")
        else:
            print("   ❌ CRITICAL FAILURE - MT5 account creation system not working")
        
        return success_rate >= 80  # 80% success rate threshold

if __name__ == "__main__":
    tester = MT5ManualAccountTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)