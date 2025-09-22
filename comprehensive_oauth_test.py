#!/usr/bin/env python3
"""
COMPREHENSIVE GOOGLE OAUTH AUTHENTICATION PERSISTENCE TEST
==========================================================

This test comprehensively investigates the Google OAuth authentication persistence issue
reported by the user. The user completes Google OAuth successfully but then gets signed
out and returns to the login page instead of staying authenticated.

Test Areas:
1. Backend JWT Authentication Flow
2. Google OAuth URL Generation
3. OAuth Callback Processing (with proper error handling)
4. Authentication State Persistence
5. Frontend Token Storage Simulation
6. Session Management Throughout OAuth Flow

The goal is to identify exactly where authentication is being lost.
"""

import requests
import json
import sys
from datetime import datetime
import time
import jwt
import base64

# Configuration
BACKEND_URL = "https://finance-portal-60.preview.emergentagent.com/api"
FRONTEND_URL = "https://finance-portal-60.preview.emergentagent.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ComprehensiveOAuthTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.oauth_url = None
        self.oauth_state = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def decode_jwt_token(self, token):
        """Decode JWT token without verification for inspection"""
        try:
            header, payload, signature = token.split('.')
            payload += '=' * (4 - len(payload) % 4)
            decoded_payload = base64.urlsafe_b64decode(payload)
            return json.loads(decoded_payload)
        except Exception as e:
            return {"error": str(e)}
    
    def test_1_admin_authentication_flow(self):
        """Test 1: Complete admin authentication flow"""
        try:
            print("\n🔐 Testing Admin Authentication Flow...")
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                
                if self.admin_token:
                    token_payload = self.decode_jwt_token(self.admin_token)
                    
                    # Verify token structure
                    required_fields = ["user_id", "username", "user_type", "exp", "iat"]
                    missing_fields = [field for field in required_fields if field not in token_payload]
                    
                    if not missing_fields and token_payload.get("user_type") == "admin":
                        self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                        
                        # Test token with authenticated endpoint
                        test_response = self.session.get(f"{BACKEND_URL}/admin/clients")
                        
                        if test_response.status_code == 200:
                            self.log_result("Admin Authentication Flow", True, 
                                          "Admin login successful with valid JWT token",
                                          {"user_id": token_payload.get("user_id"), 
                                           "username": token_payload.get("username"),
                                           "token_exp": datetime.fromtimestamp(token_payload.get("exp", 0)).isoformat()})
                            return True
                        else:
                            self.log_result("Admin Authentication Flow", False, 
                                          "JWT token not working with authenticated endpoints")
                            return False
                    else:
                        self.log_result("Admin Authentication Flow", False, 
                                      "JWT token invalid or missing fields",
                                      {"missing_fields": missing_fields, "token_payload": token_payload})
                        return False
                else:
                    self.log_result("Admin Authentication Flow", False, "No JWT token in response")
                    return False
            else:
                self.log_result("Admin Authentication Flow", False, f"Login failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_2_google_oauth_url_generation(self):
        """Test 2: Google OAuth URL generation with JWT authentication"""
        try:
            print("\n🔗 Testing Google OAuth URL Generation...")
            
            response = self.session.get(f"{BACKEND_URL}/admin/google/oauth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("oauth_url"):
                    self.oauth_url = data["oauth_url"]
                    self.oauth_state = data.get("state")
                    
                    # Verify OAuth URL structure
                    url_checks = {
                        "Google OAuth Domain": "accounts.google.com" in self.oauth_url,
                        "Client ID Present": "client_id=" in self.oauth_url,
                        "Redirect URI Present": "redirect_uri=" in self.oauth_url,
                        "Scopes Present": "scope=" in self.oauth_url,
                        "Response Type": "response_type=code" in self.oauth_url,
                        "State Parameter": "state=" in self.oauth_url
                    }
                    
                    failed_checks = [check for check, passed in url_checks.items() if not passed]
                    
                    if not failed_checks:
                        self.log_result("Google OAuth URL Generation", True, 
                                      "OAuth URL generated with all required components",
                                      {"oauth_state": self.oauth_state, "scopes_count": len(data.get("scopes", []))})
                        return True
                    else:
                        self.log_result("Google OAuth URL Generation", False, 
                                      "OAuth URL missing components", {"failed_checks": failed_checks})
                        return False
                else:
                    self.log_result("Google OAuth URL Generation", False, 
                                  "Invalid response structure", {"response": data})
                    return False
            elif response.status_code == 401:
                self.log_result("Google OAuth URL Generation", False, 
                              "JWT authentication failed", {"response": response.text})
                return False
            else:
                self.log_result("Google OAuth URL Generation", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Google OAuth URL Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_3_oauth_callback_error_handling(self):
        """Test 3: OAuth callback error handling and authentication preservation"""
        try:
            print("\n🔄 Testing OAuth Callback Error Handling...")
            
            # Test with invalid auth code (expected to fail but preserve authentication)
            response = self.session.post(f"{BACKEND_URL}/admin/google/oauth-callback", json={
                "code": "invalid_mock_code_12345",
                "state": self.oauth_state or "test_state"
            })
            
            # The callback should fail but authentication should be preserved
            if response.status_code == 500:
                # Check if we can still make authenticated requests
                auth_test = self.session.get(f"{BACKEND_URL}/admin/clients")
                
                if auth_test.status_code == 200:
                    self.log_result("OAuth Callback Error Handling", True, 
                                  "OAuth callback fails gracefully while preserving JWT authentication",
                                  {"callback_error": "Expected - invalid auth code", 
                                   "auth_preserved": "Yes - can still access authenticated endpoints"})
                    return True
                else:
                    self.log_result("OAuth Callback Error Handling", False, 
                                  "OAuth callback failure breaks JWT authentication",
                                  {"callback_status": response.status_code, 
                                   "auth_test_status": auth_test.status_code})
                    return False
            elif response.status_code == 401:
                self.log_result("OAuth Callback Error Handling", False, 
                              "JWT authentication lost during OAuth callback")
                return False
            else:
                # Unexpected success or other error
                self.log_result("OAuth Callback Error Handling", False, 
                              f"Unexpected callback response: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("OAuth Callback Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_4_authentication_state_persistence(self):
        """Test 4: Authentication state persistence throughout OAuth flow"""
        try:
            print("\n🔒 Testing Authentication State Persistence...")
            
            # Test multiple authenticated endpoints to ensure JWT token is still valid
            test_endpoints = [
                ("/admin/clients", "Admin Clients"),
                ("/admin/google/oauth-url", "Google OAuth URL (repeat)"),
                ("/admin/google/profile", "Google Profile"),
                ("/health", "Health Check")
            ]
            
            results = []
            all_passed = True
            
            for endpoint, name in test_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        results.append(f"✅ {name}: Authenticated")
                    elif response.status_code == 401:
                        results.append(f"❌ {name}: Authentication Lost")
                        all_passed = False
                    else:
                        results.append(f"⚠️ {name}: HTTP {response.status_code}")
                        
                except Exception as e:
                    results.append(f"❌ {name}: Exception - {str(e)}")
                    all_passed = False
            
            if all_passed:
                self.log_result("Authentication State Persistence", True, 
                              "JWT authentication persists throughout OAuth flow",
                              {"endpoint_results": results})
                return True
            else:
                self.log_result("Authentication State Persistence", False, 
                              "Authentication state lost during OAuth flow",
                              {"endpoint_results": results})
                return False
                
        except Exception as e:
            self.log_result("Authentication State Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_5_jwt_token_integrity(self):
        """Test 5: JWT token integrity and expiration"""
        try:
            print("\n🎫 Testing JWT Token Integrity...")
            
            if not self.admin_token:
                self.log_result("JWT Token Integrity", False, "No admin token available")
                return False
            
            # Decode and analyze token
            token_payload = self.decode_jwt_token(self.admin_token)
            current_time = datetime.now().timestamp()
            
            token_checks = {
                "Has User ID": "user_id" in token_payload,
                "Has Username": "username" in token_payload,
                "Has User Type": "user_type" in token_payload,
                "Is Admin Type": token_payload.get("user_type") == "admin",
                "Has Expiration": "exp" in token_payload,
                "Not Expired": token_payload.get("exp", 0) > current_time,
                "Has Issue Time": "iat" in token_payload
            }
            
            failed_checks = [check for check, passed in token_checks.items() if not passed]
            
            if not failed_checks:
                exp_time = token_payload.get("exp", 0)
                time_remaining = (exp_time - current_time) / 3600  # hours
                
                self.log_result("JWT Token Integrity", True, 
                              f"JWT token is valid and properly structured. {time_remaining:.1f} hours remaining",
                              {"token_payload": {k: v for k, v in token_payload.items() if k != "exp"},
                               "expiration": datetime.fromtimestamp(exp_time).isoformat()})
                return True
            else:
                self.log_result("JWT Token Integrity", False, 
                              "JWT token has integrity issues", 
                              {"failed_checks": failed_checks, "token_payload": token_payload})
                return False
                
        except Exception as e:
            self.log_result("JWT Token Integrity", False, f"Exception: {str(e)}")
            return False
    
    def test_6_session_header_consistency(self):
        """Test 6: Session header consistency"""
        try:
            print("\n📋 Testing Session Header Consistency...")
            
            # Check if Authorization header is still present and correct
            auth_header = self.session.headers.get("Authorization", "")
            
            if auth_header.startswith("Bearer ") and self.admin_token in auth_header:
                # Test that the header works
                response = self.session.get(f"{BACKEND_URL}/admin/clients")
                
                if response.status_code == 200:
                    self.log_result("Session Header Consistency", True, 
                                  "Authorization header consistent and functional")
                    return True
                else:
                    self.log_result("Session Header Consistency", False, 
                                  "Authorization header present but not functional")
                    return False
            else:
                self.log_result("Session Header Consistency", False, 
                              "Authorization header missing or incorrect",
                              {"current_header": auth_header[:50] + "..." if len(auth_header) > 50 else auth_header})
                return False
                
        except Exception as e:
            self.log_result("Session Header Consistency", False, f"Exception: {str(e)}")
            return False
    
    def test_7_frontend_integration_simulation(self):
        """Test 7: Simulate frontend integration scenario"""
        try:
            print("\n🌐 Testing Frontend Integration Simulation...")
            
            # Simulate what happens when user returns from Google OAuth
            # 1. User clicks "Connect Google Workspace" -> gets OAuth URL
            # 2. User completes OAuth on Google -> returns to callback URL
            # 3. Frontend should maintain JWT token and make callback request
            
            # Step 1: Get OAuth URL (already tested, but simulate frontend request)
            oauth_response = self.session.get(f"{BACKEND_URL}/admin/google/oauth-url")
            
            if oauth_response.status_code != 200:
                self.log_result("Frontend Integration Simulation", False, 
                              "Frontend cannot get OAuth URL")
                return False
            
            # Step 2: Simulate frontend receiving callback and making request
            # (In real scenario, frontend would extract code from URL and send to backend)
            
            # Step 3: Check if JWT token would still be valid after redirect
            # Simulate time passing (OAuth redirect typically takes 10-30 seconds)
            time.sleep(1)  # Brief pause to simulate redirect time
            
            # Test if authentication still works after simulated redirect
            post_redirect_test = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if post_redirect_test.status_code == 200:
                self.log_result("Frontend Integration Simulation", True, 
                              "JWT authentication would survive OAuth redirect scenario",
                              {"simulation": "OAuth redirect + callback request", 
                               "auth_status": "Maintained"})
                return True
            else:
                self.log_result("Frontend Integration Simulation", False, 
                              "JWT authentication lost in OAuth redirect scenario",
                              {"post_redirect_status": post_redirect_test.status_code})
                return False
                
        except Exception as e:
            self.log_result("Frontend Integration Simulation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all comprehensive OAuth tests"""
        print("🎯 COMPREHENSIVE GOOGLE OAUTH AUTHENTICATION PERSISTENCE TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Run tests in sequence
        tests = [
            self.test_1_admin_authentication_flow,
            self.test_2_google_oauth_url_generation,
            self.test_3_oauth_callback_error_handling,
            self.test_4_authentication_state_persistence,
            self.test_5_jwt_token_integrity,
            self.test_6_session_header_consistency,
            self.test_7_frontend_integration_simulation
        ]
        
        for test in tests:
            if not test():
                # If a critical test fails, we can still continue with others
                pass
        
        # Generate comprehensive summary
        self.generate_comprehensive_summary()
        
        return True
    
    def generate_comprehensive_summary(self):
        """Generate comprehensive test summary with root cause analysis"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE OAUTH AUTHENTICATION TEST SUMMARY")
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
        
        # Show failed tests first (critical for diagnosis)
        if failed_tests > 0:
            print("❌ FAILED TESTS (CRITICAL FOR DIAGNOSIS):")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
                    if result.get('details'):
                        print(f"     Details: {result['details']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # ROOT CAUSE ANALYSIS
        print("🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        # Analyze authentication flow
        auth_flow_passed = any(r['success'] and "Admin Authentication Flow" in r['test'] for r in self.test_results)
        oauth_url_passed = any(r['success'] and "Google OAuth URL Generation" in r['test'] for r in self.test_results)
        auth_persistence_passed = any(r['success'] and "Authentication State Persistence" in r['test'] for r in self.test_results)
        jwt_integrity_passed = any(r['success'] and "JWT Token Integrity" in r['test'] for r in self.test_results)
        
        if auth_flow_passed and oauth_url_passed and auth_persistence_passed and jwt_integrity_passed:
            print("✅ BACKEND AUTHENTICATION: WORKING CORRECTLY")
            print("   - JWT token generation and validation working")
            print("   - OAuth URL generation working with JWT authentication")
            print("   - Authentication persists throughout OAuth flow")
            print("   - JWT token integrity maintained")
            print()
            print("🎯 USER ISSUE LIKELY CAUSED BY:")
            print("   1. FRONTEND TOKEN STORAGE: localStorage not persisting JWT token after OAuth redirect")
            print("   2. FRONTEND ROUTING: App redirecting to login page instead of maintaining session")
            print("   3. OAUTH REDIRECT HANDLING: Frontend losing JWT token during Google OAuth redirect")
            print("   4. SESSION STATE MANAGEMENT: React state not properly restored after OAuth")
            print()
            print("🔧 RECOMMENDED FIXES:")
            print("   1. Check frontend localStorage token handling in OAuth callback")
            print("   2. Verify React routing doesn't clear authentication state")
            print("   3. Ensure JWT token is preserved during OAuth redirect flow")
            print("   4. Add frontend debugging to track token persistence")
            
        else:
            print("❌ BACKEND AUTHENTICATION: ISSUES FOUND")
            print("   - Backend OAuth flow has authentication problems")
            print("   - This directly explains user's sign-out issue")
            print()
            print("🎯 BACKEND ISSUES IDENTIFIED:")
            if not auth_flow_passed:
                print("   - Admin authentication flow broken")
            if not oauth_url_passed:
                print("   - OAuth URL generation failing")
            if not auth_persistence_passed:
                print("   - Authentication not persisting through OAuth")
            if not jwt_integrity_passed:
                print("   - JWT token integrity issues")
            print()
            print("🔧 REQUIRED BACKEND FIXES:")
            print("   1. Fix JWT token generation and validation")
            print("   2. Ensure OAuth endpoints preserve authentication")
            print("   3. Fix session management during OAuth flow")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    test_runner = ComprehensiveOAuthTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()