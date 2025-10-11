"""
FUND CALCULATION FIX - Add Separation Account to Fund Assets
Resolves missing separation interest in fund profitability calculations
"""

import asyncio
from datetime import datetime, timezone
from config.database import get_database

async def fix_fund_calculations():
    """
    Add comprehensive fund calculation including separation account
    """
    try:
        print("🏦 IMPLEMENTING FUND CALCULATION FIX...")
        
        # Get database connection
        db = await get_database()
        
        # Get all MT5 accounts
        mt5_accounts = await db.mt5_accounts.find({}).to_list(length=None)
        
        print(f"📊 Found {len(mt5_accounts)} MT5 accounts")
        
        # Calculate fund components
        separation_accounts = [acc for acc in mt5_accounts if acc.get('fund_code') == 'INTEREST_SEPARATION']
        trading_accounts = [acc for acc in mt5_accounts if acc.get('fund_code') in ['CORE', 'BALANCE', 'DYNAMIC', 'UNLIMITED']]
        
        print(f"💰 Separation accounts: {len(separation_accounts)}")
        print(f"📈 Trading accounts: {len(trading_accounts)}")
        
        # Calculate separation interest (revenue)
        total_separation_interest = 0
        for acc in separation_accounts:
            balance = float(acc.get('balance', 0))
            total_separation_interest += balance
            print(f"   Account {acc.get('account_id', acc.get('mt5_login'))}: ${balance:.2f}")
        
        # Calculate MT5 trading profits/losses  
        total_mt5_profit_loss = 0
        for acc in trading_accounts:
            profit_loss = float(acc.get('profit_loss', 0))
            total_mt5_profit_loss += profit_loss
            print(f"   Account {acc.get('account_id', acc.get('mt5_login'))}: ${profit_loss:.2f}")
        
        # Calculate total fund assets (separation + trading)
        total_fund_assets = total_separation_interest + total_mt5_profit_loss
        
        # Get all investments to calculate obligations
        investments = await db.investments.find({}).to_list(length=None)
        
        total_client_obligations = 0
        for inv in investments:
            principal = float(inv.get('principal_amount', 0))
            total_client_obligations += principal
        
        # Calculate net profitability (assets - obligations)
        net_fund_profitability = total_fund_assets - total_client_obligations
        
        print(f"\n📊 FUND CALCULATION RESULTS:")
        print(f"   💰 Separation Interest: ${total_separation_interest:,.2f}")
        print(f"   📈 MT5 Trading P&L: ${total_mt5_profit_loss:,.2f}")
        print(f"   🏦 Total Fund Assets: ${total_fund_assets:,.2f}")
        print(f"   📋 Client Obligations: ${total_client_obligations:,.2f}")
        print(f"   💎 Net Profitability: ${net_fund_profitability:+,.2f}")
        
        # Store calculation in database for API access
        calculation_result = {
            'calculation_timestamp': datetime.now(timezone.utc),
            'separation_interest': total_separation_interest,
            'mt5_trading_pnl': total_mt5_profit_loss,
            'total_fund_assets': total_fund_assets,
            'client_obligations': total_client_obligations,
            'net_fund_profitability': net_fund_profitability,
            'separation_accounts_count': len(separation_accounts),
            'trading_accounts_count': len(trading_accounts),
            'calculation_method': 'autonomous_fix_v1'
        }
        
        # Update or insert the calculation
        await db.fund_calculations.replace_one(
            {'_id': 'current'},
            {'_id': 'current', **calculation_result},
            upsert=True
        )
        
        print(f"✅ Fund calculation stored in database")
        
        return calculation_result
        
    except Exception as e:
        print(f"❌ Fund calculation fix failed: {str(e)}")
        return None

# Run the fund calculation fix
if __name__ == "__main__":
    print("🚨 EXECUTING FUND CALCULATION FIX")
    result = asyncio.run(fix_fund_calculations())
    if result:
        print("✅ FUND CALCULATION FIX SUCCESSFUL")
        print(f"Net Fund Profitability: ${result['net_fund_profitability']:+,.2f}")
    else:
        print("❌ FUND CALCULATION FIX FAILED")