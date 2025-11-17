#!/usr/bin/env python3
"""
Google Workspace API Testing - Critical OAuth Endpoints Verification

Context:
Testing all Google Workspace OAuth endpoints to verify Calendar, Drive, and Sheets APIs 
are working correctly after recent fixes.

Backend URL: https://alloc-wizard.preview.emergentagent.com/api
Auth: Admin token (login with username: admin, password: password123)

Test Endpoints:
1. Calendar Endpoint - /api/admin/google/calendar/events
2. Drive Endpoint - /api/admin/google/drive/files  
3. Sheets Endpoint (NEW) - /api/admin/google/sheets/spreadsheets

Success Criteria:
- All 3 endpoints should return HTTP 200, 401 (auth required), or 500 (proper error)
- Response should have proper JSON structure with "success" field
- Error messages should be clear and actionable
- No 404 errors (endpoint not found)

Note: Since Google OAuth is not connected, we expect proper authentication error responses, NOT 404 errors.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://alloc-wizard.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class GoogleWorkspaceAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details, http_status=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "http_status": http_status,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if http_status:
            print(f"   HTTP Status: {http_status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate(self):
        """Authenticate as admin and get JWT token"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}", 200)
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", response.status_code)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Authentication failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_google_calendar_endpoint(self):
        """Test Google Calendar Endpoint - /api/admin/google/calendar/events"""
        try:
            url = f"{BACKEND_URL}/api/admin/google/calendar/events"
            response = self.session.get(url)
            
            # Check for 404 (endpoint not found) - this is a FAIL
            if response.status_code == 404:
                self.log_test("Calendar Endpoint Exists", False, "Endpoint returns 404 - endpoint not implemented", 404)
                return False
            
            # Expected responses: 200 (success), 401 (auth required), 500 (proper error)
            if response.status_code in [200, 401, 500]:
                try:
                    data = response.json()
                    
                    # Check for proper JSON structure
                    if isinstance(data, dict):
                        # Check for success field or error structure
                        has_success_field = 'success' in data
                        has_error_field = 'error' in data or 'message' in data
                        
                        if has_success_field or has_error_field:
                            if response.status_code == 200:
                                self.log_test("Calendar Endpoint Response", True, f"Valid response structure with success field", 200)
                            elif response.status_code == 401:
                                self.log_test("Calendar Endpoint Response", True, f"Proper auth error response: {data.get('message', 'Auth required')}", 401)
                            else:  # 500
                                error_msg = data.get('message', data.get('error', 'Internal server error'))
                                if 'oauth' in error_msg.lower() or 'google' in error_msg.lower() or 'token' in error_msg.lower():
                                    self.log_test("Calendar Endpoint Response", True, f"Proper Google OAuth error: {error_msg}", 500)
                                else:
                                    self.log_test("Calendar Endpoint Response", True, f"Server error with clear message: {error_msg}", 500)
                            return True
                        else:
                            self.log_test("Calendar Endpoint Response", False, f"Response missing success/error fields: {data}", response.status_code)
                            return False
                    else:
                        self.log_test("Calendar Endpoint Response", False, f"Invalid JSON structure: {data}", response.status_code)
                        return False
                        
                except json.JSONDecodeError:
                    self.log_test("Calendar Endpoint Response", False, f"Invalid JSON response: {response.text[:200]}", response.status_code)
                    return False
            else:
                self.log_test("Calendar Endpoint Response", False, f"Unexpected HTTP status: {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Calendar Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_google_drive_endpoint(self):
        """Test Google Drive Endpoint - /api/admin/google/drive/files"""
        try:
            url = f"{BACKEND_URL}/api/admin/google/drive/files"
            response = self.session.get(url)
            
            # Check for 404 (endpoint not found) - this is a FAIL
            if response.status_code == 404:
                self.log_test("Drive Endpoint Exists", False, "Endpoint returns 404 - endpoint not implemented", 404)
                return False
            
            # Expected responses: 200 (success), 401 (auth required), 500 (proper error)
            if response.status_code in [200, 401, 500]:
                try:
                    data = response.json()
                    
                    # Check for proper JSON structure
                    if isinstance(data, dict):
                        # Check for success field or error structure
                        has_success_field = 'success' in data
                        has_error_field = 'error' in data or 'message' in data
                        
                        if has_success_field or has_error_field:
                            if response.status_code == 200:
                                self.log_test("Drive Endpoint Response", True, f"Valid response structure with success field", 200)
                            elif response.status_code == 401:
                                self.log_test("Drive Endpoint Response", True, f"Proper auth error response: {data.get('message', 'Auth required')}", 401)
                            else:  # 500
                                error_msg = data.get('message', data.get('error', 'Internal server error'))
                                if 'oauth' in error_msg.lower() or 'google' in error_msg.lower() or 'token' in error_msg.lower():
                                    self.log_test("Drive Endpoint Response", True, f"Proper Google OAuth error: {error_msg}", 500)
                                else:
                                    self.log_test("Drive Endpoint Response", True, f"Server error with clear message: {error_msg}", 500)
                            return True
                        else:
                            self.log_test("Drive Endpoint Response", False, f"Response missing success/error fields: {data}", response.status_code)
                            return False
                    else:
                        self.log_test("Drive Endpoint Response", False, f"Invalid JSON structure: {data}", response.status_code)
                        return False
                        
                except json.JSONDecodeError:
                    self.log_test("Drive Endpoint Response", False, f"Invalid JSON response: {response.text[:200]}", response.status_code)
                    return False
            else:
                self.log_test("Drive Endpoint Response", False, f"Unexpected HTTP status: {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Drive Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_google_sheets_endpoint(self):
        """Test Google Sheets Endpoint (NEW) - /api/admin/google/sheets/spreadsheets"""
        try:
            url = f"{BACKEND_URL}/api/admin/google/sheets/spreadsheets"
            response = self.session.get(url)
            
            # Check for 404 (endpoint not found) - this is a FAIL
            if response.status_code == 404:
                self.log_test("Sheets Endpoint Exists", False, "Endpoint returns 404 - endpoint not implemented", 404)
                return False
            
            # Expected responses: 200 (success), 401 (auth required), 500 (proper error)
            if response.status_code in [200, 401, 500]:
                try:
                    data = response.json()
                    
                    # Check for proper JSON structure
                    if isinstance(data, dict):
                        # Check for success field or error structure
                        has_success_field = 'success' in data
                        has_error_field = 'error' in data or 'message' in data
                        
                        if has_success_field or has_error_field:
                            if response.status_code == 200:
                                self.log_test("Sheets Endpoint Response", True, f"Valid response structure with success field", 200)
                            elif response.status_code == 401:
                                self.log_test("Sheets Endpoint Response", True, f"Proper auth error response: {data.get('message', 'Auth required')}", 401)
                            else:  # 500
                                error_msg = data.get('message', data.get('error', 'Internal server error'))
                                if 'oauth' in error_msg.lower() or 'google' in error_msg.lower() or 'token' in error_msg.lower():
                                    self.log_test("Sheets Endpoint Response", True, f"Proper Google OAuth error: {error_msg}", 500)
                                else:
                                    self.log_test("Sheets Endpoint Response", True, f"Server error with clear message: {error_msg}", 500)
                            return True
                        else:
                            self.log_test("Sheets Endpoint Response", False, f"Response missing success/error fields: {data}", response.status_code)
                            return False
                    else:
                        self.log_test("Sheets Endpoint Response", False, f"Invalid JSON structure: {data}", response.status_code)
                        return False
                        
                except json.JSONDecodeError:
                    self.log_test("Sheets Endpoint Response", False, f"Invalid JSON response: {response.text[:200]}", response.status_code)
                    return False
            else:
                self.log_test("Sheets Endpoint Response", False, f"Unexpected HTTP status: {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Sheets Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_google_workspace_tests(self):
        """Run complete Google Workspace API testing"""
        print("🔍 GOOGLE WORKSPACE API TESTING - CRITICAL OAUTH ENDPOINTS VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        print("📋 STEP 1: Authenticate as Admin")
        if not self.authenticate():
            print("❌ Authentication failed. Cannot test Google endpoints.")
            return False
        print()
        
        # Step 2: Test Calendar Endpoint
        print("📋 STEP 2: Test Google Calendar Endpoint")
        print("Testing /api/admin/google/calendar/events...")
        calendar_success = self.test_google_calendar_endpoint()
        print()
        
        # Step 3: Test Drive Endpoint
        print("📋 STEP 3: Test Google Drive Endpoint")
        print("Testing /api/admin/google/drive/files...")
        drive_success = self.test_google_drive_endpoint()
        print()
        
        # Step 4: Test Sheets Endpoint (NEW)
        print("📋 STEP 4: Test Google Sheets Endpoint (NEW)")
        print("Testing /api/admin/google/sheets/spreadsheets...")
        sheets_success = self.test_google_sheets_endpoint()
        print()
        
        # Summary
        self.print_test_summary()
        
        # Return overall success - all 3 endpoints must be accessible (not 404)
        return calendar_success and drive_success and sheets_success
    
    def print_test_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 GOOGLE WORKSPACE API TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    status_info = f" (HTTP {result['http_status']})" if result.get('http_status') else ""
                    print(f"   • {result['test']}{status_info}: {result['details']}")
            print()
        
        print("✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result['success']:
                status_info = f" (HTTP {result['http_status']})" if result.get('http_status') else ""
                print(f"   • {result['test']}{status_info}: {result['details']}")
        print()
        
        # Endpoint-specific results
        print("🔍 ENDPOINT VERIFICATION RESULTS:")
        
        # Calendar Endpoint
        calendar_success = any('Calendar Endpoint' in r['test'] and r['success'] for r in self.test_results)
        calendar_404 = any('Calendar Endpoint' in r['test'] and r.get('http_status') == 404 for r in self.test_results)
        
        print(f"   📅 Calendar Endpoint (/api/admin/google/calendar/events):")
        if calendar_404:
            print(f"     ❌ CRITICAL: Returns 404 - endpoint not implemented")
        elif calendar_success:
            print(f"     ✅ Accessible with proper error handling")
        else:
            print(f"     ❌ Issues with response structure or error handling")
        
        # Drive Endpoint
        drive_success = any('Drive Endpoint' in r['test'] and r['success'] for r in self.test_results)
        drive_404 = any('Drive Endpoint' in r['test'] and r.get('http_status') == 404 for r in self.test_results)
        
        print(f"   📁 Drive Endpoint (/api/admin/google/drive/files):")
        if drive_404:
            print(f"     ❌ CRITICAL: Returns 404 - endpoint not implemented")
        elif drive_success:
            print(f"     ✅ Accessible with proper error handling")
        else:
            print(f"     ❌ Issues with response structure or error handling")
        
        # Sheets Endpoint
        sheets_success = any('Sheets Endpoint' in r['test'] and r['success'] for r in self.test_results)
        sheets_404 = any('Sheets Endpoint' in r['test'] and r.get('http_status') == 404 for r in self.test_results)
        
        print(f"   📊 Sheets Endpoint (/api/admin/google/sheets/spreadsheets):")
        if sheets_404:
            print(f"     ❌ CRITICAL: Returns 404 - endpoint not implemented")
        elif sheets_success:
            print(f"     ✅ Accessible with proper error handling")
        else:
            print(f"     ❌ Issues with response structure or error handling")
        
        print()
        print("🎯 SUCCESS CRITERIA EVALUATION:")
        
        # Overall status
        all_endpoints_accessible = calendar_success and drive_success and sheets_success
        no_404_errors = not (calendar_404 or drive_404 or sheets_404)
        
        print(f"   {'✅' if all_endpoints_accessible else '❌'} All 3 endpoints accessible (no 404 errors)")
        print(f"   {'✅' if no_404_errors else '❌'} No missing endpoint implementations")
        
        # Check for proper error responses
        proper_auth_errors = any('Proper auth error' in r['details'] for r in self.test_results if r['success'])
        proper_oauth_errors = any('Proper Google OAuth error' in r['details'] for r in self.test_results if r['success'])
        
        print(f"   {'✅' if proper_auth_errors or proper_oauth_errors else '❌'} Proper authentication/OAuth error responses")
        
        # JSON structure validation
        valid_json_responses = any('Valid response structure' in r['details'] for r in self.test_results if r['success'])
        
        print(f"   {'✅' if valid_json_responses else '❌'} Valid JSON response structures")
        
        print()
        print("📋 FINAL ASSESSMENT:")
        
        if all_endpoints_accessible and no_404_errors:
            print("   ✅ SUCCESS: All Google Workspace API endpoints are properly implemented")
            print("   🎉 Calendar, Drive, and Sheets APIs are accessible with proper error handling")
            print("   📝 Expected behavior: OAuth authentication errors (not 404 endpoint errors)")
        else:
            print("   ❌ ISSUES FOUND: Some Google Workspace API endpoints have problems")
            
            if calendar_404:
                print("   🔧 Calendar endpoint needs implementation")
            if drive_404:
                print("   🔧 Drive endpoint needs implementation")
            if sheets_404:
                print("   🔧 Sheets endpoint needs implementation")
        
        print()

def main():
    """Main test execution"""
    tester = GoogleWorkspaceAPITester()
    success = tester.run_google_workspace_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()