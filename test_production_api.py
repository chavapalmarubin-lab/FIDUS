#!/usr/bin/env python3
"""Test Production API on Render/Preview"""
import requests
import json

# Try both possible URLs
URLS = [
    "https://alloc-wizard.preview.emergentagent.com",
    "https://fidus-investment-platform.onrender.com"
]

def test_url(base_url):
    """Test Money Managers API at given URL"""
    print(f"\n{'='*80}")
    print(f"Testing: {base_url}")
    print(f"{'='*80}")
    
    try:
        # Test if server is up
        health_url = f"{base_url}/api/health"
        try:
            health = requests.get(health_url, timeout=10)
            print(f"✅ Server is reachable (status {health.status_code})")
        except:
            print(f"⚠️  Health endpoint not responding")
        
        # Test Money Managers endpoint
        api_url = f"{base_url}/api/admin/money-managers"
        print(f"\n📡 Testing: {api_url}")
        
        response = requests.get(api_url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict):
                managers = data.get('managers', [])
                count = data.get('count', len(managers))
            else:
                managers = data
                count = len(managers)
            
            print(f"\n✅ SUCCESS!")
            print(f"   Managers Found: {count}")
            
            # Check for zeros
            zero_count = 0
            for mgr in managers:
                initial = mgr.get('initial_allocation', 0)
                equity = mgr.get('current_equity', 0)
                
                if initial == 0 or equity == 0:
                    zero_count += 1
                    print(f"   ⚠️  {mgr.get('manager_name', 'Unknown')}: Initial=${initial}, Equity=${equity}")
            
            if zero_count == 0:
                print(f"   ✅ NO managers with $0 values!")
                return True
            else:
                print(f"   ❌ {zero_count} managers still have $0 values")
                return False
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# Test all URLs
print("="*80)
print("PRODUCTION API TESTING")
print("="*80)

for url in URLS:
    success = test_url(url)
    if success:
        print(f"\n🎉 {url} is working correctly!")
        break

