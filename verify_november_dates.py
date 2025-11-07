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
    now = datetime.now(timezone.utc)
    
    print("="*80)
    print("VERIFYING NOVEMBER DEALS")
    print("="*80)
    print(f"Start: {start_of_month}")
    print(f"Now: {now}")
    print()
    
    # Get first and last deal in November
    first_deal = await db.mt5_deals_history.find_one(
        {'time': {'$gte': start_of_month}},
        sort=[('time', 1)]
    )
    
    last_deal = await db.mt5_deals_history.find_one(
        {'time': {'$gte': start_of_month}},
        sort=[('time', -1)]
    )
    
    if first_deal:
        print(f"First deal in November: {first_deal.get('time')}")
    if last_deal:
        print(f"Last deal in November: {last_deal.get('time')}")
    
    print()
    
    # Count by day
    print("Deals by Day in November:")
    print("-"*80)
    
    for day in range(1, 8):
        day_start = datetime(2025, 11, day, 0, 0, 0, tzinfo=timezone.utc)
        day_end = datetime(2025, 11, day, 23, 59, 59, tzinfo=timezone.utc)
        
        deals = await db.mt5_deals_history.find({
            'type': {'$in': [0, 1]},
            'time': {'$gte': day_start, '$lte': day_end}
        }).to_list(None)
        
        volume = sum(d.get('volume', 0) for d in deals)
        rebate = volume * 5.05
        
        print(f"Nov {day}: {len(deals):,} trades, {volume:.2f} lots → ${rebate:,.2f}")
    
    print("-"*80)
    
    # Total
    all_deals = await db.mt5_deals_history.find({
        'type': {'$in': [0, 1]},
        'time': {'$gte': start_of_month, '$lte': now}
    }).to_list(None)
    
    total_vol = sum(d.get('volume', 0) for d in all_deals)
    total_rebate = total_vol * 5.05
    
    print(f"TOTAL (Nov 1-7): {len(all_deals):,} trades, {total_vol:.2f} lots → ${total_rebate:,.2f}")
    
    client.close()

asyncio.run(check())
