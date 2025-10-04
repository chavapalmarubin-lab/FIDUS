#!/usr/bin/env python3
"""
Final MongoDB Atlas Connection Test
After IP whitelist has been updated by user
"""

import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime

def test_mongodb_connection():
    """Test MongoDB Atlas connection after IP whitelist update"""
    
    # Load environment variables
    env_file = Path('/app/backend/.env')
    load_dotenv(env_file)
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'fidus_production')
    
    print("=" * 60)
    print("🔍 FINAL MONGODB ATLAS CONNECTION TEST")
    print("=" * 60)
    print(f"Database: {db_name}")
    print(f"Timestamp: {datetime.now()}")
    print(f"Expected IP in whitelist: 34.16.56.64/32 and 0.0.0.0/0")
    print()
    
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return False
    
    try:
        print("🔗 Attempting connection to MongoDB Atlas...")
        
        # Test connection with increased timeout
        client = MongoClient(
            mongo_url, 
            serverSelectionTimeoutMS=15000,  # 15 second timeout
            connectTimeoutMS=10000,          # 10 second connect timeout
            socketTimeoutMS=10000            # 10 second socket timeout
        )
        
        # Test database connection
        result = client.admin.command('ping')
        print("✅ MongoDB Atlas ping successful:", result)
        
        # Access the database
        db = client[db_name]
        
        # Get collections
        collections = db.list_collection_names()
        print(f"\n📊 Database '{db_name}' collections ({len(collections)} total):")
        
        total_documents = 0
        for collection_name in collections:
            try:
                count = db[collection_name].count_documents({})
                total_documents += count
                print(f"  ✅ {collection_name}: {count:,} documents")
            except Exception as e:
                print(f"  ❌ {collection_name}: Error counting - {e}")
        
        print(f"\n📈 Total documents in database: {total_documents:,}")
        
        # Test data retrieval from key collections
        print(f"\n👥 Testing data retrieval:")
        
        # Test users collection
        if 'users' in collections:
            users = list(db['users'].find().limit(3))
            print(f"  Users sample: {len(users)} users found")
            for user in users:
                user_id = user.get('username', user.get('email', user.get('_id', 'Unknown')))
                user_type = user.get('user_type', user.get('type', 'unknown'))
                print(f"    - {user_id} ({user_type})")
        
        # Test investments collection
        if 'investments' in collections:
            investments = list(db['investments'].find().limit(3))
            print(f"  Investments sample: {len(investments)} investments found")
            for investment in investments:
                client_id = investment.get('client_id', 'Unknown')
                amount = investment.get('principal_amount', 0)
                fund = investment.get('fund_code', 'Unknown')
                print(f"    - Client {client_id}: ${amount:,.2f} in {fund}")
        
        # Close connection
        client.close()
        
        print("\n" + "=" * 60)
        print("🎉 MONGODB ATLAS CONNECTION FULLY OPERATIONAL!")
        print("✅ Ready for Phase 2: Database Architecture Implementation")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Details: {e}")
        
        # Provide troubleshooting guidance
        if "SSL" in str(e):
            print(f"\n🔧 SSL Error - Troubleshooting steps:")
            print(f"   1. Verify MongoDB Atlas cluster is running")
            print(f"   2. Check Network Access whitelist includes:")
            print(f"      - 34.16.56.64/32 (our Kubernetes IP)")
            print(f"      - 0.0.0.0/0 (temporary for testing)")
            print(f"   3. Wait 30-60 seconds after adding IPs")
            print(f"   4. Verify cluster has not been paused")
        
        elif "timeout" in str(e).lower():
            print(f"\n🔧 Timeout Error - Possible causes:")
            print(f"   1. Network latency issues")
            print(f"   2. Cluster overloaded")
            print(f"   3. Firewall blocking connection")
        
        else:
            print(f"\n🔧 General Error - Check:")
            print(f"   1. MongoDB Atlas cluster status")
            print(f"   2. Connection string accuracy")
            print(f"   3. Database credentials")
        
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    if success:
        print(f"\n🚀 Next steps:")
        print(f"   1. Proceed to Phase 2: Database Architecture")
        print(f"   2. Setup MT5 Bridge Service on Windows VPS")
        print(f"   3. Begin data validation and cleanup")
    else:
        print(f"\n⏸️  Please resolve MongoDB Atlas connection before proceeding")