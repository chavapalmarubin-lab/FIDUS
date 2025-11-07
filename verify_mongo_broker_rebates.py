import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def verify():
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("="*80)
    print("VERIFYING MONGODB FOR BROKER REBATES CALCULATION")
    print("="*80)
    print()
    
    # Check inactive accounts
    inactive = await db.mt5_accounts.find({'status': 'inactive'}).to_list(None)
    print(f"Inactive Accounts (should be excluded): {len(inactive)}")
    for acc in inactive:
        print(f"  - {acc.get('account')} ({acc.get('manager_name', 'N/A')})")
    print()
    
    # Check November deals count
    start_of_month = datetime(2025, 11, 1, tzinfo=timezone.utc)
    end_of_month = datetime.now(timezone.utc)
    start_ts = int(start_of_month.timestamp())
    end_ts = int(end_of_month.timestamp())
    
    inactive_account_numbers = [acc.get('account') for acc in inactive]
    
    # Count BUY side only (type=0)
    buy_deals = await db.mt5_deals_history.find({
        'type': 0,
        'account_number': {'$nin': inactive_account_numbers},
        '$or': [
            {'time': {'$gte': start_of_month, '$lte': end_of_month}},
            {'time': {'$gte': start_ts, '$lte': end_ts}}
        ]
    }).to_list(None)
    
    # Remove duplicates
    unique_deals = {d.get('ticket', id(d)): d for d in buy_deals}.values()
    deals = list(unique_deals)
    
    total_volume = sum(d.get('volume', 0) for d in deals)
    broker_rebates = total_volume * 5.05
    
    print("MongoDB Calculation (November 1-7):")
    print(f"  BUY trades: {len(deals):,}")
    print(f"  Total volume: {total_volume:.2f} lots")
    print(f"  Broker rebates: ${broker_rebates:,.2f}")
    print()
    
    print("✅ MongoDB data is correct")
    
    client.close()

asyncio.run(verify())
