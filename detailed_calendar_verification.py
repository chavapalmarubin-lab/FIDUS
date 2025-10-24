#!/usr/bin/env python3
"""
Detailed Calendar Verification
Get detailed calendar data to verify specific amounts and dates from the review request.
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://prospects-portal.preview.emergentagent.com/api"

def authenticate_and_get_calendar():
    """Authenticate and get detailed calendar data"""
    session = requests.Session()
    
    # Authenticate
    login_data = {
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    }
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ Authentication failed")
        return None
    
    token = response.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Get calendar data
    response = session.get(f"{BACKEND_URL}/client/client_alejandro/calendar")
    if response.status_code != 200:
        print("❌ Calendar request failed")
        return None
    
    return response.json()

def analyze_calendar_data(data):
    """Analyze calendar data in detail"""
    if not data.get("success"):
        print(f"❌ Calendar API error: {data.get('error')}")
        return
    
    calendar = data.get("calendar", {})
    
    print("🎯 DETAILED CALENDAR ANALYSIS FOR ALEJANDRO")
    print("=" * 60)
    
    # Contract Summary
    summary = calendar.get("contract_summary", {})
    print(f"\n📋 CONTRACT SUMMARY:")
    print(f"   Total Investment: ${summary.get('total_investment', 0):,.2f}")
    print(f"   Total Interest: ${summary.get('total_interest', 0):,.2f}")
    print(f"   Total Value: ${summary.get('total_value', 0):,.2f}")
    print(f"   Contract Start: {summary.get('contract_start', 'N/A')}")
    print(f"   Contract End: {summary.get('contract_end', 'N/A')}")
    print(f"   Duration: {summary.get('contract_duration_days', 0)} days")
    
    # Calendar Events Analysis
    events = calendar.get("calendar_events", [])
    print(f"\n📅 CALENDAR EVENTS ({len(events)} total):")
    
    # Group events by type
    events_by_type = {}
    for event in events:
        event_type = event.get("type", "unknown")
        if event_type not in events_by_type:
            events_by_type[event_type] = []
        events_by_type[event_type].append(event)
    
    for event_type, type_events in events_by_type.items():
        print(f"\n   {event_type.upper()} ({len(type_events)} events):")
        for event in sorted(type_events, key=lambda x: x.get("date", "")):
            date = event.get("date", "")
            if isinstance(date, str):
                date = date[:10]  # Get YYYY-MM-DD
            else:
                date = date.strftime("%Y-%m-%d") if date else "N/A"
            
            fund = event.get("fund_code", "")
            amount = event.get("amount", 0)
            title = event.get("title", "")
            
            if amount > 0:
                print(f"     {date} | {fund:7} | ${amount:>8,.2f} | {title}")
            else:
                print(f"     {date} | {fund:7} | {'':>10} | {title}")
    
    # Monthly Timeline Analysis
    timeline = calendar.get("monthly_timeline", {})
    print(f"\n📊 MONTHLY TIMELINE ({len(timeline)} months):")
    
    for month_key in sorted(timeline.keys()):
        month_data = timeline[month_key]
        month_name = month_data.get("month_name", month_key)
        total_due = month_data.get("total_due", 0)
        core_interest = month_data.get("core_interest", 0)
        balance_interest = month_data.get("balance_interest", 0)
        principal = month_data.get("principal_amount", 0)
        
        if total_due > 0:
            print(f"\n   {month_name} (${total_due:,.2f} total):")
            if core_interest > 0:
                print(f"     CORE Interest: ${core_interest:,.2f}")
            if balance_interest > 0:
                print(f"     BALANCE Interest: ${balance_interest:,.2f}")
            if principal > 0:
                print(f"     Principal: ${principal:,.2f}")
    
    # Verify specific expected values from review request
    print(f"\n🔍 VERIFICATION AGAINST REVIEW REQUEST:")
    
    # Check December 2025 CORE payment
    dec_2025 = timeline.get("2025-12", {})
    dec_core = dec_2025.get("core_interest", 0)
    expected_core = 272.27
    
    if abs(dec_core - expected_core) < 1:
        print(f"   ✅ December 2025 CORE payment: ${dec_core:.2f} (expected ~${expected_core})")
    else:
        print(f"   ❌ December 2025 CORE payment: ${dec_core:.2f} (expected ~${expected_core})")
    
    # Check February 2026 combined payment
    feb_2026 = timeline.get("2026-02", {})
    feb_total = feb_2026.get("total_due", 0)
    expected_feb_total = 7772.27
    
    if abs(feb_total - expected_feb_total) < 10:
        print(f"   ✅ February 2026 total payment: ${feb_total:.2f} (expected ~${expected_feb_total})")
    else:
        print(f"   ❌ February 2026 total payment: ${feb_total:.2f} (expected ~${expected_feb_total})")
    
    # Check total investment
    total_inv = summary.get('total_investment', 0)
    expected_total = 118151.41
    
    if abs(total_inv - expected_total) < 1:
        print(f"   ✅ Total investment: ${total_inv:.2f} (expected ${expected_total})")
    else:
        print(f"   ❌ Total investment: ${total_inv:.2f} (expected ${expected_total})")
    
    # Check contract duration
    duration = summary.get('contract_duration_days', 0)
    if duration == 426:
        print(f"   ✅ Contract duration: {duration} days (expected 426)")
    else:
        print(f"   ❌ Contract duration: {duration} days (expected 426)")

if __name__ == "__main__":
    data = authenticate_and_get_calendar()
    if data:
        analyze_calendar_data(data)
    else:
        print("❌ Failed to get calendar data")