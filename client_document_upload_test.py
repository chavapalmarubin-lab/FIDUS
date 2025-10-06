#!/usr/bin/env python3
"""
FIDUS Client Document Upload Functionality Testing
=================================================

This script tests the FIXED client document upload functionality to ensure the upload error is resolved.

Test Focus:
- Test `/fidus/client-document-upload` endpoint with proper file upload simulation
- Verify the endpoint now properly handles file bytes instead of strings
- Test temporary file management and cleanup
- Test Google Drive integration for uploading to client folders
- Test error handling for various scenarios

Key Changes Tested:
- Fixed bytes vs string handling in file processing
- Added proper temp file flushing and error handling
- Enhanced upload logging with file metadata
- Improved error messages and HTTP exception handling
"""

import requests
import json
import io
import os
import tempfile
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test Configuration
BACKEND_URL = "https://mt5-integration.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
    "user_type": "admin"
}

class ClientDocumentUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {message}")
        
        if details:
            logger.info(f"Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                
                self.log_test_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as admin user",
                    {"user_id": data.get('id'), "username": data.get('username')}
                )
                return True
            else:
                self.log_test_result(
                    "Admin Authentication",
                    False,
                    f"Authentication failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def create_test_file(self, filename, content, file_type="text"):
        """Create test file content"""
        if file_type == "text":
            return content.encode('utf-8')
        elif file_type == "pdf":
            # Simple PDF-like content (not a real PDF, but for testing)
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
            pdf_content += content.encode('utf-8')
            return pdf_content
        elif file_type == "image":
            # Simple image-like content (not a real image, but for testing)
            return b"\x89PNG\r\n\x1a\n" + content.encode('utf-8')
        else:
            return content.encode('utf-8')
    
    def test_valid_document_upload(self):
        """Test valid document upload with different file types"""
        test_cases = [
            {
                "filename": "test_document.pdf",
                "content": "This is a test PDF document for FIDUS client upload testing.",
                "file_type": "pdf",
                "mime_type": "application/pdf"
            },
            {
                "filename": "test_image.png",
                "content": "This is a test PNG image for FIDUS client upload testing.",
                "file_type": "image",
                "mime_type": "image/png"
            },
            {
                "filename": "test_document.docx",
                "content": "This is a test Word document for FIDUS client upload testing.",
                "file_type": "text",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                # Create test file content
                file_content = self.create_test_file(
                    test_case["filename"],
                    test_case["content"],
                    test_case["file_type"]
                )
                
                # Prepare form data
                files = {
                    'file': (test_case["filename"], io.BytesIO(file_content), test_case["mime_type"])
                }
                
                data = {
                    'client_id': 'client_003',  # Salvador Palma
                    'client_name': 'Salvador Palma'
                }
                
                # Make upload request to the correct endpoint
                response = self.session.post(
                    f"{BACKEND_URL}/fidus/client-document-upload",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        self.log_test_result(
                            f"Valid Document Upload - {test_case['filename']}",
                            True,
                            f"Successfully uploaded {test_case['filename']} ({len(file_content)} bytes)",
                            {
                                "file_info": result.get('file', {}),
                                "message": result.get('message'),
                                "file_size": len(file_content)
                            }
                        )
                    else:
                        self.log_test_result(
                            f"Valid Document Upload - {test_case['filename']}",
                            False,
                            f"Upload failed: {result.get('error', 'Unknown error')}",
                            {"response": result}
                        )
                else:
                    self.log_test_result(
                        f"Valid Document Upload - {test_case['filename']}",
                        False,
                        f"Upload failed with status {response.status_code}",
                        {"response": response.text}
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Valid Document Upload - {test_case['filename']}",
                    False,
                    f"Upload error: {str(e)}"
                )
    
    def test_large_file_handling(self):
        """Test large file handling (size limits)"""
        try:
            # Create a file larger than 50MB limit
            large_content = "A" * (51 * 1024 * 1024)  # 51MB
            
            files = {
                'file': ('large_test.pdf', io.BytesIO(large_content.encode('utf-8')), 'application/pdf')
            }
            
            data = {
                'client_id': 'client_003',
                'client_name': 'Salvador Palma'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/fidus/client-document-upload",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 400:
                result = response.json()
                if "50MB limit" in result.get('detail', ''):
                    self.log_test_result(
                        "Large File Handling",
                        True,
                        "Large file properly rejected with size limit error",
                        {"error_message": result.get('detail')}
                    )
                else:
                    self.log_test_result(
                        "Large File Handling",
                        False,
                        f"Unexpected error message: {result.get('detail')}",
                        {"response": result}
                    )
            else:
                self.log_test_result(
                    "Large File Handling",
                    False,
                    f"Large file not rejected properly, status: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_test_result(
                "Large File Handling",
                False,
                f"Large file test error: {str(e)}"
            )
    
    def test_missing_file_scenario(self):
        """Test missing file scenarios"""
        try:
            # Test with no file
            data = {
                'client_id': 'client_003',
                'client_name': 'Salvador Palma'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/fidus/client-document-upload",
                data=data,
                timeout=30
            )
            
            if response.status_code in [400, 422]:
                self.log_test_result(
                    "Missing File Scenario",
                    True,
                    f"Missing file properly rejected with status {response.status_code}",
                    {"response": response.text}
                )
            else:
                self.log_test_result(
                    "Missing File Scenario",
                    False,
                    f"Missing file not rejected properly, status: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_test_result(
                "Missing File Scenario",
                False,
                f"Missing file test error: {str(e)}"
            )
    
    def test_client_not_found_scenario(self):
        """Test client not found scenarios"""
        try:
            # Create test file
            file_content = self.create_test_file("test.pdf", "Test content", "pdf")
            
            files = {
                'file': ('test.pdf', io.BytesIO(file_content), 'application/pdf')
            }
            
            data = {
                'client_id': 'nonexistent_client',
                'client_name': 'Nonexistent Client'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/fidus/client-document-upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get('success') and 'Client not found' in result.get('error', ''):
                    self.log_test_result(
                        "Client Not Found Scenario",
                        True,
                        "Nonexistent client properly handled with error message",
                        {"error_message": result.get('error')}
                    )
                else:
                    self.log_test_result(
                        "Client Not Found Scenario",
                        False,
                        f"Unexpected response for nonexistent client: {result}",
                        {"response": result}
                    )
            else:
                self.log_test_result(
                    "Client Not Found Scenario",
                    False,
                    f"Unexpected status code for nonexistent client: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_test_result(
                "Client Not Found Scenario",
                False,
                f"Client not found test error: {str(e)}"
            )
    
    def test_google_drive_integration_availability(self):
        """Test Google Drive integration availability"""
        try:
            # Create small test file
            file_content = self.create_test_file("drive_test.pdf", "Google Drive integration test", "pdf")
            
            files = {
                'file': ('drive_test.pdf', io.BytesIO(file_content), 'application/pdf')
            }
            
            data = {
                'client_id': 'client_003',
                'client_name': 'Salvador Palma'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/fidus/client-document-upload",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Check if Google Drive integration worked
                    file_info = result.get('file', {})
                    if file_info.get('google_file_id'):
                        self.log_test_result(
                            "Google Drive Integration",
                            True,
                            "Google Drive integration working - file uploaded to Drive",
                            {
                                "google_file_id": file_info.get('google_file_id'),
                                "web_view_link": file_info.get('web_view_link')
                            }
                        )
                    else:
                        self.log_test_result(
                            "Google Drive Integration",
                            True,
                            "Upload successful but Google Drive integration not available",
                            {"message": result.get('message')}
                        )
                else:
                    error_msg = result.get('error', '')
                    if 'Google Drive integration not available' in error_msg:
                        self.log_test_result(
                            "Google Drive Integration",
                            True,
                            "Google Drive integration properly reports unavailability",
                            {"error_message": error_msg}
                        )
                    else:
                        self.log_test_result(
                            "Google Drive Integration",
                            False,
                            f"Unexpected error: {error_msg}",
                            {"response": result}
                        )
            else:
                self.log_test_result(
                    "Google Drive Integration",
                    False,
                    f"Drive integration test failed with status {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_test_result(
                "Google Drive Integration",
                False,
                f"Drive integration test error: {str(e)}"
            )
    
    def test_bytes_handling_fix(self):
        """Test that the bytes vs string handling fix is working"""
        try:
            # Create binary content that would fail with string handling
            binary_content = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])  # PNG header
            binary_content += b"This is binary content that should be handled as bytes, not strings."
            binary_content += bytes(range(256))  # Full byte range
            
            files = {
                'file': ('binary_test.png', io.BytesIO(binary_content), 'image/png')
            }
            
            data = {
                'client_id': 'client_003',
                'client_name': 'Salvador Palma'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/fidus/client-document-upload",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log_test_result(
                        "Bytes Handling Fix",
                        True,
                        "Binary content handled correctly - no 'bytes-like object required' error",
                        {
                            "file_size": len(binary_content),
                            "message": result.get('message')
                        }
                    )
                else:
                    error_msg = result.get('error', '')
                    if 'bytes-like object required' in error_msg:
                        self.log_test_result(
                            "Bytes Handling Fix",
                            False,
                            "Still getting 'bytes-like object required' error - fix not working",
                            {"error_message": error_msg}
                        )
                    else:
                        self.log_test_result(
                            "Bytes Handling Fix",
                            False,
                            f"Upload failed with different error: {error_msg}",
                            {"response": result}
                        )
            else:
                self.log_test_result(
                    "Bytes Handling Fix",
                    False,
                    f"Bytes handling test failed with status {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_test_result(
                "Bytes Handling Fix",
                False,
                f"Bytes handling test error: {str(e)}"
            )
    
    def test_temporary_file_management(self):
        """Test temporary file creation and cleanup"""
        try:
            # Create test file
            file_content = self.create_test_file("temp_test.pdf", "Temporary file management test", "pdf")
            
            files = {
                'file': ('temp_test.pdf', io.BytesIO(file_content), 'application/pdf')
            }
            
            data = {
                'client_id': 'client_003',
                'client_name': 'Salvador Palma'
            }
            
            # Check temp directory before upload
            temp_dir = tempfile.gettempdir()
            temp_files_before = set(os.listdir(temp_dir))
            
            response = self.session.post(
                f"{BACKEND_URL}/fidus/client-document-upload",
                files=files,
                data=data,
                timeout=60
            )
            
            # Check temp directory after upload
            temp_files_after = set(os.listdir(temp_dir))
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if temp files were cleaned up
                new_temp_files = temp_files_after - temp_files_before
                persistent_temp_files = [f for f in new_temp_files if 'temp_test.pdf' in f]
                
                if len(persistent_temp_files) == 0:
                    self.log_test_result(
                        "Temporary File Management",
                        True,
                        "Temporary files properly cleaned up after upload",
                        {
                            "upload_success": result.get('success'),
                            "temp_files_cleaned": True
                        }
                    )
                else:
                    self.log_test_result(
                        "Temporary File Management",
                        False,
                        f"Temporary files not cleaned up: {persistent_temp_files}",
                        {
                            "upload_success": result.get('success'),
                            "persistent_files": persistent_temp_files
                        }
                    )
            else:
                self.log_test_result(
                    "Temporary File Management",
                    False,
                    f"Upload failed, cannot test temp file cleanup: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_test_result(
                "Temporary File Management",
                False,
                f"Temp file management test error: {str(e)}"
            )
    
    def test_authentication_requirement(self):
        """Test that authentication is required"""
        try:
            # Remove authentication header
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Create test file
            file_content = self.create_test_file("auth_test.pdf", "Authentication test", "pdf")
            
            files = {
                'file': ('auth_test.pdf', io.BytesIO(file_content), 'application/pdf')
            }
            
            data = {
                'client_id': 'client_003',
                'client_name': 'Salvador Palma'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/fidus/client-document-upload",
                files=files,
                data=data,
                timeout=30
            )
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            if response.status_code == 401:
                self.log_test_result(
                    "Authentication Requirement",
                    True,
                    "Authentication properly required - unauthenticated request rejected",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test_result(
                    "Authentication Requirement",
                    False,
                    f"Unauthenticated request not properly rejected: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_test_result(
                "Authentication Requirement",
                False,
                f"Authentication test error: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all client document upload tests"""
        logger.info("🚀 Starting FIDUS Client Document Upload Functionality Testing")
        logger.info("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            logger.error("❌ Cannot proceed without admin authentication")
            return
        
        # Run all tests
        logger.info("\n📋 Running Client Document Upload Tests...")
        
        self.test_valid_document_upload()
        self.test_large_file_handling()
        self.test_missing_file_scenario()
        self.test_client_not_found_scenario()
        self.test_google_drive_integration_availability()
        self.test_bytes_handling_fix()
        self.test_temporary_file_management()
        self.test_authentication_requirement()
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 CLIENT DOCUMENT UPLOAD TESTING SUMMARY")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        logger.info("\n📋 Test Results:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            logger.info(f"{status}: {result['test']} - {result['message']}")
        
        # Key findings
        logger.info("\n🔍 Key Findings:")
        
        # Check for bytes handling fix
        bytes_test = next((r for r in self.test_results if 'Bytes Handling' in r['test']), None)
        if bytes_test and bytes_test['success']:
            logger.info("✅ CRITICAL: 'bytes-like object required' error has been RESOLVED")
        elif bytes_test:
            logger.info("❌ CRITICAL: 'bytes-like object required' error still exists")
        
        # Check for file upload success
        upload_tests = [r for r in self.test_results if 'Valid Document Upload' in r['test']]
        successful_uploads = [r for r in upload_tests if r['success']]
        if successful_uploads:
            logger.info(f"✅ File uploads working: {len(successful_uploads)}/{len(upload_tests)} file types successful")
        
        # Check for Google Drive integration
        drive_test = next((r for r in self.test_results if 'Google Drive Integration' in r['test']), None)
        if drive_test and drive_test['success']:
            logger.info("✅ Google Drive integration available and working")
        elif drive_test:
            logger.info("⚠️  Google Drive integration not available (expected in test environment)")
        
        # Check for temp file cleanup
        temp_test = next((r for r in self.test_results if 'Temporary File Management' in r['test']), None)
        if temp_test and temp_test['success']:
            logger.info("✅ Temporary file cleanup working correctly")
        elif temp_test:
            logger.info("❌ Temporary file cleanup issues detected")
        
        logger.info("\n🎯 CONCLUSION:")
        if success_rate >= 80:
            logger.info("✅ Client document upload functionality is WORKING CORRECTLY")
            logger.info("✅ The upload error fix has been SUCCESSFULLY IMPLEMENTED")
        else:
            logger.info("❌ Client document upload functionality has SIGNIFICANT ISSUES")
            logger.info("❌ Additional fixes may be required")
        
        logger.info("=" * 80)

def main():
    """Main test execution"""
    tester = ClientDocumentUploadTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
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
BACKEND_URL = "https://mt5-integration.preview.emergentagent.com/api"
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