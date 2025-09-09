#!/usr/bin/env python3
"""
Real MT5 Account Connection Script - Windows Bridge Compatible
============================================================

This script connects to REAL MT5 accounts via Windows Bridge Service
and creates Salvador Palma's investments from actual historical data.

REQUIREMENTS:
1. Windows VM with MetaTrader5 terminal running
2. MT5 Windows Bridge Service running on Windows VM
3. MT5_BRIDGE_URL environment variable configured
4. Both MT5 accounts connected on Windows VM

REAL CREDENTIALS:
- DooTechnology-Live: 9928326 / R1d567j! → BALANCE Fund
- VT Markets PAMM: 15759668 / BggHyVTDQ5@ → CORE Fund
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
import uuid

# Add backend to path
sys.path.append('/app/backend')

from mongodb_integration import mongodb_manager

async def connect_real_mt5_accounts_via_bridge():
    """Connect to real MT5 accounts via Windows Bridge Service"""
    
    print("🌉 CONNECTING TO MT5 ACCOUNTS VIA WINDOWS BRIDGE")
    print("=" * 60)
    
    # Check bridge configuration
    bridge_url = os.environ.get('MT5_BRIDGE_URL')
    if not bridge_url:
        print("❌ CRITICAL: MT5_BRIDGE_URL not configured")
        print("   Set environment variable: MT5_BRIDGE_URL=http://mt5-bridge.internal:8080")
        return False
    
    print(f"🔗 Bridge URL: {bridge_url}")
    
    # Real MT5 accounts to connect
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
    
    # Connect to MT5 API
    from real_mt5_api import real_mt5_api
    
    successful_connections = 0
    
    for account_info in accounts_to_connect:
        print(f"\n🏦 Connecting to {account_info['name']}...")
        print(f"   Login: {account_info['mt5_login']}")
        print(f"   Server: {account_info['server']}")
        print(f"   Fund: {account_info['fund_code']}")
        
        # Connect to real MT5 account via bridge
        real_data = await real_mt5_api.connect_and_get_real_data(
            account_info['mt5_login'],
            account_info['password'],
            account_info['server']
        )
        
        if real_data['status'] == 'connected':
            print(f"   ✅ Connection successful via {real_data.get('connection_method', 'unknown')}!")
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
                        'data_source': 'MT5_REAL_API',
                        'connection_method': real_data.get('connection_method', 'bridge'),
                        'bridge_url': real_data.get('bridge_url')
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
                    'deposit_date': first_deposit['date'] if isinstance(first_deposit['date'], datetime) else datetime.fromisoformat(first_deposit['date'])
                }
                
                investment_id = mongodb_manager.create_investment(investment_data)
                
                if investment_id:
                    print(f"   ✅ Created investment: {investment_id}")
                    print(f"   Fund: {account_info['fund_code']}")
                    print(f"   First Deposit Date: {first_deposit['date']}")
                    successful_connections += 1
                else:
                    print(f"   ❌ Failed to create investment")
            else:
                print(f"   ⚠️  No deposit history found - account may be new")
                
        else:
            print(f"   ❌ Connection failed: {real_data.get('error', 'Unknown error')}")
            print(f"   Status: {real_data['status']}")
            
            # Mark as connection failed
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
    
    return successful_connections == len(accounts_to_connect)

async def verify_deployment():
    """Verify the deployment was successful"""
    
    print(f"\n📊 DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    # Check MT5 accounts
    accounts = mongodb_manager.get_client_mt5_accounts('client_003')
    print(f"MT5 Accounts: {len(accounts)}")
    
    connected_accounts = 0
    for acc in accounts:
        status = acc.get('status', 'unknown')
        broker = acc.get('broker_name', 'Unknown')
        equity = acc.get('current_equity', 0)
        
        print(f"   {broker}: {status} - ${equity:,.2f}")
        if status == 'connected':
            connected_accounts += 1
    
    # Check investments
    investments = mongodb_manager.get_client_investments('client_003')
    print(f"\nInvestments: {len(investments)}")
    
    total_portfolio = 0
    fund_breakdown = {}
    
    for inv in investments:
        fund = inv['fund_code']
        current_value = inv['current_value']
        data_source = inv.get('data_source', 'Unknown')
        
        print(f"   {fund} Fund: ${current_value:,.2f} (Source: {data_source})")
        
        total_portfolio += current_value
        fund_breakdown[fund] = current_value
    
    print(f"\nTotal Portfolio: ${total_portfolio:,.2f}")
    
    # Success criteria
    print(f"\n🎯 SUCCESS CRITERIA:")
    print(f"   ✅ MT5 Accounts Connected: {connected_accounts}/2")
    print(f"   ✅ Investments Created: {len(investments)}/2")
    print(f"   ✅ BALANCE Fund: ${fund_breakdown.get('BALANCE', 0):,.2f}")
    print(f"   ✅ CORE Fund: ${fund_breakdown.get('CORE', 0):,.2f}")
    
    success = (connected_accounts == 2 and len(investments) == 2)
    
    if success:
        print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"   Salvador Palma can now see his real MT5-based investments")
        print(f"   BALANCE Fund from DooTechnology: ${fund_breakdown.get('BALANCE', 0):,.2f}")
        print(f"   CORE Fund from VT Markets PAMM: ${fund_breakdown.get('CORE', 0):,.2f}")
    else:
        print(f"\n❌ DEPLOYMENT INCOMPLETE")
        print(f"   Check Windows VM and bridge service status")
        print(f"   Verify MT5 accounts are connected on Windows VM")
    
    return success

async def main():
    """Main deployment function"""
    
    try:
        print("🚀 MT5 WINDOWS BRIDGE DEPLOYMENT")
        print("=" * 60)
        print("CONNECTING TO REAL MT5 ACCOUNTS:")
        print("1. DooTechnology-Live: 9928326 → BALANCE Fund")
        print("2. VT Markets PAMM: 15759668 → CORE Fund")
        print()
        
        # Connect to real MT5 accounts
        connection_success = await connect_real_mt5_accounts_via_bridge()
        
        # Verify deployment
        deployment_success = await verify_deployment()
        
        if deployment_success:
            print(f"\n✅ SUCCESS: Salvador Palma MT5 investments are now live!")
            return 0
        else:
            print(f"\n❌ FAILURE: Deployment incomplete - check bridge service")
            return 1
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return 1

if __name__ == "__main__":
    print("REQUIREMENTS:")
    print("1. Windows VM running with MetaTrader5 terminal")
    print("2. MT5 Bridge Service running on Windows VM")
    print("3. Environment variable: MT5_BRIDGE_URL")
    print("4. Network connectivity between Linux app and Windows VM")
    print()
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)