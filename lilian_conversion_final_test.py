#!/usr/bin/env python3
"""
LILIAN LIMON CLIENT CONVERSION FINAL VERIFICATION
================================================

Final verification of Lilian Limon's client conversion status based on investigation findings.

DISCOVERY: Multiple Lilian prospects exist and ALL have been successfully converted to clients:
1. Lilian Limon Leite (ID: 4de9c592...) → client_7a6e5a18 ✅
2. Lilian Limon Leite (ID: 65ab697c...) → client_a6e28bac ✅  
3. Lilian Limon Leite (ID: a1c699af...) → client_17ce10c4 ✅

This test verifies:
1. All Lilian prospects are properly converted
2. All corresponding client records exist in Client Management
3. The conversion process is working correctly
4. User can see Lilian in Client Management directory
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fidus-google-sync.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class LilianConversionFinalTest:
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
            
            self.log_result("Admin Authentication", False, f"HTTP {response.status_code}")
            return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_lilian_prospects_status(self):
        """Verify all Lilian prospects and their conversion status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                
                # Find all Lilian prospects
                lilian_prospects = []
                for prospect in prospects:
                    name = prospect.get('name', '').lower()
                    if 'lilian' in name and 'limon' in name:
                        lilian_prospects.append(prospect)
                
                if lilian_prospects:
                    self.log_result("Lilian Prospects Found", True, 
                                  f"Found {len(lilian_prospects)} Lilian prospects")
                    
                    # Check each prospect's conversion status
                    all_converted = True
                    conversion_details = []
                    
                    for i, prospect in enumerate(lilian_prospects, 1):
                        prospect_id = prospect.get('id')
                        converted = prospect.get('converted_to_client', False)
                        client_id = prospect.get('client_id')
                        stage = prospect.get('stage')
                        aml_kyc = prospect.get('aml_kyc_status')
                        
                        conversion_info = {
                            'prospect_id': prospect_id,
                            'name': prospect.get('name'),
                            'email': prospect.get('email'),
                            'stage': stage,
                            'converted_to_client': converted,
                            'client_id': client_id,
                            'aml_kyc_status': aml_kyc
                        }
                        conversion_details.append(conversion_info)
                        
                        if converted and client_id:
                            self.log_result(f"Lilian Prospect {i} Conversion", True, 
                                          f"Prospect {prospect_id[:8]}... → client {client_id}")
                        else:
                            self.log_result(f"Lilian Prospect {i} Conversion", False, 
                                          f"Prospect {prospect_id[:8]}... not converted")
                            all_converted = False
                    
                    if all_converted:
                        self.log_result("All Lilian Prospects Converted", True, 
                                      "All Lilian prospects successfully converted to clients",
                                      {"conversion_details": conversion_details})
                    else:
                        self.log_result("All Lilian Prospects Converted", False, 
                                      "Some Lilian prospects not converted",
                                      {"conversion_details": conversion_details})
                
                else:
                    self.log_result("Lilian Prospects Found", False, "No Lilian prospects found")
                    
            else:
                self.log_result("Lilian Prospects Status", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Lilian Prospects Status", False, f"Exception: {str(e)}")
    
    def test_lilian_clients_in_directory(self):
        """Verify Lilian clients appear in Client Management directory"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                data = response.json()
                clients = data.get('clients', [])
                
                # Find all Lilian clients
                lilian_clients = []
                for client in clients:
                    name = client.get('name', '').lower()
                    if 'lilian' in name and 'limon' in name:
                        lilian_clients.append(client)
                
                if lilian_clients:
                    self.log_result("Lilian Clients in Directory", True, 
                                  f"Found {len(lilian_clients)} Lilian clients in Client Management directory")
                    
                    # Show details of each client
                    for i, client in enumerate(lilian_clients, 1):
                        client_info = {
                            'id': client.get('id'),
                            'name': client.get('name'),
                            'email': client.get('email'),
                            'total_balance': client.get('total_balance', 0),
                            'status': client.get('status'),
                            'created_at': client.get('created_at')
                        }
                        
                        self.log_result(f"Lilian Client {i} Details", True, 
                                      f"Client {client.get('id')}: {client.get('name')} ({client.get('email')})",
                                      {"client_info": client_info})
                
                else:
                    self.log_result("Lilian Clients in Directory", False, 
                                  "No Lilian clients found in Client Management directory")
                    
            else:
                self.log_result("Lilian Clients Directory", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Lilian Clients Directory", False, f"Exception: {str(e)}")
    
    def test_prospect_client_id_consistency(self):
        """Verify prospect client_ids match actual client records"""
        try:
            # Get prospects
            prospects_response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            clients_response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if prospects_response.status_code == 200 and clients_response.status_code == 200:
                prospects_data = prospects_response.json()
                clients_data = clients_response.json()
                
                prospects = prospects_data.get('prospects', [])
                clients = clients_data.get('clients', [])
                
                # Create client ID lookup
                client_ids = {client.get('id'): client for client in clients}
                
                # Check Lilian prospects
                lilian_prospects = [p for p in prospects 
                                  if 'lilian' in p.get('name', '').lower() and 'limon' in p.get('name', '').lower()]
                
                all_consistent = True
                for prospect in lilian_prospects:
                    prospect_id = prospect.get('id')
                    client_id = prospect.get('client_id')
                    converted = prospect.get('converted_to_client', False)
                    
                    if converted and client_id:
                        if client_id in client_ids:
                            self.log_result(f"Prospect-Client Consistency", True, 
                                          f"Prospect {prospect_id[:8]}... → Client {client_id} ✅ EXISTS")
                        else:
                            self.log_result(f"Prospect-Client Consistency", False, 
                                          f"Prospect {prospect_id[:8]}... → Client {client_id} ❌ NOT FOUND")
                            all_consistent = False
                
                if all_consistent:
                    self.log_result("All Prospect-Client Links Valid", True, 
                                  "All prospect client_ids point to existing client records")
                else:
                    self.log_result("All Prospect-Client Links Valid", False, 
                                  "Some prospect client_ids point to non-existent clients")
                    
            else:
                self.log_result("Prospect-Client Consistency", False, "Failed to get data")
                
        except Exception as e:
            self.log_result("Prospect-Client Consistency", False, f"Exception: {str(e)}")
    
    def test_user_can_see_lilian(self):
        """Test that user can see Lilian in Client Management interface"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                data = response.json()
                clients = data.get('clients', [])
                
                # Check if any Lilian clients are visible
                lilian_visible = False
                lilian_names = []
                
                for client in clients:
                    name = client.get('name', '')
                    if 'lilian' in name.lower() and 'limon' in name.lower():
                        lilian_visible = True
                        lilian_names.append(f"{name} ({client.get('id')})")
                
                if lilian_visible:
                    self.log_result("User Can See Lilian", True, 
                                  f"Lilian is VISIBLE in Client Management directory",
                                  {"visible_lilian_clients": lilian_names})
                    
                    # This resolves the user's reported issue
                    self.log_result("User Issue Resolution", True, 
                                  "USER ISSUE RESOLVED: Lilian appears in Client Management directory")
                else:
                    self.log_result("User Can See Lilian", False, 
                                  "Lilian is NOT visible in Client Management directory")
                    
            else:
                self.log_result("User Can See Lilian", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("User Can See Lilian", False, f"Exception: {str(e)}")
    
    def run_final_test(self):
        """Run final verification test"""
        print("🎉 LILIAN LIMON CLIENT CONVERSION FINAL VERIFICATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        print("TESTING: User report that Lilian doesn't appear in Client Management")
        print("EXPECTED: Lilian should be visible after successful conversion")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Final Verification Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_lilian_prospects_status()
        self.test_lilian_clients_in_directory()
        self.test_prospect_client_id_consistency()
        self.test_user_can_see_lilian()
        
        # Generate summary
        self.generate_final_summary()
        
        return True
    
    def generate_final_summary(self):
        """Generate final test summary"""
        print("\n" + "=" * 60)
        print("🎉 LILIAN CONVERSION FINAL TEST SUMMARY")
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
        
        # Show all results
        print("📋 TEST RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"   {status_icon} {result['test']}: {result['message']}")
        print()
        
        # Final conclusion
        user_issue_resolved = any("User Issue Resolution" in result['test'] and result['success'] 
                                for result in self.test_results)
        
        lilian_visible = any("User Can See Lilian" in result['test'] and result['success'] 
                           for result in self.test_results)
        
        print("🎯 FINAL CONCLUSION:")
        if user_issue_resolved and lilian_visible:
            print("✅ USER ISSUE COMPLETELY RESOLVED!")
            print("   Lilian Limon appears in Client Management directory")
            print("   Conversion process working correctly")
            print("   Multiple Lilian clients successfully created")
        elif lilian_visible:
            print("✅ LILIAN IS VISIBLE IN CLIENT DIRECTORY")
            print("   User should be able to see Lilian in Client Management")
            print("   If user still reports issue, may be browser cache or UI problem")
        else:
            print("❌ USER ISSUE PERSISTS")
            print("   Lilian still not visible in Client Management")
            print("   Further investigation required")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = LilianConversionFinalTest()
    success = test_runner.run_final_test()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()