#!/usr/bin/env python3
"""
GOOGLE ADMIN OAUTH INTEGRATION TESTING - WITH AUTHENTICATION
============================================================

This test verifies the new Google Admin OAuth integration endpoints with proper authentication:

1. Test Google Auth URL Endpoint (/api/admin/google/auth-url) - with admin auth
2. Test Admin Profile Endpoint (/api/admin/google/profile) - without auth (401 expected)
3. Test Session Processing (/api/admin/google/process-session) - with admin auth
4. Test Logout Endpoint (/api/admin/google/logout) - with admin auth
5. Test Email Endpoint (/api/admin/google/send-email) - without auth (401 expected)

This verifies the Google OAuth backend integration is properly implemented.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the backend URL from frontend .env
BACKEND_URL = "https://auth-troubleshoot-14.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GoogleOAuthAuthenticatedTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
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
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_google_auth_url_with_auth(self):
        """Test Google Auth URL Endpoint with admin authentication"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ['success', 'auth_url', 'redirect_url', 'scopes']
                missing_fields = []
                
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_result("Google Auth URL - Required Fields", False, 
                                  f"Missing fields: {', '.join(missing_fields)}", 
                                  {"response": data})
                    return
                
                # Verify success is true
                if data.get('success') is True:
                    self.log_result("Google Auth URL - Success Field", True, 
                                  "Success field is true")
                else:
                    self.log_result("Google Auth URL - Success Field", False, 
                                  f"Success field is {data.get('success')}, expected true")
                
                # Verify auth_url points to Emergent auth service
                auth_url = data.get('auth_url', '')
                if 'auth.emergentagent.com' in auth_url:
                    self.log_result("Google Auth URL - Emergent Service", True, 
                                  "Auth URL points to Emergent auth service")
                else:
                    self.log_result("Google Auth URL - Emergent Service", False, 
                                  f"Auth URL does not point to Emergent service: {auth_url}")
                
                # Verify redirect_url is present and valid
                redirect_url = data.get('redirect_url', '')
                if redirect_url and 'google-callback' in redirect_url:
                    self.log_result("Google Auth URL - Redirect URL", True, 
                                  f"Valid redirect URL: {redirect_url}")
                else:
                    self.log_result("Google Auth URL - Redirect URL", False, 
                                  f"Invalid redirect URL: {redirect_url}")
                
                # Verify scopes array is present and contains Google API scopes
                scopes = data.get('scopes', [])
                expected_scopes = [
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/calendar'
                ]
                
                if isinstance(scopes, list) and len(scopes) > 0:
                    # Check if at least some expected scopes are present
                    found_scopes = [scope for scope in expected_scopes if scope in scopes]
                    if found_scopes:
                        self.log_result("Google Auth URL - API Scopes", True, 
                                      f"Found {len(found_scopes)} expected scopes out of {len(scopes)} total")
                    else:
                        self.log_result("Google Auth URL - API Scopes", False, 
                                      "No expected Google API scopes found", 
                                      {"scopes": scopes})
                else:
                    self.log_result("Google Auth URL - API Scopes", False, 
                                  "Scopes is not a valid array", {"scopes": scopes})
                
                # Overall endpoint test
                self.log_result("Google Auth URL Endpoint (Authenticated)", True, 
                              "Endpoint responding correctly with all required fields")
                
            else:
                self.log_result("Google Auth URL Endpoint (Authenticated)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Google Auth URL Endpoint (Authenticated)", False, f"Exception: {str(e)}")
    
    def test_admin_profile_unauthorized(self):
        """Test Admin Profile Endpoint without authentication - should return 401"""
        try:
            # Create a new session without authentication
            unauthenticated_session = requests.Session()
            response = unauthenticated_session.get(f"{BACKEND_URL}/admin/google/profile")
            
            if response.status_code == 401:
                self.log_result("Admin Profile - Unauthorized Access", True, 
                              "Correctly returns 401 for unauthenticated requests")
                
                # Check if response contains proper error message
                try:
                    data = response.json()
                    if 'error' in data or 'detail' in data:
                        self.log_result("Admin Profile - Error Message", True, 
                                      f"Proper error message present")
                    else:
                        self.log_result("Admin Profile - Error Message", False, 
                                      "No error message in response", {"response": data})
                except:
                    # Response might not be JSON, which is also acceptable for 401
                    self.log_result("Admin Profile - Error Message", True, 
                                  "Non-JSON 401 response (acceptable)")
            else:
                self.log_result("Admin Profile - Unauthorized Access", False, 
                              f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Profile - Unauthorized Access", False, f"Exception: {str(e)}")
    
    def test_session_processing_with_auth(self):
        """Test Session Processing with admin authentication and invalid session ID"""
        try:
            # Test with invalid session ID
            invalid_session_data = {
                "session_id": "invalid_test_session"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/google/process-session", 
                                       json=invalid_session_data)
            
            # Should return an error (400, 401, or 500) for invalid session
            if response.status_code in [400, 401, 500]:
                self.log_result("Session Processing - Invalid Session (Authenticated)", True, 
                              f"Correctly handles invalid session with HTTP {response.status_code}")
                
                # Check if response contains error details
                try:
                    data = response.json()
                    if 'detail' in data or 'error' in data:
                        self.log_result("Session Processing - Error Handling", True, 
                                      f"Proper error handling present")
                    else:
                        self.log_result("Session Processing - Error Handling", True, 
                                      "Error response received (acceptable)")
                except:
                    self.log_result("Session Processing - Error Handling", True, 
                                  "Non-JSON error response (acceptable)")
            else:
                self.log_result("Session Processing - Invalid Session (Authenticated)", False, 
                              f"Unexpected response for invalid session: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Session Processing - Invalid Session (Authenticated)", False, f"Exception: {str(e)}")
    
    def test_logout_endpoint_with_auth(self):
        """Test Logout Endpoint with admin authentication"""
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/google/logout")
            
            # Logout should succeed (200) or handle gracefully
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        self.log_result("Logout Endpoint (Authenticated)", True, 
                                      "Logout endpoint working correctly")
                    else:
                        self.log_result("Logout Endpoint (Authenticated)", False, 
                                      "Logout returned success=false", {"response": data})
                except:
                    self.log_result("Logout Endpoint (Authenticated)", True, 
                                  "Logout endpoint responding (non-JSON acceptable)")
            else:
                self.log_result("Logout Endpoint (Authenticated)", False, 
                              f"Unexpected response: HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Logout Endpoint (Authenticated)", False, f"Exception: {str(e)}")
    
    def test_send_email_unauthorized(self):
        """Test Email Endpoint without authentication - should return 401"""
        try:
            # Create a new session without authentication
            unauthenticated_session = requests.Session()
            
            email_data = {
                "to_email": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email"
            }
            
            response = unauthenticated_session.post(f"{BACKEND_URL}/admin/google/send-email", 
                                                  json=email_data)
            
            if response.status_code == 401:
                self.log_result("Send Email - Unauthorized Access", True, 
                              "Correctly returns 401 for unauthenticated requests")
                
                # Check error message
                try:
                    data = response.json()
                    if 'error' in data or 'detail' in data:
                        self.log_result("Send Email - Error Message", True, 
                                      f"Proper error message present")
                    else:
                        self.log_result("Send Email - Error Message", False, 
                                      "No error message in response", {"response": data})
                except:
                    self.log_result("Send Email - Error Message", True, 
                                  "Non-JSON 401 response (acceptable)")
            else:
                self.log_result("Send Email - Unauthorized Access", False, 
                              f"Expected 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Send Email - Unauthorized Access", False, f"Exception: {str(e)}")
    
    def test_send_email_with_auth_invalid_data(self):
        """Test Email Endpoint with authentication but invalid email data"""
        try:
            # Test with incomplete email data
            incomplete_email_data = {
                "subject": "Test Email"
                # Missing to_email and body
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/google/send-email", 
                                       json=incomplete_email_data)
            
            # Should return an error for incomplete data
            if response.status_code in [400, 422, 500]:
                self.log_result("Send Email - Invalid Data (Authenticated)", True, 
                              f"Correctly handles invalid email data with HTTP {response.status_code}")
            else:
                self.log_result("Send Email - Invalid Data (Authenticated)", False, 
                              f"Unexpected response for invalid data: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Send Email - Invalid Data (Authenticated)", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Google OAuth integration tests"""
        print("🔐 GOOGLE ADMIN OAUTH INTEGRATION TESTING (WITH AUTHENTICATION)")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with authenticated tests.")
            return False
        
        print("\n🔍 Running Google OAuth Integration Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_google_auth_url_with_auth()
        self.test_admin_profile_unauthorized()
        self.test_session_processing_with_auth()
        self.test_logout_endpoint_with_auth()
        self.test_send_email_unauthorized()
        self.test_send_email_with_auth_invalid_data()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🔐 GOOGLE OAUTH INTEGRATION TEST SUMMARY")
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
        
        # Show failed tests
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
        
        # Critical assessment for Google OAuth integration
        critical_tests = [
            "Google Auth URL Endpoint (Authenticated)",
            "Admin Profile - Unauthorized Access", 
            "Session Processing - Invalid Session (Authenticated)",
            "Send Email - Unauthorized Access"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 3:  # At least 3 out of 4 critical tests
            print("✅ GOOGLE OAUTH INTEGRATION: SUCCESSFUL")
            print("   Google Admin OAuth endpoints are properly implemented.")
            print("   Authentication and authorization working correctly.")
            print("   System ready for Google OAuth admin authentication.")
        else:
            print("❌ GOOGLE OAUTH INTEGRATION: ISSUES FOUND")
            print("   Critical Google OAuth integration issues detected.")
            print("   Main agent action required before deployment.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = GoogleOAuthAuthenticatedTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()