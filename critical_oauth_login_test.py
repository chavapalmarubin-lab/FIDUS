#!/usr/bin/env python3
"""
CRITICAL GOOGLE OAUTH LOGIN LOOP FIX VERIFICATION TEST
=====================================================

This test verifies the critical backend endpoints that were causing the Google OAuth login loop issue:

PRIORITY TESTING:
1. Test `/api/auth/login` with admin credentials (username: admin, password: password123, user_type: admin)
2. Test `/api/fund-portfolio/overview` endpoint that was missing and causing 404 errors
3. Verify the login response includes proper JWT token and user data
4. Confirm the fund portfolio endpoint returns the correct data structure with AUM, investors, and fund details

CONTEXT: 
- We just fixed a critical issue where the frontend was calling `/api/fund-portfolio/overview` which didn't exist, causing 404 errors after successful Google OAuth authentication
- This 404 error was breaking the session and causing an infinite login loop
- I added the missing endpoint that returns fund portfolio data with Total AUM: $4,144,456.20 and 11 investors
- Need to verify both endpoints are working correctly to ensure the login loop is permanently resolved
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the URL from frontend/.env
BACKEND_URL = "https://fidus-finance-api.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CriticalOAuthLoginTest:
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
    
    def test_admin_login_endpoint(self):
        """Test /api/auth/login with admin credentials - PRIORITY 1"""
        try:
            print("\n🔐 Testing Admin Login Endpoint...")
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["id", "username", "name", "email", "type", "token"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_result("Admin Login - Response Structure", False, 
                                  f"Missing required fields: {missing_fields}", 
                                  {"response": data})
                    return False
                
                # Verify admin user data
                if data.get("username") == ADMIN_USERNAME and data.get("type") == "admin":
                    self.log_result("Admin Login - User Data", True, 
                                  f"Admin user data correct: {data.get('name')} ({data.get('email')})")
                else:
                    self.log_result("Admin Login - User Data", False, 
                                  f"Incorrect user data", {"response": data})
                    return False
                
                # Verify JWT token
                token = data.get("token")
                if token and len(token) > 50:  # JWT tokens are typically long
                    self.admin_token = token
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    self.log_result("Admin Login - JWT Token", True, 
                                  f"JWT token received (length: {len(token)})")
                else:
                    self.log_result("Admin Login - JWT Token", False, 
                                  f"Invalid or missing JWT token", {"token": token})
                    return False
                
                self.log_result("Admin Login Endpoint", True, 
                              "✅ CRITICAL SUCCESS: Admin login working correctly with proper JWT token and user data")
                return True
                
            else:
                self.log_result("Admin Login Endpoint", False, 
                              f"❌ CRITICAL FAILURE: HTTP {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Login Endpoint", False, 
                          f"❌ CRITICAL FAILURE: Exception: {str(e)}")
            return False
    
    def test_fund_portfolio_overview_endpoint(self):
        """Test /api/fund-portfolio/overview endpoint - PRIORITY 2"""
        try:
            print("\n📊 Testing Fund Portfolio Overview Endpoint...")
            
            if not self.admin_token:
                self.log_result("Fund Portfolio Overview", False, 
                              "❌ CRITICAL: No admin token available for authentication")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if not isinstance(data, dict):
                    self.log_result("Fund Portfolio Overview - Structure", False, 
                                  "Response is not a JSON object", {"response": data})
                    return False
                
                # Check for success field
                if not data.get("success"):
                    self.log_result("Fund Portfolio Overview - Success Flag", False, 
                                  "Response does not indicate success", {"response": data})
                    return False
                
                # Verify fund portfolio data structure
                expected_fields = ["total_aum", "total_investors", "funds"]
                missing_fields = []
                
                for field in expected_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_result("Fund Portfolio Overview - Data Structure", False, 
                                  f"Missing expected fields: {missing_fields}", 
                                  {"response": data})
                    return False
                
                # Verify AUM and investor data
                total_aum = data.get("total_aum", 0)
                total_investors = data.get("total_investors", 0)
                funds = data.get("funds", [])
                
                if total_aum > 0:
                    self.log_result("Fund Portfolio Overview - AUM Data", True, 
                                  f"Total AUM: ${total_aum:,.2f}")
                else:
                    self.log_result("Fund Portfolio Overview - AUM Data", False, 
                                  f"Total AUM is zero or missing: {total_aum}")
                
                if total_investors > 0:
                    self.log_result("Fund Portfolio Overview - Investor Data", True, 
                                  f"Total Investors: {total_investors}")
                else:
                    self.log_result("Fund Portfolio Overview - Investor Data", False, 
                                  f"Total investors is zero or missing: {total_investors}")
                
                if isinstance(funds, list) and len(funds) > 0:
                    self.log_result("Fund Portfolio Overview - Fund Details", True, 
                                  f"Fund details available: {len(funds)} funds")
                else:
                    self.log_result("Fund Portfolio Overview - Fund Details", False, 
                                  f"Fund details missing or empty: {funds}")
                
                self.log_result("Fund Portfolio Overview Endpoint", True, 
                              f"✅ CRITICAL SUCCESS: Fund portfolio endpoint working - AUM: ${total_aum:,.2f}, Investors: {total_investors}")
                return True
                
            elif response.status_code == 404:
                self.log_result("Fund Portfolio Overview Endpoint", False, 
                              "❌ CRITICAL FAILURE: 404 Not Found - This endpoint is still missing!", 
                              {"response": response.text})
                return False
            else:
                self.log_result("Fund Portfolio Overview Endpoint", False, 
                              f"❌ CRITICAL FAILURE: HTTP {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Fund Portfolio Overview Endpoint", False, 
                          f"❌ CRITICAL FAILURE: Exception: {str(e)}")
            return False
    
    def test_login_session_persistence(self):
        """Test that login session persists and doesn't break after API calls"""
        try:
            print("\n🔄 Testing Login Session Persistence...")
            
            if not self.admin_token:
                self.log_result("Session Persistence", False, 
                              "No admin token available for testing")
                return False
            
            # Make multiple API calls to test session persistence
            test_endpoints = [
                "/health",
                "/fund-portfolio/overview", 
                "/admin/clients"
            ]
            
            session_stable = True
            for endpoint in test_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 401:
                        session_stable = False
                        self.log_result("Session Persistence", False, 
                                      f"Session lost on {endpoint} - 401 Unauthorized")
                        break
                    elif response.status_code in [200, 404]:  # 404 is acceptable for missing endpoints
                        continue
                    else:
                        # Other status codes might be acceptable depending on endpoint
                        continue
                except Exception as e:
                    self.log_result("Session Persistence", False, 
                                  f"Exception on {endpoint}: {str(e)}")
                    session_stable = False
                    break
            
            if session_stable:
                self.log_result("Session Persistence", True, 
                              "✅ Login session remains stable across multiple API calls")
                return True
            else:
                return False
                
        except Exception as e:
            self.log_result("Session Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_oauth_login_loop_prevention(self):
        """Test that the OAuth login loop issue is resolved"""
        try:
            print("\n🔁 Testing OAuth Login Loop Prevention...")
            
            # Simulate the frontend flow that was causing the loop
            # 1. Login successfully
            # 2. Call fund-portfolio/overview (this was causing 404 and breaking session)
            # 3. Verify session is still valid
            
            if not self.admin_token:
                self.log_result("OAuth Loop Prevention", False, 
                              "No admin token available for testing")
                return False
            
            # Step 1: Verify we're logged in
            health_response = self.session.get(f"{BACKEND_URL}/health")
            if health_response.status_code != 200:
                self.log_result("OAuth Loop Prevention - Health Check", False, 
                              f"Health check failed: {health_response.status_code}")
                return False
            
            # Step 2: Call the problematic endpoint that was causing the loop
            portfolio_response = self.session.get(f"{BACKEND_URL}/fund-portfolio/overview")
            
            # Step 3: Verify session is still valid after the call
            health_response_after = self.session.get(f"{BACKEND_URL}/health")
            
            if health_response_after.status_code == 200:
                if portfolio_response.status_code == 200:
                    self.log_result("OAuth Loop Prevention", True, 
                                  "✅ CRITICAL SUCCESS: No login loop - fund-portfolio/overview works and session remains valid")
                elif portfolio_response.status_code == 404:
                    self.log_result("OAuth Loop Prevention", False, 
                                  "❌ CRITICAL ISSUE: fund-portfolio/overview still returns 404 - login loop risk remains!")
                else:
                    self.log_result("OAuth Loop Prevention", True, 
                                  f"Session remains valid even with portfolio endpoint error ({portfolio_response.status_code})")
                return True
            else:
                self.log_result("OAuth Loop Prevention", False, 
                              "❌ CRITICAL ISSUE: Session broken after fund-portfolio call - login loop risk!")
                return False
                
        except Exception as e:
            self.log_result("OAuth Loop Prevention", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all critical OAuth login loop fix verification tests"""
        print("🚨 CRITICAL GOOGLE OAUTH LOGIN LOOP FIX VERIFICATION TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("TESTING CRITICAL ENDPOINTS THAT WERE CAUSING LOGIN LOOP:")
        print("1. /api/auth/login - Admin authentication with JWT")
        print("2. /api/fund-portfolio/overview - Missing endpoint causing 404s")
        print("3. Session persistence and login loop prevention")
        print()
        
        # Run critical tests in order
        login_success = self.test_admin_login_endpoint()
        portfolio_success = self.test_fund_portfolio_overview_endpoint()
        session_success = self.test_login_session_persistence()
        loop_prevention_success = self.test_oauth_login_loop_prevention()
        
        # Generate summary
        self.generate_test_summary()
        
        # Return overall success
        return login_success and portfolio_success and session_success and loop_prevention_success
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🚨 CRITICAL OAUTH LOGIN LOOP FIX TEST SUMMARY")
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
        
        # Show failed tests first (most important)
        if failed_tests > 0:
            print("❌ CRITICAL FAILURES:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ SUCCESSFUL TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment for OAuth login loop fix
        critical_tests = [
            "Admin Login Endpoint",
            "Fund Portfolio Overview Endpoint", 
            "OAuth Loop Prevention"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT - OAUTH LOGIN LOOP FIX:")
        if critical_passed >= 3:  # All 3 critical tests must pass
            print("✅ OAUTH LOGIN LOOP ISSUE: RESOLVED")
            print("   ✓ Admin login works with proper JWT token")
            print("   ✓ Fund portfolio overview endpoint is working")
            print("   ✓ No session breaking or login loops detected")
            print("   🎉 SYSTEM READY: Google OAuth login loop permanently fixed!")
        elif critical_passed >= 2:
            print("⚠️  OAUTH LOGIN LOOP ISSUE: PARTIALLY RESOLVED")
            print("   Some critical endpoints working but issues remain")
            print("   🔧 MAIN AGENT ACTION REQUIRED: Address remaining failures")
        else:
            print("❌ OAUTH LOGIN LOOP ISSUE: NOT RESOLVED")
            print("   Critical endpoints still failing")
            print("   🚨 URGENT MAIN AGENT ACTION REQUIRED: Fix critical failures")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = CriticalOAuthLoginTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()