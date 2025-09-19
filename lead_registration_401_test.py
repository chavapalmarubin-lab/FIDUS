#!/usr/bin/env python3
"""
LEAD REGISTRATION 401 ERROR REPRODUCTION TEST
============================================

This test reproduces the exact 401 error during lead registration document upload 
for "Lilian Limon Leite" as reported in the urgent bug fix request.

ISSUE REPORTED:
- User completed new user registration process
- Error "Request failed with status code 401" appears during Document Upload step (step 4)
- This should be a public endpoint, not requiring authentication

TEST WORKFLOW:
1. Create prospect "Lilian Limon Leite" via POST /api/crm/prospects
2. Upload government ID document via POST /api/crm/prospects/{id}/documents
3. Upload proof of address document via POST /api/crm/prospects/{id}/documents
4. Identify where 401 error occurs and root cause

Expected: Both endpoints should work without authentication (public endpoints)
"""

import requests
import json
import sys
import io
from datetime import datetime
import time

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://wealth-portal-17.preview.emergentagent.com/api"

class LeadRegistration401Test:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.prospect_id = None
        
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
    
    def create_mock_document_file(self, filename="government_id.jpg"):
        """Create a mock document file for upload testing"""
        # Create a simple mock image file content
        mock_content = b"MOCK_DOCUMENT_CONTENT_FOR_TESTING_" + filename.encode() + b"_END"
        return io.BytesIO(mock_content), filename
    
    def test_prospect_creation(self):
        """Test creating prospect 'Lilian Limon Leite' - should be public endpoint"""
        try:
            prospect_data = {
                "name": "Lilian Limon Leite",
                "email": "lilian.limon.leite@example.com",
                "phone": "+1-555-0123",
                "notes": "Lead registration test for 401 error reproduction"
            }
            
            # Make request WITHOUT authentication headers
            response = self.session.post(
                f"{BACKEND_URL}/crm/prospects",
                json=prospect_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.prospect_id = data.get("prospect_id")
                if self.prospect_id:
                    self.log_result(
                        "Prospect Creation (Public)", 
                        True, 
                        f"Successfully created prospect: {prospect_data['name']}",
                        {"prospect_id": self.prospect_id, "response": data}
                    )
                    return True
                else:
                    self.log_result(
                        "Prospect Creation (Public)", 
                        False, 
                        "No prospect_id returned in response",
                        {"response": data}
                    )
                    return False
            elif response.status_code == 401:
                self.log_result(
                    "Prospect Creation (Public)", 
                    False, 
                    "❌ CRITICAL: 401 Unauthorized - Prospect creation requires auth (should be public!)",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
            else:
                self.log_result(
                    "Prospect Creation (Public)", 
                    False, 
                    f"HTTP {response.status_code} error",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result("Prospect Creation (Public)", False, f"Exception: {str(e)}")
            return False
    
    def test_document_upload_government_id(self):
        """Test uploading government ID document - should be public endpoint"""
        if not self.prospect_id:
            self.log_result(
                "Government ID Upload", 
                False, 
                "Cannot test - no prospect_id available"
            )
            return False
            
        try:
            # Create mock government ID file
            file_content, filename = self.create_mock_document_file("lilian_government_id.jpg")
            
            # Prepare multipart form data
            files = {
                'file': (filename, file_content, 'image/jpeg')
            }
            data = {
                'document_type': 'government_id',
                'notes': 'Government ID for Lilian Limon Leite - Lead Registration Test'
            }
            
            # Make request WITHOUT authentication headers
            response = self.session.post(
                f"{BACKEND_URL}/crm/prospects/{self.prospect_id}/documents",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                self.log_result(
                    "Government ID Upload (Public)", 
                    True, 
                    "Successfully uploaded government ID document",
                    {"document_id": response_data.get("document_id"), "response": response_data}
                )
                return True
            elif response.status_code == 401:
                self.log_result(
                    "Government ID Upload (Public)", 
                    False, 
                    "🚨 CRITICAL BUG REPRODUCED: 401 Unauthorized - Document upload requires auth (should be public!)",
                    {"status_code": response.status_code, "response": response.text, "prospect_id": self.prospect_id}
                )
                return False
            else:
                self.log_result(
                    "Government ID Upload (Public)", 
                    False, 
                    f"HTTP {response.status_code} error",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result("Government ID Upload (Public)", False, f"Exception: {str(e)}")
            return False
    
    def test_document_upload_proof_of_address(self):
        """Test uploading proof of address document - should be public endpoint"""
        if not self.prospect_id:
            self.log_result(
                "Proof of Address Upload", 
                False, 
                "Cannot test - no prospect_id available"
            )
            return False
            
        try:
            # Create mock proof of address file
            file_content, filename = self.create_mock_document_file("lilian_proof_of_address.pdf")
            
            # Prepare multipart form data
            files = {
                'file': (filename, file_content, 'application/pdf')
            }
            data = {
                'document_type': 'proof_of_address',
                'notes': 'Proof of Address for Lilian Limon Leite - Lead Registration Test'
            }
            
            # Make request WITHOUT authentication headers
            response = self.session.post(
                f"{BACKEND_URL}/crm/prospects/{self.prospect_id}/documents",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                self.log_result(
                    "Proof of Address Upload (Public)", 
                    True, 
                    "Successfully uploaded proof of address document",
                    {"document_id": response_data.get("document_id"), "response": response_data}
                )
                return True
            elif response.status_code == 401:
                self.log_result(
                    "Proof of Address Upload (Public)", 
                    False, 
                    "🚨 CRITICAL BUG REPRODUCED: 401 Unauthorized - Document upload requires auth (should be public!)",
                    {"status_code": response.status_code, "response": response.text, "prospect_id": self.prospect_id}
                )
                return False
            else:
                self.log_result(
                    "Proof of Address Upload (Public)", 
                    False, 
                    f"HTTP {response.status_code} error",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result("Proof of Address Upload (Public)", False, f"Exception: {str(e)}")
            return False
    
    def test_with_authentication(self):
        """Test the same endpoints WITH authentication to compare behavior"""
        try:
            # First authenticate as admin
            auth_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            })
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                token = auth_data.get("token")
                if token:
                    # Set authorization header
                    self.session.headers.update({"Authorization": f"Bearer {token}"})
                    
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        "Successfully authenticated as admin for comparison test"
                    )
                    
                    # Test document upload WITH authentication
                    if self.prospect_id:
                        file_content, filename = self.create_mock_document_file("lilian_test_with_auth.jpg")
                        
                        files = {
                            'file': (filename, file_content, 'image/jpeg')
                        }
                        data = {
                            'document_type': 'additional_document',
                            'notes': 'Test with authentication for comparison'
                        }
                        
                        response = self.session.post(
                            f"{BACKEND_URL}/crm/prospects/{self.prospect_id}/documents",
                            files=files,
                            data=data
                        )
                        
                        if response.status_code == 200:
                            self.log_result(
                                "Document Upload (With Auth)", 
                                True, 
                                "Document upload works WITH authentication",
                                {"response": response.json()}
                            )
                        else:
                            self.log_result(
                                "Document Upload (With Auth)", 
                                False, 
                                f"Document upload failed even WITH auth: HTTP {response.status_code}",
                                {"response": response.text}
                            )
                    
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {auth_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Test", False, f"Exception: {str(e)}")
            return False
    
    def test_endpoint_accessibility(self):
        """Test basic endpoint accessibility"""
        endpoints_to_test = [
            ("/health", "Health Check"),
            ("/crm/prospects", "CRM Prospects Endpoint")
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                # Test GET request without auth
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code in [200, 405]:  # 405 = Method Not Allowed is OK for POST-only endpoints
                    self.log_result(
                        f"Endpoint Access - {name}", 
                        True, 
                        f"Endpoint accessible: {endpoint} (HTTP {response.status_code})"
                    )
                else:
                    self.log_result(
                        f"Endpoint Access - {name}", 
                        False, 
                        f"Endpoint issue: {endpoint} (HTTP {response.status_code})"
                    )
            except Exception as e:
                self.log_result(f"Endpoint Access - {name}", False, f"Exception: {str(e)}")
    
    def analyze_root_cause(self):
        """Analyze the root cause of 401 errors"""
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 50)
        
        # Check if prospect creation worked
        prospect_creation_success = any(
            result['success'] and 'Prospect Creation' in result['test'] 
            for result in self.test_results
        )
        
        # Check if document upload failed with 401
        document_upload_401 = any(
            not result['success'] and 'Upload' in result['test'] and '401' in result['message']
            for result in self.test_results
        )
        
        if prospect_creation_success and document_upload_401:
            print("✅ PROSPECT CREATION: Works without authentication (correct)")
            print("❌ DOCUMENT UPLOAD: Returns 401 error (BUG CONFIRMED)")
            print("\n🚨 ROOT CAUSE IDENTIFIED:")
            print("   The document upload endpoint /api/crm/prospects/{id}/documents")
            print("   is incorrectly requiring authentication when it should be public.")
            print("   This matches the exact user report: '401 error during Document Upload step'")
            
        elif not prospect_creation_success:
            print("❌ PROSPECT CREATION: Also failing - broader authentication issue")
            
        else:
            print("🤔 UNEXPECTED RESULTS: Need further investigation")
    
    def run_all_tests(self):
        """Run all lead registration 401 error reproduction tests"""
        print("🚨 LEAD REGISTRATION 401 ERROR REPRODUCTION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Subject: Lilian Limon Leite")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        print("🔍 Testing Lead Registration Workflow...")
        print("-" * 50)
        
        # Test the exact workflow reported by user
        self.test_endpoint_accessibility()
        
        # Step 1: Create prospect (should work)
        prospect_created = self.test_prospect_creation()
        
        if prospect_created:
            # Step 2: Upload government ID (reported to fail with 401)
            self.test_document_upload_government_id()
            
            # Step 3: Upload proof of address (also likely to fail with 401)
            self.test_document_upload_proof_of_address()
            
            # Step 4: Test with authentication for comparison
            self.test_with_authentication()
        
        # Analyze results
        self.analyze_root_cause()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🚨 LEAD REGISTRATION 401 ERROR TEST SUMMARY")
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
        
        # Show failed tests (these are the bugs)
        if failed_tests > 0:
            print("🚨 FAILED TESTS (BUGS IDENTIFIED):")
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
        
        # Critical bug assessment
        document_upload_bugs = sum(1 for result in self.test_results 
                                 if not result['success'] and 'Upload' in result['test'] and '401' in result['message'])
        
        print("🚨 CRITICAL BUG ASSESSMENT:")
        if document_upload_bugs > 0:
            print("❌ BUG CONFIRMED: Document upload endpoints return 401 errors")
            print("   This exactly matches the user report: 'Request failed with status code 401'")
            print("   during Document Upload step (step 4) of lead registration.")
            print()
            print("🔧 REQUIRED FIX:")
            print("   Remove authentication requirement from document upload endpoint:")
            print("   POST /api/crm/prospects/{prospect_id}/documents")
            print("   This should be a public endpoint for lead registration workflow.")
        else:
            print("✅ NO 401 ERRORS: Document upload endpoints working correctly")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = LeadRegistration401Test()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()