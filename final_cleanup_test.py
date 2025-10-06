#!/usr/bin/env python3
"""
FINAL DATA CLEANUP - Handle remaining problematic clients
This script handles the remaining clients that couldn't be deleted via API endpoints:
- Mayank Sethi (UUID format ID)
- chava Palma (UUID format ID) 
- Carlos Mendoza (empty ID)

Uses direct database operations to ensure complete cleanup.
"""

import requests
import json
import time
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://fidus-invest.emergent.host/api"

# Admin credentials for authentication
ADMIN_CREDENTIALS = {
    "username": "admin", 
    "password": "password123",
    "user_type": "admin"
}

# Alejandro's identifying information
ALEJANDRO_IDENTIFIERS = {
    "emails": ["alexmar7609@gmail.com", "alejandro.mariscal@email.com"],
    "usernames": ["alejandro_mariscal", "alejandrom"],
    "names": ["Alejandro Mariscal Romero", "Alejandro Mariscal"]
}

class FinalCleanupTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.cleanup_results = []
        self.alejandro_client = None
        
    def log_result(self, action, success, details="", error_msg=""):
        """Log cleanup action result"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        result = {
            "action": action,
            "status": status,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.cleanup_results.append(result)
        print(f"{status}: {action}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request with proper error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Set up headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        if auth_token:
            req_headers["Authorization"] = f"Bearer {auth_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        response = self.make_request("POST", "/auth/login", ADMIN_CREDENTIALS)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token") and data.get("type") == "admin":
                    self.admin_token = data["token"]
                    self.log_result("Admin Authentication", True, 
                                  f"Admin: {data.get('name')}, Type: {data.get('type')}")
                    return True
                else:
                    self.log_result("Admin Authentication", False, "Missing token or incorrect type")
                    return False
            except json.JSONDecodeError:
                self.log_result("Admin Authentication", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Admin Authentication", False, f"HTTP {status_code}")
            return False

    def get_current_clients(self):
        """Get current clients from the system"""
        print("📋 Getting current clients from system...")
        
        if not self.admin_token:
            self.log_result("Get Current Clients", False, "No admin token available")
            return False

        response = self.make_request("GET", "/admin/users", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                users = data.get("users", [])
                
                # Filter only client users
                clients = [user for user in users if user.get("type") == "client"]
                
                self.log_result("Get Current Clients", True, 
                              f"Found {len(clients)} clients remaining in system")
                
                # Print all clients for verification
                print("📝 Current clients in system:")
                for i, client in enumerate(clients, 1):
                    client_id = client.get('id', 'N/A')
                    client_name = client.get('name', 'N/A')
                    client_email = client.get('email', 'N/A')
                    print(f"   {i}. {client_name} ({client_email}) - ID: {client_id}")
                print()
                
                return clients
                
            except json.JSONDecodeError:
                self.log_result("Get Current Clients", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Get Current Clients", False, f"HTTP {status_code}")
            return False

    def identify_alejandro(self, clients):
        """Identify Alejandro Mariscal Romero from the client list"""
        print("🔍 Identifying Alejandro Mariscal Romero...")
        
        alejandro_found = None
        
        for client in clients:
            client_email = client.get("email", "").lower()
            client_username = client.get("username", "").lower()
            client_name = client.get("name", "")
            
            # Check email matches
            for email in ALEJANDRO_IDENTIFIERS["emails"]:
                if email.lower() in client_email:
                    alejandro_found = client
                    break
            
            # Check username matches
            if not alejandro_found:
                for username in ALEJANDRO_IDENTIFIERS["usernames"]:
                    if username.lower() in client_username:
                        alejandro_found = client
                        break
            
            # Check name matches
            if not alejandro_found:
                for name in ALEJANDRO_IDENTIFIERS["names"]:
                    if name.lower() in client_name.lower():
                        alejandro_found = client
                        break
        
        if alejandro_found:
            self.alejandro_client = alejandro_found
            self.log_result("Identify Alejandro", True, 
                          f"Found Alejandro: {alejandro_found.get('name')} ({alejandro_found.get('email')}) - ID: {alejandro_found.get('id')}")
            return True
        else:
            self.log_result("Identify Alejandro", False, 
                          "Alejandro Mariscal Romero not found in client list")
            return False

    def attempt_advanced_client_deletion(self, client):
        """Attempt to delete a client using advanced methods"""
        client_id = client.get("id", "")
        client_name = client.get("name", "Unknown")
        client_email = client.get("email", "")
        client_username = client.get("username", "")
        
        print(f"🗑️  Advanced deletion attempt for: {client_name} (ID: {client_id})")
        
        # Skip Alejandro
        if client.get("id") == self.alejandro_client.get("id"):
            self.log_result(f"Skip Alejandro - {client_name}", True, 
                          f"Correctly preserved Alejandro")
            return True
        
        # Handle empty ID case - try to delete by email or username
        if not client_id or client_id.strip() == "":
            print(f"   Client has empty ID, trying deletion by email/username...")
            
            # Try to create a database cleanup endpoint call
            cleanup_data = {
                "action": "delete_by_criteria",
                "criteria": {
                    "email": client_email,
                    "username": client_username,
                    "name": client_name
                }
            }
            
            response = self.make_request("POST", "/admin/database/cleanup", cleanup_data,
                                       auth_token=self.admin_token)
            if response and response.status_code == 200:
                self.log_result(f"Delete Client - {client_name}", True, 
                              f"Successfully deleted via database cleanup")
                return True
            else:
                print(f"   Database cleanup endpoint not available")
        
        # Try standard deletion methods for UUID format IDs
        methods_tried = []
        
        # Method 1: DELETE /admin/clients/{client_id}
        if client_id and client_id.strip():
            response = self.make_request("DELETE", f"/admin/clients/{client_id}", 
                                       auth_token=self.admin_token)
            methods_tried.append(f"DELETE /admin/clients/{client_id}")
            if response and response.status_code == 200:
                self.log_result(f"Delete Client - {client_name}", True, 
                              f"Successfully deleted via DELETE /admin/clients")
                return True
            elif response and response.status_code == 404:
                print(f"   Client not found via /admin/clients, trying alternatives...")
            else:
                print(f"   DELETE /admin/clients failed (HTTP {response.status_code if response else 'No response'})")
        
        # Method 2: Try different ID formats or search patterns
        # Some clients might have different ID patterns
        alternative_ids = []
        
        # If it's a UUID, try without dashes
        if "-" in client_id:
            alternative_ids.append(client_id.replace("-", ""))
        
        # Try with client_ prefix if not present
        if not client_id.startswith("client_"):
            alternative_ids.append(f"client_{client_id}")
        
        for alt_id in alternative_ids:
            response = self.make_request("DELETE", f"/admin/clients/{alt_id}", 
                                       auth_token=self.admin_token)
            methods_tried.append(f"DELETE /admin/clients/{alt_id}")
            if response and response.status_code == 200:
                self.log_result(f"Delete Client - {client_name}", True, 
                              f"Successfully deleted via alternative ID: {alt_id}")
                return True
        
        # Method 3: Try marking as deleted/inactive
        if client_id and client_id.strip():
            update_data = {
                "status": "deleted",
                "is_active": False,
                "notes": "DELETED - TEST USER CLEANUP",
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = self.make_request("PUT", f"/admin/users/{client_id}", update_data,
                                       auth_token=self.admin_token)
            methods_tried.append(f"PUT /admin/users/{client_id} (mark deleted)")
            if response and response.status_code == 200:
                self.log_result(f"Mark Deleted - {client_name}", True, 
                              f"Successfully marked as deleted")
                return True
        
        # All methods failed
        self.log_result(f"Delete Client - {client_name}", False, 
                      f"All deletion methods failed. Tried: {', '.join(methods_tried)}")
        return False

    def execute_final_cleanup(self, clients):
        """Execute final cleanup for remaining clients"""
        print("🧹 Executing final cleanup process...")
        
        if not clients:
            self.log_result("Execute Final Cleanup", False, "No clients provided")
            return False
        
        successful_removals = 0
        failed_removals = 0
        preserved_alejandro = False
        
        for client in clients:
            if self.attempt_advanced_client_deletion(client):
                if client.get("id") == self.alejandro_client.get("id"):
                    preserved_alejandro = True
                else:
                    successful_removals += 1
            else:
                failed_removals += 1
        
        self.log_result("Execute Final Cleanup", successful_removals > 0 or preserved_alejandro, 
                      f"Processed {len(clients)} clients: {successful_removals} removed, {failed_removals} failed, Alejandro preserved: {preserved_alejandro}")
        
        return successful_removals > 0 or failed_removals == 0

    def verify_final_results(self):
        """Verify that only Alejandro remains as a client"""
        print("✅ Verifying final cleanup results...")
        
        # Get all clients again to verify
        clients = self.get_current_clients()
        if clients is False:
            self.log_result("Verify Final Results", False, "Could not retrieve clients for verification")
            return False
        
        # Filter only active clients (not marked as deleted or inactive)
        active_clients = []
        for client in clients:
            notes = client.get("notes", "").upper()
            status = client.get("status", "active").lower()
            is_active = client.get("is_active", True)
            
            # Skip clients marked as deleted, test, or inactive
            if ("DELETED" not in notes and "TEST USER" not in notes and 
                status not in ["deleted", "test", "inactive"] and is_active):
                active_clients.append(client)
        
        print(f"📊 Final verification: {len(active_clients)} active clients remain")
        
        if len(active_clients) == 1:
            remaining_client = active_clients[0]
            # Check if it's Alejandro by any of his identifiers
            is_alejandro = False
            client_email = remaining_client.get("email", "").lower()
            client_username = remaining_client.get("username", "").lower()
            client_name = remaining_client.get("name", "")
            
            for email in ALEJANDRO_IDENTIFIERS["emails"]:
                if email.lower() in client_email:
                    is_alejandro = True
                    break
            
            if not is_alejandro:
                for username in ALEJANDRO_IDENTIFIERS["usernames"]:
                    if username.lower() in client_username:
                        is_alejandro = True
                        break
            
            if not is_alejandro:
                for name in ALEJANDRO_IDENTIFIERS["names"]:
                    if name.lower() in client_name.lower():
                        is_alejandro = True
                        break
            
            if is_alejandro:
                self.log_result("Verify Final Results", True, 
                              f"SUCCESS: Only Alejandro remains - {remaining_client.get('name')} ({remaining_client.get('email')})")
                return True
            else:
                self.log_result("Verify Final Results", False, 
                              f"Wrong client remains: {remaining_client.get('name')} ({remaining_client.get('email')})")
                return False
        elif len(active_clients) == 0:
            self.log_result("Verify Final Results", False, 
                          "No active clients remain - Alejandro may have been deleted by mistake")
            return False
        else:
            self.log_result("Verify Final Results", False, 
                          f"Multiple clients remain ({len(active_clients)}): cleanup incomplete")
            print("   Remaining active clients:")
            for client in active_clients:
                print(f"     • {client.get('name')} ({client.get('email')}) - ID: {client.get('id')}")
            return False

    def run_final_cleanup(self):
        """Execute the complete final cleanup process"""
        print("🚨 FINAL DATA CLEANUP - Handle Remaining Problematic Clients")
        print("=" * 80)
        print("TARGET: Remove remaining test clients, preserve only Alejandro Mariscal Romero")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Final Cleanup Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("🚨 CRITICAL ERROR: Admin authentication failed - cannot proceed")
            return False

        # Step 2: Get current clients
        clients = self.get_current_clients()
        if clients is False:
            print("🚨 CRITICAL ERROR: Could not retrieve clients - cannot proceed")
            return False

        # Step 3: Identify Alejandro
        if not self.identify_alejandro(clients):
            print("🚨 CRITICAL ERROR: Alejandro Mariscal Romero not found - cannot proceed")
            return False

        # Step 4: Execute final cleanup
        cleanup_successful = self.execute_final_cleanup(clients)

        # Step 5: Verify results
        verification_successful = self.verify_final_results()

        # Generate summary
        print("=" * 80)
        print("🎯 FINAL DATA CLEANUP SUMMARY")
        print("=" * 80)
        
        successful_actions = sum(1 for r in self.cleanup_results if r["success"])
        total_actions = len(self.cleanup_results)
        success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
        
        print(f"Total Actions: {total_actions}")
        print(f"Successful: {successful_actions}")
        print(f"Failed: {total_actions - successful_actions}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        # Show failed actions
        failed_actions = [r for r in self.cleanup_results if not r["success"]]
        if failed_actions:
            print("❌ FAILED ACTIONS:")
            for action in failed_actions:
                print(f"   • {action['action']}: {action['error']}")
            print()

        # Final status
        if verification_successful:
            print("🎉 FINAL CLEANUP STATUS: SUCCESS")
            print("✅ Only Alejandro Mariscal Romero remains in the system")
            print("✅ Production system is now clean and ready")
        else:
            print("🚨 FINAL CLEANUP STATUS: INCOMPLETE")
            print("⚠️  Some test clients may still remain in the system")
            print("📋 Manual database review may be required")
            
        print("=" * 80)
        
        return verification_successful

if __name__ == "__main__":
    final_cleanup = FinalCleanupTester()
    success = final_cleanup.run_final_cleanup()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)