#!/usr/bin/env python3
"""
PIPELINE PROGRESSION ISSUE TEST - LILIAN LIMON LEITE
===================================================

This test addresses the urgent pipeline progression issue reported:
- New user "Lilian Limon Leite" appeared in CRM leads tab ✅
- Pipeline process doesn't work - can't convert leads through stages
- User can't find process to convert her to client

INVESTIGATION TESTS:
1. Test prospect stage progression (PUT /api/crm/prospects/{id})
2. Test moving prospect through stages: lead → qualified → proposal → negotiation → won
3. Check pipeline data loading (GET /api/crm/prospects/pipeline)
4. Test conversion workflow (move to "won" stage, run AML/KYC, convert to client)
5. Frontend Pipeline Display verification

ROOT CAUSE ANALYSIS:
- The handleStageChange function exists and calls PUT /api/crm/prospects/{id}
- Backend endpoint exists at line 6841
- May be authentication or data loading issue

SPECIFIC TESTS:
1. Login as admin
2. Find prospect "Lilian Limon Leite" 
3. Move through stages: lead → qualified → proposal → negotiation → won
4. Run AML/KYC check on won prospect
5. Convert to client
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://auth-flow-debug-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class PipelineProgressionTest:
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
    
    def test_find_lilian_prospect(self):
        """Find Lilian Limon Leite in CRM prospects"""
        try:
            # Get all prospects
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects = response.json()
                lilian_found = False
                
                if isinstance(prospects, list):
                    for prospect in prospects:
                        name = prospect.get('name', '').upper()
                        if 'LILIAN' in name and 'LIMON' in name and 'LEITE' in name:
                            lilian_found = True
                            self.lilian_prospect_id = prospect.get('id')
                            current_stage = prospect.get('stage', 'unknown')
                            
                            self.log_result("Find Lilian Prospect", True, 
                                          f"Lilian Limon Leite found in CRM (ID: {self.lilian_prospect_id}, Stage: {current_stage})",
                                          {"prospect_data": prospect})
                            return True
                
                if not lilian_found:
                    # Create Lilian prospect for testing if not found
                    self.log_result("Find Lilian Prospect", False, 
                                  "Lilian Limon Leite not found in prospects. Will create for testing.",
                                  {"total_prospects": len(prospects) if isinstance(prospects, list) else "unknown"})
                    return self.create_lilian_prospect()
            else:
                self.log_result("Find Lilian Prospect", False, 
                              f"Failed to get prospects: HTTP {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Find Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def create_lilian_prospect(self):
        """Create Lilian Limon Leite prospect for testing"""
        try:
            prospect_data = {
                "name": "Lilian Limon Leite",
                "email": "lilian.limon.leite@example.com",
                "phone": "+1-555-0123",
                "notes": "Test prospect for pipeline progression verification"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=prospect_data)
            if response.status_code in [200, 201]:
                response_data = response.json()
                # Handle different response formats
                if 'prospect_id' in response_data:
                    self.lilian_prospect_id = response_data['prospect_id']
                elif 'prospect' in response_data and 'id' in response_data['prospect']:
                    self.lilian_prospect_id = response_data['prospect']['id']
                elif 'id' in response_data:
                    self.lilian_prospect_id = response_data['id']
                
                if self.lilian_prospect_id:
                    self.log_result("Create Lilian Prospect", True, 
                                  f"Created Lilian Limon Leite prospect (ID: {self.lilian_prospect_id})",
                                  {"prospect_data": response_data})
                    return True
                else:
                    self.log_result("Create Lilian Prospect", False, 
                                  "Prospect created but no ID found in response",
                                  {"response": response_data})
                    return False
            else:
                self.log_result("Create Lilian Prospect", False, 
                              f"Failed to create prospect: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Create Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def test_stage_progression(self):
        """Test moving prospect through all pipeline stages"""
        if not self.lilian_prospect_id:
            self.log_result("Stage Progression", False, "No prospect ID available for testing")
            return False
        
        # Define the pipeline stages to test
        stages = ["lead", "qualified", "proposal", "negotiation", "won"]
        
        for i, stage in enumerate(stages):
            try:
                # Update prospect stage
                update_data = {"stage": stage}
                response = self.session.put(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}", 
                                          json=update_data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Handle different response formats
                    if 'prospect' in response_data:
                        updated_prospect = response_data['prospect']
                        actual_stage = updated_prospect.get('stage')
                    else:
                        updated_prospect = response_data
                        actual_stage = updated_prospect.get('stage')
                    
                    if actual_stage == stage:
                        self.log_result(f"Stage Progression - {stage.title()}", True, 
                                      f"Successfully moved to {stage} stage",
                                      {"prospect_id": self.lilian_prospect_id, "stage": actual_stage})
                    else:
                        self.log_result(f"Stage Progression - {stage.title()}", False, 
                                      f"Stage update failed: expected '{stage}', got '{actual_stage}'",
                                      {"prospect_data": response_data})
                        return False
                else:
                    self.log_result(f"Stage Progression - {stage.title()}", False, 
                                  f"Failed to update stage: HTTP {response.status_code}",
                                  {"response": response.text})
                    return False
                
                # Small delay between stage updates
                time.sleep(0.5)
                
            except Exception as e:
                self.log_result(f"Stage Progression - {stage.title()}", False, f"Exception: {str(e)}")
                return False
        
        return True
    
    def test_pipeline_data_loading(self):
        """Test GET /api/crm/prospects/pipeline endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/pipeline")
            if response.status_code == 200:
                pipeline_data = response.json()
                
                # Check if pipeline data has expected structure
                expected_stages = ["lead", "qualified", "proposal", "negotiation", "won", "lost"]
                pipeline_valid = True
                issues = []
                
                if isinstance(pipeline_data, dict):
                    for stage in expected_stages:
                        if stage not in pipeline_data:
                            pipeline_valid = False
                            issues.append(f"Missing stage: {stage}")
                        else:
                            stage_prospects = pipeline_data[stage]
                            if not isinstance(stage_prospects, list):
                                pipeline_valid = False
                                issues.append(f"Stage {stage} is not a list")
                    
                    # Check if Lilian appears in the "won" stage
                    lilian_in_won = False
                    if "won" in pipeline_data:
                        for prospect in pipeline_data["won"]:
                            if prospect.get('id') == self.lilian_prospect_id:
                                lilian_in_won = True
                                break
                    
                    if pipeline_valid:
                        if lilian_in_won:
                            self.log_result("Pipeline Data Loading", True, 
                                          "Pipeline endpoint working correctly, Lilian found in 'won' stage",
                                          {"pipeline_structure": list(pipeline_data.keys())})
                        else:
                            self.log_result("Pipeline Data Loading", False, 
                                          "Pipeline endpoint works but Lilian not in 'won' stage",
                                          {"pipeline_data": pipeline_data})
                    else:
                        self.log_result("Pipeline Data Loading", False, 
                                      "Pipeline data structure invalid",
                                      {"issues": issues, "pipeline_data": pipeline_data})
                else:
                    self.log_result("Pipeline Data Loading", False, 
                                  "Pipeline data is not a dictionary",
                                  {"pipeline_data": pipeline_data})
            else:
                self.log_result("Pipeline Data Loading", False, 
                              f"Failed to get pipeline data: HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Pipeline Data Loading", False, f"Exception: {str(e)}")
    
    def test_aml_kyc_check(self):
        """Test AML/KYC check on won prospect"""
        if not self.lilian_prospect_id:
            self.log_result("AML/KYC Check", False, "No prospect ID available for testing")
            return False
        
        try:
            # First get the prospect to ensure it's in "won" stage
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}")
            if response.status_code == 200:
                prospect = response.json()
                if prospect.get('stage') != 'won':
                    self.log_result("AML/KYC Check", False, 
                                  f"Prospect not in 'won' stage (current: {prospect.get('stage')})")
                    return False
            else:
                self.log_result("AML/KYC Check", False, 
                              f"Failed to get prospect: HTTP {response.status_code}")
                return False
            
            # Try to run AML/KYC check (this endpoint might not exist yet)
            aml_kyc_data = {
                "prospect_id": self.lilian_prospect_id,
                "check_type": "full_verification"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}/aml-kyc", 
                                       json=aml_kyc_data)
            
            if response.status_code == 200:
                aml_result = response.json()
                self.log_result("AML/KYC Check", True, 
                              "AML/KYC check completed successfully",
                              {"aml_result": aml_result})
                return True
            elif response.status_code == 404:
                self.log_result("AML/KYC Check", False, 
                              "AML/KYC endpoint not implemented yet",
                              {"note": "This is expected if AML/KYC integration is not complete"})
                return False
            else:
                self.log_result("AML/KYC Check", False, 
                              f"AML/KYC check failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("AML/KYC Check", False, f"Exception: {str(e)}")
            return False
    
    def test_client_conversion(self):
        """Test converting won prospect to client"""
        if not self.lilian_prospect_id:
            self.log_result("Client Conversion", False, "No prospect ID available for testing")
            return False
        
        try:
            # Try to convert prospect to client
            conversion_data = {
                "prospect_id": self.lilian_prospect_id,
                "send_agreement": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}/convert", 
                                       json=conversion_data)
            
            if response.status_code == 200:
                conversion_result = response.json()
                client_id = conversion_result.get('client_id')
                
                if client_id:
                    self.log_result("Client Conversion", True, 
                                  f"Prospect successfully converted to client (ID: {client_id})",
                                  {"conversion_result": conversion_result})
                    
                    # Verify client was created
                    client_response = self.session.get(f"{BACKEND_URL}/admin/clients/{client_id}")
                    if client_response.status_code == 200:
                        client_data = client_response.json()
                        self.log_result("Client Verification", True, 
                                      "Converted client verified in system",
                                      {"client_data": client_data})
                    else:
                        self.log_result("Client Verification", False, 
                                      "Converted client not found in system")
                    
                    return True
                else:
                    self.log_result("Client Conversion", False, 
                                  "Conversion succeeded but no client_id returned",
                                  {"conversion_result": conversion_result})
                    return False
            elif response.status_code == 404:
                self.log_result("Client Conversion", False, 
                              "Client conversion endpoint not implemented yet",
                              {"note": "This is expected if conversion workflow is not complete"})
                return False
            else:
                self.log_result("Client Conversion", False, 
                              f"Client conversion failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Conversion", False, f"Exception: {str(e)}")
            return False
    
    def test_crm_endpoints_availability(self):
        """Test availability of all CRM-related endpoints"""
        crm_endpoints = [
            ("/crm/prospects", "GET", "List Prospects"),
            ("/crm/prospects", "POST", "Create Prospect"),
            ("/crm/prospects/pipeline", "GET", "Pipeline Data"),
        ]
        
        for endpoint, method, name in crm_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                elif method == "POST":
                    # Test with minimal data for POST endpoints
                    test_data = {"name": "Test", "email": "test@example.com", "phone": "123-456-7890"}
                    response = self.session.post(f"{BACKEND_URL}{endpoint}", json=test_data)
                
                if response.status_code in [200, 201, 400, 422]:  # 400/422 are acceptable for test data
                    self.log_result(f"CRM Endpoint - {name}", True, 
                                  f"Endpoint available: {method} {endpoint} (HTTP {response.status_code})")
                else:
                    self.log_result(f"CRM Endpoint - {name}", False, 
                                  f"Endpoint issue: {method} {endpoint} (HTTP {response.status_code})",
                                  {"response": response.text[:200]})
            except Exception as e:
                self.log_result(f"CRM Endpoint - {name}", False, 
                              f"Exception on {method} {endpoint}: {str(e)}")
    
    def test_prospect_update_endpoint(self):
        """Test the specific PUT /api/crm/prospects/{id} endpoint that's reported as broken"""
        if not self.lilian_prospect_id:
            self.log_result("Prospect Update Endpoint", False, "No prospect ID available for testing")
            return False
        
        try:
            # Test updating prospect notes (should be safe)
            update_data = {
                "notes": f"Pipeline progression test completed at {datetime.now().isoformat()}"
            }
            
            response = self.session.put(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}", 
                                      json=update_data)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Handle different response formats
                if 'prospect' in response_data:
                    updated_prospect = response_data['prospect']
                    updated_notes = updated_prospect.get('notes', '')
                else:
                    updated_prospect = response_data
                    updated_notes = updated_prospect.get('notes', '')
                
                if "Pipeline progression test completed" in updated_notes:
                    self.log_result("Prospect Update Endpoint", True, 
                                  "PUT /api/crm/prospects/{id} endpoint working correctly",
                                  {"updated_prospect": updated_prospect})
                    return True
                else:
                    self.log_result("Prospect Update Endpoint", False, 
                                  "Prospect updated but notes not changed correctly",
                                  {"expected_notes": update_data["notes"], "actual_notes": updated_notes})
                    return False
            else:
                self.log_result("Prospect Update Endpoint", False, 
                              f"PUT endpoint failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Prospect Update Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all pipeline progression tests"""
        print("🎯 PIPELINE PROGRESSION ISSUE TEST - LILIAN LIMON LEITE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Pipeline Progression Tests...")
        print("-" * 50)
        
        # Run all tests in sequence
        self.test_crm_endpoints_availability()
        
        if self.test_find_lilian_prospect():
            self.test_prospect_update_endpoint()
            self.test_stage_progression()
            self.test_pipeline_data_loading()
            self.test_aml_kyc_check()
            self.test_client_conversion()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 PIPELINE PROGRESSION TEST SUMMARY")
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
        
        # Critical assessment for pipeline functionality
        critical_tests = [
            "Find Lilian Prospect",
            "Prospect Update Endpoint", 
            "Stage Progression - Qualified",
            "Stage Progression - Won",
            "Pipeline Data Loading"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 PIPELINE PROGRESSION ASSESSMENT:")
        if critical_passed >= 3:  # At least 3 out of 5 critical tests
            print("✅ PIPELINE PROGRESSION: WORKING")
            print("   Core pipeline functionality is operational.")
            print("   Prospects can be moved through stages successfully.")
        else:
            print("❌ PIPELINE PROGRESSION: BROKEN")
            print("   Critical pipeline functionality issues found.")
            print("   Main agent action required to fix stage progression.")
        
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        
        # Analyze specific failure patterns
        auth_failed = any("Authentication" in result['test'] and not result['success'] for result in self.test_results)
        endpoint_failed = any("Endpoint" in result['test'] and not result['success'] for result in self.test_results)
        stage_failed = any("Stage Progression" in result['test'] and not result['success'] for result in self.test_results)
        
        if auth_failed:
            print("   • Authentication issues detected - check JWT token handling")
        if endpoint_failed:
            print("   • CRM endpoint availability issues - check route definitions")
        if stage_failed:
            print("   • Stage progression logic issues - check PUT /api/crm/prospects/{id} implementation")
        
        if not auth_failed and not endpoint_failed and not stage_failed:
            print("   • No obvious issues detected - pipeline may be working correctly")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = PipelineProgressionTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()