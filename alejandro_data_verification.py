#!/usr/bin/env python3
"""
ALEJANDRO DATA VERIFICATION TEST
Test that backend endpoints return CORRECT data for Alejandro ONLY
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://referral-tracker-8.preview.emergentagent.com"

def login_admin():
    """Login as admin and get JWT token"""
    print("🔐 Logging in as admin...")
    
    login_data = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data, timeout=30)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print("✅ Admin login successful")
                return token
            else:
                print("❌ No token in login response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_portfolio_fund_allocations(token):
    """Test /api/portfolio/fund-allocations endpoint"""
    print("\n📊 Testing /api/portfolio/fund-allocations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/portfolio/fund-allocations", headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            # Extract total_aum from nested data structure
            data_section = data.get('data', {})
            total_aum = data_section.get('total_aum', 0)
            print(f"Total AUM: ${total_aum:,.2f}")
            
            # Check if it's the expected value
            expected_aum = 118151.41
            if abs(total_aum - expected_aum) < 0.01:  # Allow for small floating point differences
                print(f"✅ CORRECT: Total AUM = ${total_aum:,.2f} (expected ${expected_aum:,.2f})")
                
                # Check fund breakdown
                funds = data_section.get('funds', [])
                core_fund = None
                balance_fund = None
                
                for fund in funds:
                    if fund.get('fund_code') == 'CORE':
                        core_fund = fund
                    elif fund.get('fund_code') == 'BALANCE':
                        balance_fund = fund
                
                if core_fund:
                    core_aum = core_fund.get('aum', 0)
                    print(f"CORE Fund AUM: ${core_aum:,.2f}")
                    if abs(core_aum - 18151.41) < 0.01:
                        print("✅ CORE Fund amount correct")
                    else:
                        print(f"❌ CORE Fund amount incorrect: ${core_aum:,.2f} (expected $18,151.41)")
                
                if balance_fund:
                    balance_aum = balance_fund.get('aum', 0)
                    print(f"BALANCE Fund AUM: ${balance_aum:,.2f}")
                    if abs(balance_aum - 100000.00) < 0.01:
                        print("✅ BALANCE Fund amount correct")
                    else:
                        print(f"❌ BALANCE Fund amount incorrect: ${balance_aum:,.2f} (expected $100,000.00)")
                
                return True
            else:
                print(f"❌ WRONG: Total AUM = ${total_aum:,.2f} (expected ${expected_aum:,.2f})")
                if total_aum > 200000:
                    print("🚨 CRITICAL: Returning $236k or similar - THIS IS WRONG!")
                return False
        else:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing portfolio endpoint: {str(e)}")
        return False

def test_investments_summary(token):
    """Test /api/investments/summary endpoint"""
    print("\n💰 Testing /api/investments/summary...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/investments/summary", headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            # Extract key values from nested data structure
            data_section = data.get('data', {})
            total_aum = data_section.get('total_aum', 0)
            active_clients = data_section.get('active_clients', 0)
            total_investments = data_section.get('total_investments', 0)
            
            print(f"Total AUM: ${total_aum:,.2f}")
            print(f"Active Clients: {active_clients}")
            print(f"Total Investments: {total_investments}")
            
            # Check values
            success = True
            
            # Check total_aum
            expected_aum = 118151.41
            if abs(total_aum - expected_aum) < 0.01:
                print(f"✅ CORRECT: Total AUM = ${total_aum:,.2f}")
            else:
                print(f"❌ WRONG: Total AUM = ${total_aum:,.2f} (expected ${expected_aum:,.2f})")
                if total_aum > 200000:
                    print("🚨 CRITICAL: Returning $236k or similar - THIS IS WRONG!")
                success = False
            
            # Check active_clients
            if active_clients == 1:
                print(f"✅ CORRECT: Active Clients = {active_clients}")
            else:
                print(f"❌ WRONG: Active Clients = {active_clients} (expected 1)")
                if active_clients == 2:
                    print("🚨 CRITICAL: Returning 2 clients - THIS IS WRONG!")
                success = False
            
            # Check total_investments
            if total_investments == 2:
                print(f"✅ CORRECT: Total Investments = {total_investments}")
            else:
                print(f"❌ WRONG: Total Investments = {total_investments} (expected 2)")
                success = False
            
            return success
        else:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing investments endpoint: {str(e)}")
        return False

def test_mt5_accounts_all(token):
    """Test /api/mt5/accounts/all endpoint"""
    print("\n🏦 Testing /api/mt5/accounts/all...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/mt5/accounts/all", headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            # Extract accounts
            accounts = data.get('accounts', [])
            account_count = len(accounts)
            
            print(f"Number of accounts returned: {account_count}")
            
            # Expected account numbers
            expected_accounts = [886557, 886066, 886602, 885822, 891234, 886528, 891215]
            
            if account_count == 7:
                print("✅ CORRECT: 7 accounts returned")
                
                # Check specific account numbers
                returned_account_numbers = []
                for account in accounts:
                    account_num = account.get('account')
                    if account_num:
                        returned_account_numbers.append(int(account_num))
                
                print(f"Returned account numbers: {sorted(returned_account_numbers)}")
                print(f"Expected account numbers: {sorted(expected_accounts)}")
                
                missing_accounts = set(expected_accounts) - set(returned_account_numbers)
                extra_accounts = set(returned_account_numbers) - set(expected_accounts)
                
                if not missing_accounts and not extra_accounts:
                    print("✅ CORRECT: All expected accounts present")
                    return True
                else:
                    if missing_accounts:
                        print(f"❌ Missing accounts: {missing_accounts}")
                    if extra_accounts:
                        print(f"❌ Extra accounts: {extra_accounts}")
                    return False
            else:
                print(f"❌ WRONG: {account_count} accounts returned (expected 7)")
                return False
        else:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MT5 accounts endpoint: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 ALEJANDRO DATA VERIFICATION TEST")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test time: {datetime.now()}")
    print()
    
    # Step 1: Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        sys.exit(1)
    
    # Step 2: Test all endpoints
    results = {}
    
    results['portfolio'] = test_portfolio_fund_allocations(token)
    results['investments'] = test_investments_summary(token)
    results['mt5_accounts'] = test_mt5_accounts_all(token)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for endpoint, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{endpoint.upper()}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED - Alejandro data is CORRECT!")
    else:
        print("🚨 SOME TESTS FAILED - Backend data needs IMMEDIATE FIX!")
        print()
        print("CRITICAL ISSUES TO FIX:")
        if not results['portfolio']:
            print("- Portfolio fund allocations returning wrong total AUM")
        if not results['investments']:
            print("- Investments summary returning wrong AUM/client count")
        if not results['mt5_accounts']:
            print("- MT5 accounts not returning all 7 expected accounts")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)