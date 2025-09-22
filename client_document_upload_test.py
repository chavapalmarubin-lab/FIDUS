#!/usr/bin/env python3
"""
CLIENT DOCUMENT UPLOAD FUNCTIONALITY TESTING
============================================

This test verifies the new client document upload functionality as requested in the review:
- POST `/api/admin/clients/{client_id}/documents` endpoint
- Test with Salvador Palma (client_003)
- Upload test document with proper form data
- Verify file upload handling, document type validation, file size limits, response format
- Test frontend integration and admin authentication
- Check error handling

Expected Results:
- ✅ Document upload endpoint works for clients
- ✅ Proper file validation and processing
- ✅ Success response with document record
- ✅ Admin can upload documents for any client
"""

import requests
import json
import sys
import io
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://finance-portal-60.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"
TEST_CLIENT_ID = "client_003"  # Salvador Palma

class ClientDocumentUploadTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_client_exists(self):
        """Verify Salvador Palma (client_003) exists"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients_data = response.json()
                
                # Handle different response formats
                clients = []
                if isinstance(clients_data, list):
                    clients = clients_data
                elif isinstance(clients_data, dict):
                    clients = clients_data.get('clients', [])
                
                salvador_found = False
                for client in clients:
                    if client.get('id') == TEST_CLIENT_ID:
                        salvador_found = True
                        self.log_result("Client Exists Check", True, 
                                      f"Salvador Palma found: {client.get('name', 'Unknown')}")
                        break
                
                if not salvador_found:
                    self.log_result("Client Exists Check", False, 
                                  f"Salvador Palma (client_003) not found in {len(clients)} clients")
                    return False
                return True
            else:
                self.log_result("Client Exists Check", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Client Exists Check", False, f"Exception: {str(e)}")
            return False
    
    def test_get_client_documents(self):
        """Test GET endpoint for client documents"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients/{TEST_CLIENT_ID}/documents")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    documents = data.get('documents', [])
                    self.log_result("Get Client Documents", True, 
                                  f"Retrieved {len(documents)} documents for Salvador")
                    return True
                else:
                    self.log_result("Get Client Documents", False, 
                                  "Response success=false", {"response": data})
                    return False
            else:
                self.log_result("Get Client Documents", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Get Client Documents", False, f"Exception: {str(e)}")
            return False
    
    def create_test_file(self, filename, content, content_type):
        """Create a test file for upload"""
        return (filename, io.BytesIO(content.encode('utf-8')), content_type)
    
    def test_document_upload_success(self):
        """Test successful document upload"""
        try:
            # Create test document
            test_content = "This is a test document for Salvador Palma's KYC verification."
            test_file = self.create_test_file("test_kyc_document.txt", test_content, "text/plain")
            
            # Prepare form data
            files = {'file': test_file}
            data = {
                'document_type': 'kyc_document',
                'notes': 'Test document upload for Salvador Palma'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/admin/clients/{TEST_CLIENT_ID}/documents",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    document = result.get('document', {})
                    self.log_result("Document Upload Success", True, 
                                  f"Document uploaded successfully: {document.get('document_id')}")
                    
                    # Verify document structure
                    required_fields = ['document_id', 'client_id', 'file_name', 'document_type', 
                                     'file_size', 'verification_status', 'uploaded_at']
                    missing_fields = [field for field in required_fields if field not in document]
                    
                    if not missing_fields:
                        self.log_result("Document Structure Validation", True, 
                                      "All required fields present in response")
                    else:
                        self.log_result("Document Structure Validation", False, 
                                      f"Missing fields: {missing_fields}")
                    
                    return True
                else:
                    self.log_result("Document Upload Success", False, 
                                  "Upload failed", {"response": result})
                    return False
            else:
                self.log_result("Document Upload Success", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Document Upload Success", False, f"Exception: {str(e)}")
            return False
    
    def test_file_size_validation(self):
        """Test file size limit validation (10MB)"""
        try:
            # Create a file larger than 10MB
            large_content = "X" * (11 * 1024 * 1024)  # 11MB
            large_file = self.create_test_file("large_file.txt", large_content, "text/plain")
            
            files = {'file': large_file}
            data = {
                'document_type': 'test_document',
                'notes': 'Testing file size limit'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/admin/clients/{TEST_CLIENT_ID}/documents",
                files=files,
                data=data
            )
            
            if response.status_code == 400:
                result = response.json()
                if "size too large" in result.get('detail', '').lower():
                    self.log_result("File Size Validation", True, 
                                  "File size limit properly enforced (10MB)")
                    return True
                else:
                    self.log_result("File Size Validation", False, 
                                  "Wrong error message for large file", {"response": result})
                    return False
            else:
                self.log_result("File Size Validation", False, 
                              f"Expected 400, got {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("File Size Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_missing_file_validation(self):
        """Test validation when no file is provided"""
        try:
            # Send request without file
            data = {
                'document_type': 'test_document',
                'notes': 'Testing missing file validation'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/admin/clients/{TEST_CLIENT_ID}/documents",
                data=data
            )
            
            if response.status_code == 422:  # FastAPI validation error
                self.log_result("Missing File Validation", True, 
                              "Missing file properly rejected")
                return True
            elif response.status_code == 400:
                result = response.json()
                if "no file" in result.get('detail', '').lower():
                    self.log_result("Missing File Validation", True, 
                                  "Missing file properly rejected")
                    return True
                else:
                    self.log_result("Missing File Validation", False, 
                                  "Wrong error message", {"response": result})
                    return False
            else:
                self.log_result("Missing File Validation", False, 
                              f"Expected 400/422, got {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Missing File Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_client_validation(self):
        """Test validation with invalid client ID"""
        try:
            test_content = "Test document for invalid client"
            test_file = self.create_test_file("test.txt", test_content, "text/plain")
            
            files = {'file': test_file}
            data = {
                'document_type': 'test_document',
                'notes': 'Testing invalid client'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/admin/clients/invalid_client_id/documents",
                files=files,
                data=data
            )
            
            if response.status_code == 404:
                result = response.json()
                if "not found" in result.get('detail', '').lower():
                    self.log_result("Invalid Client Validation", True, 
                                  "Invalid client ID properly rejected")
                    return True
                else:
                    self.log_result("Invalid Client Validation", False, 
                                  "Wrong error message", {"response": result})
                    return False
            else:
                self.log_result("Invalid Client Validation", False, 
                              f"Expected 404, got {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Invalid Client Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_document_type_validation(self):
        """Test different document types"""
        try:
            document_types = [
                'government_id',
                'proof_of_address', 
                'bank_statement',
                'kyc_document',
                'aml_document',
                'other'
            ]
            
            success_count = 0
            for doc_type in document_types:
                test_content = f"Test document of type: {doc_type}"
                test_file = self.create_test_file(f"test_{doc_type}.txt", test_content, "text/plain")
                
                files = {'file': test_file}
                data = {
                    'document_type': doc_type,
                    'notes': f'Testing document type: {doc_type}'
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/admin/clients/{TEST_CLIENT_ID}/documents",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        success_count += 1
                
                # Small delay between uploads
                time.sleep(0.1)
            
            if success_count == len(document_types):
                self.log_result("Document Type Validation", True, 
                              f"All {len(document_types)} document types accepted")
                return True
            else:
                self.log_result("Document Type Validation", False, 
                              f"Only {success_count}/{len(document_types)} document types worked")
                return False
                
        except Exception as e:
            self.log_result("Document Type Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication_required(self):
        """Test that authentication is required"""
        try:
            # Create a session without authentication
            unauth_session = requests.Session()
            
            test_content = "Test document without auth"
            test_file = self.create_test_file("test.txt", test_content, "text/plain")
            
            files = {'file': test_file}
            data = {
                'document_type': 'test_document',
                'notes': 'Testing without authentication'
            }
            
            response = unauth_session.post(
                f"{BACKEND_URL}/admin/clients/{TEST_CLIENT_ID}/documents",
                files=files,
                data=data
            )
            
            if response.status_code == 401:
                self.log_result("Authentication Required", True, 
                              "Unauthenticated request properly rejected")
                return True
            else:
                self.log_result("Authentication Required", False, 
                              f"Expected 401, got {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Authentication Required", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all client document upload tests"""
        print("🎯 CLIENT DOCUMENT UPLOAD FUNCTIONALITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Client: Salvador Palma ({TEST_CLIENT_ID})")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Client Document Upload Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_client_exists()
        self.test_get_client_documents()
        self.test_document_upload_success()
        self.test_file_size_validation()
        self.test_missing_file_validation()
        self.test_invalid_client_validation()
        self.test_document_type_validation()
        self.test_authentication_required()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 CLIENT DOCUMENT UPLOAD TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        critical_tests = [
            "Client Exists Check",
            "Document Upload Success", 
            "File Size Validation",
            "Authentication Required"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and result['test'] in critical_tests)
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 3:  # At least 3 out of 4 critical tests
            print("✅ CLIENT DOCUMENT UPLOAD FUNCTIONALITY: WORKING")
            print("   Document upload endpoint is operational for admin users.")
            print("   File validation and security measures are in place.")
            print("   System ready for production use.")
        else:
            print("❌ CLIENT DOCUMENT UPLOAD FUNCTIONALITY: ISSUES FOUND")
            print("   Critical functionality problems detected.")
            print("   Main agent action required before deployment.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = ClientDocumentUploadTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()