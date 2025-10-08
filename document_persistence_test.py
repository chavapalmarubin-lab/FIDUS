#!/usr/bin/env python3
"""
CRITICAL DOCUMENT UPLOAD PERSISTENCE TESTING
============================================

This test investigates the critical issue reported in the review request:
- User uploaded documents 4 times for Lilian Limon Leite
- After refresh, documents go back to "missing" status
- Documents disappearing after refresh is unacceptable for production

Test Focus:
1. Check document storage mechanism (persistent vs memory)
2. Test document persistence across sessions
3. Verify document retrieval after server restart
4. Check if documents are saved to MongoDB permanently
5. Test Lilian's specific document status

Expected Results:
- Documents should persist permanently after upload
- Never disappear after refresh
- Be retrievable across sessions
"""

import requests
import json
import sys
import time
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://mt5-deploy-debug.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class DocumentPersistenceTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.lilian_prospect_id = None
        
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
    
    def find_lilian_prospect(self):
        """Find Lilian Limon Leite prospect in the system"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects = response.json()
                
                # Look for Lilian in prospects list
                for prospect in prospects:
                    if "lilian" in prospect.get('name', '').lower() and "limon" in prospect.get('name', '').lower():
                        self.lilian_prospect_id = prospect.get('id')
                        self.log_result("Find Lilian Prospect", True, 
                                      f"Found Lilian Limon Leite: {prospect.get('name')} (ID: {self.lilian_prospect_id})",
                                      {"prospect_data": prospect})
                        return True
                
                self.log_result("Find Lilian Prospect", False, 
                              "Lilian Limon Leite not found in prospects list",
                              {"total_prospects": len(prospects), "prospect_names": [p.get('name') for p in prospects]})
                return False
            else:
                self.log_result("Find Lilian Prospect", False, 
                              f"Failed to get prospects: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Find Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def check_document_storage_mechanism(self):
        """Check if documents are stored in persistent storage or memory"""
        try:
            # Test document categories endpoint
            response = self.session.get(f"{BACKEND_URL}/documents/categories")
            if response.status_code == 200:
                categories = response.json()
                self.log_result("Document Categories API", True, 
                              f"Document categories available: {len(categories)} categories",
                              {"categories": categories})
            else:
                self.log_result("Document Categories API", False, 
                              f"HTTP {response.status_code}: Document categories not accessible")
            
            # Test document listing endpoint
            response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
            if response.status_code == 200:
                documents = response.json()
                document_count = len(documents) if isinstance(documents, list) else documents.get('total_documents', 0)
                
                self.log_result("Document Storage Check", True, 
                              f"Found {document_count} documents in storage",
                              {"document_count": document_count, "sample_docs": documents[:3] if isinstance(documents, list) else documents})
                
                # Check for Lilian's documents specifically
                lilian_docs = []
                if isinstance(documents, list):
                    for doc in documents:
                        if 'lilian' in str(doc).lower():
                            lilian_docs.append(doc)
                
                if lilian_docs:
                    self.log_result("Lilian Document Check", True, 
                                  f"Found {len(lilian_docs)} documents related to Lilian",
                                  {"lilian_documents": lilian_docs})
                else:
                    self.log_result("Lilian Document Check", False, 
                                  "No documents found for Lilian in storage")
                
                return True
            else:
                self.log_result("Document Storage Check", False, 
                              f"HTTP {response.status_code}: Cannot access document storage")
                return False
                
        except Exception as e:
            self.log_result("Document Storage Check", False, f"Exception: {str(e)}")
            return False
    
    def test_document_upload_persistence(self):
        """Test document upload and verify persistence"""
        try:
            # Create a test document
            test_document_content = f"Test document for persistence check - {datetime.now().isoformat()}"
            
            # Prepare file for upload
            files = {
                'document': ('test_persistence_doc.txt', test_document_content, 'text/plain')
            }
            
            data = {
                'uploader_id': 'admin_001',
                'uploader_type': 'admin',
                'category': 'other',
                'client_id': 'test_client'
            }
            
            # Upload document
            response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            
            if response.status_code == 200:
                upload_result = response.json()
                document_id = upload_result.get('document_id')
                
                self.log_result("Document Upload", True, 
                              f"Document uploaded successfully: {document_id}",
                              {"upload_result": upload_result})
                
                # Wait a moment then check if document persists
                time.sleep(2)
                
                # Check if document is still accessible
                response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
                if response.status_code == 200:
                    documents = response.json()
                    
                    # Look for our uploaded document
                    found_document = False
                    if isinstance(documents, list):
                        for doc in documents:
                            if doc.get('id') == document_id or doc.get('document_id') == document_id:
                                found_document = True
                                self.log_result("Document Persistence Check", True, 
                                              "Uploaded document found in storage after upload",
                                              {"document": doc})
                                break
                    
                    if not found_document:
                        self.log_result("Document Persistence Check", False, 
                                      "Uploaded document NOT found in storage - indicates memory-only storage!")
                
                return True
            else:
                self.log_result("Document Upload", False, 
                              f"HTTP {response.status_code}: Document upload failed",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Document Upload Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_lilian_document_status(self):
        """Test Lilian's specific document status"""
        if not self.lilian_prospect_id:
            self.log_result("Lilian Document Status", False, "Cannot test - Lilian prospect ID not found")
            return False
        
        try:
            # Check if there's a prospect document endpoint
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}/documents")
            
            if response.status_code == 200:
                documents = response.json()
                self.log_result("Lilian Prospect Documents", True, 
                              f"Found {len(documents)} documents for Lilian",
                              {"documents": documents})
            elif response.status_code == 404:
                self.log_result("Lilian Prospect Documents", False, 
                              "Prospect documents endpoint not found - may indicate missing functionality")
            else:
                self.log_result("Lilian Prospect Documents", False, 
                              f"HTTP {response.status_code}: Cannot access Lilian's documents")
            
            # Check general document storage for Lilian
            response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
            if response.status_code == 200:
                all_documents = response.json()
                lilian_documents = []
                
                if isinstance(all_documents, list):
                    for doc in all_documents:
                        # Check various fields that might contain Lilian's info
                        doc_str = json.dumps(doc).lower()
                        if 'lilian' in doc_str or 'limon' in doc_str or self.lilian_prospect_id in doc_str:
                            lilian_documents.append(doc)
                
                if lilian_documents:
                    self.log_result("Lilian Document Search", True, 
                                  f"Found {len(lilian_documents)} documents related to Lilian in general storage",
                                  {"lilian_documents": lilian_documents})
                else:
                    self.log_result("Lilian Document Search", False, 
                                  "No documents found for Lilian in general storage - confirms user report!")
            
            return True
            
        except Exception as e:
            self.log_result("Lilian Document Status", False, f"Exception: {str(e)}")
            return False
    
    def test_database_persistence(self):
        """Test if documents are saved to MongoDB permanently"""
        try:
            # Check database health
            response = self.session.get(f"{BACKEND_URL}/health/ready")
            if response.status_code == 200:
                health_data = response.json()
                database_status = health_data.get('database', 'unknown')
                
                if database_status == 'connected':
                    self.log_result("Database Connection", True, "Database is connected and ready")
                else:
                    self.log_result("Database Connection", False, f"Database status: {database_status}")
            
            # Check database metrics
            response = self.session.get(f"{BACKEND_URL}/health/metrics")
            if response.status_code == 200:
                metrics = response.json()
                db_info = metrics.get('database', {})
                
                collections = db_info.get('collections', 0)
                data_size = db_info.get('data_size', 0)
                
                self.log_result("Database Metrics", True, 
                              f"Database has {collections} collections, {data_size} bytes data",
                              {"database_metrics": db_info})
                
                # If no collections or very small data size, might indicate memory-only storage
                if collections == 0 or data_size < 1000:
                    self.log_result("Database Content Warning", False, 
                                  "Database appears to have minimal data - may indicate memory-only storage")
            
            return True
            
        except Exception as e:
            self.log_result("Database Persistence Check", False, f"Exception: {str(e)}")
            return False
    
    def test_session_persistence(self):
        """Test document persistence across sessions"""
        try:
            # Create a new session (simulating refresh/restart)
            new_session = requests.Session()
            
            # Authenticate with new session
            response = new_session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                if token:
                    new_session.headers.update({"Authorization": f"Bearer {token}"})
                    
                    # Check if documents are still accessible with new session
                    response = new_session.get(f"{BACKEND_URL}/documents/admin/all")
                    if response.status_code == 200:
                        documents = response.json()
                        document_count = len(documents) if isinstance(documents, list) else documents.get('total_documents', 0)
                        
                        self.log_result("Session Persistence", True, 
                                      f"Documents accessible in new session: {document_count} documents",
                                      {"document_count": document_count})
                        
                        # Compare with original session
                        original_response = self.session.get(f"{BACKEND_URL}/documents/admin/all")
                        if original_response.status_code == 200:
                            original_documents = original_response.json()
                            original_count = len(original_documents) if isinstance(original_documents, list) else original_documents.get('total_documents', 0)
                            
                            if document_count == original_count:
                                self.log_result("Session Consistency", True, 
                                              "Document count consistent across sessions")
                            else:
                                self.log_result("Session Consistency", False, 
                                              f"Document count mismatch: original={original_count}, new={document_count}")
                    else:
                        self.log_result("Session Persistence", False, 
                                      f"Cannot access documents in new session: HTTP {response.status_code}")
                else:
                    self.log_result("Session Persistence", False, "Failed to get token for new session")
            else:
                self.log_result("Session Persistence", False, 
                              f"Failed to authenticate new session: HTTP {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_result("Session Persistence", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all document persistence tests"""
        print("🚨 CRITICAL DOCUMENT UPLOAD PERSISTENCE TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("Issue: Documents uploaded for Lilian disappearing after refresh")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Document Persistence Investigation...")
        print("-" * 50)
        
        # Run all tests
        self.find_lilian_prospect()
        self.check_document_storage_mechanism()
        self.test_document_upload_persistence()
        self.test_lilian_document_status()
        self.test_database_persistence()
        self.test_session_persistence()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🚨 DOCUMENT PERSISTENCE TEST SUMMARY")
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
        
        # Show failed tests (critical issues)
        if failed_tests > 0:
            print("❌ CRITICAL ISSUES FOUND:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ WORKING FUNCTIONALITY:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment for document persistence
        critical_tests = [
            "Document Storage Check",
            "Document Upload",
            "Document Persistence Check",
            "Session Persistence",
            "Database Connection"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 DOCUMENT PERSISTENCE ASSESSMENT:")
        if critical_passed >= 3:  # At least 3 out of 5 critical tests
            print("✅ DOCUMENT PERSISTENCE: WORKING")
            print("   Documents are properly stored and persist across sessions.")
            print("   Issue may be frontend-related or specific to Lilian's workflow.")
        else:
            print("❌ DOCUMENT PERSISTENCE: BROKEN")
            print("   Critical document persistence issues found.")
            print("   Documents may be stored in memory only and lost on refresh.")
            print("   URGENT: Fix document storage to use persistent database.")
        
        # Specific Lilian assessment
        lilian_tests = [test for test in self.test_results if 'lilian' in test['test'].lower()]
        if lilian_tests:
            lilian_passed = sum(1 for test in lilian_tests if test['success'])
            print(f"\n🎯 LILIAN SPECIFIC ASSESSMENT:")
            if lilian_passed == 0:
                print("❌ LILIAN DOCUMENT ISSUE CONFIRMED")
                print("   No documents found for Lilian - confirms user report!")
                print("   Documents uploaded 4 times but not persisting.")
            else:
                print("✅ LILIAN DOCUMENTS FOUND")
                print("   Some document data found for Lilian.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = DocumentPersistenceTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()