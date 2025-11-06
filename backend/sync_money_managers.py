import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def sync_managers():
    """Sync money_managers collection with the 5 active managers"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("🔧 SYNCING MONEY MANAGERS COLLECTION")
    print("="*80)
    
    # 5 Active managers per Chava's specifications
    active_managers = [
        {
            "manager_id": "manager_uno14",
            "name": "UNO14 Manager",
            "display_name": "UNO14 Manager",
            "status": "active",
            "type": "MAM",
            "assigned_accounts": [886602],
            "profile_url": "https://www.fxblue.com/users/gestion_global",
            "fund_type": "BALANCE",
            "updated_at": datetime.utcnow()
        },
        {
            "manager_id": "manager_tradinghub_gold",
            "name": "TradingHub Gold",
            "display_name": "TradingHub Gold",
            "status": "active",
            "type": "Copy",
            "assigned_accounts": [886557, 891215],
            "profile_url": "https://ratings.multibankfx.com/widgets/ratings/1359?widgetKey=social_platform_ratings",
            "fund_type": "BALANCE",
            "updated_at": datetime.utcnow()
        },
        {
            "manager_id": "manager_provider1_assev",
            "name": "Provider1-Assev",
            "display_name": "Provider1-Assev",
            "status": "active",
            "type": "Copy",
            "assigned_accounts": [897589],
            "profile_url": "https://ratings.mexatlantic.com/widgets/ratings/5201?widgetKey=social_platform_ratings",
            "fund_type": "BALANCE",
            "updated_at": datetime.utcnow()
        },
        {
            "manager_id": "manager_cp_strategy",
            "name": "CP Strategy",
            "display_name": "CP Strategy",
            "status": "active",
            "type": "Copy",
            "assigned_accounts": [885822, 897590],
            "profile_url": "https://ratings.mexatlantic.com/widgets/ratings/3157?widgetKey=social",
            "fund_type": "CORE",
            "updated_at": datetime.utcnow()
        },
        {
            "manager_id": "manager_alefloreztrader",
            "name": "alefloreztrader",
            "display_name": "alefloreztrader",
            "status": "active",
            "type": "Copy",
            "assigned_accounts": [897591, 897599],
            "profile_url": "https://ratings.multibankfx.com/widgets/ratings/4119?widgetKey=social_platform_ratings",
            "fund_type": "SEPARATION",
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Update GoldenTrade to inactive
    await db.money_managers.update_one(
        {"manager_id": "manager_goldentrade"},
        {
            "$set": {
                "status": "inactive",
                "updated_at": datetime.utcnow()
            }
        }
    )
    print("✅ Set GoldenTrade to inactive")
    
    # Upsert all active managers
    for manager in active_managers:
        result = await db.money_managers.update_one(
            {"manager_id": manager["manager_id"]},
            {"$set": manager},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"✅ Created: {manager['name']}")
        else:
            print(f"✅ Updated: {manager['name']}")
    
    # Verify
    print(f"\n{'='*80}")
    print("VERIFICATION:")
    print(f"{'='*80}")
    
    active = await db.money_managers.find({"status": "active"}).to_list(None)
    inactive = await db.money_managers.find({"status": "inactive"}).to_list(None)
    
    print(f"\n✅ ACTIVE MANAGERS: {len(active)}")
    for mgr in active:
        accounts_str = ", ".join(str(a) for a in mgr.get("assigned_accounts", []))
        print(f"   - {mgr['name']} ({mgr['fund_type']}) - Accounts: {accounts_str}")
    
    print(f"\n⏸️  INACTIVE MANAGERS: {len(inactive)}")
    for mgr in inactive:
        accounts_str = ", ".join(str(a) for a in mgr.get("assigned_accounts", []))
        print(f"   - {mgr['name']} - Accounts: {accounts_str}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(sync_managers())
