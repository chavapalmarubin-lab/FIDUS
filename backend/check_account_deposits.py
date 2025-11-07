import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check_deposits():
    """Check deposit history for accounts with $0 initial allocation"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    # Accounts with $0 initial allocation
    zero_accounts = [897589, 897590, 897591, 897599]
    
    print("="*80)
    print("CHECKING DEPOSIT HISTORY FOR ACCOUNTS WITH $0 INITIAL ALLOCATION")
    print("="*80)
    
    for acc_num in zero_accounts:
        print(f"\n📊 Account {acc_num}:")
        
        # Get account info
        acc = await db.mt5_accounts.find_one({"account": acc_num})
        if acc:
            print(f"   Manager: {acc.get('manager_name', 'N/A')}")
            print(f"   Capital Source: {acc.get('capital_source', 'N/A')}")
            print(f"   Current Balance: ${acc.get('balance', 0):,.2f}")
            print(f"   Current Equity: ${acc.get('equity', 0):,.2f}")
        
        # Find all deposits (entry type 2 = balance operation)
        deposits = await db.mt5_deals_history.find({
            "account_number": acc_num,
            "entry": 2,  # Balance operation
            "profit": {"$gt": 0}  # Positive = deposit
        }).sort("time", 1).to_list(None)
        
        print(f"   Total Deposits Found: {len(deposits)}")
        
        total_deposits = 0
        if deposits:
            print(f"   Deposit History:")
            for dep in deposits:
                amount = dep.get("profit", 0)
                date = dep.get("time", "N/A")
                total_deposits += amount
                print(f"     - {date}: ${amount:,.2f}")
            
            print(f"   TOTAL DEPOSITED: ${total_deposits:,.2f}")
            
            # This should be the initial_allocation
            if total_deposits > 0:
                print(f"   ✅ SHOULD SET initial_allocation = ${total_deposits:,.2f}")
        else:
            print(f"   ⚠️  NO DEPOSITS FOUND - Account may have been transferred or started with balance")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_deposits())
