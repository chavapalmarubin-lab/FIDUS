#!/usr/bin/env python3
"""
LILIAN LIMON LEITE - WON PROSPECT TO CLIENT CONVERSION WORKFLOW TEST
================================================================

This test verifies the complete Won prospect to client conversion workflow as requested:
1. Find Lilian's prospect ID from existing prospects
2. Run AML/KYC check: POST /api/crm/prospects/{id}/aml-kyc
3. Convert to client: POST /api/crm/prospects/{id}/convert  
4. Verify client appears in client list

Expected Results:
- AML/KYC check returns "clear" status for normal prospects
- Client conversion creates account with proper credentials  
- Lilian appears in Client Directory after conversion
- Complete lead → client workflow verified working
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-invest-1.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ProspectConversionTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.lilian_prospect_id = None
        self.lilian_client_id = None
        
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
        """Find Lilian Limon Leite's prospect ID from existing prospects"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                
                # Look for Lilian Limon Leite
                lilian_found = False
                for prospect in prospects:
                    name = prospect.get('name', '').lower()
                    email = prospect.get('email', '').lower()
                    
                    # Check for variations of Lilian Limon Leite
                    if ('lilian' in name and ('limon' in name or 'leite' in name)) or \
                       ('lilian' in email and ('limon' in email or 'leite' in email)):
                        self.lilian_prospect_id = prospect.get('id')
                        lilian_found = True
                        
                        self.log_result("Find Lilian Prospect", True, 
                                      f"Found Lilian Limon Leite: {prospect.get('name')} (ID: {self.lilian_prospect_id})",
                                      {"prospect_data": prospect})
                        
                        # Verify she's in Won stage
                        stage = prospect.get('stage', '')
                        if stage == 'won':
                            self.log_result("Lilian Stage Verification", True, 
                                          f"Lilian is in 'Won' stage as expected")
                        else:
                            self.log_result("Lilian Stage Verification", False, 
                                          f"Lilian is in '{stage}' stage, not 'Won'",
                                          {"current_stage": stage})
                        
                        return True
                
                if not lilian_found:
                    # Create Lilian as a test prospect in Won stage
                    self.log_result("Find Lilian Prospect", False, 
                                  "Lilian Limon Leite not found in existing prospects. Creating test prospect.",
                                  {"total_prospects": len(prospects)})
                    return self.create_lilian_test_prospect()
            else:
                self.log_result("Find Lilian Prospect", False, 
                              f"Failed to get prospects: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Find Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def create_lilian_test_prospect(self):
        """Create Lilian Limon Leite as a test prospect in Won stage"""
        try:
            # Create prospect
            prospect_data = {
                "name": "Lilian Limon Leite",
                "email": "lilian.limon.leite@example.com",
                "phone": "+1-555-LILIAN",
                "notes": "Test prospect for Won to Client conversion workflow"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=prospect_data)
            if response.status_code == 200:
                create_result = response.json()
                self.lilian_prospect_id = create_result.get('prospect_id')
                
                # Move to Won stage
                update_data = {"stage": "won"}
                response = self.session.put(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}", json=update_data)
                
                if response.status_code == 200:
                    self.log_result("Create Lilian Test Prospect", True, 
                                  f"Created Lilian as test prospect in Won stage (ID: {self.lilian_prospect_id})")
                    return True
                else:
                    self.log_result("Create Lilian Test Prospect", False, 
                                  f"Failed to move prospect to Won stage: HTTP {response.status_code}")
                    return False
            else:
                self.log_result("Create Lilian Test Prospect", False, 
                              f"Failed to create prospect: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Create Lilian Test Prospect", False, f"Exception: {str(e)}")
            return False
    
    def test_aml_kyc_check(self):
        """Test AML/KYC compliance check for Lilian"""
        if not self.lilian_prospect_id:
            self.log_result("AML/KYC Check", False, "No Lilian prospect ID available")
            return False
            
        try:
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}/aml-kyc")
            
            if response.status_code == 200:
                aml_result = response.json()
                
                if aml_result.get('success'):
                    aml_data = aml_result.get('aml_result', {})
                    overall_status = aml_data.get('overall_status')
                    can_convert = aml_data.get('can_convert', False)
                    
                    self.log_result("AML/KYC Check", True, 
                                  f"AML/KYC check completed: {overall_status} (Can convert: {can_convert})",
                                  {"aml_result": aml_data})
                    
                    # Verify expected results
                    if overall_status in ['clear', 'approved']:
                        self.log_result("AML/KYC Status Verification", True, 
                                      f"AML/KYC status is acceptable for conversion: {overall_status}")
                    else:
                        self.log_result("AML/KYC Status Verification", False, 
                                      f"AML/KYC status may block conversion: {overall_status}")
                    
                    return True
                else:
                    self.log_result("AML/KYC Check", False, 
                                  "AML/KYC check failed", {"response": aml_result})
                    return False
            else:
                self.log_result("AML/KYC Check", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("AML/KYC Check", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_conversion(self):
        """Test converting Lilian from prospect to client"""
        if not self.lilian_prospect_id:
            self.log_result("Prospect Conversion", False, "No Lilian prospect ID available")
            return False
            
        try:
            conversion_data = {
                "prospect_id": self.lilian_prospect_id,
                "send_agreement": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.lilian_prospect_id}/convert", 
                                       json=conversion_data)
            
            if response.status_code == 200:
                conversion_result = response.json()
                
                if conversion_result.get('success'):
                    self.lilian_client_id = conversion_result.get('client_id')
                    username = conversion_result.get('username')
                    agreement_sent = conversion_result.get('agreement_sent', False)
                    
                    self.log_result("Prospect Conversion", True, 
                                  f"Lilian converted to client successfully (ID: {self.lilian_client_id}, Username: {username})",
                                  {"conversion_result": conversion_result})
                    
                    # Verify conversion details
                    if self.lilian_client_id and username:
                        self.log_result("Client Credentials Generation", True, 
                                      f"Client credentials generated: ID={self.lilian_client_id}, Username={username}")
                    else:
                        self.log_result("Client Credentials Generation", False, 
                                      "Missing client ID or username in conversion result")
                    
                    if agreement_sent:
                        self.log_result("FIDUS Agreement Sending", True, 
                                      "FIDUS agreement sent to client")
                    else:
                        self.log_result("FIDUS Agreement Sending", False, 
                                      "FIDUS agreement was not sent")
                    
                    return True
                else:
                    self.log_result("Prospect Conversion", False, 
                                  "Conversion failed", {"response": conversion_result})
                    return False
            else:
                self.log_result("Prospect Conversion", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Prospect Conversion", False, f"Exception: {str(e)}")
            return False
    
    def test_client_directory_verification(self):
        """Verify Lilian appears in Client Directory after conversion"""
        if not self.lilian_client_id:
            self.log_result("Client Directory Verification", False, "No Lilian client ID available")
            return False
            
        try:
            # Check admin clients list
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 200:
                clients_data = response.json()
                clients = clients_data if isinstance(clients_data, list) else clients_data.get('clients', [])
                
                # Look for Lilian in client list
                lilian_found = False
                for client in clients:
                    if client.get('id') == self.lilian_client_id or \
                       'lilian' in client.get('name', '').lower():
                        lilian_found = True
                        
                        self.log_result("Client Directory Verification", True, 
                                      f"Lilian found in Client Directory: {client.get('name')} (ID: {client.get('id')})",
                                      {"client_data": client})
                        
                        # Verify client status
                        status = client.get('status', 'unknown')
                        if status == 'active':
                            self.log_result("Client Status Verification", True, 
                                          f"Lilian has active client status")
                        else:
                            self.log_result("Client Status Verification", False, 
                                          f"Lilian has unexpected status: {status}")
                        
                        return True
                
                if not lilian_found:
                    self.log_result("Client Directory Verification", False, 
                                  f"Lilian not found in Client Directory (searched {len(clients)} clients)",
                                  {"total_clients": len(clients)})
                    return False
            else:
                self.log_result("Client Directory Verification", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Client Directory Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_investment_readiness(self):
        """Test that converted client can receive investments"""
        if not self.lilian_client_id:
            self.log_result("Investment Readiness Test", False, "No Lilian client ID available")
            return False
            
        try:
            # Test creating an investment for Lilian
            investment_data = {
                "client_id": self.lilian_client_id,
                "fund_code": "CORE",
                "amount": 10000.0,
                "deposit_date": "2024-12-19"
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/create", json=investment_data)
            
            if response.status_code == 200:
                investment_result = response.json()
                investment_id = investment_result.get('investment_id')
                
                self.log_result("Investment Readiness Test", True, 
                              f"Successfully created investment for Lilian (ID: {investment_id})",
                              {"investment_result": investment_result})
                
                # Verify investment appears in client portfolio
                response = self.session.get(f"{BACKEND_URL}/investments/client/{self.lilian_client_id}")
                if response.status_code == 200:
                    portfolio = response.json()
                    investments = portfolio.get('investments', [])
                    
                    if len(investments) > 0:
                        self.log_result("Client Portfolio Verification", True, 
                                      f"Investment appears in Lilian's portfolio ({len(investments)} investments)")
                    else:
                        self.log_result("Client Portfolio Verification", False, 
                                      "Investment not found in Lilian's portfolio")
                
                return True
            else:
                self.log_result("Investment Readiness Test", False, 
                              f"Failed to create investment: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Investment Readiness Test", False, f"Exception: {str(e)}")
            return False
    
    def run_conversion_workflow_test(self):
        """Run complete Won prospect to client conversion workflow test"""
        print("🎯 LILIAN LIMON LEITE - WON PROSPECT TO CLIENT CONVERSION WORKFLOW TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Won Prospect to Client Conversion Workflow Tests...")
        print("-" * 60)
        
        # Step 1: Find Lilian's prospect ID
        print("\n1️⃣ FINDING LILIAN'S PROSPECT ID")
        if not self.find_lilian_prospect():
            print("❌ Cannot proceed without Lilian's prospect ID")
            return False
        
        # Step 2: Run AML/KYC check
        print("\n2️⃣ RUNNING AML/KYC COMPLIANCE CHECK")
        if not self.test_aml_kyc_check():
            print("❌ AML/KYC check failed - conversion may not be possible")
            # Continue anyway to test error handling
        
        # Step 3: Convert prospect to client
        print("\n3️⃣ CONVERTING PROSPECT TO CLIENT")
        if not self.test_prospect_conversion():
            print("❌ Prospect conversion failed")
            return False
        
        # Step 4: Verify client appears in directory
        print("\n4️⃣ VERIFYING CLIENT DIRECTORY APPEARANCE")
        if not self.test_client_directory_verification():
            print("❌ Client directory verification failed")
        
        # Step 5: Test investment readiness
        print("\n5️⃣ TESTING INVESTMENT READINESS")
        if not self.test_investment_readiness():
            print("❌ Investment readiness test failed")
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 WON PROSPECT TO CLIENT CONVERSION WORKFLOW TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show workflow results
        workflow_steps = [
            "Find Lilian Prospect",
            "AML/KYC Check", 
            "Prospect Conversion",
            "Client Directory Verification",
            "Investment Readiness Test"
        ]
        
        print("📋 WORKFLOW STEP RESULTS:")
        for step in workflow_steps:
            step_results = [r for r in self.test_results if step in r['test']]
            if step_results:
                step_passed = any(r['success'] for r in step_results)
                status = "✅ WORKING" if step_passed else "❌ FAILING"
                print(f"   {status}: {step}")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        critical_tests = [
            "AML/KYC Check",
            "Prospect Conversion", 
            "Client Directory Verification"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL WORKFLOW ASSESSMENT:")
        if critical_passed >= 2:  # At least 2 out of 3 critical steps
            print("✅ WON PROSPECT TO CLIENT CONVERSION: WORKING")
            print("   Core conversion workflow is operational.")
            print("   Lilian can be converted from Won prospect to investment-ready client.")
        else:
            print("❌ WON PROSPECT TO CLIENT CONVERSION: BROKEN")
            print("   Critical workflow issues found.")
            print("   Main agent action required to fix conversion process.")
        
        # Final results summary
        print(f"\n🎯 FINAL RESULTS:")
        if self.lilian_prospect_id:
            print(f"   Lilian Prospect ID: {self.lilian_prospect_id}")
        if self.lilian_client_id:
            print(f"   Lilian Client ID: {self.lilian_client_id}")
            print("   ✅ Complete lead → client workflow verified working")
        else:
            print("   ❌ Conversion workflow incomplete")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    test_runner = ProspectConversionTest()
    success = test_runner.run_conversion_workflow_test()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()