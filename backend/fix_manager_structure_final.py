"""
Fix manager structure based on Chava's exact specifications
5 ACTIVE managers for November 2025
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("FIXING MANAGER STRUCTURE - NOVEMBER 2025")
    print("="*80)
    print()
    
    # Define the CORRECT manager assignments
    manager_assignments = {
        # SEPARATION accounts (alefloreztrader)
        897591: {
            "manager": "alefloreztrader",
            "manager_name": "Alejandro Flores Trader",
            "fund_type": "SEPARATION",
            "status": "active"
        },
        897599: {
            "manager": "alefloreztrader", 
            "manager_name": "Alejandro Flores Trader",
            "fund_type": "SEPARATION",
            "status": "active"
        },
        
        # BALANCE fund - Provider1-Assev
        897589: {
            "manager": "Provider1-Assev",
            "manager_name": "Provider1-Assev",
            "fund_type": "BALANCE",
            "capital_source": "reinvested_profit",
            "status": "active"
        },
        
        # BALANCE fund - TradingHub Gold Provider
        886557: {
            "manager": "TradingHub Gold Provider",
            "manager_name": "TradingHub Gold Provider",
            "fund_type": "BALANCE",
            "capital_source": "client",
            "status": "active"
        },
        891215: {
            "manager": "TradingHub Gold Provider",
            "manager_name": "TradingHub Gold Provider", 
            "fund_type": "BALANCE",
            "capital_source": "fidus",
            "status": "active"
        },
        
        # BALANCE fund - UNO14 Manager (MAM)
        886602: {
            "manager": "UNO14 Manager",
            "manager_name": "UNO14 Manager",
            "fund_type": "BALANCE",
            "capital_source": "client",
            "execution_method": "MAM",
            "status": "active"
        },
        
        # CORE fund - CP Strategy
        897590: {
            "manager": "CP Strategy Provider",
            "manager_name": "CP Strategy Provider",
            "fund_type": "CORE",
            "capital_source": "reinvested_profit",
            "status": "active"
        },
        885822: {
            "manager": "CP Strategy Provider",
            "manager_name": "CP Strategy Provider",
            "fund_type": "CORE",
            "capital_source": "client",
            "status": "active"
        },
        
        # GoldenTrade - INACTIVE (don't delete, might use later)
        886066: {
            "manager": "GoldenTrade Manager",
            "manager_name": "GoldenTrade Manager",
            "fund_type": "BALANCE",
            "capital_source": "client",
            "status": "inactive",
            "notes": "Not allocated this month - funds moved out"
        },
        
        # Other accounts
        891234: {
            "fund_type": "CORE",
            "capital_source": "client",
            "status": "inactive"
        },
        886528: {
            "manager": "alefloreztrader",
            "manager_name": "Alejandro Flores Trader",
            "fund_type": "SEPARATION",
            "capital_source": "intermediary",
            "status": "active",
            "notes": "Intermediary hub"
        }
    }
    
    # Update each account
    for account_num, updates in manager_assignments.items():
        result = await db.mt5_accounts.update_one(
            {"account": account_num},
            {"$set": updates}
        )
        
        status = "✅" if result.modified_count > 0 else "⚠️"
        manager = updates.get('manager', 'None')
        print(f"{status} Account {account_num}: {manager} ({updates.get('fund_type')})")
    
    print()
    print("="*80)
    print("VERIFICATION - 5 ACTIVE MANAGERS")
    print("="*80)
    print()
    
    # Verify by manager
    active_managers = {}
    all_accounts = await db.mt5_accounts.find({}).to_list(None)
    
    for acc in all_accounts:
        manager = acc.get('manager')
        status = acc.get('status')
        if manager and status == 'active':
            if manager not in active_managers:
                active_managers[manager] = []
            active_managers[manager].append({
                'account': acc.get('account'),
                'fund_type': acc.get('fund_type'),
                'capital_source': acc.get('capital_source')
            })
    
    print(f"Total Active Managers: {len(active_managers)}")
    print()
    
    for i, (manager, accounts) in enumerate(active_managers.items(), 1):
        print(f"{i}. {manager}")
        for acc in accounts:
            print(f"   - Account {acc['account']} ({acc['fund_type']}, {acc['capital_source']})")
        print()
    
    if len(active_managers) == 5:
        print("✅ CORRECT! 5 active managers")
    else:
        print(f"❌ WRONG! Found {len(active_managers)} managers (expected 5)")
    
    client.close()

asyncio.run(fix())
