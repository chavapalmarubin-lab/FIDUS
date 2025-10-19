#!/usr/bin/env python3
"""
SEPARATION ACCOUNTS VERIFICATION TEST
====================================

Quick test to verify the fix for separation_accounts in cash flow response.

Test Objectives:
1. Login as Admin (admin/password123)
2. GET /api/admin/cashflow/overview?timeframe=3_months
3. Check response for:
   - summary.separation_accounts - Should now exist ✅
   - summary.separation_accounts['891215'] - Should have account details ✅  
   - summary.separation_accounts['886528'] - Should have account details ✅
   - summary.broker_rebates - Should still be $363.60 ✅

Expected Results:
- separation_accounts key exists in summary
- Both separation accounts (891215 and 886528) have account details
- broker_rebates remains $363.60
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://fidus-api-bridge.preview.emergentagent.com"

def test_separation_accounts_verification():
    """Test separation_accounts in cash flow response"""
    print("🔍 SEPARATION ACCOUNTS VERIFICATION TEST")
    print("=" * 50)
    
    try:
        # Step 1: Admin Login
        print("\n1️⃣ ADMIN LOGIN")
        login_url = f"{BACKEND_URL}/api/auth/login"
        login_payload = {
            "username": "admin",
            "password": "password123",
            "user_type": "admin"
        }
        
        login_response = requests.post(login_url, json=login_payload, timeout=30)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
            
        login_data = login_response.json()
        token = login_data.get('token')
        print(f"   ✅ Admin login successful")
        
        # Step 2: Get Cash Flow Overview
        print("\n2️⃣ CASH FLOW OVERVIEW REQUEST")
        cashflow_url = f"{BACKEND_URL}/api/admin/cashflow/overview?timeframe=3_months"
        headers = {"Authorization": f"Bearer {token}"}
        
        cashflow_response = requests.get(cashflow_url, headers=headers, timeout=30)
        print(f"   Cash Flow Status: {cashflow_response.status_code}")
        
        if cashflow_response.status_code != 200:
            print(f"   ❌ Cash flow request failed: {cashflow_response.text}")
            return False
            
        cashflow_data = cashflow_response.json()
        print(f"   ✅ Cash flow data retrieved successfully")
        
        # Step 3: Verify separation_accounts
        print("\n3️⃣ SEPARATION ACCOUNTS VERIFICATION")
        
        summary = cashflow_data.get('summary', {})
        
        # Check if separation_accounts exists
        separation_accounts = summary.get('separation_accounts')
        if separation_accounts is None:
            print(f"   ❌ separation_accounts key NOT FOUND in summary")
            print(f"   Available summary keys: {list(summary.keys())}")
            return False
        
        print(f"   ✅ separation_accounts key EXISTS in summary")
        print(f"   📊 separation_accounts type: {type(separation_accounts)}")
        
        # Check account 891215
        account_891215 = separation_accounts.get('891215')
        if account_891215 is None:
            print(f"   ❌ Account 891215 NOT FOUND in separation_accounts")
            print(f"   Available accounts: {list(separation_accounts.keys())}")
        else:
            print(f"   ✅ Account 891215 EXISTS: {account_891215}")
        
        # Check account 886528
        account_886528 = separation_accounts.get('886528')
        if account_886528 is None:
            print(f"   ❌ Account 886528 NOT FOUND in separation_accounts")
            print(f"   Available accounts: {list(separation_accounts.keys())}")
        else:
            print(f"   ✅ Account 886528 EXISTS: {account_886528}")
        
        # Step 4: Verify broker_rebates
        print("\n4️⃣ BROKER REBATES VERIFICATION")
        
        broker_rebates = summary.get('broker_rebates')
        print(f"   📊 broker_rebates: ${broker_rebates}")
        
        if broker_rebates == 363.60:
            print(f"   ✅ broker_rebates is correct: $363.60")
        else:
            print(f"   ⚠️ broker_rebates is ${broker_rebates} (expected $363.60)")
        
        # Step 5: Summary Report
        print("\n5️⃣ VERIFICATION SUMMARY")
        print("=" * 30)
        
        results = {
            "separation_accounts_exists": separation_accounts is not None,
            "account_891215_exists": account_891215 is not None,
            "account_886528_exists": account_886528 is not None,
            "broker_rebates_correct": broker_rebates == 363.60,
            "broker_rebates_value": broker_rebates
        }
        
        success_count = sum([
            results["separation_accounts_exists"],
            results["account_891215_exists"], 
            results["account_886528_exists"],
            results["broker_rebates_correct"]
        ])
        
        print(f"   ✅ separation_accounts exists: {results['separation_accounts_exists']}")
        print(f"   ✅ Account 891215 exists: {results['account_891215_exists']}")
        print(f"   ✅ Account 886528 exists: {results['account_886528_exists']}")
        print(f"   ✅ broker_rebates correct: {results['broker_rebates_correct']} (${results['broker_rebates_value']})")
        
        print(f"\n🎯 VERIFICATION SCORE: {success_count}/4 ({success_count/4*100:.1f}%)")
        
        if success_count == 4:
            print("🎉 ALL VERIFICATIONS PASSED - SEPARATION ACCOUNTS FIX SUCCESSFUL!")
            return True
        else:
            print("⚠️ SOME VERIFICATIONS FAILED - NEEDS ATTENTION")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_separation_accounts_verification()
    sys.exit(0 if success else 1)