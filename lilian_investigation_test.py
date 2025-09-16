#!/usr/bin/env python3
"""
LILIAN LIMON LEITE CLIENT CONVERSION INVESTIGATION TEST
=====================================================

This test investigates the critical issue reported in the review request:
- Backend testing claimed Lilian was converted to client "client_a04533ff" ✅
- BUT user screenshots show she's NOT in Client Directory ❌
- Only 3 clients visible: Salvador Palma, Maria Rodriguez, Gerardo Briones
- Lilian Limon Leite is missing from client list

Investigation Plan:
1. Check actual client list API - what clients actually exist?
2. Verify Lilian's prospect status - is she converted or still in prospects?
3. Test client conversion process if needed
4. Check database synchronization between prospects and clients
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

class LilianInvestigationTest:
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
    
    def test_actual_client_list(self):
        """Check what clients actually exist in the system"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                
                if isinstance(clients, list):
                    client_names = [client.get('name', 'Unknown') for client in clients]
                    client_ids = [client.get('id', 'Unknown') for client in clients]
                    
                    # Check if Lilian is in the client list
                    lilian_found = False
                    lilian_client = None
                    
                    for client in clients:
                        name = client.get('name', '').lower()
                        if 'lilian' in name or 'limon' in name or 'leite' in name:
                            lilian_found = True
                            lilian_client = client
                            self.lilian_client_id = client.get('id')
                            break
                    
                    if lilian_found:
                        self.log_result("Lilian in Client List", True, 
                                      f"Lilian found in client list: {lilian_client.get('name')} (ID: {lilian_client.get('id')})",
                                      {"lilian_client": lilian_client})
                    else:
                        self.log_result("Lilian in Client List", False, 
                                      f"Lilian NOT found in client list. Found {len(clients)} clients: {client_names}",
                                      {"all_clients": clients})
                    
                    # Check for the specific client_a04533ff mentioned in review
                    client_a04533ff_found = any(client.get('id') == 'client_a04533ff' for client in clients)
                    if client_a04533ff_found:
                        self.log_result("Client A04533FF Exists", True, "client_a04533ff found in database")
                    else:
                        self.log_result("Client A04533FF Exists", False, "client_a04533ff NOT found in database")
                    
                else:
                    self.log_result("Client List Format", False, "Unexpected client list format", {"response": clients})
                    
            else:
                self.log_result("Get Client List", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Get Client List", False, f"Exception: {str(e)}")
    
    def test_lilian_prospect_status(self):
        """Check Lilian's status in the prospects system"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects = response.json()
                
                if isinstance(prospects, list):
                    # Look for Lilian in prospects
                    lilian_prospect = None
                    
                    for prospect in prospects:
                        name = prospect.get('name', '').lower()
                        if 'lilian' in name or 'limon' in name or 'leite' in name:
                            lilian_prospect = prospect
                            self.lilian_prospect_id = prospect.get('id')
                            break
                    
                    if lilian_prospect:
                        converted = lilian_prospect.get('converted_to_client', False)
                        client_id = lilian_prospect.get('client_id', '')
                        stage = lilian_prospect.get('stage', 'unknown')
                        
                        self.log_result("Lilian Prospect Found", True, 
                                      f"Lilian found in prospects: {lilian_prospect.get('name')}",
                                      {
                                          "prospect_id": lilian_prospect.get('id'),
                                          "converted_to_client": converted,
                                          "client_id": client_id,
                                          "stage": stage,
                                          "full_prospect": lilian_prospect
                                      })
                        
                        # Check conversion status
                        if converted and client_id:
                            self.log_result("Lilian Conversion Status", True, 
                                          f"Lilian marked as converted to client_id: {client_id}")
                        elif converted and not client_id:
                            self.log_result("Lilian Conversion Status", False, 
                                          "Lilian marked as converted but no client_id set")
                        else:
                            self.log_result("Lilian Conversion Status", False, 
                                          "Lilian NOT marked as converted to client")
                    else:
                        self.log_result("Lilian Prospect Found", False, 
                                      f"Lilian NOT found in prospects. Found {len(prospects)} prospects")
                        
                else:
                    self.log_result("Prospects List Format", False, "Unexpected prospects format", {"response": prospects})
                    
            else:
                self.log_result("Get Prospects List", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Get Prospects List", False, f"Exception: {str(e)}")
    
    def test_database_synchronization(self):
        """Check if there's a synchronization issue between prospects and clients"""
        try:
            if self.lilian_prospect_id and self.lilian_client_id:
                # Both exist - check if they're properly linked
                self.log_result("Database Sync Check", True, 
                              f"Both prospect ({self.lilian_prospect_id}) and client ({self.lilian_client_id}) exist")
            elif self.lilian_prospect_id and not self.lilian_client_id:
                # Prospect exists but no client - conversion issue
                self.log_result("Database Sync Check", False, 
                              "Lilian exists as prospect but not as client - conversion failed or incomplete")
            elif not self.lilian_prospect_id and self.lilian_client_id:
                # Client exists but no prospect - unusual but possible
                self.log_result("Database Sync Check", True, 
                              "Lilian exists as client but not in prospects - conversion completed and prospect removed")
            else:
                # Neither exists
                self.log_result("Database Sync Check", False, 
                              "Lilian not found in either prospects or clients")
                
        except Exception as e:
            self.log_result("Database Sync Check", False, f"Exception: {str(e)}")
    
    def test_client_conversion_process(self):
        """Test the client conversion process if Lilian is still a prospect"""
        try:
            if not self.lilian_prospect_id:
                self.log_result("Client Conversion Test", False, "Cannot test conversion - Lilian prospect not found")
                return
            
            if self.lilian_client_id:
                self.log_result("Client Conversion Test", True, "Conversion not needed - Lilian already exists as client")
                return
            
            # Attempt to convert Lilian from prospect to client
            conversion_data = {
                "prospect_id": self.lilian_prospect_id,
                "send_agreement": False  # Don't send email during test
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/convert", json=conversion_data)
            
            if response.status_code == 200:
                result = response.json()
                new_client_id = result.get('client_id')
                
                if new_client_id:
                    self.log_result("Client Conversion Process", True, 
                                  f"Successfully converted Lilian to client: {new_client_id}",
                                  {"conversion_result": result})
                    
                    # Verify the new client exists
                    time.sleep(2)  # Wait for database update
                    self.verify_new_client(new_client_id)
                else:
                    self.log_result("Client Conversion Process", False, 
                                  "Conversion returned success but no client_id", {"result": result})
            else:
                self.log_result("Client Conversion Process", False, 
                              f"Conversion failed: HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Client Conversion Process", False, f"Exception: {str(e)}")
    
    def verify_new_client(self, client_id):
        """Verify that a newly converted client appears in the client list"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                
                if isinstance(clients, list):
                    new_client_found = any(client.get('id') == client_id for client in clients)
                    
                    if new_client_found:
                        self.log_result("New Client Verification", True, 
                                      f"Newly converted client {client_id} found in client list")
                    else:
                        self.log_result("New Client Verification", False, 
                                      f"Newly converted client {client_id} NOT found in client list")
                else:
                    self.log_result("New Client Verification", False, "Could not verify - unexpected client list format")
            else:
                self.log_result("New Client Verification", False, f"Could not verify - HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("New Client Verification", False, f"Exception: {str(e)}")
    
    def test_client_directory_api(self):
        """Test the specific API that the frontend Client Directory uses"""
        try:
            # Test different possible endpoints that might be used for client directory
            endpoints_to_test = [
                "/admin/clients",
                "/clients",
                "/admin/client-directory",
                "/client-directory"
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        client_count = len(data) if isinstance(data, list) else data.get('total_clients', 0)
                        
                        self.log_result(f"Client Directory API - {endpoint}", True, 
                                      f"Endpoint working, found {client_count} clients")
                        
                        # Check if Lilian is in this endpoint's response
                        if isinstance(data, list):
                            lilian_in_response = any('lilian' in client.get('name', '').lower() or 
                                                   'limon' in client.get('name', '').lower() or
                                                   'leite' in client.get('name', '').lower()
                                                   for client in data)
                            
                            if lilian_in_response:
                                self.log_result(f"Lilian in {endpoint}", True, "Lilian found in this endpoint")
                            else:
                                self.log_result(f"Lilian in {endpoint}", False, "Lilian NOT found in this endpoint")
                    else:
                        self.log_result(f"Client Directory API - {endpoint}", False, 
                                      f"HTTP {response.status_code}")
                except:
                    # Skip endpoints that don't exist
                    pass
                    
        except Exception as e:
            self.log_result("Client Directory API Test", False, f"Exception: {str(e)}")
    
    def run_investigation(self):
        """Run the complete Lilian investigation"""
        print("🚨 LILIAN LIMON LEITE CLIENT CONVERSION INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        print()
        print("ISSUE: Backend claimed Lilian converted to client_a04533ff but she's not visible in Client Directory")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with investigation.")
            return False
        
        print("\n🔍 Running Lilian Investigation Tests...")
        print("-" * 50)
        
        # Run investigation tests in logical order
        self.test_actual_client_list()
        self.test_lilian_prospect_status()
        self.test_database_synchronization()
        self.test_client_directory_api()
        self.test_client_conversion_process()
        
        # Generate investigation summary
        self.generate_investigation_summary()
        
        return True
    
    def generate_investigation_summary(self):
        """Generate comprehensive investigation summary"""
        print("\n" + "=" * 60)
        print("🚨 LILIAN INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check if Lilian exists as client
        lilian_client_exists = any(result['success'] and 'Lilian in Client List' in result['test'] 
                                 for result in self.test_results)
        
        # Check if Lilian exists as prospect
        lilian_prospect_exists = any(result['success'] and 'Lilian Prospect Found' in result['test'] 
                                   for result in self.test_results)
        
        # Check if client_a04533ff exists
        client_a04533ff_exists = any(result['success'] and 'Client A04533FF Exists' in result['test'] 
                                   for result in self.test_results)
        
        if lilian_client_exists:
            print("✅ Lilian EXISTS in client list - Review request may be outdated")
        else:
            print("❌ Lilian NOT FOUND in client list - Issue confirmed")
        
        if client_a04533ff_exists:
            print("✅ client_a04533ff EXISTS in database")
        else:
            print("❌ client_a04533ff NOT FOUND in database - Backend test claim was false")
        
        if lilian_prospect_exists:
            print("✅ Lilian found in prospects system")
        else:
            print("❌ Lilian NOT found in prospects system")
        
        print()
        
        # Root cause analysis
        print("🎯 ROOT CAUSE ANALYSIS:")
        
        if not lilian_client_exists and not client_a04533ff_exists:
            print("❌ CRITICAL: Backend testing claim was FALSE")
            print("   - client_a04533ff does not exist in database")
            print("   - Lilian was never actually converted to client")
            print("   - Previous testing reports were inaccurate")
        elif not lilian_client_exists and client_a04533ff_exists:
            print("⚠️  PARTIAL: client_a04533ff exists but not linked to Lilian")
            print("   - Database inconsistency between prospects and clients")
            print("   - Conversion process may have failed partially")
        elif lilian_client_exists:
            print("✅ SUCCESS: Lilian properly converted and visible")
            print("   - Issue may have been resolved since review request")
            print("   - Frontend may need cache refresh")
        
        print()
        
        # Action items
        print("🚀 REQUIRED ACTIONS:")
        
        if not lilian_client_exists:
            print("1. 🔧 URGENT: Complete Lilian's client conversion")
            print("   - Run prospect-to-client conversion process")
            print("   - Ensure proper database linking")
            print("   - Verify client appears in Client Directory")
            
        if not client_a04533ff_exists and lilian_prospect_exists:
            print("2. 🔧 URGENT: Fix conversion process")
            print("   - Previous conversion attempts failed")
            print("   - Debug client creation endpoint")
            print("   - Ensure database writes are successful")
        
        print("3. 📊 VERIFY: Test Client Directory frontend")
        print("   - Ensure frontend is calling correct API endpoint")
        print("   - Check for caching issues")
        print("   - Verify client list rendering")
        
        print("\n" + "=" * 60)

def main():
    """Main investigation execution"""
    investigator = LilianInvestigationTest()
    success = investigator.run_investigation()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()