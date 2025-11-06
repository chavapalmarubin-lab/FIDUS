"""
Test the Three-Tier P&L Calculator
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.three_tier_pnl_calculator import ThreeTierPnLCalculator
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_calculator():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    calculator = ThreeTierPnLCalculator(db)
    
    print("="*80)
    print("TESTING THREE-TIER P&L CALCULATOR")
    print("="*80)
    print()
    
    # Test 1: Admin View (All Three Tiers)
    print("TEST 1: Admin View (All Tiers)")
    print("-"*80)
    admin_view = await calculator.get_admin_view()
    print(json.dumps(admin_view, indent=2, default=str))
    print()
    
    # Test 2: Client View (Alejandro)
    print("\nTEST 2: Client View (Alejandro)")
    print("-"*80)
    client_view = await calculator.get_client_view('client_alejandro')
    print(json.dumps(client_view, indent=2, default=str))
    print()
    
    # Test 3: Individual Tier Calculations
    print("\nTEST 3: Individual Tier Details")
    print("-"*80)
    
    print("\n📊 CLIENT TIER:")
    client_tier = await calculator.calculate_tier_pnl('client', 'client_alejandro')
    print(f"  Investment: ${client_tier['initial_allocation']:,.2f}")
    print(f"  Current Equity: ${client_tier['current_equity']:,.2f}")
    print(f"  Withdrawals: ${client_tier['profit_withdrawals']:,.2f}")
    print(f"  P&L: ${client_tier['true_pnl']:,.2f}")
    print(f"  Return: {client_tier['return_percent']:.2f}%")
    print(f"  Accounts: {client_tier['account_count']}")
    
    print("\n📊 FIDUS TIER:")
    fidus_tier = await calculator.calculate_tier_pnl('fidus')
    print(f"  Investment: ${fidus_tier['initial_allocation']:,.2f}")
    print(f"  Current Equity: ${fidus_tier['current_equity']:,.2f}")
    print(f"  Withdrawals: ${fidus_tier['profit_withdrawals']:,.2f}")
    print(f"  P&L: ${fidus_tier['true_pnl']:,.2f}")
    print(f"  Return: {fidus_tier['return_percent']:.2f}%")
    print(f"  Accounts: {fidus_tier['account_count']}")
    
    print("\n📊 REINVESTED TIER:")
    reinvest_tier = await calculator.calculate_tier_pnl('reinvested_profit')
    print(f"  Investment: ${reinvest_tier['initial_allocation']:,.2f}")
    print(f"  Current Equity: ${reinvest_tier['current_equity']:,.2f}")
    print(f"  P&L: ${reinvest_tier['true_pnl']:,.2f}")
    print(f"  Accounts: {reinvest_tier['account_count']}")
    
    print()
    print("="*80)
    print("✅ THREE-TIER P&L CALCULATOR TEST COMPLETE")
    print("="*80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_calculator())
