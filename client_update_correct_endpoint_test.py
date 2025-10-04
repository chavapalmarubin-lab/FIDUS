#!/usr/bin/env python3
"""
CLIENT UPDATE CORRECT ENDPOINT TESTING
======================================

Testing the actual client update endpoint that exists in the backend:
- PUT /api/admin/clients/{client_id}/update (not /api/clients/{client_id})

This test will verify if the backend endpoint is working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fidus-admin.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def test_correct_client_update_endpoint():
    """Test the correct client update endpoint"""
    session = requests.Session()
    
    # Authenticate as admin
    print("🔐 Authenticating as admin...")
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    })
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return False
    
    token = response.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ Successfully authenticated as admin")
    
    # Get existing clients
    print("\n📋 Getting existing clients...")
    response = session.get(f"{BACKEND_URL}/admin/clients")
    
    if response.status_code != 200:
        print(f"❌ Failed to get clients: {response.status_code}")
        return False
    
    clients_data = response.json()
    if isinstance(clients_data, dict) and 'clients' in clients_data:
        clients = clients_data['clients']
    else:
        clients = clients_data
    
    print(f"✅ Found {len(clients)} clients")
    
    # Find a test client (prefer Alejandro or Salvador)
    test_client = None
    for client in clients:
        name = client.get('name', '').lower()
        if 'alejandro' in name or 'salvador' in name:
            test_client = client
            break
    
    if not test_client:
        test_client = clients[0] if clients else None
    
    if not test_client:
        print("❌ No test client available")
        return False
    
    client_id = test_client.get('id')
    client_name = test_client.get('name')
    print(f"🎯 Testing with client: {client_name} (ID: {client_id})")
    
    # Test the CORRECT endpoint: /admin/clients/{client_id}/update
    print(f"\n🔧 Testing PUT /admin/clients/{client_id}/update...")
    
    update_data = {
        "name": client_name,  # Keep same name
        "email": test_client.get('email', 'test@example.com'),
        "phone": test_client.get('phone', '+1-555-0123'),
        "status": "active",
        "notes": f"Test update at {datetime.now().isoformat()}"
    }
    
    response = session.put(f"{BACKEND_URL}/admin/clients/{client_id}/update", json=update_data)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("✅ SUCCESS: Client update endpoint is working!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        except json.JSONDecodeError:
            print(f"✅ SUCCESS: HTTP 200 but response is not JSON: {response.text}")
            return True
    else:
        print(f"❌ FAILED: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_wrong_endpoint():
    """Test the wrong endpoint that frontend might be calling"""
    session = requests.Session()
    
    # Authenticate as admin
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    })
    
    if response.status_code != 200:
        return False
    
    token = response.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Test the WRONG endpoint that frontend might be calling
    print(f"\n❌ Testing WRONG endpoint: PUT /clients/test_id...")
    
    update_data = {"name": "Test"}
    response = session.put(f"{BACKEND_URL}/clients/test_id", json=update_data)
    
    print(f"Response Status: {response.status_code}")
    if response.status_code == 404:
        print("✅ CONFIRMED: /clients/{id} endpoint does NOT exist (returns 404)")
        return True
    else:
        print(f"❌ UNEXPECTED: Expected 404 but got {response.status_code}")
        return False

if __name__ == "__main__":
    print("🎯 CLIENT UPDATE ENDPOINT INVESTIGATION")
    print("=" * 60)
    
    # Test correct endpoint
    correct_works = test_correct_client_update_endpoint()
    
    # Test wrong endpoint
    wrong_confirmed = test_wrong_endpoint()
    
    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION RESULTS")
    print("=" * 60)
    
    if correct_works and wrong_confirmed:
        print("✅ ROOT CAUSE IDENTIFIED:")
        print("   - Backend endpoint EXISTS at: PUT /api/admin/clients/{id}/update")
        print("   - Frontend is calling WRONG endpoint: PUT /api/clients/{id}")
        print("   - This is a FRONTEND-BACKEND MISMATCH issue")
        print("\n🔧 SOLUTION:")
        print("   - Frontend needs to call: PUT /api/admin/clients/{id}/update")
        print("   - OR Backend needs to add: PUT /api/clients/{id} endpoint")
    elif correct_works:
        print("✅ Backend endpoint is working correctly")
        print("❌ Issue is likely frontend calling wrong endpoint")
    else:
        print("❌ Backend endpoint has issues")
    
    print("\n" + "=" * 60)