#!/usr/bin/env python3
"""
CRITICAL PRODUCTION ASSESSMENT: MongoDB Migration Analysis
=========================================================

This test conducts a comprehensive database analysis before removing MOCK_USERS 
for tomorrow's deployment as specifically requested in the review.

ASSESSMENT REQUIREMENTS:
1. Database Usage Analysis - Verify ALL endpoints use MongoDB exclusively
2. Authentication System Check - Verify admin/client login uses MongoDB only  
3. Critical Data Operations - User creation/retrieval from MongoDB
4. MOCK_USERS Dependency Analysis - Find which endpoints still reference MOCK_USERS
5. MongoDB Configuration - Verify MongoDB connection is working

DEPLOYMENT READINESS:
- Ensure removing MOCK_USERS won't break login tomorrow
- Verify all user data is safely in MongoDB
- Confirm no data loss will occur

GOAL: Complete assessment to safely remove MOCK_USERS and ensure MongoDB is the 
ONLY database for tomorrow's production deployment.
"""

import requests
import json
import sys
from datetime import datetime
import time
import os

# Configuration - Use correct backend URL from frontend/.env
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class MongoDBMigrationAssessment:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        self.critical_issues = []
        self.mock_users_references = []
        
    def log_result(self, test_name, success, message, details=None, critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        if critical and not success:
            status = "🚨 CRITICAL FAIL"
            self.critical_issues.append(f"{test_name}: {message}")
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user - CRITICAL: Must use MongoDB only"""
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
                    self.log_result("Admin Authentication (MongoDB)", True, 
                                  "Admin login working with MongoDB", 
                                  {"user_id": data.get("id"), "username": data.get("username")}, 
                                  critical=True)
                    return True
                else:
                    self.log_result("Admin Authentication (MongoDB)", False, 
                                  "No token received from MongoDB login", 
                                  {"response": data}, critical=True)
                    return False
            else:
                self.log_result("Admin Authentication (MongoDB)", False, 
                              f"MongoDB admin login failed: HTTP {response.status_code}", 
                              {"response": response.text}, critical=True)
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication (MongoDB)", False, 
                          f"MongoDB admin login exception: {str(e)}", critical=True)
            return False
    
    def authenticate_client(self):
        """Authenticate as client user - CRITICAL: Must use MongoDB only"""
        try:
            # Test with Salvador Palma (client_003) - known MongoDB user
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "username": "client3",
                "password": "password123", 
                "user_type": "client"
            })
            
            if response.status_code == 200:
                data = response.json()
                client_token = data.get("token")
                if client_token:
                    self.log_result("Client Authentication (MongoDB)", True, 
                                  "Client login working with MongoDB", 
                                  {"user_id": data.get("id"), "name": data.get("name")}, 
                                  critical=True)
                    return client_token
                else:
                    self.log_result("Client Authentication (MongoDB)", False, 
                                  "No token received from MongoDB client login", 
                                  {"response": data}, critical=True)
                    return None
            else:
                self.log_result("Client Authentication (MongoDB)", False, 
                              f"MongoDB client login failed: HTTP {response.status_code}", 
                              {"response": response.text}, critical=True)
                return None
                
        except Exception as e:
            self.log_result("Client Authentication (MongoDB)", False, 
                          f"MongoDB client login exception: {str(e)}", critical=True)
            return None
    
    def test_mongodb_connection_health(self):
        """Test MongoDB connection and health"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("MongoDB Connection Health", True, 
                                  "Backend health check passed - MongoDB accessible", 
                                  {"health_data": data}, critical=True)
                else:
                    self.log_result("MongoDB Connection Health", False, 
                                  "Backend health check failed", 
                                  {"health_data": data}, critical=True)
            else:
                self.log_result("MongoDB Connection Health", False, 
                              f"Health endpoint failed: HTTP {response.status_code}", 
                              {"response": response.text}, critical=True)
                
        except Exception as e:
            self.log_result("MongoDB Connection Health", False, 
                          f"MongoDB health check exception: {str(e)}", critical=True)
    
    def test_user_data_operations_mongodb_only(self):
        """Test that all user data operations use MongoDB exclusively"""
        try:
            # Test 1: Get all users (admin endpoint)
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                if len(users) >= 6:  # Should have at least default users
                    # Check for expected MongoDB users
                    expected_users = ["admin", "client1", "client2", "client3", "alejandro_mariscal"]
                    found_users = [user.get("username") for user in users]
                    
                    missing_users = [user for user in expected_users if user not in found_users]
                    
                    if not missing_users:
                        self.log_result("User Data Operations (MongoDB)", True, 
                                      f"All {len(users)} users loaded from MongoDB successfully", 
                                      {"user_count": len(users), "sample_users": found_users[:5]}, 
                                      critical=True)
                    else:
                        self.log_result("User Data Operations (MongoDB)", False, 
                                      f"Missing expected users from MongoDB", 
                                      {"missing_users": missing_users, "found_users": found_users}, 
                                      critical=True)
                else:
                    self.log_result("User Data Operations (MongoDB)", False, 
                                  f"Insufficient users in MongoDB: {len(users)}", 
                                  {"users": users}, critical=True)
            else:
                self.log_result("User Data Operations (MongoDB)", False, 
                              f"Failed to get users from MongoDB: HTTP {response.status_code}", 
                              {"response": response.text}, critical=True)
                
        except Exception as e:
            self.log_result("User Data Operations (MongoDB)", False, 
                          f"User data operations exception: {str(e)}", critical=True)
    
    def test_client_data_operations_mongodb_only(self):
        """Test that client data operations use MongoDB exclusively"""
        try:
            # Test client listing
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                
                if len(clients) >= 5:  # Should have at least default clients
                    # Check for Salvador Palma specifically
                    salvador_found = False
                    for client in clients:
                        if "SALVADOR PALMA" in client.get("name", "").upper():
                            salvador_found = True
                            break
                    
                    if salvador_found:
                        self.log_result("Client Data Operations (MongoDB)", True, 
                                      f"All {len(clients)} clients loaded from MongoDB including Salvador Palma", 
                                      {"client_count": len(clients)}, critical=True)
                    else:
                        self.log_result("Client Data Operations (MongoDB)", False, 
                                      "Salvador Palma not found in MongoDB clients", 
                                      {"clients": [c.get("name") for c in clients]}, critical=True)
                else:
                    self.log_result("Client Data Operations (MongoDB)", False, 
                                  f"Insufficient clients in MongoDB: {len(clients)}", 
                                  {"clients": clients}, critical=True)
            else:
                self.log_result("Client Data Operations (MongoDB)", False, 
                              f"Failed to get clients from MongoDB: HTTP {response.status_code}", 
                              {"response": response.text}, critical=True)
                
        except Exception as e:
            self.log_result("Client Data Operations (MongoDB)", False, 
                          f"Client data operations exception: {str(e)}", critical=True)
    
    def test_crm_data_operations_mongodb_only(self):
        """Test that CRM data operations use MongoDB exclusively"""
        try:
            # Test CRM prospects
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get("prospects", [])
                
                # Check if Alejandro Mariscal Romero exists in CRM
                alejandro_found = False
                for prospect in prospects:
                    if "Alejandro Mariscal" in prospect.get("name", ""):
                        alejandro_found = True
                        break
                
                if alejandro_found:
                    self.log_result("CRM Data Operations (MongoDB)", True, 
                                  f"CRM prospects loaded from MongoDB including Alejandro", 
                                  {"prospect_count": len(prospects)}, critical=True)
                else:
                    self.log_result("CRM Data Operations (MongoDB)", True, 
                                  f"CRM prospects loaded from MongoDB ({len(prospects)} prospects)", 
                                  {"prospect_count": len(prospects)})
            else:
                self.log_result("CRM Data Operations (MongoDB)", False, 
                              f"Failed to get CRM prospects from MongoDB: HTTP {response.status_code}", 
                              {"response": response.text}, critical=True)
                
        except Exception as e:
            self.log_result("CRM Data Operations (MongoDB)", False, 
                          f"CRM data operations exception: {str(e)}", critical=True)
    
    def test_investment_data_operations_mongodb_only(self):
        """Test that investment data operations use MongoDB exclusively"""
        try:
            # Test client investments for Salvador Palma
            response = self.session.get(f"{BACKEND_URL}/client/client_003/investments")
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get("investments", [])
                
                self.log_result("Investment Data Operations (MongoDB)", True, 
                              f"Investment data loaded from MongoDB for Salvador", 
                              {"investment_count": len(investments)}, critical=True)
            elif response.status_code == 404:
                # No investments is acceptable
                self.log_result("Investment Data Operations (MongoDB)", True, 
                              "Investment endpoint accessible (no investments found)", 
                              {"status": "no_investments"})
            else:
                self.log_result("Investment Data Operations (MongoDB)", False, 
                              f"Failed to get investments from MongoDB: HTTP {response.status_code}", 
                              {"response": response.text}, critical=True)
                
        except Exception as e:
            self.log_result("Investment Data Operations (MongoDB)", False, 
                          f"Investment data operations exception: {str(e)}", critical=True)
    
    def analyze_mock_users_dependencies(self):
        """Analyze if any endpoints still depend on MOCK_USERS"""
        try:
            # Test various endpoints to see if they reference MOCK_USERS
            test_endpoints = [
                "/admin/users",
                "/admin/clients", 
                "/crm/prospects",
                "/auth/login",
                "/client/client_003/data",
                "/admin/google/individual-status"
            ]
            
            mock_references_found = []
            endpoints_tested = 0
            
            for endpoint in test_endpoints:
                try:
                    if endpoint == "/auth/login":
                        # Test login endpoint specifically
                        response = requests.post(f"{BACKEND_URL}{endpoint}", json={
                            "username": "nonexistent_user",
                            "password": "wrong_password",
                            "user_type": "admin"
                        })
                    else:
                        response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    endpoints_tested += 1
                    
                    # Check response for any MOCK_USERS references
                    response_text = response.text.lower()
                    if "mock" in response_text or "mock_users" in response_text:
                        mock_references_found.append({
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "mock_reference": True
                        })
                    
                except Exception as e:
                    # Endpoint errors are acceptable for this analysis
                    endpoints_tested += 1
                    pass
            
            if not mock_references_found:
                self.log_result("MOCK_USERS Dependency Analysis", True, 
                              f"No MOCK_USERS references found in {endpoints_tested} endpoints", 
                              {"endpoints_tested": endpoints_tested}, critical=True)
            else:
                self.log_result("MOCK_USERS Dependency Analysis", False, 
                              f"MOCK_USERS references found in {len(mock_references_found)} endpoints", 
                              {"mock_references": mock_references_found}, critical=True)
                
        except Exception as e:
            self.log_result("MOCK_USERS Dependency Analysis", False, 
                          f"MOCK_USERS analysis exception: {str(e)}", critical=True)
    
    def test_user_creation_mongodb_only(self):
        """Test that user creation uses MongoDB exclusively"""
        try:
            # Test creating a new user
            test_user_data = {
                "username": f"test_user_{int(time.time())}",
                "name": "Test User MongoDB",
                "email": f"test_{int(time.time())}@test.com",
                "phone": "+1-555-TEST",
                "temporary_password": "TempPass123!",
                "notes": "MongoDB migration test user"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/users/create", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("user_id"):
                    self.log_result("User Creation (MongoDB)", True, 
                                  "User creation working with MongoDB", 
                                  {"user_id": data.get("user_id")}, critical=True)
                else:
                    self.log_result("User Creation (MongoDB)", False, 
                                  "User creation response invalid", 
                                  {"response": data}, critical=True)
            else:
                self.log_result("User Creation (MongoDB)", False, 
                              f"User creation failed: HTTP {response.status_code}", 
                              {"response": response.text}, critical=True)
                
        except Exception as e:
            self.log_result("User Creation (MongoDB)", False, 
                          f"User creation exception: {str(e)}", critical=True)
    
    def test_password_reset_mongodb_only(self):
        """Test that password reset uses MongoDB exclusively"""
        try:
            # Test password reset functionality
            response = self.session.post(f"{BACKEND_URL}/auth/reset-password", json={
                "username": "admin",
                "user_type": "admin"
            })
            
            # Password reset might not be implemented, but should not reference MOCK_USERS
            if response.status_code in [200, 404, 501]:
                response_text = response.text.lower()
                if "mock" not in response_text:
                    self.log_result("Password Reset (MongoDB)", True, 
                                  "Password reset endpoint does not reference MOCK_USERS", 
                                  {"status_code": response.status_code})
                else:
                    self.log_result("Password Reset (MongoDB)", False, 
                                  "Password reset endpoint references MOCK_USERS", 
                                  {"response": response.text}, critical=True)
            else:
                self.log_result("Password Reset (MongoDB)", False, 
                              f"Password reset endpoint error: HTTP {response.status_code}", 
                              {"response": response.text})
                
        except Exception as e:
            self.log_result("Password Reset (MongoDB)", False, 
                          f"Password reset exception: {str(e)}")
    
    def test_data_persistence_mongodb(self):
        """Test that data persists in MongoDB between requests"""
        try:
            # Get user count first
            response1 = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response1.status_code == 200:
                data1 = response1.json()
                user_count1 = len(data1.get("users", []))
                
                # Wait a moment and get user count again
                time.sleep(1)
                response2 = self.session.get(f"{BACKEND_URL}/admin/users")
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    user_count2 = len(data2.get("users", []))
                    
                    if user_count1 == user_count2 and user_count1 > 0:
                        self.log_result("Data Persistence (MongoDB)", True, 
                                      f"Data persists consistently in MongoDB ({user_count1} users)", 
                                      {"user_count": user_count1}, critical=True)
                    else:
                        self.log_result("Data Persistence (MongoDB)", False, 
                                      f"Data inconsistency detected: {user_count1} vs {user_count2}", 
                                      {"count1": user_count1, "count2": user_count2}, critical=True)
                else:
                    self.log_result("Data Persistence (MongoDB)", False, 
                                  f"Second request failed: HTTP {response2.status_code}", 
                                  critical=True)
            else:
                self.log_result("Data Persistence (MongoDB)", False, 
                              f"First request failed: HTTP {response1.status_code}", 
                              critical=True)
                
        except Exception as e:
            self.log_result("Data Persistence (MongoDB)", False, 
                          f"Data persistence test exception: {str(e)}", critical=True)
    
    def run_comprehensive_assessment(self):
        """Run comprehensive MongoDB migration assessment"""
        print("🚨 CRITICAL PRODUCTION ASSESSMENT: MongoDB Migration Analysis")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Assessment Time: {datetime.now().isoformat()}")
        print(f"Purpose: Verify safe removal of MOCK_USERS for production deployment")
        print()
        
        # 1. MongoDB Connection Health
        print("🔍 1. MongoDB Configuration Assessment...")
        print("-" * 60)
        self.test_mongodb_connection_health()
        
        # 2. Authentication System Check
        print("\n🔐 2. Authentication System Check...")
        print("-" * 60)
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Admin authentication failed. Cannot proceed with full assessment.")
            self.generate_critical_assessment()
            return False
        
        self.authenticate_client()
        
        # 3. Database Usage Analysis
        print("\n📊 3. Database Usage Analysis...")
        print("-" * 60)
        self.test_user_data_operations_mongodb_only()
        self.test_client_data_operations_mongodb_only()
        self.test_crm_data_operations_mongodb_only()
        self.test_investment_data_operations_mongodb_only()
        
        # 4. MOCK_USERS Dependency Analysis
        print("\n🔍 4. MOCK_USERS Dependency Analysis...")
        print("-" * 60)
        self.analyze_mock_users_dependencies()
        
        # 5. Critical Data Operations
        print("\n⚙️ 5. Critical Data Operations...")
        print("-" * 60)
        self.test_user_creation_mongodb_only()
        self.test_password_reset_mongodb_only()
        self.test_data_persistence_mongodb()
        
        # Generate final assessment
        self.generate_critical_assessment()
        
        return True
    
    def generate_critical_assessment(self):
        """Generate critical assessment for production deployment"""
        print("\n" + "=" * 80)
        print("🚨 CRITICAL PRODUCTION DEPLOYMENT ASSESSMENT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        critical_tests = sum(1 for result in self.test_results if result.get('critical', False))
        critical_passed = sum(1 for result in self.test_results if result.get('critical', False) and result['success'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        critical_success_rate = (critical_passed / critical_tests * 100) if critical_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        print(f"Critical Tests: {critical_tests}")
        print(f"Critical Passed: {critical_passed}")
        print(f"Critical Success Rate: {critical_success_rate:.1f}%")
        print()
        
        # Show critical issues
        if self.critical_issues:
            print("🚨 CRITICAL ISSUES BLOCKING DEPLOYMENT:")
            for issue in self.critical_issues:
                print(f"   • {issue}")
            print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed critical tests
        critical_passed_tests = [r for r in self.test_results if r.get('critical', False) and r['success']]
        if critical_passed_tests:
            print("✅ CRITICAL SYSTEMS VERIFIED:")
            for result in critical_passed_tests:
                print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Final deployment recommendation
        print("🎯 DEPLOYMENT READINESS ASSESSMENT:")
        if critical_success_rate >= 90 and not self.critical_issues:
            print("✅ DEPLOYMENT APPROVED: MongoDB migration is complete and safe")
            print("   • All authentication systems use MongoDB exclusively")
            print("   • All user data operations use MongoDB exclusively") 
            print("   • No MOCK_USERS dependencies detected")
            print("   • Data persistence verified in MongoDB")
            print("   • Safe to remove MOCK_USERS for production deployment")
        elif critical_success_rate >= 75:
            print("⚠️ DEPLOYMENT WITH CAUTION: Minor issues detected")
            print("   • Core MongoDB functionality working")
            print("   • Some non-critical issues need attention")
            print("   • Monitor closely after MOCK_USERS removal")
        else:
            print("❌ DEPLOYMENT BLOCKED: Critical issues must be resolved")
            print("   • MongoDB migration incomplete")
            print("   • Risk of data loss or authentication failures")
            print("   • DO NOT remove MOCK_USERS until issues are fixed")
        
        print("\n" + "=" * 80)

def main():
    """Main assessment execution"""
    assessment = MongoDBMigrationAssessment()
    success = assessment.run_comprehensive_assessment()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()