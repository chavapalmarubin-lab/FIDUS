#!/usr/bin/env python3
"""
FIDUS MT5 Integration Assessment Test Suite
Comprehensive testing of current MT5 integration to identify gaps and opportunities for enhancement.

Focus Areas:
1. Backend MT5 Integration Assessment
2. Frontend MT5 Integration Assessment  
3. Integration Completeness Analysis
4. Production Readiness Review

Goal: Provide comprehensive assessment of current MT5 integration status and create enhancement roadmap.
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class MT5IntegrationAssessmentTester:
    def __init__(self, base_url="https://fidus-invest.emergent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_user = None
        self.client_user = None
        self.assessment_results = {
            "backend_mt5": {"working": [], "missing": [], "issues": []},
            "frontend_mt5": {"working": [], "missing": [], "issues": []},
            "integration_completeness": {"complete": [], "incomplete": [], "missing": []},
            "production_readiness": {"ready": [], "needs_work": [], "critical_issues": []}
        }
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

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
        """Setup admin and client authentication"""
        print("\n" + "="*80)
        print("🔐 SETTING UP AUTHENTICATION")
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
            print("   ❌ Admin login failed - cannot proceed with admin tests")
            return False

        # Test client login (Salvador Palma)
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
            print("   ❌ Client login failed - cannot proceed with client tests")
            return False
            
        return True

    def assess_backend_mt5_integration(self) -> bool:
        """1. Backend MT5 Integration Assessment"""
        print("\n" + "="*80)
        print("🔧 1. BACKEND MT5 INTEGRATION ASSESSMENT")
        print("="*80)
        
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }
        
        client_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.client_user.get('token')}"
        }
        
        client_id = self.client_user.get('id')
        
        # Test MT5 Bridge Health Check
        print("\n📊 Testing MT5 Bridge Health Check")
        success, response = self.run_test(
            "MT5 Bridge Health Check",
            "GET",
            "api/mt5/bridge/health",
            200,
            headers=admin_headers
        )
        
        if success:
            bridge_health = response.get('bridge_health', {})
            if bridge_health.get('success'):
                self.assessment_results["backend_mt5"]["working"].append("MT5 Bridge Health Check - Bridge Accessible")
            else:
                self.assessment_results["backend_mt5"]["issues"].append(f"MT5 Bridge Health Check - Bridge Unreachable: {bridge_health.get('error')}")
        else:
            self.assessment_results["backend_mt5"]["missing"].append("MT5 Bridge Health Check - Endpoint Not Working")

        # Test MT5 Client Accounts Endpoint
        print("\n📊 Testing MT5 Client Accounts")
        success, response = self.run_test(
            "Get Client MT5 Accounts",
            "GET",
            f"api/mt5/client/{client_id}/accounts",
            200,
            headers=client_headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            summary = response.get('summary', {})
            self.assessment_results["backend_mt5"]["working"].append(f"Client MT5 Accounts - {len(accounts)} accounts found")
            
            if accounts:
                # Check account structure
                account = accounts[0]
                required_fields = ['account_id', 'mt5_login', 'broker_code', 'broker_name', 'mt5_server', 'fund_code']
                missing_fields = [field for field in required_fields if field not in account]
                
                if missing_fields:
                    self.assessment_results["backend_mt5"]["issues"].append(f"MT5 Account Structure - Missing fields: {missing_fields}")
                else:
                    self.assessment_results["backend_mt5"]["working"].append("MT5 Account Structure - All required fields present")
        else:
            self.assessment_results["backend_mt5"]["missing"].append("Client MT5 Accounts - Endpoint Not Working")

        # Test MT5 Admin Accounts Overview
        print("\n📊 Testing MT5 Admin Accounts Overview")
        success, response = self.run_test(
            "Get MT5 Admin Accounts Overview",
            "GET",
            "api/mt5/admin/accounts",
            200,
            headers=admin_headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            summary = response.get('summary', {})
            self.assessment_results["backend_mt5"]["working"].append(f"Admin MT5 Accounts Overview - {len(accounts)} accounts, Summary: {summary}")
        else:
            self.assessment_results["backend_mt5"]["missing"].append("Admin MT5 Accounts Overview - Endpoint Not Working")

        # Test MT5 Performance Overview
        print("\n📊 Testing MT5 Performance Overview")
        success, response = self.run_test(
            "Get MT5 Performance Overview",
            "GET",
            "api/mt5/admin/performance/overview",
            200,
            headers=admin_headers
        )
        
        if success:
            overview = response.get('overview', {})
            required_fields = ['total_accounts', 'total_allocated', 'total_equity', 'total_profit_loss']
            missing_fields = [field for field in required_fields if field not in overview]
            
            if missing_fields:
                self.assessment_results["backend_mt5"]["issues"].append(f"MT5 Performance Overview - Missing fields: {missing_fields}")
            else:
                self.assessment_results["backend_mt5"]["working"].append("MT5 Performance Overview - Complete structure")
        else:
            self.assessment_results["backend_mt5"]["missing"].append("MT5 Performance Overview - Endpoint Not Working")

        # Test MT5 Brokers List
        print("\n📊 Testing MT5 Brokers List")
        success, response = self.run_test(
            "Get MT5 Brokers",
            "GET",
            "api/mt5/brokers",
            200,
            headers=admin_headers
        )
        
        if success:
            brokers = response.get('brokers', [])
            self.assessment_results["backend_mt5"]["working"].append(f"MT5 Brokers List - {len(brokers)} brokers available")
            
            # Check broker structure
            if brokers:
                broker = brokers[0]
                required_fields = ['code', 'name', 'servers']
                missing_fields = [field for field in required_fields if field not in broker]
                
                if missing_fields:
                    self.assessment_results["backend_mt5"]["issues"].append(f"MT5 Broker Structure - Missing fields: {missing_fields}")
                else:
                    self.assessment_results["backend_mt5"]["working"].append("MT5 Broker Structure - Complete")
        else:
            self.assessment_results["backend_mt5"]["missing"].append("MT5 Brokers List - Endpoint Not Working")

        # Test MT5 System Status
        print("\n📊 Testing MT5 System Status")
        success, response = self.run_test(
            "Get MT5 System Status",
            "GET",
            "api/mt5/admin/system-status",
            200,
            headers=admin_headers
        )
        
        if success:
            status = response.get('status', {})
            self.assessment_results["backend_mt5"]["working"].append(f"MT5 System Status - Available: {status}")
        else:
            self.assessment_results["backend_mt5"]["missing"].append("MT5 System Status - Endpoint Not Working")

        # Test MT5 Manual Account Addition
        print("\n📊 Testing MT5 Manual Account Addition")
        success, response = self.run_test(
            "Add Manual MT5 Account",
            "POST",
            "api/mt5/admin/add-manual-account",
            200,
            data={
                "client_id": client_id,
                "mt5_login": 12345678,
                "mt5_password": "TestPass123!",
                "mt5_server": "Multibank-Demo",
                "broker_code": "multibank",
                "fund_code": "CORE"
            },
            headers=admin_headers
        )
        
        if success:
            self.assessment_results["backend_mt5"]["working"].append("MT5 Manual Account Addition - Working")
        else:
            self.assessment_results["backend_mt5"]["issues"].append("MT5 Manual Account Addition - Failed (may be expected with bridge unreachable)")

        # Test MT5 Credentials Update
        print("\n📊 Testing MT5 Credentials Update")
        success, response = self.run_test(
            "Update MT5 Credentials",
            "POST",
            "api/mt5/admin/credentials/update",
            404,  # Expect 404 for non-existent account
            data={
                "client_id": client_id,
                "fund_code": "CORE",
                "mt5_login": 87654321,
                "mt5_password": "UpdatedPass123!",
                "mt5_server": "Updated-Server"
            },
            headers=admin_headers
        )
        
        if success:
            self.assessment_results["backend_mt5"]["working"].append("MT5 Credentials Update - Proper error handling")
        else:
            self.assessment_results["backend_mt5"]["issues"].append("MT5 Credentials Update - Unexpected behavior")

        return True

    def assess_frontend_mt5_integration(self) -> bool:
        """2. Frontend MT5 Integration Assessment"""
        print("\n" + "="*80)
        print("🖥️ 2. FRONTEND MT5 INTEGRATION ASSESSMENT")
        print("="*80)
        
        # Note: Since we're testing backend APIs, we'll assess frontend integration
        # by checking if the backend provides the necessary data structures
        # that frontend components would need
        
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }
        
        client_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.client_user.get('token')}"
        }
        
        client_id = self.client_user.get('id')
        
        # Test data structure for MetaQuotesData component
        print("\n📊 Testing Data for MetaQuotesData Component")
        success, response = self.run_test(
            "MT5 Realtime Data (for MetaQuotesData)",
            "GET",
            "api/mt5/admin/realtime-data",
            200,
            headers=admin_headers
        )
        
        if success:
            realtime_data = response.get('realtime_data', {})
            if 'quotes' in realtime_data or 'symbols' in realtime_data:
                self.assessment_results["frontend_mt5"]["working"].append("MetaQuotesData - Backend provides realtime data structure")
            else:
                self.assessment_results["frontend_mt5"]["issues"].append("MetaQuotesData - Backend data structure incomplete")
        else:
            self.assessment_results["frontend_mt5"]["missing"].append("MetaQuotesData - Backend endpoint not working")

        # Test data structure for ClientMT5View component
        print("\n📊 Testing Data for ClientMT5View Component")
        success, response = self.run_test(
            "Client MT5 Performance (for ClientMT5View)",
            "GET",
            f"api/mt5/client/{client_id}/performance",
            200,
            headers=client_headers
        )
        
        if success:
            summary = response.get('summary', {})
            accounts = summary.get('accounts', [])
            
            # Check if data structure supports client MT5 view
            required_fields = ['total_allocated', 'total_equity', 'total_profit_loss']
            missing_fields = [field for field in required_fields if field not in summary]
            
            if missing_fields:
                self.assessment_results["frontend_mt5"]["issues"].append(f"ClientMT5View - Missing summary fields: {missing_fields}")
            else:
                self.assessment_results["frontend_mt5"]["working"].append("ClientMT5View - Backend provides complete performance data")
                
            if accounts:
                account = accounts[0]
                account_fields = ['account_id', 'mt5_login', 'broker_name', 'profit_loss', 'profit_loss_percentage']
                missing_account_fields = [field for field in account_fields if field not in account]
                
                if missing_account_fields:
                    self.assessment_results["frontend_mt5"]["issues"].append(f"ClientMT5View - Missing account fields: {missing_account_fields}")
                else:
                    self.assessment_results["frontend_mt5"]["working"].append("ClientMT5View - Backend provides complete account data")
        else:
            self.assessment_results["frontend_mt5"]["missing"].append("ClientMT5View - Backend endpoint not working")

        # Test data structure for Admin MT5 Management
        print("\n📊 Testing Data for Admin MT5 Management Interface")
        success, response = self.run_test(
            "MT5 Accounts by Broker (for Admin Management)",
            "GET",
            "api/mt5/admin/accounts/by-broker",
            200,
            headers=admin_headers
        )
        
        if success:
            brokers = response.get('brokers', {})
            if brokers:
                self.assessment_results["frontend_mt5"]["working"].append("Admin MT5 Management - Backend provides broker-grouped data")
            else:
                self.assessment_results["frontend_mt5"]["issues"].append("Admin MT5 Management - Backend data structure incomplete")
        else:
            self.assessment_results["frontend_mt5"]["missing"].append("Admin MT5 Management - Backend endpoint not working")

        # Test CRM MT5 Integration endpoints
        print("\n📊 Testing CRM MT5 Integration Endpoints")
        crm_mt5_endpoints = [
            ("CRM Client MT5 Account", f"api/crm/mt5/client/{client_id}/account"),
            ("CRM Client MT5 Positions", f"api/crm/mt5/client/{client_id}/positions"),
            ("CRM Client MT5 History", f"api/crm/mt5/client/{client_id}/history"),
            ("CRM Admin MT5 Overview", "api/crm/mt5/admin/overview")
        ]
        
        for endpoint_name, endpoint_url in crm_mt5_endpoints:
            success, response = self.run_test(
                endpoint_name,
                "GET",
                endpoint_url,
                200,
                headers=admin_headers
            )
            
            if success:
                self.assessment_results["frontend_mt5"]["working"].append(f"{endpoint_name} - Available")
            else:
                self.assessment_results["frontend_mt5"]["missing"].append(f"{endpoint_name} - Not working")

        return True

    def assess_integration_completeness(self) -> bool:
        """3. Integration Completeness Analysis"""
        print("\n" + "="*80)
        print("🔗 3. INTEGRATION COMPLETENESS ANALYSIS")
        print("="*80)
        
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }
        
        client_id = self.client_user.get('id')
        
        # Test Investment-MT5 Integration
        print("\n📊 Testing Investment-MT5 Integration")
        
        # Create test investment to see if MT5 account is created
        success, response = self.run_test(
            "Create Investment (MT5 Integration Test)",
            "POST",
            "api/investments/create",
            200,
            data={
                "client_id": client_id,
                "fund_code": "CORE",
                "amount": 25000.0,
                "deposit_date": "2024-12-19"
            },
            headers=admin_headers
        )
        
        if success:
            investment_id = response.get('investment_id')
            if investment_id:
                self.assessment_results["integration_completeness"]["complete"].append("Investment Creation - Successfully creates investments")
                
                # Check if MT5 account was created/updated
                success2, response2 = self.run_test(
                    "Check MT5 Account After Investment",
                    "GET",
                    f"api/mt5/client/{client_id}/accounts",
                    200,
                    headers=admin_headers
                )
                
                if success2:
                    accounts = response2.get('accounts', [])
                    core_accounts = [acc for acc in accounts if acc.get('fund_code') == 'CORE']
                    
                    if core_accounts:
                        self.assessment_results["integration_completeness"]["complete"].append("Investment-MT5 Integration - MT5 accounts created for investments")
                    else:
                        self.assessment_results["integration_completeness"]["incomplete"].append("Investment-MT5 Integration - No MT5 accounts found for CORE fund")
                else:
                    self.assessment_results["integration_completeness"]["incomplete"].append("Investment-MT5 Integration - Cannot verify MT5 account creation")
            else:
                self.assessment_results["integration_completeness"]["incomplete"].append("Investment Creation - No investment ID returned")
        else:
            self.assessment_results["integration_completeness"]["missing"].append("Investment Creation - Failed")

        # Test MT5 Historical Data Integration
        print("\n📊 Testing MT5 Historical Data Integration")
        success, response = self.run_test(
            "MT5 Historical Data",
            "GET",
            "api/mt5/admin/historical-data/test_account_id",
            404,  # Expect 404 for non-existent account
            headers=admin_headers
        )
        
        if success:
            self.assessment_results["integration_completeness"]["complete"].append("MT5 Historical Data - Endpoint available with proper error handling")
        else:
            self.assessment_results["integration_completeness"]["incomplete"].append("MT5 Historical Data - Endpoint behavior unexpected")

        # Test MT5 Position Tracking
        print("\n📊 Testing MT5 Position Tracking")
        success, response = self.run_test(
            "MT5 Account Positions",
            "GET",
            "api/mt5/admin/account/test_account_id/positions",
            404,  # Expect 404 for non-existent account
            headers=admin_headers
        )
        
        if success:
            self.assessment_results["integration_completeness"]["complete"].append("MT5 Position Tracking - Endpoint available")
        else:
            self.assessment_results["integration_completeness"]["incomplete"].append("MT5 Position Tracking - Endpoint not working")

        # Test MT5 Account Activity
        print("\n📊 Testing MT5 Account Activity")
        success, response = self.run_test(
            "MT5 Account Activity",
            "GET",
            "api/mt5/admin/account/test_account_id/activity",
            404,  # Expect 404 for non-existent account
            headers=admin_headers
        )
        
        if success:
            self.assessment_results["integration_completeness"]["complete"].append("MT5 Account Activity - Endpoint available")
        else:
            self.assessment_results["integration_completeness"]["incomplete"].append("MT5 Account Activity - Endpoint not working")

        # Test MT5 Account Disconnect
        print("\n📊 Testing MT5 Account Management")
        success, response = self.run_test(
            "MT5 Account Disconnect",
            "POST",
            "api/mt5/admin/account/test_account_id/disconnect",
            404,  # Expect 404 for non-existent account
            headers=admin_headers
        )
        
        if success:
            self.assessment_results["integration_completeness"]["complete"].append("MT5 Account Management - Disconnect functionality available")
        else:
            self.assessment_results["integration_completeness"]["incomplete"].append("MT5 Account Management - Disconnect functionality not working")

        return True

    def assess_production_readiness(self) -> bool:
        """4. Production Readiness Review"""
        print("\n" + "="*80)
        print("🚀 4. PRODUCTION READINESS REVIEW")
        print("="*80)
        
        admin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.admin_user.get('token')}"
        }
        
        # Test Error Handling and Fallback Behavior
        print("\n📊 Testing Error Handling and Fallback Behavior")
        
        # Test with invalid client ID
        success, response = self.run_test(
            "Error Handling - Invalid Client ID",
            "GET",
            "api/mt5/client/invalid_client_id/accounts",
            200,  # Should return empty results, not error
            headers=admin_headers
        )
        
        if success:
            accounts = response.get('accounts', [])
            if len(accounts) == 0:
                self.assessment_results["production_readiness"]["ready"].append("Error Handling - Invalid client ID handled gracefully")
            else:
                self.assessment_results["production_readiness"]["needs_work"].append("Error Handling - Invalid client ID returns unexpected data")
        else:
            self.assessment_results["production_readiness"]["needs_work"].append("Error Handling - Invalid client ID not handled properly")

        # Test Authentication Requirements
        print("\n📊 Testing Authentication and Security")
        
        # Test without authentication
        success, response = self.run_test(
            "Security - Unauthenticated Access",
            "GET",
            "api/mt5/admin/accounts",
            401,  # Should require authentication
        )
        
        if success:
            self.assessment_results["production_readiness"]["ready"].append("Security - Admin endpoints require authentication")
        else:
            self.assessment_results["production_readiness"]["critical_issues"].append("Security - Admin endpoints accessible without authentication")

        # Test client access to admin endpoints
        client_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.client_user.get('token')}"
        }
        
        success, response = self.run_test(
            "Security - Client Access to Admin Endpoints",
            "GET",
            "api/mt5/admin/accounts",
            403,  # Should be forbidden for clients
            headers=client_headers
        )
        
        if success:
            self.assessment_results["production_readiness"]["ready"].append("Security - Admin endpoints properly restricted from clients")
        else:
            self.assessment_results["production_readiness"]["critical_issues"].append("Security - Clients can access admin endpoints")

        # Test Logging and Monitoring
        print("\n📊 Testing Logging and Monitoring Capabilities")
        
        # Check if system status provides monitoring data
        success, response = self.run_test(
            "Monitoring - System Status",
            "GET",
            "api/mt5/admin/system-status",
            200,
            headers=admin_headers
        )
        
        if success:
            status = response.get('status', {})
            if 'bridge_status' in status or 'last_sync' in status:
                self.assessment_results["production_readiness"]["ready"].append("Monitoring - System status provides monitoring data")
            else:
                self.assessment_results["production_readiness"]["needs_work"].append("Monitoring - System status lacks monitoring details")
        else:
            self.assessment_results["production_readiness"]["needs_work"].append("Monitoring - System status endpoint not working")

        # Test Configuration Management
        print("\n📊 Testing Configuration Management")
        
        # Check if brokers and servers are configurable
        success, response = self.run_test(
            "Configuration - Broker Management",
            "GET",
            "api/mt5/brokers",
            200,
            headers=admin_headers
        )
        
        if success:
            brokers = response.get('brokers', [])
            if len(brokers) > 1:
                self.assessment_results["production_readiness"]["ready"].append("Configuration - Multiple brokers supported")
            else:
                self.assessment_results["production_readiness"]["needs_work"].append("Configuration - Limited broker support")
                
            # Check server configuration
            if brokers:
                broker = brokers[0]
                servers = broker.get('servers', [])
                if len(servers) > 1:
                    self.assessment_results["production_readiness"]["ready"].append("Configuration - Multiple servers per broker supported")
                else:
                    self.assessment_results["production_readiness"]["needs_work"].append("Configuration - Limited server options")
        else:
            self.assessment_results["production_readiness"]["needs_work"].append("Configuration - Broker configuration not accessible")

        return True

    def generate_enhancement_roadmap(self) -> Dict[str, Any]:
        """Generate enhancement roadmap based on assessment results"""
        roadmap = {
            "immediate_priorities": [],
            "short_term_enhancements": [],
            "long_term_improvements": [],
            "production_blockers": []
        }
        
        # Analyze results and categorize improvements
        
        # Critical issues become production blockers
        if self.assessment_results["production_readiness"]["critical_issues"]:
            roadmap["production_blockers"].extend(self.assessment_results["production_readiness"]["critical_issues"])
        
        # Missing backend functionality becomes immediate priorities
        if self.assessment_results["backend_mt5"]["missing"]:
            roadmap["immediate_priorities"].extend([f"Backend: {item}" for item in self.assessment_results["backend_mt5"]["missing"]])
        
        # Backend issues become short-term enhancements
        if self.assessment_results["backend_mt5"]["issues"]:
            roadmap["short_term_enhancements"].extend([f"Backend: {item}" for item in self.assessment_results["backend_mt5"]["issues"]])
        
        # Frontend missing functionality
        if self.assessment_results["frontend_mt5"]["missing"]:
            roadmap["immediate_priorities"].extend([f"Frontend: {item}" for item in self.assessment_results["frontend_mt5"]["missing"]])
        
        # Frontend issues
        if self.assessment_results["frontend_mt5"]["issues"]:
            roadmap["short_term_enhancements"].extend([f"Frontend: {item}" for item in self.assessment_results["frontend_mt5"]["issues"]])
        
        # Integration completeness
        if self.assessment_results["integration_completeness"]["missing"]:
            roadmap["immediate_priorities"].extend([f"Integration: {item}" for item in self.assessment_results["integration_completeness"]["missing"]])
        
        if self.assessment_results["integration_completeness"]["incomplete"]:
            roadmap["short_term_enhancements"].extend([f"Integration: {item}" for item in self.assessment_results["integration_completeness"]["incomplete"]])
        
        # Production readiness
        if self.assessment_results["production_readiness"]["needs_work"]:
            roadmap["long_term_improvements"].extend([f"Production: {item}" for item in self.assessment_results["production_readiness"]["needs_work"]])
        
        return roadmap

    def run_comprehensive_assessment(self) -> bool:
        """Run comprehensive MT5 integration assessment"""
        print("\n" + "="*100)
        print("🚀 STARTING COMPREHENSIVE MT5 INTEGRATION ASSESSMENT")
        print("="*100)
        print("Goal: Assess current MT5 integration and identify enhancement opportunities")
        print("="*100)
        
        # Setup authentication
        if not self.setup_authentication():
            print("\n❌ Authentication setup failed - cannot proceed")
            return False
        
        # Run assessment phases
        assessment_phases = [
            ("Backend MT5 Integration Assessment", self.assess_backend_mt5_integration),
            ("Frontend MT5 Integration Assessment", self.assess_frontend_mt5_integration),
            ("Integration Completeness Analysis", self.assess_integration_completeness),
            ("Production Readiness Review", self.assess_production_readiness)
        ]
        
        phase_results = []
        
        for phase_name, phase_method in assessment_phases:
            print(f"\n🔄 Running {phase_name}...")
            try:
                result = phase_method()
                phase_results.append((phase_name, result))
                
                if result:
                    print(f"✅ {phase_name} - COMPLETED")
                else:
                    print(f"❌ {phase_name} - FAILED")
            except Exception as e:
                print(f"❌ {phase_name} - ERROR: {str(e)}")
                phase_results.append((phase_name, False))
        
        # Generate enhancement roadmap
        roadmap = self.generate_enhancement_roadmap()
        
        # Print comprehensive results
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE MT5 INTEGRATION ASSESSMENT RESULTS")
        print("="*100)
        
        # Backend Assessment Results
        print("\n🔧 BACKEND MT5 INTEGRATION:")
        print(f"   ✅ Working: {len(self.assessment_results['backend_mt5']['working'])} items")
        for item in self.assessment_results['backend_mt5']['working']:
            print(f"      • {item}")
        
        print(f"   ❌ Missing: {len(self.assessment_results['backend_mt5']['missing'])} items")
        for item in self.assessment_results['backend_mt5']['missing']:
            print(f"      • {item}")
        
        print(f"   ⚠️ Issues: {len(self.assessment_results['backend_mt5']['issues'])} items")
        for item in self.assessment_results['backend_mt5']['issues']:
            print(f"      • {item}")
        
        # Frontend Assessment Results
        print("\n🖥️ FRONTEND MT5 INTEGRATION:")
        print(f"   ✅ Working: {len(self.assessment_results['frontend_mt5']['working'])} items")
        for item in self.assessment_results['frontend_mt5']['working']:
            print(f"      • {item}")
        
        print(f"   ❌ Missing: {len(self.assessment_results['frontend_mt5']['missing'])} items")
        for item in self.assessment_results['frontend_mt5']['missing']:
            print(f"      • {item}")
        
        print(f"   ⚠️ Issues: {len(self.assessment_results['frontend_mt5']['issues'])} items")
        for item in self.assessment_results['frontend_mt5']['issues']:
            print(f"      • {item}")
        
        # Integration Completeness Results
        print("\n🔗 INTEGRATION COMPLETENESS:")
        print(f"   ✅ Complete: {len(self.assessment_results['integration_completeness']['complete'])} items")
        for item in self.assessment_results['integration_completeness']['complete']:
            print(f"      • {item}")
        
        print(f"   ⚠️ Incomplete: {len(self.assessment_results['integration_completeness']['incomplete'])} items")
        for item in self.assessment_results['integration_completeness']['incomplete']:
            print(f"      • {item}")
        
        print(f"   ❌ Missing: {len(self.assessment_results['integration_completeness']['missing'])} items")
        for item in self.assessment_results['integration_completeness']['missing']:
            print(f"      • {item}")
        
        # Production Readiness Results
        print("\n🚀 PRODUCTION READINESS:")
        print(f"   ✅ Ready: {len(self.assessment_results['production_readiness']['ready'])} items")
        for item in self.assessment_results['production_readiness']['ready']:
            print(f"      • {item}")
        
        print(f"   ⚠️ Needs Work: {len(self.assessment_results['production_readiness']['needs_work'])} items")
        for item in self.assessment_results['production_readiness']['needs_work']:
            print(f"      • {item}")
        
        print(f"   🚨 Critical Issues: {len(self.assessment_results['production_readiness']['critical_issues'])} items")
        for item in self.assessment_results['production_readiness']['critical_issues']:
            print(f"      • {item}")
        
        # Enhancement Roadmap
        print("\n" + "="*100)
        print("🗺️ MT5 INTEGRATION ENHANCEMENT ROADMAP")
        print("="*100)
        
        print(f"\n🚨 PRODUCTION BLOCKERS ({len(roadmap['production_blockers'])} items):")
        for item in roadmap['production_blockers']:
            print(f"   • {item}")
        
        print(f"\n🔥 IMMEDIATE PRIORITIES ({len(roadmap['immediate_priorities'])} items):")
        for item in roadmap['immediate_priorities']:
            print(f"   • {item}")
        
        print(f"\n📈 SHORT-TERM ENHANCEMENTS ({len(roadmap['short_term_enhancements'])} items):")
        for item in roadmap['short_term_enhancements']:
            print(f"   • {item}")
        
        print(f"\n🔮 LONG-TERM IMPROVEMENTS ({len(roadmap['long_term_improvements'])} items):")
        for item in roadmap['long_term_improvements']:
            print(f"   • {item}")
        
        # Overall Assessment
        total_working = (len(self.assessment_results['backend_mt5']['working']) + 
                        len(self.assessment_results['frontend_mt5']['working']) + 
                        len(self.assessment_results['integration_completeness']['complete']) + 
                        len(self.assessment_results['production_readiness']['ready']))
        
        total_issues = (len(self.assessment_results['backend_mt5']['missing']) + 
                       len(self.assessment_results['backend_mt5']['issues']) + 
                       len(self.assessment_results['frontend_mt5']['missing']) + 
                       len(self.assessment_results['frontend_mt5']['issues']) + 
                       len(self.assessment_results['integration_completeness']['incomplete']) + 
                       len(self.assessment_results['integration_completeness']['missing']) + 
                       len(self.assessment_results['production_readiness']['needs_work']) + 
                       len(self.assessment_results['production_readiness']['critical_issues']))
        
        total_items = total_working + total_issues
        completion_percentage = (total_working / total_items * 100) if total_items > 0 else 0
        
        print(f"\n📈 Overall Assessment:")
        print(f"   Individual Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        print(f"   MT5 Integration Completeness: {completion_percentage:.1f}%")
        print(f"   Working Features: {total_working}")
        print(f"   Issues to Address: {total_issues}")
        
        # Determine overall success
        overall_success = (completion_percentage >= 70 and 
                          len(self.assessment_results['production_readiness']['critical_issues']) == 0)
        
        if overall_success:
            print(f"\n🎉 MT5 INTEGRATION ASSESSMENT COMPLETED SUCCESSFULLY!")
            print("   Current MT5 integration is functional with room for enhancement.")
        else:
            print(f"\n⚠️ MT5 INTEGRATION ASSESSMENT COMPLETED WITH SIGNIFICANT GAPS")
            print("   MT5 integration needs substantial work before production readiness.")
        
        return overall_success

def main():
    """Main test execution"""
    print("🔧 FIDUS MT5 Integration Assessment Suite")
    print("Comprehensive assessment of current MT5 integration status")
    print("Focus: Backend, Frontend, Integration Completeness, Production Readiness")
    
    tester = MT5IntegrationAssessmentTester()
    
    try:
        success = tester.run_comprehensive_assessment()
        
        if success:
            print("\n✅ MT5 Integration Assessment completed successfully!")
            print("   System shows good MT5 integration foundation with enhancement opportunities")
            sys.exit(0)
        else:
            print("\n❌ MT5 Integration Assessment reveals significant gaps!")
            print("   System needs substantial MT5 integration work")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Assessment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Assessment failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()