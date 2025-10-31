#!/usr/bin/env python3
"""
CHECK LILIAN'S CURRENT STATUS TEST
==================================

This test checks Lilian's current status - whether she's a prospect or client
and provides the exact current state for debugging.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Use PRODUCTION environment
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def authenticate():
    """Authenticate as admin"""
    session = requests.Session()
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})
            return session
    return None

def main():
    print("🔍 CHECKING LILIAN'S CURRENT STATUS")
    print("=" * 50)
    
    session = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    print("✅ Authenticated successfully")
    print()
    
    # Check prospects
    print("🔍 CHECKING PROSPECTS...")
    response = session.get(f"{BACKEND_URL}/crm/prospects")
    if response.status_code == 200:
        prospects_data = response.json()
        
        if isinstance(prospects_data, dict):
            prospects = prospects_data.get('prospects', [])
        elif isinstance(prospects_data, list):
            prospects = prospects_data
        else:
            prospects = []
        
        print(f"Total prospects: {len(prospects)}")
        
        lilian_prospect = None
        for prospect in prospects:
            if isinstance(prospect, dict):
                name = prospect.get('name', '').upper()
                if 'LILIAN' in name:
                    lilian_prospect = prospect
                    break
        
        if lilian_prospect:
            print("✅ FOUND LILIAN AS PROSPECT:")
            print(f"   ID: {lilian_prospect.get('id')}")
            print(f"   Name: {lilian_prospect.get('name')}")
            print(f"   Stage: {lilian_prospect.get('stage')}")
            print(f"   AML/KYC Status: {lilian_prospect.get('aml_kyc_status')}")
            print(f"   Converted to Client: {lilian_prospect.get('converted_to_client')}")
            print(f"   Client ID: {lilian_prospect.get('client_id')}")
        else:
            print("❌ Lilian not found in prospects")
    else:
        print(f"❌ Failed to get prospects: HTTP {response.status_code}")
    
    print()
    
    # Check clients
    print("🔍 CHECKING CLIENTS...")
    response = session.get(f"{BACKEND_URL}/admin/clients")
    if response.status_code == 200:
        clients = response.json()
        print(f"Total clients: {len(clients)}")
        
        lilian_client = None
        if isinstance(clients, list):
            for client in clients:
                if isinstance(client, dict):
                    name = client.get('name', '').upper()
                    if 'LILIAN' in name:
                        lilian_client = client
                        break
        
        if lilian_client:
            print("✅ FOUND LILIAN AS CLIENT:")
            print(f"   ID: {lilian_client.get('id')}")
            print(f"   Name: {lilian_client.get('name')}")
            print(f"   Email: {lilian_client.get('email')}")
            print(f"   Username: {lilian_client.get('username')}")
        else:
            print("❌ Lilian not found in clients")
    else:
        print(f"❌ Failed to get clients: HTTP {response.status_code}")
    
    print()
    print("🎯 CONCLUSION:")
    if lilian_prospect:
        # Check Convert button conditions
        stage = lilian_prospect.get('stage')
        aml_kyc_status = lilian_prospect.get('aml_kyc_status')
        converted_to_client = lilian_prospect.get('converted_to_client')
        
        if (stage == "won" and aml_kyc_status == "clear" and converted_to_client == False):
            print("✅ CONVERT BUTTON SHOULD BE VISIBLE")
            print("   All conditions met: stage='won', aml_kyc_status='clear', converted_to_client=false")
        else:
            print("❌ CONVERT BUTTON NOT VISIBLE")
            print(f"   Conditions: stage='{stage}' (need 'won'), aml_kyc_status='{aml_kyc_status}' (need 'clear'), converted_to_client={converted_to_client} (need false)")
    elif lilian_client:
        print("✅ LILIAN SUCCESSFULLY CONVERTED TO CLIENT")
        print("   Convert button no longer needed - conversion completed")
    else:
        print("❌ LILIAN NOT FOUND IN SYSTEM")
        print("   Need to create Lilian's prospect profile")

if __name__ == "__main__":
    main()