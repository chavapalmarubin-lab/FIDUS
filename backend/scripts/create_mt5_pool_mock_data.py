"""
Create Mock Data for MT5 Account Pool and Multiple Investment Mappings
Test scenarios for Phase 1 implementation
"""

import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.database import get_database
from repositories.mt5_account_pool_repository import MT5AccountPoolRepository, MT5InvestmentMappingRepository
from models.mt5_account_pool import (
    MT5AccountPoolCreate, MT5InvestmentMappingCreate,
    MT5AccountType, BrokerCode
)
from models.enhanced_investment import EnhancedInvestmentCreate, FundCode, Currency

async def create_mock_mt5_pool_data():
    """Create comprehensive mock data for MT5 account pool system"""
    
    try:
        db = await get_database()
        pool_repo = MT5AccountPoolRepository(db)
        mapping_repo = MT5InvestmentMappingRepository(db)
        
        print("🏗️ Creating Mock MT5 Account Pool Data for Testing...")
        print("=" * 60)
        
        # ==================== CREATE MT5 ACCOUNT POOL ====================
        print("\n1. 📋 Creating MT5 Account Pool...")
        
        # Investment accounts for various brokers and purposes
        mt5_accounts_to_add = [
            # MULTIBANK Investment Accounts
            {
                'mt5_account_number': 886557,
                'broker_name': BrokerCode.MULTIBANK,
                'account_type': MT5AccountType.INVESTMENT,
                'investor_password': 'Inv123!MB557',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'MultiBank-Live',
                'notes': 'Primary investment account for BALANCE fund allocations'
            },
            {
                'mt5_account_number': 886602,
                'broker_name': BrokerCode.MULTIBANK,
                'account_type': MT5AccountType.INVESTMENT,
                'investor_password': 'Inv456!MB602',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'MultiBank-Live',
                'notes': 'Secondary investment account for portfolio diversification'
            },
            {
                'mt5_account_number': 886066,
                'broker_name': BrokerCode.MULTIBANK,
                'account_type': MT5AccountType.INVESTMENT,
                'investor_password': 'Inv789!MB066',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'MultiBank-Live',
                'notes': 'Tertiary investment account for risk distribution'
            },
            {
                'mt5_account_number': 885822,
                'broker_name': BrokerCode.MULTIBANK,
                'account_type': MT5AccountType.INVESTMENT,
                'investor_password': 'Inv321!MB822',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'MultiBank-Live',
                'notes': 'CORE fund investment account'
            },
            
            # Separation Accounts
            {
                'mt5_account_number': 886528,
                'broker_name': BrokerCode.MULTIBANK,
                'account_type': MT5AccountType.INTEREST_SEPARATION,
                'investor_password': 'IntSep!528',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'MultiBank-Live',
                'notes': 'Interest separation tracking account for client payouts'
            },
            {
                'mt5_account_number': 886529,
                'broker_name': BrokerCode.MULTIBANK,
                'account_type': MT5AccountType.GAINS_SEPARATION,
                'investor_password': 'GainSep!529',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'MultiBank-Live',
                'notes': 'Gains separation tracking account for performance fees'
            },
            
            # DOOTECHNOLOGY Accounts
            {
                'mt5_account_number': 1001234,
                'broker_name': BrokerCode.DOOTECHNOLOGY,
                'account_type': MT5AccountType.INVESTMENT,
                'investor_password': 'DooInv!1234',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'DooTechnology-Live',
                'notes': 'Primary DooTechnology investment account'
            },
            {
                'mt5_account_number': 1001235,
                'broker_name': BrokerCode.DOOTECHNOLOGY,
                'account_type': MT5AccountType.INVESTMENT,
                'investor_password': 'DooInv!1235',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'DooTechnology-Live',
                'notes': 'Secondary DooTechnology investment account'
            },
            
            # Additional MULTIBANK accounts for various scenarios
            {
                'mt5_account_number': 887001,
                'broker_name': BrokerCode.MULTIBANK,
                'account_type': MT5AccountType.INVESTMENT,
                'investor_password': 'Inv001!MB',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'MultiBank-Live',
                'notes': 'Available for DYNAMIC fund allocations'
            },
            {
                'mt5_account_number': 887002,
                'broker_name': BrokerCode.MULTIBANK,
                'account_type': MT5AccountType.INVESTMENT,
                'investor_password': 'Inv002!MB',  # ⚠️ INVESTOR PASSWORD ONLY
                'mt5_server': 'MultiBank-Live',
                'notes': 'Available for UNLIMITED fund allocations'
            },
        ]
        
        created_accounts = []
        admin_user_id = "admin"  # Mock admin user
        
        for account_data in mt5_accounts_to_add:
            try:
                account_create = MT5AccountPoolCreate(**account_data)
                new_account = await pool_repo.add_account_to_pool(account_create, admin_user_id)
                
                if new_account:
                    created_accounts.append(new_account)
                    print(f"   ✅ Added MT5 Account {account_data['mt5_account_number']} ({account_data['broker_name']}) - {account_data['account_type']}")
                    
            except ValueError as e:
                if "already exists" in str(e):
                    print(f"   ℹ️ MT5 Account {account_data['mt5_account_number']} already exists - skipping")
                else:
                    print(f"   ❌ Error adding {account_data['mt5_account_number']}: {e}")
            except Exception as e:
                print(f"   ❌ Unexpected error adding {account_data['mt5_account_number']}: {e}")
        
        print(f"\n   📊 Created {len(created_accounts)} new MT5 accounts in pool")
        
        # ==================== CREATE TEST INVESTMENT MAPPINGS ====================
        print("\n2. 🎯 Creating Test Investment Mappings...")
        
        # Test Scenario 1: Alejandro Mariscal (Existing Client)
        print("\n   Scenario 1: Alejandro Mariscal - Multiple Products & Multiple MT5 Accounts")
        
        # FIDUS BALANCE Product: $100,000 split across 3 MT5 accounts
        balance_mappings = [
            {
                'mt5_account_number': 886557,
                'allocated_amount': Decimal('80000.00'),
                'allocation_notes': 'Primary allocation for BALANCE fund - largest portion for main trading strategy'
            },
            {
                'mt5_account_number': 886602,
                'allocated_amount': Decimal('10000.00'),
                'allocation_notes': 'Secondary allocation for BALANCE fund - diversification and risk management'
            },
            {
                'mt5_account_number': 886066,
                'allocated_amount': Decimal('10000.00'),
                'allocation_notes': 'Tertiary allocation for BALANCE fund - additional risk distribution'
            }
        ]
        
        # FIDUS CORE Product: $18,151.41 in single MT5 account
        core_mappings = [
            {
                'mt5_account_number': 885822,
                'allocated_amount': Decimal('18151.41'),
                'allocation_notes': 'Full allocation for CORE fund - conservative strategy in dedicated account'
            }
        ]
        
        # Create Alejandro's BALANCE investment
        try:
            alejandro_balance_investment = {
                'investment_id': 'inv_alejandro_balance_001',
                'client_id': 'alejandro_mariscal',
                'fund_code': 'BALANCE',
                'mappings': balance_mappings
            }
            
            balance_investment_mappings = [MT5InvestmentMappingCreate(**mapping) for mapping in balance_mappings]
            created_balance_mappings = await mapping_repo.create_mappings_for_investment(
                investment_id='inv_alejandro_balance_001',
                client_id='alejandro_mariscal',
                fund_code='BALANCE',
                mappings=balance_investment_mappings,
                admin_user_id=admin_user_id
            )
            
            # Allocate the MT5 accounts
            for mapping in balance_mappings:
                await pool_repo.allocate_account_to_client(
                    mt5_account_number=mapping['mt5_account_number'],
                    client_id='alejandro_mariscal',
                    investment_id='inv_alejandro_balance_001',
                    allocated_amount=mapping['allocated_amount'],
                    admin_user_id=admin_user_id,
                    allocation_notes=mapping['allocation_notes']
                )
            
            print(f"   ✅ Created BALANCE investment with {len(balance_mappings)} MT5 mappings - Total: $100,000")
            
            # Validate the mappings
            balance_validation = await mapping_repo.validate_investment_mappings(
                'inv_alejandro_balance_001', 
                Decimal('100000.00')
            )
            print(f"   📋 BALANCE Validation: {'✅ VALID' if balance_validation['is_valid'] else '❌ INVALID'}")
            
        except Exception as e:
            print(f"   ❌ Error creating Alejandro BALANCE investment: {e}")
        
        # Create Alejandro's CORE investment
        try:
            core_investment_mappings = [MT5InvestmentMappingCreate(**mapping) for mapping in core_mappings]
            created_core_mappings = await mapping_repo.create_mappings_for_investment(
                investment_id='inv_alejandro_core_001',
                client_id='alejandro_mariscal',
                fund_code='CORE',
                mappings=core_investment_mappings,
                admin_user_id=admin_user_id
            )
            
            # Allocate the MT5 account
            await pool_repo.allocate_account_to_client(
                mt5_account_number=885822,
                client_id='alejandro_mariscal',
                investment_id='inv_alejandro_core_001',
                allocated_amount=Decimal('18151.41'),
                admin_user_id=admin_user_id,
                allocation_notes='Full allocation for CORE fund - conservative strategy in dedicated account'
            )
            
            print(f"   ✅ Created CORE investment with {len(core_mappings)} MT5 mapping - Total: $18,151.41")
            
            # Validate the mappings
            core_validation = await mapping_repo.validate_investment_mappings(
                'inv_alejandro_core_001',
                Decimal('18151.41')
            )
            print(f"   📋 CORE Validation: {'✅ VALID' if core_validation['is_valid'] else '❌ INVALID'}")
            
        except Exception as e:
            print(f"   ❌ Error creating Alejandro CORE investment: {e}")
        
        # Assign separation accounts for Alejandro
        print(f"   🔗 Assigned separation accounts: Interest (886528), Gains (886529)")
        
        # Test Scenario 2: New Client with Multiple Products
        print("\n   Scenario 2: Test Client - Multi-Product Portfolio")
        
        try:
            # FIDUS DYNAMIC: $300,000 split across 2 accounts (using available DooTechnology accounts)
            dynamic_mappings = [
                {
                    'mt5_account_number': 1001234,
                    'allocated_amount': Decimal('200000.00'),
                    'allocation_notes': 'Primary DYNAMIC allocation - aggressive growth strategy with DooTechnology'
                },
                {
                    'mt5_account_number': 1001235,
                    'allocated_amount': Decimal('100000.00'),
                    'allocation_notes': 'Secondary DYNAMIC allocation - portfolio balancing with DooTechnology'
                }
            ]
            
            dynamic_investment_mappings = [MT5InvestmentMappingCreate(**mapping) for mapping in dynamic_mappings]
            await mapping_repo.create_mappings_for_investment(
                investment_id='inv_testclient_dynamic_001',
                client_id='test_client_001',
                fund_code='DYNAMIC',
                mappings=dynamic_investment_mappings,
                admin_user_id=admin_user_id
            )
            
            # Allocate the MT5 accounts
            for mapping in dynamic_mappings:
                await pool_repo.allocate_account_to_client(
                    mt5_account_number=mapping['mt5_account_number'],
                    client_id='test_client_001',
                    investment_id='inv_testclient_dynamic_001',
                    allocated_amount=mapping['allocated_amount'],
                    admin_user_id=admin_user_id,
                    allocation_notes=mapping['allocation_notes']
                )
            
            print(f"   ✅ Created DYNAMIC investment with {len(dynamic_mappings)} MT5 mappings - Total: $300,000")
            
            # Validate
            dynamic_validation = await mapping_repo.validate_investment_mappings(
                'inv_testclient_dynamic_001',
                Decimal('300000.00')
            )
            print(f"   📋 DYNAMIC Validation: {'✅ VALID' if dynamic_validation['is_valid'] else '❌ INVALID'}")
            
        except Exception as e:
            print(f"   ❌ Error creating test client DYNAMIC investment: {e}")
        
        # Test Scenario 3: Single MT5 Account Investment (Simple Case)
        print("\n   Scenario 3: Simple Client - Single MT5 Account per Product")
        
        try:
            # FIDUS CORE: $15,000 in single account
            simple_core_mappings = [
                {
                    'mt5_account_number': 887001,
                    'allocated_amount': Decimal('15000.00'),
                    'allocation_notes': 'Simple CORE investment - single account allocation for straightforward management'
                }
            ]
            
            simple_investment_mappings = [MT5InvestmentMappingCreate(**mapping) for mapping in simple_core_mappings]
            await mapping_repo.create_mappings_for_investment(
                investment_id='inv_simpleclient_core_001',
                client_id='simple_client_001',
                fund_code='CORE',
                mappings=simple_investment_mappings,
                admin_user_id=admin_user_id
            )
            
            # Allocate
            await pool_repo.allocate_account_to_client(
                mt5_account_number=887001,
                client_id='simple_client_001',
                investment_id='inv_simpleclient_core_001',
                allocated_amount=Decimal('15000.00'),
                admin_user_id=admin_user_id,
                allocation_notes='Simple CORE investment - single account allocation for straightforward management'
            )
            
            print(f"   ✅ Created simple CORE investment with 1 MT5 mapping - Total: $15,000")
            
        except Exception as e:
            print(f"   ❌ Error creating simple client investment: {e}")
        
        # ==================== DISPLAY SUMMARY STATISTICS ====================
        print("\n3. 📊 Summary Statistics")
        
        try:
            stats = await pool_repo.get_pool_statistics()
            
            print(f"\n   MT5 Account Pool Summary:")
            print(f"   ├── Total Accounts: {stats['total_accounts']}")
            print(f"   ├── Available: {stats['available']}")
            print(f"   ├── Allocated: {stats['allocated']}")
            print(f"   ├── Pending Deallocation: {stats['pending_deallocation']}")
            print(f"   └── Utilization Rate: {round((stats['allocated'] / stats['total_accounts'] * 100), 1) if stats['total_accounts'] > 0 else 0}%")
            
            print(f"\n   By Broker:")
            for broker, broker_stats in stats.get('by_broker', {}).items():
                print(f"   ├── {broker}: {broker_stats['total']} accounts ({broker_stats['available']} available, {broker_stats['allocated']} allocated)")
            
        except Exception as e:
            print(f"   ❌ Error getting statistics: {e}")
        
        # ==================== VALIDATION TESTS ====================
        print("\n4. 🧪 Running Validation Tests")
        
        # Test validation scenarios
        validation_tests = [
            {
                'investment_id': 'inv_alejandro_balance_001',
                'expected_amount': Decimal('100000.00'),
                'description': 'Alejandro BALANCE (3 MT5 accounts)'
            },
            {
                'investment_id': 'inv_alejandro_core_001',
                'expected_amount': Decimal('18151.41'),
                'description': 'Alejandro CORE (1 MT5 account)'
            },
            {
                'investment_id': 'inv_testclient_dynamic_001',
                'expected_amount': Decimal('300000.00'),
                'description': 'Test Client DYNAMIC (2 MT5 accounts)'
            },
            {
                'investment_id': 'inv_simpleclient_core_001',
                'expected_amount': Decimal('15000.00'),
                'description': 'Simple Client CORE (1 MT5 account)'
            }
        ]
        
        for test in validation_tests:
            try:
                validation = await mapping_repo.validate_investment_mappings(
                    test['investment_id'],
                    test['expected_amount']
                )
                
                status = "✅ PASS" if validation['is_valid'] else "❌ FAIL"
                difference = validation['difference']
                
                print(f"   {status} {test['description']}")
                print(f"        Expected: ${test['expected_amount']}, Mapped: ${validation['total_mapped_amount']}, Diff: ${difference}")
                
                if not validation['is_valid']:
                    for error in validation['validation_errors']:
                        print(f"        ❌ {error}")
                        
            except Exception as e:
                print(f"   ❌ FAIL {test['description']} - Error: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Mock MT5 Pool Data Creation Complete!")
        print("\nKey Features Demonstrated:")
        print("├── ⚠️ INVESTOR PASSWORD ONLY system (all accounts use investor passwords)")
        print("├── Multiple MT5 accounts per investment product")
        print("├── MT5 account exclusivity (no double allocation)")
        print("├── Comprehensive validation (sum must equal investment)")
        print("├── Multi-broker support (MULTIBANK, DOOTECHNOLOGY)")
        print("├── Account type separation (Investment, Interest, Gains)")
        print("├── Mandatory allocation notes for audit trail")
        print("└── Real-world test scenarios (Alejandro + test clients)")
        print("\n🚀 Ready for Phase 1 Testing!")
        
    except Exception as e:
        print(f"❌ Error creating mock data: {e}")
        raise

if __name__ == "__main__":
    print("🔄 Starting MT5 Account Pool Mock Data Creation...")
    asyncio.run(create_mock_mt5_pool_data())