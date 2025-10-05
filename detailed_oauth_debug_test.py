#!/usr/bin/env python3
"""
Detailed OAuth Debug Test - Simulating exact user experience

This test simulates the exact user experience when clicking "Connect Google Workspace" button
and investigates why the user sees "Connection Failed" and "Google Auth Success: false"
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

class DetailedOAuthDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin user...")
        
        login_payload = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_payload, timeout=30)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("token") and data.get("type") == "admin":
                self.admin_token = data["token"]
                print(f"✅ Admin authenticated: {data.get('name')}, ID: {data.get('id')}")
                return True
        
        print("❌ Admin authentication failed")
        return False

    def debug_connection_status_detailed(self):
        """Debug the connection status that user sees"""
        print("\n🔍 DEBUGGING CONNECTION STATUS (What user sees)...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return
            
        # Test the exact endpoint that FullGoogleWorkspace.js calls
        response = self.session.get(
            f"{BACKEND_URL}/google/connection/test-all", 
            headers={"Authorization": f"Bearer {self.admin_token}"},
            timeout=30
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Connection Status Response (HTTP {response.status_code}):")
                print(json.dumps(data, indent=2))
                
                # Analyze what the frontend sees
                print("\n🎯 FRONTEND ANALYSIS:")
                print(f"   • overall_status: {data.get('overall_status', 'MISSING')}")
                print(f"   • connected: {data.get('connected', 'MISSING')}")
                print(f"   • success: {data.get('success', 'MISSING')}")
                print(f"   • is_expired: {data.get('is_expired', 'MISSING')}")
                
                # Check services
                services = data.get('services', {})
                print(f"   • services count: {len(services)}")
                for service, status in services.items():
                    service_status = status.get('status', 'unknown') if isinstance(status, dict) else status
                    print(f"     - {service}: {service_status}")
                
                # Check what triggers "Connection Failed"
                is_connected = data.get('connected', False)
                is_expired = data.get('is_expired', True)
                overall_status = data.get('overall_status', 'disconnected')
                
                print(f"\n🚨 CONNECTION ANALYSIS:")
                print(f"   • Frontend sees connected: {is_connected}")
                print(f"   • Frontend sees expired: {is_expired}")
                print(f"   • Overall status: {overall_status}")
                
                if not is_connected or is_expired:
                    print("   ❌ This explains 'Connection Failed' - user appears disconnected")
                else:
                    print("   ✅ User should see connected status")
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response (HTTP {response.status_code})")
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Connection status check failed: HTTP {status_code}")

    def debug_oauth_url_generation_detailed(self):
        """Debug OAuth URL generation with detailed analysis"""
        print("\n🔍 DEBUGGING OAUTH URL GENERATION (Connect button behavior)...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return None
            
        # Test the exact endpoint that handleConnectToGoogle() calls
        response = self.session.get(
            f"{BACKEND_URL}/auth/google/url", 
            headers={"Authorization": f"Bearer {self.admin_token}"},
            timeout=30
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ OAuth URL Response (HTTP {response.status_code}):")
                print(json.dumps(data, indent=2))
                
                # Check what the frontend expects
                success = data.get('success', False)
                auth_url = data.get('auth_url', '')
                error = data.get('error', '')
                
                print(f"\n🎯 FRONTEND OAUTH ANALYSIS:")
                print(f"   • success: {success}")
                print(f"   • auth_url present: {bool(auth_url)}")
                print(f"   • auth_url length: {len(auth_url) if auth_url else 0}")
                print(f"   • error: {error}")
                
                if success and auth_url:
                    print("   ✅ OAuth URL generation working - button should redirect")
                    print(f"   • URL preview: {auth_url[:100]}...")
                    return auth_url
                else:
                    print("   ❌ OAuth URL generation failed - this explains connection failure")
                    return None
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response (HTTP {response.status_code})")
                return None
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ OAuth URL generation failed: HTTP {status_code}")
            return None

    def debug_gmail_api_fallback(self):
        """Debug Gmail API call that shows 'No emails returned from Gmail API, using fallback'"""
        print("\n🔍 DEBUGGING GMAIL API FALLBACK MESSAGE...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return
            
        # Test the Gmail API endpoint
        response = self.session.get(
            f"{BACKEND_URL}/google/gmail/real-messages", 
            headers={"Authorization": f"Bearer {self.admin_token}"},
            timeout=30
        )
        
        if response:
            try:
                data = response.json()
                print(f"✅ Gmail API Response (HTTP {response.status_code}):")
                print(json.dumps(data, indent=2))
                
                # Analyze the response
                success = data.get('success', False)
                messages = data.get('messages', [])
                auth_required = data.get('auth_required', False)
                error = data.get('error', '')
                
                print(f"\n🎯 GMAIL API ANALYSIS:")
                print(f"   • success: {success}")
                print(f"   • messages count: {len(messages) if isinstance(messages, list) else 'N/A'}")
                print(f"   • auth_required: {auth_required}")
                print(f"   • error: {error}")
                
                if not success or not messages:
                    print("   ❌ This explains 'No emails returned from Gmail API, using fallback'")
                    if auth_required:
                        print("   • Reason: Authentication required (OAuth not completed)")
                    elif error:
                        print(f"   • Reason: Error - {error}")
                    else:
                        print("   • Reason: Unknown - no success flag or empty messages")
                else:
                    print(f"   ✅ Gmail API working - {len(messages)} messages returned")
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response (HTTP {response.status_code})")
        else:
            print("❌ Gmail API request failed - no response")

    def debug_oauth_callback_accessibility(self):
        """Debug OAuth callback endpoint accessibility"""
        print("\n🔍 DEBUGGING OAUTH CALLBACK ACCESSIBILITY...")
        
        # Test callback endpoint without parameters (should not be 404)
        response = self.session.get(f"{BACKEND_URL}/admin/google-callback", timeout=30)
        
        if response:
            print(f"✅ OAuth Callback Response (HTTP {response.status_code}):")
            if response.status_code == 404:
                print("   ❌ Callback endpoint returns 404 - OAuth flow cannot complete")
            elif response.status_code in [400, 401, 403]:
                print("   ✅ Callback endpoint accessible (expected error without OAuth params)")
            else:
                print(f"   ✅ Callback endpoint accessible (HTTP {response.status_code})")
                
            # Try to get response content
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    print("   Response data:", json.dumps(data, indent=2))
                else:
                    content = response.text[:200]
                    print(f"   Response content: {content}...")
            except:
                print("   Response content: Unable to parse")
        else:
            print("❌ OAuth callback request failed - no response")

    def debug_alternative_endpoints(self):
        """Debug alternative OAuth endpoints that might be used"""
        print("\n🔍 DEBUGGING ALTERNATIVE OAUTH ENDPOINTS...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return
            
        # Test Emergent OAuth endpoint
        print("Testing Emergent OAuth endpoint...")
        response = self.session.get(
            f"{BACKEND_URL}/admin/google/auth-url", 
            headers={"Authorization": f"Bearer {self.admin_token}"},
            timeout=30
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Emergent OAuth Response (HTTP {response.status_code}):")
                print(json.dumps(data, indent=2))
                
                auth_url = data.get('auth_url', '')
                if auth_url:
                    print("   ✅ Emergent OAuth working")
                    if 'auth.emergentagent.com' in auth_url:
                        print("   • Uses external Emergent OAuth service")
                    elif 'accounts.google.com' in auth_url:
                        print("   • Uses direct Google OAuth")
                else:
                    print("   ❌ Emergent OAuth missing auth_url")
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response (HTTP {response.status_code})")
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Emergent OAuth failed: HTTP {status_code}")

    def run_detailed_debug(self):
        """Run comprehensive OAuth debugging"""
        print("🚀 DETAILED OAUTH DEBUG - Investigating 'Connection Failed' Issue")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Debug Started: {datetime.now(timezone.utc).isoformat()}")
        print("Simulating exact user experience when clicking 'Connect Google Workspace'")
        print("=" * 80)

        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("🚨 Cannot proceed without admin authentication")
            return

        # Step 2: Debug connection status (what user sees)
        self.debug_connection_status_detailed()

        # Step 3: Debug OAuth URL generation (Connect button behavior)
        oauth_url = self.debug_oauth_url_generation_detailed()

        # Step 4: Debug Gmail API fallback message
        self.debug_gmail_api_fallback()

        # Step 5: Debug OAuth callback accessibility
        self.debug_oauth_callback_accessibility()

        # Step 6: Debug alternative endpoints
        self.debug_alternative_endpoints()

        print("\n" + "=" * 80)
        print("🎯 SUMMARY OF FINDINGS")
        print("=" * 80)
        
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("Based on the detailed debugging above, the issue is likely:")
        print("1. User sees 'Connection Failed' because connection status shows disconnected")
        print("2. 'Google Auth Success: false' indicates OAuth flow not completing")
        print("3. 'No emails returned from Gmail API, using fallback' due to missing OAuth tokens")
        print("\n💡 RECOMMENDED ACTIONS:")
        print("1. Check if OAuth tokens are properly stored after callback")
        print("2. Verify OAuth callback URL matches Google Console configuration")
        print("3. Ensure frontend is calling the correct OAuth endpoint")
        print("4. Check for any browser console errors during OAuth flow")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    debugger = DetailedOAuthDebugger()
    debugger.run_detailed_debug()