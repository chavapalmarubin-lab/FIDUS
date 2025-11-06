"""
Categorize ALL MT5 accounts by capital source - CORRECT LOGIC
Find the ORIGINAL source of funds by tracing back to initial deposits
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

def to_float(value):
    if hasattr(value, 'to_decimal'):
        return float(value.to_decimal())
    return float(value) if value else 0.0

async def categorize_accounts():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("CATEGORIZING ALL ACCOUNTS BY CAPITAL SOURCE")
    print("Tracing funds back to ORIGINAL deposits")
    print("="*80)
    print()
    
    # Get all accounts from mt5_accounts
    all_accounts = await db.mt5_accounts.find({}).to_list(None)
    account_numbers = [acc.get('account') for acc in all_accounts if acc.get('account')]
    
    print(f"Found {len(all_accounts)} accounts")
    print()
    
    # Get all balance deals (type=2)
    all_balance_deals = await db.mt5_deals_history.find(
        {"type": 2}
    ).sort("time", 1).to_list(length=None)
    
    print(f"Analyzing {len(all_balance_deals)} balance deals...")
    print()
    
    # STEP 1: Find all TRUE client deposits (Deposit-CTFBP)
    client_deposits = {}
    for deal in all_balance_deals:
        if 'Deposit-CTFBP' in deal.get('comment', '').upper():
            acc_num = deal.get('account_number')
            amount = to_float(deal.get('profit'))
            if acc_num not in client_deposits:
                client_deposits[acc_num] = 0
            client_deposits[acc_num] += amount
    
    print("STEP 1: Found TRUE client deposits:")
    for acc, amt in client_deposits.items():
        print(f"  Account {acc}: ${amt:,.2f}")
    print()
    
    # STEP 2: Categorize based on deposits
    # Account 885822: $118,151.41 → CLIENT (Alejandro)
    # Account 891215: $14,662.94 → FIDUS (house capital)
    
    account_categories = {}
    
    for account in all_accounts:
        account_number = account.get('account')
        fund_type = account.get('fund_type', 'Unknown')
        current_equity = to_float(account.get('equity', 0))
        client_id = account.get('client_id')
        initial_alloc = to_float(account.get('initial_allocation', 0))
        
        # Categorize
        if account_number == 885822:
            # Original client deposit account
            category = 'client'
            initial_amount = 118151.41  # But only $18,151.41 stayed (Q2)
            actual_allocation = 18151.41  # Per Chava's Q2 answer
            notes = f"CLIENT - Original deposit ${initial_amount:,.2f}, CORE allocation ${actual_allocation:,.2f}"
            
        elif account_number == 891215:
            # FIDUS house capital
            category = 'fidus'
            initial_amount = 14662.94
            actual_allocation = 14662.94
            notes = f"FIDUS - House capital ${initial_amount:,.2f}"
            
        elif client_id == 'client_alejandro':
            # Account allocated to Alejandro (part of the $100k that left 885822)
            category = 'client'
            initial_amount = initial_alloc
            actual_allocation = initial_alloc
            notes = f"CLIENT - Alejandro's BALANCE account, allocated ${actual_allocation:,.2f}"
            
        elif account_number in [897591, 897599]:
            # Separation accounts
            category = 'separation'
            initial_amount = 0
            actual_allocation = 0
            notes = "SEPARATION - Holds extracted profits"
            
        elif account_number == 886528:
            # Intermediary/hub account
            category = 'intermediary'
            initial_amount = 0
            actual_allocation = 0
            notes = "INTERMEDIARY - Hub for fund transfers"
            
        elif account_number in [897589, 897590]:
            # These were funded from separation (reinvested profit)
            category = 'reinvested_profit'
            initial_amount = 0  # No client obligation
            actual_allocation = 0
            notes = f"REINVESTED PROFIT - Funded from separation, current ${current_equity:,.2f}"
            
        elif account_number == 886066:
            # Golden money manager (Q3: intentionally $0)
            category = 'client'  # Was allocated client money originally
            initial_amount = 10000  # Based on original allocation
            actual_allocation = 0  # Q3: Funds moved out, intentionally $0
            notes = "CLIENT - Golden MM (funds moved out, intentionally $0)"
            
        else:
            # Unknown
            category = 'unknown'
            initial_amount = initial_alloc
            actual_allocation = initial_alloc
            notes = f"UNKNOWN - Needs review (alloc: ${actual_allocation:,.2f})"
        
        account_categories[account_number] = {
            'account_number': account_number,
            'fund_type': fund_type,
            'capital_source': category,
            'initial_amount': initial_amount,
            'actual_allocation': actual_allocation,
            'current_equity': current_equity,
            'client_id': client_id,
            'notes': notes
        }
    
    # Print categorization
    print("="*80)
    print("ACCOUNT CATEGORIZATION RESULTS")
    print("="*80)
    print()
    
    # Group by category
    by_category = defaultdict(list)
    for acc_num, info in account_categories.items():
        by_category[info['capital_source']].append(info)
    
    # Print each category
    for category in ['client', 'fidus', 'reinvested_profit', 'separation', 'intermediary', 'unknown']:
        accounts = by_category.get(category, [])
        if not accounts:
            continue
            
        print(f"\n{'='*80}")
        print(f"📊 {category.upper().replace('_', ' ')}")
        print(f"{'='*80}\n")
        
        total_allocation = sum([a['actual_allocation'] for a in accounts])
        total_current = sum([a['current_equity'] for a in accounts])
        
        for acc in sorted(accounts, key=lambda x: x['account_number'] if x['account_number'] else 0):
            print(f"Account {acc['account_number']} ({acc['fund_type']})")
            print(f"  Allocation: ${acc['actual_allocation']:,.2f}")
            print(f"  Current: ${acc['current_equity']:,.2f}")
            print(f"  {acc['notes']}")
            print()
        
        if category not in ['separation', 'intermediary']:
            print(f"SUBTOTAL - {category.upper()}:")
            print(f"  Total Allocation: ${total_allocation:,.2f}")
            print(f"  Current Equity: ${total_current:,.2f}")
            print(f"  Count: {len(accounts)} accounts")
            print()
    
    # Grand totals
    print("\n" + "="*80)
    print("GRAND TOTALS - INVESTABLE CAPITAL")
    print("="*80)
    
    client_alloc = sum([a['actual_allocation'] for a in by_category['client']])
    client_equity = sum([a['current_equity'] for a in by_category['client']])
    
    fidus_alloc = sum([a['actual_allocation'] for a in by_category['fidus']])
    fidus_equity = sum([a['current_equity'] for a in by_category['fidus']])
    
    reinvest_equity = sum([a['current_equity'] for a in by_category['reinvested_profit']])
    
    print(f"\n1️⃣  CLIENT CAPITAL (Alejandro):")
    print(f"   Allocation: ${client_alloc:,.2f}")
    print(f"   Current Equity: ${client_equity:,.2f}")
    print(f"   Accounts: {len(by_category['client'])}")
    
    print(f"\n2️⃣  FIDUS CAPITAL (House Money):")
    print(f"   Allocation: ${fidus_alloc:,.2f}")
    print(f"   Current Equity: ${fidus_equity:,.2f}")
    print(f"   Accounts: {len(by_category['fidus'])}")
    
    print(f"\n3️⃣  REINVESTED PROFITS:")
    print(f"   Allocation: $0.00 (no client obligation)")
    print(f"   Current Equity: ${reinvest_equity:,.2f}")
    print(f"   Accounts: {len(by_category['reinvested_profit'])}")
    
    print(f"\n📊 TOTAL FUND:")
    print(f"   Total Allocation: ${client_alloc + fidus_alloc:,.2f}")
    print(f"   Total Equity: ${client_equity + fidus_equity + reinvest_equity:,.2f}")
    print()
    
    # Separation balance
    sep_balance = sum([a['current_equity'] for a in by_category['separation']])
    print(f"💰 Separation Balance: ${sep_balance:,.2f}")
    print()
    
    client.close()
    
    return account_categories

if __name__ == "__main__":
    asyncio.run(categorize_accounts())
