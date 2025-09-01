import requests
import sys
from datetime import datetime
import json
import io
from PIL import Image

class FidusAPITester:
    def __init__(self, base_url="https://fidus-portal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.client_user = None
        self.admin_user = None
        self.application_id = None
        self.extracted_data = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_client_login(self):
        """Test client login"""
        success, response = self.run_test(
            "Client Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client1", 
                "password": "password123",
                "user_type": "client"
            }
        )
        if success:
            self.client_user = response
            print(f"   Client logged in: {response.get('name', 'Unknown')}")
        return success

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            }
        )
        if success:
            self.admin_user = response
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
        return success

    def test_invalid_login(self):
        """Test invalid login credentials"""
        success, _ = self.run_test(
            "Invalid Login",
            "POST",
            "api/auth/login",
            401,
            data={
                "username": "invalid", 
                "password": "wrong",
                "user_type": "client"
            }
        )
        return success

    def test_client_data(self):
        """Test getting client data"""
        if not self.client_user:
            print("❌ Skipping client data test - no client user available")
            return False
            
        client_id = self.client_user.get('id')
        success, response = self.run_test(
            "Get Client Data",
            "GET",
            f"api/client/{client_id}/data",
            200
        )
        
        if success:
            # Verify response structure
            required_keys = ['balance', 'transactions', 'monthly_statement']
            missing_keys = [key for key in required_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
                
            # Check balance structure
            balance = response.get('balance', {})
            balance_keys = ['total_balance', 'fidus_funds', 'core_balance', 'dynamic_balance']
            for key in balance_keys:
                if key in balance:
                    print(f"   {key}: {balance[key]}")
                    
            # Check transactions
            transactions = response.get('transactions', [])
            print(f"   Transactions count: {len(transactions)}")
            
        return success

    def test_client_transactions_filtered(self):
        """Test getting filtered client transactions"""
        if not self.client_user:
            print("❌ Skipping filtered transactions test - no client user available")
            return False
            
        client_id = self.client_user.get('id')
        
        # Test with fund_type filter
        success, response = self.run_test(
            "Get Filtered Transactions (fund_type=fidus)",
            "GET",
            f"api/client/{client_id}/transactions?fund_type=fidus",
            200
        )
        
        if success:
            transactions = response.get('transactions', [])
            print(f"   Filtered transactions count: {len(transactions)}")
            if transactions:
                # Verify all transactions are fidus type
                fidus_count = sum(1 for t in transactions if t.get('fund_type') == 'fidus')
                print(f"   Fidus transactions: {fidus_count}/{len(transactions)}")
                
        return success

    def test_admin_portfolio_summary(self):
        """Test getting admin portfolio summary"""
        success, response = self.run_test(
            "Get Portfolio Summary",
            "GET",
            "api/admin/portfolio-summary",
            200
        )
        
        if success:
            # Verify response structure
            required_keys = ['aum', 'allocation', 'weekly_performance', 'ytd_return']
            missing_keys = [key for key in required_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
                
            # Check specific values
            aum = response.get('aum')
            ytd_return = response.get('ytd_return')
            allocation = response.get('allocation', {})
            weekly_performance = response.get('weekly_performance', [])
            
            print(f"   AUM: {aum}")
            print(f"   YTD Return: {ytd_return}%")
            print(f"   Allocation funds: {list(allocation.keys())}")
            print(f"   Weekly performance weeks: {len(weekly_performance)}")
                
        return success

    def test_admin_clients(self):
        """Test getting all clients for admin"""
        success, response = self.run_test(
            "Get All Clients",
            "GET",
            "api/admin/clients",
            200
        )
        
        if success:
            clients = response.get('clients', [])
            print(f"   Clients count: {len(clients)}")
            if clients:
                for client in clients:
                    print(f"   Client: {client.get('name')} - Balance: {client.get('total_balance')}")
                
        return success

def main():
    print("🚀 Starting FIDUS API Testing...")
    print("=" * 50)
    
    tester = FidusAPITester()
    
    # Test authentication endpoints
    print("\n📋 AUTHENTICATION TESTS")
    print("-" * 30)
    tester.test_client_login()
    tester.test_admin_login()
    tester.test_invalid_login()
    
    # Test client endpoints
    print("\n📋 CLIENT ENDPOINTS TESTS")
    print("-" * 30)
    tester.test_client_data()
    tester.test_client_transactions_filtered()
    
    # Test admin endpoints
    print("\n📋 ADMIN ENDPOINTS TESTS")
    print("-" * 30)
    tester.test_admin_portfolio_summary()
    tester.test_admin_clients()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend APIs are working correctly.")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())