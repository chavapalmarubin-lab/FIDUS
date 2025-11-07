import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check():
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Check accounts with client capital_source
    accounts = await db.mt5_accounts.find({
        'capital_source': {'$in': ['client_core', 'client_balance']}
    }).to_list(None)
    
    print(f"Found {len(accounts)} accounts with client capital_source")
    
    total_pnl = 0
    for acc in accounts:
        acc_num = acc.get('account')
        equity = acc.get('equity', 0)
        initial = acc.get('initial_allocation', 0)
        pnl = equity - initial if initial > 0 else 0
        total_pnl += pnl
        
        print(f"Account {acc_num}: Equity ${equity:,.2f} - Initial ${initial:,.2f} = P&L ${pnl:,.2f}")
    
    print(f"\nTotal P&L: ${total_pnl:,.2f}")
    
    client.close()

asyncio.run(check())
