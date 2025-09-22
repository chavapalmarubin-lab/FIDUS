#!/usr/bin/env python3
"""
COMPREHENSIVE LEAD-TO-CLIENT CONVERSION TESTING
===============================================

This test provides a complete analysis of the lead-to-client conversion process:
1. Find all prospects and analyze their current status
2. Identify prospects eligible for conversion (won + clear AML/KYC + not converted)
3. Test conversion endpoint functionality
4. Check for data inconsistencies between prospects and clients
5. Verify complete conversion workflow integrity
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://finance-portal-60.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ComprehensiveConversionTest:
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
            
            self.log_result("Admin Authentication", False, f"HTTP {response.status_code}")
            return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def analyze_current_system_state(self):
        """Analyze current prospects and clients in the system"""
        try:
            # Get all prospects
            prospects_response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if prospects_response.status_code != 200:
                self.log_result("System State Analysis", False, "Failed to get prospects")
                return None, None
            
            prospects_data = prospects_response.json()
            prospects = prospects_data.get('prospects', [])
            
            # Get all clients
            clients_response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if clients_response.status_code != 200:
                self.log_result("System State Analysis", False, "Failed to get clients")
                return None, None
            
            clients_data = clients_response.json()
            clients = clients_data.get('clients', [])
            
            # Analyze prospects
            prospect_analysis = {
                "total_prospects": len(prospects),
                "by_stage": {},
                "by_aml_status": {},
                "converted_count": 0,
                "eligible_for_conversion": []
            }
            
            for prospect in prospects:
                stage = prospect.get('stage', 'unknown')
                aml_status = prospect.get('aml_kyc_status', 'unknown')
                converted = prospect.get('converted_to_client', False)
                
                prospect_analysis["by_stage"][stage] = prospect_analysis["by_stage"].get(stage, 0) + 1
                prospect_analysis["by_aml_status"][aml_status] = prospect_analysis["by_aml_status"].get(aml_status, 0) + 1
                
                if converted:
                    prospect_analysis["converted_count"] += 1
                
                # Check if eligible for conversion
                if (stage == 'won' and 
                    aml_status in ['clear', 'approved'] and 
                    not converted):
                    prospect_analysis["eligible_for_conversion"].append({
                        "id": prospect.get('id'),
                        "name": prospect.get('name'),
                        "email": prospect.get('email'),
                        "stage": stage,
                        "aml_status": aml_status
                    })
            
            # Analyze clients
            client_analysis = {
                "total_clients": len(clients),
                "converted_from_prospects": 0,
                "client_ids": [c.get('id') for c in clients]
            }
            
            for client in clients:
                if client.get('created_from_prospect'):
                    client_analysis["converted_from_prospects"] += 1
            
            self.log_result("System State Analysis", True, 
                          f"Found {len(prospects)} prospects, {len(clients)} clients")
            
            print(f"   Prospect Stages: {prospect_analysis['by_stage']}")
            print(f"   AML/KYC Status: {prospect_analysis['by_aml_status']}")
            print(f"   Eligible for Conversion: {len(prospect_analysis['eligible_for_conversion'])}")
            print(f"   Already Converted: {prospect_analysis['converted_count']}")
            
            return prospect_analysis, client_analysis
            
        except Exception as e:
            self.log_result("System State Analysis", False, f"Exception: {str(e)}")
            return None, None
    
    def test_conversion_button_logic(self, prospect_analysis):
        """Test the logic for showing Convert buttons"""
        if not prospect_analysis:
            self.log_result("Convert Button Logic", False, "No prospect analysis available")
            return
        
        eligible_prospects = prospect_analysis["eligible_for_conversion"]
        
        if len(eligible_prospects) > 0:
            self.log_result("Convert Button Logic", True, 
                          f"{len(eligible_prospects)} prospects should show Convert button")
            
            for prospect in eligible_prospects:
                print(f"   ✅ {prospect['name']}: stage={prospect['stage']}, aml_status={prospect['aml_status']}")
        else:
            self.log_result("Convert Button Logic", True, 
                          "No prospects currently eligible for conversion (all already converted or not ready)")
    
    def test_conversion_endpoint_functionality(self, prospect_analysis):
        """Test the actual conversion endpoint"""
        if not prospect_analysis:
            return
        
        eligible_prospects = prospect_analysis["eligible_for_conversion"]
        
        if len(eligible_prospects) == 0:
            self.log_result("Conversion Endpoint Test", True, 
                          "No eligible prospects to test (all already converted)")
            return
        
        # Test conversion with first eligible prospect
        test_prospect = eligible_prospects[0]
        prospect_id = test_prospect["id"]
        prospect_name = test_prospect["name"]
        
        try:
            conversion_request = {
                "prospect_id": prospect_id,
                "send_agreement": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/convert", 
                                       json=conversion_request)
            
            if response.status_code == 200:
                result = response.json()
                client_id = result.get('client_id')
                
                if client_id:
                    self.log_result("Conversion Endpoint Test", True, 
                                  f"Successfully converted {prospect_name} to {client_id}")
                    
                    # Verify the conversion was properly recorded
                    self.verify_conversion_integrity(prospect_id, client_id, prospect_name)
                else:
                    self.log_result("Conversion Endpoint Test", False, 
                                  "Conversion succeeded but no client_id returned")
            else:
                self.log_result("Conversion Endpoint Test", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Conversion Endpoint Test", False, f"Exception: {str(e)}")
    
    def verify_conversion_integrity(self, prospect_id, client_id, prospect_name):
        """Verify that conversion was properly recorded in both prospect and client records"""
        try:
            # Check prospect was updated
            prospects_response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if prospects_response.status_code == 200:
                prospects_data = prospects_response.json()
                prospects = prospects_data.get('prospects', [])
                
                prospect_found = False
                for prospect in prospects:
                    if prospect.get('id') == prospect_id:
                        prospect_found = True
                        converted = prospect.get('converted_to_client', False)
                        stored_client_id = prospect.get('client_id', '')
                        
                        if converted and stored_client_id == client_id:
                            self.log_result("Prospect Update Verification", True, 
                                          f"Prospect {prospect_name} properly marked as converted")
                        else:
                            self.log_result("Prospect Update Verification", False, 
                                          f"Prospect conversion status incorrect", 
                                          {"converted": converted, "client_id": stored_client_id})
                        break
                
                if not prospect_found:
                    self.log_result("Prospect Update Verification", False, 
                                  f"Prospect {prospect_id} not found after conversion")
            
            # Check client was created
            clients_response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if clients_response.status_code == 200:
                clients_data = clients_response.json()
                clients = clients_data.get('clients', [])
                
                client_found = False
                for client in clients:
                    if client.get('id') == client_id:
                        client_found = True
                        client_name = client.get('name', '')
                        
                        if prospect_name.upper() in client_name.upper():
                            self.log_result("Client Creation Verification", True, 
                                          f"Client {client_id} created with correct name")
                        else:
                            self.log_result("Client Creation Verification", False, 
                                          f"Client name mismatch", 
                                          {"expected": prospect_name, "actual": client_name})
                        break
                
                if not client_found:
                    self.log_result("Client Creation Verification", False, 
                                  f"Client {client_id} not found in clients list")
                    
        except Exception as e:
            self.log_result("Conversion Integrity Verification", False, f"Exception: {str(e)}")
    
    def check_data_inconsistencies(self):
        """Check for data inconsistencies between prospects and clients"""
        try:
            # Get current prospects and clients
            prospects_response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            clients_response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if prospects_response.status_code != 200 or clients_response.status_code != 200:
                self.log_result("Data Consistency Check", False, "Failed to get data for consistency check")
                return
            
            prospects = prospects_response.json().get('prospects', [])
            clients = clients_response.json().get('clients', [])
            client_ids = [c.get('id') for c in clients]
            
            inconsistencies = []
            
            for prospect in prospects:
                converted = prospect.get('converted_to_client', False)
                client_id = prospect.get('client_id', '')
                prospect_name = prospect.get('name', 'Unknown')
                
                if converted and client_id:
                    # Check if client_id exists
                    if client_id not in client_ids:
                        inconsistencies.append({
                            "prospect_name": prospect_name,
                            "prospect_id": prospect.get('id'),
                            "client_id": client_id,
                            "issue": "Client record does not exist"
                        })
                elif converted and not client_id:
                    inconsistencies.append({
                        "prospect_name": prospect_name,
                        "prospect_id": prospect.get('id'),
                        "client_id": "None",
                        "issue": "Marked as converted but no client_id"
                    })
            
            if len(inconsistencies) == 0:
                self.log_result("Data Consistency Check", True, 
                              "No data inconsistencies found - all converted prospects have valid client records")
            else:
                self.log_result("Data Consistency Check", False, 
                              f"Found {len(inconsistencies)} data inconsistencies")
                
                for inconsistency in inconsistencies:
                    print(f"   ❌ {inconsistency['prospect_name']}: {inconsistency['issue']}")
                    
        except Exception as e:
            self.log_result("Data Consistency Check", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive lead-to-client conversion test"""
        print("🎯 COMPREHENSIVE LEAD-TO-CLIENT CONVERSION TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Comprehensive Conversion Tests...")
        print("-" * 50)
        
        # Analyze current system state
        prospect_analysis, client_analysis = self.analyze_current_system_state()
        
        # Test conversion button logic
        self.test_conversion_button_logic(prospect_analysis)
        
        # Test conversion endpoint functionality
        self.test_conversion_endpoint_functionality(prospect_analysis)
        
        # Check for data inconsistencies
        self.check_data_inconsistencies()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE CONVERSION TEST SUMMARY")
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
        
        # Overall assessment
        print("🚨 OVERALL ASSESSMENT:")
        if success_rate >= 80:
            print("✅ LEAD-TO-CLIENT CONVERSION SYSTEM: FULLY OPERATIONAL")
            print("   All critical conversion functionality working correctly.")
            print("   System ready for production use.")
        elif success_rate >= 60:
            print("⚠️  LEAD-TO-CLIENT CONVERSION SYSTEM: MOSTLY WORKING")
            print("   Core functionality operational with minor issues.")
            print("   Review failed tests for improvements.")
        else:
            print("❌ LEAD-TO-CLIENT CONVERSION SYSTEM: NEEDS ATTENTION")
            print("   Critical issues found in conversion workflow.")
            print("   Main agent action required.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = ComprehensiveConversionTest()
    success = test_runner.run_comprehensive_test()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()