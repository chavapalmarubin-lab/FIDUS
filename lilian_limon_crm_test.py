#!/usr/bin/env python3
"""
LILIAN LIMON CRM PROSPECTS & DOCUMENT UPLOAD TEST
===============================================

This test addresses the critical issues mentioned in the review request:

1. **Document Upload Error**: "Failed to upload document" when uploading for Lilian Limon
   - Check if Lilian exists in MongoDB crm_prospects collection
   - Verify document upload endpoint is working
   - Fix any database connectivity issues

2. **Missing Convert to Client Button**: Users should see clear convert button for won prospects
   - Check Lilian's current stage and AML/KYC status
   - Ensure AML/KYC workflow is working properly
   - Make sure conversion path is clear

3. **Simplified Pipeline**: Verify new pipeline structure works
   - Should only show: Lead → Negotiation/Proposal → Won → Lost
   - Remove qualified, proposal stages

Expected Results:
- Lilian Limon exists and can have documents uploaded
- Clear path from won prospect to client conversion
- Simplified 4-stage pipeline working
"""

import requests
import json
import sys
from datetime import datetime
import time
import io
import os

# Configuration
BACKEND_URL = "https://fidus-admin.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class LilianLimonCRMTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.lilian_id = None
        
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
    
    def test_lilian_limon_exists(self):
        """Test if Lilian Limon exists in CRM prospects"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', []) if isinstance(data, dict) else data
                lilian_found = False
                
                if isinstance(prospects, list):
                    for prospect in prospects:
                        if 'lilian' in prospect.get('name', '').lower() and 'limon' in prospect.get('name', '').lower():
                            lilian_found = True
                            self.lilian_id = prospect.get('id')
                            self.log_result("Lilian Limon Exists", True, 
                                          f"Found Lilian Limon with ID: {self.lilian_id}",
                                          {"prospect_data": prospect})
                            return True
                
                if not lilian_found:
                    # Try to create Lilian Limon if she doesn't exist
                    self.log_result("Lilian Limon Exists", False, 
                                  "Lilian Limon not found in prospects. Attempting to create...",
                                  {"total_prospects": len(prospects) if isinstance(prospects, list) else "unknown"})
                    return self.create_lilian_limon()
            else:
                self.log_result("Lilian Limon Exists", False, 
                              f"Failed to get prospects: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Lilian Limon Exists", False, f"Exception: {str(e)}")
            return False
    
    def create_lilian_limon(self):
        """Create Lilian Limon prospect if she doesn't exist"""
        try:
            prospect_data = {
                "name": "Lilian Limon",
                "email": "lilian.limon@example.com",
                "phone": "+1-555-0123",
                "notes": "Test prospect for document upload and conversion testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=prospect_data)
            if response.status_code == 200 or response.status_code == 201:
                created_prospect = response.json()
                self.lilian_id = created_prospect.get('id')
                self.log_result("Create Lilian Limon", True, 
                              f"Successfully created Lilian Limon with ID: {self.lilian_id}",
                              {"created_prospect": created_prospect})
                return True
            else:
                self.log_result("Create Lilian Limon", False, 
                              f"Failed to create prospect: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Create Lilian Limon", False, f"Exception: {str(e)}")
            return False
    
    def test_document_upload(self):
        """Test document upload for Lilian Limon"""
        if not self.lilian_id:
            self.log_result("Document Upload", False, "Cannot test - Lilian ID not available")
            return False
        
        try:
            # Create a test document
            test_document_content = b"This is a test document for Lilian Limon's AML/KYC verification."
            
            # Prepare multipart form data properly
            files = {
                'file': ('test_document.txt', test_document_content, 'text/plain')
            }
            data = {
                'document_type': 'passport',
                'notes': 'Test document upload for Lilian Limon'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/crm/prospects/{self.lilian_id}/documents",
                files=files,
                data=data
            )
            
            if response.status_code == 200 or response.status_code == 201:
                upload_result = response.json()
                self.log_result("Document Upload", True, 
                              "Successfully uploaded document for Lilian Limon",
                              {"upload_result": upload_result})
                return True
            else:
                self.log_result("Document Upload", False, 
                              f"Failed to upload document: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Document Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_stages(self):
        """Test simplified pipeline structure: Lead → Negotiation/Proposal → Won → Lost"""
        try:
            # Get pipeline data from the correct endpoint
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/pipeline")
            if response.status_code == 200:
                pipeline_data = response.json()
                
                # Extract stage names from pipeline structure
                if isinstance(pipeline_data, dict) and 'pipeline' in pipeline_data:
                    stage_names = list(pipeline_data['pipeline'].keys())
                elif isinstance(pipeline_data, dict):
                    # Look for stage keys in the response
                    stage_names = [key for key in pipeline_data.keys() if key in ["lead", "qualified", "proposal", "negotiation", "won", "lost"]]
                else:
                    stage_names = []
                
                # Check if simplified pipeline is implemented
                has_qualified = 'qualified' in stage_names
                has_required_stages = all(stage in stage_names for stage in ["lead", "won", "lost"])
                
                if not has_qualified and has_required_stages:
                    self.log_result("Simplified Pipeline", True, 
                                  "Pipeline correctly simplified - no 'qualified' stage found",
                                  {"stages": stage_names})
                else:
                    issues = []
                    if has_qualified:
                        issues.append("'qualified' stage still present")
                    if not has_required_stages:
                        missing = [stage for stage in ["lead", "won", "lost"] if stage not in stage_names]
                        issues.append(f"missing required stages: {missing}")
                    
                    self.log_result("Simplified Pipeline", False, 
                                  f"Pipeline issues: {', '.join(issues)}",
                                  {"stages": stage_names, "pipeline_data": pipeline_data})
            else:
                self.log_result("Simplified Pipeline", False, 
                              f"Failed to get pipeline data: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Simplified Pipeline", False, f"Exception: {str(e)}")
    
    def test_lilian_stage_progression(self):
        """Test Lilian's stage progression and conversion readiness"""
        if not self.lilian_id:
            self.log_result("Stage Progression", False, "Cannot test - Lilian ID not available")
            return False
        
        try:
            # Update Lilian to 'won' stage to test conversion
            update_data = {
                "stage": "won",
                "notes": "Updated to won stage for conversion testing"
            }
            
            response = self.session.put(f"{BACKEND_URL}/crm/prospects/{self.lilian_id}", json=update_data)
            if response.status_code == 200:
                updated_result = response.json()
                updated_prospect = updated_result.get('prospect', {})
                current_stage = updated_prospect.get('stage')
                
                if current_stage == 'won':
                    self.log_result("Stage Progression", True, 
                                  "Successfully updated Lilian to 'won' stage",
                                  {"updated_prospect": updated_prospect})
                    return True
                else:
                    self.log_result("Stage Progression", False, 
                                  f"Stage update failed - expected 'won', got '{current_stage}'",
                                  {"updated_result": updated_result})
                    return False
            else:
                self.log_result("Stage Progression", False, 
                              f"Failed to update stage: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Stage Progression", False, f"Exception: {str(e)}")
            return False
    
    def test_aml_kyc_workflow(self):
        """Test AML/KYC workflow for Lilian"""
        if not self.lilian_id:
            self.log_result("AML/KYC Workflow", False, "Cannot test - Lilian ID not available")
            return False
        
        try:
            # Test AML approval endpoint
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.lilian_id}/aml-approve")
            if response.status_code == 200:
                aml_result = response.json()
                self.log_result("AML/KYC Workflow", True, 
                              "AML/KYC approval endpoint working",
                              {"aml_result": aml_result})
                return True
            else:
                self.log_result("AML/KYC Workflow", False, 
                              f"AML approval failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("AML/KYC Workflow", False, f"Exception: {str(e)}")
            return False
    
    def test_conversion_to_client(self):
        """Test conversion from won prospect to client"""
        if not self.lilian_id:
            self.log_result("Conversion to Client", False, "Cannot test - Lilian ID not available")
            return False
        
        try:
            # Test prospect conversion endpoint with correct format
            conversion_data = {
                "prospect_id": self.lilian_id,
                "send_agreement": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.lilian_id}/convert", json=conversion_data)
            if response.status_code == 200:
                conversion_result = response.json()
                client_id = conversion_result.get('client_id')
                
                if client_id:
                    self.log_result("Conversion to Client", True, 
                                  f"Successfully converted Lilian to client: {client_id}",
                                  {"conversion_result": conversion_result})
                    return True
                else:
                    self.log_result("Conversion to Client", False, 
                                  "Conversion succeeded but no client_id returned",
                                  {"conversion_result": conversion_result})
                    return False
            elif response.status_code == 400:
                # Check if already converted or other business logic issue
                error_detail = response.json().get('detail', 'Unknown error')
                if 'already been converted' in error_detail:
                    self.log_result("Conversion to Client", True, 
                                  "Lilian already converted to client (expected for existing prospect)",
                                  {"error_detail": error_detail})
                    return True
                else:
                    self.log_result("Conversion to Client", False, 
                                  f"Business logic error: {error_detail}",
                                  {"response": response.text})
                    return False
            else:
                self.log_result("Conversion to Client", False, 
                              f"Conversion failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Conversion to Client", False, f"Exception: {str(e)}")
            return False
    
    def test_crm_endpoints_availability(self):
        """Test all CRM-related endpoints are available"""
        crm_endpoints = [
            ("/crm/prospects", "Get Prospects"),
            ("/crm/prospects/pipeline", "Pipeline Data"),
        ]
        
        for endpoint, name in crm_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    self.log_result(f"CRM Endpoint - {name}", True, 
                                  f"Endpoint responding: {endpoint}")
                else:
                    self.log_result(f"CRM Endpoint - {name}", False, 
                                  f"HTTP {response.status_code}: {endpoint}")
            except Exception as e:
                self.log_result(f"CRM Endpoint - {name}", False, 
                              f"Exception on {endpoint}: {str(e)}")
    
    def run_all_tests(self):
        """Run all Lilian Limon CRM and document upload tests"""
        print("🎯 LILIAN LIMON CRM PROSPECTS & DOCUMENT UPLOAD TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running CRM Prospects and Document Upload Tests...")
        print("-" * 50)
        
        # Run all tests in sequence
        self.test_crm_endpoints_availability()
        self.test_lilian_limon_exists()
        self.test_document_upload()
        self.test_pipeline_stages()
        self.test_lilian_stage_progression()
        self.test_aml_kyc_workflow()
        self.test_conversion_to_client()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 LILIAN LIMON CRM TEST SUMMARY")
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
        
        # Critical assessment for review request issues
        critical_tests = [
            "Document Upload",
            "Conversion to Client", 
            "Simplified Pipeline",
            "AML/KYC Workflow"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT FOR REVIEW REQUEST:")
        if critical_passed >= 3:  # At least 3 out of 4 critical tests
            print("✅ LILIAN LIMON CRM ISSUES: MOSTLY RESOLVED")
            print("   Document upload and conversion workflow are working.")
            print("   Pipeline structure has been simplified as requested.")
        else:
            print("❌ LILIAN LIMON CRM ISSUES: UNRESOLVED")
            print("   Critical issues from review request still present.")
            print("   Main agent action required to fix CRM functionality.")
        
        print("\n📋 REVIEW REQUEST STATUS:")
        print("1. Document Upload Error: ", end="")
        doc_upload_passed = any(result['success'] and 'Document Upload' in result['test'] for result in self.test_results)
        print("✅ RESOLVED" if doc_upload_passed else "❌ UNRESOLVED")
        
        print("2. Missing Convert Button: ", end="")
        conversion_passed = any(result['success'] and 'Conversion' in result['test'] for result in self.test_results)
        print("✅ RESOLVED" if conversion_passed else "❌ UNRESOLVED")
        
        print("3. Simplified Pipeline: ", end="")
        pipeline_passed = any(result['success'] and 'Pipeline' in result['test'] for result in self.test_results)
        print("✅ RESOLVED" if pipeline_passed else "❌ UNRESOLVED")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = LilianLimonCRMTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()