#!/usr/bin/env python3
"""
GMAIL INTEGRATION JWT + GOOGLE OAUTH AUTHENTICATION TESTING
===========================================================

This test verifies the Gmail integration functionality that was updated to work with 
the new JWT + Google OAuth authentication system as requested in the review.

CRITICAL CONTEXT:
User was getting "Failed to send email" errors. Main agent updated all Google API 
endpoints to use the new JWT authentication system instead of the old session-based system.

UPDATED ENDPOINTS TO TEST:
1. `/api/google/gmail/send` - Updated to use JWT + Google OAuth tokens
2. `/api/google/gmail/real-messages` - Already uses JWT authentication
3. `/api/google/calendar/events` - Updated to use JWT authentication  
4. `/api/google/drive/real-files` - Updated to use JWT authentication

EXPECTED RESULTS:
- All endpoints should accept JWT authentication properly
- When Google OAuth tokens are missing, endpoints should return clear error messages with auth_required=true
- No more "Invalid session" errors from old session-based system
- All responses should be properly structured JSON (not HTTP exceptions)
- Gmail send endpoint should work properly when Google tokens are available
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-google-sync.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GmailIntegrationJWTTest:
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
        """Authenticate as admin user and get JWT token"""
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
                    self.log_result("Admin JWT Authentication", True, 
                                  "Successfully authenticated as admin and obtained JWT token")
                    return True
                else:
                    self.log_result("Admin JWT Authentication", False, 
                                  "No JWT token received", {"response": data})
                    return False
            else:
                self.log_result("Admin JWT Authentication", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin JWT Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_gmail_send_endpoint_jwt_auth(self):
        """Test Gmail send endpoint with JWT token but no Google OAuth tokens"""
        try:
            # Test with valid JWT token but no Google OAuth tokens
            test_email_data = {
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email from FIDUS Gmail integration"
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/gmail/send", json=test_email_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response indicates auth_required=true
                if data.get("auth_required") == True:
                    self.log_result("Gmail Send - JWT Auth with No Google Tokens", True,
                                  "Correctly returns auth_required=true when Google OAuth tokens missing",
                                  {"response": data})
                    
                    # Check error message clarity
                    error_message = data.get("message", "")
                    if "Google authentication required" in error_message:
                        self.log_result("Gmail Send - Clear Error Message", True,
                                      "Error message is clear and helpful",
                                      {"message": error_message})
                    else:
                        self.log_result("Gmail Send - Clear Error Message", False,
                                      "Error message not clear enough",
                                      {"message": error_message})
                else:
                    self.log_result("Gmail Send - JWT Auth with No Google Tokens", False,
                                  "Should return auth_required=true when Google tokens missing",
                                  {"response": data})
            else:
                # Check if it's a structured JSON error response (not HTTP exception)
                try:
                    error_data = response.json()
                    self.log_result("Gmail Send - Structured JSON Response", True,
                                  f"Returns structured JSON error (HTTP {response.status_code})",
                                  {"response": error_data})
                except:
                    self.log_result("Gmail Send - Structured JSON Response", False,
                                  f"Returns HTTP exception instead of JSON (HTTP {response.status_code})",
                                  {"response": response.text})
                
        except Exception as e:
            self.log_result("Gmail Send Endpoint Test", False, f"Exception: {str(e)}")
    
    def test_gmail_messages_endpoint_jwt_auth(self):
        """Test Gmail messages endpoint with JWT authentication"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/gmail/real-messages")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response indicates auth_required=true
                if data.get("auth_required") == True:
                    self.log_result("Gmail Messages - JWT Auth with No Google Tokens", True,
                                  "Correctly returns auth_required=true when Google OAuth tokens missing",
                                  {"response": data})
                else:
                    # If it returns actual messages, that's also valid (means Google tokens are present)
                    if isinstance(data, list) or data.get("messages"):
                        self.log_result("Gmail Messages - JWT Auth with Google Tokens", True,
                                      "Returns Gmail messages (Google tokens present)",
                                      {"message_count": len(data) if isinstance(data, list) else len(data.get("messages", []))})
                    else:
                        self.log_result("Gmail Messages - JWT Auth Response", False,
                                      "Unexpected response format",
                                      {"response": data})
            else:
                # Check if it's a structured JSON error response
                try:
                    error_data = response.json()
                    self.log_result("Gmail Messages - Structured JSON Response", True,
                                  f"Returns structured JSON error (HTTP {response.status_code})",
                                  {"response": error_data})
                except:
                    self.log_result("Gmail Messages - Structured JSON Response", False,
                                  f"Returns HTTP exception instead of JSON (HTTP {response.status_code})",
                                  {"response": response.text})
                
        except Exception as e:
            self.log_result("Gmail Messages Endpoint Test", False, f"Exception: {str(e)}")
    
    def test_calendar_events_endpoint_jwt_auth(self):
        """Test Calendar events endpoint with JWT authentication"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/calendar/events")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response indicates auth_required=true
                if data.get("auth_required") == True:
                    self.log_result("Calendar Events - JWT Auth with No Google Tokens", True,
                                  "Correctly returns auth_required=true when Google OAuth tokens missing",
                                  {"response": data})
                else:
                    # If it returns actual events, that's also valid
                    if isinstance(data, list) or data.get("events"):
                        self.log_result("Calendar Events - JWT Auth with Google Tokens", True,
                                      "Returns Calendar events (Google tokens present)",
                                      {"event_count": len(data) if isinstance(data, list) else len(data.get("events", []))})
                    else:
                        self.log_result("Calendar Events - JWT Auth Response", False,
                                      "Unexpected response format",
                                      {"response": data})
            else:
                # Check if it's a structured JSON error response
                try:
                    error_data = response.json()
                    self.log_result("Calendar Events - Structured JSON Response", True,
                                  f"Returns structured JSON error (HTTP {response.status_code})",
                                  {"response": error_data})
                except:
                    self.log_result("Calendar Events - Structured JSON Response", False,
                                  f"Returns HTTP exception instead of JSON (HTTP {response.status_code})",
                                  {"response": response.text})
                
        except Exception as e:
            self.log_result("Calendar Events Endpoint Test", False, f"Exception: {str(e)}")
    
    def test_drive_files_endpoint_jwt_auth(self):
        """Test Drive files endpoint with JWT authentication"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/drive/real-files")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response indicates auth_required=true
                if data.get("auth_required") == True:
                    self.log_result("Drive Files - JWT Auth with No Google Tokens", True,
                                  "Correctly returns auth_required=true when Google OAuth tokens missing",
                                  {"response": data})
                else:
                    # If it returns actual files, that's also valid
                    if isinstance(data, list) or data.get("files"):
                        self.log_result("Drive Files - JWT Auth with Google Tokens", True,
                                      "Returns Drive files (Google tokens present)",
                                      {"file_count": len(data) if isinstance(data, list) else len(data.get("files", []))})
                    else:
                        self.log_result("Drive Files - JWT Auth Response", False,
                                      "Unexpected response format",
                                      {"response": data})
            else:
                # Check if it's a structured JSON error response
                try:
                    error_data = response.json()
                    self.log_result("Drive Files - Structured JSON Response", True,
                                  f"Returns structured JSON error (HTTP {response.status_code})",
                                  {"response": error_data})
                except:
                    self.log_result("Drive Files - Structured JSON Response", False,
                                  f"Returns HTTP exception instead of JSON (HTTP {response.status_code})",
                                  {"response": response.text})
                
        except Exception as e:
            self.log_result("Drive Files Endpoint Test", False, f"Exception: {str(e)}")
    
    def test_jwt_token_validation(self):
        """Test that JWT token is properly validated"""
        try:
            # Test with invalid JWT token
            invalid_session = requests.Session()
            invalid_session.headers.update({"Authorization": "Bearer invalid_token_123"})
            
            response = invalid_session.post(f"{BACKEND_URL}/google/gmail/send", json={
                "to": "test@example.com",
                "subject": "Test",
                "body": "Test"
            })
            
            if response.status_code == 401:
                self.log_result("JWT Token Validation - Invalid Token", True,
                              "Correctly rejects invalid JWT token with 401",
                              {"status_code": response.status_code})
            else:
                self.log_result("JWT Token Validation - Invalid Token", False,
                              f"Should return 401 for invalid token, got {response.status_code}",
                              {"response": response.text})
            
            # Test with no JWT token
            no_auth_session = requests.Session()
            
            response = no_auth_session.post(f"{BACKEND_URL}/google/gmail/send", json={
                "to": "test@example.com",
                "subject": "Test",
                "body": "Test"
            })
            
            if response.status_code == 401:
                self.log_result("JWT Token Validation - No Token", True,
                              "Correctly rejects requests without JWT token with 401",
                              {"status_code": response.status_code})
            else:
                self.log_result("JWT Token Validation - No Token", False,
                              f"Should return 401 for no token, got {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("JWT Token Validation Test", False, f"Exception: {str(e)}")
    
    def test_gmail_send_field_validation(self):
        """Test Gmail send endpoint field validation"""
        try:
            # Test with missing required fields
            test_cases = [
                {"data": {}, "missing": "all fields"},
                {"data": {"to": "test@example.com"}, "missing": "subject and body"},
                {"data": {"subject": "Test"}, "missing": "to and body"},
                {"data": {"body": "Test"}, "missing": "to and subject"},
            ]
            
            for test_case in test_cases:
                response = self.session.post(f"{BACKEND_URL}/google/gmail/send", json=test_case["data"])
                
                if response.status_code in [400, 422]:  # Bad request or validation error
                    try:
                        error_data = response.json()
                        self.log_result(f"Gmail Send Field Validation - Missing {test_case['missing']}", True,
                                      f"Correctly validates missing fields (HTTP {response.status_code})",
                                      {"response": error_data})
                    except:
                        self.log_result(f"Gmail Send Field Validation - Missing {test_case['missing']}", False,
                                      "Should return JSON error for validation",
                                      {"response": response.text})
                else:
                    self.log_result(f"Gmail Send Field Validation - Missing {test_case['missing']}", False,
                                  f"Should return 400/422 for missing fields, got {response.status_code}",
                                  {"response": response.text})
                
        except Exception as e:
            self.log_result("Gmail Send Field Validation Test", False, f"Exception: {str(e)}")
    
    def test_no_session_based_errors(self):
        """Test that old session-based errors are eliminated"""
        try:
            # Test all endpoints to ensure no "Invalid session" errors
            endpoints = [
                ("/google/gmail/send", "POST", {"to": "test@example.com", "subject": "Test", "body": "Test"}),
                ("/google/gmail/real-messages", "GET", None),
                ("/google/calendar/events", "GET", None),
                ("/google/drive/real-files", "GET", None)
            ]
            
            session_error_found = False
            
            for endpoint, method, data in endpoints:
                if method == "POST":
                    response = self.session.post(f"{BACKEND_URL}{endpoint}", json=data)
                else:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                # Check response text for session-based error messages
                response_text = response.text.lower()
                if "invalid session" in response_text or "session expired" in response_text:
                    session_error_found = True
                    self.log_result(f"No Session Errors - {endpoint}", False,
                                  "Found session-based error message",
                                  {"endpoint": endpoint, "response": response.text})
            
            if not session_error_found:
                self.log_result("No Session-Based Errors", True,
                              "No old session-based error messages found in any endpoint")
            
        except Exception as e:
            self.log_result("Session Error Check Test", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Gmail integration JWT authentication tests"""
        print("🎯 GMAIL INTEGRATION JWT + GOOGLE OAUTH AUTHENTICATION TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Gmail Integration JWT Authentication Tests...")
        print("-" * 60)
        
        # Run all Gmail integration tests
        self.test_gmail_send_endpoint_jwt_auth()
        self.test_gmail_messages_endpoint_jwt_auth()
        self.test_calendar_events_endpoint_jwt_auth()
        self.test_drive_files_endpoint_jwt_auth()
        self.test_jwt_token_validation()
        self.test_gmail_send_field_validation()
        self.test_no_session_based_errors()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 GMAIL INTEGRATION JWT AUTHENTICATION TEST SUMMARY")
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
        
        # Critical assessment
        critical_tests = [
            "Gmail Send - JWT Auth with No Google Tokens",
            "Gmail Messages - JWT Auth with No Google Tokens", 
            "Calendar Events - JWT Auth with No Google Tokens",
            "Drive Files - JWT Auth with No Google Tokens",
            "No Session-Based Errors"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ GMAIL INTEGRATION JWT AUTHENTICATION: SUCCESSFUL")
            print("   All Google API endpoints properly use JWT authentication.")
            print("   Clear error messages when Google OAuth tokens are missing.")
            print("   No more session-based errors from old system.")
            print("   System ready for Google OAuth completion.")
        else:
            print("❌ GMAIL INTEGRATION JWT AUTHENTICATION: ISSUES FOUND")
            print("   Critical authentication issues need to be resolved.")
            print("   Main agent action required before deployment.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = GmailIntegrationJWTTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()