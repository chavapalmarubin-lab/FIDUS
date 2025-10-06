#!/usr/bin/env python3
"""
SCHEMA VALIDATION FIX TEST
==========================

This test specifically verifies the schema validation fix as requested in the review:
- Test POST /api/admin/users/create with the exact test user data provided
- Verify that MongoDB validation errors are resolved
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://tradehub-mt5.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def test_schema_validation_fix():
    """Test the specific schema validation fix with exact test data from review"""
    session = requests.Session()
    
    # Authenticate as admin
    print("🔐 Authenticating as admin...")
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    })
    
    if response.status_code != 200:
        print(f"❌ Admin authentication failed: HTTP {response.status_code}")
        return False
    
    token = response.json().get("token")
    if not token:
        print("❌ No token received from authentication")
        return False
    
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ Admin authentication successful")
    
    # Test the exact user data from the review request
    print("\n🧪 Testing schema validation fix with exact test data...")
    test_user_data = {
        "username": "test_user_schema",
        "name": "Schema Test User",
        "email": "schema.test@fidus.com",
        "phone": "+1-555-9999",
        "notes": "Testing schema validation fix",
        "temporary_password": "TempPass123!"
    }
    
    print(f"Test data: {json.dumps(test_user_data, indent=2)}")
    
    response = session.post(f"{BACKEND_URL}/admin/users/create", json=test_user_data)
    
    print(f"\n📊 Response Status: HTTP {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"Response Data: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response Text: {response.text}")
    
    if response.status_code in [200, 201]:
        print("✅ SCHEMA VALIDATION FIX: SUCCESS")
        print("   User creation worked without MongoDB validation errors")
        return True
    else:
        print("❌ SCHEMA VALIDATION FIX: FAILED")
        print("   User creation still has MongoDB validation errors")
        return False

if __name__ == "__main__":
    print("🎯 SCHEMA VALIDATION FIX TEST")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    success = test_schema_validation_fix()
    
    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Schema validation fix verified successfully!")