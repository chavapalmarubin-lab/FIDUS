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
    
    # Start of November
    start_of_month = datetime(2025, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    
    print("="*80)
    print("BROKER REBATES VOLUME BREAKDOWN (November 2025)")
    print("="*80)
    print()
    
    # Get all deals in November
    deals = await db.mt5_deals_history.find({
        'type': {'$in': [0, 1]},
        'time': {'$gte': start_of_month, '$lte': now}
    }).to_list(None)
    
    print(f"Total deals found: {len(deals)}")
    print()
    
    # Group by account
    account_volumes = {}
    for deal in deals:
        acc = deal.get('account_number', deal.get('account', 'Unknown'))
        volume = deal.get('volume', 0)
        
        if acc not in account_volumes:
            account_volumes[acc] = {'trades': 0, 'volume': 0}
        
        account_volumes[acc]['trades'] += 1
        account_volumes[acc]['volume'] += volume
    
    # Show by account
    print("Volume by Account:")
    print("-" * 80)
    
    total_volume = 0
    for acc, data in sorted(account_volumes.items(), key=lambda x: x[1]['volume'], reverse=True):
        volume = data['volume']
        trades = data['trades']
        rebate = volume * 5.05
        total_volume += volume
        
        print(f"Account {acc}: {trades:,} trades, {volume:.2f} lots → ${rebate:,.2f}")
    
    print("-" * 80)
    print(f"TOTAL: {len(deals):,} trades, {total_volume:.2f} lots → ${total_volume * 5.05:,.2f}")
    print()
    
    # Check which accounts are client vs others
    print("="*80)
    print("ACCOUNT TYPES:")
    print("="*80)
    
    for acc in sorted(account_volumes.keys()):
        acc_doc = await db.mt5_accounts.find_one({'account': acc})
        if acc_doc:
            capital_source = acc_doc.get('capital_source', 'unknown')
            manager = acc_doc.get('manager_name', 'N/A')
            print(f"Account {acc}: {capital_source:15s} - {manager}")
    
    print()
    print("Expected rebate (~$1,300): Volume should be ~257 lots")
    print(f"Current calculation: {total_volume:.2f} lots = ${total_volume * 5.05:,.2f}")
    
    client.close()

asyncio.run(check())
