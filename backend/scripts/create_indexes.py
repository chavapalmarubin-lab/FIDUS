#!/usr/bin/env python3
"""
Create MongoDB Indexes Script
Applies optimized indexes to all FIDUS collections
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.database import connection_manager
from database.schemas import FidusIndexes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndexCreator:
    """Manages index creation for all collections"""
    
    def __init__(self):
        self.db = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = await connection_manager.get_database()
    
    async def create_collection_indexes(self, collection_name: str, indexes: list):
        """Create indexes for a specific collection"""
        try:
            collection = self.db[collection_name]
            
            print(f"\n📊 Creating indexes for '{collection_name}' collection:")
            
            for index_spec in indexes:
                keys = index_spec['keys']
                options = index_spec.get('options', {})
                index_name = options.get('name', f"idx_{list(keys.keys())[0]}")
                
                try:
                    # Create the index
                    await collection.create_index(
                        list(keys.items()),
                        **options
                    )
                    print(f"   ✅ Created index: {index_name} on {list(keys.keys())}")
                    
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ⚠️  Index {index_name} already exists - skipping")
                    else:
                        print(f"   ❌ Failed to create index {index_name}: {e}")
                        raise
            
            # Get index information
            indexes_info = await collection.list_indexes().to_list(length=None)
            print(f"   📈 Total indexes: {len(indexes_info)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes for {collection_name}: {e}")
            return False
    
    async def create_all_indexes(self):
        """Create indexes for all collections"""
        
        print("🔨 MONGODB INDEX CREATION")
        print("=" * 50)
        print("Creating optimized indexes for all FIDUS collections")
        print("This will improve query performance and enforce constraints")
        print("=" * 50)
        
        # Index specifications for each collection
        collections_indexes = {
            'users': FidusIndexes.users_indexes(),
            'investments': FidusIndexes.investments_indexes(),
            'crm_prospects': FidusIndexes.crm_prospects_indexes(),
            'mt5_accounts': FidusIndexes.mt5_accounts_indexes(),
            'sessions': FidusIndexes.sessions_indexes(),
            'documents': FidusIndexes.documents_indexes(),
            'admin_google_sessions': FidusIndexes.admin_google_sessions_indexes()
        }
        
        success_count = 0
        total_collections = len(collections_indexes)
        
        for collection_name, indexes in collections_indexes.items():
            success = await self.create_collection_indexes(collection_name, indexes)
            if success:
                success_count += 1
        
        print(f"\n" + "=" * 50)
        print(f"📊 INDEX CREATION SUMMARY")
        print(f"   Successful: {success_count}/{total_collections} collections")
        print(f"   Failed: {total_collections - success_count}/{total_collections} collections")
        
        if success_count == total_collections:
            print("✅ All indexes created successfully!")
        else:
            print("⚠️  Some indexes failed to create - check logs")
        
        return success_count == total_collections
    
    async def list_all_indexes(self):
        """List all existing indexes"""
        
        print("\n🔍 EXISTING INDEXES OVERVIEW")
        print("=" * 40)
        
        collections = await self.db.list_collection_names()
        
        for collection_name in sorted(collections):
            collection = self.db[collection_name]
            indexes = await collection.list_indexes().to_list(length=None)
            
            print(f"\n📁 Collection: {collection_name}")
            print(f"   Indexes: {len(indexes)}")
            
            for idx in indexes:
                index_name = idx.get('name', 'unnamed')
                index_keys = list(idx.get('key', {}).keys())
                unique = idx.get('unique', False)
                unique_str = " [UNIQUE]" if unique else ""
                
                print(f"   - {index_name}: {index_keys}{unique_str}")
    
    async def drop_all_custom_indexes(self):
        """Drop all custom indexes (keep only _id)"""
        
        print("\n🗑️  DROPPING CUSTOM INDEXES")
        print("=" * 30)
        print("⚠️  This will drop all non-_id indexes")
        
        collections = await self.db.list_collection_names()
        
        for collection_name in collections:
            try:
                collection = self.db[collection_name]
                
                # Get current indexes
                indexes = await collection.list_indexes().to_list(length=None)
                custom_indexes = [idx for idx in indexes if idx.get('name') != '_id_']
                
                if custom_indexes:
                    print(f"   📁 {collection_name}: Dropping {len(custom_indexes)} custom indexes")
                    await collection.drop_indexes()
                    print(f"      ✅ Custom indexes dropped")
                else:
                    print(f"   📁 {collection_name}: No custom indexes to drop")
                    
            except Exception as e:
                print(f"   ❌ Error dropping indexes for {collection_name}: {e}")
    
    async def get_index_usage_stats(self):
        """Get index usage statistics (if available)"""
        
        print("\n📊 INDEX USAGE STATISTICS")
        print("=" * 30)
        
        try:
            # This command requires admin privileges and may not be available in Atlas
            server_status = await self.db.command('serverStatus')
            
            if 'indexCounters' in server_status:
                index_stats = server_status['indexCounters']
                print(f"   Index accesses: {index_stats.get('accesses', 'N/A')}")
                print(f"   Index hits: {index_stats.get('hits', 'N/A')}")
                print(f"   Index misses: {index_stats.get('misses', 'N/A')}")
            else:
                print("   Index usage statistics not available")
                
        except Exception as e:
            print(f"   Index usage statistics not available: {e}")

async def main():
    """Main index creation execution"""
    
    creator = IndexCreator()
    
    try:
        await creator.initialize()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == 'list':
                await creator.list_all_indexes()
            elif command == 'drop':
                await creator.drop_all_custom_indexes()
            elif command == 'stats':
                await creator.get_index_usage_stats()
            else:
                print(f"Unknown command: {command}")
                print("Available commands: list, drop, stats")
        else:
            # Default: create all indexes
            success = await creator.create_all_indexes()
            
            # Show existing indexes
            await creator.list_all_indexes()
            
            if success:
                print("\n🎉 Index creation completed successfully!")
                print("💡 Database is now optimized for production queries")
            else:
                print("\n⚠️  Index creation completed with some errors")
                print("📝 Check logs for detailed error information")
        
    except Exception as e:
        logger.error(f"Index creation failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await connection_manager.close_connection()

if __name__ == "__main__":
    asyncio.run(main())