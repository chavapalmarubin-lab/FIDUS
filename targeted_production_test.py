#!/usr/bin/env python3
"""
TARGETED PRODUCTION TEST - Focus on specific issues found
"""

import requests
import json

class TargetedTester:
    def __init__(self, base_url="https://fidus-invest.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.client_token = None
        
    def authenticate(self):
        """Get JWT tokens"""
        # Admin login
        response = requests.post(f"{self.base_url}/api/auth/login", json={
            "username": "admin", "password": "password123", "user_type": "admin"
        })
        if response.status_code == 200:
            self.admin_token = response.json()['token']
            print("✅ Admin authenticated")
        
        # Client login  
        response = requests.post(f"{self.base_url}/api/auth/login", json={
            "username": "client1", "password": "password123", "user_type": "client"
        })
        if response.status_code == 200:
            self.client_token = response.json()['token']
            print("✅ Client authenticated")
    
    def test_cashflow_issue(self):
        """Test cashflow endpoint to understand zero values"""
        print("\n🔍 INVESTIGATING CASHFLOW ZERO VALUES...")
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = requests.get(f"{self.base_url}/api/admin/cashflow/overview", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Cashflow response: {json.dumps(data, indent=2)}")
            
            # Check if there are any cash flows at all
            cash_flows = data.get('cash_flows', [])
            print(f"Number of cash flow records: {len(cash_flows)}")
            
            if cash_flows:
                print("Sample cash flow records:")
                for i, flow in enumerate(cash_flows[:3]):
                    print(f"  {i+1}. {flow}")
        else:
            print(f"❌ Cashflow endpoint failed: {response.status_code}")
    
    def test_redemption_structure(self):
        """Test redemption endpoint structure"""
        print("\n🔍 INVESTIGATING REDEMPTION STRUCTURE...")
        
        headers = {'Authorization': f'Bearer {self.client_token}'}
        response = requests.get(f"{self.base_url}/api/redemptions/client/client_001", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            redemptions = data.get('available_redemptions', [])
            
            print(f"Number of available redemptions: {len(redemptions)}")
            
            if redemptions:
                print("Sample redemption structure:")
                sample = redemptions[0]
                print(f"Keys in redemption: {list(sample.keys())}")
                print(f"Sample redemption: {json.dumps(sample, indent=2)}")
        else:
            print(f"❌ Redemption endpoint failed: {response.status_code}")
    
    def test_gmail_endpoints(self):
        """Test available Gmail endpoints"""
        print("\n🔍 TESTING AVAILABLE GMAIL ENDPOINTS...")
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test auth-url
        response = requests.get(f"{self.base_url}/api/gmail/auth-url", headers=headers)
        print(f"Gmail auth-url: {response.status_code}")
        
        # Test authenticate
        response = requests.post(f"{self.base_url}/api/gmail/authenticate", headers=headers)
        print(f"Gmail authenticate: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    
    def test_portfolio_summary_details(self):
        """Test portfolio summary in detail"""
        print("\n🔍 DETAILED PORTFOLIO SUMMARY ANALYSIS...")
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = requests.get(f"{self.base_url}/api/admin/portfolio-summary", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Portfolio summary: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Portfolio summary failed: {response.status_code}")
    
    def run_tests(self):
        """Run all targeted tests"""
        print("🎯 TARGETED PRODUCTION ISSUE INVESTIGATION")
        print("=" * 60)
        
        self.authenticate()
        
        if self.admin_token and self.client_token:
            self.test_cashflow_issue()
            self.test_redemption_structure()
            self.test_gmail_endpoints()
            self.test_portfolio_summary_details()
        else:
            print("❌ Authentication failed")

if __name__ == "__main__":
    tester = TargetedTester()
    tester.run_tests()