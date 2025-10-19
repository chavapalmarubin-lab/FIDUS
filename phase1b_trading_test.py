#!/usr/bin/env python3
"""
Phase 1B Trading Analytics Multi-Account Testing
Focused test for the specific requirements in the review request
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase1BTradingTest:
    """Focused test for Phase 1B multi-account Trading Analytics"""
    
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://fidus-api-bridge.preview.emergentagent.com')
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        
        # Phase 1B accounts as specified in review
        self.all_accounts = [886557, 886066, 886602, 885822]
        
        logger.info(f"🚀 Phase 1B Trading Analytics Test initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
        logger.info(f"   Testing accounts: {self.all_accounts}")
    
    async def setup(self):
        """Setup test environment"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'Content-Type': 'application/json'}
            )
            
            # Authenticate as admin
            login_data = {
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }
            
            async with self.session.post(f"{self.backend_url}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get('token')
                    
                    if self.admin_token:
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.admin_token}'
                        })
                        logger.info("✅ Admin authentication successful")
                        return True
                    else:
                        logger.error("❌ No token received from login")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Admin login failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Setup failed: {str(e)}")
            return False
    
    async def test_overview_with_account_parameter(self):
        """Test overview endpoint with account parameter as specified in review"""
        logger.info("🧪 Testing Overview Endpoint with Account Parameter")
        
        results = []
        
        # Test 1: account=0 for all accounts
        try:
            url = f"{self.backend_url}/admin/trading/analytics/overview?account=0"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    accounts_included = data.get('accounts_included', [])
                    analytics = data.get('analytics', {})
                    
                    if set(accounts_included) == set(self.all_accounts):
                        results.append("✅ account=0 returns all 4 accounts")
                        logger.info(f"   All accounts included: {accounts_included}")
                    else:
                        results.append(f"❌ account=0 wrong accounts: {accounts_included}")
                    
                    if analytics and 'overview' in analytics:
                        overview = analytics['overview']
                        results.append(f"✅ Aggregated data - Trades: {overview.get('total_trades', 0)}, P&L: ${overview.get('total_pnl', 0):.2f}")
                    else:
                        results.append("❌ Missing aggregated analytics data")
                else:
                    results.append(f"❌ account=0 failed: HTTP {response.status}")
        except Exception as e:
            results.append(f"❌ account=0 error: {str(e)}")
        
        # Test 2: account=886557 for specific account
        try:
            url = f"{self.backend_url}/admin/trading/analytics/overview?account=886557"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    accounts_included = data.get('accounts_included', [])
                    analytics = data.get('analytics', {})
                    
                    if accounts_included == [886557]:
                        results.append("✅ account=886557 returns specific account")
                    else:
                        results.append(f"❌ account=886557 wrong filter: {accounts_included}")
                    
                    if analytics and 'overview' in analytics:
                        overview = analytics['overview']
                        results.append(f"✅ Account 886557 data - Trades: {overview.get('total_trades', 0)}, P&L: ${overview.get('total_pnl', 0):.2f}")
                    else:
                        results.append("❌ Missing account-specific analytics")
                else:
                    results.append(f"❌ account=886557 failed: HTTP {response.status}")
        except Exception as e:
            results.append(f"❌ account=886557 error: {str(e)}")
        
        return results
    
    async def test_daily_with_account_parameter(self):
        """Test daily endpoint with account parameter"""
        logger.info("🧪 Testing Daily Performance with Account Parameter")
        
        results = []
        
        # Test aggregation vs specific account
        try:
            # All accounts
            url_all = f"{self.backend_url}/admin/trading/analytics/daily?account=0&days=7"
            async with self.session.get(url_all) as response:
                if response.status == 200:
                    data = await response.json()
                    daily_performance = data.get('daily_performance', [])
                    account = data.get('account')
                    
                    results.append(f"✅ All accounts daily: {len(daily_performance)} entries, account field: {account}")
                else:
                    results.append(f"❌ All accounts daily failed: HTTP {response.status}")
            
            # Specific account
            url_specific = f"{self.backend_url}/admin/trading/analytics/daily?account=886557&days=7"
            async with self.session.get(url_specific) as response:
                if response.status == 200:
                    data = await response.json()
                    daily_performance = data.get('daily_performance', [])
                    account = data.get('account')
                    
                    results.append(f"✅ Specific account daily: {len(daily_performance)} entries, account: {account}")
                else:
                    results.append(f"❌ Specific account daily failed: HTTP {response.status}")
                    
        except Exception as e:
            results.append(f"❌ Daily performance error: {str(e)}")
        
        return results
    
    async def test_trades_with_account_parameter(self):
        """Test trades endpoint with account parameter"""
        logger.info("🧪 Testing Trades with Account Parameter")
        
        results = []
        
        try:
            # All accounts trades
            url_all = f"{self.backend_url}/admin/trading/analytics/trades?account=0&limit=20"
            async with self.session.get(url_all) as response:
                if response.status == 200:
                    data = await response.json()
                    trades = data.get('trades', [])
                    account = data.get('account')
                    
                    if trades:
                        account_numbers = set(trade.get('account') for trade in trades)
                        results.append(f"✅ All accounts trades: {len(trades)} trades from accounts {sorted(account_numbers)}")
                    else:
                        results.append("⚠️ No trades from all accounts")
                else:
                    results.append(f"❌ All accounts trades failed: HTTP {response.status}")
            
            # Wait a bit to avoid rate limiting
            await asyncio.sleep(1)
            
            # Specific account trades (886557)
            url_specific = f"{self.backend_url}/admin/trading/analytics/trades?account=886557&limit=10"
            async with self.session.get(url_specific) as response:
                if response.status == 200:
                    data = await response.json()
                    trades = data.get('trades', [])
                    account = data.get('account')
                    
                    if trades:
                        # Verify all trades are from correct account
                        correct_account_trades = [t for t in trades if t.get('account') == 886557]
                        if len(correct_account_trades) == len(trades):
                            results.append(f"✅ Account 886557 trades: {len(trades)} trades, all correctly filtered")
                        else:
                            results.append(f"❌ Account 886557 filtering failed: {len(correct_account_trades)}/{len(trades)} correct")
                    else:
                        results.append("⚠️ No trades for account 886557")
                else:
                    results.append(f"❌ Account 886557 trades failed: HTTP {response.status}")
                    
        except Exception as e:
            results.append(f"❌ Trades filtering error: {str(e)}")
        
        return results
    
    async def test_sync_all_accounts(self):
        """Test sync endpoint should sync all 4 accounts"""
        logger.info("🧪 Testing Sync for All 4 Accounts")
        
        results = []
        
        try:
            url = f"{self.backend_url}/admin/trading/analytics/sync"
            async with self.session.post(url) as response:
                if response.status == 200:
                    data = await response.json()
                    sync_result = data.get('sync_result', {})
                    
                    accounts_processed = sync_result.get('accounts_processed', 0)
                    total_trades_synced = sync_result.get('total_trades_synced', 0)
                    daily_summaries_created = sync_result.get('daily_summaries_created', 0)
                    errors = sync_result.get('errors', [])
                    
                    if accounts_processed == 4:
                        results.append(f"✅ All 4 accounts processed")
                    else:
                        results.append(f"⚠️ {accounts_processed}/4 accounts processed")
                    
                    results.append(f"✅ Sync results - Trades: {total_trades_synced}, Summaries: {daily_summaries_created}, Errors: {len(errors)}")
                    
                    if errors:
                        for error in errors[:2]:  # Show first 2 errors
                            results.append(f"   Error: {error}")
                            
                elif response.status == 429:
                    results.append("⚠️ Rate limited - sync endpoint busy")
                else:
                    results.append(f"❌ Sync failed: HTTP {response.status}")
                    
        except Exception as e:
            results.append(f"❌ Sync error: {str(e)}")
        
        return results
    
    async def test_account_specific_functionality(self):
        """Test that each account generates different data based on profiles"""
        logger.info("🧪 Testing Account-Specific Functionality")
        
        results = []
        account_data = {}
        
        # Get data for each account individually
        for account_num in self.all_accounts:
            try:
                # Get overview for this account
                url = f"{self.backend_url}/admin/trading/analytics/overview?account={account_num}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        analytics = data.get('analytics', {})
                        overview = analytics.get('overview', {})
                        
                        account_data[account_num] = {
                            'total_trades': overview.get('total_trades', 0),
                            'total_pnl': overview.get('total_pnl', 0),
                            'win_rate': overview.get('win_rate', 0)
                        }
                        
                        profile_name = {
                            886557: "BALANCE $80K (most active)",
                            886066: "BALANCE $10K (moderate)",
                            886602: "BALANCE $10K (moderate)", 
                            885822: "CORE $18K (strategic)"
                        }.get(account_num, f"Account {account_num}")
                        
                        results.append(f"✅ {profile_name}: {overview.get('total_trades', 0)} trades, P&L: ${overview.get('total_pnl', 0):.2f}")
                    else:
                        results.append(f"❌ Account {account_num} overview failed: HTTP {response.status}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                results.append(f"❌ Account {account_num} error: {str(e)}")
        
        # Analyze patterns
        if len(account_data) >= 2:
            trade_counts = [data['total_trades'] for data in account_data.values()]
            pnl_values = [data['total_pnl'] for data in account_data.values()]
            
            if len(set(trade_counts)) > 1:
                results.append("✅ Accounts show different trade activity levels")
            else:
                results.append("⚠️ All accounts show same trade activity")
            
            # Check if 886557 is most active as expected
            if account_data.get(886557, {}).get('total_trades', 0) > 0:
                results.append("✅ Account 886557 (BALANCE $80K) shows activity as expected")
            else:
                results.append("⚠️ Account 886557 (most active) shows no activity")
        
        return results
    
    async def run_all_tests(self):
        """Run all Phase 1B tests"""
        logger.info("🚀 Starting Phase 1B Multi-Account Trading Analytics Tests")
        
        if not await self.setup():
            return False
        
        all_results = []
        
        # Run tests with delays to avoid rate limiting
        test_functions = [
            ("Overview with Account Parameter", self.test_overview_with_account_parameter),
            ("Daily Performance with Account Parameter", self.test_daily_with_account_parameter),
            ("Trades with Account Parameter", self.test_trades_with_account_parameter),
            ("Sync All 4 Accounts", self.test_sync_all_accounts),
            ("Account-Specific Functionality", self.test_account_specific_functionality)
        ]
        
        for test_name, test_func in test_functions:
            try:
                results = await test_func()
                all_results.extend(results)
                
                # Log results for this test
                logger.info(f"   {test_name} completed:")
                for result in results:
                    logger.info(f"     {result}")
                
                # Delay between tests to avoid rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                error_msg = f"❌ {test_name} failed: {str(e)}"
                all_results.append(error_msg)
                logger.error(error_msg)
        
        # Summary
        passed = len([r for r in all_results if r.startswith("✅")])
        warnings = len([r for r in all_results if r.startswith("⚠️")])
        failed = len([r for r in all_results if r.startswith("❌")])
        
        logger.info("📊 Phase 1B Test Summary:")
        logger.info(f"   ✅ Passed: {passed}")
        logger.info(f"   ⚠️ Warnings: {warnings}")
        logger.info(f"   ❌ Failed: {failed}")
        logger.info(f"   Total: {len(all_results)}")
        
        success_rate = (passed / len(all_results)) * 100 if all_results else 0
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        return success_rate > 70  # Consider 70%+ as success
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()

async def main():
    """Main execution"""
    test_suite = Phase1BTradingTest()
    
    try:
        success = await test_suite.run_all_tests()
        
        print("\n" + "="*80)
        print("PHASE 1B MULTI-ACCOUNT TRADING ANALYTICS TEST RESULTS")
        print("="*80)
        print(f"Overall Result: {'PASS' if success else 'FAIL'}")
        print("="*80)
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return False
        
    finally:
        await test_suite.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)