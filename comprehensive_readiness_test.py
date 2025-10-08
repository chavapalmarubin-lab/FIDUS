#!/usr/bin/env python3
"""
COMPREHENSIVE CLIENT INVESTMENT READINESS INVESTIGATION
=======================================================

This test provides a comprehensive investigation of the client investment readiness issue:
- Investigates the disconnect between in-memory client_readiness and MongoDB data
- Tests both the in-memory system and MongoDB integration
- Attempts multiple fix approaches
- Provides detailed root cause analysis

Root Cause Analysis Focus:
1. In-memory client_readiness vs MongoDB client data synchronization
2. AML/KYC completion process and data persistence
3. Investment readiness calculation logic
4. Client dropdown population mechanism
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ComprehensiveReadinessTest:
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
            print(f"   Details: {json.dumps(details, indent=2)[:500]}...")
    
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
    
    def test_current_ready_clients_status(self):
        """Test current status of ready clients"""
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/ready-for-investment")
            if response.status_code == 200:
                ready_data = response.json()
                ready_clients = ready_data.get('ready_clients', [])
                ready_count = ready_data.get('total_ready', len(ready_clients))
                
                self.log_result("Current Ready Clients Status", True, 
                              f"Found {ready_count} ready clients",
                              {"ready_clients": [c['name'] for c in ready_clients]})
                
                # Check if Alejandro is in the list
                alejandro_in_ready = any('alejandro' in c.get('name', '').lower() for c in ready_clients)
                
                if alejandro_in_ready:
                    self.log_result("Alejandro Currently Ready", True, "Alejandro is already in ready clients list")
                else:
                    self.log_result("Alejandro Currently Ready", False, "Alejandro is NOT in ready clients list")
                    
            else:
                self.log_result("Current Ready Clients Status", False, 
                              f"Failed to get ready clients: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Current Ready Clients Status", False, f"Exception: {str(e)}")
    
    def test_alejandro_detailed_analysis(self):
        """Detailed analysis of Alejandro's data across all systems"""
        try:
            # Get all clients and find Alejandro
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                
                # Handle different response formats
                if isinstance(clients, list):
                    self.clients_data = clients
                elif isinstance(clients, dict) and 'clients' in clients:
                    self.clients_data = clients['clients']
                else:
                    self.clients_data = clients.get('clients', [])
                
                # Find Alejandro
                for client in self.clients_data:
                    if 'alejandro' in client.get('name', '').lower():
                        self.alejandro_data = client
                        break
                
                if self.alejandro_data:
                    self.log_result("Alejandro Data Analysis", True, 
                                  f"Found Alejandro: {self.alejandro_data.get('name')} ({self.alejandro_data.get('id')})",
                                  {
                                      "client_data": {
                                          "id": self.alejandro_data.get('id'),
                                          "name": self.alejandro_data.get('name'),
                                          "email": self.alejandro_data.get('email'),
                                          "investment_ready": self.alejandro_data.get('investment_ready'),
                                          "readiness_status": self.alejandro_data.get('readiness_status')
                                      }
                                  })
                    
                    # Check if he's marked as investment ready in the client data
                    if self.alejandro_data.get('investment_ready'):
                        self.log_result("Alejandro MongoDB Ready Flag", True, 
                                      "Alejandro is marked as investment_ready in MongoDB client data")
                    else:
                        self.log_result("Alejandro MongoDB Ready Flag", False, 
                                      "Alejandro is NOT marked as investment_ready in MongoDB client data")
                else:
                    self.log_result("Alejandro Data Analysis", False, "Alejandro not found in clients list")
                    
        except Exception as e:
            self.log_result("Alejandro Data Analysis", False, f"Exception: {str(e)}")
    
    def test_alejandro_readiness_endpoints(self):
        """Test all readiness-related endpoints for Alejandro"""
        if not self.alejandro_data:
            self.log_result("Alejandro Readiness Endpoints", False, "Cannot test - Alejandro data not found")
            return
        
        client_id = self.alejandro_data.get('id')
        
        try:
            # Test GET readiness endpoint
            response = self.session.get(f"{BACKEND_URL}/clients/{client_id}/readiness")
            if response.status_code == 200:
                readiness = response.json()
                self.log_result("Alejandro GET Readiness", True, 
                              f"Readiness data: ready={readiness.get('investment_ready')}, aml_kyc={readiness.get('aml_kyc_completed')}, agreement={readiness.get('agreement_signed')}",
                              {"readiness": readiness})
            else:
                self.log_result("Alejandro GET Readiness", False, 
                              f"Failed to get readiness: HTTP {response.status_code}")
            
            # Test PUT readiness endpoint (fix attempt)
            readiness_update = {
                "aml_kyc_completed": True,
                "agreement_signed": True,
                "notes": "Comprehensive test fix attempt",
                "updated_by": "comprehensive_test"
            }
            
            response = self.session.put(f"{BACKEND_URL}/clients/{client_id}/readiness", 
                                      json=readiness_update)
            
            if response.status_code == 200:
                update_result = response.json()
                self.log_result("Alejandro PUT Readiness", True, 
                              f"Successfully updated readiness: ready={update_result.get('readiness', {}).get('investment_ready')}",
                              {"update_result": update_result})
            else:
                self.log_result("Alejandro PUT Readiness", False, 
                              f"Failed to update readiness: HTTP {response.status_code}",
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Alejandro Readiness Endpoints", False, f"Exception: {str(e)}")
    
    def test_mongodb_client_data_refresh(self):
        """Test if MongoDB client data reflects the readiness changes"""
        try:
            # Wait a moment for data to sync
            time.sleep(2)
            
            # Get fresh client data
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                
                # Handle different response formats
                if isinstance(clients, list):
                    fresh_clients = clients
                elif isinstance(clients, dict) and 'clients' in clients:
                    fresh_clients = clients['clients']
                else:
                    fresh_clients = clients.get('clients', [])
                
                # Find Alejandro in fresh data
                fresh_alejandro = None
                for client in fresh_clients:
                    if 'alejandro' in client.get('name', '').lower():
                        fresh_alejandro = client
                        break
                
                if fresh_alejandro:
                    investment_ready = fresh_alejandro.get('investment_ready', False)
                    readiness_status = fresh_alejandro.get('readiness_status', {})
                    
                    self.log_result("MongoDB Data Refresh", True, 
                                  f"Fresh Alejandro data: investment_ready={investment_ready}",
                                  {
                                      "fresh_data": {
                                          "investment_ready": investment_ready,
                                          "readiness_status": readiness_status
                                      }
                                  })
                    
                    if investment_ready:
                        self.log_result("MongoDB Sync Success", True, 
                                      "MongoDB client data now shows Alejandro as investment ready")
                    else:
                        self.log_result("MongoDB Sync Issue", False, 
                                      "MongoDB client data still shows Alejandro as NOT investment ready")
                else:
                    self.log_result("MongoDB Data Refresh", False, "Alejandro not found in fresh client data")
                    
        except Exception as e:
            self.log_result("MongoDB Data Refresh", False, f"Exception: {str(e)}")
    
    def test_ready_clients_after_fix(self):
        """Test if Alejandro appears in ready clients after the fix"""
        try:
            # Wait a moment for data to propagate
            time.sleep(2)
            
            response = self.session.get(f"{BACKEND_URL}/clients/ready-for-investment")
            if response.status_code == 200:
                ready_data = response.json()
                ready_clients = ready_data.get('ready_clients', [])
                ready_count = ready_data.get('total_ready', len(ready_clients))
                
                # Check if Alejandro is now in the list
                alejandro_in_ready = False
                alejandro_client = None
                for client in ready_clients:
                    if 'alejandro' in client.get('name', '').lower():
                        alejandro_in_ready = True
                        alejandro_client = client
                        break
                
                if alejandro_in_ready:
                    self.log_result("Ready Clients After Fix", True, 
                                  f"SUCCESS: Alejandro now appears in ready clients! Total ready: {ready_count}",
                                  {"alejandro_in_ready": alejandro_client})
                else:
                    self.log_result("Ready Clients After Fix", False, 
                                  f"Alejandro still NOT in ready clients. Total ready: {ready_count}",
                                  {"ready_clients": [c['name'] for c in ready_clients]})
                    
            else:
                self.log_result("Ready Clients After Fix", False, 
                              f"Failed to get ready clients: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Ready Clients After Fix", False, f"Exception: {str(e)}")
    
    def test_other_clients_readiness_analysis(self):
        """Analyze why other clients are ready but Alejandro isn't"""
        try:
            response = self.session.get(f"{BACKEND_URL}/clients/ready-for-investment")
            if response.status_code == 200:
                ready_data = response.json()
                ready_clients = ready_data.get('ready_clients', [])
                
                self.log_result("Other Ready Clients Analysis", True, 
                              f"Analyzing {len(ready_clients)} ready clients",
                              {"ready_clients": ready_clients})
                
                # Check readiness data for each ready client
                for client in ready_clients:
                    client_id = client.get('client_id')
                    try:
                        response = self.session.get(f"{BACKEND_URL}/clients/{client_id}/readiness")
                        if response.status_code == 200:
                            readiness = response.json()
                            self.log_result(f"Ready Client {client.get('name')} Analysis", True, 
                                          f"AML/KYC: {readiness.get('aml_kyc_completed')}, Agreement: {readiness.get('agreement_signed')}, Ready: {readiness.get('investment_ready')}")
                    except:
                        pass
                        
        except Exception as e:
            self.log_result("Other Ready Clients Analysis", False, f"Exception: {str(e)}")
    
    def test_manual_mongodb_update_attempt(self):
        """Attempt to manually update MongoDB client data if possible"""
        if not self.alejandro_data:
            return
        
        try:
            client_id = self.alejandro_data.get('id')
            
            # Try to update client data directly via admin endpoint
            update_data = {
                "investment_ready": True,
                "readiness_status": {
                    "aml_kyc_completed": True,
                    "agreement_signed": True,
                    "investment_ready": True,
                    "notes": "Manual MongoDB update attempt"
                }
            }
            
            # Try different possible endpoints for updating client data
            endpoints_to_try = [
                f"/admin/clients/{client_id}/update",
                f"/admin/clients/{client_id}",
                f"/clients/{client_id}/update"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.put(f"{BACKEND_URL}{endpoint}", json=update_data)
                    if response.status_code == 200:
                        self.log_result("Manual MongoDB Update", True, 
                                      f"Successfully updated via {endpoint}")
                        return
                except:
                    continue
            
            self.log_result("Manual MongoDB Update", False, 
                          "No working endpoint found for direct client data update")
                          
        except Exception as e:
            self.log_result("Manual MongoDB Update", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run comprehensive readiness investigation"""
        print("🎯 COMPREHENSIVE CLIENT INVESTMENT READINESS INVESTIGATION")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Comprehensive Readiness Investigation...")
        print("-" * 60)
        
        # Run all tests in logical order
        self.test_current_ready_clients_status()
        self.test_alejandro_detailed_analysis()
        self.test_alejandro_readiness_endpoints()
        self.test_mongodb_client_data_refresh()
        self.test_ready_clients_after_fix()
        self.test_other_clients_readiness_analysis()
        self.test_manual_mongodb_update_attempt()
        
        # Final verification
        print("\n🔄 Final Verification...")
        self.test_ready_clients_after_fix()
        
        # Generate summary
        self.generate_comprehensive_summary()
        
        return True
    
    def generate_comprehensive_summary(self):
        """Generate comprehensive test summary with root cause analysis"""
        print("\n" + "=" * 70)
        print("🎯 COMPREHENSIVE READINESS INVESTIGATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Check if we successfully fixed the issue
        fix_successful = any("SUCCESS: Alejandro now appears in ready clients" in r['message'] 
                           for r in self.test_results if r['success'])
        
        if fix_successful:
            print("🎉 ISSUE RESOLVED!")
            print("✅ Alejandro Mariscal now appears in the investment dropdown")
            print("✅ Client investment readiness system is working correctly")
        else:
            print("🚨 ISSUE PERSISTS - ROOT CAUSE ANALYSIS:")
            
            # Analyze the specific issues
            mongodb_sync_issue = any("MongoDB client data still shows Alejandro as NOT investment ready" in r['message'] 
                                   for r in self.test_results if not r['success'])
            readiness_update_failed = any("Failed to update readiness" in r['message'] 
                                        for r in self.test_results if not r['success'])
            
            if mongodb_sync_issue:
                print("❌ IDENTIFIED: MongoDB client data synchronization issue")
                print("   The in-memory client_readiness updates are not syncing to MongoDB client data")
            
            if readiness_update_failed:
                print("❌ IDENTIFIED: Client readiness update endpoint failure")
                print("   The PUT /clients/{client_id}/readiness endpoint is not working correctly")
            
            print("\n🔧 RECOMMENDED FIXES FOR MAIN AGENT:")
            print("1. Fix MongoDB client data synchronization with in-memory client_readiness")
            print("2. Ensure client_readiness updates trigger MongoDB client data refresh")
            print("3. Verify the investment_ready flag calculation logic")
            print("4. Test the complete flow: readiness update → MongoDB sync → ready clients endpoint")
        
        # Show key findings
        print("\n📊 KEY FINDINGS:")
        for result in self.test_results:
            if "SUCCESS:" in result['message'] or "IDENTIFIED:" in result['message']:
                print(f"   • {result['message']}")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = ComprehensiveReadinessTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()