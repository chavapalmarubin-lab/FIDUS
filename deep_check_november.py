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
    
    print("="*80)
    print("DEEP CHECK: ALL DEALS IN mt5_deals_history")
    print("="*80)
    print()
    
    # Get total count
    total_count = await db.mt5_deals_history.count_documents({})
    print(f"Total deals in collection: {total_count:,}")
    print()
    
    # Check date range of ALL deals
    oldest = await db.mt5_deals_history.find_one(sort=[('time', 1)])
    newest = await db.mt5_deals_history.find_one(sort=[('time', -1)])
    
    if oldest:
        print(f"Oldest deal: {oldest.get('time')}")
    if newest:
        print(f"Newest deal: {newest.get('time')}")
    print()
    
    # Check if 'time' field exists for all
    deals_with_time = await db.mt5_deals_history.count_documents({'time': {'$exists': True}})
    print(f"Deals with 'time' field: {deals_with_time:,}")
    print()
    
    # Sample some deals from different dates
    print("Sample deals from different time periods:")
    print("-"*80)
    
    # Get deals from early November (without timezone)
    nov_start_naive = datetime(2025, 11, 1)
    nov_deals_naive = await db.mt5_deals_history.count_documents({
        'time': {'$gte': nov_start_naive}
    })
    print(f"Deals >= Nov 1 (naive datetime): {nov_deals_naive:,}")
    
    # Try with UTC timezone
    nov_start_utc = datetime(2025, 11, 1, tzinfo=timezone.utc)
    nov_deals_utc = await db.mt5_deals_history.count_documents({
        'time': {'$gte': nov_start_utc}
    })
    print(f"Deals >= Nov 1 (UTC timezone): {nov_deals_utc:,}")
    
    # Try different date formats
    print()
    print("Checking date field type:")
    sample_deals = await db.mt5_deals_history.find({}).limit(5).to_list(5)
    for i, deal in enumerate(sample_deals, 1):
        time_val = deal.get('time')
        print(f"{i}. time field type: {type(time_val)}, value: {time_val}")
    
    print()
    print("Getting deals by month (last 3 months):")
    print("-"*80)
    
    for month in [9, 10, 11]:
        month_start = datetime(2025, month, 1)
        month_end = datetime(2025, month + 1, 1) if month < 11 else datetime(2025, 12, 1)
        
        deals = await db.mt5_deals_history.find({
            'type': {'$in': [0, 1]},
            'time': {'$gte': month_start, '$lt': month_end}
        }).to_list(None)
        
        volume = sum(d.get('volume', 0) for d in deals)
        rebate = volume * 5.05
        
        month_name = month_start.strftime('%B')
        print(f"{month_name}: {len(deals):,} trades, {volume:.2f} lots → ${rebate:,.2f}")
    
    client.close()

asyncio.run(check())
