#!/usr/bin/env python3
"""
URGENT DEMO ISSUE: Investment Creation Endpoint Testing
Test the specific investment creation workflow that's failing during the live demo
"""

import requests
import json
import sys
from datetime import datetime

class UrgentInvestmentTester:
    def __init__(self, base_url="https://fidus-workspace-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.errors_found = []
        
    def log_error(self, error_msg):
        """Log errors for detailed reporting"""
        self.errors_found.append(error_msg)
        print(f"🚨 ERROR: {error_msg}")
    
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test with detailed error reporting"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 {name}")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
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
            
            # Always show response content for debugging
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response Text: {response.text}")
                response_data = {}
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED")
                return True, response_data
            else:
                error_msg = f"{name} - Expected {expected_status}, got {response.status_code}"
                self.log_error(error_msg)
                print(f"❌ FAILED - {error_msg}")
                return False, response_data

        except Exception as e:
            error_msg = f"{name} - Exception: {str(e)}"
            self.log_error(error_msg)
            print(f"❌ FAILED - {error_msg}")
            return False, {}

    def test_investment_creation_urgent(self):
        """Test the exact investment creation scenario from the demo"""
        print("\n" + "="*80)
        print("🚨 URGENT DEMO ISSUE: Testing Investment Creation Endpoint")
        print("="*80)
        
        # Sample data from the review request
        sample_data = {
            "client_id": "client_001",
            "fund_code": "CORE", 
            "amount": 25000,
            "payment_method": "wire_transfer"
        }
        
        print(f"\n📋 Testing with EXACT sample data from demo:")
        print(f"   Client ID: {sample_data['client_id']}")
        print(f"   Fund Code: {sample_data['fund_code']}")
        print(f"   Amount: ${sample_data['amount']:,}")
        print(f"   Payment Method: {sample_data['payment_method']}")
        
        success, response = self.run_test(
            "🎯 CRITICAL: Investment Creation with Demo Data",
            "POST",
            "api/investments/create",
            200,
            data=sample_data
        )
        
        if not success:
            print(f"\n🚨 INVESTMENT CREATION FAILED!")
            print(f"   This is the exact error the demo user is experiencing!")
            
            # Check for specific error patterns
            if response:
                error_detail = response.get('detail', '')
                error_message = response.get('message', '')
                
                if 'client' in error_detail.lower() or 'client' in error_message.lower():
                    self.log_error("CLIENT DATA ISSUE: Problem with client_001 data")
                
                if 'fund' in error_detail.lower() or 'fund' in error_message.lower():
                    self.log_error("FUND CONFIGURATION ISSUE: Problem with CORE fund setup")
                
                if 'minimum' in error_detail.lower() or 'minimum' in error_message.lower():
                    self.log_error("MINIMUM INVESTMENT ISSUE: $25,000 may be below minimum")
                
                if 'readiness' in error_detail.lower() or 'readiness' in error_message.lower():
                    self.log_error("CLIENT READINESS ISSUE: Client may not be investment-ready")
                
                if 'database' in error_detail.lower() or 'mongodb' in error_detail.lower():
                    self.log_error("DATABASE ISSUE: MongoDB connection or data problem")
        
        return success

    def test_client_data_dependencies(self):
        """Test if client_001 exists and has proper data"""
        print(f"\n🔍 Checking Client Dependencies...")
        
        # Test 1: Check if client exists
        success, response = self.run_test(
            "Check Client Exists (client_001)",
            "GET",
            "api/client/client_001/data",
            200
        )
        
        if not success:
            self.log_error("CLIENT NOT FOUND: client_001 does not exist or is not accessible")
            return False
        
        # Test 2: Check client readiness
        success, response = self.run_test(
            "Check Client Investment Readiness",
            "GET",
            "api/clients/client_001/readiness",
            200
        )
        
        if success:
            investment_ready = response.get('investment_ready', False)
            if not investment_ready:
                self.log_error("CLIENT NOT READY: client_001 is not marked as investment-ready")
                print(f"   Readiness Status: {response}")
        
        return True

    def test_fund_configuration_dependencies(self):
        """Test if CORE fund is properly configured"""
        print(f"\n🔍 Checking Fund Configuration Dependencies...")
        
        success, response = self.run_test(
            "Check Fund Configuration",
            "GET",
            "api/investments/funds/config",
            200
        )
        
        if success:
            funds = response.get('funds', [])
            core_fund = None
            
            for fund in funds:
                if fund.get('fund_code') == 'CORE':
                    core_fund = fund
                    break
            
            if not core_fund:
                self.log_error("CORE FUND NOT FOUND: CORE fund is not in configuration")
                return False
            
            # Check minimum investment
            min_investment = core_fund.get('minimum_investment', 0)
            if min_investment > 25000:
                self.log_error(f"MINIMUM INVESTMENT TOO HIGH: CORE fund requires ${min_investment:,}, but demo uses $25,000")
            
            print(f"   ✅ CORE Fund Found:")
            print(f"      Name: {core_fund.get('name')}")
            print(f"      Minimum Investment: ${core_fund.get('minimum_investment', 0):,}")
            print(f"      Interest Rate: {core_fund.get('interest_rate', 0)}%")
            
        return success

    def test_mongodb_integration(self):
        """Test if MongoDB integration is working"""
        print(f"\n🔍 Checking MongoDB Integration...")
        
        # Test getting all clients to check MongoDB connection
        success, response = self.run_test(
            "Check MongoDB Connection (Get All Clients)",
            "GET",
            "api/clients/all",
            200
        )
        
        if success:
            clients = response.get('clients', [])
            client_001_found = False
            
            for client in clients:
                if client.get('id') == 'client_001':
                    client_001_found = True
                    print(f"   ✅ client_001 found in MongoDB:")
                    print(f"      Name: {client.get('name')}")
                    print(f"      Email: {client.get('email')}")
                    break
            
            if not client_001_found:
                self.log_error("CLIENT_001 NOT IN MONGODB: client_001 not found in database")
        
        return success

    def test_alternative_investment_scenarios(self):
        """Test alternative scenarios to isolate the issue"""
        print(f"\n🔍 Testing Alternative Investment Scenarios...")
        
        # Test 1: Try with different amount (higher)
        alt_data_1 = {
            "client_id": "client_001",
            "fund_code": "CORE", 
            "amount": 50000,  # Higher amount
            "payment_method": "wire_transfer"
        }
        
        success1, response1 = self.run_test(
            "Alternative Test: Higher Amount ($50,000)",
            "POST",
            "api/investments/create",
            200,
            data=alt_data_1
        )
        
        # Test 2: Try with different client (if exists)
        alt_data_2 = {
            "client_id": "client_002",  # Different client
            "fund_code": "CORE", 
            "amount": 25000,
            "payment_method": "wire_transfer"
        }
        
        success2, response2 = self.run_test(
            "Alternative Test: Different Client (client_002)",
            "POST",
            "api/investments/create",
            200,
            data=alt_data_2
        )
        
        # Test 3: Try with different fund
        alt_data_3 = {
            "client_id": "client_001",
            "fund_code": "BALANCE",  # Different fund
            "amount": 50000,  # BALANCE typically has higher minimum
            "payment_method": "wire_transfer"
        }
        
        success3, response3 = self.run_test(
            "Alternative Test: Different Fund (BALANCE)",
            "POST",
            "api/investments/create",
            200,
            data=alt_data_3
        )
        
        # Analyze results
        if success1 and not success2 and not success3:
            self.log_error("AMOUNT ISSUE: Only higher amounts work - minimum investment problem")
        elif not success1 and success2 and not success3:
            self.log_error("CLIENT ISSUE: Only different clients work - client_001 specific problem")
        elif not success1 and not success2 and success3:
            self.log_error("FUND ISSUE: Only different funds work - CORE fund specific problem")
        
        return any([success1, success2, success3])

    def test_required_fields_validation(self):
        """Test if all required fields are being processed correctly"""
        print(f"\n🔍 Testing Required Fields Validation...")
        
        # Test missing client_id
        missing_client = {
            "fund_code": "CORE", 
            "amount": 25000,
            "payment_method": "wire_transfer"
        }
        
        success1, response1 = self.run_test(
            "Validation Test: Missing client_id",
            "POST",
            "api/investments/create",
            422,  # Should return validation error
            data=missing_client
        )
        
        # Test missing fund_code
        missing_fund = {
            "client_id": "client_001",
            "amount": 25000,
            "payment_method": "wire_transfer"
        }
        
        success2, response2 = self.run_test(
            "Validation Test: Missing fund_code",
            "POST",
            "api/investments/create",
            422,  # Should return validation error
            data=missing_fund
        )
        
        # Test missing amount
        missing_amount = {
            "client_id": "client_001",
            "fund_code": "CORE",
            "payment_method": "wire_transfer"
        }
        
        success3, response3 = self.run_test(
            "Validation Test: Missing amount",
            "POST",
            "api/investments/create",
            422,  # Should return validation error
            data=missing_amount
        )
        
        if success1 and success2 and success3:
            print("   ✅ Field validation working correctly")
        else:
            self.log_error("VALIDATION ISSUE: Required field validation not working properly")
        
        return success1 and success2 and success3

    def run_urgent_diagnosis(self):
        """Run complete urgent diagnosis for the demo issue"""
        print("\n" + "🚨"*40)
        print("URGENT DEMO DIAGNOSIS - INVESTMENT CREATION FAILURE")
        print("🚨"*40)
        
        # Step 1: Test the exact failing scenario
        main_success = self.test_investment_creation_urgent()
        
        # Step 2: Check all dependencies
        self.test_client_data_dependencies()
        self.test_fund_configuration_dependencies()
        self.test_mongodb_integration()
        
        # Step 3: Test validation and alternatives
        self.test_required_fields_validation()
        self.test_alternative_investment_scenarios()
        
        # Final diagnosis
        print(f"\n" + "="*80)
        print("🎯 URGENT DIAGNOSIS RESULTS")
        print("="*80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.errors_found:
            print(f"\n🚨 CRITICAL ERRORS FOUND ({len(self.errors_found)}):")
            for i, error in enumerate(self.errors_found, 1):
                print(f"   {i}. {error}")
        
        if main_success:
            print(f"\n✅ INVESTMENT CREATION IS WORKING!")
            print(f"   The demo issue may be resolved or was temporary.")
        else:
            print(f"\n❌ INVESTMENT CREATION IS FAILING!")
            print(f"   This confirms the demo issue exists.")
            
            # Provide specific recommendations
            print(f"\n💡 IMMEDIATE ACTIONS NEEDED:")
            
            if any("CLIENT" in error for error in self.errors_found):
                print(f"   1. Fix client_001 data or readiness status")
            
            if any("FUND" in error for error in self.errors_found):
                print(f"   2. Check CORE fund configuration and minimum investment")
            
            if any("DATABASE" in error for error in self.errors_found):
                print(f"   3. Verify MongoDB connection and data integrity")
            
            if any("VALIDATION" in error for error in self.errors_found):
                print(f"   4. Fix API endpoint validation logic")
        
        return main_success

if __name__ == "__main__":
    print("🚨 URGENT INVESTMENT CREATION DIAGNOSIS")
    print("Testing the specific issue reported during live demo...")
    
    tester = UrgentInvestmentTester()
    success = tester.run_urgent_diagnosis()
    
    # Exit with appropriate code for automation
    sys.exit(0 if success else 1)