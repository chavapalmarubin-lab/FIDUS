import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def fix_allocations():
    """Fix initial_allocation for accounts that have $0"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("="*80)
    print("FIXING INITIAL ALLOCATIONS FOR ZERO-VALUE ACCOUNTS")
    print("="*80)
    
    # For reinvested_profit and separation accounts, set initial_allocation to a base value
    # so we can track their performance
    
    # These accounts were funded from profits - set initial allocation to first known balance
    updates = [
        {
            "account": 897589,
            "name": "Provider1-Assev",
            "initial_allocation": 5000.00,  # Started with ~$5k
            "capital_source": "reinvested_profit"
        },
        {
            "account": 897590,
            "name": "CP Strategy",  
            "initial_allocation": 16000.00,  # Started with ~$16k
            "capital_source": "reinvested_profit"
        },
        {
            "account": 897591,
            "name": "alefloreztrader",
            "initial_allocation": 5000.00,  # Started with ~$5k
            "capital_source": "separation"
        },
        {
            "account": 897599,
            "name": "alefloreztrader",
            "initial_allocation": 15600.00,  # Started with ~$15.6k
            "capital_source": "separation"
        }
    ]
    
    for update in updates:
        acc_num = update["account"]
        initial = update["initial_allocation"]
        
        # Get current account data
        acc = await db.mt5_accounts.find_one({"account": acc_num})
        if not acc:
            print(f"❌ Account {acc_num} not found")
            continue
        
        current_balance = acc.get("balance", 0)
        current_equity = acc.get("equity", 0)
        
        # Calculate true P&L based on initial allocation
        true_pnl = current_equity - initial
        
        result = await db.mt5_accounts.update_one(
            {"account": acc_num},
            {
                "$set": {
                    "initial_allocation": initial,
                    "true_pnl": true_pnl,
                    "capital_source": update["capital_source"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        print(f"\n✅ Account {acc_num} ({update['name']}):")
        print(f"   Initial Allocation: ${initial:,.2f}")
        print(f"   Current Equity: ${current_equity:,.2f}")
        print(f"   True P&L: ${true_pnl:,.2f}")
        print(f"   Return: {(true_pnl / initial * 100) if initial > 0 else 0:.2f}%")
    
    print(f"\n{'='*80}")
    print("VERIFICATION - ALL ACCOUNTS:")
    print(f"{'='*80}")
    
    all_accounts = await db.mt5_accounts.find(
        {"account": {"$in": [886557, 886602, 891215, 897589, 885822, 897590, 897591, 897599]}}
    ).to_list(None)
    
    total_allocation = 0
    total_equity = 0
    
    for acc in all_accounts:
        acc_num = acc["account"]
        initial = acc.get("initial_allocation", 0)
        equity = acc.get("equity", 0)
        manager = acc.get("manager_name", "N/A")
        
        total_allocation += initial
        total_equity += equity
        
        print(f"\nAccount {acc_num} ({manager}):")
        print(f"  Initial: ${initial:,.2f} | Equity: ${equity:,.2f} | P&L: ${equity - initial:,.2f}")
    
    print(f"\n{'='*80}")
    print(f"TOTALS:")
    print(f"  Total Initial Allocation: ${total_allocation:,.2f}")
    print(f"  Total Current Equity: ${total_equity:,.2f}")
    print(f"  Total P&L: ${total_equity - total_allocation:,.2f}")
    print(f"{'='*80}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_allocations())
