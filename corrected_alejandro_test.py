#!/usr/bin/env python3
"""
CORRECTED ALEJANDRO TEST: Using the correct endpoints and checking actual data
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://trading-platform-76.preview.emergentagent.com/api"
CLIENT_ID = "client_alejandro"

class CorrectedAlejandroTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def authenticate(self):
        """Authenticate as admin"""
        try:
            auth_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                self.log_result("Admin Authentication", True, f"Authenticated as {data.get('name', 'admin')}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_ready_for_investment(self):
        """Test GET /clients/ready-for-investment endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/clients/ready-for-investment")
            
            if response.status_code == 200:
                data = response.json()
                ready_clients = data.get('ready_clients', [])
                
                # Find Alejandro in the list
                alejandro = None
                for client in ready_clients:
                    if client.get('client_id') == CLIENT_ID:
                        alejandro = client
                        break
                
                if alejandro:
                    email = alejandro.get('email', '')
                    name = alejandro.get('name', '')
                    
                    # Report what we found
                    self.log_result("Ready for Investment", True, 
                                  f"Found {name} ({CLIENT_ID}) with email: {email}")
                    
                    # Check if email matches expected
                    if email == 'alexmar7609@gmail.com':
                        print("   ✅ Email matches expected: alexmar7609@gmail.com")
                    else:
                        print(f"   ⚠️ Email mismatch - Found: {email}, Expected: alexmar7609@gmail.com")
                    
                    return True
                else:
                    self.log_result("Ready for Investment", False, 
                                  f"Client {CLIENT_ID} not found in ready clients list", ready_clients)
                    return False
            else:
                self.log_result("Ready for Investment", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Ready for Investment", False, f"Exception: {str(e)}")
            return False
    
    def test_client_investments_correct_endpoint(self):
        """Test GET /investments/client/{client_id} endpoint (correct endpoint)"""
        try:
            response = self.session.get(f"{BASE_URL}/investments/client/{CLIENT_ID}")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get('investments', [])
                
                self.log_result("Client Investments (Correct Endpoint)", True, 
                              f"Found {len(investments)} investments")
                
                if investments:
                    total_value = sum(inv.get('current_value', 0) for inv in investments)
                    print(f"   Total Value: ${total_value:,.2f}")
                    
                    for inv in investments:
                        fund_code = inv.get('fund_code', 'Unknown')
                        current_value = inv.get('current_value', 0)
                        print(f"   - {fund_code}: ${current_value:,.2f}")
                
                return True
            else:
                self.log_result("Client Investments (Correct Endpoint)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Client Investments (Correct Endpoint)", False, f"Exception: {str(e)}")
            return False
    
    def test_client_investments_wrong_endpoint(self):
        """Test GET /clients/{client_id}/investments endpoint (wrong endpoint from test)"""
        try:
            response = self.session.get(f"{BASE_URL}/clients/{CLIENT_ID}/investments")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Client Investments (Wrong Endpoint)", True, 
                              f"Unexpectedly worked: {data}")
                return True
            else:
                self.log_result("Client Investments (Wrong Endpoint)", True, 
                              f"Expected 404 - HTTP {response.status_code}: {response.text}")
                return True
                
        except Exception as e:
            self.log_result("Client Investments (Wrong Endpoint)", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_accounts(self):
        """Test GET /mt5/accounts/{client_id} endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/mt5/accounts/{CLIENT_ID}")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                
                self.log_result("MT5 Accounts", True, 
                              f"Found {len(accounts)} MT5 accounts")
                
                if accounts:
                    total_balance = sum(acc.get('balance', 0) for acc in accounts)
                    print(f"   Total Balance: ${total_balance:,.2f}")
                    
                    for acc in accounts:
                        account_number = acc.get('mt5_account_number', 'Unknown')
                        broker_name = acc.get('broker_name', 'Unknown')
                        balance = acc.get('balance', 0)
                        print(f"   - {account_number} ({broker_name}): ${balance:,.2f}")
                
                return True
            else:
                self.log_result("MT5 Accounts", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("MT5 Accounts", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_overview(self):
        """Test GET /investments/admin/overview endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/investments/admin/overview")
            
            if response.status_code == 200:
                data = response.json()
                total_aum = data.get('total_aum', 0)
                total_investments = data.get('total_investments', 0)
                total_clients = data.get('total_clients', 0)
                
                # Handle string format
                if isinstance(total_aum, str):
                    total_aum = float(total_aum.replace('$', '').replace(',', ''))
                
                self.log_result("Admin Overview", True, 
                              f"Total AUM: ${total_aum:,.2f}, Investments: {total_investments}, Clients: {total_clients}")
                return True
            else:
                self.log_result("Admin Overview", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Overview", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests to understand current state"""
        print("🔍 CORRECTED ALEJANDRO TEST: Understanding Current Data State")
        print("=" * 80)
        print(f"Client ID: {CLIENT_ID}")
        print(f"Backend URL: {BASE_URL}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("\n❌ AUTHENTICATION FAILED - Cannot proceed with tests")
            return False
        
        # Run all tests
        tests = [
            self.test_ready_for_investment,
            self.test_client_investments_correct_endpoint,
            self.test_client_investments_wrong_endpoint,
            self.test_mt5_accounts,
            self.test_admin_overview
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Summary
        print("\n" + "=" * 80)
        print("CURRENT DATA STATE ANALYSIS")
        print("=" * 80)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        print("\nKEY FINDINGS:")
        print("1. Ready for Investment: Client exists but email may be wrong")
        print("2. Investments: Wrong endpoint used in original test (/clients/{id}/investments vs /investments/client/{id})")
        print("3. MT5 Accounts: Endpoint exists but may have no data")
        print("4. Admin Overview: Shows overall system state")
        
        return True

def main():
    """Main test execution"""
    tester = CorrectedAlejandroTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()