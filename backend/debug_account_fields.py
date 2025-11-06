"""
Debug: Check actual field names in collections
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_fields():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("DEBUGGING COLLECTION FIELDS")
    print("="*80)
    print()
    
    # Check mt5_accounts structure
    print("MT5_ACCOUNTS Sample:")
    print("-"*80)
    sample_account = await db.mt5_accounts.find_one()
    if sample_account:
        for key, value in sample_account.items():
            if hasattr(value, 'to_decimal'):
                value = float(value.to_decimal())
            print(f"  {key}: {value}")
    print()
    
    # Get all accounts and their IDs
    print("ALL ACCOUNTS:")
    print("-"*80)
    all_accounts = await db.mt5_accounts.find({}).to_list(None)
    for acc in all_accounts:
        acc_id = acc.get('account_id') or acc.get('account_number') or acc.get('_id')
        fund_type = acc.get('fund_type', 'Unknown')
        equity = acc.get('equity', 0)
        if hasattr(equity, 'to_decimal'):
            equity = float(equity.to_decimal())
        print(f"  ID: {acc_id} | Type: {fund_type} | Equity: ${equity:,.2f}")
    print()
    
    # Check mt5_deals_history structure
    print("MT5_DEALS_HISTORY Sample:")
    print("-"*80)
    sample_deal = await db.mt5_deals_history.find_one({"type": 2})
    if sample_deal:
        for key, value in sample_deal.items():
            if hasattr(value, 'to_decimal'):
                value = float(value.to_decimal())
            value_str = str(value)[:80]
            print(f"  {key}: {value_str}")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_fields())
