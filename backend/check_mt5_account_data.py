import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check_data():
    """Check actual MT5 account data in database"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("="*80)
    print("CHECKING MT5 ACCOUNTS DATA IN MONGODB")
    print("="*80)
    
    # Check all accounts that should have managers
    all_accounts = [886557, 886602, 891215, 897589, 885822, 897590, 897591, 897599, 886528]
    
    for acc_num in all_accounts:
        acc = await db.mt5_accounts.find_one({"account": acc_num})
        
        if acc:
            print(f"\n📊 Account {acc_num}:")
            print(f"   Manager: {acc.get('manager_name', 'N/A')}")
            print(f"   Balance: ${acc.get('balance', 0):,.2f}")
            print(f"   Equity: ${acc.get('equity', 0):,.2f}")
            print(f"   Initial Allocation: ${acc.get('initial_allocation', 0):,.2f}")
            print(f"   Profit Withdrawals: ${acc.get('profit_withdrawals', 0):,.2f}")
            print(f"   True P&L: ${acc.get('true_pnl', 0):,.2f}")
            print(f"   Last Updated: {acc.get('last_update', 'N/A')}")
        else:
            print(f"\n❌ Account {acc_num}: NOT FOUND in mt5_accounts collection")
    
    # Check if there are any accounts with capital_source
    print(f"\n{'='*80}")
    print("ACCOUNTS WITH CAPITAL_SOURCE TAG:")
    print(f"{'='*80}")
    
    tagged_accounts = await db.mt5_accounts.find({"capital_source": {"$exists": True}}).to_list(None)
    print(f"Found {len(tagged_accounts)} accounts with capital_source")
    
    for acc in tagged_accounts:
        print(f"  Account {acc['account']}: {acc.get('capital_source')} - Initial: ${acc.get('initial_allocation', 0):,.2f}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_data())
