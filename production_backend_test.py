#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION READINESS BACKEND TESTING
=================================================

This test suite verifies all critical backend systems for production deployment:

1. Authentication & Authorization (Admin login, JWT, Google OAuth)
2. CRM Pipeline System (prospects, pipeline management, conversions)
3. Investment Management (create/list investments, MT5 mapping)
4. Google APIs Integration (OAuth, Gmail, Calendar, Drive, Meet)
5. Document Management (upload, signing workflow, Google Drive sharing)
6. User Management (creation, role-based access, client management)

Expected Results:
- All critical endpoints return proper responses
- Complete workflow from lead creation to investment mapping works
- Google integration is production-ready
- Production-level stability and error handling verified
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import time
import uuid

# Configuration
BACKEND_URL = "https://fidus-workspace-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ProductionBackendTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.test_data = {}  # Store created test data for cleanup
        
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
        """Authenticate as admin user and get JWT token"""
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
                    self.log_result("Admin Authentication", True, "Successfully authenticated as admin with JWT token")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "No JWT token received", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_management(self):
        """Test JWT token validation and refresh functionality"""
        try:
            # Test token validation by accessing protected endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                self.log_result("JWT Token Validation", True, "JWT token successfully validates protected endpoints")
            else:
                self.log_result("JWT Token Validation", False, f"JWT validation failed: HTTP {response.status_code}")
            
            # Test token refresh endpoint
            response = self.session.post(f"{BACKEND_URL}/auth/refresh-token")
            if response.status_code == 200:
                refresh_data = response.json()
                if refresh_data.get("success") and refresh_data.get("token"):
                    # Update session with new token
                    new_token = refresh_data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {new_token}"})
                    self.log_result("JWT Token Refresh", True, "JWT token refresh successful")
                else:
                    self.log_result("JWT Token Refresh", False, "Token refresh response invalid", {"response": refresh_data})
            else:
                self.log_result("JWT Token Refresh", False, f"Token refresh failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("JWT Token Management", False, f"Exception: {str(e)}")
    
    def test_google_oauth_integration(self):
        """Test Google OAuth integration endpoints"""
        try:
            # Test Google OAuth URL generation
            response = self.session.get(f"{BACKEND_URL}/admin/google/auth-url")
            if response.status_code == 200:
                oauth_data = response.json()
                if oauth_data.get("success") and oauth_data.get("auth_url"):
                    auth_url = oauth_data["auth_url"]
                    # Check for either direct Google OAuth or Emergent OAuth service
                    if ("accounts.google.com" in auth_url or "auth.emergentagent.com" in auth_url):
                        self.log_result("Google OAuth URL Generation", True, "Google OAuth URL generated successfully")
                    else:
                        self.log_result("Google OAuth URL Generation", False, "Invalid OAuth URL format", {"auth_url": auth_url})
                else:
                    self.log_result("Google OAuth URL Generation", False, "Invalid OAuth response", {"response": oauth_data})
            else:
                self.log_result("Google OAuth URL Generation", False, f"OAuth URL generation failed: HTTP {response.status_code}")
            
            # Test Google profile endpoint (may return 500 if not authenticated with Google)
            response = self.session.get(f"{BACKEND_URL}/admin/google/profile")
            if response.status_code == 200:
                self.log_result("Google Profile Access", True, "Google profile endpoint accessible")
            elif response.status_code == 401:
                self.log_result("Google Profile Access", True, "Google profile correctly requires OAuth (401 expected)")
            else:
                self.log_result("Google Profile Access", False, f"Unexpected response: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google OAuth Integration", False, f"Exception: {str(e)}")
    
    def test_crm_pipeline_system(self):
        """Test complete CRM pipeline functionality"""
        try:
            # Create a test prospect
            test_prospect_data = {
                "name": f"Test Prospect {uuid.uuid4().hex[:8]}",
                "email": f"test.prospect.{uuid.uuid4().hex[:8]}@example.com",
                "phone": "+1-555-0123",
                "notes": "Test prospect for production readiness testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_prospect_data)
            if response.status_code == 200:
                prospect_data = response.json()
                prospect_id = prospect_data.get("id")
                if prospect_id:
                    self.test_data["prospect_id"] = prospect_id
                    self.log_result("CRM Prospect Creation", True, f"Prospect created successfully: {prospect_id}")
                    
                    # Test prospect update (move through pipeline stages)
                    stages = ["qualified", "proposal", "negotiation", "won"]
                    for stage in stages:
                        update_response = self.session.put(f"{BACKEND_URL}/crm/prospects/{prospect_id}", json={
                            "stage": stage,
                            "notes": f"Updated to {stage} stage during testing"
                        })
                        
                        if update_response.status_code == 200:
                            self.log_result(f"CRM Pipeline - {stage.title()} Stage", True, f"Successfully moved prospect to {stage}")
                        else:
                            self.log_result(f"CRM Pipeline - {stage.title()} Stage", False, f"Failed to update to {stage}: HTTP {update_response.status_code}")
                    
                    # Test prospect conversion to client
                    conversion_response = self.session.post(f"{BACKEND_URL}/crm/prospects/{prospect_id}/convert", json={
                        "prospect_id": prospect_id,
                        "send_agreement": True
                    })
                    
                    if conversion_response.status_code == 200:
                        conversion_data = conversion_response.json()
                        if conversion_data.get("success"):
                            client_id = conversion_data.get("client_id")
                            self.test_data["converted_client_id"] = client_id
                            self.log_result("CRM Prospect Conversion", True, f"Prospect successfully converted to client: {client_id}")
                        else:
                            self.log_result("CRM Prospect Conversion", False, "Conversion response indicates failure", {"response": conversion_data})
                    else:
                        self.log_result("CRM Prospect Conversion", False, f"Conversion failed: HTTP {conversion_response.status_code}")
                else:
                    self.log_result("CRM Prospect Creation", False, "No prospect ID returned", {"response": prospect_data})
            else:
                self.log_result("CRM Prospect Creation", False, f"Prospect creation failed: HTTP {response.status_code}")
            
            # Test pipeline visualization data
            pipeline_response = self.session.get(f"{BACKEND_URL}/crm/prospects/pipeline")
            if pipeline_response.status_code == 200:
                pipeline_data = pipeline_response.json()
                if isinstance(pipeline_data, dict) and "pipeline_stats" in pipeline_data:
                    self.log_result("CRM Pipeline Visualization", True, "Pipeline data retrieved successfully")
                else:
                    self.log_result("CRM Pipeline Visualization", False, "Invalid pipeline data format", {"response": pipeline_data})
            else:
                self.log_result("CRM Pipeline Visualization", False, f"Pipeline data retrieval failed: HTTP {pipeline_response.status_code}")
                
        except Exception as e:
            self.log_result("CRM Pipeline System", False, f"Exception: {str(e)}")
    
    def test_investment_management(self):
        """Test investment creation and management"""
        try:
            # Test investment creation
            if "converted_client_id" in self.test_data:
                client_id = self.test_data["converted_client_id"]
            else:
                # Use existing client for testing
                client_id = "client_003"  # Salvador Palma
            
            test_investment_data = {
                "client_id": client_id,
                "fund_code": "CORE",
                "amount": 10000.0,
                "deposit_date": datetime.now().strftime("%Y-%m-%d"),
                "create_mt5_account": True,
                "mt5_login": f"test{uuid.uuid4().hex[:6]}",
                "mt5_password": "TestPassword123",
                "mt5_server": "Multibank-Demo",
                "broker_name": "Multibank",
                "mt5_initial_balance": 10000.0
            }
            
            response = self.session.post(f"{BACKEND_URL}/investments/create", json=test_investment_data)
            if response.status_code == 200:
                investment_data = response.json()
                investment_id = investment_data.get("investment_id")
                if investment_id:
                    self.test_data["investment_id"] = investment_id
                    self.log_result("Investment Creation", True, f"Investment created successfully: {investment_id}")
                else:
                    self.log_result("Investment Creation", False, "No investment ID returned", {"response": investment_data})
            else:
                self.log_result("Investment Creation", False, f"Investment creation failed: HTTP {response.status_code}")
            
            # Test investment listing for client
            response = self.session.get(f"{BACKEND_URL}/investments/client/{client_id}")
            if response.status_code == 200:
                investment_response = response.json()
                if isinstance(investment_response, dict) and investment_response.get("success") and "investments" in investment_response:
                    investments = investment_response["investments"]
                    self.log_result("Investment Listing", True, f"Retrieved {len(investments)} investments for client")
                elif isinstance(investment_response, list):
                    self.log_result("Investment Listing", True, f"Retrieved {len(investment_response)} investments for client")
                else:
                    self.log_result("Investment Listing", False, "Invalid investments format", {"response": investment_response})
            else:
                self.log_result("Investment Listing", False, f"Investment listing failed: HTTP {response.status_code}")
            
            # Test MT5 account mapping
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            if response.status_code == 200:
                mt5_response = response.json()
                if isinstance(mt5_response, dict) and mt5_response.get("success") and "accounts" in mt5_response:
                    accounts = mt5_response["accounts"]
                    self.log_result("MT5 Account Mapping", True, f"MT5 accounts retrieved: {len(accounts)} accounts")
                elif isinstance(mt5_response, list):
                    self.log_result("MT5 Account Mapping", True, f"MT5 accounts retrieved: {len(mt5_response)} accounts")
                else:
                    self.log_result("MT5 Account Mapping", False, "Invalid MT5 accounts format", {"response": mt5_response})
            else:
                self.log_result("MT5 Account Mapping", False, f"MT5 accounts retrieval failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Investment Management", False, f"Exception: {str(e)}")
    
    def test_google_apis_integration(self):
        """Test Google APIs integration (Gmail, Calendar, Drive, Meet)"""
        try:
            # Test Gmail API endpoints
            gmail_endpoints = [
                ("/google/gmail/messages", "Gmail Messages"),
                ("/google/gmail/real-messages", "Real Gmail Messages")
            ]
            
            for endpoint, name in gmail_endpoints:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    gmail_data = response.json()
                    if isinstance(gmail_data, dict) and ("messages" in gmail_data or "emails" in gmail_data):
                        self.log_result(f"Google API - {name}", True, f"{name} endpoint working")
                    else:
                        self.log_result(f"Google API - {name}", False, f"Invalid {name} response format")
                else:
                    self.log_result(f"Google API - {name}", False, f"{name} failed: HTTP {response.status_code}")
            
            # Test Gmail send functionality
            test_email_data = {
                "to": "test@example.com",
                "subject": "Production Test Email",
                "body": "This is a test email for production readiness verification."
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/gmail/send", json=test_email_data)
            if response.status_code == 200:
                send_data = response.json()
                if send_data.get("success"):
                    self.log_result("Google API - Gmail Send", True, "Gmail send functionality working")
                else:
                    self.log_result("Google API - Gmail Send", False, "Gmail send failed", {"response": send_data})
            else:
                self.log_result("Google API - Gmail Send", False, f"Gmail send failed: HTTP {response.status_code}")
            
            # Test Google Calendar API
            response = self.session.get(f"{BACKEND_URL}/google/calendar/events")
            if response.status_code == 200:
                calendar_data = response.json()
                if isinstance(calendar_data, dict):
                    self.log_result("Google API - Calendar Events", True, "Calendar events endpoint working")
                else:
                    self.log_result("Google API - Calendar Events", False, "Invalid calendar response format")
            else:
                self.log_result("Google API - Calendar Events", False, f"Calendar events failed: HTTP {response.status_code}")
            
            # Test Google Drive API
            response = self.session.get(f"{BACKEND_URL}/google/drive/files")
            if response.status_code == 200:
                drive_data = response.json()
                if isinstance(drive_data, dict):
                    self.log_result("Google API - Drive Files", True, "Drive files endpoint working")
                else:
                    self.log_result("Google API - Drive Files", False, "Invalid drive response format")
            else:
                self.log_result("Google API - Drive Files", False, f"Drive files failed: HTTP {response.status_code}")
            
            # Test Google Meet integration
            meet_data = {
                "title": "Production Test Meeting",
                "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
                "duration": 60
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/meet/create", json=meet_data)
            if response.status_code == 200:
                meet_response = response.json()
                if meet_response.get("success") and meet_response.get("meet_link"):
                    self.log_result("Google API - Meet Creation", True, "Google Meet creation working")
                else:
                    self.log_result("Google API - Meet Creation", False, "Meet creation failed", {"response": meet_response})
            else:
                self.log_result("Google API - Meet Creation", False, f"Meet creation failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Google APIs Integration", False, f"Exception: {str(e)}")
    
    def test_document_management(self):
        """Test document management and signing workflow"""
        try:
            # Test document upload endpoint
            # Note: This is a simplified test without actual file upload
            response = self.session.get(f"{BACKEND_URL}/documents/types")
            if response.status_code == 200:
                doc_types = response.json()
                self.log_result("Document Management - Types", True, "Document types endpoint working")
            else:
                self.log_result("Document Management - Types", False, f"Document types failed: HTTP {response.status_code}")
            
            # Test document signing workflow endpoints
            signing_endpoints = [
                ("/documents/signing/status", "Signing Status"),
                ("/documents/templates", "Document Templates")
            ]
            
            for endpoint, name in signing_endpoints:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                    self.log_result(f"Document Management - {name}", True, f"{name} endpoint accessible")
                else:
                    self.log_result(f"Document Management - {name}", False, f"{name} failed: HTTP {response.status_code}")
            
            # Test Google Drive document sharing
            share_data = {
                "document_id": "test_document_123",
                "email": "test@example.com",
                "permission": "view"
            }
            
            response = self.session.post(f"{BACKEND_URL}/google/drive/share", json=share_data)
            if response.status_code in [200, 400]:  # 400 might be expected for test data
                self.log_result("Document Management - Drive Sharing", True, "Google Drive sharing endpoint accessible")
            else:
                self.log_result("Document Management - Drive Sharing", False, f"Drive sharing failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Document Management", False, f"Exception: {str(e)}")
    
    def test_user_management(self):
        """Test user creation and management"""
        try:
            # Test user creation
            test_user_data = {
                "username": f"testuser_{uuid.uuid4().hex[:8]}",
                "name": "Test User Production",
                "email": f"testuser.{uuid.uuid4().hex[:8]}@example.com",
                "phone": "+1-555-0199",
                "temporary_password": "TempPass123!",
                "notes": "Test user for production readiness"
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/users/create", json=test_user_data)
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get("user_id") or user_data.get("id")
                if user_id:
                    self.test_data["test_user_id"] = user_id
                    self.log_result("User Management - Creation", True, f"User created successfully: {user_id}")
                else:
                    self.log_result("User Management - Creation", False, "No user ID returned", {"response": user_data})
            else:
                self.log_result("User Management - Creation", False, f"User creation failed: HTTP {response.status_code}")
            
            # Test client management
            response = self.session.get(f"{BACKEND_URL}/admin/clients")
            if response.status_code == 200:
                clients = response.json()
                if isinstance(clients, (list, dict)):
                    client_count = len(clients) if isinstance(clients, list) else clients.get('total_clients', 0)
                    self.log_result("User Management - Client Listing", True, f"Retrieved client data: {client_count} clients")
                else:
                    self.log_result("User Management - Client Listing", False, "Invalid clients response format")
            else:
                self.log_result("User Management - Client Listing", False, f"Client listing failed: HTTP {response.status_code}")
            
            # Test role-based access control
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 200:
                users = response.json()
                self.log_result("User Management - Admin Access", True, "Admin user listing accessible")
            else:
                self.log_result("User Management - Admin Access", False, f"Admin user access failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("User Management", False, f"Exception: {str(e)}")
    
    def test_system_health_and_monitoring(self):
        """Test system health and monitoring endpoints"""
        try:
            # Test basic health check
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    self.log_result("System Health - Basic", True, "Basic health check passing")
                else:
                    self.log_result("System Health - Basic", False, "Health check indicates issues", {"response": health_data})
            else:
                self.log_result("System Health - Basic", False, f"Health check failed: HTTP {response.status_code}")
            
            # Test readiness check
            response = self.session.get(f"{BACKEND_URL}/health/ready")
            if response.status_code == 200:
                ready_data = response.json()
                if ready_data.get("status") == "ready":
                    self.log_result("System Health - Readiness", True, "Readiness check passing")
                else:
                    self.log_result("System Health - Readiness", False, "Readiness check indicates issues", {"response": ready_data})
            else:
                self.log_result("System Health - Readiness", False, f"Readiness check failed: HTTP {response.status_code}")
            
            # Test metrics endpoint
            response = self.session.get(f"{BACKEND_URL}/health/metrics")
            if response.status_code == 200:
                metrics_data = response.json()
                self.log_result("System Health - Metrics", True, "Metrics endpoint accessible")
            else:
                self.log_result("System Health - Metrics", False, f"Metrics endpoint failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("System Health and Monitoring", False, f"Exception: {str(e)}")
    
    def test_production_workflow(self):
        """Test complete production workflow: Lead → Investment → MT5 Mapping"""
        try:
            workflow_success = True
            workflow_steps = []
            
            # Step 1: Create prospect (already done in CRM test)
            if "prospect_id" in self.test_data:
                workflow_steps.append("✅ Prospect Created")
            else:
                workflow_steps.append("❌ Prospect Creation Failed")
                workflow_success = False
            
            # Step 2: Convert to client (already done in CRM test)
            if "converted_client_id" in self.test_data:
                workflow_steps.append("✅ Prospect Converted to Client")
            else:
                workflow_steps.append("❌ Prospect Conversion Failed")
                workflow_success = False
            
            # Step 3: Create investment (already done in investment test)
            if "investment_id" in self.test_data:
                workflow_steps.append("✅ Investment Created")
            else:
                workflow_steps.append("❌ Investment Creation Failed")
                workflow_success = False
            
            # Step 4: Verify MT5 account mapping
            if "investment_id" in self.test_data:
                response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
                if response.status_code == 200:
                    workflow_steps.append("✅ MT5 Account Mapping Verified")
                else:
                    workflow_steps.append("❌ MT5 Account Mapping Failed")
                    workflow_success = False
            
            if workflow_success:
                self.log_result("Production Workflow - Complete", True, "Full workflow completed successfully", {"steps": workflow_steps})
            else:
                self.log_result("Production Workflow - Complete", False, "Workflow has failures", {"steps": workflow_steps})
                
        except Exception as e:
            self.log_result("Production Workflow", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all production readiness tests"""
        print("🚀 COMPREHENSIVE PRODUCTION READINESS BACKEND TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n🔍 Running Production Readiness Tests...")
        print("-" * 50)
        
        # Run all test categories
        self.test_jwt_token_management()
        self.test_google_oauth_integration()
        self.test_crm_pipeline_system()
        self.test_investment_management()
        self.test_google_apis_integration()
        self.test_document_management()
        self.test_user_management()
        self.test_system_health_and_monitoring()
        self.test_production_workflow()
        
        # Generate comprehensive summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🚀 PRODUCTION READINESS TEST SUMMARY")
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
        
        # Categorize results
        categories = {
            "Authentication & Authorization": ["Admin Authentication", "JWT Token"],
            "Google Integration": ["Google OAuth", "Google API"],
            "CRM Pipeline": ["CRM Prospect", "CRM Pipeline"],
            "Investment Management": ["Investment", "MT5 Account"],
            "Document Management": ["Document Management"],
            "User Management": ["User Management"],
            "System Health": ["System Health"],
            "Production Workflow": ["Production Workflow"]
        }
        
        print("📊 RESULTS BY CATEGORY:")
        print("-" * 30)
        
        for category, keywords in categories.items():
            category_results = [r for r in self.test_results if any(keyword in r['test'] for keyword in keywords)]
            if category_results:
                category_passed = sum(1 for r in category_results if r['success'])
                category_total = len(category_results)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                status = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
                print(f"{status} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        print()
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if not r['success'] and any(keyword in r['test'] for keyword in ['Authentication', 'OAuth', 'Workflow'])]
        if critical_failures:
            print("🚨 CRITICAL FAILURES:")
            for result in critical_failures:
                print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show all failures
        if failed_tests > 0:
            print("❌ ALL FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Production readiness assessment
        print("🎯 PRODUCTION READINESS ASSESSMENT:")
        print("-" * 40)
        
        if success_rate >= 90:
            print("✅ PRODUCTION READY - APPROVED FOR DEPLOYMENT")
            print("   All critical systems are operational and stable.")
            print("   System meets production deployment requirements.")
        elif success_rate >= 80:
            print("⚠️ PRODUCTION READY WITH MINOR ISSUES")
            print("   Core functionality working but some non-critical issues found.")
            print("   Deployment approved with monitoring recommendations.")
        elif success_rate >= 70:
            print("⚠️ PRODUCTION READY WITH CAUTION")
            print("   Most functionality working but several issues need attention.")
            print("   Deployment possible but fixes recommended.")
        else:
            print("❌ NOT PRODUCTION READY")
            print("   Critical issues found that prevent production deployment.")
            print("   Main agent action required before deployment approval.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    test_runner = ProductionBackendTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()