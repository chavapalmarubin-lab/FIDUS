#!/usr/bin/env python3
"""Find the correct Render backend API URL"""
import requests

# The backend might be on a different subdomain or port
POSSIBLE_URLS = [
    "https://fidus-investment-platform.onrender.com/api/admin/money-managers",
    "https://fidus-backend.onrender.com/api/admin/money-managers", 
    "https://fidus-api.onrender.com/api/admin/money-managers",
]

print("="*80)
print("SEARCHING FOR CORRECT RENDER BACKEND URL")
print("="*80)
print()

found_url = None

for url in POSSIBLE_URLS:
    print(f"Testing: {url}")
    try:
        response = requests.get(url, timeout=10)
        content_type = response.headers.get('content-type', '')
        
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {content_type}")
        
        # Check if it's JSON (backend) or HTML (frontend)
        if 'application/json' in content_type:
            print(f"  ✅ Found JSON API!")
            print()
            
            # Try to parse
            try:
                data = response.json()
                if isinstance(data, dict):
                    print(f"  Response keys: {list(data.keys())}")
                    if 'managers' in data:
                        print(f"  ✅ This is the Money Managers endpoint!")
                        print(f"  Managers count: {len(data['managers'])}")
                        found_url = url
                        break
                else:
                    print(f"  Response is a list with {len(data)} items")
            except:
                pass
        else:
            print(f"  ⚠️  Returns HTML (frontend)")
        
        print()
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        print()

if found_url:
    print(f"\n🎉 Found backend API: {found_url}")
else:
    print("\n❌ Could not find backend API.")
    print("\nThe Render URL https://fidus-investment-platform.onrender.com")
    print("is serving the frontend React app, not the backend API.")
    print("\nThis means either:")
    print("1. Backend and frontend are on the same server but routes are configured differently")
    print("2. Backend is on a separate Render service with different URL")
    print("3. The deployment needs to be updated")

