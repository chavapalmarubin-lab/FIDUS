"""
Check ACTUAL current equity for all client accounts
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

async def check_equity():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("ACTUAL CURRENT EQUITY - CLIENT ACCOUNTS")
    print("="*80)
    print()
    
    # Get all CLIENT accounts
    client_accounts = await db.mt5_accounts.find({
        'capital_source': 'client'
    }).sort('account', 1).to_list(None)
    
    print(f"Found {len(client_accounts)} client accounts\n")
    
    total_equity = 0
    
    for acc in client_accounts:
        acc_num = acc.get('account')
        fund_type = acc.get('fund_type', 'Unknown')
        initial = to_float(acc.get('initial_allocation', 0))
        equity = to_float(acc.get('equity', 0))
        
        total_equity += equity
        
        print(f"Account {acc_num} ({fund_type}):")
        print(f"  Initial Allocation: ${initial:,.2f}")
        print(f"  Current Equity: ${equity:,.2f}")
        print(f"  Change: ${equity - initial:,.2f}")
        print()
    
    print("="*80)
    print(f"TOTAL CLIENT EQUITY: ${total_equity:,.2f}")
    print("="*80)
    print()
    
    # Show what I calculated vs actual
    print("VERIFICATION:")
    print(f"  My calculation showed: $27,742.41")
    print(f"  Actual from database: ${total_equity:,.2f}")
    print(f"  Difference: ${total_equity - 27742.41:,.2f}")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_equity())
