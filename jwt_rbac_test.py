#!/usr/bin/env python3
"""
JWT Role-Based Access Control (RBAC) Testing Suite
Tests the JWT authentication middleware and role-based access control implementation.

Focus Areas:
1. Admin Access Control - Admin JWT tokens can access admin endpoints
2. Client Access Control - Client JWT tokens CANNOT access admin endpoints (403 Forbidden)
3. Client Endpoints - Client JWT tokens CAN access client-specific endpoints
4. Role Validation - Verify 403 error messages clearly indicate admin access required
5. Mixed Access - Test endpoints that are protected but not admin-only
"""

import requests
import sys
import json
from datetime import datetime

class JWTRBACTester:
    def __init__(self, base_url="https://invest-manager-9.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.client_token = None
        self.admin_user = None
        self.client_user = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def make_request(self, method, endpoint, token=None, data=None, expected_status=None):
        """Make HTTP request with optional JWT token"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            print(f"   {method} {endpoint} -> {response.status_code}")
            
            if expected_status and response.status_code != expected_status:
                print(f"   Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Response: {error_data}")
                except:
                    print(f"   Response text: {response.text[:200]}")
                return False, {"status_code": response.status_code}
            
            try:
                response_data = response.json()
                response_data["status_code"] = response.status_code
                return True, response_data
            except:
                return True, {"status_code": response.status_code, "text": response.text}
                
        except Exception as e:
            print(f"   Request failed: {str(e)}")
            return False, {"status_code": 0}

    def test_admin_login_jwt(self):
        """Test admin login and JWT token generation"""
        print("\n🔐 Testing Admin Login with JWT Token Generation...")
        
        success, response = self.make_request(
            'POST', 
            'api/auth/login',
            data={
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            },
            expected_status=200
        )
        
        if success and 'token' in response:
            self.admin_token = response['token']
            self.admin_user = response
            self.log_test(
                "Admin Login with JWT", 
                True, 
                f"Token received: {self.admin_token[:20]}... | User: {response.get('name', 'Unknown')}"
            )
            return True
        else:
            self.log_test("Admin Login with JWT", False, "No JWT token in response")
            return False

    def test_client_login_jwt(self):
        """Test client login and JWT token generation"""
        print("\n🔐 Testing Client Login with JWT Token Generation...")
        
        success, response = self.make_request(
            'POST',
            'api/auth/login', 
            data={
                "username": "client1",
                "password": "password123",
                "user_type": "client"
            },
            expected_status=200
        )
        
        if success and 'token' in response:
            self.client_token = response['token']
            self.client_user = response
            self.log_test(
                "Client Login with JWT", 
                True, 
                f"Token received: {self.client_token[:20]}... | User: {response.get('name', 'Unknown')}"
            )
            return True
        else:
            self.log_test("Client Login with JWT", False, "No JWT token in response")
            return False

    def test_admin_access_control(self):
        """Test admin JWT token can access admin endpoints"""
        print("\n🔑 Testing Admin Access Control - Admin Token Should Access Admin Endpoints...")
        
        if not self.admin_token:
            self.log_test("Admin Access Control", False, "No admin token available")
            return False
        
        # Test multiple admin endpoints
        admin_endpoints = [
            'api/admin/portfolio-summary',
            'api/admin/clients', 
            'api/admin/funds-overview',
            'api/investments/admin/overview'
        ]
        
        all_passed = True
        for endpoint in admin_endpoints:
            success, response = self.make_request(
                'GET',
                endpoint,
                token=self.admin_token,
                expected_status=200
            )
            
            if success:
                self.log_test(f"Admin Access: {endpoint}", True, "200 OK - Access granted")
            else:
                self.log_test(f"Admin Access: {endpoint}", False, "Access denied")
                all_passed = False
        
        return all_passed

    def test_client_access_control_forbidden(self):
        """Test client JWT token CANNOT access admin endpoints (should return 403 Forbidden)"""
        print("\n🚫 Testing Client Access Control - Client Token Should Get 403 Forbidden on Admin Endpoints...")
        
        if not self.client_token:
            self.log_test("Client Access Control (403 Test)", False, "No client token available")
            return False
        
        # Test admin endpoints that should return 403 for client tokens
        admin_endpoints = [
            'api/admin/portfolio-summary',
            'api/admin/clients',
            'api/admin/funds-overview', 
            'api/investments/admin/overview'
        ]
        
        all_passed = True
        for endpoint in admin_endpoints:
            success, response = self.make_request(
                'GET',
                endpoint,
                token=self.client_token
            )
            
            # Check if we got 403 Forbidden
            status_code = response.get('status_code', 0)
            if status_code == 403:
                error_msg = response.get('message', response.get('error', 'Forbidden'))
                self.log_test(f"Client 403 Test: {endpoint}", True, f"403 Forbidden - {error_msg}")
            else:
                self.log_test(f"Client 403 Test: {endpoint}", False, f"Expected 403, got {status_code}: {response}")
                all_passed = False
        
        return all_passed

    def test_client_endpoints_access(self):
        """Test client JWT token CAN access client-specific endpoints"""
        print("\n✅ Testing Client Endpoints Access - Client Token Should Access Client Endpoints...")
        
        if not self.client_token or not self.client_user:
            self.log_test("Client Endpoints Access", False, "No client token/user available")
            return False
        
        client_id = self.client_user.get('id')
        if not client_id:
            self.log_test("Client Endpoints Access", False, "No client ID available")
            return False
        
        # Test client-specific endpoints
        client_endpoints = [
            f'api/investments/client/{client_id}',
            f'api/client/{client_id}/data',
            f'api/redemptions/client/{client_id}'
        ]
        
        all_passed = True
        for endpoint in client_endpoints:
            success, response = self.make_request(
                'GET',
                endpoint,
                token=self.client_token,
                expected_status=200
            )
            
            if success:
                self.log_test(f"Client Access: {endpoint}", True, "200 OK - Access granted")
            else:
                self.log_test(f"Client Access: {endpoint}", False, "Access denied")
                all_passed = False
        
        return all_passed

    def test_role_validation_error_messages(self):
        """Test that 403 error messages clearly indicate admin access required and show user type"""
        print("\n📝 Testing Role Validation Error Messages - Should Clearly Indicate Admin Required...")
        
        if not self.client_token:
            self.log_test("Role Validation Messages", False, "No client token available")
            return False
        
        # Test one admin endpoint to check error message quality
        success, response = self.make_request(
            'GET',
            'api/admin/portfolio-summary',
            token=self.client_token
        )
        
        # Look for clear error message indicating admin access required
        error_message = response.get('message', response.get('detail', response.get('error', '')))
        
        # Check if error message is informative
        has_admin_mention = 'admin' in error_message.lower()
        has_forbidden_mention = 'forbidden' in error_message.lower() or '403' in str(response.get('status_code', ''))
        has_user_type = 'client' in error_message.lower() or 'user' in error_message.lower()
        
        if has_admin_mention and has_forbidden_mention:
            self.log_test(
                "Role Validation Error Message", 
                True, 
                f"Clear error message: {error_message}"
            )
            return True
        else:
            self.log_test(
                "Role Validation Error Message", 
                False, 
                f"Unclear error message: {error_message}"
            )
            return False

    def test_mixed_access_endpoints(self):
        """Test endpoints that are protected but not admin-only - both admin and client tokens should work"""
        print("\n🔄 Testing Mixed Access Endpoints - Both Admin and Client Should Access...")
        
        if not self.admin_token or not self.client_token:
            self.log_test("Mixed Access Endpoints", False, "Missing admin or client token")
            return False
        
        # Test investment creation endpoint (protected but not admin-only)
        investment_data = {
            "client_id": self.client_user.get('id') if self.client_user else "client_001",
            "fund_code": "CORE",
            "amount": 15000
        }
        
        # Test with admin token
        admin_success, admin_response = self.make_request(
            'POST',
            'api/investments/create',
            token=self.admin_token,
            data=investment_data
        )
        
        # Test with client token  
        client_success, client_response = self.make_request(
            'POST',
            'api/investments/create',
            token=self.client_token,
            data=investment_data
        )
        
        # Both should succeed (or fail for business logic reasons, not auth)
        admin_auth_ok = admin_success or ('status_code' in admin_response and admin_response['status_code'] != 401 and admin_response['status_code'] != 403)
        client_auth_ok = client_success or ('status_code' in client_response and client_response['status_code'] != 401 and client_response['status_code'] != 403)
        
        if admin_auth_ok and client_auth_ok:
            self.log_test(
                "Mixed Access - Investment Creation", 
                True, 
                "Both admin and client tokens can access (auth passed)"
            )
            return True
        else:
            self.log_test(
                "Mixed Access - Investment Creation", 
                False, 
                f"Auth failed - Admin: {admin_response}, Client: {client_response}"
            )
            return False

    def test_no_token_access(self):
        """Test that protected endpoints require authentication (no token = 401)"""
        print("\n🔒 Testing No Token Access - Should Get 401 Unauthorized...")
        
        # Test admin endpoint without token
        success, response = self.make_request(
            'GET',
            'api/admin/portfolio-summary'
        )
        
        # Should get 401 Unauthorized
        status_code = response.get('status_code', 0)
        if status_code == 401:
            error_msg = response.get('message', response.get('error', 'Unauthorized'))
            self.log_test("No Token Access", True, f"401 Unauthorized - {error_msg}")
            return True
        else:
            self.log_test("No Token Access", False, f"Expected 401, got {status_code}: {response}")
            return False

    def test_invalid_token_access(self):
        """Test that invalid JWT tokens are rejected (401)"""
        print("\n🔓 Testing Invalid Token Access - Should Get 401 Unauthorized...")
        
        # Test with invalid token
        success, response = self.make_request(
            'GET',
            'api/admin/portfolio-summary',
            token='invalid.jwt.token'
        )
        
        # Should get 401 Unauthorized
        status_code = response.get('status_code', 0)
        if status_code == 401:
            error_msg = response.get('message', response.get('error', 'Unauthorized'))
            self.log_test("Invalid Token Access", True, f"401 Unauthorized - {error_msg}")
            return True
        else:
            self.log_test("Invalid Token Access", False, f"Expected 401, got {status_code}: {response}")
            return False

    def run_all_tests(self):
        """Run all JWT RBAC tests"""
        print("=" * 80)
        print("🔐 JWT ROLE-BASED ACCESS CONTROL (RBAC) TESTING SUITE")
        print("=" * 80)
        print("Testing JWT authentication middleware and role-based access control...")
        print(f"Base URL: {self.base_url}")
        print()
        
        # Authentication Tests
        admin_login_ok = self.test_admin_login_jwt()
        client_login_ok = self.test_client_login_jwt()
        
        if not admin_login_ok or not client_login_ok:
            print("\n❌ CRITICAL: Login tests failed. Cannot proceed with RBAC tests.")
            return False
        
        # Core RBAC Tests
        test_results = []
        
        # 1. Admin Access Control
        test_results.append(self.test_admin_access_control())
        
        # 2. Client Access Control (403 Forbidden)
        test_results.append(self.test_client_access_control_forbidden())
        
        # 3. Client Endpoints Access
        test_results.append(self.test_client_endpoints_access())
        
        # 4. Role Validation Error Messages
        test_results.append(self.test_role_validation_error_messages())
        
        # 5. Mixed Access Endpoints
        test_results.append(self.test_mixed_access_endpoints())
        
        # Additional Security Tests
        test_results.append(self.test_no_token_access())
        test_results.append(self.test_invalid_token_access())
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 JWT RBAC TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if all(test_results):
            print("\n✅ ALL JWT RBAC TESTS PASSED!")
            print("🔐 Role-based access control is working correctly:")
            print("   • Admin tokens can access admin endpoints")
            print("   • Client tokens are blocked from admin endpoints (403 Forbidden)")
            print("   • Client tokens can access client endpoints")
            print("   • Error messages are clear and informative")
            print("   • Mixed access endpoints work for both roles")
            print("   • Authentication is properly enforced")
            return True
        else:
            print("\n❌ SOME JWT RBAC TESTS FAILED!")
            print("🚨 Role-based access control issues detected:")
            failed_tests = self.tests_run - self.tests_passed
            print(f"   • {failed_tests} test(s) failed")
            print("   • Review the detailed output above for specific issues")
            return False

def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://invest-manager-9.preview.emergentagent.com"
    
    tester = JWTRBACTester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()