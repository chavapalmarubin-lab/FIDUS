#!/usr/bin/env python3
"""
Fix Alejandro's investments - ensure ONLY the correct 4 investments exist
"""
import requests
import json

BASE_URL = "https://fidus-invest.emergent.host"

def get_admin_token():
    """Get admin JWT token"""
    login_data = {
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print(f"Login failed: {response.text}")
        return None

def check_investments(token):
    """Check current investments"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get investments or client data
    endpoints = [
        "/api/investments/all",
        "/api/clients/all", 
        "/api/admin/users",
        "/api/investments/client/alejandrom"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"\n--- {endpoint} ---")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:500]}...")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error calling {endpoint}: {e}")

def main():
    print("🔍 INVESTIGATING ALEJANDRO'S CURRENT INVESTMENTS")
    print("=" * 50)
    
    token = get_admin_token()
    if not token:
        print("❌ Could not get admin token")
        return
        
    print("✅ Got admin token")
    
    # Check current state
    check_investments(token)
    
    print("\n🎯 REQUIRED INVESTMENTS:")
    print("1. $80,000 BALANCE → MT5: 886557")
    print("2. $10,000 BALANCE → MT5: 886602") 
    print("3. $10,000 BALANCE → MT5: 886066")
    print("4. $18,151.41 CORE → MT5: 885822")
    print("TOTAL: $118,151.41")

if __name__ == "__main__":
    main()