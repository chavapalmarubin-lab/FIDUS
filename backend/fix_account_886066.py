"""
Fix account 886066 initial allocation
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_account():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("FIXING ACCOUNT 886066 INITIAL ALLOCATION")
    print("="*80)
    print()
    
    # Update account 886066
    result = await db.mt5_accounts.update_one(
        {"account": 886066},
        {"$set": {
            "capital_source": "client",
            "client_id": "client_alejandro",
            "initial_allocation": 10000.00,  # CORRECTED!
            "notes": "Originally allocated $10k to Golden manager, funds removed month 2"
        }}
    )
    
    if result.modified_count > 0:
        print("✅ Account 886066 updated successfully!")
        print("   initial_allocation: $0.00 → $10,000.00")
    else:
        print("⚠️  Account 886066 not modified (may already be correct)")
    print()
    
    # Verify the fix
    print("VERIFICATION:")
    print("-"*80)
    
    client_accounts = await db.mt5_accounts.find({'capital_source': 'client'}).to_list(None)
    
    total = 0
    for acc in client_accounts:
        acc_num = acc.get('account')
        initial = float(acc.get('initial_allocation', 0))
        if hasattr(acc.get('initial_allocation'), 'to_decimal'):
            initial = float(acc.get('initial_allocation').to_decimal())
        
        total += initial
        print(f"Account {acc_num}: ${initial:,.2f}")
    
    print()
    print(f"TOTAL CLIENT ALLOCATION: ${total:,.2f}")
    
    if abs(total - 118151.41) < 0.01:
        print("✅ CORRECT! Matches expected $118,151.41")
    else:
        print(f"❌ ERROR! Expected $118,151.41, got ${total:,.2f}")
    
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_account())
