import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def update_allocations():
    """Update initial_allocation with CORRECT values from Chava"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("="*80)
    print("UPDATING INITIAL ALLOCATIONS PER CHAVA'S SPECIFICATIONS")
    print("="*80)
    print()
    
    # CORRECT allocations from Chava
    correct_allocations = [
        # alefloreztrader - SEPARATION
        {"account": 897591, "initial_allocation": 5000.00, "manager": "alefloreztrader"},
        {"account": 897599, "initial_allocation": 15653.76, "manager": "alefloreztrader"},
        
        # Provider1-Assev (Name # 27) - BALANCE
        {"account": 897589, "initial_allocation": 5000.00, "manager": "Provider1-Assev"},
        
        # TradingHub Gold - BALANCE
        {"account": 886557, "initial_allocation": 10000.00, "manager": "TradingHub Gold"},
        {"account": 891215, "initial_allocation": 70000.00, "manager": "TradingHub Gold"},
        
        # UNO14 Manager - BALANCE (MAM)
        {"account": 886602, "initial_allocation": 15000.00, "manager": "UNO14 Manager"},
        
        # CP Strategy - CORE
        {"account": 897590, "initial_allocation": 16000.00, "manager": "CP Strategy"},
        {"account": 885822, "initial_allocation": 2151.41, "manager": "CP Strategy"}
    ]
    
    for allocation in correct_allocations:
        acc_num = allocation["account"]
        initial = allocation["initial_allocation"]
        manager = allocation["manager"]
        
        # Get current account data
        acc = await db.mt5_accounts.find_one({"account": acc_num})
        if not acc:
            print(f"❌ Account {acc_num} not found in database")
            continue
        
        current_equity = acc.get("equity", 0)
        
        # Calculate true P&L
        true_pnl = current_equity - initial
        
        # Update
        result = await db.mt5_accounts.update_one(
            {"account": acc_num},
            {
                "$set": {
                    "initial_allocation": initial,
                    "true_pnl": true_pnl,
                    "manager_name": manager,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        print(f"✅ Account {acc_num} ({manager}):")
        print(f"   Initial Allocation: ${initial:,.2f}")
        print(f"   Current Equity: ${current_equity:,.2f}")
        print(f"   True P&L: ${true_pnl:,.2f}")
        print(f"   Return: {(true_pnl / initial * 100) if initial > 0 else 0:.2f}%")
        print()
    
    # Verify totals
    print("="*80)
    print("VERIFICATION - TOTAL BY MANAGER:")
    print("="*80)
    print()
    
    managers = {}
    for allocation in correct_allocations:
        manager = allocation["manager"]
        if manager not in managers:
            managers[manager] = {"accounts": [], "total_allocation": 0, "total_equity": 0}
        
        managers[manager]["accounts"].append(allocation["account"])
        managers[manager]["total_allocation"] += allocation["initial_allocation"]
        
        acc = await db.mt5_accounts.find_one({"account": allocation["account"]})
        if acc:
            managers[manager]["total_equity"] += acc.get("equity", 0)
    
    for manager, data in managers.items():
        total_alloc = data["total_allocation"]
        total_equity = data["total_equity"]
        total_pnl = total_equity - total_alloc
        return_pct = (total_pnl / total_alloc * 100) if total_alloc > 0 else 0
        
        print(f"{manager}:")
        print(f"  Accounts: {data['accounts']}")
        print(f"  Total Initial: ${total_alloc:,.2f}")
        print(f"  Total Equity: ${total_equity:,.2f}")
        print(f"  Total P&L: ${total_pnl:,.2f}")
        print(f"  Return: {return_pct:.2f}%")
        print()
    
    # Grand totals
    grand_total_alloc = sum(a["initial_allocation"] for a in correct_allocations)
    all_accounts = await db.mt5_accounts.find(
        {"account": {"$in": [a["account"] for a in correct_allocations]}}
    ).to_list(None)
    grand_total_equity = sum(acc.get("equity", 0) for acc in all_accounts)
    
    print("="*80)
    print(f"GRAND TOTALS:")
    print(f"  Total Initial Allocation: ${grand_total_alloc:,.2f}")
    print(f"  Total Current Equity: ${grand_total_equity:,.2f}")
    print(f"  Total P&L: ${grand_total_equity - grand_total_alloc:,.2f}")
    print("="*80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_allocations())
