"""
MT5 Deal History Analysis Script - CORRECTED FIELD NAME
Purpose: Extract complete transaction history using account_number
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()

# MT5 Deal Type Mapping
DEAL_TYPE_MAP = {
    0: "BUY",
    1: "SELL", 
    2: "BALANCE",  # Deposits, withdrawals, transfers
}

def format_timestamp(ts):
    """Convert Unix timestamp to readable date"""
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(ts)

async def analyze_mt5_deals():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    print("=" * 80)
    print("PHASE 1: MT5 DEAL HISTORY ANALYSIS - CORRECTED")
    print("=" * 80)
    print()
    
    # Priority Accounts Analysis
    print("ANALYZING PRIORITY ACCOUNTS")
    print("=" * 80)
    
    priority_accounts = [
        (885822, "CORE - $18k deposit"),
        (886557, "BALANCE - Part of $100k"),
        (886602, "BALANCE - Part of $100k"),
        (891215, "BALANCE - Part of $100k"),
        (897589, "BALANCE - The $5k problem"),
        (886066, "BALANCE - The $10k now $0"),
        (891234, "CORE"),
        (897590, "CORE"),
        (897591, "SEPARATION"),
        (897599, "SEPARATION"),
    ]
    
    for account_num, description in priority_accounts:
        # Query by account_number not account_id
        deals = await db.mt5_deals_history.find(
            {"account_number": account_num}
        ).sort("time", 1).to_list(length=None)
        
        print(f"\n{'=' * 80}")
        print(f"📊 ACCOUNT {account_num} - {description}")
        print(f"{'=' * 80}")
        
        if deals:
            print(f"Total Deals: {len(deals)}\n")
            
            # Filter BALANCE type deals (type 2) for deposits/withdrawals/transfers
            balance_deals = [d for d in deals if d.get('type') == 2]
            trade_deals = [d for d in deals if d.get('type') in [0, 1]]
            
            if balance_deals:
                print(f"💰 BALANCE OPERATIONS ({len(balance_deals)} deals):")
                print("-" * 80)
                
                running_total = 0
                for idx, deal in enumerate(balance_deals, 1):
                    deal_time = format_timestamp(deal.get('time', 'N/A'))
                    profit = deal.get('profit', 0)
                    comment = deal.get('comment', '')
                    
                    if hasattr(profit, 'to_decimal'):
                        profit = float(profit.to_decimal())
                    
                    running_total += profit
                    
                    print(f"{idx:3}. {deal_time}")
                    print(f"     Amount: ${profit:12,.2f} | Running Total: ${running_total:12,.2f}")
                    print(f"     Comment: '{comment}'")
                    print()
            
            if trade_deals:
                print(f"\n📈 TRADING OPERATIONS ({len(trade_deals)} deals):")
                print("-" * 80)
                
                total_trading_profit = sum([
                    float(d.get('profit', 0).to_decimal()) if hasattr(d.get('profit', 0), 'to_decimal') 
                    else float(d.get('profit', 0)) 
                    for d in trade_deals
                ])
                
                print(f"Total Trading P&L: ${total_trading_profit:,.2f}")
                print(f"(Not showing individual {len(trade_deals)} trades for brevity)")
                print()
        else:
            print("❌ No deals found for this account\n")
    
    # Summary of all deposit-like transactions
    print("\n" + "=" * 80)
    print("SUMMARY: ALL BALANCE TYPE DEALS (Potential Deposits/Withdrawals)")
    print("=" * 80)
    
    all_balance_deals = await db.mt5_deals_history.find(
        {"type": 2, "profit": {"$gt": 1000}}  # Focus on significant amounts
    ).sort("time", 1).to_list(length=500)  # Limit to 500
    
    print(f"\nFound {len(all_balance_deals)} balance deals > $1,000")
    print("\nGROUPED BY ACCOUNT:\n")
    
    from collections import defaultdict
    account_balance_deals = defaultdict(list)
    
    for deal in all_balance_deals:
        acc_num = deal.get('account_number')
        profit = deal.get('profit', 0)
        if hasattr(profit, 'to_decimal'):
            profit = float(profit.to_decimal())
        
        account_balance_deals[acc_num].append({
            'time': format_timestamp(deal.get('time')),
            'amount': profit,
            'comment': deal.get('comment', '')
        })
    
    for acc_num in sorted(account_balance_deals.keys()):
        deals_list = account_balance_deals[acc_num]
        total_deposits = sum([d['amount'] for d in deals_list])
        
        print(f"\nAccount {acc_num}:")
        print(f"  Total Deposits: ${total_deposits:,.2f}")
        print(f"  Number of Transactions: {len(deals_list)}")
        for d in deals_list:
            print(f"    - {d['time']}: ${d['amount']:,.2f} | '{d['comment']}'")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(analyze_mt5_deals())
