#!/usr/bin/env python3
"""
REFERRAL AGENT PORTAL COMPREHENSIVE TESTING SUITE
Testing production MongoDB Atlas & Render API integration

Portal URL: https://viking-trade-dash-1.preview.emergentagent.com/referral-agent/login
Production API: https://viking-trade-dash-1.preview.emergentagent.com/api

Test Coverage:
1. Salvador Palma Login & Dashboard
2. Josselyn Arellano López Login & Dashboard  
3. Leads Management (Salvador)
4. Clients Management (Salvador)
5. Commission Schedule (Salvador)
6. Data Segregation Security
7. Protected Routes
8. Token Validation
9. Logout

Expected Results:
- Salvador: ~$118,000 in client investments, ~$3,326.76 commissions, Alejandro as client
- Josselyn: Empty state (0 leads, 0 clients, $0 commissions)
- Data segregation enforced (agents only see their data)
- All CRUD operations work
- No 500 errors or crashes
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

class ReferralAgentPortalTester:
    def __init__(self):
        self.base_url = "https://viking-trade-dash-1.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.salvador_token = None
        self.josselyn_token = None
        self.test_results = []
        
        # Test credentials
        self.salvador_credentials = {
            "email": "chava@alyarglobal.com",
            "password": "FidusAgent2025!"
        }
        
        self.josselyn_credentials = {
            "email": "Jazioni@yahoo.com.mx", 
            "password": "FidusAgent2025!"
        }
        
    def log_test(self, test_name: str, status: str, details: str, expected: Any = None, actual: Any = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,  # PASS, FAIL, ERROR
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {details}")
        
        if expected is not None and actual is not None:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
    
    def test_salvador_login_dashboard(self) -> bool:
        """TEST 1: Salvador Palma Login & Dashboard"""
        try:
            print("\n🔐 Testing Salvador Palma Login & Dashboard...")
            
            # Step 1: POST login to /api/referral-agent/auth/login
            login_response = requests.post(
                f"{self.base_url}/referral-agent/auth/login",
                json=self.salvador_credentials,
                timeout=30
            )
            
            if login_response.status_code != 200:
                self.log_test("Salvador Login", "FAIL", 
                            f"Login failed with HTTP {login_response.status_code}: {login_response.text}")
                return False
            
            login_data = login_response.json()
            
            # Step 2: Verify JWT token received
            if not login_data.get('access_token'):
                self.log_test("Salvador JWT Token", "FAIL", "No JWT token received in login response")
                return False
            
            self.salvador_token = login_data['access_token']
            self.log_test("Salvador Login", "PASS", "Successfully authenticated and received JWT token")
            
            # Set authorization header for subsequent requests
            headers = {'Authorization': f'Bearer {self.salvador_token}'}
            
            # Step 3: GET dashboard from /api/referral-agent/crm/dashboard
            dashboard_response = requests.get(
                f"{self.base_url}/referral-agent/crm/dashboard",
                headers=headers,
                timeout=30
            )
            
            if dashboard_response.status_code != 200:
                self.log_test("Salvador Dashboard API", "FAIL", 
                            f"Dashboard API failed with HTTP {dashboard_response.status_code}: {dashboard_response.text}")
                return False
            
            dashboard_data = dashboard_response.json()
            
            # Step 4: Verify Salvador's stats
            success = True
            
            # Check for Alejandro as client
            clients = dashboard_data.get('clients', [])
            alejandro_found = False
            for client in clients:
                if 'alejandro' in client.get('name', '').lower() or 'mariscal' in client.get('name', '').lower():
                    alejandro_found = True
                    break
            
            if alejandro_found:
                self.log_test("Salvador - Alejandro Client", "PASS", "Alejandro appears in Salvador's clients")
            else:
                self.log_test("Salvador - Alejandro Client", "FAIL", "Alejandro not found in Salvador's clients")
                success = False
            
            # Check client investments (~$118,000)
            total_investments = dashboard_data.get('total_client_investments', 0)
            expected_investments = 118000  # Allow some tolerance
            
            if abs(total_investments - expected_investments) < 5000:  # $5k tolerance
                self.log_test("Salvador - Client Investments", "PASS", 
                            f"Client investments within expected range", 
                            f"~${expected_investments:,}", 
                            f"${total_investments:,}")
            else:
                self.log_test("Salvador - Client Investments", "FAIL", 
                            f"Client investments outside expected range", 
                            f"~${expected_investments:,}", 
                            f"${total_investments:,}")
                success = False
            
            # Check commission data (~$3,326.76)
            total_commissions = dashboard_data.get('total_commissions', 0)
            expected_commissions = 3326.76
            
            if abs(total_commissions - expected_commissions) < 100:  # $100 tolerance
                self.log_test("Salvador - Commission Data", "PASS", 
                            f"Commission data within expected range", 
                            f"~${expected_commissions:,.2f}", 
                            f"${total_commissions:,.2f}")
            else:
                self.log_test("Salvador - Commission Data", "FAIL", 
                            f"Commission data outside expected range", 
                            f"~${expected_commissions:,.2f}", 
                            f"${total_commissions:,.2f}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Salvador Login & Dashboard Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_josselyn_login_dashboard(self) -> bool:
        """TEST 2: Josselyn Arellano López Login & Dashboard"""
        try:
            print("\n🔐 Testing Josselyn Arellano López Login & Dashboard...")
            
            # Step 1: POST login to /api/referral-agent/auth/login
            login_response = requests.post(
                f"{self.base_url}/referral-agent/auth/login",
                json=self.josselyn_credentials,
                timeout=30
            )
            
            if login_response.status_code != 200:
                self.log_test("Josselyn Login", "FAIL", 
                            f"Login failed with HTTP {login_response.status_code}: {login_response.text}")
                return False
            
            login_data = login_response.json()
            
            # Step 2: Verify JWT token received
            if not login_data.get('access_token'):
                self.log_test("Josselyn JWT Token", "FAIL", "No JWT token received in login response")
                return False
            
            self.josselyn_token = login_data['access_token']
            self.log_test("Josselyn Login", "PASS", "Successfully authenticated and received JWT token")
            
            # Set authorization header for subsequent requests
            headers = {'Authorization': f'Bearer {self.josselyn_token}'}
            
            # Step 3: GET dashboard from /api/referral-agent/crm/dashboard
            dashboard_response = requests.get(
                f"{self.base_url}/referral-agent/crm/dashboard",
                headers=headers,
                timeout=30
            )
            
            if dashboard_response.status_code != 200:
                self.log_test("Josselyn Dashboard API", "FAIL", 
                            f"Dashboard API failed with HTTP {dashboard_response.status_code}: {dashboard_response.text}")
                return False
            
            dashboard_data = dashboard_response.json()
            
            # Step 4: Verify empty state handling (0 leads, 0 clients, $0 commissions)
            success = True
            
            # Check leads count = 0
            leads_count = dashboard_data.get('leads_count', 0)
            if leads_count == 0:
                self.log_test("Josselyn - Leads Count", "PASS", "Leads count is 0 as expected for empty state")
            else:
                self.log_test("Josselyn - Leads Count", "FAIL", 
                            f"Expected 0 leads, got {leads_count}")
                success = False
            
            # Check clients count = 0
            clients_count = dashboard_data.get('clients_count', 0)
            if clients_count == 0:
                self.log_test("Josselyn - Clients Count", "PASS", "Clients count is 0 as expected for empty state")
            else:
                self.log_test("Josselyn - Clients Count", "FAIL", 
                            f"Expected 0 clients, got {clients_count}")
                success = False
            
            # Check commissions = $0
            total_commissions = dashboard_data.get('total_commissions', 0)
            if total_commissions == 0:
                self.log_test("Josselyn - Commissions", "PASS", "Commissions are $0 as expected for empty state")
            else:
                self.log_test("Josselyn - Commissions", "FAIL", 
                            f"Expected $0 commissions, got ${total_commissions}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Josselyn Login & Dashboard Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_leads_management_salvador(self) -> bool:
        """TEST 3: Leads Management (Salvador)"""
        try:
            print("\n📋 Testing Leads Management (Salvador)...")
            
            if not self.salvador_token:
                self.log_test("Leads Management Setup", "FAIL", "Salvador token not available")
                return False
            
            headers = {'Authorization': f'Bearer {self.salvador_token}'}
            success = True
            
            # 1. GET /api/referral-agent/crm/leads
            leads_response = requests.get(
                f"{self.base_url}/referral-agent/crm/leads",
                headers=headers,
                timeout=30
            )
            
            if leads_response.status_code != 200:
                self.log_test("Salvador Leads API", "FAIL", 
                            f"Leads API failed with HTTP {leads_response.status_code}: {leads_response.text}")
                return False
            
            leads_data = leads_response.json()
            leads = leads_data.get('leads', [])
            
            self.log_test("Salvador Leads API", "PASS", 
                        f"Successfully retrieved {len(leads)} leads")
            
            # 2. Filter by status: converted
            converted_response = requests.get(
                f"{self.base_url}/referral-agent/crm/leads?status=converted",
                headers=headers,
                timeout=30
            )
            
            if converted_response.status_code == 200:
                converted_data = converted_response.json()
                converted_leads = converted_data.get('leads', [])
                self.log_test("Salvador Converted Leads", "PASS", 
                            f"Retrieved {len(converted_leads)} converted leads")
            else:
                self.log_test("Salvador Converted Leads", "FAIL", 
                            f"Converted leads filter failed: HTTP {converted_response.status_code}")
                success = False
            
            # 3. Filter by status: pending
            pending_response = requests.get(
                f"{self.base_url}/referral-agent/crm/leads?status=pending",
                headers=headers,
                timeout=30
            )
            
            if pending_response.status_code == 200:
                pending_data = pending_response.json()
                pending_leads = pending_data.get('leads', [])
                self.log_test("Salvador Pending Leads", "PASS", 
                            f"Retrieved {len(pending_leads)} pending leads")
            else:
                self.log_test("Salvador Pending Leads", "FAIL", 
                            f"Pending leads filter failed: HTTP {pending_response.status_code}")
                success = False
            
            # 4. Test lead detail (if leads exist)
            if leads:
                lead_id = leads[0].get('id') or leads[0].get('lead_id')
                if lead_id:
                    detail_response = requests.get(
                        f"{self.base_url}/referral-agent/crm/leads/{lead_id}",
                        headers=headers,
                        timeout=30
                    )
                    
                    if detail_response.status_code == 200:
                        self.log_test("Salvador Lead Detail", "PASS", 
                                    f"Successfully retrieved lead detail for {lead_id}")
                        
                        # 5. Test add note
                        note_data = {"note_text": "Test note from automated testing"}
                        note_response = requests.post(
                            f"{self.base_url}/referral-agent/crm/leads/{lead_id}/notes",
                            headers=headers,
                            json=note_data,
                            timeout=30
                        )
                        
                        if note_response.status_code in [200, 201]:
                            self.log_test("Salvador Add Note", "PASS", "Successfully added note to lead")
                        else:
                            self.log_test("Salvador Add Note", "FAIL", 
                                        f"Add note failed: HTTP {note_response.status_code}")
                            success = False
                        
                        # 6. Test update status
                        status_data = {
                            "status": "contacted",
                            "next_follow_up": "2025-12-01"
                        }
                        status_response = requests.put(
                            f"{self.base_url}/referral-agent/crm/leads/{lead_id}/status",
                            headers=headers,
                            json=status_data,
                            timeout=30
                        )
                        
                        if status_response.status_code == 200:
                            self.log_test("Salvador Update Status", "PASS", "Successfully updated lead status")
                        else:
                            self.log_test("Salvador Update Status", "FAIL", 
                                        f"Update status failed: HTTP {status_response.status_code}")
                            success = False
                    else:
                        self.log_test("Salvador Lead Detail", "FAIL", 
                                    f"Lead detail failed: HTTP {detail_response.status_code}")
                        success = False
            else:
                self.log_test("Salvador Lead Operations", "PASS", 
                            "No leads available for CRUD testing (expected for some agents)")
            
            return success
            
        except Exception as e:
            self.log_test("Leads Management Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_clients_management_salvador(self) -> bool:
        """TEST 4: Clients Management (Salvador)"""
        try:
            print("\n👥 Testing Clients Management (Salvador)...")
            
            if not self.salvador_token:
                self.log_test("Clients Management Setup", "FAIL", "Salvador token not available")
                return False
            
            headers = {'Authorization': f'Bearer {self.salvador_token}'}
            
            # GET /api/referral-agent/crm/clients
            clients_response = requests.get(
                f"{self.base_url}/referral-agent/crm/clients",
                headers=headers,
                timeout=30
            )
            
            if clients_response.status_code != 200:
                self.log_test("Salvador Clients API", "FAIL", 
                            f"Clients API failed with HTTP {clients_response.status_code}: {clients_response.text}")
                return False
            
            clients_data = clients_response.json()
            clients = clients_data.get('clients', [])
            
            success = True
            
            # Should return Alejandro Mariscal
            alejandro_found = False
            alejandro_client = None
            
            for client in clients:
                client_name = client.get('name', '').lower()
                if 'alejandro' in client_name and 'mariscal' in client_name:
                    alejandro_found = True
                    alejandro_client = client
                    break
            
            if alejandro_found:
                self.log_test("Salvador - Alejandro Client Found", "PASS", 
                            f"Found Alejandro Mariscal in Salvador's clients")
                
                # Verify investment data
                total_investment = alejandro_client.get('total_investment', 0)
                expected_investment = 118000  # ~$118,000
                
                if abs(total_investment - expected_investment) < 5000:  # $5k tolerance
                    self.log_test("Alejandro Total Investment", "PASS", 
                                f"Investment amount within expected range", 
                                f"~${expected_investment:,}", 
                                f"${total_investment:,}")
                else:
                    self.log_test("Alejandro Total Investment", "FAIL", 
                                f"Investment amount outside expected range", 
                                f"~${expected_investment:,}", 
                                f"${total_investment:,}")
                    success = False
                
                # Check active investments count
                active_investments = alejandro_client.get('active_investments_count', 0)
                if active_investments > 0:
                    self.log_test("Alejandro Active Investments", "PASS", 
                                f"Has {active_investments} active investments")
                else:
                    self.log_test("Alejandro Active Investments", "FAIL", 
                                "No active investments found")
                    success = False
                
                # Check investment breakdown by fund
                investments = alejandro_client.get('investments', [])
                fund_breakdown = {}
                for inv in investments:
                    fund_code = inv.get('fund_code', 'UNKNOWN')
                    amount = inv.get('amount', 0)
                    fund_breakdown[fund_code] = fund_breakdown.get(fund_code, 0) + amount
                
                if fund_breakdown:
                    self.log_test("Alejandro Fund Breakdown", "PASS", 
                                f"Investment breakdown: {fund_breakdown}")
                else:
                    self.log_test("Alejandro Fund Breakdown", "FAIL", 
                                "No fund breakdown available")
                    success = False
                
            else:
                self.log_test("Salvador - Alejandro Client Found", "FAIL", 
                            "Alejandro Mariscal not found in Salvador's clients")
                success = False
            
            self.log_test("Salvador Clients API", "PASS", 
                        f"Successfully retrieved {len(clients)} clients")
            
            return success
            
        except Exception as e:
            self.log_test("Clients Management Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_commission_schedule_salvador(self) -> bool:
        """TEST 5: Commission Schedule (Salvador)"""
        try:
            print("\n💰 Testing Commission Schedule (Salvador)...")
            
            if not self.salvador_token:
                self.log_test("Commission Schedule Setup", "FAIL", "Salvador token not available")
                return False
            
            headers = {'Authorization': f'Bearer {self.salvador_token}'}
            
            # GET /api/referral-agent/commissions/schedule
            schedule_response = requests.get(
                f"{self.base_url}/referral-agent/commissions/schedule",
                headers=headers,
                timeout=30
            )
            
            if schedule_response.status_code != 200:
                self.log_test("Salvador Commission Schedule API", "FAIL", 
                            f"Commission schedule API failed with HTTP {schedule_response.status_code}: {schedule_response.text}")
                return False
            
            schedule_data = schedule_response.json()
            commissions = schedule_data.get('commissions', [])
            
            success = True
            
            # Calculate total commissions
            total_commissions = sum(comm.get('amount', 0) for comm in commissions)
            expected_total = 3326.76
            
            if abs(total_commissions - expected_total) < 100:  # $100 tolerance
                self.log_test("Salvador Total Commissions", "PASS", 
                            f"Total commissions within expected range", 
                            f"~${expected_total:,.2f}", 
                            f"${total_commissions:,.2f}")
            else:
                self.log_test("Salvador Total Commissions", "FAIL", 
                            f"Total commissions outside expected range", 
                            f"~${expected_total:,.2f}", 
                            f"${total_commissions:,.2f}")
                success = False
            
            # Check payment status (paid/pending)
            paid_count = len([c for c in commissions if c.get('status') == 'paid'])
            pending_count = len([c for c in commissions if c.get('status') == 'pending'])
            
            self.log_test("Salvador Commission Status", "PASS", 
                        f"Commission status breakdown: {paid_count} paid, {pending_count} pending")
            
            # Verify client attribution
            client_attributions = set()
            for comm in commissions:
                client_id = comm.get('client_id')
                if client_id:
                    client_attributions.add(client_id)
            
            if client_attributions:
                self.log_test("Salvador Client Attribution", "PASS", 
                            f"Commissions attributed to {len(client_attributions)} clients")
            else:
                self.log_test("Salvador Client Attribution", "FAIL", 
                            "No client attribution found in commissions")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Commission Schedule Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_data_segregation_security(self) -> bool:
        """TEST 6: Data Segregation Security"""
        try:
            print("\n🔒 Testing Data Segregation Security...")
            
            if not self.salvador_token or not self.josselyn_token:
                self.log_test("Data Segregation Setup", "FAIL", "Both agent tokens not available")
                return False
            
            success = True
            
            # Test 1: Salvador should not see Josselyn's data
            salvador_headers = {'Authorization': f'Bearer {self.salvador_token}'}
            josselyn_headers = {'Authorization': f'Bearer {self.josselyn_token}'}
            
            # Get Salvador's dashboard data
            salvador_dashboard = requests.get(
                f"{self.base_url}/referral-agent/crm/dashboard",
                headers=salvador_headers,
                timeout=30
            )
            
            # Get Josselyn's dashboard data
            josselyn_dashboard = requests.get(
                f"{self.base_url}/referral-agent/crm/dashboard",
                headers=josselyn_headers,
                timeout=30
            )
            
            if salvador_dashboard.status_code == 200 and josselyn_dashboard.status_code == 200:
                salvador_data = salvador_dashboard.json()
                josselyn_data = josselyn_dashboard.json()
                
                # Salvador should have data, Josselyn should have empty state
                salvador_clients = salvador_data.get('clients_count', 0)
                josselyn_clients = josselyn_data.get('clients_count', 0)
                
                if salvador_clients > 0 and josselyn_clients == 0:
                    self.log_test("Data Segregation - Dashboard", "PASS", 
                                f"Salvador has {salvador_clients} clients, Josselyn has {josselyn_clients} (proper segregation)")
                else:
                    self.log_test("Data Segregation - Dashboard", "FAIL", 
                                f"Unexpected data distribution: Salvador {salvador_clients}, Josselyn {josselyn_clients}")
                    success = False
                
                # Check commission segregation
                salvador_commissions = salvador_data.get('total_commissions', 0)
                josselyn_commissions = josselyn_data.get('total_commissions', 0)
                
                if salvador_commissions > 0 and josselyn_commissions == 0:
                    self.log_test("Data Segregation - Commissions", "PASS", 
                                f"Salvador has ${salvador_commissions:,.2f}, Josselyn has ${josselyn_commissions:,.2f} (proper segregation)")
                else:
                    self.log_test("Data Segregation - Commissions", "FAIL", 
                                f"Unexpected commission distribution: Salvador ${salvador_commissions:,.2f}, Josselyn ${josselyn_commissions:,.2f}")
                    success = False
            else:
                self.log_test("Data Segregation Test", "FAIL", 
                            "Could not retrieve dashboard data for both agents")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Data Segregation Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_protected_routes(self) -> bool:
        """TEST 7: Protected Routes"""
        try:
            print("\n🛡️ Testing Protected Routes...")
            
            success = True
            
            # Test 1: No Token - GET /api/referral-agent/crm/dashboard
            no_token_response = requests.get(
                f"{self.base_url}/referral-agent/crm/dashboard",
                timeout=30
            )
            
            if no_token_response.status_code in [401, 403]:
                self.log_test("Protected Route - No Token", "PASS", 
                            f"Correctly rejected request without token (HTTP {no_token_response.status_code})")
            else:
                self.log_test("Protected Route - No Token", "FAIL", 
                            f"Should reject request without token, got HTTP {no_token_response.status_code}")
                success = False
            
            # Test 2: Invalid Token - GET /api/referral-agent/crm/dashboard
            invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
            invalid_token_response = requests.get(
                f"{self.base_url}/referral-agent/crm/dashboard",
                headers=invalid_headers,
                timeout=30
            )
            
            if invalid_token_response.status_code in [401, 403]:
                self.log_test("Protected Route - Invalid Token", "PASS", 
                            f"Correctly rejected request with invalid token (HTTP {invalid_token_response.status_code})")
            else:
                self.log_test("Protected Route - Invalid Token", "FAIL", 
                            f"Should reject request with invalid token, got HTTP {invalid_token_response.status_code}")
                success = False
            
            # Test 3: Malformed Token
            malformed_headers = {'Authorization': 'Bearer'}
            malformed_response = requests.get(
                f"{self.base_url}/referral-agent/crm/dashboard",
                headers=malformed_headers,
                timeout=30
            )
            
            if malformed_response.status_code in [401, 403]:
                self.log_test("Protected Route - Malformed Token", "PASS", 
                            f"Correctly rejected request with malformed token (HTTP {malformed_response.status_code})")
            else:
                self.log_test("Protected Route - Malformed Token", "FAIL", 
                            f"Should reject request with malformed token, got HTTP {malformed_response.status_code}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Protected Routes Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_token_validation(self) -> bool:
        """TEST 8: Token Validation"""
        try:
            print("\n🎫 Testing Token Validation...")
            
            if not self.salvador_token or not self.josselyn_token:
                self.log_test("Token Validation Setup", "FAIL", "Agent tokens not available")
                return False
            
            success = True
            
            # Test 1: GET /api/referral-agent/auth/me with Salvador's token
            salvador_headers = {'Authorization': f'Bearer {self.salvador_token}'}
            salvador_me_response = requests.get(
                f"{self.base_url}/referral-agent/auth/me",
                headers=salvador_headers,
                timeout=30
            )
            
            if salvador_me_response.status_code == 200:
                salvador_me_data = salvador_me_response.json()
                
                # Verify Salvador's agent info
                agent_name = salvador_me_data.get('name', '')
                agent_email = salvador_me_data.get('email', '')
                referral_code = salvador_me_data.get('referralCode', '')
                
                if 'salvador' in agent_name.lower() or 'palma' in agent_name.lower():
                    self.log_test("Salvador Token Validation - Name", "PASS", 
                                f"Correct agent name returned: {agent_name}")
                else:
                    self.log_test("Salvador Token Validation - Name", "FAIL", 
                                f"Unexpected agent name: {agent_name}")
                    success = False
                
                if agent_email == self.salvador_credentials['email']:
                    self.log_test("Salvador Token Validation - Email", "PASS", 
                                f"Correct email returned: {agent_email}")
                else:
                    self.log_test("Salvador Token Validation - Email", "FAIL", 
                                f"Email mismatch: expected {self.salvador_credentials['email']}, got {agent_email}")
                    success = False
                
                if referral_code:
                    self.log_test("Salvador Token Validation - Referral Code", "PASS", 
                                f"Referral code present: {referral_code}")
                else:
                    self.log_test("Salvador Token Validation - Referral Code", "FAIL", 
                                "No referral code returned")
                    success = False
            else:
                self.log_test("Salvador Token Validation", "FAIL", 
                            f"/me endpoint failed for Salvador: HTTP {salvador_me_response.status_code}")
                success = False
            
            # Test 2: GET /api/referral-agent/auth/me with Josselyn's token
            josselyn_headers = {'Authorization': f'Bearer {self.josselyn_token}'}
            josselyn_me_response = requests.get(
                f"{self.base_url}/referral-agent/auth/me",
                headers=josselyn_headers,
                timeout=30
            )
            
            if josselyn_me_response.status_code == 200:
                josselyn_me_data = josselyn_me_response.json()
                
                # Verify Josselyn's agent info
                agent_name = josselyn_me_data.get('name', '')
                agent_email = josselyn_me_data.get('email', '')
                
                if 'josselyn' in agent_name.lower() or 'arellano' in agent_name.lower():
                    self.log_test("Josselyn Token Validation - Name", "PASS", 
                                f"Correct agent name returned: {agent_name}")
                else:
                    self.log_test("Josselyn Token Validation - Name", "FAIL", 
                                f"Unexpected agent name: {agent_name}")
                    success = False
                
                if agent_email == self.josselyn_credentials['email']:
                    self.log_test("Josselyn Token Validation - Email", "PASS", 
                                f"Correct email returned: {agent_email}")
                else:
                    self.log_test("Josselyn Token Validation - Email", "FAIL", 
                                f"Email mismatch: expected {self.josselyn_credentials['email']}, got {agent_email}")
                    success = False
            else:
                self.log_test("Josselyn Token Validation", "FAIL", 
                            f"/me endpoint failed for Josselyn: HTTP {josselyn_me_response.status_code}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Token Validation Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_logout(self) -> bool:
        """TEST 9: Logout"""
        try:
            print("\n🚪 Testing Logout...")
            
            if not self.salvador_token:
                self.log_test("Logout Setup", "FAIL", "Salvador token not available")
                return False
            
            success = True
            
            # Test 1: POST /api/referral-agent/auth/logout with valid token
            salvador_headers = {'Authorization': f'Bearer {self.salvador_token}'}
            logout_response = requests.post(
                f"{self.base_url}/referral-agent/auth/logout",
                headers=salvador_headers,
                timeout=30
            )
            
            if logout_response.status_code == 200:
                self.log_test("Salvador Logout", "PASS", "Successfully logged out Salvador")
                
                # Test 2: Subsequent requests with same token should fail
                test_response = requests.get(
                    f"{self.base_url}/referral-agent/crm/dashboard",
                    headers=salvador_headers,
                    timeout=30
                )
                
                if test_response.status_code in [401, 403]:
                    self.log_test("Post-Logout Token Invalidation", "PASS", 
                                f"Token correctly invalidated after logout (HTTP {test_response.status_code})")
                else:
                    self.log_test("Post-Logout Token Invalidation", "FAIL", 
                                f"Token still valid after logout: HTTP {test_response.status_code}")
                    success = False
            else:
                self.log_test("Salvador Logout", "FAIL", 
                            f"Logout failed: HTTP {logout_response.status_code}: {logout_response.text}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("Logout Test", "ERROR", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all Referral Agent Portal tests"""
        print("🚀 Starting Referral Agent Portal Comprehensive Testing")
        print("=" * 80)
        print(f"Portal URL: https://viking-trade-dash-1.preview.emergentagent.com/referral-agent/login")
        print(f"Production API: {self.base_url}")
        print("=" * 80)
        
        # Define all tests
        tests = [
            ("Salvador Palma Login & Dashboard", self.test_salvador_login_dashboard),
            ("Josselyn Arellano López Login & Dashboard", self.test_josselyn_login_dashboard),
            ("Leads Management (Salvador)", self.test_leads_management_salvador),
            ("Clients Management (Salvador)", self.test_clients_management_salvador),
            ("Commission Schedule (Salvador)", self.test_commission_schedule_salvador),
            ("Data Segregation Security", self.test_data_segregation_security),
            ("Protected Routes", self.test_protected_routes),
            ("Token Validation", self.test_token_validation),
            ("Logout", self.test_logout)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*60}")
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(f"{test_name} Exception", "ERROR", f"Test failed with exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 REFERRAL AGENT PORTAL TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Determine overall status
        if success_rate >= 90:
            status = "✅ All tests passed - ready for production"
        elif success_rate >= 70:
            status = "⚠️ Minor issues found - review needed"
        else:
            status = "❌ Critical failures - rollback needed"
        
        print(f"Overall Status: {status}")
        
        # Print detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test_name']}: {result['details']}")
            
            if result.get("expected") and result.get("actual"):
                print(f"   Expected: {result['expected']}")
                print(f"   Actual: {result['actual']}")
        
        print("\n" + "=" * 80)
        
        # Critical success criteria check
        critical_tests = [
            "Salvador Login", "Josselyn Login", "Salvador - Alejandro Client Found",
            "Salvador - Client Investments", "Salvador Total Commissions",
            "Data Segregation - Dashboard", "Protected Route - No Token"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if any(critical in result['test_name'] for critical in critical_tests) 
                            and result['status'] == 'PASS')
        
        print(f"Critical Tests Passed: {critical_passed}/{len(critical_tests)}")
        
        if critical_passed == len(critical_tests):
            print("🎉 PORTAL IS PRODUCTION-READY!")
            print("✅ Both agents can login successfully")
            print("✅ Salvador sees Alejandro's data correctly")
            print("✅ Data segregation enforced")
            print("✅ Protected routes working")
            return True
        else:
            print("🚨 CRITICAL ISSUES FOUND - PORTAL NOT READY")
            return False

def main():
    """Main test execution"""
    tester = ReferralAgentPortalTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()