#!/usr/bin/env python3
import requests

session = requests.Session()

# Authenticate
auth_response = session.post('https://investor-dash-1.preview.emergentagent.com/api/auth/login', json={
    'username': 'admin',
    'password': 'password123',
    'user_type': 'admin'
})

if auth_response.status_code == 200:
    token = auth_response.json().get('token')
    session.headers.update({'Authorization': f'Bearer {token}'})
    
    # Check for existing investments
    response = session.get('https://investor-dash-1.preview.emergentagent.com/api/investments/client/client_003')
    if response.status_code == 200:
        data = response.json()
        investments = data.get('investments', [])
        print(f'Found {len(investments)} investments for client_003')
        
        for inv in investments:
            print(f'Investment: {inv.get("fund_code")} - ${inv.get("principal_amount")} - ID: {inv.get("investment_id")}')
            
            # Test projections for this investment
            inv_id = inv.get('investment_id')
            if inv_id:
                proj_response = session.get(f'https://investor-dash-1.preview.emergentagent.com/api/investments/{inv_id}/projections')
                if proj_response.status_code == 200:
                    proj_data = proj_response.json()
                    payments = proj_data.get('projected_payments', [])
                    print(f'  Projections: {len(payments)} payments')
                    for payment in payments[:5]:
                        print(f'    {payment.get("date")}: ${payment.get("amount")} ({payment.get("payment_months")} months, {payment.get("frequency")})')
                else:
                    print(f'  Projections failed: {proj_response.status_code} - {proj_response.text}')
    else:
        print(f'Failed to get investments: {response.status_code} - {response.text}')
else:
    print(f'Auth failed: {auth_response.status_code}')