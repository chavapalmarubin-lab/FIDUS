#!/usr/bin/env python3

import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.append('/app/backend')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def debug_fund_portfolio_endpoint():
    """Debug the fund portfolio endpoint to see what's happening"""
    try:
        print("🔍 Debugging fund portfolio endpoint...")
        
        # Import required modules
        from fund_performance_calculator import get_all_funds_performance, calculate_fund_weighted_performance
        print("✅ Successfully imported fund_performance_calculator")
        
        # Import database connection (same as server.py)
        import os
        from motor.motor_asyncio import AsyncIOMotorClient
        from dotenv import load_dotenv
        from pathlib import Path
        
        ROOT_DIR = Path('/app/backend')
        load_dotenv(ROOT_DIR / '.env')
        
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(
            mongo_url,
            minPoolSize=5,
            maxPoolSize=100,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=10000,
            connectTimeoutMS=10000,
            retryWrites=True
        )
        db = client[os.environ.get('DB_NAME', 'fidus_production')]
        print("✅ Successfully created database connection (same as server.py)")
        
        # Import FIDUS_FUND_CONFIG (same as server.py)
        from server import FIDUS_FUND_CONFIG
        print(f"✅ FIDUS_FUND_CONFIG has {len(FIDUS_FUND_CONFIG)} funds")
        
        # Execute the exact same logic as the fund-portfolio/overview endpoint
        print("\n🔄 Executing fund-portfolio/overview endpoint logic...")
        
        funds_overview = {}
        
        # Get all investments directly from MongoDB
        investments_cursor = db.investments.find({})
        all_investments = await investments_cursor.to_list(length=None)
        print(f"✅ Found {len(all_investments)} investments")
        
        # Get MT5 accounts for allocation details
        mt5_cursor = db.mt5_accounts.find({})
        all_mt5_accounts = await mt5_cursor.to_list(length=None)
        print(f"✅ Found {len(all_mt5_accounts)} MT5 accounts")
        
        # Get weighted performance for all funds
        all_performance = await get_all_funds_performance(db)
        print(f"✅ Got performance data: {list(all_performance.keys())}")
        
        for fund_code, fund_config in FIDUS_FUND_CONFIG.items():
            print(f"\n🔍 Processing {fund_code} fund...")
            
            # Calculate fund AUM from investments
            fund_investments = [inv for inv in all_investments if inv.get('fund_code') == fund_code]
            fund_aum = sum(inv.get('principal_amount', 0) for inv in fund_investments)
            total_investors = len(set(inv.get('client_id') for inv in fund_investments))
            print(f"   Fund investments: {len(fund_investments)}, AUM: ${fund_aum}, Investors: {total_investors}")
            
            # Get MT5 allocations for this fund
            # Note: MT5 accounts use 'fund_type' field, not 'fund_code'
            fund_mt5_accounts = [mt5 for mt5 in all_mt5_accounts if mt5.get('fund_type') == fund_code]
            total_mt5_allocation = sum(mt5.get('balance', 0) for mt5 in fund_mt5_accounts)
            mt5_account_count = len(fund_mt5_accounts)
            print(f"   MT5 accounts: {mt5_account_count}, MT5 allocation: ${total_mt5_allocation}")
            
            # Get weighted performance for this fund
            fund_performance = all_performance.get('funds', {}).get(fund_code, {})
            weighted_return = fund_performance.get('weighted_return', 0.0)
            total_true_pnl = fund_performance.get('total_true_pnl', 0.0)
            print(f"   Performance: {weighted_return}% return, ${total_true_pnl} P&L")
            
            funds_overview[fund_code] = {
                "fund_code": fund_code,
                "fund_name": fund_config.name,
                "fund_type": fund_code,
                "aum": round(fund_aum, 2),
                "total_investors": total_investors,
                "interest_rate": fund_config.interest_rate,
                "client_investments": round(fund_aum, 2),
                "minimum_investment": fund_config.minimum_investment,
                "mt5_allocation": round(total_mt5_allocation, 2),
                "mt5_accounts_count": mt5_account_count,  # THIS IS THE KEY FIELD!
                "allocation_match": abs(fund_aum - total_mt5_allocation) < 0.01,
                "performance_ytd": round(weighted_return, 2),
                "nav_per_share": round(1.0 + (weighted_return / 100), 4),
                "total_true_pnl": round(total_true_pnl, 2),
                "management_fee": 0.0,
                "performance_fee": 0.0,
                "total_rebates": 0.0
            }
            print(f"   ✅ Created fund overview with mt5_accounts_count: {mt5_account_count}")
        
        total_aum = sum(fund["aum"] for fund in funds_overview.values())
        total_investors = sum(fund["total_investors"] for fund in funds_overview.values())
        portfolio_weighted_return = all_performance.get('portfolio_totals', {}).get('weighted_return', 0.0)
        
        result = {
            "success": True,
            "funds": funds_overview,
            "total_aum": round(total_aum, 2),
            "aum": round(total_aum, 2),
            "ytd_return": round(portfolio_weighted_return, 2),
            "total_investors": total_investors,
            "fund_count": len([f for f in funds_overview.values() if f["aum"] > 0])
        }
        
        print(f"\n✅ Successfully created response with {len(result['funds'])} funds")
        
        # Check if mt5_accounts_count is in the response
        for fund_code, fund_data in result['funds'].items():
            mt5_count = fund_data.get('mt5_accounts_count', 'MISSING')
            print(f"   {fund_code}: mt5_accounts_count = {mt5_count}")
        
        print(f"\n🎉 Endpoint logic completed successfully!")
        print(f"📊 Result summary:")
        print(f"   - Total AUM: ${result['total_aum']}")
        print(f"   - Total Investors: {result['total_investors']}")
        print(f"   - YTD Return: {result['ytd_return']}%")
        print(f"   - Fund Count: {result['fund_count']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in debug: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(debug_fund_portfolio_endpoint())
    if result:
        print(f"\n✅ Debug completed successfully - the endpoint should return mt5_accounts_count!")
    else:
        print(f"\n❌ Debug failed - there's an issue with the endpoint logic")