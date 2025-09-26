#!/usr/bin/env python3
"""
Debug MT5 Data Source
====================

This script will help us understand where the MT5 account data is coming from
since MongoDB is empty but API returns 14 accounts.
"""

import requests
import json
import os
from pymongo import MongoClient

def check_api_response():
    """Check what the API actually returns"""
    print("🔍 CHECKING API RESPONSE")
    print("=" * 30)
    
    # Authenticate first
    base_url = "https://invest-portal-31.preview.emergentagent.com"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get MT5 accounts
    mt5_response = requests.get(f"{base_url}/api/mt5/admin/accounts", headers=headers)
    
    print(f"API Status: {mt5_response.status_code}")
    
    if mt5_response.status_code == 200:
        data = mt5_response.json()
        accounts = data.get('accounts', [])
        print(f"Accounts returned: {len(accounts)}")
        
        if accounts:
            print("\nFirst account details:")
            first_account = accounts[0]
            for key, value in first_account.items():
                print(f"  {key}: {value}")
            
            print(f"\nAll account IDs:")
            for acc in accounts:
                print(f"  - {acc.get('account_id')}: {acc.get('client_id')} ({acc.get('fund_code')})")
    else:
        print(f"❌ API Error: {mt5_response.text}")

def check_mongodb_direct():
    """Check MongoDB directly"""
    print("\n🔍 CHECKING MONGODB DIRECTLY")
    print("=" * 35)
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Check all collections
        collections = db.list_collection_names()
        print(f"Collections: {collections}")
        
        # Check for any MT5 related data
        for collection_name in collections:
            if 'mt5' in collection_name.lower():
                count = db[collection_name].count_documents({})
                print(f"{collection_name}: {count} documents")
                
                if count > 0:
                    sample = db[collection_name].find_one()
                    print(f"Sample: {sample}")
        
        # Check for any documents with mt5_login
        for collection_name in collections:
            count = db[collection_name].count_documents({'mt5_login': {'$exists': True}})
            if count > 0:
                print(f"{collection_name} has {count} documents with mt5_login")
        
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB Error: {str(e)}")

def check_backend_logs():
    """Check if there are any backend logs that might give us clues"""
    print("\n🔍 CHECKING FOR BACKEND LOGS")
    print("=" * 35)
    
    try:
        # Check supervisor logs
        import subprocess
        result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.out.log'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Backend stdout logs:")
            print(result.stdout)
        
        result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.err.log'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Backend stderr logs:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Log check error: {str(e)}")

def main():
    print("MT5 Data Source Debug")
    print("=" * 25)
    
    check_api_response()
    check_mongodb_direct()
    check_backend_logs()

if __name__ == "__main__":
    main()