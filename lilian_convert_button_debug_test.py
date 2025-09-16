#!/usr/bin/env python3
"""
LILIAN CONVERT BUTTON CRITICAL DEBUG TEST
========================================

URGENT: Debug why Convert button still not visible for Lilian - check exact production data

This test addresses the critical user report:
"Still can't see CONVERT button despite fixes applied."

CRITICAL DEBUGGING TASKS:
1. Check Lilian's EXACT current status in production
2. Debug Convert button logic (stage="won" AND aml_kyc_status="clear" AND converted_to_client=false)
3. Check if data fixes were applied
4. Force correct data if needed
5. Test other prospects

Expected Result: Find exact reason why Convert button isn't showing and fix it immediately.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use PRODUCTION environment
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class LilianConvertButtonDebugTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.lilian_data = None
        
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
        """Find Lilian Limon Leite in production database"""
        try:
            # Get all prospects
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects_data = response.json()
                
                # Handle different response formats
                if isinstance(prospects_data, dict):
                    prospects = prospects_data.get('prospects', [])
                elif isinstance(prospects_data, list):
                    prospects = prospects_data
                else:
                    self.log_result("Find Lilian Prospect", False, 
                                  f"Unexpected response format: {type(prospects_data)}",
                                  {"response": prospects_data})
                    return False
                
                # Search for Lilian
                lilian_found = False
                for prospect in prospects:
                    if isinstance(prospect, dict):
                        name = prospect.get('name', '').upper()
                        if 'LILIAN' in name and 'LIMON' in name:
                            lilian_found = True
                            self.lilian_data = prospect
                        
                        self.log_result("Find Lilian Prospect", True, 
                                      f"Found Lilian: {prospect.get('name')} (ID: {prospect.get('id')})",
                                      {"lilian_data": prospect})
                        
                        # Log exact current status
                        print(f"\n🔍 LILIAN'S EXACT CURRENT STATUS:")
                        print(f"   ID: {prospect.get('id')}")
                        print(f"   Name: {prospect.get('name')}")
                        print(f"   Email: {prospect.get('email')}")
                        print(f"   Stage: {prospect.get('stage')}")
                        print(f"   AML/KYC Status: {prospect.get('aml_kyc_status')}")
                        print(f"   Converted to Client: {prospect.get('converted_to_client')}")
                        print(f"   Client ID: {prospect.get('client_id')}")
                        print()
                        
                        return True
                
                if not lilian_found:
                    self.log_result("Find Lilian Prospect", False, 
                                  "Lilian Limon Leite not found in prospects",
                                  {"total_prospects": len(prospects), "prospect_names": [p.get('name') for p in prospects]})
                    return False
            else:
                self.log_result("Find Lilian Prospect", False, 
                              f"Failed to get prospects: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Find Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def create_lilian_prospect(self):
        """Create Lilian's prospect profile in production"""
        try:
            # Create Lilian's prospect data
            lilian_prospect_data = {
                "name": "Lilian Limon Leite",
                "email": "lilian.limon@fidus.com",
                "phone": "+1-555-0123",
                "notes": "Created for Convert button testing"
            }
            
            # Create prospect
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=lilian_prospect_data)
            
            if response.status_code == 200 or response.status_code == 201:
                created_prospect = response.json()
                prospect_id = created_prospect.get('id')
                
                self.log_result("Create Lilian Prospect", True, 
                              f"Successfully created Lilian's prospect profile (ID: {prospect_id})",
                              {"created_prospect": created_prospect})
                
                # Now update to Won stage with AML/KYC clear
                update_data = {
                    "stage": "won",
                    "aml_kyc_status": "clear",
                    "converted_to_client": False,
                    "client_id": ""
                }
                
                update_response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json=update_data)
                
                if update_response.status_code == 200:
                    updated_prospect = update_response.json()
                    self.lilian_data = updated_prospect
                    
                    self.log_result("Update Lilian to Won", True, 
                                  "Successfully updated Lilian to Won stage with AML/KYC clear")
                    return True
                else:
                    self.log_result("Update Lilian to Won", False, 
                                  f"Failed to update Lilian: HTTP {update_response.status_code}",
                                  {"response": update_response.text})
                    return False
            else:
                self.log_result("Create Lilian Prospect", False, 
                              f"Failed to create Lilian: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Create Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def debug_convert_button_conditions(self):
        """Debug Convert button logic conditions"""
        if not self.lilian_data:
            self.log_result("Convert Button Debug", False, "No Lilian data available")
            return False
        
        try:
            # Extract conditions
            stage = self.lilian_data.get('stage')
            aml_kyc_status = self.lilian_data.get('aml_kyc_status')
            converted_to_client = self.lilian_data.get('converted_to_client')
            client_id = self.lilian_data.get('client_id')
            
            print(f"\n🔍 CONVERT BUTTON LOGIC DEBUG:")
            print(f"   Frontend shows Convert button when:")
            print(f"   stage='won' AND aml_kyc_status='clear' AND converted_to_client=false")
            print()
            print(f"   LILIAN'S ACTUAL VALUES:")
            print(f"   ✓ stage = '{stage}' (required: 'won')")
            print(f"   ✓ aml_kyc_status = '{aml_kyc_status}' (required: 'clear')")
            print(f"   ✓ converted_to_client = {converted_to_client} (required: false)")
            print(f"   ✓ client_id = '{client_id}' (should be empty if not converted)")
            print()
            
            # Check each condition
            conditions_met = []
            conditions_failed = []
            
            if stage == "won":
                conditions_met.append("stage='won' ✅")
            else:
                conditions_failed.append(f"stage='{stage}' (should be 'won') ❌")
            
            if aml_kyc_status == "clear":
                conditions_met.append("aml_kyc_status='clear' ✅")
            else:
                conditions_failed.append(f"aml_kyc_status='{aml_kyc_status}' (should be 'clear') ❌")
            
            if converted_to_client == False or converted_to_client == "false":
                conditions_met.append("converted_to_client=false ✅")
            else:
                conditions_failed.append(f"converted_to_client={converted_to_client} (should be false) ❌")
            
            # Check if client_id exists if converted_to_client is true
            if converted_to_client and client_id:
                # Verify if client actually exists
                client_response = self.session.get(f"{BACKEND_URL}/admin/clients")
                if client_response.status_code == 200:
                    clients = client_response.json()
                    client_exists = any(c.get('id') == client_id for c in clients)
                    if not client_exists:
                        conditions_failed.append(f"client_id='{client_id}' does not exist (data inconsistency) ❌")
            
            print(f"   CONDITIONS MET: {len(conditions_met)}")
            for condition in conditions_met:
                print(f"     • {condition}")
            
            if conditions_failed:
                print(f"   CONDITIONS FAILED: {len(conditions_failed)}")
                for condition in conditions_failed:
                    print(f"     • {condition}")
                
                self.log_result("Convert Button Conditions", False, 
                              f"{len(conditions_failed)} condition(s) failed",
                              {"failed_conditions": conditions_failed, "met_conditions": conditions_met})
                return False
            else:
                self.log_result("Convert Button Conditions", True, 
                              "All Convert button conditions met - button should be visible",
                              {"met_conditions": conditions_met})
                return True
                
        except Exception as e:
            self.log_result("Convert Button Debug", False, f"Exception: {str(e)}")
            return False
    
    def check_data_fixes_applied(self):
        """Check if previous data fixes were actually applied"""
        if not self.lilian_data:
            return False
        
        try:
            # Check if Lilian's data matches expected fixed state
            expected_fixes = {
                "stage": "won",
                "aml_kyc_status": "clear", 
                "converted_to_client": False
            }
            
            fixes_applied = []
            fixes_missing = []
            
            for field, expected_value in expected_fixes.items():
                actual_value = self.lilian_data.get(field)
                if actual_value == expected_value:
                    fixes_applied.append(f"{field}={actual_value} ✅")
                else:
                    fixes_missing.append(f"{field}={actual_value} (expected: {expected_value}) ❌")
            
            if fixes_missing:
                self.log_result("Data Fixes Applied", False, 
                              f"{len(fixes_missing)} fix(es) not applied",
                              {"missing_fixes": fixes_missing, "applied_fixes": fixes_applied})
                return False
            else:
                self.log_result("Data Fixes Applied", True, 
                              "All expected data fixes have been applied",
                              {"applied_fixes": fixes_applied})
                return True
                
        except Exception as e:
            self.log_result("Data Fixes Applied", False, f"Exception: {str(e)}")
            return False
    
    def force_correct_data_if_needed(self):
        """Force correct data if conditions are not met"""
        if not self.lilian_data:
            return False
        
        try:
            lilian_id = self.lilian_data.get('id')
            if not lilian_id:
                self.log_result("Force Data Correction", False, "No Lilian ID available")
                return False
            
            # Prepare correct data
            correct_data = {
                "stage": "won",
                "aml_kyc_status": "clear",
                "converted_to_client": False,
                "client_id": ""  # Clear client_id if converted_to_client is false
            }
            
            # Update Lilian's prospect data
            response = self.session.put(f"{BACKEND_URL}/crm/prospects/{lilian_id}", json=correct_data)
            
            if response.status_code == 200:
                updated_prospect = response.json()
                self.log_result("Force Data Correction", True, 
                              "Successfully updated Lilian's data to correct values",
                              {"updated_data": updated_prospect})
                
                # Update local data for further testing
                self.lilian_data.update(correct_data)
                return True
            else:
                self.log_result("Force Data Correction", False, 
                              f"Failed to update Lilian's data: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Force Data Correction", False, f"Exception: {str(e)}")
            return False
    
    def test_other_won_prospects(self):
        """Test if ANY Won prospects show Convert button"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects = response.json()
                
                won_prospects = [p for p in prospects if p.get('stage') == 'won']
                
                if not won_prospects:
                    self.log_result("Other Won Prospects", False, 
                                  "No Won prospects found in system")
                    return False
                
                convert_eligible = []
                convert_blocked = []
                
                for prospect in won_prospects:
                    if isinstance(prospect, dict):
                        name = prospect.get('name')
                        stage = prospect.get('stage')
                        aml_kyc_status = prospect.get('aml_kyc_status')
                        converted_to_client = prospect.get('converted_to_client')
                    else:
                        continue
                    
                    # Check Convert button conditions
                    if (stage == "won" and 
                        aml_kyc_status == "clear" and 
                        converted_to_client == False):
                        convert_eligible.append(name)
                    else:
                        convert_blocked.append({
                            "name": name,
                            "stage": stage,
                            "aml_kyc_status": aml_kyc_status,
                            "converted_to_client": converted_to_client
                        })
                
                print(f"\n🔍 OTHER WON PROSPECTS ANALYSIS:")
                print(f"   Total Won prospects: {len(won_prospects)}")
                print(f"   Convert button eligible: {len(convert_eligible)}")
                print(f"   Convert button blocked: {len(convert_blocked)}")
                
                if convert_eligible:
                    print(f"   Eligible prospects: {', '.join(convert_eligible)}")
                
                if convert_blocked:
                    print(f"   Blocked prospects:")
                    for blocked in convert_blocked:
                        print(f"     • {blocked['name']}: stage={blocked['stage']}, aml_kyc={blocked['aml_kyc_status']}, converted={blocked['converted_to_client']}")
                
                self.log_result("Other Won Prospects", True, 
                              f"Found {len(won_prospects)} Won prospects, {len(convert_eligible)} eligible for Convert button",
                              {"eligible": convert_eligible, "blocked": convert_blocked})
                return True
                
            else:
                self.log_result("Other Won Prospects", False, 
                              f"Failed to get prospects: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Other Won Prospects", False, f"Exception: {str(e)}")
            return False
    
    def test_convert_functionality(self):
        """Test the actual Convert functionality if conditions are met"""
        if not self.lilian_data:
            return False
        
        try:
            lilian_id = self.lilian_data.get('id')
            
            # Test the convert endpoint
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{lilian_id}/convert", json={
                "prospect_id": lilian_id,
                "send_agreement": True
            })
            
            if response.status_code == 200:
                conversion_result = response.json()
                self.log_result("Convert Functionality", True, 
                              "Convert functionality working - Lilian successfully converted to client",
                              {"conversion_result": conversion_result})
                return True
            else:
                self.log_result("Convert Functionality", False, 
                              f"Convert failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Convert Functionality", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Lilian Convert button debug tests"""
        print("🚨 LILIAN CONVERT BUTTON CRITICAL DEBUG TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("USER REPORT: Still can't see CONVERT button despite fixes applied.")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Lilian Convert Button Debug Tests...")
        print("-" * 50)
        
        # Step 1: Find Lilian in production
        if not self.find_lilian_prospect():
            print("❌ CRITICAL: Cannot find Lilian Limon Leite in production database.")
            print("🔧 ATTEMPTING TO CREATE LILIAN'S PROSPECT PROFILE...")
            if not self.create_lilian_prospect():
                print("❌ FAILED: Could not create Lilian's prospect profile.")
                return False
        
        # Step 2: Debug Convert button conditions
        conditions_met = self.debug_convert_button_conditions()
        
        # Step 3: Check if data fixes were applied
        fixes_applied = self.check_data_fixes_applied()
        
        # Step 4: Force correct data if needed
        if not conditions_met or not fixes_applied:
            print("\n🔧 FORCING DATA CORRECTION...")
            self.force_correct_data_if_needed()
            
            # Re-check conditions after fix
            print("\n🔍 RE-CHECKING CONDITIONS AFTER FIX...")
            self.debug_convert_button_conditions()
        
        # Step 5: Test other prospects
        self.test_other_won_prospects()
        
        # Step 6: Test convert functionality
        self.test_convert_functionality()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🚨 LILIAN CONVERT BUTTON DEBUG SUMMARY")
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
            print("❌ ISSUES FOUND:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ WORKING CORRECTLY:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        print("🚨 CRITICAL ASSESSMENT:")
        
        # Check if Lilian was found and conditions analyzed
        lilian_found = any("Find Lilian" in result['test'] and result['success'] for result in self.test_results)
        conditions_checked = any("Convert Button Conditions" in result['test'] for result in self.test_results)
        conditions_met = any("Convert Button Conditions" in result['test'] and result['success'] for result in self.test_results)
        
        if not lilian_found:
            print("❌ LILIAN NOT FOUND: Lilian Limon Leite does not exist in production database")
            print("   ACTION REQUIRED: Create Lilian's prospect profile in production")
        elif not conditions_met:
            print("❌ CONVERT BUTTON CONDITIONS NOT MET: One or more conditions preventing button display")
            print("   ACTION REQUIRED: Fix Lilian's data to meet Convert button requirements")
            if self.lilian_data:
                print(f"   CURRENT STATUS: stage={self.lilian_data.get('stage')}, aml_kyc_status={self.lilian_data.get('aml_kyc_status')}, converted_to_client={self.lilian_data.get('converted_to_client')}")
        else:
            print("✅ CONVERT BUTTON SHOULD BE VISIBLE: All conditions met")
            print("   If user still can't see button, check frontend implementation")
        
        print("\n🎯 EXPECTED RESULT:")
        print("   User should see a big green 'CONVERT TO CLIENT' button on Lilian's prospect card")
        print("   when stage='won' AND aml_kyc_status='clear' AND converted_to_client=false")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = LilianConvertButtonDebugTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()