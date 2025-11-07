import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check():
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Check the accounts that are aggregated
    accounts = [886557, 891215, 885822, 897590]
    
    for acc_num in accounts:
        acc = await db.mt5_accounts.find_one({'account': acc_num})
        if acc:
            equity = acc.get('equity', 0)
            initial = acc.get('initial_allocation', 0)
            withdrawals = acc.get('profit_withdrawals', 0)
            
            # What the service calculates
            service_pnl = equity + withdrawals - initial
            # What it should be
            correct_pnl = equity - initial
            
            print(f"Account {acc_num}:")
            print(f"  Equity: ${equity:,.2f}")
            print(f"  Initial: ${initial:,.2f}")
            print(f"  Profit Withdrawals: ${withdrawals:,.2f}")
            print(f"  Service calculates: ${service_pnl:,.2f} (equity + withdrawals - initial)")
            print(f"  SHOULD BE: ${correct_pnl:,.2f} (equity - initial)")
            print()
    
    client.close()

asyncio.run(check())
