"""
Test Render Production API
"""
import requests
import json

BACKEND_URL = "https://referral-portal-5.preview.emergentagent.com"

print("="*80)
print("TESTING RENDER PRODUCTION API")
print("="*80)
print()

# Get admin token (you'll need to provide real credentials)
print("TEST 1: Health Check")
print("-"*80)

try:
    response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Health: {data.get('status')}")
        print("✅ API is reachable")
    else:
        print(f"❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Connection error: {str(e)}")

print()
print("TEST 2: Login (Get Token)")
print("-"*80)

try:
    login_response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": "admin", "password": "password123"},
        timeout=10
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('token')
        print(f"✅ Login successful, token obtained")
        
        # Test Three-Tier P&L endpoint
        print()
        print("TEST 3: Three-Tier P&L Endpoint")
        print("-"*80)
        
        headers = {"Authorization": f"Bearer {token}"}
        pnl_response = requests.get(
            f"{BACKEND_URL}/api/pnl/three-tier",
            headers=headers,
            timeout=10
        )
        
        if pnl_response.status_code == 200:
            pnl_data = pnl_response.json()
            if pnl_data.get('success'):
                client_pnl = pnl_data['data']['client_pnl']
                fidus_pnl = pnl_data['data']['fidus_pnl']
                
                print(f"✅ Three-Tier P&L endpoint working")
                print(f"   Client Investment: ${client_pnl['initial_allocation']:,.2f}")
                print(f"   FIDUS Investment: ${fidus_pnl['initial_allocation']:,.2f}")
                
                # Verify critical numbers
                if abs(client_pnl['initial_allocation'] - 118151.41) < 1:
                    print(f"   ✅ Client investment correct ($118,151.41)")
                else:
                    print(f"   ❌ Client investment wrong: ${client_pnl['initial_allocation']:,.2f}")
                
                if abs(fidus_pnl['initial_allocation'] - 14662.94) < 1:
                    print(f"   ✅ FIDUS investment correct ($14,662.94)")
                else:
                    print(f"   ❌ FIDUS investment wrong: ${fidus_pnl['initial_allocation']:,.2f}")
            else:
                print(f"❌ API returned success=false")
        else:
            print(f"❌ Three-tier P&L failed: {pnl_response.status_code}")
            print(f"   Response: {pnl_response.text[:200]}")
        
        # Test Trading Analytics endpoint
        print()
        print("TEST 4: Trading Analytics Portfolio Endpoint")
        print("-"*80)
        
        analytics_response = requests.get(
            f"{BACKEND_URL}/api/admin/trading-analytics/portfolio?period_days=30",
            headers=headers,
            timeout=10
        )
        
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            if analytics_data.get('success'):
                portfolio = analytics_data['portfolio']
                print(f"✅ Trading Analytics endpoint working")
                print(f"   Client AUM: ${portfolio.get('client_aum', 0):,.2f}")
                print(f"   Total AUM: ${portfolio.get('total_aum', 0):,.2f}")
                
                if abs(portfolio.get('client_aum', 0) - 118151.41) < 1:
                    print(f"   ✅ Client AUM correct")
                else:
                    print(f"   ⚠️  Client AUM: ${portfolio.get('client_aum', 0):,.2f}")
            else:
                print(f"❌ API returned success=false")
        else:
            print(f"❌ Trading Analytics failed: {analytics_response.status_code}")
            print(f"   Response: {analytics_response.text[:200]}")
        
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")

except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("="*80)
print("RENDER API TESTING COMPLETE")
print("="*80)
