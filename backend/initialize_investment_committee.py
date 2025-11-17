"""
Initialize Investment Committee Database Collections
Creates fund_allocation_state and allocation_history collections with current data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from bson import ObjectId

async def initialize_investment_committee():
    """Initialize Investment Committee collections with current state"""
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb+srv://emergent-ops:BpzaxqxDCjz1yWY4@fidus.y1p9be2.mongodb.net/fidus_production')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('fidus_production')
    
    print("🚀 Initializing Investment Committee Database...")
    print("=" * 60)
    
    # ========================================================================
    # STEP 1: Create fund_allocation_state collection
    # ========================================================================
    print("\n📊 STEP 1: Creating fund_allocation_state collection...")
    
    # Drop existing if present (for clean initialization)
    await db.fund_allocation_state.drop()
    print("   ✓ Dropped existing fund_allocation_state collection")
    
    # Initialize BALANCE Fund with current allocations
    balance_fund = {
        "fund_type": "BALANCE",
        "total_capital": 90500.00,
        "allocated_capital": 40000.00,
        "unallocated_capital": 50500.00,
        "cash_reserves": 0.00,
        
        "manager_allocations": [
            {
                "manager_name": "Spaniard Stock CFDs",
                "allocated_amount": 20000.00,
                "allocation_percentage": 22.1,
                "accounts": [
                    {"account_number": 901351, "amount": 10000.00, "type": "master"},
                    {"account_number": 901353, "amount": 10000.00, "type": "copy"}
                ]
            },
            {
                "manager_name": "UNO14 Manager",
                "allocated_amount": 15000.00,
                "allocation_percentage": 16.6,
                "accounts": [
                    {"account_number": 886602, "amount": 15000.00, "type": "MAM"}
                ]
            },
            {
                "manager_name": "Provider1-Assev",
                "allocated_amount": 5000.00,
                "allocation_percentage": 5.5,
                "accounts": [
                    {"account_number": 897589, "amount": 5000.00, "type": "master"}
                ]
            }
        ],
        
        "last_updated": datetime.utcnow(),
        "updated_by": "admin_initialization",
        "status": "active",
        "notes": "Initialized Nov 17, 2025 after TradingHub Gold removal"
    }
    
    await db.fund_allocation_state.insert_one(balance_fund)
    print(f"   ✓ Inserted BALANCE fund state: ${balance_fund['total_capital']:,.2f} total")
    
    # Initialize CORE Fund
    core_fund = {
        "fund_type": "CORE",
        "total_capital": 18151.41,
        "allocated_capital": 18151.41,
        "unallocated_capital": 0.00,
        "cash_reserves": 0.00,
        
        "manager_allocations": [
            {
                "manager_name": "CP Strategy",
                "allocated_amount": 18151.41,
                "allocation_percentage": 100.0,
                "accounts": [
                    {"account_number": 885822, "amount": 2151.41, "type": "master"},
                    {"account_number": 897590, "amount": 16000.00, "type": "copy"}
                ]
            }
        ],
        
        "last_updated": datetime.utcnow(),
        "updated_by": "admin_initialization",
        "status": "active"
    }
    
    await db.fund_allocation_state.insert_one(core_fund)
    print(f"   ✓ Inserted CORE fund state: ${core_fund['total_capital']:,.2f} total")
    
    # Initialize SEPARATION Fund
    separation_fund = {
        "fund_type": "SEPARATION",
        "total_capital": 20653.00,
        "allocated_capital": 20653.00,
        "unallocated_capital": 0.00,
        "cash_reserves": 0.00,
        
        "manager_allocations": [
            {
                "manager_name": "alefloreztrader",
                "allocated_amount": 20653.00,
                "allocation_percentage": 100.0,
                "accounts": [
                    {"account_number": 897591, "amount": 5000.00, "type": "master"},
                    {"account_number": 897599, "amount": 15653.00, "type": "copy"}
                ]
            }
        ],
        
        "last_updated": datetime.utcnow(),
        "updated_by": "admin_initialization",
        "status": "active"
    }
    
    await db.fund_allocation_state.insert_one(separation_fund)
    print(f"   ✓ Inserted SEPARATION fund state: ${separation_fund['total_capital']:,.2f} total")
    
    # Create indexes
    await db.fund_allocation_state.create_index([("fund_type", 1)], unique=True)
    await db.fund_allocation_state.create_index([("manager_allocations.manager_name", 1)])
    await db.fund_allocation_state.create_index([("last_updated", -1)])
    print("   ✓ Created indexes on fund_allocation_state")
    
    # ========================================================================
    # STEP 2: Create allocation_history collection
    # ========================================================================
    print("\n📜 STEP 2: Creating allocation_history collection...")
    
    # Drop existing if present
    await db.allocation_history.drop()
    print("   ✓ Dropped existing allocation_history collection")
    
    # Create history record for TradingHub Gold removal
    tradinghub_removal = {
        "timestamp": datetime.utcnow(),
        "fund_type": "BALANCE",
        "action_type": "manager_removed",
        "performed_by": "admin_committee",
        "affected_manager": "TradingHub Gold",
        "affected_accounts": [886557, 891215],
        
        "before_state": {
            "total_capital": 100000.00,
            "allocated_capital": 100000.00,
            "unallocated_capital": 0.00,
            "manager_allocation": 80000.00
        },
        
        "after_state": {
            "total_capital": 90500.00,
            "allocated_capital": 20000.00,
            "unallocated_capital": 70500.00,
            "manager_allocation": 0.00
        },
        
        "financial_impact": {
            "capital_change": -9500.00,
            "loss_amount": 9500.00,
            "gain_amount": 0.00,
            "allocation_change": -80000.00
        },
        
        "notes": "TradingHub Gold removed after $9,500 loss. Committee decision to absorb loss and reallocate remaining capital.",
        "committee_meeting_id": None
    }
    
    await db.allocation_history.insert_one(tradinghub_removal)
    print("   ✓ Inserted TradingHub Gold removal record")
    
    # Create Spaniard Stock CFDs allocation record
    spaniard_allocation = {
        "timestamp": datetime.utcnow(),
        "fund_type": "BALANCE",
        "action_type": "manager_added",
        "performed_by": "admin_committee",
        "affected_manager": "Spaniard Stock CFDs",
        "affected_accounts": [901351, 901353],
        
        "before_state": {
            "total_capital": 90500.00,
            "allocated_capital": 20000.00,
            "unallocated_capital": 70500.00,
            "manager_allocation": 0.00
        },
        
        "after_state": {
            "total_capital": 90500.00,
            "allocated_capital": 40000.00,
            "unallocated_capital": 50500.00,
            "manager_allocation": 20000.00
        },
        
        "financial_impact": {
            "capital_change": 0.00,
            "loss_amount": 0.00,
            "gain_amount": 0.00,
            "allocation_change": 20000.00
        },
        
        "notes": "New manager Spaniard Stock CFDs allocated $20,000 (2 accounts: 901351 Master $10K, 901353 Copy $10K)",
        "committee_meeting_id": None
    }
    
    await db.allocation_history.insert_one(spaniard_allocation)
    print("   ✓ Inserted Spaniard Stock CFDs allocation record")
    
    # Create indexes
    await db.allocation_history.create_index([("timestamp", -1)])
    await db.allocation_history.create_index([("fund_type", 1), ("timestamp", -1)])
    await db.allocation_history.create_index([("affected_manager", 1)])
    await db.allocation_history.create_index([("action_type", 1)])
    print("   ✓ Created indexes on allocation_history")
    
    # ========================================================================
    # STEP 3: Update MT5 accounts with allocation info
    # ========================================================================
    print("\n🏦 STEP 3: Updating MT5 accounts with allocation info...")
    
    # Spaniard Stock CFDs accounts
    accounts_to_update = [
        {
            "account": 901351,
            "allocated_capital": 10000.00,
            "manager_assigned": "Spaniard Stock CFDs",
            "fund_type": "BALANCE",
            "allocation_type": "master",
            "copy_trading_config": {
                "is_copy_account": False,
                "copy_from_account": None,
                "copy_platform": None,
                "copy_ratio": None
            },
            "last_allocation_update": datetime.utcnow(),
            "allocation_notes": "Master account for Spaniard Stock CFDs strategy"
        },
        {
            "account": 901353,
            "allocated_capital": 10000.00,
            "manager_assigned": "Spaniard Stock CFDs",
            "fund_type": "BALANCE",
            "allocation_type": "copy",
            "copy_trading_config": {
                "is_copy_account": True,
                "copy_from_account": 901351,
                "copy_platform": "Biking",
                "copy_ratio": 1.0
            },
            "last_allocation_update": datetime.utcnow(),
            "allocation_notes": "Copy account via Biking platform, copying account 901351"
        }
    ]
    
    for account_data in accounts_to_update:
        account_num = account_data["account"]
        
        # Check if account exists
        existing = await db.mt5_accounts.find_one({"account": account_num})
        
        if existing:
            # Update existing account
            await db.mt5_accounts.update_one(
                {"account": account_num},
                {"$set": account_data}
            )
            print(f"   ✓ Updated existing account {account_num}")
        else:
            # Create new account
            account_data.update({
                "balance": 0.0,
                "equity": 0.0,
                "profit": 0.0,
                "margin": 0.0,
                "free_margin": 0.0,
                "margin_level": 0.0,
                "leverage": 100,
                "currency": "USD",
                "broker": "MEXAtlantic",
                "server": "MEXAtlantic-Real",
                "status": "active",
                "name": f"Spaniard Stock CFDs - Account {account_num}",
                "client_name": "FIDUS BALANCE Fund",
                "last_sync": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            await db.mt5_accounts.insert_one(account_data)
            print(f"   ✓ Created new account {account_num}")
    
    # Update other allocated accounts
    other_allocations = [
        (886602, "UNO14 Manager", 15000.00, "BALANCE", "MAM"),
        (897589, "Provider1-Assev", 5000.00, "BALANCE", "master"),
        (885822, "CP Strategy", 2151.41, "CORE", "master"),
        (897590, "CP Strategy", 16000.00, "CORE", "copy"),
        (897591, "alefloreztrader", 5000.00, "SEPARATION", "master"),
        (897599, "alefloreztrader", 15653.00, "SEPARATION", "copy")
    ]
    
    for account_num, manager, amount, fund, alloc_type in other_allocations:
        await db.mt5_accounts.update_one(
            {"account": account_num},
            {"$set": {
                "allocated_capital": amount,
                "manager_assigned": manager,
                "fund_type": fund,
                "allocation_type": alloc_type,
                "last_allocation_update": datetime.utcnow()
            }},
            upsert=False
        )
        print(f"   ✓ Updated account {account_num} - {manager} (${amount:,.2f})")
    
    # ========================================================================
    # STEP 4: Add Spaniard Stock CFDs and JOSE to money_managers
    # ========================================================================
    print("\n👥 STEP 4: Updating money_managers collection...")
    
    # Check if Spaniard Stock CFDs exists
    spaniard_exists = await db.money_managers.find_one({"name": "Spaniard Stock CFDs"})
    
    if not spaniard_exists:
        spaniard_manager = {
            "manager_id": "mgr_spaniard_stock_cfds",
            "name": "Spaniard Stock CFDs",
            "display_name": "Spaniard Stock CFDs",
            "strategy_name": "Stock CFDs Trading",
            "status": "active",
            "execution_method": "Copy Trade",
            "assigned_accounts": [901351, 901353],
            "fund_type": "BALANCE",
            "broker": "MEXAtlantic",
            "profile_url": None,
            "rating_url": None,
            "total_allocated": 20000.00,
            "current_allocation": {
                "fund_type": "BALANCE",
                "allocated_amount": 20000.00,
                "accounts": [
                    {"account_number": 901351, "amount": 10000.00, "type": "master"},
                    {"account_number": 901353, "amount": 10000.00, "type": "copy"}
                ],
                "last_updated": datetime.utcnow()
            },
            "allocation_history": [
                {
                    "date": datetime.utcnow(),
                    "allocated_amount": 20000.00,
                    "action": "initial_allocation"
                }
            ],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.money_managers.insert_one(spaniard_manager)
        print("   ✓ Created Spaniard Stock CFDs manager")
    else:
        print("   ⚠ Spaniard Stock CFDs already exists, skipping")
    
    # Add JOSE as pending manager
    jose_exists = await db.money_managers.find_one({"name": "JOSE"})
    
    if not jose_exists:
        jose_manager = {
            "manager_id": "mgr_jose_lucrum",
            "name": "JOSE",
            "display_name": "JOSE",
            "strategy_name": "HFT Rebate Arbitrage Strategy",
            "status": "pending_activation",
            "execution_method": "Copy Trade",
            "assigned_accounts": [],
            "fund_type": None,
            "broker": "LUCRUM",
            "profile_url": None,
            "rating_url": None,
            "total_allocated": 0.00,
            "current_allocation": None,
            "allocation_history": [],
            "active": False,
            "notes": "HFT Rebate Arbitrage Strategy - Account opening in process at LUCRUM",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.money_managers.insert_one(jose_manager)
        print("   ✓ Created JOSE manager (pending_activation)")
    else:
        print("   ⚠ JOSE already exists, skipping")
    
    # ========================================================================
    # STEP 5: Verification
    # ========================================================================
    print("\n✅ STEP 5: Verification...")
    
    # Count documents
    fund_states_count = await db.fund_allocation_state.count_documents({})
    history_count = await db.allocation_history.count_documents({})
    managers_count = await db.money_managers.count_documents({"status": "active"})
    
    print(f"   ✓ Fund allocation states: {fund_states_count}")
    print(f"   ✓ Allocation history records: {history_count}")
    print(f"   ✓ Active money managers: {managers_count}")
    
    # Show BALANCE fund summary
    balance = await db.fund_allocation_state.find_one({"fund_type": "BALANCE"})
    print(f"\n📊 BALANCE Fund Summary:")
    print(f"   Total Capital:     ${balance['total_capital']:,.2f}")
    print(f"   Allocated:         ${balance['allocated_capital']:,.2f}")
    print(f"   Unallocated:       ${balance['unallocated_capital']:,.2f}")
    print(f"   Active Managers:   {len(balance['manager_allocations'])}")
    
    print("\n" + "=" * 60)
    print("✅ Investment Committee Database Initialization Complete!")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(initialize_investment_committee())
