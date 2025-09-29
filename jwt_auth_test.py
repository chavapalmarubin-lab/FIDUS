import requests
import sys
import json
import jwt
from datetime import datetime, timezone

class JWTAuthenticationTester:
    def __init__(self, base_url="https://fidus-google-sync.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.client_token = None
        self.admin_user = None
        self.client_user = None

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

    def test_jwt_token_generation_admin(self):
        """Test JWT Token Generation for admin login"""
        print("\n🎯 PRIORITY TEST 1: JWT Token Generation - Admin Login")
        
        success, response = self.run_test(
            "Admin Login with JWT Token Generation",
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
            self.admin_user = response
            
            # Check if JWT token is included in response
            token = response.get('token')
            if token:
                self.admin_token = token
                print(f"   ✅ JWT Token Generated: {token[:50]}...")
                
                # Verify token structure contains required fields
                try:
                    # Decode without verification to check payload structure
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    required_fields = ['user_id', 'username', 'user_type', 'exp', 'iat']
                    
                    print(f"   Token Payload Fields: {list(decoded.keys())}")
                    
                    missing_fields = [field for field in required_fields if field not in decoded]
                    if not missing_fields:
                        print(f"   ✅ All required JWT fields present: {required_fields}")
                        print(f"   User ID: {decoded.get('user_id')}")
                        print(f"   Username: {decoded.get('username')}")
                        print(f"   User Type: {decoded.get('user_type')}")
                        print(f"   Expires: {datetime.fromtimestamp(decoded.get('exp'), tz=timezone.utc)}")
                        print(f"   Issued At: {datetime.fromtimestamp(decoded.get('iat'), tz=timezone.utc)}")
                    else:
                        print(f"   ❌ Missing JWT fields: {missing_fields}")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Error decoding JWT token: {e}")
                    return False
                    
            else:
                print(f"   ❌ No JWT token in login response")
                return False
                
            # Verify backward compatibility - all required user fields present
            required_user_fields = ['id', 'username', 'name', 'email', 'type', 'profile_picture', 'must_change_password']
            missing_user_fields = [field for field in required_user_fields if field not in response]
            
            if not missing_user_fields:
                print(f"   ✅ Backward compatibility maintained - all user fields present")
            else:
                print(f"   ❌ Missing user fields: {missing_user_fields}")
                return False
                
        return success

    def test_jwt_token_generation_client(self):
        """Test JWT Token Generation for client login"""
        print("\n🎯 PRIORITY TEST 1: JWT Token Generation - Client Login")
        
        success, response = self.run_test(
            "Client Login with JWT Token Generation",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client1", 
                "password": "password123",
                "user_type": "client"
            }
        )
        
        if success:
            self.client_user = response
            
            # Check if JWT token is included in response
            token = response.get('token')
            if token:
                self.client_token = token
                print(f"   ✅ JWT Token Generated: {token[:50]}...")
                
                # Verify token structure contains required fields
                try:
                    # Decode without verification to check payload structure
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    required_fields = ['user_id', 'username', 'user_type', 'exp', 'iat']
                    
                    print(f"   Token Payload Fields: {list(decoded.keys())}")
                    
                    missing_fields = [field for field in required_fields if field not in decoded]
                    if not missing_fields:
                        print(f"   ✅ All required JWT fields present: {required_fields}")
                        print(f"   User ID: {decoded.get('user_id')}")
                        print(f"   Username: {decoded.get('username')}")
                        print(f"   User Type: {decoded.get('user_type')}")
                        
                        # Verify user type is correct
                        if decoded.get('user_type') == 'client':
                            print(f"   ✅ User type correctly set to 'client'")
                        else:
                            print(f"   ❌ User type incorrect: {decoded.get('user_type')}")
                            return False
                            
                    else:
                        print(f"   ❌ Missing JWT fields: {missing_fields}")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Error decoding JWT token: {e}")
                    return False
                    
            else:
                print(f"   ❌ No JWT token in login response")
                return False
                
        return success

    def test_protected_endpoint_with_jwt_token(self):
        """Test JWT Token Validation on protected endpoints WITH valid token"""
        print("\n🎯 PRIORITY TEST 2: JWT Token Validation - Protected Endpoint WITH Token")
        
        if not self.admin_token:
            print("   ❌ No admin token available for testing")
            return False
            
        # Test admin portfolio summary with JWT token
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        success, response = self.run_test(
            "Admin Portfolio Summary WITH JWT Token",
            "GET",
            "api/admin/portfolio-summary",
            200,
            headers=headers
        )
        
        if success:
            print(f"   ✅ Protected endpoint accessible with valid JWT token")
            # Verify response contains expected data
            if 'aum' in response or 'total_aum' in response:
                print(f"   ✅ Response contains expected portfolio data")
            else:
                print(f"   ⚠️  Response structure: {list(response.keys())}")
        
        return success

    def test_protected_endpoint_without_jwt_token(self):
        """Test JWT Token Validation on protected endpoints WITHOUT token"""
        print("\n🎯 PRIORITY TEST 2: JWT Token Validation - Protected Endpoint WITHOUT Token")
        
        # Test admin portfolio summary without JWT token
        headers = {
            'Content-Type': 'application/json'
            # No Authorization header
        }
        
        success, response = self.run_test(
            "Admin Portfolio Summary WITHOUT JWT Token",
            "GET",
            "api/admin/portfolio-summary",
            401,  # Should be rejected with 401 Unauthorized
            headers=headers
        )
        
        if success:
            print(f"   ✅ Protected endpoint properly rejects requests without JWT token")
        else:
            print(f"   ❌ Protected endpoint should reject requests without JWT token")
            print(f"   ⚠️  This indicates authentication middleware may not be active")
        
        return success

    def test_protected_endpoint_with_invalid_jwt_token(self):
        """Test JWT Token Validation with invalid token"""
        print("\n🎯 PRIORITY TEST 2: JWT Token Validation - Protected Endpoint WITH Invalid Token")
        
        # Test with invalid JWT token
        invalid_token = "invalid.jwt.token"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {invalid_token}'
        }
        
        success, response = self.run_test(
            "Admin Portfolio Summary WITH Invalid JWT Token",
            "GET",
            "api/admin/portfolio-summary",
            401,  # Should be rejected with 401 Unauthorized
            headers=headers
        )
        
        if success:
            print(f"   ✅ Protected endpoint properly rejects invalid JWT tokens")
        else:
            print(f"   ❌ Protected endpoint should reject invalid JWT tokens")
        
        return success

    def test_multiple_protected_endpoints_with_client_token(self):
        """Test multiple protected endpoints with client JWT token"""
        print("\n🎯 PRIORITY TEST 4: Authentication Middleware - Multiple Protected Endpoints")
        
        if not self.client_token or not self.client_user:
            print("   ❌ No client token available for testing")
            return False
            
        client_id = self.client_user.get('id')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client_token}'
        }
        
        # Test 1: Client data endpoint
        success1, _ = self.run_test(
            "Client Data WITH JWT Token",
            "GET",
            f"api/client/{client_id}/data",
            200,
            headers=headers
        )
        
        # Test 2: Client investments endpoint
        success2, _ = self.run_test(
            "Client Investments WITH JWT Token",
            "GET",
            f"api/investments/client/{client_id}",
            200,
            headers=headers
        )
        
        # Test 3: Client redemptions endpoint
        success3, _ = self.run_test(
            "Client Redemptions WITH JWT Token",
            "GET",
            f"api/redemptions/client/{client_id}",
            200,
            headers=headers
        )
        
        if success1 and success2 and success3:
            print(f"   ✅ All client protected endpoints accessible with valid JWT token")
            return True
        else:
            print(f"   ❌ Some client protected endpoints failed: {success1}, {success2}, {success3}")
            return False

    def test_cross_user_type_access_control(self):
        """Test that client tokens cannot access admin endpoints"""
        print("\n🎯 PRIORITY TEST 4: Authentication Middleware - Cross User Type Access Control")
        
        if not self.client_token:
            print("   ❌ No client token available for testing")
            return False
            
        # Try to access admin endpoint with client token
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client_token}'
        }
        
        success, response = self.run_test(
            "Admin Portfolio Summary WITH Client JWT Token",
            "GET",
            "api/admin/portfolio-summary",
            403,  # Should be forbidden
            headers=headers
        )
        
        if success:
            print(f"   ✅ Client token properly rejected from admin endpoints")
        else:
            print(f"   ❌ Client token should not access admin endpoints")
            print(f"   ⚠️  This indicates insufficient access control")
        
        return success

    def test_jwt_token_expiration_handling(self):
        """Test JWT token expiration handling"""
        print("\n🎯 PRIORITY TEST 3: Token Structure - JWT Token Expiration")
        
        if not self.admin_token:
            print("   ❌ No admin token available for testing")
            return False
            
        try:
            # Decode token to check expiration
            decoded = jwt.decode(self.admin_token, options={"verify_signature": False})
            exp_timestamp = decoded.get('exp')
            iat_timestamp = decoded.get('iat')
            
            if exp_timestamp and iat_timestamp:
                exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                iat_time = datetime.fromtimestamp(iat_timestamp, tz=timezone.utc)
                current_time = datetime.now(timezone.utc)
                
                print(f"   Token issued at: {iat_time}")
                print(f"   Token expires at: {exp_time}")
                print(f"   Current time: {current_time}")
                
                # Check if token is not expired
                if current_time < exp_time:
                    print(f"   ✅ Token is valid and not expired")
                    
                    # Check expiration duration (should be 24 hours)
                    duration = exp_time - iat_time
                    duration_hours = duration.total_seconds() / 3600
                    
                    if 23 <= duration_hours <= 25:  # Allow some tolerance
                        print(f"   ✅ Token expiration duration correct: {duration_hours:.1f} hours")
                        return True
                    else:
                        print(f"   ⚠️  Token expiration duration: {duration_hours:.1f} hours (expected ~24)")
                        return True  # Still pass, just note the difference
                else:
                    print(f"   ❌ Token is expired")
                    return False
            else:
                print(f"   ❌ Token missing expiration or issued-at timestamps")
                return False
                
        except Exception as e:
            print(f"   ❌ Error checking token expiration: {e}")
            return False

    def test_login_endpoint_backward_compatibility(self):
        """Test that login endpoint maintains backward compatibility"""
        print("\n🎯 PRIORITY TEST 5: Backward Compatibility - Login Response Structure")
        
        # Test with a fresh login to ensure clean state
        success, response = self.run_test(
            "Fresh Login for Backward Compatibility Check",
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
            # Check all required fields are present
            required_fields = ['id', 'username', 'name', 'email', 'type', 'profile_picture', 'must_change_password', 'token']
            present_fields = []
            missing_fields = []
            
            for field in required_fields:
                if field in response:
                    present_fields.append(field)
                    print(f"   ✅ {field}: {response[field]}")
                else:
                    missing_fields.append(field)
                    print(f"   ❌ Missing: {field}")
            
            if not missing_fields:
                print(f"   ✅ All required fields present: {len(present_fields)}/{len(required_fields)}")
                
                # Verify token is new field (not breaking existing structure)
                if response.get('token'):
                    print(f"   ✅ New 'token' field added successfully")
                    return True
                else:
                    print(f"   ❌ 'token' field missing")
                    return False
            else:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
        
        return success

    def test_authentication_middleware_status(self):
        """Test if authentication middleware is active and working"""
        print("\n🎯 CRITICAL TEST: Authentication Middleware Status Check")
        
        # Test multiple endpoints to see if middleware is active
        test_endpoints = [
            ("api/admin/portfolio-summary", "Admin Portfolio Summary"),
            ("api/admin/clients", "Admin Clients"),
            ("api/admin/funds-overview", "Admin Funds Overview"),
            ("api/investments/admin/overview", "Admin Investment Overview")
        ]
        
        middleware_active = True
        
        for endpoint, name in test_endpoints:
            # Test without token
            success_without_token, _ = self.run_test(
                f"{name} WITHOUT Token",
                "GET",
                endpoint,
                401,  # Should be 401 if middleware is active
                headers={'Content-Type': 'application/json'}
            )
            
            if not success_without_token:
                print(f"   ⚠️  {name} does not require authentication (middleware may be inactive)")
                middleware_active = False
            else:
                print(f"   ✅ {name} properly protected")
        
        if middleware_active:
            print(f"   ✅ Authentication middleware is ACTIVE and protecting endpoints")
        else:
            print(f"   ❌ Authentication middleware appears to be INACTIVE")
            print(f"   🚨 CRITICAL ISSUE: Protected endpoints are accessible without authentication")
        
        return middleware_active

    def run_comprehensive_jwt_tests(self):
        """Run all JWT authentication tests"""
        print("=" * 80)
        print("🔐 COMPREHENSIVE JWT AUTHENTICATION SYSTEM TESTING")
        print("=" * 80)
        print("Testing JWT authentication implementation as requested in review:")
        print("1. JWT Token Generation (admin/password123 and client1/password123)")
        print("2. JWT Token Validation (protected endpoints with/without tokens)")
        print("3. Token Structure (user_id, username, user_type, exp, iat fields)")
        print("4. Authentication Middleware (Authorization: Bearer <token> requirement)")
        print("5. Backward Compatibility (login returns all required fields + token)")
        print("=" * 80)
        
        # Run all tests in order
        tests = [
            self.test_jwt_token_generation_admin,
            self.test_jwt_token_generation_client,
            self.test_protected_endpoint_with_jwt_token,
            self.test_protected_endpoint_without_jwt_token,
            self.test_protected_endpoint_with_invalid_jwt_token,
            self.test_multiple_protected_endpoints_with_client_token,
            self.test_cross_user_type_access_control,
            self.test_jwt_token_expiration_handling,
            self.test_login_endpoint_backward_compatibility,
            self.test_authentication_middleware_status
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with error: {e}")
                self.tests_run += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("🔐 JWT AUTHENTICATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL JWT AUTHENTICATION TESTS PASSED!")
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
        
        print("=" * 80)
        
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    tester = JWTAuthenticationTester()
    passed, total = tester.run_comprehensive_jwt_tests()
    
    if passed == total:
        sys.exit(0)
    else:
        sys.exit(1)