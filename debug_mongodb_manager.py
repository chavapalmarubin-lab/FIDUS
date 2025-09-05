#!/usr/bin/env python3
"""
Debug MongoDB Manager
====================

Check what the MongoDB manager is actually doing
"""

import sys
import os

# Add backend to path
sys.path.append('/app/backend')

from mongodb_integration import mongodb_manager

def main():
    print("MongoDB Manager Debug")
    print("=" * 25)
    
    try:
        # Check what database it's connected to
        print(f"Database name: {mongodb_manager.db_name}")
        print(f"Database: {mongodb_manager.db}")
        
        # Check collections
        collections = mongodb_manager.db.list_collection_names()
        print(f"Collections: {collections}")
        
        # Try to get MT5 accounts
        accounts = mongodb_manager.get_all_mt5_accounts()
        print(f"MT5 accounts returned: {len(accounts)}")
        
        if accounts:
            print("First account:")
            print(accounts[0])
        
        # Check if there are any MT5 accounts in the database
        mt5_count = mongodb_manager.db.mt5_accounts.count_documents({})
        print(f"MT5 accounts in database: {mt5_count}")
        
        # Check if there are any documents at all
        total_docs = 0
        for collection_name in collections:
            count = mongodb_manager.db[collection_name].count_documents({})
            total_docs += count
            print(f"{collection_name}: {count} documents")
        
        print(f"Total documents in database: {total_docs}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()