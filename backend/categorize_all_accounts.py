"""
Categorize ALL MT5 accounts by capital source using deal history
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

def format_ts(ts):
    try:
        if isinstance(ts, str):
            return ts[:19]
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M')
    except:
        return str(ts)[:19]

async def categorize_accounts():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("CATEGORIZING ALL ACCOUNTS BY CAPITAL SOURCE")
    print("Using MT5 Deal History as Source of Truth")
    print("="*80)
    print()
    
    # Get all accounts from mt5_accounts
    all_accounts = await db.mt5_accounts.find({}).to_list(None)
    
    print(f"Found {len(all_accounts)} accounts in mt5_accounts collection")
    print()
    
    # Get all balance deals (type=2)
    all_balance_deals = await db.mt5_deals_history.find(
        {"type": 2}
    ).sort("time", 1).to_list(length=None)
    
    print(f"Analyzing {len(all_balance_deals)} balance deals...")
    print()
    
    # Categorize each account
    account_categories = {}
    
    for account in all_accounts:
        account_id = account.get('account_id')
        fund_type = account.get('fund_type', 'Unknown')
        
        # Get all balance deals for this account
        account_deals = [
            d for d in all_balance_deals 
            if d.get('account_number') == account_id
        ]
        
        # Find client deposits (Deposit-CTFBP)
        client_deposits = [
            d for d in account_deals
            if 'Deposit-CTFBP' in d.get('comment', '').upper()
        ]
        
        # Find if account received money from separation accounts
        from_separation = [
            d for d in account_deals
            if d.get('profit', 0) > 0 
            and ('886528' in d.get('comment', '') or '897591' in d.get('comment', ''))
            and 'Transfer from #' in d.get('comment', '')
        ]
        
        # Categorize
        if client_deposits:
            # Has direct client deposit
            client_deposit_amount = sum([
                float(d['profit'].to_decimal() if hasattr(d['profit'], 'to_decimal') else d['profit'])
                for d in client_deposits
            ])
            
            category = 'client'
            initial_amount = client_deposit_amount
            notes = f"Client deposit: ${client_deposit_amount:,.2f}"
            
        elif from_separation:
            # Funded from separation (reinvested profit)
            reinvest_amount = sum([
                float(d['profit'].to_decimal() if hasattr(d['profit'], 'to_decimal') else d['profit'])
                for d in from_separation
            ])
            
            category = 'reinvested_profit'
            initial_amount = reinvest_amount
            notes = f"Reinvested from separation: ${reinvest_amount:,.2f}"
            
        elif account_id in [897591, 897599]:
            # Separation accounts
            category = 'separation'
            initial_amount = 0
            notes = "Separation account (holds extracted profits)"
            
        else:
            # Check if it's the FIDUS capital account (891215 with $14,662.94)
            if account_id == 891215:
                category = 'fidus'
                initial_amount = 14662.94
                notes = "FIDUS house capital"
            else:
                # Unknown - needs manual review
                category = 'unknown'
                initial_amount = 0
                notes = "No clear capital source - check manually"
        
        account_categories[account_id] = {
            'account_id': account_id,
            'fund_type': fund_type,
            'capital_source': category,
            'initial_amount': initial_amount,
            'current_equity': float(account.get('equity', 0)),
            'notes': notes
        }
    
    # Print categorization
    print("="*80)
    print("ACCOUNT CATEGORIZATION RESULTS")
    print("="*80)
    print()
    
    # Group by category
    by_category = defaultdict(list)
    for acc_id, info in account_categories.items():
        by_category[info['capital_source']].append(info)
    
    # Print each category
    for category in ['client', 'fidus', 'reinvested_profit', 'separation', 'unknown']:
        accounts = by_category.get(category, [])
        if not accounts:
            continue
            
        print(f"\n{'='*80}")
        print(f"📊 {category.upper().replace('_', ' ')}")
        print(f"{'='*80}\n")
        
        total_initial = sum([a['initial_amount'] for a in accounts])
        total_current = sum([a['current_equity'] for a in accounts])
        
        for acc in sorted(accounts, key=lambda x: x['account_id']):
            print(f"Account {acc['account_id']} ({acc['fund_type']})")
            print(f"  Initial: ${acc['initial_amount']:,.2f}")
            print(f"  Current: ${acc['current_equity']:,.2f}")
            print(f"  Notes: {acc['notes']}")
            print()
        
        print(f"SUBTOTAL - {category.upper()}:")
        print(f"  Initial Investment: ${total_initial:,.2f}")
        print(f"  Current Equity: ${total_current:,.2f}")
        print(f"  Count: {len(accounts)} accounts")
        print()
    
    # Grand totals
    print("\n" + "="*80)
    print("GRAND TOTALS")
    print("="*80)
    
    client_total = sum([a['initial_amount'] for a in by_category['client']])
    fidus_total = sum([a['initial_amount'] for a in by_category['fidus']])
    reinvest_total = sum([a['initial_amount'] for a in by_category['reinvested_profit']])
    
    print(f"\nClient Capital: ${client_total:,.2f}")
    print(f"FIDUS Capital: ${fidus_total:,.2f}")
    print(f"Reinvested Profits: ${reinvest_total:,.2f}")
    print(f"TOTAL FUND: ${client_total + fidus_total + reinvest_total:,.2f}")
    print()
    
    # Check for unknowns
    if by_category['unknown']:
        print("\n⚠️  WARNING: Unknown capital source accounts:")
        for acc in by_category['unknown']:
            print(f"  - Account {acc['account_id']} ({acc['fund_type']})")
        print("\nThese need manual review!")
    
    client.close()
    
    return account_categories

if __name__ == "__main__":
    asyncio.run(categorize_accounts())
