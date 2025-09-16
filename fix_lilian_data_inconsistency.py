#!/usr/bin/env python3
"""
FIX LILIAN DATA INCONSISTENCY
=============================

This script fixes the critical data inconsistency where Lilian is marked as
converted_to_client=True with client_id='client_abd45072' but that client
doesn't exist in the database.

This prevents the Convert button from showing.
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
    print("🔧 FIXING LILIAN DATA INCONSISTENCY")
    print("=" * 50)
    
    session = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    print("✅ Authenticated successfully")
    print()
    
    # Find Lilian's prospect ID
    lilian_id = "4de9c592-9b15-4c32-a268-e1f8459878b9"  # From previous test
    
    print(f"🔧 Fixing Lilian's data inconsistency (ID: {lilian_id})")
    
    # Reset Lilian's status to proper values for Convert button
    correct_data = {
        "stage": "won",
        "aml_kyc_status": "clear",
        "converted_to_client": False,
        "client_id": ""
    }
    
    print("Setting correct values:")
    print(f"   stage: 'won'")
    print(f"   aml_kyc_status: 'clear'")
    print(f"   converted_to_client: false")
    print(f"   client_id: '' (empty)")
    print()
    
    # Update Lilian's prospect data
    response = session.put(f"{BACKEND_URL}/crm/prospects/{lilian_id}", json=correct_data)
    
    if response.status_code == 200:
        updated_prospect = response.json()
        print("✅ SUCCESSFULLY UPDATED LILIAN'S DATA")
        print(f"   Stage: {updated_prospect.get('stage')}")
        print(f"   AML/KYC Status: {updated_prospect.get('aml_kyc_status')}")
        print(f"   Converted to Client: {updated_prospect.get('converted_to_client')}")
        print(f"   Client ID: '{updated_prospect.get('client_id')}'")
        print()
        
        # Verify Convert button conditions
        stage = updated_prospect.get('stage')
        aml_kyc_status = updated_prospect.get('aml_kyc_status')
        converted_to_client = updated_prospect.get('converted_to_client')
        
        if (stage == "won" and aml_kyc_status == "clear" and converted_to_client == False):
            print("🎯 CONVERT BUTTON CONDITIONS MET!")
            print("✅ stage='won' AND aml_kyc_status='clear' AND converted_to_client=false")
            print()
            print("🎉 EXPECTED RESULT:")
            print("   User should now see a big green 'CONVERT TO CLIENT' button")
            print("   on Lilian's prospect card in production.")
        else:
            print("❌ Convert button conditions still not met")
            print(f"   stage='{stage}', aml_kyc_status='{aml_kyc_status}', converted_to_client={converted_to_client}")
    else:
        print(f"❌ FAILED TO UPDATE LILIAN'S DATA: HTTP {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    main()