#!/usr/bin/env python3
"""
Money Managers API Production Test
Test the /api/admin/money-managers endpoint after database fixes
"""

import requests
import json
from datetime import datetime

# Production API URL
BACKEND_URL = "https://trading-platform-110.preview.emergentagent.com"
API_ENDPOINT = f"{BACKEND_URL}/api/admin/money-managers"
LOGIN_ENDPOINT = f"{BACKEND_URL}/api/auth/login"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def get_admin_token():
    """Login and get admin JWT token"""
    print("🔐 Logging in as admin to get JWT token...")
    
    try:
        response = requests.post(
            LOGIN_ENDPOINT,
            json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print(f"✅ Successfully logged in as admin")
                return token
            else:
                print(f"❌ Login response missing token")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_money_managers_api():
    """Test Money Managers API on production"""
    
    print("=" * 80)
    print("MONEY MANAGERS API PRODUCTION TEST")
    print("=" * 80)
    print(f"Testing endpoint: {API_ENDPOINT}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    print()
    
    try:
        # Get admin token first
        token = get_admin_token()
        if not token:
            print("❌ CRITICAL ERROR: Failed to get admin token")
            return False
        
        print()
        
        # Make GET request to the endpoint with auth header
        print("📡 Making GET request to /api/admin/money-managers...")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(API_ENDPOINT, headers=headers, timeout=30)
        
        print(f"✅ Response Status Code: {response.status_code}")
        print()
        
        if response.status_code != 200:
            print(f"❌ CRITICAL ERROR: Expected status 200, got {response.status_code}")
            print(f"Response Text: {response.text}")
            return False
        
        # Parse JSON response
        data = response.json()
        
        print("=" * 80)
        print("RESPONSE DATA ANALYSIS")
        print("=" * 80)
        print()
        
        # Check if data is wrapped in a dict with "managers" key
        if isinstance(data, dict) and 'managers' in data:
            print(f"✅ Response structure: dict with 'managers' key")
            managers = data['managers']
            print(f"   Additional fields: {', '.join([k for k in data.keys() if k != 'managers'])}")
        elif isinstance(data, list):
            print(f"✅ Response structure: direct list of managers")
            managers = data
        else:
            print(f"❌ CRITICAL ERROR: Unexpected response structure")
            print(f"Response: {json.dumps(data, indent=2)}")
            return False
        
        print()
        
        # Count managers
        manager_count = len(managers)
        print(f"📊 Total Managers Found: {manager_count}")
        print(f"   Expected: 5 managers")
        
        if manager_count != 5:
            print(f"⚠️  WARNING: Expected 5 managers, found {manager_count}")
        else:
            print(f"✅ Manager count matches expected value")
        print()
        
        # Track issues
        issues = []
        zero_allocation_managers = []
        zero_equity_managers = []
        
        print("=" * 80)
        print("INDIVIDUAL MANAGER VALIDATION")
        print("=" * 80)
        print()
        
        # Expected managers with approximate values
        expected_managers = {
            "UNO14 Manager": {"allocation": 10000, "equity": 15700},
            "TradingHub Gold": {"allocation": 94000, "equity": 78000},
            "Provider1-Assev": {"allocation": 5000, "equity": 5000},
            "CP Strategy": {"allocation": 34000, "equity": 18000},
            "alefloreztrader": {"allocation": 20000, "equity": 20000}
        }
        
        # Validate each manager
        for idx, manager in enumerate(managers, 1):
            print(f"Manager #{idx}: {manager.get('manager_name', 'UNKNOWN')}")
            print("-" * 80)
            
            # Extract key fields
            manager_name = manager.get('manager_name', 'UNKNOWN')
            initial_allocation = manager.get('initial_allocation', 0)
            current_equity = manager.get('current_equity', 0)
            total_pnl = manager.get('total_pnl', 0)
            return_percentage = manager.get('return_percentage', 0)
            assigned_accounts = manager.get('assigned_accounts', [])
            
            # Display values
            print(f"   Manager Name: {manager_name}")
            print(f"   Initial Allocation: ${initial_allocation:,.2f}")
            print(f"   Current Equity: ${current_equity:,.2f}")
            print(f"   Total P&L: ${total_pnl:,.2f}")
            print(f"   Return %: {return_percentage:.2f}%")
            print(f"   Assigned Accounts: {len(assigned_accounts)} accounts")
            
            # Validate initial_allocation
            if initial_allocation == 0:
                print(f"   ❌ CRITICAL: initial_allocation is $0.00")
                zero_allocation_managers.append(manager_name)
                issues.append(f"{manager_name}: initial_allocation is $0.00")
            else:
                print(f"   ✅ initial_allocation is NOT $0.00")
            
            # Validate current_equity
            if current_equity == 0:
                print(f"   ❌ CRITICAL: current_equity is $0.00")
                zero_equity_managers.append(manager_name)
                issues.append(f"{manager_name}: current_equity is $0.00")
            else:
                print(f"   ✅ current_equity is NOT $0.00")
            
            # Validate assigned_accounts
            if len(assigned_accounts) == 0:
                print(f"   ⚠️  WARNING: No assigned accounts")
                issues.append(f"{manager_name}: No assigned accounts")
            else:
                print(f"   ✅ Has {len(assigned_accounts)} assigned account(s)")
            
            # Compare with expected values (if available)
            if manager_name in expected_managers:
                expected = expected_managers[manager_name]
                expected_allocation = expected['allocation']
                expected_equity = expected['equity']
                
                print(f"   📋 Expected Values:")
                print(f"      Allocation: ~${expected_allocation:,.0f} (Actual: ${initial_allocation:,.2f})")
                print(f"      Equity: ~${expected_equity:,.0f} (Actual: ${current_equity:,.2f})")
                
                # Check if values are in reasonable range (within 50% variance)
                allocation_diff = abs(initial_allocation - expected_allocation) / expected_allocation * 100
                equity_diff = abs(current_equity - expected_equity) / expected_equity * 100
                
                if allocation_diff > 50:
                    print(f"   ⚠️  Allocation differs by {allocation_diff:.1f}% from expected")
                if equity_diff > 50:
                    print(f"   ⚠️  Equity differs by {equity_diff:.1f}% from expected")
            
            print()
        
        print("=" * 80)
        print("CRITICAL VALIDATION SUMMARY")
        print("=" * 80)
        print()
        
        # Summary of critical checks
        print(f"✓ Total Managers: {manager_count} (Expected: 5)")
        print(f"✓ Managers with $0 initial_allocation: {len(zero_allocation_managers)}")
        print(f"✓ Managers with $0 current_equity: {len(zero_equity_managers)}")
        print()
        
        if zero_allocation_managers:
            print("❌ CRITICAL ISSUE: Managers with $0 initial_allocation:")
            for name in zero_allocation_managers:
                print(f"   - {name}")
            print()
        
        if zero_equity_managers:
            print("❌ CRITICAL ISSUE: Managers with $0 current_equity:")
            for name in zero_equity_managers:
                print(f"   - {name}")
            print()
        
        # Overall result
        print("=" * 80)
        print("TEST RESULT")
        print("=" * 80)
        print()
        
        if len(issues) == 0 and manager_count == 5:
            print("✅ ALL TESTS PASSED!")
            print("   - All 5 managers present")
            print("   - NO managers with $0 initial_allocation")
            print("   - NO managers with $0 current_equity")
            print("   - All managers have assigned accounts")
            print()
            print("🎉 Money Managers API is working correctly!")
            return True
        else:
            print(f"❌ TESTS FAILED: {len(issues)} issue(s) found")
            print()
            print("Issues:")
            for issue in issues:
                print(f"   - {issue}")
            print()
            return False
        
    except requests.exceptions.Timeout:
        print("❌ CRITICAL ERROR: Request timed out after 30 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CRITICAL ERROR: Connection failed - {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ CRITICAL ERROR: Invalid JSON response - {str(e)}")
        print(f"Response Text: {response.text}")
        return False
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Unexpected error - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_money_managers_api()
    exit(0 if success else 1)
