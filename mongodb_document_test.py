#!/usr/bin/env python3
"""
MONGODB DOCUMENT PERSISTENCE INVESTIGATION
==========================================

This test specifically investigates the MongoDB document storage issue.
The problem appears to be that documents are falling back to in-memory storage
instead of being properly saved to MongoDB.

Investigation Focus:
1. Test MongoDB connection directly
2. Check if create_document method works
3. Verify document retrieval from MongoDB
4. Check if MongoDB integration is failing silently
"""

import requests
import json
import sys
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://fidus-invest-1.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class MongoDBDocumentTest:
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
    
    def test_mongodb_health(self):
        """Test MongoDB connection health"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health/ready")
            if response.status_code == 200:
                health_data = response.json()
                database_status = health_data.get('database', 'unknown')
                
                if database_status == 'connected':
                    self.log_result("MongoDB Health", True, "MongoDB is connected and ready")
                else:
                    self.log_result("MongoDB Health", False, f"MongoDB status: {database_status}")
                    
                return database_status == 'connected'
            else:
                self.log_result("MongoDB Health", False, f"Health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("MongoDB Health", False, f"Exception: {str(e)}")
            return False
    
    def test_mongodb_metrics(self):
        """Test MongoDB metrics and collections"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health/metrics")
            if response.status_code == 200:
                metrics = response.json()
                db_info = metrics.get('database', {})
                
                collections = db_info.get('collections', 0)
                data_size = db_info.get('data_size', 0)
                
                self.log_result("MongoDB Metrics", True, 
                              f"MongoDB has {collections} collections, {data_size} bytes data",
                              {"database_metrics": db_info})
                
                # Check if documents collection exists
                if collections > 0:
                    self.log_result("MongoDB Collections", True, 
                                  f"MongoDB has {collections} collections - documents collection likely exists")
                else:
                    self.log_result("MongoDB Collections", False, 
                                  "MongoDB has 0 collections - documents collection missing!")
                
                return collections > 0
            else:
                self.log_result("MongoDB Metrics", False, f"Metrics failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("MongoDB Metrics", False, f"Exception: {str(e)}")
            return False
    
    def test_document_upload_with_debug(self):
        """Test document upload with detailed debugging"""
        try:
            # Create a test document with unique content
            test_content = f"MONGODB TEST DOCUMENT - {datetime.now().isoformat()}"
            
            # Prepare file for upload
            files = {
                'document': ('mongodb_test.txt', test_content, 'text/plain')
            }
            
            data = {
                'uploader_id': 'admin_001',
                'uploader_type': 'admin',
                'category': 'other',
                'client_id': 'test_mongodb'
            }
            
            print(f"📤 Uploading test document with content: {test_content[:50]}...")
            
            # Upload document
            response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            if response.status_code == 200:
                upload_result = response.json()
                document_id = upload_result.get('document_id')
                
                self.log_result("Document Upload", True, 
                              f"Document uploaded successfully: {document_id}",
                              {"upload_result": upload_result})
                
                return document_id
            else:
                self.log_result("Document Upload", False, 
                              f"HTTP {response.status_code}: Document upload failed",
                              {"response": response.text})
                return None
                
        except Exception as e:
            self.log_result("Document Upload", False, f"Exception: {str(e)}")
            return None
    
    def test_document_retrieval_mongodb(self, document_id):
        """Test if document can be retrieved from MongoDB"""
        try:
            # Get all documents
            response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
            
            if response.status_code == 200:
                result = response.json()
                documents = result.get('documents', [])
                
                print(f"📥 Retrieved {len(documents)} documents from storage")
                
                # Look for our uploaded document
                found_document = None
                for doc in documents:
                    if doc.get('document_id') == document_id or doc.get('id') == document_id:
                        found_document = doc
                        break
                
                if found_document:
                    self.log_result("Document Retrieval", True, 
                                  "Document found in storage after upload",
                                  {"document": found_document})
                    
                    # Check if it has MongoDB-specific fields
                    has_mongodb_fields = 'created_at' in found_document and 'updated_at' in found_document
                    if has_mongodb_fields:
                        self.log_result("MongoDB Storage Confirmed", True, 
                                      "Document has MongoDB timestamp fields - stored in database")
                    else:
                        self.log_result("MongoDB Storage Warning", False, 
                                      "Document missing MongoDB fields - may be in memory storage")
                    
                    return True
                else:
                    self.log_result("Document Retrieval", False, 
                                  f"Document {document_id} NOT found in storage - lost after upload!",
                                  {"available_documents": [d.get('document_id', d.get('id')) for d in documents]})
                    return False
            else:
                self.log_result("Document Retrieval", False, 
                              f"HTTP {response.status_code}: Cannot retrieve documents")
                return False
                
        except Exception as e:
            self.log_result("Document Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_document_persistence_after_delay(self, document_id):
        """Test if document persists after a delay (simulating refresh)"""
        try:
            import time
            print("⏳ Waiting 5 seconds to simulate refresh/delay...")
            time.sleep(5)
            
            # Try to retrieve document again
            response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
            
            if response.status_code == 200:
                result = response.json()
                documents = result.get('documents', [])
                
                # Look for our document
                found_document = None
                for doc in documents:
                    if doc.get('document_id') == document_id or doc.get('id') == document_id:
                        found_document = doc
                        break
                
                if found_document:
                    self.log_result("Document Persistence After Delay", True, 
                                  "Document still exists after 5-second delay")
                    return True
                else:
                    self.log_result("Document Persistence After Delay", False, 
                                  "Document DISAPPEARED after 5-second delay - confirms memory storage issue!")
                    return False
            else:
                self.log_result("Document Persistence After Delay", False, 
                              f"HTTP {response.status_code}: Cannot check persistence")
                return False
                
        except Exception as e:
            self.log_result("Document Persistence After Delay", False, f"Exception: {str(e)}")
            return False
    
    def test_multiple_document_uploads(self):
        """Test multiple document uploads to see pattern"""
        try:
            uploaded_docs = []
            
            for i in range(3):
                test_content = f"MULTI TEST DOCUMENT {i+1} - {datetime.now().isoformat()}"
                
                files = {
                    'document': (f'multi_test_{i+1}.txt', test_content, 'text/plain')
                }
                
                data = {
                    'uploader_id': 'admin_001',
                    'uploader_type': 'admin',
                    'category': 'other',
                    'client_id': f'test_multi_{i+1}'
                }
                
                response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
                
                if response.status_code == 200:
                    upload_result = response.json()
                    document_id = upload_result.get('document_id')
                    uploaded_docs.append(document_id)
                    print(f"📤 Uploaded document {i+1}: {document_id}")
                else:
                    print(f"❌ Failed to upload document {i+1}: HTTP {response.status_code}")
            
            if uploaded_docs:
                self.log_result("Multiple Document Upload", True, 
                              f"Successfully uploaded {len(uploaded_docs)} documents",
                              {"document_ids": uploaded_docs})
                
                # Check if all are retrievable
                response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
                if response.status_code == 200:
                    result = response.json()
                    documents = result.get('documents', [])
                    
                    found_count = 0
                    for doc_id in uploaded_docs:
                        for doc in documents:
                            if doc.get('document_id') == doc_id or doc.get('id') == doc_id:
                                found_count += 1
                                break
                    
                    if found_count == len(uploaded_docs):
                        self.log_result("Multiple Document Retrieval", True, 
                                      f"All {found_count} documents found in storage")
                    else:
                        self.log_result("Multiple Document Retrieval", False, 
                                      f"Only {found_count}/{len(uploaded_docs)} documents found - some lost!")
                
                return uploaded_docs
            else:
                self.log_result("Multiple Document Upload", False, "No documents uploaded successfully")
                return []
                
        except Exception as e:
            self.log_result("Multiple Document Upload", False, f"Exception: {str(e)}")
            return []
    
    def run_all_tests(self):
        """Run all MongoDB document tests"""
        print("🔍 MONGODB DOCUMENT PERSISTENCE INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("Focus: Investigating why documents disappear after refresh")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running MongoDB Document Investigation...")
        print("-" * 50)
        
        # Run tests in sequence
        mongodb_healthy = self.test_mongodb_health()
        mongodb_has_collections = self.test_mongodb_metrics()
        
        if mongodb_healthy and mongodb_has_collections:
            print("\n📤 Testing Document Upload and Persistence...")
            document_id = self.test_document_upload_with_debug()
            
            if document_id:
                self.test_document_retrieval_mongodb(document_id)
                self.test_document_persistence_after_delay(document_id)
            
            print("\n📤 Testing Multiple Document Uploads...")
            self.test_multiple_document_uploads()
        else:
            print("⚠️ MongoDB issues detected - skipping document tests")
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🔍 MONGODB DOCUMENT INVESTIGATION SUMMARY")
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
        
        # Show critical failures
        if failed_tests > 0:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show working functionality
        if passed_tests > 0:
            print("✅ WORKING FUNCTIONALITY:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Root cause analysis
        print("🚨 ROOT CAUSE ANALYSIS:")
        
        mongodb_tests = [r for r in self.test_results if 'mongodb' in r['test'].lower()]
        mongodb_working = all(r['success'] for r in mongodb_tests)
        
        persistence_tests = [r for r in self.test_results if 'persistence' in r['test'].lower() or 'retrieval' in r['test'].lower()]
        persistence_working = all(r['success'] for r in persistence_tests)
        
        if mongodb_working and not persistence_working:
            print("❌ MONGODB INTEGRATION ISSUE")
            print("   MongoDB is connected but documents are not persisting.")
            print("   Likely cause: create_document() method failing silently.")
            print("   Documents falling back to in-memory storage.")
            print("   SOLUTION: Fix MongoDB document creation in mongodb_integration.py")
        elif not mongodb_working:
            print("❌ MONGODB CONNECTION ISSUE")
            print("   MongoDB connection or configuration problems.")
            print("   SOLUTION: Check MongoDB connection and database setup.")
        elif persistence_working:
            print("✅ MONGODB PERSISTENCE WORKING")
            print("   Documents are properly stored in MongoDB.")
            print("   Issue may be frontend-specific or user workflow related.")
        else:
            print("❓ UNCLEAR ROOT CAUSE")
            print("   Need additional investigation.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = MongoDBDocumentTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()