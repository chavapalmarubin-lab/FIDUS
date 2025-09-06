#!/usr/bin/env python3
"""
Emergency Data Cleanup Script
Removes fake test investments created during MT5 testing
ONLY removes client_001 test data, preserves Salvador Palma (client_003) legitimate data
"""

import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from mongodb_integration import mongodb_manager

def cleanup_fake_test_data():
    """Remove fake client_001 test investments and MT5 mappings"""
    
    print("🚨 EMERGENCY DATA CLEANUP - REMOVING FAKE TEST DATA")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_investment_db')
        client = MongoClient(mongo_url)
        db_name = mongo_url.split('/')[-1]
        db = client[db_name]
        
        print(f"📊 Connected to database: {db_name}")
        
        # 1. Check current state before cleanup
        print("\n📋 BEFORE CLEANUP:")
        investments_before = list(db.investments.find({}, {"client_id": 1, "fund_code": 1, "principal_amount": 1, "created_at": 1}))
        mt5_accounts_before = list(db.mt5_accounts.find({}, {"client_id": 1, "account_id": 1, "total_allocated": 1}))
        
        print(f"   - Total investments: {len(investments_before)}")
        print(f"   - Total MT5 accounts: {len(mt5_accounts_before)}")
        
        # Show breakdown by client
        client_investments = {}
        for inv in investments_before:
            cid = inv['client_id']
            if cid not in client_investments:
                client_investments[cid] = 0
            client_investments[cid] += 1
        
        for client_id, count in client_investments.items():
            print(f"   - {client_id}: {count} investments")
        
        # 2. Identify fake client_001 data (created during testing on 2025-09-06)
        fake_investments = list(db.investments.find({
            "client_id": "client_001",
            "created_at": {"$gte": datetime(2025, 9, 6, 21, 0, 0, tzinfo=timezone.utc)}
        }))
        
        fake_mt5_accounts = list(db.mt5_accounts.find({
            "client_id": "client_001"
        }))
        
        print(f"\n🎯 FAKE DATA IDENTIFIED:")
        print(f"   - Fake investments to delete: {len(fake_investments)}")
        print(f"   - Fake MT5 accounts to delete: {len(fake_mt5_accounts)}")
        
        # Show details of fake data
        for inv in fake_investments:
            print(f"   - Investment: {inv['fund_code']} ${inv['principal_amount']:,.2f} ({inv.get('created_at', 'No date')})")
        
        # 3. Verify Salvador Palma data is preserved
        salvador_investments = list(db.investments.find({"client_id": "client_003"}))
        salvador_mt5 = list(db.mt5_accounts.find({"client_id": "client_003"}))
        
        print(f"\n✅ SALVADOR PALMA DATA TO PRESERVE:")
        print(f"   - Legitimate investments: {len(salvador_investments)}")
        print(f"   - Legitimate MT5 accounts: {len(salvador_mt5)}")
        
        for inv in salvador_investments:
            print(f"   - Investment: {inv['fund_code']} ${inv['principal_amount']:,.2f} ({inv.get('created_at', 'No date')})")
        
        # 4. Confirm cleanup
        if len(fake_investments) > 0 or len(fake_mt5_accounts) > 0:
            print(f"\n⚠️  READY TO DELETE:")
            print(f"   - {len(fake_investments)} fake investments")
            print(f"   - {len(fake_mt5_accounts)} fake MT5 accounts")
            
            response = input("\n🚨 Proceed with cleanup? (yes/no): ").strip().lower()
            
            if response == 'yes':
                # Delete fake investments
                if len(fake_investments) > 0:
                    result = db.investments.delete_many({
                        "client_id": "client_001",
                        "created_at": {"$gte": datetime(2025, 9, 6, 21, 0, 0, tzinfo=timezone.utc)}
                    })
                    print(f"✅ Deleted {result.deleted_count} fake investments")
                
                # Delete fake MT5 accounts
                if len(fake_mt5_accounts) > 0:
                    result = db.mt5_accounts.delete_many({
                        "client_id": "client_001"
                    })
                    print(f"✅ Deleted {result.deleted_count} fake MT5 accounts")
                
                # 5. Verify cleanup results
                print("\n📋 AFTER CLEANUP:")
                investments_after = list(db.investments.find({}, {"client_id": 1, "fund_code": 1, "principal_amount": 1}))
                mt5_accounts_after = list(db.mt5_accounts.find({}, {"client_id": 1, "account_id": 1}))
                
                print(f"   - Total investments: {len(investments_after)}")
                print(f"   - Total MT5 accounts: {len(mt5_accounts_after)}")
                
                # Verify Salvador Palma data intact
                salvador_investments_after = list(db.investments.find({"client_id": "client_003"}))
                if len(salvador_investments_after) == len(salvador_investments):
                    print("✅ Salvador Palma data preserved correctly")
                else:
                    print("❌ WARNING: Salvador Palma data may have been affected!")
                
                print("\n🎉 CLEANUP COMPLETED SUCCESSFULLY!")
                print("   - Fund Performance dashboard should now show only Salvador Palma's BALANCE fund")
                
            else:
                print("❌ Cleanup cancelled by user")
        else:
            print("\n✅ No fake data found - database is clean")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    cleanup_fake_test_data()