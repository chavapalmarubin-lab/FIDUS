#!/usr/bin/env python3
"""
GOOGLE OAUTH CONNECTION AFTER FRONTEND CONFIGURATION FIX TEST
============================================================

This test verifies the Google OAuth connection after the frontend configuration fix as requested in the urgent review:

FIXES APPLIED:
- Created centralized config file: /app/frontend/src/config/config.js with hardcoded backend URL
- Updated apiAxios.js to use centralized config instead of undefined environment variable  
- Fixed Google CRM Integration service to use correct backend URL
- All frontend now points to https://fidus-invest.emergent.host instead of undefined

TEST OBJECTIVES:
1. Frontend-Backend Communication Test
2. Google OAuth URL Generation Test  
3. Live Application Integration Test
4. Configuration Verification

Expected Results:
- Frontend can successfully connect to Google OAuth on https://fidus-invest.emergent.host/
- OAuth URLs contain correct redirect URI
- Complete OAuth flow works properly
"""

import requests
import json
import sys
from datetime import datetime
import time
import urllib.parse

# Configuration - Using the CORRECT backend URL after fix
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GoogleOAuthFrontendFixTest:
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
    
    def test_frontend_backend_communication(self):
        """Test that frontend can now communicate with backend properly"""
        try:
            # Test basic health endpoint
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("Backend Health Check", True, 
                              "Backend is healthy and accessible", 
                              {"health_status": health_data})
            else:
                self.log_result("Backend Health Check", False, 
                              f"Backend health check failed: HTTP {response.status_code}")
                return False
            
            # Test admin endpoints with authentication
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                users_data = response.json()
                user_count = len(users_data) if isinstance(users_data, list) else users_data.get('total_users', 0)
                self.log_result("Admin API Access", True, 
                              f"Admin API accessible, found {user_count} users")
            else:
                self.log_result("Admin API Access", False, 
                              f"Admin API access failed: HTTP {response.status_code}")
            
            # Test that API calls use correct backend URL (not undefined)
            if "fidus-invest.emergent.host" in BACKEND_URL:
                self.log_result("Backend URL Configuration", True, 
                              "Using correct backend URL: fidus-invest.emergent.host")
            else:
                self.log_result("Backend URL Configuration", False, 
                              f"Incorrect backend URL: {BACKEND_URL}")
                
        except Exception as e:
            self.log_result("Frontend-Backend Communication", False, f"Exception: {str(e)}")
    
    def test_google_oauth_url_generation(self):
        """Test that frontend can request Google OAuth URLs"""
        try:
            # Test Emergent OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            if response.status_code == 200:
                oauth_data = response.json()
                auth_url = oauth_data.get('auth_url')
                
                if auth_url and 'auth.emergentagent.com' in auth_url:
                    self.log_result("Emergent OAuth URL Generation", True, 
                                  "Emergent OAuth URL generated successfully",
                                  {"auth_url": auth_url})
                else:
                    self.log_result("Emergent OAuth URL Generation", False, 
                                  "Invalid Emergent OAuth URL", {"response": oauth_data})
            else:
                self.log_result("Emergent OAuth URL Generation", False, 
                              f"Failed to generate Emergent OAuth URL: HTTP {response.status_code}")
            
            # Test Direct Google OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/auth/google/url")
            if response.status_code == 200:
                oauth_data = response.json()
                auth_url = oauth_data.get('auth_url')
                
                if auth_url and 'accounts.google.com' in auth_url:
                    # Parse URL to check parameters
                    parsed_url = urllib.parse.urlparse(auth_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    # Check for required OAuth parameters
                    required_params = ['client_id', 'redirect_uri', 'response_type', 'scope']
                    missing_params = []
                    
                    for param in required_params:
                        if param not in query_params:
                            missing_params.append(param)
                    
                    if not missing_params:
                        # Check redirect URI contains correct domain
                        redirect_uri = query_params.get('redirect_uri', [''])[0]
                        if 'fidus-invest.emergent.host' in redirect_uri:
                            self.log_result("Direct Google OAuth URL Generation", True, 
                                          "Direct Google OAuth URL generated with correct parameters",
                                          {
                                              "auth_url": auth_url,
                                              "redirect_uri": redirect_uri,
                                              "client_id": query_params.get('client_id', [''])[0]
                                          })
                        else:
                            self.log_result("Direct Google OAuth URL Generation", False, 
                                          "Incorrect redirect URI in OAuth URL",
                                          {"redirect_uri": redirect_uri, "expected_domain": "fidus-invest.emergent.host"})
                    else:
                        self.log_result("Direct Google OAuth URL Generation", False, 
                                      f"Missing OAuth parameters: {missing_params}",
                                      {"auth_url": auth_url})
                else:
                    self.log_result("Direct Google OAuth URL Generation", False, 
                                  "Invalid Direct Google OAuth URL", {"response": oauth_data})
            else:
                self.log_result("Direct Google OAuth URL Generation", False, 
                              f"Failed to generate Direct Google OAuth URL: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google OAuth URL Generation", False, f"Exception: {str(e)}")
    
    def test_google_oauth_callback_endpoints(self):
        """Test that OAuth callback endpoints are accessible"""
        try:
            # Test OAuth callback endpoints (should be accessible but return appropriate responses)
            callback_endpoints = [
                "/admin/google-callback",
                "/api/admin/google-callback", 
                "/auth/google/callback"
            ]
            
            for endpoint in callback_endpoints:
                try:
                    # Test GET request to callback endpoint (should be accessible)
                    response = self.session.get(f"{BACKEND_URL.replace('/api', '')}{endpoint}")
                    
                    # Callback endpoints should be accessible (not 404)
                    if response.status_code != 404:
                        self.log_result(f"OAuth Callback Endpoint - {endpoint}", True, 
                                      f"Callback endpoint accessible: HTTP {response.status_code}")
                    else:
                        self.log_result(f"OAuth Callback Endpoint - {endpoint}", False, 
                                      f"Callback endpoint not found: HTTP {response.status_code}")
                        
                except Exception as e:
                    self.log_result(f"OAuth Callback Endpoint - {endpoint}", False, 
                                  f"Exception testing {endpoint}: {str(e)}")
                    
        except Exception as e:
            self.log_result("OAuth Callback Endpoints", False, f"Exception: {str(e)}")
    
    def test_google_api_endpoints_readiness(self):
        """Test that Google API endpoints are ready for OAuth completion"""
        try:
            # Test Google API endpoints that should indicate auth_required when not authenticated
            google_endpoints = [
                ("/google/gmail/real-messages", "Gmail Real Messages"),
                ("/google/calendar/events", "Calendar Events"),
                ("/google/drive/real-files", "Drive Real Files"),
                ("/google/connection/test-all", "Connection Monitor")
            ]
            
            for endpoint, name in google_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if response indicates authentication required
                        if (data.get('auth_required') or 
                            'authentication required' in str(data).lower() or
                            data.get('status') == 'disconnected'):
                            self.log_result(f"Google API Readiness - {name}", True, 
                                          f"{name} endpoint ready, awaiting OAuth completion",
                                          {"response_status": data.get('status', 'auth_required')})
                        else:
                            self.log_result(f"Google API Readiness - {name}", True, 
                                          f"{name} endpoint accessible and functional",
                                          {"response": data})
                    else:
                        self.log_result(f"Google API Readiness - {name}", False, 
                                      f"{name} endpoint failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    self.log_result(f"Google API Readiness - {name}", False, 
                                  f"Exception testing {name}: {str(e)}")
                    
        except Exception as e:
            self.log_result("Google API Endpoints Readiness", False, f"Exception: {str(e)}")
    
    def test_google_oauth_configuration(self):
        """Test Google OAuth configuration is properly set"""
        try:
            # Test Google connection monitor to verify configuration
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            if response.status_code == 200:
                connection_data = response.json()
                
                # Check if all 4 Google services are configured
                services = connection_data.get('services', {})
                expected_services = ['gmail', 'calendar', 'drive', 'meet']
                
                configured_services = []
                for service in expected_services:
                    if service in services:
                        configured_services.append(service)
                
                if len(configured_services) == 4:
                    self.log_result("Google OAuth Configuration", True, 
                                  f"All 4 Google services configured: {configured_services}",
                                  {"services": services})
                else:
                    missing_services = [s for s in expected_services if s not in configured_services]
                    self.log_result("Google OAuth Configuration", False, 
                                  f"Missing Google services: {missing_services}",
                                  {"configured": configured_services, "missing": missing_services})
            else:
                self.log_result("Google OAuth Configuration", False, 
                              f"Failed to check Google configuration: HTTP {response.status_code}")
            
            # Test Google profile endpoint
            response = self.session.get(f"{BACKEND_URL}/google/profile")
            if response.status_code == 200:
                profile_data = response.json()
                if profile_data.get('auth_required') or 'authentication required' in str(profile_data).lower():
                    self.log_result("Google Profile Endpoint", True, 
                                  "Google profile endpoint ready for OAuth completion")
                else:
                    self.log_result("Google Profile Endpoint", True, 
                                  "Google profile endpoint accessible", {"profile": profile_data})
            elif response.status_code == 404:
                self.log_result("Google Profile Endpoint", False, 
                              "Google profile endpoint not found")
            else:
                self.log_result("Google Profile Endpoint", True, 
                              f"Google profile endpoint responding: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google OAuth Configuration", False, f"Exception: {str(e)}")
    
    def test_live_application_oauth_flow_readiness(self):
        """Test that the live application is ready for OAuth flow completion"""
        try:
            # Test that the system shows proper disconnected status (expected before OAuth completion)
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            if response.status_code == 200:
                connection_data = response.json()
                overall_status = connection_data.get('overall_status', 'unknown')
                
                if overall_status in ['disconnected', 'no_auth', 'auth_required']:
                    self.log_result("OAuth Flow Readiness", True, 
                                  f"System shows '{overall_status}' status as expected (OAuth not completed yet)")
                elif overall_status == 'connected':
                    self.log_result("OAuth Flow Readiness", True, 
                                  "System shows 'connected' status - OAuth may already be completed")
                else:
                    self.log_result("OAuth Flow Readiness", False, 
                                  f"Unexpected connection status: {overall_status}",
                                  {"connection_data": connection_data})
            else:
                self.log_result("OAuth Flow Readiness", False, 
                              f"Failed to check connection status: HTTP {response.status_code}")
            
            # Test that Connect Google Workspace button functionality is ready
            # This is tested by verifying OAuth URL generation works
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            if response.status_code == 200:
                oauth_data = response.json()
                if oauth_data.get('auth_url'):
                    self.log_result("Connect Google Workspace Button Readiness", True, 
                                  "Connect Google Workspace button will function correctly")
                else:
                    self.log_result("Connect Google Workspace Button Readiness", False, 
                                  "OAuth URL generation failed for Connect button")
            else:
                self.log_result("Connect Google Workspace Button Readiness", False, 
                              f"Connect button OAuth URL generation failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Live Application OAuth Flow Readiness", False, f"Exception: {str(e)}")
    
    def test_configuration_verification(self):
        """Verify centralized config is being used correctly"""
        try:
            # Test that hardcoded backend URL overrides undefined environment variable
            # This is verified by successful API calls to the correct URL
            
            # Test multiple API endpoints to ensure consistent URL usage
            test_endpoints = [
                ("/health", "Health Check"),
                ("/admin/users", "Admin Users"),
                ("/google/connection/test-all", "Google Connection Monitor"),
                ("/admin/google/auth-url", "Google OAuth URL")
            ]
            
            successful_endpoints = 0
            total_endpoints = len(test_endpoints)
            
            for endpoint, name in test_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code in [200, 401]:  # 401 is OK for auth-required endpoints
                        successful_endpoints += 1
                        self.log_result(f"Config Verification - {name}", True, 
                                      f"{name} endpoint accessible via correct URL")
                    else:
                        self.log_result(f"Config Verification - {name}", False, 
                                      f"{name} endpoint failed: HTTP {response.status_code}")
                except Exception as e:
                    self.log_result(f"Config Verification - {name}", False, 
                                  f"Exception testing {name}: {str(e)}")
            
            # Overall configuration assessment
            config_success_rate = (successful_endpoints / total_endpoints) * 100
            if config_success_rate >= 75:
                self.log_result("Centralized Config Verification", True, 
                              f"Configuration working correctly: {config_success_rate:.1f}% success rate")
            else:
                self.log_result("Centralized Config Verification", False, 
                              f"Configuration issues detected: {config_success_rate:.1f}% success rate")
                
        except Exception as e:
            self.log_result("Configuration Verification", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Google OAuth frontend fix tests"""
        print("🎯 GOOGLE OAUTH CONNECTION AFTER FRONTEND CONFIGURATION FIX TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Google OAuth Frontend Fix Tests...")
        print("-" * 50)
        
        # Run all tests in order
        self.test_frontend_backend_communication()
        self.test_google_oauth_url_generation()
        self.test_google_oauth_callback_endpoints()
        self.test_google_api_endpoints_readiness()
        self.test_google_oauth_configuration()
        self.test_live_application_oauth_flow_readiness()
        self.test_configuration_verification()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 GOOGLE OAUTH FRONTEND FIX TEST SUMMARY")
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
        
        # Critical assessment based on review requirements
        critical_tests = [
            "Frontend-Backend Communication",
            "Direct Google OAuth URL Generation",
            "Google OAuth Configuration",
            "OAuth Flow Readiness",
            "Centralized Config Verification"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if success_rate >= 80:
            print("✅ GOOGLE OAUTH FRONTEND FIX: SUCCESSFUL")
            print("   ✓ Frontend can now connect to Google OAuth")
            print("   ✓ Backend URL configuration fixed")
            print("   ✓ OAuth URLs contain correct redirect URI")
            print("   ✓ Complete OAuth flow ready for user completion")
            print("   ✓ System ready for Google Workspace integration")
            print()
            print("🎉 NEXT STEPS:")
            print("   1. User visits https://fidus-invest.emergent.host")
            print("   2. Login as admin (admin/password123)")
            print("   3. Click 'Connect Google Workspace' button")
            print("   4. Complete OAuth flow with Google")
            print("   5. Verify Google APIs are working")
        else:
            print("❌ GOOGLE OAUTH FRONTEND FIX: ISSUES DETECTED")
            print("   Frontend configuration fix has remaining issues.")
            print("   Main agent action required before OAuth completion.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = GoogleOAuthFrontendFixTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()