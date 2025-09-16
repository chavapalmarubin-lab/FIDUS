#!/usr/bin/env python3
"""
LILIAN LIMON LEITE DOCUMENT INVESTIGATION
=========================================

Since MongoDB document persistence is working correctly, the issue must be
specific to Lilian's workflow or the prospect document system. This test
investigates:

1. Prospect document upload system (different from general documents)
2. Lilian's specific prospect record and document status
3. Frontend-backend integration for prospect documents
4. Document status tracking for prospects

The user reported:
- Uploaded documents 4 times for Lilian Limon Leite
- After refresh, documents go back to "missing" status
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://aml-kyc-portal.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class LilianDocumentInvestigation:
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
        """Find Lilian Limon Leite in the CRM prospects system"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects_data = response.json()
                
                # Handle different response formats
                prospects = []
                if isinstance(prospects_data, list):
                    prospects = prospects_data
                elif isinstance(prospects_data, dict):
                    prospects = prospects_data.get('prospects', [])
                
                print(f"🔍 Found {len(prospects)} total prospects in CRM system")
                
                # Look for Lilian
                for prospect in prospects:
                    name = prospect.get('name', '').lower()
                    if 'lilian' in name and ('limon' in name or 'leite' in name):
                        self.lilian_prospect_id = prospect.get('id')
                        self.log_result("Find Lilian Prospect", True, 
                                      f"Found Lilian: {prospect.get('name')} (ID: {self.lilian_prospect_id})",
                                      {"prospect_data": prospect})
                        return True
                
                # If not found, list all prospect names for debugging
                prospect_names = [p.get('name', 'Unknown') for p in prospects]
                self.log_result("Find Lilian Prospect", False, 
                              "Lilian Limon Leite not found in CRM prospects",
                              {"total_prospects": len(prospects), "prospect_names": prospect_names})
                return False
            else:
                self.log_result("Find Lilian Prospect", False, 
                              f"Failed to get prospects: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Find Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def check_prospect_document_system(self):
        """Check if prospect document system exists and works"""
        try:
            # Test prospect document endpoints
            if not self.lilian_prospect_id:
                # Create a test prospect for testing
                test_prospect_data = {
                    "name": "Test Prospect for Document Investigation",
                    "email": "test.prospect@investigation.com",
                    "phone": "+1-555-TEST-DOC",
                    "notes": "Created for document investigation testing"
                }
                
                response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect_data)
                if response.status_code == 200:
                    prospect_result = response.json()
                    test_prospect_id = prospect_result.get('id')
                    self.log_result("Create Test Prospect", True, 
                                  f"Created test prospect: {test_prospect_id}")
                    
                    # Use test prospect for document testing
                    self.lilian_prospect_id = test_prospect_id
                else:
                    self.log_result("Create Test Prospect", False, 
                                  f"Failed to create test prospect: HTTP {response.status_code}")
                    return False
            
            # Test prospect document endpoints
            prospect_id = self.lilian_prospect_id
            
            # Check if prospect documents endpoint exists
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/{prospect_id}/documents")
            if response.status_code == 200:
                documents = response.json()
                self.log_result("Prospect Documents Endpoint", True, 
                              f"Prospect documents endpoint working: {len(documents)} documents found",
                              {"documents": documents})
            elif response.status_code == 404:
                self.log_result("Prospect Documents Endpoint", False, 
                              "Prospect documents endpoint not found (404)")
            else:
                self.log_result("Prospect Documents Endpoint", False, 
                              f"Prospect documents endpoint error: HTTP {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_result("Prospect Document System Check", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_document_upload(self):
        """Test prospect document upload functionality"""
        if not self.lilian_prospect_id:
            self.log_result("Prospect Document Upload", False, "No prospect ID available for testing")
            return False
        
        try:
            # Test uploading a document to the prospect
            test_content = f"Test prospect document - {datetime.now().isoformat()}"
            
            files = {
                'file': ('test_prospect_doc.txt', test_content, 'text/plain')
            }
            
            data = {
                'document_type': 'identity_document',
                'notes': 'Test document upload for investigation'
            }
            
            prospect_id = self.lilian_prospect_id
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/documents", 
                                       files=files, data=data)
            
            if response.status_code == 200:
                upload_result = response.json()
                self.log_result("Prospect Document Upload", True, 
                              "Prospect document uploaded successfully",
                              {"upload_result": upload_result})
                
                # Try to retrieve the document
                response = self.session.get(f"{BACKEND_URL}/crm/prospects/{prospect_id}/documents")
                if response.status_code == 200:
                    documents = response.json()
                    if len(documents) > 0:
                        self.log_result("Prospect Document Retrieval", True, 
                                      f"Document found after upload: {len(documents)} documents")
                    else:
                        self.log_result("Prospect Document Retrieval", False, 
                                      "No documents found after upload - persistence issue!")
                
                return True
            else:
                self.log_result("Prospect Document Upload", False, 
                              f"Prospect document upload failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Prospect Document Upload", False, f"Exception: {str(e)}")
            return False
    
    def investigate_document_status_tracking(self):
        """Investigate how document status is tracked for prospects"""
        if not self.lilian_prospect_id:
            self.log_result("Document Status Investigation", False, "No prospect ID available")
            return False
        
        try:
            prospect_id = self.lilian_prospect_id
            
            # Get prospect details
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/{prospect_id}")
            if response.status_code == 200:
                prospect_data = response.json()
                
                # Check for document-related fields
                document_fields = {}
                for key, value in prospect_data.items():
                    if 'document' in key.lower() or 'kyc' in key.lower() or 'aml' in key.lower():
                        document_fields[key] = value
                
                if document_fields:
                    self.log_result("Document Status Fields", True, 
                                  f"Found document-related fields in prospect: {list(document_fields.keys())}",
                                  {"document_fields": document_fields})
                else:
                    self.log_result("Document Status Fields", False, 
                                  "No document-related fields found in prospect data")
                
                # Check if there's a document status that might be resetting
                status_fields = ['status', 'document_status', 'kyc_status', 'aml_status']
                for field in status_fields:
                    if field in prospect_data:
                        self.log_result(f"Status Field: {field}", True, 
                                      f"{field}: {prospect_data[field]}")
                
                return True
            else:
                self.log_result("Document Status Investigation", False, 
                              f"Cannot get prospect details: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Document Status Investigation", False, f"Exception: {str(e)}")
            return False
    
    def check_frontend_backend_integration(self):
        """Check for potential frontend-backend integration issues"""
        try:
            # Check if there are different document endpoints that might be used by frontend
            endpoints_to_test = [
                "/documents/admin/all",
                "/documents/categories",
                "/crm/prospects",
                "/crm/admin/dashboard"
            ]
            
            working_endpoints = []
            failing_endpoints = []
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 200:
                        working_endpoints.append(endpoint)
                    else:
                        failing_endpoints.append(f"{endpoint} (HTTP {response.status_code})")
                except Exception as e:
                    failing_endpoints.append(f"{endpoint} (Exception: {str(e)})")
            
            self.log_result("Frontend-Backend Integration", True, 
                          f"Working endpoints: {len(working_endpoints)}, Failing: {len(failing_endpoints)}",
                          {"working": working_endpoints, "failing": failing_endpoints})
            
            # Check if there are any CORS or authentication issues
            if failing_endpoints:
                self.log_result("Endpoint Issues", False, 
                              f"Some endpoints failing: {failing_endpoints}")
            
            return True
            
        except Exception as e:
            self.log_result("Frontend-Backend Integration", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Lilian document investigation tests"""
        print("🔍 LILIAN LIMON LEITE DOCUMENT INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("Focus: Investigating Lilian's specific document upload issues")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Lilian Document Investigation...")
        print("-" * 50)
        
        # Run investigation tests
        self.find_lilian_prospect()
        self.check_prospect_document_system()
        self.test_prospect_document_upload()
        self.investigate_document_status_tracking()
        self.check_frontend_backend_integration()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🔍 LILIAN DOCUMENT INVESTIGATION SUMMARY")
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
        
        # Show critical findings
        if failed_tests > 0:
            print("❌ CRITICAL FINDINGS:")
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
        
        # Specific analysis for Lilian's issue
        print("🚨 LILIAN DOCUMENT ISSUE ANALYSIS:")
        
        lilian_found = any('lilian' in r['test'].lower() and r['success'] for r in self.test_results)
        prospect_system_working = any('prospect' in r['test'].lower() and 'upload' in r['test'].lower() and r['success'] for r in self.test_results)
        
        if not lilian_found:
            print("❌ LILIAN NOT FOUND IN SYSTEM")
            print("   Lilian Limon Leite prospect record not found in CRM.")
            print("   This could explain why her documents appear to be missing.")
            print("   SOLUTION: Create Lilian's prospect record or check if she was deleted.")
        elif not prospect_system_working:
            print("❌ PROSPECT DOCUMENT SYSTEM ISSUES")
            print("   Prospect document upload/retrieval system has problems.")
            print("   This could cause documents to not persist properly.")
            print("   SOLUTION: Fix prospect document endpoints and storage.")
        else:
            print("✅ SYSTEM APPEARS FUNCTIONAL")
            print("   Both Lilian's record and prospect document system working.")
            print("   Issue may be:")
            print("   - Frontend caching problems")
            print("   - Specific workflow steps not tested")
            print("   - User interface not reflecting backend state")
            print("   - Document status field resetting on refresh")
        
        print("\n🎯 RECOMMENDED ACTIONS:")
        print("1. Check if Lilian Limon Leite prospect record exists")
        print("2. Verify prospect document upload endpoints work")
        print("3. Test frontend document status display logic")
        print("4. Check for document status field reset issues")
        print("5. Investigate frontend caching or state management")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = LilianDocumentInvestigation()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()