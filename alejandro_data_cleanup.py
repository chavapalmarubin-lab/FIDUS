#!/usr/bin/env python3
"""
Alejandro Data Cleanup Script
Clean up Alejandro's data to match exact production specifications:
- Keep only 2 investments: BALANCE $100,000 + CORE $18,151.41
- Update MT5 account balances to total $118,151.41
- Remove extra investments
"""

import requests
import json
import sys
from datetime import datetime

# Use the correct backend URL
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class AlejandroDataCleanup:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin"""
        try:
            login_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    print(f"✅ Authenticated as {data.get('name', 'admin')}")
                    return True
            
            print("❌ Authentication failed")
            return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_current_investments(self):
        """Get current investments for Alejandro"""
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/client/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get("investments", [])
                
                print(f"\n📊 Current Investments ({len(investments)} total):")
                for inv in investments:
                    print(f"  - {inv['fund_code']}: ${inv['principal_amount']:,.2f} (ID: {inv['investment_id'][:8]}...)")
                
                return investments
            else:
                print(f"❌ Failed to get investments: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting investments: {str(e)}")
            return []
    
    def get_current_mt5_accounts(self):
        """Get current MT5 accounts for Alejandro"""
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                
                print(f"\n🏦 Current MT5 Accounts ({len(accounts)} total):")
                for acc in accounts:
                    print(f"  - {acc['mt5_account_number']}: ${acc['balance']:,.2f} ({acc['fund_code']})")
                
                return accounts
            else:
                print(f"❌ Failed to get MT5 accounts: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting MT5 accounts: {str(e)}")
            return []
    
    def identify_target_investments(self, investments):
        """Identify which investments to keep (BALANCE $100k + CORE $18,151.41)"""
        balance_investments = [inv for inv in investments if inv['fund_code'] == 'BALANCE']
        core_investments = [inv for inv in investments if inv['fund_code'] == 'CORE']
        
        # Find the BALANCE investment with $100,000
        target_balance = None
        for inv in balance_investments:
            if abs(inv['principal_amount'] - 100000.0) < 0.01:
                target_balance = inv
                break
        
        # Find the CORE investment with $18,151.41
        target_core = None
        for inv in core_investments:
            if abs(inv['principal_amount'] - 18151.41) < 0.01:
                target_core = inv
                break
        
        # Identify investments to remove
        keep_ids = []
        if target_balance:
            keep_ids.append(target_balance['investment_id'])
        if target_core:
            keep_ids.append(target_core['investment_id'])
        
        remove_investments = [inv for inv in investments if inv['investment_id'] not in keep_ids]
        
        print(f"\n🎯 Target Investments:")
        if target_balance:
            print(f"  ✅ BALANCE: ${target_balance['principal_amount']:,.2f} (Keep: {target_balance['investment_id'][:8]}...)")
        else:
            print(f"  ❌ BALANCE: $100,000.00 not found")
        
        if target_core:
            print(f"  ✅ CORE: ${target_core['principal_amount']:,.2f} (Keep: {target_core['investment_id'][:8]}...)")
        else:
            print(f"  ❌ CORE: $18,151.41 not found")
        
        print(f"\n🗑️ Investments to Remove ({len(remove_investments)}):")
        for inv in remove_investments:
            print(f"  - {inv['fund_code']}: ${inv['principal_amount']:,.2f} (ID: {inv['investment_id'][:8]}...)")
        
        return target_balance, target_core, remove_investments
    
    def remove_investment(self, investment_id):
        """Remove an investment (this would need to be implemented in the backend)"""
        # Note: This endpoint may not exist, so we'll just log what should be done
        print(f"  🗑️ Would remove investment: {investment_id[:8]}...")
        
        # Try to call a delete endpoint if it exists
        try:
            response = self.session.delete(f"{BACKEND_URL}/investments/{investment_id}")
            if response.status_code == 200:
                print(f"    ✅ Successfully removed investment {investment_id[:8]}...")
                return True
            else:
                print(f"    ⚠️ Delete endpoint returned HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"    ⚠️ Delete endpoint not available or failed: {str(e)}")
            return False
    
    def update_mt5_balances(self, accounts):
        """Update MT5 account balances to total $118,151.41"""
        if len(accounts) != 4:
            print(f"❌ Expected 4 MT5 accounts, found {len(accounts)}")
            return False
        
        # Distribute the total amount across 4 accounts
        # Based on the expected values, let's distribute proportionally
        total_target = 118151.41
        
        # Distribute based on fund allocation:
        # BALANCE fund: $100,000 across 3 accounts
        # CORE fund: $18,151.41 across 1 account
        
        balance_accounts = [acc for acc in accounts if acc['fund_code'] == 'BALANCE']
        core_accounts = [acc for acc in accounts if acc['fund_code'] == 'CORE']
        
        print(f"\n💰 Updating MT5 Account Balances:")
        print(f"  Target Total: ${total_target:,.2f}")
        print(f"  BALANCE accounts: {len(balance_accounts)}")
        print(f"  CORE accounts: {len(core_accounts)}")
        
        # For now, just log what should be done since we may not have update endpoints
        if len(balance_accounts) == 3:
            balance_per_account = 100000.0 / 3
            for i, acc in enumerate(balance_accounts):
                print(f"    📝 Would set account {acc['mt5_account_number']}: ${balance_per_account:,.2f}")
        
        if len(core_accounts) == 1:
            core_amount = 18151.41
            for acc in core_accounts:
                print(f"    📝 Would set account {acc['mt5_account_number']}: ${core_amount:,.2f}")
        
        print("  ⚠️ MT5 balance update endpoints may need to be implemented")
        return True
    
    def run_cleanup(self):
        """Run the complete data cleanup process"""
        print("🧹 ALEJANDRO DATA CLEANUP")
        print("=" * 50)
        print("Target: 2 investments (BALANCE $100k + CORE $18,151.41)")
        print("Target: 4 MT5 accounts totaling $118,151.41")
        print("=" * 50)
        
        # Authenticate
        if not self.authenticate_admin():
            return False
        
        # Get current data
        investments = self.get_current_investments()
        mt5_accounts = self.get_current_mt5_accounts()
        
        if not investments:
            print("❌ No investments found")
            return False
        
        # Identify target investments
        target_balance, target_core, remove_investments = self.identify_target_investments(investments)
        
        if not target_balance or not target_core:
            print("❌ Required investments not found")
            return False
        
        # Remove extra investments
        if remove_investments:
            print(f"\n🗑️ Removing {len(remove_investments)} extra investments:")
            for inv in remove_investments:
                self.remove_investment(inv['investment_id'])
        else:
            print("\n✅ No extra investments to remove")
        
        # Update MT5 balances
        if mt5_accounts:
            self.update_mt5_balances(mt5_accounts)
        else:
            print("❌ No MT5 accounts found")
        
        print("\n" + "=" * 50)
        print("🎯 CLEANUP SUMMARY")
        print("=" * 50)
        print("✅ Identified target investments")
        print(f"📝 Would remove {len(remove_investments)} extra investments")
        print("📝 Would update MT5 account balances")
        print("\n⚠️ Note: Some operations may require backend endpoint implementation")
        
        return True

if __name__ == "__main__":
    cleanup = AlejandroDataCleanup()
    success = cleanup.run_cleanup()
    sys.exit(0 if success else 1)