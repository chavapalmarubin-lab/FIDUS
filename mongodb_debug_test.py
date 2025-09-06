#!/usr/bin/env python3
"""
MongoDB Debug Test
Check if MT5 accounts are being stored and retrieved correctly from MongoDB
"""

import sys
import os
sys.path.append('/app/backend')

from mongodb_integration import mongodb_manager
from datetime import datetime, timezone

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("🔍 Testing MongoDB Connection...")
    
    try:
        # Test basic connection
        print(f"   Database Name: {mongodb_manager.db_name}")
        print(f"   MongoDB URL: {os.environ.get('MONGO_URL', 'Not set')}")
        
        # Test ping
        result = mongodb_manager.client.admin.command('ping')
        print(f"   ✅ MongoDB Ping: {result}")
        
        # List collections
        collections = mongodb_manager.db.list_collection_names()
        print(f"   📊 Collections: {collections}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ MongoDB connection failed: {str(e)}")
        return False

def test_mt5_accounts_collection():
    """Test MT5 accounts collection directly"""
    print("\n🔍 Testing MT5 Accounts Collection...")
    
    try:
        # Count documents in mt5_accounts collection
        count = mongodb_manager.db.mt5_accounts.count_documents({})
        print(f"   📊 Total MT5 accounts in database: {count}")
        
        # Get all MT5 accounts
        accounts = list(mongodb_manager.db.mt5_accounts.find({}))
        print(f"   📊 Retrieved {len(accounts)} accounts")
        
        if accounts:
            print(f"   🔍 Sample account structure:")
            sample_account = accounts[0]
            for key, value in sample_account.items():
                if key != '_id':  # Skip MongoDB ObjectId
                    print(f"      {key}: {value}")
                    
            # Look for Salvador's account specifically
            salvador_accounts = []
            for acc in accounts:
                if (acc.get('client_id') == 'client_003' or 
                    acc.get('mt5_login') == 9928326 or
                    'client_003' in str(acc.get('account_id', ''))):
                    salvador_accounts.append(acc)
                    
            print(f"   🎯 Salvador's accounts found: {len(salvador_accounts)}")
            for acc in salvador_accounts:
                print(f"      - Account ID: {acc.get('account_id')}")
                print(f"      - Client ID: {acc.get('client_id')}")
                print(f"      - MT5 Login: {acc.get('mt5_login')}")
                print(f"      - Fund Code: {acc.get('fund_code')}")
                print(f"      - Status: {acc.get('status')}")
                print(f"      - Created: {acc.get('created_at')}")
        else:
            print(f"   ❌ No MT5 accounts found in database!")
            
        return len(accounts) > 0
        
    except Exception as e:
        print(f"   ❌ Error accessing MT5 accounts collection: {str(e)}")
        return False

def test_mongodb_manager_methods():
    """Test MongoDB manager methods"""
    print("\n🔍 Testing MongoDB Manager Methods...")
    
    try:
        # Test get_all_mt5_accounts method
        accounts = mongodb_manager.get_all_mt5_accounts()
        print(f"   📊 get_all_mt5_accounts() returned: {len(accounts)} accounts")
        
        if accounts:
            print(f"   ✅ MongoDB manager can retrieve accounts")
            for acc in accounts:
                print(f"      - {acc.get('account_id')} (Client: {acc.get('client_id')}, Login: {acc.get('mt5_login')})")
        else:
            print(f"   ❌ MongoDB manager returned empty list")
            
        # Test get_client_mt5_accounts for Salvador
        salvador_accounts = mongodb_manager.get_client_mt5_accounts('client_003')
        print(f"   📊 get_client_mt5_accounts('client_003') returned: {len(salvador_accounts)} accounts")
        
        if salvador_accounts:
            print(f"   ✅ Found Salvador's accounts via MongoDB manager")
            for acc in salvador_accounts:
                print(f"      - {acc.get('account_id')} (Login: {acc.get('mt5_login')})")
        else:
            print(f"   ❌ No accounts found for Salvador via MongoDB manager")
            
        return len(accounts) > 0
        
    except Exception as e:
        print(f"   ❌ Error testing MongoDB manager methods: {str(e)}")
        return False

