import requests
import json

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
print("CASH FLOW CALCULATION RESULTS")
print("="*80)
print()
print("Fund Assets (Inflows):")
print(f"  MT5 Trading P&L: ${data['total_profit_loss']:,.2f}")
print(f"  Broker Interest: ${data['broker_interest']:,.2f}")
print(f"  Broker Rebates: ${data['broker_rebates']:,.2f}")
print(f"  TOTAL INFLOWS: ${data['total_inflows']:,.2f}")
print()
print("Fund Liabilities (Obligations):")
print(f"  Client Interest Obligations: ${data['client_interest_obligations']:,.2f}")
print(f"  Client Principal Redemptions: ${data['client_principal_redemptions']:,.2f}")
print(f"  Referral Commissions: ${data['referral_commissions']:,.2f}")
print(f"  TOTAL LIABILITIES: ${data['total_liabilities']:,.2f}")
print()
print("Net Position:")
print(f"  NET PROFIT/LOSS: ${data['net_profit']:,.2f}")
print()

# Check if fund is profitable
if data['net_profit'] > 0:
    print("✅ Fund is PROFITABLE")
elif data['net_profit'] < 0:
    print("❌ Fund is NOT profitable (net loss)")
else:
    print("⚖️  Fund is break-even")

print()
print("="*80)
