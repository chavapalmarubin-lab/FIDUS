#!/usr/bin/env python3
"""
STATUS-BASED CLEANUP - Mark remaining test clients as inactive
Since direct deletion doesn't work for UUID format IDs, this script will:
1. Mark all remaining test clients as "inactive" 
2. Preserve only Alejandro Mariscal Romero as "active"
3. Verify final results

This effectively removes test clients from active use while preserving data integrity.
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

class StatusCleanupTester:
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
                              f"Found {len(clients)} clients in system")
                
                # Print all clients for verification
                print("📝 Current clients in system:")
                for i, client in enumerate(clients, 1):
                    client_id = client.get('id', 'N/A')
                    client_name = client.get('name', 'N/A')
                    client_email = client.get('email', 'N/A')
                    client_status = client.get('status', 'active')
                    print(f"   {i}. {client_name} ({client_email}) - ID: {client_id} - Status: {client_status}")
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

    def update_client_status(self, client, new_status):
        """Update a client's status using the status endpoint"""
        client_id = client.get("id", "")
        client_name = client.get("name", "Unknown")
        
        print(f"📝 Updating status for: {client_name} (ID: {client_id}) to '{new_status}'")
        
        # Skip clients with empty IDs
        if not client_id or client_id.strip() == "":
            self.log_result(f"Update Status - {client_name}", False, 
                          f"Client has empty ID - cannot update status")
            return False
        
        # Prepare status update data
        status_data = {"status": new_status}
        
        # Try the status update endpoint
        response = self.make_request("PUT", f"/admin/clients/{client_id}/status", status_data,
                                   auth_token=self.admin_token)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    self.log_result(f"Update Status - {client_name}", True, 
                                  f"Successfully updated status to '{new_status}'")
                    return True
                else:
                    self.log_result(f"Update Status - {client_name}", False, 
                                  f"Status update response indicates failure: {data}")
                    return False
            except json.JSONDecodeError:
                # If no JSON response but HTTP 200, assume success
                self.log_result(f"Update Status - {client_name}", True, 
                              f"Status updated to '{new_status}' (HTTP 200)")
                return True
        else:
            status_code = response.status_code if response else "No response"
            error_msg = ""
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Unknown error")
                except:
                    error_msg = f"HTTP {status_code}"
            
            self.log_result(f"Update Status - {client_name}", False, 
                          f"Status update failed: {error_msg}")
            return False

    def execute_status_cleanup(self, clients):
        """Execute status-based cleanup for all clients"""
        print("🧹 Executing status-based cleanup process...")
        
        if not clients:
            self.log_result("Execute Status Cleanup", False, "No clients provided")
            return False
        
        successful_updates = 0
        failed_updates = 0
        alejandro_preserved = False
        
        for client in clients:
            client_id = client.get("id")
            client_name = client.get("name", "Unknown")
            
            # Handle Alejandro - ensure he's active
            if client_id == self.alejandro_client.get("id"):
                if self.update_client_status(client, "active"):
                    alejandro_preserved = True
                    print(f"   ✅ Alejandro preserved as active")
                else:
                    print(f"   ⚠️  Failed to ensure Alejandro is active")
            else:
                # Mark all other clients as inactive
                if self.update_client_status(client, "inactive"):
                    successful_updates += 1
                    print(f"   ✅ {client_name} marked as inactive")
                else:
                    failed_updates += 1
                    print(f"   ❌ Failed to mark {client_name} as inactive")
        
        self.log_result("Execute Status Cleanup", successful_updates > 0 or alejandro_preserved, 
                      f"Processed {len(clients)} clients: {successful_updates} marked inactive, {failed_updates} failed, Alejandro preserved: {alejandro_preserved}")
        
        return successful_updates > 0 or failed_updates == 0

    def verify_status_cleanup(self):
        """Verify that only Alejandro is active, others are inactive"""
        print("✅ Verifying status-based cleanup results...")
        
        # Get all clients again to verify
        clients = self.get_current_clients()
        if clients is False:
            self.log_result("Verify Status Cleanup", False, "Could not retrieve clients for verification")
            return False
        
        # Filter only active clients
        active_clients = []
        inactive_clients = []
        
        for client in clients:
            status = client.get("status", "active").lower()
            if status == "active":
                active_clients.append(client)
            else:
                inactive_clients.append(client)
        
        print(f"📊 Status verification: {len(active_clients)} active, {len(inactive_clients)} inactive clients")
        
        if len(active_clients) == 1:
            remaining_active = active_clients[0]
            # Check if it's Alejandro by any of his identifiers
            is_alejandro = False
            client_email = remaining_active.get("email", "").lower()
            client_username = remaining_active.get("username", "").lower()
            client_name = remaining_active.get("name", "")
            
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
                self.log_result("Verify Status Cleanup", True, 
                              f"SUCCESS: Only Alejandro is active - {remaining_active.get('name')} ({remaining_active.get('email')}). {len(inactive_clients)} clients marked inactive.")
                return True
            else:
                self.log_result("Verify Status Cleanup", False, 
                              f"Wrong client is active: {remaining_active.get('name')} ({remaining_active.get('email')})")
                return False
        elif len(active_clients) == 0:
            self.log_result("Verify Status Cleanup", False, 
                          "No active clients remain - Alejandro may have been marked inactive by mistake")
            return False
        else:
            self.log_result("Verify Status Cleanup", False, 
                          f"Multiple clients are still active ({len(active_clients)}): cleanup incomplete")
            print("   Remaining active clients:")
            for client in active_clients:
                print(f"     • {client.get('name')} ({client.get('email')}) - ID: {client.get('id')}")
            return False

    def run_status_cleanup(self):
        """Execute the complete status-based cleanup process"""
        print("🚨 STATUS-BASED CLEANUP - Mark Test Clients as Inactive")
        print("=" * 80)
        print("STRATEGY: Mark all test clients as 'inactive', keep only Alejandro as 'active'")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Status Cleanup Started: {datetime.now(timezone.utc).isoformat()}")
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

        # Step 4: Execute status cleanup
        cleanup_successful = self.execute_status_cleanup(clients)

        # Step 5: Verify results
        verification_successful = self.verify_status_cleanup()

        # Generate summary
        print("=" * 80)
        print("🎯 STATUS-BASED CLEANUP SUMMARY")
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
            print("🎉 STATUS CLEANUP: SUCCESS")
            print("✅ Only Alejandro Mariscal Romero is active")
            print("✅ All test clients marked as inactive")
            print("✅ Production system is now clean and ready")
        else:
            print("🚨 STATUS CLEANUP: INCOMPLETE")
            print("⚠️  Some test clients may still be active")
            print("📋 Manual review may be required")
            
        print("=" * 80)
        
        return verification_successful

if __name__ == "__main__":
    status_cleanup = StatusCleanupTester()
    success = status_cleanup.run_status_cleanup()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)