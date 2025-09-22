#!/usr/bin/env python3
"""
LILIAN DETAILED ANALYSIS - Convert Button Issue
==============================================

Since Lilian's client DOES exist, let's analyze why the Convert button isn't showing.
The issue might be more complex than initially thought.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fidus-workspace.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def get_admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    })
    
    if response.status_code == 200:
        return response.json().get("token")
    return None

def main():
    print("🔍 LILIAN DETAILED ANALYSIS - Convert Button Issue")
    print("=" * 60)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n1️⃣ CHECKING LILIAN'S PROSPECT DATA...")
    print("-" * 40)
    
    # Get prospects
    response = requests.get(f"{BACKEND_URL}/crm/prospects", headers=headers)
    if response.status_code == 200:
        data = response.json()
        prospects = data.get('prospects', [])
        
        lilian_prospect = None
        for prospect in prospects:
            if 'lilian' in prospect.get('name', '').lower() and 'limon' in prospect.get('name', '').lower():
                lilian_prospect = prospect
                break
        
        if lilian_prospect:
            print(f"✅ Found Lilian Prospect:")
            print(f"   ID: {lilian_prospect.get('id')}")
            print(f"   Name: {lilian_prospect.get('name')}")
            print(f"   Email: {lilian_prospect.get('email')}")
            print(f"   Stage: {lilian_prospect.get('stage')}")
            print(f"   AML/KYC Status: {lilian_prospect.get('aml_kyc_status')}")
            print(f"   Converted to Client: {lilian_prospect.get('converted_to_client')}")
            print(f"   Client ID: {lilian_prospect.get('client_id')}")
            print(f"   Created: {lilian_prospect.get('created_at')}")
            print(f"   Updated: {lilian_prospect.get('updated_at')}")
        else:
            print("❌ Lilian prospect not found")
            return
    else:
        print(f"❌ Failed to get prospects: {response.status_code}")
        return
    
    print("\n2️⃣ CHECKING LILIAN'S CLIENT DATA...")
    print("-" * 40)
    
    # Get clients
    response = requests.get(f"{BACKEND_URL}/admin/clients", headers=headers)
    if response.status_code == 200:
        data = response.json()
        clients = data.get('clients', [])
        
        lilian_client = None
        client_id = lilian_prospect.get('client_id')
        
        for client in clients:
            if client.get('id') == client_id:
                lilian_client = client
                break
        
        if lilian_client:
            print(f"✅ Found Lilian Client:")
            print(f"   ID: {lilian_client.get('id')}")
            print(f"   Name: {lilian_client.get('name')}")
            print(f"   Email: {lilian_client.get('email')}")
            print(f"   Total Balance: ${lilian_client.get('total_balance', 0):,.2f}")
            print(f"   Status: {lilian_client.get('status')}")
            print(f"   Created: {lilian_client.get('created_at')}")
            print(f"   Last Activity: {lilian_client.get('last_activity')}")
        else:
            print(f"❌ Lilian client not found with ID: {client_id}")
    else:
        print(f"❌ Failed to get clients: {response.status_code}")
    
    print("\n3️⃣ ANALYZING CONVERT BUTTON LOGIC...")
    print("-" * 40)
    
    # Analyze the exact conditions
    stage = lilian_prospect.get('stage')
    aml_kyc_status = lilian_prospect.get('aml_kyc_status')
    converted_to_client = lilian_prospect.get('converted_to_client', False)
    client_id = lilian_prospect.get('client_id')
    
    print(f"Current Values:")
    print(f"   stage: '{stage}'")
    print(f"   aml_kyc_status: '{aml_kyc_status}'")
    print(f"   converted_to_client: {converted_to_client}")
    print(f"   client_id: '{client_id}'")
    
    print(f"\nFrontend Button Logic Analysis:")
    print(f"   prospect.stage === 'won': {stage == 'won'}")
    print(f"   aml_kyc_status === 'clear' || 'approved': {aml_kyc_status in ['clear', 'approved']}")
    print(f"   !converted_to_client: {not converted_to_client}")
    
    should_show_convert = (
        stage == 'won' and 
        aml_kyc_status in ['clear', 'approved'] and 
        not converted_to_client
    )
    
    print(f"\n🎯 SHOULD SHOW CONVERT BUTTON: {should_show_convert}")
    
    if not should_show_convert:
        print(f"\n🚨 REASON CONVERT BUTTON NOT SHOWING:")
        if stage != 'won':
            print(f"   • Stage is '{stage}', needs to be 'won'")
        if aml_kyc_status not in ['clear', 'approved']:
            print(f"   • AML/KYC status is '{aml_kyc_status}', needs to be 'clear' or 'approved'")
        if converted_to_client:
            print(f"   • converted_to_client is {converted_to_client}, needs to be false")
    
    print("\n4️⃣ CHECKING PIPELINE DATA...")
    print("-" * 40)
    
    # Check pipeline endpoint
    response = requests.get(f"{BACKEND_URL}/crm/prospects/pipeline", headers=headers)
    if response.status_code == 200:
        data = response.json()
        pipeline = data.get('pipeline', {})
        won_prospects = pipeline.get('won', [])
        
        lilian_in_won = None
        for prospect in won_prospects:
            if prospect.get('id') == lilian_prospect.get('id'):
                lilian_in_won = prospect
                break
        
        if lilian_in_won:
            print(f"✅ Lilian found in 'won' stage of pipeline:")
            print(f"   Stage: {lilian_in_won.get('stage')}")
            print(f"   AML/KYC Status: {lilian_in_won.get('aml_kyc_status')}")
            print(f"   Converted: {lilian_in_won.get('converted_to_client')}")
            print(f"   Client ID: {lilian_in_won.get('client_id')}")
            
            # Check if pipeline data matches main prospects data
            pipeline_converted = lilian_in_won.get('converted_to_client', False)
            main_converted = lilian_prospect.get('converted_to_client', False)
            
            if pipeline_converted != main_converted:
                print(f"⚠️  DATA INCONSISTENCY:")
                print(f"   Main prospects endpoint: converted_to_client = {main_converted}")
                print(f"   Pipeline endpoint: converted_to_client = {pipeline_converted}")
        else:
            print(f"❌ Lilian not found in 'won' stage of pipeline")
    else:
        print(f"❌ Failed to get pipeline data: {response.status_code}")
    
    print("\n5️⃣ SOLUTION ANALYSIS...")
    print("-" * 40)
    
    if lilian_client and converted_to_client:
        print(f"🔍 ANALYSIS RESULT:")
        print(f"   • Lilian prospect exists with stage='won' and aml_kyc_status='clear'")
        print(f"   • Lilian client exists with ID '{client_id}'")
        print(f"   • converted_to_client=True (this prevents Convert button)")
        print(f"   • This appears to be CORRECT behavior - Lilian is already converted!")
        
        print(f"\n💡 POSSIBLE EXPLANATIONS:")
        print(f"   1. Lilian was already successfully converted to client")
        print(f"   2. The Convert button should NOT show (working as intended)")
        print(f"   3. User might be expecting a different button or action")
        print(f"   4. Frontend might need to show 'Already Converted' status instead")
        
        print(f"\n🎯 RECOMMENDED ACTIONS:")
        print(f"   1. Verify with user if Lilian should already be converted")
        print(f"   2. If she should NOT be converted, reset her status:")
        print(f"      - Set converted_to_client = false")
        print(f"      - Clear client_id = ''")
        print(f"      - Delete client record if needed")
        print(f"   3. If she SHOULD be converted, update frontend to show proper status")
    else:
        print(f"🚨 DATA INCONSISTENCY DETECTED - needs immediate fix")

if __name__ == "__main__":
    main()