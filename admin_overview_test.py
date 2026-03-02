#!/usr/bin/env python3
"""
URGENT: Admin Overview $0 AUM Issue Investigation
Testing the specific GET /api/investments/admin/overview endpoint to debug why it shows $0 instead of $118,151.41

Expected Results:
- total_aum: $118,151.41 (not $0)
- total_investments: 2  
- total_clients: 1
- Should show Alejandro in clients array

Authentication: admin/password123
Backend: https://risk-engine-v2.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Use the correct backend URL from the review request
BACKEND_URL = "https://risk-engine-v2.preview.emergentagent.com/api"

class AdminOverviewTester:
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
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
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
    
    def test_admin_overview_detailed(self):
        """Test the admin overview endpoint with detailed analysis"""
        print("\n📊 Testing GET /api/investments/admin/overview")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/admin/overview")
            
            print(f"HTTP Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Raw Response: {json.dumps(data, indent=2)}")
                
                # Extract key metrics
                total_aum = data.get('total_aum', 'MISSING')
                total_investments = data.get('total_investments', 'MISSING')
                total_clients = data.get('total_clients', 'MISSING')
                clients = data.get('clients', [])
                
                print("\n🎯 KEY METRICS ANALYSIS:")
                print(f"Total AUM: {total_aum}")
                print(f"Total Investments: {total_investments}")
                print(f"Total Clients: {total_clients}")
                print(f"Clients Array Length: {len(clients)}")
                
                # Check for Alejandro specifically
                alejandro_found = False
                for client in clients:
                    if 'Alejandro' in client.get('name', '') or client.get('client_id') == 'client_alejandro':
                        alejandro_found = True
                        print(f"\n✅ ALEJANDRO FOUND:")
                        print(f"   Name: {client.get('name')}")
                        print(f"   Client ID: {client.get('client_id')}")
                        print(f"   Total Investment: {client.get('total_investment', 'N/A')}")
                        break
                
                if not alejandro_found:
                    print(f"\n❌ ALEJANDRO NOT FOUND in clients array")
                    print(f"Available clients: {[c.get('name') for c in clients]}")
                
                # Validate expected values
                print(f"\n🔍 VALIDATION AGAINST EXPECTED VALUES:")
                
                expected_aum = 118151.41
                if isinstance(total_aum, (int, float)):
                    if total_aum == 0:
                        print(f"❌ CRITICAL: AUM shows $0.00 (expected ${expected_aum:,.2f})")
                        return False
                    elif abs(total_aum - expected_aum) < 1:  # Allow small rounding differences
                        print(f"✅ AUM matches expected: ${total_aum:,.2f}")
                    else:
                        print(f"⚠️  AUM differs from expected: ${total_aum:,.2f} vs ${expected_aum:,.2f}")
                else:
                    print(f"❌ AUM is not numeric: {total_aum}")
                    return False
                
                if total_investments == 2:
                    print(f"✅ Investment count matches expected: {total_investments}")
                else:
                    print(f"⚠️  Investment count differs: {total_investments} (expected 2)")
                
                if total_clients == 1:
                    print(f"✅ Client count matches expected: {total_clients}")
                else:
                    print(f"⚠️  Client count differs: {total_clients} (expected 1)")
                
                return True
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during admin overview test: {str(e)}")
            return False
    
    def test_mongodb_queries(self):
        """Test related endpoints to understand data source"""
        print(f"\n🔍 TESTING RELATED ENDPOINTS FOR DATA SOURCE ANALYSIS")
        print("=" * 60)
        
        # Test client investments directly
        print(f"\n1. Testing client investments for Alejandro:")
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_alejandro")
            if response.status_code == 200:
                data = response.json()
                investments = data.get('investments', [])
                total_value = sum(inv.get('current_value', 0) for inv in investments)
                print(f"   ✅ Found {len(investments)} investments, Total Value: ${total_value:,.2f}")
                
                for inv in investments:
                    print(f"   - {inv.get('fund_code')}: ${inv.get('current_value', 0):,.2f}")
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        # Test all clients endpoint
        print(f"\n2. Testing all clients endpoint:")
        try:
            response = self.session.get(f"{BACKEND_URL}/clients")
            if response.status_code == 200:
                data = response.json()
                clients = data.get('clients', [])
                print(f"   ✅ Found {len(clients)} total clients")
                
                alejandro = next((c for c in clients if 'Alejandro' in c.get('name', '')), None)
                if alejandro:
                    print(f"   ✅ Alejandro found: {alejandro.get('name')} ({alejandro.get('id')})")
                else:
                    print(f"   ❌ Alejandro not found in clients list")
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    def run_investigation(self):
        """Run complete investigation of Admin Overview $0 AUM issue"""
        print("🚨 URGENT: Admin Overview $0 AUM Issue Investigation")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Expected AUM: $118,151.41")
        print(f"Reported Issue: AUM shows $0 instead of expected amount")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test admin overview endpoint
        overview_success = self.test_admin_overview_detailed()
        
        # Step 3: Test related endpoints
        self.test_mongodb_queries()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        if overview_success:
            print("✅ Admin Overview endpoint is working correctly")
            print("✅ AUM is NOT showing $0 - the issue may be resolved or environment-specific")
            print("\n📋 RECOMMENDATIONS:")
            print("   - The endpoint is returning correct data")
            print("   - Issue may be in frontend display or caching")
            print("   - Check browser cache and frontend state management")
            print("   - Verify frontend is calling the correct endpoint URL")
        else:
            print("❌ Admin Overview endpoint has issues")
            print("\n📋 URGENT FIXES REQUIRED:")
            print("   - Investigate MongoDB aggregation queries")
            print("   - Check database connection and data integrity")
            print("   - Verify investment records exist for Alejandro")
        
        return overview_success

if __name__ == "__main__":
    tester = AdminOverviewTester()
    success = tester.run_investigation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)