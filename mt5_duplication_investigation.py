#!/usr/bin/env python3
"""
MT5 Account Duplication Investigation and Cleanup Script
=======================================================

This script investigates and fixes the MT5 account duplication issue where:
- Multiple accounts exist with login 9928326
- Salvador Palma (client_003) should have exactly ONE DooTechnology BALANCE account
- No client_001 accounts should exist with DooTechnology login 9928326

Priority 1: Investigate Current MT5 Accounts
Priority 2: Clean Up Duplicate Accounts  
Priority 3: Verify Correct Data
"""

import requests
import json
from datetime import datetime
import sys

class MT5DuplicationInvestigator:
    def __init__(self, base_url="https://tradehub-mt5.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.issues_found = []
        self.duplicate_accounts = []
        self.correct_account = None
        self.auth_token = None
        
    def log_issue(self, severity, description, data=None):
        """Log an issue found during investigation"""
        issue = {
            "severity": severity,  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
            "description": description,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.issues_found.append(issue)
        print(f"🚨 {severity}: {description}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def authenticate_admin(self):
        """Authenticate as admin to get JWT token"""
        print("\n🔐 Authenticating as admin...")
        
        success, response = self.run_api_call("POST", "api/auth/login", 200, {
            "username": "admin",
            "password": "password123", 
            "user_type": "admin"
        })
        
        if success and response.get('token'):
            self.auth_token = response['token']
            print(f"   ✅ Admin authentication successful")
            return True
        else:
            print(f"   ❌ Admin authentication failed: {response}")
            return False
    
    def run_api_call(self, method, endpoint, expected_status=200, data=None):
        """Make API call and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add JWT token if available
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        self.tests_run += 1
        print(f"\n🔍 {method} {endpoint}")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == expected_status:
                self.tests_passed += 1
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"   ❌ Expected {expected_status}, got {response.status_code}")
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
    
    def priority_1_investigate_current_accounts(self):
        """Priority 1: Investigate Current MT5 Accounts"""
        print("\n" + "="*80)
        print("PRIORITY 1: INVESTIGATING CURRENT MT5 ACCOUNTS")
        print("="*80)
        
        # Get all MT5 accounts
        success, response = self.run_api_call("GET", "api/mt5/admin/accounts")
        if not success:
            self.log_issue("CRITICAL", "Cannot retrieve MT5 accounts", response)
            return False
        
        accounts = response.get('accounts', [])
        print(f"\n📊 TOTAL MT5 ACCOUNTS FOUND: {len(accounts)}")
        
        # Analyze accounts by login 9928326
        login_9928326_accounts = []
        salvador_accounts = []
        client_001_accounts = []
        
        for account in accounts:
            mt5_login = account.get('mt5_login')
            client_id = account.get('client_id')
            fund_code = account.get('fund_code')
            broker_code = account.get('broker_code', 'unknown')
            
            print(f"\n📋 Account: {account.get('account_id', 'N/A')}")
            print(f"   Client ID: {client_id}")
            print(f"   MT5 Login: {mt5_login}")
            print(f"   Fund Code: {fund_code}")
            print(f"   Broker Code: {broker_code}")
            print(f"   Allocated: ${account.get('total_allocated', 0):,.2f}")
            
            # Check for login 9928326
            if mt5_login == 9928326:
                login_9928326_accounts.append(account)
                print(f"   🎯 FOUND LOGIN 9928326!")
            
            # Check for Salvador Palma accounts
            if client_id == "client_0fd630c3":  # Salvador Palma
                salvador_accounts.append(account)
                print(f"   👤 SALVADOR PALMA ACCOUNT")
            
            # Check for client_001 accounts
            if client_id == "client_001":
                client_001_accounts.append(account)
                print(f"   👤 CLIENT_001 ACCOUNT")
        
        # Report findings
        print(f"\n🔍 INVESTIGATION RESULTS:")
        print(f"   Accounts with login 9928326: {len(login_9928326_accounts)}")
        print(f"   Salvador Palma accounts: {len(salvador_accounts)}")
        print(f"   Client_001 accounts: {len(client_001_accounts)}")
        
        # Check for duplicates with login 9928326
        if len(login_9928326_accounts) > 1:
            self.log_issue("CRITICAL", 
                          f"DUPLICATE ACCOUNTS FOUND: {len(login_9928326_accounts)} accounts with login 9928326",
                          login_9928326_accounts)
            self.duplicate_accounts = login_9928326_accounts
        elif len(login_9928326_accounts) == 1:
            print(f"   ✅ Only one account with login 9928326 found")
            self.correct_account = login_9928326_accounts[0]
        else:
            self.log_issue("HIGH", "No accounts found with login 9928326")
        
        # Check if client_001 has login 9928326
        client_001_with_9928326 = [acc for acc in client_001_accounts if acc.get('mt5_login') == 9928326]
        if client_001_with_9928326:
            self.log_issue("CRITICAL", 
                          f"CLIENT_001 HAS LOGIN 9928326: Should belong to Salvador Palma only",
                          client_001_with_9928326)
        
        # Check Salvador's accounts
        salvador_with_9928326 = [acc for acc in salvador_accounts if acc.get('mt5_login') == 9928326]
        if len(salvador_with_9928326) == 0:
            self.log_issue("HIGH", "Salvador Palma has no account with login 9928326")
        elif len(salvador_with_9928326) > 1:
            self.log_issue("CRITICAL", 
                          f"Salvador Palma has {len(salvador_with_9928326)} accounts with login 9928326",
                          salvador_with_9928326)
        else:
            salvador_account = salvador_with_9928326[0]
            expected_fund = "BALANCE"
            expected_broker = "dootechnology"
            
            if salvador_account.get('fund_code') != expected_fund:
                self.log_issue("HIGH", 
                              f"Salvador's account fund is {salvador_account.get('fund_code')}, expected {expected_fund}",
                              salvador_account)
            
            if salvador_account.get('broker_code') != expected_broker:
                self.log_issue("HIGH", 
                              f"Salvador's account broker is {salvador_account.get('broker_code')}, expected {expected_broker}",
                              salvador_account)
        
        return True
    
    def priority_2_clean_duplicate_accounts(self):
        """Priority 2: Clean Up Duplicate Accounts"""
        print("\n" + "="*80)
        print("PRIORITY 2: CLEANING UP DUPLICATE ACCOUNTS")
        print("="*80)
        
        if not self.duplicate_accounts:
            print("✅ No duplicate accounts found to clean up")
            return True
        
        print(f"🧹 Found {len(self.duplicate_accounts)} duplicate accounts with login 9928326")
        
        # Identify the correct account (Salvador Palma, BALANCE fund, DooTechnology)
        correct_account = None
        accounts_to_delete = []
        
        for account in self.duplicate_accounts:
            client_id = account.get('client_id')
            fund_code = account.get('fund_code')
            broker_code = account.get('broker_code', 'unknown')
            
            print(f"\n📋 Analyzing account: {account.get('account_id')}")
            print(f"   Client: {client_id}")
            print(f"   Fund: {fund_code}")
            print(f"   Broker: {broker_code}")
            
            # Check if this is the correct Salvador Palma BALANCE DooTechnology account
            if (client_id == "client_0fd630c3" and 
                fund_code == "BALANCE" and 
                broker_code == "dootechnology"):
                correct_account = account
                print(f"   ✅ CORRECT ACCOUNT IDENTIFIED")
            else:
                accounts_to_delete.append(account)
                print(f"   ❌ DUPLICATE TO DELETE")
        
        if not correct_account:
            self.log_issue("CRITICAL", 
                          "Cannot identify correct Salvador Palma BALANCE DooTechnology account",
                          self.duplicate_accounts)
            return False
        
        print(f"\n🎯 CORRECT ACCOUNT: {correct_account.get('account_id')}")
        print(f"   Client: {correct_account.get('client_id')} (Salvador Palma)")
        print(f"   Fund: {correct_account.get('fund_code')} (BALANCE)")
        print(f"   Broker: {correct_account.get('broker_code')} (DooTechnology)")
        print(f"   Login: {correct_account.get('mt5_login')} (9928326)")
        
        # Delete duplicate accounts
        for account in accounts_to_delete:
            account_id = account.get('account_id')
            print(f"\n🗑️  Deleting duplicate account: {account_id}")
            
            success, response = self.run_api_call("DELETE", f"api/mt5/admin/accounts/{account_id}")
            if success:
                print(f"   ✅ Successfully deleted duplicate account")
            else:
                self.log_issue("HIGH", f"Failed to delete duplicate account {account_id}", response)
        
        self.correct_account = correct_account
        return True
    
    def priority_3_verify_correct_data(self):
        """Priority 3: Verify Correct Data"""
        print("\n" + "="*80)
        print("PRIORITY 3: VERIFYING CORRECT DATA")
        print("="*80)
        
        # Re-fetch all accounts to verify cleanup
        success, response = self.run_api_call("GET", "api/mt5/admin/accounts")
        if not success:
            self.log_issue("CRITICAL", "Cannot re-fetch MT5 accounts for verification", response)
            return False
        
        accounts = response.get('accounts', [])
        print(f"\n📊 TOTAL MT5 ACCOUNTS AFTER CLEANUP: {len(accounts)}")
        
        # Verify only one account with login 9928326
        login_9928326_accounts = [acc for acc in accounts if acc.get('mt5_login') == 9928326]
        
        if len(login_9928326_accounts) == 0:
            self.log_issue("CRITICAL", "No accounts with login 9928326 found after cleanup")
            return False
        elif len(login_9928326_accounts) > 1:
            self.log_issue("CRITICAL", 
                          f"Still {len(login_9928326_accounts)} accounts with login 9928326 after cleanup",
                          login_9928326_accounts)
            return False
        else:
            account = login_9928326_accounts[0]
            print(f"✅ EXACTLY ONE ACCOUNT WITH LOGIN 9928326 FOUND")
            print(f"   Account ID: {account.get('account_id')}")
            print(f"   Client ID: {account.get('client_id')}")
            print(f"   Fund Code: {account.get('fund_code')}")
            print(f"   Broker Code: {account.get('broker_code')}")
            
            # Verify it belongs to Salvador Palma
            if account.get('client_id') != "client_0fd630c3":
                self.log_issue("CRITICAL", 
                              f"Login 9928326 belongs to {account.get('client_id')}, not Salvador Palma (client_0fd630c3)")
                return False
            
            # Verify it's BALANCE fund
            if account.get('fund_code') != "BALANCE":
                self.log_issue("HIGH", 
                              f"Login 9928326 is {account.get('fund_code')} fund, expected BALANCE")
            
            # Verify it's DooTechnology broker
            if account.get('broker_code') != "dootechnology":
                self.log_issue("HIGH", 
                              f"Login 9928326 is {account.get('broker_code')} broker, expected dootechnology")
        
        # Test by-broker endpoint
        success, response = self.run_api_call("GET", "api/mt5/admin/accounts/by-broker")
        if success:
            print(f"\n📊 ACCOUNTS BY BROKER:")
            for broker, broker_accounts in response.items():
                print(f"   {broker}: {len(broker_accounts)} accounts")
                
                # Check for login 9928326 in each broker
                login_9928326_in_broker = [acc for acc in broker_accounts if acc.get('mt5_login') == 9928326]
                if login_9928326_in_broker:
                    print(f"     🎯 Login 9928326 found in {broker}")
                    if broker != "dootechnology":
                        self.log_issue("HIGH", f"Login 9928326 found in {broker}, should be in dootechnology only")
        
        # Verify no client_001 accounts with login 9928326
        client_001_accounts = [acc for acc in accounts if acc.get('client_id') == "client_001"]
        client_001_with_9928326 = [acc for acc in client_001_accounts if acc.get('mt5_login') == 9928326]
        
        if client_001_with_9928326:
            self.log_issue("CRITICAL", 
                          f"CLIENT_001 still has {len(client_001_with_9928326)} accounts with login 9928326")
            return False
        else:
            print(f"✅ NO CLIENT_001 ACCOUNTS WITH LOGIN 9928326")
        
        return True
    
    def generate_final_report(self):
        """Generate final investigation and cleanup report"""
        print("\n" + "="*80)
        print("FINAL MT5 DUPLICATION INVESTIGATION REPORT")
        print("="*80)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total API calls: {self.tests_run}")
        print(f"   Successful calls: {self.tests_passed}")
        print(f"   Issues found: {len(self.issues_found)}")
        
        if self.issues_found:
            print(f"\n🚨 ISSUES FOUND:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue['severity']}: {issue['description']}")
        else:
            print(f"\n✅ NO ISSUES FOUND - MT5 accounts are properly configured")
        
        # Final verification
        if self.correct_account:
            print(f"\n🎯 CORRECT ACCOUNT VERIFIED:")
            print(f"   Account ID: {self.correct_account.get('account_id')}")
            print(f"   Client: Salvador Palma (client_0fd630c3)")
            print(f"   MT5 Login: 9928326")
            print(f"   Fund: {self.correct_account.get('fund_code')}")
            print(f"   Broker: {self.correct_account.get('broker_code')}")
            print(f"   Allocated: ${self.correct_account.get('total_allocated', 0):,.2f}")
        
        # Determine overall status
        critical_issues = [issue for issue in self.issues_found if issue['severity'] == 'CRITICAL']
        high_issues = [issue for issue in self.issues_found if issue['severity'] == 'HIGH']
        
        if critical_issues:
            print(f"\n❌ INVESTIGATION STATUS: CRITICAL ISSUES REMAIN")
            print(f"   {len(critical_issues)} critical issues need immediate attention")
            return False
        elif high_issues:
            print(f"\n⚠️  INVESTIGATION STATUS: HIGH PRIORITY ISSUES FOUND")
            print(f"   {len(high_issues)} high priority issues should be addressed")
            return True
        else:
            print(f"\n✅ INVESTIGATION STATUS: ALL ISSUES RESOLVED")
            print(f"   MT5 account duplication has been successfully cleaned up")
            return True
    
    def run_full_investigation(self):
        """Run complete MT5 duplication investigation and cleanup"""
        print("🔍 STARTING MT5 ACCOUNT DUPLICATION INVESTIGATION")
        print("=" * 80)
        
        try:
            # Authenticate first
            if not self.authenticate_admin():
                print("❌ Admin authentication failed")
                return False
            
            # Priority 1: Investigate current accounts
            if not self.priority_1_investigate_current_accounts():
                print("❌ Priority 1 investigation failed")
                return False
            
            # Priority 2: Clean up duplicates (only if duplicates found)
            if not self.priority_2_clean_duplicate_accounts():
                print("❌ Priority 2 cleanup failed")
                return False
            
            # Priority 3: Verify correct data
            if not self.priority_3_verify_correct_data():
                print("❌ Priority 3 verification failed")
                return False
            
            # Generate final report
            success = self.generate_final_report()
            
            return success
            
        except Exception as e:
            print(f"❌ Investigation failed with exception: {str(e)}")
            return False

def main():
    """Main function to run MT5 duplication investigation"""
    print("MT5 Account Duplication Investigation and Cleanup")
    print("=" * 50)
    
    investigator = MT5DuplicationInvestigator()
    success = investigator.run_full_investigation()
    
    if success:
        print("\n🎉 MT5 DUPLICATION INVESTIGATION COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n💥 MT5 DUPLICATION INVESTIGATION FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()