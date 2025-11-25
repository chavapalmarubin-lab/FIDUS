#!/usr/bin/env python3
"""
MONEY MANAGERS API DEBUG TEST
Debug the exact API response structure to understand the data format
"""

import requests
import json
import sys
from datetime import datetime

class MoneyManagersDebugger:
    def __init__(self):
        self.base_url = "https://truth-fincore.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating as admin...")
            
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    print("✅ Successfully authenticated as admin")
                    return True
                else:
                    print("❌ No token received in response")
                    return False
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during authentication: {str(e)}")
            return False
    
    def debug_money_managers_api(self):
        """Debug Money Managers API response"""
        try:
            print("\n🔍 Debugging Money Managers API Response...")
            
            response = self.session.get(f"{self.base_url}/admin/trading-analytics/managers")
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return
            
            data = response.json()
            
            print("\n📋 COMPLETE API RESPONSE:")
            print("=" * 50)
            print(json.dumps(data, indent=2, default=str))
            print("=" * 50)
            
            # Analyze structure
            print(f"\n📊 RESPONSE ANALYSIS:")
            print(f"Top-level keys: {list(data.keys())}")
            
            managers = data.get('managers', [])
            print(f"Number of managers: {len(managers)}")
            
            if managers:
                print(f"\n📋 MANAGER DETAILS:")
                for i, manager in enumerate(managers):
                    print(f"\nManager {i+1}:")
                    print(f"  Type: {type(manager)}")
                    if isinstance(manager, dict):
                        print(f"  Keys: {list(manager.keys())}")
                        for key, value in manager.items():
                            print(f"  {key}: {value} (type: {type(value)})")
                    else:
                        print(f"  Value: {manager}")
            
            # Check for summary data
            summary_fields = ['total_managers', 'total_pnl', 'average_return', 'average_sharpe', 
                            'best_performer', 'worst_performer']
            
            print(f"\n📈 SUMMARY DATA:")
            for field in summary_fields:
                if field in data:
                    print(f"  {field}: {data[field]}")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")

def main():
    """Main debug execution"""
    debugger = MoneyManagersDebugger()
    
    if debugger.authenticate_admin():
        debugger.debug_money_managers_api()
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    main()