import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json

load_dotenv('/app/backend/.env')

async def check_fields():
    """Check exact fields in investments"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Get all investments
    investments = await db.investments.find({}).to_list(None)
    
    for i, inv in enumerate(investments, 1):
        print(f"\n{'='*60}")
        print(f"INVESTMENT #{i}")
        print(f"{'='*60}")
        for key, value in inv.items():
            if key != '_id':
                print(f"{key:30s}: {value}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_fields())
