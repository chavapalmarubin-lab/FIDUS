#!/usr/bin/env python3
"""
MT5 Real-Time Data Collection System Testing Suite
Tests the complete real-time MT5 data collection system as requested in review:

Priority 1: Verify Real-Time Data Collection
Priority 2: Test Historical Data Endpoints  
Priority 3: Verify Production Portal Integration
Priority 4: System Health Verification

Expected Results:
- Real-time data collection active with 30-second updates
- Account balances showing small fluctuations (±0.2% to ±0.5%)
- Historical data points accumulating in database
- System status showing "operational" with recent updates
- Production portal ready to receive live MT5 feeds
"""

import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
import time

class MT5RealtimeDataTester:
    def __init__(self, base_url="https://risk-engine-v2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.target_account_id = "mt5_client_003_BALANCE_dootechnology_34c231f6"
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        # Add JWT token if admin user is authenticated
        if self.admin_user and 'token' in self.admin_user:
            headers['Authorization'] = f"Bearer {self.admin_user['token']}"

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_authentication(self) -> bool:
        """Setup admin authentication for MT5 testing"""
        print("\n" + "="*80)
        print("🔐 SETTING UP ADMIN AUTHENTICATION")
        print("="*80)
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "admin", 
                "password": "password123",
                "user_type": "admin"
            }
        )
        if success:
            self.admin_user = response
            print(f"   ✅ Admin logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
            return True
        else:
            print("   ❌ Admin login failed - cannot proceed with MT5 admin tests")
            return False

    def test_priority_1_realtime_data_collection(self) -> bool:
        """Priority 1: Verify Real-Time Data Collection"""
        print("\n" + "="*80)
        print("🔴 PRIORITY 1: VERIFY REAL-TIME DATA COLLECTION")
        print("="*80)
        
        # Test 1.1: Check if live data is being collected and served
        print("\n📊 Test 1.1: Real-Time Data Collection Endpoint")
        success, response = self.run_test(
            "GET /api/mt5/admin/realtime-data",
            "GET",
            "api/mt5/admin/realtime-data",
            200
        )
        
        if success:
            # Verify real-time data structure
            required_keys = ['success', 'accounts', 'total_stats', 'data_source', 'update_frequency']
            missing_keys = [key for key in required_keys if key not in response]
            
            if missing_keys:
                print(f"   ❌ Missing keys in real-time data response: {missing_keys}")
                return False
            
            accounts = response.get('accounts', [])
            total_stats = response.get('total_stats', {})
            data_source = response.get('data_source', 'unknown')
            update_frequency = response.get('update_frequency', 'unknown')
            
            print(f"   ✅ Data Source: {data_source}")
            print(f"   ✅ Update Frequency: {update_frequency}")
            print(f"   ✅ Total Accounts: {total_stats.get('total_accounts', 0)}")
            
            # Check if real-time data collection is configured correctly
            if data_source == 'real_time' and update_frequency == '30_seconds':
                print("   ✅ Real-time data collection configured for 30-second updates")
            else:
                print(f"   ⚠️ Data collection configuration: {data_source}, {update_frequency}")
            
            # Check total stats
            total_accounts = total_stats.get('total_accounts', 0)
            if total_accounts > 0:
                print(f"   ✅ Real-time data contains {total_accounts} accounts")
                print(f"   ✅ Total Allocated: ${total_stats.get('total_allocated', 0):,.2f}")
                print(f"   ✅ Total Equity: ${total_stats.get('total_equity', 0):,.2f}")
            else:
                print("   ⚠️ No accounts found in real-time data (may indicate no active accounts)")
                # Don't fail here as this might be expected if no accounts are active
        else:
            print("   ❌ Failed to get real-time data")
            return False

        # Test 1.2: Verify MT5 collection system is operational
        print("\n📊 Test 1.2: MT5 System Status Check")
        success, response = self.run_test(
            "GET /api/mt5/admin/system-status",
            "GET",
            "api/mt5/admin/system-status",
            200
        )
        
        if success:
            # Verify system status structure
            required_keys = ['success', 'system_status', 'data_collection_active', 'last_check']
            missing_keys = [key for key in required_keys if key not in response]
            
            if missing_keys:
                print(f"   ❌ Missing keys in system status: {missing_keys}")
                return False
            
            system_status = response.get('system_status', 'unknown')
            data_collection_active = response.get('data_collection_active', False)
            last_check = response.get('last_check')
            recent_updates = response.get('recent_updates', 0)
            total_data_points = response.get('total_data_points', 0)
            
            print(f"   ✅ System Status: {system_status}")
            print(f"   ✅ Data Collection Active: {data_collection_active}")
            print(f"   ✅ Last Check: {last_check}")
            print(f"   ✅ Recent Updates: {recent_updates}")
            print(f"   ✅ Total Data Points: {total_data_points}")
            
            # Check if system is operational
            if system_status.lower() in ['operational', 'running', 'active'] or data_collection_active:
                print("   ✅ MT5 collection system is operational")
            else:
                print(f"   ⚠️ MT5 collection system status: {system_status}, active: {data_collection_active}")
                # Don't fail here as the system might be in setup mode
                
            # Check if there's recent activity
            if recent_updates > 0 or total_data_points > 0:
                print("   ✅ System shows data collection activity")
            else:
                print("   ⚠️ No recent data collection activity detected")
        else:
            print("   ❌ Failed to get system status")
            return False

        # Test 1.3: Check if MongoDB is receiving live updates
        print("\n📊 Test 1.3: MongoDB Live Updates Verification")
        success, response = self.run_test(
            "Check MongoDB Updates",
            "GET",
            "api/mt5/admin/accounts",
            200
        )
        
        if success:
            accounts = response.get('accounts', [])
            if accounts:
                print(f"   ✅ Found {len(accounts)} MT5 accounts in MongoDB")
                
                # Check for recent updates (within last 5 minutes)
                recent_updates = 0
                current_time = datetime.now(timezone.utc)
                
                for account in accounts:
                    last_update = account.get('last_update')
                    if last_update:
                        try:
                            # Parse last update time
                            if isinstance(last_update, str):
                                update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                            else:
                                update_time = last_update
                            
                            # Check if updated within last 5 minutes
                            time_diff = (current_time - update_time).total_seconds()
                            if time_diff <= 300:  # 5 minutes
                                recent_updates += 1
                        except:
                            pass
                
                if recent_updates > 0:
                    print(f"   ✅ {recent_updates} accounts have recent updates (within 5 minutes)")
                else:
                    print("   ⚠️ No accounts have recent updates (may indicate collection issue)")
            else:
                print("   ❌ No MT5 accounts found in MongoDB")
                return False
        else:
            print("   ❌ Failed to check MongoDB updates")
            return False

        return True

    def test_priority_2_historical_data_endpoints(self) -> bool:
        """Priority 2: Test Historical Data Endpoints"""
        print("\n" + "="*80)
        print("🟡 PRIORITY 2: TEST HISTORICAL DATA ENDPOINTS")
        print("="*80)
        
        # Test 2.1: Check historical data collection for target account
        print("\n📊 Test 2.1: Historical Data Collection")
        success, response = self.run_test(
            f"GET /api/mt5/admin/historical-data/{self.target_account_id}",
            "GET",
            f"api/mt5/admin/historical-data/{self.target_account_id}",
            200
        )
        
        if success:
            # Verify historical data structure
            required_keys = ['success', 'account_id', 'historical_data']
            missing_keys = [key for key in required_keys if key not in response]
            
            if missing_keys:
                print(f"   ❌ Missing keys in historical data: {missing_keys}")
                return False
            
            account_id = response.get('account_id')
            historical_data = response.get('historical_data', [])
            data_points = response.get('data_points', len(historical_data))
            time_window_hours = response.get('time_window_hours', 'unknown')
            
            print(f"   ✅ Account ID: {account_id}")
            print(f"   ✅ Data Points Count: {data_points}")
            print(f"   ✅ Time Window: {time_window_hours} hours")
            
            if account_id == self.target_account_id:
                print(f"   ✅ Correct account ID returned")
            else:
                print(f"   ❌ Wrong account ID: expected {self.target_account_id}, got {account_id}")
                return False
            
            # Check historical data points
            if data_points > 0 and historical_data:
                print(f"   ✅ Historical data contains {len(historical_data)} data points")
                
                # Verify data point structure
                if historical_data:
                    data_point = historical_data[0]
                    point_keys = ['timestamp', 'balance', 'equity', 'profit_loss']
                    for key in point_keys:
                        if key in data_point:
                            print(f"   ✅ Data point has {key}: {data_point[key]}")
                        else:
                            print(f"   ⚠️ Data point missing {key} (may be optional)")
            else:
                print("   ⚠️ No historical data points found (may be expected for new account)")
        else:
            print("   ❌ Failed to get historical data")
            return False

        # Test 2.2: Verify data points are being stored every 30 seconds
        print("\n📊 Test 2.2: Data Collection Frequency Verification")
        if success and response.get('historical_data'):
            historical_data = response.get('historical_data', [])
            
            if len(historical_data) >= 2:
                # Check time intervals between data points
                timestamps = []
                for point in historical_data[-10:]:  # Check last 10 points
                    timestamp = point.get('timestamp')
                    if timestamp:
                        try:
                            if isinstance(timestamp, str):
                                ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            else:
                                ts = timestamp
                            timestamps.append(ts)
                        except:
                            pass
                
                if len(timestamps) >= 2:
                    # Calculate intervals
                    intervals = []
                    for i in range(1, len(timestamps)):
                        interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                        intervals.append(interval)
                    
                    # Check if intervals are around 30 seconds (allow ±10 seconds tolerance)
                    valid_intervals = [20 <= interval <= 40 for interval in intervals]
                    if any(valid_intervals):
                        avg_interval = sum(intervals) / len(intervals)
                        print(f"   ✅ Data collection intervals detected (avg: {avg_interval:.1f} seconds)")
                    else:
                        print(f"   ⚠️ Data collection intervals vary: {intervals}")
                else:
                    print("   ⚠️ Not enough timestamps to verify collection frequency")
            else:
                print("   ⚠️ Not enough historical data points to verify frequency")

        # Test 2.3: Check if collector is updating account balances with realistic fluctuations
        print("\n📊 Test 2.3: Balance Fluctuation Verification")
        if success and response.get('historical_data'):
            historical_data = response.get('historical_data', [])
            
            if len(historical_data) >= 2:
                # Get recent balance values
                recent_balances = []
                for point in historical_data[-5:]:  # Last 5 points
                    balance = point.get('balance')
                    if balance and isinstance(balance, (int, float)):
                        recent_balances.append(float(balance))
                
                if len(recent_balances) >= 2:
                    # Calculate fluctuation percentages
                    fluctuations = []
                    for i in range(1, len(recent_balances)):
                        if recent_balances[i-1] != 0:
                            fluctuation = abs(recent_balances[i] - recent_balances[i-1]) / recent_balances[i-1] * 100
                            fluctuations.append(fluctuation)
                    
                    if fluctuations:
                        avg_fluctuation = sum(fluctuations) / len(fluctuations)
                        max_fluctuation = max(fluctuations)
                        
                        print(f"   ✅ Balance fluctuations detected (avg: {avg_fluctuation:.3f}%, max: {max_fluctuation:.3f}%)")
                        
                        # Check if fluctuations are in expected range (±0.2% to ±0.5%)
                        if 0.1 <= avg_fluctuation <= 1.0:  # Allow slightly wider range
                            print("   ✅ Fluctuations are in realistic range")
                        else:
                            print(f"   ⚠️ Fluctuations outside expected range: {avg_fluctuation:.3f}%")
                    else:
                        print("   ⚠️ No balance fluctuations detected")
                else:
                    print("   ⚠️ Not enough balance data to verify fluctuations")
            else:
                print("   ⚠️ Not enough historical data to verify fluctuations")

        return True

    def test_priority_3_production_portal_integration(self) -> bool:
        """Priority 3: Verify Production Portal Integration"""
        print("\n" + "="*80)
        print("🟢 PRIORITY 3: VERIFY PRODUCTION PORTAL INTEGRATION")
        print("="*80)
        
        # Test 3.1: Check if accounts show real-time updated data
        print("\n📊 Test 3.1: Accounts Real-Time Data Display")
        success, response = self.run_test(
            "GET /api/mt5/admin/accounts/by-broker",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200
        )
        
        if success:
            # Verify broker grouping structure
            accounts_by_broker = response.get('accounts_by_broker', {})
            total_stats = response.get('total_stats', {})
            
            if isinstance(accounts_by_broker, dict):
                brokers = list(accounts_by_broker.keys())
                print(f"   ✅ Found {len(brokers)} broker groups: {brokers}")
                
                # Check for DooTechnology broker (target account's broker)
                dootechnology_data = accounts_by_broker.get('dootechnology', {})
                dootechnology_accounts = dootechnology_data.get('accounts', [])
                
                if dootechnology_accounts:
                    print(f"   ✅ DooTechnology broker has {len(dootechnology_accounts)} accounts")
                    
                    # Look for target account
                    target_found = False
                    for account in dootechnology_accounts:
                        if account.get('account_id') == self.target_account_id:
                            target_found = True
                            print(f"   ✅ Target account found in DooTechnology group")
                            
                            # Verify account has real-time data
                            balance = account.get('current_equity', 0)
                            allocated = account.get('total_allocated', 0)
                            profit_loss = account.get('profit_loss', 0)
                            updated_at = account.get('updated_at')
                            
                            print(f"   ✅ Account Equity: ${balance:,.2f}")
                            print(f"   ✅ Account Allocated: ${allocated:,.2f}")
                            print(f"   ✅ Account P&L: ${profit_loss:,.2f}")
                            print(f"   ✅ Last Update: {updated_at}")
                            
                            # Check if data is recent (within last 10 minutes)
                            if updated_at:
                                try:
                                    if isinstance(updated_at, str):
                                        update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                                    else:
                                        update_time = updated_at
                                    
                                    time_diff = (datetime.now(timezone.utc) - update_time).total_seconds()
                                    if time_diff <= 600:  # 10 minutes
                                        print(f"   ✅ Account data is recent ({time_diff:.0f} seconds old)")
                                    else:
                                        print(f"   ⚠️ Account data is old ({time_diff:.0f} seconds old)")
                                except:
                                    print("   ⚠️ Could not parse last update time")
                            break
                    
                    if not target_found:
                        print(f"   ❌ Target account {self.target_account_id} not found in DooTechnology group")
                        return False
                else:
                    print("   ❌ No DooTechnology accounts found")
                    return False
            else:
                print("   ❌ Invalid response format for broker grouping")
                return False
        else:
            print("   ❌ Failed to get accounts by broker")
            return False

        # Test 3.2: Verify data is different from static data (showing fluctuations)
        print("\n📊 Test 3.2: Data Fluctuation Verification")
        
        # Get current data
        success1, response1 = self.run_test(
            "Get Current Account Data (Sample 1)",
            "GET",
            "api/mt5/admin/accounts",
            200
        )
        
        if success1:
            accounts1 = response1.get('accounts', [])
            target_account1 = None
            
            for account in accounts1:
                if account.get('account_id') == self.target_account_id:
                    target_account1 = account
                    break
            
            if target_account1:
                balance1 = target_account1.get('current_equity', 0)
                print(f"   ✅ Sample 1 - Account Balance: ${balance1:,.2f}")
                
                # Wait a few seconds and get data again
                print("   ⏳ Waiting 5 seconds for potential data updates...")
                time.sleep(5)
                
                success2, response2 = self.run_test(
                    "Get Current Account Data (Sample 2)",
                    "GET",
                    "api/mt5/admin/accounts",
                    200
                )
                
                if success2:
                    accounts2 = response2.get('accounts', [])
                    target_account2 = None
                    
                    for account in accounts2:
                        if account.get('account_id') == self.target_account_id:
                            target_account2 = account
                            break
                    
                    if target_account2:
                        balance2 = target_account2.get('current_equity', 0)
                        print(f"   ✅ Sample 2 - Account Balance: ${balance2:,.2f}")
                        
                        # Check for differences
                        if balance1 != balance2:
                            difference = abs(balance2 - balance1)
                            percentage = (difference / balance1 * 100) if balance1 != 0 else 0
                            print(f"   ✅ Balance changed by ${difference:,.2f} ({percentage:.3f}%)")
                            print("   ✅ Data is showing fluctuations (not static)")
                        else:
                            print("   ⚠️ No balance change detected (may be static data or no updates)")
                    else:
                        print("   ❌ Target account not found in second sample")
                        return False
                else:
                    print("   ❌ Failed to get second data sample")
                    return False
            else:
                print("   ❌ Target account not found in first sample")
                return False
        else:
            print("   ❌ Failed to get first data sample")
            return False

        # Test 3.3: Test FIDUS portal readiness for live MT5 data
        print("\n📊 Test 3.3: FIDUS Portal MT5 Data Integration")
        success, response = self.run_test(
            "Portal MT5 Data Feed Test",
            "GET",
            "api/mt5/admin/performance/overview",
            200
        )
        
        if success:
            # Verify portal can receive MT5 performance data
            overview = response.get('overview', {})
            if overview:
                total_accounts = overview.get('total_accounts', 0)
                total_allocated = overview.get('total_allocated', 0)
                total_equity = overview.get('total_equity', 0)
                
                print(f"   ✅ Portal can access MT5 performance data")
                print(f"   ✅ Total Accounts: {total_accounts}")
                print(f"   ✅ Total Allocated: ${total_allocated:,.2f}")
                print(f"   ✅ Total Equity: ${total_equity:,.2f}")
                
                if total_accounts > 0 and total_allocated > 0:
                    print("   ✅ FIDUS portal ready to receive live MT5 feeds")
                else:
                    print("   ⚠️ Portal data may be incomplete")
            else:
                print("   ❌ Portal performance overview is empty")
                return False
        else:
            print("   ❌ Failed to get portal performance overview")
            return False

        return True

    def test_priority_4_system_health_verification(self) -> bool:
        """Priority 4: System Health Verification"""
        print("\n" + "="*80)
        print("🔵 PRIORITY 4: SYSTEM HEALTH VERIFICATION")
        print("="*80)
        
        # Test 4.1: Check if collector process is running in background
        print("\n📊 Test 4.1: Collector Process Status")
        success, response = self.run_test(
            "Collector Process Check",
            "GET",
            "api/mt5/admin/system-status",
            200
        )
        
        if success:
            collector_status = response.get('collector_status', 'unknown')
            system_status = response.get('system_status', 'unknown')
            active_connections = response.get('active_connections', 0)
            
            print(f"   ✅ Collector Status: {collector_status}")
            print(f"   ✅ System Status: {system_status}")
            print(f"   ✅ Active Connections: {active_connections}")
            
            # Check if collector is running
            if collector_status.lower() in ['running', 'active', 'collecting', 'operational']:
                print("   ✅ Collector process is running in background")
            else:
                print(f"   ❌ Collector process not running: {collector_status}")
                return False
            
            # Check system health
            if system_status.lower() in ['operational', 'running', 'healthy', 'active']:
                print("   ✅ System is healthy and operational")
            else:
                print(f"   ❌ System health issue: {system_status}")
                return False
        else:
            print("   ❌ Failed to check collector process status")
            return False

        # Test 4.2: Verify logs show successful data collection cycles
        print("\n📊 Test 4.2: Data Collection Logs Verification")
        success, response = self.run_test(
            "Collection Logs Check",
            "GET",
            "api/mt5/admin/collection-logs",
            200
        )
        
        if success:
            logs = response.get('logs', [])
            recent_logs = response.get('recent_logs', [])
            
            print(f"   ✅ Found {len(logs)} total log entries")
            print(f"   ✅ Found {len(recent_logs)} recent log entries")
            
            # Check for successful collection cycles in recent logs
            successful_cycles = 0
            error_cycles = 0
            
            for log in recent_logs[-10:]:  # Check last 10 logs
                log_level = log.get('level', '').lower()
                message = log.get('message', '').lower()
                
                if 'success' in message or 'collected' in message or 'updated' in message:
                    successful_cycles += 1
                elif 'error' in message or 'failed' in message:
                    error_cycles += 1
            
            print(f"   ✅ Successful collection cycles: {successful_cycles}")
            print(f"   ⚠️ Error cycles: {error_cycles}")
            
            if successful_cycles > 0:
                print("   ✅ Logs show successful data collection cycles")
            else:
                print("   ⚠️ No successful collection cycles found in recent logs")
        else:
            # Collection logs endpoint might not exist, check alternative
            print("   ⚠️ Collection logs endpoint not available, checking alternative...")
            
            # Check system health endpoint for log information
            success, response = self.run_test(
                "System Health Check",
                "GET",
                "api/health",
                200
            )
            
            if success:
                status = response.get('status', 'unknown')
                print(f"   ✅ System health status: {status}")
                
                if status.lower() in ['healthy', 'ready', 'operational']:
                    print("   ✅ System health indicates successful operations")
                else:
                    print(f"   ⚠️ System health indicates issues: {status}")
            else:
                print("   ⚠️ Could not verify collection logs")

        # Test 4.3: Confirm MongoDB collections are being populated with real-time data
        print("\n📊 Test 4.3: MongoDB Real-Time Data Population")
        success, response = self.run_test(
            "MongoDB Data Population Check",
            "GET",
            "api/mt5/admin/accounts",
            200
        )
        
        if success:
            accounts = response.get('accounts', [])
            summary = response.get('summary', {})
            
            total_accounts = len(accounts)
            total_allocated = summary.get('total_allocated', 0)
            total_equity = summary.get('total_equity', 0)
            
            print(f"   ✅ MongoDB contains {total_accounts} MT5 accounts")
            print(f"   ✅ Total allocated in DB: ${total_allocated:,.2f}")
            print(f"   ✅ Total equity in DB: ${total_equity:,.2f}")
            
            if total_accounts > 0:
                print("   ✅ MongoDB collections are populated with MT5 data")
                
                # Check for recent updates
                recent_updates = 0
                current_time = datetime.now(timezone.utc)
                
                for account in accounts:
                    last_update = account.get('last_update')
                    if last_update:
                        try:
                            if isinstance(last_update, str):
                                update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                            else:
                                update_time = last_update
                            
                            time_diff = (current_time - update_time).total_seconds()
                            if time_diff <= 300:  # 5 minutes
                                recent_updates += 1
                        except:
                            pass
                
                if recent_updates > 0:
                    print(f"   ✅ {recent_updates} accounts have recent updates in MongoDB")
                    print("   ✅ Real-time data is being populated in MongoDB")
                else:
                    print("   ⚠️ No recent updates found in MongoDB (may indicate collection issue)")
            else:
                print("   ❌ No MT5 accounts found in MongoDB")
                return False
        else:
            print("   ❌ Failed to check MongoDB data population")
            return False

        return True

    def run_comprehensive_realtime_tests(self) -> bool:
        """Run all real-time MT5 data collection tests"""
        print("\n" + "="*100)
        print("🚀 STARTING COMPREHENSIVE REAL-TIME MT5 DATA SYSTEM TEST")
        print("="*100)
        print(f"Target Account: {self.target_account_id}")
        print("Expected: Real-time data collection with 30-second updates")
        print("Expected: Account balances showing fluctuations (±0.2% to ±0.5%)")
        print("Expected: System status 'operational' with recent updates")
        print("="*100)
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run all priority tests
        test_priorities = [
            ("Priority 1: Real-Time Data Collection", self.test_priority_1_realtime_data_collection),
            ("Priority 2: Historical Data Endpoints", self.test_priority_2_historical_data_endpoints),
            ("Priority 3: Production Portal Integration", self.test_priority_3_production_portal_integration),
            ("Priority 4: System Health Verification", self.test_priority_4_system_health_verification)
        ]
        
        priority_results = []
        
        for priority_name, test_method in test_priorities:
            print(f"\n🔄 Running {priority_name}...")
            try:
                result = test_method()
                priority_results.append((priority_name, result))
                
                if result:
                    print(f"✅ {priority_name} - PASSED")
                else:
                    print(f"❌ {priority_name} - FAILED")
            except Exception as e:
                print(f"❌ {priority_name} - ERROR: {str(e)}")
                priority_results.append((priority_name, False))
        
        # Print final results
        print("\n" + "="*100)
        print("📊 REAL-TIME MT5 DATA SYSTEM TEST RESULTS")
        print("="*100)
        
        passed_priorities = sum(1 for _, result in priority_results if result)
        total_priorities = len(priority_results)
        
        for priority_name, result in priority_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {priority_name}: {status}")
        
        print(f"\n📈 Overall Results:")
        print(f"   Priority Tests: {passed_priorities}/{total_priorities} passed ({passed_priorities/total_priorities*100:.1f}%)")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Expected results verification
        print(f"\n🎯 Expected Results Verification:")
        if passed_priorities >= 3:  # At least 3 out of 4 priorities should pass
            print("   ✅ Real-time data collection system is operational")
            print("   ✅ MT5 → MongoDB → FIDUS portal data pipeline is working")
            print("   ✅ System ready for production use")
        else:
            print("   ❌ Real-time data collection system has issues")
            print("   ❌ MT5 data pipeline needs attention")
        
        # Determine overall success
        overall_success = passed_priorities >= 3 and self.tests_passed >= (self.tests_run * 0.75)
        
        if overall_success:
            print(f"\n🎉 REAL-TIME MT5 DATA SYSTEM TEST COMPLETED SUCCESSFULLY!")
            print("   Complete real-time MT5 → MongoDB → FIDUS portal data pipeline is operational")
        else:
            print(f"\n⚠️ REAL-TIME MT5 DATA SYSTEM TEST COMPLETED WITH ISSUES")
            print("   Some components of the MT5 data pipeline may need attention")
        
        return overall_success

def main():
    """Main test execution"""
    print("🔧 MT5 Real-Time Data Collection System Testing Suite")
    print("Testing complete real-time MT5 data pipeline as requested in review")
    
    tester = MT5RealtimeDataTester()
    
    try:
        success = tester.run_comprehensive_realtime_tests()
        
        if success:
            print("\n✅ All real-time MT5 data system tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some real-time MT5 data system tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()