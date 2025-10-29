# MT5 Bridge Connection Diagnostic
# This script checks how the Bridge is connecting to MT5

import requests
import json

def check_bridge_connection_method():
    """Check if Bridge is using single connection or multiple logins"""
    
    print("=" * 70)
    print("MT5 BRIDGE CONNECTION DIAGNOSTIC")
    print("=" * 70)
    print()
    
    bridge_url = "http://92.118.45.135:8000"
    
    # Test multiple account queries in quick succession
    accounts = ["886557", "886066", "886602"]
    
    print("Testing rapid account queries (should NOT cause terminal switching):")
    print()
    
    for account in accounts:
        try:
            response = requests.get(
                f"{bridge_url}/api/mt5/account/{account}/info",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                balance = data.get('live_data', {}).get('balance', 0)
                print(f"✓ Account {account}: ${balance:.2f}")
            else:
                print(f"✗ Account {account}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"✗ Account {account}: Error - {str(e)}")
    
    print()
    print("=" * 70)
    print("DIAGNOSIS:")
    print("=" * 70)
    print()
    print("If you see:")
    print("  • All accounts return real balances → Bridge is working correctly")
    print("  • Some accounts show $0 → Bridge is causing terminal switching")
    print()
    print("The Bridge should use MetaTrader5.initialize() ONCE")
    print("Then query all accounts via positions_get(group='*')")
    print("WITHOUT calling initialize() or login() for each account")
    print()

if __name__ == "__main__":
    check_bridge_connection_method()
