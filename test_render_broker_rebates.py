#!/usr/bin/env python3
import requests
import json

BACKEND_URL = "https://fidus-api.onrender.com"

print("="*80)
print("TESTING RENDER PRODUCTION API - BROKER REBATES")
print("="*80)
print()

# Login
print("Step 1: Authenticating...")
try:
    login_response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"username": "admin", "password": "password123", "user_type": "admin"},
        timeout=15
    )
    
    if login_response.status_code == 200:
        token = login_response.json().get('token')
        print("✅ Successfully authenticated")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {str(e)}")
    exit(1)

print()
print("Step 2: Getting Cash Flow data...")

try:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BACKEND_URL}/api/admin/cashflow/complete",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ Cash Flow API Response Received")
        print()
        print("="*80)
        print("BROKER REBATES DATA FROM RENDER")
        print("="*80)
        print()
        print(f"Current Month: {data.get('current_month', 'N/A')}")
        print(f"Period Type: {data.get('broker_rebates_period', 'N/A')}")
        print(f"Start Date: {data.get('broker_rebates_start_date', 'N/A')}")
        print(f"Days Elapsed: {data.get('broker_rebates_days', 0)}")
        print()
        print(f"Total Trades: {data.get('trades_count', 0):,}")
        print(f"Total Volume: {data.get('total_volume_lots', 0):.2f} lots")
        print(f"Broker Rebates: ${data.get('broker_rebates', 0):,.2f}")
        print()
        print("="*80)
        print("CASH FLOW SUMMARY")
        print("="*80)
        print()
        print("Fund Assets (Inflows):")
        print(f"  MT5 Trading P&L: ${data.get('total_profit_loss', 0):,.2f}")
        print(f"  Broker Interest: ${data.get('broker_interest', 0):,.2f}")
        print(f"  Broker Rebates: ${data.get('broker_rebates', 0):,.2f}")
        print(f"  TOTAL INFLOWS: ${data.get('total_inflows', 0):,.2f}")
        print()
        
        # Verify correct calculation
        broker_rebates = data.get('broker_rebates', 0)
        expected_range_low = 1500
        expected_range_high = 1800
        
        if expected_range_low <= broker_rebates <= expected_range_high:
            print(f"✅ VERIFIED: Broker rebates ${broker_rebates:,.2f} is in expected range (${expected_range_low}-${expected_range_high})")
        else:
            print(f"⚠️  WARNING: Broker rebates ${broker_rebates:,.2f} outside expected range")
        
    else:
        print(f"❌ API request failed: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

