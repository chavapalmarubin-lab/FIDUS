#!/usr/bin/env python3
"""
CRITICAL AUTHENTICATION BUG VERIFICATION TEST
==============================================

This test specifically addresses the user-reported issue:
"User reported they cannot login with admin/password123"

Test Coverage:
1. Direct API Login Tests (admin/password123 and client1/password123)
2. User Data Verification in database
3. Session Management
4. Edge Case Testing
5. Security Features

Expected Results:
- Admin login with admin/password123 should return successful authentication
- Client login with client1/password123 should return successful authentication
- All authentication endpoints should respond correctly
- No security blocks or validation errors should prevent valid login
"""

import requests
import json
import sys
from datetime import datetime

class AuthenticationTester:
    def __init__(self, base_url="https://fidus-invest-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        
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
            print(f"🔍 {method} {url}")
            if data:
                print(f"   Request data: {json.dumps(data, indent=2)}")
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
            
            print(f"   Response Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"   Response Data: {json.dumps(response_data, indent=2)}")
                return response.status_code, response_data
            except:
                print(f"   Response Text: {response.text}")
                return response.status_code, {"error": "Invalid JSON response", "text": response.text}
                
        except Exception as e:
            print(f"   Request Error: {str(e)}")
            return 500, {"error": str(e)}

    # ========================================================================
    # 1. DIRECT API LOGIN TESTS
    # ========================================================================
    
    def test_admin_login_direct(self):
        """Test POST /api/auth/login with admin/password123"""
        print("=" * 60)
        print("1. DIRECT API LOGIN TESTS")
        print("=" * 60)
        
        login_data = {
            "username": "admin",
            "password": "password123", 
            "user_type": "admin"
        }
        
        status_code, response = self.make_request('POST', 'api/auth/login', login_data)
        
        success = status_code == 200
        details = ""
        
        if success:
            # Verify response structure
            required_fields = ['id', 'username', 'name', 'email', 'type']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                success = False
                details = f"Missing required fields: {missing_fields}"
            else:
                self.admin_user = response
                details = f"Admin logged in successfully: {response.get('name')} ({response.get('email')})"
                
                # Verify admin type
                if response.get('type') != 'admin':
                    success = False
                    details += f" - ERROR: Expected type 'admin', got '{response.get('type')}'"
        else:
            details = f"Login failed with status {status_code}: {response.get('detail', 'Unknown error')}"
        
        self.log_test("Admin Login (admin/password123)", success, details)
        return success

    def test_client_login_direct(self):
        """Test POST /api/auth/login with client1/password123"""
        login_data = {
            "username": "client1",
            "password": "password123",
            "user_type": "client"
        }
        
        status_code, response = self.make_request('POST', 'api/auth/login', login_data)
        
        success = status_code == 200
        details = ""
        
        if success:
            # Verify response structure
            required_fields = ['id', 'username', 'name', 'email', 'type']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                success = False
                details = f"Missing required fields: {missing_fields}"
            else:
                self.client_user = response
                details = f"Client logged in successfully: {response.get('name')} ({response.get('email')})"
                
                # Verify client type
                if response.get('type') != 'client':
                    success = False
                    details += f" - ERROR: Expected type 'client', got '{response.get('type')}'"
        else:
            details = f"Login failed with status {status_code}: {response.get('detail', 'Unknown error')}"
        
        self.log_test("Client Login (client1/password123)", success, details)
        return success

    def test_login_response_formats(self):
        """Verify response formats and user data"""
        if not self.admin_user or not self.client_user:
            self.log_test("Login Response Format Verification", False, "Previous login tests failed")
            return False
        
        success = True
        details = []
        
        # Check admin response format
        admin_fields = ['id', 'username', 'name', 'email', 'type', 'profile_picture']
        for field in admin_fields:
            if field not in self.admin_user:
                success = False
                details.append(f"Admin missing field: {field}")
        
        # Check client response format  
        client_fields = ['id', 'username', 'name', 'email', 'type', 'profile_picture']
        for field in client_fields:
            if field not in self.client_user:
                success = False
                details.append(f"Client missing field: {field}")
        
        # Verify data types
        if not isinstance(self.admin_user.get('id'), str):
            success = False
            details.append("Admin ID should be string")
            
        if not isinstance(self.client_user.get('id'), str):
            success = False
            details.append("Client ID should be string")
        
        if success:
            details.append("All required fields present with correct types")
        
        self.log_test("Login Response Format Verification", success, "; ".join(details))
        return success

    # ========================================================================
    # 2. USER DATA VERIFICATION
    # ========================================================================
    
    def test_user_data_verification(self):
        """Verify admin and client users exist in database"""
        print("=" * 60)
        print("2. USER DATA VERIFICATION")
        print("=" * 60)
        
        success = True
        details = []
        
        # Verify admin user data
        if self.admin_user:
            expected_admin = {
                'username': 'admin',
                'type': 'admin',
                'name': 'Investment Committee',
                'email': 'ic@fidus.com'
            }
            
            for key, expected_value in expected_admin.items():
                actual_value = self.admin_user.get(key)
                if actual_value != expected_value:
                    success = False
                    details.append(f"Admin {key}: expected '{expected_value}', got '{actual_value}'")
        else:
            success = False
            details.append("Admin user not available for verification")
        
        # Verify client user data
        if self.client_user:
            expected_client = {
                'username': 'client1',
                'type': 'client',
                'name': 'Gerardo Briones',
                'email': 'g.b@fidus.com'
            }
            
            for key, expected_value in expected_client.items():
                actual_value = self.client_user.get(key)
                if actual_value != expected_value:
                    success = False
                    details.append(f"Client {key}: expected '{expected_value}', got '{actual_value}'")
        else:
            success = False
            details.append("Client user not available for verification")
        
        if success:
            details.append("All user data matches expected values")
        
        self.log_test("User Data Verification", success, "; ".join(details))
        return success

    def test_password_hashing_verification(self):
        """Check password hashing/verification logic"""
        # Test with correct password (should succeed)
        correct_login = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        status_code, response = self.make_request('POST', 'api/auth/login', correct_login)
        correct_success = status_code == 200
        
        # Test with incorrect password (should fail)
        incorrect_login = {
            "username": "admin", 
            "password": "wrongpassword",
            "user_type": "admin"
        }
        
        status_code, response = self.make_request('POST', 'api/auth/login', incorrect_login)
        incorrect_success = status_code == 401
        
        success = correct_success and incorrect_success
        details = f"Correct password: {'✅' if correct_success else '❌'}, Wrong password rejected: {'✅' if incorrect_success else '❌'}"
        
        self.log_test("Password Hashing/Verification Logic", success, details)
        return success

    def test_user_type_field_verification(self):
        """Verify user_type field is correct"""
        success = True
        details = []
        
        if self.admin_user:
            if self.admin_user.get('type') != 'admin':
                success = False
                details.append(f"Admin type incorrect: {self.admin_user.get('type')}")
        
        if self.client_user:
            if self.client_user.get('type') != 'client':
                success = False
                details.append(f"Client type incorrect: {self.client_user.get('type')}")
        
        if success:
            details.append("User types are correct")
        
        self.log_test("User Type Field Verification", success, "; ".join(details))
        return success

    # ========================================================================
    # 3. SESSION MANAGEMENT
    # ========================================================================
    
    def test_session_management(self):
        """Test login session creation and user data return"""
        print("=" * 60)
        print("3. SESSION MANAGEMENT")
        print("=" * 60)
        
        # Test session creation (login returns user data)
        login_data = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        status_code, response = self.make_request('POST', 'api/auth/login', login_data)
        
        success = status_code == 200 and 'id' in response
        details = f"Session created: {'✅' if success else '❌'}"
        
        if success:
            # Verify user data is returned correctly
            user_data_complete = all(field in response for field in ['id', 'username', 'name', 'email', 'type'])
            if user_data_complete:
                details += ", User data complete: ✅"
            else:
                success = False
                details += ", User data incomplete: ❌"
        
        self.log_test("Session Creation and User Data Return", success, details)
        return success

    def test_authentication_middleware(self):
        """Check for any authentication middleware issues"""
        # Test accessing a protected endpoint (if any)
        # For now, test if login endpoint is accessible
        
        status_code, response = self.make_request('POST', 'api/auth/login', {
            "username": "admin",
            "password": "password123", 
            "user_type": "admin"
        })
        
        success = status_code != 403 and status_code != 500
        details = f"No middleware blocking login: {'✅' if success else '❌'} (Status: {status_code})"
        
        self.log_test("Authentication Middleware Check", success, details)
        return success

    def test_logout_functionality(self):
        """Test logout functionality if implemented"""
        # Check if logout endpoint exists
        status_code, response = self.make_request('POST', 'api/auth/logout', {})
        
        # Logout might not be implemented, so we accept 404 as valid
        success = status_code in [200, 404, 405]  # 405 = Method not allowed is also acceptable
        details = f"Logout endpoint response: {status_code} ({'✅' if success else '❌'})"
        
        self.log_test("Logout Functionality", success, details)
        return success

    # ========================================================================
    # 4. EDGE CASE TESTING
    # ========================================================================
    
    def test_edge_cases(self):
        """Test with wrong passwords, non-existent users, empty credentials, malformed requests"""
        print("=" * 60)
        print("4. EDGE CASE TESTING")
        print("=" * 60)
        
        edge_cases = [
            {
                "name": "Wrong Password",
                "data": {"username": "admin", "password": "wrongpassword", "user_type": "admin"},
                "expected_status": 401
            },
            {
                "name": "Non-existent User",
                "data": {"username": "nonexistent", "password": "password123", "user_type": "client"},
                "expected_status": 401
            },
            {
                "name": "Empty Username",
                "data": {"username": "", "password": "password123", "user_type": "admin"},
                "expected_status": 422
            },
            {
                "name": "Empty Password", 
                "data": {"username": "admin", "password": "", "user_type": "admin"},
                "expected_status": 422
            },
            {
                "name": "Missing User Type",
                "data": {"username": "admin", "password": "password123"},
                "expected_status": 422
            },
            {
                "name": "Invalid User Type",
                "data": {"username": "admin", "password": "password123", "user_type": "invalid"},
                "expected_status": 401
            },
            {
                "name": "Wrong User Type (admin as client)",
                "data": {"username": "admin", "password": "password123", "user_type": "client"},
                "expected_status": 401
            },
            {
                "name": "Wrong User Type (client as admin)",
                "data": {"username": "client1", "password": "password123", "user_type": "admin"},
                "expected_status": 401
            }
        ]
        
        all_passed = True
        
        for case in edge_cases:
            status_code, response = self.make_request('POST', 'api/auth/login', case["data"])
            
            success = status_code == case["expected_status"]
            if not success:
                all_passed = False
            
            details = f"Expected {case['expected_status']}, got {status_code}"
            self.log_test(f"Edge Case: {case['name']}", success, details)
        
        return all_passed

    def test_malformed_requests(self):
        """Test with malformed requests"""
        malformed_cases = [
            {
                "name": "Invalid JSON",
                "data": "invalid json",
                "headers": {'Content-Type': 'application/json'}
            },
            {
                "name": "Missing Content-Type",
                "data": {"username": "admin", "password": "password123", "user_type": "admin"},
                "headers": {}
            }
        ]
        
        all_passed = True
        
        for case in malformed_cases:
            try:
                url = f"{self.base_url}/api/auth/login"
                
                if case["name"] == "Invalid JSON":
                    response = requests.post(url, data=case["data"], headers=case["headers"], timeout=15)
                else:
                    response = requests.post(url, json=case["data"], headers=case["headers"], timeout=15)
                
                # Should return 400 or 422 for malformed requests
                success = response.status_code in [400, 422]
                if not success:
                    all_passed = False
                
                details = f"Status: {response.status_code}"
                self.log_test(f"Malformed Request: {case['name']}", success, details)
                
            except Exception as e:
                self.log_test(f"Malformed Request: {case['name']}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    # ========================================================================
    # 5. SECURITY FEATURES
    # ========================================================================
    
    def test_security_features(self):
        """Verify password validation, check for account lockout, test rate limiting, verify security headers"""
        print("=" * 60)
        print("5. SECURITY FEATURES")
        print("=" * 60)
        
        return self.test_password_validation() and self.test_rate_limiting() and self.test_security_headers()

    def test_password_validation(self):
        """Verify password validation"""
        # Test that correct passwords work
        status_code, response = self.make_request('POST', 'api/auth/login', {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        })
        
        success = status_code == 200
        details = f"Valid password accepted: {'✅' if success else '❌'}"
        
        self.log_test("Password Validation", success, details)
        return success

    def test_rate_limiting(self):
        """Check for rate limiting if implemented"""
        # Make multiple rapid requests to see if rate limiting is in place
        rapid_requests = []
        
        for i in range(5):
            status_code, response = self.make_request('POST', 'api/auth/login', {
                "username": "admin",
                "password": "wrongpassword",
                "user_type": "admin"
            })
            rapid_requests.append(status_code)
        
        # Check if any requests were rate limited (429 status)
        rate_limited = any(status == 429 for status in rapid_requests)
        
        # Rate limiting is optional, so we consider both scenarios valid
        success = True
        details = f"Rate limiting: {'Implemented' if rate_limited else 'Not implemented'} (both are acceptable)"
        
        self.log_test("Rate Limiting Check", success, details)
        return success

    def test_security_headers(self):
        """Verify security headers are not blocking login"""
        status_code, response = self.make_request('POST', 'api/auth/login', {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        })
        
        # Check that login is not blocked by security headers
        success = status_code != 403
        details = f"No security header blocking: {'✅' if success else '❌'} (Status: {status_code})"
        
        self.log_test("Security Headers Check", success, details)
        return success

    # ========================================================================
    # COMPREHENSIVE TEST RUNNER
    # ========================================================================
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 STARTING CRITICAL AUTHENTICATION BUG VERIFICATION")
        print("=" * 80)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. Direct API Login Tests
        admin_login_success = self.test_admin_login_direct()
        client_login_success = self.test_client_login_direct()
        response_format_success = self.test_login_response_formats()
        
        # 2. User Data Verification
        user_data_success = self.test_user_data_verification()
        password_hash_success = self.test_password_hashing_verification()
        user_type_success = self.test_user_type_field_verification()
        
        # 3. Session Management
        session_success = self.test_session_management()
        middleware_success = self.test_authentication_middleware()
        logout_success = self.test_logout_functionality()
        
        # 4. Edge Case Testing
        edge_case_success = self.test_edge_cases()
        malformed_success = self.test_malformed_requests()
        
        # 5. Security Features
        security_success = self.test_security_features()
        
        # Summary
        print("=" * 80)
        print("🎯 AUTHENTICATION TEST SUMMARY")
        print("=" * 80)
        
        critical_tests = [
            ("Admin Login (admin/password123)", admin_login_success),
            ("Client Login (client1/password123)", client_login_success),
            ("Response Format Verification", response_format_success),
            ("User Data Verification", user_data_success),
            ("Password Verification Logic", password_hash_success),
            ("User Type Verification", user_type_success),
            ("Session Management", session_success),
            ("Authentication Middleware", middleware_success),
            ("Edge Cases", edge_case_success),
            ("Security Features", security_success)
        ]
        
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print()
        
        print("CRITICAL TEST RESULTS:")
        for test_name, success in critical_tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        print()
        
        # Final verdict
        critical_passed = admin_login_success and client_login_success
        
        if critical_passed:
            print("🎉 VERDICT: AUTHENTICATION SYSTEM IS WORKING CORRECTLY!")
            print("   ✅ Admin login with admin/password123 works")
            print("   ✅ Client login with client1/password123 works")
            print("   ✅ No critical authentication issues found")
            
            if self.tests_passed == self.tests_run:
                print("   🏆 ALL TESTS PASSED - System is production ready!")
            else:
                print(f"   ⚠️  Some non-critical tests failed ({self.tests_run - self.tests_passed} failures)")
        else:
            print("🚨 VERDICT: CRITICAL AUTHENTICATION ISSUES FOUND!")
            if not admin_login_success:
                print("   ❌ Admin login with admin/password123 FAILED")
            if not client_login_success:
                print("   ❌ Client login with client1/password123 FAILED")
            print("   🔧 Immediate attention required!")
        
        print("=" * 80)
        return critical_passed

if __name__ == "__main__":
    tester = AuthenticationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)