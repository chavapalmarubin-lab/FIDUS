import requests
import json
from datetime import datetime

# Login
login = requests.post(
    "http://localhost:8001/api/auth/login",
    json={"username": "admin", "password": "password123", "user_type": "admin"}
)
token = login.json()['token']

# Get cash flow
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8001/api/admin/cashflow/complete", headers=headers)

data = response.json()

print("="*80)
print("BROKER REBATES - MONTHLY CALCULATION")
print("="*80)
print()
print(f"Current Month: {data.get('current_month', 'N/A')}")
print(f"Period Type: {data.get('broker_rebates_period', 'N/A')}")
print(f"Start Date: {data.get('broker_rebates_start_date', 'N/A')}")
print(f"End Date: {data.get('broker_rebates_end_date', 'N/A')}")
print(f"Days Elapsed: {data.get('broker_rebates_days', 0)}")
print()
print(f"Total Trades: {data.get('trades_count', 0)}")
print(f"Total Volume: {data.get('total_volume_lots', 0):.2f} lots")
print(f"Broker Rebates: ${data.get('broker_rebates', 0):,.2f}")
print()
print("="*80)
print("CASH FLOW SUMMARY")
print("="*80)
print()
print("Fund Assets (Inflows):")
print(f"  MT5 Trading P&L: ${data['total_profit_loss']:,.2f}")
print(f"  Broker Interest (Separation): ${data['broker_interest']:,.2f}")
print(f"  Broker Rebates (THIS MONTH): ${data['broker_rebates']:,.2f}")
print(f"  TOTAL INFLOWS: ${data['total_inflows']:,.2f}")
print()
print(f"✅ Broker rebates now calculated from start of {data.get('current_month', 'month')} to today")
print()

