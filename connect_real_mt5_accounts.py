#!/usr/bin/env python3
"""
Real MT5 Account Connection Script
================================

This script connects to the REAL MT5 accounts with provided credentials
and creates investments based on actual historical data.

REAL CREDENTIALS PROVIDED:
1. DooTechnology-Live: 9928326 / R1d567j! → BALANCE Fund
2. VT Markets PAMM: 15759668 / BggHyVTDQ5@ → CORE Fund
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
import uuid

# Add backend to path
sys.path.append('/app/backend')

from mongodb_integration import mongodb_manager

async def connect_real_mt5_accounts():
    """Connect to real MT5 accounts and create investments from historical data"""
    
    print("🔌 CONNECTING TO REAL MT5 ACCOUNTS")
    print("=" * 60)
    
    # Real MT5 credentials provided by user
    accounts_to_connect = [
        {
            'name': 'DooTechnology',
            'mt5_login': 9928326,
            'password': 'R1d567j!',
            'server': 'DooTechnology-Live',
            'fund_code': 'BALANCE',
            'broker_code': 'dootechnology'
        },
        {
            'name': 'VT Markets PAMM',
            'mt5_login': 15759668,
            'password': 'BggHyVTDQ5@',
            'server': 'VTMarkets-PAMM',
            'fund_code': 'CORE',
            'broker_code': 'vt'
        }
    ]
    
    # Try to import and use real MT5 API
    try:
        from real_mt5_api import real_mt5_api
        
        for account_info in accounts_to_connect:
            print(f"\n🏦 Connecting to {account_info['name']}...")
            print(f"   Login: {account_info['mt5_login']}")
            print(f"   Server: {account_info['server']}")
            
            # Connect to real MT5 account
            real_data = await real_mt5_api.connect_and_get_real_data(
                account_info['mt5_login'],
                account_info['password'],
                account_info['server']
            )
            
            if real_data['status'] == 'connected':
                print(f"   ✅ Connection successful!")
                print(f"   Current Balance: ${real_data['current_balance']:,.2f}")
                print(f"   Current Equity: ${real_data['current_equity']:,.2f}")
                print(f"   Total Deposits: ${real_data['total_deposits']:,.2f}")
                print(f"   Profit/Loss: ${real_data['profit_loss']:,.2f}")
                print(f"   Deposit History: {len(real_data['deposit_history'])} transactions")
                
                # Update MT5 account in database with real data
                mongodb_manager.db.mt5_accounts.update_one(
                    {'client_id': 'client_003', 'mt5_login': account_info['mt5_login']},
                    {
                        '$set': {
                            'status': 'connected',
                            'current_balance': real_data['current_balance'],
                            'current_equity': real_data['current_equity'],
                            'total_allocated': real_data['total_deposits'],
                            'profit_loss': real_data['profit_loss'],
                            'last_mt5_sync': datetime.now(timezone.utc),
                            'data_source': 'MT5_REAL_API'
                        }
                    }
                )
                
                # Create investment based on real historical data
                if real_data['deposit_history'] and len(real_data['deposit_history']) > 0:
                    first_deposit = real_data['deposit_history'][0]
                    
                    investment_data = {
                        'client_id': 'client_003',
                        'fund_code': account_info['fund_code'],
                        'principal_amount': real_data['total_deposits'],
                        'current_value': real_data['current_equity'],
                        'mt5_login': account_info['mt5_login'],
                        'broker_code': account_info['broker_code'],
                        'broker_name': account_info['name'],
                        'data_source': 'MT5_REAL_TIME',
                        'deposit_date': first_deposit['date']
                    }
                    
                    investment_id = mongodb_manager.create_investment(investment_data)
                    
                    if investment_id:
                        print(f"   ✅ Created investment: {investment_id}")
                        print(f"   Fund: {account_info['fund_code']}")
                        print(f"   First Deposit Date: {first_deposit['date']}")
                    else:
                        print(f"   ❌ Failed to create investment")
                
            else:
                print(f"   ❌ Connection failed: {real_data.get('error', 'Unknown error')}")
                
                # Mark as disconnected
                mongodb_manager.db.mt5_accounts.update_one(
                    {'client_id': 'client_003', 'mt5_login': account_info['mt5_login']},
                    {
                        '$set': {
                            'status': 'connection_failed',
                            'last_error': real_data.get('error', 'Connection failed'),
                            'last_attempt': datetime.now(timezone.utc)
                        }
                    }
                )
    
    except ImportError:
        print("❌ MetaTrader5 library not available")
        print("   Install with: pip install MetaTrader5")
        print("   Running in simulation mode...")
        
        # Simulation mode - create sample data structure
        await simulate_mt5_connections(accounts_to_connect)
    
    except Exception as e:
        print(f"❌ Error connecting to MT5: {str(e)}")

async def simulate_mt5_connections(accounts_to_connect):
    """Simulate MT5 connections for development/testing"""
    
    print("\n📋 SIMULATION MODE - WHAT WOULD HAPPEN WITH REAL CONNECTIONS:")
    
    for account_info in accounts_to_connect:
        print(f"\n🏦 {account_info['name']} (Login: {account_info['mt5_login']}):")
        print(f"   Would connect to: {account_info['server']}")
        print(f"   Would retrieve: Historical deposit data")
        print(f"   Would create: {account_info['fund_code']} fund investment")
        print(f"   Would map to: Salvador Palma client_003")
        
        # Update database to show ready for real connection
        mongodb_manager.db.mt5_accounts.update_one(
            {'client_id': 'client_003', 'mt5_login': account_info['mt5_login']},
            {
                '$set': {
                    'status': 'credentials_ready',
                    'ready_for_real_connection': True,
                    'last_updated': datetime.now(timezone.utc)
                }
            }
        )
    
    print(f"\n✅ Database updated - ready for real MT5 connections")
    print(f"✅ When MetaTrader5 library is available, run this script again")

async def main():
    """Main function"""
    try:
        await connect_real_mt5_accounts()
        
        # Show final status
        print(f"\n📊 FINAL STATUS:")
        accounts = mongodb_manager.get_client_mt5_accounts('client_003')
        investments = mongodb_manager.get_client_investments('client_003')
        
        print(f"   MT5 Accounts: {len(accounts)}")
        for acc in accounts:
            print(f"     - {acc.get('broker_name')}: {acc.get('status', 'unknown')}")
        
        print(f"   Investments: {len(investments)}")
        for inv in investments:
            print(f"     - {inv['fund_code']}: ${inv['current_value']:,.2f}")
        
        print(f"\n🎯 NEXT STEPS:")
        if len(investments) == 0:
            print(f"   1. Install MetaTrader5 library: pip install MetaTrader5")
            print(f"   2. Ensure network access to MT5 servers")
            print(f"   3. Run this script in production environment")
            print(f"   4. Verify real historical data is retrieved")
        else:
            print(f"   ✅ Salvador Palma investments created from real MT5 data")
        
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)