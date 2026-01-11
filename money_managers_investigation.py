#!/usr/bin/env python3
"""
MONEY MANAGERS COLLECTION INVESTIGATION

Context: Chava has clarified that managers are identified through the `money_managers` collection 
(not magic numbers). We need to verify the manager-to-account-to-fund mapping.

Your Task:
1. Login as Admin (admin/password123)
2. Query money_managers Collection
3. Verify Expected Structure
4. Calculate Total P&L
5. Get Fund Mapping
6. Report Format

Expected Structure:
CP Strategy Provider:
- Account: 885822 (CORE Fund)
- P&L: +$101.23

TradingHub Gold Provider:
- Account: 886557 (BALANCE Fund)
- P&L: +$4,973.56

GoldenTrade Provider:
- Account: 886066 (BALANCE Fund)
- P&L: +$692.22

UNO14 MAM Manager:
- Account: 886602 (BALANCE Fund)
- P&L: +$1,136.10

Expected Total P&L: $101 + $4,974 + $692 + $1,136 = $6,903
"""

import requests
import json
import sys
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os

# Backend URL from environment
BACKEND_URL = "https://fintech-dashboard-60.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class MoneyManagersInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.mongo_client = None
        self.db = None
        self.investigation_results = []
        
    def log_result(self, category, success, details):
        """Log investigation results"""
        status = "✅ SUCCESS" if success else "❌ ISSUE"
        self.investigation_results.append({
            "category": category,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {category}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def connect_to_mongodb(self):
        """Connect to MongoDB to investigate money_managers collection"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client['fidus_production']
            
            # Test connection
            self.mongo_client.admin.command('ping')
            self.log_result("MongoDB Connection", True, "Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            self.log_result("MongoDB Connection", False, f"Failed to connect: {str(e)}")
            return False
    
    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    self.log_result("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token in response")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def query_money_managers_collection(self):
        """Query money_managers collection directly from MongoDB"""
        try:
            # Get all active managers from money_managers collection
            managers_cursor = self.db.money_managers.find({'status': 'active'})
            managers = list(managers_cursor)
            
            if not managers:
                self.log_result("Money Managers Collection Query", False, "No active managers found in money_managers collection")
                return []
            
            self.log_result("Money Managers Collection Query", True, f"Found {len(managers)} active managers in collection")
            
            # Process each manager
            manager_details = []
            for manager in managers:
                manager_info = {
                    'name': manager.get('name', 'Unknown'),
                    'strategy_name': manager.get('strategy_name', 'Unknown'),
                    'assigned_accounts': manager.get('assigned_accounts', []),
                    'initial_allocation': manager.get('initial_allocation', 0),
                    'current_equity': manager.get('current_equity', 0),
                    'true_pnl': manager.get('true_pnl', 0),
                    'win_rate': manager.get('win_rate', 0),
                    'profit_factor': manager.get('profit_factor', 0),
                    'risk_level': manager.get('risk_level', 'Unknown'),
                    'manager_id': str(manager.get('_id', ''))
                }
                manager_details.append(manager_info)
                
                # Log individual manager details
                self.log_result(f"Manager: {manager_info['name']}", True, 
                    f"Strategy: {manager_info['strategy_name']}, "
                    f"Accounts: {manager_info['assigned_accounts']}, "
                    f"P&L: ${manager_info['true_pnl']:,.2f}")
            
            return manager_details
            
        except Exception as e:
            self.log_result("Money Managers Collection Query", False, f"Exception: {str(e)}")
            return []
    
    def get_fund_mapping(self):
        """Get fund mapping from investments or fund_portfolio collections"""
        try:
            fund_mapping = {}
            
            # Try to get fund mapping from investments collection
            investments_cursor = self.db.investments.find({})
            investments = list(investments_cursor)
            
            if investments:
                for investment in investments:
                    mt5_account = investment.get('mt5_account')
                    fund_code = investment.get('fund_code')
                    if mt5_account and fund_code:
                        fund_mapping[str(mt5_account)] = fund_code
            
            # Also try fund_portfolio collection
            try:
                fund_portfolio_cursor = self.db.fund_portfolio.find({})
                fund_portfolios = list(fund_portfolio_cursor)
                
                for portfolio in fund_portfolios:
                    accounts = portfolio.get('mt5_accounts', [])
                    fund_code = portfolio.get('fund_code')
                    if accounts and fund_code:
                        for account in accounts:
                            fund_mapping[str(account)] = fund_code
            except:
                pass  # Collection might not exist
            
            # Also check mt5_accounts collection for fund_code
            try:
                mt5_accounts_cursor = self.db.mt5_accounts.find({})
                mt5_accounts = list(mt5_accounts_cursor)
                
                for account in mt5_accounts:
                    account_num = str(account.get('account', account.get('mt5_login', '')))
                    fund_code = account.get('fund_code', account.get('fund_type'))
                    if account_num and fund_code:
                        fund_mapping[account_num] = fund_code
            except:
                pass
            
            if fund_mapping:
                self.log_result("Fund Mapping Retrieved", True, f"Found {len(fund_mapping)} account-to-fund mappings")
                for account, fund in fund_mapping.items():
                    print(f"   Account {account} → {fund} Fund")
            else:
                self.log_result("Fund Mapping Retrieved", False, "No fund mapping found")
            
            return fund_mapping
            
        except Exception as e:
            self.log_result("Fund Mapping Retrieval", False, f"Exception: {str(e)}")
            return {}
    
    def verify_expected_structure(self, managers, fund_mapping):
        """Verify the expected manager-to-account-to-fund structure"""
        try:
            # Expected structure from the request
            expected_structure = {
                'CP Strategy Provider': {
                    'account': '885822',
                    'fund': 'CORE',
                    'expected_pnl': 101.23
                },
                'TradingHub Gold Provider': {
                    'account': '886557',
                    'fund': 'BALANCE',
                    'expected_pnl': 4973.56
                },
                'GoldenTrade Provider': {
                    'account': '886066',
                    'fund': 'BALANCE',
                    'expected_pnl': 692.22
                },
                'UNO14 MAM Manager': {
                    'account': '886602',
                    'fund': 'BALANCE',
                    'expected_pnl': 1136.10
                }
            }
            
            verification_results = {}
            total_actual_pnl = 0
            
            for manager in managers:
                manager_name = manager['name']
                strategy_name = manager['strategy_name']
                
                # Try to match by name or strategy name
                matched_expected = None
                for expected_name, expected_data in expected_structure.items():
                    if (expected_name.lower() in manager_name.lower() or 
                        expected_name.lower() in strategy_name.lower() or
                        manager_name.lower() in expected_name.lower() or
                        strategy_name.lower() in expected_name.lower()):
                        matched_expected = expected_data
                        break
                
                if matched_expected:
                    # Verify account assignment
                    assigned_accounts = manager['assigned_accounts']
                    expected_account = matched_expected['account']
                    expected_fund = matched_expected['fund']
                    expected_pnl = matched_expected['expected_pnl']
                    actual_pnl = manager['true_pnl']
                    
                    account_match = expected_account in [str(acc) for acc in assigned_accounts]
                    fund_match = False
                    
                    # Check fund mapping
                    if expected_account in fund_mapping:
                        actual_fund = fund_mapping[expected_account]
                        fund_match = actual_fund == expected_fund
                    
                    # Check P&L (allow some variance)
                    pnl_match = abs(actual_pnl - expected_pnl) < 100  # Allow $100 variance
                    
                    verification_results[manager_name] = {
                        'account_match': account_match,
                        'fund_match': fund_match,
                        'pnl_match': pnl_match,
                        'expected_account': expected_account,
                        'actual_accounts': assigned_accounts,
                        'expected_fund': expected_fund,
                        'actual_fund': fund_mapping.get(expected_account, 'Unknown'),
                        'expected_pnl': expected_pnl,
                        'actual_pnl': actual_pnl
                    }
                    
                    total_actual_pnl += actual_pnl
                    
                    # Log verification for this manager
                    status = account_match and fund_match and pnl_match
                    details = (f"Account: {expected_account} ({'✓' if account_match else '✗'}), "
                             f"Fund: {expected_fund} ({'✓' if fund_match else '✗'}), "
                             f"P&L: ${actual_pnl:,.2f} vs ${expected_pnl:,.2f} ({'✓' if pnl_match else '✗'})")
                    
                    self.log_result(f"Verification: {manager_name}", status, details)
                else:
                    self.log_result(f"Verification: {manager_name}", False, "No matching expected structure found")
            
            # Calculate total P&L
            expected_total_pnl = sum(data['expected_pnl'] for data in expected_structure.values())
            pnl_total_match = abs(total_actual_pnl - expected_total_pnl) < 200  # Allow $200 variance
            
            self.log_result("Total P&L Calculation", pnl_total_match, 
                f"Expected: ${expected_total_pnl:,.2f}, Actual: ${total_actual_pnl:,.2f}")
            
            return verification_results, total_actual_pnl
            
        except Exception as e:
            self.log_result("Expected Structure Verification", False, f"Exception: {str(e)}")
            return {}, 0
    
    def generate_manager_report(self, managers, fund_mapping, verification_results, total_pnl):
        """Generate the final manager-to-account mapping report"""
        try:
            print("\n" + "=" * 80)
            print("=== MANAGER TO ACCOUNT MAPPING ===")
            print("=" * 80)
            
            # Group by fund
            balance_managers = []
            core_managers = []
            other_managers = []
            
            balance_total = 0
            core_total = 0
            
            for manager in managers:
                manager_name = manager['name']
                assigned_accounts = manager['assigned_accounts']
                true_pnl = manager['true_pnl']
                
                # Determine fund based on assigned accounts
                manager_fund = None
                for account in assigned_accounts:
                    account_str = str(account)
                    if account_str in fund_mapping:
                        manager_fund = fund_mapping[account_str]
                        break
                
                manager_info = {
                    'name': manager_name,
                    'accounts': assigned_accounts,
                    'pnl': true_pnl,
                    'fund': manager_fund
                }
                
                if manager_fund == 'BALANCE':
                    balance_managers.append(manager_info)
                    balance_total += true_pnl
                elif manager_fund == 'CORE':
                    core_managers.append(manager_info)
                    core_total += true_pnl
                else:
                    other_managers.append(manager_info)
            
            # Print BALANCE Fund section
            print(f"\nBALANCE Fund ($100,000):")
            for manager in balance_managers:
                accounts_str = ', '.join(str(acc) for acc in manager['accounts'])
                print(f"- {manager['name']} → {accounts_str} → +${manager['pnl']:,.2f}")
            print(f"Subtotal: +${balance_total:,.2f}")
            
            # Print CORE Fund section
            print(f"\nCORE Fund ($18,151):")
            for manager in core_managers:
                accounts_str = ', '.join(str(acc) for acc in manager['accounts'])
                print(f"- {manager['name']} → {accounts_str} → +${manager['pnl']:,.2f}")
            
            # Add unassigned accounts if any
            # Check for account 891234 which might be unassigned
            if '891234' in fund_mapping and fund_mapping['891234'] == 'CORE':
                unassigned_found = True
                for manager in core_managers:
                    if '891234' in [str(acc) for acc in manager['accounts']]:
                        unassigned_found = False
                        break
                if unassigned_found:
                    print(f"- Unassigned → 891234 → $0")
            
            print(f"Subtotal: +${core_total:,.2f}")
            
            # Print other managers if any
            if other_managers:
                print(f"\nOther Managers:")
                for manager in other_managers:
                    accounts_str = ', '.join(str(acc) for acc in manager['accounts'])
                    print(f"- {manager['name']} → {accounts_str} → +${manager['pnl']:,.2f}")
            
            # Print total
            print(f"\nTOTAL P&L: ${total_pnl:,.0f}")
            
            self.log_result("Manager Report Generated", True, f"Report generated with {len(managers)} managers")
            
        except Exception as e:
            self.log_result("Manager Report Generation", False, f"Exception: {str(e)}")
    
    def run_investigation(self):
        """Run complete money managers collection investigation"""
        print("🔍 MONEY MANAGERS COLLECTION INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Connect to MongoDB
        print("📋 STEP 1: Connect to MongoDB")
        if not self.connect_to_mongodb():
            print("❌ MongoDB connection failed. Cannot investigate money_managers collection.")
            return False
        print()
        
        # Step 2: Authenticate as Admin
        print("📋 STEP 2: Login as Admin (admin/password123)")
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with investigation.")
            return False
        print()
        
        # Step 3: Query money_managers Collection
        print("📋 STEP 3: Query money_managers Collection")
        managers = self.query_money_managers_collection()
        if not managers:
            print("❌ No managers found. Cannot proceed with verification.")
            return False
        print()
        
        # Step 4: Get Fund Mapping
        print("📋 STEP 4: Get Fund Mapping")
        fund_mapping = self.get_fund_mapping()
        print()
        
        # Step 5: Verify Expected Structure
        print("📋 STEP 5: Verify Expected Structure")
        verification_results, total_pnl = self.verify_expected_structure(managers, fund_mapping)
        print()
        
        # Step 6: Generate Report
        print("📋 STEP 6: Generate Manager Report")
        self.generate_manager_report(managers, fund_mapping, verification_results, total_pnl)
        print()
        
        # Summary
        self.print_investigation_summary()
        
        return True
    
    def print_investigation_summary(self):
        """Print investigation summary"""
        print("=" * 80)
        print("📊 MONEY MANAGERS INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_checks = len(self.investigation_results)
        successful_checks = sum(1 for result in self.investigation_results if result['success'])
        failed_checks = total_checks - successful_checks
        success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0
        
        print(f"Total Checks: {total_checks}")
        print(f"Successful: {successful_checks}")
        print(f"Issues Found: {failed_checks}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_checks > 0:
            print("❌ ISSUES IDENTIFIED:")
            for result in self.investigation_results:
                if not result['success']:
                    print(f"   • {result['category']}: {result['details']}")
            print()
        
        print("✅ SUCCESSFUL CHECKS:")
        for result in self.investigation_results:
            if result['success']:
                print(f"   • {result['category']}: {result['details']}")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check if all expected managers were found
        manager_verification_count = sum(1 for r in self.investigation_results 
                                       if r['category'].startswith('Verification:') and r['success'])
        
        if manager_verification_count >= 4:
            print("   ✅ All expected managers found and verified")
        else:
            print(f"   ⚠️ Only {manager_verification_count}/4 expected managers verified")
        
        # Check if total P&L matches
        total_pnl_success = any('Total P&L Calculation' in r['category'] and r['success'] 
                               for r in self.investigation_results)
        
        if total_pnl_success:
            print("   ✅ Total P&L calculation matches expected ($6,903)")
        else:
            print("   ❌ Total P&L calculation does not match expected")
        
        # Check if fund mapping is complete
        fund_mapping_success = any('Fund Mapping Retrieved' in r['category'] and r['success'] 
                                  for r in self.investigation_results)
        
        if fund_mapping_success:
            print("   ✅ Fund-to-account mapping retrieved successfully")
        else:
            print("   ❌ Fund-to-account mapping incomplete or missing")
        
        print()

def main():
    """Main investigation execution"""
    investigator = MoneyManagersInvestigation()
    success = investigator.run_investigation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()