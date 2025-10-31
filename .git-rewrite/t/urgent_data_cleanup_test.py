#!/usr/bin/env python3
"""
URGENT DATA CLEANUP TASK - FIDUS Production Client Management
Execute immediate cleanup to remove ALL test clients except Alejandro Mariscal Romero

CRITICAL REQUIREMENT: Delete/remove ALL clients except Alejandro Mariscal Romero

Task Steps:
1. Get All Clients: GET `/api/admin/users` - identify all clients in system
2. Identify Alejandro: Find client with email "alexmar7609@gmail.com" or "alejandro.mariscal@email.com" 
3. Delete Test Clients: Remove/deactivate ALL other clients:
   - Gerardo Briones
   - Maria Rodriguez  
   - Salvador Palma
   - Javier Gonzalez
   - Jorge Gonzalez
   - Test User Phase2

Deletion Methods:
- Try DELETE endpoint if available: DELETE `/api/admin/users/{user_id}`
- Or mark as inactive: PUT `/api/admin/users/{user_id}` with `{"is_active": false}`
- Or mark as test: PUT `/api/admin/users/{user_id}` with `{"notes": "TEST USER - DO NOT USE"}`

Context: Production system has 7 test clients that must be removed. Only Alejandro Mariscal Romero is the real client.
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

# Test clients to be removed
TEST_CLIENTS_TO_REMOVE = [
    "Gerardo Briones",
    "Maria Rodriguez", 
    "Salvador Palma",
    "Javier Gonzalez",
    "Jorge Gonzalez",
    "Test User Phase2"
]

class UrgentDataCleanupTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.cleanup_results = []
        self.alejandro_client = None
        self.clients_to_remove = []
        
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

    def get_all_clients(self):
        """Get all clients from the system"""
        print("📋 Getting all clients from system...")
        
        if not self.admin_token:
            self.log_result("Get All Clients", False, "No admin token available")
            return False

        response = self.make_request("GET", "/admin/users", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                users = data.get("users", [])
                
                # Filter only client users
                clients = [user for user in users if user.get("type") == "client"]
                
                self.log_result("Get All Clients", True, 
                              f"Found {len(clients)} clients in system (Total users: {len(users)})")
                
                # Print all clients for verification
                print("📝 Current clients in system:")
                for i, client in enumerate(clients, 1):
                    print(f"   {i}. {client.get('name', 'N/A')} ({client.get('email', 'N/A')}) - ID: {client.get('id', 'N/A')}")
                print()
                
                return clients
                
            except json.JSONDecodeError:
                self.log_result("Get All Clients", False, "Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            self.log_result("Get All Clients", False, f"HTTP {status_code}")
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

    def identify_clients_to_remove(self, clients):
        """Identify all clients that should be removed (everyone except Alejandro)"""
        print("🎯 Identifying clients to remove...")
        
        if not self.alejandro_client:
            self.log_result("Identify Clients to Remove", False, "Alejandro not identified")
            return False
        
        alejandro_id = self.alejandro_client.get("id")
        
        # All clients except Alejandro should be removed
        self.clients_to_remove = [client for client in clients if client.get("id") != alejandro_id]
        
        self.log_result("Identify Clients to Remove", True, 
                      f"Identified {len(self.clients_to_remove)} clients for removal")
        
        print("🗑️  Clients marked for removal:")
        for i, client in enumerate(self.clients_to_remove, 1):
            print(f"   {i}. {client.get('name', 'N/A')} ({client.get('email', 'N/A')}) - ID: {client.get('id', 'N/A')}")
        print()
        
        return True

    def attempt_client_deletion(self, client):
        """Attempt to delete a client using various methods"""
        client_id = client.get("id")
        client_name = client.get("name", "Unknown")
        
        print(f"🗑️  Attempting to delete client: {client_name} (ID: {client_id})")
        
        # Skip clients with empty IDs
        if not client_id or client_id.strip() == "":
            self.log_result(f"Delete Client - {client_name}", False, 
                          f"Client has empty ID - cannot delete")
            return False
        
        # Method 1: Try DELETE endpoint for clients
        response = self.make_request("DELETE", f"/admin/clients/{client_id}", 
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    self.log_result(f"Delete Client - {client_name}", True, 
                                  f"Successfully deleted via DELETE /admin/clients endpoint")
                    return True
                else:
                    print(f"   DELETE response indicates failure: {data}")
            except json.JSONDecodeError:
                print(f"   DELETE succeeded but invalid JSON response")
                self.log_result(f"Delete Client - {client_name}", True, 
                              f"Successfully deleted (HTTP 200)")
                return True
        elif response and response.status_code == 404:
            print(f"   Client not found (HTTP 404), may already be deleted")
            self.log_result(f"Delete Client - {client_name}", True, 
                          f"Client not found - may already be deleted")
            return True
        else:
            status_code = response.status_code if response else "No response"
            print(f"   DELETE failed (HTTP {status_code}), trying alternative methods...")
        
        # Method 2: Try DELETE endpoint for users
        response = self.make_request("DELETE", f"/admin/users/{client_id}", 
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            self.log_result(f"Delete Client - {client_name}", True, 
                          f"Successfully deleted via DELETE /admin/users endpoint")
            return True
        elif response and response.status_code == 404:
            print(f"   User DELETE endpoint not found, trying update methods...")
        else:
            print(f"   User DELETE failed (HTTP {response.status_code if response else 'No response'}), trying update methods...")
        
        # Method 3: Try marking as inactive
        update_data = {"is_active": False, "status": "inactive"}
        response = self.make_request("PUT", f"/admin/users/{client_id}", update_data,
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            self.log_result(f"Deactivate Client - {client_name}", True, 
                          f"Successfully marked as inactive")
            return True
        elif response and response.status_code == 404:
            print(f"   PUT endpoint not found, trying final method...")
        else:
            print(f"   Deactivation failed (HTTP {response.status_code if response else 'No response'}), trying final method...")
        
        # Method 4: Try marking with test notes
        update_data = {"notes": "TEST USER - DO NOT USE - MARKED FOR DELETION", "status": "test"}
        response = self.make_request("PUT", f"/admin/users/{client_id}", update_data,
                                   auth_token=self.admin_token)
        if response and response.status_code == 200:
            self.log_result(f"Mark Test Client - {client_name}", True, 
                          f"Successfully marked as test user")
            return True
        else:
            self.log_result(f"Delete Client - {client_name}", False, 
                          f"All deletion methods failed")
            return False

    def execute_client_cleanup(self):
        """Execute the client cleanup process"""
        print("🧹 Executing client cleanup process...")
        
        if not self.clients_to_remove:
            self.log_result("Execute Cleanup", False, "No clients identified for removal")
            return False
        
        successful_removals = 0
        failed_removals = 0
        
        for client in self.clients_to_remove:
            if self.attempt_client_deletion(client):
                successful_removals += 1
            else:
                failed_removals += 1
        
        self.log_result("Execute Client Cleanup", successful_removals > 0, 
                      f"Removed {successful_removals} clients, {failed_removals} failed")
        
        return successful_removals > 0

    def verify_cleanup_results(self):
        """Verify that only Alejandro remains as a client"""
        print("✅ Verifying cleanup results...")
        
        # Get all clients again to verify
        clients = self.get_all_clients()
        if not clients:
            self.log_result("Verify Cleanup", False, "Could not retrieve clients for verification")
            return False
        
        # Filter only active clients (not marked as test or inactive)
        active_clients = []
        for client in clients:
            notes = client.get("notes", "").upper()
            status = client.get("status", "active").lower()
            is_active = client.get("is_active", True)
            
            # Skip clients marked as test or inactive
            if "TEST USER" not in notes and status != "test" and status != "inactive" and is_active:
                active_clients.append(client)
        
        if len(active_clients) == 1:
            remaining_client = active_clients[0]
            if remaining_client.get("id") == self.alejandro_client.get("id"):
                self.log_result("Verify Cleanup", True, 
                              f"SUCCESS: Only Alejandro remains - {remaining_client.get('name')} ({remaining_client.get('email')})")
                return True
            else:
                self.log_result("Verify Cleanup", False, 
                              f"Wrong client remains: {remaining_client.get('name')} ({remaining_client.get('email')})")
                return False
        elif len(active_clients) == 0:
            self.log_result("Verify Cleanup", False, 
                          "No active clients remain - Alejandro may have been deleted by mistake")
            return False
        else:
            self.log_result("Verify Cleanup", False, 
                          f"Multiple clients remain ({len(active_clients)}): cleanup incomplete")
            print("   Remaining active clients:")
            for client in active_clients:
                print(f"     • {client.get('name')} ({client.get('email')})")
            return False

    def run_urgent_cleanup(self):
        """Execute the complete urgent data cleanup process"""
        print("🚨 URGENT DATA CLEANUP TASK - FIDUS Production Client Management")
        print("=" * 80)
        print("CRITICAL REQUIREMENT: Delete/remove ALL clients except Alejandro Mariscal Romero")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Cleanup Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("🚨 CRITICAL ERROR: Admin authentication failed - cannot proceed")
            return False

        # Step 2: Get all clients
        clients = self.get_all_clients()
        if not clients:
            print("🚨 CRITICAL ERROR: Could not retrieve clients - cannot proceed")
            return False

        # Step 3: Identify Alejandro
        if not self.identify_alejandro(clients):
            print("🚨 CRITICAL ERROR: Alejandro Mariscal Romero not found - cannot proceed")
            return False

        # Step 4: Identify clients to remove
        if not self.identify_clients_to_remove(clients):
            print("🚨 CRITICAL ERROR: Could not identify clients for removal - cannot proceed")
            return False

        # Step 5: Execute cleanup
        if not self.execute_client_cleanup():
            print("⚠️  WARNING: Client cleanup had issues - verifying results")

        # Step 6: Verify results
        cleanup_successful = self.verify_cleanup_results()

        # Generate summary
        print("=" * 80)
        print("🎯 URGENT DATA CLEANUP SUMMARY")
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
        if cleanup_successful:
            print("🎉 CLEANUP STATUS: SUCCESS - Only Alejandro Mariscal Romero remains")
            print("✅ Production system is now clean and ready")
        else:
            print("🚨 CLEANUP STATUS: FAILED - Manual intervention required")
            print("❌ Production system still contains test clients")
            
        print("=" * 80)
        
        return cleanup_successful

if __name__ == "__main__":
    cleanup_tester = UrgentDataCleanupTester()
    success = cleanup_tester.run_urgent_cleanup()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)