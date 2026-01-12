"""
Test Render Production API Endpoints
"""
import requests
import json

BACKEND_URL = "https://viking-analytics.preview.emergentagent.com"

print("="*80)
print("RENDER PRODUCTION API VERIFICATION")
print("="*80)
print()

# Test 1: Health Check
print("TEST 1: Health Check")
print("-"*80)
try:
    response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
    if response.status_code == 200:
        print(f"✅ API is healthy and reachable")
        print(f"   Status: {response.json().get('status')}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Connection error: {str(e)}")

print()

# Test 2: Portfolio Endpoint (public)
print("TEST 2: Trading Analytics Portfolio Endpoint")
print("-"*80)
try:
    response = requests.get(
        f"{BACKEND_URL}/api/admin/trading-analytics/portfolio?period_days=30",
        timeout=15
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            portfolio = data.get('portfolio', {})
            print(f"✅ Portfolio endpoint working")
            print(f"   Client AUM: ${portfolio.get('client_aum', 0):,.2f}")
            print(f"   Total AUM: ${portfolio.get('total_aum', 0):,.2f}")
            
            # Verify critical numbers
            client_aum = portfolio.get('client_aum', 0)
            if abs(client_aum - 118151.41) < 1:
                print(f"   ✅ Client AUM matches expected ($118,151.41)")
            else:
                print(f"   ⚠️  Client AUM: ${client_aum:,.2f} (expected $118,151.41)")
        else:
            print(f"❌ API returned success=false")
            print(f"   Error: {data.get('error', 'Unknown')}")
    elif response.status_code == 401:
        print(f"⚠️  Requires authentication (expected for admin endpoints)")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()

# Test 3: Check if new endpoints exist
print("TEST 3: New Three-Tier P&L Endpoints")
print("-"*80)

endpoints_to_check = [
    "/api/pnl/three-tier",
    "/api/pnl/fund-performance",
    "/api/admin/money-managers"
]

for endpoint in endpoints_to_check:
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {endpoint} - Working")
        elif response.status_code == 401 or response.status_code == 403:
            print(f"✅ {endpoint} - Exists (requires auth)")
        elif response.status_code == 404:
            print(f"❌ {endpoint} - Not Found (needs deployment)")
        else:
            print(f"⚠️  {endpoint} - Status {response.status_code}")
    except Exception as e:
        print(f"❌ {endpoint} - Error: {str(e)}")

print()
print("="*80)
print("RENDER API VERIFICATION COMPLETE")
print("="*80)
print()
print("NOTE: If new endpoints return 404, they need to be deployed.")
print("      Run 'Save to GitHub' to trigger Render deployment.")
print()
