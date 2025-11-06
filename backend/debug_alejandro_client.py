"""
Debug Alejandro's Client Dashboard Issue
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

def to_float(val):
    if hasattr(val, 'to_decimal'):
        return float(val.to_decimal())
    return float(val) if val else 0.0

async def debug():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("DEBUGGING ALEJANDRO'S CLIENT DASHBOARD")
    print("="*80)
    print()
    
    # Step 1: Find Alejandro's user account
    print("STEP 1: Finding Alejandro's User Account")
    print("-"*80)
    
    users = await db.users.find({"type": "client"}).to_list(None)
    
    print(f"Found {len(users)} client users:")
    for user in users:
        print(f"\n  User ID: {user.get('id')}")
        print(f"  Username: {user.get('username')}")
        print(f"  Name: {user.get('name')}")
        print(f"  Email: {user.get('email')}")
        print(f"  Type: {user.get('type')}")
        print(f"  Status: {user.get('status')}")
    
    # Step 2: Check what client_id is used in investments
    print("\n" + "="*80)
    print("STEP 2: Checking Investments Collection")
    print("-"*80)
    
    investments = await db.investments.find({}).to_list(None)
    
    print(f"Found {len(investments)} investments:")
    for inv in investments:
        print(f"\n  Investment ID: {inv.get('investment_id')}")
        print(f"  Client ID: {inv.get('client_id')}")
        print(f"  Fund Type: {inv.get('fund_type')}")
        print(f"  Amount: ${to_float(inv.get('amount', 0)):,.2f}")
        print(f"  Status: {inv.get('status')}")
    
    # Step 3: Check mt5_accounts client_id field
    print("\n" + "="*80)
    print("STEP 3: Checking MT5 Accounts client_id Field")
    print("-"*80)
    
    accounts = await db.mt5_accounts.find({'capital_source': 'client'}).to_list(None)
    
    print(f"Found {len(accounts)} CLIENT accounts:")
    for acc in accounts:
        acc_num = acc.get('account')
        client_id = acc.get('client_id')
        fund_type = acc.get('fund_type')
        initial = to_float(acc.get('initial_allocation', 0))
        equity = to_float(acc.get('equity', 0))
        
        print(f"\n  Account {acc_num} ({fund_type}):")
        print(f"    client_id: '{client_id}'")
        print(f"    initial_allocation: ${initial:,.2f}")
        print(f"    equity: ${equity:,.2f}")
    
    # Step 4: Check what the client portfolio endpoint would return
    print("\n" + "="*80)
    print("STEP 4: Simulating Client Portfolio Query")
    print("-"*80)
    
    # Try different possible client_ids
    possible_ids = [
        "client_alejandro",
        "alejandro_mariscal",
        "client_alejandro_mariscal",
        "124567"  # His FIDUS account number from screenshot
    ]
    
    for test_id in possible_ids:
        print(f"\nTrying client_id: '{test_id}'")
        
        # Query investments
        inv_query = await db.investments.find_one({"client_id": test_id})
        print(f"  Investments found: {'Yes' if inv_query else 'No'}")
        
        # Query mt5_accounts
        acc_query = await db.mt5_accounts.find({"client_id": test_id}).to_list(None)
        print(f"  MT5 accounts found: {len(acc_query)}")
    
    print()
    print("="*80)
    print("DIAGNOSIS")
    print("="*80)
    print()
    print("The issue is likely one of:")
    print("1. client_id mismatch between users and accounts")
    print("2. client_id field not set correctly on accounts")
    print("3. Client portfolio endpoint using wrong client_id")
    print()
    
    client.close()

asyncio.run(debug())
