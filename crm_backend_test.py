#!/usr/bin/env python3
"""
FIDUS CRM & ENHANCED FUNCTIONALITY BACKEND API TESTING SUITE
============================================================

Testing newly implemented and enhanced functionality as requested in review:
1. CRM Pipeline System endpoints
2. User Administration System endpoints  
3. Document Signing System endpoints
4. Enhanced Functionality Verification with JWT authentication

Focus Areas:
- Complete CRM pipeline functionality (Lead → Negotiation → Won/Lost)
- Won leads conversion to clients with AML/KYC checks
- User Administration functions (standard user management)
- Document Signing: "Send for Signature" functionality
- JWT authentication verification across all endpoints
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration - Use production URL as specified in review
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "password123", "user_type": "admin"}

class FIDUSCRMBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.test_results = []
        self.test_prospect_id = None
        self.test_user_id = None
        self.test_document_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results with detailed information"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_admin(self) -> bool:
        """Authenticate as admin and get JWT token"""
        print("🔐 AUTHENTICATING AS ADMIN")
        print("-" * 30)
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("token")
                if self.jwt_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                    self.log_test("Admin Authentication", True, 
                                f"JWT token obtained and set in headers. Token: {self.jwt_token[:30]}...")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No JWT token in response", data)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_crm_pipeline_system(self):
        """Test CRM Pipeline System endpoints as specified in review"""
        print("🔍 TESTING CRM PIPELINE SYSTEM")
        print("=" * 50)
        
        # Test 1: GET /api/crm/prospects (fetch all prospects)
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                data = response.json()
                prospects = data.get("prospects", [])
                pipeline_stats = data.get("pipeline_stats", {})
                total_prospects = data.get("total_prospects", 0)
                
                self.log_test("GET /api/crm/prospects (fetch all prospects)", True, 
                            f"Retrieved {len(prospects)} prospects. Total: {total_prospects}. Pipeline stages: {list(pipeline_stats.keys())}", 
                            {"prospect_count": len(prospects), "pipeline_stats": pipeline_stats, "total_prospects": total_prospects})
            else:
                self.log_test("GET /api/crm/prospects (fetch all prospects)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/crm/prospects (fetch all prospects)", False, f"Exception: {str(e)}")

        # Test 2: GET /api/crm/prospects/pipeline (pipeline data)
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/pipeline")
            if response.status_code == 200:
                data = response.json()
                pipeline = data.get("pipeline", {})
                pipeline_stages = list(pipeline.keys())
                stage_counts = {stage: len(prospects) for stage, prospects in pipeline.items()}
                
                self.log_test("GET /api/crm/prospects/pipeline (pipeline data)", True, 
                            f"Pipeline stages: {pipeline_stages}. Stage counts: {stage_counts}", 
                            {"pipeline_stages": pipeline_stages, "stage_counts": stage_counts})
            else:
                self.log_test("GET /api/crm/prospects/pipeline (pipeline data)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/crm/prospects/pipeline (pipeline data)", False, f"Exception: {str(e)}")

        # Test 3: POST /api/crm/prospects (create prospect)
        test_prospect_data = {
            "name": "CRM Test Prospect",
            "email": "crm.test.prospect@fidus.com",
            "phone": "+1-555-CRM-TEST",
            "notes": "Created during CRM backend testing for pipeline workflow verification"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect_data)
            if response.status_code == 200:
                data = response.json()
                prospect_id = data.get("prospect_id")
                prospect_data = data.get("prospect", {})
                
                self.log_test("POST /api/crm/prospects (create prospect)", True, 
                            f"Created prospect with ID: {prospect_id}. Initial stage: {prospect_data.get('stage', 'unknown')}", 
                            {"prospect_id": prospect_id, "prospect_stage": prospect_data.get('stage')})
                
                # Store prospect ID for further tests
                self.test_prospect_id = prospect_id
            else:
                self.log_test("POST /api/crm/prospects (create prospect)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/crm/prospects (create prospect)", False, f"Exception: {str(e)}")

        # Test 4: PUT /api/crm/prospects/{id} (update prospect stages: lead → negotiation → won/lost)
        if self.test_prospect_id:
            # Test stage progression as specified in review: Lead → Negotiation → Won
            stages_to_test = [
                ("negotiation", "Moving from lead to negotiation stage"),
                ("won", "Moving to won stage for client conversion eligibility")
            ]
            
            for stage, description in stages_to_test:
                try:
                    update_data = {"stage": stage}
                    response = self.session.put(f"{BACKEND_URL}/crm/prospects/{self.test_prospect_id}", json=update_data)
                    if response.status_code == 200:
                        data = response.json()
                        updated_prospect = data.get("prospect", {})
                        updated_stage = updated_prospect.get("stage")
                        
                        self.log_test(f"PUT /api/crm/prospects/{{id}} (update to {stage})", True, 
                                    f"{description}. Updated stage: {updated_stage}", 
                                    {"target_stage": stage, "updated_stage": updated_stage})
                    else:
                        self.log_test(f"PUT /api/crm/prospects/{{id}} (update to {stage})", False, 
                                    f"HTTP {response.status_code}. {description}", response.text)
                except Exception as e:
                    self.log_test(f"PUT /api/crm/prospects/{{id}} (update to {stage})", False, 
                                f"Exception during {description}: {str(e)}")

        # Test 5: POST /api/crm/prospects/{id}/aml-kyc (AML/KYC checks)
        if self.test_prospect_id:
            try:
                response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.test_prospect_id}/aml-kyc")
                if response.status_code == 200:
                    data = response.json()
                    aml_result = data.get("aml_result", {})
                    overall_status = aml_result.get("overall_status")
                    risk_score = aml_result.get("risk_score")
                    
                    self.log_test("POST /api/crm/prospects/{id}/aml-kyc (AML/KYC checks)", True, 
                                f"AML/KYC check completed. Status: {overall_status}, Risk Score: {risk_score}", 
                                {"aml_status": overall_status, "risk_score": risk_score, "aml_result": aml_result})
                else:
                    self.log_test("POST /api/crm/prospects/{id}/aml-kyc (AML/KYC checks)", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/crm/prospects/{id}/aml-kyc (AML/KYC checks)", False, f"Exception: {str(e)}")

        # Test 6: POST /api/crm/prospects/{id}/convert (convert won prospects to clients)
        if self.test_prospect_id:
            try:
                conversion_data = {"prospect_id": self.test_prospect_id, "send_agreement": True}
                response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.test_prospect_id}/convert", json=conversion_data)
                if response.status_code == 200:
                    data = response.json()
                    client_id = data.get("client_id")
                    client_username = data.get("client_username")
                    agreement_sent = data.get("agreement_sent", False)
                    
                    self.log_test("POST /api/crm/prospects/{id}/convert (convert won prospects to clients)", True, 
                                f"Prospect converted to client. Client ID: {client_id}, Username: {client_username}, Agreement sent: {agreement_sent}", 
                                {"client_id": client_id, "client_username": client_username, "agreement_sent": agreement_sent})
                else:
                    self.log_test("POST /api/crm/prospects/{id}/convert (convert won prospects to clients)", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/crm/prospects/{id}/convert (convert won prospects to clients)", False, f"Exception: {str(e)}")

    def test_user_administration_system(self):
        """Test User Administration System endpoints"""
        print("🔍 TESTING USER ADMINISTRATION SYSTEM")
        print("=" * 50)
        
        # Test 1: POST /api/admin/users/create (create new users with temporary passwords)
        test_user_data = {
            "username": "crmtest_user",
            "name": "CRM Test User",
            "email": "crmtest.user@fidus.com",
            "phone": "+1-555-CRM-USER",
            "temporary_password": "CRMTemp123!",
            "notes": "Created during CRM backend testing for user administration verification"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/users/create", json=test_user_data)
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("user_id")
                success_message = data.get("message", "")
                
                self.log_test("POST /api/admin/users/create (create new users with temporary passwords)", True, 
                            f"User created successfully. User ID: {user_id}. Message: {success_message}", 
                            {"user_id": user_id, "username": test_user_data["username"], "message": success_message})
                
                # Store user ID for further tests
                self.test_user_id = user_id
            else:
                self.log_test("POST /api/admin/users/create (create new users with temporary passwords)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/admin/users/create (create new users with temporary passwords)", False, f"Exception: {str(e)}")

        # Test 2: Verify user creation workflow and password management
        if self.test_user_id:
            # Test login with temporary password to verify workflow
            temp_login_data = {
                "username": test_user_data["username"],
                "password": test_user_data["temporary_password"],
                "user_type": "client"
            }
            
            try:
                # Create a separate session for user login test
                user_session = requests.Session()
                response = user_session.post(f"{BACKEND_URL}/auth/login", json=temp_login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    must_change_password = data.get("must_change_password", False)
                    user_token = data.get("token")
                    user_type = data.get("type")
                    
                    self.log_test("Verify user creation workflow and password management", True, 
                                f"Temporary password login successful. Must change password: {must_change_password}, User type: {user_type}, Token received: {bool(user_token)}", 
                                {"must_change_password": must_change_password, "user_type": user_type, "token_received": bool(user_token)})
                else:
                    self.log_test("Verify user creation workflow and password management", False, 
                                f"Temporary password login failed. HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Verify user creation workflow and password management", False, f"Exception: {str(e)}")

    def test_document_signing_system(self):
        """Test Document Signing System endpoints"""
        print("🔍 TESTING DOCUMENT SIGNING SYSTEM")
        print("=" * 50)
        
        # Test 1: GET /api/documents/categories (document categories)
        try:
            response = self.session.get(f"{BACKEND_URL}/documents/categories")
            if response.status_code == 200:
                data = response.json()
                shared_categories = data.get("shared_categories", [])
                admin_categories = data.get("admin_categories", [])
                
                self.log_test("GET /api/documents/categories (document categories)", True, 
                            f"Retrieved document categories. Shared: {len(shared_categories)} categories, Admin: {len(admin_categories)} categories", 
                            {"shared_categories": shared_categories, "admin_categories": admin_categories})
            else:
                self.log_test("GET /api/documents/categories (document categories)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/documents/categories (document categories)", False, f"Exception: {str(e)}")

        # Test 2: POST /api/documents/upload (document upload)
        try:
            # Create a test document for upload
            test_document_content = b"FIDUS CRM Backend Test Document\n\nThis document was created during CRM backend testing to verify document upload functionality.\n\nTest Details:\n- Created for signature workflow testing\n- Salvador Palma as default signee verification\n- Document signing system validation\n\nTimestamp: " + datetime.now().isoformat().encode()
            
            files = {"document": ("crm_test_document.txt", test_document_content, "text/plain")}
            data = {
                "category": "client_agreements",
                "uploader_id": "admin_001",
                "uploader_type": "admin"
            }
            
            response = self.session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
            if response.status_code == 200:
                response_data = response.json()
                document_id = response_data.get("document_id")
                file_name = response_data.get("file_name")
                category = response_data.get("category")
                
                self.log_test("POST /api/documents/upload (document upload)", True, 
                            f"Document uploaded successfully. Document ID: {document_id}, File: {file_name}, Category: {category}", 
                            {"document_id": document_id, "file_name": file_name, "category": category})
                
                # Store document ID for further tests
                self.test_document_id = document_id
            else:
                self.log_test("POST /api/documents/upload (document upload)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/documents/upload (document upload)", False, f"Exception: {str(e)}")

        # Test 3: POST /api/documents/{id}/send-for-signature (enhanced signature workflow)
        if self.test_document_id:
            # Test with Salvador Palma as default signee as specified in review
            signature_request = {
                "recipient_email": "chava@alyarglobal.com",  # Salvador's actual email
                "recipient_name": "Salvador Palma",
                "subject": "FIDUS Document Signature Request - CRM Backend Test",
                "message": "Dear Salvador,\n\nPlease review and sign this document as part of our CRM backend testing verification.\n\nThis tests the enhanced signature workflow with you as the default FIDUS signee.\n\nBest regards,\nFIDUS Investment Management",
                "signature_required": True
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/documents/{self.test_document_id}/send-for-signature", 
                                           json=signature_request)
                if response.status_code == 200:
                    data = response.json()
                    gmail_message_id = data.get("gmail_message_id")
                    success = data.get("success", False)
                    
                    self.log_test("POST /api/documents/{id}/send-for-signature (enhanced signature workflow)", True, 
                                f"Signature request sent to Salvador Palma. Gmail Message ID: {gmail_message_id}, Success: {success}", 
                                {"gmail_message_id": gmail_message_id, "success": success, "recipient": "Salvador Palma"})
                else:
                    self.log_test("POST /api/documents/{id}/send-for-signature (enhanced signature workflow)", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/documents/{id}/send-for-signature (enhanced signature workflow)", False, f"Exception: {str(e)}")

        # Test 4: POST /api/documents/{id}/send-notification (email notifications)
        if self.test_document_id:
            notification_request = {
                "recipient_email": "chava@alyarglobal.com",  # Salvador's actual email
                "subject": "FIDUS Document Notification - CRM Backend Test",
                "message": "Dear Salvador,\n\nThis is a test notification for the document signing workflow verification.\n\nThe CRM backend testing is validating email notification functionality as part of the enhanced document signing system.\n\nBest regards,\nFIDUS Investment Management"
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/documents/{self.test_document_id}/send-notification", 
                                           json=notification_request)
                if response.status_code == 200:
                    data = response.json()
                    notification_sent = data.get("success", False)
                    message = data.get("message", "")
                    
                    self.log_test("POST /api/documents/{id}/send-notification (email notifications)", True, 
                                f"Email notification sent to Salvador Palma. Success: {notification_sent}, Message: {message}", 
                                {"notification_sent": notification_sent, "message": message, "recipient": "Salvador Palma"})
                else:
                    self.log_test("POST /api/documents/{id}/send-notification (email notifications)", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/documents/{id}/send-notification (email notifications)", False, f"Exception: {str(e)}")

    def test_enhanced_functionality_verification(self):
        """Test Enhanced Functionality Verification with JWT authentication"""
        print("🔍 TESTING ENHANCED FUNCTIONALITY VERIFICATION")
        print("=" * 50)
        
        # Test 1: Verify all endpoints work with proper JWT authentication
        jwt_test_endpoints = [
            ("GET", "/crm/prospects", "CRM prospects endpoint"),
            ("GET", "/crm/prospects/pipeline", "CRM pipeline endpoint"),
            ("GET", "/documents/categories", "Document categories endpoint"),
            ("GET", "/admin/documents", "Admin documents endpoint")
        ]
        
        for method, endpoint, description in jwt_test_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    self.log_test(f"JWT Authentication - {description}", True, 
                                f"Endpoint {endpoint} accessible with JWT token. HTTP 200 OK")
                elif response.status_code == 401:
                    self.log_test(f"JWT Authentication - {description}", False, 
                                f"JWT authentication failed for {endpoint}. HTTP 401 Unauthorized", response.text)
                else:
                    self.log_test(f"JWT Authentication - {description}", False, 
                                f"Unexpected response for {endpoint}. HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test(f"JWT Authentication - {description}", False, f"Exception accessing {endpoint}: {str(e)}")

        # Test 2: Test complete prospect-to-client conversion workflow
        if self.test_prospect_id:
            try:
                # Get updated prospect details to verify complete workflow
                response = self.session.get(f"{BACKEND_URL}/crm/prospects")
                if response.status_code == 200:
                    data = response.json()
                    prospects = data.get("prospects", [])
                    test_prospect = next((p for p in prospects if p.get("id") == self.test_prospect_id), None)
                    
                    if test_prospect:
                        stage = test_prospect.get("stage")
                        converted = test_prospect.get("converted_to_client", False)
                        aml_status = test_prospect.get("aml_kyc_status")
                        client_id = test_prospect.get("client_id")
                        
                        workflow_complete = (stage == "won" and converted and aml_status == "clear" and client_id)
                        
                        self.log_test("Complete prospect-to-client conversion workflow", workflow_complete, 
                                    f"Workflow status - Stage: {stage}, Converted: {converted}, AML Status: {aml_status}, Client ID: {client_id}", 
                                    {"stage": stage, "converted": converted, "aml_status": aml_status, "client_id": client_id, "workflow_complete": workflow_complete})
                    else:
                        self.log_test("Complete prospect-to-client conversion workflow", False, 
                                    f"Test prospect {self.test_prospect_id} not found in prospects list")
                else:
                    self.log_test("Complete prospect-to-client conversion workflow", False, 
                                f"Failed to retrieve prospects. HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Complete prospect-to-client conversion workflow", False, f"Exception: {str(e)}")

        # Test 3: Validate document signing workflow with Salvador Palma as default signee
        if self.test_document_id:
            try:
                response = self.session.get(f"{BACKEND_URL}/documents/{self.test_document_id}/status")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    document_info = data.get("document", {})
                    
                    self.log_test("Document signing workflow with Salvador Palma as default signee", True, 
                                f"Document status retrieved successfully. Status: {status}, Document info available: {bool(document_info)}", 
                                {"document_status": status, "document_info": document_info})
                else:
                    self.log_test("Document signing workflow with Salvador Palma as default signee", False, 
                                f"Failed to get document status. HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Document signing workflow with Salvador Palma as default signee", False, f"Exception: {str(e)}")

    def generate_comprehensive_summary(self):
        """Generate comprehensive test summary with detailed analysis"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 FIDUS CRM & ENHANCED FUNCTIONALITY BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Completion Time: {datetime.now().isoformat()}")
        print()
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results by test area
        test_categories = {
            "CRM Pipeline System": [],
            "User Administration System": [],
            "Document Signing System": [],
            "Enhanced Functionality Verification": [],
            "Authentication": []
        }
        
        for test in self.test_results:
            test_name = test["test_name"]
            if "crm" in test_name.lower() or "prospect" in test_name.lower():
                test_categories["CRM Pipeline System"].append(test)
            elif "user" in test_name.lower() or "admin/users" in test_name.lower():
                test_categories["User Administration System"].append(test)
            elif "document" in test_name.lower() or "signature" in test_name.lower():
                test_categories["Document Signing System"].append(test)
            elif "jwt" in test_name.lower() or "workflow" in test_name.lower():
                test_categories["Enhanced Functionality Verification"].append(test)
            elif "authentication" in test_name.lower():
                test_categories["Authentication"].append(test)
        
        # Print category summaries
        for category, tests in test_categories.items():
            if tests:
                category_passed = len([t for t in tests if t["success"]])
                category_total = len(tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                print(f"📋 {category.upper()}:")
                print(f"   Tests: {category_total}, Passed: {category_passed}, Success Rate: {category_rate:.1f}%")
                
                for test in tests:
                    status = "✅" if test["success"] else "❌"
                    print(f"   {status} {test['test_name']}")
                print()
        
        # Print failed tests details if any
        if failed_tests > 0:
            print("❌ FAILED TESTS DETAILS:")
            print("-" * 40)
            for test in self.test_results:
                if not test["success"]:
                    print(f"• {test['test_name']}")
                    print(f"  Details: {test['details']}")
                    if test.get('response_data'):
                        print(f"  Response: {test['response_data']}")
                    print()
        
        # Print key achievements
        print("🎉 KEY ACHIEVEMENTS:")
        print("-" * 20)
        key_achievements = [t for t in self.test_results if t["success"] and any(keyword in t["test_name"].lower() for keyword in ["create", "convert", "upload", "send-for-signature"])]
        for achievement in key_achievements:
            print(f"✅ {achievement['test_name']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_categories": {cat: len(tests) for cat, tests in test_categories.items() if tests},
            "test_results": self.test_results,
            "backend_url": BACKEND_URL,
            "completion_time": datetime.now().isoformat()
        }

    def run_all_tests(self):
        """Run all CRM and enhanced functionality backend tests"""
        print("🚀 STARTING FIDUS CRM & ENHANCED FUNCTIONALITY BACKEND TESTING")
        print("=" * 80)
        print("Testing newly implemented and enhanced functionality as requested in review:")
        print("1. CRM Pipeline System endpoints")
        print("2. User Administration System endpoints")  
        print("3. Document Signing System endpoints")
        print("4. Enhanced Functionality Verification with JWT authentication")
        print()
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            print("This indicates a fundamental issue with the JWT authentication system.")
            return self.generate_comprehensive_summary()
        
        # Step 2: Run all test suites
        self.test_crm_pipeline_system()
        self.test_user_administration_system()
        self.test_document_signing_system()
        self.test_enhanced_functionality_verification()
        
        # Step 3: Generate comprehensive summary
        return self.generate_comprehensive_summary()

def main():
    """Main test execution function"""
    tester = FIDUSCRMBackendTester()
    summary = tester.run_all_tests()
    
    # Save detailed results to file
    results_file = "/app/crm_backend_test_results.json"
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n📄 Detailed test results saved to: {results_file}")
    
    # Determine overall success
    success_threshold = 80.0  # 80% success rate required
    overall_success = summary["success_rate"] >= success_threshold
    
    if overall_success:
        print(f"🎉 OVERALL RESULT: SUCCESS (Success Rate: {summary['success_rate']:.1f}% >= {success_threshold}%)")
    else:
        print(f"❌ OVERALL RESULT: NEEDS ATTENTION (Success Rate: {summary['success_rate']:.1f}% < {success_threshold}%)")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)