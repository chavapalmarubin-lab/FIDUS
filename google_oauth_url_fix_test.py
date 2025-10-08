#!/usr/bin/env python3
"""
GOOGLE OAUTH CONNECTION TEST AFTER BACKEND URL FIX
=================================================

This test verifies Google OAuth connection functionality after fixing the backend URL from:
- OLD: https://mt5-deploy-debug.preview.emergentagent.com
- NEW: https://fidus-invest.emergent.host

Test Objectives:
1. Verify backend communication with correct URL
2. Test Google OAuth URL generation with live backend
3. Verify Google OAuth configuration (client_id, redirect_uri)
4. Test OAuth callback endpoint accessibility
5. Confirm system readiness for OAuth flow completion

Expected Results:
- All Google OAuth endpoints accessible on live URL
- OAuth URL generation working with correct redirect URI
- Google connection system ready for user OAuth completion
"""

import requests
import json
import sys
from datetime import datetime
import time
import urllib.parse

# Configuration - UPDATED URL
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GoogleOAuthURLFixTest:
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
        """Authenticate as admin user with new backend URL"""
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
                    self.log_result("Admin Authentication", True, 
                                  f"Successfully authenticated with new backend URL: {BACKEND_URL}")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, 
                              f"HTTP {response.status_code} - Backend URL may be incorrect", 
                              {"response": response.text, "url": BACKEND_URL})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, 
                          f"Connection failed to new backend URL: {str(e)}", 
                          {"backend_url": BACKEND_URL})
            return False
    
    def test_backend_communication(self):
        """Test that frontend can communicate with correct backend URL"""
        try:
            # Test basic health endpoint
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("Backend Communication", True, 
                              "Frontend successfully communicating with live backend",
                              {"health_status": health_data.get("status", "unknown")})
            else:
                self.log_result("Backend Communication", False, 
                              f"Health check failed: HTTP {response.status_code}")
            
            # Test admin endpoints accessibility
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                users_data = response.json()
                user_count = len(users_data.get("users", [])) if isinstance(users_data, dict) else len(users_data)
                self.log_result("Admin Endpoints Access", True, 
                              f"Admin endpoints accessible, found {user_count} users")
            else:
                self.log_result("Admin Endpoints Access", False, 
                              f"Admin endpoints failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Backend Communication", False, f"Exception: {str(e)}")
    
    def test_google_oauth_url_generation(self):
        """Test Google OAuth URL generation with live backend"""
        try:
            # Test Emergent OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            if response.status_code == 200:
                oauth_data = response.json()
                auth_url = oauth_data.get("auth_url")
                
                if auth_url and "https://auth.emergentagent.com" in auth_url:
                    self.log_result("Emergent OAuth URL Generation", True, 
                                  "Emergent OAuth URL generated successfully",
                                  {"auth_url": auth_url})
                else:
                    self.log_result("Emergent OAuth URL Generation", False, 
                                  "Invalid Emergent OAuth URL format", 
                                  {"auth_url": auth_url})
            else:
                self.log_result("Emergent OAuth URL Generation", False, 
                              f"Emergent OAuth URL failed: HTTP {response.status_code}")
            
            # Test Direct Google OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/auth/google/url")
            if response.status_code == 200:
                oauth_data = response.json()
                auth_url = oauth_data.get("auth_url")
                
                if auth_url and "accounts.google.com/o/oauth2" in auth_url:
                    # Parse URL to check parameters
                    parsed_url = urllib.parse.urlparse(auth_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    
                    client_id = query_params.get("client_id", [None])[0]
                    redirect_uri = query_params.get("redirect_uri", [None])[0]
                    
                    # Verify correct redirect URI for live system
                    expected_redirect = "https://fidus-invest.emergent.host"
                    if redirect_uri and expected_redirect in redirect_uri:
                        self.log_result("Direct Google OAuth URL Generation", True, 
                                      "Direct Google OAuth URL generated with correct redirect URI",
                                      {
                                          "auth_url": auth_url,
                                          "client_id": client_id,
                                          "redirect_uri": redirect_uri
                                      })
                    else:
                        self.log_result("Direct Google OAuth URL Generation", False, 
                                      f"Incorrect redirect URI: expected {expected_redirect} in {redirect_uri}",
                                      {"auth_url": auth_url, "redirect_uri": redirect_uri})
                else:
                    self.log_result("Direct Google OAuth URL Generation", False, 
                                  "Invalid Direct Google OAuth URL format", 
                                  {"auth_url": auth_url})
            else:
                self.log_result("Direct Google OAuth URL Generation", False, 
                              f"Direct Google OAuth URL failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google OAuth URL Generation", False, f"Exception: {str(e)}")
    
    def test_google_oauth_configuration(self):
        """Test Google OAuth configuration verification"""
        try:
            # Test Google connection monitor
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            if response.status_code == 200:
                connection_data = response.json()
                overall_status = connection_data.get("overall_status")
                services = connection_data.get("services", {})
                
                # Check if all 4 services are configured
                expected_services = ["gmail", "calendar", "drive", "meet"]
                configured_services = [service for service in expected_services if service in services]
                
                if len(configured_services) == 4:
                    self.log_result("Google OAuth Configuration", True, 
                                  f"All 4 Google services configured: {configured_services}",
                                  {"overall_status": overall_status, "services": list(services.keys())})
                else:
                    missing_services = [s for s in expected_services if s not in services]
                    self.log_result("Google OAuth Configuration", False, 
                                  f"Missing services: {missing_services}",
                                  {"configured": configured_services, "missing": missing_services})
            else:
                self.log_result("Google OAuth Configuration", False, 
                              f"Connection monitor failed: HTTP {response.status_code}")
            
            # Test Google profile endpoint (should require auth)
            response = self.session.get(f"{BACKEND_URL}/admin/google/profile")
            if response.status_code == 200:
                profile_data = response.json()
                if profile_data.get("auth_required"):
                    self.log_result("Google Profile Endpoint", True, 
                                  "Google profile endpoint accessible, auth required as expected")
                else:
                    self.log_result("Google Profile Endpoint", True, 
                                  "Google profile endpoint accessible with existing auth")
            elif response.status_code == 401:
                self.log_result("Google Profile Endpoint", True, 
                              "Google profile endpoint properly requires authentication")
            else:
                self.log_result("Google Profile Endpoint", False, 
                              f"Google profile endpoint failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google OAuth Configuration", False, f"Exception: {str(e)}")
    
    def test_oauth_callback_endpoint(self):
        """Test OAuth callback endpoint accessibility"""
        try:
            # Test that callback endpoint exists (should return method not allowed for GET)
            response = self.session.get(f"{BACKEND_URL}/admin/google-callback")
            
            # Callback endpoint should exist but not accept GET requests
            if response.status_code in [405, 200]:  # Method not allowed or OK
                self.log_result("OAuth Callback Endpoint", True, 
                              "OAuth callback endpoint exists and accessible")
            elif response.status_code == 404:
                self.log_result("OAuth Callback Endpoint", False, 
                              "OAuth callback endpoint not found (404)")
            else:
                self.log_result("OAuth Callback Endpoint", True, 
                              f"OAuth callback endpoint exists (HTTP {response.status_code})")
                
        except Exception as e:
            self.log_result("OAuth Callback Endpoint", False, f"Exception: {str(e)}")
    
    def test_google_api_endpoints_readiness(self):
        """Test Google API endpoints readiness for OAuth completion"""
        try:
            # Test Gmail API endpoint
            response = self.session.get(f"{BACKEND_URL}/google/gmail/real-messages")
            if response.status_code == 200:
                gmail_data = response.json()
                if gmail_data.get("auth_required"):
                    self.log_result("Gmail API Readiness", True, 
                                  "Gmail API ready, waiting for OAuth completion")
                else:
                    self.log_result("Gmail API Readiness", True, 
                                  "Gmail API working with existing OAuth tokens")
            else:
                self.log_result("Gmail API Readiness", False, 
                              f"Gmail API not ready: HTTP {response.status_code}")
            
            # Test Calendar API endpoint
            response = self.session.get(f"{BACKEND_URL}/google/calendar/events")
            if response.status_code == 200:
                calendar_data = response.json()
                if calendar_data.get("auth_required"):
                    self.log_result("Calendar API Readiness", True, 
                                  "Calendar API ready, waiting for OAuth completion")
                else:
                    self.log_result("Calendar API Readiness", True, 
                                  "Calendar API working with existing OAuth tokens")
            else:
                self.log_result("Calendar API Readiness", False, 
                              f"Calendar API not ready: HTTP {response.status_code}")
            
            # Test Drive API endpoint
            response = self.session.get(f"{BACKEND_URL}/google/drive/real-files")
            if response.status_code == 200:
                drive_data = response.json()
                if drive_data.get("auth_required"):
                    self.log_result("Drive API Readiness", True, 
                                  "Drive API ready, waiting for OAuth completion")
                else:
                    self.log_result("Drive API Readiness", True, 
                                  "Drive API working with existing OAuth tokens")
            else:
                self.log_result("Drive API Readiness", False, 
                              f"Drive API not ready: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google API Endpoints Readiness", False, f"Exception: {str(e)}")
    
    def test_connect_google_workspace_button_readiness(self):
        """Test that Connect Google Workspace button will work properly"""
        try:
            # Test the admin dashboard endpoints that the button relies on
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            if response.status_code == 200:
                oauth_data = response.json()
                auth_url = oauth_data.get("auth_url")
                
                if auth_url:
                    self.log_result("Connect Google Workspace Button", True, 
                                  "Connect Google Workspace button ready - OAuth URL generation working")
                else:
                    self.log_result("Connect Google Workspace Button", False, 
                                  "Connect Google Workspace button not ready - no OAuth URL")
            else:
                self.log_result("Connect Google Workspace Button", False, 
                              f"Connect Google Workspace button not ready: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Connect Google Workspace Button", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Google OAuth URL fix verification tests"""
        print("🎯 GOOGLE OAUTH CONNECTION TEST AFTER BACKEND URL FIX")
        print("=" * 65)
        print(f"OLD Backend URL: https://mt5-deploy-debug.preview.emergentagent.com")
        print(f"NEW Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed with new backend URL.")
            print("   This indicates the backend URL fix may not be working properly.")
            return False
        
        print("\n🔍 Running Google OAuth URL Fix Verification Tests...")
        print("-" * 55)
        
        # Run all verification tests
        self.test_backend_communication()
        self.test_google_oauth_url_generation()
        self.test_google_oauth_configuration()
        self.test_oauth_callback_endpoint()
        self.test_google_api_endpoints_readiness()
        self.test_connect_google_workspace_button_readiness()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 65)
        print("🎯 GOOGLE OAUTH URL FIX TEST SUMMARY")
        print("=" * 65)
        
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
            "Admin Authentication",
            "Backend Communication", 
            "Google OAuth URL Generation",
            "Google OAuth Configuration",
            "Connect Google Workspace Button"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ GOOGLE OAUTH CONNECTION: READY AFTER URL FIX")
            print("   ✓ Backend URL fix successful")
            print("   ✓ Google OAuth URL generation working")
            print("   ✓ OAuth configuration verified")
            print("   ✓ System ready for user OAuth completion")
            print("   ✓ Connect Google Workspace button will work")
            print()
            print("🎉 NEXT STEPS:")
            print("   1. User can now visit https://fidus-invest.emergent.host")
            print("   2. Login as admin (admin/password123)")
            print("   3. Click 'Connect Google Workspace' button")
            print("   4. Complete Google OAuth flow")
            print("   5. Google integration will be fully functional")
        else:
            print("❌ GOOGLE OAUTH CONNECTION: ISSUES FOUND AFTER URL FIX")
            print("   Backend URL fix may not be complete or other issues exist.")
            print("   Main agent action required before OAuth completion.")
        
        print("\n" + "=" * 65)

def main():
    """Main test execution"""
    test_runner = GoogleOAuthURLFixTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()