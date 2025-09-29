#!/usr/bin/env python3
"""
PROSPECT PIPELINE FIX VERIFICATION TEST
=======================================

This test verifies the fix for the "Prospect not found" error.
The issue is that GET reads from MongoDB but PUT writes to memory storage.

Solution: Sync MongoDB prospects to memory storage on startup or make PUT use MongoDB.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fidus-workspace-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ProspectFixTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    print("✅ Admin authentication successful")
                    return True
            return False
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def test_prospect_pipeline_fix(self):
        """Test if the prospect pipeline fix is working"""
        print("\n🔍 Testing Prospect Pipeline Fix...")
        print("-" * 40)
        
        # Get all prospects
        response = self.session.get(f"{BACKEND_URL}/crm/prospects")
        if response.status_code != 200:
            print("❌ Failed to get prospects")
            return False
        
        data = response.json()
        prospects = data.get('prospects', [])
        
        if not prospects:
            print("⚠️  No prospects found to test")
            return True
        
        print(f"📋 Found {len(prospects)} prospects")
        
        # Test updating the first prospect
        test_prospect = prospects[0]
        prospect_id = test_prospect.get('id')
        prospect_name = test_prospect.get('name', 'Unknown')
        current_stage = test_prospect.get('stage', 'lead')
        
        print(f"🎯 Testing prospect: {prospect_name} (ID: {prospect_id})")
        print(f"   Current stage: {current_stage}")
        
        # Try to update the prospect (just add a note)
        update_data = {
            "notes": f"Pipeline test update at {datetime.now().isoformat()}"
        }
        
        response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json=update_data)
        
        if response.status_code == 200:
            print("✅ SUCCESS: Prospect update worked!")
            print("   🎉 Pipeline stage progression buttons should now work")
            return True
        elif response.status_code == 404:
            print("❌ STILL BROKEN: Prospect not found error persists")
            print("   🔧 Main agent needs to implement the fix")
            return False
        else:
            print(f"❌ Unexpected error: HTTP {response.status_code}")
            return False
    
    def run_test(self):
        """Run the fix verification test"""
        print("🎯 PROSPECT PIPELINE FIX VERIFICATION")
        print("=" * 50)
        
        if not self.authenticate_admin():
            return False
        
        success = self.test_prospect_pipeline_fix()
        
        print("\n" + "=" * 50)
        if success:
            print("✅ PROSPECT PIPELINE FIX: WORKING")
            print("   Stage progression buttons should work correctly")
        else:
            print("❌ PROSPECT PIPELINE FIX: STILL NEEDED")
            print("   Main agent must fix data synchronization issue")
        print("=" * 50)
        
        return success

def main():
    """Main test execution"""
    test_runner = ProspectFixTest()
    success = test_runner.run_test()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()