#!/usr/bin/env python3
"""
CRITICAL PRODUCTION DATABASE INVESTIGATION TEST
==============================================

This test investigates the critical issue where production deployment shows:
- Total AUM: $0
- Total Clients: 0  
- Total Accounts: 0
- "No MT5 accounts found"

Despite Salvador Palma's data being restored in the database, the production application
at https://fidus-invest.emergent.host/ shows empty state.

INVESTIGATION FOCUS:
1. Production Database Service - Does Emergent deployment use a managed MongoDB service?
2. Environment Variables in Production - What MONGO_URL is actually used?
3. Database Access Methods - How to access the actual production database?
4. API-Based Data Creation - Can we use API endpoints to create Salvador's data?
5. Production Database Connection Test - Connect to the deployed application's actual database

GOAL: Identify the correct production database and create Salvador's data where 
the deployed application can actually access it.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
PRODUCTION_URL = "https://fidus-invest.emergent.host/api"
PREVIEW_URL = "https://auth-flow-debug-2.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class ProductionDatabaseInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.production_data = {}
        self.preview_data = {}
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate_admin(self, base_url):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{base_url}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                if token:
                    return token
                else:
                    self.log_result(f"Admin Authentication ({base_url})", False, "No token received", {"response": data})
                    return None
            else:
                self.log_result(f"Admin Authentication ({base_url})", False, f"HTTP {response.status_code}", {"response": response.text})
                return None
                
        except Exception as e:
            self.log_result(f"Admin Authentication ({base_url})", False, f"Exception: {str(e)}")
            return None
    
    def test_environment_comparison(self):
        """Compare production vs preview environment data"""
        print("\n🔍 TESTING ENVIRONMENT COMPARISON")
        print("=" * 60)
        
        # Test both environments
        environments = [
            ("Production", PRODUCTION_URL),
            ("Preview", PREVIEW_URL)
        ]
        
        for env_name, base_url in environments:
            print(f"\n📊 Testing {env_name} Environment: {base_url}")
            
            # Authenticate
            token = self.authenticate_admin(base_url)
            if not token:
                continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test critical endpoints
            endpoints = [
                ("/health", "Health Check"),
                ("/admin/clients", "Admin Clients"),
                ("/admin/investments", "Admin Investments"),
                ("/mt5/admin/accounts", "MT5 Accounts"),
                ("/admin/fund-performance/dashboard", "Fund Performance"),
                ("/admin/cashflow/overview", "Cash Flow Management")
            ]
            
            env_data = {}
            
            for endpoint, name in endpoints:
                try:
                    response = self.session.get(f"{base_url}{endpoint}", headers=headers, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        env_data[endpoint] = data
                        
                        # Extract key metrics
                        if endpoint == "/admin/clients":
                            client_count = len(data) if isinstance(data, list) else data.get('total_clients', 0)
                            print(f"   {name}: {client_count} clients")
                            
                        elif endpoint == "/admin/investments":
                            investment_count = len(data) if isinstance(data, list) else data.get('total_investments', 0)
                            total_aum = data.get('total_aum', 0) if isinstance(data, dict) else 0
                            print(f"   {name}: {investment_count} investments, ${total_aum:,.2f} AUM")
                            
                        elif endpoint == "/mt5/admin/accounts":
                            if isinstance(data, dict):
                                accounts = data.get('accounts', [])
                                summary = data.get('summary', {})
                                account_count = len(accounts) if accounts else summary.get('total_accounts', 0)
                                total_allocated = summary.get('total_allocated', 0)
                                print(f"   {name}: {account_count} accounts, ${total_allocated:,.2f} allocated")
                            else:
                                account_count = len(data) if isinstance(data, list) else 0
                                print(f"   {name}: {account_count} accounts")
                                
                        elif endpoint == "/admin/fund-performance/dashboard":
                            if isinstance(data, dict):
                                records = data.get('performance_records', [])
                                print(f"   {name}: {len(records)} performance records")
                            else:
                                print(f"   {name}: Response received")
                                
                        elif endpoint == "/admin/cashflow/overview":
                            if isinstance(data, dict):
                                mt5_profits = data.get('mt5_trading_profits', 0)
                                client_obligations = data.get('client_interest_obligations', 0)
                                print(f"   {name}: MT5 ${mt5_profits:,.2f}, Obligations ${client_obligations:,.2f}")
                            else:
                                print(f"   {name}: Response received")
                                
                        else:
                            print(f"   {name}: ✅ OK")
                            
                    else:
                        print(f"   {name}: ❌ HTTP {response.status_code}")
                        env_data[endpoint] = {"error": response.status_code, "text": response.text}
                        
                except Exception as e:
                    print(f"   {name}: ❌ Exception: {str(e)}")
                    env_data[endpoint] = {"error": str(e)}
            
            # Store environment data
            if env_name == "Production":
                self.production_data = env_data
            else:
                self.preview_data = env_data
    
    def test_salvador_data_presence(self):
        """Test for Salvador Palma's specific data in both environments"""
        print("\n🔍 TESTING SALVADOR PALMA DATA PRESENCE")
        print("=" * 60)
        
        environments = [
            ("Production", PRODUCTION_URL, self.production_data),
            ("Preview", PREVIEW_URL, self.preview_data)
        ]
        
        for env_name, base_url, env_data in environments:
            print(f"\n📊 Salvador Data Check - {env_name}")
            
            # Authenticate
            token = self.authenticate_admin(base_url)
            if not token:
                continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            # Check for Salvador specifically
            salvador_found = False
            salvador_data = {}
            
            # Check clients
            try:
                response = self.session.get(f"{base_url}/admin/clients", headers=headers, timeout=15)
                if response.status_code == 200:
                    clients = response.json()
                    if isinstance(clients, list):
                        for client in clients:
                            if (client.get('id') == 'client_003' or 
                                'SALVADOR' in client.get('name', '').upper() or
                                'chava@alyarglobal.com' in client.get('email', '')):
                                salvador_found = True
                                salvador_data['client'] = client
                                print(f"   ✅ Salvador client found: {client.get('name')} ({client.get('id')})")
                                break
                    
                    if not salvador_found:
                        print(f"   ❌ Salvador client NOT found in {len(clients) if isinstance(clients, list) else 0} clients")
                        
            except Exception as e:
                print(f"   ❌ Error checking clients: {str(e)}")
            
            # Check Salvador's investments
            if salvador_found:
                try:
                    response = self.session.get(f"{base_url}/investments/client/client_003", headers=headers, timeout=15)
                    if response.status_code == 200:
                        investments = response.json()
                        salvador_data['investments'] = investments
                        
                        if isinstance(investments, list) and len(investments) > 0:
                            print(f"   ✅ Salvador investments found: {len(investments)} investments")
                            
                            # Check for specific investments
                            balance_found = False
                            core_found = False
                            total_amount = 0
                            
                            for inv in investments:
                                fund_code = inv.get('fund_code')
                                principal = inv.get('principal_amount', 0)
                                total_amount += principal
                                
                                if fund_code == 'BALANCE' and abs(principal - 1263485.40) < 1:
                                    balance_found = True
                                    print(f"     • BALANCE fund: ${principal:,.2f} ✅")
                                elif fund_code == 'CORE' and abs(principal - 4000.00) < 1:
                                    core_found = True
                                    print(f"     • CORE fund: ${principal:,.2f} ✅")
                                else:
                                    print(f"     • {fund_code} fund: ${principal:,.2f}")
                            
                            print(f"   Total Investment Amount: ${total_amount:,.2f}")
                            
                            if balance_found and core_found:
                                print(f"   ✅ Both expected investments found")
                            else:
                                missing = []
                                if not balance_found:
                                    missing.append("BALANCE ($1,263,485.40)")
                                if not core_found:
                                    missing.append("CORE ($4,000.00)")
                                print(f"   ❌ Missing investments: {', '.join(missing)}")
                                
                        else:
                            print(f"   ❌ Salvador has 0 investments")
                            
                    else:
                        print(f"   ❌ Failed to get Salvador's investments: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error checking Salvador's investments: {str(e)}")
            
            # Check Salvador's MT5 accounts
            if salvador_found:
                try:
                    response = self.session.get(f"{base_url}/mt5/admin/accounts", headers=headers, timeout=15)
                    if response.status_code == 200:
                        mt5_data = response.json()
                        
                        salvador_mt5_accounts = []
                        if isinstance(mt5_data, dict):
                            accounts = mt5_data.get('accounts', [])
                        else:
                            accounts = mt5_data if isinstance(mt5_data, list) else []
                        
                        for account in accounts:
                            if account.get('client_id') == 'client_003':
                                salvador_mt5_accounts.append(account)
                        
                        salvador_data['mt5_accounts'] = salvador_mt5_accounts
                        
                        if len(salvador_mt5_accounts) > 0:
                            print(f"   ✅ Salvador MT5 accounts found: {len(salvador_mt5_accounts)} accounts")
                            
                            # Check for specific accounts
                            doo_found = False
                            vt_found = False
                            
                            for account in salvador_mt5_accounts:
                                login = str(account.get('login', ''))
                                broker = str(account.get('broker', ''))
                                
                                if login == '9928326':
                                    doo_found = True
                                    print(f"     • DooTechnology account: Login {login} ✅")
                                elif login == '15759667':
                                    vt_found = True
                                    print(f"     • VT Markets account: Login {login} ✅")
                                else:
                                    print(f"     • Other account: Login {login}, Broker {broker}")
                            
                            if doo_found and vt_found:
                                print(f"   ✅ Both expected MT5 accounts found")
                            else:
                                missing = []
                                if not doo_found:
                                    missing.append("DooTechnology (9928326)")
                                if not vt_found:
                                    missing.append("VT Markets (15759667)")
                                print(f"   ❌ Missing MT5 accounts: {', '.join(missing)}")
                                
                        else:
                            print(f"   ❌ Salvador has 0 MT5 accounts")
                            
                    else:
                        print(f"   ❌ Failed to get MT5 accounts: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error checking MT5 accounts: {str(e)}")
            
            # Store Salvador data for comparison
            if env_name == "Production":
                self.production_salvador = salvador_data
            else:
                self.preview_salvador = salvador_data
    
    def test_database_connectivity_investigation(self):
        """Investigate database connectivity and configuration"""
        print("\n🔍 TESTING DATABASE CONNECTIVITY INVESTIGATION")
        print("=" * 60)
        
        # Test database health endpoints
        environments = [
            ("Production", PRODUCTION_URL),
            ("Preview", PREVIEW_URL)
        ]
        
        for env_name, base_url in environments:
            print(f"\n📊 Database Connectivity - {env_name}")
            
            # Test health endpoints
            health_endpoints = [
                ("/health", "Basic Health"),
                ("/health/ready", "Readiness Check"),
                ("/health/metrics", "Health Metrics")
            ]
            
            for endpoint, name in health_endpoints:
                try:
                    response = self.session.get(f"{base_url}{endpoint}", timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   {name}: ✅ OK")
                        
                        # Extract database info if available
                        if 'database' in data:
                            db_status = data['database']
                            print(f"     Database Status: {db_status}")
                            
                        if isinstance(data.get('database'), dict):
                            db_info = data['database']
                            if 'collections' in db_info:
                                collections = db_info['collections']
                                print(f"     Collections: {collections}")
                                
                            if 'data_size' in db_info:
                                data_size = db_info['data_size']
                                print(f"     Data Size: {data_size} bytes")
                            
                    else:
                        print(f"   {name}: ❌ HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   {name}: ❌ Exception: {str(e)}")
    
    def test_api_based_data_creation(self):
        """Test if we can create Salvador's data via API endpoints"""
        print("\n🔍 TESTING API-BASED DATA CREATION")
        print("=" * 60)
        
        # Focus on production environment
        print(f"\n📊 Testing Data Creation in Production")
        
        # Authenticate
        token = self.authenticate_admin(PRODUCTION_URL)
        if not token:
            print("❌ Cannot authenticate with production - skipping API data creation test")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: Try to create Salvador's client profile
        print("\n1️⃣ Testing Client Creation")
        try:
            client_data = {
                "username": "client3",
                "name": "SALVADOR PALMA",
                "email": "chava@alyarglobal.com",
                "phone": "+1-555-SALVADOR",
                "notes": "Created via API for production database investigation"
            }
            
            response = self.session.post(f"{PRODUCTION_URL}/admin/clients/create", 
                                       json=client_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Client creation successful: {result}")
            elif response.status_code == 409:
                print(f"   ✅ Client already exists (expected)")
            else:
                print(f"   ❌ Client creation failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Client creation exception: {str(e)}")
        
        # Test 2: Try to create Salvador's BALANCE investment
        print("\n2️⃣ Testing BALANCE Investment Creation")
        try:
            investment_data = {
                "client_id": "client_003",
                "fund_code": "BALANCE",
                "amount": 1263485.40,
                "deposit_date": "2025-04-01"
            }
            
            response = self.session.post(f"{PRODUCTION_URL}/investments/create", 
                                       json=investment_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                investment_id = result.get('investment_id')
                print(f"   ✅ BALANCE investment created: {investment_id}")
            else:
                print(f"   ❌ BALANCE investment creation failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ BALANCE investment creation exception: {str(e)}")
        
        # Test 3: Try to create Salvador's CORE investment
        print("\n3️⃣ Testing CORE Investment Creation")
        try:
            investment_data = {
                "client_id": "client_003",
                "fund_code": "CORE",
                "amount": 4000.00,
                "deposit_date": "2025-09-04"
            }
            
            response = self.session.post(f"{PRODUCTION_URL}/investments/create", 
                                       json=investment_data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                investment_id = result.get('investment_id')
                print(f"   ✅ CORE investment created: {investment_id}")
            else:
                print(f"   ❌ CORE investment creation failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ CORE investment creation exception: {str(e)}")
        
        # Test 4: Verify data was created
        print("\n4️⃣ Testing Data Verification After Creation")
        time.sleep(2)  # Wait for data to be processed
        
        try:
            response = self.session.get(f"{PRODUCTION_URL}/admin/clients", headers=headers, timeout=15)
            if response.status_code == 200:
                clients = response.json()
                client_count = len(clients) if isinstance(clients, list) else clients.get('total_clients', 0)
                print(f"   Clients after creation: {client_count}")
                
                # Look for Salvador
                salvador_found = False
                if isinstance(clients, list):
                    for client in clients:
                        if client.get('id') == 'client_003':
                            salvador_found = True
                            print(f"   ✅ Salvador found: {client.get('name')}")
                            break
                
                if not salvador_found:
                    print(f"   ❌ Salvador still not found after creation attempt")
                    
        except Exception as e:
            print(f"   ❌ Verification exception: {str(e)}")
    
    def run_investigation(self):
        """Run complete production database investigation"""
        print("🚨 CRITICAL PRODUCTION DATABASE INVESTIGATION")
        print("=" * 80)
        print(f"Investigation Time: {datetime.now().isoformat()}")
        print(f"Production URL: {PRODUCTION_URL}")
        print(f"Preview URL: {PREVIEW_URL}")
        print()
        
        print("PROBLEM: Production shows $0 AUM, 0 clients, 0 accounts despite database restoration")
        print("GOAL: Find the actual production database and create Salvador's data there")
        print()
        
        # Run investigation tests
        self.test_environment_comparison()
        self.test_salvador_data_presence()
        self.test_database_connectivity_investigation()
        self.test_api_based_data_creation()
        
        # Generate comprehensive analysis
        self.generate_investigation_analysis()
        
        return True
    
    def generate_investigation_analysis(self):
        """Generate comprehensive investigation analysis"""
        print("\n" + "=" * 80)
        print("🔍 PRODUCTION DATABASE INVESTIGATION ANALYSIS")
        print("=" * 80)
        
        # Compare environments
        print("\n📊 ENVIRONMENT COMPARISON:")
        
        # Production analysis
        print("\n🏭 PRODUCTION ENVIRONMENT:")
        prod_clients = 0
        prod_investments = 0
        prod_mt5_accounts = 0
        
        if '/admin/clients' in self.production_data:
            clients_data = self.production_data['/admin/clients']
            if isinstance(clients_data, list):
                prod_clients = len(clients_data)
            elif isinstance(clients_data, dict):
                prod_clients = clients_data.get('total_clients', 0)
        
        if '/admin/investments' in self.production_data:
            inv_data = self.production_data['/admin/investments']
            if isinstance(inv_data, list):
                prod_investments = len(inv_data)
            elif isinstance(inv_data, dict):
                prod_investments = inv_data.get('total_investments', 0)
        
        if '/mt5/admin/accounts' in self.production_data:
            mt5_data = self.production_data['/mt5/admin/accounts']
            if isinstance(mt5_data, dict):
                accounts = mt5_data.get('accounts', [])
                prod_mt5_accounts = len(accounts)
            elif isinstance(mt5_data, list):
                prod_mt5_accounts = len(mt5_data)
        
        print(f"   Clients: {prod_clients}")
        print(f"   Investments: {prod_investments}")
        print(f"   MT5 Accounts: {prod_mt5_accounts}")
        
        # Preview analysis
        print("\n🔍 PREVIEW ENVIRONMENT:")
        prev_clients = 0
        prev_investments = 0
        prev_mt5_accounts = 0
        
        if '/admin/clients' in self.preview_data:
            clients_data = self.preview_data['/admin/clients']
            if isinstance(clients_data, list):
                prev_clients = len(clients_data)
            elif isinstance(clients_data, dict):
                prev_clients = clients_data.get('total_clients', 0)
        
        if '/admin/investments' in self.preview_data:
            inv_data = self.preview_data['/admin/investments']
            if isinstance(inv_data, list):
                prev_investments = len(inv_data)
            elif isinstance(inv_data, dict):
                prev_investments = inv_data.get('total_investments', 0)
        
        if '/mt5/admin/accounts' in self.preview_data:
            mt5_data = self.preview_data['/mt5/admin/accounts']
            if isinstance(mt5_data, dict):
                accounts = mt5_data.get('accounts', [])
                prev_mt5_accounts = len(accounts)
            elif isinstance(mt5_data, list):
                prev_mt5_accounts = len(mt5_data)
        
        print(f"   Clients: {prev_clients}")
        print(f"   Investments: {prev_investments}")
        print(f"   MT5 Accounts: {prev_mt5_accounts}")
        
        # Root cause analysis
        print("\n🚨 ROOT CAUSE ANALYSIS:")
        
        if prod_clients == 0 and prod_investments == 0 and prod_mt5_accounts == 0:
            if prev_clients > 0 or prev_investments > 0 or prev_mt5_accounts > 0:
                print("   ❌ CONFIRMED: Production database is COMPLETELY EMPTY")
                print("   ❌ Preview environment has data, production does not")
                print("   🔍 ROOT CAUSE: Production uses DIFFERENT database than preview")
                print("   💡 SOLUTION: Need to deploy data to production database or fix database connection")
            else:
                print("   ❌ BOTH environments are empty - system-wide data issue")
                print("   🔍 ROOT CAUSE: Database restoration may have failed in both environments")
        elif prod_clients > 0 and prod_investments == 0:
            print("   ❌ PARTIAL DATA: Production has clients but no investments")
            print("   🔍 ROOT CAUSE: Investment data not properly synced to production database")
        else:
            print("   ✅ Production has some data - investigating specific Salvador data...")
        
        # Salvador-specific analysis
        print("\n👤 SALVADOR PALMA SPECIFIC ANALYSIS:")
        
        salvador_in_prod = hasattr(self, 'production_salvador') and bool(self.production_salvador)
        salvador_in_prev = hasattr(self, 'preview_salvador') and bool(self.preview_salvador)
        
        if not salvador_in_prod and salvador_in_prev:
            print("   ❌ CONFIRMED: Salvador exists in preview but NOT in production")
            print("   🔍 ROOT CAUSE: Salvador's data not deployed to production database")
            print("   💡 SOLUTION: Deploy Salvador's data to production database")
        elif not salvador_in_prod and not salvador_in_prev:
            print("   ❌ Salvador missing from BOTH environments")
            print("   🔍 ROOT CAUSE: Database restoration failed completely")
        elif salvador_in_prod:
            print("   ✅ Salvador found in production - investigating data completeness...")
            
            prod_salvador = getattr(self, 'production_salvador', {})
            has_client = 'client' in prod_salvador
            has_investments = 'investments' in prod_salvador and len(prod_salvador['investments']) > 0
            has_mt5 = 'mt5_accounts' in prod_salvador and len(prod_salvador['mt5_accounts']) > 0
            
            print(f"     Client Profile: {'✅' if has_client else '❌'}")
            print(f"     Investments: {'✅' if has_investments else '❌'}")
            print(f"     MT5 Accounts: {'✅' if has_mt5 else '❌'}")
            
            if has_client and not has_investments:
                print("   🔍 ROOT CAUSE: Salvador's client exists but investments missing")
                print("   💡 SOLUTION: Create Salvador's investments in production")
        
        # Final recommendations
        print("\n💡 RECOMMENDED ACTIONS:")
        
        if prod_clients == 0:
            print("   1. 🚨 CRITICAL: Production database is empty")
            print("      - Verify production MONGO_URL environment variable")
            print("      - Check if production uses managed MongoDB service")
            print("      - Deploy complete database restoration to production")
        
        print("   2. 📋 IMMEDIATE STEPS:")
        print("      - Use API endpoints to create Salvador's data in production")
        print("      - Verify production database connection configuration")
        print("      - Test data persistence after creation")
        
        print("   3. 🔧 INVESTIGATION NEEDED:")
        print("      - What database service does Emergent deployment actually use?")
        print("      - Are there production-specific environment variables?")
        print("      - How to access the actual production database directly?")
        
        # Test summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        
        print(f"\n📊 INVESTIGATION SUMMARY:")
        print(f"   Tests Run: {total_tests}")
        print(f"   Tests Passed: {passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
        
        print("\n" + "=" * 80)

def main():
    """Main investigation execution"""
    investigator = ProductionDatabaseInvestigator()
    success = investigator.run_investigation()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()