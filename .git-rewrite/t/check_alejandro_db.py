#!/usr/bin/env python3
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def check_alejandro():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'fidus_production')]
    
    print("🔍 Checking Alejandro's data in MongoDB...")
    
    # Find Alejandro in users collection
    user = await db.users.find_one({'username': 'alejandro_mariscal'})
    if user:
        print(f'✅ Alejandro User ID: {user.get("id")}')
        print(f'✅ Alejandro Email: {user.get("email")}')
        client_id = user.get('id')
    else:
        print('❌ User not found, trying client_alejandro')
        client_id = 'client_alejandro'
    
    # Check client_readiness
    readiness = await db.client_readiness.find_one({'client_id': client_id})
    if readiness:
        print(f'✅ Readiness Record found: investment_ready={readiness.get("investment_ready")}')
    else:
        print('❌ No readiness record found')
    
    # Check investments
    investments = await db.investments.find({'client_id': client_id}).to_list(length=None)
    print(f'📊 Investments found: {len(investments)}')
    total_investments = 0
    for inv in investments:
        amount = inv.get("principal_amount", 0)
        total_investments += amount
        print(f'  - {inv.get("fund_code")}: ${amount:,.2f}')
    print(f'💰 Total Investment Amount: ${total_investments:,.2f}')
    
    # Check MT5 accounts
    mt5_accounts = await db.mt5_accounts.find({'client_id': client_id}).to_list(length=None)
    print(f'🏦 MT5 Accounts found: {len(mt5_accounts)}')
    total_mt5_balance = 0
    for acc in mt5_accounts:
        balance = acc.get("balance", 0)
        total_mt5_balance += balance
        print(f'  - {acc.get("mt5_account_number")}: ${balance:,.2f} ({acc.get("broker_name")})')
    print(f'💰 Total MT5 Balance: ${total_mt5_balance:,.2f}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_alejandro())