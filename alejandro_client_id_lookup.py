#!/usr/bin/env python3
"""
Alejandro Client ID Database Lookup
Find Alejandro's actual client ID in MongoDB database
"""

import asyncio
import os
import sys
import requests
import json
from datetime import datetime

# Add backend directory to path
sys.path.append('/app/backend')

# Backend URL from environment
BACKEND_URL = "https://mt5-integration.preview.emergentagent.com"

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

async def authenticate_admin():
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
            print(f"🔑 JWT Token: {token[:50]}...")
            return token
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def query_database_for_alejandro(token):
    """Query MongoDB for Alejandro using various search methods"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*80)
    print("🔍 SEARCHING FOR ALEJANDRO MARISCAL ROMERO IN DATABASE")
    print("="*80)
    
    # Search methods to try
    search_methods = [
        {
            "name": "Email Search: alexmar7609@gmail.com",
            "endpoint": "/api/admin/users",
            "description": "Search all users for email alexmar7609@gmail.com"
        },
        {
            "name": "Email Search: alejandro.mariscal@email.com", 
            "endpoint": "/api/admin/users",
            "description": "Search all users for email alejandro.mariscal@email.com"
        },
        {
            "name": "Name Search: Alejandro",
            "endpoint": "/api/admin/users", 
            "description": "Search all users for name containing Alejandro"
        },
        {
            "name": "Username Search: alejandro",
            "endpoint": "/api/admin/users",
            "description": "Search all users for username containing alejandro"
        },
        {
            "name": "Direct Client ID: client_alejandro",
            "endpoint": "/api/admin/users/client_alejandro",
            "description": "Direct lookup using client_alejandro ID"
        },
        {
            "name": "Ready Clients Endpoint",
            "endpoint": "/api/clients/ready-for-investment",
            "description": "Check ready clients list for Alejandro"
        },
        {
            "name": "All Clients List",
            "endpoint": "/api/admin/clients",
            "description": "Get all clients and search for Alejandro"
        }
    ]
    
    found_records = []
    
    for method in search_methods:
        print(f"\n📋 {method['name']}")
        print(f"   {method['description']}")
        
        try:
            response = requests.get(f"{BACKEND_URL}{method['endpoint']}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code} - Success")
                
                # Search through the response data
                alejandro_records = search_for_alejandro_in_data(data, method['name'])
                found_records.extend(alejandro_records)
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    return found_records

def search_for_alejandro_in_data(data, search_method):
    """Search for Alejandro in response data"""
    found_records = []
    
    # Convert data to searchable format
    if isinstance(data, dict):
        search_data = [data] if any(key in data for key in ['id', 'username', 'name', 'email']) else data.get('users', data.get('clients', [data]))
    elif isinstance(data, list):
        search_data = data
    else:
        search_data = [data]
    
    # Flatten if nested
    if isinstance(search_data, dict):
        search_data = list(search_data.values()) if search_data else []
    
    # Search terms for Alejandro
    search_terms = [
        'alejandro', 'mariscal', 'romero',
        'alexmar7609@gmail.com', 'alejandro.mariscal@email.com',
        'client_alejandro', 'alejandrom'
    ]
    
    for item in search_data:
        if isinstance(item, dict):
            # Check all fields for Alejandro-related terms
            item_text = json.dumps(item, default=str).lower()
            
            for term in search_terms:
                if term.lower() in item_text:
                    print(f"   🎯 FOUND MATCH in {search_method}:")
                    print(f"      ID: {item.get('id', 'N/A')}")
                    print(f"      Username: {item.get('username', 'N/A')}")
                    print(f"      Name: {item.get('name', 'N/A')}")
                    print(f"      Email: {item.get('email', 'N/A')}")
                    print(f"      Type: {item.get('type', 'N/A')}")
                    print(f"      Status: {item.get('status', 'N/A')}")
                    
                    found_records.append({
                        'search_method': search_method,
                        'matched_term': term,
                        'record': item
                    })
                    break
    
    if not found_records:
        print(f"   ⚪ No Alejandro records found in {search_method}")
    
    return found_records

def check_client_readiness(token, client_ids):
    """Check client readiness for found client IDs"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n" + "="*80)
    print("🔍 CHECKING CLIENT READINESS FOR FOUND IDs")
    print("="*80)
    
    for client_id in client_ids:
        print(f"\n📋 Checking readiness for: {client_id}")
        
        try:
            # Check individual readiness
            response = requests.get(f"{BACKEND_URL}/api/clients/{client_id}/readiness", headers=headers)
            
            if response.status_code == 200:
                readiness_data = response.json()
                print(f"   ✅ Readiness Status Found:")
                print(f"      Investment Ready: {readiness_data.get('investment_ready', 'N/A')}")
                print(f"      AML/KYC Completed: {readiness_data.get('aml_kyc_completed', 'N/A')}")
                print(f"      Agreement Signed: {readiness_data.get('agreement_signed', 'N/A')}")
                print(f"      Override: {readiness_data.get('readiness_override', 'N/A')}")
                print(f"      Override Reason: {readiness_data.get('readiness_override_reason', 'N/A')}")
            else:
                print(f"   ❌ Readiness check failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error checking readiness: {str(e)}")

