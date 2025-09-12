#!/usr/bin/env python3
"""
Direct MongoDB Test
"""

from mongodb_integration import mongodb_manager
import json

# Test direct database access
print('Testing direct MongoDB access...')
try:
    investments = mongodb_manager.get_client_investments('client_003')
    print(f'Direct DB query found {len(investments)} investments for client_003')
    for inv in investments:
        print(f'  - {inv.get("fund_code")}: ${inv.get("principal_amount", 0):,.2f}')
        
    # Test MT5 accounts
    mt5_accounts = mongodb_manager.get_client_mt5_accounts('client_003')
    print(f'Direct DB query found {len(mt5_accounts)} MT5 accounts for client_003')
    for acc in mt5_accounts:
        print(f'  - Login: {acc.get("login")}, Broker: {acc.get("broker")}')
        
except Exception as e:
    print(f'Error: {e}')