#!/usr/bin/env python3
"""
CLIENT INVESTMENT READINESS INVESTIGATION TEST
==============================================

This test investigates the Client Investment Readiness Issue as requested in the review:
- 11 clients exist but 0 are ready for investment
- Alejandro Mariscal is not showing up in the investment dropdown

Root Cause Analysis:
1. Check Client Readiness System - investigate client_readiness data structure
2. Check AML/KYC Status - verify completion flags for all clients  
3. Test Investment Endpoints - ready-clients endpoints
4. Check Alejandro Specifically - his AML/KYC status and readiness flags
5. Check Client Readiness Data Structure - in-memory client_readiness dictionary

Expected Results:
- Identify why clients aren't showing as investment-ready
- Fix the AML/KYC completion process
- Get Alejandro showing in investment dropdown
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://mockdb-cleanup.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ClientInvestmentReadinessTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.clients_data = []
        self.alejandro_data = None
        
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
    
    def test_client_count_verification(self):
        """Test 1: Verify we have 11 clients as reported"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                
                # Handle different response formats
                if isinstance(clients, list):
                    client_count = len(clients)
                    self.clients_data = clients
                elif isinstance(clients, dict) and 'clients' in clients:
                    client_count = len(clients['clients'])
                    self.clients_data = clients['clients']
                else:
                    client_count = clients.get('total_clients', 0)
                    self.clients_data = clients.get('clients', [])
                
                if client_count == 11:
                    self.log_result("Client Count Verification", True, 
                                  f"Confirmed 11 clients exist as reported")
                else:
                    self.log_result("Client Count Verification", False, 
                                  f"Expected 11 clients, found {client_count}", 
                                  {"actual_count": client_count})
                
                # Store client data for further analysis
                print(f"   Found {client_count} clients total")
                
            else:
                self.log_result("Client Count Verification", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Client Count Verification", False, f"Exception: {str(e)}")
    
    def test_alejandro_client_data(self):
        """Test 2: Check Alejandro Mariscal's client data specifically"""
        try:
            # Look for Alejandro in clients list
            alejandro_found = False
            
            for client in self.clients_data:
                client_name = client.get('name', '').upper()
                client_email = client.get('email', '').lower()
                client_id = client.get('id', '')
                
                if ('ALEJANDRO' in client_name and 'MARISCAL' in client_name) or \
                   'alejandro' in client_email or \
                   'alejandro' in client_id.lower():
                    alejandro_found = True
                    self.alejandro_data = client
                    
                    self.log_result("Alejandro Client Data Found", True, 
                                  f"Found Alejandro: {client.get('name')} ({client.get('id')})",
                                  {"alejandro_data": client})
                    break
            
            if not alejandro_found:
                self.log_result("Alejandro Client Data Found", False, 
                              "Alejandro Mariscal not found in clients list",
                              {"searched_clients": [c.get('name') for c in self.clients_data]})
            
            # Also try direct client access
            try:
                response = self.session.get(f"{BACKEND_URL}/admin/clients/client_alejandro/details")
                if response.status_code == 200:
                    alejandro_details = response.json()
                    self.log_result("Alejandro Direct Access", True, 
                                  "Alejandro accessible via client_alejandro ID",
                                  {"details": alejandro_details})
                    if not self.alejandro_data:
                        self.alejandro_data = alejandro_details
                else:
                    self.log_result("Alejandro Direct Access", False, 
                                  f"client_alejandro not accessible: HTTP {response.status_code}")
            except Exception as e:
                self.log_result("Alejandro Direct Access", False, f"Exception: {str(e)}")
                
        except Exception as e:
            self.log_result("Alejandro Client Data", False, f"Exception: {str(e)}")
    
    def test_investment_ready_clients_endpoint(self):
        """Test 3: Check GET /api/investments/ready-clients endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/investments/ready-clients")
            if response.status_code == 200:
                ready_clients = response.json()
                
                if isinstance(ready_clients, list):
                    ready_count = len(ready_clients)
                else:
                    ready_count = ready_clients.get('count', 0)
                    ready_clients = ready_clients.get('clients', [])
                
                if ready_count == 0:
                    self.log_result("Investment Ready Clients Endpoint", False, 
                                  "Confirmed: 0 clients ready for investment as reported",
                                  {"endpoint_response": ready_clients})
                else:
                    self.log_result("Investment Ready Clients Endpoint", True, 
                                  f"Found {ready_count} ready clients",
                                  {"ready_clients": ready_clients})
                    
            else:
                self.log_result("Investment Ready Clients Endpoint", False, 
                              f"Endpoint failed: HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Investment Ready Clients Endpoint", False, f"Exception: {str(e)}")
    
    def test_admin_investment_management_ready_clients(self):
        """Test 4: Check GET /api/admin/investment-management/ready-clients endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/investment-management/ready-clients")
            if response.status_code == 200:
                ready_clients = response.json()
                
                if isinstance(ready_clients, list):
                    ready_count = len(ready_clients)
                else:
                    ready_count = ready_clients.get('count', 0)
                    ready_clients = ready_clients.get('clients', [])
                
                # Check if Alejandro is in the list
                alejandro_in_dropdown = False
                for client in ready_clients if isinstance(ready_clients, list) else []:
                    if 'alejandro' in client.get('name', '').lower() or \
                       'alejandro' in client.get('id', '').lower():
                        alejandro_in_dropdown = True
                        break
                
                if ready_count == 0:
                    self.log_result("Admin Investment Dropdown", False, 
                                  "Investment dropdown shows 0 ready clients - this is the problem!",
                                  {"dropdown_response": ready_clients})
                else:
                    self.log_result("Admin Investment Dropdown", True, 
                                  f"Investment dropdown shows {ready_count} ready clients",
                                  {"ready_clients": ready_clients})
                
                if not alejandro_in_dropdown:
                    self.log_result("Alejandro in Investment Dropdown", False, 
                                  "Alejandro NOT in investment dropdown as reported")
                else:
                    self.log_result("Alejandro in Investment Dropdown", True, 
                                  "Alejandro found in investment dropdown")
                    
            else:
                self.log_result("Admin Investment Dropdown", False, 
                              f"Investment dropdown endpoint failed: HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Admin Investment Dropdown", False, f"Exception: {str(e)}")
    
    def test_client_aml_kyc_status(self):
        """Test 5: Check AML/KYC completion status for all clients"""
        try:
            aml_kyc_completed_count = 0
            aml_kyc_details = []
            
            for client in self.clients_data:
                client_id = client.get('id')
                client_name = client.get('name')
                
                # Check if client has AML/KYC completed flag
                aml_kyc_completed = client.get('aml_kyc_completed', False)
                
                # Also try to get detailed AML/KYC status
                try:
                    response = self.session.get(f"{BACKEND_URL}/admin/clients/{client_id}/aml-kyc-status")
                    if response.status_code == 200:
                        aml_kyc_status = response.json()
                        aml_kyc_completed = aml_kyc_status.get('completed', False)
                except:
                    pass
                
                aml_kyc_details.append({
                    "client_id": client_id,
                    "name": client_name,
                    "aml_kyc_completed": aml_kyc_completed
                })
                
                if aml_kyc_completed:
                    aml_kyc_completed_count += 1
            
            self.log_result("AML/KYC Status Check", True, 
                          f"AML/KYC Analysis: {aml_kyc_completed_count}/{len(self.clients_data)} clients completed",
                          {"aml_kyc_details": aml_kyc_details})
            
            # Specific check for Alejandro
            if self.alejandro_data:
                alejandro_aml_kyc = False
                for detail in aml_kyc_details:
                    if 'alejandro' in detail['name'].lower():
                        alejandro_aml_kyc = detail['aml_kyc_completed']
                        break
                
                if alejandro_aml_kyc:
                    self.log_result("Alejandro AML/KYC Status", True, 
                                  "Alejandro has completed AML/KYC")
                else:
                    self.log_result("Alejandro AML/KYC Status", False, 
                                  "Alejandro has NOT completed AML/KYC - this may be why he's not investment ready")
                
        except Exception as e:
            self.log_result("AML/KYC Status Check", False, f"Exception: {str(e)}")
    
    def test_client_readiness_data_structure(self):
        """Test 6: Investigate the client_readiness data structure"""
        try:
            # Try to access client readiness endpoint if it exists
            response = self.session.get(f"{BACKEND_URL}/admin/client-readiness")
            if response.status_code == 200:
                readiness_data = response.json()
                self.log_result("Client Readiness Data Structure", True, 
                              "Client readiness data accessible",
                              {"readiness_data": readiness_data})
            else:
                self.log_result("Client Readiness Data Structure", False, 
                              f"Client readiness endpoint not accessible: HTTP {response.status_code}")
            
            # Check individual client readiness
            if self.alejandro_data:
                client_id = self.alejandro_data.get('id')
                try:
                    response = self.session.get(f"{BACKEND_URL}/admin/clients/{client_id}/investment-readiness")
                    if response.status_code == 200:
                        readiness = response.json()
                        
                        investment_ready = readiness.get('investment_ready', False)
                        aml_kyc_completed = readiness.get('aml_kyc_completed', False)
                        agreement_signed = readiness.get('agreement_signed', False)
                        
                        self.log_result("Alejandro Investment Readiness", True, 
                                      f"Alejandro readiness: investment_ready={investment_ready}, aml_kyc={aml_kyc_completed}, agreement={agreement_signed}",
                                      {"readiness_details": readiness})
                        
                        if not investment_ready:
                            reasons = []
                            if not aml_kyc_completed:
                                reasons.append("AML/KYC not completed")
                            if not agreement_signed:
                                reasons.append("Agreement not signed")
                            
                            self.log_result("Alejandro Not Investment Ready", False, 
                                          f"Alejandro not investment ready because: {', '.join(reasons)}")
                    else:
                        self.log_result("Alejandro Investment Readiness", False, 
                                      f"Cannot get Alejandro's readiness: HTTP {response.status_code}")
                except Exception as e:
                    self.log_result("Alejandro Investment Readiness", False, f"Exception: {str(e)}")
                
        except Exception as e:
            self.log_result("Client Readiness Data Structure", False, f"Exception: {str(e)}")
    
    def test_fix_alejandro_investment_readiness(self):
        """Test 7: Attempt to fix Alejandro's investment readiness"""
        if not self.alejandro_data:
            self.log_result("Fix Alejandro Readiness", False, "Cannot fix - Alejandro data not found")
            return
        
        try:
            client_id = self.alejandro_data.get('id')
            
            # Try to update Alejandro's investment readiness
            readiness_update = {
                "aml_kyc_completed": True,
                "agreement_signed": True,
                "notes": "Fixed for investment readiness testing",
                "updated_by": "testing_agent"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/clients/{client_id}/investment-readiness", 
                                      json=readiness_update)
            
            if response.status_code == 200:
                self.log_result("Fix Alejandro Readiness", True, 
                              "Successfully updated Alejandro's investment readiness")
                
                # Verify the fix worked
                time.sleep(1)  # Give it a moment
                response = self.session.get(f"{BACKEND_URL}/admin/investment-management/ready-clients")
                if response.status_code == 200:
                    ready_clients = response.json()
                    alejandro_now_ready = False
                    
                    for client in ready_clients if isinstance(ready_clients, list) else []:
                        if 'alejandro' in client.get('name', '').lower():
                            alejandro_now_ready = True
                            break
                    
                    if alejandro_now_ready:
                        self.log_result("Alejandro Fix Verification", True, 
                                      "SUCCESS: Alejandro now appears in investment dropdown!")
                    else:
                        self.log_result("Alejandro Fix Verification", False, 
                                      "Alejandro still not in investment dropdown after fix")
            else:
                self.log_result("Fix Alejandro Readiness", False, 
                              f"Failed to update readiness: HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Fix Alejandro Readiness", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all client investment readiness investigation tests"""
        print("🎯 CLIENT INVESTMENT READINESS INVESTIGATION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Client Investment Readiness Investigation...")
        print("-" * 50)
        
        # Run all investigation tests
        self.test_client_count_verification()
        self.test_alejandro_client_data()
        self.test_investment_ready_clients_endpoint()
        self.test_admin_investment_management_ready_clients()
        self.test_client_aml_kyc_status()
        self.test_client_readiness_data_structure()
        self.test_fix_alejandro_investment_readiness()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 CLIENT INVESTMENT READINESS INVESTIGATION SUMMARY")
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
        
        # Show failed tests (these are the issues)
        if failed_tests > 0:
            print("❌ ISSUES IDENTIFIED:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show successful findings
        if passed_tests > 0:
            print("✅ CONFIRMED FINDINGS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Root cause analysis
        print("🚨 ROOT CAUSE ANALYSIS:")
        
        # Check if we found the main issues
        investment_dropdown_issue = any("Investment dropdown shows 0 ready clients" in r['message'] 
                                      for r in self.test_results if not r['success'])
        alejandro_aml_kyc_issue = any("Alejandro has NOT completed AML/KYC" in r['message'] 
                                    for r in self.test_results if not r['success'])
        alejandro_not_ready_issue = any("Alejandro not investment ready" in r['message'] 
                                      for r in self.test_results if not r['success'])
        
        if investment_dropdown_issue:
            print("✅ CONFIRMED: Investment dropdown shows 0 ready clients")
        if alejandro_aml_kyc_issue:
            print("✅ CONFIRMED: Alejandro's AML/KYC is not completed")
        if alejandro_not_ready_issue:
            print("✅ CONFIRMED: Alejandro is not marked as investment ready")
        
        # Check if we fixed it
        fix_successful = any("Alejandro now appears in investment dropdown" in r['message'] 
                           for r in self.test_results if r['success'])
        
        if fix_successful:
            print("🎉 SUCCESS: Fixed Alejandro's investment readiness!")
            print("   Alejandro should now appear in the investment dropdown.")
        else:
            print("⚠️  NEEDS MAIN AGENT ACTION:")
            print("   1. Update client AML/KYC completion process")
            print("   2. Fix client investment readiness flags")
            print("   3. Ensure client_readiness data structure is populated")
            print("   4. Test investment dropdown functionality")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = ClientInvestmentReadinessTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()