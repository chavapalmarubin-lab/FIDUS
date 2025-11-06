"""
Check ALL 11 accounts equity - COMPLETE PORTFOLIO
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

def to_float(value):
    if hasattr(value, 'to_decimal'):
        return float(value.to_decimal())
    return float(value) if value else 0.0

async def check_all_equity():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("ALL 11 ACCOUNTS - COMPLETE PORTFOLIO EQUITY")
    print("="*80)
    print()
    
    # Get ALL accounts
    all_accounts = await db.mt5_accounts.find({}).sort('account', 1).to_list(None)
    
    print(f"Found {len(all_accounts)} accounts\n")
    
    by_source = {}
    grand_total = 0
    
    for acc in all_accounts:
        acc_num = acc.get('account')
        fund_type = acc.get('fund_type', 'Unknown')
        capital_source = acc.get('capital_source', 'unknown')
        initial = to_float(acc.get('initial_allocation', 0))
        equity = to_float(acc.get('equity', 0))
        
        if capital_source not in by_source:
            by_source[capital_source] = {
                'accounts': [],
                'total_initial': 0,
                'total_equity': 0
            }
        
        by_source[capital_source]['accounts'].append({
            'account': acc_num,
            'fund_type': fund_type,
            'initial': initial,
            'equity': equity
        })
        by_source[capital_source]['total_initial'] += initial
        by_source[capital_source]['total_equity'] += equity
        grand_total += equity
    
    # Print by category
    for source in ['client', 'fidus', 'reinvested_profit', 'separation', 'intermediary']:
        if source not in by_source:
            continue
            
        data = by_source[source]
        print(f"\n{'='*80}")
        print(f"📊 {source.upper().replace('_', ' ')}")
        print(f"{'='*80}\n")
        
        for acc in data['accounts']:
            print(f"Account {acc['account']} ({acc['fund_type']}):")
            print(f"  Initial: ${acc['initial']:,.2f}")
            print(f"  Equity: ${acc['equity']:,.2f}")
            print()
        
        print(f"SUBTOTAL - {source.upper()}:")
        print(f"  Initial: ${data['total_initial']:,.2f}")
        print(f"  Equity: ${data['total_equity']:,.2f}")
        print()
    
    print("="*80)
    print(f"🎯 GRAND TOTAL - ALL 11 ACCOUNTS")
    print("="*80)
    print(f"Total Initial Allocation: ${sum([by_source[s]['total_initial'] for s in by_source]):,.2f}")
    print(f"Total Current Equity: ${grand_total:,.2f}")
    print()
    
    # Calculate CLIENT view (all accounts equity)
    client_investment = 118151.41
    separation_balance = by_source.get('separation', {}).get('total_equity', 0)
    
    print("="*80)
    print(f"📊 ALEJANDRO'S COMPLETE PORTFOLIO VALUE")
    print("="*80)
    print(f"Initial Investment: ${client_investment:,.2f}")
    print(f"Total Portfolio Equity (all accounts): ${grand_total:,.2f}")
    print(f"  - Separation Balance: ${separation_balance:,.2f}")
    print(f"  - Trading Accounts: ${grand_total - separation_balance:,.2f}")
    print()
    print(f"Total Value: ${grand_total:,.2f}")
    print(f"P&L: ${grand_total - client_investment:,.2f}")
    print(f"Return: {(grand_total - client_investment) / client_investment * 100:.2f}%")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_all_equity())
