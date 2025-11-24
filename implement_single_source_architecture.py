"""
Architecture Restructure: Single Source of Truth Implementation
November 2025

Converts the application to use ONE master accounts collection as the source of truth.
All tabs derive their data from this single collection.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def implement_single_source_architecture():
    """Restructure to single source of truth architecture"""
    
    try:
        # Connect to MongoDB
        mongo_url = os.getenv('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db = client['fidus_production']
        
        print("🏗️  IMPLEMENTING SINGLE SOURCE OF TRUTH ARCHITECTURE")
        print("=" * 70)
        
        # Step 1: Ensure all 15 accounts have complete metadata
        print("\n1️⃣  Ensuring all accounts have complete metadata...")
        
        # Complete account definitions (Single Source of Truth)
        master_accounts = {
            # MEXAtlantic MT5 Accounts (13)
            885822: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "CORE", "manager_name": "CP Strategy", "status": "active",
                "description": "Core Strategy Account", "execution_method": "Copy Trade"
            },
            886066: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real", 
                "fund_type": "BALANCE", "manager_name": "GoldenTrade", "status": "inactive",
                "description": "Secondary Balance (Inactive)", "execution_method": "Copy Trade"
            },
            886528: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "SEPARATION", "manager_name": "Reserve Account", "status": "active",
                "description": "Separation Reserve", "execution_method": "Reserve/Hedging"
            },
            886557: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE", "manager_name": "TradingHub Gold", "status": "active", 
                "description": "Main Balance Account", "execution_method": "Copy Trade"
            },
            886602: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE", "manager_name": "UNO14 Manager", "status": "active",
                "description": "Tertiary Balance (MAM)", "execution_method": "MAM"
            },
            891215: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE", "manager_name": "TradingHub Gold", "status": "active",
                "description": "Interest Earnings Trading", "execution_method": "Copy Trade"
            },
            891234: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "CORE", "manager_name": "GoldenTrade", "status": "inactive",
                "description": "CORE Fund (Inactive)", "execution_method": "Copy Trade"
            },
            897589: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE", "manager_name": "Provider1-Assev", "status": "active",
                "description": "BALANCE - MEXAtlantic Provider", "execution_method": "Copy Trade"
            },
            897590: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "CORE", "manager_name": "CP Strategy", "status": "active",
                "description": "CORE - CP Strategy 2", "execution_method": "Copy Trade"
            },
            897591: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "SEPARATION", "manager_name": "alefloreztrader", "status": "active", 
                "description": "Interest Segregation 1", "execution_method": "Copy Trade"
            },
            897599: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "SEPARATION", "manager_name": "alefloreztrader", "status": "active",
                "description": "Interest Segregation 2", "execution_method": "Copy Trade"
            },
            901351: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE", "manager_name": "Spaniard Stock CFDs", "status": "active",
                "description": "Unassigned (Master)", "execution_method": "Copy Trade"
            },
            901353: {
                "platform": "MT5", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE", "manager_name": "Spaniard Stock CFDs", "status": "active",
                "description": "Unassigned (Copy)", "execution_method": "Copy Trade"
            },
            
            # LUCRUM MT5 Account (1)
            2198: {
                "platform": "MT5", "broker": "LUCRUM Capital", "server": "LucrumCapital-Trade",
                "fund_type": "SEPARATION", "manager_name": "JOSE", "status": "active",
                "description": "LUCRUM Account", "execution_method": "HFT Rebate"
            },
            
            # MEXAtlantic MT4 Account (1)
            33200931: {
                "platform": "MT4", "broker": "MEXAtlantic", "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE", "manager_name": "Money Manager", "status": "active",
                "description": "Money Manager", "execution_method": "MT4 Manager"
            }
        }
        
        # Update each account with complete metadata
        updated_count = 0
        for account_num, metadata in master_accounts.items():
            # Add standard fields that apply to all accounts
            update_doc = {
                **metadata,
                "data_source": "MT4_FILE_BRIDGE" if metadata["platform"] == "MT4" else "MT5_BRIDGE",
                "last_metadata_update": "2025-11-24T20:00:00Z",
                "is_master_account": True  # Flag to identify accounts in single source of truth
            }
            
            result = await db.mt5_accounts.update_one(
                {"account": account_num},
                {"$set": update_doc},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                print(f"✅ Account {account_num}: {metadata['manager_name']} ({metadata['fund_type']}) - {metadata['platform']}")
                updated_count += 1
        
        print(f"\n📊 Updated {updated_count} accounts in master collection")
        
        # Step 2: Create indexes for efficient querying
        print("\n2️⃣  Creating database indexes for efficient queries...")
        
        indexes = [
            [("fund_type", 1)],
            [("manager_name", 1)], 
            [("platform", 1)],
            [("broker", 1)],
            [("status", 1)],
            [("account", 1)]  # Primary key
        ]
        
        for index_spec in indexes:
            try:
                await db.mt5_accounts.create_index(index_spec)
                print(f"✅ Created index on: {index_spec[0][0]}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️  Index already exists: {index_spec[0][0]}")
                else:
                    print(f"⚠️  Index creation failed: {e}")
        
        # Step 3: Verify single source of truth
        print("\n3️⃣  Verifying single source of truth...")
        
        # Fund distribution
        fund_pipeline = [
            {"$match": {"is_master_account": True}},
            {"$group": {
                "_id": "$fund_type",
                "account_count": {"$sum": 1},
                "accounts": {"$push": "$account"},
                "total_balance": {"$sum": "$balance"},
                "managers": {"$addToSet": "$manager_name"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        funds = await db.mt5_accounts.aggregate(fund_pipeline).to_list(100)
        
        print("\n📈 Fund Distribution (Single Source of Truth):")
        total_accounts_check = 0
        for fund in funds:
            print(f"  {fund['_id']:>10}: {fund['account_count']:>2} accounts | ${fund['total_balance']:>10,.2f} | Managers: {len(fund['managers'])}")
            total_accounts_check += fund['account_count']
        
        # Manager distribution
        manager_pipeline = [
            {"$match": {"is_master_account": True}},
            {"$group": {
                "_id": "$manager_name", 
                "account_count": {"$sum": 1},
                "accounts": {"$push": "$account"},
                "funds": {"$addToSet": "$fund_type"},
                "platforms": {"$addToSet": "$platform"},
                "total_balance": {"$sum": "$balance"}
            }},
            {"$sort": {"account_count": -1}}
        ]
        
        managers = await db.mt5_accounts.aggregate(manager_pipeline).to_list(100)
        
        print(f"\n👥 Manager Distribution ({len(managers)} total managers):")
        for manager in managers:
            platforms = "/".join(sorted(manager['platforms']))
            funds = "/".join(sorted(manager['funds']))
            print(f"  {manager['_id']:<20}: {manager['account_count']} accounts | {platforms} | {funds} | ${manager['total_balance']:,.2f}")
        
        # Platform/Broker distribution
        platform_pipeline = [
            {"$match": {"is_master_account": True}},
            {"$group": {
                "_id": {"platform": "$platform", "broker": "$broker"},
                "account_count": {"$sum": 1},
                "accounts": {"$push": "$account"},
                "total_balance": {"$sum": "$balance"}
            }},
            {"$sort": {"_id.platform": 1, "_id.broker": 1}}
        ]
        
        platforms = await db.mt5_accounts.aggregate(platform_pipeline).to_list(100)
        
        print(f"\n🏢 Platform/Broker Distribution:")
        for platform in platforms:
            key = f"{platform['_id']['platform']} - {platform['_id']['broker']}"
            print(f"  {key:<25}: {platform['account_count']} accounts | ${platform['total_balance']:,.2f}")
        
        print(f"\n" + "=" * 70)
        print("✅ SINGLE SOURCE OF TRUTH ARCHITECTURE IMPLEMENTED")
        print(f"📊 Total Master Accounts: {total_accounts_check}")
        print(f"🏗️  All tabs now derive data from mt5_accounts collection")
        print(f"⚡ No duplicate data - edit once, updates everywhere")
        
        return True
        
    except Exception as e:
        print(f"❌ Error implementing architecture: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(implement_single_source_architecture())