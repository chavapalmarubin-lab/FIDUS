#!/usr/bin/env python3
"""
System Data Check - Verify what data is actually in the system
"""

import requests
import json

def check_system_data():
    base_url = "https://fidus-google-sync.preview.emergentagent.com"
    
    # Authenticate as admin
    auth_response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin",
        "password": "password123",
        "user_type": "admin"
    })
    
    if auth_response.status_code != 200:
        print("❌ Failed to authenticate as admin")
        return
    
    token = auth_response.json().get('token')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    print("🔍 SYSTEM DATA CHECK")
    print("=" * 50)
    
    # Check all clients
    print("\n📋 ALL CLIENTS:")
    clients_response = requests.get(f"{base_url}/api/clients/all", headers=headers)
    if clients_response.status_code == 200:
        clients = clients_response.json().get('clients', [])
        for client in clients:
            print(f"   - {client.get('name')} (ID: {client.get('id')}) - Investments: {client.get('total_investments', 0)}")
    else:
        print(f"   ❌ Failed to get clients: {clients_response.status_code}")
    
    # Check investment overview
    print("\n💰 INVESTMENT OVERVIEW:")
    inv_response = requests.get(f"{base_url}/api/investments/admin/overview", headers=headers)
    if inv_response.status_code == 200:
        overview = inv_response.json()
        print(f"   Total Investments: {overview.get('total_investments', 0)}")
        print(f"   Total Clients: {overview.get('total_clients', 0)}")
        print(f"   Total AUM: ${overview.get('total_aum', 0):,.2f}")
        
        fund_summaries = overview.get('fund_summaries', [])
        for fund in fund_summaries:
            print(f"   {fund.get('fund_code')}: {fund.get('investment_count', 0)} investments, ${fund.get('total_amount', 0):,.2f}")
    else:
        print(f"   ❌ Failed to get investment overview: {inv_response.status_code}")
    
    # Check Salvador specifically
    print("\n👤 SALVADOR PALMA SPECIFIC DATA:")
    salvador_id = "client_003"
    
    # Check Salvador's investments
    salvador_inv_response = requests.get(f"{base_url}/api/investments/client/{salvador_id}", headers=headers)
    if salvador_inv_response.status_code == 200:
        salvador_data = salvador_inv_response.json()
        investments = salvador_data.get('investments', [])
        print(f"   Salvador's Investments: {len(investments)}")
        for inv in investments:
            print(f"     - {inv.get('fund_code')}: ${inv.get('principal_amount', 0):,.2f} (Deposit: {inv.get('deposit_date', 'N/A')})")
    else:
        print(f"   ❌ Failed to get Salvador's investments: {salvador_inv_response.status_code}")
    
    # Check MT5 accounts
    print("\n🔗 MT5 ACCOUNTS:")
    mt5_response = requests.get(f"{base_url}/api/mt5/admin/accounts", headers=headers)
    if mt5_response.status_code == 200:
        mt5_data = mt5_response.json()
        accounts = mt5_data.get('accounts', [])
        print(f"   Total MT5 Accounts: {len(accounts)}")
        for acc in accounts:
            print(f"     - Login: {acc.get('mt5_login')} (Client: {acc.get('client_id')}, Broker: {acc.get('broker_name')})")
    else:
        print(f"   ❌ Failed to get MT5 accounts: {mt5_response.status_code}")
    
    # Check fund performance dashboard
    print("\n📊 FUND PERFORMANCE DASHBOARD:")
    perf_response = requests.get(f"{base_url}/api/admin/fund-performance/dashboard", headers=headers)
    if perf_response.status_code == 200:
        perf_data = perf_response.json()
        fund_performance = perf_data.get('fund_performance', [])
        print(f"   Fund Performance Entries: {len(fund_performance)}")
        for entry in fund_performance:
            print(f"     - Client: {entry.get('client_id')}, Fund: {entry.get('fund_code')}, Amount: ${entry.get('principal_amount', 0):,.2f}")
    else:
        print(f"   ❌ Failed to get fund performance: {perf_response.status_code}")

if __name__ == "__main__":
    check_system_data()