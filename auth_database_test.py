#!/usr/bin/env python3
"""
AUTHENTICATION DATABASE VERIFICATION TEST
==========================================

This test focuses on verifying the authentication system works with the database
and checks for any intermittent issues or database problems.
"""

import requests
import json
import sys
import time
from datetime import datetime

class AuthDatabaseTester:
    def __init__(self, base_url="https://fidus-admin.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
        
        if details:
            print(f"   Details: {details}")
        print()

    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            
            try:
                response_data = response.json()
                return response.status_code, response_data
            except:
                return response.status_code, {"error": "Invalid JSON response", "text": response.text}
                
        except Exception as e:
            return 500, {"error": str(e)}

    def test_repeated_admin_login(self):
        """Test admin login multiple times to check for intermittent issues"""
        print("🔍 Testing repeated admin login (checking for intermittent issues)...")
        
        successes = 0
        failures = 0
        
        for i in range(10):
            status_code, response = self.make_request('POST', 'api/auth/login', {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            })
            
            if status_code == 200 and response.get('type') == 'admin':
                successes += 1
                print(f"   Attempt {i+1}: ✅ Success")
            else:
                failures += 1
                print(f"   Attempt {i+1}: ❌ Failed (Status: {status_code})")
            
            time.sleep(0.5)  # Small delay between requests
        
        success = failures == 0
        details = f"Successes: {successes}/10, Failures: {failures}/10"
        
        self.log_test("Repeated Admin Login Test", success, details)
        return success

    def test_repeated_client_login(self):
        """Test client login multiple times to check for intermittent issues"""
        print("🔍 Testing repeated client login (checking for intermittent issues)...")
        
        successes = 0
        failures = 0
        
        for i in range(10):
            status_code, response = self.make_request('POST', 'api/auth/login', {
                "username": "client1",
                "password": "password123",
                "user_type": "client"
            })
            
            if status_code == 200 and response.get('type') == 'client':
                successes += 1
                print(f"   Attempt {i+1}: ✅ Success")
            else:
                failures += 1
                print(f"   Attempt {i+1}: ❌ Failed (Status: {status_code})")
            
            time.sleep(0.5)  # Small delay between requests
        
        success = failures == 0
        details = f"Successes: {successes}/10, Failures: {failures}/10"
        
        self.log_test("Repeated Client Login Test", success, details)
        return success

    def test_concurrent_logins(self):
        """Test concurrent login attempts"""
        print("🔍 Testing concurrent login attempts...")
        
        import threading
        import queue
        
        results = queue.Queue()
        
        def login_test(username, user_type, result_queue):
            status_code, response = self.make_request('POST', 'api/auth/login', {
                "username": username,
                "password": "password123",
                "user_type": user_type
            })
            result_queue.put((username, status_code == 200 and response.get('type') == user_type))
        
        # Start concurrent login threads
        threads = []
        for i in range(5):
            # Alternate between admin and client logins
            if i % 2 == 0:
                thread = threading.Thread(target=login_test, args=("admin", "admin", results))
            else:
                thread = threading.Thread(target=login_test, args=("client1", "client", results))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        successes = 0
        failures = 0
        
        while not results.empty():
            username, success = results.get()
            if success:
                successes += 1
                print(f"   {username}: ✅ Success")
            else:
                failures += 1
                print(f"   {username}: ❌ Failed")
        
        success = failures == 0
        details = f"Concurrent successes: {successes}/5, Failures: {failures}/5"
        
        self.log_test("Concurrent Login Test", success, details)
        return success

    def test_database_user_existence(self):
        """Verify users exist in database by testing login and getting user data"""
        print("🔍 Testing database user existence...")
        
        # Test admin user
        admin_status, admin_response = self.make_request('POST', 'api/auth/login', {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        })
        
        admin_exists = admin_status == 200 and 'id' in admin_response
        
        # Test client user
        client_status, client_response = self.make_request('POST', 'api/auth/login', {
            "username": "client1",
            "password": "password123",
            "user_type": "client"
        })
        
        client_exists = client_status == 200 and 'id' in client_response
        
        success = admin_exists and client_exists
        details = f"Admin exists: {'✅' if admin_exists else '❌'}, Client exists: {'✅' if client_exists else '❌'}"
        
        if admin_exists:
            details += f" | Admin ID: {admin_response.get('id')}"
        if client_exists:
            details += f" | Client ID: {client_response.get('id')}"
        
        self.log_test("Database User Existence", success, details)
        return success

    def test_authentication_response_consistency(self):
        """Test that authentication responses are consistent"""
        print("🔍 Testing authentication response consistency...")
        
        # Get multiple responses for the same user
        responses = []
        
        for i in range(5):
            status_code, response = self.make_request('POST', 'api/auth/login', {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            })
            
            if status_code == 200:
                responses.append(response)
        
        if len(responses) < 2:
            self.log_test("Authentication Response Consistency", False, "Not enough successful responses to compare")
            return False
        
        # Check if all responses are identical
        first_response = responses[0]
        consistent = True
        
        for response in responses[1:]:
            for key in ['id', 'username', 'name', 'email', 'type']:
                if response.get(key) != first_response.get(key):
                    consistent = False
                    break
        
        details = f"Tested {len(responses)} responses, Consistent: {'✅' if consistent else '❌'}"
        
        self.log_test("Authentication Response Consistency", consistent, details)
        return consistent

    def test_password_case_sensitivity(self):
        """Test password case sensitivity"""
        print("🔍 Testing password case sensitivity...")
        
        # Test correct password
        correct_status, _ = self.make_request('POST', 'api/auth/login', {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        })
        
        # Test wrong case password
        wrong_case_status, _ = self.make_request('POST', 'api/auth/login', {
            "username": "admin",
            "password": "Password123",  # Capital P
            "user_type": "admin"
        })
        
        success = correct_status == 200 and wrong_case_status != 200
        details = f"Correct password: {'✅' if correct_status == 200 else '❌'}, Wrong case rejected: {'✅' if wrong_case_status != 200 else '❌'}"
        
        self.log_test("Password Case Sensitivity", success, details)
        return success

    def test_username_case_sensitivity(self):
        """Test username case sensitivity"""
        print("🔍 Testing username case sensitivity...")
        
        # Test correct username
        correct_status, _ = self.make_request('POST', 'api/auth/login', {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        })
        
        # Test wrong case username
        wrong_case_status, _ = self.make_request('POST', 'api/auth/login', {
            "username": "Admin",  # Capital A
            "password": "password123",
            "user_type": "admin"
        })
        
        success = correct_status == 200 and wrong_case_status != 200
        details = f"Correct username: {'✅' if correct_status == 200 else '❌'}, Wrong case rejected: {'✅' if wrong_case_status != 200 else '❌'}"
        
        self.log_test("Username Case Sensitivity", success, details)
        return success

    def test_client_data_access_after_login(self):
        """Test accessing client data after successful login"""
        print("🔍 Testing client data access after login...")
        
        # Login as client
        login_status, login_response = self.make_request('POST', 'api/auth/login', {
            "username": "client1",
            "password": "password123",
            "user_type": "client"
        })
        
        if login_status != 200:
            self.log_test("Client Data Access After Login", False, "Login failed")
            return False
        
        client_id = login_response.get('id')
        if not client_id:
            self.log_test("Client Data Access After Login", False, "No client ID in login response")
            return False
        
        # Try to access client data
        data_status, data_response = self.make_request('GET', f'api/client/{client_id}/data')
        
        success = data_status == 200 and 'balance' in data_response
        details = f"Login: {'✅' if login_status == 200 else '❌'}, Data access: {'✅' if success else '❌'}"
        
        if success:
            balance = data_response.get('balance', {})
            details += f" | Total balance: {balance.get('total_balance', 0)}"
        
        self.log_test("Client Data Access After Login", success, details)
        return success

    def test_admin_data_access_after_login(self):
        """Test accessing admin data after successful login"""
        print("🔍 Testing admin data access after login...")
        
        # Login as admin
        login_status, login_response = self.make_request('POST', 'api/auth/login', {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        })
        
        if login_status != 200:
            self.log_test("Admin Data Access After Login", False, "Login failed")
            return False
        
        # Try to access admin data (portfolio summary)
        data_status, data_response = self.make_request('GET', 'api/admin/portfolio-summary')
        
        success = data_status == 200 and ('aum' in data_response or 'total_aum' in data_response)
        details = f"Login: {'✅' if login_status == 200 else '❌'}, Data access: {'✅' if success else '❌'}"
        
        if success:
            aum = data_response.get('aum') or data_response.get('total_aum', 0)
            details += f" | AUM: ${aum:,.2f}" if isinstance(aum, (int, float)) else f" | AUM: {aum}"
        
        self.log_test("Admin Data Access After Login", success, details)
        return success

    def run_all_tests(self):
        """Run all database authentication tests"""
        print("🔍 STARTING AUTHENTICATION DATABASE VERIFICATION")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Run all tests
        tests = [
            self.test_repeated_admin_login,
            self.test_repeated_client_login,
            self.test_concurrent_logins,
            self.test_database_user_existence,
            self.test_authentication_response_consistency,
            self.test_password_case_sensitivity,
            self.test_username_case_sensitivity,
            self.test_client_data_access_after_login,
            self.test_admin_data_access_after_login
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                results.append(False)
                self.tests_run += 1
        
        # Summary
        print("=" * 70)
        print("🎯 DATABASE AUTHENTICATION TEST SUMMARY")
        print("=" * 70)
        
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print()
        
        all_passed = all(results)
        
        if all_passed:
            print("🎉 VERDICT: AUTHENTICATION DATABASE INTEGRATION IS WORKING PERFECTLY!")
            print("   ✅ No intermittent issues detected")
            print("   ✅ Database users exist and are accessible")
            print("   ✅ Authentication responses are consistent")
            print("   ✅ Data access works after login")
        else:
            print("⚠️  VERDICT: SOME DATABASE AUTHENTICATION ISSUES DETECTED")
            failed_count = len([r for r in results if not r])
            print(f"   ❌ {failed_count} test(s) failed")
            print("   🔧 Review database connectivity and user data")
        
        print("=" * 70)
        return all_passed

if __name__ == "__main__":
    tester = AuthDatabaseTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)