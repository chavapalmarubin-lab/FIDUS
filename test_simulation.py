#!/usr/bin/env python3
import requests
import json

# Test the simulation endpoint directly
session = requests.Session()

# Authenticate
auth_response = session.post('https://invest-portal-31.preview.emergentagent.com/api/auth/login', json={
    'username': 'admin',
    'password': 'password123',
    'user_type': 'admin'
})

if auth_response.status_code == 200:
    token = auth_response.json().get('token')
    session.headers.update({'Authorization': f'Bearer {token}'})
    
    # Test simulation
    sim_response = session.post('https://invest-portal-31.preview.emergentagent.com/api/investments/simulate', json={
        'investments': [
            {'fund_code': 'BALANCE', 'amount': 100000},
            {'fund_code': 'DYNAMIC', 'amount': 250000}
        ],
        'timeframe_months': 24,
        'simulation_name': 'Unified Calculation Test'
    })
    
    if sim_response.status_code == 200:
        data = sim_response.json()
        simulation = data.get('simulation', {})
        
        print("=== SIMULATION RESPONSE ANALYSIS ===")
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        print()
        
        # Check fund breakdown for payment schedules
        fund_breakdown = simulation.get('fund_breakdown', [])
        for fund in fund_breakdown:
            print(f"Fund: {fund.get('fund_code')}")
            print(f"  Redemption Frequency: {fund.get('redemption_frequency')}")
            print(f"  Interest Rate: {fund.get('interest_rate')}%")
            print(f"  Total Interest: ${fund.get('total_interest')}")
            print(f"  ROI: {fund.get('roi_percentage')}%")
            
            # Check projections for payment amounts
            projections = fund.get('projections', [])
            print(f"  Projections: {len(projections)} months")
            
            # Look for interest payments in projections
            interest_payments = []
            for proj in projections:
                if proj.get('interest_earned', 0) > 0 and not proj.get('in_incubation', True):
                    interest_payments.append({
                        'month': proj.get('month'),
                        'date': proj.get('date'),
                        'interest': proj.get('interest_earned'),
                        'current_value': proj.get('current_value')
                    })
            
            print(f"  Interest Payments: {len(interest_payments)}")
            for payment in interest_payments[:8]:
                print(f"    Month {payment['month']}: ${payment['interest']} (Total: ${payment['current_value']})")
            print()
        
        # Check if there's a calendar_events field
        if 'calendar_events' in simulation:
            events = simulation['calendar_events']
            print(f"Calendar Events Found: {len(events)}")
            for event in events[:10]:
                print(f"  {event}")
        else:
            print("No calendar_events field found in simulation response")
            
        # Show all top-level keys in simulation
        print(f"Simulation keys: {list(simulation.keys())}")
        
    else:
        print('Simulation Error:', sim_response.status_code, sim_response.text)
else:
    print('Auth failed:', auth_response.status_code, auth_response.text)