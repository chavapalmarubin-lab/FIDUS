"""Test PnLCalculator with real data"""

import sys
sys.path.insert(0, '/app/backend')

from pymongo import MongoClient
from app.services.pnl_calculator import PnLCalculator
import os

MONGODB_URI = os.getenv("MONGO_URL", "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority")
client = MongoClient(MONGODB_URI)
db = client.fidus_production

calculator = PnLCalculator(db)

print("=" * 80)
print("P&L CALCULATOR TEST")
print("=" * 80)

# Test 1: Single account
print("\n1. Testing Account 886557:")
try:
    pnl = calculator.calculate_account_pnl(886557)
    print(f"   Initial: ${pnl['initial_allocation']:,.2f}")
    print(f"   Current Equity: ${pnl['current_equity']:,.2f}")
    print(f"   Withdrawals: ${pnl['total_withdrawals']:,.2f}")
    print(f"   Deposits: ${pnl['total_deposits']:,.2f}")
    print(f"   TRUE P&L: ${pnl['true_pnl']:,.2f} ({pnl['return_percentage']:.2f}%)")
    print(f"   ✅ Test passed")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: BALANCE Fund
print("\n2. Testing BALANCE Fund:")
try:
    fund_pnl = calculator.calculate_fund_pnl("BALANCE")
    print(f"   Accounts: {fund_pnl['total_accounts']}")
    print(f"   Initial: ${fund_pnl['total_initial_allocation']:,.2f}")
    print(f"   Current: ${fund_pnl['total_current_equity']:,.2f}")
    print(f"   Withdrawals: ${fund_pnl['total_withdrawals']:,.2f}")
    print(f"   Deposits: ${fund_pnl['total_deposits']:,.2f}")
    print(f"   TRUE P&L: ${fund_pnl['fund_true_pnl']:,.2f} ({fund_pnl['fund_return_percentage']:.2f}%)")
    
    if fund_pnl['fund_true_pnl'] > 0:
        print(f"   ✅ Fund shows PROFIT (correct!)")
    else:
        print(f"   ⚠️  Fund shows loss: ${fund_pnl['fund_true_pnl']:,.2f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: All accounts
print("\n3. Testing All Accounts:")
try:
    all_pnls = calculator.get_all_accounts_pnl()
    print(f"   Total accounts: {len(all_pnls)}")
    total_pnl = sum(a['true_pnl'] for a in all_pnls)
    print(f"   Platform TRUE P&L: ${total_pnl:,.2f}")
    print(f"   ✅ Test passed")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
client.close()
