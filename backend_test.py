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