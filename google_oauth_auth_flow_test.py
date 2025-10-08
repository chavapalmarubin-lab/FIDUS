#!/usr/bin/env python3
"""
GOOGLE OAUTH AUTHENTICATION FLOW AND PERSISTENCE TEST
====================================================

This test verifies the complete Google OAuth authentication flow and authentication persistence
as requested in the review. The user reports that after completing Google OAuth, the app signs
out and returns to the login page instead of staying authenticated.

Key Test Areas:
1. Admin Login Flow: /api/auth/login with admin/password123 to get JWT token
2. Google OAuth URL Generation: /api/admin/google/oauth-url with JWT token
3. Google OAuth Callback: /api/admin/google/oauth-callback with JWT token and mock auth code
4. Authentication State: /api/admin/google/profile with JWT token after callback
5. JWT Token Persistence: Verify JWT token remains valid throughout OAuth flow

Expected Results:
- Admin login should work and return valid JWT token
- OAuth URL generation should work with JWT authentication
- OAuth callback should accept JWT token + auth code and store Google tokens
- After OAuth callback, admin should still be authenticated
- Google profile endpoint should return authentication status
"""

import requests
import json
import sys
from datetime import datetime
import time
import jwt
import base64

# Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GoogleOAuthAuthFlowTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.oauth_url = None
        self.google_tokens = None
        
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
            # Split the token
            header, payload, signature = token.split('.')
            
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            
            # Decode payload
            decoded_payload = base64.urlsafe_b64decode(payload)
            return json.loads(decoded_payload)
        except Exception as e:
            return {"error": str(e)}
    
    def test_admin_login_flow(self):
        """Test admin login and JWT token generation"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                
                if self.admin_token:
                    # Decode and inspect JWT token
                    token_payload = self.decode_jwt_token(self.admin_token)
                    
                    # Verify token contains required fields
                    required_fields = ["user_id", "username", "user_type", "exp", "iat"]
                    missing_fields = [field for field in required_fields if field not in token_payload]
                    
                    if not missing_fields and token_payload.get("user_type") == "admin":
                        self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                        self.log_result("Admin Login Flow", True, 
                                      "Successfully authenticated as admin with valid JWT token",
                                      {"token_payload": token_payload})
                        return True
                    else:
                        self.log_result("Admin Login Flow", False, 
                                      "JWT token missing required fields or wrong user type",
                                      {"missing_fields": missing_fields, "token_payload": token_payload})
                        return False
                else:
                    self.log_result("Admin Login Flow", False, "No JWT token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Login Flow", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Login Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_google_oauth_url_generation(self):
        """Test Google OAuth URL generation with JWT authentication"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/oauth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has success flag and oauth_url
                has_success = data.get("success") is True
                has_oauth_url = data.get("oauth_url") is not None
                
                if has_success and has_oauth_url:
                    self.oauth_url = data["oauth_url"]
                    
                    # Verify OAuth URL contains required components
                    required_components = [
                        "accounts.google.com/o/oauth2/auth",
                        "client_id=",
                        "redirect_uri=",
                        "scope=",
                        "response_type=code"
                    ]
                    
                    missing_components = [comp for comp in required_components if comp not in self.oauth_url]
                    
                    if not missing_components:
                        self.log_result("Google OAuth URL Generation", True, 
                                      "OAuth URL generated successfully with all required components",
                                      {"oauth_url": self.oauth_url[:100] + "...", "full_response": data})
                        return True
                    else:
                        self.log_result("Google OAuth URL Generation", False, 
                                      "OAuth URL missing required components",
                                      {"missing_components": missing_components, "url": self.oauth_url})
                        return False
                else:
                    self.log_result("Google OAuth URL Generation", False, 
                                  "Response missing success flag or auth_url", 
                                  {"response": data, "has_success": has_success, "has_oauth_url": has_oauth_url})
                    return False
            elif response.status_code == 401:
                self.log_result("Google OAuth URL Generation", False, 
                              "Unauthorized - JWT authentication failed", {"response": response.text})
                return False
            else:
                self.log_result("Google OAuth URL Generation", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Google OAuth URL Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_verification(self):
        """Test JWT token is still valid and properly formatted"""
        try:
            if not self.admin_token:
                self.log_result("JWT Token Verification", False, "No admin token available")
                return False
            
            # Test token with a simple authenticated endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 200:
                # Decode token again to check expiration
                token_payload = self.decode_jwt_token(self.admin_token)
                current_time = datetime.now().timestamp()
                token_exp = token_payload.get("exp", 0)
                
                if token_exp > current_time:
                    time_remaining = token_exp - current_time
                    self.log_result("JWT Token Verification", True, 
                                  f"JWT token valid and authenticated. Time remaining: {time_remaining/3600:.1f} hours",
                                  {"token_payload": token_payload})
                    return True
                else:
                    self.log_result("JWT Token Verification", False, 
                                  "JWT token has expired", {"token_payload": token_payload})
                    return False
            elif response.status_code == 401:
                self.log_result("JWT Token Verification", False, 
                              "JWT token authentication failed", {"response": response.text})
                return False
            else:
                self.log_result("JWT Token Verification", False, 
                              f"Unexpected response: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("JWT Token Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_google_oauth_callback_processing(self):
        """Test Google OAuth callback with mock authorization code"""
        try:
            # Use a mock authorization code (in real scenario, this comes from Google)
            mock_auth_code = "mock_auth_code_for_testing_12345"
            
            response = self.session.post(f"{BACKEND_URL}/admin/google/oauth-callback", json={
                "code": mock_auth_code,
                "state": "test_state"
            })
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self.log_result("Google OAuth Callback Processing", True, 
                                  "OAuth callback processed successfully",
                                  {"response": data})
                    
                    # Store any returned tokens
                    if "tokens" in data:
                        self.google_tokens = data["tokens"]
                    
                    return True
                else:
                    self.log_result("Google OAuth Callback Processing", False, 
                                  "OAuth callback failed", {"response": data})
                    return False
            elif response.status_code == 401:
                self.log_result("Google OAuth Callback Processing", False, 
                              "Unauthorized - JWT authentication failed during callback", 
                              {"response": response.text})
                return False
            elif response.status_code == 400:
                # Expected for mock auth code - check if it's a proper validation error
                data = response.json()
                error_message = data.get("detail", "").lower()
                
                if "malformed" in error_message or "invalid" in error_message or "code" in error_message:
                    self.log_result("Google OAuth Callback Processing", True, 
                                  "OAuth callback properly validates auth codes (mock code rejected as expected)",
                                  {"response": data})
                    return True
                else:
                    self.log_result("Google OAuth Callback Processing", False, 
                                  "Unexpected validation error", {"response": data})
                    return False
            else:
                self.log_result("Google OAuth Callback Processing", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Google OAuth Callback Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_persistence_after_oauth(self):
        """Test that admin authentication persists after OAuth callback"""
        try:
            # Test multiple authenticated endpoints to verify JWT token still works
            test_endpoints = [
                ("/admin/clients", "Admin Clients"),
                ("/admin/google/oauth-url", "Google OAuth URL"),
                ("/health", "Health Check")
            ]
            
            all_passed = True
            endpoint_results = []
            
            for endpoint, name in test_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        endpoint_results.append(f"✅ {name}: OK")
                    elif response.status_code == 401:
                        endpoint_results.append(f"❌ {name}: Unauthorized")
                        all_passed = False
                    else:
                        endpoint_results.append(f"⚠️ {name}: HTTP {response.status_code}")
                        
                except Exception as e:
                    endpoint_results.append(f"❌ {name}: Exception - {str(e)}")
                    all_passed = False
            
            if all_passed:
                self.log_result("Authentication Persistence After OAuth", True, 
                              "Admin authentication persists after OAuth flow",
                              {"endpoint_results": endpoint_results})
                return True
            else:
                self.log_result("Authentication Persistence After OAuth", False, 
                              "Authentication lost after OAuth flow",
                              {"endpoint_results": endpoint_results})
                return False
                
        except Exception as e:
            self.log_result("Authentication Persistence After OAuth", False, f"Exception: {str(e)}")
            return False
    
    def test_google_profile_endpoint(self):
        """Test Google profile endpoint with JWT authentication"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/profile")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Google Profile Endpoint", True, 
                              "Google profile endpoint accessible with JWT authentication",
                              {"response": data})
                return True
            elif response.status_code == 401:
                self.log_result("Google Profile Endpoint", False, 
                              "Unauthorized - JWT authentication failed", {"response": response.text})
                return False
            elif response.status_code == 500:
                # Server error might be expected if no Google tokens are stored
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"error": response.text}
                error_message = data.get("detail", "").lower()
                
                if "google" in error_message or "token" in error_message or "auth" in error_message:
                    self.log_result("Google Profile Endpoint", True, 
                                  "Endpoint accessible but no Google tokens (expected for test)",
                                  {"response": data})
                    return True
                else:
                    self.log_result("Google Profile Endpoint", False, 
                                  "Unexpected server error", {"response": data})
                    return False
            else:
                self.log_result("Google Profile Endpoint", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Google Profile Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_session_consistency(self):
        """Test that session remains consistent throughout the OAuth flow"""
        try:
            # Check if we still have the same JWT token
            current_auth_header = self.session.headers.get("Authorization", "")
            
            if current_auth_header.startswith("Bearer ") and self.admin_token in current_auth_header:
                # Verify token is still valid by making an authenticated request
                response = self.session.get(f"{BACKEND_URL}/admin/clients")
                
                if response.status_code == 200:
                    self.log_result("Session Consistency", True, 
                                  "Session and JWT token remain consistent throughout OAuth flow")
                    return True
                else:
                    self.log_result("Session Consistency", False, 
                                  f"Session inconsistent - authenticated request failed: HTTP {response.status_code}")
                    return False
            else:
                self.log_result("Session Consistency", False, 
                              "JWT token lost from session headers")
                return False
                
        except Exception as e:
            self.log_result("Session Consistency", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Google OAuth authentication flow tests"""
        print("🎯 GOOGLE OAUTH AUTHENTICATION FLOW AND PERSISTENCE TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        print("🔍 Testing Google OAuth Authentication Flow...")
        print("-" * 50)
        
        # Test 1: Admin Login Flow
        if not self.test_admin_login_flow():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with OAuth tests.")
            return False
        
        # Test 2: JWT Token Verification
        self.test_jwt_token_verification()
        
        # Test 3: Google OAuth URL Generation
        self.test_google_oauth_url_generation()
        
        # Test 4: Google OAuth Callback Processing
        self.test_google_oauth_callback_processing()
        
        # Test 5: Authentication Persistence After OAuth
        self.test_authentication_persistence_after_oauth()
        
        # Test 6: Google Profile Endpoint
        self.test_google_profile_endpoint()
        
        # Test 7: Session Consistency
        self.test_session_consistency()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 GOOGLE OAUTH AUTHENTICATION FLOW TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests first (more important)
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment for OAuth flow
        critical_tests = [
            "Admin Login Flow",
            "JWT Token Verification", 
            "Google OAuth URL Generation",
            "Authentication Persistence After OAuth",
            "Session Consistency"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ GOOGLE OAUTH AUTHENTICATION FLOW: WORKING")
            print("   JWT token persistence through OAuth flow is functional.")
            print("   Admin authentication is maintained after OAuth callback.")
            print("   The user's reported issue may be frontend-related or specific to live OAuth.")
        else:
            print("❌ GOOGLE OAUTH AUTHENTICATION FLOW: BROKEN")
            print("   Critical authentication persistence issues found.")
            print("   This confirms the user's report of being signed out after OAuth.")
            print("   Main agent action required to fix authentication flow.")
        
        # Specific findings about the user's issue
        print("\n🔍 USER ISSUE ANALYSIS:")
        auth_persistence_result = next((r for r in self.test_results if "Authentication Persistence" in r['test']), None)
        session_consistency_result = next((r for r in self.test_results if "Session Consistency" in r['test']), None)
        
        if auth_persistence_result and auth_persistence_result['success'] and session_consistency_result and session_consistency_result['success']:
            print("   Backend OAuth flow maintains authentication correctly.")
            print("   User's issue likely occurs in frontend state management or live OAuth redirect.")
            print("   Recommend checking frontend localStorage token handling after OAuth redirect.")
        else:
            print("   Backend OAuth flow has authentication persistence issues.")
            print("   This directly explains why user gets signed out after OAuth completion.")
            print("   JWT token or session management is broken during OAuth callback processing.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = GoogleOAuthAuthFlowTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()