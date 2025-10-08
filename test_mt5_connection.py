#!/usr/bin/env python3
"""
MT5 CONNECTION TEST FOR ALEJANDRO'S ACCOUNTS
===========================================

This script tests direct MT5 connectivity with the correct installation path.
Run this on the Windows VPS to verify MT5 connectivity.
"""

import MetaTrader5 as mt5
import sys
from datetime import datetime

print("=" * 60)
print("MT5 CONNECTION TEST - ALEJANDRO'S ACCOUNTS")
print("=" * 60)

# Use the CORRECT MT5 path as provided by user
mt5_path = r"C:\Program Files\MEX Atlantic MT5 Terminal\terminal64.exe"

print(f"\nMT5 Path: {mt5_path}")
print("Initializing MT5...")

# Initialize MT5 with the EXPLICIT path
if not mt5.initialize(path=mt5_path):
    error = mt5.last_error()
    print(f"❌ FAILED TO INITIALIZE MT5!")
    print(f"   Error code: {error}")
    print(f"\nTroubleshooting:")
    print(f"   1. Verify MT5 is at: {mt5_path}")
    print(f"   2. Check file permissions")
    print(f"   3. Ensure no other MT5 instances are running")
    print(f"   4. Try running as Administrator")
    sys.exit(1)

print("✅ MT5 INITIALIZED SUCCESSFULLY!")
version = mt5.version()
print(f"   Version: {version}")

terminal_info = mt5.terminal_info()
if terminal_info:
    print(f"   Terminal: {terminal_info.name}")
    print(f"   Company: {terminal_info.company}")
    print(f"   Path: {terminal_info.path}")
else:
    print("   ⚠️ Could not get terminal info")

# Test connection to ALL 4 of Alejandro's MT5 accounts
print("\n" + "=" * 60)
print("TESTING ALEJANDRO'S 4 MT5 ACCOUNTS")
print("=" * 60)

# Alejandro's REAL account details as specified
accounts = [
    {
        "login": 886557, 
        "allocated_amount": 80000.00, 
        "fund": "BALANCE",
        "description": "Main BALANCE account"
    },
    {
        "login": 886066, 
        "allocated_amount": 10000.00, 
        "fund": "BALANCE",
        "description": "Secondary BALANCE account"
    },
    {
        "login": 886602, 
        "allocated_amount": 10000.00, 
        "fund": "BALANCE",
        "description": "Tertiary BALANCE account"
    },
    {
        "login": 885822, 
        "allocated_amount": 18151.41, 
        "fund": "CORE",
        "description": "CORE fund account"
    },
]

# REAL credentials as specified
password = "FIDUS13@"
server = "MEXAtlantic-Real"

print(f"Server: {server}")
print(f"Password: {password}")
print(f"Expected Total: $118,151.41")

results = []
total_allocated = 118151.41

for i, account in enumerate(accounts, 1):
    print(f"\n{i}. Testing Account {account['login']} ({account['fund']} Fund)...")
    print(f"   Description: {account['description']}")
    print(f"   Expected Amount: ${account['allocated_amount']:,.2f}")
    
    # Attempt login
    authorized = mt5.login(account['login'], password, server)
    
    if not authorized:
        error = mt5.last_error()
        print(f"   ❌ LOGIN FAILED")
        print(f"   Error Code: {error[0]} - {error[1]}")
        
        results.append({
            "login": account['login'],
            "fund": account['fund'],
            "status": "LOGIN_FAILED",
            "error": error,
            "allocated_amount": account['allocated_amount']
        })
        continue
    
    print(f"   ✅ LOGIN SUCCESSFUL")
    
    # Get account information
    account_info = mt5.account_info()
    if account_info:
        balance = account_info.balance
        equity = account_info.equity
        margin = account_info.margin
        margin_free = account_info.margin_free
        profit = account_info.profit
        currency = account_info.currency
        leverage = account_info.leverage
        
        print(f"   📊 LIVE ACCOUNT DATA:")
        print(f"      Balance: ${balance:,.2f} {currency}")
        print(f"      Equity: ${equity:,.2f} {currency}")
        print(f"      Profit/Loss: ${profit:,.2f} {currency}")
        print(f"      Margin Used: ${margin:,.2f} {currency}")
        print(f"      Free Margin: ${margin_free:,.2f} {currency}")
        print(f"      Leverage: 1:{leverage}")
        print(f"      Server: {account_info.server}")
        
        # Calculate return percentage vs allocated
        return_pct = (profit / account['allocated_amount'] * 100) if account['allocated_amount'] > 0 else 0
        print(f"      Return vs Allocated: {return_pct:.2f}%")
        
        results.append({
            "login": account['login'],
            "fund": account['fund'],
            "status": "SUCCESS",
            "balance": balance,
            "equity": equity,
            "profit": profit,
            "margin": margin,
            "margin_free": margin_free,
            "currency": currency,
            "leverage": leverage,
            "return_pct": return_pct,
            "allocated_amount": account['allocated_amount']
        })
    else:
        print(f"   ⚠️ LOGIN OK but could not retrieve account info")
        results.append({
            "login": account['login'],
            "fund": account['fund'],
            "status": "CONNECTED_NO_DATA",
            "allocated_amount": account['allocated_amount']
        })

