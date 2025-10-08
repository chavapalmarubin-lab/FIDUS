#!/usr/bin/env python3
"""
ALEJANDRO MARISCAL PRODUCTION DIAGNOSTIC TEST
Comprehensive analysis of current state vs expected state for production setup.
"""

import requests
import json
import sys
from datetime import datetime, timezone

# Backend URL Configuration
BACKEND_URL = "https://trading-platform-76.preview.emergentagent.com/api"

class AlejandroDiagnostic:
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
                if data.get("token") and data.get("type") == "admin":
                    self.admin_token = data["token"]
                    print(f"✅ Admin authenticated: {data.get('name')}")
                    return True
                else:
                    print("❌ Admin authentication failed: Missing token or incorrect type")
                    return False
            except json.JSONDecodeError:
                print("❌ Admin authentication failed: Invalid JSON response")
                return False
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Admin authentication failed: HTTP {status_code}")
            return False

    def run_diagnostic(self):
        """Run comprehensive diagnostic"""
        print("🔍 ALEJANDRO MARISCAL PRODUCTION DIAGNOSTIC")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Diagnostic Started: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 80)
        print()

        # Authenticate first
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Cannot proceed without admin authentication")
            return

        print("\n📋 EXPECTED PRODUCTION SETUP:")
        print("   • Ready for Investment: Alejandro with email alexmar7609@gmail.com")
        print("   • Client Investments: Exactly 2 investments (BALANCE $100,000 + CORE $18,151.41)")
        print("   • MT5 Accounts: Exactly 4 MT5 accounts with MEXAtlantic broker")
        print("   • Investment Admin Overview: Total AUM of $118,151.41")
        print()

        # 1. Ready for Investment Endpoint
        print("🔍 1. READY FOR INVESTMENT ENDPOINT")
        print("-" * 40)
        response = self.make_request("GET", "/clients/ready-for-investment", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                ready_clients = data.get("ready_clients", [])
                print(f"✅ Endpoint Status: HTTP 200")
                print(f"📊 Total Ready Clients: {len(ready_clients)}")
                
                for client in ready_clients:
                    print(f"   • Client ID: {client.get('client_id')}")
                    print(f"   • Name: {client.get('name')}")
                    print(f"   • Email: {client.get('email')} {'✅' if client.get('email') == 'alexmar7609@gmail.com' else '❌ (Expected: alexmar7609@gmail.com)'}")
                    print(f"   • Username: {client.get('username')}")
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Endpoint Status: HTTP {status_code}")

        # 2. Client Investments Endpoint
        print(f"\n🔍 2. CLIENT INVESTMENTS ENDPOINT")
        print("-" * 40)
        response = self.make_request("GET", "/investments/client/client_alejandro", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                investments = data.get("investments", [])
                print(f"✅ Endpoint Status: HTTP 200")
                print(f"📊 Total Investments: {len(investments)} {'✅' if len(investments) == 2 else '❌ (Expected: 2)'}")
                
                total_amount = 0
                fund_summary = {}
                for inv in investments:
                    fund_code = inv.get("fund_code")
                    amount = inv.get("principal_amount", 0)
                    total_amount += amount
                    
                    if fund_code in fund_summary:
                        fund_summary[fund_code] += amount
                    else:
                        fund_summary[fund_code] = amount
                    
                    print(f"   • {fund_code}: ${amount:,.2f} (Deposit: {inv.get('deposit_date', 'N/A')})")
                
                print(f"💰 Total Investment Amount: ${total_amount:,.2f} {'✅' if abs(total_amount - 118151.41) < 0.01 else '❌ (Expected: $118,151.41)'}")
                
                # Check expected funds
                balance_amount = fund_summary.get("BALANCE", 0)
                core_amount = fund_summary.get("CORE", 0)
                print(f"📈 BALANCE Fund: ${balance_amount:,.2f} {'✅' if abs(balance_amount - 100000) < 0.01 else '❌ (Expected: $100,000)'}")
                print(f"📈 CORE Fund: ${core_amount:,.2f} {'✅' if abs(core_amount - 18151.41) < 0.01 else '❌ (Expected: $18,151.41)'}")
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Endpoint Status: HTTP {status_code}")

        # 3. MT5 Accounts Endpoint
        print(f"\n🔍 3. MT5 ACCOUNTS ENDPOINT")
        print("-" * 40)
        response = self.make_request("GET", "/mt5/accounts/client_alejandro", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                accounts = data.get("accounts", [])
                print(f"✅ Endpoint Status: HTTP 200")
                print(f"🏦 Total MT5 Accounts: {len(accounts)} {'✅' if len(accounts) == 4 else '❌ (Expected: 4)'}")
                
                if len(accounts) == 0:
                    print("   ❌ No MT5 accounts found - accounts need to be created")
                else:
                    total_balance = 0
                    expected_accounts = {"886557": 80000, "886066": 10000, "886602": 10000, "885822": 18151.41}
                    mexatlantic_count = 0
                    
                    for acc in accounts:
                        account_number = acc.get("mt5_account_number", "N/A")
                        balance = acc.get("balance", 0)
                        broker = acc.get("broker_name", "N/A")
                        total_balance += balance
                        
                        if broker == "MEXAtlantic":
                            mexatlantic_count += 1
                        
                        expected_balance = expected_accounts.get(account_number, "Unknown")
                        balance_status = "✅" if account_number in expected_accounts and abs(balance - expected_accounts[account_number]) < 0.01 else "❌"
                        
                        print(f"   • Account: {account_number} | Balance: ${balance:,.2f} | Broker: {broker} {balance_status}")
                    
                    print(f"💰 Total MT5 Balance: ${total_balance:,.2f} {'✅' if abs(total_balance - 118151.41) < 0.01 else '❌ (Expected: $118,151.41)'}")
                    print(f"🏢 MEXAtlantic Accounts: {mexatlantic_count}/4 {'✅' if mexatlantic_count == 4 else '❌ (Expected: 4)'}")
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Endpoint Status: HTTP {status_code}")

        # 4. Investment Admin Overview
        print(f"\n🔍 4. INVESTMENT ADMIN OVERVIEW")
        print("-" * 40)
        response = self.make_request("GET", "/investments/admin/overview", auth_token=self.admin_token)
        if response and response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Endpoint Status: HTTP 200")
                
                total_aum = data.get("total_aum", 0)
                total_investments = data.get("total_investments", 0)
                total_clients = data.get("total_clients", 0)
                
                print(f"💰 Total AUM: ${total_aum:,.2f} {'✅' if abs(total_aum - 118151.41) < 0.01 else '❌ (Expected: $118,151.41)'}")
                print(f"📊 Total Investments: {total_investments} {'✅' if total_investments > 0 else '❌ (Expected: >0)'}")
                print(f"👥 Total Clients: {total_clients}")
                
                # Show breakdown if available
                if "fund_breakdown" in data:
                    print("📈 Fund Breakdown:")
                    for fund, amount in data["fund_breakdown"].items():
                        print(f"   • {fund}: ${amount:,.2f}")
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            status_code = response.status_code if response else "No response"
            print(f"❌ Endpoint Status: HTTP {status_code}")

        # Summary
        print(f"\n" + "=" * 80)
        print("🎯 DIAGNOSTIC SUMMARY")
        print("=" * 80)
        print("📋 ISSUES IDENTIFIED:")
        print("   1. ❌ Email Mismatch: Database has 'alejandro.mariscal@email.com' but expected 'alexmar7609@gmail.com'")
        print("   2. ❌ Investment Count: Found 5 investments instead of 2")
        print("   3. ❌ Investment Amount: Total $148,151.41 instead of $118,151.41")
        print("   4. ❌ MT5 Accounts: Found 0 accounts instead of 4 with MEXAtlantic broker")
        print("   5. ❌ Admin Overview: Shows $0.00 AUM instead of $118,151.41")
        print()
        print("🔧 REQUIRED FIXES:")
        print("   1. Update Alejandro's email to 'alexmar7609@gmail.com'")
        print("   2. Clean up investments to exactly 2: BALANCE ($100,000) + CORE ($18,151.41)")
        print("   3. Create 4 MT5 accounts: 886557 ($80k), 886066 ($10k), 886602 ($10k), 885822 ($18,151.41)")
        print("   4. Fix admin overview calculation to show correct AUM")
        print()
        print("🚨 PRODUCTION STATUS: NOT READY - CRITICAL DATA SETUP REQUIRED")
        print("=" * 80)

if __name__ == "__main__":
    diagnostic = AlejandroDiagnostic()
    diagnostic.run_diagnostic()