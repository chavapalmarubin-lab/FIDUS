#!/usr/bin/env python3
"""
Debug OAuth Tokens Structure
"""

import requests
import json

# Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def main():
    session = requests.Session()
    
    # Authenticate
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get individual status to see token structure
        response = session.get(f"{BACKEND_URL}/admin/google/individual-status")
        if response.status_code == 200:
            data = response.json()
            print("Individual Status Response:")
            print(json.dumps(data, indent=2))
            
            # Check if connected
            if data.get('connected'):
                google_info = data.get('google_info', {})
                print(f"\nGoogle Info Keys: {list(google_info.keys())}")
                
                # Check for scope information
                if 'scopes' in google_info:
                    print(f"Scopes: {google_info['scopes']}")
                elif 'granted_scopes' in google_info:
                    print(f"Granted Scopes: {google_info['granted_scopes']}")
                else:
                    print("No scope information found in google_info")
        else:
            print(f"Individual status error: {response.status_code} - {response.text}")
    else:
        print(f"Auth error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()