# Get current positions if any account is connected
print(f"\n" + "=" * 40)
print("CHECKING OPEN POSITIONS")
print("=" * 40)

for result in results:
    if result["status"] == "SUCCESS":
        print(f"\nChecking positions for account {result['login']}...")
        
        # Login to this account
        if mt5.login(result['login'], password, server):
            positions = mt5.positions_get()
            
            if positions:
                print(f"   📈 {len(positions)} open position(s):")
                for pos in positions:
                    print(f"      {pos.symbol}: {pos.type_str} {pos.volume} lots, P&L: ${pos.profit:.2f}")
            else:
                print(f"   📊 No open positions")
        else:
            print(f"   ❌ Could not reconnect to check positions")

# Final Summary
print("\n" + "=" * 60)
print("FINAL TEST SUMMARY")
print("=" * 60)

total_equity = 0
total_profit = 0
total_balance = 0
successful_connections = 0

balance_fund_total = 0
core_fund_total = 0

for result in results:
    status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
    print(f"{status_icon} Account {result['login']} ({result['fund']}): {result['status']}")
    
    if result["status"] == "SUCCESS":
        successful_connections += 1
        total_equity += result["equity"]
        total_profit += result["profit"]
        total_balance += result["balance"]
        
        if result["fund"] == "BALANCE":
            balance_fund_total += result["equity"]
        elif result["fund"] == "CORE":
            core_fund_total += result["equity"]
        
        print(f"   Balance: ${result['balance']:,.2f} | Equity: ${result['equity']:,.2f} | P&L: ${result['profit']:,.2f}")
    elif result["status"] == "LOGIN_FAILED":
        print(f"   Error: {result['error']}")

print(f"\n📊 PORTFOLIO SUMMARY:")
print(f"   Successful Connections: {successful_connections}/4")

if successful_connections > 0:
    print(f"   Total Balance: ${total_balance:,.2f}")
    print(f"   Total Equity: ${total_equity:,.2f}")
    print(f"   Total P&L: ${total_profit:,.2f}")
    print(f"   Overall Return: {(total_profit/total_allocated)*100:.2f}%")
    
    print(f"\n💰 BY FUND:")
    print(f"   BALANCE Fund Total: ${balance_fund_total:,.2f}")
    print(f"   CORE Fund Total: ${core_fund_total:,.2f}")
    
    # Performance vs Expected
    balance_expected_monthly = 100000 * 0.025  # 2.5% monthly
    core_expected_monthly = 18151.41 * 0.015   # 1.5% monthly
    
    print(f"\n🎯 PERFORMANCE vs EXPECTED:")
    print(f"   BALANCE Expected (monthly): ${balance_expected_monthly:,.2f}")
    print(f"   CORE Expected (monthly): ${core_expected_monthly:,.2f}")
    print(f"   Total Expected: ${balance_expected_monthly + core_expected_monthly:,.2f}/month")

print(f"\n⏰ Test completed at: {datetime.now()}")

# Shutdown MT5
mt5.shutdown()
print(f"\n✅ MT5 CONNECTION TEST COMPLETE!")

if successful_connections == 4:
    print(f"🎉 ALL 4 ACCOUNTS CONNECTED SUCCESSFULLY!")
    print(f"💡 MT5 Bridge Service can now be configured with this path.")
else:
    print(f"⚠️  Only {successful_connections}/4 accounts connected.")
    print(f"💡 Check credentials for failed accounts.")