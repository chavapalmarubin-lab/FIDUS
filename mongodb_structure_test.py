#!/usr/bin/env python3
"""
MONGODB STRUCTURE VERIFICATION TEST
December 19, 2025

Verifies the MongoDB structure for SSOT architecture:
1. mt5_accounts has all 15 accounts
2. money_managers has NO assigned_accounts field (SSOT compliance)
3. Data consistency verification
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://lucrum-api-debug.preview.emergentagent.com"
TIMEOUT = 30

class MongoDBStructureTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.results = []
        
    def log_result(self, test_name: str, success: bool, details: str, response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status} {test_name}: {details}")
        if response_time > 0:
            print(f"   Response time: {response_time * 1000:.2f}ms")
    
    def test_mongodb_structure(self):
        """Test MongoDB structure via SSOT health endpoint"""
        print("\n🔍 Testing MongoDB Structure...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v2/health/ssot")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                validation = data.get('validation', {})
                
                # Test 1: mt5_accounts has all 15 accounts
                total_accounts = validation.get('total_accounts', 0)
                if total_accounts == 15:
                    self.log_result("MongoDB - mt5_accounts Count", True, 
                                  f"mt5_accounts collection has 15 accounts ✓", response_time)
                else:
                    self.log_result("MongoDB - mt5_accounts Count", False, 
                                  f"Expected 15 accounts in mt5_accounts, got {total_accounts}", response_time)
                
                # Test 2: money_managers has NO assigned_accounts field (SSOT compliance)
                ssot_violation = validation.get('ssot_violation', {})
                violated = ssot_violation.get('violated', True)
                managers_with_accounts = ssot_violation.get('managers_with_account_lists', 0)
                
                if not violated and managers_with_accounts == 0:
                    self.log_result("MongoDB - SSOT Compliance", True, 
                                  "money_managers collection has NO assigned_accounts field ✓", response_time)
                else:
                    self.log_result("MongoDB - SSOT Compliance", False, 
                                  f"SSOT violation: {managers_with_accounts} managers have assigned_accounts field", response_time)
                
                # Test 3: Data completeness
                completeness = validation.get('data_completeness', {})
                platforms = completeness.get('platforms', [])
                brokers = completeness.get('brokers', [])
                funds = completeness.get('fund_types', [])
                managers = completeness.get('managers', [])
                
                # Check expected data
                expected_platforms = ['MT4', 'MT5']
                expected_brokers = ['MEXAtlantic', 'LUCRUM Capital']
                expected_funds = ['CORE', 'BALANCE', 'SEPARATION']
                
                platforms_ok = all(p in platforms for p in expected_platforms)
                brokers_ok = all(b in brokers for b in expected_brokers)
                funds_ok = all(f in funds for f in expected_funds)
                
                if platforms_ok and brokers_ok and funds_ok:
                    self.log_result("MongoDB - Data Completeness", True, 
                                  f"All expected data present: {len(platforms)} platforms, {len(brokers)} brokers, {len(funds)} funds, {len(managers)} managers ✓", response_time)
                else:
                    missing = []
                    if not platforms_ok: missing.append("platforms")
                    if not brokers_ok: missing.append("brokers") 
                    if not funds_ok: missing.append("funds")
                    
                    self.log_result("MongoDB - Data Completeness", False, 
                                  f"Missing expected data in: {missing}", response_time)
                
                return True
                
            else:
                self.log_result("MongoDB Structure", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("MongoDB Structure", False, f"Exception: {str(e)}")
            return False
    
    def test_data_consistency(self):
        """Test data consistency across derived endpoints"""
        print("\n🔍 Testing Data Consistency...")
        
        try:
            # Get data from all endpoints
            endpoints = {
                'accounts': '/api/v2/accounts/all',
                'fund_portfolio': '/api/v2/derived/fund-portfolio', 
                'money_managers': '/api/v2/derived/money-managers',
                'cash_flow': '/api/v2/derived/cash-flow',
                'trading_analytics': '/api/v2/derived/trading-analytics'
            }
            
            endpoint_data = {}
            
            for name, endpoint in endpoints.items():
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    endpoint_data[name] = response.json()
                    self.log_result(f"Data Consistency - {name.title()} Fetch", True, 
                                  f"Successfully fetched {name} data ✓", response_time)
                else:
                    self.log_result(f"Data Consistency - {name.title()} Fetch", False, 
                                  f"Failed to fetch {name}: HTTP {response.status_code}", response_time)
                    return False
            
            # Verify consistency
            accounts_data = endpoint_data.get('accounts', {})
            fund_data = endpoint_data.get('fund_portfolio', {})
            managers_data = endpoint_data.get('money_managers', {})
            cash_flow_data = endpoint_data.get('cash_flow', {})
            analytics_data = endpoint_data.get('trading_analytics', {})
            
            # Test 1: Total account counts should match
            accounts_total = accounts_data.get('summary', {}).get('total_accounts', 0)
            fund_total = fund_data.get('summary', {}).get('total_accounts', 0)
            cash_flow_total = cash_flow_data.get('summary', {}).get('total_accounts', 0)
            analytics_total = analytics_data.get('analytics', {}).get('overview', {}).get('total_accounts', 0)
            
            if accounts_total == fund_total == analytics_total:
                self.log_result("Data Consistency - Account Counts", True, 
                              f"Account counts consistent: {accounts_total} across endpoints ✓")
            else:
                self.log_result("Data Consistency - Account Counts", False, 
                              f"Account counts inconsistent: accounts={accounts_total}, funds={fund_total}, analytics={analytics_total}")
            
            # Test 2: Active account counts should match
            accounts_active = accounts_data.get('summary', {}).get('active_accounts', 0)
            cash_flow_active = cash_flow_data.get('summary', {}).get('total_accounts', 0)  # cash flow only shows active
            
            if accounts_active == cash_flow_active:
                self.log_result("Data Consistency - Active Accounts", True, 
                              f"Active account counts consistent: {accounts_active} ✓")
            else:
                self.log_result("Data Consistency - Active Accounts", False, 
                              f"Active account counts inconsistent: accounts={accounts_active}, cash_flow={cash_flow_active}")
            
            # Test 3: Manager counts should be consistent
            managers_count = managers_data.get('summary', {}).get('total_managers', 0)
            analytics_managers = len(analytics_data.get('analytics', {}).get('by_manager', {}))
            
            if managers_count == analytics_managers:
                self.log_result("Data Consistency - Manager Counts", True, 
                              f"Manager counts consistent: {managers_count} ✓")
            else:
                self.log_result("Data Consistency - Manager Counts", False, 
                              f"Manager counts inconsistent: managers={managers_count}, analytics={analytics_managers}")
            
            # Test 4: Fund counts should be consistent
            fund_count = fund_data.get('summary', {}).get('fund_count', 0)
            analytics_funds = len(analytics_data.get('analytics', {}).get('by_fund', {}))
            
            if fund_count == analytics_funds:
                self.log_result("Data Consistency - Fund Counts", True, 
                              f"Fund counts consistent: {fund_count} ✓")
            else:
                self.log_result("Data Consistency - Fund Counts", False, 
                              f"Fund counts inconsistent: funds={fund_count}, analytics={analytics_funds}")
            
            return True
            
        except Exception as e:
            self.log_result("Data Consistency", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all MongoDB structure tests"""
        print("🚀 MONGODB STRUCTURE VERIFICATION")
        print("=" * 50)
        print(f"Base URL: {self.base_url}")
        print(f"Start time: {datetime.now().isoformat()}")
        print("=" * 50)
        
        # Run tests
        self.test_mongodb_structure()
        self.test_data_consistency()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("📊 MONGODB STRUCTURE TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"End time: {datetime.now().isoformat()}")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.results:
            if result['success']:
                print(f"  • {result['test']}: {result['details']}")
        
        print("=" * 50)


if __name__ == "__main__":
    tester = MongoDBStructureTest()
    tester.run_all_tests()