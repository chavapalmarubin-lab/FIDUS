"""
Explore all MongoDB collections to find MT5 data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def explore_collections():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_investment']
    
    print("=" * 80)
    print("EXPLORING MONGODB COLLECTIONS")
    print("=" * 80)
    print()
    
    # List all collections
    collections = await db.list_collection_names()
    print(f"Found {len(collections)} collections:")
    for coll in collections:
        count = await db[coll].count_documents({})
        print(f"  📁 {coll}: {count} documents")
    print()
    
    # Check mt5_accounts structure
    print("=" * 80)
    print("MT5_ACCOUNTS STRUCTURE")
    print("=" * 80)
    
    sample_account = await db.mt5_accounts.find_one()
    if sample_account:
        print("\nSample Account Document:")
        for key, value in sample_account.items():
            value_str = str(value)[:100] if len(str(value)) > 100 else str(value)
            print(f"  {key}: {value_str}")
    
    # Get a specific account to see full details
    print("\n" + "=" * 80)
    print("SPECIFIC ACCOUNT ANALYSIS - Account 885822 (CORE)")
    print("=" * 80)
    
    account_885822 = await db.mt5_accounts.find_one({"account_id": 885822})
    if account_885822:
        print("\nFull Document for 885822:")
        for key, value in account_885822.items():
            if hasattr(value, 'to_decimal'):
                value = float(value.to_decimal())
            print(f"  {key}: {value}")
    
    # Check if there are any deal/transaction related fields
    print("\n" + "=" * 80)
    print("CHECKING FOR TRANSACTION DATA IN mt5_accounts")
    print("=" * 80)
    
    # Sample a few accounts to see if they have transaction history
    accounts = await db.mt5_accounts.find().limit(3).to_list(length=3)
    for acc in accounts:
        acc_id = acc.get('account_id', 'Unknown')
        print(f"\n📊 Account {acc_id}:")
        print(f"   Keys: {list(acc.keys())}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(explore_collections())
