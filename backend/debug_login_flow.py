"""
Debug the actual login flow for Alejandro
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def debug():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("DEBUGGING ALEJANDRO'S LOGIN FLOW")
    print("="*80)
    print()
    
    # Step 1: Find user by username
    print("STEP 1: Finding user by username 'alejandro_mariscal'")
    print("-"*80)
    
    user = await db.users.find_one({"username": "alejandro_mariscal"})
    
    if user:
        print(f"✅ User found:")
        print(f"   User ID: {user.get('id')}")
        print(f"   Username: {user.get('username')}")
        print(f"   Name: {user.get('name')}")
        print(f"   Type: {user.get('type')}")
        print()
        
        user_id = user.get('id')
        
        # Step 2: Check what client_id is used after login
        print("STEP 2: After login, frontend will use user_id from token")
        print("-"*80)
        print(f"Frontend will use: '{user_id}'")
        print()
        
        # Step 3: Check investments with this user_id
        print("STEP 3: Checking investments with this user_id")
        print("-"*80)
        
        possible_ids = [
            user_id,
            "client_alejandro",
            "client_alejandro_mariscal"
        ]
        
        for test_id in possible_ids:
            investments = await db.investments.find({"client_id": test_id}).to_list(None)
            mt5_accounts = await db.mt5_accounts.find({"client_id": test_id, "capital_source": "client"}).to_list(None)
            
            print(f"\nTesting client_id: '{test_id}'")
            print(f"  Investments: {len(investments)}")
            print(f"  MT5 Accounts: {len(mt5_accounts)}")
            
            if investments:
                total = sum([float(inv.get('amount', 0)) for inv in investments])
                print(f"  Total Investment: ${total:,.2f}")
            
            if mt5_accounts:
                total_equity = sum([float(acc.get('equity', 0)) for acc in mt5_accounts])
                print(f"  Total Equity: ${total_equity:,.2f}")
        
        print()
        print("="*80)
        print("DIAGNOSIS")
        print("="*80)
        print()
        print(f"The frontend is using user_id: '{user_id}'")
        print(f"But investments are stored with client_id: 'client_alejandro'")
        print()
        print("SOLUTION: Update endpoint mapping to handle user_id → client_id conversion")
        
    else:
        print("❌ User not found with username 'alejandro_mariscal'")
    
    client.close()

asyncio.run(debug())
