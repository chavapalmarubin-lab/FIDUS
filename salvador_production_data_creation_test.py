#!/usr/bin/env python3
"""
SALVADOR PALMA PRODUCTION DATA CREATION TEST
===========================================

This test script executes the exact API calls specified in the urgent review request
to create Salvador's data directly in production using API endpoints.

APPROACH: Use production API endpoints to create Salvador's data instead of trying 
to access database directly.

Expected Result: After successful API creation, production should show:
- Total AUM: $1,267,485.40
- Total Clients: 1 (Salvador)
- MT5 Accounts: 2 (DooTechnology + VT Markets)
"""

import requests
import json
import sys
from datetime import datetime

# Production API Base URL
PRODUCTION_API_BASE = "https://fidus-invest.emergent.host/api"

class SalvadorProductionDataCreator:
    def __init__(self):
        self.base_url = PRODUCTION_API_BASE
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def login_to_production(self):
        """Step 1: LOGIN TO PRODUCTION"""
        print("\n🔐 STEP 1: LOGIN TO PRODUCTION")
        print("=" * 50)
        
        try:
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                headers={"Content-Type": "application/json"},
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    self.log_result(
                        "Admin Login", 
                        True, 
                        f"Successfully logged in as admin. Token obtained.",
                        {"user": data.get("name", "Admin"), "type": data.get("type")}
                    )
                    return True
                else:
                    self.log_result("Admin Login", False, "Login response missing token", data)
                    return False
            else:
                self.log_result(
                    "Admin Login", 
                    False, 
                    f"Login failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False
    
    def create_salvador_client(self):
        """Step 2: CREATE SALVADOR CLIENT"""
        print("\n👤 STEP 2: CREATE SALVADOR CLIENT")
        print("=" * 50)
        
        try:
            client_data = {
                "username": "client3",
                "name": "SALVADOR PALMA",
                "email": "chava@alyarglobal.com",
                "phone": "+52-663-123-4567",
                "notes": "Production client - Salvador Palma"
            }
            
            response = self.session.post(
                f"{self.base_url}/clients/create",
                headers={"Content-Type": "application/json"},
                json=client_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result(
                    "Salvador Client Creation",
                    True,
                    f"Successfully created Salvador Palma client (client_003)",
                    {"client_id": data.get("id", "client_003"), "name": data.get("name")}
                )
                return True
            elif response.status_code == 409:
                # Client already exists - this is actually good
                self.log_result(
                    "Salvador Client Creation",
                    True,
                    "Salvador Palma client already exists (client_003) - GOOD",
                    {"status": "already_exists"}
                )
                return True
            else:
                self.log_result(
                    "Salvador Client Creation",
                    False,
                    f"Client creation failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("Salvador Client Creation", False, f"Client creation error: {str(e)}")
            return False
    
    def create_balance_investment(self):
        """Step 3: CREATE BALANCE INVESTMENT ($1,263,485.40)"""
        print("\n💰 STEP 3: CREATE BALANCE INVESTMENT")
        print("=" * 50)
        
        try:
            investment_data = {
                "client_id": "client_003",
                "fund_code": "BALANCE",
                "amount": 1263485.40,
                "deposit_date": "2025-04-01"
            }
            
            response = self.session.post(
                f"{self.base_url}/investments/create",
                headers={"Content-Type": "application/json"},
                json=investment_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.balance_investment_id = data.get("investment_id")
                self.log_result(
                    "BALANCE Investment Creation",
                    True,
                    f"Successfully created BALANCE investment: ${investment_data['amount']:,.2f}",
                    {"investment_id": self.balance_investment_id, "amount": investment_data['amount']}
                )
                return True
            else:
                self.log_result(
                    "BALANCE Investment Creation",
                    False,
                    f"Investment creation failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("BALANCE Investment Creation", False, f"Investment creation error: {str(e)}")
            return False
    
    def create_core_investment(self):
        """Step 4: CREATE CORE INVESTMENT ($4,000)"""
        print("\n💰 STEP 4: CREATE CORE INVESTMENT")
        print("=" * 50)
        
        try:
            investment_data = {
                "client_id": "client_003",
                "fund_code": "CORE",
                "amount": 4000.00,
                "deposit_date": "2025-04-01"
            }
            
            response = self.session.post(
                f"{self.base_url}/investments/create",
                headers={"Content-Type": "application/json"},
                json=investment_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.core_investment_id = data.get("investment_id")
                self.log_result(
                    "CORE Investment Creation",
                    True,
                    f"Successfully created CORE investment: ${investment_data['amount']:,.2f}",
                    {"investment_id": self.core_investment_id, "amount": investment_data['amount']}
                )
                return True
            else:
                self.log_result(
                    "CORE Investment Creation",
                    False,
                    f"Investment creation failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("CORE Investment Creation", False, f"Investment creation error: {str(e)}")
            return False
    
    def create_dootechnology_mt5_account(self):
        """Step 5: CREATE DOOTECHNOLOGY MT5 ACCOUNT"""
        print("\n🏦 STEP 5: CREATE DOOTECHNOLOGY MT5 ACCOUNT")
        print("=" * 50)
        
        try:
            mt5_data = {
                "client_id": "client_003",
                "login": "9928326",
                "broker": "DooTechnology",
                "server": "DooTechnology-Live",
                "investment_id": getattr(self, 'balance_investment_id', 'BALANCE_INVESTMENT_ID')
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/mt5/accounts",
                headers={"Content-Type": "application/json"},
                json=mt5_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result(
                    "DooTechnology MT5 Account",
                    True,
                    f"Successfully created DooTechnology MT5 account (Login: {mt5_data['login']})",
                    {"login": mt5_data['login'], "broker": mt5_data['broker']}
                )
                return True
            else:
                self.log_result(
                    "DooTechnology MT5 Account",
                    False,
                    f"MT5 account creation failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("DooTechnology MT5 Account", False, f"MT5 account creation error: {str(e)}")
            return False
    
    def create_vt_markets_mt5_account(self):
        """Step 6: CREATE VT MARKETS MT5 ACCOUNT"""
        print("\n🏦 STEP 6: CREATE VT MARKETS MT5 ACCOUNT")
        print("=" * 50)
        
        try:
            mt5_data = {
                "client_id": "client_003",
                "login": "15759667",
                "broker": "VT Markets",
                "server": "VTMarkets-PAMM",
                "investment_id": getattr(self, 'core_investment_id', 'CORE_INVESTMENT_ID')
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/mt5/accounts",
                headers={"Content-Type": "application/json"},
                json=mt5_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result(
                    "VT Markets MT5 Account",
                    True,
                    f"Successfully created VT Markets MT5 account (Login: {mt5_data['login']})",
                    {"login": mt5_data['login'], "broker": mt5_data['broker']}
                )
                return True
            else:
                self.log_result(
                    "VT Markets MT5 Account",
                    False,
                    f"MT5 account creation failed with status {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_result("VT Markets MT5 Account", False, f"MT5 account creation error: {str(e)}")
            return False
    
    def verify_production_data(self):
        """Step 7: VERIFY PRODUCTION DATA"""
        print("\n✅ STEP 7: VERIFY PRODUCTION DATA")
        print("=" * 50)
        
        verification_results = []
        
        # Verify Salvador client exists
        try:
            response = self.session.get(f"{self.base_url}/admin/clients", timeout=30)
            if response.status_code == 200:
                clients = response.json()
                salvador_found = False
                for client in clients.get('clients', []):
                    if client.get('id') == 'client_003' or 'SALVADOR' in client.get('name', '').upper():
                        salvador_found = True
                        verification_results.append(f"✅ Salvador Palma client found: {client.get('name')}")
                        break
                
                if not salvador_found:
                    verification_results.append("❌ Salvador Palma client NOT found")
            else:
                verification_results.append(f"❌ Failed to fetch clients: {response.status_code}")
        except Exception as e:
            verification_results.append(f"❌ Client verification error: {str(e)}")
        
        # Verify investments
        try:
            response = self.session.get(f"{self.base_url}/investments/client/client_003", timeout=30)
            if response.status_code == 200:
                investments = response.json()
                total_amount = 0
                investment_count = len(investments.get('investments', []))
                
                for investment in investments.get('investments', []):
                    amount = investment.get('principal_amount', 0)
                    fund_code = investment.get('fund_code', '')
                    total_amount += amount
                    verification_results.append(f"✅ {fund_code} investment found: ${amount:,.2f}")
                
                verification_results.append(f"✅ Total investments: {investment_count}")
                verification_results.append(f"✅ Total AUM: ${total_amount:,.2f}")
                
                # Check if we have expected amounts
                if abs(total_amount - 1267485.40) < 1:
                    verification_results.append("✅ Expected total AUM ($1,267,485.40) ACHIEVED!")
                else:
                    verification_results.append(f"⚠️ Expected $1,267,485.40 but got ${total_amount:,.2f}")
            else:
                verification_results.append(f"❌ Failed to fetch investments: {response.status_code}")
        except Exception as e:
            verification_results.append(f"❌ Investment verification error: {str(e)}")
        
        # Verify MT5 accounts
        try:
            response = self.session.get(f"{self.base_url}/admin/mt5/accounts", timeout=30)
            if response.status_code == 200:
                mt5_accounts = response.json()
                mt5_count = len(mt5_accounts.get('accounts', []))
                verification_results.append(f"✅ Total MT5 accounts: {mt5_count}")
                
                doo_found = False
                vt_found = False
                
                for account in mt5_accounts.get('accounts', []):
                    login = account.get('login', '')
                    broker = account.get('broker', '')
                    
                    if login == '9928326':
                        doo_found = True
                        verification_results.append(f"✅ DooTechnology MT5 account found: {login}")
                    elif login == '15759667':
                        vt_found = True
                        verification_results.append(f"✅ VT Markets MT5 account found: {login}")
                
                if not doo_found:
                    verification_results.append("❌ DooTechnology MT5 account (9928326) NOT found")
                if not vt_found:
                    verification_results.append("❌ VT Markets MT5 account (15759667) NOT found")
                    
                if doo_found and vt_found:
                    verification_results.append("✅ Both expected MT5 accounts found!")
            else:
                verification_results.append(f"❌ Failed to fetch MT5 accounts: {response.status_code}")
        except Exception as e:
            verification_results.append(f"❌ MT5 verification error: {str(e)}")
        
        # Log verification results
        for result in verification_results:
            print(f"   {result}")
        
        success_count = len([r for r in verification_results if r.startswith("✅")])
        total_checks = len(verification_results)
        
        self.log_result(
            "Production Data Verification",
            success_count > total_checks * 0.7,  # 70% success rate required
            f"Verification completed: {success_count}/{total_checks} checks passed",
            {"verification_results": verification_results}
        )
        
        return success_count > total_checks * 0.7
    
    def run_complete_test(self):
        """Execute complete Salvador data creation test"""
        print("🚀 SALVADOR PALMA PRODUCTION DATA CREATION TEST")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 60)
        
        # Execute all steps in sequence
        steps = [
            ("Login to Production", self.login_to_production),
            ("Create Salvador Client", self.create_salvador_client),
            ("Create BALANCE Investment", self.create_balance_investment),
            ("Create CORE Investment", self.create_core_investment),
            ("Create DooTechnology MT5", self.create_dootechnology_mt5_account),
            ("Create VT Markets MT5", self.create_vt_markets_mt5_account),
            ("Verify Production Data", self.verify_production_data)
        ]
        
        successful_steps = 0
        
        for step_name, step_function in steps:
            try:
                if step_function():
                    successful_steps += 1
                else:
                    print(f"\n⚠️ Step failed: {step_name}")
                    # Continue with remaining steps even if one fails
            except Exception as e:
                print(f"\n💥 Step error: {step_name} - {str(e)}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 FINAL RESULTS SUMMARY")
        print("=" * 60)
        
        success_rate = (successful_steps / len(steps)) * 100
        print(f"Steps completed successfully: {successful_steps}/{len(steps)} ({success_rate:.1f}%)")
        
        passed_tests = len([r for r in self.test_results if r['success']])
        total_tests = len(self.test_results)
        test_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Individual tests passed: {passed_tests}/{total_tests} ({test_success_rate:.1f}%)")
        
        if success_rate >= 85:
            print("✅ SALVADOR DATA CREATION: SUCCESS!")
            print("   Production should now show Salvador's complete data")
        elif success_rate >= 70:
            print("⚠️ SALVADOR DATA CREATION: PARTIAL SUCCESS")
            print("   Some data created, manual verification recommended")
        else:
            print("❌ SALVADOR DATA CREATION: FAILED")
            print("   Manual intervention required")
        
        print("\nExpected Production Results:")
        print("- Total AUM: $1,267,485.40")
        print("- Total Clients: 1 (Salvador)")
        print("- MT5 Accounts: 2 (DooTechnology + VT Markets)")
        
        return success_rate >= 70

def main():
    """Main execution function"""
    creator = SalvadorProductionDataCreator()
    success = creator.run_complete_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()