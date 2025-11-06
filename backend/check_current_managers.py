import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("CURRENT MANAGERS IN DATABASE")
    print("="*80)
    print()
    
    managers = await db.money_managers.find({}).to_list(None)
    
    print(f"Found {len(managers)} managers:")
    print()
    
    for mgr in managers:
        mgr_id = mgr.get('manager_id')
        name = mgr.get('name', 'Unknown')
        status = mgr.get('status', 'Unknown')
        accounts = mgr.get('accounts', [])
        
        print(f"Manager ID: {mgr_id}")
        print(f"  Name: {name}")
        print(f"  Status: {status}")
        print(f"  Accounts: {accounts}")
        print()
    
    # Check mt5_accounts for manager assignments
    print("="*80)
    print("MT5 ACCOUNTS - MANAGER ASSIGNMENTS")
    print("="*80)
    print()
    
    accounts = await db.mt5_accounts.find({}).sort('account', 1).to_list(None)
    
    for acc in accounts:
        acc_num = acc.get('account')
        manager = acc.get('manager', 'None')
        fund_type = acc.get('fund_type', 'Unknown')
        
        print(f"Account {acc_num} ({fund_type}): Manager = {manager}")
    
    client.close()

asyncio.run(check())
