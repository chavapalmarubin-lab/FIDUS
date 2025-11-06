import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check_managers():
    """Check what managers actually exist in the database"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("📊 EXISTING MANAGERS IN DATABASE:")
    print("="*60)
    
    managers = await db.money_managers.find({}).to_list(None)
    
    for i, mgr in enumerate(managers, 1):
        print(f"\n{i}. Manager:")
        print(f"   ID: {mgr.get('_id')}")
        print(f"   manager_id: {mgr.get('manager_id')}")
        print(f"   name: {mgr.get('name')}")
        print(f"   display_name: {mgr.get('display_name')}")
        print(f"   status: {mgr.get('status')}")
        print(f"   assigned_accounts: {mgr.get('assigned_accounts')}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL MANAGERS: {len(managers)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_managers())
