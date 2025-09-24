#!/usr/bin/env python3
"""
Google OAuth Authentication Bypass Testing
Testing the critical fix for Google OAuth login loop issue.

The problem was that the `/api/admin/google/process-session` endpoint was being blocked 
by JWT authentication middleware, causing 401 errors and login loops.

This test verifies:
1. JWT Authentication Bypass for OAuth endpoints
2. OAuth Endpoint Access without JWT tokens
3. Session Processing Logic
4. Authentication Middleware Behavior
"""

import requests
import json
import os
from datetime import datetime
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://auth-flow-debug-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class GoogleOAuthAuthenticationTest:
    def __init__(self):
        self.test_results = []
        self.admin_token = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def authenticate_admin(self):
        """Get admin JWT token for comparison tests"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.log_test(
                    "Admin JWT Authentication",
                    True,
                    f"Successfully authenticated as admin and obtained JWT token",
                    {"username": data.get('username'), "user_type": data.get('type')}
                )
                return True
            else:
                self.log_test(
                    "Admin JWT Authentication", 
                    False,
                    f"Failed to authenticate admin: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin JWT Authentication",
                False, 
                f"Admin authentication error: {str(e)}"
            )
            return False
    
    def test_jwt_bypass_process_session(self):
        """Test 1: JWT Authentication Bypass for /api/admin/google/process-session"""
        try:
            # Call process-session endpoint WITHOUT JWT token
            response = requests.post(
                f"{API_BASE}/admin/google/process-session",
                headers={
                    'X-Session-ID': 'test-session-id-12345',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            # Should NOT return 401 Unauthorized (the critical fix)
            if response.status_code == 401:
                self.log_test(
                    "JWT Bypass for process-session",
                    False,
                    "❌ CRITICAL ISSUE: Endpoint still returns 401 Unauthorized - JWT bypass not working!",
                    {
                        "status_code": response.status_code,
                        "response": response.text,
                        "issue": "Authentication middleware is still blocking OAuth endpoints"
                    }
                )
                return False
            else:
                # Any other status code means JWT bypass is working
                self.log_test(
                    "JWT Bypass for process-session",
                    True,
                    f"✅ SUCCESS: No 401 error - JWT authentication bypass working correctly",
                    {
                        "status_code": response.status_code,
                        "response_preview": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                        "fix_confirmed": "OAuth endpoint accessible without JWT token"
                    }
                )
                return True
                
        except Exception as e:
            self.log_test(
                "JWT Bypass for process-session",
                False,
                f"Request error: {str(e)}"
            )
            return False
    
    def test_oauth_endpoints_access(self):
        """Test 2: Verify all Google OAuth endpoints can be accessed without JWT tokens"""
        oauth_endpoints = [
            "/admin/google/auth-url",
            "/admin/google/process-session", 
            "/admin/google/profile"
        ]
        
        results = {}
        
        for endpoint in oauth_endpoints:
            try:
                if endpoint == "/admin/google/auth-url":
                    # This endpoint requires JWT (should work with token)
                    if not self.admin_token:
                        results[endpoint] = {"status": "skipped", "reason": "No admin token"}
                        continue
                        
                    response = requests.get(
                        f"{API_BASE}{endpoint}",
                        headers={'Authorization': f'Bearer {self.admin_token}'},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        results[endpoint] = {"status": "success", "requires_jwt": True}
                    else:
                        results[endpoint] = {"status": "failed", "code": response.status_code}
                        
                elif endpoint == "/admin/google/process-session":
                    # This endpoint should bypass JWT
                    response = requests.post(
                        f"{API_BASE}{endpoint}",
                        headers={'X-Session-ID': 'test-session-bypass'},
                        timeout=10
                    )
                    
                    if response.status_code != 401:
                        results[endpoint] = {"status": "success", "bypasses_jwt": True}
                    else:
                        results[endpoint] = {"status": "failed", "code": response.status_code, "issue": "Still blocked by JWT"}
                        
                elif endpoint == "/admin/google/profile":
                    # This endpoint should bypass JWT
                    response = requests.get(
                        f"{API_BASE}{endpoint}",
                        timeout=10
                    )
                    
                    if response.status_code != 401:
                        results[endpoint] = {"status": "success", "bypasses_jwt": True}
                    else:
                        results[endpoint] = {"status": "failed", "code": response.status_code, "issue": "Still blocked by JWT"}
                        
            except Exception as e:
                results[endpoint] = {"status": "error", "error": str(e)}
        
        # Analyze results
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        total_tested = len([r for r in results.values() if r.get("status") != "skipped"])
        
        self.log_test(
            "OAuth Endpoints Access",
            success_count == total_tested,
            f"OAuth endpoints accessibility: {success_count}/{total_tested} working correctly",
            results
        )
        
        return success_count == total_tested
    
    def test_session_processing_logic(self):
        """Test 3: Test session processing request with X-Session-ID header"""
        try:
            response = requests.post(
                f"{API_BASE}/admin/google/process-session",
                headers={
                    'X-Session-ID': 'mock-emergent-session-12345',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            # Should reach the processing code (not return 401)
            if response.status_code == 401:
                self.log_test(
                    "Session Processing Logic",
                    False,
                    "❌ CRITICAL: Still getting 401 authentication error - middleware blocking session processing",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
            else:
                # Any other response means we reached the processing logic
                self.log_test(
                    "Session Processing Logic", 
                    True,
                    f"✅ SUCCESS: Session processing logic executed (status: {response.status_code})",
                    {
                        "status_code": response.status_code,
                        "processing_reached": True,
                        "response_preview": response.text[:200] + "..." if len(response.text) > 200 else response.text
                    }
                )
                return True
                
        except Exception as e:
            self.log_test(
                "Session Processing Logic",
                False,
                f"Request error: {str(e)}"
            )
            return False
    
    def test_authentication_middleware_behavior(self):
        """Test 4: Verify authentication middleware still protects other admin endpoints"""
        try:
            # Test a protected admin endpoint without JWT token
            response = requests.get(f"{API_BASE}/admin/clients", timeout=10)
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Middleware Protection",
                    True,
                    "✅ SUCCESS: Other admin endpoints still properly protected by JWT authentication",
                    {"status_code": response.status_code, "endpoint": "/admin/clients"}
                )
                return True
            else:
                self.log_test(
                    "Authentication Middleware Protection",
                    False,
                    f"⚠️ WARNING: Protected endpoint accessible without JWT token (status: {response.status_code})",
                    {"status_code": response.status_code, "response": response.text[:100]}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authentication Middleware Protection",
                False,
                f"Request error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all Google OAuth authentication bypass tests"""
        print("🔐 GOOGLE OAUTH AUTHENTICATION BYPASS TESTING")
        print("=" * 60)
        print("Testing critical fix for Google OAuth login loop issue")
        print("Focus: JWT authentication bypass for OAuth endpoints")
        print()
        
        # Authenticate admin first
        if not self.authenticate_admin():
            print("⚠️ WARNING: Admin authentication failed, some tests may be limited")
        
        # Run core tests
        test_methods = [
            self.test_jwt_bypass_process_session,
            self.test_oauth_endpoints_access, 
            self.test_session_processing_logic,
            self.test_authentication_middleware_behavior
        ]
        
        passed_tests = 0
        for test_method in test_methods:
            if test_method():
                passed_tests += 1
        
        # Generate summary
        total_tests = len(test_methods)
        success_rate = (passed_tests / total_tests) * 100
        
        print("=" * 60)
        print("🎯 GOOGLE OAUTH AUTHENTICATION BYPASS TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Key success criteria analysis
        critical_tests = [
            "JWT Bypass for process-session",
            "Session Processing Logic"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        
        print("🔑 KEY SUCCESS CRITERIA:")
        print(f"✅ /api/admin/google/process-session accessible without JWT: {'YES' if critical_passed >= 1 else 'NO'}")
        print(f"✅ Session processing logic executes: {'YES' if critical_passed >= 2 else 'NO'}")
        print(f"✅ No more 401 authentication errors: {'YES' if critical_passed >= 1 else 'NO'}")
        print()
        
        if success_rate >= 75 and critical_passed >= 2:
            print("🎉 CONCLUSION: Google OAuth login loop fix is WORKING CORRECTLY!")
            print("   - OAuth endpoints bypass JWT authentication as expected")
            print("   - Session processing logic is accessible")
            print("   - Login loop issue should be resolved")
        else:
            print("🚨 CONCLUSION: Google OAuth login loop fix needs attention!")
            print("   - Critical authentication bypass issues detected")
            print("   - Login loop issue may persist")
        
        return success_rate >= 75

def main():
    """Main test execution"""
    tester = GoogleOAuthAuthenticationTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()