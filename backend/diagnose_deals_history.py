from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGO_URL", "mongodb+srv://YOUR_MONGODB_URL_HERE")
client = MongoClient(MONGODB_URI)
db = client.fidus_production

print("=" * 80)
print("MT5 DEALS HISTORY DIAGNOSTIC")
print("=" * 80)

# Check if collection exists
collections = db.list_collection_names()
print(f"\n1. Collections in database: {len(collections)}")
print(f"   mt5_deals_history exists: {'mt5_deals_history' in collections}")

if 'mt5_deals_history' not in collections:
    print("\n❌ CRITICAL: mt5_deals_history collection does NOT exist!")
    print("   This is why withdrawals show $0.00")
    print("   You need to sync deal history from MT5 terminals")
    exit(1)

# Check total documents
total_deals = db.mt5_deals_history.count_documents({})
print(f"\n2. Total deals in mt5_deals_history: {total_deals}")

if total_deals == 0:
    print("\n❌ CRITICAL: Collection exists but is EMPTY!")
    print("   No deal history has been synced from MT5")
    exit(1)

# Check for balance operations (type=2)
balance_ops = db.mt5_deals_history.count_documents({"type": 2})
print(f"\n3. Balance operations (type=2): {balance_ops}")

if balance_ops == 0:
    print("\n❌ CRITICAL: No type=2 (balance) operations found!")
    print("   Deposits and withdrawals are not being synced")
    
# Show sample documents
print("\n4. Sample documents from mt5_deals_history:")
samples = list(db.mt5_deals_history.find().limit(5))
for i, doc in enumerate(samples, 1):
    print(f"\n   Sample {i}:")
    print(f"   - Account: {doc.get('account')}")
    print(f"   - Type: {doc.get('type')}")
    print(f"   - Profit: ${doc.get('profit', 0):.2f}")
    print(f"   - Time: {doc.get('time')}")
    print(f"   - Comment: {doc.get('comment', 'N/A')}")

# Check specific accounts
print("\n5. Checking key accounts:")
key_accounts = [885822, 886066, 886557, 886602, 886528]

for acc in key_accounts:
    count = db.mt5_deals_history.count_documents({"account": acc})
    print(f"   Account {acc}: {count} deals")
    
    if count > 0:
        # Check for type=2 deals
        balance_count = db.mt5_deals_history.count_documents({
            "account": acc,
            "type": 2
        })
        print(f"      - Balance operations: {balance_count}")
        
        if balance_count > 0:
            # Show one example
            example = db.mt5_deals_history.find_one({
                "account": acc,
                "type": 2
            })
            print(f"      - Example: ${example.get('profit', 0):.2f} on {example.get('time')}")

# Check separation account specifically
print("\n6. Separation Account 886528 (where profits should be):")
sep_balance_ops = list(db.mt5_deals_history.find({
    "account": 886528,
    "type": 2
}).limit(10))

print(f"   Found {len(sep_balance_ops)} balance operations")
if len(sep_balance_ops) > 0:
    total_in = sum(d.get('profit', 0) for d in sep_balance_ops if d.get('profit', 0) > 0)
    print(f"   Total deposits to 886528: ${total_in:,.2f}")
    print("   Recent operations:")
    for op in sep_balance_ops[:5]:
        print(f"      ${op.get('profit', 0):,.2f} on {op.get('time')}")
else:
    print("   ❌ No balance operations found for separation account!")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)

client.close()
