"""
Test Render Production API - Corrected Login
"""
import requests

BACKEND_URL = "https://tradingbridge-4.preview.emergentagent.com"

print("="*80)
print("TESTING RENDER PRODUCTION API")
print("="*80)
print()

print("TEST 1: Health Check")
print("-"*80)
response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
print(f"Status: {response.status_code}")
print(f"✅ API is reachable" if response.status_code == 200 else "❌ API not reachable")
print()

print("TEST 2: Login (Corrected Format)")
print("-"*80)

try:
    # Use form data format
    login_response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        data={
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        },
        timeout=10
    )
    
    print(f"Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('access_token') or token_data.get('token')
        print(f"✅ Login successful")
        
        # Test Three-Tier P&L
        print()
        print("TEST 3: Three-Tier P&L Endpoint")
        print("-"*80)
        
        headers = {"Authorization": f"Bearer {token}"}
        pnl_response = requests.get(
            f"{BACKEND_URL}/api/pnl/three-tier",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {pnl_response.status_code}")
        
        if pnl_response.status_code == 200:
            pnl_data = pnl_response.json()
            client_inv = pnl_data['data']['client_pnl']['initial_allocation']
            fidus_inv = pnl_data['data']['fidus_pnl']['initial_allocation']
            
            print(f"✅ Three-Tier P&L working")
            print(f"   Client: ${client_inv:,.2f} {'✅' if abs(client_inv - 118151.41) < 1 else '❌'}")
            print(f"   FIDUS: ${fidus_inv:,.2f} {'✅' if abs(fidus_inv - 14662.94) < 1 else '❌'}")
        else:
            print(f"❌ Failed: {pnl_response.text[:100]}")
        
        # Test Trading Analytics
        print()
        print("TEST 4: Trading Analytics")
        print("-"*80)
        
        analytics_response = requests.get(
            f"{BACKEND_URL}/api/admin/trading-analytics/portfolio?period_days=30",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {analytics_response.status_code}")
        
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            client_aum = analytics['portfolio'].get('client_aum', 0)
            
            print(f"✅ Trading Analytics working")
            print(f"   Client AUM: ${client_aum:,.2f} {'✅' if abs(client_aum - 118151.41) < 1 else '❌'}")
        else:
            print(f"❌ Failed: {analytics_response.text[:100]}")
            
    else:
        print(f"❌ Login failed: {login_response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("="*80)
print("✅ RENDER API VERIFICATION COMPLETE")
print("="*80)
