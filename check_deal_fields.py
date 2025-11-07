import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check():
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    start_of_month = datetime(2025, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    # Get one sample deal to see field structure
    sample = await db.mt5_deals_history.find_one({'time': {'$gte': start_of_month}})
    
    print("Sample deal structure:")
    print("="*80)
    for key, value in sample.items():
        if key != '_id':
            print(f"{key}: {value}")
    
    print()
    print("="*80)
    print("Checking account_number vs account field:")
    print("="*80)
    
    # Check both field names
    deals_by_account_number = await db.mt5_deals_history.count_documents({
        'time': {'$gte': start_of_month},
        'account_number': {'$exists': True}
    })
    
    deals_by_account = await db.mt5_deals_history.count_documents({
        'time': {'$gte': start_of_month},
        'account': {'$exists': True}
    })
    
    print(f"Deals with 'account_number' field: {deals_by_account_number}")
    print(f"Deals with 'account' field: {deals_by_account}")
    
    client.close()

asyncio.run(check())
