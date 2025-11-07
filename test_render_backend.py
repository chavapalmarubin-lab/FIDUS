#!/usr/bin/env python3
"""Find the correct Render backend API URL"""
import requests

# The backend might be on a different subdomain or port
POSSIBLE_URLS = [
    "https://fidus-investment-platform.onrender.com/api/admin/money-managers",
    "https://fidus-backend.onrender.com/api/admin/money-managers",
    "https://fidus-api.onrender.com/api/admin/money-managers",
    "https://fidus-investment-platform.onrender.com:8001/api/admin/money-managers",
]

print("="*80)
print("SEARCHING FOR CORRECT RENDER BACKEND URL")
print("="*80)
print()

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
                        return url
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

print("Could not find backend API. The Render deployment might need verification.")
print()
print("Please check:")
print("1. Is the backend service deployed separately on Render?")
print("2. What is the actual backend URL in production?")
print("3. Check Render dashboard for the backend service URL")

