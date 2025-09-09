#!/usr/bin/env python3
"""
MT5 Data Enforcer - Production Data Integrity
=============================================

This script ensures that ALL investment data comes ONLY from MT5 accounts.
It runs checks and enforces production constraints.
"""

import pymongo
from pymongo import MongoClient
import os
from datetime import datetime, timezone
import sys

def connect_to_database():
    """Connect to production database"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    return client['fidus_investment_db']

def enforce_mt5_data_only():
    """Enforce that all investment data comes from MT5 accounts only"""
    print("🔒 MT5 DATA ENFORCER - PRODUCTION MODE")
    print("=" * 60)
    
    db = connect_to_database()
    
    # 1. Check all investments have MT5 mapping
    print("🔍 Checking investment data integrity...")
    
    all_investments = list(db.investments.find({}))
    valid_investments = 0
    invalid_investments = 0
    
    for inv in all_investments:
        client_id = inv['client_id']
        fund_code = inv['fund_code']
        investment_id = inv['investment_id']
        
        # Check MT5 requirements
        has_mt5_login = 'mt5_login' in inv and inv['mt5_login']
        has_broker_code = 'broker_code' in inv and inv['broker_code']
        is_mt5_source = inv.get('data_source') == 'MT5_REAL_TIME'
        
        if has_mt5_login and has_broker_code and is_mt5_source:
            # Verify MT5 account exists
            mt5_account = db.mt5_accounts.find_one({
                'client_id': client_id,
                'mt5_login': inv['mt5_login'],
                'broker_code': inv['broker_code'],
                'status': 'active'
            })
            
            if mt5_account:
                valid_investments += 1
                print(f"   ✅ {client_id} - {fund_code}: MT5 {inv['mt5_login']} ({inv['broker_code']})")
            else:
                invalid_investments += 1
                print(f"   ❌ {client_id} - {fund_code}: MT5 account not found!")
        else:
            invalid_investments += 1
            print(f"   ❌ {client_id} - {fund_code}: Missing MT5 mapping!")
    
    print(f"\n📊 INVESTMENT DATA INTEGRITY:")
    print(f"   Valid MT5-mapped investments: {valid_investments}")
    print(f"   Invalid investments: {invalid_investments}")
    
    # 2. Sync investment values with MT5 accounts
    print(f"\n🔄 SYNCING INVESTMENT VALUES WITH MT5 DATA...")
    
    synced_count = 0
    for inv in all_investments:
        if inv.get('data_source') == 'MT5_REAL_TIME' and inv.get('mt5_login'):
            mt5_account = db.mt5_accounts.find_one({
                'client_id': inv['client_id'],
                'mt5_login': inv['mt5_login'],
                'broker_code': inv['broker_code']
            })
            
            if mt5_account:
                # Update investment current_value from MT5 equity
                current_equity = mt5_account['current_equity']
                
                db.investments.update_one(
                    {'investment_id': inv['investment_id']},
                    {
                        '$set': {
                            'current_value': current_equity,
                            'last_mt5_sync': datetime.now(timezone.utc)
                        }
                    }
                )
                synced_count += 1
                print(f"   ✅ Synced {inv['fund_code']}: ${current_equity:,.2f}")
    
    print(f"\n✅ Synced {synced_count} investments with MT5 data")
    
    # 3. Create monitoring rules
    print(f"\n🔒 INSTALLING PRODUCTION MONITORING RULES...")
    
    monitoring_rules = {
        'rule_type': 'mt5_data_enforcer',
        'created_at': datetime.now(timezone.utc),
        'rules': {
            'no_mock_data': True,
            'mt5_mapping_required': True,
            'allowed_data_sources': ['MT5_REAL_TIME'],
            'blocked_operations': ['manual_investment_creation'],
            'required_fields': ['mt5_login', 'broker_code', 'data_source']
        }
    }
    
    db.system_rules.replace_one(
        {'rule_type': 'mt5_data_enforcer'},
        monitoring_rules,
        upsert=True
    )
    
    print("   ✅ Production monitoring rules installed")
    
    # 4. Final validation
    print(f"\n🎯 FINAL PRODUCTION VALIDATION:")
    
    total_portfolio_value = 0
    client_portfolios = {}
    
    for inv in db.investments.find({'data_source': 'MT5_REAL_TIME'}):
        client_id = inv['client_id']
        current_value = inv.get('current_value', 0)
        
        if client_id not in client_portfolios:
            client_portfolios[client_id] = {'total': 0, 'funds': {}}
        
        client_portfolios[client_id]['total'] += current_value
        client_portfolios[client_id]['funds'][inv['fund_code']] = current_value
        total_portfolio_value += current_value
    
    print(f"   Total System AUM: ${total_portfolio_value:,.2f}")
    
    for client_id, portfolio in client_portfolios.items():
        client_name = 'Unknown'
        client_doc = db.users.find_one({'user_id': client_id})
        if client_doc:
            client_name = client_doc.get('name', client_id)
        
        print(f"   {client_name}: ${portfolio['total']:,.2f}")
        for fund, value in portfolio['funds'].items():
            print(f"     - {fund}: ${value:,.2f}")
    
    print(f"\n🔒 PRODUCTION STATUS: MT5 DATA ONLY ENFORCED")
    return valid_investments, invalid_investments

if __name__ == "__main__":
    try:
        valid, invalid = enforce_mt5_data_only()
        
        if invalid > 0:
            print(f"\n⚠️  WARNING: {invalid} investments need MT5 mapping!")
            sys.exit(1)
        else:
            print(f"\n✅ SUCCESS: All {valid} investments are MT5-mapped")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)