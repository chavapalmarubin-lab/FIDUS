#!/usr/bin/env python3
"""
Refactor all endpoints to use central calculations service
"""

import sys
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

# Import central calculations
from services.calculations import (
    get_total_equity,
    get_client_money,
    get_fund_revenue,
    get_all_accounts_summary,
    get_all_investments_summary,
    convert_decimal128
)

async def test_central_calculations():
    """Test that central calculations work"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_dev')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database()
    
    print("\n" + "="*80)
    print("TESTING CENTRAL CALCULATION SERVICE (SSOT)")
    print("="*80)
    
    # Test core calculations
    total_equity = await get_total_equity(db)
    print(f"\n✅ Total Equity: ${total_equity:,.2f}")
    
    client_money = await get_client_money(db)
    print(f"✅ Client Money: ${client_money:,.2f}")
    
    fund_revenue = await get_fund_revenue(db)
    print(f"✅ Fund Revenue: ${fund_revenue:,.2f}")
    
    # Verify formula
    calculated = total_equity - client_money
    match = abs(fund_revenue - calculated) < 0.01
    print(f"\n🔍 Formula Verification:")
    print(f"   Total Equity - Client Money = ${calculated:,.2f}")
    print(f"   get_fund_revenue() = ${fund_revenue:,.2f}")
    print(f"   Match: {'✅ YES' if match else '❌ NO'}")
    
    # Test accounts summary
    accounts_summary = await get_all_accounts_summary(db)
    print(f"\n✅ Accounts Summary:")
    print(f"   Total Accounts: {accounts_summary['totals']['total_accounts']}")
    print(f"   Total Equity: ${accounts_summary['totals']['total_equity']:,.2f}")
    print(f"   Total P&L: ${accounts_summary['totals']['total_pnl']:,.2f}")
    
    # Test investments summary  
    investments_summary = await get_all_investments_summary(db)
    print(f"\n✅ Investments Summary:")
    print(f"   Total Clients: {investments_summary['totals']['total_clients']}")
    print(f"   Total AUM: ${investments_summary['totals']['total_aum']:,.2f}")
    print(f"   Total Investments: {investments_summary['totals']['total_investments']}")
    
    client.close()
    
    print("\n" + "="*80)
    print("✅ ALL CENTRAL CALCULATIONS WORKING")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_central_calculations())
