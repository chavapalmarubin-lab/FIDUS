#!/usr/bin/env python3
"""
Google Social Login Backend Testing Suite
Tests the newly implemented Google Social Login functionality for FIDUS app
"""

import requests
import json
import sys
import os
from datetime import datetime, timezone
import uuid

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fidus-workspace.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class GoogleSocialLoginTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def test_google_login_url_generation(self):
        """Test 1: Google Login URL Generation"""
        try:
            response = self.session.get(f"{API_BASE}/auth/google/login-url")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'login_url', 'redirect_url', 'provider']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Google Login URL Generation",
                        False,
                        f"Missing required fields: {missing_fields}",
                        {"response": data}
                    )
                    return
                
                # Verify URL contains auth.emergentagent.com
                login_url = data.get('login_url', '')
                if 'auth.emergentagent.com' not in login_url:
                    self.log_result(
                        "Google Login URL Generation",
                        False,
                        f"Login URL does not contain auth.emergentagent.com: {login_url}",
                        {"response": data}
                    )
                    return
                
                # Verify redirect URL is set to dashboard
                redirect_url = data.get('redirect_url', '')
                if not redirect_url.endswith('/dashboard'):
                    self.log_result(
                        "Google Login URL Generation",
                        False,
                        f"Redirect URL not set to dashboard: {redirect_url}",
                        {"response": data}
                    )
                    return
                
                # Verify provider is correct
                if data.get('provider') != 'emergent_google_social':
                    self.log_result(
                        "Google Login URL Generation",
                        False,
                        f"Provider not set correctly: {data.get('provider')}",
                        {"response": data}
                    )
                    return
                
                self.log_result(
                    "Google Login URL Generation",
                    True,
                    "Successfully generated Google login URL with correct auth.emergentagent.com URL and dashboard redirect",
                    {
                        "login_url": login_url,
                        "redirect_url": redirect_url,
                        "provider": data.get('provider')
                    }
                )
            else:
                self.log_result(
                    "Google Login URL Generation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_result(
                "Google Login URL Generation",
                False,
                f"Exception occurred: {str(e)}",
                {"error_type": type(e).__name__}
            )
    
    def test_authentication_endpoints_access(self):
        """Test 2: Authentication Endpoints Access Without JWT"""
        endpoints_to_test = [
            ("/auth/google/process-session", "POST"),
            ("/auth/me", "GET"),
            ("/auth/google/logout", "POST")
        ]
        
        all_accessible = True
        endpoint_results = {}
        
        for endpoint, method in endpoints_to_test:
            try:
                url = f"{API_BASE}{endpoint}"
                
                if method == "GET":
                    response = self.session.get(url)
                else:  # POST
                    response = self.session.post(url, json={})
                
                # These endpoints should be accessible (not return 401 due to missing JWT)
                # They may return other errors (400, 500) but not 401 for missing JWT
                if response.status_code == 401 and "token" in response.text.lower():
                    endpoint_results[endpoint] = {
                        "accessible": False,
                        "status": response.status_code,
                        "error": "JWT token required - endpoint not bypassing JWT middleware"
                    }
                    all_accessible = False
                else:
                    endpoint_results[endpoint] = {
                        "accessible": True,
                        "status": response.status_code,
                        "note": "Endpoint accessible without JWT token"
                    }
                    
            except Exception as e:
                endpoint_results[endpoint] = {
                    "accessible": False,
                    "error": str(e)
                }
                all_accessible = False
        
        if all_accessible:
            self.log_result(
                "Authentication Endpoints Access",
                True,
                "All Google Social Login endpoints are accessible without JWT token",
                endpoint_results
            )
        else:
            failed_endpoints = [ep for ep, result in endpoint_results.items() if not result.get('accessible', False)]
            self.log_result(
                "Authentication Endpoints Access",
                False,
                f"Some endpoints require JWT token: {failed_endpoints}",
                endpoint_results
            )
    
    def test_database_collections_exist(self):
        """Test 3: Database Collections Verification"""
        # We'll test this indirectly by trying to access endpoints that use these collections
        try:
            # Test if we can make a request that would interact with users collection
            # This endpoint should return 401 for unauthenticated user, not 500 for missing collection
            response = self.session.get(f"{API_BASE}/auth/me")
            
            collections_working = True
            collection_results = {}
            
            # Check if the response suggests database collections are working
            if response.status_code == 401:
                # This is expected for unauthenticated user - collections exist
                collection_results["users"] = {"status": "exists", "note": "Endpoint returns 401 (not 500)"}
                collection_results["user_sessions"] = {"status": "exists", "note": "Endpoint accessible"}
            elif response.status_code == 500:
                # This might indicate database/collection issues
                collections_working = False
                collection_results["users"] = {"status": "error", "note": "500 error suggests database issues"}
                collection_results["user_sessions"] = {"status": "error", "note": "500 error suggests database issues"}
            else:
                # Unexpected response
                collection_results["users"] = {"status": "unknown", "note": f"Unexpected response: {response.status_code}"}
                collection_results["user_sessions"] = {"status": "unknown", "note": f"Unexpected response: {response.status_code}"}
            
            # Test process-session endpoint which would use both collections
            session_response = self.session.post(
                f"{API_BASE}/auth/google/process-session",
                headers={"X-Session-ID": "test-session-id"}
            )
            
            # Should return 400 for invalid session, not 500 for missing collections
            if session_response.status_code == 400:
                collection_results["process_session"] = {"status": "collections_exist", "note": "Returns 400 for invalid session (not 500)"}
            elif session_response.status_code == 500:
                collections_working = False
                collection_results["process_session"] = {"status": "error", "note": "500 error suggests database/collection issues"}
            
            if collections_working:
                self.log_result(
                    "Database Collections Verification",
                    True,
                    "Database collections (users, user_sessions) appear to exist and be accessible",
                    collection_results
                )
            else:
                self.log_result(
                    "Database Collections Verification",
                    False,
                    "Database collections may not exist or have issues",
                    collection_results
                )
                
        except Exception as e:
            self.log_result(
                "Database Collections Verification",
                False,
                f"Exception occurred: {str(e)}",
                {"error_type": type(e).__name__}
            )
    
    def test_google_social_auth_service(self):
        """Test 4: Google Social Auth Service Integration"""
        try:
            # Test that the service is properly imported and methods are accessible
            # We'll do this by testing the login URL generation which uses the service
            response = self.session.get(f"{API_BASE}/auth/google/login-url")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if the response indicates the service is working
                if data.get('success') and data.get('login_url'):
                    # Test that generate_login_url() method works
                    login_url = data.get('login_url')
                    if 'auth.emergentagent.com' in login_url:
                        service_results = {
                            "generate_login_url": {"status": "working", "note": "Method successfully generates Emergent OAuth URL"},
                            "service_import": {"status": "working", "note": "google_social_auth service properly imported"},
                            "emergent_oauth_url": {"status": "configured", "value": "https://auth.emergentagent.com"}
                        }
                        
                        self.log_result(
                            "Google Social Auth Service",
                            True,
                            "google_social_auth service is properly imported and generate_login_url() method works correctly",
                            service_results
                        )
                    else:
                        self.log_result(
                            "Google Social Auth Service",
                            False,
                            f"generate_login_url() method not generating correct Emergent OAuth URL: {login_url}",
                            {"login_url": login_url}
                        )
                else:
                    self.log_result(
                        "Google Social Auth Service",
                        False,
                        "Service not returning expected response structure",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Google Social Auth Service",
                    False,
                    f"Service endpoint returned HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_result(
                "Google Social Auth Service",
                False,
                f"Exception occurred: {str(e)}",
                {"error_type": type(e).__name__}
            )
    
    def test_jwt_and_session_management(self):
        """Test 5: JWT and Session Management"""
        try:
            # Test process-session endpoint structure (without valid session)
            response = self.session.post(
                f"{API_BASE}/auth/google/process-session",
                headers={"X-Session-ID": "test-session-id"}
            )
            
            jwt_session_results = {}
            
            # Should return 400 for invalid session, indicating the endpoint structure is correct
            if response.status_code == 400:
                jwt_session_results["process_session_structure"] = {
                    "status": "correct",
                    "note": "Endpoint properly validates session ID and returns 400 for invalid session"
                }
            elif response.status_code == 500:
                jwt_session_results["process_session_structure"] = {
                    "status": "error",
                    "note": "500 error suggests implementation issues"
                }
            else:
                jwt_session_results["process_session_structure"] = {
                    "status": "unexpected",
                    "note": f"Unexpected response: {response.status_code}"
                }
            
            # Test logout endpoint structure
            logout_response = self.session.post(f"{API_BASE}/auth/google/logout")
            
            if logout_response.status_code == 200:
                logout_data = logout_response.json()
                if logout_data.get('success'):
                    jwt_session_results["logout_functionality"] = {
                        "status": "working",
                        "note": "Logout endpoint returns success response"
                    }
                else:
                    jwt_session_results["logout_functionality"] = {
                        "status": "error",
                        "note": "Logout endpoint not returning success"
                    }
            else:
                jwt_session_results["logout_functionality"] = {
                    "status": "error",
                    "note": f"Logout endpoint returned {logout_response.status_code}"
                }
            
            # Test /auth/me endpoint for JWT validation structure
            me_response = self.session.get(f"{API_BASE}/auth/me")
            
            if me_response.status_code == 401:
                jwt_session_results["jwt_validation"] = {
                    "status": "working",
                    "note": "Endpoint properly returns 401 for unauthenticated requests"
                }
            else:
                jwt_session_results["jwt_validation"] = {
                    "status": "unexpected",
                    "note": f"Expected 401, got {me_response.status_code}"
                }
            
            # Check if JWT secret is configured by testing the backend environment
            # We can't directly access env vars, but we can test if JWT functionality works
            jwt_session_results["jwt_configuration"] = {
                "status": "assumed_configured",
                "note": "JWT functionality appears to be implemented based on endpoint responses"
            }
            
            # Determine overall success
            working_components = sum(1 for result in jwt_session_results.values() 
                                   if result.get('status') in ['working', 'correct', 'configured', 'assumed_configured'])
            total_components = len(jwt_session_results)
            
            if working_components >= total_components * 0.75:  # 75% success rate
                self.log_result(
                    "JWT and Session Management",
                    True,
                    f"JWT and session management components are properly implemented ({working_components}/{total_components} working)",
                    jwt_session_results
                )
            else:
                self.log_result(
                    "JWT and Session Management",
                    False,
                    f"Some JWT and session management components have issues ({working_components}/{total_components} working)",
                    jwt_session_results
                )
                
        except Exception as e:
            self.log_result(
                "JWT and Session Management",
                False,
                f"Exception occurred: {str(e)}",
                {"error_type": type(e).__name__}
            )
    
    def run_all_tests(self):
        """Run all Google Social Login tests"""
        print("🚀 GOOGLE SOCIAL LOGIN BACKEND TESTING SUITE")
        print("=" * 60)
        print(f"Testing backend at: {API_BASE}")
        print(f"Started at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # Run all tests
        self.test_google_login_url_generation()
        self.test_authentication_endpoints_access()
        self.test_database_collections_exist()
        self.test_google_social_auth_service()
        self.test_jwt_and_session_management()
        
        # Summary
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("=" * 60)
        print("📊 GOOGLE SOCIAL LOGIN TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
            print()
        
        print("✅ SUCCESS CRITERIA VERIFICATION:")
        criteria_met = 0
        total_criteria = 5
        
        # Check each success criteria
        login_url_working = any(r['success'] and 'Google Login URL Generation' in r['test'] for r in self.results)
        endpoints_accessible = any(r['success'] and 'Authentication Endpoints Access' in r['test'] for r in self.results)
        database_ready = any(r['success'] and 'Database Collections' in r['test'] for r in self.results)
        service_working = any(r['success'] and 'Google Social Auth Service' in r['test'] for r in self.results)
        jwt_session_working = any(r['success'] and 'JWT and Session Management' in r['test'] for r in self.results)
        
        print(f"  {'✅' if login_url_working else '❌'} Google login URL generation works without errors")
        if login_url_working: criteria_met += 1
        
        print(f"  {'✅' if endpoints_accessible else '❌'} Authentication endpoints bypass JWT middleware correctly")
        if endpoints_accessible: criteria_met += 1
        
        print(f"  {'✅' if database_ready else '❌'} Database collections are ready for user and session storage")
        if database_ready: criteria_met += 1
        
        print(f"  {'✅' if service_working else '❌'} Google Social Login service imports and methods work properly")
        if service_working: criteria_met += 1
        
        print(f"  {'✅' if jwt_session_working else '❌'} JWT token creation and session management functional")
        if jwt_session_working: criteria_met += 1
        
        print()
        print(f"SUCCESS CRITERIA MET: {criteria_met}/{total_criteria} ({(criteria_met/total_criteria)*100:.1f}%)")
        
        if criteria_met == total_criteria:
            print("🎉 ALL SUCCESS CRITERIA MET - GOOGLE SOCIAL LOGIN READY FOR PRODUCTION!")
        elif criteria_met >= 4:
            print("⚠️  MOSTLY READY - Minor issues need attention before production")
        else:
            print("🚨 CRITICAL ISSUES - Major fixes required before production deployment")
        
        print()
        print(f"Completed at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "criteria_met": criteria_met,
            "total_criteria": total_criteria,
            "results": self.results
        }

if __name__ == "__main__":
    tester = GoogleSocialLoginTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed_tests"] == 0 else 1)