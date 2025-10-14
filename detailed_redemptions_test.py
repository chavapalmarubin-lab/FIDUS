#!/usr/bin/env python3
"""
Detailed Redemptions Endpoint Testing - Verify Specific Requirements
"""

import requests
import json
from datetime import datetime, timezone

# Configuration
BACKEND_URL = "https://fidus-trade.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def login_as_alejandro():
    """Login as Alejandro to get JWT token"""
    response = requests.post(f"{API_BASE}/auth/login", json={
        "username": "alejandro_mariscal",
        "password": "password123",
        "user_type": "client"
    }, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('token')
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_redemptions_endpoint():
    """Test the redemptions endpoint and print detailed results"""
    print("🎯 DETAILED REDEMPTIONS ENDPOINT TESTING")
    print("=" * 60)
    
    # Login
    token = login_as_alejandro()
    if not token:
        print("❌ Failed to authenticate")
        return
    
    print("✅ Successfully authenticated as Alejandro")
    
    # Test redemptions endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/redemptions/client/client_alejandro", 
                          headers=headers, timeout=15)
    
    if response.status_code != 200:
        print(f"❌ Redemptions endpoint failed: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    print(f"✅ Redemptions endpoint returned HTTP 200")
    print(f"✅ Response success: {data.get('success')}")
    
    # Print full response structure
    print("\n📋 FULL RESPONSE STRUCTURE:")
    print(json.dumps(data, indent=2, default=str))
    
    # Analyze investments
    available_redemptions = data.get('available_redemptions', [])
    print(f"\n📊 INVESTMENT ANALYSIS:")
    print(f"   Total investments found: {len(available_redemptions)}")
    
    for i, investment in enumerate(available_redemptions, 1):
        print(f"\n🏦 INVESTMENT {i}:")
        print(f"   Fund Code: {investment.get('fund_code')}")
        print(f"   Fund Name: {investment.get('fund_name')}")
        print(f"   Principal Amount: ${investment.get('principal_amount')}")
        print(f"   Deposit Date: {investment.get('deposit_date')}")
        print(f"   Interest Start Date: {investment.get('interest_start_date')}")
        print(f"   Status: {investment.get('status')}")
        print(f"   Redemption Frequency: {investment.get('redemption_frequency')}")
        
        schedule = investment.get('redemption_schedule', [])
        print(f"   Redemption Schedule: {len(schedule)} payments")
        
        if schedule:
            print(f"   First Payment: {schedule[0].get('date')} - ${schedule[0].get('amount')} ({schedule[0].get('type')})")
            print(f"   Last Payment: {schedule[-1].get('date')} - ${schedule[-1].get('amount')} ({schedule[-1].get('type')})")
            
            # Check for NaN or Invalid Date
            nan_count = 0
            invalid_date_count = 0
            
            for payment in schedule:
                amount = payment.get('amount')
                date_str = payment.get('date')
                
                if amount is None or (isinstance(amount, float) and str(amount).lower() == 'nan'):
                    nan_count += 1
                
                if not date_str or date_str == 'Invalid Date':
                    invalid_date_count += 1
            
            print(f"   NaN Amounts: {nan_count}")
            print(f"   Invalid Dates: {invalid_date_count}")
    
    print(f"\n🎯 VERIFICATION SUMMARY:")
    print(f"   ✅ Endpoint returns 200 OK: YES")
    print(f"   ✅ Success field is true: {data.get('success')}")
    print(f"   ✅ Available redemptions present: {len(available_redemptions) > 0}")
    print(f"   ✅ Both CORE and BALANCE funds: {len([i for i in available_redemptions if i.get('fund_code') in ['CORE', 'BALANCE']]) == 2}")
    print(f"   ✅ No $NaN amounts found: {all(not (amount is None or (isinstance(amount, float) and str(amount).lower() == 'nan')) for inv in available_redemptions for payment in inv.get('redemption_schedule', []) for amount in [payment.get('amount')])}")
    print(f"   ✅ No Invalid Dates found: {all(date_str and date_str != 'Invalid Date' for inv in available_redemptions for payment in inv.get('redemption_schedule', []) for date_str in [payment.get('date')])}")

if __name__ == "__main__":
    test_redemptions_endpoint()