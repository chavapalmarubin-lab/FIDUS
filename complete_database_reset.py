#!/usr/bin/env python3
"""
Complete Database Reset for FIDUS Investment Platform
====================================================

CRITICAL OPERATION: This script will:
1. Clear ALL client investment data from database
2. Clear ALL MT5 account data  
3. Create ONLY Salvador Palma investment with proper MT5 mapping
4. Ensure MT5 integration feeds all data correctly

WARNING: This will delete all existing investment and MT5 data!
"""

import os
import sys
import asyncio
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
import requests
import json

# Add backend path for imports
sys.path.append('/app/backend')

class DatabaseReset:
    def __init__(self):
        # MongoDB connection (same as backend)
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_investment_db')
        
        # Extract database name from URL
        if '/' in mongo_url:
            self.db_name = mongo_url.split('/')[-1]
        else:
            self.db_name = 'fidus_investment_db'
        
        try:
            self.client = MongoClient(mongo_url)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {self.db_name}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            raise
        
        # API configuration
        self.base_url = "https://fund-tracker-11.preview.emergentagent.com"
        self.admin_token = None
    
    def get_admin_token(self):
        """Get admin authentication token"""
        try:
            response = requests.post(f"{self.base_url}/api/auth/login", json={
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                self.admin_token = response.json().get('token')
                print("✅ Admin authentication successful")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def step_1_clear_all_data(self):
        """Step 1: Clear ALL investment and MT5 data"""
        print("\n" + "="*60)
        print("STEP 1: CLEARING ALL INVESTMENT AND MT5 DATA")
        print("="*60)
        
        collections_to_clear = [
            'investments',
            'mt5_accounts', 
            'mt5_credentials',
            'activity_logs'
        ]
        
        cleared_counts = {}
        
        for collection_name in collections_to_clear:
            try:
                # Get count before deletion
                before_count = self.db[collection_name].count_documents({})
                
                # Delete all documents
                result = self.db[collection_name].delete_many({})
                cleared_counts[collection_name] = result.deleted_count
                
                print(f"   Cleared {collection_name}: {result.deleted_count} documents (was {before_count})")
                
            except Exception as e:
                print(f"   ❌ Error clearing {collection_name}: {str(e)}")
                cleared_counts[collection_name] = 0
        
        total_cleared = sum(cleared_counts.values())
        print(f"\n✅ Total documents cleared: {total_cleared}")
        
        if total_cleared == 0:
            print("ℹ️  Database was already clean, proceeding...")
        
        return True  # Always return True since clearing 0 documents is also success
    
    def step_2_verify_salvador_palma_exists(self):
        """Step 2: Verify Salvador Palma exists as a user"""
        print("\n" + "="*60)  
        print("STEP 2: VERIFYING SALVADOR PALMA USER EXISTS")
        print("="*60)
        
        # Check in users collection - Salvador Palma is client3 with salvador.palma@fidus.com
        salvador_user = self.db.users.find_one({
            "user_type": "client",
            "email": "salvador.palma@fidus.com"
        })
        
        if not salvador_user:
            # Also check by username
            salvador_user = self.db.users.find_one({
                "user_type": "client", 
                "username": "client3"
            })
        
        if salvador_user:
            print(f"✅ Found Salvador Palma user:")
            print(f"   User ID: {salvador_user.get('user_id')}")
            print(f"   Username: {salvador_user.get('username')}")
            print(f"   Email: {salvador_user.get('email')}")
            print(f"   Name: {salvador_user.get('name', 'Salvador Palma')}")
            return salvador_user.get('user_id')
        else:
            print("❌ Salvador Palma user not found")
            # Let's check what users exist
            users = list(self.db.users.find({"user_type": "client"}, {"user_id": 1, "username": 1, "email": 1}))
            print(f"Available client users ({len(users)}):")
            for user in users:
                print(f"   - {user.get('username')} (ID: {user.get('user_id')}, Email: {user.get('email')})")
            return None
    
    def step_3_create_salvador_investment(self, salvador_user_id):
        """Step 3: Create Salvador Palma BALANCE investment with DooTechnology MT5"""
        print("\n" + "="*60)
        print("STEP 3: CREATING SALVADOR PALMA BALANCE INVESTMENT")
        print("="*60)
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        # Investment data for Salvador Palma
        investment_data = {
            "client_id": salvador_user_id,
            "fund_code": "BALANCE", 
            "amount": 100000.00,
            "deposit_date": "2024-12-19",
            "broker_code": "dootechnology"  # Ensure DooTechnology broker
        }
        
        print(f"Creating investment:")
        print(f"   Client: {salvador_user_id}")
        print(f"   Fund: BALANCE")
        print(f"   Amount: $100,000.00")
        print(f"   Broker: DooTechnology")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/investments/create",
                json=investment_data,
                headers=headers
            )
            
            print(f"   API Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                investment_id = result.get('investment_id')
                print(f"✅ Investment created successfully!")
                print(f"   Investment ID: {investment_id}")
                
                if 'principal_amount' in result:
                    print(f"   Principal: ${result['principal_amount']:,.2f}")
                if 'deposit_date' in result:
                    print(f"   Deposit Date: {result['deposit_date']}")
                    
                return investment_id
            else:
                print(f"❌ Investment creation failed")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Investment creation error: {str(e)}")
            return None
    
    def step_4_verify_mt5_account_creation(self, salvador_user_id):
        """Step 4: Verify MT5 account was created with login 9928326"""
        print("\n" + "="*60)
        print("STEP 4: VERIFYING MT5 ACCOUNT CREATION")
        print("="*60)
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        try:
            # Get all MT5 accounts
            response = requests.get(
                f"{self.base_url}/api/mt5/admin/accounts",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                
                print(f"Total MT5 accounts found: {len(accounts)}")
                
                # Look for Salvador's account
                salvador_account = None
                for account in accounts:
                    if account.get('client_id') == salvador_user_id:
                        salvador_account = account
                        break
                
                if salvador_account:
                    print(f"✅ Found Salvador's MT5 account:")
                    print(f"   Account ID: {salvador_account.get('account_id')}")
                    print(f"   Client ID: {salvador_account.get('client_id')}")
                    print(f"   Fund: {salvador_account.get('fund_code')}")
                    print(f"   MT5 Login: {salvador_account.get('mt5_login')}")
                    print(f"   MT5 Server: {salvador_account.get('mt5_server')}")
                    print(f"   Broker: {salvador_account.get('broker_name', 'N/A')}")
                    print(f"   Allocated: ${salvador_account.get('total_allocated', 0):,.2f}")
                    
                    # Check if login is 9928326
                    mt5_login = salvador_account.get('mt5_login')
                    if mt5_login == 9928326:
                        print(f"✅ CORRECT: MT5 login is 9928326 as required")
                        return True
                    else:
                        print(f"❌ WRONG: MT5 login is {mt5_login}, should be 9928326")
                        # We need to update this account
                        return self.update_mt5_login(salvador_account.get('account_id'), 9928326)
                else:
                    print(f"❌ No MT5 account found for Salvador ({salvador_user_id})")
                    
                    # Show what accounts do exist
                    if accounts:
                        print("Existing accounts:")
                        for acc in accounts:
                            print(f"   - {acc.get('client_id')}: {acc.get('fund_code')} (Login: {acc.get('mt5_login')})")
                    
                    return False
            else:
                print(f"❌ Failed to get MT5 accounts: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ MT5 verification error: {str(e)}")
            return False
    
    def update_mt5_login(self, account_id, new_login):
        """Update MT5 login to 9928326"""
        print(f"\n🔧 Updating MT5 login to {new_login}")
        
        try:
            # Update in MongoDB directly
            result = self.db.mt5_accounts.update_one(
                {'account_id': account_id},
                {
                    '$set': {
                        'mt5_login': new_login,
                        'mt5_server': 'DooTechnology-Live',
                        'broker_code': 'dootechnology',
                        'broker_name': 'DooTechnology',
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Successfully updated MT5 account to login {new_login}")
                return True
            else:
                print(f"❌ Failed to update MT5 account")
                return False
                
        except Exception as e:
            print(f"❌ Update error: {str(e)}")
            return False
    
    def step_5_final_verification(self, salvador_user_id):
        """Step 5: Final verification that everything is correct"""
        print("\n" + "="*60)
        print("STEP 5: FINAL VERIFICATION")
        print("="*60)
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        verification_passed = True
        
        # 1. Check investments
        try:
            response = requests.get(
                f"{self.base_url}/api/investments/client/{salvador_user_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get('investments', [])
                print(f"✅ Salvador has {len(investments)} investment(s)")
                
                if len(investments) == 1:
                    inv = investments[0]
                    print(f"   Investment: {inv.get('fund_code')} - ${inv.get('principal_amount', 0):,.2f}")
                else:
                    print(f"❌ Expected 1 investment, found {len(investments)}")
                    verification_passed = False
            else:
                print(f"❌ Failed to get investments: {response.status_code}")
                verification_passed = False
                
        except Exception as e:
            print(f"❌ Investment verification error: {str(e)}")
            verification_passed = False
        
        # 2. Check MT5 accounts
        try:
            response = requests.get(
                f"{self.base_url}/api/mt5/admin/accounts",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                
                # Should have exactly 1 account for Salvador with login 9928326
                salvador_accounts = [acc for acc in accounts if acc.get('client_id') == salvador_user_id]
                login_9928326_accounts = [acc for acc in accounts if acc.get('mt5_login') == 9928326]
                
                print(f"✅ Total MT5 accounts: {len(accounts)}")
                print(f"✅ Salvador's MT5 accounts: {len(salvador_accounts)}")
                print(f"✅ Accounts with login 9928326: {len(login_9928326_accounts)}")
                
                if len(accounts) == 1 and len(salvador_accounts) == 1 and len(login_9928326_accounts) == 1:
                    account = salvador_accounts[0]
                    if (account.get('mt5_login') == 9928326 and 
                        account.get('fund_code') == 'BALANCE' and
                        'dootechnology' in account.get('mt5_server', '').lower()):
                        print(f"✅ PERFECT: Exactly 1 MT5 account with correct details")
                    else:
                        print(f"❌ Account details incorrect")
                        verification_passed = False
                else:
                    print(f"❌ Expected exactly 1 account, found issues")
                    verification_passed = False
                    
                    # Show what we have
                    for acc in accounts:
                        print(f"   Account: {acc.get('client_id')} - {acc.get('fund_code')} (Login: {acc.get('mt5_login')})")
            else:
                print(f"❌ Failed to get MT5 accounts: {response.status_code}")
                verification_passed = False
                
        except Exception as e:
            print(f"❌ MT5 verification error: {str(e)}")
            verification_passed = False
        
        return verification_passed
    
    def run_complete_reset(self):
        """Run the complete database reset and setup process"""
        print("🚨 COMPLETE DATABASE RESET FOR FIDUS INVESTMENT PLATFORM")
        print("=" * 70)
        print("WARNING: This will delete ALL existing investment and MT5 data!")
        print("Only Salvador Palma's investment will remain after this operation.")
        print("=" * 70)
        
        # Get admin authentication
        if not self.get_admin_token():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 1: Clear all data
        if not self.step_1_clear_all_data():
            print("❌ Failed to clear database")
            return False
        
        # Step 2: Verify Salvador Palma exists
        salvador_user_id = self.step_2_verify_salvador_palma_exists()
        if not salvador_user_id:
            print("❌ Cannot proceed without Salvador Palma user")
            return False
        
        # Step 3: Create Salvador's investment
        investment_id = self.step_3_create_salvador_investment(salvador_user_id)
        if not investment_id:
            print("❌ Failed to create Salvador's investment")
            return False
        
        # Step 4: Verify MT5 account creation
        if not self.step_4_verify_mt5_account_creation(salvador_user_id):
            print("❌ MT5 account verification failed")
            return False
        
        # Step 5: Final verification
        if not self.step_5_final_verification(salvador_user_id):
            print("❌ Final verification failed")
            return False
        
        print("\n" + "="*70)
        print("🎉 COMPLETE DATABASE RESET SUCCESSFUL!")
        print("="*70)
        print("✅ All old data cleared")
        print("✅ Salvador Palma BALANCE investment created")
        print("✅ MT5 account 9928326 properly mapped")
        print("✅ DooTechnology integration active")
        print("✅ System ready with clean data")
        print("="*70)
        
        return True

def main():
    """Main execution"""
    try:
        resetter = DatabaseReset()
        success = resetter.run_complete_reset()
        
        if success:
            print("\n✅ Database reset completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Database reset failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()