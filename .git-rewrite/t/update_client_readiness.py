#!/usr/bin/env python3
"""
Update multiple clients to be investment ready
"""

import requests
import json
from datetime import datetime, timezone

BACKEND_URL = "https://fidus-invest.emergent.host/api"

def authenticate_admin():
    """Authenticate as admin"""
    login_payload = {
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    return None

def update_client_readiness(admin_token, client_id, client_name):
    """Update client readiness"""
    update_data = {
        "aml_kyc_completed": True,
        "agreement_signed": True,
        "account_creation_date": datetime.now(timezone.utc).isoformat(),
        "updated_by": "admin_001",
        "notes": f"Updated for investment readiness - {datetime.now(timezone.utc).isoformat()}"
    }
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.put(f"{BACKEND_URL}/clients/{client_id}/readiness", json=update_data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            readiness = data.get("readiness", {})
            investment_ready = readiness.get("investment_ready", False)
            print(f"✅ Updated {client_name} - Investment Ready: {investment_ready}")
            return True
    
    print(f"❌ Failed to update {client_name}")
    return False

def main():
    print("🔧 Updating Client Readiness Status...")
    
    # Authenticate
    admin_token = authenticate_admin()
    if not admin_token:
        print("❌ Failed to authenticate as admin")
        return
    
    # Clients to update
    clients_to_update = [
        ("client_003", "SALVADOR PALMA"),
        ("client_001", "Gerardo Briones"),
        ("client_002", "Maria Rodriguez"),
        ("client_004", "Javier Gonzalez"),
        ("client_005", "Jorge Gonzalez")
    ]
    
    updated_count = 0
    for client_id, client_name in clients_to_update:
        if update_client_readiness(admin_token, client_id, client_name):
            updated_count += 1
    
    print(f"\n🎯 Updated {updated_count}/{len(clients_to_update)} clients")
    
    # Check ready clients endpoint
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BACKEND_URL}/clients/ready-for-investment", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        ready_clients = data.get("ready_clients", [])
        print(f"\n📋 Ready Clients ({len(ready_clients)}):")
        for client in ready_clients:
            print(f"   • {client.get('name')} ({client.get('client_id')}) - {client.get('email')}")
    else:
        print("❌ Failed to check ready clients endpoint")

if __name__ == "__main__":
    main()