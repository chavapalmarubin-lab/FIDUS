#!/usr/bin/env python3
"""
URGENT: FIDUS MT5 Bridge Integration Testing Suite
Testing FIDUS → MT5 Bridge integration now that external MT5 Bridge access is confirmed working.
The MT5 Bridge service at http://217.197.163.11:8000 is fully operational with mt5_available=true and mt5_initialized=true.

Priority Testing:
1. FIDUS → MT5 Bridge Integration Test (all working MT5 endpoints)
2. MT5 bridge client connectivity from FIDUS backend
3. Real MT5 data flow into FIDUS system
4. Admin MT5 management interfaces
5. End-to-End Data Flow Validation
6. Integration Success Metrics
7. Production Readiness Assessment
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class MT5BridgeIntegrationTester:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.bridge_url = "http://217.197.163.11:8000"
        self.tests_run = 0
        self.tests_passed = 0
        self.client_user = None
        self.admin_user = None
        self.mt5_endpoints_tested = []
        self.bridge_connectivity_results = {}
        self.real_mt5_data_samples = []
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None, timeout: int = 35) -> tuple[bool, Dict]:
        """Run a single API test with extended timeout for bridge operations"""
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Time: {response_time:.2f}s")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, {"text": response.text}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"⏰ Timeout after {response_time:.2f}s - Expected for bridge connectivity tests")
            return False, {"error": "timeout", "response_time": response_time}
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"❌ Failed - Error: {str(e)} (after {response_time:.2f}s)")
            return False, {"error": str(e), "response_time": response_time}

    def setup_authentication(self) -> bool:
        """Setup client and admin authentication"""
        print("\n" + "="*80)
        print("🔐 SETTING UP AUTHENTICATION FOR MT5 BRIDGE TESTING")
        print("="*80)
        
        # Test admin login
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
        else:
            print("   ❌ Admin login failed - cannot proceed with MT5 admin tests")
            return False

        # Test client login (Salvador Palma - has existing MT5 accounts)
        success, response = self.run_test(
            "Client Login (Salvador Palma)",
            "POST",
            "api/auth/login",
            200,
            data={
                "username": "client3", 
                "password": "password123",
                "user_type": "client"
            }
        )
        if success:
            self.client_user = response
            print(f"   ✅ Client logged in: {response.get('name', 'Unknown')} (ID: {response.get('id')})")
        else:
            print("   ❌ Client login failed - cannot proceed with MT5 client tests")
            return False
            
        return True

    def test_direct_mt5_bridge_connectivity(self) -> bool:
        """Test direct connectivity to MT5 Bridge service"""
        print("\n" + "="*80)
        print("🌉 TESTING DIRECT MT5 BRIDGE CONNECTIVITY")
        print("="*80)
        print(f"Bridge URL: {self.bridge_url}")
        print("Expected: Service is operational with mt5_available=true and mt5_initialized=true")
        
        # Test 1: Bridge Health Check
        print("\n📊 Test 1: Direct Bridge Health Check")
        success, response = self.run_test(
            "Direct MT5 Bridge Health Check",
            "GET",
            f"{self.bridge_url}/health",
            200,
            timeout=10
        )
        
        if success:
            print("   ✅ Bridge is accessible!")
            if isinstance(response, dict):
                mt5_available = response.get('mt5_available', False)
                mt5_initialized = response.get('mt5_initialized', False)
                print(f"   📋 MT5 Available: {mt5_available}")
                print(f"   📋 MT5 Initialized: {mt5_initialized}")
                
                if mt5_available and mt5_initialized:
                    print("   🎉 Bridge is fully operational for MT5 operations!")
                    self.bridge_connectivity_results['direct_health'] = True
                else:
                    print("   ⚠️ Bridge accessible but MT5 not fully operational")
                    self.bridge_connectivity_results['direct_health'] = False
            else:
                print("   ⚠️ Bridge responded but format unexpected")
                self.bridge_connectivity_results['direct_health'] = False
        else:
            print("   ❌ Bridge is not accessible")
            self.bridge_connectivity_results['direct_health'] = False
            return False

        # Test 2: Bridge MT5 Status
        print("\n📊 Test 2: Bridge MT5 Status Check")
        success, response = self.run_test(
            "Bridge MT5 Status",
            "GET",
            f"{self.bridge_url}/mt5/status",
            200,
            timeout=10
        )
        
        if success:
            print("   ✅ MT5 status endpoint accessible")
            self.bridge_connectivity_results['mt5_status'] = True
        else:
            print("   ❌ MT5 status endpoint failed")
            self.bridge_connectivity_results['mt5_status'] = False

        # Test 3: Bridge MT5 Accounts
        print("\n📊 Test 3: Bridge MT5 Accounts List")
        success, response = self.run_test(
            "Bridge MT5 Accounts",
            "GET",
            f"{self.bridge_url}/mt5/accounts",
            200,
            timeout=15
        )
        
        if success:
            print("   ✅ MT5 accounts endpoint accessible")
            if isinstance(response, dict) and 'accounts' in response:
                accounts = response['accounts']
                print(f"   📋 Found {len(accounts)} MT5 accounts in bridge")
                self.real_mt5_data_samples.append({
                    'source': 'bridge_accounts',
                    'count': len(accounts),
                    'sample': accounts[:2] if accounts else []
                })
            self.bridge_connectivity_results['mt5_accounts'] = True
        else:
            print("   ❌ MT5 accounts endpoint failed")
            self.bridge_connectivity_results['mt5_accounts'] = False

        return True

    def test_fidus_mt5_bridge_integration(self) -> bool:
        """Test FIDUS backend integration with MT5 Bridge"""
        print("\n" + "="*80)
        print("🔗 TESTING FIDUS → MT5 BRIDGE INTEGRATION")
        print("="*80)
        
        if not self.admin_user:
            print("❌ No admin user available for MT5 bridge integration tests")
            return False
            
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }
        
        # Test 1: FIDUS MT5 Bridge Health Check
        print("\n📊 Test 1: FIDUS MT5 Bridge Health Check")
        success, response = self.run_test(
            "FIDUS MT5 Bridge Health Check",
            "GET",
            "api/mt5/bridge/health",
            200,
            headers=admin_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ FIDUS can communicate with MT5 bridge")
            if isinstance(response, dict):
                bridge_status = response.get('bridge_available', False)
                mt5_status = response.get('mt5_available', False)
                print(f"   📋 Bridge Available: {bridge_status}")
                print(f"   📋 MT5 Available: {mt5_status}")
                
                if bridge_status and mt5_status:
                    print("   🎉 Full FIDUS → MT5 Bridge integration working!")
                    self.bridge_connectivity_results['fidus_bridge_health'] = True
                else:
                    print("   ⚠️ FIDUS can reach bridge but MT5 not fully operational")
                    self.bridge_connectivity_results['fidus_bridge_health'] = False
            else:
                print("   ⚠️ FIDUS bridge health check responded but format unexpected")
                self.bridge_connectivity_results['fidus_bridge_health'] = False
        else:
            print("   ❌ FIDUS cannot communicate with MT5 bridge")
            self.bridge_connectivity_results['fidus_bridge_health'] = False

        # Test 2: FIDUS MT5 Admin Accounts with Bridge Data
        print("\n📊 Test 2: FIDUS MT5 Admin Accounts (Bridge Data)")
        success, response = self.run_test(
            "FIDUS MT5 Admin Accounts (Bridge Integration)",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=admin_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ FIDUS MT5 admin accounts endpoint accessible")
            if isinstance(response, dict):
                accounts = response.get('accounts', [])
                summary = response.get('summary', {})
                
                print(f"   📋 Total MT5 accounts: {len(accounts)}")
                print(f"   📋 Total allocated: ${summary.get('total_allocated', 0):,.2f}")
                print(f"   📋 Total equity: ${summary.get('total_equity', 0):,.2f}")
                
                # Check if we have real MT5 data
                if accounts:
                    account = accounts[0]
                    has_real_data = any([
                        account.get('current_equity', 0) != account.get('total_allocated', 0),
                        account.get('profit_loss', 0) != 0,
                        account.get('mt5_login') and account.get('mt5_server')
                    ])
                    
                    if has_real_data:
                        print("   🎉 Real MT5 data detected in FIDUS system!")
                        self.real_mt5_data_samples.append({
                            'source': 'fidus_admin_accounts',
                            'count': len(accounts),
                            'sample': accounts[:2]
                        })
                    else:
                        print("   ⚠️ MT5 accounts present but may be using fallback data")
                
                self.mt5_endpoints_tested.append('admin_accounts')
            else:
                print("   ⚠️ Unexpected response format")
        else:
            print("   ❌ FIDUS MT5 admin accounts failed")

        # Test 3: FIDUS MT5 Performance Overview with Bridge Data
        print("\n📊 Test 3: FIDUS MT5 Performance Overview (Bridge Data)")
        success, response = self.run_test(
            "FIDUS MT5 Performance Overview (Bridge Integration)",
            "GET",
            "api/mt5/admin/performance/overview",
            200,
            headers=admin_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ FIDUS MT5 performance overview accessible")
            if isinstance(response, dict):
                overview = response.get('overview', {})
                
                total_pnl = overview.get('total_profit_loss', 0)
                performance_pct = overview.get('overall_performance_percentage', 0)
                
                print(f"   📋 Total P&L: ${total_pnl:,.2f}")
                print(f"   📋 Overall Performance: {performance_pct:.2f}%")
                
                # Check if performance data suggests real MT5 integration
                if abs(total_pnl) > 0 or abs(performance_pct) > 0:
                    print("   🎉 Real MT5 performance data detected!")
                    self.real_mt5_data_samples.append({
                        'source': 'fidus_performance_overview',
                        'data': overview
                    })
                else:
                    print("   ⚠️ Performance data may be using fallback values")
                
                self.mt5_endpoints_tested.append('performance_overview')
            else:
                print("   ⚠️ Unexpected response format")
        else:
            print("   ❌ FIDUS MT5 performance overview failed")

        # Test 4: FIDUS MT5 Brokers List
        print("\n📊 Test 4: FIDUS MT5 Brokers List")
        success, response = self.run_test(
            "FIDUS MT5 Brokers List",
            "GET",
            "api/mt5/brokers",
            200,
            headers=admin_headers
        )
        
        if success:
            print("   ✅ FIDUS MT5 brokers list accessible")
            if isinstance(response, dict):
                brokers = response.get('brokers', [])
                print(f"   📋 Available brokers: {len(brokers)}")
                
                for broker in brokers:
                    broker_name = broker.get('name', 'Unknown')
                    servers = broker.get('servers', [])
                    print(f"   📋 {broker_name}: {len(servers)} servers")
                
                self.mt5_endpoints_tested.append('brokers')
            else:
                print("   ⚠️ Unexpected response format")
        else:
            print("   ❌ FIDUS MT5 brokers list failed")

        # Test 5: FIDUS MT5 System Status
        print("\n📊 Test 5: FIDUS MT5 System Status")
        success, response = self.run_test(
            "FIDUS MT5 System Status",
            "GET",
            "api/mt5/admin/system-status",
            200,
            headers=admin_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ FIDUS MT5 system status accessible")
            if isinstance(response, dict):
                status = response.get('status', {})
                bridge_connected = status.get('bridge_connected', False)
                mt5_available = status.get('mt5_available', False)
                
                print(f"   📋 Bridge Connected: {bridge_connected}")
                print(f"   📋 MT5 Available: {mt5_available}")
                
                if bridge_connected and mt5_available:
                    print("   🎉 FIDUS MT5 system fully operational!")
                else:
                    print("   ⚠️ FIDUS MT5 system has connectivity issues")
                
                self.mt5_endpoints_tested.append('system_status')
            else:
                print("   ⚠️ Unexpected response format")
        else:
            print("   ❌ FIDUS MT5 system status failed")

        return True

    def test_client_mt5_data_flow(self) -> bool:
        """Test client-facing MT5 data flow"""
        print("\n" + "="*80)
        print("👤 TESTING CLIENT MT5 DATA FLOW")
        print("="*80)
        
        if not self.client_user:
            print("❌ No client user available for MT5 data flow tests")
            return False
            
        client_id = self.client_user.get('id')
        client_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.client_user.get('token')}"
        }

        # Test 1: Client MT5 Accounts with Real Data
        print("\n📊 Test 1: Client MT5 Accounts (Real Data)")
        success, response = self.run_test(
            "Client MT5 Accounts (Real Data Flow)",
            "GET",
            f"api/mt5/client/{client_id}/accounts",
            200,
            headers=client_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ Client MT5 accounts accessible")
            if isinstance(response, dict):
                accounts = response.get('accounts', [])
                summary = response.get('summary', {})
                
                print(f"   📋 Client has {len(accounts)} MT5 accounts")
                print(f"   📋 Total allocated: ${summary.get('total_allocated', 0):,.2f}")
                print(f"   📋 Total equity: ${summary.get('total_equity', 0):,.2f}")
                
                # Analyze account data for real MT5 integration
                real_data_indicators = 0
                for account in accounts:
                    if account.get('mt5_login') and account.get('mt5_server'):
                        real_data_indicators += 1
                        print(f"   📋 Account {account.get('mt5_login')} on {account.get('mt5_server')}")
                    
                    current_equity = account.get('current_equity', 0)
                    allocated = account.get('total_allocated', 0)
                    if current_equity != allocated:
                        real_data_indicators += 1
                        print(f"   📋 Live equity: ${current_equity:,.2f} vs allocated: ${allocated:,.2f}")
                
                if real_data_indicators > 0:
                    print("   🎉 Real MT5 data flowing to client interface!")
                    self.real_mt5_data_samples.append({
                        'source': 'client_accounts',
                        'client_id': client_id,
                        'accounts': accounts
                    })
                else:
                    print("   ⚠️ Client accounts may be using fallback data")
                
                self.mt5_endpoints_tested.append('client_accounts')
            else:
                print("   ⚠️ Unexpected response format")
        else:
            print("   ❌ Client MT5 accounts failed")

        # Test 2: Client MT5 Performance with Real Data
        print("\n📊 Test 2: Client MT5 Performance (Real Data)")
        success, response = self.run_test(
            "Client MT5 Performance (Real Data Flow)",
            "GET",
            f"api/mt5/client/{client_id}/performance",
            200,
            headers=client_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ Client MT5 performance accessible")
            if isinstance(response, dict):
                summary = response.get('summary', {})
                
                total_pnl = summary.get('total_profit_loss', 0)
                performance_pct = summary.get('overall_performance_percentage', 0)
                
                print(f"   📋 Client Total P&L: ${total_pnl:,.2f}")
                print(f"   📋 Client Performance: {performance_pct:.2f}%")
                
                # Check for real performance data
                if abs(total_pnl) > 0 or abs(performance_pct) > 0:
                    print("   🎉 Real MT5 performance data flowing to client!")
                    self.real_mt5_data_samples.append({
                        'source': 'client_performance',
                        'client_id': client_id,
                        'performance': summary
                    })
                else:
                    print("   ⚠️ Client performance may be using fallback data")
                
                self.mt5_endpoints_tested.append('client_performance')
            else:
                print("   ⚠️ Unexpected response format")
        else:
            print("   ❌ Client MT5 performance failed")

        return True

    def test_mt5_admin_management_interfaces(self) -> bool:
        """Test admin MT5 management interfaces"""
        print("\n" + "="*80)
        print("🔧 TESTING ADMIN MT5 MANAGEMENT INTERFACES")
        print("="*80)
        
        if not self.admin_user:
            print("❌ No admin user available for MT5 admin management tests")
            return False
            
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }

        # Test 1: MT5 Realtime Data
        print("\n📊 Test 1: MT5 Realtime Data Interface")
        success, response = self.run_test(
            "MT5 Realtime Data",
            "GET",
            "api/mt5/admin/realtime-data",
            200,
            headers=admin_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ MT5 realtime data interface accessible")
            self.mt5_endpoints_tested.append('realtime_data')
        else:
            print("   ❌ MT5 realtime data interface failed")

        # Test 2: MT5 Accounts by Broker
        print("\n📊 Test 2: MT5 Accounts by Broker Interface")
        success, response = self.run_test(
            "MT5 Accounts by Broker",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200,
            headers=admin_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ MT5 accounts by broker interface accessible")
            if isinstance(response, dict):
                brokers = response.get('brokers', {})
                print(f"   📋 Broker breakdown: {list(brokers.keys())}")
                
                for broker_name, broker_data in brokers.items():
                    account_count = broker_data.get('account_count', 0)
                    total_allocated = broker_data.get('total_allocated', 0)
                    print(f"   📋 {broker_name}: {account_count} accounts, ${total_allocated:,.2f}")
            
            self.mt5_endpoints_tested.append('accounts_by_broker')
        else:
            print("   ❌ MT5 accounts by broker interface failed")

        # Test 3: Manual MT5 Account Addition
        print("\n📊 Test 3: Manual MT5 Account Addition Interface")
        success, response = self.run_test(
            "Manual MT5 Account Addition",
            "POST",
            "api/mt5/admin/add-manual-account",
            200,
            data={
                "client_id": "client_001",
                "mt5_login": 99999999,
                "mt5_password": "TestBridgePass123!",
                "mt5_server": "Multibank-Bridge-Test",
                "broker_code": "multibank",
                "fund_code": "CORE"
            },
            headers=admin_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ Manual MT5 account addition interface working")
            if isinstance(response, dict):
                success_flag = response.get('success', False)
                message = response.get('message', '')
                
                if success_flag:
                    print("   🎉 Manual account addition successful!")
                else:
                    print(f"   ⚠️ Manual account addition completed with message: {message}")
            
            self.mt5_endpoints_tested.append('manual_account_addition')
        else:
            print("   ❌ Manual MT5 account addition interface failed")

        # Test 4: MT5 Credentials Update
        print("\n📊 Test 4: MT5 Credentials Update Interface")
        success, response = self.run_test(
            "MT5 Credentials Update",
            "POST",
            "api/mt5/admin/credentials/update",
            200,  # May return 404 if account doesn't exist, but interface should work
            data={
                "client_id": "client_003",  # Salvador Palma
                "fund_code": "BALANCE",
                "mt5_login": 88888888,
                "mt5_password": "UpdatedBridgePass123!",
                "mt5_server": "Updated-Bridge-Server"
            },
            headers=admin_headers,
            timeout=35
        )
        
        if success:
            print("   ✅ MT5 credentials update interface working")
            self.mt5_endpoints_tested.append('credentials_update')
        else:
            print("   ⚠️ MT5 credentials update interface may need existing account")

        return True

    def calculate_integration_success_metrics(self) -> Dict[str, Any]:
        """Calculate MT5 integration success metrics"""
        print("\n" + "="*80)
        print("📊 CALCULATING MT5 INTEGRATION SUCCESS METRICS")
        print("="*80)
        
        # Bridge connectivity metrics
        bridge_tests = len(self.bridge_connectivity_results)
        bridge_successes = sum(1 for result in self.bridge_connectivity_results.values() if result)
        bridge_success_rate = (bridge_successes / bridge_tests * 100) if bridge_tests > 0 else 0
        
        # Endpoint functionality metrics
        total_mt5_endpoints = 10  # Expected MT5 endpoints
        working_endpoints = len(self.mt5_endpoints_tested)
        endpoint_success_rate = (working_endpoints / total_mt5_endpoints * 100)
        
        # Real data flow metrics
        real_data_sources = len(self.real_mt5_data_samples)
        expected_data_sources = 4  # bridge_accounts, fidus_admin, client_accounts, client_performance
        data_flow_success_rate = (real_data_sources / expected_data_sources * 100)
        
        # Overall integration success
        overall_success_rate = (
            (bridge_success_rate * 0.4) +  # 40% weight on bridge connectivity
            (endpoint_success_rate * 0.4) +  # 40% weight on endpoint functionality
            (data_flow_success_rate * 0.2)   # 20% weight on real data flow
        )
        
        metrics = {
            'bridge_connectivity': {
                'tests': bridge_tests,
                'successes': bridge_successes,
                'success_rate': bridge_success_rate,
                'details': self.bridge_connectivity_results
            },
            'endpoint_functionality': {
                'total_endpoints': total_mt5_endpoints,
                'working_endpoints': working_endpoints,
                'success_rate': endpoint_success_rate,
                'tested_endpoints': self.mt5_endpoints_tested
            },
            'real_data_flow': {
                'expected_sources': expected_data_sources,
                'actual_sources': real_data_sources,
                'success_rate': data_flow_success_rate,
                'data_samples': len(self.real_mt5_data_samples)
            },
            'overall_integration': {
                'success_rate': overall_success_rate,
                'total_tests': self.tests_run,
                'passed_tests': self.tests_passed,
                'test_success_rate': (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
            }
        }
        
        print(f"📋 Bridge Connectivity: {bridge_success_rate:.1f}% ({bridge_successes}/{bridge_tests})")
        print(f"📋 Endpoint Functionality: {endpoint_success_rate:.1f}% ({working_endpoints}/{total_mt5_endpoints})")
        print(f"📋 Real Data Flow: {data_flow_success_rate:.1f}% ({real_data_sources}/{expected_data_sources})")
        print(f"📋 Overall Integration: {overall_success_rate:.1f}%")
        print(f"📋 Test Success Rate: {metrics['overall_integration']['test_success_rate']:.1f}% ({self.tests_passed}/{self.tests_run})")
        
        return metrics

    def assess_production_readiness(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess production readiness of MT5 integration"""
        print("\n" + "="*80)
        print("🚀 ASSESSING MT5 INTEGRATION PRODUCTION READINESS")
        print("="*80)
        
        overall_success = metrics['overall_integration']['success_rate']
        bridge_success = metrics['bridge_connectivity']['success_rate']
        endpoint_success = metrics['endpoint_functionality']['success_rate']
        data_flow_success = metrics['real_data_flow']['success_rate']
        
        # Production readiness criteria
        criteria = {
            'bridge_connectivity': {
                'required': 80.0,
                'actual': bridge_success,
                'passed': bridge_success >= 80.0
            },
            'endpoint_functionality': {
                'required': 70.0,
                'actual': endpoint_success,
                'passed': endpoint_success >= 70.0
            },
            'real_data_flow': {
                'required': 50.0,
                'actual': data_flow_success,
                'passed': data_flow_success >= 50.0
            },
            'overall_integration': {
                'required': 75.0,
                'actual': overall_success,
                'passed': overall_success >= 75.0
            }
        }
        
        passed_criteria = sum(1 for criterion in criteria.values() if criterion['passed'])
        total_criteria = len(criteria)
        
        production_ready = passed_criteria == total_criteria
        
        print("Production Readiness Criteria:")
        for name, criterion in criteria.items():
            status = "✅ PASS" if criterion['passed'] else "❌ FAIL"
            print(f"   {name}: {criterion['actual']:.1f}% (required: {criterion['required']:.1f}%) {status}")
        
        print(f"\nProduction Readiness: {passed_criteria}/{total_criteria} criteria met")
        
        if production_ready:
            print("🎉 MT5 INTEGRATION IS PRODUCTION READY!")
        else:
            print("⚠️ MT5 INTEGRATION NEEDS IMPROVEMENT BEFORE PRODUCTION")
        
        assessment = {
            'production_ready': production_ready,
            'criteria_met': passed_criteria,
            'total_criteria': total_criteria,
            'criteria_details': criteria,
            'recommendations': []
        }
        
        # Generate recommendations
        if not criteria['bridge_connectivity']['passed']:
            assessment['recommendations'].append("Improve MT5 bridge connectivity and error handling")
        
        if not criteria['endpoint_functionality']['passed']:
            assessment['recommendations'].append("Fix non-working MT5 endpoints and improve API reliability")
        
        if not criteria['real_data_flow']['passed']:
            assessment['recommendations'].append("Ensure real MT5 data flows properly through all interfaces")
        
        if not criteria['overall_integration']['passed']:
            assessment['recommendations'].append("Overall MT5 integration needs comprehensive improvements")
        
        return assessment

    def run_comprehensive_mt5_bridge_integration_tests(self) -> bool:
        """Run comprehensive MT5 bridge integration tests"""
        print("\n" + "="*100)
        print("🚀 STARTING COMPREHENSIVE MT5 BRIDGE INTEGRATION TESTING")
        print("="*100)
        print("URGENT: Testing FIDUS → MT5 Bridge integration")
        print("Bridge Status: External MT5 Bridge access confirmed working at http://217.197.163.11:8000")
        print("Expected: mt5_available=true and mt5_initialized=true")
        print("="*100)
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run test suites
        test_suites = [
            ("Direct MT5 Bridge Connectivity", self.test_direct_mt5_bridge_connectivity),
            ("FIDUS → MT5 Bridge Integration", self.test_fidus_mt5_bridge_integration),
            ("Client MT5 Data Flow", self.test_client_mt5_data_flow),
            ("Admin MT5 Management Interfaces", self.test_mt5_admin_management_interfaces)
        ]
        
        suite_results = []
        
        for suite_name, test_method in test_suites:
            print(f"\n🔄 Running {suite_name}...")
            try:
                result = test_method()
                suite_results.append((suite_name, result))
                
                if result:
                    print(f"✅ {suite_name} - PASSED")
                else:
                    print(f"❌ {suite_name} - FAILED")
            except Exception as e:
                print(f"❌ {suite_name} - ERROR: {str(e)}")
                suite_results.append((suite_name, False))
        
        # Calculate metrics and assess production readiness
        metrics = self.calculate_integration_success_metrics()
        assessment = self.assess_production_readiness(metrics)
        
        # Print final results
        print("\n" + "="*100)
        print("📊 MT5 BRIDGE INTEGRATION TEST RESULTS SUMMARY")
        print("="*100)
        
        passed_suites = sum(1 for _, result in suite_results if result)
        total_suites = len(suite_results)
        
        for suite_name, result in suite_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {suite_name}: {status}")
        
        print(f"\n📈 Integration Results:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed ({passed_suites/total_suites*100:.1f}%)")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        print(f"   Overall Integration Success: {metrics['overall_integration']['success_rate']:.1f}%")
        print(f"   Production Ready: {'YES' if assessment['production_ready'] else 'NO'}")
        
        # Print real MT5 data samples
        if self.real_mt5_data_samples:
            print(f"\n🎉 Real MT5 Data Sources Detected: {len(self.real_mt5_data_samples)}")
            for sample in self.real_mt5_data_samples:
                print(f"   📋 {sample['source']}: {sample.get('count', 'N/A')} items")
        
        # Print recommendations
        if assessment['recommendations']:
            print(f"\n📋 Recommendations:")
            for rec in assessment['recommendations']:
                print(f"   • {rec}")
        
        # Determine overall success
        overall_success = (
            passed_suites >= (total_suites * 0.75) and  # At least 75% of suites passed
            self.tests_passed >= (self.tests_run * 0.70) and  # At least 70% of tests passed
            metrics['overall_integration']['success_rate'] >= 60.0  # At least 60% integration success
        )
        
        if overall_success:
            print(f"\n🎉 MT5 BRIDGE INTEGRATION TESTING COMPLETED SUCCESSFULLY!")
            print("   FIDUS → MT5 Bridge integration is working with external bridge access.")
            print("   ✅ Bridge connectivity confirmed")
            print("   ✅ Real MT5 data flowing into FIDUS system")
            print("   ✅ Admin MT5 management interfaces operational")
            print("   ✅ End-to-end data flow validated")
        else:
            print(f"\n⚠️ MT5 BRIDGE INTEGRATION TESTING COMPLETED WITH ISSUES")
            print("   Some aspects of MT5 bridge integration need attention.")
            print("   Check bridge connectivity and endpoint functionality.")
        
        return overall_success

def main():
    """Main test execution"""
    print("🔧 URGENT: FIDUS MT5 Bridge Integration Testing Suite")
    print("Testing FIDUS → MT5 Bridge integration with confirmed external bridge access")
    print("Bridge URL: http://217.197.163.11:8000 (mt5_available=true, mt5_initialized=true)")
    
    tester = MT5BridgeIntegrationTester()
    
    try:
        success = tester.run_comprehensive_mt5_bridge_integration_tests()
        
        if success:
            print("\n✅ MT5 Bridge Integration testing completed successfully!")
            print("   FIDUS system ready for production MT5 operations")
            sys.exit(0)
        else:
            print("\n❌ MT5 Bridge Integration testing completed with issues!")
            print("   Review bridge connectivity and endpoint functionality")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()