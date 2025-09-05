#!/usr/bin/env python3
"""
MT5 Account Direct MongoDB Fix
=============================

Since there's no DELETE API endpoint for MT5 accounts, this script directly
manipulates the MongoDB data to fix the duplication issue.

Strategy:
1. Connect directly to MongoDB
2. Delete all client_001 accounts with login 9928326
3. Update one of Salvador's BALANCE accounts to use login 9928326
4. Verify the fix
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime, timezone
import json

class MT5DirectFixer:
    def __init__(self):
        # Get MongoDB connection from environment
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        try:
            self.client = MongoClient(mongo_url)
            self.db = self.client[db_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {db_name}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            raise
        
        self.actions_taken = []
    
    def get_current_mt5_accounts(self):
        """Get current MT5 accounts from MongoDB"""
        try:
            accounts = list(self.db.mt5_accounts.find({}))
            print(f"📊 Found {len(accounts)} MT5 accounts in database")
            return accounts
        except Exception as e:
            print(f"❌ Error getting MT5 accounts: {str(e)}")
            return []
    
    def analyze_current_state(self):
        """Analyze current MT5 account state"""
        print("\n" + "="*60)
        print("ANALYZING CURRENT MT5 ACCOUNT STATE")
        print("="*60)
        
        accounts = self.get_current_mt5_accounts()
        
        # Find accounts with login 9928326
        login_9928326_accounts = [acc for acc in accounts if acc.get('mt5_login') == 9928326]
        
        print(f"\n🔍 ACCOUNTS WITH LOGIN 9928326: {len(login_9928326_accounts)}")
        for acc in login_9928326_accounts:
            print(f"   - {acc.get('account_id')}: {acc.get('client_id')} ({acc.get('fund_code')})")
        
        # Find Salvador's accounts
        salvador_accounts = [acc for acc in accounts if acc.get('client_id') == 'client_0fd630c3']
        
        print(f"\n👤 SALVADOR PALMA ACCOUNTS: {len(salvador_accounts)}")
        for acc in salvador_accounts:
            print(f"   - {acc.get('account_id')}: {acc.get('fund_code')} (Login: {acc.get('mt5_login')})")
        
        # Find client_001 accounts
        client_001_accounts = [acc for acc in accounts if acc.get('client_id') == 'client_001']
        
        print(f"\n👤 CLIENT_001 ACCOUNTS: {len(client_001_accounts)}")
        for acc in client_001_accounts:
            if acc.get('mt5_login') == 9928326:
                print(f"   - {acc.get('account_id')}: {acc.get('fund_code')} (Login: {acc.get('mt5_login')}) ⚠️  DUPLICATE")
            else:
                print(f"   - {acc.get('account_id')}: {acc.get('fund_code')} (Login: {acc.get('mt5_login')})")
        
        return login_9928326_accounts, salvador_accounts, client_001_accounts
    
    def delete_duplicate_accounts(self, login_9928326_accounts):
        """Delete duplicate client_001 accounts with login 9928326"""
        print("\n" + "="*60)
        print("DELETING DUPLICATE CLIENT_001 ACCOUNTS")
        print("="*60)
        
        # Find client_001 accounts with login 9928326
        duplicates_to_delete = [
            acc for acc in login_9928326_accounts 
            if acc.get('client_id') == 'client_001'
        ]
        
        print(f"🗑️  Found {len(duplicates_to_delete)} duplicate accounts to delete")
        
        deleted_count = 0
        for account in duplicates_to_delete:
            account_id = account.get('account_id')
            print(f"\n   Deleting: {account_id}")
            print(f"   Client: {account.get('client_id')}")
            print(f"   Fund: {account.get('fund_code')}")
            print(f"   Login: {account.get('mt5_login')}")
            
            try:
                result = self.db.mt5_accounts.delete_one({'account_id': account_id})
                if result.deleted_count > 0:
                    print(f"   ✅ Successfully deleted")
                    deleted_count += 1
                    self.actions_taken.append(f"Deleted duplicate account {account_id}")
                else:
                    print(f"   ❌ Account not found for deletion")
            except Exception as e:
                print(f"   ❌ Error deleting account: {str(e)}")
        
        print(f"\n📊 DELETION SUMMARY: {deleted_count}/{len(duplicates_to_delete)} accounts deleted")
        return deleted_count == len(duplicates_to_delete)
    
    def create_correct_salvador_account(self, salvador_accounts):
        """Create or update Salvador's account to have login 9928326"""
        print("\n" + "="*60)
        print("CREATING CORRECT SALVADOR ACCOUNT")
        print("="*60)
        
        # Find Salvador's BALANCE accounts
        salvador_balance_accounts = [
            acc for acc in salvador_accounts 
            if acc.get('fund_code') == 'BALANCE'
        ]
        
        if not salvador_balance_accounts:
            print("❌ No Salvador BALANCE accounts found!")
            return False
        
        # Use the first BALANCE account and update it
        target_account = salvador_balance_accounts[0]
        account_id = target_account.get('account_id')
        
        print(f"\n🎯 Updating Salvador's account: {account_id}")
        print(f"   Current Login: {target_account.get('mt5_login')}")
        print(f"   New Login: 9928326")
        print(f"   Fund: {target_account.get('fund_code')}")
        print(f"   Broker: DooTechnology")
        
        try:
            # Update the account with correct login and broker info
            update_data = {
                'mt5_login': 9928326,
                'mt5_server': 'DooTechnology-Live',
                'broker_code': 'dootechnology',
                'broker_name': 'DooTechnology',
                'updated_at': datetime.now(timezone.utc)
            }
            
            result = self.db.mt5_accounts.update_one(
                {'account_id': account_id},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                print(f"   ✅ Successfully updated account")
                self.actions_taken.append(f"Updated Salvador's account {account_id} to login 9928326")
                return True
            else:
                print(f"   ❌ Account not found for update")
                return False
                
        except Exception as e:
            print(f"   ❌ Error updating account: {str(e)}")
            return False
    
    def verify_fix(self):
        """Verify that the fix was successful"""
        print("\n" + "="*60)
        print("VERIFYING FIX")
        print("="*60)
        
        accounts = self.get_current_mt5_accounts()
        
        # Check for accounts with login 9928326
        login_9928326_accounts = [acc for acc in accounts if acc.get('mt5_login') == 9928326]
        
        print(f"📊 Accounts with login 9928326: {len(login_9928326_accounts)}")
        
        if len(login_9928326_accounts) == 0:
            print("❌ No accounts with login 9928326 found!")
            return False
        elif len(login_9928326_accounts) > 1:
            print("❌ Still multiple accounts with login 9928326!")
            for acc in login_9928326_accounts:
                print(f"   - {acc.get('account_id')}: {acc.get('client_id')} ({acc.get('fund_code')})")
            return False
        else:
            account = login_9928326_accounts[0]
            print(f"✅ EXACTLY ONE ACCOUNT WITH LOGIN 9928326:")
            print(f"   Account ID: {account.get('account_id')}")
            print(f"   Client: {account.get('client_id')}")
            print(f"   Fund: {account.get('fund_code')}")
            print(f"   Broker: {account.get('broker_code', 'unknown')}")
            print(f"   Server: {account.get('mt5_server')}")
            print(f"   Allocated: ${account.get('total_allocated', 0):,.2f}")
            
            # Verify it's Salvador Palma's BALANCE account
            if (account.get('client_id') == 'client_0fd630c3' and 
                account.get('fund_code') == 'BALANCE' and
                account.get('broker_code') == 'dootechnology'):
                print(f"\n🎉 SUCCESS: Login 9928326 correctly belongs to Salvador Palma's BALANCE DooTechnology account!")
                return True
            else:
                print(f"\n❌ INCORRECT: Login 9928326 does not match expected criteria")
                return False
    
    def generate_final_report(self):
        """Generate final report"""
        print("\n" + "="*60)
        print("MT5 DIRECT FIX FINAL REPORT")
        print("="*60)
        
        print(f"\n📋 ACTIONS TAKEN:")
        for i, action in enumerate(self.actions_taken, 1):
            print(f"   {i}. {action}")
        
        if not self.actions_taken:
            print("   No actions were taken")
        
        # Final state check
        accounts = self.get_current_mt5_accounts()
        login_9928326_accounts = [acc for acc in accounts if acc.get('mt5_login') == 9928326]
        
        print(f"\n📊 FINAL STATE:")
        print(f"   Total MT5 accounts: {len(accounts)}")
        print(f"   Accounts with login 9928326: {len(login_9928326_accounts)}")
        
        if len(login_9928326_accounts) == 1:
            account = login_9928326_accounts[0]
            if (account.get('client_id') == 'client_0fd630c3' and 
                account.get('fund_code') == 'BALANCE' and
                account.get('broker_code') == 'dootechnology'):
                print(f"   ✅ GOAL ACHIEVED: Salvador Palma has exactly ONE BALANCE DooTechnology account with login 9928326")
                return True
            else:
                print(f"   ❌ GOAL NOT ACHIEVED: Login 9928326 belongs to wrong client/fund/broker")
                return False
        else:
            print(f"   ❌ GOAL NOT ACHIEVED: Should have exactly 1 account with login 9928326")
            return False
    
    def run_fix(self):
        """Run the complete fix process"""
        print("🔧 STARTING MT5 DIRECT MONGODB FIX")
        print("=" * 40)
        
        try:
            # Step 1: Analyze current state
            login_9928326_accounts, salvador_accounts, client_001_accounts = self.analyze_current_state()
            
            # Step 2: Delete duplicate accounts
            if not self.delete_duplicate_accounts(login_9928326_accounts):
                print("❌ Failed to delete duplicate accounts")
                return False
            
            # Step 3: Create/update correct Salvador account
            if not self.create_correct_salvador_account(salvador_accounts):
                print("❌ Failed to create correct Salvador account")
                return False
            
            # Step 4: Verify fix
            if not self.verify_fix():
                print("❌ Fix verification failed")
                return False
            
            # Step 5: Generate report
            success = self.generate_final_report()
            
            return success
            
        except Exception as e:
            print(f"❌ Fix failed with exception: {str(e)}")
            return False
        finally:
            # Close MongoDB connection
            self.client.close()

def main():
    """Main function"""
    print("MT5 Account Direct MongoDB Fix")
    print("=" * 35)
    
    fixer = MT5DirectFixer()
    success = fixer.run_fix()
    
    if success:
        print("\n🎉 MT5 DIRECT FIX COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n💥 MT5 DIRECT FIX FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()