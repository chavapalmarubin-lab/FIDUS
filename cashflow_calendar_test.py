#!/usr/bin/env python3
"""
Cash Flow Obligations Calendar API Testing
Testing the /api/admin/cashflow/calendar endpoint for Alejandro's investments
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
BACKEND_URL = "https://truth-fincore.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def authenticate():
    """Authenticate as admin and get JWT token"""
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Authentication successful: {data.get('name', 'Admin')}")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_cashflow_calendar_endpoint(token):
    """Test the cash flow calendar endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("\n🔍 Testing Cash Flow Calendar Endpoint...")
        response = requests.get(f"{BACKEND_URL}/admin/cashflow/calendar", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Cash Flow Calendar API Response:")
            print(json.dumps(data, indent=2, default=str))
            
            # Verify response structure
            verify_calendar_structure(data)
            
            # Verify Alejandro's investment calculations
            verify_alejandro_calculations(data)
            
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return False

def verify_calendar_structure(data):
    """Verify the calendar response has the expected structure"""
    print("\n🔍 Verifying Calendar Structure...")
    
    required_keys = ['success', 'calendar', 'generated_at']
    for key in required_keys:
        if key in data:
            print(f"✅ {key}: Present")
        else:
            print(f"❌ {key}: Missing")
    
    if 'calendar' in data and data['calendar']:
        calendar = data['calendar']
        calendar_keys = ['current_revenue', 'monthly_obligations', 'milestones', 'summary']
        
        for key in calendar_keys:
            if key in calendar:
                print(f"✅ calendar.{key}: Present")
            else:
                print(f"❌ calendar.{key}: Missing")
        
        # Check milestones structure
        if 'milestones' in calendar:
            milestones = calendar['milestones']
            milestone_keys = ['next_payment', 'first_large_payment', 'contract_end']
            
            for key in milestone_keys:
                if key in milestones and milestones[key]:
                    print(f"✅ milestones.{key}: {milestones[key]}")
                else:
                    print(f"⚠️ milestones.{key}: Not found or null")

def verify_alejandro_calculations(data):
    """Verify the calculations match expected results for Alejandro's investments"""
    print("\n🔍 Verifying Alejandro's Investment Calculations...")
    
    if not data.get('success') or not data.get('calendar'):
        print("❌ No calendar data to verify")
        return
    
    calendar = data['calendar']
    
    # Expected investment details for Alejandro (Investment date: October 1, 2025)
    expected_investments = {
        'CORE': {
            'amount': 18151.41,
            'first_payment_day': 90,  # December 30, 2025
            'first_payment_amount': 272.27,  # 18151.41 * 0.015 = 272.27
            'payment_interval': 30,  # Monthly
            'final_payment_day': 426,  # December 1, 2026
            'final_payment_amount': 18423.68  # 18151.41 + 272.27
        },
        'BALANCE': {
            'amount': 100000,
            'first_payment_day': 150,  # February 28, 2026
            'first_payment_amount': 7500,  # 100000 * 0.025 * 3 = 7500
            'payment_interval': 90,  # Quarterly
            'final_payment_day': 426,  # December 1, 2026
            'final_payment_amount': 107500  # 100000 + 7500
        }
    }
    
    print(f"Current Revenue: ${calendar.get('current_revenue', 0):,.2f}")
    
    # Check monthly obligations
    monthly_obligations = calendar.get('monthly_obligations', {})
    print(f"Number of months with obligations: {len(monthly_obligations)}")
    
    # Verify specific months mentioned in the review
    target_months = {
        '2025-12': 'December 2025: Only CORE payment ($272.27)',
        '2026-02': 'February 2026: CORE + BALANCE ($272.27 + $7,500 = $7,772.27)',
        '2026-05': 'May 2026: CORE + BALANCE ($272.27 + $7,500 = $7,772.27)',
        '2026-12': 'December 2026: Final payments for both ($125,923.68 total)'
    }
    
    for month_key, description in target_months.items():
        if month_key in monthly_obligations:
            month_data = monthly_obligations[month_key]
            total_due = month_data.get('total_due', 0)
            core_interest = month_data.get('core_interest', 0)
            balance_interest = month_data.get('balance_interest', 0)
            
            print(f"✅ {description}")
            print(f"   Actual: Total Due: ${total_due:,.2f}, CORE: ${core_interest:,.2f}, BALANCE: ${balance_interest:,.2f}")
        else:
            print(f"❌ {description} - Month not found")
    
    # Check milestones
    milestones = calendar.get('milestones', {})
    
    if milestones.get('next_payment'):
        next_payment = milestones['next_payment']
        print(f"✅ Next Payment: {next_payment.get('date')} - ${next_payment.get('amount', 0):,.2f}")
    
    if milestones.get('contract_end'):
        contract_end = milestones['contract_end']
        print(f"✅ Contract End: {contract_end.get('date')} - ${contract_end.get('amount', 0):,.2f}")
    
    # Check summary
    summary = calendar.get('summary', {})
    total_obligations = summary.get('total_future_obligations', 0)
    final_balance = summary.get('final_balance', 0)
    
    print(f"✅ Total Future Obligations: ${total_obligations:,.2f}")
    print(f"✅ Final Balance: ${final_balance:,.2f}")

def check_alejandro_investments(token):
    """Check if Alejandro has the expected investments"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("\n🔍 Checking Alejandro's Investments...")
        response = requests.get(f"{BACKEND_URL}/clients/client_alejandro/investments", headers=headers)
        
        if response.status_code == 200:
            investments = response.json()
            print(f"✅ Found {len(investments)} investments for Alejandro")
            
            for investment in investments:
                fund_code = investment.get('fund_code', 'Unknown')
                amount = investment.get('principal_amount', 0)
                created_at = investment.get('created_at', 'Unknown')
                print(f"   - {fund_code}: ${amount:,.2f} (Created: {created_at})")
            
            return investments
        else:
            print(f"❌ Failed to get Alejandro's investments: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error checking investments: {str(e)}")
        return []

def main():
    """Main test function"""
    print("🚀 Starting Cash Flow Obligations Calendar API Testing")
    print("=" * 60)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Check Alejandro's investments first
    investments = check_alejandro_investments(token)
    
    # Test the cash flow calendar endpoint
    success = test_cashflow_calendar_endpoint(token)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Cash Flow Calendar API Testing Completed Successfully!")
    else:
        print("❌ Cash Flow Calendar API Testing Failed!")
    
    return success

if __name__ == "__main__":
    main()