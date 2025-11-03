"""
New Month Allocation Script
Adds new MT5 accounts and Money Managers for the new allocation period
"""

import os
from pymongo import MongoClient
from datetime import datetime
import uuid

def main():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("NEW MONTH ALLOCATION - Adding New Accounts and Managers")
    print("=" * 80)
    
    # ===================================================================
    # STEP 1: Add New Money Managers
    # ===================================================================
    print("\n📋 STEP 1: Adding New Money Managers...")
    print("-" * 80)
    
    new_managers = [
        {
            "manager_id": "mexatlantic_5201",
            "manager_name": "MEXAtlantic Provider 5201",  # Placeholder - update with real name
            "profile_type": "copy_trade",
            "profile_url": "https://ratings.mexatlantic.com/widgets/ratings/5201?widgetKey=social_platform_ratings",
            "true_pnl": 0.0,
            "performance_fee_rate": 0.2,
            "stats": {
                "total_trades": 0,
                "win_rate": 0,
                "sharpe_ratio": 0
            },
            "is_active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        },
        {
            "manager_id": "alefloreztrader",
            "manager_name": "alefloreztrader",
            "profile_type": "copy_trade",
            "profile_url": "https://ratings.multibankfx.com/widgets/ratings/4119?widgetKey=social_platform_ratings",
            "true_pnl": 0.0,
            "performance_fee_rate": 0.2,
            "stats": {
                "total_trades": 0,
                "win_rate": 87.47,  # From profile
                "sharpe_ratio": 0.12,  # From profile
                "total_return": 87.47,
                "rating": 92.775,
                "age_days": 517
            },
            "is_active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        }
    ]
    
    for manager in new_managers:
        existing = db.money_managers.find_one({"manager_id": manager["manager_id"]})
        if existing:
            print(f"⚠️  Manager {manager['manager_name']} already exists, skipping...")
        else:
            result = db.money_managers.insert_one(manager)
            print(f"✅ Added manager: {manager['manager_name']}")
            print(f"   ID: {manager['manager_id']}")
            print(f"   Profile: {manager['profile_url']}")
    
    # ===================================================================
    # STEP 2: Add New MT5 Accounts
    # ===================================================================
    print("\n📋 STEP 2: Adding New MT5 Accounts...")
    print("-" * 80)
    
    # Note: Initial allocations should be fetched from MT5 real data
    # For now, using placeholder values based on user's information
    new_accounts = [
        {
            "account": 897590,
            "password": "Fidus13!",
            "name": "CORE - CP Strategy 2",
            "fund_type": "CORE",
            "fund_code": "CORE",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "manager_name": "CP Strategy",
            "target_amount": 0,  # To be updated
            "initial_allocation": 0,  # To be updated with real MT5 data
            "is_active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        },
        {
            "account": 897589,
            "password": "Fidus13!",
            "name": "BALANCE - MEXAtlantic Provider",
            "fund_type": "BALANCE",
            "fund_code": "BALANCE",
            "server": "MEXAtlantic-Real",
            "broker_name": "MEXAtlantic",
            "manager_name": "MEXAtlantic Provider 5201",
            "target_amount": 5000,
            "initial_allocation": 5000,  # User specified $5,000
            "is_active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        },
        {
            "account": 897591,
            "password": "Fidus13!",
            "name": "Interest Segregation 1 - alefloreztrader",
            "fund_type": "SEPARATION",  # Interest Segregation
            "fund_code": "SEPARATION",
            "server": "MultibankFX-Real",
            "broker_name": "MultibankFX",
            "manager_name": "alefloreztrader",
            "target_amount": 0,  # To be updated
            "initial_allocation": 0,  # To be updated with real MT5 data
            "is_active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        },
        {
            "account": 897599,
            "password": "Fidus13!",
            "name": "Interest Segregation 2 - alefloreztrader",
            "fund_type": "SEPARATION",  # Interest Segregation
            "fund_code": "SEPARATION",
            "server": "MultibankFX-Real",
            "broker_name": "MultibankFX",
            "manager_name": "alefloreztrader",
            "target_amount": 0,  # To be updated
            "initial_allocation": 0,  # To be updated with real MT5 data
            "is_active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        }
    ]
    
    for account in new_accounts:
        existing = db.mt5_account_config.find_one({"account": account["account"]})
        if existing:
            print(f"⚠️  Account {account['account']} already exists, skipping...")
        else:
            result = db.mt5_account_config.insert_one(account)
            print(f"✅ Added account: {account['account']}")
            print(f"   Name: {account['name']}")
            print(f"   Fund: {account['fund_type']}")
            print(f"   Manager: {account['manager_name']}")
            print(f"   Initial Allocation: ${account['initial_allocation']:,.2f}")
    
    # ===================================================================
    # STEP 3: Update MT5 Deals Sync Service Account List
    # ===================================================================
    print("\n📋 STEP 3: Account List Update Required...")
    print("-" * 80)
    print("⚠️  NOTE: The mt5_deals_sync_service.py file needs to be updated manually")
    print("   to include the new accounts in the managed_accounts list:")
    print("   Current: [885822, 886066, 886528, 886557, 886602, 891215, 891234]")
    print("   New: Add [897590, 897589, 897591, 897599]")
    print("   Updated list should be:")
    print("   [885822, 886066, 886528, 886557, 886602, 891215, 891234, 897590, 897589, 897591, 897599]")
    
    # ===================================================================
    # STEP 4: Show Current State
    # ===================================================================
    print("\n📊 STEP 4: Current Database State")
    print("-" * 80)
    
    all_accounts = list(db.mt5_account_config.find({}, {"_id": 0, "password": 0}).sort("account", 1))
    print(f"\n📈 Total MT5 Accounts: {len(all_accounts)}")
    
    for acc in all_accounts:
        print(f"\n  Account {acc.get('account')}: {acc.get('name')}")
        print(f"    Fund: {acc.get('fund_type')} | Manager: {acc.get('manager_name')}")
        print(f"    Initial Allocation: ${acc.get('initial_allocation', 0):,.2f}")
    
    all_managers = list(db.money_managers.find({}, {"_id": 0}))
    print(f"\n\n👥 Total Money Managers: {len(all_managers)}")
    
    for mgr in all_managers:
        print(f"\n  {mgr.get('manager_name')}")
        print(f"    ID: {mgr.get('manager_id')}")
        print(f"    Profile: {mgr.get('profile_url', 'N/A')}")
    
    # ===================================================================
    # STEP 5: Summary and Next Steps
    # ===================================================================
    print("\n" + "=" * 80)
    print("✅ NEW MONTH ALLOCATION SCRIPT COMPLETED")
    print("=" * 80)
    print("\n📝 NEXT STEPS:")
    print("   1. ⚠️  Update initial_allocation values with real MT5 equity data")
    print("   2. Update mt5_deals_sync_service.py with new account numbers")
    print("   3. Update mt5_auto_sync_service.py with new account numbers")
    print("   4. Restart backend service: sudo supervisorctl restart backend")
    print("   5. Verify frontend displays all accounts correctly")
    print("   6. Run full sync: POST /api/admin/mt5-deals/sync-all")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
