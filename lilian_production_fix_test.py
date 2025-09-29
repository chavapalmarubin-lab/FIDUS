#!/usr/bin/env python3
"""
LILIAN PRODUCTION ENVIRONMENT FIX TEST
=====================================

This test addresses the critical issue identified:
- Preview environment: Lilian exists as client_a04533ff ✅
- Production environment: Lilian does NOT exist ❌
- User sees production environment, hence the complaint

This test will:
1. Verify the issue exists in production
2. Create Lilian as a prospect in production
3. Convert her to client in production
4. Verify she appears in Client Directory
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
PRODUCTION_URL = "https://fidus-invest.emergent.host/api"
PREVIEW_URL = "https://fidus-workspace-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class LilianProductionFixTest:
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
    
    def authenticate_admin(self, backend_url):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{backend_url}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication", True, f"Successfully authenticated as admin on {backend_url}")
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
    
    def verify_environment_difference(self):
        """Verify the difference between preview and production environments"""
        print("\n🔍 VERIFYING ENVIRONMENT DIFFERENCE...")
        print("-" * 50)
        
        # Check preview environment
        if self.authenticate_admin(PREVIEW_URL):
            try:
                response = self.session.get(f"{PREVIEW_URL}/admin/clients")
                if response.status_code == 200:
                    response_data = response.json()
                    clients = response_data.get('clients', []) if isinstance(response_data, dict) else response_data
                    
                    lilian_in_preview = any('lilian' in client.get('name', '').lower() for client in clients)
                    self.log_result("Lilian in Preview", lilian_in_preview, 
                                  f"Lilian {'found' if lilian_in_preview else 'not found'} in preview environment")
                else:
                    self.log_result("Preview Environment Check", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result("Preview Environment Check", False, f"Exception: {str(e)}")
        
        # Check production environment
        if self.authenticate_admin(PRODUCTION_URL):
            try:
                response = self.session.get(f"{PRODUCTION_URL}/admin/clients")
                if response.status_code == 200:
                    response_data = response.json()
                    clients = response_data.get('clients', []) if isinstance(response_data, dict) else response_data
                    
                    lilian_in_production = any('lilian' in client.get('name', '').lower() for client in clients)
                    self.log_result("Lilian in Production", lilian_in_production, 
                                  f"Lilian {'found' if lilian_in_production else 'not found'} in production environment")
                    
                    if not lilian_in_production:
                        self.log_result("Environment Difference Confirmed", True, 
                                      "Issue confirmed: Lilian exists in preview but not in production")
                else:
                    self.log_result("Production Environment Check", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result("Production Environment Check", False, f"Exception: {str(e)}")
    
    def create_lilian_prospect_in_production(self):
        """Create Lilian as a prospect in production environment"""
        try:
            if not self.authenticate_admin(PRODUCTION_URL):
                self.log_result("Create Lilian Prospect", False, "Authentication failed")
                return False
            
            # Create Lilian as prospect
            prospect_data = {
                "name": "Lilian Limon Leite",
                "email": "lilian.limon.leite@example.com",
                "phone": "+1-555-0123",
                "notes": "Created for production environment fix - Client Directory issue resolution"
            }
            
            response = self.session.post(f"{PRODUCTION_URL}/crm/prospects", json=prospect_data)
            
            if response.status_code == 200:
                result = response.json()
                self.lilian_prospect_id = result.get('id') or result.get('prospect_id')
                
                self.log_result("Create Lilian Prospect", True, 
                              f"Successfully created Lilian as prospect: {self.lilian_prospect_id}",
                              {"prospect_data": result})
                return True
            else:
                self.log_result("Create Lilian Prospect", False, 
                              f"Failed to create prospect: HTTP {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Create Lilian Prospect", False, f"Exception: {str(e)}")
            return False
    
    def move_lilian_to_won_stage(self):
        """Move Lilian to 'won' stage to enable conversion"""
        try:
            if not self.lilian_prospect_id:
                self.log_result("Move to Won Stage", False, "No prospect ID available")
                return False
            
            # Update prospect to 'won' stage
            update_data = {
                "stage": "won",
                "notes": "Moved to won stage for client conversion - Production fix"
            }
            
            response = self.session.put(f"{PRODUCTION_URL}/crm/prospects/{self.lilian_prospect_id}", json=update_data)
            
            if response.status_code == 200:
                self.log_result("Move to Won Stage", True, "Successfully moved Lilian to 'won' stage")
                return True
            else:
                self.log_result("Move to Won Stage", False, 
                              f"Failed to update stage: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Move to Won Stage", False, f"Exception: {str(e)}")
            return False
    
    def convert_lilian_to_client(self):
        """Convert Lilian from prospect to client in production"""
        try:
            if not self.lilian_prospect_id:
                self.log_result("Convert to Client", False, "No prospect ID available")
                return False
            
            # Convert prospect to client
            conversion_data = {
                "prospect_id": self.lilian_prospect_id,
                "send_agreement": False  # Don't send email during fix
            }
            
            response = self.session.post(f"{PRODUCTION_URL}/crm/prospects/{self.lilian_prospect_id}/convert", json=conversion_data)
            
            if response.status_code == 200:
                result = response.json()
                self.lilian_client_id = result.get('client_id')
                
                self.log_result("Convert to Client", True, 
                              f"Successfully converted Lilian to client: {self.lilian_client_id}",
                              {"conversion_result": result})
                return True
            else:
                self.log_result("Convert to Client", False, 
                              f"Conversion failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Convert to Client", False, f"Exception: {str(e)}")
            return False
    
    def verify_lilian_in_client_directory(self):
        """Verify Lilian now appears in the Client Directory"""
        try:
            # Wait a moment for database update
            time.sleep(3)
            
            response = self.session.get(f"{PRODUCTION_URL}/admin/clients")
            
            if response.status_code == 200:
                response_data = response.json()
                clients = response_data.get('clients', []) if isinstance(response_data, dict) else response_data
                
                # Look for Lilian in client list
                lilian_client = None
                for client in clients:
                    if 'lilian' in client.get('name', '').lower() or client.get('id') == self.lilian_client_id:
                        lilian_client = client
                        break
                
                if lilian_client:
                    self.log_result("Lilian in Client Directory", True, 
                                  f"SUCCESS: Lilian now appears in Client Directory as {lilian_client.get('name')} (ID: {lilian_client.get('id')})",
                                  {"client_data": lilian_client})
                    return True
                else:
                    self.log_result("Lilian in Client Directory", False, 
                                  "Lilian still not found in Client Directory after conversion",
                                  {"total_clients": len(clients), "client_names": [c.get('name') for c in clients]})
                    return False
            else:
                self.log_result("Verify Client Directory", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Verify Client Directory", False, f"Exception: {str(e)}")
            return False
    
    def test_frontend_client_directory_access(self):
        """Test that the frontend can access the client directory with Lilian"""
        try:
            # Test the exact endpoint the frontend uses
            response = self.session.get(f"{PRODUCTION_URL}/admin/clients")
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if response format matches what frontend expects
                if isinstance(response_data, dict) and 'clients' in response_data:
                    clients = response_data['clients']
                    total_clients = len(clients)
                    
                    # Look for Lilian specifically
                    lilian_visible = any('lilian' in client.get('name', '').lower() for client in clients)
                    
                    self.log_result("Frontend Client Directory Access", True, 
                                  f"Client directory accessible with {total_clients} clients, Lilian visible: {lilian_visible}")
                    
                    if lilian_visible:
                        self.log_result("Frontend Lilian Visibility", True, 
                                      "SUCCESS: Lilian is now visible to frontend Client Directory")
                    else:
                        self.log_result("Frontend Lilian Visibility", False, 
                                      "Lilian still not visible to frontend")
                else:
                    self.log_result("Frontend Response Format", False, 
                                  "Unexpected response format for frontend", {"response": response_data})
            else:
                self.log_result("Frontend Client Directory Access", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend Client Directory Access", False, f"Exception: {str(e)}")
    
    def run_production_fix(self):
        """Run the complete production fix process"""
        print("🚨 LILIAN PRODUCTION ENVIRONMENT FIX")
        print("=" * 60)
        print(f"Production URL: {PRODUCTION_URL}")
        print(f"Preview URL: {PREVIEW_URL}")
        print(f"Fix Time: {datetime.now().isoformat()}")
        print()
        print("OBJECTIVE: Create Lilian in production environment so she appears in Client Directory")
        print()
        
        # Step 1: Verify the environment difference
        self.verify_environment_difference()
        
        print("\n🔧 EXECUTING PRODUCTION FIX...")
        print("-" * 50)
        
        # Step 2: Create Lilian as prospect in production
        if self.create_lilian_prospect_in_production():
            # Step 3: Move to won stage
            if self.move_lilian_to_won_stage():
                # Step 4: Convert to client
                if self.convert_lilian_to_client():
                    # Step 5: Verify she appears in client directory
                    self.verify_lilian_in_client_directory()
                    # Step 6: Test frontend access
                    self.test_frontend_client_directory_access()
        
        # Generate fix summary
        self.generate_fix_summary()
        
        return True
    
    def generate_fix_summary(self):
        """Generate comprehensive fix summary"""
        print("\n" + "=" * 60)
        print("🚨 LILIAN PRODUCTION FIX SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Operations: {total_tests}")
        print(f"Successful: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Key results
        print("🎯 KEY RESULTS:")
        
        # Check if fix was successful
        lilian_created = any(result['success'] and 'Create Lilian Prospect' in result['test'] 
                           for result in self.test_results)
        lilian_converted = any(result['success'] and 'Convert to Client' in result['test'] 
                             for result in self.test_results)
        lilian_visible = any(result['success'] and 'Lilian in Client Directory' in result['test'] 
                           for result in self.test_results)
        frontend_access = any(result['success'] and 'Frontend Lilian Visibility' in result['test'] 
                            for result in self.test_results)
        
        if lilian_created:
            print("✅ Lilian successfully created as prospect in production")
        else:
            print("❌ Failed to create Lilian as prospect in production")
        
        if lilian_converted:
            print("✅ Lilian successfully converted to client in production")
        else:
            print("❌ Failed to convert Lilian to client in production")
        
        if lilian_visible:
            print("✅ Lilian now visible in production Client Directory")
        else:
            print("❌ Lilian still not visible in production Client Directory")
        
        if frontend_access:
            print("✅ Frontend can now access Lilian in Client Directory")
        else:
            print("❌ Frontend still cannot access Lilian in Client Directory")
        
        print()
        
        # Overall assessment
        print("🏆 OVERALL ASSESSMENT:")
        
        if lilian_visible and frontend_access:
            print("✅ PRODUCTION FIX SUCCESSFUL!")
            print("   - Lilian Limon Leite now appears in production Client Directory")
            print("   - User complaint resolved")
            print("   - Frontend can display Lilian alongside other clients")
            print("   - Production environment now matches preview environment")
        elif lilian_converted:
            print("⚠️  PARTIAL SUCCESS")
            print("   - Lilian converted to client but visibility issues remain")
            print("   - May need frontend cache refresh or additional debugging")
        else:
            print("❌ PRODUCTION FIX FAILED")
            print("   - Unable to create or convert Lilian in production")
            print("   - User complaint remains unresolved")
            print("   - Additional investigation required")
        
        print("\n" + "=" * 60)

def main():
    """Main fix execution"""
    fixer = LilianProductionFixTest()
    success = fixer.run_production_fix()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()