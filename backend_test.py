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

    def create_test_image(self):
        """Create a test image for document upload"""
        try:
            img = Image.new('RGB', (300, 200), color='white')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            return img_buffer
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None

    def test_registration_create_application(self):
        """Test registration application creation"""
        test_data = {
            "personalInfo": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@test.com",
                "phone": "+1-555-0123",
                "dateOfBirth": "1990-05-15",
                "nationality": "US",
                "address": "123 Test Street",
                "city": "Test City",
                "postalCode": "12345",
                "country": "United States"
            },
            "documentType": "passport"
        }
        
        success, response = self.run_test(
            "Create Registration Application",
            "POST",
            "api/registration/create-application",
            200,
            data=test_data
        )
        
        if success:
            self.application_id = response.get("applicationId")
            print(f"   Application ID: {self.application_id}")
        
        return success

    def test_document_processing(self):
        """Test document upload and processing"""
        if not self.application_id:
            print("❌ Skipping document processing - no application ID available")
            return False
            
        # Create test image
        test_image = self.create_test_image()
        if not test_image:
            print("❌ Failed to create test image")
            return False
        
        try:
            files = {
                'document': ('test_passport.jpg', test_image, 'image/jpeg')
            }
            data = {
                'documentType': 'passport',
                'applicationId': self.application_id
            }
            
            url = f"{self.base_url}/api/registration/process-document"
            print(f"\n🔍 Testing Document Processing...")
            print(f"   URL: {url}")
            
            response = requests.post(url, files=files, data=data, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            self.tests_run += 1
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    self.extracted_data = response_data.get("extractedData")
                    print(f"   Extracted data keys: {list(self.extracted_data.keys()) if self.extracted_data else 'None'}")
                except:
                    pass
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.tests_run += 1
            return False

    def test_aml_kyc_verification(self):
        """Test AML/KYC verification"""
        if not self.application_id:
            print("❌ Skipping AML/KYC verification - no application ID available")
            return False
            
        test_data = {
            "applicationId": self.application_id,
            "personalInfo": {
                "firstName": "John",
                "lastName": "Doe", 
                "email": "john.doe@test.com",
                "phone": "+1-555-0123",
                "dateOfBirth": "1990-05-15",
                "nationality": "US",
                "address": "123 Test Street",
                "city": "Test City",
                "postalCode": "12345",
                "country": "United States"
            },
            "extractedData": self.extracted_data
        }
        
        success, response = self.run_test(
            "AML/KYC Verification",
            "POST",
            "api/registration/aml-kyc-check",
            200,
            data=test_data
        )
        
        if success:
            risk_score = response.get("riskScore", "N/A")
            status = response.get("status", "N/A")
            print(f"   Status: {status}, Risk Score: {risk_score}")
        
        return success

    def test_application_finalization(self):
        """Test application finalization"""
        if not self.application_id:
            print("❌ Skipping application finalization - no application ID available")
            return False
            
        test_data = {
            "applicationId": self.application_id,
            "approved": True
        }
        
        success, response = self.run_test(
            "Application Finalization",
            "POST",
            "api/registration/finalize",
            200,
            data=test_data
        )
        
        if success:
            credentials = response.get("credentials", {})
            username = credentials.get("username", "N/A")
            print(f"   New user created: {username}")
        
        return success

    def test_admin_pending_applications(self):
        """Test admin pending applications endpoint"""
        success, response = self.run_test(
            "Admin Pending Applications",
            "GET",
            "api/admin/pending-applications",
            200
        )
        
        if success:
            applications = response.get("applications", [])
            print(f"   Pending applications: {len(applications)}")
        
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
    
    # Test registration endpoints
    print("\n📋 REGISTRATION ENDPOINTS TESTS")
    print("-" * 30)
    tester.test_registration_create_application()
    tester.test_document_processing()
    tester.test_aml_kyc_verification()
    tester.test_application_finalization()
    tester.test_admin_pending_applications()
    
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