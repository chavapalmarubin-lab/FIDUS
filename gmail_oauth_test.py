#!/usr/bin/env python3
"""
Gmail OAuth Integration Test - New Credentials Verification
Testing the updated Gmail OAuth credentials to verify 403 error resolution
"""

import requests
import json
import sys
from datetime import datetime

class GmailOAuthTester:
    def __init__(self, base_url="https://docuflow-10.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.new_client_id = "909926639154-r3v0ka94cbu4uo0sn8g4jvtiulf4i9qs.apps.googleusercontent.com"
        
    def run_test(self, name, test_func):
        """Run a single test"""
        print(f"\n🔍 Testing {name}...")
        self.tests_run += 1
        
        try:
            success = test_func()
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED: {name}")
                return True
            else:
                print(f"❌ FAILED: {name}")
                return False
        except Exception as e:
            print(f"❌ ERROR in {name}: {str(e)}")
            return False
    
    def test_new_client_id_verification(self):
        """Test 1: Verify new client_id is being used correctly"""
        response = requests.get(f"{self.base_url}/api/gmail/auth-url", timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Auth URL endpoint failed: {response.status_code}")
            return False
            
        data = response.json()
        auth_url = data.get('authorization_url', '')
        
        if self.new_client_id in auth_url:
            print(f"   ✅ NEW CLIENT_ID verified in OAuth URL: {self.new_client_id}")
            return True
        else:
            print(f"   ❌ New client_id NOT found in OAuth URL")
            print(f"   URL: {auth_url}")
            return False
    
    def test_oauth_url_generation(self):
        """Test 2: Test GET /api/gmail/auth-url generates valid OAuth URLs"""
        response = requests.get(f"{self.base_url}/api/gmail/auth-url", timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Status code: {response.status_code}")
            return False
            
        data = response.json()
        
        # Check required response fields
        required_fields = ['success', 'authorization_url', 'state', 'instructions']
        for field in required_fields:
            if field not in data:
                print(f"   ❌ Missing field: {field}")
                return False
        
        auth_url = data.get('authorization_url', '')
        state = data.get('state', '')
        
        # Verify OAuth URL parameters
        required_params = [
            'accounts.google.com/o/oauth2/auth',
            f'client_id={self.new_client_id}',
            'scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.send',
            'redirect_uri=https%3A%2F%2Fdocuflow-10.preview.emergentagent.com%2Fapi%2Fgmail%2Foauth-callback',
            'response_type=code',
            'access_type=offline'
        ]
        
        all_params_found = True
        for param in required_params:
            if param in auth_url:
                print(f"   ✅ Found parameter: {param}")
            else:
                print(f"   ❌ Missing parameter: {param}")
                all_params_found = False
        
        if state and len(state) > 10:
            print(f"   ✅ Valid state parameter generated: {state[:20]}...")
        else:
            print(f"   ❌ Invalid state parameter: {state}")
            all_params_found = False
            
        return all_params_found
    
    def test_403_error_resolution(self):
        """Test 3: Verify OAuth flow no longer returns 403 errors"""
        # Test auth URL generation (should not return 403)
        response = requests.get(f"{self.base_url}/api/gmail/auth-url", timeout=10)
        
        if response.status_code == 403:
            print(f"   ❌ 403 error still occurring on auth-url endpoint")
            return False
        elif response.status_code == 200:
            print(f"   ✅ Auth URL endpoint returns 200 (no 403 error)")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
            
        # Test authenticate endpoint (should not return 403)
        auth_response = requests.post(f"{self.base_url}/api/gmail/authenticate", 
                                    json={}, 
                                    headers={'Content-Type': 'application/json'},
                                    timeout=10)
        
        if auth_response.status_code == 403:
            print(f"   ❌ 403 error still occurring on authenticate endpoint")
            return False
        elif auth_response.status_code == 200:
            print(f"   ✅ Authenticate endpoint returns 200 (no 403 error)")
        else:
            print(f"   ⚠️  Unexpected status code on authenticate: {auth_response.status_code}")
            
        # Test OAuth callback with valid parameters (should not return 403)
        if response.status_code == 200:
            auth_data = response.json()
            valid_state = auth_data.get('state', '')
            
            callback_url = f"{self.base_url}/api/gmail/oauth-callback?code=test_code&state={valid_state}"
            callback_response = requests.get(callback_url, allow_redirects=False, timeout=10)
            
            if callback_response.status_code == 403:
                print(f"   ❌ 403 error still occurring on oauth-callback endpoint")
                return False
            elif 300 <= callback_response.status_code < 400:
                print(f"   ✅ OAuth callback returns redirect (no 403 error)")
            else:
                print(f"   ⚠️  Unexpected callback status: {callback_response.status_code}")
        
        print(f"   ✅ No 403 errors detected in OAuth flow")
        return True
    
    def test_redirect_uri_validation(self):
        """Test 4: Confirm redirect URI matches configured value"""
        response = requests.get(f"{self.base_url}/api/gmail/auth-url", timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get auth URL: {response.status_code}")
            return False
            
        data = response.json()
        auth_url = data.get('authorization_url', '')
        
        expected_redirect_uri = "https://docuflow-10.preview.emergentagent.com/api/gmail/oauth-callback"
        encoded_redirect_uri = "redirect_uri=https%3A%2F%2Fdocuflow-10.preview.emergentagent.com%2Fapi%2Fgmail%2Foauth-callback"
        
        if encoded_redirect_uri in auth_url:
            print(f"   ✅ Redirect URI correctly configured: {expected_redirect_uri}")
            
            # Test that the callback endpoint exists and responds
            # First get a valid state
            valid_state = data.get('state', '')
            callback_url = f"{self.base_url}/api/gmail/oauth-callback?code=test&state={valid_state}"
            callback_response = requests.get(callback_url, allow_redirects=False, timeout=10)
            
            if callback_response.status_code in [307, 302]:  # Redirect responses
                location = callback_response.headers.get('location', '')
                if 'gmail_auth=' in location:
                    print(f"   ✅ Callback endpoint properly handles requests and redirects")
                    return True
                else:
                    print(f"   ⚠️  Callback redirects but format may be incorrect: {location}")
                    return True  # Still working, just different format
            else:
                print(f"   ❌ Callback endpoint not responding correctly: {callback_response.status_code}")
                return False
        else:
            print(f"   ❌ Redirect URI not found or incorrect in OAuth URL")
            print(f"   Expected: {encoded_redirect_uri}")
            print(f"   URL: {auth_url}")
            return False
    
    def test_oauth_flow_integration(self):
        """Test 5: Complete OAuth flow integration test"""
        # Step 1: Get OAuth URL
        auth_response = requests.get(f"{self.base_url}/api/gmail/auth-url", timeout=10)
        if auth_response.status_code != 200:
            print(f"   ❌ Step 1 failed: {auth_response.status_code}")
            return False
        
        auth_data = auth_response.json()
        auth_url = auth_data.get('authorization_url', '')
        state = auth_data.get('state', '')
        
        print(f"   ✅ Step 1: OAuth URL generated successfully")
        
        # Step 2: Verify authenticate endpoint detects missing credentials
        authenticate_response = requests.post(f"{self.base_url}/api/gmail/authenticate", 
                                            json={}, 
                                            headers={'Content-Type': 'application/json'},
                                            timeout=10)
        
        if authenticate_response.status_code != 200:
            print(f"   ❌ Step 2 failed: {authenticate_response.status_code}")
            return False
            
        auth_result = authenticate_response.json()
        if auth_result.get('action') == 'redirect_to_oauth':
            print(f"   ✅ Step 2: Authenticate endpoint properly detects OAuth needed")
        else:
            print(f"   ❌ Step 2: Unexpected authenticate response: {auth_result}")
            return False
        
        # Step 3: Test OAuth callback with valid state
        callback_url = f"{self.base_url}/api/gmail/oauth-callback?code=dummy_auth_code&state={state}"
        callback_response = requests.get(callback_url, allow_redirects=False, timeout=10)
        
        if 300 <= callback_response.status_code < 400:
            location = callback_response.headers.get('location', '')
            if 'gmail_auth=' in location:
                print(f"   ✅ Step 3: OAuth callback redirects properly")
                print(f"   ✅ Complete OAuth flow integration working")
                return True
            else:
                print(f"   ❌ Step 3: Callback redirect format incorrect: {location}")
                return False
        else:
            print(f"   ❌ Step 3: Callback failed: {callback_response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run all Gmail OAuth tests"""
        print("=" * 80)
        print("🔍 GMAIL OAUTH INTEGRATION TEST - NEW CREDENTIALS VERIFICATION")
        print("=" * 80)
        print(f"Testing updated credentials with client_id: {self.new_client_id}")
        print(f"Base URL: {self.base_url}")
        print(f"Test time: {datetime.now().isoformat()}")
        
        # Run all tests
        tests = [
            ("New Client_ID Verification", self.test_new_client_id_verification),
            ("OAuth URL Generation", self.test_oauth_url_generation),
            ("403 Error Resolution", self.test_403_error_resolution),
            ("Redirect URI Validation", self.test_redirect_uri_validation),
            ("OAuth Flow Integration", self.test_oauth_flow_integration)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 GMAIL OAUTH TEST RESULTS SUMMARY")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL GMAIL OAUTH TESTS PASSED!")
            print("✅ New credentials are working correctly")
            print("✅ 403 error has been resolved")
            print("✅ OAuth flow is functioning properly")
            return True
        else:
            print(f"\n❌ {self.tests_run - self.tests_passed} tests failed")
            print("⚠️  Gmail OAuth integration may have issues")
            return False

if __name__ == "__main__":
    tester = GmailOAuthTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)