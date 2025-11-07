import requests
import json

# Login
login = requests.post(
    "http://localhost:8001/api/auth/login",
    json={"username": "admin", "password": "password123", "user_type": "admin"}
)
token = login.json()['token']

# Get managers
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8001/api/admin/money-managers", headers=headers)

data = response.json()

print("="*80)
print("MONEY MANAGERS API RESPONSE")
print("="*80)
print(f"\nTotal Managers: {data.get('count', 0)}")
print()

for i, mgr in enumerate(data.get('managers', []), 1):
    print(f"{i}. Manager:")
    print(f"   manager_name: {mgr.get('manager_name', 'N/A')}")
    print(f"   execution_type: {mgr.get('execution_type', 'N/A')}")
    
    perf = mgr.get('performance', {})
    print(f"   Performance:")
    print(f"     total_allocated: ${perf.get('total_allocated', 0):,.2f}")
    print(f"     current_equity: ${perf.get('current_equity', 0):,.2f}")
    print(f"     total_pnl: ${perf.get('total_pnl', 0):,.2f}")
    print(f"     true_pnl: ${perf.get('true_pnl', 0):,.2f}")
    
    # Calculate what it SHOULD be
    allocated = perf.get('total_allocated', 0)
    equity = perf.get('current_equity', 0)
    correct_pnl = equity - allocated
    print(f"   CORRECT P&L should be: ${correct_pnl:,.2f}")
    print()

