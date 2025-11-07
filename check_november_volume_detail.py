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
    
    # Check EACH active client account
    active_accounts = [886557, 886602, 885822, 897589, 897590]
    
    print("="*80)
    print("NOVEMBER VOLUME BY ACTIVE CLIENT ACCOUNT")
    print("="*80)
    print()
    
    total_vol = 0
    total_trades = 0
    
    for acc in active_accounts:
        deals = await db.mt5_deals_history.find({
            'type': {'$in': [0, 1]},
            'time': {'$gte': start_of_month},
            'account_number': acc
        }).to_list(None)
        
        volume = sum(d.get('volume', 0) for d in deals)
        rebate = volume * 5.05
        
        total_vol += volume
        total_trades += len(deals)
        
        acc_doc = await db.mt5_accounts.find_one({'account': acc})
        manager = acc_doc.get('manager_name', 'N/A') if acc_doc else 'N/A'
        
        print(f"Account {acc} ({manager}):")
        print(f"  Trades: {len(deals):,}")
        print(f"  Volume: {volume:.2f} lots")
        print(f"  Rebate: ${rebate:,.2f}")
        print()
    
    print("="*80)
    print(f"TOTAL: {total_trades:,} trades, {total_vol:.2f} lots → ${total_vol * 5.05:,.2f}")
    print("="*80)
    print()
    print(f"Expected: ~$1,300 (you mentioned)")
    print(f"That would be: {1300 / 5.05:.2f} lots")
    
    client.close()

asyncio.run(check())
