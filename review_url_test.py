#!/usr/bin/env python3
"""
Testing the EXACT URL from the review request to see if there's a difference
Review request specified: https://trading-platform-76.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Use the EXACT URL from the review request
REVIEW_BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class ReviewURLTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        try:
            login_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            response = self.session.post(f"{REVIEW_BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    print(f"✅ Successfully authenticated as {data.get('name', 'admin')}")
                    return True
                else:
                    print(f"❌ No token in response: {data}")
                    return False
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
    
    def test_admin_overview_exact(self):
        """Test the EXACT endpoint from review request"""
        print(f"\n📊 Testing EXACT endpoint: GET {REVIEW_BACKEND_URL}/investments/admin/overview")
        print("=" * 80)
        
        try:
            response = self.session.get(f"{REVIEW_BACKEND_URL}/investments/admin/overview")
            
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key metrics
                total_aum = data.get('total_aum', 'MISSING')
                total_investments = data.get('total_investments', 'MISSING')
                total_clients = data.get('total_clients', 'MISSING')
                clients = data.get('clients', [])
                
                print(f"\n🎯 REVIEW REQUEST VALIDATION:")
                print(f"Expected AUM: $118,151.41")
                print(f"Actual AUM: ${total_aum:,.2f}" if isinstance(total_aum, (int, float)) else f"Actual AUM: {total_aum}")
                print(f"Expected Investments: 2")
                print(f"Actual Investments: {total_investments}")
                print(f"Expected Clients: 1")
                print(f"Actual Clients: {total_clients}")
                
                # Check for Alejandro specifically
                alejandro_found = False
                for client in clients:
                    if 'Alejandro' in client.get('client_name', '') or client.get('client_id') == 'client_alejandro':
                        alejandro_found = True
                        print(f"\n✅ ALEJANDRO FOUND IN CLIENTS ARRAY:")
                        print(f"   Name: {client.get('client_name')}")
                        print(f"   Client ID: {client.get('client_id')}")
                        print(f"   Total Invested: ${client.get('total_invested', 0):,.2f}")
                        print(f"   Current Value: ${client.get('current_value', 0):,.2f}")
                        print(f"   Investment Count: {client.get('investment_count', 0)}")
                        break
                
                if not alejandro_found:
                    print(f"\n❌ ALEJANDRO NOT FOUND in clients array")
                
                # Critical issue check
                if isinstance(total_aum, (int, float)) and total_aum == 0:
                    print(f"\n🚨 CRITICAL ISSUE CONFIRMED: AUM shows $0.00!")
                    print(f"This matches the reported issue in the review request.")
                    return False
                elif isinstance(total_aum, (int, float)) and total_aum > 0:
                    print(f"\n✅ AUM is NOT $0 - shows ${total_aum:,.2f}")
                    print(f"The reported issue may be resolved or environment-specific.")
                    
                    # Check if it matches expected amount
                    expected_aum = 118151.41
                    if abs(total_aum - expected_aum) < 1:
                        print(f"✅ AUM matches expected amount exactly!")
                    else:
                        print(f"⚠️  AUM differs from expected: ${total_aum:,.2f} vs ${expected_aum:,.2f}")
                        print(f"Difference: ${abs(total_aum - expected_aum):,.2f}")
                
                return True
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during admin overview test: {str(e)}")
            return False
    
    def run_review_test(self):
        """Run test using exact review request parameters"""
        print("🚨 TESTING EXACT REVIEW REQUEST SCENARIO")
        print("=" * 80)
        print(f"Backend URL: {REVIEW_BACKEND_URL}")
        print(f"Authentication: admin/password123")
        print(f"Target Endpoint: GET /api/investments/admin/overview")
        print(f"Expected Issue: total_aum shows $0 instead of $118,151.41")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test admin overview endpoint
        overview_success = self.test_admin_overview_exact()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 REVIEW REQUEST TEST SUMMARY")
        print("=" * 80)
        
        if overview_success:
            print("✅ Endpoint is accessible and returning data")
            print("✅ The reported $0 AUM issue is NOT currently present")
            print("\n📋 POSSIBLE EXPLANATIONS:")
            print("   1. Issue was already fixed by main agent")
            print("   2. Issue is intermittent or environment-specific")
            print("   3. Issue occurs under specific conditions not tested")
            print("   4. Frontend caching or display issue, not backend")
            print("\n📋 RECOMMENDATIONS:")
            print("   - Verify frontend is calling correct endpoint")
            print("   - Check browser cache and frontend state")
            print("   - Test with different authentication states")
            print("   - Monitor endpoint over time for intermittent issues")
        else:
            print("❌ Endpoint has issues or $0 AUM problem confirmed")
            print("\n📋 URGENT FIXES REQUIRED:")
            print("   - Investigate MongoDB aggregation queries")
            print("   - Check database connection and data integrity")
            print("   - Verify investment records exist and are accessible")
        
        return overview_success

if __name__ == "__main__":
    tester = ReviewURLTester()
    success = tester.run_review_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)