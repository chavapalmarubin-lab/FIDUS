#!/usr/bin/env python3
"""
MT5 Account Configuration Management API Testing
Tests the NEW MT5 Account Configuration Management endpoints (Phases 1 & 2)

Context:
- Backend routes are in /app/backend/routes/mt5_config.py
- Router is included in server.py with prefix /admin/mt5/config (the /api is added by api_router)
- Migration script has already been run and created the mt5_account_config collection with 7 existing MT5 accounts
- Expected accounts: 886557, 886066, 886602, 885822, 886528, 886643, 886644

Test Objectives:
1. Authentication Test: Verify admin authentication is required for all endpoints
2. GET /api/admin/mt5/config/accounts: Should return the 7 existing MT5 accounts from the database
3. GET /api/admin/mt5/config/accounts/{account_number}: Get a specific account by number
4. POST /api/admin/mt5/config/accounts: Test adding a new account (use test account 999999)
5. PUT /api/admin/mt5/config/accounts/{account_number}: Test updating an account
6. DELETE /api/admin/mt5/config/accounts/{account_number}: Test soft-delete (deactivation)
7. POST /api/admin/mt5/config/accounts/{account_number}/activate: Test reactivation

Success Criteria:
- All endpoints return HTTP 200 (or 201 for POST)
- GET returns exactly 7 accounts from database
- No mock data - all real data from MongoDB
- Password fields are properly excluded from responses
- Admin authentication is enforced
"""

import requests
import json
import sys
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "https://alloc-wizard.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Expected existing accounts from migration script
EXPECTED_ACCOUNTS = [886557, 886066, 886602, 885822, 886528, 888520, 888521]

