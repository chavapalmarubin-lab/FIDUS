#!/usr/bin/env python3
"""
Phase 2 Backend Endpoints Debug Testing

Debug the 5 new endpoints to see their actual response structure
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://viking-trade-dash-1.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class Phase2DebugTesting:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
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
                    print("✅ Successfully authenticated as admin")
                    return True
                else:
                    print("❌ No token in response")
                    return False
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
    
    def debug_endpoint(self, endpoint_path, description):
        """Debug a specific endpoint"""
        print(f"\n🔍 DEBUGGING: {description}")
        print(f"Endpoint: {endpoint_path}")
        print("-" * 60)
        
        try:
            url = f"{BACKEND_URL}{endpoint_path}"
            response = self.session.get(url)
            
            print(f"HTTP Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response JSON:")
                    print(json.dumps(data, indent=2, default=str))
                except:
                    print(f"Response Text: {response.text}")
            else:
                print(f"Error Response: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")
    
    def run_debug_testing(self):
        """Run debug testing for all Phase 2 endpoints"""
        print("🔍 PHASE 2 BACKEND ENDPOINTS DEBUG TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Debug Time: {datetime.now().isoformat()}")
        
        # Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot debug endpoints.")
            return False
        
        # Debug each endpoint
        endpoints = [
            ("/api/portfolio/fund-allocations", "Portfolio Fund Allocations"),
            ("/api/investments/summary", "Investments Summary"),
            ("/api/analytics/trading-metrics?account=all", "Analytics Trading Metrics"),
            ("/api/money-managers/performance", "Money Managers Performance"),
            ("/api/mt5/accounts/all", "MT5 Accounts All")
        ]
        
        for endpoint_path, description in endpoints:
            self.debug_endpoint(endpoint_path, description)
        
        print("\n" + "=" * 80)
        print("🎯 DEBUG TESTING COMPLETE")
        print("=" * 80)

def main():
    """Main debug execution"""
    debugger = Phase2DebugTesting()
    debugger.run_debug_testing()

if __name__ == "__main__":
    main()