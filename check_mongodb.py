#!/usr/bin/env python3
"""
Check MongoDB connectivity and current database state
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime

# Get MongoDB URL from environment
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_investment_db')

def check_mongodb():
    try:
        print("🔍 Checking MongoDB connectivity...")
        print(f"MongoDB URL: {MONGO_URL}")
        
        # Connect to MongoDB
        client = MongoClient(MONGO_URL)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database
        db_name = MONGO_URL.split('/')[-1]
        db = client[db_name]
        
        print(f"📊 Database: {db_name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📋 Collections found: {len(collections)}")
        
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"   - {collection_name}: {count} documents")
            
            # Show sample document if exists
            if count > 0:
                sample = collection.find_one()
                print(f"     Sample: {list(sample.keys()) if sample else 'None'}")
        
        # Database statistics
        stats = db.command("dbstats")
        print(f"📈 Database size: {stats.get('dataSize', 0)} bytes")
        print(f"📈 Storage size: {stats.get('storageSize', 0)} bytes")
        
        # Test write operation
        test_collection = db['connection_test']
        test_doc = {
            'test': True,
            'timestamp': datetime.now(),
            'message': 'Production readiness test'
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test write successful: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({'_id': result.inserted_id})
        print("✅ Test cleanup successful")
        
        return True, db_name, collections
        
    except Exception as e:
        print(f"❌ MongoDB error: {str(e)}")
        return False, None, []

if __name__ == "__main__":
    success, db_name, collections = check_mongodb()
    
    if success:
        print("\n🎉 MongoDB is ready for production!")
        print(f"Database: {db_name}")
        print(f"Collections: {collections}")
    else:
        print("\n💥 MongoDB needs attention before production deployment")
        sys.exit(1)