def direct_mongodb_query():
    """Attempt direct MongoDB queries if possible"""
    print(f"\n" + "="*80)
    print("🔍 ATTEMPTING DIRECT MONGODB QUERIES")
    print("="*80)
    
    try:
        # Import MongoDB components
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        # Get MongoDB URL from environment
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            print("❌ MONGO_URL not found in environment")
            return
        
        print(f"✅ MongoDB URL found: {mongo_url[:50]}...")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'fidus_production')]
        
        print(f"✅ Connected to database: {db.name}")
        
        # Run async queries
        asyncio.run(run_mongodb_queries(db))
        
    except Exception as e:
        print(f"❌ Direct MongoDB query failed: {str(e)}")

async def run_mongodb_queries(db):
    """Run MongoDB queries for Alejandro"""
    
    # Search queries
    queries = [
        {
            "name": "Email: alexmar7609@gmail.com",
            "collection": "users",
            "query": {"email": "alexmar7609@gmail.com"}
        },
        {
            "name": "Email: alejandro.mariscal@email.com", 
            "collection": "users",
            "query": {"email": "alejandro.mariscal@email.com"}
        },
        {
            "name": "Name contains Alejandro",
            "collection": "users", 
            "query": {"name": {"$regex": "Alejandro", "$options": "i"}}
        },
        {
            "name": "Username contains alejandro",
            "collection": "users",
            "query": {"username": {"$regex": "alejandro", "$options": "i"}}
        },
        {
            "name": "ID: client_alejandro",
            "collection": "users",
            "query": {"id": "client_alejandro"}
        },
        {
            "name": "Client Readiness Collection",
            "collection": "client_readiness", 
            "query": {}
        }
    ]
    
    for query_info in queries:
        print(f"\n📋 MongoDB Query: {query_info['name']}")
        print(f"   Collection: {query_info['collection']}")
        print(f"   Query: {query_info['query']}")
        
        try:
            collection = db[query_info['collection']]
            
            if query_info['query']:
                cursor = collection.find(query_info['query'])
            else:
                cursor = collection.find().limit(10)  # Limit for readiness collection
            
            documents = await cursor.to_list(length=100)
            
            if documents:
                print(f"   ✅ Found {len(documents)} document(s)")
                for doc in documents:
                    print(f"      📄 Document:")
                    print(f"         ID: {doc.get('id', doc.get('_id', 'N/A'))}")
                    print(f"         Username: {doc.get('username', 'N/A')}")
                    print(f"         Name: {doc.get('name', 'N/A')}")
                    print(f"         Email: {doc.get('email', 'N/A')}")
                    if 'client_id' in doc:
                        print(f"         Client ID: {doc.get('client_id', 'N/A')}")
                    if 'investment_ready' in doc:
                        print(f"         Investment Ready: {doc.get('investment_ready', 'N/A')}")
            else:
                print(f"   ⚪ No documents found")
                
        except Exception as e:
            print(f"   ❌ Query error: {str(e)}")

def main():
    """Main function to find Alejandro's client ID"""
    print("🔍 ALEJANDRO CLIENT ID LOOKUP TOOL")
    print("="*80)
    print("Searching for Alejandro Mariscal Romero in MongoDB database")
    print("Target email: alexmar7609@gmail.com")
    print("="*80)
    
    # Step 1: Authenticate as admin
    token = authenticate_admin()
    if not token:
        print("❌ Cannot proceed without admin authentication")
        return
    
    # Step 2: Query database via API endpoints
    found_records = query_database_for_alejandro(token)
    
    # Step 3: Check readiness for found client IDs
    if found_records:
        client_ids = list(set([record['record'].get('id') for record in found_records if record['record'].get('id')]))
        if client_ids:
            check_client_readiness(token, client_ids)
    
    # Step 4: Attempt direct MongoDB queries
    direct_mongodb_query()
    
    # Step 5: Summary
    print(f"\n" + "="*80)
    print("📊 SEARCH SUMMARY")
    print("="*80)
    
    if found_records:
        print(f"✅ Found {len(found_records)} matching record(s) for Alejandro:")
        
        unique_records = {}
        for record in found_records:
            record_id = record['record'].get('id', 'unknown')
            if record_id not in unique_records:
                unique_records[record_id] = record['record']
        
        for record_id, record_data in unique_records.items():
            print(f"\n🎯 CLIENT RECORD:")
            print(f"   ID: {record_id}")
            print(f"   Username: {record_data.get('username', 'N/A')}")
            print(f"   Name: {record_data.get('name', 'N/A')}")
            print(f"   Email: {record_data.get('email', 'N/A')}")
            print(f"   Type: {record_data.get('type', 'N/A')}")
            print(f"   Status: {record_data.get('status', 'N/A')}")
    else:
        print("❌ No records found for Alejandro Mariscal Romero")
        print("   Searched for:")
        print("   - Email: alexmar7609@gmail.com")
        print("   - Email: alejandro.mariscal@email.com") 
        print("   - Name: Alejandro, Mariscal, Romero")
        print("   - Username: alejandro, alejandrom")
        print("   - ID: client_alejandro")
    
    print(f"\n✅ Alejandro Client ID lookup completed")

if __name__ == "__main__":
    main()