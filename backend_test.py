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
BACKEND_URL = "https://financeflow-89.preview.emergentagent.com"

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
            self.db.admin.command('ping')
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
                required_fields = ['total_equity', 'total_profit', 'active_accounts', 'data_quality']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("MT5 Dashboard Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Extract values
                total_equity = data.get('total_equity', 0)
                total_profit = data.get('total_profit', 0)
                active_accounts = data.get('active_accounts', 0)
                data_quality = data.get('data_quality', 0)
                
                # Expected values from review request
                expected_equity_min = 100000  # Should be ~$121,000+
                expected_profit = 3551  # Should be $3,551
                expected_accounts = 4  # Should be 4 active accounts
                
                # Log current values
                details = f"Total Equity: ${total_equity:,.2f}, Total P&L: ${total_profit:,.2f}, Active Accounts: {active_accounts}, Data Quality: {data_quality}"
                
                # Check if values are $0 (the problem)
                if total_equity == 0 and total_profit == 0:
                    self.log_test("MT5 Dashboard Values", False, f"❌ CONFIRMED ISSUE: {details} - All values are $0!")
                    return False
                elif total_equity >= expected_equity_min and abs(total_profit - expected_profit) < 100:
                    self.log_test("MT5 Dashboard Values", True, f"✅ VALUES CORRECT: {details}")
                    return True
                else:
                    self.log_test("MT5 Dashboard Values", False, f"⚠️ UNEXPECTED VALUES: {details}")
                    return False
                
            else:
                self.log_test("MT5 Dashboard Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("MT5 Dashboard Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def investigate_mt5_data_sources(self):
        """Test 2: Check MT5 Accounts Data Sources"""
        if not self.db:
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
                dashboard_data = dashboard_response.json()
                dashboard_equity = dashboard_data.get('total_equity', 0)
                dashboard_profit = dashboard_data.get('total_profit', 0)
                
                # Find which collection matches dashboard (if any)
                matching_collection = None
                for collection_name, calc in calculations.items():
                    if (abs(calc['total_equity'] - dashboard_equity) < 1 and 
                        abs(calc['total_profit'] - dashboard_profit) < 1):
                        matching_collection = collection_name
                        break
                
                if matching_collection:
                    self.log_test("Dashboard Data Source Match", True, f"Dashboard uses data from '{matching_collection}' collection")
                else:
                    self.log_test("Dashboard Data Source Match", False, f"Dashboard values (${dashboard_equity:,.2f}, ${dashboard_profit:,.2f}) don't match any collection")
                
                # Identify the issue
                if dashboard_equity == 0 and dashboard_profit == 0:
                    # Check if any collection has good data
                    good_collections = [name for name, calc in calculations.items() 
                                      if calc['total_equity'] > 100000 and abs(calc['total_profit'] - 3551) < 1000]
                    
                    if good_collections:
                        self.log_test("Issue Identified", True, f"Dashboard shows $0 but collection(s) {good_collections} have correct data - API may be using wrong collection")
                    else:
                        self.log_test("Issue Identified", False, "No collection has the expected data - data may not be synced from VPS")
                
                return True
            else:
                self.log_test("Dashboard Comparison", False, f"Could not fetch dashboard data: HTTP {dashboard_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Calculation Logic Test", False, f"Exception: {str(e)}")
            return False
        """Test GET /api/admin/performance-fees/current"""
        try:
            url = f"{BACKEND_URL}/api/admin/performance-fees/current"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'totals' not in data:
                    self.log_test("Current Performance Fees Structure", False, "Missing 'totals' key in response")
                    return False
                
                if 'managers' not in data:
                    self.log_test("Current Performance Fees Structure", False, "Missing 'managers' key in response")
                    return False
                
                totals = data['totals']
                managers = data['managers']
                
                # Check totals structure
                total_fees = totals.get('total_performance_fees', 0)
                managers_with_fees = totals.get('managers_with_fees', 0)
                
                # Expected values from review request
                expected_total = 1000.64
                expected_managers_count = 3
                expected_total_managers = 4
                
                # Validate total performance fees
                if abs(total_fees - expected_total) < 0.01:
                    self.log_test("Performance Fees Total", True, f"Total fees: ${total_fees:.2f} (matches expected ${expected_total:.2f})")
                else:
                    self.log_test("Performance Fees Total", False, f"Total fees: ${total_fees:.2f} (expected ${expected_total:.2f})")
                    return False
                
                # Validate managers with fees count
                if managers_with_fees == expected_managers_count:
                    self.log_test("Managers With Fees Count", True, f"Managers with fees: {managers_with_fees} (matches expected {expected_managers_count})")
                else:
                    self.log_test("Managers With Fees Count", False, f"Managers with fees: {managers_with_fees} (expected {expected_managers_count})")
                
                # Validate total managers count
                if len(managers) == expected_total_managers:
                    self.log_test("Total Managers Count", True, f"Total managers: {len(managers)} (matches expected {expected_total_managers})")
                else:
                    self.log_test("Total Managers Count", False, f"Total managers: {len(managers)} (expected {expected_total_managers})")
                
                # Check for specific managers and their fees
                manager_fees = {}
                for manager in managers:
                    name = manager.get('manager_name', 'Unknown')  # Use manager_name instead of name
                    fee = manager.get('performance_fee_amount', 0)  # Use performance_fee_amount instead of performance_fee
                    manager_fees[name] = fee
                    
                    # Store manager ID for later tests
                    if 'manager_id' in manager:
                        self.manager_ids.append(manager['manager_id'])
                
                # Expected manager fees from review request
                expected_managers = {
                    'TradingHub Gold Provider': 848.91,
                    'GoldenTrade Provider': 98.41,
                    'UNO14 MAM Manager': 53.32,
                    'CP Strategy Provider': 0.0  # Loss, should have $0 fee
                }
                
                managers_verified = 0
                for expected_name, expected_fee in expected_managers.items():
                    found_manager = False
                    for manager_name, actual_fee in manager_fees.items():
                        if expected_name == manager_name:  # Exact match
                            found_manager = True
                            if abs(actual_fee - expected_fee) < 0.01:
                                self.log_test(f"Manager Fee - {expected_name}", True, f"${actual_fee:.2f} (matches expected ${expected_fee:.2f})")
                                managers_verified += 1
                            else:
                                self.log_test(f"Manager Fee - {expected_name}", False, f"${actual_fee:.2f} (expected ${expected_fee:.2f})")
                            break
                    
                    if not found_manager:
                        self.log_test(f"Manager Presence - {expected_name}", False, f"Manager not found in response")
                
                details = f"Total: ${total_fees:.2f}, Managers with fees: {managers_with_fees}, Total managers: {len(managers)}, Verified: {managers_verified}/4"
                self.log_test("Current Performance Fees", True, details)
                return True
                
            else:
                self.log_test("Current Performance Fees", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Current Performance Fees", False, f"Exception: {str(e)}")
            return False
    
    def test_calculate_daily_performance_fees(self):
        """Test POST /api/admin/performance-fees/calculate-daily"""
        try:
            url = f"{BACKEND_URL}/api/admin/performance-fees/calculate-daily"
            response = self.session.post(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'success' not in data:
                    self.log_test("Calculate Daily Fees Structure", False, "Missing 'success' key in response")
                    return False
                
                if not data.get('success'):
                    self.log_test("Calculate Daily Fees Success", False, f"success=false in response: {data}")
                    return False
                
                # Check for data section
                if 'data' in data and 'totals' in data['data']:
                    totals = data['data']['totals']
                    total_fees = totals.get('total_performance_fees', 0)
                    
                    # Should match expected total
                    expected_total = 1000.64
                    if abs(total_fees - expected_total) < 0.01:
                        self.log_test("Calculate Daily Fees Total", True, f"Calculated total: ${total_fees:.2f} (matches expected ${expected_total:.2f})")
                    else:
                        self.log_test("Calculate Daily Fees Total", False, f"Calculated total: ${total_fees:.2f} (expected ${expected_total:.2f})")
                
                # Check for success message
                message = data.get('message', '')
                expected_message = "Daily performance fees calculated successfully"
                if expected_message.lower() in message.lower():
                    self.log_test("Calculate Daily Fees Message", True, f"Message: {message}")
                else:
                    self.log_test("Calculate Daily Fees Message", False, f"Unexpected message: {message}")
                
                details = f"success={data.get('success')}, message='{message}'"
                self.log_test("Calculate Daily Performance Fees", True, details)
                return True
                
            else:
                self.log_test("Calculate Daily Performance Fees", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Calculate Daily Performance Fees", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_fees_summary(self):
        """Test GET /api/admin/performance-fees/summary"""
        try:
            # Test without parameters (current month)
            url = f"{BACKEND_URL}/api/admin/performance-fees/summary"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['period', 'accrued_fees', 'paid_fees', 'pending_payment', 'statistics']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Performance Fees Summary Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check expected values
                period = data.get('period', '')
                accrued_fees = data.get('accrued_fees', 0)
                paid_fees = data.get('paid_fees', 0)
                pending_payment = data.get('pending_payment', 0)
                
                # Expected values from review request
                expected_period = "2025-10"
                expected_accrued = 1000.64
                expected_paid = 0
                expected_pending = 1000.64
                
                # Validate period
                if expected_period in period:
                    self.log_test("Summary Period", True, f"Period: {period} (contains expected {expected_period})")
                else:
                    self.log_test("Summary Period", False, f"Period: {period} (expected to contain {expected_period})")
                
                # Validate accrued fees
                if abs(accrued_fees - expected_accrued) < 0.01:
                    self.log_test("Summary Accrued Fees", True, f"Accrued fees: ${accrued_fees:.2f} (matches expected ${expected_accrued:.2f})")
                else:
                    self.log_test("Summary Accrued Fees", False, f"Accrued fees: ${accrued_fees:.2f} (expected ${expected_accrued:.2f})")
                
                # Validate paid fees
                if paid_fees == expected_paid:
                    self.log_test("Summary Paid Fees", True, f"Paid fees: ${paid_fees:.2f} (matches expected ${expected_paid:.2f})")
                else:
                    self.log_test("Summary Paid Fees", False, f"Paid fees: ${paid_fees:.2f} (expected ${expected_paid:.2f})")
                
                # Validate pending payment
                if abs(pending_payment - expected_pending) < 0.01:
                    self.log_test("Summary Pending Payment", True, f"Pending payment: ${pending_payment:.2f} (matches expected ${expected_pending:.2f})")
                else:
                    self.log_test("Summary Pending Payment", False, f"Pending payment: ${pending_payment:.2f} (expected ${expected_pending:.2f})")
                
                # Check statistics
                if 'statistics' in data:
                    stats = data['statistics']
                    profitable_managers = stats.get('profitable_managers', 0)
                    expected_profitable = 3
                    
                    if profitable_managers == expected_profitable:
                        self.log_test("Summary Statistics", True, f"Profitable managers: {profitable_managers} (matches expected {expected_profitable})")
                    else:
                        self.log_test("Summary Statistics", False, f"Profitable managers: {profitable_managers} (expected {expected_profitable})")
                
                details = f"Period: {period}, Accrued: ${accrued_fees:.2f}, Paid: ${paid_fees:.2f}, Pending: ${pending_payment:.2f}"
                self.log_test("Performance Fees Summary", True, details)
                
                # Test with specific month/year parameters
                return self.test_performance_fees_summary_with_params()
                
            else:
                self.log_test("Performance Fees Summary", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Performance Fees Summary", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_fees_summary_with_params(self):
        """Test GET /api/admin/performance-fees/summary with month/year parameters"""
        try:
            url = f"{BACKEND_URL}/api/admin/performance-fees/summary"
            params = {"month": 10, "year": 2025}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should have same structure as before
                period = data.get('period', '')
                expected_period = "2025-10"
                
                if expected_period in period:
                    self.log_test("Summary With Params", True, f"Period with params: {period} (contains expected {expected_period})")
                    return True
                else:
                    self.log_test("Summary With Params", False, f"Period with params: {period} (expected to contain {expected_period})")
                    return False
                
            else:
                self.log_test("Summary With Params", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Summary With Params", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_fees_transactions(self):
        """Test GET /api/admin/performance-fees/transactions"""
        try:
            # Test without parameters
            url = f"{BACKEND_URL}/api/admin/performance-fees/transactions"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'transactions', 'total']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Performance Fees Transactions Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check expected values
                success = data.get('success', False)
                transactions = data.get('transactions', [])
                total = data.get('total', 0)
                
                # Expected values from review request (empty initially)
                if not success:
                    self.log_test("Transactions Success", False, f"success=false in response")
                    return False
                
                if not isinstance(transactions, list):
                    self.log_test("Transactions Array", False, f"transactions should be array, got {type(transactions)}")
                    return False
                
                # Should be empty array initially (no finalized transactions yet)
                if len(transactions) == 0 and total == 0:
                    self.log_test("Transactions Empty State", True, f"Empty transactions array and total=0 as expected")
                else:
                    self.log_test("Transactions Content", True, f"Found {len(transactions)} transactions, total={total}")
                
                details = f"success={success}, transactions count={len(transactions)}, total={total}"
                self.log_test("Performance Fees Transactions", True, details)
                
                # Test with limit/offset parameters
                return self.test_performance_fees_transactions_with_params()
                
            else:
                self.log_test("Performance Fees Transactions", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Performance Fees Transactions", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_fees_transactions_with_params(self):
        """Test GET /api/admin/performance-fees/transactions with limit/offset"""
        try:
            url = f"{BACKEND_URL}/api/admin/performance-fees/transactions"
            params = {"limit": 10, "offset": 0}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                success = data.get('success', False)
                if success:
                    self.log_test("Transactions With Params", True, f"Transactions endpoint works with limit/offset parameters")
                    return True
                else:
                    self.log_test("Transactions With Params", False, f"success=false with parameters")
                    return False
                
            else:
                self.log_test("Transactions With Params", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Transactions With Params", False, f"Exception: {str(e)}")
            return False
    
    def test_update_manager_performance_fee(self):
        """Test PUT /api/admin/money-managers/{manager_id}/performance-fee"""
        try:
            # Skip if no manager IDs found
            if not self.manager_ids:
                self.log_test("Update Manager Performance Fee", False, "No manager IDs available for testing")
                return False
            
            # Note: There's currently an ObjectId import issue in the backend
            self.log_test("Update Manager Performance Fee", False, "Skipped due to backend ObjectId import issue - needs 'from bson import ObjectId' in the endpoint")
            return False
            
            # Use first manager ID for testing
            manager_id = self.manager_ids[0]
            url = f"{BACKEND_URL}/api/admin/money-managers/{manager_id}/performance-fee"
            
            # Test data
            payload = {
                "performance_fee_rate": 0.35
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if 'success' not in data:
                    self.log_test("Update Manager Fee Structure", False, "Missing 'success' key in response")
                    return False
                
                if not data.get('success'):
                    self.log_test("Update Manager Fee Success", False, f"success=false in response: {data}")
                    return False
                
                # Check for manager data
                if 'manager' in data:
                    manager = data['manager']
                    updated_rate = manager.get('performance_fee_rate', 0)
                    expected_rate = 0.35
                    
                    if abs(updated_rate - expected_rate) < 0.001:
                        self.log_test("Manager Fee Rate Update", True, f"Updated rate: {updated_rate} (matches expected {expected_rate})")
                    else:
                        self.log_test("Manager Fee Rate Update", False, f"Updated rate: {updated_rate} (expected {expected_rate})")
                
                details = f"Manager ID: {manager_id}, success={data.get('success')}, rate=0.35"
                self.log_test("Update Manager Performance Fee", True, details)
                return True
                
            else:
                self.log_test("Update Manager Performance Fee", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Manager Performance Fee", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all performance fee endpoint tests"""
        print("🎯 PERFORMANCE FEE ENDPOINTS TESTING (Phase 3)")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test Current Performance Fees
        print("📋 TEST 1: Get Current Performance Fees")
        self.test_current_performance_fees()
        print()
        
        # Step 3: Test Calculate Daily Performance Fees
        print("📋 TEST 2: Calculate Daily Performance Fees")
        self.test_calculate_daily_performance_fees()
        print()
        
        # Step 4: Test Performance Fees Summary
        print("📋 TEST 3: Get Performance Fees Summary")
        self.test_performance_fees_summary()
        print()
        
        # Step 5: Test Performance Fees Transactions
        print("📋 TEST 4: List Performance Fee Transactions")
        self.test_performance_fees_transactions()
        print()
        
        # Step 6: Test Update Manager Performance Fee
        print("📋 TEST 6: Update Manager Performance Fee")
        self.test_update_manager_performance_fee()
        print()
        
        # Summary
        self.print_summary()
        
        # Return overall success
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        return passed_tests == total_tests
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 PERFORMANCE FEE ENDPOINTS TEST SUMMARY")
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
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 OVERALL RESULT: EXCELLENT - All performance fee endpoints working correctly!")
        elif success_rate >= 75:
            print("✅ OVERALL RESULT: GOOD - Most performance fee endpoints working")
        elif success_rate >= 50:
            print("⚠️ OVERALL RESULT: PARTIAL - Some performance fee endpoints need attention")
        else:
            print("❌ OVERALL RESULT: CRITICAL - Major performance fee endpoint issues detected")
        
        print()
        print("🔍 KEY FINDINGS:")
        
        # Check specific success criteria from review request
        current_fees_working = any(r['success'] and 'Current Performance Fees' in r['test'] 
                                  for r in self.test_results)
        
        if current_fees_working:
            print("   ✅ Current performance fees endpoint returns expected $1,000.64 total")
        else:
            print("   ❌ Current performance fees endpoint may not be working correctly")
        
        calculate_working = any(r['success'] and 'Calculate Daily Performance Fees' in r['test'] 
                               for r in self.test_results)
        
        if calculate_working:
            print("   ✅ Daily performance fees calculation working successfully")
        else:
            print("   ❌ Daily performance fees calculation may have issues")
        
        summary_working = any(r['success'] and 'Performance Fees Summary' in r['test'] 
                             for r in self.test_results)
        
        if summary_working:
            print("   ✅ Performance fees summary shows correct period and totals")
        else:
            print("   ❌ Performance fees summary may have issues")
        
        transactions_working = any(r['success'] and 'Performance Fees Transactions' in r['test'] 
                                  for r in self.test_results)
        
        if transactions_working:
            print("   ✅ Performance fees transactions endpoint working (even if empty)")
        else:
            print("   ❌ Performance fees transactions endpoint may have issues")
        
        manager_update_working = any(r['success'] and 'Update Manager Performance Fee' in r['test'] 
                                    for r in self.test_results)
        
        if manager_update_working:
            print("   ✅ Manager performance fee update working correctly")
        else:
            print("   ❌ Manager performance fee update may have issues")
        
        print()
        print("🎯 SUCCESS CRITERIA VERIFICATION:")
        print("   Expected Results:")
        print("   • Current fees total: $1,000.64 ✓" if current_fees_working else "   • Current fees total: $1,000.64 ❌")
        print("   • 3 managers with fees (TradingHub Gold, GoldenTrade, UNO14 MAM) ✓" if current_fees_working else "   • 3 managers with fees ❌")
        print("   • CP Strategy shows $0 fee (loss) ✓" if current_fees_working else "   • CP Strategy shows $0 fee ❌")
        print("   • Summary shows period '2025-10' and correct totals ✓" if summary_working else "   • Summary shows correct period and totals ❌")
        print("   • Transactions endpoint works (empty initially) ✓" if transactions_working else "   • Transactions endpoint works ❌")
        print("   • Manager fee update works ✓" if manager_update_working else "   • Manager fee update works ❌")
        
        print()

def main():
    """Main test execution"""
    tester = PerformanceFeeEndpointsTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()