"""
Update mt5_accounts collection with capital_source tags
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def update_tags():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("UPDATING CAPITAL_SOURCE TAGS")
    print("="*80)
    print()
    
    # Define capital source mapping
    capital_source_map = {
        # CLIENT ACCOUNTS (Alejandro)
        885822: {"capital_source": "client", "client_id": "client_alejandro", "initial_allocation": 18151.41},
        886557: {"capital_source": "client", "client_id": "client_alejandro", "initial_allocation": 80000.00},
        886602: {"capital_source": "client", "client_id": "client_alejandro", "initial_allocation": 10000.00},
        886066: {"capital_source": "client", "client_id": "client_alejandro", "initial_allocation": 0.00},
        886528: {"capital_source": "intermediary", "client_id": None, "initial_allocation": 0.00},
        891234: {"capital_source": "client", "client_id": "client_alejandro", "initial_allocation": 0.00},
        
        # FIDUS ACCOUNTS (House Money)
        891215: {"capital_source": "fidus", "client_id": None, "initial_allocation": 14662.94},
        
        # REINVESTED PROFIT
        897589: {"capital_source": "reinvested_profit", "client_id": None, "initial_allocation": 0.00},
        897590: {"capital_source": "reinvested_profit", "client_id": None, "initial_allocation": 0.00},
        
        # SEPARATION
        897591: {"capital_source": "separation", "client_id": None, "initial_allocation": 0.00},
        897599: {"capital_source": "separation", "client_id": None, "initial_allocation": 0.00},
    }
    
    updated_count = 0
    
    for account_number, tags in capital_source_map.items():
        result = await db.mt5_accounts.update_one(
            {"account": account_number},
            {"$set": tags}
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated account {account_number}: {tags['capital_source']}")
            updated_count += 1
        else:
            # Try to find if account exists
            existing = await db.mt5_accounts.find_one({"account": account_number})
            if existing:
                print(f"⚠️  Account {account_number} found but not modified (may already have tags)")
            else:
                print(f"❌ Account {account_number} not found in database")
    
    print()
    print(f"Total accounts updated: {updated_count}")
    print()
    
    # Verify the updates
    print("="*80)
    print("VERIFICATION - Capital Source Distribution")
    print("="*80)
    print()
    
    for source in ['client', 'fidus', 'reinvested_profit', 'separation', 'intermediary']:
        count = await db.mt5_accounts.count_documents({"capital_source": source})
        accounts = await db.mt5_accounts.find({"capital_source": source}).to_list(None)
        account_nums = [acc.get('account') for acc in accounts]
        print(f"{source.upper()}: {count} accounts - {account_nums}")
    
    print()
    print("✅ Capital source tagging complete!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_tags())
