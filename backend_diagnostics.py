#!/usr/bin/env python3
"""
DETAILED BACKEND DIAGNOSTICS - 4 PRIORITY ISSUES
Investigating the actual data structures returned by each endpoint
"""

import requests
import json
import sys
from datetime import datetime

class BackendDiagnostics:
    def __init__(self):
        self.base_url = "https://fidus-risk-deep.preview.emergentagent.com/api"
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
    
    def diagnose_fund_portfolio(self):
        """Diagnose Fund Portfolio endpoint"""
        print("\n" + "="*60)
        print("📊 DIAGNOSING FUND PORTFOLIO ENDPOINT")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/fund-portfolio/overview")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print("\nFull Response Structure:")
                print(json.dumps(data, indent=2, default=str)[:2000] + "..." if len(str(data)) > 2000 else json.dumps(data, indent=2, default=str))
                
                # Look for funds in different possible locations
                funds = []
                if isinstance(data, list):
                    funds = data
                elif isinstance(data, dict):
                    for key in ['funds', 'data', 'fund_data', 'portfolio']:
                        if key in data:
                            funds = data[key]
                            print(f"\nFound funds in key: {key}")
                            break
                
                if funds:
                    print(f"\nFound {len(funds)} funds:")
                    for i, fund in enumerate(funds):
                        if isinstance(fund, dict):
                            fund_code = fund.get('fund_code', fund.get('code', fund.get('name', f'Fund_{i}')))
                            print(f"  Fund {i+1}: {fund_code}")
                            print(f"    Keys: {list(fund.keys())}")
                            if 'total_rebates' in fund:
                                print(f"    total_rebates: {fund['total_rebates']}")
                            else:
                                print("    ❌ total_rebates field missing")
                else:
                    print("❌ No funds found in response")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    def diagnose_cashflow(self):
        """Diagnose Cash Flow endpoint"""
        print("\n" + "="*60)
        print("💰 DIAGNOSING CASH FLOW ENDPOINT")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/admin/cashflow/overview?timeframe=3months&fund=all")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print("\nFull Response Structure:")
                print(json.dumps(data, indent=2, default=str)[:2000] + "..." if len(str(data)) > 2000 else json.dumps(data, indent=2, default=str))
                
                # Check for required fields
                if isinstance(data, dict):
                    print(f"\nLooking for required fields:")
                    print(f"  total_client_obligations: {'✅' if 'total_client_obligations' in data else '❌'} {data.get('total_client_obligations', 'MISSING')}")
                    print(f"  total_fund_outflows: {'✅' if 'total_fund_outflows' in data else '❌'} {data.get('total_fund_outflows', 'MISSING')}")
                    
                    # Look for similar fields
                    similar_fields = [k for k in data.keys() if 'obligation' in k.lower() or 'outflow' in k.lower() or 'client' in k.lower()]
                    if similar_fields:
                        print(f"  Similar fields found: {similar_fields}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    def diagnose_trading_analytics(self):
        """Diagnose Trading Analytics endpoint"""
        print("\n" + "="*60)
        print("📈 DIAGNOSING TRADING ANALYTICS ENDPOINT")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/admin/fund-performance/dashboard")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print("\nFull Response Structure:")
                print(json.dumps(data, indent=2, default=str)[:2000] + "..." if len(str(data)) > 2000 else json.dumps(data, indent=2, default=str))
                
                # Check for by_fund structure
                if isinstance(data, dict):
                    print(f"\nLooking for by_fund structure:")
                    by_fund = data.get('by_fund', {})
                    print(f"  by_fund exists: {'✅' if 'by_fund' in data else '❌'}")
                    
                    if by_fund:
                        print(f"  by_fund keys: {list(by_fund.keys())}")
                        core_fund = by_fund.get('CORE', {})
                        print(f"  CORE fund exists: {'✅' if 'CORE' in by_fund else '❌'}")
                        
                        if core_fund:
                            print(f"  CORE fund keys: {list(core_fund.keys())}")
                            print(f"  account_count: {'✅' if 'account_count' in core_fund else '❌'} {core_fund.get('account_count', 'MISSING')}")
                        else:
                            print("  ❌ CORE fund data missing")
                    else:
                        print("  ❌ by_fund structure missing")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    def diagnose_money_managers(self):
        """Diagnose Money Managers endpoint"""
        print("\n" + "="*60)
        print("👥 DIAGNOSING MONEY MANAGERS ENDPOINT")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/admin/trading-analytics/managers")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Type: {type(data)}")
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print("\nFull Response Structure:")
                print(json.dumps(data, indent=2, default=str)[:1500] + "..." if len(str(data)) > 1500 else json.dumps(data, indent=2, default=str))
                
                # Extract managers
                managers = []
                if isinstance(data, list):
                    managers = data
                elif isinstance(data, dict):
                    for key in ['managers', 'data', 'manager_data']:
                        if key in data:
                            managers = data[key]
                            print(f"\nFound managers in key: {key}")
                            break
                
                if managers:
                    print(f"\nFound {len(managers)} managers:")
                    expected_managers = ["CP Strategy", "TradingHub Gold", "GoldenTrade", "UNO14"]
                    excluded_managers = ["Manual Trading", "Manager None"]
                    
                    for i, manager in enumerate(managers):
                        if isinstance(manager, dict):
                            name = manager.get('name', manager.get('manager_name', f'Manager_{i}'))
                            print(f"  Manager {i+1}: {name}")
                            print(f"    Keys: {list(manager.keys())}")
                            
                            # Check if it matches expected or excluded
                            is_expected = any(exp in name for exp in expected_managers)
                            is_excluded = any(exc in name for exc in excluded_managers)
                            print(f"    Expected: {'✅' if is_expected else '❌'}")
                            print(f"    Excluded: {'❌' if is_excluded else '✅'}")
                        else:
                            print(f"  Manager {i+1}: {manager} (not a dict)")
                else:
                    print("❌ No managers found in response")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    def run_diagnostics(self):
        """Run all diagnostics"""
        print("🔍 COMPREHENSIVE BACKEND DIAGNOSTICS")
        print("Investigating actual data structures for 4 priority issues")
        
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed.")
            return
        
        self.diagnose_fund_portfolio()
        self.diagnose_cashflow()
        self.diagnose_trading_analytics()
        self.diagnose_money_managers()
        
        print("\n" + "="*60)
        print("🎯 DIAGNOSTICS COMPLETE")
        print("="*60)
        print("Use the above information to understand the actual API response structures")
        print("and adjust the test expectations accordingly.")

def main():
    """Main execution"""
    diagnostics = BackendDiagnostics()
    diagnostics.run_diagnostics()

if __name__ == "__main__":
    main()