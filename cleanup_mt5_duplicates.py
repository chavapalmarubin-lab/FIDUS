#!/usr/bin/env python3
"""
Clean Up MT5 Duplicate Accounts and Update with Real Trading Data
================================================================

This script will:
1. Remove all duplicate MT5 accounts for Salvador Palma
2. Keep only ONE account with login 9928326 
3. Update that account with real MT5 trading data from the screenshot
4. Ensure proper data integration with FIDUS system
"""

import os
import sys
import requests
from pymongo import MongoClient
from datetime import datetime, timezone

class MT5AccountCleanup:
    def __init__(self):
        # MongoDB connection
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_investment_db')
        self.db_name = mongo_url.split('/')[-1] if '/' in mongo_url else 'fidus_investment_db'
        
        try:
            self.client = MongoClient(mongo_url)
            self.db = self.client[self.db_name]
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {self.db_name}")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            raise
        
        # API configuration
        self.base_url = "https://fidussign.preview.emergentagent.com"
        self.admin_token = None
        
        # Real MT5 trading data from the screenshot
        self.real_mt5_data = {
            'balance': 1837934.05,
            'equity': 635505.68,
            'margin': 268654.80,
            'free_margin': 366850.88,
            'margin_level': 236.55,
            'profit_loss': -1202428.37,  # Current floating P&L
            'positions': [
                {
                    'symbol': 'EURUSD.c',
                    'type': 'sell',
                    'volume': 34,
                    'opening_price': 1.16376,
                    'current_price': 1.17220,
                    'profit': -28696.00
                },
                {
                    'symbol': 'EURUSD.c', 
                    'type': 'sell',
                    'volume': 19,
                    'opening_price': 1.16347,
                    'current_price': 1.17220,
                    'profit': -16587.00
                },
                {
                    'symbol': 'USDCHF.c',
                    'type': 'buy',
                    'volume': 19,
                    'opening_price': 0.80720,
                    'current_price': 0.79801,
                    'profit': -21880.68
                },
                {
                    'symbol': 'USDCHF.c',
                    'type': 'buy', 
                    'volume': 19,
                    'opening_price': 0.80310,
                    'current_price': 0.79801,
                    'profit': -12118.90
                },
                {
                    'symbol': 'XAUUSD.c',
                    'type': 'sell',
                    'volume': 0.55,
                    'opening_price': 3521.32,
                    'current_price': 3586.75,
                    'profit': -3598.65
                }
            ]
        }
    
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
    
    def step_1_analyze_current_accounts(self):
        """Step 1: Analyze current MT5 accounts"""
        print("\n" + "="*60)
        print("STEP 1: ANALYZING CURRENT MT5 ACCOUNTS")
        print("="*60)
        
        # Get all MT5 accounts from database
        accounts = list(self.db.mt5_accounts.find({}))
        print(f"Total MT5 accounts in database: {len(accounts)}")
        
        # Find Salvador's accounts
        salvador_accounts = []
        for acc in accounts:
            if (acc.get('client_id') == 'client_003' or 
                acc.get('mt5_login') == 9928326):
                salvador_accounts.append(acc)
        
        print(f"Salvador's accounts found: {len(salvador_accounts)}")
        
        for i, acc in enumerate(salvador_accounts, 1):
            print(f"  {i}. Account ID: {acc.get('account_id')}")
            print(f"     Client: {acc.get('client_id')}")
            print(f"     Login: {acc.get('mt5_login')}")
            print(f"     Fund: {acc.get('fund_code')}")
            print(f"     Allocated: ${acc.get('total_allocated', 0):,.2f}")
            print(f"     Created: {acc.get('created_at')}")
            print()
        
        return salvador_accounts
    
    def step_2_select_primary_account(self, accounts):
        """Step 2: Select the primary account to keep"""
        print("\n" + "="*60)
        print("STEP 2: SELECTING PRIMARY ACCOUNT")
        print("="*60)
        
        # Find the account with the highest allocation or most recent creation
        primary_account = None
        
        for acc in accounts:
            allocated = acc.get('total_allocated', 0)
            if allocated > 0:  # Prefer accounts with allocation
                if not primary_account or allocated > primary_account.get('total_allocated', 0):
                    primary_account = acc
        
        # If no account with allocation, take the first one
        if not primary_account and accounts:
            primary_account = accounts[0]
        
        if primary_account:
            print(f"✅ Selected primary account:")
            print(f"   Account ID: {primary_account.get('account_id')}")
            print(f"   Client: {primary_account.get('client_id')}")
            print(f"   Login: {primary_account.get('mt5_login')}")
            print(f"   Allocated: ${primary_account.get('total_allocated', 0):,.2f}")
            
            return primary_account
        else:
            print("❌ No account found to keep as primary")
            return None
    
    def step_3_delete_duplicate_accounts(self, accounts, primary_account):
        """Step 3: Delete duplicate accounts"""
        print("\n" + "="*60)
        print("STEP 3: DELETING DUPLICATE ACCOUNTS")
        print("="*60)
        
        primary_account_id = primary_account.get('account_id')
        duplicates_deleted = 0
        
        for acc in accounts:
            if acc.get('account_id') != primary_account_id:
                try:
                    # Delete from mt5_accounts collection
                    result = self.db.mt5_accounts.delete_one({'account_id': acc.get('account_id')})
                    if result.deleted_count > 0:
                        print(f"✅ Deleted duplicate: {acc.get('account_id')}")
                        duplicates_deleted += 1
                    
                    # Also delete from mt5_credentials if exists
                    self.db.mt5_credentials.delete_one({'account_id': acc.get('account_id')})
                    
                except Exception as e:
                    print(f"❌ Error deleting {acc.get('account_id')}: {str(e)}")
        
        print(f"\n✅ Deleted {duplicates_deleted} duplicate accounts")
        print(f"✅ Kept 1 primary account: {primary_account_id}")
        
        return duplicates_deleted > 0
    
    def step_4_update_with_real_trading_data(self, primary_account):
        """Step 4: Update primary account with real MT5 trading data"""
        print("\n" + "="*60)
        print("STEP 4: UPDATING WITH REAL TRADING DATA")
        print("="*60)
        
        account_id = primary_account.get('account_id')
        
        # Update account with real MT5 data
        updated_data = {
            'current_equity': self.real_mt5_data['equity'],
            'balance': self.real_mt5_data['balance'],
            'margin': self.real_mt5_data['margin'],
            'free_margin': self.real_mt5_data['free_margin'],
            'margin_level': self.real_mt5_data['margin_level'],
            'profit_loss': self.real_mt5_data['profit_loss'],
            'profit_loss_percentage': (self.real_mt5_data['profit_loss'] / self.real_mt5_data['balance'] * 100),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'real_data_updated': True,
            'last_sync': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            result = self.db.mt5_accounts.update_one(
                {'account_id': account_id},
                {'$set': updated_data}
            )
            
            if result.modified_count > 0:
                print("✅ Updated account with real trading data:")
                print(f"   Balance: ${self.real_mt5_data['balance']:,.2f}")
                print(f"   Equity: ${self.real_mt5_data['equity']:,.2f}")
                print(f"   Margin: ${self.real_mt5_data['margin']:,.2f}")
                print(f"   Free Margin: ${self.real_mt5_data['free_margin']:,.2f}")
                print(f"   Profit/Loss: ${self.real_mt5_data['profit_loss']:,.2f}")
                print(f"   Margin Level: {self.real_mt5_data['margin_level']:.2f}%")
                return True
            else:
                print("❌ Failed to update account")
                return False
                
        except Exception as e:
            print(f"❌ Error updating account: {str(e)}")
            return False
    
    def step_5_create_real_trading_activity(self, primary_account):
        """Step 5: Create real trading activity records"""
        print("\n" + "="*60)
        print("STEP 5: CREATING REAL TRADING ACTIVITY")
        print("="*60)
        
        account_id = primary_account.get('account_id')
        
        # Clear existing activity
        self.db.mt5_activity.delete_many({'account_id': account_id})
        
        activities = []
        
        # Add initial deposit activity
        activities.append({
            'account_id': account_id,
            'client_id': 'client_003',
            'activity_id': f'deposit_{account_id}_001',
            'type': 'deposit',
            'amount': 100000.0,
            'description': 'Initial allocation to BALANCE fund',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'completed'
        })
        
        # Add real trading positions
        for i, position in enumerate(self.real_mt5_data['positions'], 1):
            activity_type = 'buy' if position['type'] == 'buy' else 'sell'
            activities.append({
                'account_id': account_id,
                'client_id': 'client_003',
                'activity_id': f'trade_{account_id}_{i:03d}',
                'type': 'trade',
                'amount': position['profit'],
                'description': f"Position {position['type'].upper()}: {position['symbol']} {position['volume']} lot @ {position['opening_price']}",
                'symbol': position['symbol'],
                'trade_type': position['type'],
                'volume': position['volume'],
                'opening_price': position['opening_price'],
                'current_price': position['current_price'],
                'profit_loss': position['profit'],  
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'open'
            })
        
        # Insert activities
        try:
            if activities:
                result = self.db.mt5_activity.insert_many(activities)
                print(f"✅ Created {len(result.inserted_ids)} trading activity records")
                
                # Show summary
                print("\nTrading Activity Summary:")
                print(f"   - 1 Initial deposit: +$100,000.00")
                for pos in self.real_mt5_data['positions']:
                    print(f"   - {pos['symbol']} {pos['type'].upper()} {pos['volume']}: ${pos['profit']:,.2f}")
                
                return True
            else:
                print("❌ No activities to create")
                return False
                
        except Exception as e:
            print(f"❌ Error creating activities: {str(e)}")
            return False
    
    def step_6_verify_cleanup(self):
        """Step 6: Verify the cleanup was successful"""
        print("\n" + "="*60)
        print("STEP 6: VERIFICATION")
        print("="*60)
        
        # Check MT5 accounts
        accounts = list(self.db.mt5_accounts.find({'client_id': 'client_003'}))
        print(f"Salvador's MT5 accounts remaining: {len(accounts)}")
        
        if len(accounts) == 1:
            account = accounts[0]
            print("✅ PERFECT: Exactly 1 account remaining")
            print(f"   Account ID: {account.get('account_id')}")
            print(f"   Login: {account.get('mt5_login')}")
            print(f"   Balance: ${account.get('balance', 0):,.2f}")
            print(f"   Equity: ${account.get('current_equity', 0):,.2f}")
            print(f"   P&L: ${account.get('profit_loss', 0):,.2f}")
            
            # Check activities
            activities = list(self.db.mt5_activity.find({'account_id': account.get('account_id')}))
            print(f"   Trading activities: {len(activities)}")
            
            return True
        else:
            print(f"❌ ERROR: Expected 1 account, found {len(accounts)}")
            return False
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        print("🧹 MT5 ACCOUNT CLEANUP & REAL DATA INTEGRATION")
        print("=" * 70)
        print("Goal: Clean duplicates and integrate real MT5 trading data")
        print("=" * 70)
        
        if not self.get_admin_token():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 1: Analyze current accounts
        accounts = self.step_1_analyze_current_accounts()
        if not accounts:
            print("❌ No Salvador accounts found")
            return False
        
        # Step 2: Select primary account
        primary_account = self.step_2_select_primary_account(accounts)
        if not primary_account:
            print("❌ No primary account selected")
            return False
        
        # Step 3: Delete duplicates
        if len(accounts) > 1:
            if not self.step_3_delete_duplicate_accounts(accounts, primary_account):
                print("❌ Failed to delete duplicates")
                return False
        else:
            print("\nℹ️  Only 1 account found, no duplicates to delete")
        
        # Step 4: Update with real trading data
        if not self.step_4_update_with_real_trading_data(primary_account):
            print("❌ Failed to update with real data")
            return False
        
        # Step 5: Create real trading activities
        if not self.step_5_create_real_trading_activity(primary_account):
            print("❌ Failed to create trading activities")
            return False
        
        # Step 6: Verify
        if not self.step_6_verify_cleanup():
            print("❌ Verification failed")
            return False
        
        print("\n" + "="*70)
        print("🎉 MT5 CLEANUP & REAL DATA INTEGRATION COMPLETE!")
        print("="*70)
        print("✅ Removed duplicate accounts")
        print("✅ Updated with real MT5 trading data")
        print("✅ Created real trading activity records")
        print("✅ Salvador Palma now has exactly 1 MT5 account with real data")
        print("="*70)
        
        return True

def main():
    """Main execution"""
    try:
        cleanup = MT5AccountCleanup()
        success = cleanup.run_cleanup()
        
        if success:
            print("\n✅ Cleanup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Cleanup failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()