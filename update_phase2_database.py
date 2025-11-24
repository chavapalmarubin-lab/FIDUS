"""
Phase 2 Database Updates - 15 Account Structure
Updates mt5_accounts and money_managers collections with correct metadata
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def update_phase2_data():
    """Update database with Phase 2 account structure (15 accounts)"""
    
    try:
        # Connect to MongoDB
        mongo_url = os.getenv('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db = client['fidus_production']
        
        print("🔄 Updating Phase 2 Account Structure (15 Accounts)")
        print("=" * 60)
        
        # Account metadata updates
        account_updates = {
            # LUCRUM Account
            2198: {
                "platform": "MT5",
                "broker": "LUCRUM Capital", 
                "server": "LucrumCapital-Trade",
                "fund_type": "SEPARATION",
                "manager_name": "JOSE",
                "strategy": "HFT Rebate Arbitrage",
                "status": "active"
            },
            
            # MEXAtlantic MT4 Account
            33200931: {
                "platform": "MT4",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real", 
                "fund_type": "BALANCE",
                "manager_name": "Money Manager",
                "strategy": "MT4 Manual Trading",
                "status": "active"
            },
            
            # MEXAtlantic MT5 Account Updates
            885822: {
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "CORE",
                "manager_name": "CP Strategy",
                "strategy": "Copy Trading",
                "status": "active"
            },
            
            886066: {
                "platform": "MT5", 
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE",
                "manager_name": "GoldenTrade",
                "strategy": "Copy Trading",
                "status": "inactive"
            },
            
            886528: {
                "platform": "MT5",
                "broker": "MEXAtlantic", 
                "server": "MEXAtlantic-Real",
                "fund_type": "SEPARATION",
                "manager_name": "Reserve Account",
                "strategy": "Reserve/Hedging", 
                "status": "active"
            },
            
            886557: {
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE",
                "manager_name": "TradingHub Gold",
                "strategy": "Copy Trading",
                "status": "active"
            },
            
            886602: {
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real", 
                "fund_type": "BALANCE",
                "manager_name": "UNO14 Manager",
                "strategy": "MAM",
                "status": "active"
            },
            
            891215: {
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE", 
                "manager_name": "TradingHub Gold",
                "strategy": "Copy Trading",
                "status": "active"
            },
            
            891234: {
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "CORE",
                "manager_name": "GoldenTrade", 
                "strategy": "Copy Trading",
                "status": "inactive"
            },
            
            897589: {
                "platform": "MT5", 
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE",
                "manager_name": "Provider1-Assev",
                "strategy": "Copy Trading",
                "status": "active"
            },
            
            897590: {
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "CORE",
                "manager_name": "CP Strategy",
                "strategy": "Copy Trading", 
                "status": "active"
            },
            
            897591: {
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "SEPARATION",
                "manager_name": "alefloreztrader",
                "strategy": "Copy Trading",
                "status": "active"
            },
            
            897599: {
                "platform": "MT5", 
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "SEPARATION",
                "manager_name": "alefloreztrader",
                "strategy": "Copy Trading", 
                "status": "active"
            },
            
            901351: {
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE",
                "manager_name": "Spaniard Stock CFDs",
                "strategy": "Stock CFDs Master",
                "status": "active"
            },
            
            901353: {
                "platform": "MT5",
                "broker": "MEXAtlantic", 
                "server": "MEXAtlantic-Real",
                "fund_type": "BALANCE",
                "manager_name": "Spaniard Stock CFDs",
                "strategy": "Stock CFDs Copy",
                "status": "active"
            }
        }
        
        # Update each account
        updated_count = 0
        for account_num, metadata in account_updates.items():
            result = await db.mt5_accounts.update_one(
                {"account": account_num},
                {"$set": metadata},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                print(f"✅ Updated account {account_num}: {metadata['manager_name']} ({metadata['fund_type']})")
                updated_count += 1
            else:
                print(f"⚠️ Account {account_num}: No update needed")
        
        print(f"\n📊 Updated {updated_count} accounts")
        
        # Money Managers collection update
        print("\n" + "=" * 60)
        print("🔄 Updating Money Managers Collection")
        
        managers = [
            {
                "manager_id": "spaniard_stock_cfds",
                "name": "Spaniard Stock CFDs",
                "execution_method": "Copy Trade",
                "fund_type": "BALANCE",
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "accounts": [901351, 901353],
                "strategy": "Stock CFDs Trading",
                "status": "active",
                "created_date": "2025-11-24"
            },
            {
                "manager_id": "jose_hft",
                "name": "JOSE", 
                "execution_method": "HFT Rebate",
                "fund_type": "SEPARATION",
                "platform": "MT5",
                "broker": "LUCRUM Capital",
                "accounts": [2198],
                "strategy": "HFT Rebate Arbitrage",
                "status": "active",
                "created_date": "2025-11-24"
            },
            {
                "manager_id": "money_manager_mt4",
                "name": "Money Manager",
                "execution_method": "MT4 Manager", 
                "fund_type": "BALANCE",
                "platform": "MT4",
                "broker": "MEXAtlantic", 
                "accounts": [33200931],
                "strategy": "MT4 Manual Trading",
                "status": "active",
                "created_date": "2025-11-24"
            },
            {
                "manager_id": "cp_strategy",
                "name": "CP Strategy",
                "execution_method": "Copy Trade",
                "fund_type": "CORE", 
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "accounts": [885822, 897590],
                "strategy": "Algorithmic Copy Trading",
                "status": "active",
                "created_date": "2025-11-24"
            },
            {
                "manager_id": "tradinghub_gold",
                "name": "TradingHub Gold",
                "execution_method": "Copy Trade",
                "fund_type": "BALANCE",
                "platform": "MT5", 
                "broker": "MEXAtlantic",
                "accounts": [886557, 891215],
                "strategy": "Gold Trading Specialist",
                "status": "active",
                "created_date": "2025-11-24"
            },
            {
                "manager_id": "uno14_manager", 
                "name": "UNO14 Manager",
                "execution_method": "MAM",
                "fund_type": "BALANCE",
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "accounts": [886602],
                "strategy": "Multi-Account Manager",
                "status": "active", 
                "created_date": "2025-11-24"
            },
            {
                "manager_id": "provider1_assev",
                "name": "Provider1-Assev",
                "execution_method": "Copy Trade",
                "fund_type": "BALANCE",
                "platform": "MT5",
                "broker": "MEXAtlantic", 
                "accounts": [897589],
                "strategy": "Forex Copy Trading",
                "status": "active",
                "created_date": "2025-11-24"
            },
            {
                "manager_id": "alefloreztrader",
                "name": "alefloreztrader",
                "execution_method": "Copy Trade", 
                "fund_type": "SEPARATION",
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "accounts": [897591, 897599],
                "strategy": "Separation Strategy",
                "status": "active",
                "created_date": "2025-11-24"
            },
            {
                "manager_id": "goldentrade",
                "name": "GoldenTrade", 
                "execution_method": "Copy Trade",
                "fund_type": "INACTIVE",
                "platform": "MT5",
                "broker": "MEXAtlantic",
                "accounts": [886066, 891234],
                "strategy": "Inactive Manager",
                "status": "inactive",
                "created_date": "2025-11-24"
            }
        ]
        
        # Update money managers
        manager_count = 0
        for manager in managers:
            result = await db.money_managers.update_one(
                {"manager_id": manager["manager_id"]},
                {"$set": manager},
                upsert=True
            )
            
            if result.matched_count > 0 or result.upserted_id:
                print(f"✅ Updated manager: {manager['name']} ({len(manager['accounts'])} accounts)")
                manager_count += 1
        
        print(f"\n💼 Updated {manager_count} money managers")
        
        # Verification
        print("\n" + "=" * 60)
        print("🔍 VERIFICATION")
        
        total_accounts = await db.mt5_accounts.count_documents({})
        active_accounts = await db.mt5_accounts.count_documents({"status": "active"})
        total_managers = await db.money_managers.count_documents({})
        active_managers = await db.money_managers.count_documents({"status": "active"})
        
        # Fund breakdown
        core_accounts = await db.mt5_accounts.count_documents({"fund_type": "CORE"})
        balance_accounts = await db.mt5_accounts.count_documents({"fund_type": "BALANCE"})  
        separation_accounts = await db.mt5_accounts.count_documents({"fund_type": "SEPARATION"})
        
        print(f"📊 Total Accounts: {total_accounts} (Active: {active_accounts})")
        print(f"💼 Total Managers: {total_managers} (Active: {active_managers})")
        print(f"🏦 Fund Breakdown:")
        print(f"   - CORE: {core_accounts} accounts")
        print(f"   - BALANCE: {balance_accounts} accounts") 
        print(f"   - SEPARATION: {separation_accounts} accounts")
        
        # Platform breakdown
        mt5_accounts = await db.mt5_accounts.count_documents({"platform": "MT5"})
        mt4_accounts = await db.mt5_accounts.count_documents({"platform": "MT4"})
        mexatlantic_accounts = await db.mt5_accounts.count_documents({"broker": "MEXAtlantic"})
        lucrum_accounts = await db.mt5_accounts.count_documents({"broker": "LUCRUM Capital"})
        
        print(f"🔧 Platform Breakdown:")
        print(f"   - MT5: {mt5_accounts} accounts")
        print(f"   - MT4: {mt4_accounts} accounts")
        print(f"🏢 Broker Breakdown:")
        print(f"   - MEXAtlantic: {mexatlantic_accounts} accounts")
        print(f"   - LUCRUM Capital: {lucrum_accounts} accounts")
        
        print("\n✅ Phase 2 Database Update Complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(update_phase2_data())