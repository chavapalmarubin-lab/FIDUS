#!/usr/bin/env python3
"""
API FIX ALL LILIAN PROSPECTS
============================

This script uses the API to find and fix all Lilian prospects.
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
    print("🔧 API FIX ALL LILIAN PROSPECTS")
    print("=" * 50)
    
    session = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    print("✅ Authenticated successfully")
    print()
    
    # Get all prospects via API
    print("🔍 Getting all prospects via API...")
    response = session.get(f"{BACKEND_URL}/crm/prospects")
    if response.status_code != 200:
        print(f"❌ Failed to get prospects: HTTP {response.status_code}")
        return
    
    prospects_data = response.json()
    
    if isinstance(prospects_data, dict):
        prospects = prospects_data.get('prospects', [])
    elif isinstance(prospects_data, list):
        prospects = prospects_data
    else:
        prospects = []
    
    print(f"Found {len(prospects)} total prospects")
    
    # Find all Lilian prospects
    lilian_prospects = []
    for prospect in prospects:
        if isinstance(prospect, dict):
            name = prospect.get('name', '').upper()
            if 'LILIAN' in name:
                lilian_prospects.append(prospect)
    
    print(f"Found {len(lilian_prospects)} Lilian prospects")
    
    if not lilian_prospects:
        print("❌ No Lilian prospects found")
        return
    
    # Fix each Lilian prospect
    fixed_count = 0
    for i, prospect in enumerate(lilian_prospects, 1):
        lilian_id = prospect.get('id')
        name = prospect.get('name')
        
        print(f"\n🔧 Fixing Lilian #{i}: {name} (ID: {lilian_id})")
        print(f"   Current stage: {prospect.get('stage')}")
        print(f"   Current aml_kyc_status: {prospect.get('aml_kyc_status')}")
        print(f"   Current converted_to_client: {prospect.get('converted_to_client')}")
        print(f"   Current client_id: {prospect.get('client_id')}")
        
        # Check if already correct
        stage = prospect.get('stage')
        aml_kyc_status = prospect.get('aml_kyc_status')
        converted_to_client = prospect.get('converted_to_client')
        
        if (stage == "won" and aml_kyc_status == "clear" and converted_to_client == False):
            print(f"   ✅ Lilian #{i} already has correct conditions - Convert button should be visible")
            fixed_count += 1
            continue
        
        # Need to fix this prospect
        # Since the API update endpoint doesn't support aml_kyc_status and converted_to_client,
        # we need to use a different approach
        
        # First, try to update what we can via API
        update_data = {
            "stage": "won"
        }
        
        response = session.put(f"{BACKEND_URL}/crm/prospects/{lilian_id}", json=update_data)
        
        if response.status_code == 200:
            print(f"   ✅ Updated stage to 'won' for Lilian #{i}")
        else:
            print(f"   ❌ Failed to update stage for Lilian #{i}: HTTP {response.status_code}")
        
        # For aml_kyc_status and converted_to_client, we need to check if there's a specific endpoint
        # or if we need to reset the conversion status
        
        # If this prospect was converted but the client doesn't exist, reset it
        if converted_to_client and prospect.get('client_id'):
            client_id = prospect.get('client_id')
            
            # Check if client exists
            client_response = session.get(f"{BACKEND_URL}/admin/clients")
            if client_response.status_code == 200:
                clients = client_response.json()
                client_exists = False
                if isinstance(clients, list):
                    client_exists = any(c.get('id') == client_id for c in clients if isinstance(c, dict))
                
                if not client_exists:
                    print(f"   🔍 Client {client_id} doesn't exist - this is a data inconsistency")
                    print(f"   🔧 This prospect needs manual database fix for converted_to_client and aml_kyc_status")
                else:
                    print(f"   ✅ Client {client_id} exists - prospect was properly converted")
        
        # For now, mark as needing manual fix
        print(f"   ⚠️  Lilian #{i} needs manual database fix for aml_kyc_status and converted_to_client fields")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Total Lilian prospects found: {len(lilian_prospects)}")
    print(f"   Prospects with correct conditions: {fixed_count}")
    print(f"   Prospects needing manual fix: {len(lilian_prospects) - fixed_count}")
    
    if fixed_count > 0:
        print("\n🎉 EXPECTED RESULT:")
        print("   User should see a big green 'CONVERT TO CLIENT' button")
        print("   on Lilian's prospect card(s) that have correct conditions.")
    
    # Show all Lilian prospects for debugging
    print(f"\n🔍 ALL LILIAN PROSPECTS DETAILS:")
    for i, prospect in enumerate(lilian_prospects, 1):
        print(f"   Lilian #{i}:")
        print(f"     ID: {prospect.get('id')}")
        print(f"     Name: {prospect.get('name')}")
        print(f"     Stage: {prospect.get('stage')}")
        print(f"     AML/KYC Status: {prospect.get('aml_kyc_status')}")
        print(f"     Converted to Client: {prospect.get('converted_to_client')}")
        print(f"     Client ID: {prospect.get('client_id')}")
        
        # Check conditions
        stage = prospect.get('stage')
        aml_kyc_status = prospect.get('aml_kyc_status')
        converted_to_client = prospect.get('converted_to_client')
        
        if (stage == "won" and aml_kyc_status == "clear" and converted_to_client == False):
            print(f"     🎯 Convert button: SHOULD BE VISIBLE")
        else:
            print(f"     ❌ Convert button: NOT VISIBLE")
            conditions = []
            if stage != "won":
                conditions.append(f"stage='{stage}' (need 'won')")
            if aml_kyc_status != "clear":
                conditions.append(f"aml_kyc_status='{aml_kyc_status}' (need 'clear')")
            if converted_to_client != False:
                conditions.append(f"converted_to_client={converted_to_client} (need false)")
            print(f"     Issues: {', '.join(conditions)}")
        print()

if __name__ == "__main__":
    main()