"""
P&L Data Verification Script
Checks if all required data exists before building calculator
"""

from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB connection
MONGODB_URI = os.getenv("MONGO_URL", "mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority")
client = MongoClient(MONGODB_URI)
db = client.fidus_production

print("=" * 80)
print("FIDUS P&L DATA VERIFICATION")
print("=" * 80)

# Initialize results
verification_passed = True
issues = []

# Check 1: mt5_deals_history collection
print("\n1. Checking mt5_deals_history collection...")
collections = db.list_collection_names()
has_deals = "mt5_deals_history" in collections

if has_deals:
    print("   ✅ Collection exists")
    
    # Count balance operations
    balance_ops = db.mt5_deals_history.count_documents({"type": 2})
    print(f"   ✅ Balance operations found: {balance_ops}")
    
    if balance_ops == 0:
        print("   ⚠️  WARNING: No balance operations found")
        verification_passed = False
        issues.append("No balance operations in mt5_deals_history")
    
    # Sample document
    sample = db.mt5_deals_history.find_one({"type": 2})
    if sample:
        print(f"   ✅ Sample: Account {sample.get('account')}, Amount ${sample.get('profit', 0):.2f}")
else:
    print("   ❌ Collection does NOT exist")
    verification_passed = False
    issues.append("mt5_deals_history collection missing")

# Check 2: Balance operations per key account
print("\n2. Checking balance operations for key accounts...")
key_accounts = [885822, 886066, 886557, 886602, 886528]

for acc_num in key_accounts:
    withdrawals = list(db.mt5_deals_history.find({
        "account": acc_num,
        "type": 2,
        "profit": {"$lt": 0}
    }).limit(5))
    
    deposits = list(db.mt5_deals_history.find({
        "account": acc_num,
        "type": 2,
        "profit": {"$gt": 0}
    }).limit(5))
    
    total_w = sum(abs(w.get('profit', 0)) for w in withdrawals)
    total_d = sum(d.get('profit', 0) for d in deposits)
    
    print(f"   Account {acc_num}:")
    print(f"      Withdrawals: {len(withdrawals)} ops, ${total_w:,.2f}")
    print(f"      Deposits: {len(deposits)} ops, ${total_d:,.2f}")

# Check 3: mt5_account_config collection
print("\n3. Checking mt5_account_config collection...")
has_config = "mt5_account_config" in collections

if has_config:
    configs = list(db.mt5_account_config.find())
    print(f"   ✅ Collection exists with {len(configs)} accounts")
    
    if len(configs) == 0:
        print("   ⚠️  WARNING: No account configurations found")
        verification_passed = False
        issues.append("No accounts in mt5_account_config")
    
    # Check if configs have initial_allocation
    configs_with_allocation = [c for c in configs if c.get('initial_allocation')]
    print(f"   ✅ Accounts with initial_allocation: {len(configs_with_allocation)}/{len(configs)}")
    
    if len(configs_with_allocation) < len(configs):
        print(f"   ⚠️  WARNING: {len(configs) - len(configs_with_allocation)} accounts missing initial_allocation")
else:
    print("   ❌ Collection does NOT exist")
    verification_passed = False
    issues.append("mt5_account_config collection missing")

# Check 4: mt5_accounts collection (current data)
print("\n4. Checking mt5_accounts collection...")
has_accounts = "mt5_accounts" in collections

if has_accounts:
    accounts = list(db.mt5_accounts.find())
    print(f"   ✅ Collection exists with {len(accounts)} accounts")
    
    if len(accounts) == 0:
        print("   ⚠️  WARNING: No current account data")
        verification_passed = False
        issues.append("No accounts in mt5_accounts")
    
    # Check data freshness
    recent = db.mt5_accounts.find_one(sort=[("updated_at", -1)])
    if recent and recent.get('updated_at'):
        age = datetime.utcnow() - recent['updated_at']
        print(f"   ✅ Most recent update: {age.seconds // 60} minutes ago")
        
        if age.seconds > 600:  # 10 minutes
            print(f"   ⚠️  WARNING: Data may be stale (>10 minutes old)")
else:
    print("   ❌ Collection does NOT exist")
    verification_passed = False
    issues.append("mt5_accounts collection missing")

# Check 5: money_managers collection
print("\n5. Checking money_managers collection...")
has_managers = "money_managers" in collections

if has_managers:
    managers = list(db.money_managers.find())
    print(f"   ✅ Collection exists with {len(managers)} managers")
else:
    print("   ⚠️  Collection does not exist (optional)")

# Summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)

if verification_passed:
    print("\n✅ ALL REQUIRED DATA IS AVAILABLE")
    print("✅ You can proceed to build the PnLCalculator service")
    print("\nNEXT STEP: Create /backend/app/services/pnl_calculator.py")
else:
    print("\n❌ VERIFICATION FAILED - Issues found:")
    for issue in issues:
        print(f"   - {issue}")
    print("\n⚠️  You must fix these data issues before proceeding")
    print("\nREQUIRED ACTIONS:")
    if "mt5_deals_history collection missing" in issues:
        print("   1. Sync deal history from MT5 terminals")
    if "No balance operations" in issues:
        print("   2. Ensure type=2 deals are being synced")
    if "mt5_account_config collection missing" in issues:
        print("   3. Create account configuration documents")

client.close()

# Exit with appropriate code
exit(0 if verification_passed else 1)
