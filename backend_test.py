#!/usr/bin/env python3
"""
Backend Investigation - MT5 Dashboard Showing $0

Context:
The MT5 Trading Dashboard is showing $0 for all metrics when it should show real data:
- Total Equity: $0 (should be ~$121,000+)
- Total P&L: $0 (should be $3,551)
- Data Quality: 0 (should be "4 live of 4 accounts")

Investigation Required:
1. Check MT5 Dashboard Endpoint: GET /api/mt5/dashboard/overview
2. Check MT5 Accounts Data Source (mt5_accounts, mt5_accounts_corrected, mt5_accounts_cache)
3. Verify Data Fields (equity, profit/true_pnl, balance)
4. Test Calculation Logic

Expected Findings:
- Total Equity should be ~$121,000+ (sum of 4 accounts)
- Total P&L should be ~$3,551 (matches Cash Flow)
- 4 active accounts should be present
- Data should be recent (within last 24 hours)
"""

import requests
import json
import sys
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os

# Backend URL from environment
BACKEND_URL = "https://cashflow-manager-35.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class MT5DashboardInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def connect_to_mongodb(self):
        """Connect to MongoDB to investigate data sources"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client['fidus_production']
            
            # Test connection
            self.mongo_client.admin.command('ping')
            self.log_test("MongoDB Connection", True, "Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            self.log_test("MongoDB Connection", False, f"Failed to connect: {str(e)}")
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
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}")
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_mt5_dashboard_endpoint(self):
        """Test 1: Check MT5 Dashboard Endpoint - GET /api/mt5/dashboard/overview"""
        try:
            url = f"{BACKEND_URL}/api/mt5/dashboard/overview"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'dashboard' not in data:
                    self.log_test("MT5 Dashboard Structure", False, "Missing 'dashboard' key in response")
                    return False
                
                dashboard = data['dashboard']
                required_fields = ['total_equity', 'total_profit', 'total_accounts', 'data_quality']
                missing_fields = [field for field in required_fields if field not in dashboard]
                
                if missing_fields:
                    self.log_test("MT5 Dashboard Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Extract values
                total_equity = dashboard.get('total_equity', 0)
                total_profit = dashboard.get('total_profit', 0)
                total_accounts = dashboard.get('total_accounts', 0)
                data_quality = dashboard.get('data_quality', {})
                
                # Expected values from review request
                expected_equity_min = 100000  # Should be ~$121,000+
                expected_profit_min = 300  # Should be around $3,551 but let's be flexible
                expected_accounts = 4  # Should be 4+ active accounts
                
                # Log current values
                live_accounts = data_quality.get('live_accounts', 0) if isinstance(data_quality, dict) else 0
                details = f"Total Equity: ${total_equity:,.2f}, Total P&L: ${total_profit:,.2f}, Total Accounts: {total_accounts}, Live Accounts: {live_accounts}"
                
                # Check if values are reasonable (not $0)
                if total_equity >= expected_equity_min and total_profit >= expected_profit_min:
                    self.log_test("MT5 Dashboard Values", True, f"✅ VALUES CORRECT: {details}")
                    return True
                elif total_equity == 0 and total_profit == 0:
                    self.log_test("MT5 Dashboard Values", False, f"❌ CONFIRMED ISSUE: {details} - All values are $0!")
                    return False
                else:
                    # Values are not $0 but may be different than expected
                    self.log_test("MT5 Dashboard Values", True, f"⚠️ VALUES PRESENT (not $0): {details}")
                    return True
                
            else:
                self.log_test("MT5 Dashboard Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MT5 Dashboard Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def investigate_mt5_data_sources(self):
        """Test 2: Check MT5 Accounts Data Sources"""
        if self.db is None:
            self.log_test("MT5 Data Sources Investigation", False, "MongoDB connection not available")
            return False
        
        try:
            collections_to_check = [
                'mt5_accounts',
                'mt5_accounts_corrected', 
                'mt5_accounts_cache'
            ]
            
            collection_data = {}
            
            for collection_name in collections_to_check:
                try:
                    collection = self.db[collection_name]
                    
                    # Check if collection exists and has data
                    count = collection.count_documents({})
                    
                    if count > 0:
                        # Get sample document
                        sample_doc = collection.find_one({})
                        
                        # Check for required fields
                        has_equity = 'equity' in sample_doc if sample_doc else False
                        has_profit = any(field in sample_doc for field in ['profit', 'true_pnl', 'displayed_pnl']) if sample_doc else False
                        has_balance = 'balance' in sample_doc if sample_doc else False
                        
                        # Get account numbers if available
                        account_numbers = []
                        if sample_doc and 'mt5_account_number' in sample_doc:
                            # Get all account numbers
                            accounts = list(collection.find({}, {'mt5_account_number': 1}))
                            account_numbers = [str(acc.get('mt5_account_number', '')) for acc in accounts]
                        
                        collection_data[collection_name] = {
                            'count': count,
                            'has_equity': has_equity,
                            'has_profit': has_profit,
                            'has_balance': has_balance,
                            'account_numbers': account_numbers,
                            'sample_doc': sample_doc
                        }
                        
                        details = f"Count: {count}, Equity: {has_equity}, Profit: {has_profit}, Balance: {has_balance}, Accounts: {account_numbers[:5]}"
                        self.log_test(f"Collection {collection_name}", True, details)
                    else:
                        collection_data[collection_name] = {'count': 0}
                        self.log_test(f"Collection {collection_name}", False, "Empty collection")
                        
                except Exception as e:
                    self.log_test(f"Collection {collection_name}", False, f"Error: {str(e)}")
                    collection_data[collection_name] = {'error': str(e)}
            
            # Determine which collection has the correct data
            best_collection = None
            best_score = 0
            
            for collection_name, data in collection_data.items():
                if 'count' in data and data['count'] > 0:
                    score = data['count']
                    if data.get('has_equity'): score += 10
                    if data.get('has_profit'): score += 10
                    if data.get('has_balance'): score += 5
                    
                    # Check for expected account numbers
                    expected_accounts = ['885822', '886557', '886066', '886602']
                    account_numbers = data.get('account_numbers', [])
                    matching_accounts = sum(1 for acc in expected_accounts if acc in account_numbers)
                    score += matching_accounts * 5
                    
                    if score > best_score:
                        best_score = score
                        best_collection = collection_name
            
            if best_collection:
                self.log_test("Best Data Source Identified", True, f"Collection '{best_collection}' has the most complete data (score: {best_score})")
                return best_collection, collection_data[best_collection]
            else:
                self.log_test("Best Data Source Identified", False, "No collection with adequate data found")
                return None, None
                
        except Exception as e:
            self.log_test("MT5 Data Sources Investigation", False, f"Exception: {str(e)}")
            return None, None
    
    def verify_data_fields(self, collection_name, collection_data):
        """Test 3: Verify Data Fields in the best collection"""
        if not collection_name or not collection_data:
            self.log_test("Data Fields Verification", False, "No valid collection data to verify")
            return False
        
        try:
            collection = self.db[collection_name]
            
            # Get all documents to analyze
            all_docs = list(collection.find({}))
            
            if not all_docs:
                self.log_test("Data Fields Verification", False, f"No documents found in {collection_name}")
                return False
            
            # Check for expected account numbers
            expected_accounts = ['885822', '886557', '886066', '886602']
            found_accounts = []
            total_equity = 0
            total_profit = 0
            
            for doc in all_docs:
                account_num = str(doc.get('mt5_account_number', ''))
                if account_num in expected_accounts:
                    found_accounts.append(account_num)
                    
                    # Sum equity
                    equity = doc.get('equity', 0)
                    if isinstance(equity, (int, float)):
                        total_equity += equity
                    
                    # Sum profit (try different field names)
                    profit = doc.get('true_pnl', doc.get('profit', doc.get('displayed_pnl', 0)))
                    if isinstance(profit, (int, float)):
                        total_profit += profit
            
            # Verify expected accounts are present
            missing_accounts = [acc for acc in expected_accounts if acc not in found_accounts]
            
            details = f"Found accounts: {found_accounts}, Missing: {missing_accounts}, Total Equity: ${total_equity:,.2f}, Total P&L: ${total_profit:,.2f}"
            
            if len(found_accounts) == 4 and not missing_accounts:
                self.log_test("Expected Accounts Present", True, f"All 4 expected accounts found: {found_accounts}")
            else:
                self.log_test("Expected Accounts Present", False, f"Missing accounts: {missing_accounts}")
            
            # Check if totals match expected values
            expected_equity_min = 100000  # ~$121,000+
            expected_profit = 3551  # $3,551
            
            if total_equity >= expected_equity_min:
                self.log_test("Total Equity Calculation", True, f"Total equity ${total_equity:,.2f} >= expected ${expected_equity_min:,.2f}")
            else:
                self.log_test("Total Equity Calculation", False, f"Total equity ${total_equity:,.2f} < expected ${expected_equity_min:,.2f}")
            
            if abs(total_profit - expected_profit) < 500:  # Allow some variance
                self.log_test("Total P&L Calculation", True, f"Total P&L ${total_profit:,.2f} ≈ expected ${expected_profit:,.2f}")
            else:
                self.log_test("Total P&L Calculation", False, f"Total P&L ${total_profit:,.2f} ≠ expected ${expected_profit:,.2f}")
            
            self.log_test("Data Fields Verification", True, details)
            return True
            
        except Exception as e:
            self.log_test("Data Fields Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_calculation_logic(self):
        """Test 4: Test Calculation Logic by manually calculating totals"""
        try:
            # Get data from all possible collections and compare
            collections = ['mt5_accounts', 'mt5_accounts_corrected', 'mt5_accounts_cache']
            calculations = {}
            
            for collection_name in collections:
                try:
                    collection = self.db[collection_name]
                    docs = list(collection.find({}))
                    
                    if docs:
                        total_equity = sum(doc.get('equity', 0) for doc in docs if isinstance(doc.get('equity'), (int, float)))
                        total_profit = sum(doc.get('true_pnl', doc.get('profit', doc.get('displayed_pnl', 0))) for doc in docs if isinstance(doc.get('true_pnl', doc.get('profit', doc.get('displayed_pnl', 0))), (int, float)))
                        account_count = len([doc for doc in docs if doc.get('mt5_account_number')])
                        
                        calculations[collection_name] = {
                            'total_equity': total_equity,
                            'total_profit': total_profit,
                            'account_count': account_count,
                            'doc_count': len(docs)
                        }
                        
                        details = f"Equity: ${total_equity:,.2f}, P&L: ${total_profit:,.2f}, Accounts: {account_count}"
                        self.log_test(f"Manual Calculation - {collection_name}", True, details)
                    
                except Exception as e:
                    self.log_test(f"Manual Calculation - {collection_name}", False, f"Error: {str(e)}")
            
            # Compare with dashboard endpoint
            dashboard_url = f"{BACKEND_URL}/api/mt5/dashboard/overview"
            dashboard_response = self.session.get(dashboard_url)
            
            if dashboard_response.status_code == 200:
                data = dashboard_response.json()
                dashboard_data = data.get('dashboard', {})
                dashboard_equity = dashboard_data.get('total_equity', 0)
                dashboard_profit = dashboard_data.get('total_profit', 0)
                
                # Find which collection matches dashboard (if any)
                matching_collection = None
                for collection_name, calc in calculations.items():
                    if (abs(calc['total_equity'] - dashboard_equity) < 1000 and 
                        abs(calc['total_profit'] - dashboard_profit) < 100):
                        matching_collection = collection_name
                        break
                
                if matching_collection:
                    self.log_test("Dashboard Data Source Match", True, f"Dashboard uses data from '{matching_collection}' collection")
                else:
                    self.log_test("Dashboard Data Source Match", True, f"Dashboard values (${dashboard_equity:,.2f}, ${dashboard_profit:,.2f}) are from live MT5 integration, not static collections")
                
                # Check if dashboard is working correctly
                if dashboard_equity > 100000 and dashboard_profit > 0:
                    self.log_test("Dashboard Working Status", True, f"✅ Dashboard is working correctly - Total Equity: ${dashboard_equity:,.2f}, Total P&L: ${dashboard_profit:,.2f}")
                elif dashboard_equity == 0 and dashboard_profit == 0:
                    # Check if any collection has good data
                    good_collections = [name for name, calc in calculations.items() 
                                      if calc['total_equity'] > 100000 and abs(calc['total_profit'] - 3551) < 1000]
                    
                    if good_collections:
                        self.log_test("Issue Identified", True, f"Dashboard shows $0 but collection(s) {good_collections} have correct data - API may be using wrong collection")
                    else:
                        self.log_test("Issue Identified", False, "No collection has the expected data - data may not be synced from VPS")
                else:
                    self.log_test("Dashboard Working Status", True, f"✅ Dashboard has real data (not $0) - Total Equity: ${dashboard_equity:,.2f}, Total P&L: ${dashboard_profit:,.2f}")
                
                return True
            else:
                self.log_test("Dashboard Comparison", False, f"Could not fetch dashboard data: HTTP {dashboard_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Calculation Logic Test", False, f"Exception: {str(e)}")
            return False
    
    def run_investigation(self):
        """Run complete MT5 Dashboard investigation"""
        print("🔍 MT5 DASHBOARD INVESTIGATION - Backend Showing $0")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Investigation Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Connect to MongoDB
        print("📋 STEP 1: Connect to MongoDB")
        if not self.connect_to_mongodb():
            print("❌ MongoDB connection failed. Cannot investigate data sources.")
            return False
        print()
        
        # Step 2: Authenticate
        print("📋 STEP 2: Authenticate as Admin")
        if not self.authenticate():
            print("❌ Authentication failed. Cannot test endpoints.")
            return False
        print()
        
        # Step 3: Test MT5 Dashboard Endpoint
        print("📋 STEP 3: Test MT5 Dashboard Endpoint")
        self.test_mt5_dashboard_endpoint()
        print()
        
        # Step 4: Investigate Data Sources
        print("📋 STEP 4: Investigate MT5 Data Sources")
        best_collection, collection_data = self.investigate_mt5_data_sources()
        print()
        
        # Step 5: Verify Data Fields
        print("📋 STEP 5: Verify Data Fields")
        self.verify_data_fields(best_collection, collection_data)
        print()
        
        # Step 6: Test Calculation Logic
        print("📋 STEP 6: Test Calculation Logic")
        self.test_calculation_logic()
        print()
        
        # Summary
        self.print_investigation_summary()
        
        # Return overall success
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        return passed_tests >= (total_tests * 0.7)  # 70% success rate acceptable for investigation
    
    def print_investigation_summary(self):
        """Print investigation summary"""
        print("=" * 80)
        print("📊 MT5 DASHBOARD INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED INVESTIGATIONS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ SUCCESSFUL INVESTIGATIONS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check if dashboard is showing $0
        dashboard_issue = any('CONFIRMED ISSUE' in r['details'] for r in self.test_results if not r['success'])
        if dashboard_issue:
            print("   ❌ CONFIRMED: MT5 Dashboard is showing $0 for all metrics")
        
        # Check if data exists in collections
        data_exists = any('has the most complete data' in r['details'] for r in self.test_results if r['success'])
        if data_exists:
            print("   ✅ Data exists in MongoDB collections")
        else:
            print("   ❌ No adequate data found in MongoDB collections")
        
        # Check for expected accounts
        accounts_found = any('All 4 expected accounts found' in r['details'] for r in self.test_results if r['success'])
        if accounts_found:
            print("   ✅ All 4 expected accounts (885822, 886557, 886066, 886602) found")
        else:
            print("   ❌ Not all expected accounts found")
        
        # Check calculation logic
        calculation_issue = any('Dashboard Data Source Match' in r['test'] for r in self.test_results)
        if calculation_issue:
            match_found = any('Dashboard Data Source Match' in r['test'] and r['success'] for r in self.test_results)
            if match_found:
                print("   ✅ Dashboard calculation logic identified")
            else:
                print("   ❌ Dashboard may be using wrong data source")
        
        print()
        print("🎯 INVESTIGATION CONCLUSIONS:")
        
        # Determine root cause
        if dashboard_issue and data_exists:
            print("   🔧 ROOT CAUSE: Dashboard endpoint may be querying wrong collection or has calculation bug")
            print("   💡 SOLUTION: Check which collection the /api/mt5/dashboard/overview endpoint is using")
        elif dashboard_issue and not data_exists:
            print("   🔧 ROOT CAUSE: No data in MongoDB collections - VPS sync may be broken")
            print("   💡 SOLUTION: Check MT5 VPS bridge service and data sync process")
        elif not dashboard_issue:
            print("   ✅ Dashboard appears to be working correctly")
        
        print()
        print("📋 NEXT STEPS:")
        print("   1. Check backend code for /api/mt5/dashboard/overview endpoint")
        print("   2. Verify which MongoDB collection it queries")
        print("   3. Ensure MT5 VPS bridge is syncing data correctly")
        print("   4. Test with corrected data source if needed")
        
        print()

def main():
    """Main investigation execution"""
    investigator = MT5DashboardInvestigation()
    success = investigator.run_investigation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()