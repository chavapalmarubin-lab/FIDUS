#!/usr/bin/env python3
"""
CRM Prospects Integration with Portal Leads Testing
Test the integration between existing CRM prospects and new Portal leads
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://data-integrity-13.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123",
    "user_type": "admin"
}

class CRMProspectsIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                self.log_test("Admin Authentication", True, f"Token received: {self.admin_token[:20]}...")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_crm_prospects_endpoint(self):
        """Test GET /api/crm/prospects - should include both CRM prospects and portal leads"""
        try:
            response = self.session.get(f"{API_BASE}/crm/prospects", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has prospects array
                if 'prospects' in data:
                    prospects = data['prospects']
                elif isinstance(data, list):
                    prospects = data
                else:
                    self.log_test("CRM Prospects Endpoint Structure", False, "Response doesn't contain prospects array")
                    return False
                
                # Analyze prospects for integration
                crm_prospects = []
                portal_leads = []
                
                for prospect in prospects:
                    prospect_id = prospect.get('prospect_id', prospect.get('id', ''))
                    if prospect_id.startswith('portal_lead_'):
                        portal_leads.append(prospect)
                    else:
                        crm_prospects.append(prospect)
                
                total_prospects = len(prospects)
                crm_count = len(crm_prospects)
                portal_count = len(portal_leads)
                
                self.log_test(
                    "CRM Prospects Endpoint", 
                    True, 
                    f"Total: {total_prospects}, CRM: {crm_count}, Portal: {portal_count}"
                )
                
                # Verify portal leads have correct transformation
                if portal_leads:
                    sample_portal_lead = portal_leads[0]
                    required_fields = ['prospect_id', 'name', 'email', 'phone', 'stage', 'notes', 'created_at']
                    missing_fields = [field for field in required_fields if field not in sample_portal_lead]
                    
                    if not missing_fields:
                        # Check specific portal lead transformations
                        has_portal_prefix = sample_portal_lead['prospect_id'].startswith('portal_lead_')
                        has_stage_lead = sample_portal_lead.get('stage') == 'lead'
                        has_portal_notes = 'Prospects Portal' in sample_portal_lead.get('notes', '')
                        has_source = sample_portal_lead.get('source') == 'prospects_portal'
                        
                        transformation_checks = {
                            'Portal ID prefix': has_portal_prefix,
                            'Stage = lead': has_stage_lead,
                            'Portal notes': has_portal_notes,
                            'Source field': has_source
                        }
                        
                        passed_checks = sum(transformation_checks.values())
                        total_checks = len(transformation_checks)
                        
                        self.log_test(
                            "Portal Lead Transformation", 
                            passed_checks >= 3,  # At least 3 out of 4 checks should pass
                            f"Checks passed: {passed_checks}/{total_checks} - {transformation_checks}"
                        )
                    else:
                        self.log_test("Portal Lead Fields", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Portal Lead Integration", False, "No portal leads found in response")
                
                return True
                
            else:
                self.log_test("CRM Prospects Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("CRM Prospects Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_create_test_lead(self):
        """Test creating a test lead via prospects portal endpoint"""
        try:
            test_lead_data = {
                "email": "test.integration@example.com",
                "phone": "+1234567890",
                "source": "prospects_portal"
            }
            
            response = self.session.post(
                f"{API_BASE}/prospects/lead",
                json=test_lead_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                lead_id = data.get('leadId') or data.get('lead_id') or data.get('id')
                
                if lead_id:
                    self.log_test("Create Test Lead", True, f"Lead created with ID: {lead_id}")
                    
                    # Verify the lead appears in CRM prospects
                    return self.verify_test_lead_in_crm(test_lead_data['email'])
                else:
                    self.log_test("Create Test Lead", False, "No lead ID returned")
                    return False
            else:
                self.log_test("Create Test Lead", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Test Lead", False, f"Exception: {str(e)}")
            return False
    
    def verify_test_lead_in_crm(self, test_email):
        """Verify that the test lead appears in CRM prospects"""
        try:
            response = self.session.get(f"{API_BASE}/crm/prospects", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', data if isinstance(data, list) else [])
                
                # Look for our test lead
                test_lead = None
                for prospect in prospects:
                    if prospect.get('email') == test_email:
                        test_lead = prospect
                        break
                
                if test_lead:
                    # Verify it has portal_lead_ prefix
                    has_portal_prefix = test_lead.get('prospect_id', '').startswith('portal_lead_')
                    self.log_test(
                        "Test Lead in CRM", 
                        has_portal_prefix, 
                        f"Found lead with ID: {test_lead.get('prospect_id')}"
                    )
                    return has_portal_prefix
                else:
                    self.log_test("Test Lead in CRM", False, "Test lead not found in CRM prospects")
                    return False
            else:
                self.log_test("Test Lead in CRM Verification", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test Lead in CRM Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_data_structure_consistency(self):
        """Test that all prospects have consistent data structure"""
        try:
            response = self.session.get(f"{API_BASE}/crm/prospects", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', data if isinstance(data, list) else [])
                
                if not prospects:
                    self.log_test("Data Structure Consistency", False, "No prospects found")
                    return False
                
                required_fields = ['name', 'email', 'phone', 'stage', 'notes', 'created_at']
                # prospect_id or id field is required
                id_fields = ['prospect_id', 'id']
                inconsistent_prospects = []
                
                for prospect in prospects:
                    # Check if at least one ID field exists
                    has_id = any(field in prospect for field in id_fields)
                    missing_fields = [field for field in required_fields if field not in prospect]
                    
                    if not has_id:
                        missing_fields.append('prospect_id/id')
                    
                    if missing_fields:
                        prospect_id = prospect.get('prospect_id', prospect.get('id', 'unknown'))
                        inconsistent_prospects.append({
                            'id': prospect_id,
                            'missing': missing_fields
                        })
                
                if not inconsistent_prospects:
                    self.log_test("Data Structure Consistency", True, f"All {len(prospects)} prospects have required fields")
                    return True
                else:
                    self.log_test(
                        "Data Structure Consistency", 
                        False, 
                        f"{len(inconsistent_prospects)} prospects missing fields: {inconsistent_prospects[:3]}"
                    )
                    return False
            else:
                self.log_test("Data Structure Consistency", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Data Structure Consistency", False, f"Exception: {str(e)}")
            return False
    
    def test_portal_lead_engagement_data(self):
        """Test that portal leads have engagement score and simulator sessions"""
        try:
            response = self.session.get(f"{API_BASE}/crm/prospects", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', data if isinstance(data, list) else [])
                
                portal_leads = [p for p in prospects if p.get('prospect_id', '').startswith('portal_lead_')]
                
                if not portal_leads:
                    self.log_test("Portal Lead Engagement Data", False, "No portal leads found")
                    return False
                
                engagement_data_count = 0
                for lead in portal_leads:
                    has_engagement_score = 'engagement_score' in lead
                    has_simulator_sessions = 'simulator_sessions' in lead
                    
                    if has_engagement_score or has_simulator_sessions:
                        engagement_data_count += 1
                
                success_rate = engagement_data_count / len(portal_leads)
                self.log_test(
                    "Portal Lead Engagement Data", 
                    success_rate > 0,  # At least some portal leads should have engagement data
                    f"{engagement_data_count}/{len(portal_leads)} portal leads have engagement data"
                )
                return success_rate > 0
                
            else:
                self.log_test("Portal Lead Engagement Data", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Portal Lead Engagement Data", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all CRM prospects integration tests"""
        print("🎯 CRM PROSPECTS INTEGRATION WITH PORTAL LEADS TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test main CRM prospects endpoint
        self.test_crm_prospects_endpoint()
        
        # Step 3: Test creating a new lead and verifying integration
        self.test_create_test_lead()
        
        # Step 4: Test data structure consistency
        self.test_data_structure_consistency()
        
        # Step 5: Test portal lead engagement data
        self.test_portal_lead_engagement_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\nFAILED TESTS:")
            for test in failed_tests:
                print(f"❌ {test['test']}: {test['details']}")
        
        print(f"\n🎯 CRM PROSPECTS INTEGRATION STATUS: {'✅ WORKING' if success_rate >= 70 else '❌ NEEDS FIXES'}")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = CRMProspectsIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)