#!/usr/bin/env python3
"""
LILIAN LIMON LEITE AML/KYC BUTTON INVESTIGATION TEST
===================================================

This test investigates the critical issue reported by the user:
- Lilian is in "Won" stage with "KYC: 4/4 (100%)" ✅
- BUT no AML/KYC button is visible on her prospect card ❌  
- User can't find how to run AML/KYC check to convert to client

Investigation Plan:
1. Check Lilian's current data via GET /api/crm/prospects
2. Check her aml_kyc_status field - this might be blocking the button
3. Test AML/KYC button logic: shows when prospect.stage === 'won' && !prospect.aml_kyc_status
4. Fix button visibility logic if needed
5. Test complete conversion workflow

Expected Results:
- Find Lilian Limon Leite in prospects
- Identify why AML/KYC button is not showing
- Test AML/KYC workflow
- Verify Convert button appears after AML/KYC check
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

class LilianAMLKYCInvestigationTest:
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
        """Find Lilian Limon Leite in prospects database"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects_data = response.json()
                
                # Handle different response formats
                if isinstance(prospects_data, list):
                    prospects = prospects_data
                elif isinstance(prospects_data, dict) and 'prospects' in prospects_data:
                    prospects = prospects_data['prospects']
                else:
                    prospects = []
                
                # Look for Lilian Limon Leite
                lilian_found = False
                for prospect in prospects:
                    if isinstance(prospect, dict):
                        name = prospect.get('name', '').upper()
                        if 'LILIAN' in name and ('LIMON' in name or 'LEITE' in name):
                            lilian_found = True
                            self.lilian_prospect = prospect
                        
                        self.log_result("Find Lilian Prospect", True, 
                                      f"Found Lilian: {prospect.get('name')} (ID: {prospect.get('id')})",
                                      {"prospect_data": prospect})
                        
                        # Analyze her current status
                        stage = prospect.get('stage', 'unknown')
                        aml_kyc_status = prospect.get('aml_kyc_status')
                        converted = prospect.get('converted_to_client', False)
                        
                        print(f"   📊 LILIAN'S CURRENT STATUS:")
                        print(f"      Stage: {stage}")
                        print(f"      AML/KYC Status: {aml_kyc_status}")
                        print(f"      Converted to Client: {converted}")
                        print(f"      Email: {prospect.get('email', 'N/A')}")
                        print(f"      Phone: {prospect.get('phone', 'N/A')}")
                        
                        return True
                
                if not lilian_found:
                    self.log_result("Find Lilian Prospect", False, 
                                  "Lilian Limon Leite not found in prospects database",
                                  {"total_prospects": len(prospects), 
                                   "prospect_names": [p.get('name', 'Unknown') for p in prospects[:10]]})
                    return False
                    
            else:
                self.log_result("Find Lilian Prospect", False, 
                              f"Failed to get prospects: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Find Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def analyze_aml_kyc_button_logic(self):
        """Analyze why AML/KYC button might not be showing"""
        if not self.lilian_prospect:
            self.log_result("AML/KYC Button Logic Analysis", False, "No Lilian prospect data to analyze")
            return False
        
        try:
            stage = self.lilian_prospect.get('stage', '')
            aml_kyc_status = self.lilian_prospect.get('aml_kyc_status')
            converted = self.lilian_prospect.get('converted_to_client', False)
            
            # Frontend logic: shows AML/KYC button when prospect.stage === 'won' && !prospect.aml_kyc_status
            should_show_aml_button = (stage == 'won' and not aml_kyc_status and not converted)
            
            analysis = {
                "stage_is_won": stage == 'won',
                "aml_kyc_status_empty": not aml_kyc_status,
                "not_converted": not converted,
                "should_show_aml_button": should_show_aml_button
            }
            
            if should_show_aml_button:
                self.log_result("AML/KYC Button Logic Analysis", True, 
                              "AML/KYC button SHOULD be visible based on current data",
                              analysis)
                
                # This suggests a frontend issue
                print("   🔍 DIAGNOSIS: Frontend may not be properly checking button visibility logic")
                print("   💡 RECOMMENDATION: Check frontend ProspectManagement.js component")
                
            else:
                # Identify the blocking condition
                blocking_reasons = []
                if stage != 'won':
                    blocking_reasons.append(f"Stage is '{stage}' (should be 'won')")
                if aml_kyc_status:
                    blocking_reasons.append(f"AML/KYC status already set to '{aml_kyc_status}'")
                if converted:
                    blocking_reasons.append("Already converted to client")
                
                self.log_result("AML/KYC Button Logic Analysis", True, 
                              f"AML/KYC button correctly hidden. Blocking reasons: {', '.join(blocking_reasons)}",
                              analysis)
                
                if aml_kyc_status:
                    print("   🔍 DIAGNOSIS: AML/KYC already completed - button should show 'Re-run AML/KYC' or 'Convert'")
                    print("   💡 RECOMMENDATION: Modify frontend to show appropriate next action button")
            
            return True
            
        except Exception as e:
            self.log_result("AML/KYC Button Logic Analysis", False, f"Exception: {str(e)}")
            return False
    
    def test_aml_kyc_workflow(self):
        """Test the AML/KYC workflow for Lilian"""
        if not self.lilian_prospect:
            self.log_result("AML/KYC Workflow Test", False, "No Lilian prospect data to test")
            return False
        
        try:
            prospect_id = self.lilian_prospect.get('id')
            if not prospect_id:
                self.log_result("AML/KYC Workflow Test", False, "No prospect ID found")
                return False
            
            # Test AML/KYC endpoint
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/aml-kyc")
            
            if response.status_code == 200:
                aml_result = response.json()
                
                self.log_result("AML/KYC Workflow Test", True, 
                              f"AML/KYC check completed successfully",
                              {"aml_result": aml_result})
                
                # Check if result allows conversion
                can_convert = aml_result.get('aml_result', {}).get('can_convert', False)
                overall_status = aml_result.get('aml_result', {}).get('overall_status', 'unknown')
                
                print(f"   📊 AML/KYC RESULT:")
                print(f"      Overall Status: {overall_status}")
                print(f"      Can Convert: {can_convert}")
                
                if can_convert:
                    print("   ✅ RESULT: Convert button should now be visible")
                else:
                    print("   ⚠️  RESULT: Additional compliance steps may be required")
                
                return True
                
            elif response.status_code == 400:
                error_detail = response.json().get('detail', 'Unknown error')
                self.log_result("AML/KYC Workflow Test", False, 
                              f"AML/KYC check failed: {error_detail}")
                
                if "already" in error_detail.lower():
                    print("   🔍 DIAGNOSIS: AML/KYC may have already been completed")
                    return self.test_conversion_workflow()
                
                return False
                
            else:
                self.log_result("AML/KYC Workflow Test", False, 
                              f"AML/KYC check failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("AML/KYC Workflow Test", False, f"Exception: {str(e)}")
            return False
    
    def test_conversion_workflow(self):
        """Test the prospect to client conversion workflow"""
        if not self.lilian_prospect:
            self.log_result("Conversion Workflow Test", False, "No Lilian prospect data to test")
            return False
        
        try:
            prospect_id = self.lilian_prospect.get('id')
            if not prospect_id:
                self.log_result("Conversion Workflow Test", False, "No prospect ID found")
                return False
            
            # Test conversion endpoint
            conversion_data = {
                "prospect_id": prospect_id,
                "send_agreement": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/convert", 
                                       json=conversion_data)
            
            if response.status_code == 200:
                conversion_result = response.json()
                
                self.log_result("Conversion Workflow Test", True, 
                              "Prospect to client conversion completed successfully",
                              {"conversion_result": conversion_result})
                
                client_id = conversion_result.get('client', {}).get('id')
                if client_id:
                    print(f"   🎉 SUCCESS: Lilian converted to client with ID: {client_id}")
                    print("   ✅ RESULT: Complete Won → Client conversion workflow working")
                
                return True
                
            elif response.status_code == 400:
                error_detail = response.json().get('detail', 'Unknown error')
                self.log_result("Conversion Workflow Test", False, 
                              f"Conversion failed: {error_detail}")
                
                if "aml" in error_detail.lower() or "kyc" in error_detail.lower():
                    print("   🔍 DIAGNOSIS: AML/KYC compliance required before conversion")
                    print("   💡 RECOMMENDATION: Complete AML/KYC check first")
                elif "already converted" in error_detail.lower():
                    print("   🔍 DIAGNOSIS: Lilian has already been converted to a client")
                    print("   💡 RECOMMENDATION: Check clients list for Lilian's client record")
                
                return False
                
            else:
                self.log_result("Conversion Workflow Test", False, 
                              f"Conversion failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Conversion Workflow Test", False, f"Exception: {str(e)}")
            return False
    
    def create_lilian_prospect_if_missing(self):
        """Create Lilian Limon Leite prospect if she doesn't exist"""
        try:
            # Create Lilian as a Won prospect for testing
            lilian_data = {
                "name": "Lilian Limon Leite",
                "email": "lilian.leite@example.com",
                "phone": "+1-555-0123",
                "notes": "KYC: 4/4 (100%) - Ready for AML/KYC check and conversion"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=lilian_data)
            
            if response.status_code == 200:
                prospect = response.json()
                prospect_id = prospect.get('id')
                
                # Update to Won stage
                update_data = {"stage": "won"}
                update_response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", 
                                                 json=update_data)
                
                if update_response.status_code == 200:
                    self.log_result("Create Lilian Prospect", True, 
                                  f"Created Lilian Limon Leite prospect in Won stage (ID: {prospect_id})")
                    
                    # Refresh prospect data
                    return self.find_lilian_prospect()
                else:
                    self.log_result("Create Lilian Prospect", False, 
                                  f"Failed to update prospect to Won stage: HTTP {update_response.status_code}")
                    return False
            else:
                self.log_result("Create Lilian Prospect", False, 
                              f"Failed to create prospect: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Create Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def test_frontend_button_conditions(self):
        """Test all conditions that affect frontend button visibility"""
        if not self.lilian_prospect:
            self.log_result("Frontend Button Conditions", False, "No Lilian prospect data to analyze")
            return False
        
        try:
            prospect = self.lilian_prospect
            
            # Test all button visibility conditions
            conditions = {
                "stage_is_won": prospect.get('stage') == 'won',
                "not_converted": not prospect.get('converted_to_client', False),
                "aml_kyc_status": prospect.get('aml_kyc_status'),
                "has_aml_kyc_status": bool(prospect.get('aml_kyc_status')),
                "aml_kyc_result_id": prospect.get('aml_kyc_result_id')
            }
            
            # Determine which buttons should be visible
            button_visibility = {
                "aml_kyc_button": conditions["stage_is_won"] and not conditions["has_aml_kyc_status"] and not conditions["not_converted"],
                "rerun_aml_kyc_button": conditions["stage_is_won"] and conditions["has_aml_kyc_status"] and conditions["aml_kyc_status"] not in ['clear', 'approved'],
                "convert_button": conditions["stage_is_won"] and conditions["aml_kyc_status"] in ['clear', 'approved'] and not conditions["not_converted"]
            }
            
            self.log_result("Frontend Button Conditions", True, 
                          "Analyzed all frontend button visibility conditions",
                          {"conditions": conditions, "button_visibility": button_visibility})
            
            print("   📊 BUTTON VISIBILITY ANALYSIS:")
            for button, should_show in button_visibility.items():
                status = "SHOULD SHOW" if should_show else "SHOULD HIDE"
                print(f"      {button}: {status}")
            
            # Provide specific recommendations
            if button_visibility["aml_kyc_button"]:
                print("   💡 RECOMMENDATION: AML/KYC button should be visible - check frontend implementation")
            elif button_visibility["convert_button"]:
                print("   💡 RECOMMENDATION: Convert button should be visible - AML/KYC already completed")
            elif button_visibility["rerun_aml_kyc_button"]:
                print("   💡 RECOMMENDATION: Re-run AML/KYC button should be visible - previous check needs retry")
            else:
                print("   💡 RECOMMENDATION: Check prospect stage and AML/KYC status requirements")
            
            return True
            
        except Exception as e:
            self.log_result("Frontend Button Conditions", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Lilian AML/KYC investigation tests"""
        print("🔍 LILIAN LIMON LEITE AML/KYC BUTTON INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Lilian AML/KYC Investigation Tests...")
        print("-" * 50)
        
        # Try to find Lilian first
        if not self.find_lilian_prospect():
            print("\n⚠️  Lilian not found. Creating test prospect...")
            if not self.create_lilian_prospect_if_missing():
                print("❌ CRITICAL: Could not find or create Lilian prospect. Cannot proceed.")
                return False
        
        # Run investigation tests
        self.analyze_aml_kyc_button_logic()
        self.test_frontend_button_conditions()
        self.test_aml_kyc_workflow()
        self.test_conversion_workflow()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🔍 LILIAN AML/KYC INVESTIGATION SUMMARY")
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
        
        # Critical findings
        print("🚨 CRITICAL FINDINGS:")
        if self.lilian_prospect:
            stage = self.lilian_prospect.get('stage', 'unknown')
            aml_status = self.lilian_prospect.get('aml_kyc_status')
            converted = self.lilian_prospect.get('converted_to_client', False)
            
            print(f"   📊 Lilian's Status: Stage={stage}, AML/KYC={aml_status}, Converted={converted}")
            
            if stage == 'won' and not aml_status and not converted:
                print("   ✅ DIAGNOSIS: AML/KYC button SHOULD be visible")
                print("   💡 ACTION REQUIRED: Check frontend ProspectManagement.js component")
            elif stage == 'won' and aml_status in ['clear', 'approved']:
                print("   ✅ DIAGNOSIS: Convert button SHOULD be visible")
                print("   💡 ACTION REQUIRED: AML/KYC completed, ready for conversion")
            elif converted:
                print("   ✅ DIAGNOSIS: Already converted to client")
                print("   💡 ACTION REQUIRED: Check clients list for Lilian's record")
            else:
                print("   ⚠️  DIAGNOSIS: Prospect not in correct state for AML/KYC")
                print("   💡 ACTION REQUIRED: Move to Won stage first")
        else:
            print("   ❌ DIAGNOSIS: Lilian Limon Leite not found in system")
            print("   💡 ACTION REQUIRED: Create prospect record for Lilian")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = LilianAMLKYCInvestigationTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()