def test_create_test_account():
    """Test creating a test MT5 account"""
    print("\n🔍 Testing MT5 Account Creation...")
    
    try:
        # Create test account data
        test_account_data = {
            'account_id': f'test_mt5_account_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'client_id': 'client_003',
            'fund_code': 'BALANCE',
            'broker_code': 'dootechnology',
            'broker_name': 'DooTechnology',
            'mt5_login': 9928326,
            'mt5_server': 'DooTechnology-Live',
            'total_allocated': 100000.0,
            'current_equity': 100000.0,
            'profit_loss': 0.0,
            'investment_ids': [],
            'status': 'active',
            'manual_entry': True
        }
        
        # Create account using MongoDB manager
        created_account_id = mongodb_manager.create_mt5_account(test_account_data)
        
        if created_account_id:
            print(f"   ✅ Test account created: {created_account_id}")
            
            # Verify it was stored
            accounts = mongodb_manager.get_all_mt5_accounts()
            found_account = None
            for acc in accounts:
                if acc.get('account_id') == created_account_id:
                    found_account = acc
                    break
                    
            if found_account:
                print(f"   ✅ Test account found in database after creation")
                print(f"      - Account ID: {found_account.get('account_id')}")
                print(f"      - Client ID: {found_account.get('client_id')}")
                print(f"      - MT5 Login: {found_account.get('mt5_login')}")
                return True
            else:
                print(f"   ❌ Test account NOT found in database after creation")
                return False
        else:
            print(f"   ❌ Failed to create test account")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing account creation: {str(e)}")
        return False

def test_database_consistency():
    """Test database consistency and data integrity"""
    print("\n🔍 Testing Database Consistency...")
    
    try:
        # Check if collections exist
        collections = mongodb_manager.db.list_collection_names()
        required_collections = ['mt5_accounts', 'investments', 'users', 'client_profiles']
        
        print(f"   📊 Available collections: {collections}")
        
        missing_collections = [col for col in required_collections if col not in collections]
        if missing_collections:
            print(f"   ⚠️  Missing collections: {missing_collections}")
        else:
            print(f"   ✅ All required collections exist")
            
        # Check Salvador's investment data
        investments_count = mongodb_manager.db.investments.count_documents({'client_id': 'client_003'})
        print(f"   📊 Salvador's investments in database: {investments_count}")
        
        if investments_count > 0:
            investments = list(mongodb_manager.db.investments.find({'client_id': 'client_003'}))
            for inv in investments:
                print(f"      - Investment ID: {inv.get('investment_id')}")
                print(f"      - Fund Code: {inv.get('fund_code')}")
                print(f"      - Principal: ${inv.get('principal_amount', 0):,.2f}")
        else:
            print(f"   ❌ No investments found for Salvador in database")
            
        # Check Salvador's user data
        user = mongodb_manager.db.users.find_one({'user_id': 'client_003'})
        if user:
            print(f"   ✅ Salvador's user record found")
            print(f"      - Username: {user.get('username')}")
            print(f"      - User Type: {user.get('user_type')}")
        else:
            print(f"   ❌ Salvador's user record not found")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing database consistency: {str(e)}")
        return False

def main():
    """Main function to run MongoDB debug tests"""
    print("🔧 MONGODB DEBUG TEST FOR MT5 ACCOUNTS")
    print("="*60)
    print("Goal: Verify if MT5 accounts are being stored and retrieved correctly")
    print("="*60)
    
    # Run all tests
    tests = [
        ("MongoDB Connection", test_mongodb_connection),
        ("MT5 Accounts Collection", test_mt5_accounts_collection),
        ("MongoDB Manager Methods", test_mongodb_manager_methods),
        ("Create Test Account", test_create_test_account),
        ("Database Consistency", test_database_consistency)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"RUNNING: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 MONGODB DEBUG TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"📊 Tests Passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    if passed == total:
        print(f"\n✅ All MongoDB tests passed - database is working correctly")
        return 0
    else:
        print(f"\n❌ {total - passed} MongoDB tests failed - database issues detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())