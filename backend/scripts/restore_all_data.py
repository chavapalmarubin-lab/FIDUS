"""
Comprehensive Data Restoration Script
Restores all MT5 accounts, money managers, and investments with correct schema
"""
import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def restore_all_data():
    """Restore all production data with correct schema"""
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("=" * 80)
    print("DATA RESTORATION SCRIPT - FIDUS PRODUCTION")
    print("=" * 80)
    
    # Step 1: Create all 7 MT5 accounts with correct schema
    print("\n[1/4] Creating MT5 Accounts...")
    
    mt5_accounts = [
        {
            "account": 886557,
            "name": "Main Balance Account",
            "fund_type": "BALANCE",
            "broker_name": "MEXAtlantic",
            "server": "MEXAtlantic-Real",
            "balance": 80000.00,
            "equity": 84973.66,
            "profit": 4973.66,
            "margin": 1000.00,
            "free_margin": 83973.66,
            "margin_level": 8497.37,
            "currency": "USD",
            "leverage": 500,
            "is_active": True,
            "connection_status": "active",
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "account": 886066,
            "name": "Secondary Balance Account",
            "fund_type": "BALANCE",
            "broker_name": "MEXAtlantic",
            "server": "MEXAtlantic-Real",
            "balance": 10000.00,
            "equity": 10692.22,
            "profit": 692.22,
            "margin": 0.00,
            "free_margin": 10692.22,
            "margin_level": 0.00,
            "currency": "USD",
            "leverage": 500,
            "is_active": True,
            "connection_status": "active",
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "account": 886602,
            "name": "Tertiary Balance Account",
            "fund_type": "BALANCE",
            "broker_name": "MEXAtlantic",
            "server": "MEXAtlantic-Real",
            "balance": 10000.00,
            "equity": 11136.10,
            "profit": 1136.10,
            "margin": 0.00,
            "free_margin": 11136.10,
            "margin_level": 0.00,
            "currency": "USD",
            "leverage": 500,
            "is_active": True,
            "connection_status": "active",
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "account": 885822,
            "name": "Core Account",
            "fund_type": "CORE",
            "broker_name": "MEXAtlantic",
            "server": "MEXAtlantic-Real",
            "balance": 18151.41,
            "equity": 18038.47,
            "profit": -112.94,
            "margin": 0.00,
            "free_margin": 18038.47,
            "margin_level": 0.00,
            "currency": "USD",
            "leverage": 500,
            "is_active": True,
            "connection_status": "active",
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "account": 886528,
            "name": "Separation Account",
            "fund_type": "SEPARATION",
            "broker_name": "MEXAtlantic",
            "server": "MEXAtlantic-Real",
            "balance": 0.00,
            "equity": 0.00,
            "profit": 0.00,
            "margin": 0.00,
            "free_margin": 0.00,
            "margin_level": 0.00,
            "currency": "USD",
            "leverage": 500,
            "is_active": True,
            "connection_status": "active",
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "account": 891215,
            "name": "Account 891215 - Interest Earnings Trading",
            "fund_type": "SEPARATION",
            "broker_name": "MEXAtlantic",
            "server": "MEXAtlantic-Real",
            "balance": 0.00,
            "equity": 0.00,
            "profit": 0.00,
            "margin": 0.00,
            "free_margin": 0.00,
            "margin_level": 0.00,
            "currency": "USD",
            "leverage": 500,
            "is_active": True,
            "connection_status": "active",
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "account": 891234,
            "name": "Account 891234 - CORE Fund",
            "fund_type": "CORE",
            "broker_name": "MEXAtlantic",
            "server": "MEXAtlantic-Real",
            "balance": 8000.00,
            "equity": 8000.00,
            "profit": 0.00,
            "margin": 0.00,
            "free_margin": 8000.00,
            "margin_level": 0.00,
            "currency": "USD",
            "leverage": 500,
            "is_active": True,
            "connection_status": "active",
            "last_sync": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    # Delete existing MT5 accounts
    await db.mt5_accounts.delete_many({})
    print(f"  ✓ Cleared existing MT5 accounts")
    
    # Insert new accounts
    result = await db.mt5_accounts.insert_many(mt5_accounts)
    print(f"  ✓ Created {len(result.inserted_ids)} MT5 accounts")
    
    # Step 2: Create money managers
    print("\n[2/4] Creating Money Managers...")
    
    money_managers = [
        {
            "manager_id": "tradinghub_gold",
            "manager_name": "TradingHub Gold Provider",
            "profile_type": "copy_trade",
            "true_pnl": 4973.66,
            "performance_fee_rate": 0.20,
            "stats": {
                "total_trades": 150,
                "win_rate": 65.5,
                "sharpe_ratio": 1.85
            },
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "manager_id": "goldentrade",
            "manager_name": "GoldenTrade Provider",
            "profile_type": "copy_trade",
            "true_pnl": 1828.32,
            "performance_fee_rate": 0.20,
            "stats": {
                "total_trades": 89,
                "win_rate": 58.2,
                "sharpe_ratio": 1.42
            },
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "manager_id": "uno14_mam",
            "manager_name": "UNO14 MAM Manager",
            "profile_type": "mam",
            "true_pnl": -112.94,
            "performance_fee_rate": 0.20,
            "stats": {
                "total_trades": 45,
                "win_rate": 44.4,
                "sharpe_ratio": 0.89
            },
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "manager_id": "cp_strategy",
            "manager_name": "CP Strategy Provider",
            "profile_type": "copy_trade",
            "true_pnl": -112.94,
            "performance_fee_rate": 0.20,
            "stats": {
                "total_trades": 32,
                "win_rate": 40.6,
                "sharpe_ratio": 0.72
            },
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    # Delete existing money managers
    await db.money_managers.delete_many({})
    print(f"  ✓ Cleared existing money managers")
    
    # Insert new managers
    result = await db.money_managers.insert_many(money_managers)
    print(f"  ✓ Created {len(result.inserted_ids)} money managers")
    
    # Step 3: Fix investments
    print("\n[3/4] Fixing Investments...")
    
    # Update Alejandro's investments with correct data
    await db.investments.update_many(
        {"client_id": {"$in": ["client_alejandro", "client_alejandro_mariscal"]}},
        {"$set": {"client_id": "client_alejandro"}}
    )
    print(f"  ✓ Standardized client_id to 'client_alejandro'")
    
    # Update BALANCE investment
    balance_result = await db.investments.update_one(
        {"client_id": "client_alejandro", "fund_code": "BALANCE"},
        {"$set": {
            "client_name": "Alejandro Mariscal",
            "initial_amount": 100000.00,
            "current_value": 100000.00,
            "status": "active"
        }}
    )
    print(f"  ✓ Updated BALANCE investment: modified={balance_result.modified_count}")
    
    # Update CORE investment
    core_result = await db.investments.update_one(
        {"client_id": "client_alejandro", "fund_code": "CORE"},
        {"$set": {
            "client_name": "Alejandro Mariscal",
            "initial_amount": 18151.41,
            "current_value": 18151.41,
            "status": "active"
        }}
    )
    print(f"  ✓ Updated CORE investment: modified={core_result.modified_count}")
    
    # Step 4: Update user data
    print("\n[4/4] Fixing User Data...")
    
    # Update Alejandro's user record
    user_result = await db.users.update_one(
        {"username": "alejandro_mariscal"},
        {"$set": {
            "full_name": "Alejandro Mariscal",
            "user_type": "client",
            "client_id": "client_alejandro"
        }}
    )
    print(f"  ✓ Updated user data: modified={user_result.modified_count}")
    
    # Verification
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    mt5_count = await db.mt5_accounts.count_documents({})
    print(f"  MT5 Accounts: {mt5_count}")
    
    managers_count = await db.money_managers.count_documents({})
    print(f"  Money Managers: {managers_count}")
    
    investments_count = await db.investments.count_documents({"client_id": "client_alejandro"})
    print(f"  Alejandro's Investments: {investments_count}")
    
    # Show account details
    print("\n  MT5 Account Details:")
    async for acc in db.mt5_accounts.find({}, {"account": 1, "name": 1, "fund_type": 1, "equity": 1, "profit": 1}):
        print(f"    - {acc['account']}: {acc['name']} ({acc['fund_type']}) - Equity: ${acc['equity']:,.2f}, P&L: ${acc['profit']:,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ DATA RESTORATION COMPLETE")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(restore_all_data())
