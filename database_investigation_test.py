#!/usr/bin/env python3
"""
Database Investigation: Check what client IDs and data exist for Alejandro
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class DatabaseInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
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
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_payload = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        response = self.make_request("POST", "/auth/login", login_payload)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get("token"):
                    self.admin_token = data["token"]
                    print(f"✅ Admin authenticated: {data.get('name')}")
                    return True
                else:
                    print("❌ Admin authentication failed: No token")
                    return False
            except json.JSONDecodeError:
                print("❌ Admin authentication failed: Invalid JSON")
                return False
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Admin authentication failed: HTTP {status_code}")
            return False

    def investigate_database(self):
        """Investigate what's in the database"""
        print("\n🔍 DATABASE INVESTIGATION")
        print("=" * 60)
        
        if not self.admin_token:
            print("❌ No admin token available")
            return

        # 1. Check all users
        print("\n1. ALL USERS IN DATABASE:")
        response = self.make_request("GET", "/admin/users", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                users = data.get("users", [])
                print(f"   Found {len(users)} users:")
                for user in users:
                    if "alejandro" in user.get("username", "").lower() or "alejandro" in user.get("name", "").lower():
                        print(f"   🎯 ALEJANDRO: ID={user.get('id')}, Username={user.get('username')}, Name={user.get('name')}, Email={user.get('email')}")
                    else:
                        print(f"   • ID={user.get('id')}, Username={user.get('username')}, Name={user.get('name')}")
            except json.JSONDecodeError:
                print("   ❌ Invalid JSON response")
        else:
            print(f"   ❌ Failed to get users: HTTP {response.status_code if response else 'No response'}")

        # 2. Check ready for investment
        print("\n2. READY FOR INVESTMENT:")
        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                print(f"   Found {len(ready_clients)} ready clients:")
                for client in ready_clients:
                    print(f"   • Client ID: {client.get('client_id')}")
                    print(f"     Name: {client.get('name')}")
                    print(f"     Email: {client.get('email')}")
                    print(f"     Username: {client.get('username')}")
                    print()
            except json.JSONDecodeError:
                print("   ❌ Invalid JSON response")
        else:
            print(f"   ❌ Failed to get ready clients: HTTP {response.status_code if response else 'No response'}")

        # 3. Check investments for both possible client IDs
        print("\n3. INVESTMENTS CHECK:")
        client_ids_to_check = ["client_alejandro", "client_alejandro_mariscal"]
        
        for client_id in client_ids_to_check:
            print(f"\n   Checking investments for {client_id}:")
            
            # Try the client-specific endpoint
            response = self.make_request("GET", f"/clients/{client_id}/investments", auth_token=self.admin_token)
            if response:
                print(f"   /clients/{client_id}/investments: HTTP {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        investments = data.get("investments", [])
                        print(f"     Found {len(investments)} investments")
                        for inv in investments:
                            print(f"     • {inv.get('fund_code')}: ${inv.get('principal_amount', 0):,.2f}")
                    except json.JSONDecodeError:
                        print("     ❌ Invalid JSON response")
            
            # Try the general investment endpoint
            response = self.make_request("GET", f"/investments/client/{client_id}", auth_token=self.admin_token)
            if response:
                print(f"   /investments/client/{client_id}: HTTP {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        investments = data.get("investments", [])
                        print(f"     Found {len(investments)} investments")
                        for inv in investments:
                            print(f"     • {inv.get('fund_code')}: ${inv.get('principal_amount', 0):,.2f}")
                    except json.JSONDecodeError:
                        print("     ❌ Invalid JSON response")

        # 4. Check MT5 accounts for both possible client IDs
        print("\n4. MT5 ACCOUNTS CHECK:")
        for client_id in client_ids_to_check:
            print(f"\n   Checking MT5 accounts for {client_id}:")
            response = self.make_request("GET", f"/mt5/accounts/{client_id}", auth_token=self.admin_token)
            if response:
                print(f"   HTTP {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        accounts = data.get("accounts", [])
                        print(f"     Found {len(accounts)} MT5 accounts")
                        for acc in accounts:
                            print(f"     • Account: {acc.get('mt5_account_number')}, Balance: ${acc.get('balance', 0):,.2f}, Broker: {acc.get('broker_name')}")
                    except json.JSONDecodeError:
                        print("     ❌ Invalid JSON response")

        # 5. Check admin overview
        print("\n5. ADMIN OVERVIEW:")
        response = self.make_request("GET", "/investments/admin/overview", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                print(f"   Total AUM: ${data.get('total_aum', 0):,.2f}")
                print(f"   Total Investments: {data.get('total_investments', 0)}")
                print(f"   Total Clients: {data.get('total_clients', 0)}")
            except json.JSONDecodeError:
                print("   ❌ Invalid JSON response")
        else:
            print(f"   ❌ Failed to get admin overview: HTTP {response.status_code if response else 'No response'}")

    def run_investigation(self):
        """Run the database investigation"""
        print("🚀 DATABASE INVESTIGATION: Alejandro Mariscal Setup")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)

        # Authenticate first
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Admin authentication failed. Cannot proceed.")
            return

        # Run investigation
        self.investigate_database()

        print("\n" + "=" * 80)
        print("🎯 INVESTIGATION COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    investigator = DatabaseInvestigator()
    investigator.run_investigation()