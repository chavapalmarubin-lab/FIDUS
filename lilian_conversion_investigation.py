#!/usr/bin/env python3
"""
LILIAN LIMON CLIENT CONVERSION INVESTIGATION
==========================================

Critical bug investigation: User clicked "Convert to Client" button for Lilian Limon 
but she does NOT appear in the Client Management directory.

Investigation Plan:
1. Check Lilian's current status in prospects database
2. Verify if client record was created properly  
3. Test /api/admin/clients endpoint
4. Check for data inconsistency between prospect and client records
5. Test complete conversion flow if needed

Expected Findings:
- Identify exact issue with Lilian's conversion
- Determine if prospect marked as converted but no client record
- Or if client record exists but not showing in management interface
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://auth-flow-debug-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class LilianConversionInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.lilian_prospect_data = None
        self.lilian_client_data = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log investigation result"""
        status = "✅ FOUND" if success else "❌ ISSUE"
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
    
    def investigate_lilian_prospect_status(self):
        """Check Lilian's current status in prospects database"""
        try:
            # Get all prospects and search for Lilian
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects = response.json()
                lilian_prospects = []
                
                # Search for Lilian in prospects
                if isinstance(prospects, list):
                    for prospect in prospects:
                        name = prospect.get('name', '').lower()
                        if 'lilian' in name and 'limon' in name:
                            lilian_prospects.append(prospect)
                
                if lilian_prospects:
                    if len(lilian_prospects) == 1:
                        self.lilian_prospect_data = lilian_prospects[0]
                        prospect = self.lilian_prospect_data
                        
                        # Analyze prospect status
                        stage = prospect.get('stage')
                        converted_to_client = prospect.get('converted_to_client', False)
                        client_id = prospect.get('client_id')
                        aml_kyc_status = prospect.get('aml_kyc_status')
                        
                        status_info = {
                            'id': prospect.get('id'),
                            'name': prospect.get('name'),
                            'email': prospect.get('email'),
                            'stage': stage,
                            'converted_to_client': converted_to_client,
                            'client_id': client_id,
                            'aml_kyc_status': aml_kyc_status
                        }
                        
                        self.log_result("Lilian Prospect Found", True, 
                                      f"Found Lilian Limon Leite in prospects database",
                                      {"prospect_status": status_info})
                        
                        # Check for conversion issues
                        if converted_to_client and client_id:
                            self.log_result("Lilian Conversion Status", False, 
                                          f"Prospect marked as converted (client_id: {client_id}) - investigating client record",
                                          {"conversion_data": status_info})
                        elif stage == 'won' and not converted_to_client:
                            self.log_result("Lilian Conversion Status", False, 
                                          "Prospect in 'won' stage but not converted to client",
                                          {"conversion_data": status_info})
                        else:
                            self.log_result("Lilian Conversion Status", True, 
                                          f"Prospect status normal: stage={stage}, converted={converted_to_client}")
                    
                    else:
                        self.log_result("Lilian Prospect Found", False, 
                                      f"Found {len(lilian_prospects)} Lilian prospects (expected 1)",
                                      {"multiple_prospects": lilian_prospects})
                else:
                    self.log_result("Lilian Prospect Found", False, 
                                  "Lilian Limon not found in prospects database",
                                  {"total_prospects": len(prospects) if isinstance(prospects, list) else "unknown"})
            else:
                self.log_result("Lilian Prospect Search", False, 
                              f"Failed to get prospects: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Lilian Prospect Investigation", False, f"Exception: {str(e)}")
    
    def investigate_lilian_client_record(self):
        """Verify if Lilian's client record exists"""
        try:
            # Get all clients and search for Lilian
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                lilian_clients = []
                
                # Search for Lilian in clients
                if isinstance(clients, list):
                    for client in clients:
                        name = client.get('name', '').lower()
                        if 'lilian' in name and 'limon' in name:
                            lilian_clients.append(client)
                
                if lilian_clients:
                    if len(lilian_clients) == 1:
                        self.lilian_client_data = lilian_clients[0]
                        client = self.lilian_client_data
                        
                        client_info = {
                            'id': client.get('id'),
                            'name': client.get('name'),
                            'email': client.get('email'),
                            'username': client.get('username'),
                            'total_balance': client.get('total_balance', 0)
                        }
                        
                        self.log_result("Lilian Client Record", True, 
                                      f"Found Lilian client record in Client Management",
                                      {"client_data": client_info})
                        
                        # Check if this matches prospect's client_id
                        if self.lilian_prospect_data:
                            prospect_client_id = self.lilian_prospect_data.get('client_id')
                            actual_client_id = client.get('id')
                            
                            if prospect_client_id == actual_client_id:
                                self.log_result("Client-Prospect ID Match", True, 
                                              f"Client ID matches prospect record: {actual_client_id}")
                            else:
                                self.log_result("Client-Prospect ID Match", False, 
                                              f"ID mismatch - Prospect: {prospect_client_id}, Client: {actual_client_id}")
                    
                    else:
                        self.log_result("Lilian Client Record", False, 
                                      f"Found {len(lilian_clients)} Lilian clients (expected 1)",
                                      {"multiple_clients": lilian_clients})
                else:
                    self.log_result("Lilian Client Record", False, 
                                  "Lilian Limon NOT found in Client Management directory",
                                  {"total_clients": len(clients) if isinstance(clients, list) else "unknown",
                                   "client_names": [c.get('name') for c in clients] if isinstance(clients, list) else []})
            else:
                self.log_result("Lilian Client Search", False, 
                              f"Failed to get clients: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Lilian Client Investigation", False, f"Exception: {str(e)}")
    
    def investigate_client_id_validity(self):
        """Check if prospect's client_id actually exists in database"""
        if not self.lilian_prospect_data:
            self.log_result("Client ID Validity Check", False, "No prospect data available")
            return
        
        prospect_client_id = self.lilian_prospect_data.get('client_id')
        if not prospect_client_id:
            self.log_result("Client ID Validity Check", True, "No client_id in prospect record")
            return
        
        try:
            # Try to get specific client by ID
            response = self.session.get(f"{BACKEND_URL}/admin/clients/{prospect_client_id}")
            if response.status_code == 200:
                client_data = response.json()
                self.log_result("Client ID Validity Check", True, 
                              f"Client ID {prospect_client_id} exists in database",
                              {"client_data": client_data})
            elif response.status_code == 404:
                self.log_result("Client ID Validity Check", False, 
                              f"Client ID {prospect_client_id} does NOT exist in database - DATA INCONSISTENCY FOUND!",
                              {"prospect_client_id": prospect_client_id, "http_status": 404})
            else:
                self.log_result("Client ID Validity Check", False, 
                              f"Error checking client ID {prospect_client_id}: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Client ID Validity Check", False, f"Exception: {str(e)}")
    
    def test_client_management_endpoint(self):
        """Test /api/admin/clients endpoint specifically"""
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                
                if isinstance(clients, list):
                    client_count = len(clients)
                    client_names = [client.get('name', 'Unknown') for client in clients]
                    
                    self.log_result("Client Management Endpoint", True, 
                                  f"Endpoint working - {client_count} clients found",
                                  {"client_names": client_names})
                    
                    # Check if Lilian is in the list
                    lilian_in_list = any('lilian' in name.lower() and 'limon' in name.lower() 
                                       for name in client_names)
                    
                    if lilian_in_list:
                        self.log_result("Lilian in Client List", True, "Lilian found in client management list")
                    else:
                        self.log_result("Lilian in Client List", False, 
                                      "Lilian NOT found in client management list - THIS IS THE REPORTED BUG!",
                                      {"available_clients": client_names})
                else:
                    self.log_result("Client Management Endpoint", False, 
                                  "Unexpected response format", {"response": clients})
            else:
                self.log_result("Client Management Endpoint", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Client Management Endpoint", False, f"Exception: {str(e)}")
    
    def test_conversion_flow_if_needed(self):
        """Test complete conversion flow if Lilian needs to be converted"""
        if not self.lilian_prospect_data:
            self.log_result("Conversion Flow Test", False, "No prospect data available for conversion test")
            return
        
        prospect = self.lilian_prospect_data
        converted_to_client = prospect.get('converted_to_client', False)
        stage = prospect.get('stage')
        aml_kyc_status = prospect.get('aml_kyc_status')
        
        # Check if conversion is needed
        if converted_to_client and self.lilian_client_data:
            self.log_result("Conversion Flow Test", True, "Conversion already completed successfully")
            return
        
        if stage != 'won':
            self.log_result("Conversion Flow Test", False, 
                          f"Cannot convert - prospect not in 'won' stage (current: {stage})")
            return
        
        if aml_kyc_status != 'clear':
            self.log_result("Conversion Flow Test", False, 
                          f"Cannot convert - AML/KYC not clear (current: {aml_kyc_status})")
            return
        
        # If we reach here, prospect should be convertible
        prospect_id = prospect.get('id')
        
        try:
            # Test conversion endpoint
            conversion_data = {
                "prospect_id": prospect_id,
                "send_agreement": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/convert", json=conversion_data)
            if response.status_code == 200:
                conversion_result = response.json()
                new_client_id = conversion_result.get('client_id')
                
                self.log_result("Conversion Flow Test", True, 
                              f"Conversion successful - new client_id: {new_client_id}",
                              {"conversion_result": conversion_result})
                
                # Verify client appears in directory after conversion
                time.sleep(2)  # Wait for database update
                self.investigate_lilian_client_record()
                
            else:
                self.log_result("Conversion Flow Test", False, 
                              f"Conversion failed: HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Conversion Flow Test", False, f"Exception: {str(e)}")
    
    def run_investigation(self):
        """Run complete Lilian conversion investigation"""
        print("🚨 LILIAN LIMON CLIENT CONVERSION INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        print()
        print("REPORTED BUG: User clicked 'Convert to Client' for Lilian Limon")
        print("              but she does NOT appear in Client Management directory")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with investigation.")
            return False
        
        print("\n🔍 Running Investigation Steps...")
        print("-" * 50)
        
        # Run investigation steps
        self.investigate_lilian_prospect_status()
        self.investigate_lilian_client_record()
        self.investigate_client_id_validity()
        self.test_client_management_endpoint()
        self.test_conversion_flow_if_needed()
        
        # Generate investigation summary
        self.generate_investigation_summary()
        
        return True
    
    def generate_investigation_summary(self):
        """Generate comprehensive investigation summary"""
        print("\n" + "=" * 60)
        print("🚨 LILIAN CONVERSION INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_checks = len(self.test_results)
        issues_found = sum(1 for result in self.test_results if not result['success'])
        
        print(f"Total Checks: {total_checks}")
        print(f"Issues Found: {issues_found}")
        print()
        
        # Show all findings
        print("🔍 INVESTIGATION FINDINGS:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"   {status_icon} {result['test']}: {result['message']}")
        print()
        
        # Root cause analysis
        print("🎯 ROOT CAUSE ANALYSIS:")
        
        if self.lilian_prospect_data and self.lilian_client_data:
            print("✅ ISSUE RESOLVED: Lilian found in both prospects and clients")
            print("   The conversion appears to be working correctly.")
        
        elif self.lilian_prospect_data and not self.lilian_client_data:
            prospect = self.lilian_prospect_data
            converted = prospect.get('converted_to_client', False)
            client_id = prospect.get('client_id')
            
            if converted and client_id:
                print("❌ DATA INCONSISTENCY CONFIRMED:")
                print(f"   Prospect marked as converted (client_id: {client_id})")
                print("   BUT client record does NOT exist in database")
                print("   This is the exact bug reported by user!")
            else:
                print("❌ CONVERSION NOT COMPLETED:")
                print("   Prospect exists but conversion process was not completed")
                print("   User may have clicked convert but process failed")
        
        elif not self.lilian_prospect_data:
            print("❌ PROSPECT NOT FOUND:")
            print("   Lilian Limon not found in prospects database")
            print("   This suggests data may have been deleted or corrupted")
        
        else:
            print("❓ UNCLEAR SITUATION:")
            print("   Investigation results are inconclusive")
        
        print()
        
        # Recommended actions
        print("🔧 RECOMMENDED ACTIONS:")
        
        if self.lilian_prospect_data:
            prospect = self.lilian_prospect_data
            converted = prospect.get('converted_to_client', False)
            client_id = prospect.get('client_id')
            
            if converted and client_id and not self.lilian_client_data:
                print("1. URGENT: Fix data inconsistency")
                print(f"   - Reset prospect converted_to_client=false and client_id=''")
                print(f"   - Allow user to retry conversion process")
                print("2. Test conversion process thoroughly")
                print("3. Verify client creation logic in backend")
            
            elif not converted:
                print("1. Complete the conversion process")
                print("2. Ensure AML/KYC status is 'clear'")
                print("3. Move prospect to 'won' stage if needed")
                print("4. Test convert button functionality")
        
        else:
            print("1. Restore Lilian's prospect record")
            print("2. Set appropriate stage and AML/KYC status")
            print("3. Test complete prospect-to-client flow")
        
        print("\n" + "=" * 60)

def main():
    """Main investigation execution"""
    investigator = LilianConversionInvestigation()
    success = investigator.run_investigation()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()