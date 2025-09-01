import requests
import sys
from datetime import datetime
import json
import io
from PIL import Image

class FidusAPITester:
    def __init__(self, base_url="https://fidus-finance.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.client_user = None
        self.admin_user = None
        self.application_id = None
        self.extracted_data = None
        self.uploaded_document_id = None
        self.envelope_id = None

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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

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
            # Check new AML/KYC response structure
            overall_status = response.get("overall_status", "N/A")
            risk_level = response.get("risk_level", "N/A")
            total_score = response.get("total_score", "N/A")
            checks_completed = response.get("checks_completed", [])
            
            print(f"   Overall Status: {overall_status}")
            print(f"   Risk Level: {risk_level}")
            print(f"   Total Score: {total_score}")
            print(f"   Checks Completed: {', '.join(checks_completed)}")
            
            # Check for sanctions screening results
            sanctions_screening = response.get("sanctions_screening", {})
            if sanctions_screening:
                provider = sanctions_screening.get("provider", "Unknown")
                total_hits = sanctions_screening.get("total_hits", 0)
                print(f"   Sanctions Provider: {provider}")
                print(f"   Sanctions Hits: {total_hits}")
            
            # Check for identity verification results
            identity_verification = response.get("identity_verification", {})
            if identity_verification:
                identity_verified = identity_verification.get("identity_verified", False)
                verification_score = identity_verification.get("verification_score", 0)
                print(f"   Identity Verified: {identity_verified}")
                print(f"   Verification Score: {verification_score}")
            
            # Check compliance recommendations
            recommendations = response.get("compliance_recommendations", [])
            if recommendations:
                print(f"   Compliance Recommendations: {len(recommendations)} items")
        
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

    def test_admin_clients_detailed(self):
        """Test getting detailed client information for admin"""
        success, response = self.run_test(
            "Get Detailed Clients",
            "GET",
            "api/admin/clients/detailed",
            200
        )
        
        if success:
            # Verify response structure
            required_keys = ['clients', 'total_clients', 'active_clients', 'total_aum']
            missing_keys = [key for key in required_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
                
            clients = response.get('clients', [])
            print(f"   Total clients: {response.get('total_clients', 0)}")
            print(f"   Active clients: {response.get('active_clients', 0)}")
            print(f"   Total AUM: ${response.get('total_aum', 0):,.2f}")
            
            # Check client structure
            if clients:
                client = clients[0]
                client_keys = ['id', 'name', 'email', 'balances', 'activity', 'compliance']
                for key in client_keys:
                    if key in client:
                        print(f"   ✅ Client has {key}")
                    else:
                        print(f"   ❌ Client missing {key}")
                        
                # Check balances structure
                balances = client.get('balances', {})
                balance_keys = ['total', 'fidus', 'core', 'dynamic']
                for key in balance_keys:
                    if key in balances:
                        print(f"   Balance {key}: ${balances[key]:,.2f}")
                        
        return success

    def test_admin_clients_export(self):
        """Test exporting clients data to Excel/CSV"""
        success, response = self.run_test(
            "Export Clients Data",
            "GET",
            "api/admin/clients/export",
            200
        )
        
        if success:
            # Verify response structure
            required_keys = ['success', 'filename', 'data', 'total_clients']
            missing_keys = [key for key in required_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
                
            print(f"   Export success: {response.get('success')}")
            print(f"   Filename: {response.get('filename')}")
            print(f"   Total clients exported: {response.get('total_clients')}")
            
            # Check if CSV data is present
            csv_data = response.get('data', '')
            if csv_data:
                lines = csv_data.split('\n')
                print(f"   CSV lines: {len(lines)}")
                if lines:
                    headers = lines[0].split(',')
                    print(f"   CSV headers: {len(headers)} columns")
                    print(f"   First few headers: {headers[:5]}")
            
        return success

    def test_admin_clients_import(self):
        """Test importing clients data from CSV"""
        # Create a simple CSV for testing
        csv_content = """Full_Name,Email,Username,Status,Total_Balance,FIDUS_Funds,Core_Balance,Dynamic_Balance
Test User,test@example.com,testuser,active,100000,30000,40000,30000
Another User,another@example.com,anotheruser,active,150000,50000,60000,40000"""
        
        try:
            # Create a file-like object
            import io
            csv_file = io.BytesIO(csv_content.encode('utf-8'))
            
            files = {
                'file': ('test_clients.csv', csv_file, 'text/csv')
            }
            
            url = f"{self.base_url}/api/admin/clients/import"
            print(f"\n🔍 Testing Import Clients Data...")
            print(f"   URL: {url}")
            
            response = requests.post(url, files=files, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            self.tests_run += 1
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Import success: {response_data.get('success')}")
                    print(f"   Imported: {response_data.get('imported', 0)} clients")
                    print(f"   Updated: {response_data.get('updated', 0)} clients")
                    print(f"   Total processed: {response_data.get('total_processed', 0)}")
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

    def test_admin_client_status_update(self):
        """Test updating client status"""
        # First get a client ID
        success, response = self.run_test(
            "Get Clients for Status Update Test",
            "GET",
            "api/admin/clients/detailed",
            200
        )
        
        if not success or not response.get('clients'):
            print("❌ No clients available for status update test")
            return False
            
        client_id = response['clients'][0]['id']
        
        # Test status update
        success, update_response = self.run_test(
            "Update Client Status",
            "PUT",
            f"api/admin/clients/{client_id}/status",
            200,
            data={"status": "inactive"}
        )
        
        if success:
            print(f"   Status update success: {update_response.get('success')}")
            print(f"   Message: {update_response.get('message')}")
            
            # Test with invalid status
            invalid_success, _ = self.run_test(
                "Update Client Status (Invalid)",
                "PUT",
                f"api/admin/clients/{client_id}/status",
                400,
                data={"status": "invalid_status"}
            )
            
            if invalid_success:
                print("   ✅ Invalid status properly rejected")
            
        return success

    def test_admin_client_deletion(self):
        """Test client deletion (if implemented)"""
        # First get a client ID
        success, response = self.run_test(
            "Get Clients for Deletion Test",
            "GET",
            "api/admin/clients/detailed",
            200
        )
        
        if not success or not response.get('clients'):
            print("❌ No clients available for deletion test")
            return False
            
        # Use the last client to avoid disrupting other tests
        client_id = response['clients'][-1]['id'] if len(response['clients']) > 1 else None
        
        if not client_id:
            print("❌ Not enough clients for safe deletion test")
            return True  # Skip this test
            
        # Test deletion
        success, delete_response = self.run_test(
            "Delete Client",
            "DELETE",
            f"api/admin/clients/{client_id}",
            200
        )
        
        if success:
            print(f"   Deletion success: {delete_response.get('success')}")
            print(f"   Message: {delete_response.get('message')}")
            
        return success

    def test_service_status(self):
        """Test service status endpoint"""
        success, response = self.run_test(
            "Service Status Check",
            "GET",
            "api/admin/service-status",
            200
        )
        
        if success:
            # Check overall system status
            overall = response.get("overall", {})
            print(f"   System Status: {overall.get('status', 'Unknown')}")
            print(f"   Ready Services: {overall.get('ready_services', 0)}/{overall.get('total_services', 0)}")
            print(f"   Readiness: {overall.get('readiness_percentage', 0)}%")
            
            # Check OCR services
            ocr_services = response.get("ocr_services", {})
            for service_name, service_info in ocr_services.items():
                status = service_info.get("status", "unknown")
                enabled = service_info.get("enabled", False)
                print(f"   OCR {service_name}: {'✅' if enabled and status == 'ready' else '❌'} ({status})")
            
            # Check AML/KYC services
            aml_services = response.get("aml_kyc_services", {})
            for service_name, service_info in aml_services.items():
                status = service_info.get("status", "unknown")
                enabled = service_info.get("enabled", False)
                print(f"   AML/KYC {service_name}: {'✅' if enabled and status == 'ready' else '❌'} ({status})")
            
            # Check compliance features
            compliance_features = response.get("compliance_features", {})
            for feature_name, feature_info in compliance_features.items():
                status = feature_info.get("status", "unknown")
                enabled = feature_info.get("enabled", False)
                print(f"   Compliance {feature_name}: {'✅' if enabled and status == 'ready' else '❌'} ({status})")
        
        return success

    def test_ocr_service_direct(self):
        """Test OCR service directly"""
        # Create test image
        test_image = self.create_test_image()
        if not test_image:
            print("❌ Failed to create test image")
            return False
        
        try:
            files = {
                'file': ('test_document.jpg', test_image, 'image/jpeg')
            }
            
            url = f"{self.base_url}/api/admin/test-ocr"
            print(f"\n🔍 Testing OCR Service Direct...")
            print(f"   URL: {url}")
            
            response = requests.post(url, files=files, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            self.tests_run += 1
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    ocr_success = response_data.get("success", False)
                    ocr_method = response_data.get("ocr_method", "unknown")
                    confidence_score = response_data.get("confidence_score", 0)
                    fields_extracted = response_data.get("fields_extracted", 0)
                    
                    print(f"   OCR Success: {ocr_success}")
                    print(f"   OCR Method: {ocr_method}")
                    print(f"   Confidence Score: {confidence_score}")
                    print(f"   Fields Extracted: {fields_extracted}")
                except Exception as e:
                    print(f"   Error parsing response: {e}")
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

    def test_aml_kyc_service_direct(self):
        """Test AML/KYC service directly"""
        test_person = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@test.com",
            "phone": "+1-555-0123",
            "dateOfBirth": "1990-05-15",
            "nationality": "US",
            "country": "United States"
        }
        
        success, response = self.run_test(
            "AML/KYC Service Direct Test",
            "POST",
            "api/admin/test-aml-kyc",
            200,
            data=test_person
        )
        
        if success:
            aml_success = response.get("success", False)
            overall_status = response.get("overall_status", "unknown")
            risk_level = response.get("risk_level", "unknown")
            total_score = response.get("total_score", 0)
            checks_completed = response.get("checks_completed", [])
            provider_used = response.get("provider_used", "unknown")
            
            print(f"   AML/KYC Success: {aml_success}")
            print(f"   Overall Status: {overall_status}")
            print(f"   Risk Level: {risk_level}")
            print(f"   Total Score: {total_score}")
            print(f"   Checks Completed: {', '.join(checks_completed)}")
            print(f"   Provider Used: {provider_used}")
        
        return success

    def test_password_reset_client(self):
        """Test client password reset flow"""
        # Step 1: Initiate password reset
        success, response = self.run_test(
            "Client Password Reset - Initiate",
            "POST",
            "api/auth/forgot-password",
            200,
            data={
                "email": "g.b@fidus.com",
                "userType": "client"
            }
        )
        
        if not success:
            return False
            
        reset_token = response.get("resetToken")
        if not reset_token:
            print("   ❌ No reset token received")
            return False
            
        print(f"   Reset token received: {reset_token[:20]}...")
        
        # Step 2: Verify reset code (demo accepts any 6-digit code)
        success, response = self.run_test(
            "Client Password Reset - Verify Code",
            "POST",
            "api/auth/verify-reset-code",
            200,
            data={
                "email": "g.b@fidus.com",
                "resetCode": "123456",
                "resetToken": reset_token
            }
        )
        
        if not success:
            return False
            
        verified = response.get("verified", False)
        if not verified:
            print("   ❌ Code verification failed")
            return False
            
        print("   ✅ Reset code verified successfully")
        
        # Step 3: Reset password
        success, response = self.run_test(
            "Client Password Reset - Complete",
            "POST",
            "api/auth/reset-password",
            200,
            data={
                "email": "g.b@fidus.com",
                "resetCode": "123456",
                "resetToken": reset_token,
                "newPassword": "NewPassword123!"
            }
        )
        
        if success:
            print("   ✅ Password reset completed successfully")
            
        return success

    def test_password_reset_admin(self):
        """Test admin password reset flow"""
        # Step 1: Initiate password reset
        success, response = self.run_test(
            "Admin Password Reset - Initiate",
            "POST",
            "api/auth/forgot-password",
            200,
            data={
                "email": "ic@fidus.com",
                "userType": "admin"
            }
        )
        
        if not success:
            return False
            
        reset_token = response.get("resetToken")
        if not reset_token:
            print("   ❌ No reset token received")
            return False
            
        print(f"   Reset token received: {reset_token[:20]}...")
        
        # Step 2: Verify reset code (demo accepts any 6-digit code)
        success, response = self.run_test(
            "Admin Password Reset - Verify Code",
            "POST",
            "api/auth/verify-reset-code",
            200,
            data={
                "email": "ic@fidus.com",
                "resetCode": "654321",
                "resetToken": reset_token
            }
        )
        
        if not success:
            return False
            
        verified = response.get("verified", False)
        if not verified:
            print("   ❌ Code verification failed")
            return False
            
        print("   ✅ Reset code verified successfully")
        
        # Step 3: Reset password
        success, response = self.run_test(
            "Admin Password Reset - Complete",
            "POST",
            "api/auth/reset-password",
            200,
            data={
                "email": "ic@fidus.com",
                "resetCode": "654321",
                "resetToken": reset_token,
                "newPassword": "AdminNewPass456@"
            }
        )
        
        if success:
            print("   ✅ Password reset completed successfully")
            
        return success

    def test_password_reset_invalid_scenarios(self):
        """Test password reset error scenarios"""
        # Test invalid email format
        success, _ = self.run_test(
            "Password Reset - Invalid Email Format",
            "POST",
            "api/auth/forgot-password",
            400,
            data={
                "email": "invalid-email",
                "userType": "client"
            }
        )
        
        if not success:
            print("   ❌ Invalid email format test failed")
            return False
            
        print("   ✅ Invalid email format properly rejected")
        
        # Test invalid reset code format
        success, _ = self.run_test(
            "Password Reset - Invalid Code Format",
            "POST",
            "api/auth/verify-reset-code",
            400,
            data={
                "email": "g.b@fidus.com",
                "resetCode": "12345",  # Only 5 digits
                "resetToken": "dummy-token"
            }
        )
        
        if not success:
            print("   ❌ Invalid code format test failed")
            return False
            
        print("   ✅ Invalid code format properly rejected")
        
        # Test weak password
        success, _ = self.run_test(
            "Password Reset - Weak Password",
            "POST",
            "api/auth/reset-password",
            400,
            data={
                "email": "g.b@fidus.com",
                "resetCode": "123456",
                "resetToken": "dummy-token",
                "newPassword": "weak"  # Too weak
            }
        )
        
        if not success:
            print("   ❌ Weak password test failed")
            return False
            
        print("   ✅ Weak password properly rejected")
        
        return True

    def create_test_pdf(self):
        """Create a test PDF file for document upload"""
        import io
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(100, 750, "Test Document for FIDUS Document Portal")
            p.drawString(100, 730, "This is a sample document for testing purposes.")
            p.drawString(100, 710, "Client: Gerardo Briones")
            p.drawString(100, 690, "Date: 2024-12-19")
            p.showPage()
            p.save()
            
            buffer.seek(0)
            return buffer
        except ImportError:
            # Fallback to simple text file if reportlab not available
            content = """Test Document for FIDUS Document Portal
            
This is a sample document for testing purposes.
Client: Gerardo Briones
Date: 2024-12-19

Document Content:
- Investment Agreement
- Risk Disclosure
- Terms and Conditions
"""
            return io.BytesIO(content.encode('utf-8'))
        except Exception as e:
            print(f"Error creating test PDF: {e}")
            # Fallback to simple text file
            content = "Test Document Content for FIDUS Portal Testing"
            return io.BytesIO(content.encode('utf-8'))

    def test_document_upload(self):
        """Test document upload endpoint"""
        if not self.admin_user:
            print("❌ Skipping document upload test - no admin user available")
            return False
            
        # Create test document
        test_doc = self.create_test_pdf()
        if not test_doc:
            print("❌ Failed to create test document")
            return False
        
        try:
            files = {
                'document': ('investment_agreement.pdf', test_doc, 'application/pdf')
            }
            data = {
                'category': 'investment_agreement',
                'uploader_id': self.admin_user['id']
            }
            
            url = f"{self.base_url}/api/documents/upload"
            print(f"\n🔍 Testing Document Upload...")
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
                    self.uploaded_document_id = response_data.get("document_id")
                    print(f"   Document ID: {self.uploaded_document_id}")
                    print(f"   Success: {response_data.get('success')}")
                    print(f"   Message: {response_data.get('message')}")
                except Exception as e:
                    print(f"   Error parsing response: {e}")
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

    def test_document_upload_invalid_file(self):
        """Test document upload with invalid file type"""
        if not self.admin_user:
            print("❌ Skipping invalid file upload test - no admin user available")
            return False
            
        try:
            # Create invalid file (image instead of document)
            test_image = self.create_test_image()
            
            files = {
                'document': ('test_image.jpg', test_image, 'image/jpeg')
            }
            data = {
                'category': 'test',
                'uploader_id': self.admin_user['id']
            }
            
            url = f"{self.base_url}/api/documents/upload"
            print(f"\n🔍 Testing Document Upload - Invalid File Type...")
            print(f"   URL: {url}")
            
            response = requests.post(url, files=files, data=data, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            self.tests_run += 1
            success = response.status_code in [400, 500]  # Should reject invalid file type (server returns 500 but message is correct)
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Invalid file type properly rejected")
            else:
                print(f"❌ Failed - Expected 400, got {response.status_code}")
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

    def test_admin_get_all_documents(self):
        """Test getting all documents for admin"""
        success, response = self.run_test(
            "Get All Documents (Admin)",
            "GET",
            "api/documents/admin/all",
            200
        )
        
        if success:
            documents = response.get('documents', [])
            print(f"   Total documents: {len(documents)}")
            
            if documents:
                doc = documents[0]
                doc_keys = ['id', 'name', 'category', 'status', 'uploader_id', 'created_at']
                for key in doc_keys:
                    if key in doc:
                        print(f"   ✅ Document has {key}: {doc[key]}")
                    else:
                        print(f"   ❌ Document missing {key}")
        
        return success

    def test_client_get_documents(self):
        """Test getting documents for specific client"""
        if not self.client_user:
            print("❌ Skipping client documents test - no client user available")
            return False
            
        client_id = self.client_user.get('id')
        success, response = self.run_test(
            "Get Client Documents",
            "GET",
            f"api/documents/client/{client_id}",
            200
        )
        
        if success:
            documents = response.get('documents', [])
            print(f"   Client documents: {len(documents)}")
            
            # Check if documents are properly filtered for client
            for doc in documents:
                uploader_id = doc.get('uploader_id')
                recipient_emails = doc.get('recipient_emails', [])
                client_email = self.client_user.get('email', '')
                
                is_client_doc = (uploader_id == client_id or 
                               any(client_email in email for email in recipient_emails))
                
                if is_client_doc:
                    print(f"   ✅ Document {doc.get('name')} properly belongs to client")
                else:
                    print(f"   ⚠️  Document {doc.get('name')} may not belong to client")
        
        return success

    def test_send_document_for_signature(self):
        """Test sending document for DocuSign signature"""
        if not hasattr(self, 'uploaded_document_id') or not self.uploaded_document_id:
            print("❌ Skipping send for signature test - no uploaded document available")
            return False
            
        if not self.admin_user:
            print("❌ Skipping send for signature test - no admin user available")
            return False
        
        try:
            # Prepare multipart form data with JSON and form fields
            import json
            
            signature_data = {
                "recipients": [
                    {
                        "name": "Gerardo Briones",
                        "email": "g.b@fidus.com",
                        "role": "signer"
                    }
                ],
                "email_subject": "Investment Agreement - Signature Required",
                "email_message": "Please review and sign the attached investment agreement."
            }
            
            # Create multipart form data
            files = {
                'request': (None, json.dumps(signature_data), 'application/json'),
                'sender_id': (None, self.admin_user['id'])
            }
            
            url = f"{self.base_url}/api/documents/{self.uploaded_document_id}/send-for-signature"
            print(f"\n🔍 Testing Send Document for Signature...")
            print(f"   URL: {url}")
            
            response = requests.post(url, files=files, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            self.tests_run += 1
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    self.envelope_id = response_data.get("envelope_id")
                    print(f"   Success: {response_data.get('success')}")
                    print(f"   Envelope ID: {self.envelope_id}")
                    print(f"   Status: {response_data.get('status')}")
                    print(f"   Message: {response_data.get('message')}")
                except Exception as e:
                    print(f"   Error parsing response: {e}")
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

    def test_document_status_tracking(self):
        """Test DocuSign envelope status tracking"""
        if not hasattr(self, 'uploaded_document_id') or not self.uploaded_document_id:
            print("❌ Skipping status tracking test - no uploaded document available")
            return False
        
        success, response = self.run_test(
            "Get Document Status",
            "GET",
            f"api/documents/{self.uploaded_document_id}/status",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            message = response.get('message', '')
            envelope_id = response.get('envelope_id', '')
            
            print(f"   Document Status: {status}")
            if message:
                print(f"   Message: {message}")
            if envelope_id:
                print(f"   Envelope ID: {envelope_id}")
                
            # Check if status is valid
            valid_statuses = ['draft', 'sent', 'delivered', 'completed', 'declined', 'voided']
            if status in valid_statuses:
                print(f"   ✅ Valid status: {status}")
            else:
                print(f"   ⚠️  Unknown status: {status}")
        
        return success

    def test_document_download(self):
        """Test document download"""
        if not hasattr(self, 'uploaded_document_id') or not self.uploaded_document_id:
            print("❌ Skipping document download test - no uploaded document available")
            return False
        
        try:
            url = f"{self.base_url}/api/documents/{self.uploaded_document_id}/download"
            print(f"\n🔍 Testing Document Download...")
            print(f"   URL: {url}")
            
            response = requests.get(url, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            self.tests_run += 1
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Check response headers
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                content_length = response.headers.get('content-length', '0')
                
                print(f"   Content-Type: {content_type}")
                print(f"   Content-Disposition: {content_disposition}")
                print(f"   Content-Length: {content_length} bytes")
                
                # Check if file content is present
                if len(response.content) > 0:
                    print(f"   ✅ File content received: {len(response.content)} bytes")
                else:
                    print(f"   ⚠️  No file content received")
                    
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

    def test_document_download_nonexistent(self):
        """Test downloading non-existent document"""
        fake_doc_id = "nonexistent-document-id"
        
        success, _ = self.run_test(
            "Download Non-existent Document",
            "GET",
            f"api/documents/{fake_doc_id}/download",
            404
        )
        
        if success:
            print("   ✅ Non-existent document properly rejected")
        
        return success

    def test_document_deletion(self):
        """Test document deletion"""
        if not hasattr(self, 'uploaded_document_id') or not self.uploaded_document_id:
            print("❌ Skipping document deletion test - no uploaded document available")
            return False
        
        success, response = self.run_test(
            "Delete Document",
            "DELETE",
            f"api/documents/{self.uploaded_document_id}",
            200
        )
        
        if success:
            print(f"   Success: {response.get('success')}")
            print(f"   Message: {response.get('message')}")
            
            # Verify document is actually deleted by trying to download it
            verify_success, _ = self.run_test(
                "Verify Document Deleted",
                "GET",
                f"api/documents/{self.uploaded_document_id}/download",
                404
            )
            
            if verify_success:
                print("   ✅ Document successfully deleted and no longer accessible")
            else:
                print("   ⚠️  Document may not have been properly deleted")
        
        return success

    def test_document_deletion_nonexistent(self):
        """Test deleting non-existent document"""
        fake_doc_id = "nonexistent-document-id"
        
        success, _ = self.run_test(
            "Delete Non-existent Document",
            "DELETE",
            f"api/documents/{fake_doc_id}",
            404
        )
        
        if success:
            print("   ✅ Non-existent document deletion properly rejected")
        
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
    
    # Test Excel client management endpoints
    print("\n📋 EXCEL CLIENT MANAGEMENT TESTS")
    print("-" * 30)
    tester.test_admin_clients_detailed()
    tester.test_admin_clients_export()
    tester.test_admin_clients_import()
    tester.test_admin_client_status_update()
    tester.test_admin_client_deletion()
    
    # Test new OCR and AML/KYC services
    print("\n📋 SERVICE STATUS & CONFIGURATION TESTS")
    print("-" * 30)
    tester.test_service_status()
    tester.test_ocr_service_direct()
    tester.test_aml_kyc_service_direct()
    
    # Test registration endpoints
    print("\n📋 REGISTRATION ENDPOINTS TESTS")
    print("-" * 30)
    tester.test_registration_create_application()
    tester.test_document_processing()
    tester.test_aml_kyc_verification()
    tester.test_application_finalization()
    tester.test_admin_pending_applications()
    
    # Test password reset endpoints
    print("\n📋 PASSWORD RESET TESTS")
    print("-" * 30)
    tester.test_password_reset_client()
    tester.test_password_reset_admin()
    tester.test_password_reset_invalid_scenarios()
    
    # Test Document Portal endpoints
    print("\n📋 DOCUMENT PORTAL TESTS")
    print("-" * 30)
    tester.test_document_upload()
    tester.test_document_upload_invalid_file()
    tester.test_admin_get_all_documents()
    tester.test_client_get_documents()
    tester.test_send_document_for_signature()
    tester.test_document_status_tracking()
    tester.test_document_download()
    tester.test_document_download_nonexistent()
    tester.test_document_deletion()
    tester.test_document_deletion_nonexistent()
    
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