#!/usr/bin/env python3
"""
CRITICAL: Test Live Application Google OAuth After Supervisor Configuration Discovery

This script tests the actual live application to confirm if Google OAuth is working 
after identifying the supervisor configuration issue.

Live Application URL: https://fidus-invest.emergent.host/
"""

import requests
import json
import sys
from datetime import datetime
import urllib.parse

# Live Application Configuration
LIVE_BASE_URL = "https://fidus-invest.emergent.host"
LIVE_API_URL = f"{LIVE_BASE_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
    "user_type": "admin"
}

class LiveOAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        if critical and not success:
            status = "🚨 CRITICAL FAIL"
            
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        print()
        
    def test_live_backend_connectivity(self):
        """Test 1: Test Live Backend Directly"""
        print("=" * 80)
        print("TEST 1: LIVE BACKEND CONNECTIVITY")
        print("=" * 80)
        
        # Test basic health endpoint
        try:
            response = self.session.get(f"{LIVE_API_URL}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.log_test(
                    "Live Backend Health Check",
                    True,
                    f"Backend is healthy: {health_data.get('status', 'unknown')}",
                    critical=True
                )
            else:
                self.log_test(
                    "Live Backend Health Check",
                    False,
                    f"Health endpoint returned {response.status_code}: {response.text}",
                    critical=True
                )
                return False
        except Exception as e:
            self.log_test(
                "Live Backend Health Check",
                False,
                f"Failed to connect to live backend: {str(e)}",
                critical=True
            )
            return False
            
        # Test admin login
        try:
            response = self.session.post(
                f"{LIVE_API_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                login_data = response.json()
                self.admin_token = login_data.get('token')
                self.log_test(
                    "Admin Login on Live Backend",
                    True,
                    f"Successfully authenticated as admin, token received",
                    critical=True
                )
            else:
                self.log_test(
                    "Admin Login on Live Backend",
                    False,
                    f"Login failed with {response.status_code}: {response.text}",
                    critical=True
                )
                return False
        except Exception as e:
            self.log_test(
                "Admin Login on Live Backend",
                False,
                f"Login request failed: {str(e)}",
                critical=True
            )
            return False
            
        return True
        
    def test_google_oauth_url_generation(self):
        """Test 2: Test Google OAuth Configuration on Live"""
        print("=" * 80)
        print("TEST 2: GOOGLE OAUTH URL GENERATION ON LIVE")
        print("=" * 80)
        
        if not self.admin_token:
            self.log_test(
                "Google OAuth URL Generation",
                False,
                "No admin token available for authentication",
                critical=True
            )
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test Emergent OAuth URL generation
        try:
            response = self.session.get(
                f"{LIVE_API_URL}/admin/google/auth-url",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                oauth_data = response.json()
                auth_url = oauth_data.get('auth_url', '')
                
                if 'accounts.google.com' in auth_url and 'fidus-invest.emergent.host' in auth_url:
                    self.log_test(
                        "Emergent OAuth URL Generation",
                        True,
                        f"OAuth URL generated correctly with live domain: {auth_url[:100]}...",
                        critical=True
                    )
                else:
                    self.log_test(
                        "Emergent OAuth URL Generation",
                        False,
                        f"OAuth URL missing live domain or invalid: {auth_url}",
                        critical=True
                    )
            else:
                self.log_test(
                    "Emergent OAuth URL Generation",
                    False,
                    f"OAuth URL generation failed: {response.status_code} - {response.text}",
                    critical=True
                )
        except Exception as e:
            self.log_test(
                "Emergent OAuth URL Generation",
                False,
                f"OAuth URL request failed: {str(e)}",
                critical=True
            )
            
        # Test Direct Google OAuth URL generation
        try:
            response = self.session.get(
                f"{LIVE_API_URL}/auth/google/url",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                oauth_data = response.json()
                auth_url = oauth_data.get('auth_url', '')
                
                # Parse URL to check parameters
                parsed_url = urllib.parse.urlparse(auth_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                redirect_uri = query_params.get('redirect_uri', [''])[0]
                client_id = query_params.get('client_id', [''])[0]
                
                if 'fidus-invest.emergent.host' in redirect_uri:
                    self.log_test(
                        "Direct Google OAuth URL Generation",
                        True,
                        f"OAuth URL contains correct live redirect URI: {redirect_uri}",
                        critical=True
                    )
                else:
                    self.log_test(
                        "Direct Google OAuth URL Generation",
                        False,
                        f"OAuth URL has incorrect redirect URI: {redirect_uri}",
                        critical=True
                    )
                    
                if client_id:
                    self.log_test(
                        "Google Client ID Verification",
                        True,
                        f"Client ID present in OAuth URL: {client_id[:20]}...",
                        critical=False
                    )
                else:
                    self.log_test(
                        "Google Client ID Verification",
                        False,
                        "Client ID missing from OAuth URL",
                        critical=True
                    )
                    
            else:
                self.log_test(
                    "Direct Google OAuth URL Generation",
                    False,
                    f"Direct OAuth URL generation failed: {response.status_code} - {response.text}",
                    critical=True
                )
        except Exception as e:
            self.log_test(
                "Direct Google OAuth URL Generation",
                False,
                f"Direct OAuth URL request failed: {str(e)}",
                critical=True
            )
            
    def test_google_oauth_callback_accessibility(self):
        """Test 3: Google OAuth Callback Test"""
        print("=" * 80)
        print("TEST 3: GOOGLE OAUTH CALLBACK ACCESSIBILITY")
        print("=" * 80)
        
        # Test if OAuth callback endpoint is accessible
        callback_endpoints = [
            "/admin/google-callback",
            "/api/admin/google-callback",
            "/auth/google/callback"
        ]
        
        for endpoint in callback_endpoints:
            try:
                # Test with GET (should return method not allowed or redirect)
                response = self.session.get(f"{LIVE_BASE_URL}{endpoint}", timeout=10)
                
                if response.status_code in [200, 302, 405]:  # 405 = Method Not Allowed is expected
                    self.log_test(
                        f"OAuth Callback Endpoint Accessibility ({endpoint})",
                        True,
                        f"Endpoint accessible, returned {response.status_code}",
                        critical=False
                    )
                else:
                    self.log_test(
                        f"OAuth Callback Endpoint Accessibility ({endpoint})",
                        False,
                        f"Endpoint returned unexpected status {response.status_code}",
                        critical=False
                    )
            except Exception as e:
                self.log_test(
                    f"OAuth Callback Endpoint Accessibility ({endpoint})",
                    False,
                    f"Failed to access callback endpoint: {str(e)}",
                    critical=False
                )
                
    def test_environment_variable_verification(self):
        """Test 4: Environment Variable Verification"""
        print("=" * 80)
        print("TEST 4: ENVIRONMENT VARIABLE VERIFICATION")
        print("=" * 80)
        
        if not self.admin_token:
            self.log_test(
                "Environment Variable Verification",
                False,
                "No admin token available for verification",
                critical=True
            )
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test Google connection status to verify environment variables
        try:
            response = self.session.get(
                f"{LIVE_API_URL}/google/connection/test-all",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                connection_data = response.json()
                overall_status = connection_data.get('overall_status', 'unknown')
                services = connection_data.get('services', {})
                
                self.log_test(
                    "Google Connection Monitor",
                    True,
                    f"Connection monitor accessible, overall status: {overall_status}, services: {len(services)}",
                    critical=False
                )
                
                # Check if environment variables are properly loaded
                if services:
                    self.log_test(
                        "Google Environment Variables",
                        True,
                        f"Google services configured: {list(services.keys())}",
                        critical=True
                    )
                else:
                    self.log_test(
                        "Google Environment Variables",
                        False,
                        "No Google services configured - environment variables may be missing",
                        critical=True
                    )
            else:
                self.log_test(
                    "Google Connection Monitor",
                    False,
                    f"Connection monitor failed: {response.status_code} - {response.text}",
                    critical=True
                )
        except Exception as e:
            self.log_test(
                "Google Connection Monitor",
                False,
                f"Connection monitor request failed: {str(e)}",
                critical=True
            )
            
    def test_production_oauth_flow_readiness(self):
        """Test 5: Production OAuth Flow Test"""
        print("=" * 80)
        print("TEST 5: PRODUCTION OAUTH FLOW READINESS")
        print("=" * 80)
        
        if not self.admin_token:
            self.log_test(
                "Production OAuth Flow Readiness",
                False,
                "No admin token available for testing",
                critical=True
            )
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test Google profile endpoint (should indicate auth required)
        try:
            response = self.session.get(
                f"{LIVE_API_URL}/google/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                if profile_data.get('auth_required'):
                    self.log_test(
                        "Google Profile Endpoint",
                        True,
                        "Google profile endpoint correctly indicates authentication required",
                        critical=False
                    )
                else:
                    self.log_test(
                        "Google Profile Endpoint",
                        True,
                        "Google profile endpoint accessible - OAuth may already be completed",
                        critical=False
                    )
            else:
                self.log_test(
                    "Google Profile Endpoint",
                    False,
                    f"Google profile endpoint failed: {response.status_code} - {response.text}",
                    critical=False
                )
        except Exception as e:
            self.log_test(
                "Google Profile Endpoint",
                False,
                f"Google profile request failed: {str(e)}",
                critical=False
            )
            
        # Test Gmail API endpoint (should indicate auth required)
        try:
            response = self.session.get(
                f"{LIVE_API_URL}/google/gmail/real-messages",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                gmail_data = response.json()
                if gmail_data.get('auth_required'):
                    self.log_test(
                        "Gmail API Readiness",
                        True,
                        "Gmail API correctly indicates authentication required",
                        critical=True
                    )
                elif gmail_data.get('messages'):
                    self.log_test(
                        "Gmail API Readiness",
                        True,
                        f"Gmail API working - {len(gmail_data.get('messages', []))} messages retrieved",
                        critical=True
                    )
                else:
                    self.log_test(
                        "Gmail API Readiness",
                        False,
                        "Gmail API response format unexpected",
                        critical=True
                    )
            else:
                self.log_test(
                    "Gmail API Readiness",
                    False,
                    f"Gmail API failed: {response.status_code} - {response.text}",
                    critical=True
                )
        except Exception as e:
            self.log_test(
                "Gmail API Readiness",
                False,
                f"Gmail API request failed: {str(e)}",
                critical=True
            )
            
    def run_all_tests(self):
        """Run all live OAuth tests"""
        print("🚨 CRITICAL: Testing Live Application Google OAuth After Supervisor Configuration Discovery")
        print(f"Live Application URL: {LIVE_BASE_URL}")
        print(f"Testing at: {datetime.now().isoformat()}")
        print()
        
        # Run tests in sequence
        if not self.test_live_backend_connectivity():
            print("🚨 CRITICAL: Backend connectivity failed - cannot continue with OAuth tests")
            return self.generate_summary()
            
        self.test_google_oauth_url_generation()
        self.test_google_oauth_callback_accessibility()
        self.test_environment_variable_verification()
        self.test_production_oauth_flow_readiness()
        
        return self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("LIVE GOOGLE OAUTH TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        critical_failures = [result for result in self.test_results if result['critical'] and not result['success']]
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Critical Failures: {len(critical_failures)}")
        print()
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
            
        # Determine overall status
        if success_rate >= 90 and len(critical_failures) == 0:
            overall_status = "✅ GOOGLE OAUTH READY FOR PRODUCTION"
        elif success_rate >= 70 and len(critical_failures) <= 1:
            overall_status = "⚠️ GOOGLE OAUTH MOSTLY READY - MINOR ISSUES"
        else:
            overall_status = "❌ GOOGLE OAUTH NOT READY - CRITICAL ISSUES"
            
        print(f"OVERALL STATUS: {overall_status}")
        print()
        
        return {
            "overall_status": overall_status,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "critical_failures": len(critical_failures),
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = LiveOAuthTester()
    summary = tester.run_all_tests()
    
    # Save results to file
    with open('/app/live_oauth_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
        
    print(f"Detailed results saved to: /app/live_oauth_test_results.json")
    
    # Exit with appropriate code
    if summary['success_rate'] >= 90 and summary['critical_failures'] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()