"""
Find the correct MongoDB database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def find_database():
    mongo_url = os.environ.get('MONGO_URL')
    print(f"MONGO_URL from .env: {mongo_url}")
    print()
    
    client = AsyncIOMotorClient(mongo_url)
    
    print("=" * 80)
    print("LISTING ALL DATABASES")
    print("=" * 80)
    
    # List all databases
    db_list = await client.list_database_names()
    print(f"\nFound {len(db_list)} databases:")
    for db_name in db_list:
        print(f"\n📁 Database: {db_name}")
        db = client[db_name]
        collections = await db.list_collection_names()
        print(f"   Collections ({len(collections)}):")
        for coll in collections:
            count = await db[coll].count_documents({})
            print(f"     - {coll}: {count} documents")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(find_database())
