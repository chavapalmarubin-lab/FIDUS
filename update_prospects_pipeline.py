#!/usr/bin/env python3
"""
Update existing prospects from old stages to simplified pipeline
Move 'qualified' prospects to 'negotiation'
Move 'proposal' prospects to 'negotiation'
"""

import requests
import json
from datetime import datetime, timezone

# Configuration
BACKEND_URL = "https://invest-manager-9.preview.emergentagent.com/api"

def authenticate_admin():
    """Authenticate as admin user"""
    session = requests.Session()
    
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        if token:
            session.headers.update({
                'Authorization': f'Bearer {token}'
            })
            print("✅ Admin authentication successful")
            return session
    
    print("❌ Admin authentication failed")
    return None

def update_prospects_pipeline():
    """Update prospects from old stages to simplified pipeline"""
    session = authenticate_admin()
    if not session:
        return False
    
    # Get all prospects
    response = session.get(f"{BACKEND_URL}/crm/prospects")
    if response.status_code != 200:
        print(f"❌ Failed to get prospects: {response.status_code}")
        return False
    
    data = response.json()
    prospects = data.get('prospects', [])
    
    print(f"Found {len(prospects)} prospects")
    
    updates_made = 0
    
    for prospect in prospects:
        prospect_id = prospect.get('id')
        current_stage = prospect.get('stage')
        name = prospect.get('name', 'Unknown')
        
        new_stage = None
        
        # Update old stages to simplified pipeline
        if current_stage == 'qualified':
            new_stage = 'negotiation'
        elif current_stage == 'proposal':
            new_stage = 'negotiation'
        
        if new_stage:
            print(f"Updating {name} ({prospect_id}): {current_stage} → {new_stage}")
            
            update_response = session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json={
                "stage": new_stage
            })
            
            if update_response.status_code == 200:
                print(f"  ✅ Successfully updated {name}")
                updates_made += 1
            else:
                print(f"  ❌ Failed to update {name}: {update_response.status_code}")
        else:
            print(f"No update needed for {name} (stage: {current_stage})")
    
    print(f"\n🎯 Pipeline Update Summary:")
    print(f"Total prospects processed: {len(prospects)}")
    print(f"Updates made: {updates_made}")
    
    return updates_made > 0

if __name__ == "__main__":
    print("🎯 UPDATING PROSPECTS TO SIMPLIFIED PIPELINE")
    print("=" * 50)
    
    success = update_prospects_pipeline()
    
    if success:
        print("✅ Pipeline update completed successfully!")
    else:
        print("❌ Pipeline update failed or no updates needed")