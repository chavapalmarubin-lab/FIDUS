#!/usr/bin/env python3
"""
FIDUS Platform Architecture Audit - Backend Endpoint Testing
Testing current working endpoints to document path patterns and responses
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

class FIDUSArchitectureAuditTestSuite:
    """FIDUS Platform Architecture Audit - Backend Endpoint Testing Suite"""
    
    def __init__(self):
        # Get backend URL from frontend environment
        self.frontend_backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://k8s-to-render.preview.emergentagent.com')
        self.backend_url = self.frontend_backend_url
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.endpoint_documentation = []
        
        logger.info(f"🏗️ FIDUS Platform Architecture Audit Test Suite initialized")
        logger.info(f"   Frontend Backend URL: {self.frontend_backend_url}")
        logger.info(f"   API Base URL: {self.backend_url}")
        logger.info(f"   Purpose: Document working endpoint patterns and responses")
    
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
    
    async def test_admin_login_endpoint(self) -> Dict[str, Any]:
        """Test Admin Login Endpoint - /api/auth/login"""
        test_name = "Admin Login Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        endpoint_info = {
            'url': f"{self.backend_url}/auth/login",
            'method': 'POST',
            'path_pattern': '/api/auth/login',
            'purpose': 'Admin authentication'
        }
        
        try:
            login_data = {
                "email": "admin",
                "password": "password123"
            }
            
            async with self.session.post(endpoint_info['url'], json=login_data) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                endpoint_info.update({
                    'status_code': status_code,
                    'response_format': type(response_data).__name__,
                    'response_sample': response_data if len(str(response_data)) < 500 else str(response_data)[:500] + "..."
                })
                
                if status_code == 200:
                    validation_results.append("✅ Admin login endpoint returns HTTP 200")
                    
                    if 'token' in response_data:
                        validation_results.append("✅ JWT token returned in response")
                        self.admin_token = response_data['token']
                        # Update session headers
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.admin_token}'
                        })
                    else:
                        validation_results.append("❌ No JWT token in response")
                    
                    if 'user' in response_data or 'id' in response_data:
                        validation_results.append("✅ User information returned")
                    else:
                        validation_results.append("⚠️ Limited user information in response")
                        
                else:
                    validation_results.append(f"❌ Admin login failed: HTTP {status_code}")
                    validation_results.append(f"   Response: {response_text[:200]}")
            
            self.endpoint_documentation.append(endpoint_info)
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'endpoint_info': endpoint_info
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"],
                'endpoint_info': endpoint_info
            }
    
    async def test_health_check_endpoint(self) -> Dict[str, Any]:
        """Test Health Check or Simple GET Endpoint"""
        test_name = "Health Check Endpoint"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        health_endpoints = [
            f"{self.backend_url}/health",
            f"{self.backend_url}/status", 
            f"{self.backend_url}/ping",
            f"{self.backend_url}/"
        ]
        
        working_endpoint = None
        
        try:
            for endpoint_url in health_endpoints:
                try:
                    async with self.session.get(endpoint_url) as response:
                        status_code = response.status
                        response_text = await response.text()
                        
                        endpoint_info = {
                            'url': endpoint_url,
                            'method': 'GET',
                            'path_pattern': endpoint_url.replace(self.backend_url, '/api'),
                            'purpose': 'Health check / Status verification',
                            'status_code': status_code,
                            'response_sample': response_text[:200] if response_text else "Empty response"
                        }
                        
                        if status_code == 200:
                            validation_results.append(f"✅ Health endpoint found: {endpoint_url}")
                            validation_results.append(f"   Status: HTTP {status_code}")
                            validation_results.append(f"   Response: {response_text[:100]}...")
                            working_endpoint = endpoint_info
                            self.endpoint_documentation.append(endpoint_info)
                            break
                        else:
                            validation_results.append(f"⚠️ {endpoint_url}: HTTP {status_code}")
                            
                except Exception as e:
                    validation_results.append(f"❌ {endpoint_url}: {str(e)}")
            
            if not working_endpoint:
                validation_results.append("❌ No working health check endpoint found")
                return {
                    'test_name': test_name,
                    'status': 'FAIL',
                    'validation_results': validation_results
                }
            
            return {
                'test_name': test_name,
                'status': 'PASS',
                'validation_results': validation_results,
                'endpoint_info': working_endpoint
            }
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {str(e)}")
            return {
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'validation_results': [f"❌ Exception: {str(e)}"]
            }
    
    async def test_multi_account_trades_endpoint(self) -> Dict[str, Any]:
        """Test GET /api/admin/trading/analytics/trades with multi-account filtering"""
        test_name = "Multi-Account Trades Filtering"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        
        try:
            # Test 1: All accounts trades (account=0)
            url_all = f"{self.backend_url}/admin/trading/analytics/trades?account=0&limit=20"
            async with self.session.get(url_all) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    validation_results.append("✅ All accounts trades endpoint returns HTTP 200")
                    
                    trades = response_data.get('trades', [])
                    account = response_data.get('account')
                    
                    if account == "all":
                        validation_results.append("✅ Account field correctly shows 'all' for all accounts")
                    else:
                        validation_results.append(f"❌ Account field incorrect: {account} (expected 'all')")
                    
                    if isinstance(trades, list):
                        validation_results.append(f"✅ All accounts trades data is list ({len(trades)} entries)")
                        
                        # Check if trades from multiple accounts are present
                        if trades:
                            account_numbers = set(trade.get('account') for trade in trades)
                            expected_accounts = set(self.all_accounts)
                            
                            if account_numbers.intersection(expected_accounts):
                                validation_results.append(f"✅ Trades from multiple accounts present: {sorted(account_numbers)}")
                            else:
                                validation_results.append(f"❌ No trades from expected accounts: {sorted(account_numbers)}")
                            
                            # Check trade structure
                            sample_trade = trades[0]
                            required_fields = ['ticket', 'account', 'symbol', 'type', 'volume', 'profit']
                            missing_fields = [field for field in required_fields if field not in sample_trade]
                            
                            if not missing_fields:
                                validation_results.append("✅ Trade entry structure valid")
                                logger.info(f"   Sample trade - Account: {sample_trade.get('account')}, Symbol: {sample_trade.get('symbol')}, Profit: ${sample_trade.get('profit', 0):.2f}")
                            else:
                                validation_results.append(f"❌ Missing trade fields: {missing_fields}")
                        else:
                            validation_results.append("⚠️ No trades data from all accounts")
                    else:
                        validation_results.append("❌ All accounts trades data is not a list")
                else:
                    validation_results.append(f"❌ All accounts trades endpoint failed: HTTP {status_code}")
            
            # Test 2: Specific account trades (886557)
            url_specific = f"{self.backend_url}/admin/trading/analytics/trades?account=886557&limit=10"
            async with self.session.get(url_specific) as response:
                status_code = response.status
                response_data = await response.json()
                
                if status_code == 200:
                    validation_results.append("✅ Specific account trades endpoint returns HTTP 200")
                    
                    trades = response_data.get('trades', [])
                    account = response_data.get('account')
                    
                    if account == 886557:
                        validation_results.append(f"✅ Account field correctly shows {account}")
                    else:
                        validation_results.append(f"❌ Account field incorrect: {account} (expected 886557)")
                    
                    if isinstance(trades, list):
                        validation_results.append(f"✅ Account-specific trades data is list ({len(trades)} entries)")
                        
                        # Check that all trades are from the correct account
                        if trades:
                            wrong_account_trades = [t for t in trades if t.get('account') != 886557]
                            if not wrong_account_trades:
                                validation_results.append("✅ All trades correctly filtered by account 886557")
                            else:
                                validation_results.append(f"❌ {len(wrong_account_trades)} trades from wrong accounts")
                        else:
                            validation_results.append("⚠️ No trades data for account 886557")
                    else:
                        validation_results.append("❌ Account-specific trades data is not a list")
                else:
                    validation_results.append(f"❌ Specific account trades endpoint failed: HTTP {status_code}")
            
            # Test 3: Test each individual account for data variation
            account_trade_counts = {}
            for account_num in self.all_accounts:
                url_account = f"{self.backend_url}/admin/trading/analytics/trades?account={account_num}&limit=50"
                async with self.session.get(url_account) as response:
                    if response.status == 200:
                        data = await response.json()
                        trades = data.get('trades', [])
                        account_trade_counts[account_num] = len(trades)
                        
                        # Verify account filtering
                        if trades:
                            correct_account_trades = [t for t in trades if t.get('account') == account_num]
                            if len(correct_account_trades) == len(trades):
                                validation_results.append(f"✅ Account {account_num} filtering works correctly ({len(trades)} trades)")
                            else:
                                validation_results.append(f"❌ Account {account_num} filtering failed")
                        else:
                            validation_results.append(f"⚠️ No trades for account {account_num}")
                    else:
                        validation_results.append(f"❌ Account {account_num} trades endpoint failed")
            
            # Test 4: Verify different trading patterns per account profile
            if account_trade_counts:
                logger.info(f"   Trade counts by account: {account_trade_counts}")
                
                # Account 886557 should be most active (BALANCE $80K)
                account_886557_trades = account_trade_counts.get(886557, 0)
                if account_886557_trades > 0:
                    validation_results.append(f"✅ Account 886557 (most active) has {account_886557_trades} trades")
                else:
                    validation_results.append("⚠️ Account 886557 (most active) has no trades")
                
                # Check that different accounts have different patterns
                unique_counts = len(set(account_trade_counts.values()))
                if unique_counts > 1:
                    validation_results.append("✅ Different accounts show varied trading activity")
                else:
                    validation_results.append("⚠️ All accounts show same trading activity (may be expected)")
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'accounts_tested': self.all_accounts,
                    'account_trade_counts': account_trade_counts,
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
    
    async def test_multi_account_sync_endpoint(self) -> Dict[str, Any]:
        """Test POST /api/admin/trading/analytics/sync for all 4 accounts"""
        test_name = "Multi-Account Sync Endpoint"
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
                    
                    # Phase 1B: Check if all 4 accounts were processed
                    accounts_processed = sync_result.get('accounts_processed', 0)
                    if accounts_processed == 4:
                        validation_results.append(f"✅ All 4 accounts processed ({accounts_processed})")
                    elif accounts_processed > 0:
                        validation_results.append(f"⚠️ Partial accounts processed ({accounts_processed}/4)")
                    else:
                        validation_results.append("❌ No accounts processed")
                    
                    # Check trades synced
                    total_trades_synced = sync_result.get('total_trades_synced', 0)
                    if total_trades_synced > 0:
                        validation_results.append(f"✅ Trades synced across accounts ({total_trades_synced})")
                    else:
                        validation_results.append("⚠️ No trades synced (may be expected for new data)")
                    
                    # Check daily summaries created
                    daily_summaries = sync_result.get('daily_summaries_created', 0)
                    if daily_summaries > 0:
                        validation_results.append(f"✅ Daily summaries created ({daily_summaries})")
                    else:
                        validation_results.append("⚠️ No daily summaries created")
                    
                    # Check for errors
                    errors = sync_result.get('errors', [])
                    if not errors:
                        validation_results.append("✅ No sync errors reported")
                    else:
                        validation_results.append(f"⚠️ Sync errors reported: {len(errors)}")
                        for error in errors[:3]:  # Show first 3 errors
                            validation_results.append(f"   - {error}")
                    
                    # Check sync duration
                    duration = sync_result.get('duration_seconds', 0)
                    if duration > 0:
                        validation_results.append(f"✅ Sync completed in {duration:.2f} seconds")
                    else:
                        validation_results.append("⚠️ No duration information")
                            
                else:
                    validation_results.append("❌ Sync result data missing or invalid")
                
                logger.info(f"   Response Status: {status_code}")
                logger.info(f"   Success: {success}")
                if sync_result:
                    logger.info(f"   Accounts Processed: {sync_result.get('accounts_processed', 0)}/4")
                    logger.info(f"   Trades Synced: {sync_result.get('total_trades_synced', 0)}")
                    logger.info(f"   Daily Summaries: {sync_result.get('daily_summaries_created', 0)}")
                    logger.info(f"   Errors: {len(sync_result.get('errors', []))}")
                    logger.info(f"   Duration: {sync_result.get('duration_seconds', 0):.2f}s")
                
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
                        'accounts_processed': sync_result.get('accounts_processed') if sync_result else 0,
                        'expected_accounts': 4
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
    
    async def test_mock_data_variation(self) -> Dict[str, Any]:
        """Test that different accounts generate different mock trading patterns"""
        test_name = "Mock Data Variation by Account"
        logger.info(f"🧪 Testing {test_name}")
        
        validation_results = []
        account_patterns = {}
        
        try:
            # First, trigger sync to generate fresh mock data
            sync_url = f"{self.backend_url}/admin/trading/analytics/sync"
            async with self.session.post(sync_url) as sync_response:
                if sync_response.status == 200:
                    validation_results.append("✅ Sync triggered to generate mock data")
                else:
                    validation_results.append("❌ Failed to trigger sync for mock data")
            
            # Analyze trading patterns for each account
            for account_num in self.all_accounts:
                profile = self.account_profiles[account_num]
                
                # Get trades for this account
                trades_url = f"{self.backend_url}/admin/trading/analytics/trades?account={account_num}&limit=50"
                async with self.session.get(trades_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        trades = data.get('trades', [])
                        
                        # Analyze trading pattern
                        pattern = {
                            'trade_count': len(trades),
                            'symbols': set(),
                            'avg_volume': 0,
                            'total_profit': 0,
                            'profit_trades': 0,
                            'loss_trades': 0
                        }
                        
                        if trades:
                            pattern['symbols'] = set(trade.get('symbol', '') for trade in trades)
                            pattern['avg_volume'] = sum(trade.get('volume', 0) for trade in trades) / len(trades)
                            pattern['total_profit'] = sum(trade.get('profit', 0) for trade in trades)
                            pattern['profit_trades'] = len([t for t in trades if t.get('profit', 0) > 0])
                            pattern['loss_trades'] = len([t for t in trades if t.get('profit', 0) < 0])
                        
                        account_patterns[account_num] = pattern
                        
                        logger.info(f"   Account {account_num} ({profile['name']}): {pattern['trade_count']} trades, "
                                  f"Symbols: {sorted(pattern['symbols'])}, Avg Volume: {pattern['avg_volume']:.2f}")
                    else:
                        validation_results.append(f"❌ Failed to get trades for account {account_num}")
            
            # Verify account-specific expectations
            if 886557 in account_patterns:
                pattern_886557 = account_patterns[886557]
                if pattern_886557['trade_count'] > 0:
                    validation_results.append(f"✅ Account 886557 (BALANCE $80K) shows activity: {pattern_886557['trade_count']} trades")
                else:
                    validation_results.append("⚠️ Account 886557 (most active) has no trades")
            
            if 886066 in account_patterns and 886602 in account_patterns:
                pattern_886066 = account_patterns[886066]
                pattern_886602 = account_patterns[886602]
                if pattern_886066['trade_count'] > 0 or pattern_886602['trade_count'] > 0:
                    validation_results.append(f"✅ Moderate accounts (886066, 886602) show activity: "
                                            f"{pattern_886066['trade_count']}, {pattern_886602['trade_count']} trades")
                else:
                    validation_results.append("⚠️ Moderate accounts show no activity")
            
            if 885822 in account_patterns:
                pattern_885822 = account_patterns[885822]
                if pattern_885822['trade_count'] > 0:
                    validation_results.append(f"✅ Account 885822 (CORE $18K) shows strategic activity: {pattern_885822['trade_count']} trades")
                else:
                    validation_results.append("⚠️ Strategic account 885822 has no trades")
            
            # Check for variation in trading patterns
            if len(account_patterns) >= 2:
                trade_counts = [p['trade_count'] for p in account_patterns.values()]
                symbol_sets = [p['symbols'] for p in account_patterns.values()]
                volume_averages = [p['avg_volume'] for p in account_patterns.values() if p['avg_volume'] > 0]
                
                # Check trade count variation
                if len(set(trade_counts)) > 1:
                    validation_results.append("✅ Accounts show different trade activity levels")
                else:
                    validation_results.append("⚠️ All accounts show same trade activity (may be expected)")
                
                # Check symbol variation
                unique_symbol_combinations = len(set(frozenset(s) for s in symbol_sets if s))
                if unique_symbol_combinations > 1:
                    validation_results.append("✅ Accounts trade different symbol combinations")
                else:
                    validation_results.append("⚠️ All accounts trade same symbols")
                
                # Check volume variation
                if len(set(f"{v:.1f}" for v in volume_averages)) > 1:
                    validation_results.append("✅ Accounts show different average volumes")
                else:
                    validation_results.append("⚠️ All accounts show same average volume")
            
            # Verify expected account characteristics
            if account_patterns:
                # Account 886557 should be most active (BALANCE $80K)
                most_active_account = max(account_patterns.keys(), key=lambda k: account_patterns[k]['trade_count'])
                if most_active_account == 886557:
                    validation_results.append("✅ Account 886557 is most active as expected")
                else:
                    validation_results.append(f"⚠️ Account {most_active_account} is most active (expected 886557)")
            
            # Determine overall status
            failed_checks = [result for result in validation_results if result.startswith("❌")]
            overall_status = 'PASS' if len(failed_checks) == 0 else 'FAIL'
            
            return {
                'test_name': test_name,
                'status': overall_status,
                'validation_results': validation_results,
                'details': {
                    'account_patterns': {k: {
                        'trade_count': v['trade_count'],
                        'symbols': list(v['symbols']),
                        'avg_volume': round(v['avg_volume'], 2),
                        'total_profit': round(v['total_profit'], 2)
                    } for k, v in account_patterns.items()},
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

    async def test_database_collections(self) -> Dict[str, Any]:
        """Test that database collections store data for all 4 accounts"""
        test_name = "Database Collections Multi-Account"
        logger.info(f"🧪 Testing {test_name}")
        
        try:
            validation_results = []
            
            # First, trigger a sync to ensure collections have data
            sync_url = f"{self.backend_url}/admin/trading/analytics/sync"
            async with self.session.post(sync_url) as sync_response:
                if sync_response.status == 200:
                    validation_results.append("✅ Sync endpoint accessible for collection population")
                else:
                    validation_results.append("❌ Sync endpoint not accessible")
            
            # Test mt5_trades collection - should have trades for all accounts
            trades_url = f"{self.backend_url}/admin/trading/analytics/trades?account=0&limit=100"
            async with self.session.get(trades_url) as trades_response:
                if trades_response.status == 200:
                    trades_data = await trades_response.json()
                    trades = trades_data.get('trades', [])
                    
                    if trades:
                        validation_results.append(f"✅ MT5 trades collection accessible ({len(trades)} trades)")
                        
                        # Check if trades from all accounts are present
                        account_numbers = set(trade.get('account') for trade in trades)
                        expected_accounts = set(self.all_accounts)
                        
                        if account_numbers.intersection(expected_accounts):
                            validation_results.append(f"✅ Trades from multiple accounts in collection: {sorted(account_numbers)}")
                        else:
                            validation_results.append(f"❌ No trades from expected accounts: {sorted(account_numbers)}")
                    else:
                        validation_results.append("⚠️ MT5 trades collection empty")
                else:
                    validation_results.append("❌ MT5 trades collection not accessible")
            
            # Test daily_performance collection - should have entries for all accounts
            daily_url = f"{self.backend_url}/admin/trading/analytics/daily?account=0&days=7"
            async with self.session.get(daily_url) as daily_response:
                if daily_response.status == 200:
                    daily_data = await daily_response.json()
                    daily_performance = daily_data.get('daily_performance', [])
                    
                    if daily_performance:
                        validation_results.append(f"✅ Daily performance collection accessible ({len(daily_performance)} entries)")
                        
                        # Check aggregation functionality
                        sample_entry = daily_performance[0]
                        if 'total_trades' in sample_entry and 'total_pnl' in sample_entry:
                            validation_results.append("✅ Daily performance aggregation working")
                        else:
                            validation_results.append("❌ Daily performance aggregation incomplete")
                    else:
                        validation_results.append("⚠️ Daily performance collection empty")
                else:
                    validation_results.append("❌ Daily performance collection not accessible")
            
            # Test individual account daily performance
            accounts_with_daily_data = []
            for account_num in self.all_accounts:
                daily_account_url = f"{self.backend_url}/admin/trading/analytics/daily?account={account_num}&days=3"
                async with self.session.get(daily_account_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        daily_data = data.get('daily_performance', [])
                        if daily_data:
                            accounts_with_daily_data.append(account_num)
            
            if accounts_with_daily_data:
                validation_results.append(f"✅ Daily performance data exists for accounts: {accounts_with_daily_data}")
            else:
                validation_results.append("⚠️ No daily performance data for individual accounts")
            
            # Test analytics overview aggregation pipeline
            overview_url = f"{self.backend_url}/admin/trading/analytics/overview?account=0"
            async with self.session.get(overview_url) as overview_response:
                if overview_response.status == 200:
                    overview_data = await overview_response.json()
                    analytics = overview_data.get('analytics', {})
                    
                    if analytics and 'overview' in analytics:
                        validation_results.append("✅ Analytics aggregation pipeline working")
                        
                        overview = analytics['overview']
                        if overview.get('total_trades', 0) > 0:
                            validation_results.append(f"✅ Aggregated analytics show activity: {overview.get('total_trades')} trades")
                        else:
                            validation_results.append("⚠️ Aggregated analytics show no activity")
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
                    'collections_tested': ['mt5_trades', 'daily_performance'],
                    'accounts_with_data': accounts_with_daily_data,
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
        
        # Run all Phase 1B multi-account tests
        tests = [
            self.test_multi_account_overview_endpoint,
            self.test_multi_account_daily_performance,
            self.test_multi_account_trades_endpoint,
            self.test_multi_account_sync_endpoint,
            self.test_mock_data_variation,
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
        logger.info("📊 Trading Analytics Phase 1B Multi-Account Test Summary:")
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
                'all_accounts': self.all_accounts,
                'test_days': self.test_days,
                'phase': '1B Multi-Account'
            }
        }
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Test cleanup completed")

async def main():
    """Main test execution"""
    test_suite = TradingAnalyticsPhase1BTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*80)
        print("TRADING ANALYTICS PHASE 1B MULTI-ACCOUNT TEST RESULTS")
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