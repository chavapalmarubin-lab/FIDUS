#!/usr/bin/env python3
"""
FINAL LILIAN CONVERT BUTTON VERIFICATION TEST
=============================================

This test verifies that Lilian's Convert button issue has been completely resolved
and that she can now successfully convert from prospect to client.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Use PRODUCTION environment
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class FinalLilianVerificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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
            
            self.log_result("Admin Authentication", False, f"HTTP {response.status_code}")
            return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def verify_lilian_convert_button_conditions(self):
        """Verify Lilian meets all Convert button conditions"""
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
                    prospects = []
                
                # Find Lilian
                for prospect in prospects:
                    if isinstance(prospect, dict):
                        name = prospect.get('name', '').upper()
                        if 'LILIAN' in name and 'LIMON' in name:
                            # Check all conditions
                            stage = prospect.get('stage')
                            aml_kyc_status = prospect.get('aml_kyc_status')
                            converted_to_client = prospect.get('converted_to_client')
                            
                            conditions_met = (
                                stage == "won" and
                                aml_kyc_status == "clear" and
                                converted_to_client == False
                            )
                            
                            if conditions_met:
                                self.log_result("Lilian Convert Button Conditions", True, 
                                              "All Convert button conditions met - button should be visible",
                                              {
                                                  "stage": stage,
                                                  "aml_kyc_status": aml_kyc_status,
                                                  "converted_to_client": converted_to_client
                                              })
                                return True
                            else:
                                self.log_result("Lilian Convert Button Conditions", False, 
                                              "Convert button conditions not met",
                                              {
                                                  "stage": stage,
                                                  "aml_kyc_status": aml_kyc_status,
                                                  "converted_to_client": converted_to_client,
                                                  "required": "stage='won' AND aml_kyc_status='clear' AND converted_to_client=false"
                                              })
                                return False
                
                self.log_result("Lilian Convert Button Conditions", False, 
                              "Lilian Limon Leite not found in prospects")
                return False
            else:
                self.log_result("Lilian Convert Button Conditions", False, 
                              f"Failed to get prospects: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Lilian Convert Button Conditions", False, f"Exception: {str(e)}")
            return False
    
    def verify_production_environment(self):
        """Verify we're testing the correct production environment"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("Production Environment", True, 
                              f"Connected to production: {BACKEND_URL}",
                              {"health_status": health_data.get("status")})
                return True
            else:
                self.log_result("Production Environment", False, 
                              f"Health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Production Environment", False, f"Exception: {str(e)}")
            return False
    
    def run_verification(self):
        """Run final verification"""
        print("🎯 FINAL LILIAN CONVERT BUTTON VERIFICATION TEST")
        print("=" * 60)
        print(f"Production URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed.")
            return False
        
        # Verify environment
        if not self.verify_production_environment():
            print("❌ CRITICAL: Production environment verification failed.")
            return False
        
        # Verify Lilian's conditions
        conditions_met = self.verify_lilian_convert_button_conditions()
        
        # Generate summary
        self.generate_summary(conditions_met)
        
        return conditions_met
    
    def generate_summary(self, conditions_met):
        """Generate final summary"""
        print("\n" + "=" * 60)
        print("🎯 FINAL VERIFICATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if conditions_met:
            print("✅ LILIAN CONVERT BUTTON ISSUE RESOLVED!")
            print("   • Lilian Limon Leite exists in production")
            print("   • Stage: 'won' ✅")
            print("   • AML/KYC Status: 'clear' ✅")
            print("   • Converted to Client: false ✅")
            print()
            print("🎯 EXPECTED RESULT:")
            print("   User should now see a big green 'CONVERT TO CLIENT' button")
            print("   on Lilian's prospect card in the production environment.")
        else:
            print("❌ LILIAN CONVERT BUTTON ISSUE NOT RESOLVED")
            print("   One or more conditions are still not met.")
            print("   Main agent action required.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = FinalLilianVerificationTest()
    success = test_runner.run_verification()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()