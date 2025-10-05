#!/usr/bin/env python3
"""
FINAL SCHEMA VALIDATION TEST
===========================

Test schema validation fix with unique username to avoid conflicts.
"""

import requests
import json
import sys
from datetime import datetime
import random

# Configuration
BACKEND_URL = "https://fidus-finance-api.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def test_schema_validation_final():
    """Test schema validation with unique username"""
    session = requests.Session()
    
    # Authenticate as admin
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    })
    
    if response.status_code != 200:
        print(f"❌ Admin authentication failed: HTTP {response.status_code}")
        return False
    
    token = response.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Test with unique username
    unique_id = random.randint(1000, 9999)
    test_user_data = {
        "username": f"test_schema_{unique_id}",
        "name": "Schema Test User Final",
        "email": f"schema.test.{unique_id}@fidus.com",
        "phone": "+1-555-8888",
        "notes": "Testing schema validation fix - final test",
        "temporary_password": "TempPass123!"
    }
    
    print(f"🧪 Testing schema validation with unique user: {test_user_data['username']}")
    
    response = session.post(f"{BACKEND_URL}/admin/users/create", json=test_user_data)
    
    print(f"📊 Response Status: HTTP {response.status_code}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ SUCCESS: {data}")
        return True
    else:
        print(f"❌ FAILED: {response.text}")
        return False

if __name__ == "__main__":
    print("🎯 FINAL SCHEMA VALIDATION TEST")
    print("=" * 40)
    
    success = test_schema_validation_final()
    
    if success:
        print("\n🎉 Schema validation fix CONFIRMED working!")
    else:
        print("\n❌ Schema validation still has issues")
        sys.exit(1)