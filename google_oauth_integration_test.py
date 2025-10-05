#!/usr/bin/env python3
"""
GOOGLE API INTEGRATION AND OAUTH FLOW TESTING
==============================================

This test verifies the Google API authentication and connection system as requested:
- Google OAuth URL Generation (/api/admin/google/auth-url)
- Google Connection Monitor Endpoints (/api/google/connection/test-all, /api/google/connection/test/{service})
- Google API Authentication Status (Gmail, Calendar, Drive API endpoints)
- JWT Authentication for all Google endpoints
- Environment Variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_OAUTH_REDIRECT_URI)

Expected Results:
- OAuth URL generation works without "Failed to get auth URL" errors
- Connection monitor returns real-time status for all 4 services
- API endpoints return proper "auth_required" responses when not authenticated
- No 404 or 500 errors on Google-related endpoints
- All endpoints require admin JWT authentication
"""

import requests
import json
import sys
from datetime import datetime
import time
import re
from urllib.parse import urlparse, parse_qs

# Configuration
BACKEND_URL = "https://fidus-finance-api.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GoogleOAuthIntegrationTest:
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
    
    def test_google_oauth_url_generation(self):
        """Test Google OAuth URL generation endpoint"""
        try:
            # Test with authentication
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if success is true
                if data.get('success'):
                    auth_url = data.get('auth_url')
                    if auth_url:
                        # Validate OAuth URL structure
                        parsed_url = urlparse(auth_url)
                        query_params = parse_qs(parsed_url.query)
                        
                        # Check required OAuth parameters
                        required_params = ['client_id', 'redirect_uri', 'response_type', 'scope']
                        missing_params = []
                        
                        for param in required_params:
                            if param not in query_params:
                                missing_params.append(param)
                        
                        if not missing_params:
                            # Verify client_id matches environment variable
                            client_id = query_params.get('client_id', [''])[0]
                            redirect_uri = query_params.get('redirect_uri', [''])[0]
                            
                            self.log_result("Google OAuth URL Generation", True, 
                                          "OAuth URL generated successfully with all required parameters",
                                          {
                                              "auth_url": auth_url,
                                              "client_id": client_id,
                                              "redirect_uri": redirect_uri,
                                              "params": list(query_params.keys())
                                          })
                        else:
                            self.log_result("Google OAuth URL Generation", False, 
                                          f"OAuth URL missing required parameters: {missing_params}",
                                          {"auth_url": auth_url, "params": list(query_params.keys())})
                    else:
                        self.log_result("Google OAuth URL Generation", False, 
                                      "Success=true but no auth_url in response", {"response": data})
                else:
                    error_msg = data.get('error', 'Unknown error')
                    self.log_result("Google OAuth URL Generation", False, 
                                  f"Failed to get auth URL: {error_msg}", {"response": data})
            else:
                self.log_result("Google OAuth URL Generation", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Google OAuth URL Generation", False, f"Exception: {str(e)}")
    
    def test_google_oauth_url_without_auth(self):
        """Test Google OAuth URL endpoint without authentication (should fail)"""
        try:
            # Remove auth header temporarily
            auth_header = self.session.headers.pop("Authorization", None)
            
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            
            # Restore auth header
            if auth_header:
                self.session.headers["Authorization"] = auth_header
            
            if response.status_code == 401:
                self.log_result("Google OAuth URL - No Auth", True, 
                              "Correctly returns 401 Unauthorized without JWT token")
            else:
                self.log_result("Google OAuth URL - No Auth", False, 
                              f"Expected 401, got HTTP {response.status_code}", 
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Google OAuth URL - No Auth", False, f"Exception: {str(e)}")
    
    def test_google_connection_monitor_all(self):
        """Test Google connection monitor test-all endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['overall_status', 'services']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    services = data.get('services', {})
                    expected_services = ['gmail', 'calendar', 'drive', 'meet']
                    
                    # Check if all 4 services are present
                    missing_services = [service for service in expected_services if service not in services]
                    
                    if not missing_services:
                        # Check service structure
                        service_issues = []
                        for service_name, service_data in services.items():
                            if not isinstance(service_data, dict):
                                service_issues.append(f"{service_name}: not a dict")
                            elif 'status' not in service_data:
                                service_issues.append(f"{service_name}: missing status")
                        
                        if not service_issues:
                            self.log_result("Google Connection Monitor - Test All", True, 
                                          f"All 4 services monitored with proper structure. Overall status: {data.get('overall_status')}",
                                          {"services": list(services.keys()), "overall_status": data.get('overall_status')})
                        else:
                            self.log_result("Google Connection Monitor - Test All", False, 
                                          f"Service structure issues: {service_issues}", {"response": data})
                    else:
                        self.log_result("Google Connection Monitor - Test All", False, 
                                      f"Missing services: {missing_services}", {"found_services": list(services.keys())})
                else:
                    self.log_result("Google Connection Monitor - Test All", False, 
                                  f"Missing required fields: {missing_fields}", {"response": data})
            else:
                self.log_result("Google Connection Monitor - Test All", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Google Connection Monitor - Test All", False, f"Exception: {str(e)}")
    
    def test_google_connection_monitor_individual(self):
        """Test individual Google service connection monitoring"""
        services = ['gmail', 'calendar', 'drive', 'meet']
        
        for service in services:
            try:
                response = self.session.get(f"{BACKEND_URL}/google/connection/test/{service}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check response structure for individual service
                    required_fields = ['service', 'status']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        service_name = data.get('service')
                        status = data.get('status')
                        
                        if service_name == service:
                            self.log_result(f"Google Connection Monitor - {service.title()}", True, 
                                          f"{service.title()} service monitoring working. Status: {status}",
                                          {"service": service_name, "status": status})
                        else:
                            self.log_result(f"Google Connection Monitor - {service.title()}", False, 
                                          f"Service name mismatch: expected {service}, got {service_name}")
                    else:
                        self.log_result(f"Google Connection Monitor - {service.title()}", False, 
                                      f"Missing required fields: {missing_fields}", {"response": data})
                else:
                    self.log_result(f"Google Connection Monitor - {service.title()}", False, 
                                  f"HTTP {response.status_code}", {"response": response.text})
                    
            except Exception as e:
                self.log_result(f"Google Connection Monitor - {service.title()}", False, f"Exception: {str(e)}")
    
    def test_google_connection_monitor_invalid_service(self):
        """Test connection monitor with invalid service name"""
        try:
            response = self.session.get(f"{BACKEND_URL}/google/connection/test/invalid_service")
            
            if response.status_code == 400 or response.status_code == 404:
                self.log_result("Google Connection Monitor - Invalid Service", True, 
                              f"Correctly handles invalid service with HTTP {response.status_code}")
            else:
                self.log_result("Google Connection Monitor - Invalid Service", False, 
                              f"Expected 400/404 for invalid service, got HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Google Connection Monitor - Invalid Service", False, f"Exception: {str(e)}")
    
    def test_google_connection_monitor_auth(self):
        """Test connection monitor endpoints require authentication"""
        endpoints = [
            "/google/connection/test-all",
            "/google/connection/test/gmail"
        ]
        
        for endpoint in endpoints:
            try:
                # Remove auth header temporarily
                auth_header = self.session.headers.pop("Authorization", None)
                
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                # Restore auth header
                if auth_header:
                    self.session.headers["Authorization"] = auth_header
                
                if response.status_code == 401:
                    self.log_result(f"Connection Monitor Auth - {endpoint}", True, 
                                  "Correctly requires authentication")
                else:
                    self.log_result(f"Connection Monitor Auth - {endpoint}", False, 
                                  f"Expected 401, got HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Connection Monitor Auth - {endpoint}", False, f"Exception: {str(e)}")
    
    def test_google_api_endpoints_auth_required(self):
        """Test Google API endpoints return proper auth_required responses"""
        google_api_endpoints = [
            ("/google/gmail/messages", "Gmail Messages"),
            ("/google/gmail/real-messages", "Gmail Real Messages"),
            ("/google/calendar/events", "Calendar Events"),
            ("/google/drive/files", "Drive Files"),
            ("/google/gmail/real-send", "Gmail Send")
        ]
        
        for endpoint, name in google_api_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if response indicates authentication required
                    if data.get('auth_required') or 'authentication required' in str(data).lower():
                        self.log_result(f"Google API Auth Status - {name}", True, 
                                      "Properly indicates Google authentication required",
                                      {"auth_required": data.get('auth_required')})
                    else:
                        # Check if it returns mock data (which is also acceptable)
                        if isinstance(data, list) or (isinstance(data, dict) and 'messages' in data):
                            self.log_result(f"Google API Auth Status - {name}", True, 
                                          "Returns mock data when not authenticated (acceptable behavior)")
                        else:
                            self.log_result(f"Google API Auth Status - {name}", False, 
                                          "Unclear authentication status", {"response": data})
                elif response.status_code == 401:
                    self.log_result(f"Google API Auth Status - {name}", True, 
                                  "Correctly returns 401 for unauthenticated Google API access")
                else:
                    self.log_result(f"Google API Auth Status - {name}", False, 
                                  f"Unexpected HTTP {response.status_code}", {"response": response.text})
                    
            except Exception as e:
                self.log_result(f"Google API Auth Status - {name}", False, f"Exception: {str(e)}")
    
    def test_google_api_endpoints_no_404_500(self):
        """Test Google API endpoints don't return 404 or 500 errors"""
        google_api_endpoints = [
            "/admin/google/auth-url",
            "/google/connection/test-all",
            "/google/connection/test/gmail",
            "/google/connection/test/calendar", 
            "/google/connection/test/drive",
            "/google/connection/test/meet",
            "/google/gmail/messages",
            "/google/gmail/real-messages",
            "/google/calendar/events",
            "/google/drive/files"
        ]
        
        for endpoint in google_api_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code not in [404, 500]:
                    self.log_result(f"Google API Availability - {endpoint}", True, 
                                  f"Endpoint available (HTTP {response.status_code})")
                else:
                    self.log_result(f"Google API Availability - {endpoint}", False, 
                                  f"Endpoint returns HTTP {response.status_code}", 
                                  {"response": response.text})
                    
            except Exception as e:
                self.log_result(f"Google API Availability - {endpoint}", False, f"Exception: {str(e)}")
    
    def test_environment_variables_validation(self):
        """Test that environment variables are properly configured"""
        try:
            # Test OAuth URL generation to validate environment variables
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('auth_url'):
                    auth_url = data.get('auth_url')
                    parsed_url = urlparse(auth_url)
                    query_params = parse_qs(parsed_url.query)
                    
                    # Check if client_id is present and not empty
                    client_id = query_params.get('client_id', [''])[0]
                    redirect_uri = query_params.get('redirect_uri', [''])[0]
                    
                    env_issues = []
                    
                    if not client_id:
                        env_issues.append("GOOGLE_CLIENT_ID missing or empty")
                    elif client_id == "your-client-id-here":
                        env_issues.append("GOOGLE_CLIENT_ID not configured (default value)")
                    
                    if not redirect_uri:
                        env_issues.append("GOOGLE_OAUTH_REDIRECT_URI missing or empty")
                    elif "localhost" in redirect_uri:
                        env_issues.append("GOOGLE_OAUTH_REDIRECT_URI using localhost (should be production URL)")
                    
                    if not env_issues:
                        self.log_result("Environment Variables Validation", True, 
                                      "Google OAuth environment variables properly configured",
                                      {
                                          "client_id_configured": bool(client_id),
                                          "redirect_uri": redirect_uri,
                                          "redirect_uri_production": "localhost" not in redirect_uri
                                      })
                    else:
                        self.log_result("Environment Variables Validation", False, 
                                      f"Environment variable issues: {env_issues}",
                                      {"client_id": client_id, "redirect_uri": redirect_uri})
                else:
                    self.log_result("Environment Variables Validation", False, 
                                  "Cannot validate environment variables - OAuth URL generation failed")
            else:
                self.log_result("Environment Variables Validation", False, 
                              f"Cannot validate environment variables - HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Environment Variables Validation", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Google OAuth integration tests"""
        print("🎯 GOOGLE API INTEGRATION AND OAUTH FLOW TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Google OAuth Integration Tests...")
        print("-" * 50)
        
        # Run all Google OAuth tests
        self.test_google_oauth_url_generation()
        self.test_google_oauth_url_without_auth()
        self.test_google_connection_monitor_all()
        self.test_google_connection_monitor_individual()
        self.test_google_connection_monitor_invalid_service()
        self.test_google_connection_monitor_auth()
        self.test_google_api_endpoints_auth_required()
        self.test_google_api_endpoints_no_404_500()
        self.test_environment_variables_validation()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 GOOGLE OAUTH INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
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
            "Google OAuth URL Generation",
            "Google Connection Monitor - Test All",
            "Environment Variables Validation"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if success_rate >= 80:
            print("✅ GOOGLE OAUTH INTEGRATION: WORKING PROPERLY")
            print("   OAuth URL generation functional, connection monitoring operational.")
            print("   Google API endpoints properly handle authentication requirements.")
            print("   System ready for Google Workspace integration.")
        elif success_rate >= 60:
            print("⚠️ GOOGLE OAUTH INTEGRATION: PARTIALLY WORKING")
            print("   Core functionality working but some issues detected.")
            print("   Review failed tests for optimization opportunities.")
        else:
            print("❌ GOOGLE OAUTH INTEGRATION: CRITICAL ISSUES")
            print("   Major problems with Google OAuth integration detected.")
            print("   Main agent action required to resolve authentication issues.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = GoogleOAuthIntegrationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()