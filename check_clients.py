#!/usr/bin/env python3
import requests
import json

# Get admin token
login_response = requests.post(
    "https://invest-platform-19.preview.emergentagent.com/api/auth/login",
    json={
        "username": "admin", 
        "password": "password123",
        "user_type": "admin"
    }
)

if login_response.status_code == 200:
    token = login_response.json().get('token')
    print(f"Admin token obtained: {token[:50]}...")
    
    # Get all clients
    headers = {'Authorization': f'Bearer {token}'}
    clients_response = requests.get(
        "https://invest-platform-19.preview.emergentagent.com/api/clients/all",
        headers=headers
    )
    
    if clients_response.status_code == 200:
        clients = clients_response.json()
        print(f"\nAvailable clients:")
        for client in clients:
            print(f"  ID: {client.get('id', 'N/A')}, Name: {client.get('name', 'N/A')}, Email: {client.get('email', 'N/A')}")
    else:
        print(f"Failed to get clients: {clients_response.status_code}")
        print(clients_response.text)
else:
    print(f"Failed to login: {login_response.status_code}")
    print(login_response.text)