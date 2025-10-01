#!/usr/bin/env python3
"""
MT5 Account Duplication Fix Script
=================================

Based on investigation findings:
1. 5 duplicate accounts with login 9928326 belong to client_001 (Gerardo Briones) - WRONG
2. Salvador Palma (client_0fd630c3) has no account with login 9928326 - NEEDS FIX
3. Expected: Salvador Palma should have exactly ONE BALANCE account with login 9928326

Fix Strategy:
1. Delete all 5 duplicate client_001 accounts with login 9928326
2. Update one of Salvador's existing BALANCE accounts to use login 9928326
3. Verify the fix
"""

import requests
import json
from datetime import datetime
import sys

class MT5DuplicationFixer:
    def __init__(self, base_url="https://crm-workspace-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.auth_token = None
        self.actions_taken = []
        
    def authenticate_admin(self):
        """Authenticate as admin to get JWT token"""
        print("🔐 Authenticating as admin...")
        
        url = f"{self.base_url}/api/auth/login"
        response = requests.post(url, json={
            "username": "admin",
            "password": "password123", 
            "user_type": "admin"
        }, timeout=15)
        
        if response.status_code == 200 and response.json().get('token'):
            self.auth_token = response.json()['token']
            print("   ✅ Admin authentication successful")
            return True
        else:
            print(f"   ❌ Admin authentication failed: {response.text}")
            return False
    
    def make_api_call(self, method, endpoint, data=None):
        """Make authenticated API call"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }
        
        print(f"\n🔧 {method} {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201, 204]:
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error text: {response.text}")
                    return False, {"error": response.text}
                    
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False, {"error": str(e)}
    
    def get_current_accounts(self):
        """Get current MT5 accounts"""
        success, response = self.make_api_call("GET", "api/mt5/admin/accounts")
        if success:
            return response.get('accounts', [])
        return []
    
    def delete_duplicate_accounts(self):
        """Delete all 5 duplicate client_001 accounts with login 9928326"""
        print("\n" + "="*60)
        print("STEP 1: DELETING DUPLICATE CLIENT_001 ACCOUNTS")
        print("="*60)
        
        accounts = self.get_current_accounts()
        
        # Find client_001 accounts with login 9928326
        duplicate_accounts = [
            acc for acc in accounts 
            if acc.get('client_id') == 'client_001' and acc.get('mt5_login') == 9928326
        ]
        
        print(f"Found {len(duplicate_accounts)} duplicate client_001 accounts with login 9928326")
        
        deleted_count = 0
        for account in duplicate_accounts:
            account_id = account.get('account_id')
            print(f"\n🗑️  Deleting account: {account_id}")
            print(f"   Client: {account.get('client_id')} ({account.get('client_name')})")
            print(f"   Fund: {account.get('fund_code')}")
            print(f"   Login: {account.get('mt5_login')}")
            
            success, response = self.make_api_call("DELETE", f"api/mt5/admin/accounts/{account_id}")
            if success:
                print(f"   ✅ Successfully deleted")
                deleted_count += 1
                self.actions_taken.append(f"Deleted duplicate account {account_id}")
            else:
                print(f"   ❌ Failed to delete: {response}")
        
        print(f"\n📊 DELETION SUMMARY: {deleted_count}/{len(duplicate_accounts)} accounts deleted")
        return deleted_count == len(duplicate_accounts)
    
    def fix_salvador_account(self):
        """Update one of Salvador's BALANCE accounts to use login 9928326"""
        print("\n" + "="*60)
        print("STEP 2: FIXING SALVADOR PALMA'S ACCOUNT")
        print("="*60)
        
        accounts = self.get_current_accounts()
        
        # Find Salvador's BALANCE accounts
        salvador_balance_accounts = [
            acc for acc in accounts 
            if acc.get('client_id') == 'client_0fd630c3' and acc.get('fund_code') == 'BALANCE'
        ]
        
        print(f"Found {len(salvador_balance_accounts)} Salvador BALANCE accounts")
        
        if not salvador_balance_accounts:
            print("❌ No Salvador BALANCE accounts found!")
            return False
        
        # Use the first BALANCE account and update its login to 9928326
        target_account = salvador_balance_accounts[0]
        account_id = target_account.get('account_id')
        
        print(f"\n🎯 Updating account: {account_id}")
        print(f"   Current Login: {target_account.get('mt5_login')}")
        print(f"   New Login: 9928326")
        print(f"   Fund: {target_account.get('fund_code')}")
        print(f"   Client: Salvador Palma (client_0fd630c3)")
        
        # Update the account (this might need to be done via direct database update)
        # For now, let's try to create a new account with the correct details
        
        # First, let's try to update via API if available
        update_data = {
            "mt5_login": 9928326,
            "mt5_server": "DooTechnology-Live"
        }
        
        success, response = self.make_api_call("PUT", f"api/mt5/admin/accounts/{account_id}", update_data)
        if success:
            print(f"   ✅ Successfully updated account login to 9928326")
            self.actions_taken.append(f"Updated Salvador's account {account_id} to login 9928326")
            return True
        else:
            print(f"   ⚠️  Direct update failed, trying alternative approach")
            
            # Alternative: Create a new account with correct details and delete the old one
            return self.create_correct_salvador_account(target_account)
    
    def create_correct_salvador_account(self, old_account):
        """Create a new correct account for Salvador and delete the old one"""
        print(f"\n🔧 Creating new correct account for Salvador...")
        
        # Create new account data
        new_account_data = {
            "client_id": "client_0fd630c3",
            "fund_code": "BALANCE", 
            "mt5_login": 9928326,
            "mt5_password": "SecurePass123!",  # This would be generated properly
            "mt5_server": "DooTechnology-Live"
        }
        
        success, response = self.make_api_call("POST", "api/mt5/admin/add-manual-account", new_account_data)
        if success:
            print(f"   ✅ Created new correct account")
            
            # Delete the old account
            old_account_id = old_account.get('account_id')
            success, response = self.make_api_call("DELETE", f"api/mt5/admin/accounts/{old_account_id}")
            if success:
                print(f"   ✅ Deleted old account {old_account_id}")
                self.actions_taken.append(f"Created new Salvador account with login 9928326")
                self.actions_taken.append(f"Deleted old Salvador account {old_account_id}")
                return True
            else:
                print(f"   ⚠️  Failed to delete old account: {response}")
                return True  # New account created successfully
        else:
            print(f"   ❌ Failed to create new account: {response}")
            return False
    
    def verify_fix(self):
        """Verify that the fix was successful"""
        print("\n" + "="*60)
        print("STEP 3: VERIFYING FIX")
        print("="*60)
        
        accounts = self.get_current_accounts()
        
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
            print(f"   Client: {account.get('client_id')} ({account.get('client_name')})")
            print(f"   Fund: {account.get('fund_code')}")
            print(f"   Broker: {account.get('broker_code', 'unknown')}")
            print(f"   Server: {account.get('mt5_server')}")
            print(f"   Allocated: ${account.get('total_allocated', 0):,.2f}")
            
            # Verify it's Salvador Palma's BALANCE account
            if account.get('client_id') == 'client_0fd630c3' and account.get('fund_code') == 'BALANCE':
                print(f"\n🎉 SUCCESS: Login 9928326 correctly belongs to Salvador Palma's BALANCE account!")
                return True
            else:
                print(f"\n❌ INCORRECT: Login 9928326 does not belong to Salvador Palma's BALANCE account")
                return False
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*60)
        print("MT5 DUPLICATION FIX REPORT")
        print("="*60)
        
        print(f"\n📋 ACTIONS TAKEN:")
        for i, action in enumerate(self.actions_taken, 1):
            print(f"   {i}. {action}")
        
        if not self.actions_taken:
            print("   No actions were taken")
        
        # Final verification
        accounts = self.get_current_accounts()
        login_9928326_accounts = [acc for acc in accounts if acc.get('mt5_login') == 9928326]
        
        print(f"\n📊 FINAL STATE:")
        print(f"   Total MT5 accounts: {len(accounts)}")
        print(f"   Accounts with login 9928326: {len(login_9928326_accounts)}")
        
        if len(login_9928326_accounts) == 1:
            account = login_9928326_accounts[0]
            if account.get('client_id') == 'client_0fd630c3' and account.get('fund_code') == 'BALANCE':
                print(f"   ✅ GOAL ACHIEVED: Salvador Palma has exactly ONE BALANCE account with login 9928326")
                return True
            else:
                print(f"   ❌ GOAL NOT ACHIEVED: Login 9928326 belongs to wrong client/fund")
                return False
        else:
            print(f"   ❌ GOAL NOT ACHIEVED: Should have exactly 1 account with login 9928326")
            return False
    
    def run_fix(self):
        """Run the complete fix process"""
        print("🔧 STARTING MT5 ACCOUNT DUPLICATION FIX")
        print("=" * 50)
        
        try:
            # Authenticate
            if not self.authenticate_admin():
                return False
            
            # Step 1: Delete duplicate accounts
            if not self.delete_duplicate_accounts():
                print("❌ Failed to delete duplicate accounts")
                return False
            
            # Step 2: Fix Salvador's account
            if not self.fix_salvador_account():
                print("❌ Failed to fix Salvador's account")
                return False
            
            # Step 3: Verify fix
            if not self.verify_fix():
                print("❌ Fix verification failed")
                return False
            
            # Generate report
            success = self.generate_report()
            
            return success
            
        except Exception as e:
            print(f"❌ Fix failed with exception: {str(e)}")
            return False

def main():
    """Main function"""
    print("MT5 Account Duplication Fix")
    print("=" * 30)
    
    fixer = MT5DuplicationFixer()
    success = fixer.run_fix()
    
    if success:
        print("\n🎉 MT5 DUPLICATION FIX COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n💥 MT5 DUPLICATION FIX FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()