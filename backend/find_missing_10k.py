"""
Find the missing $10,000 in client investment calculation
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

def to_float(value):
    if hasattr(value, 'to_decimal'):
        return float(value.to_decimal())
    return float(value) if value else 0.0

async def investigate():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("INVESTIGATING MISSING $10,000 IN CLIENT INVESTMENT")
    print("="*80)
    print()
    
    # Query all CLIENT accounts
    print("STEP 1: All accounts tagged as CLIENT")
    print("-"*80)
    client_accounts = await db.mt5_accounts.find({'capital_source': 'client'}).to_list(None)
    
    total_allocation = 0
    
    for acc in client_accounts:
        acc_num = acc.get('account')
        fund_type = acc.get('fund_type')
        initial_alloc = to_float(acc.get('initial_allocation', 0))
        equity = to_float(acc.get('equity', 0))
        
        total_allocation += initial_alloc
        
        print(f"Account {acc_num} ({fund_type}):")
        print(f"  initial_allocation: ${initial_alloc:,.2f}")
        print(f"  current_equity: ${equity:,.2f}")
        print()
    
    print(f"TOTAL CLIENT ALLOCATION: ${total_allocation:,.2f}")
    print(f"EXPECTED: $118,151.41")
    print(f"DIFFERENCE: ${118151.41 - total_allocation:,.2f}")
    print()
    
    # Check account 886066 specifically
    print("STEP 2: Account 886066 (Golden Manager) Details")
    print("-"*80)
    acc_886066 = await db.mt5_accounts.find_one({'account': 886066})
    
    if acc_886066:
        print(f"Account: {acc_886066.get('account')}")
        print(f"Fund Type: {acc_886066.get('fund_type')}")
        print(f"Capital Source: {acc_886066.get('capital_source')}")
        print(f"Client ID: {acc_886066.get('client_id')}")
        print(f"Initial Allocation: ${to_float(acc_886066.get('initial_allocation', 0)):,.2f}")
        print(f"Current Equity: ${to_float(acc_886066.get('equity', 0)):,.2f}")
        print(f"Manager: {acc_886066.get('manager')}")
    print()
    
    # The problem
    print("="*80)
    print("🚨 PROBLEM IDENTIFIED")
    print("="*80)
    print()
    print("Account 886066 was allocated $10,000 to Golden manager initially.")
    print("Chava moved funds out in month 2 (current equity = $0).")
    print()
    print("BUT: initial_allocation should be $10,000, not $0!")
    print()
    print("The $10k loss should count against Alejandro's investment.")
    print("Current setting: initial_allocation = $0.00 ❌")
    print("Should be: initial_allocation = $10,000.00 ✅")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(investigate())
