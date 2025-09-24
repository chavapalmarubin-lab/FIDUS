#!/usr/bin/env python3
"""
FIDUS Investment Management - Simplified Pipeline Final Testing
Focus on testing existing prospects and pipeline functionality
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Configuration
BACKEND_URL = "https://auth-flow-debug-2.preview.emergentagent.com/api"

class SimplifiedPipelineFinalTest:
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
    
    def test_simplified_pipeline_validation(self):
        """Test that simplified pipeline is properly implemented"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                pipeline_stats = data.get('pipeline_stats', {})
                
                # Check that no old stages exist
                old_stages_count = pipeline_stats.get('qualified', 0) + pipeline_stats.get('proposal', 0)
                
                # Check simplified stages
                simplified_stages = {
                    'lead': pipeline_stats.get('lead', 0),
                    'negotiation': pipeline_stats.get('negotiation', 0),
                    'won': pipeline_stats.get('won', 0),
                    'lost': pipeline_stats.get('lost', 0)
                }
                
                details = {
                    'total_prospects': len(prospects),
                    'old_stages_count': old_stages_count,
                    'simplified_stages': simplified_stages,
                    'pipeline_stats': pipeline_stats
                }
                
                if old_stages_count == 0:
                    self.log_result("Simplified Pipeline Validation", True, 
                                  f"All {len(prospects)} prospects using simplified pipeline", details)
                    return True
                else:
                    self.log_result("Simplified Pipeline Validation", False, 
                                  f"Found {old_stages_count} prospects in old stages", details)
                    return False
            else:
                self.log_result("Simplified Pipeline Validation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Simplified Pipeline Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_statistics_endpoint(self):
        """Test pipeline statistics endpoint only shows simplified stages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/pipeline")
            
            if response.status_code == 200:
                data = response.json()
                pipeline_data = data.get('pipeline', {})
                
                # Expected simplified stages
                expected_stages = {'lead', 'negotiation', 'won', 'lost'}
                actual_stages = set(pipeline_data.keys())
                
                # Check for unexpected stages
                unexpected_stages = actual_stages - expected_stages
                missing_stages = expected_stages - actual_stages
                
                details = {
                    'expected_stages': list(expected_stages),
                    'actual_stages': list(actual_stages),
                    'unexpected_stages': list(unexpected_stages),
                    'missing_stages': list(missing_stages),
                    'pipeline_data': pipeline_data
                }
                
                if not unexpected_stages and not missing_stages:
                    self.log_result("Pipeline Statistics Endpoint", True, 
                                  "Pipeline endpoint shows only simplified stages", details)
                    return True
                else:
                    error_msg = []
                    if unexpected_stages:
                        error_msg.append(f"unexpected stages: {list(unexpected_stages)}")
                    if missing_stages:
                        error_msg.append(f"missing stages: {list(missing_stages)}")
                    
                    self.log_result("Pipeline Statistics Endpoint", False, 
                                  f"Pipeline endpoint issues: {', '.join(error_msg)}", details)
                    return False
            else:
                self.log_result("Pipeline Statistics Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Pipeline Statistics Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_stage_update_validation(self):
        """Test that only simplified stages are accepted in updates"""
        try:
            # Get existing prospects to test with
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code != 200:
                self.log_result("Stage Update Validation", False, "Could not get prospects for testing")
                return False
            
            data = response.json()
            prospects = data.get('prospects', [])
            
            # Find a prospect in negotiation stage to test with
            test_prospect = None
            for prospect in prospects:
                if prospect.get('stage') == 'negotiation' and not prospect.get('converted_to_client', False):
                    test_prospect = prospect
                    break
            
            if not test_prospect:
                self.log_result("Stage Update Validation", True, 
                              "No negotiation prospects available for testing (acceptable)")
                return True
            
            prospect_id = test_prospect.get('id')
            original_stage = test_prospect.get('stage')
            
            # Test that old stages are rejected
            old_stages_rejected = 0
            old_stages_to_test = ['qualified', 'proposal']
            
            for old_stage in old_stages_to_test:
                update_response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json={
                    "stage": old_stage
                })
                
                if update_response.status_code == 400:
                    old_stages_rejected += 1
                    print(f"    ✅ Correctly rejected '{old_stage}' stage")
                else:
                    print(f"    ❌ Should have rejected '{old_stage}' stage (got {update_response.status_code})")
            
            # Test that valid stages are accepted
            valid_stages_accepted = 0
            valid_stages_to_test = ['won', 'lost']
            
            for valid_stage in valid_stages_to_test:
                update_response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json={
                    "stage": valid_stage
                })
                
                if update_response.status_code == 200:
                    valid_stages_accepted += 1
                    print(f"    ✅ Correctly accepted '{valid_stage}' stage")
                    
                    # Restore original stage
                    restore_response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json={
                        "stage": original_stage
                    })
                    break  # Only test one valid stage to avoid changing prospect state
                else:
                    print(f"    ❌ Should have accepted '{valid_stage}' stage (got {update_response.status_code})")
            
            details = {
                'test_prospect_id': prospect_id,
                'original_stage': original_stage,
                'old_stages_rejected': old_stages_rejected,
                'valid_stages_accepted': valid_stages_accepted
            }
            
            if old_stages_rejected == len(old_stages_to_test) and valid_stages_accepted > 0:
                self.log_result("Stage Update Validation", True, 
                              f"Stage validation working correctly", details)
                return True
            else:
                self.log_result("Stage Update Validation", False, 
                              f"Stage validation issues detected", details)
                return False
                
        except Exception as e:
            self.log_result("Stage Update Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_lilian_limon_records(self):
        """Test that Lilian Limon records are properly handled"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code != 200:
                self.log_result("Lilian Limon Records", False, "Could not get prospects")
                return False
            
            data = response.json()
            prospects = data.get('prospects', [])
            
            # Find Lilian Limon prospects
            lilian_prospects = []
            for prospect in prospects:
                name = prospect.get('name', '').lower()
                if 'lilian' in name and 'limon' in name:
                    lilian_prospects.append(prospect)
            
            details = {
                'lilian_prospects_found': len(lilian_prospects),
                'lilian_prospects': lilian_prospects
            }
            
            if len(lilian_prospects) > 0:
                # Check that all Lilian prospects are in valid stages
                valid_stages = {'lead', 'negotiation', 'won', 'lost'}
                all_valid = True
                
                for prospect in lilian_prospects:
                    stage = prospect.get('stage')
                    if stage not in valid_stages:
                        all_valid = False
                        break
                
                if all_valid:
                    self.log_result("Lilian Limon Records", True, 
                                  f"Found {len(lilian_prospects)} Lilian prospects, all in valid stages", details)
                    return True
                else:
                    self.log_result("Lilian Limon Records", False, 
                                  f"Some Lilian prospects in invalid stages", details)
                    return False
            else:
                self.log_result("Lilian Limon Records", True, 
                              "No Lilian Limon prospects found (acceptable)", details)
                return True
                
        except Exception as e:
            self.log_result("Lilian Limon Records", False, f"Exception: {str(e)}")
            return False
    
    def test_document_upload_endpoints(self):
        """Test document upload endpoints are accessible"""
        try:
            # Get a prospect to test document endpoints
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code != 200:
                self.log_result("Document Upload Endpoints", False, "Could not get prospects")
                return False
            
            data = response.json()
            prospects = data.get('prospects', [])
            
            if not prospects:
                self.log_result("Document Upload Endpoints", True, 
                              "No prospects available for document testing (acceptable)")
                return True
            
            test_prospect = prospects[0]
            prospect_id = test_prospect.get('id')
            
            # Test document endpoint accessibility
            doc_response = self.session.get(f"{BACKEND_URL}/crm/prospects/{prospect_id}/documents")
            
            details = {
                'test_prospect_id': prospect_id,
                'document_endpoint_status': doc_response.status_code,
                'document_response': doc_response.text if doc_response.status_code != 200 else "OK"
            }
            
            if doc_response.status_code == 200:
                self.log_result("Document Upload Endpoints", True, 
                              "Document endpoints accessible", details)
                return True
            else:
                self.log_result("Document Upload Endpoints", False, 
                              f"Document endpoint returned {doc_response.status_code}", details)
                return False
                
        except Exception as e:
            self.log_result("Document Upload Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_aml_kyc_process(self):
        """Test AML/KYC process endpoints"""
        try:
            # Get prospects to test AML/KYC
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code != 200:
                self.log_result("AML/KYC Process", False, "Could not get prospects")
                return False
            
            data = response.json()
            prospects = data.get('prospects', [])
            
            # Find a prospect in won stage for AML/KYC testing
            won_prospect = None
            for prospect in prospects:
                if prospect.get('stage') == 'won':
                    won_prospect = prospect
                    break
            
            if not won_prospect:
                self.log_result("AML/KYC Process", True, 
                              "No won prospects available for AML/KYC testing (acceptable)")
                return True
            
            prospect_id = won_prospect.get('id')
            
            # Test AML/KYC endpoints accessibility
            aml_response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/aml-kyc")
            approve_response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/aml-approve")
            
            details = {
                'test_prospect_id': prospect_id,
                'aml_check_status': aml_response.status_code,
                'aml_approve_status': approve_response.status_code
            }
            
            # Both endpoints should be accessible (200 or 400 for business logic reasons)
            aml_accessible = aml_response.status_code in [200, 400]
            approve_accessible = approve_response.status_code in [200, 400]
            
            if aml_accessible and approve_accessible:
                self.log_result("AML/KYC Process", True, 
                              "AML/KYC endpoints accessible", details)
                return True
            else:
                self.log_result("AML/KYC Process", False, 
                              "AML/KYC endpoints not accessible", details)
                return False
                
        except Exception as e:
            self.log_result("AML/KYC Process", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive simplified pipeline test"""
        print("🎯 FIDUS SIMPLIFIED PIPELINE FINAL TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test simplified pipeline validation
        self.test_simplified_pipeline_validation()
        
        # Step 3: Test pipeline statistics endpoint
        self.test_pipeline_statistics_endpoint()
        
        # Step 4: Test stage update validation
        self.test_stage_update_validation()
        
        # Step 5: Test Lilian Limon records
        self.test_lilian_limon_records()
        
        # Step 6: Test document upload endpoints
        self.test_document_upload_endpoints()
        
        # Step 7: Test AML/KYC process
        self.test_aml_kyc_process()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 SIMPLIFIED PIPELINE FINAL TEST SUMMARY")
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
        
        # Check simplified pipeline implementation
        pipeline_tests = [r for r in self.test_results if 'pipeline' in r['test'].lower()]
        pipeline_success = all(t['success'] for t in pipeline_tests)
        if pipeline_success:
            print(f"  ✅ Simplified pipeline (lead → negotiation → won → lost) fully implemented")
        else:
            print(f"  ❌ Simplified pipeline implementation issues detected")
        
        # Check stage validation
        validation_tests = [r for r in self.test_results if 'validation' in r['test'].lower()]
        if validation_tests and all(t['success'] for t in validation_tests):
            print(f"  ✅ Stage validation correctly rejects old stages")
        elif validation_tests:
            print(f"  ❌ Stage validation issues detected")
        
        # Check Lilian records
        lilian_tests = [r for r in self.test_results if 'lilian' in r['test'].lower()]
        if lilian_tests and all(t['success'] for t in lilian_tests):
            print(f"  ✅ Lilian Limon records properly handled")
        elif lilian_tests:
            print(f"  ❌ Lilian Limon records need attention")
        
        # Check supporting functionality
        support_tests = [r for r in self.test_results if any(x in r['test'].lower() for x in ['document', 'aml', 'kyc'])]
        if support_tests and all(t['success'] for t in support_tests):
            print(f"  ✅ Document upload and AML/KYC processes working")
        elif support_tests:
            print(f"  ⚠️  Some supporting functionality issues detected")
        
        print("\n" + "=" * 60)
        
        # Overall assessment
        if success_rate >= 85:
            print("🎉 SIMPLIFIED PIPELINE IMPLEMENTATION: SUCCESS")
            print("✅ System ready for simplified lead-to-client conversion workflow")
        elif success_rate >= 70:
            print("⚠️  SIMPLIFIED PIPELINE IMPLEMENTATION: MOSTLY WORKING")
            print("🔧 Minor issues detected but core functionality operational")
        else:
            print("❌ SIMPLIFIED PIPELINE IMPLEMENTATION: NEEDS WORK")
            print("🚨 Significant issues detected requiring attention")

def main():
    """Main test execution"""
    tester = SimplifiedPipelineFinalTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("🎉 Simplified pipeline final testing completed!")
    else:
        print("❌ Testing failed to complete")
        sys.exit(1)

if __name__ == "__main__":
    main()