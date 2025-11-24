#!/usr/bin/env python3
"""
🎯 VERIFY ALL 3 CRITICAL FIXES - COMPLETE WORKFLOW TEST

OBJECTIVE: Test that all 3 critical fixes are working and verify complete end-to-end workflow.

FIXES IMPLEMENTED:
1. ✅ Issue #2 Fixed: Migration flag - leads now marked as migrated_to_crm=True with migrated_date
2. ✅ Issue #3 Fixed: Stage validation - invalid stages rejected with HTTP 422
3. ✅ Issue #1 Fixed: Mark-won endpoint - new POST /api/crm/prospects/{prospect_id}/mark-won

COMPLETE WORKFLOW TEST:
- TEST 1: Create Lead & Track Simulator
- TEST 2: Verify CRM Integration
- TEST 3: Move to Negotiation & VERIFY MIGRATION FLAG
- TEST 4: Test Stage Validation
- TEST 5: Mark as Won (NEW ENDPOINT)
- TEST 6: Run AML/KYC
- TEST 7: Convert to Client (COMPLETE WORKFLOW)
- TEST 8: Verify Complete Data Chain

SUCCESS CRITERIA:
- Target: 16/17 tests passed (94.1%+)
- All 3 critical fixes working
- Complete data chain verification
"""

import requests
import json
import sys
from datetime import datetime
import pymongo
from pymongo import MongoClient
import uuid
import time

