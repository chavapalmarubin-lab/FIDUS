import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check():
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("ALL MT5 ACCOUNTS:")
    print("="*80)
    
    accounts = await db.mt5_accounts.find({}).to_list(None)
    
    for acc in sorted(accounts, key=lambda x: x.get('account', 0)):
        acc_num = acc.get('account')
        capital = acc.get('capital_source', 'unknown')
        manager = acc.get('manager_name', 'N/A')
        status = acc.get('status', 'unknown')
        
        print(f"{acc_num}: {capital:15s} | {manager:20s} | Status: {status}")
    
    print()
    print("Per your initial allocations, ACTIVE CLIENT accounts for rebates should be:")
    print("  886557 (TradingHub) - BALANCE")
    print("  886602 (UNO14) - BALANCE") 
    print("  897589 (Provider1-Assev) - BALANCE")
    print("  885822 (CP Strategy) - CORE")
    print("  897590 (CP Strategy) - CORE")
    
    print()
    print("Should NOT include:")
    print("  891215 - FIDUS house capital")
    print("  886066 - GoldenTrade (inactive)")
    print("  897591, 897599 - Separation accounts")
    
    client.close()

asyncio.run(check())
