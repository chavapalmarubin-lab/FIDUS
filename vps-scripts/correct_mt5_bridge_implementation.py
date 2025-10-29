# CORRECT MT5 Bridge Implementation
# This is how the Bridge SHOULD query multiple accounts

import MetaTrader5 as mt5
from datetime import datetime

# INITIALIZE ONCE (not per account!)
if not mt5.initialize():
    print("MT5 initialization failed")
    mt5.shutdown()
    exit()

print("MT5 initialized successfully")
print(f"MT5 version: {mt5.version()}")
print()

# Login to MANAGER account ONCE
manager_account = 886557
manager_password = "your_password"  # From VPS
manager_server = "MEXAtlantic-Demo"  # Or your server name

authorized = mt5.login(manager_account, manager_password, manager_server)

if not authorized:
    print(f"Failed to login to manager account {manager_account}")
    mt5.shutdown()
    exit()

print(f"✓ Logged in to manager account: {manager_account}")
print()

# NOW QUERY ALL ACCOUNTS WITHOUT SWITCHING
accounts_to_query = [886557, 886066, 886602, 885822, 886528, 891215, 891234]

print("Querying all accounts through single connection:")
print("=" * 60)

for account_number in accounts_to_query:
    # Get account info
    account_info = mt5.account_info()
    
    # Get positions for this account
    # NOTE: If manager account has access, you can query any account's positions
    # Otherwise, you need to use positions_get() with symbol filter
    
    positions = mt5.positions_get(group=f"*{account_number}*")
    
    if positions is not None:
        total_profit = sum([pos.profit for pos in positions])
        print(f"Account {account_number}:")
        print(f"  Open Positions: {len(positions)}")
        print(f"  Total P&L: ${total_profit:.2f}")
    else:
        print(f"Account {account_number}: No positions or no access")
    
    print()

# Shutdown ONCE at the end
mt5.shutdown()
print("=" * 60)
print("✓ Query complete - MT5 Terminal did NOT switch accounts")
