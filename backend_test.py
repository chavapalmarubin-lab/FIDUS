#!/usr/bin/env python3
"""
Trading Analytics System Phase 1B Multi-Account Testing
Testing the expanded Trading Analytics API endpoints with multi-account support
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

class TradingAnalyticsPhase1BTestSuite:
    """Comprehensive test suite for Trading Analytics Phase 1B Multi-Account"""
    
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://fidus-integration.preview.emergentagent.com')
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        
        # Phase 1B testing parameters - All 4 accounts
        self.all_accounts = [886557, 886066, 886602, 885822]
        self.account_profiles = {
            886557: {"name": "BALANCE Fund ($80K)", "fund_type": "BALANCE", "expected_activity": "high"},
            886066: {"name": "BALANCE Fund ($10K)", "fund_type": "BALANCE", "expected_activity": "moderate"},
            886602: {"name": "BALANCE Fund ($10K)", "fund_type": "BALANCE", "expected_activity": "moderate"},
            885822: {"name": "CORE Fund ($18K)", "fund_type": "CORE", "expected_activity": "strategic"}
        }
        self.test_days = 30
        
        logger.info(f"🚀 Trading Analytics Phase 1B Multi-Account Test Suite initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
        logger.info(f"   All Accounts: {self.all_accounts}")
        logger.info(f"   Test Period: {self.test_days} days")
    
    async def setup(self):
        """Setup test environment"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'Content-Type': 'application/json'}
            )
            
            # Authenticate as admin
            await self.authenticate_admin()
            
            logger.info("✅ Test environment setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test setup failed: {str(e)}")
            return False
    
    async def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
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
                        # Update session headers with auth token
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
            logger.error(f"❌ Authentication error: {str(e)}")
            return False
    
    async def test_multi_account_overview_endpoint(self) -> Dict[str, Any]:
        """Test GET /api/admin/trading/analytics/overview with multi-account support"""
        test_name = "Multi-Account Analytics Overview"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test 1: All accounts (account=0)
            url_all = f"{self.backend_url}/admin/trading/analytics/overview?account=0"
            async with self.session.get(url_all) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    validation_results.append("✅ All accounts endpoint (account=0) returns HTTP 200")
                    
                    accounts_included = response_data.get('accounts_included', [])
                    if set(accounts_included) == set(self.all_accounts):
                        validation_results.append(f"✅ All 4 accounts included: {accounts_included}")
                    else:
                        validation_results.append(f"❌ Wrong accounts included: {accounts_included} (expected {self.all_accounts})")
                    
                    analytics = response_data.get('analytics', {})
                    if analytics and 'overview' in analytics:
                        overview = analytics['overview']
                        validation_results.append(f"✅ Aggregated overview data present")
                        logger.info(f"   All Accounts - Total P&L: ${overview.get('total_pnl', 0):.2f}")
                        logger.info(f"   All Accounts - Total Trades: {overview.get('total_trades', 0)}")
                        logger.info(f"   All Accounts - Win Rate: {overview.get('win_rate', 0):.2f}%")
                    else:
                        validation_results.append("❌ Missing aggregated analytics data")
                else:
                    validation_results.append(f"❌ All accounts endpoint failed: HTTP {status_code}")
            
            # Test 2: Specific account (886557 - most active)
            url_specific = f"{self.backend_url}/admin/trading/analytics/overview?account=886557"
            async with self.session.get(url_specific) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    validation_results.append("✅ Specific account endpoint (886557) returns HTTP 200")
                    
                    accounts_included = response_data.get('accounts_included', [])
                    if accounts_included == [886557]:
                        validation_results.append(f"✅ Correct single account included: {accounts_included}")
                    else:
                        validation_results.append(f"❌ Wrong account filter: {accounts_included} (expected [886557])")
                    
                    analytics = response_data.get('analytics', {})
                    if analytics and 'overview' in analytics:
                        overview = analytics['overview']
                        validation_results.append(f"✅ Account-specific overview data present")
                        logger.info(f"   Account 886557 - Total P&L: ${overview.get('total_pnl', 0):.2f}")
                        logger.info(f"   Account 886557 - Total Trades: {overview.get('total_trades', 0)}")
                    else:
                        validation_results.append("❌ Missing account-specific analytics data")
                else:
                    validation_results.append(f"❌ Specific account endpoint failed: HTTP {status_code}")
            
            # Test 3: Test each individual account
            for account_num in self.all_accounts:
                url_account = f"{self.backend_url}/admin/trading/analytics/overview?account={account_num}"
                async with self.session.get(url_account) as response:
                    if response.status == 200:
                        data = await response.json()
                        accounts_included = data.get('accounts_included', [])
                        if accounts_included == [account_num]:
                            validation_results.append(f"✅ Account {account_num} filtering works correctly")
                        else:
                            validation_results.append(f"❌ Account {account_num} filtering failed")
                    else:
                        validation_results.append(f"❌ Account {account_num} endpoint failed: HTTP {response.status}")
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'accounts_tested': self.all_accounts,
                    'failed_checks': len(failed_checks),
                    'total_checks': len(validation_results)
                }
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_multi_account_daily_performance(self) -> Dict[str, Any]:
        """Test GET /api/admin/trading/analytics/daily with multi-account aggregation"""
        test_name = "Multi-Account Daily Performance"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test 1: All accounts aggregation (account=0)
            url_all = f"{self.backend_url}/admin/trading/analytics/daily?account=0&days=7"
            async with self.session.get(url_all) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    validation_results.append("✅ All accounts daily aggregation returns HTTP 200")
                    
                    daily_performance = response_data.get('daily_performance', [])
                    account = response_data.get('account')
                    
                    if account == "all":
                        validation_results.append("✅ Account field correctly shows 'all' for aggregation")
                    else:
                        validation_results.append(f"❌ Account field incorrect: {account} (expected 'all')")
                    
                    if isinstance(daily_performance, list):
                        validation_results.append(f"✅ Aggregated daily data is list ({len(daily_performance)} entries)")
                        
                        # Check aggregated data structure
                        if daily_performance:
                            sample_entry = daily_performance[0]
                            required_fields = ['date', 'total_trades', 'winning_trades', 'losing_trades', 'total_pnl', 'win_rate']
                            missing_fields = [field for field in required_fields if field not in sample_entry]
                            
                            if not missing_fields:
                                validation_results.append("✅ Aggregated daily entry structure valid")
                                logger.info(f"   Sample aggregated entry - Trades: {sample_entry.get('total_trades', 0)}, P&L: ${sample_entry.get('total_pnl', 0):.2f}")
                            else:
                                validation_results.append(f"❌ Missing aggregated fields: {missing_fields}")
                        else:
                            validation_results.append("⚠️ No aggregated daily data (may be expected)")
                    else:
                        validation_results.append("❌ Aggregated daily data is not a list")
                else:
                    validation_results.append(f"❌ All accounts daily endpoint failed: HTTP {status_code}")
            
            # Test 2: Specific account daily performance (886557)
            url_specific = f"{self.backend_url}/admin/trading/analytics/daily?account=886557&days=7"
            async with self.session.get(url_specific) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    validation_results.append("✅ Specific account daily performance returns HTTP 200")
                    
                    daily_performance = response_data.get('daily_performance', [])
                    account = response_data.get('account')
                    
                    if account == 886557:
                        validation_results.append(f"✅ Account field correctly shows {account}")
                    else:
                        validation_results.append(f"❌ Account field incorrect: {account} (expected 886557)")
                    
                    if isinstance(daily_performance, list):
                        validation_results.append(f"✅ Account-specific daily data is list ({len(daily_performance)} entries)")
                        
                        # Check account-specific data
                        if daily_performance:
                            sample_entry = daily_performance[0]
                            if sample_entry.get('account') == 886557:
                                validation_results.append("✅ Daily entries correctly filtered by account")
                            else:
                                validation_results.append(f"❌ Daily entries not filtered correctly: account {sample_entry.get('account')}")
                        else:
                            validation_results.append("⚠️ No account-specific daily data")
                    else:
                        validation_results.append("❌ Account-specific daily data is not a list")
                else:
                    validation_results.append(f"❌ Specific account daily endpoint failed: HTTP {status_code}")
            
            # Test 3: Compare aggregation vs individual accounts
            # Get all accounts data and individual account data to verify aggregation logic
            all_accounts_data = None
            individual_totals = {"total_trades": 0, "total_pnl": 0.0}
            
            # Get aggregated data
            url_all_compare = f"{self.backend_url}/admin/trading/analytics/daily?account=0&days=1"
            async with self.session.get(url_all_compare) as response:
                if response.status == 200:
                    data = await response.json()
                    all_accounts_data = data.get('daily_performance', [])
            
            # Get individual account data and sum manually
            for account_num in self.all_accounts:
                url_individual = f"{self.backend_url}/admin/trading/analytics/daily?account={account_num}&days=1"
                async with self.session.get(url_individual) as response:
                    if response.status == 200:
                        data = await response.json()
                        daily_data = data.get('daily_performance', [])
                        for day in daily_data:
                            individual_totals["total_trades"] += day.get('total_trades', 0)
                            individual_totals["total_pnl"] += day.get('total_pnl', 0.0)
            
            # Compare aggregation accuracy
            if all_accounts_data and len(all_accounts_data) > 0:
                aggregated_day = all_accounts_data[0]
                agg_trades = aggregated_day.get('total_trades', 0)
                agg_pnl = aggregated_day.get('total_pnl', 0.0)
                
                if agg_trades == individual_totals["total_trades"]:
                    validation_results.append("✅ Trade count aggregation is accurate")
                else:
                    validation_results.append(f"❌ Trade count aggregation mismatch: {agg_trades} vs {individual_totals['total_trades']}")
                
                if abs(agg_pnl - individual_totals["total_pnl"]) < 0.01:  # Allow small floating point differences
                    validation_results.append("✅ P&L aggregation is accurate")
                else:
                    validation_results.append(f"❌ P&L aggregation mismatch: ${agg_pnl:.2f} vs ${individual_totals['total_pnl']:.2f}")
            else:
                validation_results.append("⚠️ Could not verify aggregation accuracy (no data)")
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'accounts_tested': self.all_accounts,
                    'failed_checks': len(failed_checks),
                    'aggregation_verified': all_accounts_data is not None
                }
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_recent_trades_endpoint(self) -> Dict[str, Any]:
        """Test GET /api/admin/trading/analytics/trades endpoint"""
        test_name = "Recent Trades Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        try:
            url = f"{self.backend_url}/admin/trading/analytics/trades"
            
            async with self.session.get(url) as response:
                status_code = response.status
                response_data = await response.json()
                
                success = response_data.get('success', False)
                trades = response_data.get('trades', [])
                account = response_data.get('account')
                limit = response_data.get('limit')
                
                validation_results = []
                
                if status_code == 200:
                    validation_results.append("✅ HTTP 200 OK response")
                else:
                    validation_results.append(f"❌ HTTP {status_code} (expected 200)")
                
                if success:
                    validation_results.append("✅ Success flag is True")
                else:
                    validation_results.append("❌ Success flag is False")
                
                if isinstance(trades, list):
                    validation_results.append(f"✅ Trades data is list ({len(trades)} entries)")
                    
                    # Check trade structure if entries exist
                    if trades:
                        sample_trade = trades[0]
                        required_fields = [
                            'ticket', 'account', 'symbol', 'type', 'volume',
                            'open_price', 'close_price', 'open_time', 'close_time', 'profit'
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in sample_trade]
                        if not missing_fields:
                            validation_results.append("✅ Trade entry structure valid")
                        else:
                            validation_results.append(f"❌ Missing trade fields: {missing_fields}")
                        
                        # Check data types
                        if isinstance(sample_trade.get('profit'), (int, float)):
                            validation_results.append("✅ Profit field is numeric")
                        else:
                            validation_results.append("❌ Profit field is not numeric")
                            
                    else:
                        validation_results.append("⚠️ No trades data (may be expected for new system)")
                else:
                    validation_results.append("❌ Trades data is not a list")
                
                if account == self.test_account:
                    validation_results.append(f"✅ Correct account returned ({account})")
                else:
                    validation_results.append(f"❌ Wrong account returned ({account}, expected {self.test_account})")
                
                if limit and isinstance(limit, int):
                    validation_results.append(f"✅ Limit parameter returned ({limit})")
                else:
                    validation_results.append("❌ Limit parameter missing or invalid")
                
                # Test with custom limit
                url_with_limit = f"{self.backend_url}/admin/trading/analytics/trades?limit=10&account={self.test_account}"
                async with self.session.get(url_with_limit) as limit_response:
                    if limit_response.status == 200:
                        validation_results.append("✅ Custom limit parameter accepted")
                    else:
                        validation_results.append("❌ Custom limit parameter rejected")
                
                logger.info(f"   Response Status: {status_code}")
                logger.info(f"   Success: {success}")
                logger.info(f"   Trades Count: {len(trades)}")
                logger.info(f"   Account: {account}")
                logger.info(f"   Limit: {limit}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 and success else 'FAIL',
                    'status_code': status_code,
                    'response_data': response_data,
                    'validation_results': validation_results,
                    'details': {
                        'endpoint': url,
                        'method': 'GET',
                        'trades_count': len(trades),
                        'account_tested': account
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_manual_sync_endpoint(self) -> Dict[str, Any]:
        """Test POST /api/admin/trading/analytics/sync endpoint"""
        test_name = "Manual Sync Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        try:
            url = f"{self.backend_url}/admin/trading/analytics/sync"
            
            async with self.session.post(url) as response:
                status_code = response.status
                response_data = await response.json()
                
                success = response_data.get('success', False)
                sync_result = response_data.get('sync_result')
                
                validation_results = []
                
                if status_code == 200:
                    validation_results.append("✅ HTTP 200 OK response")
                else:
                    validation_results.append(f"❌ HTTP {status_code} (expected 200)")
                
                if isinstance(success, bool):
                    validation_results.append(f"✅ Success flag present ({success})")
                else:
                    validation_results.append("❌ Success flag missing or invalid")
                
                if sync_result and isinstance(sync_result, dict):
                    validation_results.append("✅ Sync result data present")
                    
                    # Check sync result structure
                    expected_fields = [
                        'sync_date', 'started_at', 'accounts_processed',
                        'total_trades_synced', 'daily_summaries_created', 'success'
                    ]
                    
                    missing_fields = [field for field in expected_fields if field not in sync_result]
                    if not missing_fields:
                        validation_results.append("✅ Sync result structure complete")
                    else:
                        validation_results.append(f"❌ Missing sync result fields: {missing_fields}")
                    
                    # Check if sync processed the test account
                    accounts_processed = sync_result.get('accounts_processed', 0)
                    if accounts_processed > 0:
                        validation_results.append(f"✅ Accounts processed ({accounts_processed})")
                    else:
                        validation_results.append("⚠️ No accounts processed (may be expected)")
                    
                    # Check for errors
                    errors = sync_result.get('errors', [])
                    if not errors:
                        validation_results.append("✅ No sync errors reported")
                    else:
                        validation_results.append(f"⚠️ Sync errors reported: {len(errors)}")
                        for error in errors[:3]:  # Show first 3 errors
                            validation_results.append(f"   - {error}")
                            
                else:
                    validation_results.append("❌ Sync result data missing or invalid")
                
                logger.info(f"   Response Status: {status_code}")
                logger.info(f"   Success: {success}")
                if sync_result:
                    logger.info(f"   Accounts Processed: {sync_result.get('accounts_processed', 0)}")
                    logger.info(f"   Trades Synced: {sync_result.get('total_trades_synced', 0)}")
                    logger.info(f"   Daily Summaries: {sync_result.get('daily_summaries_created', 0)}")
                    logger.info(f"   Errors: {len(sync_result.get('errors', []))}")
                
                return {
                    'test_name': test_name,
                    'status': 'PASS' if status_code == 200 else 'FAIL',
                    'status_code': status_code,
                    'response_data': response_data,
                    'validation_results': validation_results,
                    'details': {
                        'endpoint': url,
                        'method': 'POST',
                        'sync_success': sync_result.get('success') if sync_result else None,
                        'accounts_processed': sync_result.get('accounts_processed') if sync_result else 0
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_database_collections(self) -> Dict[str, Any]:
        """Test that database collections and indexes are properly created"""
        test_name = "Database Collections & Indexes"
        logger.info(f"🧪 Testing {test_name}")
        
        try:
            # This test will verify the sync endpoint creates the necessary collections
            # by running a sync and then checking the other endpoints for data
            
            validation_results = []
            
            # First, trigger a sync to ensure collections exist
            sync_url = f"{self.backend_url}/admin/trading/analytics/sync"
            async with self.session.post(sync_url) as sync_response:
                if sync_response.status == 200:
                    validation_results.append("✅ Sync endpoint accessible for collection creation")
                else:
                    validation_results.append("❌ Sync endpoint not accessible")
            
            # Check if daily performance endpoint returns data structure (even if empty)
            daily_url = f"{self.backend_url}/admin/trading/analytics/daily"
            async with self.session.get(daily_url) as daily_response:
                if daily_response.status == 200:
                    daily_data = await daily_response.json()
                    if 'daily_performance' in daily_data:
                        validation_results.append("✅ Daily performance collection accessible")
                    else:
                        validation_results.append("❌ Daily performance collection not accessible")
                else:
                    validation_results.append("❌ Daily performance endpoint failed")
            
            # Check if trades endpoint returns data structure (even if empty)
            trades_url = f"{self.backend_url}/admin/trading/analytics/trades"
            async with self.session.get(trades_url) as trades_response:
                if trades_response.status == 200:
                    trades_data = await trades_response.json()
                    if 'trades' in trades_data:
                        validation_results.append("✅ MT5 trades collection accessible")
                    else:
                        validation_results.append("❌ MT5 trades collection not accessible")
                else:
                    validation_results.append("❌ Trades endpoint failed")
            
            # Check if analytics overview works (indicates period_performance collection)
            overview_url = f"{self.backend_url}/admin/trading/analytics/overview"
            async with self.session.get(overview_url) as overview_response:
                if overview_response.status == 200:
                    overview_data = await overview_response.json()
                    if 'analytics' in overview_data:
                        validation_results.append("✅ Analytics aggregation working (period_performance implied)")
                    else:
                        validation_results.append("❌ Analytics aggregation not working")
                else:
                    validation_results.append("❌ Analytics overview endpoint failed")
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            logger.info(f"   Database Collections Status: {overall_status}")
            logger.info(f"   Failed Checks: {len(failed_checks)}")
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'collections_tested': ['mt5_trades', 'daily_performance', 'period_performance'],
                    'failed_checks': len(failed_checks),
                    'total_checks': len(validation_results)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling for invalid requests"""
        test_name = "Error Handling"
        logger.info(f"🧪 Testing {test_name}")
        
        try:
            validation_results = []
            
            # Test invalid account parameter
            invalid_account_url = f"{self.backend_url}/admin/trading/analytics/daily?account=999999"
            async with self.session.get(invalid_account_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and len(data.get('daily_performance', [])) == 0:
                        validation_results.append("✅ Invalid account handled gracefully (empty result)")
                    else:
                        validation_results.append("⚠️ Invalid account returned data (unexpected)")
                else:
                    validation_results.append("❌ Invalid account caused server error")
            
            # Test invalid days parameter
            invalid_days_url = f"{self.backend_url}/admin/trading/analytics/daily?days=-1"
            async with self.session.get(invalid_days_url) as response:
                if response.status in [200, 400]:
                    validation_results.append("✅ Invalid days parameter handled")
                else:
                    validation_results.append("❌ Invalid days parameter caused server error")
            
            # Test invalid limit parameter
            invalid_limit_url = f"{self.backend_url}/admin/trading/analytics/trades?limit=abc"
            async with self.session.get(invalid_limit_url) as response:
                if response.status in [200, 400]:
                    validation_results.append("✅ Invalid limit parameter handled")
                else:
                    validation_results.append("❌ Invalid limit parameter caused server error")
            
            # Test unauthenticated request (remove auth header temporarily)
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            unauth_url = f"{self.backend_url}/admin/trading/analytics/overview"
            async with self.session.get(unauth_url) as response:
                if response.status == 401:
                    validation_results.append("✅ Unauthenticated request properly rejected")
                else:
                    validation_results.append(f"❌ Unauthenticated request not rejected (status: {response.status})")
            
            # Restore auth headers
            self.session.headers.update(original_headers)
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            logger.info(f"   Error Handling Status: {overall_status}")
            logger.info(f"   Failed Checks: {len(failed_checks)}")
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'error_scenarios_tested': 4,
                    'failed_checks': len(failed_checks)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Trading Analytics tests"""
        logger.info("🚀 Starting Trading Analytics Phase 1A Test Suite")
        
        if not await self.setup():
            return {
                'success': False,
                'error': 'Test setup failed',
                'results': []
            }
        
        # Run all tests
        tests = [
            self.test_analytics_overview_endpoint,
            self.test_daily_performance_endpoint,
            self.test_recent_trades_endpoint,
            self.test_manual_sync_endpoint,
            self.test_database_collections,
            self.test_error_handling
        ]
        
        results = []
        for test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                self.test_results.append(result)
            except Exception as e:
                logger.error(f"❌ Test function failed: {str(e)}")
                results.append({
                    'test_name': test_func.__name__,
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        # Calculate summary
        passed_tests = [r for r in results if r.get('status') == 'PASS']
        failed_tests = [r for r in results if r.get('status') == 'FAIL']
        error_tests = [r for r in results if r.get('status') == 'ERROR']
        
        success_rate = len(passed_tests) / len(results) * 100 if results else 0
        
        summary = {
            'total_tests': len(results),
            'passed': len(passed_tests),
            'failed': len(failed_tests),
            'errors': len(error_tests),
            'success_rate': round(success_rate, 1),
            'overall_status': 'PASS' if len(failed_tests) == 0 and len(error_tests) == 0 else 'FAIL'
        }
        
        # Log summary
        logger.info("📊 Trading Analytics Test Summary:")
        logger.info(f"   Total Tests: {summary['total_tests']}")
        logger.info(f"   Passed: {summary['passed']}")
        logger.info(f"   Failed: {summary['failed']}")
        logger.info(f"   Errors: {summary['errors']}")
        logger.info(f"   Success Rate: {summary['success_rate']}%")
        logger.info(f"   Overall Status: {summary['overall_status']}")
        
        return {
            'success': summary['overall_status'] == 'PASS',
            'summary': summary,
            'results': results,
            'test_parameters': {
                'backend_url': self.backend_url,
                'test_account': self.test_account,
                'test_days': self.test_days
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = TradingAnalyticsTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("TRADING ANALYTICS PHASE 1A TEST RESULTS")
        print("="*80)
        
        for result in results['results']:
            print(f"\n🧪 {result['test_name']}: {result['status']}")
            
            if 'validation_results' in result:
                for validation in result['validation_results']:
                    print(f"   {validation}")
            
            if result.get('status') == 'ERROR':
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Overall Status: {results['summary']['overall_status']}")
        print(f"   Success Rate: {results['summary']['success_rate']}%")
        print(f"   Tests: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
        
        if results['summary']['failed'] > 0:
            print(f"   Failed Tests: {results['summary']['failed']}")
        
        if results['summary']['errors'] > 0:
            print(f"   Error Tests: {results['summary']['errors']}")
        
        print("="*80)
        
        return results['success']
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return False
        
    finally:
        await test_suite.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)