import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def verify_balances():
    """Verify actual MT5 account balances"""
    
    mongo_url = os.getenv('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("📊 ACTUAL MT5 ACCOUNT BALANCES:")
    print("="*80)
    
    # BALANCE Fund accounts
    print("\n💼 BALANCE FUND ACCOUNTS:")
    balance_accounts = [886557, 886602, 891215, 897589]
    balance_total_equity = 0
    
    for acc_num in balance_accounts:
        acc = await db.mt5_accounts.find_one({"account": acc_num})
        if acc:
            equity = float(acc.get("equity", 0))
            balance = float(acc.get("balance", 0))
            balance_total_equity += equity
            manager = acc.get("manager_name", "N/A")
            print(f"  Account {acc_num}: Equity ${equity:,.2f}, Balance ${balance:,.2f} - {manager}")
    
    print(f"\n  BALANCE TOTAL EQUITY: ${balance_total_equity:,.2f}")
    print(f"  BALANCE AUM (Client Investment): $100,000.00")
    print(f"  BALANCE P&L: ${balance_total_equity - 100000:,.2f}")
    
    # CORE Fund accounts
    print("\n🔴 CORE FUND ACCOUNTS:")
    core_accounts = [885822, 891234, 897590]
    core_total_equity = 0
    
    for acc_num in core_accounts:
        acc = await db.mt5_accounts.find_one({"account": acc_num})
        if acc:
            equity = float(acc.get("equity", 0))
            balance = float(acc.get("balance", 0))
            core_total_equity += equity
            manager = acc.get("manager_name", "N/A")
            print(f"  Account {acc_num}: Equity ${equity:,.2f}, Balance ${balance:,.2f} - {manager}")
    
    print(f"\n  CORE TOTAL EQUITY: ${core_total_equity:,.2f}")
    print(f"  CORE AUM (Client Investment): $18,151.41")
    print(f"  CORE P&L: ${core_total_equity - 18151.41:,.2f}")
    
    # SEPARATION accounts
    print("\n🔵 SEPARATION ACCOUNTS:")
    sep_accounts = [897591, 897599, 886528]
    sep_total_equity = 0
    
    for acc_num in sep_accounts:
        acc = await db.mt5_accounts.find_one({"account": acc_num})
        if acc:
            equity = float(acc.get("equity", 0))
            balance = float(acc.get("balance", 0))
            sep_total_equity += equity
            print(f"  Account {acc_num}: Equity ${equity:,.2f}, Balance ${balance:,.2f}")
    
    print(f"\n  SEPARATION TOTAL EQUITY: ${sep_total_equity:,.2f}")
    
    # TOTAL
    print(f"\n{'='*80}")
    print(f"TOTAL PORTFOLIO:")
    print(f"  Client AUM: $118,151.41")
    print(f"  Current Equity (Client funds): ${balance_total_equity + core_total_equity:,.2f}")
    print(f"  Separation Equity: ${sep_total_equity:,.2f}")
    print(f"  GRAND TOTAL EQUITY: ${balance_total_equity + core_total_equity + sep_total_equity:,.2f}")
    print(f"  Client P&L: ${(balance_total_equity + core_total_equity) - 118151.41:,.2f}")
    print(f"{'='*80}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_balances())
