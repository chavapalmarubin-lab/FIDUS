"""
Test what the API actually returns for Alejandro
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

async def test_api():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    client_id = "client_alejandro"
    
    print("="*80)
    print("TESTING API RESPONSES FOR ALEJANDRO")
    print("="*80)
    print()
    
    # Test 1: Investments endpoint
    print("TEST 1: /api/clients/client_alejandro/investments")
    print("-"*80)
    
    # Handle client_id mapping
    actual_client_id = client_id
    if client_id == "client_alejandro_mariscal":
        actual_client_id = "client_alejandro"
    
    investments = await db.investments.find({"client_id": actual_client_id}).to_list(None)
    
    # Convert to JSON-serializable format
    investments_json = []
    for inv in investments:
        inv_dict = {
            "investment_id": inv.get('investment_id'),
            "client_id": inv.get('client_id'),
            "fund_type": inv.get('fund_type'),
            "amount": float(inv.get('amount', 0)),
            "initial_amount": float(inv.get('initial_amount', 0)),
            "status": inv.get('status'),
            "start_date": inv.get('start_date'),
            "interest_rate": float(inv.get('interest_rate', 0)),
            "payment_frequency": inv.get('payment_frequency')
        }
        investments_json.append(inv_dict)
    
    print(f"Found {len(investments_json)} investments")
    print(json.dumps(investments_json, indent=2))
    print()
    
    # Test 2: MT5 Accounts endpoint
    print("TEST 2: /api/mt5/accounts/client_alejandro")
    print("-"*80)
    
    mt5_accounts = await db.mt5_accounts.find({
        "client_id": actual_client_id,
        "capital_source": "client"
    }).to_list(None)
    
    print(f"Found {len(mt5_accounts)} MT5 accounts")
    
    for acc in mt5_accounts:
        equity = float(acc.get('equity', 0))
        if hasattr(acc.get('equity'), 'to_decimal'):
            equity = float(acc.get('equity').to_decimal())
        
        print(f"  Account {acc.get('account')} ({acc.get('fund_type')}): ${equity:,.2f}")
    
    print()
    
    # Test 3: Check what frontend expects
    print("TEST 3: What the frontend expects")
    print("-"*80)
    print("The frontend shows 4 fund types:")
    print("  - CORE FUND")
    print("  - BALANCE FUND")
    print("  - DYNAMIC FUND (not in our data)")
    print("  - UNLIMITED FUND (not in our data)")
    print()
    print("Our investments:")
    for inv in investments_json:
        print(f"  - {inv['fund_type']}: ${inv['amount']:,.2f}")
    print()
    print("Issue: Frontend might be looking for specific fund names!")
    
    client.close()

asyncio.run(test_api())
