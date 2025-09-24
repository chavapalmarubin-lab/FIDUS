#!/usr/bin/env python3
"""
MT5 Multi-Broker Diagnostic Test
Investigates specific issues found in the multi-broker MT5 system
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://auth-flow-debug-2.preview.emergentagent.com/api"

class MT5DiagnosticTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self) -> bool:
        """Authenticate as admin to get JWT token"""
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
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    print("✅ Admin authentication successful")
                    return True
            return False
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            return False

    def diagnose_manual_account_creation(self):
        """Diagnose the manual account creation issue"""
        print("\n🔍 DIAGNOSING MANUAL ACCOUNT CREATION ISSUE")
        print("=" * 60)
        
        # Test with minimal required data first
        test_data = {
            "client_id": "client_001",
            "fund_code": "CORE", 
            "broker_code": "dootechnology",
            "mt5_login": 9928326,
            "mt5_password": "R1d567j!",
            "mt5_server": "DooTechnology-Live"
        }
        
        print(f"Testing with data: {json.dumps(test_data, indent=2)}")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/mt5/admin/add-manual-account", json=test_data)
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")

    def diagnose_broker_grouping_issue(self):
        """Diagnose why accounts are not properly grouped by broker"""
        print("\n🔍 DIAGNOSING BROKER GROUPING ISSUE")
        print("=" * 60)
        
        # First, check what accounts exist
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/accounts")
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                
                print(f"Found {len(accounts)} total MT5 accounts:")
                for i, account in enumerate(accounts):
                    print(f"  Account {i+1}:")
                    print(f"    ID: {account.get('account_id')}")
                    print(f"    Client: {account.get('client_id')} ({account.get('client_name', 'N/A')})")
                    print(f"    Fund: {account.get('fund_code')}")
                    print(f"    Broker Code: {account.get('broker_code', 'MISSING')}")
                    print(f"    Broker Name: {account.get('broker_name', 'MISSING')}")
                    print(f"    Server: {account.get('mt5_server')}")
                    print()
                    
        except Exception as e:
            print(f"❌ Failed to get accounts: {str(e)}")

    def diagnose_performance_overview_issue(self):
        """Diagnose the performance overview response structure issue"""
        print("\n🔍 DIAGNOSING PERFORMANCE OVERVIEW ISSUE")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/mt5/admin/performance/overview")
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Response structure analysis:")
                print(f"  - success: {data.get('success')}")
                print(f"  - Has 'overview' key: {'overview' in data}")
                print(f"  - Has 'total_accounts' key: {'total_accounts' in data}")
                print(f"  - Has 'total_equity' key: {'total_equity' in data}")
                print(f"  - Has 'total_profit' key: {'total_profit' in data}")
                
                if 'overview' in data:
                    overview = data['overview']
                    print(f"  - Overview total_accounts: {overview.get('total_accounts')}")
                    print(f"  - Overview total_equity: {overview.get('total_equity')}")
                    print(f"  - Overview total_profit_loss: {overview.get('total_profit_loss')}")
                
                print(f"\nFull response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Failed to get performance overview: {str(e)}")

    def test_client_existence(self):
        """Test if the client exists in the system"""
        print("\n🔍 TESTING CLIENT EXISTENCE")
        print("=" * 60)
        
        try:
            # Try to get client data
            response = self.session.get(f"{BACKEND_URL}/client/client_001/data")
            print(f"Client data response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Client client_001 exists")
                print(f"Client balance: ${data.get('balance', {}).get('total_balance', 0):,.2f}")
            else:
                print(f"❌ Client not found or error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to check client: {str(e)}")

    def test_fund_validation(self):
        """Test fund code validation"""
        print("\n🔍 TESTING FUND CODE VALIDATION")
        print("=" * 60)
        
        try:
            # Get fund configuration
            response = self.session.get(f"{BACKEND_URL}/investments/funds/config")
            print(f"Fund config response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                funds = data.get('funds', [])
                fund_codes = [fund.get('fund_code') for fund in funds]
                print(f"Available fund codes: {fund_codes}")
                print(f"CORE fund exists: {'CORE' in fund_codes}")
            else:
                print(f"❌ Failed to get fund config: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to check funds: {str(e)}")

    def run_diagnostics(self):
        """Run all diagnostic tests"""
        print("🔧 MT5 MULTI-BROKER DIAGNOSTIC TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        self.test_client_existence()
        self.test_fund_validation()
        self.diagnose_broker_grouping_issue()
        self.diagnose_manual_account_creation()
        self.diagnose_performance_overview_issue()
        
        print("\n" + "=" * 80)
        print("🎯 DIAGNOSTIC SUMMARY")
        print("=" * 80)
        print("Key findings from diagnostic tests will help identify root causes")
        print("of the multi-broker MT5 integration issues.")

def main():
    """Main diagnostic execution"""
    tester = MT5DiagnosticTester()
    
    try:
        tester.run_diagnostics()
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Critical error during diagnostics: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()