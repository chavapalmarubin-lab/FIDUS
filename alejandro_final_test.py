#!/usr/bin/env python3
"""
ALEJANDRO MARISCAL FINAL PRODUCTION VERIFICATION
Based on review request: Test client_alejandro with email alexmar7609@gmail.com
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from review request
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class AlejandroFinalTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.results = []
        
    def log_test(self, name, success, details):
        """Log test result"""
        status = "✅" if success else "❌"
        print(f"{status} {name}: {details}")
        self.results.append({"name": name, "success": success, "details": details})
        
    def authenticate(self):
        """Authenticate as admin"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                self.log_test("Admin Authentication", True, f"Authenticated as {data.get('name', 'admin')}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_ready_for_investment(self):
        """Test 1: Ready for Investment Endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/clients/ready-for-investment")
            
            if response.status_code == 200:
                data = response.json()
                ready_clients = data.get('ready_clients', [])
                
                # Look for client_alejandro
                alejandro = None
                for client in ready_clients:
                    if client.get('client_id') == 'client_alejandro':
                        alejandro = client
                        break
                
                if alejandro:
                    email = alejandro.get('email', '')
                    if email == 'alexmar7609@gmail.com':
                        self.log_test("Ready for Investment", True, f"Found client_alejandro with correct email: {email}")
                        return True
                    else:
                        self.log_test("Ready for Investment", False, f"Found client_alejandro but wrong email: {email} (expected: alexmar7609@gmail.com)")
                        return False
                else:
                    client_ids = [c.get('client_id', 'unknown') for c in ready_clients]
                    self.log_test("Ready for Investment", False, f"client_alejandro not found. Available clients: {client_ids}")
                    return False
            else:
                self.log_test("Ready for Investment", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Ready for Investment", False, f"Error: {str(e)}")
            return False
    
    def test_client_investments(self):
        """Test 2: Client Investments"""
        try:
            response = self.session.get(f"{API_BASE}/clients/client_alejandro/investments")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get('investments', [])
                
                if len(investments) == 2:
                    total_value = sum(inv.get('current_value', 0) for inv in investments)
                    expected_total = 118151.41
                    
                    if abs(total_value - expected_total) < 0.01:
                        investment_details = [f"{inv.get('fund_code', 'Unknown')}: ${inv.get('current_value', 0):,.2f}" for inv in investments]
                        self.log_test("Client Investments", True, f"Found 2 investments totaling ${total_value:,.2f}: {', '.join(investment_details)}")
                        return True
                    else:
                        self.log_test("Client Investments", False, f"Found 2 investments but total ${total_value:,.2f} != expected ${expected_total:,.2f}")
                        return False
                else:
                    self.log_test("Client Investments", False, f"Expected 2 investments, found {len(investments)}")
                    return False
            else:
                self.log_test("Client Investments", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Client Investments", False, f"Error: {str(e)}")
            return False
    
    def test_mt5_accounts(self):
        """Test 3: MT5 Accounts"""
        try:
            response = self.session.get(f"{API_BASE}/mt5/accounts/client_alejandro")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                
                if len(accounts) == 4:
                    total_balance = sum(acc.get('balance', 0) for acc in accounts)
                    expected_total = 118151.41
                    
                    # Check for MEXAtlantic broker
                    mexatlantic_count = sum(1 for acc in accounts if acc.get('broker_name', '').lower() == 'mexatlantic')
                    
                    if mexatlantic_count == 4 and abs(total_balance - expected_total) < 0.01:
                        account_details = [f"{acc.get('mt5_account_number', 'Unknown')}: ${acc.get('balance', 0):,.2f}" for acc in accounts]
                        self.log_test("MT5 Accounts", True, f"Found 4 MEXAtlantic accounts totaling ${total_balance:,.2f}: {', '.join(account_details)}")
                        return True
                    else:
                        self.log_test("MT5 Accounts", False, f"Found {len(accounts)} accounts ({mexatlantic_count} MEXAtlantic) totaling ${total_balance:,.2f}")
                        return False
                else:
                    self.log_test("MT5 Accounts", False, f"Expected 4 MT5 accounts, found {len(accounts)}")
                    return False
            else:
                self.log_test("MT5 Accounts", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("MT5 Accounts", False, f"Error: {str(e)}")
            return False
    
    def test_admin_overview(self):
        """Test 4: Admin Overview"""
        try:
            response = self.session.get(f"{API_BASE}/investments/admin/overview")
            
            if response.status_code == 200:
                data = response.json()
                total_aum = data.get('total_aum', 0)
                
                # Handle string format
                if isinstance(total_aum, str):
                    total_aum = float(total_aum.replace('$', '').replace(',', ''))
                
                if total_aum > 0:
                    self.log_test("Admin Overview", True, f"Total AUM: ${total_aum:,.2f} (> $0)")
                    return True
                else:
                    self.log_test("Admin Overview", False, f"Total AUM: ${total_aum:,.2f} (should be > $0)")
                    return False
            else:
                self.log_test("Admin Overview", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Overview", False, f"Error: {str(e)}")
            return False
    
    def run_tests(self):
        """Run all tests"""
        print("🚀 ALEJANDRO MARISCAL FINAL PRODUCTION VERIFICATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Client ID: client_alejandro")
        print(f"Expected Email: alexmar7609@gmail.com")
        print(f"Expected Total: $118,151.41")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        tests = [
            self.test_ready_for_investment,
            self.test_client_investments,
            self.test_mt5_accounts,
            self.test_admin_overview
        ]
        
        results = [test() for test in tests]
        passed = sum(results)
        total = len(results)
        success_rate = (passed / total) * 100
        
        print("\n" + "=" * 60)
        print("🎯 FINAL RESULTS")
        print("=" * 60)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 PRODUCTION READY: All endpoints working correctly!")
        else:
            print("🚨 PRODUCTION ISSUES: Some endpoints failing")
            
        return success_rate == 100

if __name__ == "__main__":
    tester = AlejandroFinalTest()
    success = tester.run_tests()
    sys.exit(0 if success else 1)