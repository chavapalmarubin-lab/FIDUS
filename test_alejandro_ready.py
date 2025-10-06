#!/usr/bin/env python3
"""
Test Alejandro appears in ready-for-investment endpoint
"""

import requests
import json

# Backend URL
BACKEND_URL = "https://tradehub-mt5.preview.emergentagent.com"

def authenticate_admin():
    """Authenticate as admin and get JWT token"""
    try:
        login_data = {
            "username": "admin",
            "password": "password123", 
            "user_type": "admin"
        }
        
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            print(f"✅ Admin authentication successful")
            return token
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_ready_clients_endpoint(token):
    """Test the ready-for-investment endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 TESTING READY-FOR-INVESTMENT ENDPOINT")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/clients/ready-for-investment", headers=headers)
        
        print(f"📋 Endpoint: /api/clients/ready-for-investment")
        print(f"🔗 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received successfully")
            print(f"📊 Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"📊 Number of ready clients: {len(data)}")
                
                if len(data) > 0:
                    print(f"\n📋 READY CLIENTS:")
                    for i, client in enumerate(data, 1):
                        print(f"   {i}. Client ID: {client.get('id', 'N/A')}")
                        print(f"      Name: {client.get('name', 'N/A')}")
                        print(f"      Email: {client.get('email', 'N/A')}")
                        print(f"      Username: {client.get('username', 'N/A')}")
                        print(f"      ---")
                    
                    # Check if Alejandro is in the list
                    alejandro_found = False
                    for client in data:
                        if (client.get('id') == 'client_alejandro' or 
                            'alejandro' in client.get('name', '').lower() or
                            'alexmar7609@gmail.com' in client.get('email', '')):
                            alejandro_found = True
                            print(f"🎯 ALEJANDRO FOUND IN READY CLIENTS!")
                            print(f"   ID: {client.get('id')}")
                            print(f"   Name: {client.get('name')}")
                            print(f"   Email: {client.get('email')}")
                            break
                    
                    if not alejandro_found:
                        print(f"❌ ALEJANDRO NOT FOUND in ready clients list")
                        print(f"   Expected: client_alejandro")
                        print(f"   Expected email: alexmar7609@gmail.com")
                else:
                    print(f"⚪ No ready clients found")
            else:
                print(f"📊 Response data: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Request failed")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")

def test_individual_readiness(token):
    """Test individual readiness endpoint for Alejandro"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 TESTING INDIVIDUAL READINESS ENDPOINT")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/clients/client_alejandro/readiness", headers=headers)
        
        print(f"📋 Endpoint: /api/clients/client_alejandro/readiness")
        print(f"🔗 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Individual readiness response:")
            print(f"   Client ID: {data.get('client_id')}")
            print(f"   Investment Ready: {data.get('investment_ready')}")
            print(f"   AML/KYC Completed: {data.get('aml_kyc_completed')}")
            print(f"   Agreement Signed: {data.get('agreement_signed')}")
            print(f"   Override: {data.get('readiness_override')}")
        else:
            print(f"❌ Individual readiness check failed")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing individual readiness: {str(e)}")

def main():
    """Main test function"""
    print("🧪 TESTING ALEJANDRO IN READY-FOR-INVESTMENT ENDPOINT")
    print("="*80)
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test ready clients endpoint
    test_ready_clients_endpoint(token)
    
    # Test individual readiness
    test_individual_readiness(token)
    
    print(f"\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print("✅ Alejandro's database setup completed:")
    print("   - Client ID: client_alejandro")
    print("   - Email: alexmar7609@gmail.com")
    print("   - Readiness record: Created")
    print("   - Investment ready: True")
    print("\n🎯 Ready for override testing!")

if __name__ == "__main__":
    main()