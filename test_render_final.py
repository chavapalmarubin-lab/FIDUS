#!/usr/bin/env python3
"""Test actual Render production backend API"""
import requests
import json

BACKEND_URL = "https://fidus-api.onrender.com"

print("="*80)
print("TESTING RENDER PRODUCTION BACKEND API")
print("="*80)
print(f"Backend URL: {BACKEND_URL}")
print()

# Step 1: Login as admin
print("Step 1: Authenticating as admin...")
login_url = f"{BACKEND_URL}/api/auth/login"

try:
    login_response = requests.post(
        login_url,
        json={
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        },
        timeout=15
    )
    
    if login_response.status_code == 200:
        token = login_response.json().get('token')
        print(f"✅ Successfully authenticated")
        print()
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        exit(1)
        
except Exception as e:
    print(f"❌ Login error: {str(e)}")
    exit(1)

# Step 2: Test Money Managers endpoint
print("Step 2: Testing /api/admin/money-managers...")
api_url = f"{BACKEND_URL}/api/admin/money-managers"

try:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(api_url, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        
        # Handle response structure
        if isinstance(data, dict):
            managers = data.get('managers', [])
            count = data.get('count', len(managers))
        else:
            managers = data
            count = len(managers)
        
        print("="*80)
        print(f"MANAGERS FOUND: {count}")
        print("="*80)
        print()
        
        if count == 0:
            print("❌ CRITICAL: No managers returned from production!")
            print()
            print("This means the backend code on Render is outdated.")
            print("Need to redeploy backend to Render.")
        else:
            # Check each manager for $0 values
            zero_managers = []
            
            for i, mgr in enumerate(managers, 1):
                name = mgr.get('manager_name', mgr.get('name', 'Unknown'))
                initial = mgr.get('initial_allocation', 0)
                equity = mgr.get('current_equity', 0)
                pnl = mgr.get('total_pnl', 0)
                return_pct = mgr.get('return_percentage', 0)
                
                print(f"{i}. {name}")
                print(f"   Initial Allocation: ${initial:,.2f}")
                print(f"   Current Equity: ${equity:,.2f}")
                print(f"   Total P&L: ${pnl:,.2f}")
                print(f"   Return: {return_pct:.2f}%")
                
                if initial == 0 or equity == 0:
                    zero_managers.append(name)
                    print(f"   ❌ HAS $0 VALUES - ISSUE!")
                else:
                    print(f"   ✅ Values OK")
                print()
            
            print("="*80)
            print("PRODUCTION API STATUS")
            print("="*80)
            print(f"Total Managers: {count} (Expected: 5)")
            print(f"Managers with $0 values: {len(zero_managers)}")
            print()
            
            if count == 5 and len(zero_managers) == 0:
                print("🎉 SUCCESS! Production API is working correctly!")
                print()
                print("✅ All 5 managers present")
                print("✅ No $0 values found")
                print("✅ MongoDB Atlas data is correct")
                print("✅ Backend code deployed correctly")
            elif count != 5:
                print("❌ ISSUE: Wrong number of managers")
                print(f"   Expected: 5")
                print(f"   Found: {count}")
                print()
                print("   Action needed: Check if backend code is deployed to Render")
            elif len(zero_managers) > 0:
                print("❌ ISSUE: Managers have $0 values")
                print()
                print("   Managers with $0:")
                for name in zero_managers:
                    print(f"   - {name}")
                print()
                print("   This means MongoDB Atlas still has $0 initial_allocation")
                print("   Or backend code not using updated MongoDB data")
    else:
        print(f"❌ API request failed: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

