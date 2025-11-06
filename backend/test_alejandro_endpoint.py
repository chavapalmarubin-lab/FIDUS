import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def test():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("TESTING ALEJANDRO'S INVESTMENTS ENDPOINT")
    print("="*80)
    print()
    
    # Simulate the endpoint logic
    client_id = "client_alejandro_mariscal"
    actual_client_id = client_id if client_id != "client_alejandro_mariscal" else "client_alejandro"
    
    print(f"Frontend calls with: {client_id}")
    print(f"Backend uses: {actual_client_id}")
    print()
    
    # Query investments
    investments = await db.investments.find({"client_id": actual_client_id}).to_list(None)
    
    print(f"Found {len(investments)} investments:")
    for inv in investments:
        print(f"  - {inv['fund_type']}: ${float(inv['amount']):,.2f}")
    
    # Get MT5 accounts
    mt5_accounts = await db.mt5_accounts.find({"client_id": actual_client_id, "capital_source": "client"}).to_list(None)
    
    print(f"\nFound {len(mt5_accounts)} MT5 accounts:")
    total_equity = 0
    for acc in mt5_accounts:
        equity = float(acc.get('equity', 0))
        if hasattr(acc.get('equity'), 'to_decimal'):
            equity = float(acc.get('equity').to_decimal())
        total_equity += equity
        print(f"  - Account {acc['account']} ({acc['fund_type']}): ${equity:,.2f}")
    
    print(f"\nTotal Client Equity: ${total_equity:,.2f}")
    
    client.close()

asyncio.run(test())
