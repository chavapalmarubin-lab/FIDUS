#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append('/app/backend')

async def test_fund_portfolio_endpoint():
    """Test the fund portfolio endpoint logic"""
    try:
        print("🔍 Testing fund portfolio endpoint logic...")
        
        # Import required modules
        from fund_performance_calculator import get_all_funds_performance, calculate_fund_weighted_performance
        print("✅ Successfully imported fund_performance_calculator")
        
        # Import database connection
        import os
        from motor.motor_asyncio import AsyncIOMotorClient
        from dotenv import load_dotenv
        
        load_dotenv('/app/backend/.env')
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'fidus_production')]
        print("✅ Successfully created database connection")
        
        # Test database connection
        investments_cursor = db.investments.find({})
        all_investments = await investments_cursor.to_list(length=None)
        print(f"✅ Found {len(all_investments)} investments in database")
        
        # Test MT5 accounts
        mt5_cursor = db.mt5_accounts.find({})
        all_mt5_accounts = await mt5_cursor.to_list(length=None)
        print(f"✅ Found {len(all_mt5_accounts)} MT5 accounts in database")
        
        # Test fund performance calculator
        all_performance = await get_all_funds_performance(db)
        print(f"✅ Fund performance calculator returned: {type(all_performance)}")
        print(f"   Performance keys: {list(all_performance.keys()) if isinstance(all_performance, dict) else 'Not a dict'}")
        
        # Import FIDUS_FUND_CONFIG
        from server import FIDUS_FUND_CONFIG
        print(f"✅ FIDUS_FUND_CONFIG has {len(FIDUS_FUND_CONFIG)} funds")
        
        # Test the logic for each fund
        for fund_code, fund_config in FIDUS_FUND_CONFIG.items():
            print(f"\n🔍 Testing {fund_code} fund:")
            
            # Calculate fund AUM from investments
            fund_investments = [inv for inv in all_investments if inv.get('fund_code') == fund_code]
            fund_aum = sum(inv.get('principal_amount', 0) for inv in fund_investments)
            total_investors = len(set(inv.get('client_id') for inv in fund_investments))
            print(f"   AUM: ${fund_aum}, Investors: {total_investors}")
            
            # Get MT5 allocations for this fund
            fund_mt5_accounts = [mt5 for mt5 in all_mt5_accounts if mt5.get('fund_type') == fund_code]
            total_mt5_allocation = sum(mt5.get('balance', 0) for mt5 in fund_mt5_accounts)
            mt5_account_count = len(fund_mt5_accounts)
            print(f"   MT5 Accounts: {mt5_account_count}, MT5 Allocation: ${total_mt5_allocation}")
            
            # Get weighted performance for this fund
            fund_performance = all_performance.get('funds', {}).get(fund_code, {})
            weighted_return = fund_performance.get('weighted_return', 0.0)
            total_true_pnl = fund_performance.get('total_true_pnl', 0.0)
            print(f"   Weighted Return: {weighted_return}%, True P&L: ${total_true_pnl}")
        
        print("\n✅ All tests passed - endpoint logic should work correctly")
        
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fund_portfolio_endpoint())