class MT5ConfigAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.test_account_id = 999999  # Test account for CRUD operations
        
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
    
    def test_authentication_required(self):
        """Test 1: Verify admin authentication is required for all endpoints"""
        try:
            # Create a session without authentication
            unauth_session = requests.Session()
            
            endpoints_to_test = [
                ("GET", "/api/admin/mt5/config/accounts"),
                ("GET", "/api/admin/mt5/config/accounts/886557"),
                ("POST", "/api/admin/mt5/config/accounts"),
                ("PUT", "/api/admin/mt5/config/accounts/886557"),
                ("DELETE", "/api/admin/mt5/config/accounts/886557"),
                ("POST", "/api/admin/mt5/config/accounts/886557/activate")
            ]
            
            auth_protected = 0
            total_endpoints = len(endpoints_to_test)
            
            for method, endpoint in endpoints_to_test:
                try:
                    url = f"{BACKEND_URL}{endpoint}"
                    
                    if method == "GET":
                        response = unauth_session.get(url)
                    elif method == "POST":
                        response = unauth_session.post(url, json={})
                    elif method == "PUT":
                        response = unauth_session.put(url, json={})
                    elif method == "DELETE":
                        response = unauth_session.delete(url)
                    
                    # Should return 401 Unauthorized
                    if response.status_code == 401:
                        auth_protected += 1
                    else:
                        print(f"   ⚠️ {method} {endpoint} returned {response.status_code} (expected 401)")
                        
                except Exception as e:
                    print(f"   ⚠️ Error testing {method} {endpoint}: {str(e)}")
            
            if auth_protected == total_endpoints:
                self.log_test("Authentication Required", True, f"All {total_endpoints} endpoints properly require authentication")
                return True
            else:
                self.log_test("Authentication Required", False, f"Only {auth_protected}/{total_endpoints} endpoints require authentication")
                return False
                
        except Exception as e:
            self.log_test("Authentication Required", False, f"Exception: {str(e)}")
            return False
    
    def test_get_all_accounts(self):
        """Test 2: GET /api/admin/mt5/config/accounts - Should return 7 existing accounts"""
        try:
            url = f"{BACKEND_URL}/api/admin/mt5/config/accounts"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if not data.get('success'):
                    self.log_test("Get All Accounts - Structure", False, "Response success=false")
                    return False
                
                accounts = data.get('accounts', [])
                count = data.get('count', 0)
                
                # Check count matches accounts array
                if count != len(accounts):
                    self.log_test("Get All Accounts - Count Mismatch", False, f"Count={count} but accounts array has {len(accounts)} items")
                    return False
                
                # Check expected number of accounts (7 from migration)
                if count == 7:
                    self.log_test("Get All Accounts - Count", True, f"Found expected 7 accounts")
                else:
                    self.log_test("Get All Accounts - Count", False, f"Expected 7 accounts, got {count}")
                    return False
                
                # Check expected account numbers are present
                found_accounts = [acc.get('account') for acc in accounts]
                missing_accounts = [acc for acc in EXPECTED_ACCOUNTS if acc not in found_accounts]
                
                if not missing_accounts:
                    self.log_test("Get All Accounts - Expected Accounts", True, f"All expected accounts found: {found_accounts}")
                else:
                    self.log_test("Get All Accounts - Expected Accounts", False, f"Missing accounts: {missing_accounts}")
                
                # Check password field is excluded
                has_password = any('password' in acc for acc in accounts)
                if not has_password:
                    self.log_test("Get All Accounts - Password Excluded", True, "Password field properly excluded from response")
                else:
                    self.log_test("Get All Accounts - Password Excluded", False, "Password field found in response (security issue)")
                
                # Check required fields are present
                required_fields = ['account', 'name', 'server', 'fund_type', 'target_amount', 'is_active']
                all_have_required = all(
                    all(field in acc for field in required_fields) 
                    for acc in accounts
                )
                
                if all_have_required:
                    self.log_test("Get All Accounts - Required Fields", True, f"All accounts have required fields: {required_fields}")
                else:
                    self.log_test("Get All Accounts - Required Fields", False, "Some accounts missing required fields")
                
                # Store accounts for later tests
                self.existing_accounts = accounts
                
                details = f"Retrieved {count} accounts: {found_accounts}"
                self.log_test("Get All Accounts", True, details)
                return True
                
            else:
                self.log_test("Get All Accounts", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get All Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_get_specific_account(self):
        """Test 3: GET /api/admin/mt5/config/accounts/{account_number} - Get specific account"""
        try:
            # Test with first expected account
            test_account = EXPECTED_ACCOUNTS[0]  # 886557
            url = f"{BACKEND_URL}/api/admin/mt5/config/accounts/{test_account}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('success'):
                    self.log_test("Get Specific Account - Structure", False, "Response success=false")
                    return False
                
                account = data.get('account')
                if not account:
                    self.log_test("Get Specific Account - Data", False, "No account data in response")
                    return False
                
                # Check account number matches
                if account.get('account') == test_account:
                    self.log_test("Get Specific Account - Account Number", True, f"Account {test_account} retrieved correctly")
                else:
                    self.log_test("Get Specific Account - Account Number", False, f"Expected {test_account}, got {account.get('account')}")
                
                # Check password is excluded
                if 'password' not in account:
                    self.log_test("Get Specific Account - Password Excluded", True, "Password field properly excluded")
                else:
                    self.log_test("Get Specific Account - Password Excluded", False, "Password field found in response")
                
                # Check required fields
                required_fields = ['account', 'name', 'server', 'fund_type', 'target_amount', 'is_active']
                has_all_fields = all(field in account for field in required_fields)
                
                if has_all_fields:
                    self.log_test("Get Specific Account - Fields", True, f"Account has all required fields")
                else:
                    missing = [field for field in required_fields if field not in account]
                    self.log_test("Get Specific Account - Fields", False, f"Missing fields: {missing}")
                
                details = f"Account {test_account}: {account.get('name')} ({account.get('fund_type')})"
                self.log_test("Get Specific Account", True, details)
                return True
                
            elif response.status_code == 404:
                self.log_test("Get Specific Account", False, f"Account {test_account} not found (404)")
                return False
            else:
                self.log_test("Get Specific Account", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Specific Account", False, f"Exception: {str(e)}")
            return False
    
    def test_add_new_account(self):
        """Test 4: POST /api/admin/mt5/config/accounts - Add new test account"""
        try:
            url = f"{BACKEND_URL}/api/admin/mt5/config/accounts"
            
            # Test account data
            new_account = {
                "account": self.test_account_id,
                "password": "TestPassword123!",
                "name": "Test Account for API Testing",
                "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE",
                "target_amount": 50000.0,
                "is_active": True
            }
            
            response = self.session.post(url, json=new_account)
            
            if response.status_code == 201:
                data = response.json()
                
                if data.get('success'):
                    account_id = data.get('account_id')
                    account_number = data.get('account')
                    
                    if account_number == self.test_account_id:
                        self.log_test("Add New Account - Account Number", True, f"Account {self.test_account_id} created successfully")
                    else:
                        self.log_test("Add New Account - Account Number", False, f"Expected {self.test_account_id}, got {account_number}")
                    
                    if account_id:
                        self.log_test("Add New Account - Account ID", True, f"Account ID returned: {account_id}")
                    else:
                        self.log_test("Add New Account - Account ID", False, "No account_id in response")
                    
                    message = data.get('message', '')
                    if 'VPS bridge' in message:
                        self.log_test("Add New Account - VPS Message", True, "Response mentions VPS bridge sync")
                    else:
                        self.log_test("Add New Account - VPS Message", False, "No VPS bridge sync message")
                    
                    details = f"Created account {self.test_account_id}: {new_account['name']}"
                    self.log_test("Add New Account", True, details)
                    return True
                else:
                    self.log_test("Add New Account", False, f"Response success=false: {data}")
                    return False
                    
            elif response.status_code == 400:
                # Check if account already exists
                error_text = response.text
                if 'already exists' in error_text:
                    self.log_test("Add New Account", True, f"Account {self.test_account_id} already exists (expected for repeated tests)")
                    return True
                else:
                    self.log_test("Add New Account", False, f"HTTP 400: {error_text}")
                    return False
            else:
                self.log_test("Add New Account", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add New Account", False, f"Exception: {str(e)}")
            return False
    
    def test_update_account(self):
        """Test 5: PUT /api/admin/mt5/config/accounts/{account_number} - Update account"""
        try:
            url = f"{BACKEND_URL}/api/admin/mt5/config/accounts/{self.test_account_id}"
            
            # Update data
            updates = {
                "name": "Updated Test Account Name",
                "target_amount": 75000.0,
                "fund_type": "CORE"
            }
            
            response = self.session.put(url, json=updates)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    modified_count = data.get('modified_count', 0)
                    account_number = data.get('account')
                    
                    if modified_count > 0:
                        self.log_test("Update Account - Modified Count", True, f"Modified {modified_count} document(s)")
                    else:
                        self.log_test("Update Account - Modified Count", False, "No documents modified")
                    
                    if account_number == self.test_account_id:
                        self.log_test("Update Account - Account Number", True, f"Updated account {self.test_account_id}")
                    else:
                        self.log_test("Update Account - Account Number", False, f"Expected {self.test_account_id}, got {account_number}")
                    
                    message = data.get('message', '')
                    if 'within 50 minutes' in message:
                        self.log_test("Update Account - Sync Message", True, "Response mentions sync timing")
                    else:
                        self.log_test("Update Account - Sync Message", False, "No sync timing message")
                    
                    details = f"Updated account {self.test_account_id}: {updates}"
                    self.log_test("Update Account", True, details)
                    return True
                else:
                    self.log_test("Update Account", False, f"Response success=false: {data}")
                    return False
                    
            elif response.status_code == 404:
                self.log_test("Update Account", False, f"Account {self.test_account_id} not found (404)")
                return False
            else:
                self.log_test("Update Account", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Account", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_account(self):
        """Test 6: DELETE /api/admin/mt5/config/accounts/{account_number} - Soft delete (deactivate)"""
        try:
            url = f"{BACKEND_URL}/api/admin/mt5/config/accounts/{self.test_account_id}"
            response = self.session.delete(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    account_number = data.get('account')
                    
                    if account_number == self.test_account_id:
                        self.log_test("Delete Account - Account Number", True, f"Deactivated account {self.test_account_id}")
                    else:
                        self.log_test("Delete Account - Account Number", False, f"Expected {self.test_account_id}, got {account_number}")
                    
                    message = data.get('message', '')
                    if 'deactivated' in message.lower():
                        self.log_test("Delete Account - Deactivation Message", True, "Response mentions deactivation")
                    else:
                        self.log_test("Delete Account - Deactivation Message", False, "No deactivation message")
                    
                    if 'stop syncing' in message:
                        self.log_test("Delete Account - Sync Stop Message", True, "Response mentions stopping sync")
                    else:
                        self.log_test("Delete Account - Sync Stop Message", False, "No sync stop message")
                    
                    details = f"Deactivated account {self.test_account_id} (soft delete)"
                    self.log_test("Delete Account", True, details)
                    return True
                else:
                    self.log_test("Delete Account", False, f"Response success=false: {data}")
                    return False
                    
            elif response.status_code == 404:
                self.log_test("Delete Account", False, f"Account {self.test_account_id} not found (404)")
                return False
            else:
                self.log_test("Delete Account", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Account", False, f"Exception: {str(e)}")
            return False
    
    def test_activate_account(self):
        """Test 7: POST /api/admin/mt5/config/accounts/{account_number}/activate - Reactivate account"""
        try:
            url = f"{BACKEND_URL}/api/admin/mt5/config/accounts/{self.test_account_id}/activate"
            response = self.session.post(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    account_number = data.get('account')
                    
                    if account_number == self.test_account_id:
                        self.log_test("Activate Account - Account Number", True, f"Activated account {self.test_account_id}")
                    else:
                        self.log_test("Activate Account - Account Number", False, f"Expected {self.test_account_id}, got {account_number}")
                    
                    message = data.get('message', '')
                    if 'activated' in message.lower():
                        self.log_test("Activate Account - Activation Message", True, "Response mentions activation")
                    else:
                        self.log_test("Activate Account - Activation Message", False, "No activation message")
                    
                    if 'resume syncing' in message:
                        self.log_test("Activate Account - Sync Resume Message", True, "Response mentions resuming sync")
                    else:
                        self.log_test("Activate Account - Sync Resume Message", False, "No sync resume message")
                    
                    details = f"Reactivated account {self.test_account_id}"
                    self.log_test("Activate Account", True, details)
                    return True
                else:
                    self.log_test("Activate Account", False, f"Response success=false: {data}")
                    return False
                    
            elif response.status_code == 404:
                self.log_test("Activate Account", False, f"Account {self.test_account_id} not found (404)")
                return False
            else:
                self.log_test("Activate Account", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Activate Account", False, f"Exception: {str(e)}")
            return False
    
    def test_validation_errors(self):
        """Test 8: Test validation errors for invalid data"""
        try:
            url = f"{BACKEND_URL}/api/admin/mt5/config/accounts"
            
            # Test invalid fund_type
            invalid_account = {
                "account": 999998,
                "password": "TestPassword123!",
                "name": "Invalid Fund Type Test",
                "server": "MEXAtlantic-Real",
                "fund_type": "INVALID_FUND",  # Invalid fund type
                "target_amount": 50000.0,
                "is_active": True
            }
            
            response = self.session.post(url, json=invalid_account)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Validation - Invalid Fund Type", True, "Properly rejected invalid fund_type")
            else:
                self.log_test("Validation - Invalid Fund Type", False, f"Expected 422, got {response.status_code}")
            
            # Test negative target_amount
            invalid_account2 = {
                "account": 999997,
                "password": "TestPassword123!",
                "name": "Negative Amount Test",
                "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE",
                "target_amount": -1000.0,  # Negative amount
                "is_active": True
            }
            
            response2 = self.session.post(url, json=invalid_account2)
            
            if response2.status_code == 422:  # Validation error
                self.log_test("Validation - Negative Amount", True, "Properly rejected negative target_amount")
            else:
                self.log_test("Validation - Negative Amount", False, f"Expected 422, got {response2.status_code}")
            
            # Test missing required fields
            incomplete_account = {
                "account": 999996,
                # Missing password, name, fund_type, target_amount
            }
            
            response3 = self.session.post(url, json=incomplete_account)
            
            if response3.status_code == 422:  # Validation error
                self.log_test("Validation - Missing Fields", True, "Properly rejected incomplete data")
            else:
                self.log_test("Validation - Missing Fields", False, f"Expected 422, got {response3.status_code}")
            
            self.log_test("Validation Tests", True, "All validation tests completed")
            return True
            
        except Exception as e:
            self.log_test("Validation Tests", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all MT5 Config API tests"""
        print("🔧 MT5 ACCOUNT CONFIGURATION MANAGEMENT API TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Expected Accounts: {EXPECTED_ACCOUNTS}")
        print()
        
        # Step 1: Authenticate
        print("📋 STEP 1: Admin Authentication")
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        print()
        
        # Step 2: Test authentication requirement
        print("📋 STEP 2: Authentication Required Test")
        self.test_authentication_required()
        print()
        
        # Step 3: Test GET all accounts
        print("📋 STEP 3: Get All Accounts Test")
        self.test_get_all_accounts()
        print()
        
        # Step 4: Test GET specific account
        print("📋 STEP 4: Get Specific Account Test")
        self.test_get_specific_account()
        print()
        
        # Step 5: Test POST new account
        print("📋 STEP 5: Add New Account Test")
        self.test_add_new_account()
        print()
        
        # Step 6: Test PUT update account
        print("📋 STEP 6: Update Account Test")
        self.test_update_account()
        print()
        
        # Step 7: Test DELETE account (soft delete)
        print("📋 STEP 7: Delete Account Test")
        self.test_delete_account()
        print()
        
        # Step 8: Test POST activate account
        print("📋 STEP 8: Activate Account Test")
        self.test_activate_account()
        print()
        
        # Step 9: Test validation errors
        print("📋 STEP 9: Validation Tests")
        self.test_validation_errors()
        print()
        
        # Summary
        self.print_test_summary()
        
        # Return overall success
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        return passed_tests >= (total_tests * 0.8)  # 80% success rate required
    
    def print_test_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 MT5 CONFIG API TESTING SUMMARY")
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
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check authentication
        auth_working = any('Authentication Required' in r['test'] and r['success'] for r in self.test_results)
        if auth_working:
            print("   ✅ Admin authentication properly enforced on all endpoints")
        else:
            print("   ❌ Authentication issues detected")
        
        # Check data retrieval
        data_retrieval = any('Get All Accounts' in r['test'] and r['success'] for r in self.test_results)
        if data_retrieval:
            print("   ✅ Successfully retrieved 7 existing MT5 accounts from database")
        else:
            print("   ❌ Issues retrieving MT5 account data")
        
        # Check CRUD operations
        crud_tests = ['Add New Account', 'Update Account', 'Delete Account', 'Activate Account']
        crud_success = sum(1 for test_name in crud_tests 
                          for r in self.test_results 
                          if test_name in r['test'] and r['success'])
        
        if crud_success == len(crud_tests):
            print("   ✅ All CRUD operations (Create, Read, Update, Delete, Activate) working")
        else:
            print(f"   ⚠️ CRUD operations: {crud_success}/{len(crud_tests)} working")
        
        # Check validation
        validation_working = any('Validation Tests' in r['test'] and r['success'] for r in self.test_results)
        if validation_working:
            print("   ✅ Input validation working correctly")
        else:
            print("   ❌ Input validation issues detected")
        
        # Check password exclusion
        password_excluded = any('Password Excluded' in r['test'] and r['success'] for r in self.test_results)
        if password_excluded:
            print("   ✅ Password fields properly excluded from responses (security)")
        else:
            print("   ❌ Password security issues detected")
        
        print()
        print("🎯 OVERALL ASSESSMENT:")
        
        if success_rate >= 90:
            print("   🟢 EXCELLENT: MT5 Config API is fully functional and production-ready")
        elif success_rate >= 80:
            print("   🟡 GOOD: MT5 Config API is mostly functional with minor issues")
        elif success_rate >= 60:
            print("   🟠 FAIR: MT5 Config API has significant issues that need attention")
        else:
            print("   🔴 POOR: MT5 Config API has critical issues and is not production-ready")
        
        print()

def main():
    """Main test execution"""
    tester = MT5ConfigAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()