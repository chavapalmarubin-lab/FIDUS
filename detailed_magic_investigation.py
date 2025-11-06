#!/usr/bin/env python3
"""
DETAILED MAGIC NUMBER INVESTIGATION - DEEPER ANALYSIS

Based on initial findings:
- Only 1 magic number (#0) found with 2,668 trades
- Balance adjustments inflating P&L by $118,151.41
- True trading P&L is -$81,257.91 (significant loss)
- Expected ~$10,000 but seeing very different results

Need deeper analysis to understand:
1. What accounts are involved in these trades
2. Time distribution of trades
3. Types of deals (buy/sell vs transfers/adjustments)
4. Profit distribution analysis
5. Potential data quality issues
"""

import requests
import json
import sys
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os
from collections import defaultdict

# Backend URL from environment
BACKEND_URL = "https://fidus-fix.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class DetailedMagicInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.mongo_client = None
        self.db = None
        
    def connect_to_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client['fidus_production']
            self.mongo_client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def authenticate(self):
        """Authenticate as admin"""
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
            
            print(f"❌ Authentication failed: HTTP {response.status_code}")
            return False
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
    
    def analyze_data_structure(self):
        """Analyze the structure and quality of mt5_deals_history data"""
        try:
            print("\n🔍 ANALYZING DATA STRUCTURE AND QUALITY")
            print("=" * 60)
            
            # Get sample documents to understand structure
            sample_docs = list(self.db.mt5_deals_history.find().limit(10))
            
            if sample_docs:
                print("📋 SAMPLE DOCUMENT STRUCTURE:")
                first_doc = sample_docs[0]
                for key, value in first_doc.items():
                    print(f"   {key}: {type(value).__name__} = {value}")
                
                print(f"\n📊 FIELD ANALYSIS (from {len(sample_docs)} samples):")
                
                # Analyze field presence and types
                field_stats = defaultdict(lambda: {'count': 0, 'types': set(), 'null_count': 0})
                
                for doc in sample_docs:
                    for key, value in doc.items():
                        field_stats[key]['count'] += 1
                        field_stats[key]['types'].add(type(value).__name__)
                        if value is None or value == '':
                            field_stats[key]['null_count'] += 1
                
                for field, stats in field_stats.items():
                    types_str = ', '.join(stats['types'])
                    print(f"   {field}: {stats['count']}/{len(sample_docs)} docs, "
                          f"types: {types_str}, nulls: {stats['null_count']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing data structure: {str(e)}")
            return False
    
    def analyze_accounts_in_deals(self):
        """Analyze which accounts are involved in the deals"""
        try:
            print("\n🔍 ANALYZING ACCOUNTS IN DEALS")
            print("=" * 40)
            
            # Group by account to see distribution
            account_pipeline = [
                {
                    "$group": {
                        "_id": "$account",
                        "deal_count": {"$sum": 1},
                        "total_profit": {"$sum": "$profit"},
                        "avg_profit": {"$avg": "$profit"},
                        "min_profit": {"$min": "$profit"},
                        "max_profit": {"$max": "$profit"}
                    }
                },
                {
                    "$sort": {"deal_count": -1}
                }
            ]
            
            account_results = list(self.db.mt5_deals_history.aggregate(account_pipeline))
            
            print(f"📊 DEALS BY ACCOUNT ({len(account_results)} accounts):")
            for result in account_results:
                account = result['_id']
                count = result['deal_count']
                total_profit = result['total_profit']
                avg_profit = result['avg_profit']
                min_profit = result['min_profit']
                max_profit = result['max_profit']
                
                print(f"   Account {account}: {count:,} deals, "
                      f"Total: ${total_profit:,.2f}, "
                      f"Avg: ${avg_profit:.2f}, "
                      f"Range: ${min_profit:.2f} to ${max_profit:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing accounts: {str(e)}")
            return False
    
    def analyze_deal_types(self):
        """Analyze different types of deals based on comments and symbols"""
        try:
            print("\n🔍 ANALYZING DEAL TYPES")
            print("=" * 30)
            
            # Analyze by comment patterns
            comment_pipeline = [
                {
                    "$group": {
                        "_id": "$comment",
                        "count": {"$sum": 1},
                        "total_profit": {"$sum": "$profit"},
                        "avg_profit": {"$avg": "$profit"}
                    }
                },
                {
                    "$sort": {"count": -1}
                },
                {
                    "$limit": 20  # Top 20 comment types
                }
            ]
            
            comment_results = list(self.db.mt5_deals_history.aggregate(comment_pipeline))
            
            print(f"📊 TOP DEAL TYPES BY COMMENT:")
            for result in comment_results:
                comment = result['_id'] or 'NULL/EMPTY'
                count = result['count']
                total_profit = result['total_profit']
                avg_profit = result['avg_profit']
                
                # Truncate long comments
                display_comment = comment[:50] + "..." if len(str(comment)) > 50 else comment
                
                print(f"   '{display_comment}': {count:,} deals, "
                      f"Total: ${total_profit:,.2f}, Avg: ${avg_profit:.2f}")
            
            # Analyze by symbol
            symbol_pipeline = [
                {
                    "$group": {
                        "_id": "$symbol",
                        "count": {"$sum": 1},
                        "total_profit": {"$sum": "$profit"}
                    }
                },
                {
                    "$sort": {"count": -1}
                },
                {
                    "$limit": 10
                }
            ]
            
            symbol_results = list(self.db.mt5_deals_history.aggregate(symbol_pipeline))
            
            print(f"\n📊 TOP SYMBOLS:")
            for result in symbol_results:
                symbol = result['_id'] or 'NULL/EMPTY'
                count = result['count']
                total_profit = result['total_profit']
                
                print(f"   Symbol '{symbol}': {count:,} deals, Total: ${total_profit:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing deal types: {str(e)}")
            return False
    
    def analyze_profit_distribution(self):
        """Analyze the distribution of profits to identify outliers"""
        try:
            print("\n🔍 ANALYZING PROFIT DISTRIBUTION")
            print("=" * 35)
            
            # Get profit statistics
            profit_pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_deals": {"$sum": 1},
                        "total_profit": {"$sum": "$profit"},
                        "avg_profit": {"$avg": "$profit"},
                        "min_profit": {"$min": "$profit"},
                        "max_profit": {"$max": "$profit"}
                    }
                }
            ]
            
            profit_stats = list(self.db.mt5_deals_history.aggregate(profit_pipeline))
            
            if profit_stats:
                stats = profit_stats[0]
                print(f"📊 PROFIT STATISTICS:")
                print(f"   Total Deals: {stats['total_deals']:,}")
                print(f"   Total Profit: ${stats['total_profit']:,.2f}")
                print(f"   Average Profit: ${stats['avg_profit']:.2f}")
                print(f"   Min Profit: ${stats['min_profit']:,.2f}")
                print(f"   Max Profit: ${stats['max_profit']:,.2f}")
            
            # Find largest profit/loss deals
            print(f"\n📊 LARGEST PROFIT DEALS (Top 10):")
            largest_profits = list(self.db.mt5_deals_history.find().sort("profit", -1).limit(10))
            
            for i, deal in enumerate(largest_profits, 1):
                profit = deal.get('profit', 0)
                comment = deal.get('comment', 'N/A')
                account = deal.get('account', 'N/A')
                symbol = deal.get('symbol', 'N/A')
                
                # Truncate comment
                display_comment = comment[:40] + "..." if len(str(comment)) > 40 else comment
                
                print(f"   {i}. ${profit:,.2f} - Account: {account}, "
                      f"Symbol: {symbol}, Comment: '{display_comment}'")
            
            print(f"\n📊 LARGEST LOSS DEALS (Top 10):")
            largest_losses = list(self.db.mt5_deals_history.find().sort("profit", 1).limit(10))
            
            for i, deal in enumerate(largest_losses, 1):
                profit = deal.get('profit', 0)
                comment = deal.get('comment', 'N/A')
                account = deal.get('account', 'N/A')
                symbol = deal.get('symbol', 'N/A')
                
                # Truncate comment
                display_comment = comment[:40] + "..." if len(str(comment)) > 40 else comment
                
                print(f"   {i}. ${profit:,.2f} - Account: {account}, "
                      f"Symbol: {symbol}, Comment: '{display_comment}'")
            
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing profit distribution: {str(e)}")
            return False
    
    def identify_non_trading_deals(self):
        """Identify deals that are not actual trading (transfers, deposits, etc.)"""
        try:
            print("\n🔍 IDENTIFYING NON-TRADING DEALS")
            print("=" * 35)
            
            # Keywords that indicate non-trading deals
            non_trading_keywords = [
                "deposit", "withdrawal", "transfer", "balance", "adjustment",
                "credit", "debit", "bonus", "commission", "swap", "rollover",
                "p/l share", "profit sharing", "management fee"
            ]
            
            non_trading_deals = []
            non_trading_profit = 0
            
            # Find deals with non-trading keywords
            for keyword in non_trading_keywords:
                query = {"comment": {"$regex": keyword, "$options": "i"}}
                deals = list(self.db.mt5_deals_history.find(query))
                
                for deal in deals:
                    if deal not in non_trading_deals:
                        non_trading_deals.append(deal)
                        non_trading_profit += deal.get('profit', 0)
            
            # Also find deals with empty symbols (often non-trading)
            empty_symbol_deals = list(self.db.mt5_deals_history.find({
                "$or": [
                    {"symbol": ""},
                    {"symbol": None},
                    {"symbol": {"$exists": False}}
                ]
            }))
            
            empty_symbol_profit = sum(deal.get('profit', 0) for deal in empty_symbol_deals)
            
            print(f"📊 NON-TRADING DEALS ANALYSIS:")
            print(f"   Deals with non-trading keywords: {len(non_trading_deals)}")
            print(f"   Total profit from keyword deals: ${non_trading_profit:,.2f}")
            print(f"   Deals with empty symbols: {len(empty_symbol_deals)}")
            print(f"   Total profit from empty symbol deals: ${empty_symbol_profit:,.2f}")
            
            # Calculate pure trading P&L
            total_deals = self.db.mt5_deals_history.count_documents({})
            total_profit_result = list(self.db.mt5_deals_history.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$profit"}}}
            ]))
            total_profit = total_profit_result[0]['total'] if total_profit_result else 0
            
            # Estimate pure trading profit (excluding non-trading deals)
            pure_trading_profit = total_profit - non_trading_profit
            
            print(f"\n🎯 PURE TRADING ANALYSIS:")
            print(f"   Total P&L: ${total_profit:,.2f}")
            print(f"   Non-trading P&L: ${non_trading_profit:,.2f}")
            print(f"   Estimated pure trading P&L: ${pure_trading_profit:,.2f}")
            
            # Show sample non-trading deals
            print(f"\n📋 SAMPLE NON-TRADING DEALS:")
            for i, deal in enumerate(non_trading_deals[:5]):
                profit = deal.get('profit', 0)
                comment = deal.get('comment', 'N/A')
                account = deal.get('account', 'N/A')
                
                print(f"   {i+1}. ${profit:,.2f} - Account: {account}, Comment: '{comment}'")
            
            return True
            
        except Exception as e:
            print(f"❌ Error identifying non-trading deals: {str(e)}")
            return False
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        try:
            print("\n" + "=" * 80)
            print("📊 COMPREHENSIVE MAGIC NUMBER INVESTIGATION REPORT")
            print("=" * 80)
            
            # Get basic statistics
            total_deals = self.db.mt5_deals_history.count_documents({})
            total_profit_result = list(self.db.mt5_deals_history.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$profit"}}}
            ]))
            total_profit = total_profit_result[0]['total'] if total_profit_result else 0
            
            print(f"\n🎯 EXECUTIVE SUMMARY:")
            print(f"   Current Trading Analytics Display: ${total_profit:,.2f}")
            print(f"   Expected Amount: ~$10,000.00")
            print(f"   Variance: ${total_profit - 10000:,.2f}")
            
            # Magic number analysis
            magic_pipeline = [
                {"$group": {
                    "_id": "$magic",
                    "count": {"$sum": 1},
                    "total_profit": {"$sum": "$profit"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            magic_results = list(self.db.mt5_deals_history.aggregate(magic_pipeline))
            
            print(f"\n🔍 MAGIC NUMBER FINDINGS:")
            print(f"   Total Magic Numbers Found: {len(magic_results)}")
            
            for result in magic_results:
                magic_num = result['_id']
                count = result['count']
                profit = result['total_profit']
                print(f"   Magic #{magic_num}: {count:,} deals, ${profit:,.2f} P&L")
            
            # Balance adjustment analysis
            balance_query = {"comment": {"$regex": "deposit|withdrawal|balance|adjustment", "$options": "i"}}
            balance_deals = list(self.db.mt5_deals_history.find(balance_query))
            balance_profit = sum(deal.get('profit', 0) for deal in balance_deals)
            
            print(f"\n⚠️  BALANCE ADJUSTMENT IMPACT:")
            print(f"   Balance Adjustment Deals: {len(balance_deals)}")
            print(f"   Balance Adjustment P&L: ${balance_profit:,.2f}")
            print(f"   True Trading P&L: ${total_profit - balance_profit:,.2f}")
            
            # Recommendations
            print(f"\n🎯 RECOMMENDATIONS:")
            
            if balance_profit > 10000:
                print(f"   1. ⚠️  CRITICAL: Balance adjustments (${balance_profit:,.2f}) are significantly inflating P&L")
                print(f"   2. 🔧 IMMEDIATE ACTION: Exclude balance adjustments from Trading Analytics")
                print(f"   3. 📊 UPDATE FILTER: Add filter to exclude deals with 'deposit', 'withdrawal', 'balance', 'adjustment' in comments")
            
            true_trading_pnl = total_profit - balance_profit
            if abs(true_trading_pnl - 10000) > 5000:
                print(f"   4. 🔍 INVESTIGATE: True trading P&L (${true_trading_pnl:,.2f}) still differs significantly from expected $10,000")
                print(f"   5. 📋 REVIEW: Check for other non-trading deals (transfers, fees, etc.)")
            
            if len(magic_results) == 1:
                print(f"   6. 🎯 MANAGER IDENTIFICATION: Only 1 magic number found - may need better manager/strategy separation")
                print(f"   7. 📊 CONSIDER: Using account numbers or other fields for manager identification")
            
            print(f"\n✅ INVESTIGATION COMPLETED")
            print(f"   Next Steps: Implement filtering in Trading Analytics to exclude non-trading deals")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating comprehensive report: {str(e)}")
            return False
    
    def run_detailed_investigation(self):
        """Run complete detailed investigation"""
        print("🔍 DETAILED MAGIC NUMBER INVESTIGATION - DEEPER ANALYSIS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        
        # Step 1: Connect to MongoDB
        if not self.connect_to_mongodb():
            return False
        
        # Step 2: Authenticate
        if not self.authenticate():
            return False
        
        # Step 3: Analyze data structure
        if not self.analyze_data_structure():
            return False
        
        # Step 4: Analyze accounts
        if not self.analyze_accounts_in_deals():
            return False
        
        # Step 5: Analyze deal types
        if not self.analyze_deal_types():
            return False
        
        # Step 6: Analyze profit distribution
        if not self.analyze_profit_distribution():
            return False
        
        # Step 7: Identify non-trading deals
        if not self.identify_non_trading_deals():
            return False
        
        # Step 8: Generate comprehensive report
        if not self.generate_comprehensive_report():
            return False
        
        return True

def main():
    """Main investigation execution"""
    investigator = DetailedMagicInvestigation()
    success = investigator.run_detailed_investigation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()