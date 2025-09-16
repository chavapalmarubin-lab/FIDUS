#!/usr/bin/env python3
"""
PROSPECT PIPELINE STAGE PROGRESSION TEST
========================================

This test addresses the critical issue reported in the review request:
"Pipeline buttons are now visible and properly styled ✅
But clicking buttons causes 'Error: Prospect not found' ❌"

Root Cause Analysis:
1. Check prospect data synchronization between frontend and backend
2. Test prospect ID mapping - GET /api/crm/prospects vs frontend display  
3. Debug PUT endpoint - Test PUT /api/crm/prospects/{id} with actual prospect IDs
4. Fix data persistence issues

Expected Results:
- Prospects display correctly in GET /api/crm/prospects
- PUT /api/crm/prospects/{id} works with actual prospect IDs
- Stage progression buttons work without "Prospect not found" errors
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-invest.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ProspectPipelineTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.test_prospects = []
        
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
    
    def test_get_all_prospects(self):
        """Test GET /api/crm/prospects endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                total_prospects = data.get('total_prospects', 0)
                
                self.log_result("GET All Prospects", True, 
                              f"Found {total_prospects} prospects", 
                              {"prospects_count": total_prospects, "pipeline_stats": data.get('pipeline_stats', {})})
                
                # Store prospects for later testing
                self.test_prospects = prospects
                
                # Log prospect details for debugging
                if prospects:
                    print("   📋 Prospect Details:")
                    for i, prospect in enumerate(prospects[:5]):  # Show first 5
                        print(f"      {i+1}. ID: {prospect.get('id')}, Name: {prospect.get('name')}, Stage: {prospect.get('stage')}")
                
                return True
            else:
                self.log_result("GET All Prospects", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("GET All Prospects", False, f"Exception: {str(e)}")
            return False
    
    def test_create_test_prospect(self):
        """Create a test prospect for pipeline testing"""
        try:
            test_prospect_data = {
                "name": "Pipeline Test Prospect",
                "email": "pipeline.test@fidus.com",
                "phone": "+1-555-PIPELINE",
                "notes": "Created for pipeline stage progression testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect_data)
            if response.status_code == 200:
                data = response.json()
                prospect_id = data.get('prospect_id')
                
                if prospect_id:
                    self.log_result("Create Test Prospect", True, 
                                  f"Test prospect created with ID: {prospect_id}")
                    
                    # Add to our test prospects list
                    self.test_prospects.append({
                        'id': prospect_id,
                        'name': test_prospect_data['name'],
                        'stage': 'lead'
                    })
                    return prospect_id
                else:
                    self.log_result("Create Test Prospect", False, 
                                  "No prospect_id in response", {"response": data})
                    return None
            else:
                self.log_result("Create Test Prospect", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return None
                
        except Exception as e:
            self.log_result("Create Test Prospect", False, f"Exception: {str(e)}")
            return None
    
    def test_prospect_stage_progression(self, prospect_id, prospect_name):
        """Test stage progression for a specific prospect"""
        stages = ["qualified", "proposal", "negotiation", "won"]
        
        for stage in stages:
            try:
                update_data = {"stage": stage}
                response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json=update_data)
                
                if response.status_code == 200:
                    data = response.json()
                    updated_stage = data.get('prospect', {}).get('stage')
                    
                    if updated_stage == stage:
                        self.log_result(f"Stage Progression - {stage.title()}", True, 
                                      f"Successfully moved '{prospect_name}' to {stage}")
                    else:
                        self.log_result(f"Stage Progression - {stage.title()}", False, 
                                      f"Stage not updated correctly: expected {stage}, got {updated_stage}")
                        break
                else:
                    self.log_result(f"Stage Progression - {stage.title()}", False, 
                                  f"HTTP {response.status_code} for prospect {prospect_id}", 
                                  {"response": response.text, "prospect_name": prospect_name})
                    
                    # This is the critical error we're debugging
                    if response.status_code == 404:
                        print(f"   🚨 CRITICAL: 'Prospect not found' error for ID: {prospect_id}")
                        print(f"   🔍 This is the exact issue reported in the review request!")
                    break
                    
            except Exception as e:
                self.log_result(f"Stage Progression - {stage.title()}", False, 
                              f"Exception: {str(e)}")
                break
    
    def test_existing_prospects_update(self):
        """Test updating existing prospects to identify the root cause"""
        if not self.test_prospects:
            self.log_result("Test Existing Prospects", False, "No prospects available for testing")
            return
        
        print("\n🔍 Testing Stage Progression on Existing Prospects...")
        print("-" * 50)
        
        for i, prospect in enumerate(self.test_prospects[:3]):  # Test first 3 prospects
            prospect_id = prospect.get('id')
            prospect_name = prospect.get('name', 'Unknown')
            current_stage = prospect.get('stage', 'lead')
            
            print(f"\n   Testing Prospect {i+1}: {prospect_name} (ID: {prospect_id})")
            print(f"   Current Stage: {current_stage}")
            
            # Try to move to next stage
            next_stages = {
                'lead': 'qualified',
                'qualified': 'proposal', 
                'proposal': 'negotiation',
                'negotiation': 'won'
            }
            
            next_stage = next_stages.get(current_stage, 'qualified')
            
            try:
                update_data = {"stage": next_stage}
                response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json=update_data)
                
                if response.status_code == 200:
                    self.log_result(f"Update Existing Prospect - {prospect_name}", True, 
                                  f"Successfully moved from {current_stage} to {next_stage}")
                elif response.status_code == 404:
                    self.log_result(f"Update Existing Prospect - {prospect_name}", False, 
                                  f"PROSPECT NOT FOUND ERROR - ID: {prospect_id}", 
                                  {"current_stage": current_stage, "target_stage": next_stage})
                    
                    print(f"   🚨 ROOT CAUSE IDENTIFIED: Prospect {prospect_id} exists in GET but not in PUT!")
                else:
                    self.log_result(f"Update Existing Prospect - {prospect_name}", False, 
                                  f"HTTP {response.status_code}", {"response": response.text})
                    
            except Exception as e:
                self.log_result(f"Update Existing Prospect - {prospect_name}", False, f"Exception: {str(e)}")
    
    def test_data_synchronization_issue(self):
        """Test for data synchronization issues between MongoDB and memory storage"""
        try:
            print("\n🔍 Analyzing Data Synchronization Issues...")
            print("-" * 50)
            
            # Get prospects again to check consistency
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                
                print(f"   Total prospects found: {len(prospects)}")
                
                if prospects:
                    # Test first prospect for update capability
                    test_prospect = prospects[0]
                    prospect_id = test_prospect.get('id')
                    
                    print(f"   Testing prospect ID: {prospect_id}")
                    
                    # Try a simple update (just notes)
                    update_data = {"notes": f"Test update at {datetime.now().isoformat()}"}
                    response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json=update_data)
                    
                    if response.status_code == 200:
                        self.log_result("Data Synchronization Test", True, 
                                      "Prospect update successful - no sync issues")
                    elif response.status_code == 404:
                        self.log_result("Data Synchronization Test", False, 
                                      "CRITICAL: Prospect exists in GET but not in PUT - Memory/MongoDB sync issue",
                                      {"prospect_id": prospect_id})
                        
                        print("   🚨 ROOT CAUSE CONFIRMED:")
                        print("   📋 GET /api/crm/prospects reads from MongoDB")
                        print("   ✏️  PUT /api/crm/prospects/{id} writes to memory storage")
                        print("   💥 Data exists in MongoDB but not in memory storage!")
                    else:
                        self.log_result("Data Synchronization Test", False, 
                                      f"Unexpected HTTP {response.status_code}")
                else:
                    self.log_result("Data Synchronization Test", False, "No prospects available for testing")
            else:
                self.log_result("Data Synchronization Test", False, "Failed to get prospects for sync test")
                
        except Exception as e:
            self.log_result("Data Synchronization Test", False, f"Exception: {str(e)}")
    
    def test_pipeline_workflow_complete(self):
        """Test complete pipeline workflow from creation to won"""
        print("\n🔄 Testing Complete Pipeline Workflow...")
        print("-" * 50)
        
        # Create a new prospect for complete workflow test
        prospect_id = self.test_create_test_prospect()
        if not prospect_id:
            self.log_result("Complete Pipeline Workflow", False, "Failed to create test prospect")
            return
        
        # Test full stage progression
        self.test_prospect_stage_progression(prospect_id, "Pipeline Test Prospect")
    
    def run_all_tests(self):
        """Run all prospect pipeline tests"""
        print("🎯 PROSPECT PIPELINE STAGE PROGRESSION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("🎯 ISSUE: Pipeline buttons visible but clicking causes 'Prospect not found' error")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Prospect Pipeline Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_get_all_prospects()
        self.test_existing_prospects_update()
        self.test_data_synchronization_issue()
        self.test_pipeline_workflow_complete()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 PROSPECT PIPELINE TEST SUMMARY")
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
        
        # Show failed tests (these are the critical issues)
        if failed_tests > 0:
            print("❌ CRITICAL ISSUES FOUND:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ WORKING COMPONENTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Root cause analysis
        print("🔍 ROOT CAUSE ANALYSIS:")
        
        # Check for the specific "Prospect not found" pattern
        prospect_not_found_errors = [r for r in self.test_results 
                                   if not r['success'] and 'not found' in r['message'].lower()]
        
        if prospect_not_found_errors:
            print("❌ CONFIRMED: 'Prospect not found' errors detected")
            print("   🔍 ROOT CAUSE: Data synchronization issue between MongoDB and memory storage")
            print("   📋 GET /api/crm/prospects reads from MongoDB (prospects visible)")
            print("   ✏️  PUT /api/crm/prospects/{id} writes to memory storage (prospects not found)")
            print("   💡 SOLUTION: Fix backend to use consistent storage or sync data properly")
        else:
            print("✅ No 'Prospect not found' errors detected in current test")
        
        print("\n🎯 MAIN AGENT ACTION REQUIRED:")
        if prospect_not_found_errors:
            print("1. Fix data synchronization between MongoDB and memory storage in server.py")
            print("2. Ensure PUT /api/crm/prospects/{id} can find prospects from GET /api/crm/prospects")
            print("3. Either use MongoDB consistently or sync memory storage on startup")
            print("4. Test pipeline stage progression buttons after fix")
        else:
            print("1. Verify pipeline buttons work correctly in frontend")
            print("2. Test with actual prospect data from production environment")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = ProspectPipelineTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()