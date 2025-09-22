#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Document Sharing System
Testing the newly implemented Document Sharing System with unified document portal
"""

import requests
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
import time

# Configuration
BACKEND_URL = "https://fidussign.preview.emergentagent.com/api"

# Test data
TEST_CLIENT_ID = "client_001"  # Gerardo Briones
TEST_ADMIN_ID = "admin_001"

class DocumentSharingTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.uploaded_documents = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def create_test_file(self, filename, content="Test document content", content_type="text/plain"):
        """Create a temporary test file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f".{filename.split('.')[-1]}", delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def test_document_categories_system(self):
        """Test 1: Document Categories System"""
        print("🔍 Testing Document Categories System...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/documents/categories")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify shared categories (8 expected)
                shared_categories = data.get('shared_categories', [])
                expected_shared = [
                    'loan_agreements', 'account_opening', 'investment_documents', 
                    'insurance_forms', 'amendments', 'client_statements', 
                    'tax_documents', 'other'
                ]
                
                # Verify admin-only categories (7 expected)
                admin_only_categories = data.get('admin_only_categories', [])
                expected_admin_only = [
                    'aml_kyc_reports', 'compliance_notes', 'internal_memos',
                    'risk_assessments', 'due_diligence', 'regulatory_filings',
                    'audit_documents'
                ]
                
                shared_match = set(shared_categories) == set(expected_shared)
                admin_match = set(admin_only_categories) == set(expected_admin_only)
                
                if shared_match and admin_match:
                    self.log_test(
                        "Document Categories System",
                        True,
                        f"Found {len(shared_categories)} shared categories and {len(admin_only_categories)} admin-only categories as expected"
                    )
                else:
                    missing_shared = set(expected_shared) - set(shared_categories)
                    missing_admin = set(expected_admin_only) - set(admin_only_categories)
                    self.log_test(
                        "Document Categories System",
                        False,
                        f"Category mismatch - Missing shared: {missing_shared}, Missing admin: {missing_admin}"
                    )
            else:
                self.log_test(
                    "Document Categories System",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Document Categories System", False, error=str(e))

    def test_document_upload_shared_by_admin(self):
        """Test 2a: Document Upload - Shared Category by Admin"""
        print("🔍 Testing Document Upload - Shared Category by Admin...")
        
        try:
            # Create test file
            test_file_path = self.create_test_file("investment_doc.pdf", "Investment document content")
            
            with open(test_file_path, 'rb') as f:
                files = {'document': ('investment_doc.pdf', f, 'application/pdf')}
                data = {
                    'category': 'investment_documents',
                    'uploader_id': TEST_ADMIN_ID,
                    'uploader_type': 'admin',
                    'client_id': TEST_CLIENT_ID
                }
                
                response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            # Clean up temp file
            os.unlink(test_file_path)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('document_type') == 'shared':
                    document_id = result.get('document_id')
                    self.uploaded_documents.append(document_id)
                    self.log_test(
                        "Document Upload - Shared by Admin",
                        True,
                        f"Document uploaded successfully with ID: {document_id}, type: shared"
                    )
                else:
                    self.log_test(
                        "Document Upload - Shared by Admin",
                        False,
                        f"Unexpected response: {result}"
                    )
            else:
                self.log_test(
                    "Document Upload - Shared by Admin",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Document Upload - Shared by Admin", False, error=str(e))

    def test_document_upload_shared_by_client(self):
        """Test 2b: Document Upload - Shared Category by Client"""
        print("🔍 Testing Document Upload - Shared Category by Client...")
        
        try:
            # Create test file
            test_file_path = self.create_test_file("tax_doc.pdf", "Tax document content")
            
            with open(test_file_path, 'rb') as f:
                files = {'document': ('tax_doc.pdf', f, 'application/pdf')}
                data = {
                    'category': 'tax_documents',
                    'uploader_id': TEST_CLIENT_ID,
                    'uploader_type': 'client',
                    'client_id': TEST_CLIENT_ID
                }
                
                response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            # Clean up temp file
            os.unlink(test_file_path)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('document_type') == 'shared':
                    document_id = result.get('document_id')
                    self.uploaded_documents.append(document_id)
                    self.log_test(
                        "Document Upload - Shared by Client",
                        True,
                        f"Document uploaded successfully with ID: {document_id}, type: shared"
                    )
                else:
                    self.log_test(
                        "Document Upload - Shared by Client",
                        False,
                        f"Unexpected response: {result}"
                    )
            else:
                self.log_test(
                    "Document Upload - Shared by Client",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Document Upload - Shared by Client", False, error=str(e))

    def test_document_upload_admin_only(self):
        """Test 2c: Document Upload - Admin-Only Category"""
        print("🔍 Testing Document Upload - Admin-Only Category...")
        
        try:
            # Create test file
            test_file_path = self.create_test_file("aml_report.pdf", "AML KYC Report content")
            
            with open(test_file_path, 'rb') as f:
                files = {'document': ('aml_report.pdf', f, 'application/pdf')}
                data = {
                    'category': 'aml_kyc_reports',
                    'uploader_id': TEST_ADMIN_ID,
                    'uploader_type': 'admin'
                }
                
                response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            # Clean up temp file
            os.unlink(test_file_path)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('document_type') == 'admin_only':
                    document_id = result.get('document_id')
                    self.uploaded_documents.append(document_id)
                    self.log_test(
                        "Document Upload - Admin-Only",
                        True,
                        f"Document uploaded successfully with ID: {document_id}, type: admin_only"
                    )
                else:
                    self.log_test(
                        "Document Upload - Admin-Only",
                        False,
                        f"Unexpected response: {result}"
                    )
            else:
                self.log_test(
                    "Document Upload - Admin-Only",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Document Upload - Admin-Only", False, error=str(e))

    def test_file_validation(self):
        """Test 2d: File Validation (PDF, images, size limits)"""
        print("🔍 Testing File Validation...")
        
        # Test valid image file (camera capture)
        try:
            test_file_path = self.create_test_file("photo.jpg", "fake image content")
            
            with open(test_file_path, 'rb') as f:
                files = {'document': ('photo.jpg', f, 'image/jpeg')}
                data = {
                    'category': 'investment_documents',
                    'uploader_id': TEST_ADMIN_ID,
                    'uploader_type': 'admin'
                }
                
                response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            os.unlink(test_file_path)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.uploaded_documents.append(result.get('document_id'))
                    self.log_test(
                        "File Validation - Valid Image",
                        True,
                        "JPEG image file accepted successfully"
                    )
                else:
                    self.log_test("File Validation - Valid Image", False, f"Upload failed: {result}")
            else:
                self.log_test("File Validation - Valid Image", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("File Validation - Valid Image", False, error=str(e))

        # Test invalid file type
        try:
            test_file_path = self.create_test_file("invalid.exe", "executable content")
            
            with open(test_file_path, 'rb') as f:
                files = {'document': ('invalid.exe', f, 'application/x-executable')}
                data = {
                    'category': 'investment_documents',
                    'uploader_id': TEST_ADMIN_ID,
                    'uploader_type': 'admin'
                }
                
                response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            os.unlink(test_file_path)
            
            if response.status_code == 400:
                self.log_test(
                    "File Validation - Invalid Type",
                    True,
                    "Invalid file type properly rejected with 400 status"
                )
            else:
                self.log_test(
                    "File Validation - Invalid Type",
                    False,
                    f"Expected 400 status, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("File Validation - Invalid Type", False, error=str(e))

    def test_admin_document_retrieval(self):
        """Test 3a: Admin Document Retrieval - All Documents"""
        print("🔍 Testing Admin Document Retrieval...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                # Check if we have both shared and admin-only documents
                shared_docs = [doc for doc in documents if doc.get('document_type') == 'shared']
                admin_only_docs = [doc for doc in documents if doc.get('document_type') == 'admin_only']
                
                self.log_test(
                    "Admin Document Retrieval - All",
                    True,
                    f"Retrieved {len(documents)} total documents ({len(shared_docs)} shared, {len(admin_only_docs)} admin-only)"
                )
            else:
                self.log_test(
                    "Admin Document Retrieval - All",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Admin Document Retrieval - All", False, error=str(e))

    def test_client_document_retrieval(self):
        """Test 3b: Client Document Retrieval - Shared Only"""
        print("🔍 Testing Client Document Retrieval...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/documents/client/{TEST_CLIENT_ID}")
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                # Verify NO admin-only documents are visible to client
                admin_only_docs = [doc for doc in documents if doc.get('document_type') == 'admin_only']
                shared_docs = [doc for doc in documents if doc.get('document_type') == 'shared']
                
                if len(admin_only_docs) == 0:
                    self.log_test(
                        "Client Document Retrieval - Security",
                        True,
                        f"Client sees {len(shared_docs)} shared documents, 0 admin-only documents (correct)"
                    )
                else:
                    self.log_test(
                        "Client Document Retrieval - Security",
                        False,
                        f"SECURITY ISSUE: Client can see {len(admin_only_docs)} admin-only documents!"
                    )
            else:
                self.log_test(
                    "Client Document Retrieval - Security",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Client Document Retrieval - Security", False, error=str(e))

    def test_admin_internal_documents(self):
        """Test 3c: Admin Internal Documents Endpoint"""
        print("🔍 Testing Admin Internal Documents...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/documents/admin/internal")
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                # Verify only admin-only documents are returned
                admin_only_docs = [doc for doc in documents if doc.get('document_type') == 'admin_only']
                shared_docs = [doc for doc in documents if doc.get('document_type') == 'shared']
                
                if len(shared_docs) == 0:
                    self.log_test(
                        "Admin Internal Documents",
                        True,
                        f"Internal endpoint returns {len(admin_only_docs)} admin-only documents, 0 shared (correct)"
                    )
                else:
                    self.log_test(
                        "Admin Internal Documents",
                        False,
                        f"Internal endpoint incorrectly returns {len(shared_docs)} shared documents"
                    )
            else:
                self.log_test(
                    "Admin Internal Documents",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Admin Internal Documents", False, error=str(e))

    def test_document_sharing_logic(self):
        """Test 4: Document Sharing Logic"""
        print("🔍 Testing Document Sharing Logic...")
        
        # Test admin upload with client_id should be visible to that client
        try:
            test_file_path = self.create_test_file("shared_for_client.pdf", "Document shared with specific client")
            
            with open(test_file_path, 'rb') as f:
                files = {'document': ('shared_for_client.pdf', f, 'application/pdf')}
                data = {
                    'category': 'account_opening',
                    'uploader_id': TEST_ADMIN_ID,
                    'uploader_type': 'admin',
                    'client_id': TEST_CLIENT_ID  # Assign to specific client
                }
                
                upload_response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            os.unlink(test_file_path)
            
            if upload_response.status_code == 200:
                document_id = upload_response.json().get('document_id')
                self.uploaded_documents.append(document_id)
                
                # Check if client can see this document
                client_response = self.session.get(f"{BACKEND_URL}/documents/client/{TEST_CLIENT_ID}")
                
                if client_response.status_code == 200:
                    client_docs = client_response.json().get('documents', [])
                    shared_doc_found = any(doc.get('id') == document_id for doc in client_docs)
                    
                    if shared_doc_found:
                        self.log_test(
                            "Document Sharing - Admin to Client",
                            True,
                            f"Admin document with client_id={TEST_CLIENT_ID} is visible to client"
                        )
                    else:
                        self.log_test(
                            "Document Sharing - Admin to Client",
                            False,
                            "Admin document assigned to client is NOT visible to client"
                        )
                else:
                    self.log_test(
                        "Document Sharing - Admin to Client",
                        False,
                        f"Failed to retrieve client documents: {client_response.status_code}"
                    )
            else:
                self.log_test(
                    "Document Sharing - Admin to Client",
                    False,
                    f"Failed to upload document: {upload_response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Document Sharing - Admin to Client", False, error=str(e))

    def test_mongodb_integration(self):
        """Test 5: MongoDB Integration"""
        print("🔍 Testing MongoDB Integration...")
        
        # Upload a document and verify it's stored in MongoDB (not just in-memory)
        try:
            test_file_path = self.create_test_file("mongodb_test.pdf", "Testing MongoDB storage")
            
            with open(test_file_path, 'rb') as f:
                files = {'document': ('mongodb_test.pdf', f, 'application/pdf')}
                data = {
                    'category': 'other',
                    'uploader_id': TEST_ADMIN_ID,
                    'uploader_type': 'admin'
                }
                
                response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            os.unlink(test_file_path)
            
            if response.status_code == 200:
                document_id = response.json().get('document_id')
                self.uploaded_documents.append(document_id)
                
                # Wait a moment for MongoDB write
                time.sleep(1)
                
                # Retrieve documents to verify MongoDB storage
                admin_response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
                
                if admin_response.status_code == 200:
                    documents = admin_response.json().get('documents', [])
                    mongodb_doc = next((doc for doc in documents if doc.get('id') == document_id), None)
                    
                    if mongodb_doc and 'created_at' in mongodb_doc:
                        self.log_test(
                            "MongoDB Integration",
                            True,
                            f"Document stored in MongoDB with proper metadata (created_at: {mongodb_doc['created_at']})"
                        )
                    else:
                        self.log_test(
                            "MongoDB Integration",
                            False,
                            "Document not found in MongoDB or missing metadata"
                        )
                else:
                    self.log_test(
                        "MongoDB Integration",
                        False,
                        f"Failed to retrieve documents from MongoDB: {admin_response.status_code}"
                    )
            else:
                self.log_test(
                    "MongoDB Integration",
                    False,
                    f"Failed to upload document: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("MongoDB Integration", False, error=str(e))

    def test_cross_user_document_visibility(self):
        """Test 6: Cross-User Document Visibility"""
        print("🔍 Testing Cross-User Document Visibility...")
        
        # Test that different clients don't see each other's documents
        try:
            # Upload document for client_001
            test_file_path = self.create_test_file("client1_private.pdf", "Private document for client 1")
            
            with open(test_file_path, 'rb') as f:
                files = {'document': ('client1_private.pdf', f, 'application/pdf')}
                data = {
                    'category': 'tax_documents',
                    'uploader_id': TEST_CLIENT_ID,
                    'uploader_type': 'client',
                    'client_id': TEST_CLIENT_ID
                }
                
                response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            os.unlink(test_file_path)
            
            if response.status_code == 200:
                document_id = response.json().get('document_id')
                self.uploaded_documents.append(document_id)
                
                # Check if another client (client_002) can see this document
                other_client_response = self.session.get(f"{BACKEND_URL}/documents/client/client_002")
                
                if other_client_response.status_code == 200:
                    other_client_docs = other_client_response.json().get('documents', [])
                    private_doc_visible = any(doc.get('id') == document_id for doc in other_client_docs)
                    
                    if not private_doc_visible:
                        self.log_test(
                            "Cross-User Document Visibility",
                            True,
                            "Client's private document is NOT visible to other clients (correct)"
                        )
                    else:
                        self.log_test(
                            "Cross-User Document Visibility",
                            False,
                            "SECURITY ISSUE: Client's private document is visible to other clients!"
                        )
                else:
                    self.log_test(
                        "Cross-User Document Visibility",
                        False,
                        f"Failed to retrieve other client documents: {other_client_response.status_code}"
                    )
            else:
                self.log_test(
                    "Cross-User Document Visibility",
                    False,
                    f"Failed to upload private document: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Cross-User Document Visibility", False, error=str(e))

    def test_document_metadata_validation(self):
        """Test 7: Document Metadata Validation"""
        print("🔍 Testing Document Metadata Validation...")
        
        try:
            # Get all documents and verify metadata structure
            response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
            
            if response.status_code == 200:
                documents = response.json().get('documents', [])
                
                if documents:
                    sample_doc = documents[0]
                    required_fields = [
                        'id', 'name', 'category', 'document_type', 
                        'uploader_id', 'uploader_type', 'created_at'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in sample_doc]
                    
                    if not missing_fields:
                        # Verify document_type values
                        valid_types = ['shared', 'admin_only']
                        invalid_types = [doc for doc in documents if doc.get('document_type') not in valid_types]
                        
                        if not invalid_types:
                            self.log_test(
                                "Document Metadata Validation",
                                True,
                                f"All {len(documents)} documents have proper metadata structure and valid document_type"
                            )
                        else:
                            self.log_test(
                                "Document Metadata Validation",
                                False,
                                f"Found {len(invalid_types)} documents with invalid document_type"
                            )
                    else:
                        self.log_test(
                            "Document Metadata Validation",
                            False,
                            f"Missing required fields in document metadata: {missing_fields}"
                        )
                else:
                    self.log_test(
                        "Document Metadata Validation",
                        True,
                        "No documents found to validate (empty system)"
                    )
            else:
                self.log_test(
                    "Document Metadata Validation",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Document Metadata Validation", False, error=str(e))

    def run_all_tests(self):
        """Run all document sharing system tests"""
        print("🚀 Starting Comprehensive Document Sharing System Testing...")
        print("=" * 80)
        
        # Test 1: Document Categories System
        self.test_document_categories_system()
        
        # Test 2: Document Upload with Categorization
        self.test_document_upload_shared_by_admin()
        self.test_document_upload_shared_by_client()
        self.test_document_upload_admin_only()
        self.test_file_validation()
        
        # Test 3: Document Retrieval & Sharing Logic
        self.test_admin_document_retrieval()
        self.test_client_document_retrieval()
        self.test_admin_internal_documents()
        
        # Test 4: Document Sharing Logic
        self.test_document_sharing_logic()
        
        # Test 5: MongoDB Integration
        self.test_mongodb_integration()
        
        # Test 6: Cross-User Document Visibility
        self.test_cross_user_document_visibility()
        
        # Test 7: Document Metadata Validation
        self.test_document_metadata_validation()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 DOCUMENT SHARING SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"   • {test['test']}: {test['error']}")
            print()
        
        print("🔍 KEY FINDINGS:")
        
        # Document Categories
        categories_test = next((t for t in self.test_results if "Categories" in t['test']), None)
        if categories_test and categories_test['success']:
            print("   ✅ Document categories system working (8 shared + 7 admin-only)")
        
        # Security
        security_tests = [t for t in self.test_results if "Security" in t['test'] or "Cross-User" in t['test']]
        security_passed = all(t['success'] for t in security_tests)
        if security_passed:
            print("   ✅ Document security and access control working correctly")
        else:
            print("   ❌ SECURITY ISSUES DETECTED in document access control")
        
        # MongoDB Integration
        mongodb_test = next((t for t in self.test_results if "MongoDB" in t['test']), None)
        if mongodb_test and mongodb_test['success']:
            print("   ✅ MongoDB integration working correctly")
        
        # Upload System
        upload_tests = [t for t in self.test_results if "Upload" in t['test']]
        upload_passed = all(t['success'] for t in upload_tests)
        if upload_passed:
            print("   ✅ Document upload and categorization system working")
        
        print()
        print(f"📄 Uploaded {len(self.uploaded_documents)} test documents during testing")
        print("=" * 80)

if __name__ == "__main__":
    tester = DocumentSharingTester()
    tester.run_all_tests()