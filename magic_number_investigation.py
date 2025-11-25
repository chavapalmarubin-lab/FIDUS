#!/usr/bin/env python3
"""
URGENT MAGIC NUMBER INVESTIGATION FOR TRADING ANALYTICS

Context: We need to investigate the magic numbers in the mt5_deals_history collection 
to understand manager-level trading data. The current Trading Analytics is showing 
$36,893.50 but it should be ~$10,000.

Investigation Tasks:
1. Login as Admin (admin/password123)
2. Query mt5_deals_history collection to group deals by magic number
3. Calculate total P&L per magic number
4. Count deals per magic number  
5. Identify accounts associated with each magic
6. Check for BALANCE ADJUSTMENT deals (deposits/withdrawals that inflate P&L)
7. Report findings in specified format

Expected Findings:
- BALANCE ADJUSTMENT deals are inflating the total P&L
- True trading P&L (excluding deposits/withdrawals) should be closer to $10,000
- Magic numbers identify different managers/strategies
"""

import requests
import json
import sys
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os

# Backend URL from environment
BACKEND_URL = "https://truth-fincore.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class MagicNumberInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.mongo_client = None
        self.db = None
        self.investigation_results = {}
        
    def connect_to_mongodb(self):
        """Connect to MongoDB to investigate mt5_deals_history collection"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client['fidus_production']
            
            # Test connection
            self.mongo_client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def authenticate(self):
        """Authenticate as admin and get JWT token"""
        try:
            auth_url = f"{BACKEND_URL}/api/auth/login"
            payload = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            }
            
            response = self.session.post(auth_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    print(f"✅ Successfully authenticated as {ADMIN_USERNAME}")
                    return True
                else:
                    print("❌ No token in response")
                    return False
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
    
    def investigate_magic_numbers(self):
        """Run the required aggregation query to group deals by magic number"""
        try:
            print("\n🔍 INVESTIGATING MAGIC NUMBERS IN MT5_DEALS_HISTORY COLLECTION")
            print("=" * 80)
            
            # Check if collection exists
            collections = self.db.list_collection_names()
            if 'mt5_deals_history' not in collections:
                print("❌ mt5_deals_history collection not found!")
                print(f"Available collections: {collections}")
                return False
            
            # Get total document count
            total_deals = self.db.mt5_deals_history.count_documents({})
            print(f"📊 Total deals in mt5_deals_history: {total_deals:,}")
            
            if total_deals == 0:
                print("❌ No deals found in mt5_deals_history collection")
                return False
            
            # Run the required aggregation query
            print("\n🔍 Running aggregation query to group by magic number...")
            
            pipeline = [
                {
                    "$group": {
                        "_id": "$magic",
                        "count": {"$sum": 1},
                        "total_profit": {"$sum": "$profit"},
                        "accounts": {"$addToSet": "$account"}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            magic_results = list(self.db.mt5_deals_history.aggregate(pipeline))
            
            if not magic_results:
                print("❌ No results from aggregation query")
                return False
            
            print(f"✅ Found {len(magic_results)} different magic numbers")
            
            # Store results for reporting
            self.investigation_results['magic_numbers'] = magic_results
            
            # Calculate totals
            total_trades = sum(result['count'] for result in magic_results)
            total_pnl = sum(result['total_profit'] for result in magic_results)
            
            self.investigation_results['totals'] = {
                'total_trades': total_trades,
                'total_pnl': total_pnl
            }
            
            print(f"📊 AGGREGATION RESULTS:")
            print(f"   Total Magic Numbers: {len(magic_results)}")
            print(f"   Total Trades: {total_trades:,}")
            print(f"   Total P&L: ${total_pnl:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error investigating magic numbers: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def check_balance_adjustments(self):
        """Check for BALANCE ADJUSTMENT deals that inflate P&L"""
        try:
            print("\n🔍 CHECKING FOR BALANCE ADJUSTMENT DEALS")
            print("=" * 50)
            
            # Search for deals with balance adjustment keywords in comments
            balance_keywords = ["BALANCE", "DEPOSIT", "WITHDRAWAL", "ADJUSTMENT"]
            
            balance_deals = []
            total_balance_profit = 0
            
            for keyword in balance_keywords:
                # Case-insensitive search in comment field
                query = {"comment": {"$regex": keyword, "$options": "i"}}
                deals = list(self.db.mt5_deals_history.find(query))
                
                for deal in deals:
                    if deal not in balance_deals:  # Avoid duplicates
                        balance_deals.append(deal)
                        total_balance_profit += deal.get('profit', 0)
            
            print(f"📊 BALANCE ADJUSTMENT ANALYSIS:")
            print(f"   Balance Adjustment Deals Found: {len(balance_deals)}")
            print(f"   Total Balance Adjustment Profit: ${total_balance_profit:,.2f}")
            
            # Store results
            self.investigation_results['balance_adjustments'] = {
                'count': len(balance_deals),
                'total_profit': total_balance_profit,
                'deals': balance_deals[:10]  # Store first 10 for sample
            }
            
            # Show sample balance adjustment deals
            if balance_deals:
                print(f"\n📋 SAMPLE BALANCE ADJUSTMENT DEALS (first 5):")
                for i, deal in enumerate(balance_deals[:5]):
                    print(f"   {i+1}. Deal ID: {deal.get('deal', 'N/A')}, "
                          f"Account: {deal.get('account', 'N/A')}, "
                          f"Profit: ${deal.get('profit', 0):,.2f}, "
                          f"Comment: {deal.get('comment', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking balance adjustments: {str(e)}")
            return False
    
    def get_sample_deals_by_magic(self):
        """Get 2-3 sample deals for each magic number"""
        try:
            print("\n🔍 GETTING SAMPLE DEALS FOR EACH MAGIC NUMBER")
            print("=" * 50)
            
            magic_samples = {}
            
            for magic_result in self.investigation_results.get('magic_numbers', []):
                magic_number = magic_result['_id']
                
                # Get 3 sample deals for this magic number
                sample_deals = list(self.db.mt5_deals_history.find(
                    {"magic": magic_number}
                ).limit(3))
                
                magic_samples[magic_number] = sample_deals
            
            self.investigation_results['magic_samples'] = magic_samples
            
            print(f"✅ Retrieved sample deals for {len(magic_samples)} magic numbers")
            return True
            
        except Exception as e:
            print(f"❌ Error getting sample deals: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate the required report format"""
        try:
            print("\n" + "=" * 80)
            print("📊 MAGIC NUMBER INVESTIGATION REPORT")
            print("=" * 80)
            
            magic_results = self.investigation_results.get('magic_numbers', [])
            totals = self.investigation_results.get('totals', {})
            balance_adjustments = self.investigation_results.get('balance_adjustments', {})
            magic_samples = self.investigation_results.get('magic_samples', {})
            
            # Report format as requested
            print("\n🎯 MAGIC NUMBER BREAKDOWN:")
            for result in magic_results:
                magic_num = result['_id']
                count = result['count']
                profit = result['total_profit']
                accounts = result['accounts']
                
                print(f"Magic #{magic_num}: {count:,} trades, ${profit:,.2f} P&L, Accounts: {accounts}")
            
            print(f"\nTOTAL: {totals.get('total_trades', 0):,} trades, ${totals.get('total_pnl', 0):,.2f} P&L")
            
            # Check if total is approximately $10,000
            expected_pnl = 10000
            actual_pnl = totals.get('total_pnl', 0)
            is_close_to_expected = abs(actual_pnl - expected_pnl) < 5000  # Within $5k
            
            print(f"Does total ≈ $10,000? {'YES' if is_close_to_expected else 'NO'}")
            
            # Balance adjustments report
            print(f"\n🔍 BALANCE ADJUSTMENTS:")
            balance_count = balance_adjustments.get('count', 0)
            balance_profit = balance_adjustments.get('total_profit', 0)
            
            print(f"Balance adjustment deals found: {balance_count}")
            print(f"Total balance adjustment profit: ${balance_profit:,.2f}")
            
            # Calculate true trading P&L (excluding balance adjustments)
            true_trading_pnl = actual_pnl - balance_profit
            print(f"True trading P&L (excluding adjustments): ${true_trading_pnl:,.2f}")
            
            # Sample deals for each magic number
            print(f"\n📋 SAMPLE DEALS BY MAGIC NUMBER:")
            for magic_num, samples in magic_samples.items():
                print(f"\nMagic #{magic_num} samples:")
                for i, deal in enumerate(samples[:3]):
                    deal_id = deal.get('deal', 'N/A')
                    symbol = deal.get('symbol', 'N/A')
                    profit = deal.get('profit', 0)
                    comment = deal.get('comment', 'N/A')
                    
                    print(f"  {i+1}. Deal ID: {deal_id}, Symbol: {symbol}, "
                          f"Profit: ${profit:,.2f}, Comment: {comment}")
            
            # Manager identification strategy
            print(f"\n🎯 MANAGER IDENTIFICATION STRATEGY:")
            print("Magic numbers can be used to identify different managers/strategies:")
            
            for result in magic_results:
                magic_num = result['_id']
                count = result['count']
                profit = result['total_profit']
                
                if count > 100:  # Significant trading activity
                    avg_profit_per_trade = profit / count if count > 0 else 0
                    print(f"  Magic #{magic_num}: {count:,} trades, "
                          f"Avg ${avg_profit_per_trade:.2f}/trade - "
                          f"{'Profitable' if profit > 0 else 'Loss-making'} strategy")
            
            # Key findings summary
            print(f"\n🔍 KEY FINDINGS:")
            print(f"1. Current Trading Analytics shows: ${actual_pnl:,.2f}")
            print(f"2. Expected amount should be: ~${expected_pnl:,.2f}")
            print(f"3. Balance adjustments found: {balance_count} deals worth ${balance_profit:,.2f}")
            print(f"4. True trading P&L: ${true_trading_pnl:,.2f}")
            
            if balance_profit > 5000:
                print(f"5. ⚠️  BALANCE ADJUSTMENTS ARE INFLATING P&L by ${balance_profit:,.2f}")
                print(f"6. 🎯 Recommendation: Exclude balance adjustments from trading analytics")
            else:
                print(f"5. ✅ Balance adjustments are minimal (${balance_profit:,.2f})")
            
            if abs(true_trading_pnl - expected_pnl) < 2000:
                print(f"7. ✅ True trading P&L (${true_trading_pnl:,.2f}) is close to expected ${expected_pnl:,.2f}")
            else:
                print(f"7. ⚠️  True trading P&L (${true_trading_pnl:,.2f}) differs from expected ${expected_pnl:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating report: {str(e)}")
            return False
    
    def run_investigation(self):
        """Run complete magic number investigation"""
        print("🔍 URGENT MAGIC NUMBER INVESTIGATION FOR TRADING ANALYTICS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Connect to MongoDB
        print("📋 STEP 1: Connect to MongoDB")
        if not self.connect_to_mongodb():
            return False
        
        # Step 2: Authenticate as Admin
        print("\n📋 STEP 2: Authenticate as Admin")
        if not self.authenticate():
            return False
        
        # Step 3: Investigate Magic Numbers
        print("\n📋 STEP 3: Investigate Magic Numbers")
        if not self.investigate_magic_numbers():
            return False
        
        # Step 4: Check Balance Adjustments
        print("\n📋 STEP 4: Check Balance Adjustments")
        if not self.check_balance_adjustments():
            return False
        
        # Step 5: Get Sample Deals
        print("\n📋 STEP 5: Get Sample Deals by Magic Number")
        if not self.get_sample_deals_by_magic():
            return False
        
        # Step 6: Generate Report
        print("\n📋 STEP 6: Generate Investigation Report")
        if not self.generate_report():
            return False
        
        print("\n✅ MAGIC NUMBER INVESTIGATION COMPLETED SUCCESSFULLY")
        return True

def main():
    """Main investigation execution"""
    investigator = MagicNumberInvestigation()
    success = investigator.run_investigation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()