#!/usr/bin/env python3
"""
URGENT Google OAuth Connection Issue Testing - Live Application
Testing Google OAuth integration on https://fidus-invest.emergent.host/

Focus Areas:
1. Test Google OAuth endpoints on live system
2. Verify GOOGLE_OAUTH_REDIRECT_URI matches live domain  
3. Test Google OAuth URL generation
4. Check OAuth configuration errors
5. Test Google service account integration
6. Verify OAuth credentials validity
"""

import requests
import json
import sys
from datetime import datetime
import os
from urllib.parse import urlparse, parse_qs

# Live application URLs
LIVE_FRONTEND_URL = "https://fidus-invest.emergent.host"
BACKEND_URL_FROM_ENV = "https://trading-platform-76.preview.emergentagent.com/api"  # From frontend/.env
EXPECTED_BACKEND_URL = "https://fidus-invest.emergent.host/api"  # Expected for live app

class GoogleOAuthLiveTester:
    def __init__(self):
        self.results = []
        self.admin_token = None
        
    def log_result(self, test_name, success, details, critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        if critical and not success:
            status = "🚨 CRITICAL FAIL"
            
        result = {
            "test": test_name,
            "success": success,
            "status": status,
            "details": details,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        print()
        
    def authenticate_admin(self, backend_url):
        """Authenticate as admin to get JWT token"""
        try:
            login_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            response = requests.post(f"{backend_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as admin. Token obtained."
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False,
                    f"Failed to authenticate: {response.status_code} - {response.text}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False, 
                f"Authentication error: {str(e)}",
                critical=True
            )
            return False
    
    def get_auth_headers(self):
        """Get authorization headers with JWT token"""
        if not self.admin_token:
            return {}
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_backend_url_configuration(self):
        """Test backend URL configuration mismatch"""
        print("🔍 TESTING BACKEND URL CONFIGURATION")
        print("="*60)
        
        # Check frontend .env configuration
        frontend_backend_url = BACKEND_URL_FROM_ENV
        expected_backend_url = EXPECTED_BACKEND_URL
        
        if frontend_backend_url != expected_backend_url:
            self.log_result(
                "Backend URL Configuration",
                False,
                f"MISMATCH DETECTED! Frontend .env points to '{frontend_backend_url}' but live app should use '{expected_backend_url}'. This could cause Google OAuth redirect_uri_mismatch errors.",
                critical=True
            )
        else:
            self.log_result(
                "Backend URL Configuration", 
                True,
                f"Backend URL correctly configured: {expected_backend_url}"
            )
    
    def test_google_oauth_redirect_uri_configuration(self):
        """Test Google OAuth redirect URI configuration"""
        print("🔍 TESTING GOOGLE OAUTH REDIRECT URI CONFIGURATION")
        print("="*60)
        
        # Expected redirect URI for live application
        expected_redirect_uri = "https://fidus-invest.emergent.host/admin/google-callback"
        
        # Check backend .env configuration
        try:
            with open('/app/backend/.env', 'r') as f:
                env_content = f.read()
                
            if 'GOOGLE_OAUTH_REDIRECT_URI=' in env_content:
                # Extract the redirect URI
                for line in env_content.split('\n'):
                    if line.startswith('GOOGLE_OAUTH_REDIRECT_URI='):
                        configured_uri = line.split('=', 1)[1].strip('"')
                        
                        if configured_uri == expected_redirect_uri:
                            self.log_result(
                                "Google OAuth Redirect URI Configuration",
                                True,
                                f"Redirect URI correctly configured: {configured_uri}"
                            )
                        else:
                            self.log_result(
                                "Google OAuth Redirect URI Configuration",
                                False,
                                f"Redirect URI mismatch! Configured: '{configured_uri}', Expected: '{expected_redirect_uri}'. This will cause redirect_uri_mismatch errors.",
                                critical=True
                            )
                        break
            else:
                self.log_result(
                    "Google OAuth Redirect URI Configuration",
                    False,
                    "GOOGLE_OAUTH_REDIRECT_URI not found in backend .env file",
                    critical=True
                )
                
        except Exception as e:
            self.log_result(
                "Google OAuth Redirect URI Configuration",
                False,
                f"Error reading backend .env file: {str(e)}",
                critical=True
            )
    
    def test_google_oauth_url_generation(self, backend_url):
        """Test Google OAuth URL generation on live system"""
        print("🔍 TESTING GOOGLE OAUTH URL GENERATION")
        print("="*60)
        
        try:
            # Test Emergent OAuth service
            response = requests.get(
                f"{backend_url}/admin/google/auth-url",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                if 'accounts.google.com' in auth_url and 'client_id=' in auth_url:
                    # Parse the URL to check parameters
                    parsed_url = urlparse(auth_url)
                    query_params = parse_qs(parsed_url.query)
                    
                    client_id = query_params.get('client_id', [''])[0]
                    redirect_uri = query_params.get('redirect_uri', [''])[0]
                    
                    details = f"OAuth URL generated successfully. Client ID: {client_id[:20]}..., Redirect URI: {redirect_uri}"
                    
                    # Check if redirect URI matches live domain
                    if 'fidus-invest.emergent.host' in redirect_uri:
                        self.log_result(
                            "Google OAuth URL Generation (Emergent OAuth)",
                            True,
                            details
                        )
                    else:
                        self.log_result(
                            "Google OAuth URL Generation (Emergent OAuth)",
                            False,
                            f"{details} - WARNING: Redirect URI does not match live domain!",
                            critical=True
                        )
                else:
                    self.log_result(
                        "Google OAuth URL Generation (Emergent OAuth)",
                        False,
                        f"Invalid OAuth URL generated: {auth_url}",
                        critical=True
                    )
            else:
                self.log_result(
                    "Google OAuth URL Generation (Emergent OAuth)",
                    False,
                    f"Failed to generate OAuth URL: {response.status_code} - {response.text}",
                    critical=True
                )
                
        except Exception as e:
            self.log_result(
                "Google OAuth URL Generation (Emergent OAuth)",
                False,
                f"Error testing OAuth URL generation: {str(e)}",
                critical=True
            )
        
        # Test Direct Google OAuth
        try:
            response = requests.get(
                f"{backend_url}/auth/google/url",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url', '')
                
                if 'accounts.google.com' in auth_url:
                    parsed_url = urlparse(auth_url)
                    query_params = parse_qs(parsed_url.query)
                    
                    client_id = query_params.get('client_id', [''])[0]
                    redirect_uri = query_params.get('redirect_uri', [''])[0]
                    
                    details = f"Direct OAuth URL generated. Client ID: {client_id[:20]}..., Redirect URI: {redirect_uri}"
                    
                    if 'fidus-invest.emergent.host' in redirect_uri:
                        self.log_result(
                            "Google OAuth URL Generation (Direct OAuth)",
                            True,
                            details
                        )
                    else:
                        self.log_result(
                            "Google OAuth URL Generation (Direct OAuth)",
                            False,
                            f"{details} - WARNING: Redirect URI does not match live domain!",
                            critical=True
                        )
                else:
                    self.log_result(
                        "Google OAuth URL Generation (Direct OAuth)",
                        False,
                        f"Invalid direct OAuth URL: {auth_url}",
                        critical=True
                    )
            else:
                self.log_result(
                    "Google OAuth URL Generation (Direct OAuth)",
                    False,
                    f"Direct OAuth URL generation failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Google OAuth URL Generation (Direct OAuth)",
                False,
                f"Error testing direct OAuth URL: {str(e)}"
            )
    
    def test_google_connection_monitor(self, backend_url):
        """Test Google connection monitoring endpoints"""
        print("🔍 TESTING GOOGLE CONNECTION MONITOR")
        print("="*60)
        
        try:
            # Test connection monitor
            response = requests.get(
                f"{backend_url}/google/connection/test-all",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                overall_status = data.get('overall_status', 'unknown')
                services = data.get('services', {})
                
                working_services = sum(1 for service, status in services.items() if status.get('status') == 'connected')
                total_services = len(services)
                
                self.log_result(
                    "Google Connection Monitor",
                    True,
                    f"Connection monitor working. Overall status: {overall_status}, Services: {working_services}/{total_services} connected"
                )
            else:
                self.log_result(
                    "Google Connection Monitor",
                    False,
                    f"Connection monitor failed: {response.status_code} - {response.text}",
                    critical=True
                )
                
        except Exception as e:
            self.log_result(
                "Google Connection Monitor",
                False,
                f"Error testing connection monitor: {str(e)}",
                critical=True
            )
    
    def test_google_api_endpoints(self, backend_url):
        """Test Google API endpoints for authentication status"""
        print("🔍 TESTING GOOGLE API ENDPOINTS")
        print("="*60)
        
        # Test Gmail API
        try:
            response = requests.get(
                f"{backend_url}/google/gmail/real-messages",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Gmail API Integration",
                        True,
                        f"Gmail API working - retrieved {len(data.get('messages', []))} messages"
                    )
                else:
                    auth_required = data.get('auth_required', False)
                    if auth_required:
                        self.log_result(
                            "Gmail API Integration",
                            False,
                            "Gmail API requires Google authentication - OAuth not completed",
                            critical=True
                        )
                    else:
                        self.log_result(
                            "Gmail API Integration",
                            False,
                            f"Gmail API failed: {data.get('error', 'Unknown error')}",
                            critical=True
                        )
            else:
                self.log_result(
                    "Gmail API Integration",
                    False,
                    f"Gmail API endpoint failed: {response.status_code} - {response.text}",
                    critical=True
                )
                
        except Exception as e:
            self.log_result(
                "Gmail API Integration",
                False,
                f"Error testing Gmail API: {str(e)}",
                critical=True
            )
        
        # Test Calendar API
        try:
            response = requests.get(
                f"{backend_url}/google/calendar/events",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result(
                        "Calendar API Integration",
                        True,
                        f"Calendar API working - retrieved {len(data.get('events', []))} events"
                    )
                else:
                    auth_required = data.get('auth_required', False)
                    if auth_required:
                        self.log_result(
                            "Calendar API Integration",
                            False,
                            "Calendar API requires Google authentication - OAuth not completed",
                            critical=True
                        )
                    else:
                        self.log_result(
                            "Calendar API Integration",
                            False,
                            f"Calendar API failed: {data.get('error', 'Unknown error')}"
                        )
            else:
                self.log_result(
                    "Calendar API Integration",
                    False,
                    f"Calendar API endpoint failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Calendar API Integration",
                False,
                f"Error testing Calendar API: {str(e)}"
            )
    
    def test_backend_connectivity(self, backend_url):
        """Test basic backend connectivity"""
        print("🔍 TESTING BACKEND CONNECTIVITY")
        print("="*60)
        
        try:
            # Test health endpoint
            response = requests.get(f"{backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                self.log_result(
                    "Backend Health Check",
                    True,
                    f"Backend is healthy and accessible at {backend_url}"
                )
                return True
            else:
                self.log_result(
                    "Backend Health Check",
                    False,
                    f"Backend health check failed: {response.status_code} - {response.text}",
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Backend Health Check",
                False,
                f"Cannot connect to backend at {backend_url}: {str(e)}",
                critical=True
            )
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive Google OAuth testing"""
        print("🚨 URGENT: Google OAuth Connection Issue Testing - Live Application")
        print("="*80)
        print(f"Live Frontend: {LIVE_FRONTEND_URL}")
        print(f"Backend URL (from env): {BACKEND_URL_FROM_ENV}")
        print(f"Expected Backend URL: {EXPECTED_BACKEND_URL}")
        print("="*80)
        print()
        
        # Test 1: Backend URL Configuration
        self.test_backend_url_configuration()
        
        # Test 2: Google OAuth Redirect URI Configuration
        self.test_google_oauth_redirect_uri_configuration()
        
        # Test 3: Try to connect to the configured backend URL
        backend_accessible = self.test_backend_connectivity(BACKEND_URL_FROM_ENV)
        
        if backend_accessible:
            # Test 4: Authenticate as admin
            if self.authenticate_admin(BACKEND_URL_FROM_ENV):
                # Test 5: Google OAuth URL Generation
                self.test_google_oauth_url_generation(BACKEND_URL_FROM_ENV)
                
                # Test 6: Google Connection Monitor
                self.test_google_connection_monitor(BACKEND_URL_FROM_ENV)
                
                # Test 7: Google API Endpoints
                self.test_google_api_endpoints(BACKEND_URL_FROM_ENV)
        
        # Test with expected backend URL if different
        if BACKEND_URL_FROM_ENV != EXPECTED_BACKEND_URL:
            print("\n" + "="*80)
            print("🔄 TESTING WITH EXPECTED LIVE BACKEND URL")
            print("="*80)
            
            expected_accessible = self.test_backend_connectivity(EXPECTED_BACKEND_URL)
            
            if expected_accessible:
                if self.authenticate_admin(EXPECTED_BACKEND_URL):
                    self.test_google_oauth_url_generation(EXPECTED_BACKEND_URL)
                    self.test_google_connection_monitor(EXPECTED_BACKEND_URL)
                    self.test_google_api_endpoints(EXPECTED_BACKEND_URL)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("📊 GOOGLE OAUTH LIVE TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for r in self.results if not r['success'] and r.get('critical', False))
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Critical Failures: {critical_failures} 🚨")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show critical failures
        if critical_failures > 0:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            print("-" * 40)
            for result in self.results:
                if not result['success'] and result.get('critical', False):
                    print(f"❌ {result['test']}")
                    print(f"   {result['details']}")
                    print()
        
        # Show all failures
        if failed_tests > 0:
            print("❌ ALL FAILED TESTS:")
            print("-" * 40)
            for result in self.results:
                if not result['success']:
                    print(f"❌ {result['test']}")
                    print(f"   {result['details']}")
                    print()
        
        # Root cause analysis
        print("🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        # Check for URL mismatch
        url_mismatch = any('MISMATCH DETECTED' in r['details'] for r in self.results if not r['success'])
        redirect_uri_issue = any('redirect_uri_mismatch' in r['details'] or 'Redirect URI' in r['details'] for r in self.results if not r['success'])
        auth_required = any('auth_required' in r['details'] or 'authentication' in r['details'].lower() for r in self.results if not r['success'])
        
        if url_mismatch:
            print("🚨 CRITICAL: Backend URL mismatch detected!")
            print("   The frontend is configured to use a different backend URL than the live application.")
            print("   This will cause Google OAuth redirect_uri_mismatch errors.")
            print()
        
        if redirect_uri_issue:
            print("🚨 CRITICAL: Google OAuth redirect URI configuration issue!")
            print("   The redirect URI may not match the live domain configuration.")
            print("   This will prevent Google OAuth from working properly.")
            print()
        
        if auth_required:
            print("⚠️  Google APIs require OAuth authentication completion.")
            print("   Users need to complete the Google OAuth flow to access Google services.")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print("-" * 40)
        
        if url_mismatch:
            print("1. Update frontend/.env REACT_APP_BACKEND_URL to match live application")
            print("2. Ensure Google OAuth redirect URI matches live domain")
            print("3. Verify Google Console OAuth configuration")
        
        if redirect_uri_issue:
            print("4. Check Google Console OAuth 2.0 Client IDs configuration")
            print("5. Ensure redirect URI is added to authorized redirect URIs")
        
        if auth_required:
            print("6. Complete Google OAuth flow for admin user")
            print("7. Test end-to-end OAuth authentication process")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    tester = GoogleOAuthLiveTester()
    tester.run_comprehensive_test()