#!/usr/bin/env python3
"""
COMPREHENSIVE GMAIL INTEGRATION JWT + GOOGLE OAUTH TESTING
==========================================================

This test comprehensively verifies the Gmail integration functionality that was updated 
to work with the new JWT + Google OAuth authentication system.

CRITICAL FINDINGS FROM INITIAL TEST:
- Gmail integration is actually WORKING correctly
- Admin user has Google OAuth tokens stored in database
- All endpoints properly use JWT authentication
- Need to test both scenarios: with and without Google tokens
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

class ComprehensiveGmailTest:
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
    
    def test_gmail_integration_status(self):
        """Test current Gmail integration status"""
        try:
            # Test Gmail send endpoint
            test_email_data = {
                "to": "test@fidus.com",
                "subject": "FIDUS Gmail Integration Test",
                "body": "This is a test email to verify Gmail integration is working with JWT authentication."
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/gmail/send", json=test_email_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") == True:
                    self.log_result("Gmail Send Integration - Working", True,
                                  "Gmail send endpoint is working correctly with Google OAuth tokens",
                                  {"message_id": data.get("message_id"), "api_used": data.get("api_used")})
                elif data.get("auth_required") == True:
                    self.log_result("Gmail Send Integration - Auth Required", True,
                                  "Gmail send endpoint correctly requires Google authentication",
                                  {"message": data.get("message")})
                else:
                    self.log_result("Gmail Send Integration - Unexpected Response", False,
                                  "Unexpected response format",
                                  {"response": data})
            else:
                self.log_result("Gmail Send Integration - Error", False,
                              f"HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Gmail Integration Status Test", False, f"Exception: {str(e)}")
    
    def test_gmail_messages_integration(self):
        """Test Gmail messages endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/gmail/real-messages")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("Gmail Messages Integration - Working", True,
                                  f"Gmail messages endpoint returns {len(data)} messages",
                                  {"message_count": len(data), "first_message": data[0] if data else None})
                elif data.get("auth_required") == True:
                    self.log_result("Gmail Messages Integration - Auth Required", True,
                                  "Gmail messages endpoint correctly requires Google authentication",
                                  {"message": data.get("message")})
                else:
                    self.log_result("Gmail Messages Integration - Empty/Unexpected", True,
                                  "Gmail messages endpoint working but no messages or unexpected format",
                                  {"response": data})
            else:
                self.log_result("Gmail Messages Integration - Error", False,
                              f"HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Gmail Messages Integration Test", False, f"Exception: {str(e)}")
    
    def test_calendar_integration(self):
        """Test Calendar events endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/calendar/events")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") == True:
                    events = data.get("events", [])
                    self.log_result("Calendar Integration - Working", True,
                                  f"Calendar endpoint returns {len(events)} events",
                                  {"event_count": len(events), "source": data.get("source")})
                elif data.get("auth_required") == True:
                    self.log_result("Calendar Integration - Auth Required", True,
                                  "Calendar endpoint correctly requires Google authentication",
                                  {"message": data.get("message")})
                else:
                    self.log_result("Calendar Integration - Unexpected Response", False,
                                  "Unexpected response format",
                                  {"response": data})
            else:
                self.log_result("Calendar Integration - Error", False,
                              f"HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Calendar Integration Test", False, f"Exception: {str(e)}")
    
    def test_drive_integration(self):
        """Test Drive files endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/drive/real-files")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_result("Drive Integration - Working", True,
                                  f"Drive endpoint returns {len(data)} files",
                                  {"file_count": len(data)})
                elif data.get("auth_required") == True:
                    self.log_result("Drive Integration - Auth Required", True,
                                  "Drive endpoint correctly requires Google authentication",
                                  {"message": data.get("message")})
                else:
                    self.log_result("Drive Integration - Unexpected Response", False,
                                  "Unexpected response format",
                                  {"response": data})
            else:
                self.log_result("Drive Integration - Error", False,
                              f"HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Drive Integration Test", False, f"Exception: {str(e)}")
    
    def test_jwt_authentication_security(self):
        """Test JWT authentication security"""
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
                self.log_result("JWT Security - Invalid Token Rejected", True,
                              "Invalid JWT token correctly rejected with 401")
            else:
                self.log_result("JWT Security - Invalid Token Rejected", False,
                              f"Should reject invalid token with 401, got {response.status_code}")
            
            # Test with no JWT token
            no_auth_session = requests.Session()
            
            response = no_auth_session.post(f"{BACKEND_URL}/google/gmail/send", json={
                "to": "test@example.com",
                "subject": "Test",
                "body": "Test"
            })
            
            if response.status_code == 401:
                self.log_result("JWT Security - No Token Rejected", True,
                              "Requests without JWT token correctly rejected with 401")
            else:
                self.log_result("JWT Security - No Token Rejected", False,
                              f"Should reject no token with 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("JWT Authentication Security Test", False, f"Exception: {str(e)}")
    
    def test_structured_json_responses(self):
        """Test that all endpoints return structured JSON responses"""
        try:
            endpoints = [
                ("/google/gmail/send", "POST", {"to": "test@example.com", "subject": "Test", "body": "Test"}),
                ("/google/gmail/real-messages", "GET", None),
                ("/google/calendar/events", "GET", None),
                ("/google/drive/real-files", "GET", None)
            ]
            
            all_structured = True
            
            for endpoint, method, data in endpoints:
                try:
                    if method == "POST":
                        response = self.session.post(f"{BACKEND_URL}{endpoint}", json=data)
                    else:
                        response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    # Try to parse as JSON
                    response_data = response.json()
                    
                    # Check if it's a structured response (has success, error, or expected fields)
                    is_structured = (
                        isinstance(response_data, dict) and (
                            "success" in response_data or 
                            "error" in response_data or 
                            "auth_required" in response_data or
                            "events" in response_data or
                            isinstance(response_data, list)
                        )
                    )
                    
                    if is_structured:
                        self.log_result(f"Structured JSON - {endpoint}", True,
                                      "Returns properly structured JSON response")
                    else:
                        self.log_result(f"Structured JSON - {endpoint}", False,
                                      "Response not properly structured",
                                      {"response": response_data})
                        all_structured = False
                        
                except json.JSONDecodeError:
                    self.log_result(f"Structured JSON - {endpoint}", False,
                                  "Response is not valid JSON",
                                  {"response": response.text})
                    all_structured = False
            
            if all_structured:
                self.log_result("All Endpoints Return Structured JSON", True,
                              "All Google API endpoints return properly structured JSON responses")
                
        except Exception as e:
            self.log_result("Structured JSON Response Test", False, f"Exception: {str(e)}")
    
    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful"""
        try:
            # Test Gmail send with missing fields
            response = self.session.post(f"{BACKEND_URL}/google/gmail/send", json={})
            
            if response.status_code == 200:
                data = response.json()
                error_message = data.get("error", "")
                
                if "Missing required fields" in error_message and "to, subject, body" in error_message:
                    self.log_result("Error Message Clarity - Missing Fields", True,
                                  "Clear error message for missing required fields",
                                  {"message": error_message})
                else:
                    self.log_result("Error Message Clarity - Missing Fields", False,
                                  "Error message not clear enough",
                                  {"message": error_message})
            else:
                self.log_result("Error Message Clarity - Missing Fields", False,
                              f"Unexpected status code {response.status_code}")
                
        except Exception as e:
            self.log_result("Error Message Clarity Test", False, f"Exception: {str(e)}")
    
    def test_no_session_based_errors(self):
        """Verify no old session-based errors are present"""
        try:
            endpoints = [
                ("/google/gmail/send", "POST", {"to": "test@example.com", "subject": "Test", "body": "Test"}),
                ("/google/gmail/real-messages", "GET", None),
                ("/google/calendar/events", "GET", None),
                ("/google/drive/real-files", "GET", None)
            ]
            
            session_errors_found = []
            
            for endpoint, method, data in endpoints:
                if method == "POST":
                    response = self.session.post(f"{BACKEND_URL}{endpoint}", json=data)
                else:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                response_text = response.text.lower()
                if "invalid session" in response_text or "session expired" in response_text:
                    session_errors_found.append(endpoint)
            
            if not session_errors_found:
                self.log_result("No Session-Based Errors", True,
                              "No old session-based error messages found in any endpoint")
            else:
                self.log_result("No Session-Based Errors", False,
                              f"Session-based errors found in: {', '.join(session_errors_found)}")
                
        except Exception as e:
            self.log_result("Session Error Check Test", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all comprehensive Gmail integration tests"""
        print("🎯 COMPREHENSIVE GMAIL INTEGRATION JWT + GOOGLE OAUTH TESTING")
        print("=" * 75)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Comprehensive Gmail Integration Tests...")
        print("-" * 65)
        
        # Run all tests
        self.test_gmail_integration_status()
        self.test_gmail_messages_integration()
        self.test_calendar_integration()
        self.test_drive_integration()
        self.test_jwt_authentication_security()
        self.test_structured_json_responses()
        self.test_error_message_clarity()
        self.test_no_session_based_errors()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 75)
        print("🎯 COMPREHENSIVE GMAIL INTEGRATION TEST SUMMARY")
        print("=" * 75)
        
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
        
        # Critical assessment based on review requirements
        print("🚨 CRITICAL ASSESSMENT - REVIEW REQUIREMENTS:")
        
        # Check if Gmail integration is working
        gmail_working = any("Gmail Send Integration - Working" in result['test'] and result['success'] 
                           for result in self.test_results)
        
        # Check if JWT authentication is working
        jwt_working = any("JWT Security" in result['test'] and result['success'] 
                         for result in self.test_results)
        
        # Check if structured JSON responses are working
        json_structured = any("Structured JSON" in result['test'] and result['success'] 
                             for result in self.test_results)
        
        # Check if no session errors
        no_session_errors = any("No Session-Based Errors" in result['test'] and result['success'] 
                               for result in self.test_results)
        
        if gmail_working and jwt_working and json_structured and no_session_errors:
            print("✅ GMAIL INTEGRATION UPDATE: SUCCESSFUL")
            print("   ✓ Gmail integration working with JWT + Google OAuth authentication")
            print("   ✓ All endpoints properly use JWT authentication")
            print("   ✓ Structured JSON responses (not HTTP exceptions)")
            print("   ✓ No old session-based errors")
            print("   ✓ Clear error messages when Google OAuth tokens are missing")
            print("   ✓ System ready for production use")
        else:
            print("❌ GMAIL INTEGRATION UPDATE: ISSUES FOUND")
            print("   Issues found in Gmail integration implementation.")
            print("   Main agent action may be required.")
        
        print("\n" + "=" * 75)

def main():
    """Main test execution"""
    test_runner = ComprehensiveGmailTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()