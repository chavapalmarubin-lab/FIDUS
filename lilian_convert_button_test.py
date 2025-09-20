#!/usr/bin/env python3
"""
LILIAN CONVERT BUTTON DEBUG TEST
===============================

URGENT: Debug why Convert button not showing despite backend data fix

INVESTIGATION NEEDED:
1. Check current prospect data in MongoDB for Lilian
2. Test frontend API endpoints (GET /api/crm/prospects and GET /api/crm/prospects/pipeline)
3. Check frontend button logic: Convert button shows when:
   prospect.stage === 'won' && (aml_kyc_status === 'clear' || 'approved') && !converted_to_client
4. Force data refresh and ensure frontend gets latest prospect data

EXPECTED BUTTON LOGIC:
- Lilian should be: stage="won", aml_kyc_status="clear", converted_to_client=false
- This should trigger Convert button to appear (green button)
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://auth-troubleshoot-14.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class LilianConvertButtonTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.lilian_prospect = None
        
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
    
    def find_lilian_prospect(self):
        """Find Lilian's prospect data in MongoDB"""
        try:
            # Test GET /api/crm/prospects endpoint
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                
                # Look for Lilian Limon Leite
                lilian_found = False
                for prospect in prospects:
                    name = prospect.get('name', '').lower()
                    if 'lilian' in name and 'limon' in name:
                        self.lilian_prospect = prospect
                        lilian_found = True
                        
                        self.log_result("Find Lilian Prospect", True, 
                                      f"Found Lilian: {prospect.get('name')} (ID: {prospect.get('id')})",
                                      {"prospect_data": prospect})
                        
                        # Analyze prospect data for Convert button logic
                        stage = prospect.get('stage')
                        aml_kyc_status = prospect.get('aml_kyc_status')
                        converted_to_client = prospect.get('converted_to_client', False)
                        client_id = prospect.get('client_id')
                        
                        print(f"   📊 LILIAN'S CURRENT DATA:")
                        print(f"   Stage: {stage}")
                        print(f"   AML/KYC Status: {aml_kyc_status}")
                        print(f"   Converted to Client: {converted_to_client}")
                        print(f"   Client ID: {client_id}")
                        
                        # Check Convert button logic
                        should_show_convert = (
                            stage == 'won' and 
                            aml_kyc_status in ['clear', 'approved'] and 
                            not converted_to_client
                        )
                        
                        print(f"   🔍 CONVERT BUTTON LOGIC:")
                        print(f"   Stage == 'won': {stage == 'won'}")
                        print(f"   AML/KYC clear/approved: {aml_kyc_status in ['clear', 'approved']}")
                        print(f"   NOT converted_to_client: {not converted_to_client}")
                        print(f"   SHOULD SHOW CONVERT BUTTON: {should_show_convert}")
                        
                        return True
                
                if not lilian_found:
                    self.log_result("Find Lilian Prospect", False, 
                                  "Lilian Limon Leite not found in prospects list",
                                  {"total_prospects": len(prospects), 
                                   "prospect_names": [p.get('name') for p in prospects]})
                    return False
            else:
                self.log_result("Find Lilian Prospect", False, 
                              f"Failed to get prospects: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Find Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_endpoint(self):
        """Test GET /api/crm/prospects/pipeline endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects/pipeline")
            if response.status_code == 200:
                data = response.json()
                
                # Look for Lilian in pipeline data
                lilian_in_pipeline = False
                pipeline_stages = ['lead', 'qualified', 'proposal', 'negotiation', 'won', 'lost']
                
                for stage in pipeline_stages:
                    stage_prospects = data.get(stage, [])
                    for prospect in stage_prospects:
                        name = prospect.get('name', '').lower()
                        if 'lilian' in name and 'limon' in name:
                            lilian_in_pipeline = True
                            
                            self.log_result("Lilian in Pipeline", True, 
                                          f"Found Lilian in '{stage}' stage",
                                          {"stage": stage, "prospect_data": prospect})
                            
                            # Compare with main prospects endpoint data
                            if self.lilian_prospect:
                                main_stage = self.lilian_prospect.get('stage')
                                if stage == main_stage:
                                    self.log_result("Pipeline Data Consistency", True, 
                                                  f"Pipeline stage matches main endpoint: {stage}")
                                else:
                                    self.log_result("Pipeline Data Consistency", False, 
                                                  f"Stage mismatch: main={main_stage}, pipeline={stage}")
                            break
                    
                    if lilian_in_pipeline:
                        break
                
                if not lilian_in_pipeline:
                    self.log_result("Lilian in Pipeline", False, 
                                  "Lilian not found in pipeline data",
                                  {"pipeline_data": data})
                    return False
                
                return True
            else:
                self.log_result("Pipeline Endpoint", False, 
                              f"Failed to get pipeline: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Pipeline Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_convert_button_conditions(self):
        """Test the exact conditions for Convert button visibility"""
        if not self.lilian_prospect:
            self.log_result("Convert Button Conditions", False, "No Lilian prospect data available")
            return False
        
        try:
            # Extract key fields
            stage = self.lilian_prospect.get('stage')
            aml_kyc_status = self.lilian_prospect.get('aml_kyc_status')
            converted_to_client = self.lilian_prospect.get('converted_to_client', False)
            client_id = self.lilian_prospect.get('client_id')
            
            # Test each condition
            conditions = {
                "stage_is_won": stage == 'won',
                "aml_kyc_clear_or_approved": aml_kyc_status in ['clear', 'approved'],
                "not_converted_to_client": not converted_to_client,
                "client_id_empty": not client_id or client_id == ''
            }
            
            all_conditions_met = all(conditions.values())
            
            self.log_result("Convert Button Conditions", all_conditions_met, 
                          f"All conditions met: {all_conditions_met}",
                          {
                              "conditions": conditions,
                              "current_values": {
                                  "stage": stage,
                                  "aml_kyc_status": aml_kyc_status,
                                  "converted_to_client": converted_to_client,
                                  "client_id": client_id
                              }
                          })
            
            # If conditions not met, identify what needs fixing
            if not all_conditions_met:
                issues = []
                if not conditions["stage_is_won"]:
                    issues.append(f"Stage is '{stage}', should be 'won'")
                if not conditions["aml_kyc_clear_or_approved"]:
                    issues.append(f"AML/KYC status is '{aml_kyc_status}', should be 'clear' or 'approved'")
                if not conditions["not_converted_to_client"]:
                    issues.append(f"converted_to_client is {converted_to_client}, should be false")
                if not conditions["client_id_empty"]:
                    issues.append(f"client_id is '{client_id}', should be empty")
                
                print(f"   🚨 ISSUES PREVENTING CONVERT BUTTON:")
                for issue in issues:
                    print(f"   • {issue}")
            
            return all_conditions_met
            
        except Exception as e:
            self.log_result("Convert Button Conditions", False, f"Exception: {str(e)}")
            return False
    
    def test_client_existence(self):
        """Test if Lilian's client_id exists in the clients database"""
        if not self.lilian_prospect:
            return False
        
        client_id = self.lilian_prospect.get('client_id')
        if not client_id:
            self.log_result("Client Existence Check", True, "No client_id set - this is correct for showing Convert button")
            return True
        
        try:
            # Check if client exists
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                client_exists = False
                
                if isinstance(clients, list):
                    for client in clients:
                        if client.get('id') == client_id:
                            client_exists = True
                            break
                
                if client_exists:
                    self.log_result("Client Existence Check", False, 
                                  f"Client {client_id} exists but prospect still marked as converted",
                                  {"client_id": client_id})
                    return False
                else:
                    self.log_result("Client Existence Check", False, 
                                  f"Client {client_id} does NOT exist - data inconsistency detected",
                                  {"client_id": client_id, "total_clients": len(clients)})
                    return False
            else:
                self.log_result("Client Existence Check", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Client Existence Check", False, f"Exception: {str(e)}")
            return False
    
    def test_data_refresh(self):
        """Test data refresh by making multiple calls to ensure consistency"""
        try:
            print(f"\n🔄 TESTING DATA REFRESH AND CONSISTENCY...")
            
            # Make 3 consecutive calls to check for consistency
            for i in range(3):
                response = self.session.get(f"{BACKEND_URL}/crm/prospects")
                if response.status_code == 200:
                    data = response.json()
                    prospects = data.get('prospects', [])
                    
                    # Find Lilian in this call
                    lilian_data = None
                    for prospect in prospects:
                        name = prospect.get('name', '').lower()
                        if 'lilian' in name and 'limon' in name:
                            lilian_data = prospect
                            break
                    
                    if lilian_data:
                        stage = lilian_data.get('stage')
                        aml_kyc_status = lilian_data.get('aml_kyc_status')
                        converted_to_client = lilian_data.get('converted_to_client', False)
                        
                        print(f"   Call {i+1}: stage={stage}, aml_kyc={aml_kyc_status}, converted={converted_to_client}")
                    else:
                        print(f"   Call {i+1}: Lilian not found")
                
                time.sleep(1)  # Small delay between calls
            
            self.log_result("Data Refresh Test", True, "Completed 3 consecutive API calls for consistency check")
            return True
            
        except Exception as e:
            self.log_result("Data Refresh Test", False, f"Exception: {str(e)}")
            return False
    
    def suggest_fix(self):
        """Suggest the exact fix needed based on test results"""
        if not self.lilian_prospect:
            print(f"\n🚨 CRITICAL: Lilian prospect not found in database!")
            print(f"   ACTION REQUIRED: Verify Lilian Limon Leite exists in MongoDB crm_prospects collection")
            return
        
        stage = self.lilian_prospect.get('stage')
        aml_kyc_status = self.lilian_prospect.get('aml_kyc_status')
        converted_to_client = self.lilian_prospect.get('converted_to_client', False)
        client_id = self.lilian_prospect.get('client_id')
        prospect_id = self.lilian_prospect.get('id')
        
        print(f"\n💡 SUGGESTED FIX FOR LILIAN CONVERT BUTTON:")
        print(f"   Prospect ID: {prospect_id}")
        print(f"   Current Data: stage={stage}, aml_kyc={aml_kyc_status}, converted={converted_to_client}, client_id={client_id}")
        
        fixes_needed = []
        
        if stage != 'won':
            fixes_needed.append(f"Update stage to 'won' (currently '{stage}')")
        
        if aml_kyc_status not in ['clear', 'approved']:
            fixes_needed.append(f"Update aml_kyc_status to 'clear' (currently '{aml_kyc_status}')")
        
        if converted_to_client:
            fixes_needed.append(f"Set converted_to_client to false (currently {converted_to_client})")
        
        if client_id:
            fixes_needed.append(f"Clear client_id field (currently '{client_id}')")
        
        if fixes_needed:
            print(f"   FIXES NEEDED:")
            for fix in fixes_needed:
                print(f"   • {fix}")
            
            # Generate MongoDB update command
            update_fields = {}
            if stage != 'won':
                update_fields['stage'] = 'won'
            if aml_kyc_status not in ['clear', 'approved']:
                update_fields['aml_kyc_status'] = 'clear'
            if converted_to_client:
                update_fields['converted_to_client'] = False
            if client_id:
                update_fields['client_id'] = ''
            
            print(f"\n   MONGODB UPDATE COMMAND:")
            print(f"   db.crm_prospects.updateOne(")
            print(f"     {{'id': '{prospect_id}'}},")
            print(f"     {{$set: {json.dumps(update_fields, indent=6)}}}")
            print(f"   )")
        else:
            print(f"   ✅ ALL CONDITIONS MET - Convert button should be visible!")
            print(f"   If button still not showing, check frontend caching or component refresh.")
    
    def run_all_tests(self):
        """Run all Lilian Convert button debug tests"""
        print("🎯 LILIAN CONVERT BUTTON DEBUG TEST")
        print("=" * 50)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Lilian Convert Button Debug Tests...")
        print("-" * 40)
        
        # Run all tests
        self.find_lilian_prospect()
        self.test_pipeline_endpoint()
        self.test_convert_button_conditions()
        self.test_client_existence()
        self.test_data_refresh()
        
        # Generate summary and suggestions
        self.generate_test_summary()
        self.suggest_fix()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 50)
        print("🎯 LILIAN CONVERT BUTTON TEST SUMMARY")
        print("=" * 50)
        
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
        
        print("=" * 50)

def main():
    """Main test execution"""
    test_runner = LilianConvertButtonTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()