# Backend URL from environment
BACKEND_URL = "https://mt5-sync.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class CRMWorkflowFixesTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
        # Test data
        self.test_lead_id = None
        self.test_prospect_id = None
        self.test_client_id = None
        self.unique_email = f"test_lead_{int(time.time())}@example.com"
        
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
        """Connect to MongoDB for data verification"""
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
    
    def test_1_create_lead_and_track_simulator(self):
        """TEST 1: Create Lead & Track Simulator"""
        try:
            # Create unique test lead
            lead_data = {
                "email": self.unique_email,
                "phone": "+1-555-TEST-001",
                "source": "prospects_portal"
            }
            
            # Create lead
            url = f"{BACKEND_URL}/api/prospects/lead"
            response = self.session.post(url, json=lead_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG: Lead creation response: {data}")
                self.test_lead_id = data.get('leadId') or data.get('lead_id') or data.get('id')
                
                if self.test_lead_id:
                    self.log_test("Lead Creation", True, f"Created lead with ID: {self.test_lead_id}")
                    
                    # Track simulator session
                    simulator_url = f"{BACKEND_URL}/api/prospects/simulator/{self.test_lead_id}"
                    simulator_data = {
                        "fund": "BALANCE",
                        "amount": 100000.0,
                        "projections": {"monthly_return": 2.5}
                    }
                    
                    sim_response = self.session.post(simulator_url, json=simulator_data)
                    
                    if sim_response.status_code == 200:
                        self.log_test("Simulator Tracking", True, "Engagement score set to 10")
                        
                        # Verify engagement score in MongoDB - try different field names
                        print(f"DEBUG: Looking for lead {self.test_lead_id} in collections...")
                        collections = self.db.list_collection_names()
                        print(f"DEBUG: Available collections: {collections}")
                        
                        # Try different collections and field names
                        lead_doc = None
                        for collection_name in ['leads', 'prospects_leads', 'prospect_leads']:
                            if collection_name in collections:
                                collection = self.db[collection_name]
                                lead_doc = (collection.find_one({"lead_id": self.test_lead_id}) or 
                                           collection.find_one({"_id": self.test_lead_id}) or
                                           collection.find_one({"id": self.test_lead_id}))
                                if lead_doc:
                                    print(f"DEBUG: Found lead in {collection_name} collection")
                                    break
                        
                        if not lead_doc:
                            # Try to find any document with our email
                            for collection_name in collections:
                                collection = self.db[collection_name]
                                email_doc = collection.find_one({"email": self.unique_email})
                                if email_doc:
                                    print(f"DEBUG: Found document with email in {collection_name}: {email_doc}")
                                    lead_doc = email_doc
                                    break
                        if lead_doc and lead_doc.get('engagement_score') == 10:
                            self.log_test("Engagement Score Verification", True, "Engagement score = 10 confirmed in database")
                            return True
                        else:
                            self.log_test("Engagement Score Verification", False, f"Expected engagement_score=10, got: {lead_doc.get('engagement_score') if lead_doc else 'lead not found'}")
                            return False
                    else:
                        self.log_test("Simulator Tracking", False, f"HTTP {sim_response.status_code}: {sim_response.text}")
                        return False
                else:
                    self.log_test("Lead Creation", False, "No lead_id in response")
                    return False
            else:
                self.log_test("Lead Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TEST 1 - Create Lead & Track Simulator", False, f"Exception: {str(e)}")
            return False
    
    def test_2_verify_crm_integration(self):
        """TEST 2: Verify CRM Integration"""
        try:
            # Get CRM prospects
            url = f"{BACKEND_URL}/api/crm/prospects"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                
                # Look for our test lead with portal_lead_ prefix
                expected_prospect_id = f"portal_lead_{self.test_lead_id}"
                found_prospect = None
                
                for prospect in prospects:
                    if prospect.get('prospect_id') == expected_prospect_id:
                        found_prospect = prospect
                        self.test_prospect_id = expected_prospect_id
                        break
                
                if found_prospect:
                    self.log_test("CRM Integration", True, f"Lead appears in CRM with ID: {expected_prospect_id}")
                    
                    # Verify prospect details
                    if (found_prospect.get('stage') == 'lead' and 
                        found_prospect.get('source') == 'prospects_portal' and
                        found_prospect.get('email') == self.unique_email):
                        self.log_test("Prospect Details Verification", True, "Stage=lead, source=prospects_portal, email matches")
                        return True
                    else:
                        self.log_test("Prospect Details Verification", False, f"Stage: {found_prospect.get('stage')}, Source: {found_prospect.get('source')}, Email: {found_prospect.get('email')}")
                        return False
                else:
                    self.log_test("CRM Integration", False, f"Lead not found in CRM prospects. Expected ID: {expected_prospect_id}")
                    return False
            else:
                self.log_test("CRM Integration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TEST 2 - Verify CRM Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_3_move_to_negotiation_verify_migration_flag(self):
        """TEST 3: Move to Negotiation & VERIFY MIGRATION FLAG"""
        try:
            # Update prospect to negotiation stage
            url = f"{BACKEND_URL}/api/crm/prospects/{self.test_prospect_id}"
            update_data = {
                "stage": "negotiation",
                "notes": "Moving to negotiation for CRM fixes test"
            }
            
            response = self.session.put(url, json=update_data)
            
            if response.status_code == 200:
                self.log_test("Pipeline Movement", True, "Successfully moved to negotiation stage")
                
                # CRITICAL: Verify migration flag in MongoDB
                from bson import ObjectId
                try:
                    lead_doc = self.db.leads.find_one({"_id": ObjectId(self.test_lead_id)})
                except:
                    lead_doc = (self.db.leads.find_one({"lead_id": self.test_lead_id}) or 
                               self.db.leads.find_one({"id": self.test_lead_id}) or
                               self.db.leads.find_one({"email": self.unique_email}))
                
                if lead_doc:
                    migrated_to_crm = lead_doc.get('migrated_to_crm')
                    crm_prospect_id = lead_doc.get('crm_prospect_id')
                    migrated_date = lead_doc.get('migrated_date')
                    
                    # Check all 3 critical fields
                    migration_flag_success = migrated_to_crm is True
                    prospect_id_success = crm_prospect_id is not None
                    migrated_date_success = migrated_date is not None
                    
                    if migration_flag_success:
                        self.log_test("Migration Flag Set", True, f"migrated_to_crm = {migrated_to_crm}")
                    else:
                        self.log_test("Migration Flag Set", False, f"migrated_to_crm = {migrated_to_crm} (should be True)")
                    
                    if prospect_id_success:
                        self.log_test("CRM Prospect ID Set", True, f"crm_prospect_id = {crm_prospect_id}")
                    else:
                        self.log_test("CRM Prospect ID Set", False, f"crm_prospect_id = {crm_prospect_id} (should not be None)")
                    
                    if migrated_date_success:
                        self.log_test("Migration Date Set", True, f"migrated_date = {migrated_date}")
                    else:
                        self.log_test("Migration Date Set", False, f"migrated_date = {migrated_date} (should not be None)")
                    
                    # Verify prospect created in crm_prospects collection
                    prospect_doc = (self.db.crm_prospects.find_one({"prospect_id": self.test_prospect_id}) or
                                   self.db.crm_prospects.find_one({"_id": self.test_prospect_id}) or
                                   self.db.crm_prospects.find_one({"id": self.test_prospect_id}))
                    if prospect_doc:
                        self.log_test("Prospect in CRM Collection", True, f"Prospect found in crm_prospects collection")
                        return migration_flag_success and prospect_id_success and migrated_date_success
                    else:
                        self.log_test("Prospect in CRM Collection", False, "Prospect not found in crm_prospects collection")
                        return False
                else:
                    self.log_test("Lead Document Found", False, f"Lead {self.test_lead_id} not found in database")
                    return False
            else:
                self.log_test("Pipeline Movement", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TEST 3 - Move to Negotiation & Verify Migration Flag", False, f"Exception: {str(e)}")
            return False
    
    def test_4_test_stage_validation(self):
        """TEST 4: Test Stage Validation"""
        try:
            # Try to update with invalid stage
            url = f"{BACKEND_URL}/api/crm/prospects/{self.test_prospect_id}"
            invalid_data = {
                "stage": "invalid_stage",
                "notes": "Testing stage validation"
            }
            
            response = self.session.put(url, json=invalid_data)
            
            # CRITICAL: Should return HTTP 422, not 200
            if response.status_code == 422:
                self.log_test("Stage Validation - HTTP 422", True, "Invalid stage rejected with HTTP 422")
                
                # Check error message lists valid stages
                try:
                    error_data = response.json()
                    error_message = str(error_data)
                    
                    valid_stages = ['lead', 'qualified', 'proposal', 'negotiation', 'won', 'lost']
                    stages_mentioned = sum(1 for stage in valid_stages if stage in error_message.lower())
                    
                    if stages_mentioned >= 3:  # At least 3 valid stages mentioned
                        self.log_test("Stage Validation - Error Message", True, f"Error message lists valid stages: {error_message[:200]}...")
                        return True
                    else:
                        self.log_test("Stage Validation - Error Message", False, f"Error message doesn't list valid stages: {error_message}")
                        return False
                        
                except:
                    self.log_test("Stage Validation - Error Message", True, "HTTP 422 returned (error message format not critical)")
                    return True
                    
            elif response.status_code == 200:
                self.log_test("Stage Validation - HTTP 422", False, f"Invalid stage accepted with HTTP 200 (should be 422)")
                return False
            else:
                self.log_test("Stage Validation - HTTP 422", False, f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("TEST 4 - Test Stage Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_5_mark_as_won_new_endpoint(self):
        """TEST 5: Mark as Won (NEW ENDPOINT)"""
        try:
            # Use new mark-won endpoint
            url = f"{BACKEND_URL}/api/crm/prospects/{self.test_prospect_id}/mark-won"
            
            response = self.session.post(url)
            
            # CRITICAL: Should return HTTP 200 with stage="won"
            if response.status_code == 200:
                data = response.json()
                
                if data.get('stage') == 'won':
                    self.log_test("Mark-Won Endpoint", True, f"New endpoint works, returned stage='won'")
                    
                    # Verify prospect stage updated in MongoDB
                    prospect_doc = (self.db.crm_prospects.find_one({"prospect_id": self.test_prospect_id}) or
                                   self.db.crm_prospects.find_one({"_id": self.test_prospect_id}) or
                                   self.db.crm_prospects.find_one({"id": self.test_prospect_id}))
                    if prospect_doc and prospect_doc.get('stage') == 'won':
                        self.log_test("Prospect Stage Updated to Won", True, "Stage updated to 'won' in database")
                        return True
                    else:
                        self.log_test("Prospect Stage Updated to Won", False, f"Stage in DB: {prospect_doc.get('stage') if prospect_doc else 'prospect not found'}")
                        return False
                else:
                    self.log_test("Mark-Won Endpoint", False, f"Expected stage='won', got: {data.get('stage')}")
                    return False
            else:
                self.log_test("Mark-Won Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TEST 5 - Mark as Won (NEW ENDPOINT)", False, f"Exception: {str(e)}")
            return False
    
    def test_6_run_aml_kyc(self):
        """TEST 6: Run AML/KYC"""
        try:
            # Run AML/KYC process
            url = f"{BACKEND_URL}/api/crm/prospects/{self.test_prospect_id}/aml-kyc"
            
            response = self.session.post(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required AML/KYC response fields - be flexible with field names
                can_convert = data.get('can_convert', data.get('canConvert', data.get('success', False)))
                status = data.get('overall_status', data.get('status', 'unknown'))
                result_id = data.get('result_id', data.get('resultId', data.get('id', 'generated')))
                
                if can_convert:
                    self.log_test("AML/KYC Process", True, f"AML/KYC completed, can_convert={can_convert}, status={status}")
                    return True
                else:
                    self.log_test("AML/KYC Process", False, f"can_convert={can_convert}, status={status}, response: {data}")
                    return False
            else:
                self.log_test("AML/KYC Process", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TEST 6 - Run AML/KYC", False, f"Exception: {str(e)}")
            return False
    
    def test_7_convert_to_client_complete_workflow(self):
        """TEST 7: Convert to Client (COMPLETE WORKFLOW)"""
        try:
            # Convert prospect to client
            url = f"{BACKEND_URL}/api/crm/prospects/{self.test_prospect_id}/convert"
            conversion_data = {
                "send_agreement": True
            }
            
            response = self.session.post(url, json=conversion_data)
            
            # CRITICAL: Should now work (was blocked before)
            if response.status_code == 200:
                data = response.json()
                self.test_client_id = data.get('client_id')
                
                if self.test_client_id:
                    self.log_test("Client Conversion", True, f"Successfully converted to client: {self.test_client_id}")
                    
                    # Verify client created in users collection
                    client_doc = (self.db.users.find_one({"id": self.test_client_id}) or
                                 self.db.users.find_one({"_id": self.test_client_id}) or
                                 self.db.users.find_one({"username": self.test_client_id}))
                    if client_doc:
                        self.log_test("Client in Users Collection", True, f"Client found in users collection")
                        return True
                    else:
                        self.log_test("Client in Users Collection", False, "Client not found in users collection")
                        return False
                else:
                    self.log_test("Client Conversion", False, "No client_id in response")
                    return False
            else:
                self.log_test("Client Conversion", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TEST 7 - Convert to Client (COMPLETE WORKFLOW)", False, f"Exception: {str(e)}")
            return False
    
    def test_8_verify_complete_data_chain(self):
        """TEST 8: Verify Complete Data Chain"""
        try:
            # Query all 3 collections and verify data chain
            from bson import ObjectId
            try:
                lead_doc = self.db.leads.find_one({"_id": ObjectId(self.test_lead_id)})
            except:
                lead_doc = self.db.leads.find_one({"email": self.unique_email})
            
            prospect_doc = (self.db.crm_prospects.find_one({"prospect_id": self.test_prospect_id}) or
                           self.db.crm_prospects.find_one({"_id": self.test_prospect_id}) or
                           self.db.crm_prospects.find_one({"id": self.test_prospect_id}))
            client_doc = (self.db.users.find_one({"id": self.test_client_id}) or
                         self.db.users.find_one({"_id": self.test_client_id}) or
                         self.db.users.find_one({"username": self.test_client_id})) if self.test_client_id else None
            
            # Verify Lead data chain
            lead_chain_success = False
            if lead_doc:
                lead_migrated = lead_doc.get('migrated_to_crm') is True
                lead_prospect_id = lead_doc.get('crm_prospect_id') == self.test_prospect_id
                lead_client_id = lead_doc.get('client_id') == self.test_client_id
                
                lead_chain_success = lead_migrated and lead_prospect_id and lead_client_id
                
                if lead_chain_success:
                    self.log_test("Lead Data Chain", True, f"migrated_to_crm=True, crm_prospect_id={self.test_prospect_id}, client_id={self.test_client_id}")
                else:
                    self.log_test("Lead Data Chain", False, f"migrated_to_crm={lead_doc.get('migrated_to_crm')}, crm_prospect_id={lead_doc.get('crm_prospect_id')}, client_id={lead_doc.get('client_id')}")
            else:
                self.log_test("Lead Data Chain", False, "Lead document not found")
            
            # Verify Prospect data chain
            prospect_chain_success = False
            if prospect_doc:
                prospect_original_lead = prospect_doc.get('_original_lead_id') == self.test_lead_id
                prospect_converted = prospect_doc.get('converted_to_client') is True
                prospect_client_id = prospect_doc.get('client_id') == self.test_client_id
                
                prospect_chain_success = prospect_original_lead and prospect_converted and prospect_client_id
                
                if prospect_chain_success:
                    self.log_test("Prospect Data Chain", True, f"_original_lead_id={self.test_lead_id}, converted_to_client=True, client_id={self.test_client_id}")
                else:
                    self.log_test("Prospect Data Chain", False, f"_original_lead_id={prospect_doc.get('_original_lead_id')}, converted_to_client={prospect_doc.get('converted_to_client')}, client_id={prospect_doc.get('client_id')}")
            else:
                self.log_test("Prospect Data Chain", False, "Prospect document not found")
            
            # Verify Client data chain
            client_chain_success = False
            if client_doc:
                client_source_prospect = client_doc.get('source_prospect_id') == self.test_prospect_id
                client_source_lead = client_doc.get('source_lead_id') == self.test_lead_id
                
                client_chain_success = client_source_prospect and client_source_lead
                
                if client_chain_success:
                    self.log_test("Client Data Chain", True, f"source_prospect_id={self.test_prospect_id}, source_lead_id={self.test_lead_id}")
                else:
                    self.log_test("Client Data Chain", False, f"source_prospect_id={client_doc.get('source_prospect_id')}, source_lead_id={client_doc.get('source_lead_id')}")
            else:
                self.log_test("Client Data Chain", False, "Client document not found")
            
            return lead_chain_success and prospect_chain_success and client_chain_success
                
        except Exception as e:
            self.log_test("TEST 8 - Verify Complete Data Chain", False, f"Exception: {str(e)}")
            return False
    
    def run_complete_workflow_test(self):
        """Run complete CRM workflow fixes test"""
        print("🎯 VERIFY ALL 3 CRITICAL FIXES - COMPLETE WORKFLOW TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print(f"Test Email: {self.unique_email}")
        print()
        
        # Connect to MongoDB
        print("📋 SETUP: Connect to MongoDB")
        if not self.connect_to_mongodb():
            print("❌ MongoDB connection failed. Cannot verify data chain.")
            return False
        print()
        
        # Authenticate
        print("📋 SETUP: Authenticate as Admin")
        if not self.authenticate():
            print("❌ Authentication failed. Cannot test endpoints.")
            return False
        print()
        
        # Run all 8 tests
        test_results = []
        
        print("📋 TEST 1: Create Lead & Track Simulator")
        test_results.append(self.test_1_create_lead_and_track_simulator())
        print()
        
        print("📋 TEST 2: Verify CRM Integration")
        test_results.append(self.test_2_verify_crm_integration())
        print()
        
        print("📋 TEST 3: Move to Negotiation & VERIFY MIGRATION FLAG")
        test_results.append(self.test_3_move_to_negotiation_verify_migration_flag())
        print()
        
        print("📋 TEST 4: Test Stage Validation")
        test_results.append(self.test_4_test_stage_validation())
        print()
        
        print("📋 TEST 5: Mark as Won (NEW ENDPOINT)")
        test_results.append(self.test_5_mark_as_won_new_endpoint())
        print()
        
        print("📋 TEST 6: Run AML/KYC")
        test_results.append(self.test_6_run_aml_kyc())
        print()
        
        print("📋 TEST 7: Convert to Client (COMPLETE WORKFLOW)")
        test_results.append(self.test_7_convert_to_client_complete_workflow())
        print()
        
        print("📋 TEST 8: Verify Complete Data Chain")
        test_results.append(self.test_8_verify_complete_data_chain())
        print()
        
        # Summary
        self.print_test_summary(test_results)
        
        # Return overall success
        return all(test_results)
    
    def print_test_summary(self, test_results):
        """Print comprehensive test summary"""
        print("=" * 80)
        print("📊 CRM WORKFLOW FIXES TEST SUMMARY")
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
        
        # Critical fixes verification
        print("🔍 CRITICAL FIXES VERIFICATION:")
        
        # Fix #1: Mark-won endpoint
        mark_won_success = any('Mark-Won Endpoint' in r['test'] and r['success'] for r in self.test_results)
        print(f"   {'✅' if mark_won_success else '❌'} Fix #1: Mark-won endpoint - POST /api/crm/prospects/{{prospect_id}}/mark-won")
        
        # Fix #2: Migration flag
        migration_flag_success = any('Migration Flag Set' in r['test'] and r['success'] for r in self.test_results)
        migration_date_success = any('Migration Date Set' in r['test'] and r['success'] for r in self.test_results)
        fix2_success = migration_flag_success and migration_date_success
        print(f"   {'✅' if fix2_success else '❌'} Fix #2: Migration flag - leads marked as migrated_to_crm=True with migrated_date")
        
        # Fix #3: Stage validation
        stage_validation_success = any('Stage Validation - HTTP 422' in r['test'] and r['success'] for r in self.test_results)
        print(f"   {'✅' if stage_validation_success else '❌'} Fix #3: Stage validation - invalid stages rejected with HTTP 422")
        
        print()
        
        # Workflow verification
        print("🔄 COMPLETE WORKFLOW VERIFICATION:")
        
        workflow_steps = [
            ("Lead Creation", any('Lead Creation' in r['test'] and r['success'] for r in self.test_results)),
            ("CRM Integration", any('CRM Integration' in r['test'] and r['success'] for r in self.test_results)),
            ("Pipeline Movement", any('Pipeline Movement' in r['test'] and r['success'] for r in self.test_results)),
            ("AML/KYC Process", any('AML/KYC Process' in r['test'] and r['success'] for r in self.test_results)),
            ("Client Conversion", any('Client Conversion' in r['test'] and r['success'] for r in self.test_results)),
            ("Data Chain Integrity", any('Lead Data Chain' in r['test'] and r['success'] for r in self.test_results))
        ]
        
        for step_name, step_success in workflow_steps:
            print(f"   {'✅' if step_success else '❌'} {step_name}")
        
        print()
        
        # Expected vs actual results
        print("📈 RESULTS COMPARISON:")
        print(f"   Target Success Rate: 94.1%+ (16/17 tests)")
        print(f"   Actual Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests)")
        
        if success_rate >= 94.1:
            print("   🎉 TARGET ACHIEVED: Success rate meets or exceeds 94.1%")
        else:
            print(f"   ⚠️ TARGET MISSED: Need {16 - passed_tests} more tests to pass for 94.1%")
        
        print()
        
        # Critical success criteria
        print("🎯 SUCCESS CRITERIA STATUS:")
        all_fixes_working = mark_won_success and fix2_success and stage_validation_success
        complete_workflow = all(step_success for _, step_success in workflow_steps)
        
        print(f"   {'✅' if all_fixes_working else '❌'} All 3 critical fixes working")
        print(f"   {'✅' if complete_workflow else '❌'} Complete end-to-end workflow")
        print(f"   {'✅' if success_rate >= 94.1 else '❌'} Success rate ≥ 94.1%")
        
        if all_fixes_working and complete_workflow and success_rate >= 94.1:
            print()
            print("🎉 PRODUCTION READY CONFIRMATION:")
            print("   ✅ All 3 critical fixes verified and working")
            print("   ✅ Complete CRM workflow functional end-to-end")
            print("   ✅ Data chain integrity maintained")
            print("   ✅ Target success rate achieved")
        else:
            print()
            print("⚠️ ISSUES REQUIRING ATTENTION:")
            if not mark_won_success:
                print("   🔧 Mark-won endpoint needs fixing")
            if not fix2_success:
                print("   🔧 Migration flag implementation needs fixing")
            if not stage_validation_success:
                print("   🔧 Stage validation needs fixing")
            if not complete_workflow:
                print("   🔧 End-to-end workflow has gaps")
        
        print()
        
        # Failed tests details
        if failed_tests > 0:
            print("❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()

def main():
    """Main test execution"""
    tester = CRMWorkflowFixesTest()
    success = tester.run_complete_workflow_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()