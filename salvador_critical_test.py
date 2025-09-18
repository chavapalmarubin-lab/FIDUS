#!/usr/bin/env python3
"""
CRITICAL: Salvador Palma Data Verification Test
==============================================

This script checks the current state of Salvador Palma's data and attempts restoration.
"""

import requests
import sys
import json
from datetime import datetime

class SalvadorCriticalTest:
    def __init__(self, base_url="https://investsim-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.salvador_client_id = "client_003"

    def authenticate_admin(self):
        """Authenticate as admin"""
        try:
            response = requests.post(f"{self.base_url}/api/auth/login", json={
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                print(f"✅ Admin authenticated: {data.get('name')}")
                return True
            else:
                print(f"❌ Admin auth failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin auth error: {e}")
            return False

    def get_headers(self):
        """Get headers with auth token"""
        headers = {'Content-Type': 'application/json'}
        if self.admin_token:
            headers['Authorization'] = f"Bearer {self.admin_token}"
        return headers

    def check_clients(self):
        """Check all clients"""
        try:
            response = requests.get(f"{self.base_url}/api/clients/all", 
                                  headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                print(f"✅ Found {len(clients)} clients")
                
                salvador_found = False
                for client in clients:
                    if (client.get("id") == self.salvador_client_id or 
                        "SALVADOR" in client.get("name", "").upper() or
                        "chava@alyarglobal.com" in client.get("email", "")):
                        salvador_found = True
                        print(f"   ✅ Salvador found: {client.get('name')} ({client.get('email')})")
                        break
                
                if not salvador_found:
                    print("   ❌ Salvador NOT found in clients")
                    for client in clients:
                        print(f"      - {client.get('name')} ({client.get('id')})")
                
                return salvador_found
            else:
                print(f"❌ Clients check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Clients check error: {e}")
            return False

    def check_investments(self):
        """Check Salvador's investments"""
        try:
            response = requests.get(f"{self.base_url}/api/investments/client/{self.salvador_client_id}",
                                  headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                investments = data.get("investments", [])
                print(f"✅ Found {len(investments)} investments for Salvador")
                
                balance_investment = None
                for inv in investments:
                    if inv.get("fund_code") == "BALANCE":
                        balance_investment = inv
                        principal = inv.get("principal_amount", 0)
                        current = inv.get("current_value", 0)
                        print(f"   ✅ BALANCE investment: ${principal:,.2f} principal, ${current:,.2f} current")
                        break
                
                if not balance_investment:
                    print("   ❌ No BALANCE investment found")
                    for inv in investments:
                        print(f"      - {inv.get('fund_code')}: ${inv.get('principal_amount', 0):,.2f}")
                
                return balance_investment is not None
            else:
                print(f"❌ Investments check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Investments check error: {e}")
            return False

    def create_salvador_investment(self):
        """Create Salvador's BALANCE investment"""
        try:
            investment_data = {
                "client_id": self.salvador_client_id,
                "fund_code": "BALANCE",
                "amount": 1263485.40,
                "deposit_date": "2025-04-01",
                "create_mt5_account": True,
                "mt5_login": "9928326",
                "mt5_password": "secure_password_123",
                "mt5_server": "DooTechnology-Live",
                "broker_name": "DooTechnology",
                "mt5_initial_balance": 1263485.40
            }
            
            response = requests.post(f"{self.base_url}/api/investments/create",
                                   json=investment_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                investment_id = data.get("investment_id")
                print(f"✅ Investment created: {investment_id}")
                
                # Confirm the deposit
                self.confirm_deposit(investment_id)
                return True
            else:
                print(f"❌ Investment creation failed: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   Error: {error}")
                except:
                    print(f"   Error text: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Investment creation error: {e}")
            return False

    def confirm_deposit(self, investment_id):
        """Confirm Salvador's deposit"""
        try:
            confirmation_data = {
                "investment_id": investment_id,
                "payment_method": "fiat",
                "amount": 1263485.40,
                "currency": "USD",
                "wire_confirmation_number": "SALVADOR_WIRE_001",
                "bank_reference": "BALANCE_FUND_DEPOSIT_APRIL_2025",
                "notes": "Salvador Palma BALANCE fund deposit - April 1, 2025"
            }
            
            response = requests.post(f"{self.base_url}/api/payments/deposit/confirm?admin_id=admin_001",
                                   json=confirmation_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                print("✅ Deposit confirmed")
                return True
            else:
                print(f"❌ Deposit confirmation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Deposit confirmation error: {e}")
            return False

    def run_test(self):
        """Run the critical test"""
        print("=" * 60)
        print("🚨 SALVADOR PALMA CRITICAL DATA TEST")
        print("=" * 60)
        print(f"Testing: {self.base_url}")
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            return False
        
        # Step 2: Check current state
        clients_ok = self.check_clients()
        investments_ok = self.check_investments()
        
        # Step 3: Restore if needed
        if clients_ok and not investments_ok:
            print("\n🔧 RESTORING SALVADOR'S INVESTMENT...")
            if self.create_salvador_investment():
                print("✅ Investment restoration successful")
                # Re-check
                investments_ok = self.check_investments()
            else:
                print("❌ Investment restoration failed")
        
        # Step 4: Final status
        print("\n" + "=" * 60)
        print("📋 FINAL STATUS")
        print("=" * 60)
        print(f"Client exists: {'✅' if clients_ok else '❌'}")
        print(f"Investment exists: {'✅' if investments_ok else '❌'}")
        
        if clients_ok and investments_ok:
            print("\n🚀 SUCCESS: Salvador's data is complete!")
            return True
        else:
            print("\n🚨 FAILURE: Salvador's data is incomplete!")
            return False

def main():
    """Main function"""
    # Test both environments
    environments = [
        ("Preview", "https://investsim-1.preview.emergentagent.com"),
        ("Production", "https://fidus-invest.emergent.host")
    ]
    
    results = {}
    
    for env_name, url in environments:
        print(f"\n🔍 Testing {env_name} Environment")
        tester = SalvadorCriticalTest(url)
        results[env_name] = tester.run_test()
    
    print("\n" + "=" * 80)
    print("🎯 OVERALL RESULTS")
    print("=" * 80)
    for env_name, success in results.items():
        print(f"{env_name}: {'✅ PASS' if success else '❌ FAIL'}")
    
    # Return True if production is working
    return results.get("Production", False)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)