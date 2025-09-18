#!/usr/bin/env python3
import requests
import json

base_url = 'https://investsim-1.preview.emergentagent.com'

# Login as admin
login_response = requests.post(f'{base_url}/api/auth/login', json={
    'username': 'admin',
    'password': 'password123', 
    'user_type': 'admin'
})

if login_response.status_code == 200:
    admin_data = login_response.json()
    token = admin_data.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get all clients
    clients_response = requests.get(f'{base_url}/api/clients/all', headers=headers)
    if clients_response.status_code == 200:
        clients_data = clients_response.json()
        clients = clients_data.get('clients', [])
        print('ALL CLIENTS IN DATABASE:')
        for client in clients:
            print(f'  ID: {client.get("id")}, Name: {client.get("name")}, Email: {client.get("email")}')
            
        # Look for Salvador specifically
        salvador_clients = [c for c in clients if 'SALVADOR' in c.get('name', '').upper() or 'PALMA' in c.get('name', '').upper()]
        if salvador_clients:
            print(f'\nSALVADOR FOUND:')
            for client in salvador_clients:
                print(f'  ID: {client.get("id")}, Name: {client.get("name")}, Email: {client.get("email")}')
                
                # Check investments for this Salvador
                inv_response = requests.get(f'{base_url}/api/investments/client/{client.get("id")}')
                if inv_response.status_code == 200:
                    inv_data = inv_response.json()
                    investments = inv_data.get('investments', [])
                    print(f'    Investments: {len(investments)}')
                    for inv in investments:
                        print(f'      Fund: {inv.get("fund_code")}, Amount: ${inv.get("current_value", 0):,.2f}')
                else:
                    print(f'    Failed to get investments: {inv_response.status_code}')
        else:
            print('\nSALVADOR NOT FOUND IN DATABASE')
            
        # Also check client_001 specifically
        print(f'\nCHECKING client_001 (Gerardo Briones):')
        gerardo_client = next((c for c in clients if c.get('id') == 'client_001'), None)
        if gerardo_client:
            print(f'  Found: {gerardo_client.get("name")} ({gerardo_client.get("email")})')
            
            # Check investments
            inv_response = requests.get(f'{base_url}/api/investments/client/client_001')
            if inv_response.status_code == 200:
                inv_data = inv_response.json()
                investments = inv_data.get('investments', [])
                print(f'    Investments: {len(investments)}')
                for inv in investments:
                    print(f'      Fund: {inv.get("fund_code")}, Amount: ${inv.get("current_value", 0):,.2f}')
            else:
                print(f'    Failed to get investments: {inv_response.status_code}')
        else:
            print('  client_001 not found')
    else:
        print(f'Failed to get clients: {clients_response.status_code}')
else:
    print(f'Failed to login as admin: {login_response.status_code}')