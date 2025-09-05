#!/usr/bin/env python3
"""
Check MongoDB Collections and Data
=================================
"""

import os
from pymongo import MongoClient

def main():
    # Get MongoDB connection from environment
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {db_name}")
        
        # List all collections
        collections = db.list_collection_names()
        print(f"\n📊 Collections in database: {len(collections)}")
        
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            print(f"   - {collection_name}: {count} documents")
            
            # If it's MT5 related, show some sample data
            if 'mt5' in collection_name.lower():
                print(f"     Sample documents:")
                for doc in db[collection_name].find().limit(2):
                    print(f"       {doc}")
        
        # Check if there are any documents with mt5_login field
        print(f"\n🔍 Searching for documents with 'mt5_login' field:")
        for collection_name in collections:
            count = db[collection_name].count_documents({'mt5_login': {'$exists': True}})
            if count > 0:
                print(f"   - {collection_name}: {count} documents with mt5_login")
                # Show sample
                sample = db[collection_name].find_one({'mt5_login': {'$exists': True}})
                print(f"     Sample: {sample}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()