"""
MT5 TRUTH ANALYSIS - Separate Client Deposits from Internal Transfers
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

async def analyze():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("="*80)
    print("MT5 DEAL HISTORY - SOURCE OF TRUTH ANALYSIS")
    print("="*80)
    print()
    
    # Get ALL balance-type deals (type=2)
    all_balance_deals = await db.mt5_deals_history.find(
        {"type": 2}
    ).sort("time", 1).to_list(length=None)
    
    print(f"Total Balance Deals: {len(all_balance_deals)}")
    print()
    
    # Categorize deals
    client_deposits = []
    profit_withdrawals = []
    internal_transfers = []
    fees = []
    other = []
    
    for deal in all_balance_deals:
        comment = deal.get('comment', '').lower()
        profit = deal.get('profit', 0)
        
        if hasattr(profit, 'to_decimal'):
            profit = float(profit.to_decimal())
        
        deal_info = {
            'account': deal.get('account_number'),
            'time': format_ts(deal.get('time')),
            'amount': profit,
            'comment': deal.get('comment', '')
        }
        
        # Categorize
        if 'deposit-ctfbp' in comment:
            client_deposits.append(deal_info)
        elif 'transfer from #' in comment or 'transfer to #' in comment or 'trf from' in comment:
            internal_transfers.append(deal_info)
        elif 'fee #' in comment:
            fees.append(deal_info)
        elif 'p/l share' in comment:
            pass  # Skip P/L shares (trading profits)
        else:
            other.append(deal_info)
    
    # === REPORT ===
    
    print("="*80)
    print("1️⃣  TRUE CLIENT DEPOSITS (Source: MT5 Deal History)")
    print("="*80)
    print()
    print("These are the ONLY real money coming IN from clients:")
    print()
    
    total_client_deposits = 0
    for i, d in enumerate(client_deposits, 1):
        total_client_deposits += d['amount']
        print(f"{i}. Account {d['account']} | {d['time']}")
        print(f"   Amount: ${d['amount']:,.2f}")
        print(f"   Comment: '{d['comment']}'")
        print()
    
    print(f"✅ TOTAL TRUE CLIENT DEPOSITS: ${total_client_deposits:,.2f}")
    print()
    print()
    
    # Check if this matches Chava's expected $118,151.41
    if abs(total_client_deposits - 118151.41) < 1:
        print("✅ MATCHES Expected: $118,151.41 from Alejandro Mariscal Romero")
    elif abs(total_client_deposits - 132814.35) < 1:
        print("⚠️  TOTAL: $132,814.35 (includes unexpected $14,662.94 deposit)")
    else:
        print(f"⚠️  TOTAL DEPOSITS: ${total_client_deposits:,.2f}")
    
    print()
    print()
    
    print("="*80)
    print("2️⃣  INTERNAL TRANSFERS (Between Trading Accounts)")
    print("="*80)
    print()
    print("These are NOT client deposits - just money moving between accounts:")
    print()
    
    # Group transfers by account
    transfers_by_account = defaultdict(list)
    for t in internal_transfers:
        transfers_by_account[t['account']].append(t)
    
    print(f"Total Internal Transfer Transactions: {len(internal_transfers)}")
    print()
    
    # Show first 20 significant transfers
    significant = [t for t in internal_transfers if abs(t['amount']) > 1000]
    print(f"Significant Transfers (>$1,000): {len(significant)}")
    print()
    print("First 20:")
    for i, t in enumerate(significant[:20], 1):
        direction = "➡️ OUT" if t['amount'] < 0 else "⬅️  IN"
        print(f"{i}. Account {t['account']} | {t['time']} | {direction} ${abs(t['amount']):,.2f}")
        print(f"   '{t['comment']}'")
        print()
    
    print()
    print("="*80)
    print("3️⃣  FEES CHARGED")
    print("="*80)
    print()
    
    total_fees = sum([f['amount'] for f in fees])
    print(f"Total Fees: ${abs(total_fees):,.2f}")
    for f in fees:
        print(f"  Account {f['account']} | {f['time']} | ${f['amount']:,.2f}")
        print(f"  '{f['comment']}'")
        print()
    
    print()
    print("="*80)
    print("4️⃣  PROFIT MOVEMENTS TO SEPARATION ACCOUNTS")
    print("="*80)
    print()
    
    # Find transfers TO separation accounts (897591, 897599)
    separation_accounts = [897591, 897599]
    transfers_to_separation = [
        t for t in internal_transfers 
        if t['account'] in separation_accounts and t['amount'] > 0
    ]
    
    print(f"Transfers TO Separation Accounts: {len(transfers_to_separation)}")
    total_to_separation = sum([t['amount'] for t in transfers_to_separation])
    print(f"Total Amount: ${total_to_separation:,.2f}")
    print()
    
    for t in transfers_to_separation:
        print(f"  Account {t['account']} | {t['time']} | ${t['amount']:,.2f}")
        print(f"  '{t['comment']}'")
        print()
    
    print()
    print("="*80)
    print("5️⃣  THE $5,000 'PROBLEM' - Account 897589")
    print("="*80)
    print()
    
    # Find all balance deals for 897589
    deals_897589 = [t for t in internal_transfers if t['account'] == 897589]
    
    if deals_897589:
        print(f"Account 897589 Balance Transactions:")
        for d in deals_897589:
            print(f"  {d['time']} | ${d['amount']:,.2f}")
            print(f"  '{d['comment']}'")
            print()
        
        # Check if any came from separation
        from_separation = [d for d in deals_897589 if '886528' in d['comment'] or '897591' in d['comment']]
        if from_separation:
            print("✅ CONFIRMED: The $5,000 in account 897589 came from SEPARATION account")
            print("   This is REINVESTED PROFIT, not client money")
    else:
        print("❌ No balance transactions found for account 897589")
    
    print()
    print()
    print("="*80)
    print("SUMMARY & CONCLUSIONS")
    print("="*80)
    print()
    print(f"✅ Total TRUE Client Deposits: ${total_client_deposits:,.2f}")
    print(f"📊 Total Internal Transfers: {len(internal_transfers)} transactions")
    print(f"💰 Total Fees Charged: ${abs(total_fees):,.2f}")
    print(f"🏦 Total to Separation: ${total_to_separation:,.2f}")
    print()
    print("RECOMMENDATION:")
    print("- Use ONLY deals with 'Deposit-CTFBP' comments as true client deposits")
    print("- ALL 'Transfer from #' are internal movements and should be ignored for P&L calc")
    print("- The correct P&L formula should be:")
    print("    TRUE P&L = Current Equity + Profit Withdrawals - TRUE Client Deposits")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(analyze())
