#!/usr/bin/env python3
"""
CRITICAL DOCUMENT PRIVACY VULNERABILITY TEST
===========================================

This test addresses the URGENT document privacy failure identified by frontend testing:
- Alejandro can see 5 documents from other clients (Salvador, Gerardo) 
- Despite backend privacy fixes being implemented
- Need to verify which endpoint is being used and why privacy is failing

Test Focus:
1. Test SECURE endpoint: /api/fidus/client-drive-folder/{client_id} (should return 0 docs)
2. Test INSECURE endpoint: /api/google/drive/client-documents/{client_id} (likely returning 5+ docs)
3. Verify Alejandro's client ID mapping and document access
4. Identify root cause of privacy breach

Alejandro's Details:
- Prospect ID: 427444c4-ab1f-44bb-a830-98bc29f4e827  
- Client ID from conversion: client_8f04d706
- Google Drive Folder: 17Y4WWD4GopxvH5xfbrMHbnNKISuTyvwV
- Expected: 0 documents (empty folder)
- Actual: 5 documents (PRIVACY BREACH!)
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-workspace-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class DocumentPrivacyTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
        # Alejandro's details from review request
        self.alejandro_prospect_id = "427444c4-ab1f-44bb-a830-98bc29f4e827"
        self.alejandro_client_id = "client_8f04d706"
        self.alejandro_folder_id = "17Y4WWD4GopxvH5xfbrMHbnNKISuTyvwV"
        
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
            print(f"   Details: {json.dumps(details, indent=2)}")
    
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
    
    def test_alejandro_client_verification(self):
        """Verify Alejandro exists as a client with correct mapping"""
        try:
            # Check if Alejandro exists in clients list
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients_data = response.json()
                clients = clients_data.get('clients', []) if isinstance(clients_data, dict) else clients_data
                
                alejandro_found = False
                alejandro_client = None
                
                for client in clients:
                    if (client.get('id') == self.alejandro_client_id or 
                        'alejandro' in client.get('name', '').lower() or
                        'alexmar7609@gmail.com' in client.get('email', '').lower()):
                        alejandro_found = True
                        alejandro_client = client
                        break
                
                if alejandro_found:
                    self.log_result("Alejandro Client Verification", True, 
                                  f"Alejandro found as client: {alejandro_client.get('name')} ({alejandro_client.get('id')})",
                                  {"client_data": alejandro_client})
                    return alejandro_client.get('id')
                else:
                    self.log_result("Alejandro Client Verification", False, 
                                  "Alejandro not found in clients list",
                                  {"total_clients": len(clients), "searched_for": [self.alejandro_client_id, "alejandro", "alexmar7609@gmail.com"]})
                    return None
            else:
                self.log_result("Alejandro Client Verification", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.log_result("Alejandro Client Verification", False, f"Exception: {str(e)}")
            return None
    
    def test_secure_endpoint_privacy(self, client_id):
        """Test the SECURE endpoint: /api/fidus/client-drive-folder/{client_id}"""
        try:
            # Test with prospect ID first
            response = self.session.get(f"{BACKEND_URL}/fidus/client-drive-folder/{self.alejandro_prospect_id}")
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                doc_count = len(documents)
                
                if doc_count == 0:
                    self.log_result("SECURE Endpoint - Prospect ID", True, 
                                  f"✅ PRIVACY SECURE: 0 documents returned for Alejandro's prospect ID",
                                  {"endpoint": f"/fidus/client-drive-folder/{self.alejandro_prospect_id}", "document_count": doc_count})
                else:
                    # PRIVACY BREACH DETECTED
                    self.log_result("SECURE Endpoint - Prospect ID", False, 
                                  f"🚨 PRIVACY BREACH: {doc_count} documents returned (expected 0)",
                                  {"endpoint": f"/fidus/client-drive-folder/{self.alejandro_prospect_id}", 
                                   "document_count": doc_count, "documents": documents[:3]})  # Show first 3 docs
            else:
                self.log_result("SECURE Endpoint - Prospect ID", False, 
                              f"HTTP {response.status_code}: {response.text}",
                              {"endpoint": f"/fidus/client-drive-folder/{self.alejandro_prospect_id}"})
            
            # Test with client ID if different
            if client_id and client_id != self.alejandro_prospect_id:
                response = self.session.get(f"{BACKEND_URL}/fidus/client-drive-folder/{client_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get('documents', [])
                    doc_count = len(documents)
                    
                    if doc_count == 0:
                        self.log_result("SECURE Endpoint - Client ID", True, 
                                      f"✅ PRIVACY SECURE: 0 documents returned for Alejandro's client ID",
                                      {"endpoint": f"/fidus/client-drive-folder/{client_id}", "document_count": doc_count})
                    else:
                        # PRIVACY BREACH DETECTED
                        self.log_result("SECURE Endpoint - Client ID", False, 
                                      f"🚨 PRIVACY BREACH: {doc_count} documents returned (expected 0)",
                                      {"endpoint": f"/fidus/client-drive-folder/{client_id}", 
                                       "document_count": doc_count, "documents": documents[:3]})
                else:
                    self.log_result("SECURE Endpoint - Client ID", False, 
                                  f"HTTP {response.status_code}: {response.text}",
                                  {"endpoint": f"/fidus/client-drive-folder/{client_id}"})
                
        except Exception as e:
            self.log_result("SECURE Endpoint Test", False, f"Exception: {str(e)}")
    
    def test_insecure_endpoint_privacy(self, client_id):
        """Test the INSECURE endpoint: /api/google/drive/client-documents/{client_id}"""
        try:
            # Test with prospect ID first
            response = self.session.get(f"{BACKEND_URL}/google/drive/client-documents/{self.alejandro_prospect_id}")
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', []) if isinstance(data, dict) else data
                doc_count = len(documents) if isinstance(documents, list) else 0
                
                if doc_count > 0:
                    # This endpoint is likely the source of privacy breach
                    self.log_result("INSECURE Endpoint - Prospect ID", False, 
                                  f"🚨 PRIVACY BREACH CONFIRMED: {doc_count} documents returned from INSECURE endpoint",
                                  {"endpoint": f"/google/drive/client-documents/{self.alejandro_prospect_id}", 
                                   "document_count": doc_count, "documents": documents[:3],
                                   "privacy_issue": "This endpoint may be returning cross-client documents"})
                else:
                    self.log_result("INSECURE Endpoint - Prospect ID", True, 
                                  f"No documents returned from insecure endpoint",
                                  {"endpoint": f"/google/drive/client-documents/{self.alejandro_prospect_id}", "document_count": doc_count})
            else:
                self.log_result("INSECURE Endpoint - Prospect ID", True, 
                              f"Endpoint not accessible: HTTP {response.status_code} (Good for privacy)",
                              {"endpoint": f"/google/drive/client-documents/{self.alejandro_prospect_id}"})
            
            # Test with client ID if different
            if client_id and client_id != self.alejandro_prospect_id:
                response = self.session.get(f"{BACKEND_URL}/google/drive/client-documents/{client_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get('documents', []) if isinstance(data, dict) else data
                    doc_count = len(documents) if isinstance(documents, list) else 0
                    
                    if doc_count > 0:
                        # This endpoint is likely the source of privacy breach
                        self.log_result("INSECURE Endpoint - Client ID", False, 
                                      f"🚨 PRIVACY BREACH CONFIRMED: {doc_count} documents returned from INSECURE endpoint",
                                      {"endpoint": f"/google/drive/client-documents/{client_id}", 
                                       "document_count": doc_count, "documents": documents[:3],
                                       "privacy_issue": "This endpoint may be returning cross-client documents"})
                    else:
                        self.log_result("INSECURE Endpoint - Client ID", True, 
                                      f"No documents returned from insecure endpoint",
                                      {"endpoint": f"/google/drive/client-documents/{client_id}", "document_count": doc_count})
                else:
                    self.log_result("INSECURE Endpoint - Client ID", True, 
                                  f"Endpoint not accessible: HTTP {response.status_code} (Good for privacy)",
                                  {"endpoint": f"/google/drive/client-documents/{client_id}"})
                
        except Exception as e:
            self.log_result("INSECURE Endpoint Test", False, f"Exception: {str(e)}")
    
    def test_cross_client_contamination(self):
        """Test if Alejandro can see documents from Salvador and Gerardo"""
        try:
            # Test known client IDs that should have documents
            test_clients = [
                ("client_003", "Salvador Palma"),
                ("client_001", "Gerardo Briones"),
                ("client_002", "Maria Rodriguez")
            ]
            
            for test_client_id, client_name in test_clients:
                # Test secure endpoint
                response = self.session.get(f"{BACKEND_URL}/fidus/client-drive-folder/{test_client_id}")
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get('documents', [])
                    doc_count = len(documents)
                    
                    if doc_count > 0:
                        self.log_result(f"Cross-Client Check - {client_name} (SECURE)", True, 
                                      f"{client_name} has {doc_count} documents in secure endpoint",
                                      {"client_id": test_client_id, "document_count": doc_count})
                    else:
                        self.log_result(f"Cross-Client Check - {client_name} (SECURE)", True, 
                                      f"{client_name} has 0 documents (expected for privacy)",
                                      {"client_id": test_client_id, "document_count": doc_count})
                
                # Test insecure endpoint
                response = self.session.get(f"{BACKEND_URL}/google/drive/client-documents/{test_client_id}")
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get('documents', []) if isinstance(data, dict) else data
                    doc_count = len(documents) if isinstance(documents, list) else 0
                    
                    if doc_count > 0:
                        self.log_result(f"Cross-Client Check - {client_name} (INSECURE)", False, 
                                      f"🚨 {client_name} has {doc_count} documents in INSECURE endpoint - potential source of privacy breach",
                                      {"client_id": test_client_id, "document_count": doc_count, 
                                       "sample_documents": documents[:2] if isinstance(documents, list) else []})
                
        except Exception as e:
            self.log_result("Cross-Client Contamination Test", False, f"Exception: {str(e)}")
    
    def test_google_drive_folder_access(self):
        """Test direct Google Drive folder access for Alejandro"""
        try:
            # Test if there's a direct Google Drive folder endpoint
            response = self.session.get(f"{BACKEND_URL}/google/drive/folder/{self.alejandro_folder_id}")
            
            if response.status_code == 200:
                data = response.json()
                files = data.get('files', [])
                file_count = len(files)
                
                if file_count == 0:
                    self.log_result("Google Drive Folder Access", True, 
                                  f"✅ Alejandro's folder is empty: {file_count} files",
                                  {"folder_id": self.alejandro_folder_id, "file_count": file_count})
                else:
                    self.log_result("Google Drive Folder Access", False, 
                                  f"Alejandro's folder has {file_count} files (expected 0)",
                                  {"folder_id": self.alejandro_folder_id, "file_count": file_count, "files": files[:3]})
            else:
                self.log_result("Google Drive Folder Access", True, 
                              f"Direct folder access not available: HTTP {response.status_code}",
                              {"folder_id": self.alejandro_folder_id})
                
        except Exception as e:
            self.log_result("Google Drive Folder Access", False, f"Exception: {str(e)}")
    
    def analyze_privacy_breach_root_cause(self):
        """Analyze the root cause of the privacy breach"""
        print("\n🔍 PRIVACY BREACH ROOT CAUSE ANALYSIS")
        print("-" * 50)
        
        # Count privacy breaches by endpoint
        secure_breaches = 0
        insecure_breaches = 0
        
        for result in self.test_results:
            if not result['success'] and 'PRIVACY BREACH' in result['message']:
                if 'SECURE Endpoint' in result['test']:
                    secure_breaches += 1
                elif 'INSECURE Endpoint' in result['test']:
                    insecure_breaches += 1
        
        print(f"Privacy breaches detected:")
        print(f"  - SECURE endpoint (/fidus/client-drive-folder): {secure_breaches}")
        print(f"  - INSECURE endpoint (/google/drive/client-documents): {insecure_breaches}")
        
        # Determine likely root cause
        if secure_breaches > 0:
            print("\n🚨 ROOT CAUSE: SECURE endpoint is NOT working correctly!")
            print("   The /api/fidus/client-drive-folder/{client_id} endpoint is returning cross-client documents.")
            print("   This indicates the privacy fix implementation has failed.")
        elif insecure_breaches > 0:
            print("\n🚨 ROOT CAUSE: Frontend is using INSECURE endpoint!")
            print("   The frontend may still be calling /api/google/drive/client-documents/{client_id}")
            print("   instead of the secure /api/fidus/client-drive-folder/{client_id} endpoint.")
        else:
            print("\n✅ No privacy breaches detected in backend endpoints.")
            print("   The issue may be in frontend implementation or caching.")
    
    def run_all_tests(self):
        """Run all document privacy tests"""
        print("🚨 CRITICAL DOCUMENT PRIVACY VULNERABILITY TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Alejandro Prospect ID: {self.alejandro_prospect_id}")
        print(f"Alejandro Client ID: {self.alejandro_client_id}")
        print(f"Alejandro Folder ID: {self.alejandro_folder_id}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Document Privacy Tests...")
        print("-" * 50)
        
        # Verify Alejandro exists as client
        alejandro_client_id = self.test_alejandro_client_verification()
        
        # Test both secure and insecure endpoints
        self.test_secure_endpoint_privacy(alejandro_client_id)
        self.test_insecure_endpoint_privacy(alejandro_client_id)
        
        # Test cross-client contamination
        self.test_cross_client_contamination()
        
        # Test direct folder access
        self.test_google_drive_folder_access()
        
        # Analyze root cause
        self.analyze_privacy_breach_root_cause()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🚨 DOCUMENT PRIVACY TEST SUMMARY")
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
        
        # Show privacy breaches
        privacy_breaches = [result for result in self.test_results 
                          if not result['success'] and 'PRIVACY BREACH' in result['message']]
        
        if privacy_breaches:
            print("🚨 PRIVACY BREACHES DETECTED:")
            for result in privacy_breaches:
                print(f"   • {result['test']}: {result['message']}")
                if result['details'].get('document_count', 0) > 0:
                    print(f"     Documents leaked: {result['details']['document_count']}")
            print()
        
        # Show successful privacy protections
        privacy_protections = [result for result in self.test_results 
                             if result['success'] and ('PRIVACY SECURE' in result['message'] or 'privacy' in result['message'].lower())]
        
        if privacy_protections:
            print("✅ PRIVACY PROTECTIONS WORKING:")
            for result in privacy_protections:
                print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        print("🚨 CRITICAL ASSESSMENT:")
        if privacy_breaches:
            print("❌ DOCUMENT PRIVACY: COMPROMISED")
            print("   Alejandro can access other clients' documents.")
            print("   URGENT ACTION REQUIRED: Fix privacy implementation immediately.")
            print("   Recommendation: Check which endpoint frontend is calling.")
        else:
            print("✅ DOCUMENT PRIVACY: SECURE")
            print("   No privacy breaches detected in backend endpoints.")
            print("   Issue may be in frontend implementation or caching.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = DocumentPrivacyTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()