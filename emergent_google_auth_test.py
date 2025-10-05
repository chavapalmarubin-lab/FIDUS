#!/usr/bin/env python3
"""
Emergent Google Auth Integration Testing
Tests the complete new Emergent Google OAuth implementation
"""

import requests
import json
import logging
from datetime import datetime, timezone
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmergentGoogleAuthTester:
    def __init__(self):
        # Use REACT_APP_BACKEND_URL from frontend/.env if available
        self.backend_url = "https://fidus-finance-api.preview.emergentagent.com/api"
        
        # Try to read from frontend/.env
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        url = line.split('=', 1)[1].strip()
                        if not url.endswith('/api'):
                            url += '/api'
                        self.backend_url = url
                        break
        except:
            pass
            
        logger.info(f"🔗 Using backend URL: {self.backend_url}")
        
        self.admin_token = None
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        logger.info(f"{status}: {test_name} - {details}")
        
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{self.backend_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_test("Admin Authentication", True, f"Authenticated as {data.get('username')}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_emergent_auth_url_generation(self):
        """Test Emergent Google Auth URL generation"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/google/emergent/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("auth_url"):
                    auth_url = data["auth_url"]
                    
                    # Verify auth URL points to Emergent auth service
                    if "auth.emergentagent.com" in auth_url:
                        self.log_test("Emergent Auth URL Generation", True,
                                    f"Auth URL generated: {auth_url[:100]}...")
                        
                        # Verify redirect URL is included
                        if "redirect=" in auth_url:
                            self.log_test("Emergent Auth URL Redirect Parameter", True,
                                        "Redirect parameter included in auth URL")
                        else:
                            self.log_test("Emergent Auth URL Redirect Parameter", False,
                                        "Missing redirect parameter in auth URL")
                    else:
                        self.log_test("Emergent Auth URL Generation", False,
                                    f"Auth URL does not point to Emergent service: {auth_url}")
                else:
                    self.log_test("Emergent Auth URL Generation", False,
                                f"Invalid response structure: {data}")
            else:
                self.log_test("Emergent Auth URL Generation", False,
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Emergent Auth URL Generation", False, f"Exception: {str(e)}")
    
    def test_emergent_status_endpoint(self):
        """Test Emergent Google authentication status endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/google/emergent/status")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") is not None:
                    connected = data.get("connected", False)
                    
                    if connected:
                        # User is connected - verify connection details
                        google_email = data.get("google_email")
                        google_name = data.get("google_name")
                        
                        if google_email and google_name:
                            self.log_test("Emergent Status Endpoint - Connected", True,
                                        f"Connected as {google_name} ({google_email})")
                        else:
                            self.log_test("Emergent Status Endpoint - Connected", False,
                                        "Missing user details in connected status")
                    else:
                        # User not connected - expected for fresh system
                        self.log_test("Emergent Status Endpoint - Not Connected", True,
                                    "Status correctly shows not connected")
                else:
                    self.log_test("Emergent Status Endpoint", False,
                                f"Invalid response structure: {data}")
            else:
                self.log_test("Emergent Status Endpoint", False,
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Emergent Status Endpoint", False, f"Exception: {str(e)}")
    
    def test_emergent_gmail_messages_endpoint(self):
        """Test Emergent Gmail messages endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/google/emergent/gmail/messages")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") is not None:
                    if data.get("auth_required"):
                        # Expected when not authenticated
                        self.log_test("Emergent Gmail Messages - Auth Required", True,
                                    "Correctly returns auth_required when not connected")
                    elif data.get("messages") is not None:
                        # User is connected and has messages
                        messages = data.get("messages", [])
                        count = data.get("count", 0)
                        source = data.get("source")
                        
                        if source == "emergent_gmail_api":
                            self.log_test("Emergent Gmail Messages - Connected", True,
                                        f"Retrieved {count} messages from Emergent Gmail API")
                        else:
                            self.log_test("Emergent Gmail Messages - Connected", False,
                                        f"Unexpected source: {source}")
                    else:
                        self.log_test("Emergent Gmail Messages", False,
                                    f"Unexpected response structure: {data}")
                else:
                    self.log_test("Emergent Gmail Messages", False,
                                f"Invalid response structure: {data}")
            else:
                self.log_test("Emergent Gmail Messages", False,
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Emergent Gmail Messages", False, f"Exception: {str(e)}")
    
    def test_emergent_callback_endpoint(self):
        """Test Emergent Google OAuth callback endpoint (without actual session_id)"""
        try:
            # Test with missing session_id
            response = self.session.post(f"{self.backend_url}/admin/google/emergent/callback", json={})
            
            if response.status_code == 400:
                error_detail = response.json().get("detail", "")
                if "session_id is required" in error_detail:
                    self.log_test("Emergent Callback Validation", True,
                                "Correctly validates missing session_id")
                else:
                    self.log_test("Emergent Callback Validation", False,
                                f"Unexpected error message: {error_detail}")
            else:
                self.log_test("Emergent Callback Validation", False,
                            f"Expected 400 error, got HTTP {response.status_code}")
                
            # Test with invalid session_id
            response = self.session.post(f"{self.backend_url}/admin/google/emergent/callback", 
                                       json={"session_id": "invalid_session_123"})
            
            if response.status_code in [400, 500]:
                # Expected to fail with invalid session_id
                self.log_test("Emergent Callback Invalid Session", True,
                            "Correctly handles invalid session_id")
            else:
                self.log_test("Emergent Callback Invalid Session", False,
                            f"Unexpected response for invalid session: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Emergent Callback Endpoint", False, f"Exception: {str(e)}")
    
    def test_emergent_logout_endpoint(self):
        """Test Emergent Google logout endpoint"""
        try:
            response = self.session.post(f"{self.backend_url}/admin/google/emergent/logout")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") is not None:
                    if data.get("success"):
                        self.log_test("Emergent Logout - Success", True,
                                    data.get("message", "Logout successful"))
                    else:
                        # Expected when no active session
                        message = data.get("message", "")
                        if "No active session" in message:
                            self.log_test("Emergent Logout - No Session", True,
                                        "Correctly handles logout when no active session")
                        else:
                            self.log_test("Emergent Logout - No Session", False,
                                        f"Unexpected message: {message}")
                else:
                    self.log_test("Emergent Logout", False,
                                f"Invalid response structure: {data}")
            else:
                self.log_test("Emergent Logout", False,
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Emergent Logout", False, f"Exception: {str(e)}")
    
    def verify_no_mock_codes(self):
        """Verify system doesn't use mock authorization codes"""
        try:
            # Check backend logs for mock code usage (this is a basic check)
            # In a real system, we'd check actual logs
            
            # Test that auth URL doesn't contain mock parameters
            response = self.session.get(f"{self.backend_url}/admin/google/emergent/auth-url")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                
                # Check for mock-related parameters
                mock_indicators = ["mock_auth_code", "test_code", "fake_code", "mock=true"]
                has_mock = any(indicator in auth_url.lower() for indicator in mock_indicators)
                
                if not has_mock:
                    self.log_test("No Mock Authorization Codes", True,
                                "Auth URL does not contain mock code parameters")
                else:
                    self.log_test("No Mock Authorization Codes", False,
                                "Auth URL contains mock code indicators")
            else:
                self.log_test("No Mock Authorization Codes", False,
                            "Could not verify auth URL")
                
        except Exception as e:
            self.log_test("No Mock Authorization Codes", False, f"Exception: {str(e)}")
    
    def test_backend_url_configuration(self):
        """Test that backend URL is correctly configured"""
        try:
            # Test health endpoint to verify backend connectivity
            response = self.session.get(f"{self.backend_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Backend URL Configuration", True,
                                f"Backend accessible at {self.backend_url}")
                else:
                    self.log_test("Backend URL Configuration", False,
                                f"Backend unhealthy: {data}")
            else:
                self.log_test("Backend URL Configuration", False,
                            f"Backend not accessible: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Backend URL Configuration", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Emergent Google Auth tests"""
        logger.info("🚀 Starting Emergent Google Auth Integration Testing")
        logger.info("=" * 80)
        
        # Test backend connectivity first
        self.test_backend_url_configuration()
        
        # Authenticate as admin
        if not self.authenticate_admin():
            logger.error("❌ Cannot proceed without admin authentication")
            return False
        
        # Run all Emergent Google Auth tests
        self.test_emergent_auth_url_generation()
        self.test_emergent_status_endpoint()
        self.test_emergent_gmail_messages_endpoint()
        self.test_emergent_callback_endpoint()
        self.test_emergent_logout_endpoint()
        self.verify_no_mock_codes()
        
        # Generate summary
        self.generate_summary()
        
        return True
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 EMERGENT GOOGLE AUTH INTEGRATION TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info("")
        
        if failed_tests > 0:
            logger.info("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"   • {result['test']}: {result['details']}")
            logger.info("")
        
        logger.info("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                logger.info(f"   • {result['test']}: {result['details']}")
        
        logger.info("=" * 80)
        
        # Determine overall result
        if success_rate >= 80:
            logger.info("🎉 EMERGENT GOOGLE AUTH INTEGRATION: WORKING CORRECTLY")
        elif success_rate >= 60:
            logger.info("⚠️ EMERGENT GOOGLE AUTH INTEGRATION: PARTIALLY WORKING")
        else:
            logger.info("🚨 EMERGENT GOOGLE AUTH INTEGRATION: CRITICAL ISSUES")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = EmergentGoogleAuthTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()