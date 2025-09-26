#!/usr/bin/env python3
"""
FIDUS Investment Management - Simplified Pipeline Testing
Testing the simplified prospect pipeline: lead → negotiation → won → lost
"""

import requests
import json
import sys
from datetime import datetime, timezone
import uuid

# Configuration
BACKEND_URL = "https://mockdb-cleanup.preview.emergentagent.com/api"

class SimplifiedPipelineTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No token received in response")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_get_existing_prospects(self):
        """Test getting existing prospects to check for old stages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                pipeline_stats = data.get('pipeline_stats', {})
                
                # Check for old stages that should be migrated
                old_stages_found = {
                    'qualified': pipeline_stats.get('qualified', 0),
                    'proposal': pipeline_stats.get('proposal', 0)
                }
                
                # Check if Lilian Limon exists and her stage
                lilian_found = False
                lilian_stage = None
                for prospect in prospects:
                    if 'lilian' in prospect.get('name', '').lower() and 'limon' in prospect.get('name', '').lower():
                        lilian_found = True
                        lilian_stage = prospect.get('stage')
                        break
                
                details = {
                    'total_prospects': len(prospects),
                    'pipeline_stats': pipeline_stats,
                    'old_stages_found': old_stages_found,
                    'lilian_found': lilian_found,
                    'lilian_stage': lilian_stage,
                    'simplified_stages': {
                        'lead': pipeline_stats.get('lead', 0),
                        'negotiation': pipeline_stats.get('negotiation', 0),
                        'won': pipeline_stats.get('won', 0),
                        'lost': pipeline_stats.get('lost', 0)
                    }
                }
                
                # Check if old stages still exist
                has_old_stages = old_stages_found['qualified'] > 0 or old_stages_found['proposal'] > 0
                
                if has_old_stages:
                    self.log_result("Check Existing Prospects", False, 
                                  f"Found old stages: qualified={old_stages_found['qualified']}, proposal={old_stages_found['proposal']}", 
                                  details)
                else:
                    self.log_result("Check Existing Prospects", True, 
                                  f"All prospects using simplified pipeline. Total: {len(prospects)}", 
                                  details)
                
                return data
            else:
                self.log_result("Check Existing Prospects", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Check Existing Prospects", False, f"Exception: {str(e)}")
            return None
    
    def test_create_test_prospect(self):
        """Create a new test prospect in 'lead' stage"""
        try:
            test_prospect_data = {
                "name": "Test Pipeline Prospect",
                "email": f"test.pipeline.{uuid.uuid4().hex[:8]}@fidus.com",
                "phone": "+1-555-TEST-001",
                "notes": "Test prospect for simplified pipeline validation"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect_data)
            
            if response.status_code == 200:
                data = response.json()
                prospect_id = data.get('prospect_id')
                prospect = data.get('prospect', {})
                
                # Verify prospect starts in 'lead' stage
                if prospect.get('stage') == 'lead':
                    self.log_result("Create Test Prospect", True, 
                                  f"Created prospect {prospect_id} in 'lead' stage", 
                                  {'prospect_id': prospect_id, 'prospect': prospect})
                    return prospect_id
                else:
                    self.log_result("Create Test Prospect", False, 
                                  f"Prospect created but not in 'lead' stage: {prospect.get('stage')}")
                    return None
            else:
                self.log_result("Create Test Prospect", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Create Test Prospect", False, f"Exception: {str(e)}")
            return None
    
    def test_move_prospect_through_pipeline(self, prospect_id):
        """Test moving prospect through simplified pipeline: lead → negotiation → won"""
        if not prospect_id:
            self.log_result("Move Through Pipeline", False, "No prospect ID provided")
            return False
        
        stages_to_test = [
            ('negotiation', 'Move to Negotiation'),
            ('won', 'Move to Won')
        ]
        
        success_count = 0
        
        for stage, test_name in stages_to_test:
            try:
                update_data = {"stage": stage}
                response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json=update_data)
                
                if response.status_code == 200:
                    data = response.json()
                    updated_prospect = data.get('prospect', {})
                    
                    if updated_prospect.get('stage') == stage:
                        self.log_result(test_name, True, 
                                      f"Successfully moved prospect to '{stage}' stage", 
                                      {'prospect_id': prospect_id, 'stage': stage})
                        success_count += 1
                    else:
                        self.log_result(test_name, False, 
                                      f"Stage update failed. Expected '{stage}', got '{updated_prospect.get('stage')}'")
                else:
                    self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(test_name, False, f"Exception: {str(e)}")
        
        return success_count == len(stages_to_test)
    
    def test_invalid_stage_rejection(self, prospect_id):
        """Test that old stages are rejected"""
        if not prospect_id:
            self.log_result("Invalid Stage Rejection", False, "No prospect ID provided")
            return False
        
        old_stages = ['qualified', 'proposal']
        rejection_count = 0
        
        for old_stage in old_stages:
            try:
                update_data = {"stage": old_stage}
                response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json=update_data)
                
                # Should get 400 error for invalid stage
                if response.status_code == 400:
                    self.log_result(f"Reject '{old_stage}' Stage", True, 
                                  f"Correctly rejected old stage '{old_stage}'", 
                                  {'error_response': response.text})
                    rejection_count += 1
                else:
                    self.log_result(f"Reject '{old_stage}' Stage", False, 
                                  f"Should have rejected '{old_stage}' stage but got HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Reject '{old_stage}' Stage", False, f"Exception: {str(e)}")
        
        return rejection_count == len(old_stages)
    
    def test_aml_kyc_process(self, prospect_id):
        """Test AML/KYC process for won prospect"""
        if not prospect_id:
            self.log_result("AML/KYC Process", False, "No prospect ID provided")
            return False
        
        try:
            # First run AML/KYC check
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/aml-kyc")
            
            if response.status_code == 200:
                aml_data = response.json()
                self.log_result("AML/KYC Check", True, 
                              "AML/KYC check completed successfully", 
                              {'aml_result': aml_data})
                
                # Then approve AML/KYC
                approve_response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/aml-approve")
                
                if approve_response.status_code == 200:
                    approve_data = approve_response.json()
                    self.log_result("AML/KYC Approval", True, 
                                  "AML/KYC approved successfully", 
                                  {'approval_result': approve_data})
                    return True
                else:
                    self.log_result("AML/KYC Approval", False, 
                                  f"HTTP {approve_response.status_code}: {approve_response.text}")
                    return False
            else:
                self.log_result("AML/KYC Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("AML/KYC Process", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_to_client_conversion(self, prospect_id):
        """Test converting won prospect to client"""
        if not prospect_id:
            self.log_result("Prospect to Client Conversion", False, "No prospect ID provided")
            return False
        
        try:
            conversion_data = {
                "prospect_id": prospect_id,
                "send_agreement": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/convert", json=conversion_data)
            
            if response.status_code == 200:
                data = response.json()
                client_id = data.get('client_id')
                username = data.get('username')
                
                self.log_result("Prospect to Client Conversion", True, 
                              f"Successfully converted prospect to client {client_id} (username: {username})", 
                              {'client_id': client_id, 'username': username, 'conversion_data': data})
                return client_id
            else:
                self.log_result("Prospect to Client Conversion", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Prospect to Client Conversion", False, f"Exception: {str(e)}")
            return None
    
    def test_document_upload_functionality(self, prospect_id):
        """Test document upload at different stages"""
        if not prospect_id:
            self.log_result("Document Upload Test", False, "No prospect ID provided")
            return False
        
        try:
            # Test getting documents for prospect
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/{prospect_id}/documents")
            
            if response.status_code == 200:
                documents_data = response.json()
                self.log_result("Document Upload Test", True, 
                              "Document endpoint accessible", 
                              {'documents': documents_data})
                return True
            else:
                self.log_result("Document Upload Test", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Document Upload Test", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_statistics(self):
        """Test pipeline statistics endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/pipeline")
            
            if response.status_code == 200:
                data = response.json()
                pipeline_data = data.get('pipeline', {})
                
                # Check that only simplified stages are present
                expected_stages = ['lead', 'negotiation', 'won', 'lost']
                unexpected_stages = []
                
                for stage in pipeline_data.keys():
                    if stage not in expected_stages:
                        unexpected_stages.append(stage)
                
                if not unexpected_stages:
                    self.log_result("Pipeline Statistics", True, 
                                  "Pipeline contains only simplified stages", 
                                  {'pipeline': pipeline_data})
                    return True
                else:
                    self.log_result("Pipeline Statistics", False, 
                                  f"Found unexpected stages: {unexpected_stages}", 
                                  {'pipeline': pipeline_data})
                    return False
            else:
                self.log_result("Pipeline Statistics", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Pipeline Statistics", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive simplified pipeline test"""
        print("🎯 FIDUS SIMPLIFIED PIPELINE TESTING STARTED")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Check existing prospects for old stages
        existing_prospects = self.test_get_existing_prospects()
        
        # Step 3: Test pipeline statistics
        self.test_pipeline_statistics()
        
        # Step 4: Create test prospect
        test_prospect_id = self.test_create_test_prospect()
        
        if test_prospect_id:
            # Step 5: Test invalid stage rejection
            self.test_invalid_stage_rejection(test_prospect_id)
            
            # Step 6: Move through simplified pipeline
            pipeline_success = self.test_move_prospect_through_pipeline(test_prospect_id)
            
            if pipeline_success:
                # Step 7: Test AML/KYC process
                aml_success = self.test_aml_kyc_process(test_prospect_id)
                
                if aml_success:
                    # Step 8: Test prospect to client conversion
                    client_id = self.test_prospect_to_client_conversion(test_prospect_id)
                    
                    if client_id:
                        print(f"✅ Complete pipeline test successful! Client created: {client_id}")
            
            # Step 9: Test document upload functionality
            self.test_document_upload_functionality(test_prospect_id)
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 SIMPLIFIED PIPELINE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"  • {result['test']}: {result['message']}")
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        
        # Check for old stages
        old_stage_tests = [r for r in self.test_results if 'old stages' in r['message'].lower()]
        if old_stage_tests:
            for test in old_stage_tests:
                if not test['success']:
                    print(f"  ⚠️  Old stages still present in system")
                else:
                    print(f"  ✅ All prospects using simplified pipeline")
        
        # Check pipeline functionality
        pipeline_tests = [r for r in self.test_results if 'pipeline' in r['test'].lower()]
        pipeline_success = all(t['success'] for t in pipeline_tests)
        if pipeline_success:
            print(f"  ✅ Simplified pipeline (lead → negotiation → won → lost) working correctly")
        else:
            print(f"  ❌ Pipeline functionality issues detected")
        
        # Check conversion process
        conversion_tests = [r for r in self.test_results if 'conversion' in r['test'].lower()]
        if conversion_tests and all(t['success'] for t in conversion_tests):
            print(f"  ✅ Lead-to-client conversion process working")
        elif conversion_tests:
            print(f"  ❌ Lead-to-client conversion issues detected")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    tester = SimplifiedPipelineTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("🎉 Simplified pipeline testing completed!")
    else:
        print("❌ Testing failed to complete")
        sys.exit(1)

if __name__ == "__main__":
    main()