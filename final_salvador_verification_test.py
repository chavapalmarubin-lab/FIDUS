#!/usr/bin/env python3
"""
FINAL SALVADOR PALMA PRODUCTION VERIFICATION TEST
================================================

EXECUTIVE SUMMARY:
This test provides final verification of Salvador Palma's production system status
and delivers clear recommendations for completing the database restoration.

FINDINGS FROM PREVIOUS TESTS:
1. Salvador's client profile EXISTS in production
2. Backend logs show "8 investments for client_003" but API returns 0
3. Investment creation API returns 500 errors
4. Production API disconnected from local MongoDB operations

PRODUCTION URL: https://fidus-invest.emergent.host/
"""

import requests
import sys
from datetime import datetime
import json

class FinalSalvadorVerificationTester:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        
        print(f"🎯 FINAL SALVADOR PALMA PRODUCTION VERIFICATION")
        print(f"   Production URL: {self.base_url}")
        print(f"   Timestamp: {datetime.now().isoformat()}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            }
        )
        if success:
            self.admin_user = response
            print(f"   Admin logged in: {response.get('name', 'Unknown')}")
        return success

    def test_salvador_client_login(self):
        """Test Salvador's client login"""
        success, response = self.run_test(
            "Salvador Client Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client3", 
                "password": "password123",
                "user_type": "client"
            }
        )
        if success:
            self.client_user = response
            print(f"   Salvador logged in: {response.get('name', 'Unknown')}")
            print(f"   Client ID: {response.get('id', 'Unknown')}")
        return success

    def verify_salvador_client_profile(self):
        """Verify Salvador's client profile exists and get details"""
        print(f"\n🔍 VERIFYING SALVADOR'S CLIENT PROFILE...")
        
        if not self.admin_user or 'token' not in self.admin_user:
            print(f"❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }
        
        success, response = self.run_test(
            "Get All Clients",
            "GET",
            "api/admin/clients",
            200,
            headers=headers
        )
        
        if success:
            clients = response.get('clients', [])
            print(f"   Total clients found: {len(clients)}")
            
            salvador_found = False
            salvador_details = None
            
            for client in clients:
                client_id = client.get('id')
                name = client.get('name', '')
                email = client.get('email', '')
                
                if client_id == 'client_003' or 'SALVADOR' in name.upper():
                    salvador_found = True
                    salvador_details = client
                    print(f"   ✅ Salvador found:")
                    print(f"     - Name: {name}")
                    print(f"     - ID: {client_id}")
                    print(f"     - Email: {email}")
                    print(f"     - Total Balance: ${client.get('total_balance', 0):,.2f}")
                    break
            
            if not salvador_found:
                print(f"   ❌ Salvador Palma (client_003) NOT found")
            
            return salvador_found, salvador_details
        
        return False, None

    def check_salvador_investments_detailed(self):
        """Check Salvador's investments with detailed analysis"""
        print(f"\n🔍 DETAILED SALVADOR INVESTMENT ANALYSIS...")
        
        success, response = self.run_test(
            "Get Salvador's Investments",
            "GET",
            "api/investments/client/client_003",
            200
        )
        
        if success:
            investments = response.get('investments', [])
            print(f"   API Response: {len(investments)} investments")
            
            if len(investments) == 0:
                print(f"   ❌ API returns 0 investments despite backend logs showing 8 investments")
                print(f"   🔍 This confirms API-database disconnect issue")
                return False, []
            else:
                print(f"   ✅ Investments found via API:")
                for inv in investments:
                    fund_code = inv.get('fund_code')
                    amount = inv.get('principal_amount', 0)
                    inv_id = inv.get('investment_id')
                    print(f"     - {fund_code}: ${amount:,.2f} (ID: {inv_id})")
                return True, investments
        
        return False, []

    def check_salvador_mt5_accounts_detailed(self):
        """Check Salvador's MT5 accounts with detailed analysis"""
        print(f"\n🔍 DETAILED SALVADOR MT5 ACCOUNT ANALYSIS...")
        
        if not self.admin_user or 'token' not in self.admin_user:
            print(f"❌ No admin token available")
            return False, []
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }
        
        success, response = self.run_test(
            "Get All MT5 Accounts",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            print(f"   API Response: {len(accounts)} total MT5 accounts")
            
            salvador_accounts = []
            for account in accounts:
                client_id = account.get('client_id')
                if client_id == 'client_003':
                    salvador_accounts.append(account)
                    login = account.get('login')
                    broker = account.get('broker')
                    equity = account.get('current_equity', 0)
                    print(f"   ✅ Salvador's MT5: {broker} - Login: {login} - Equity: ${equity:,.2f}")
            
            if len(salvador_accounts) == 0:
                print(f"   ❌ No MT5 accounts found for Salvador")
                return False, []
            
            return True, salvador_accounts
        
        return False, []

    def test_investment_creation_endpoint(self):
        """Test if investment creation endpoint is working"""
        print(f"\n🔍 TESTING INVESTMENT CREATION ENDPOINT...")
        
        if not self.admin_user or 'token' not in self.admin_user:
            print(f"❌ No admin token available")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user['token']}"
        }
        
        # Test with minimal data to see if endpoint is functional
        test_data = {
            "client_id": "client_003",
            "fund_code": "CORE",
            "amount": 1000.00,
            "deposit_date": "2025-04-01"
        }
        
        success, response = self.run_test(
            "Test Investment Creation",
            "POST",
            "api/investments/create",
            200,
            data=test_data,
            headers=headers
        )
        
        if success:
            print(f"   ✅ Investment creation endpoint is functional")
            investment_id = response.get('investment_id')
            print(f"   Created test investment: {investment_id}")
            return True
        else:
            print(f"   ❌ Investment creation endpoint has issues")
            return False

    def run_comprehensive_verification(self):
        """Run comprehensive verification and provide recommendations"""
        print(f"\n" + "="*80)
        print(f"🚀 STARTING FINAL SALVADOR PALMA PRODUCTION VERIFICATION")
        print(f"="*80)
        
        # Step 1: Authentication
        print(f"\n" + "-"*60)
        print(f"🔐 AUTHENTICATION VERIFICATION")
        print(f"-"*60)
        
        admin_login_success = self.test_admin_login()
        salvador_login_success = self.test_salvador_client_login()
        
        # Step 2: Client Profile Verification
        print(f"\n" + "-"*60)
        print(f"👤 CLIENT PROFILE VERIFICATION")
        print(f"-"*60)
        
        client_exists, client_details = self.verify_salvador_client_profile()
        
        # Step 3: Investment Analysis
        print(f"\n" + "-"*60)
        print(f"💰 INVESTMENT DATA ANALYSIS")
        print(f"-"*60)
        
        investments_found, investments = self.check_salvador_investments_detailed()
        
        # Step 4: MT5 Account Analysis
        print(f"\n" + "-"*60)
        print(f"📊 MT5 ACCOUNT ANALYSIS")
        print(f"-"*60)
        
        mt5_found, mt5_accounts = self.check_salvador_mt5_accounts_detailed()
        
        # Step 5: Endpoint Testing
        print(f"\n" + "-"*60)
        print(f"🔧 ENDPOINT FUNCTIONALITY TESTING")
        print(f"-"*60)
        
        creation_endpoint_working = self.test_investment_creation_endpoint()
        
        # Final Analysis and Recommendations
        print(f"\n" + "="*80)
        print(f"📊 FINAL VERIFICATION RESULTS & RECOMMENDATIONS")
        print(f"="*80)
        
        print(f"\n🔍 CURRENT SYSTEM STATUS:")
        print(f"   Authentication: {'✅ WORKING' if admin_login_success and salvador_login_success else '❌ ISSUES'}")
        print(f"   Salvador Profile: {'✅ EXISTS' if client_exists else '❌ MISSING'}")
        print(f"   Salvador Investments: {'✅ FOUND' if investments_found else '❌ MISSING'} ({len(investments)} found)")
        print(f"   Salvador MT5 Accounts: {'✅ FOUND' if mt5_found else '❌ MISSING'} ({len(mt5_accounts)} found)")
        print(f"   Investment Creation API: {'✅ WORKING' if creation_endpoint_working else '❌ BROKEN'}")
        
        # Determine overall status
        critical_issues = []
        if not client_exists:
            critical_issues.append("Salvador's client profile missing")
        if not investments_found:
            critical_issues.append("Salvador's investments missing from API")
        if not mt5_found:
            critical_issues.append("Salvador's MT5 accounts missing from API")
        if not creation_endpoint_working:
            critical_issues.append("Investment creation endpoint broken")
        
        print(f"\n🚨 CRITICAL ISSUES IDENTIFIED: {len(critical_issues)}")
        for i, issue in enumerate(critical_issues, 1):
            print(f"   {i}. {issue}")
        
        # Provide specific recommendations
        print(f"\n💡 RECOMMENDED ACTIONS FOR MAIN AGENT:")
        
        if len(critical_issues) == 0:
            print(f"   🎉 NO CRITICAL ISSUES - Salvador's data appears to be properly restored!")
            print(f"   ✅ All systems operational")
            print(f"   ✅ Production deployment successful")
        elif not client_exists:
            print(f"   1. 🚨 URGENT: Create Salvador's client profile (client_003)")
            print(f"   2. Create BALANCE fund investment ($1,263,485.40)")
            print(f"   3. Create CORE fund investment ($4,000.00)")
            print(f"   4. Create MT5 account mappings")
        elif not creation_endpoint_working:
            print(f"   1. 🚨 URGENT: Fix investment creation API endpoint (returns 500 error)")
            print(f"   2. Check backend database connectivity")
            print(f"   3. Investigate 'Failed to create investment in database' error")
            print(f"   4. After fixing API, create missing investments")
        else:
            print(f"   1. 🔍 INVESTIGATE: Backend logs show 8 investments but API returns 0")
            print(f"   2. Check database query logic in investment endpoints")
            print(f"   3. Verify database connection configuration")
            print(f"   4. Consider database migration or direct database operations")
        
        # Success metrics
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        overall_success = len(critical_issues) == 0
        
        print(f"\n📈 VERIFICATION METRICS:")
        print(f"   API Tests Passed: {self.tests_passed}/{self.tests_run} ({success_rate:.1f}%)")
        print(f"   Critical Issues: {len(critical_issues)}")
        print(f"   Overall Status: {'✅ SUCCESS' if overall_success else '❌ NEEDS ATTENTION'}")
        
        if overall_success:
            print(f"\n🎉 SALVADOR PALMA PRODUCTION VERIFICATION SUCCESSFUL!")
            print(f"   All required data and functionality verified")
            print(f"   Production system ready for use")
        else:
            print(f"\n⚠️  SALVADOR PALMA PRODUCTION VERIFICATION INCOMPLETE")
            print(f"   {len(critical_issues)} critical issues require main agent attention")
            print(f"   Follow recommended actions above")
        
        return overall_success

if __name__ == "__main__":
    tester = FinalSalvadorVerificationTester()
    success = tester.run_comprehensive_verification()
    
    if success:
        print(f"\n✅ VERIFICATION COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n⚠️  VERIFICATION COMPLETED - ACTION REQUIRED")
        sys.exit(1)