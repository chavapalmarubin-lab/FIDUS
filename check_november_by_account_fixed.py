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
    
    start_of_month = datetime(2025, 11, 1, tzinfo=timezone.utc)
    end_of_month = datetime.now(timezone.utc)
    
    start_ts = int(start_of_month.timestamp())
    end_ts = int(end_of_month.timestamp())
    
    print("="*80)
    print("NOVEMBER BROKER REBATES BY ACCOUNT")
    print("="*80)
    print()
    
    # Get all November deals
    deals = await db.mt5_deals_history.find({
        'type': {'$in': [0, 1]},
        '$or': [
            {'time': {'$gte': start_of_month, '$lte': end_of_month}},
            {'time': {'$gte': start_ts, '$lte': end_ts}}
        ]
    }).to_list(None)
    
    # Remove duplicates
    unique_deals = {d.get('ticket', id(d)): d for d in deals}.values()
    deals = list(unique_deals)
    
    # Group by account
    by_account = {}
    for deal in deals:
        acc = deal.get('account_number', deal.get('account', 'Unknown'))
        vol = deal.get('volume', 0)
        
        if acc not in by_account:
            by_account[acc] = {'trades': 0, 'volume': 0}
        
        by_account[acc]['trades'] += 1
        by_account[acc]['volume'] += vol
    
    # Show each account
    total_vol = 0
    total_trades = 0
    
    for acc in sorted(by_account.keys()):
        data = by_account[acc]
        vol = data['volume']
        trades = data['trades']
        rebate = vol * 5.05
        
        total_vol += vol
        total_trades += trades
        
        # Get account info
        acc_doc = await db.mt5_accounts.find_one({'account': acc})
        manager = acc_doc.get('manager_name', 'Unknown') if acc_doc else 'Unknown'
        status = acc_doc.get('status', 'unknown') if acc_doc else 'unknown'
        
        status_emoji = "✅" if status == "active" else "⏸️"
        
        print(f"{status_emoji} Account {acc} ({manager}):")
        print(f"   Trades: {trades:,}, Volume: {vol:.2f} lots → ${rebate:,.2f}")
        print()
    
    print("="*80)
    print(f"TOTAL: {total_trades:,} trades, {total_vol:.2f} lots → ${total_vol * 5.05:,.2f}")
    print("="*80)
    
    client.close()

asyncio.run(check())
