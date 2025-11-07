#!/usr/bin/env python3
"""Test Render Production API"""
import requests
import json

RENDER_URL = "https://fidus-investment-platform.onrender.com"

print("="*80)
print("TESTING RENDER PRODUCTION API")
print("="*80)
print(f"URL: {RENDER_URL}")
print()

# Test Money Managers endpoint
api_url = f"{RENDER_URL}/api/admin/money-managers"
print(f"Testing: {api_url}")
print()

try:
    response = requests.get(api_url, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
    print()
    
    if response.status_code == 200:
        # Try to parse as JSON
        try:
            data = response.json()
            print("✅ Valid JSON response received")
            print()
            
            # Handle both dict and list formats
            if isinstance(data, dict):
                managers = data.get('managers', data.get('data', []))
                count = data.get('count', len(managers))
                success = data.get('success', True)
                
                print(f"Response Structure:")
                print(f"   success: {success}")
                print(f"   count: {count}")
                print(f"   managers count: {len(managers)}")
            else:
                managers = data
                count = len(managers)
            
            print()
            print("="*80)
            print(f"MANAGERS FOUND: {count}")
            print("="*80)
            print()
            
            if count == 0:
                print("❌ CRITICAL: No managers returned!")
                print()
                print("Full Response:")
                print(json.dumps(data, indent=2))
            else:
                # Check each manager
                zero_managers = []
                
                for i, mgr in enumerate(managers, 1):
                    name = mgr.get('manager_name', mgr.get('name', 'Unknown'))
                    initial = mgr.get('initial_allocation', 0)
                    equity = mgr.get('current_equity', 0)
                    pnl = mgr.get('total_pnl', 0)
                    
                    print(f"{i}. {name}")
                    print(f"   Initial: ${initial:,.2f}")
                    print(f"   Equity: ${equity:,.2f}")
                    print(f"   P&L: ${pnl:,.2f}")
                    
                    if initial == 0 or equity == 0:
                        zero_managers.append(name)
                        print(f"   ⚠️  HAS $0 VALUES!")
                    else:
                        print(f"   ✅ OK")
                    print()
                
                print("="*80)
                print("VALIDATION SUMMARY")
                print("="*80)
                print(f"Total Managers: {count}")
                print(f"Managers with $0 values: {len(zero_managers)}")
                print()
                
                if len(zero_managers) == 0:
                    print("🎉 SUCCESS! All managers have non-zero values!")
                else:
                    print("❌ ISSUE: The following managers have $0 values:")
                    for name in zero_managers:
                        print(f"   - {name}")
        
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response")
            print(f"Error: {str(e)}")
            print()
            print("Response Text (first 1000 chars):")
            print(response.text[:1000])
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print()
        print("Response:")
        print(response.text[:1000])

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

