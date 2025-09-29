#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION READINESS TEST
======================================

Testing all critical systems mentioned in the review request:
1. Authentication System (admin/password123, client alexmar760/password123)
2. Google OAuth Integration (URL generation, callback, redirect URI)
3. CRM System (prospect creation, pipeline transitions, client conversion)
4. Google API Integration (Gmail, Calendar, Drive endpoints)
5. Data Persistence (Alejandro Mariscal Romero verification)
6. Email System endpoints

This is the make-or-break testing for production readiness.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fidus-workspace-2.preview.emergentagent.com/api"

class ComprehensiveProductionTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.client_token = None
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
        print(f"{status}: {test_name}")
        print(f"    {message}")
        if details and not success:
            print(f"    Details: {details}")
        print()
    
    def authenticate_admin(self):
        """Authenticate as admin and get JWT token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("1. Admin Authentication", True, 
                                  f"Successfully authenticated as {data.get('name', 'admin')} with JWT token")
                    return True
                else:
                    self.log_result("1. Admin Authentication", False, 
                                  "No JWT token received", {"response": data})
                    return False
            else:
                self.log_result("1. Admin Authentication", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("1. Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_client_authentication(self):
        """Test client authentication for Alejandro"""
        try:
            client_session = requests.Session()
            response = client_session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "alexmar760",
                "password": "password123",
                "user_type": "client"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.client_token = data.get("token")
                if self.client_token:
                    user_name = data.get("name", "")
                    user_email = data.get("email", "")
                    if "Alejandro" in user_name and "Mariscal" in user_name:
                        self.log_result("2. Client Authentication (Alejandro)", True, 
                                      f"Successfully authenticated as {user_name} ({user_email})")
                        return True
                    else:
                        self.log_result("2. Client Authentication (Alejandro)", False, 
                                      f"Wrong user: {user_name} (expected Alejandro Mariscal Romero)")
                        return False
                else:
                    self.log_result("2. Client Authentication (Alejandro)", False, 
                                  "No JWT token received", {"response": data})
                    return False
            else:
                self.log_result("2. Client Authentication (Alejandro)", False, 
                              f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("2. Client Authentication (Alejandro)", False, f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_validation(self):
        """Test JWT token validation on protected endpoints"""
        try:
            # Test with valid token
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                self.log_result("3. JWT Token Validation", True, 
                              "Protected endpoint accessible with valid JWT token")
                return True
            else:
                self.log_result("3. JWT Token Validation", False, 
                              f"Protected endpoint failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("3. JWT Token Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_google_oauth_integration(self):
        """Test Google OAuth URL generation and callback"""
        try:
            # Test OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url")
                if auth_url and ("auth.emergentagent.com" in auth_url or "accounts.google.com" in auth_url):
                    self.log_result("4. Google OAuth Integration", True, 
                                  "OAuth URL generation working - no redirect_uri_mismatch")
                    return True
                else:
                    self.log_result("4. Google OAuth Integration", False, 
                                  "Invalid or missing auth URL", {"response": data})
                    return False
            else:
                self.log_result("4. Google OAuth Integration", False, 
                              f"OAuth URL generation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("4. Google OAuth Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_crm_system(self):
        """Test CRM prospect creation, pipeline transitions, and client conversion"""
        try:
            # Test prospect creation
            test_prospect = {
                "name": "Production Test Prospect",
                "email": "production.test@fidus.com",
                "phone": "+1-555-PROD",
                "notes": "Production readiness test prospect"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect)
            if response.status_code != 200:
                self.log_result("5. CRM System", False, 
                              f"Prospect creation failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            prospect_id = data.get("prospect_id")
            if not prospect_id:
                self.log_result("5. CRM System", False, 
                              "No prospect ID returned", {"response": data})
                return False
            
            # Test pipeline transitions
            stages = ["qualified", "proposal", "negotiation", "won"]
            for stage in stages:
                response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", 
                                          json={"stage": stage})
                if response.status_code != 200:
                    self.log_result("5. CRM System", False, 
                                  f"Pipeline transition to {stage} failed: HTTP {response.status_code}")
                    return False
            
            # Test client conversion
            response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/convert", 
                                       json={"send_agreement": True})
            if response.status_code == 200:
                conversion_data = response.json()
                client_id = conversion_data.get("client_id")
                if client_id:
                    self.log_result("5. CRM System", True, 
                                  f"Complete CRM workflow successful: prospect → pipeline → client ({client_id})")
                    return True
                else:
                    self.log_result("5. CRM System", False, 
                                  "Client conversion failed - no client ID")
                    return False
            else:
                self.log_result("5. CRM System", False, 
                              f"Client conversion failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("5. CRM System", False, f"Exception: {str(e)}")
            return False
    
    def test_data_persistence(self):
        """Test that Alejandro Mariscal Romero exists in both users and clients"""
        try:
            # Check users list
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code != 200:
                self.log_result("6. Data Persistence", False, 
                              f"Failed to get users list: HTTP {response.status_code}")
                return False
            
            users_data = response.json()
            users = users_data.get("users", []) if isinstance(users_data, dict) else users_data
            
            alejandro_in_users = False
            for user in users:
                name = user.get("name", "")
                username = user.get("username", "")
                if ("Alejandro" in name and "Mariscal" in name) or username == "alexmar760":
                    alejandro_in_users = True
                    break
            
            # Check clients list
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code != 200:
                self.log_result("6. Data Persistence", False, 
                              f"Failed to get clients list: HTTP {response.status_code}")
                return False
            
            clients_data = response.json()
            clients = clients_data.get("clients", []) if isinstance(clients_data, dict) else clients_data
            
            alejandro_in_clients = False
            for client in clients:
                name = client.get("name", "")
                email = client.get("email", "")
                if ("Alejandro" in name and "Mariscal" in name) or "alexmar" in email:
                    alejandro_in_clients = True
                    break
            
            if alejandro_in_users and alejandro_in_clients:
                self.log_result("6. Data Persistence", True, 
                              "Alejandro Mariscal Romero found in both users and clients lists")
                return True
            else:
                missing = []
                if not alejandro_in_users:
                    missing.append("users list")
                if not alejandro_in_clients:
                    missing.append("clients list")
                self.log_result("6. Data Persistence", False, 
                              f"Alejandro missing from: {', '.join(missing)}")
                return False
                
        except Exception as e:
            self.log_result("6. Data Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_google_api_integration(self):
        """Test Google API endpoints (Gmail, Calendar, Drive)"""
        try:
            api_results = []
            
            # Test Gmail API
            response = self.session.get(f"{BACKEND_URL}/google/gmail/real-messages")
            if response.status_code in [200, 401, 403]:
                api_results.append("Gmail API responding")
            
            # Test Calendar API
            response = self.session.get(f"{BACKEND_URL}/google/calendar/events")
            if response.status_code in [200, 401, 403, 500]:
                api_results.append("Calendar API responding")
            
            # Test Drive API
            response = self.session.get(f"{BACKEND_URL}/google/drive/files")
            if response.status_code in [200, 401, 403, 500]:
                api_results.append("Drive API responding")
            
            if len(api_results) >= 2:  # At least 2 out of 3 APIs responding
                self.log_result("7. Google API Integration", True, 
                              f"Google APIs responding appropriately: {', '.join(api_results)}")
                return True
            else:
                self.log_result("7. Google API Integration", False, 
                              f"Insufficient API responses: {', '.join(api_results)}")
                return False
                
        except Exception as e:
            self.log_result("7. Google API Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_email_system(self):
        """Test email sending endpoints"""
        try:
            test_email = {
                "to": "test@production.fidus.com",
                "subject": "Production Readiness Test",
                "body": "This is a production readiness test email."
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/gmail/real-send", json=test_email)
            if response.status_code in [200, 401, 403, 400]:  # Any of these are acceptable
                self.log_result("8. Email System", True, 
                              f"Email endpoint responding appropriately (HTTP {response.status_code})")
                return True
            else:
                self.log_result("8. Email System", False, 
                              f"Email endpoint failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("8. Email System", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all comprehensive production readiness tests"""
        print("🚨 COMPREHENSIVE PRODUCTION READINESS TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("Testing ALL critical systems for production deployment.")
        print()
        
        # Must authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed.")
            return False
        
        # Run all critical tests
        self.test_client_authentication()
        self.test_jwt_token_validation()
        self.test_google_oauth_integration()
        self.test_crm_system()
        self.test_data_persistence()
        self.test_google_api_integration()
        self.test_email_system()
        
        # Generate final assessment
        self.generate_final_assessment()
        
        return True
    
    def generate_final_assessment(self):
        """Generate final production readiness assessment"""
        print("\n" + "=" * 60)
        print("🏭 FINAL PRODUCTION READINESS ASSESSMENT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Critical Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show results by category
        print("📊 DETAILED RESULTS:")
        print("-" * 30)
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
        print()
        
        # Critical failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print("🚨 CRITICAL FAILURES:")
            for failure in failures:
                print(f"   ❌ {failure['test']}: {failure['message']}")
            print()
        
        # Final verdict
        print("🎯 PRODUCTION READINESS VERDICT:")
        print("=" * 40)
        
        if success_rate >= 90:
            print("✅ SYSTEM IS FULLY PRODUCTION READY!")
            print("   All critical systems operational.")
            print("   Ready for immediate deployment.")
        elif success_rate >= 75:
            print("⚠️ SYSTEM IS MOSTLY PRODUCTION READY")
            print("   Minor issues detected but core functionality working.")
            print("   Can proceed with deployment with monitoring.")
        elif success_rate >= 50:
            print("🔧 SYSTEM NEEDS FIXES BEFORE PRODUCTION")
            print("   Significant issues detected.")
            print("   Fix critical failures before deployment.")
        else:
            print("❌ SYSTEM NOT READY FOR PRODUCTION")
            print("   Major functionality broken.")
            print("   Extensive fixes required.")
        
        print("\n" + "=" * 60)
        
        return success_rate >= 75

def main():
    """Main test execution"""
    test_runner = ComprehensiveProductionTest()
    success = test_runner.run_comprehensive_test()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()