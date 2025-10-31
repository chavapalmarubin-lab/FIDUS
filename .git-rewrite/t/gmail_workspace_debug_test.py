#!/usr/bin/env python3
"""
GMAIL API WORKSPACE TAB DEBUG TEST
=================================

This test specifically debugs the Gmail API integration failing in the Google Workspace tab
as requested in the review:

**Issue**: User successfully connected to Google OAuth and can send emails/schedule meetings 
through CRM, but the Gmail section in Google Workspace tab shows "No emails returned from 
Gmail API, using fallback" repeatedly.

**What to debug**:
1. Test Gmail API endpoint `/api/google/gmail/real-messages` that the Google Workspace tab calls
2. Check authentication tokens - Verify if Gmail API has proper auth tokens  
3. Test Gmail API response format - Check what the Gmail endpoint actually returns
4. Debug Gmail API scopes - Verify Gmail read permissions are granted
5. Check for Gmail API errors - Look for specific error messages in Gmail API calls

**Admin Credentials**: admin/password123
**Backend URL**: Use REACT_APP_BACKEND_URL from frontend/.env
"""

import requests
import json
import sys
from datetime import datetime
import time

# Backend URL Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GmailWorkspaceDebugTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result with detailed information"""
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
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user to get JWT token"""
        try:
            print("🔐 Authenticating as admin user...")
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                jwt_token = data.get("token")
                if jwt_token:
                    self.admin_token = jwt_token
                    self.session.headers.update({"Authorization": f"Bearer {jwt_token}"})
                    self.log_result("Admin Authentication", True, 
                                  f"Successfully authenticated as {data.get('name', 'admin')}")
                    return True
                else:
                    self.log_result("Admin Authentication", False, 
                                  "Login successful but no JWT token received", data)
                    return False
            else:
                self.log_result("Admin Authentication", False, 
                              f"Login failed with HTTP {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception during authentication: {str(e)}")
            return False

    def test_gmail_api_endpoint(self):
        """Test the specific Gmail API endpoint that Google Workspace tab calls"""
        try:
            print("📧 Testing Gmail API endpoint `/api/google/gmail/real-messages`...")
            
            if not self.admin_token:
                self.log_result("Gmail API Endpoint Test", False, 
                              "Cannot test - no admin authentication token")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/google/gmail/real-messages")
            
            self.log_result("Gmail API Endpoint Test", True, 
                          f"Gmail API endpoint responded with HTTP {response.status_code}",
                          {
                              "status_code": response.status_code,
                              "headers": dict(response.headers),
                              "response_text": response.text[:500] + "..." if len(response.text) > 500 else response.text
                          })
            
            # Try to parse JSON response
            try:
                data = response.json()
                return self.analyze_gmail_response(data, response.status_code)
            except json.JSONDecodeError:
                self.log_result("Gmail API Response Format", False, 
                              "Gmail API returned non-JSON response", 
                              {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_result("Gmail API Endpoint Test", False, f"Exception: {str(e)}")
            return False

    def analyze_gmail_response(self, data, status_code):
        """Analyze the Gmail API response in detail"""
        try:
            print("🔍 Analyzing Gmail API response...")
            
            # Check response structure
            success = data.get("success")
            auth_required = data.get("auth_required")
            messages = data.get("messages")
            error = data.get("error")
            source = data.get("source")
            
            analysis = {
                "success": success,
                "auth_required": auth_required,
                "messages_count": len(messages) if messages else 0,
                "error": error,
                "source": source,
                "response_keys": list(data.keys())
            }
            
            # Determine the issue based on response
            if auth_required is True:
                self.log_result("Gmail API Authentication Check", False, 
                              "Gmail API requires Google authentication - OAuth tokens missing or invalid",
                              analysis)
                return self.check_google_oauth_status()
            elif success is True and messages:
                self.log_result("Gmail API Response Analysis", True, 
                              f"Gmail API working correctly - returned {len(messages)} messages",
                              analysis)
                return True
            elif success is False and error:
                self.log_result("Gmail API Response Analysis", False, 
                              f"Gmail API returned error: {error}",
                              analysis)
                return False
            else:
                self.log_result("Gmail API Response Analysis", False, 
                              "Gmail API response format unexpected",
                              analysis)
                return False
                
        except Exception as e:
            self.log_result("Gmail API Response Analysis", False, f"Exception: {str(e)}")
            return False

    def check_google_oauth_status(self):
        """Check Google OAuth authentication status"""
        try:
            print("🔗 Checking Google OAuth authentication status...")
            
            # Test Google connection status
            response = self.session.get(f"{BACKEND_URL}/google/connection/test-all")
            
            if response.status_code == 200:
                data = response.json()
                overall_status = data.get("overall_status")
                services = data.get("services", {})
                gmail_status = services.get("gmail", {})
                
                oauth_analysis = {
                    "overall_status": overall_status,
                    "gmail_service_status": gmail_status.get("status"),
                    "gmail_response_time": gmail_status.get("response_time_ms"),
                    "gmail_error": gmail_status.get("error"),
                    "all_services": list(services.keys())
                }
                
                if gmail_status.get("status") == "connected":
                    self.log_result("Google OAuth Status Check", False, 
                                  "Google connection monitor shows Gmail as connected, but Gmail API requires auth - token mismatch issue",
                                  oauth_analysis)
                else:
                    self.log_result("Google OAuth Status Check", True, 
                                  f"Google OAuth not completed - Gmail status: {gmail_status.get('status', 'unknown')}",
                                  oauth_analysis)
                
                return self.test_oauth_url_generation()
            else:
                self.log_result("Google OAuth Status Check", False, 
                              f"Google connection status endpoint failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Google OAuth Status Check", False, f"Exception: {str(e)}")
            return False

    def test_oauth_url_generation(self):
        """Test Google OAuth URL generation"""
        try:
            print("🌐 Testing Google OAuth URL generation...")
            
            # Test direct Google OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/auth/google/url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url")
                
                if auth_url and "accounts.google.com" in auth_url:
                    # Check OAuth URL parameters
                    oauth_params = {
                        "has_client_id": "client_id=" in auth_url,
                        "has_redirect_uri": "redirect_uri=" in auth_url,
                        "has_scope": "scope=" in auth_url,
                        "has_gmail_scope": "gmail" in auth_url,
                        "has_response_type": "response_type=code" in auth_url
                    }
                    
                    self.log_result("OAuth URL Generation", True, 
                                  "Google OAuth URL generated successfully",
                                  {
                                      "auth_url_length": len(auth_url),
                                      "oauth_params": oauth_params,
                                      "auth_url_preview": auth_url[:100] + "..."
                                  })
                    
                    return self.check_gmail_scopes(auth_url)
                else:
                    self.log_result("OAuth URL Generation", False, 
                                  "Invalid OAuth URL generated",
                                  {"response": data})
                    return False
            else:
                self.log_result("OAuth URL Generation", False, 
                              f"OAuth URL generation failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("OAuth URL Generation", False, f"Exception: {str(e)}")
            return False

    def check_gmail_scopes(self, auth_url):
        """Check if Gmail scopes are properly configured in OAuth URL"""
        try:
            print("🔍 Checking Gmail API scopes in OAuth URL...")
            
            # Check for Gmail-specific scopes
            gmail_scopes = {
                "gmail_readonly": "gmail.readonly" in auth_url,
                "gmail_send": "gmail.send" in auth_url,
                "gmail_modify": "gmail.modify" in auth_url,
                "gmail_compose": "gmail.compose" in auth_url
            }
            
            has_gmail_scopes = any(gmail_scopes.values())
            
            if has_gmail_scopes:
                self.log_result("Gmail API Scopes Check", True, 
                              "Gmail API scopes found in OAuth URL",
                              {"gmail_scopes": gmail_scopes})
            else:
                self.log_result("Gmail API Scopes Check", False, 
                              "No Gmail API scopes found in OAuth URL - this could cause Gmail API failures",
                              {"gmail_scopes": gmail_scopes})
            
            return self.test_alternative_gmail_endpoints()
            
        except Exception as e:
            self.log_result("Gmail API Scopes Check", False, f"Exception: {str(e)}")
            return False

    def test_alternative_gmail_endpoints(self):
        """Test alternative Gmail endpoints to identify working vs failing ones"""
        try:
            print("🔄 Testing alternative Gmail endpoints...")
            
            gmail_endpoints = [
                "/google/gmail/real-messages",
                "/admin/gmail/messages", 
                "/google/gmail/messages",
                "/admin/google/gmail/messages"
            ]
            
            endpoint_results = {}
            
            for endpoint in gmail_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    try:
                        data = response.json()
                        endpoint_results[endpoint] = {
                            "status_code": response.status_code,
                            "success": data.get("success"),
                            "auth_required": data.get("auth_required"),
                            "error": data.get("error"),
                            "messages_count": len(data.get("messages", []))
                        }
                    except json.JSONDecodeError:
                        endpoint_results[endpoint] = {
                            "status_code": response.status_code,
                            "json_error": True,
                            "response_text": response.text[:100]
                        }
                        
                except Exception as e:
                    endpoint_results[endpoint] = {
                        "error": str(e)
                    }
            
            # Find working endpoints
            working_endpoints = [ep for ep, result in endpoint_results.items() 
                               if result.get("status_code") == 200]
            
            if working_endpoints:
                self.log_result("Alternative Gmail Endpoints", True, 
                              f"Found {len(working_endpoints)} working Gmail endpoints",
                              {"endpoint_results": endpoint_results})
            else:
                self.log_result("Alternative Gmail Endpoints", False, 
                              "No working Gmail endpoints found",
                              {"endpoint_results": endpoint_results})
            
            return self.check_backend_logs()
            
        except Exception as e:
            self.log_result("Alternative Gmail Endpoints", False, f"Exception: {str(e)}")
            return False

    def check_backend_logs(self):
        """Check for backend logs or error indicators"""
        try:
            print("📋 Checking for backend error indicators...")
            
            # Test health endpoint to see if backend is healthy
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Backend Health Check", True, 
                              f"Backend is healthy: {data.get('status')}",
                              {"health_data": data})
            else:
                self.log_result("Backend Health Check", False, 
                              f"Backend health check failed: HTTP {response.status_code}",
                              {"response": response.text})
            
            return True
            
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Exception: {str(e)}")
            return False

    def run_debug_test(self):
        """Run the complete Gmail API debug test"""
        print("🚨 GMAIL API WORKSPACE TAB DEBUG TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Issue: Gmail section in Google Workspace tab shows 'No emails returned from Gmail API, using fallback'")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test Gmail API endpoint
        self.test_gmail_api_endpoint()
        
        # Generate summary
        self.generate_debug_summary()
        
        return True

    def generate_debug_summary(self):
        """Generate debug summary with actionable recommendations"""
        print("\n" + "=" * 60)
        print("🎯 GMAIL API DEBUG SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Debug Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print()
        
        # Show all test results
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print("\n" + "🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        # Analyze the results to determine root cause
        auth_failed = any("Authentication" in r['test'] and not r['success'] for r in self.test_results)
        gmail_auth_required = any("auth_required" in str(r.get('details', {})) for r in self.test_results)
        oauth_issues = any("OAuth" in r['test'] and not r['success'] for r in self.test_results)
        scope_issues = any("Scopes" in r['test'] and not r['success'] for r in self.test_results)
        
        if auth_failed:
            print("❌ CRITICAL: Admin authentication is failing")
            print("   → Fix admin login credentials or JWT token generation")
        elif gmail_auth_required:
            print("🎯 ROOT CAUSE IDENTIFIED: Gmail API requires Google OAuth authentication")
            print("   → User needs to complete Google OAuth flow to connect Gmail")
            print("   → The 'No emails returned from Gmail API, using fallback' message occurs because:")
            print("     1. Gmail API endpoint returns auth_required=true")
            print("     2. Frontend shows fallback message instead of real Gmail data")
            print("     3. Google OAuth connection has not been completed")
        elif oauth_issues:
            print("❌ ISSUE: Google OAuth URL generation or configuration problems")
            print("   → Check Google OAuth client configuration")
        elif scope_issues:
            print("❌ ISSUE: Gmail API scopes not properly configured")
            print("   → Add gmail.readonly and gmail.send scopes to OAuth configuration")
        else:
            print("✅ Gmail API infrastructure appears to be working correctly")
            print("   → Issue may be in frontend integration or user OAuth completion")
        
        print("\n" + "💡 RECOMMENDED ACTIONS:")
        print("-" * 40)
        print("1. User should visit Google Workspace tab and click 'Connect Google Workspace'")
        print("2. Complete Google OAuth flow by granting Gmail permissions")
        print("3. After OAuth completion, Gmail API should return real messages instead of fallback")
        print("4. If OAuth is already completed, check for token expiration or refresh issues")
        
        print("\n" + "=" * 60)

def main():
    """Main debug test execution"""
    test_runner = GmailWorkspaceDebugTest()
    success = test_runner.run_debug_test()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()