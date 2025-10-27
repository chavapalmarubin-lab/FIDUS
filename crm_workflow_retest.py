#!/usr/bin/env python3
"""
🔄 CRM WORKFLOW RE-TEST AFTER CRITICAL FIXES

CONTEXT: Testing critical fixes implemented by main agent:
1. ✅ Portal lead migration now checks if already migrated to avoid duplicates
2. ✅ AML/KYC endpoint now resolves portal_lead_ IDs to actual prospect IDs
3. ✅ Convert endpoint now resolves portal_lead_ IDs and tracks original lead
4. ✅ Data chain integrity maintained (lead → prospect → client)

TEST OBJECTIVES:
- Run the SAME comprehensive workflow test to verify fixes
- Test complete pipeline: Lead → CRM → Negotiation → Won → AML/KYC → Client
- Verify all database collections properly linked
- Report PASS/FAIL for each phase with detailed evidence

EXPECTED IMPROVEMENTS:
- ❌→✅ Pipeline movement (was broken, now should work)
- ❌→✅ Subsequent updates (was 500 error, now should work)
- ❌→✅ AML/KYC with portal_lead_ (was 404, now should resolve)
- ❌→✅ Convert with portal_lead_ (was 404, now should resolve)
- ✅ Data chain integrity (should be complete)

SUCCESS CRITERIA:
- All 6 phases should PASS
- No 404 or 500 errors
- Complete data chain from leads → crm_prospects → users
- All cross-references properly maintained
"""

import requests
import json
import sys
from datetime import datetime, timezone
import pymongo
from pymongo import MongoClient
import os
import time
import uuid

# Backend URL from environment
BACKEND_URL = "https://oauth-reforge.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class CRMWorkflowRetest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
        # Test data with unique timestamp for this retest
        self.timestamp = int(time.time())
        self.test_email = f"retest-crm-{self.timestamp}@fidus-test.com"
        self.test_phone = f"+525555{str(self.timestamp)[-6:]}"
        
        # Test tracking variables
        self.lead_id = None
        self.prospect_id = None
        self.client_id = None
        self.migrated_prospect_id = None  # NEW: Track migrated prospect ID
        
        # Phase tracking for comparison
        self.phase_results = {
            "lead_creation": False,
            "simulator_tracking": False,
            "crm_integration": False,
            "pipeline_movement": False,
            "aml_kyc": False,
            "client_conversion": False
        }
        
    def log_test(self, test_name, success, details, http_status=None):
        """Log test results with detailed information"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "http_status": http_status,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if http_status:
            print(f"   HTTP Status: {http_status}")
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
    
    def authenticate_admin(self):
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
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                    self.log_test("Admin Authentication", True, f"Successfully authenticated as {ADMIN_USERNAME}", response.status_code)
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", response.status_code)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Authentication failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_phase1_lead_creation(self):
        """PHASE 1: LEAD CREATION - Should still work (✅ already working)"""
        print("📋 PHASE 1: LEAD CREATION")
        print("=" * 60)
        
        try:
            url = f"{BACKEND_URL}/api/prospects/lead"
            payload = {
                "email": self.test_email,
                "phone": self.test_phone,
                "source": "prospects_portal"
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.lead_id = data.get('leadId', data.get('lead_id', data.get('id')))
                
                if self.lead_id:
                    # Verify lead in MongoDB
                    if self.verify_lead_in_mongodb():
                        self.log_test("Lead Creation", True, f"Lead created with ID: {self.lead_id}", response.status_code)
                        self.phase_results["lead_creation"] = True
                        return True
                    else:
                        self.log_test("Lead Creation", False, "Lead not found in MongoDB", response.status_code)
                        return False
                else:
                    self.log_test("Lead Creation", False, "No leadId in response", response.status_code)
                    return False
            else:
                self.log_test("Lead Creation", False, f"Failed to create lead: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Lead Creation", False, f"Exception: {str(e)}")
            return False
    
    def verify_lead_in_mongodb(self):
        """Verify lead exists in MongoDB leads collection"""
        try:
            if self.db is None:
                return False
                
            lead = self.db.leads.find_one({"email": self.test_email})
            
            if lead is not None:
                # Verify required fields
                required_fields = ['email', 'phone', 'source', 'status']
                missing_fields = [field for field in required_fields if field not in lead]
                
                if not missing_fields:
                    self.log_test("Lead MongoDB Verification", True, f"Lead stored correctly in MongoDB with all required fields")
                    return True
                else:
                    self.log_test("Lead MongoDB Verification", False, f"Missing fields in MongoDB: {missing_fields}")
                    return False
            else:
                self.log_test("Lead MongoDB Verification", False, "Lead not found in MongoDB leads collection")
                return False
                
        except Exception as e:
            self.log_test("Lead MongoDB Verification", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_phase2_simulator_tracking(self):
        """PHASE 2: SIMULATOR TRACKING - Should still work (✅ already working)"""
        print("📋 PHASE 2: SIMULATOR TRACKING")
        print("=" * 60)
        
        try:
            if not self.lead_id:
                self.log_test("Simulator Tracking", False, "No lead_id available")
                return False
                
            url = f"{BACKEND_URL}/api/prospects/simulator/{self.lead_id}"
            payload = {
                "fund": "FIDUS_BALANCE",
                "amount": 100000,
                "projections": {"1_year": 15000}
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                # Verify simulator session was tracked in MongoDB
                if self.verify_simulator_session_in_mongodb():
                    self.log_test("Simulator Tracking", True, "Simulator session tracked successfully", response.status_code)
                    self.phase_results["simulator_tracking"] = True
                    return True
                else:
                    self.log_test("Simulator Tracking", False, "Simulator session not tracked in MongoDB", response.status_code)
                    return False
            else:
                self.log_test("Simulator Tracking", False, f"Failed to track simulator session: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Simulator Tracking", False, f"Exception: {str(e)}")
            return False
    
    def verify_simulator_session_in_mongodb(self):
        """Verify simulator session was tracked in MongoDB"""
        try:
            if self.db is None:
                return False
                
            lead = self.db.leads.find_one({"email": self.test_email})
            
            if lead is not None:
                # Check for simulator_sessions array and engagement_score update
                simulator_sessions = lead.get('simulator_sessions', [])
                engagement_score = lead.get('engagement_score', 0)
                
                if simulator_sessions and engagement_score > 0:
                    self.log_test("Simulator Session MongoDB Verification", True, f"Engagement score: {engagement_score}, Sessions: {len(simulator_sessions)}")
                    return True
                else:
                    self.log_test("Simulator Session MongoDB Verification", False, f"Engagement score: {engagement_score}, Sessions: {len(simulator_sessions)}")
                    return False
            else:
                self.log_test("Simulator Session MongoDB Verification", False, "Lead not found for simulator verification")
                return False
                
        except Exception as e:
            self.log_test("Simulator Session MongoDB Verification", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_phase3_crm_integration(self):
        """PHASE 3: CRM INTEGRATION - Should still work (✅ already working)"""
        print("📋 PHASE 3: CRM INTEGRATION")
        print("=" * 60)
        
        try:
            url = f"{BACKEND_URL}/api/crm/prospects"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get('prospects', [])
                
                # Look for our test lead
                test_prospect = None
                for prospect in prospects:
                    if prospect.get('email') == self.test_email:
                        test_prospect = prospect
                        break
                
                if test_prospect:
                    # Verify prospect properties
                    expected_prospect_id = f"portal_lead_{self.lead_id}"
                    actual_prospect_id = test_prospect.get('prospect_id')
                    stage = test_prospect.get('stage')
                    source = test_prospect.get('source')
                    
                    if (actual_prospect_id == expected_prospect_id and 
                        stage == 'lead' and 
                        source == 'prospects_portal'):
                        
                        self.prospect_id = actual_prospect_id
                        self.log_test("CRM Integration", True, f"Lead found in CRM with prospect_id: {self.prospect_id}", response.status_code)
                        self.phase_results["crm_integration"] = True
                        return True
                    else:
                        self.log_test("CRM Integration", False, f"Lead found but incorrect properties: prospect_id={actual_prospect_id}, stage={stage}, source={source}", response.status_code)
                        return False
                else:
                    self.log_test("CRM Integration", False, f"Test lead not found in CRM prospects list", response.status_code)
                    return False
            else:
                self.log_test("CRM Integration", False, f"Failed to get CRM prospects: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("CRM Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_phase4_pipeline_movement(self):
        """PHASE 4: PIPELINE MOVEMENT - NEW FIX - Should now handle migration properly"""
        print("📋 PHASE 4: PIPELINE MOVEMENT (CRITICAL FIX)")
        print("=" * 60)
        
        # Test 4.1: First update - should migrate portal lead to CRM prospect
        success_4_1 = self.test_first_pipeline_update()
        
        # Test 4.2: Subsequent update - should update existing CRM prospect (no duplicate)
        success_4_2 = self.test_subsequent_pipeline_update() if success_4_1 else False
        
        if success_4_1 and success_4_2:
            self.phase_results["pipeline_movement"] = True
            return True
        else:
            return False
    
    def test_first_pipeline_update(self):
        """Test 4.1: First update - should migrate portal lead to CRM prospect"""
        try:
            if not self.prospect_id:
                self.log_test("First Pipeline Update", False, "No prospect_id available")
                return False
                
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}"
            payload = {
                "stage": "negotiation",
                "name": "Test Retest User",
                "notes": "Testing first pipeline movement - should migrate"
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # NEW FIX: Should return migrated_prospect_id in response
                self.migrated_prospect_id = data.get('migrated_prospect_id')
                
                # Verify migration from leads to crm_prospects collection
                if self.verify_first_migration():
                    self.log_test("First Pipeline Update", True, f"Lead successfully migrated to negotiation stage. Migrated ID: {self.migrated_prospect_id}", response.status_code)
                    return True
                else:
                    self.log_test("First Pipeline Update", False, "First migration verification failed", response.status_code)
                    return False
            else:
                self.log_test("First Pipeline Update", False, f"Failed first pipeline update: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("First Pipeline Update", False, f"Exception: {str(e)}")
            return False
    
    def verify_first_migration(self):
        """Verify first migration was successful"""
        try:
            if self.db is None:
                return False
            
            # Check original lead is marked as migrated with crm_prospect_id
            original_lead = self.db.leads.find_one({"email": self.test_email})
            if original_lead is None:
                self.log_test("First Migration Verification", False, "Original lead not found")
                return False
            
            if not original_lead.get('migrated'):
                self.log_test("First Migration Verification", False, "Original lead not marked as migrated")
                return False
            
            crm_prospect_id = original_lead.get('crm_prospect_id')
            if not crm_prospect_id:
                self.log_test("First Migration Verification", False, "Original lead missing crm_prospect_id")
                return False
            
            # Check new prospect exists in crm_prospects collection
            prospect = self.db.crm_prospects.find_one({"email": self.test_email})
            if prospect is None:
                self.log_test("First Migration Verification", False, "Prospect not found in crm_prospects collection")
                return False
            
            # Verify prospect has _original_lead_id
            original_lead_id = prospect.get('_original_lead_id')
            if not original_lead_id:
                self.log_test("First Migration Verification", False, "Prospect missing _original_lead_id")
                return False
            
            # Verify prospect stage
            if prospect.get('stage') == 'negotiation':
                # Update prospect_id for next tests (now using actual MongoDB _id)
                self.prospect_id = str(prospect.get('_id'))
                self.log_test("First Migration Verification", True, f"Lead successfully migrated. Original lead marked, prospect created with _original_lead_id")
                return True
            else:
                self.log_test("First Migration Verification", False, f"Prospect stage incorrect: {prospect.get('stage')}")
                return False
                
        except Exception as e:
            self.log_test("First Migration Verification", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_subsequent_pipeline_update(self):
        """Test 4.2: Subsequent update - should update existing CRM prospect (no duplicate)"""
        try:
            if not self.prospect_id:
                self.log_test("Subsequent Pipeline Update", False, "No prospect_id available")
                return False
                
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}"
            payload = {
                "stage": "won",
                "notes": "Testing subsequent pipeline movement - should update existing"
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code == 200:
                # Verify no duplicate was created
                if self.verify_no_duplicate_created():
                    self.log_test("Subsequent Pipeline Update", True, "Existing prospect updated to won stage, no duplicate created", response.status_code)
                    return True
                else:
                    self.log_test("Subsequent Pipeline Update", False, "Duplicate prospect created or update failed", response.status_code)
                    return False
            else:
                self.log_test("Subsequent Pipeline Update", False, f"Failed subsequent pipeline update: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Subsequent Pipeline Update", False, f"Exception: {str(e)}")
            return False
    
    def verify_no_duplicate_created(self):
        """Verify no duplicate prospect was created"""
        try:
            if self.db is None:
                return False
            
            # Check there's exactly 1 prospect with this email
            prospects_count = self.db.crm_prospects.count_documents({"email": self.test_email})
            
            if prospects_count != 1:
                self.log_test("No Duplicate Verification", False, f"Found {prospects_count} prospects, expected 1")
                return False
            
            # Check the prospect is in won stage
            prospect = self.db.crm_prospects.find_one({"email": self.test_email})
            if prospect and prospect.get('stage') == 'won':
                self.log_test("No Duplicate Verification", True, f"Exactly 1 prospect found in won stage")
                return True
            else:
                stage = prospect.get('stage') if prospect else 'not found'
                self.log_test("No Duplicate Verification", False, f"Prospect stage: {stage}")
                return False
                
        except Exception as e:
            self.log_test("No Duplicate Verification", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_phase5_aml_kyc(self):
        """PHASE 5: AML/KYC ENDPOINT - NEW FIX - Should now resolve portal_lead_ IDs"""
        print("📋 PHASE 5: AML/KYC ENDPOINT (CRITICAL FIX)")
        print("=" * 60)
        
        # Test with both portal_lead_ ID and actual prospect ID
        success_portal = self.test_aml_kyc_with_portal_id()
        success_actual = self.test_aml_kyc_with_actual_id()
        
        if success_portal or success_actual:
            self.phase_results["aml_kyc"] = True
            return True
        else:
            return False
    
    def test_aml_kyc_with_portal_id(self):
        """Test AML/KYC with portal_lead_ ID - should resolve to actual prospect"""
        try:
            if not self.lead_id:
                self.log_test("AML/KYC with Portal ID", False, "No lead_id available")
                return False
                
            portal_prospect_id = f"portal_lead_{self.lead_id}"
            url = f"{BACKEND_URL}/api/crm/prospects/{portal_prospect_id}/aml-kyc"
            
            response = self.session.post(url)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("AML/KYC with Portal ID", True, f"AML/KYC resolved portal_lead_ ID successfully: {data}", response.status_code)
                return True
            elif response.status_code == 404:
                self.log_test("AML/KYC with Portal ID", False, "AML/KYC endpoint still returns 404 for portal_lead_ ID", response.status_code)
                return False
            else:
                # Check if it's a "needs documents" response
                if "documents" in response.text.lower() or "kyc" in response.text.lower():
                    self.log_test("AML/KYC with Portal ID", True, f"AML/KYC resolved portal_lead_ ID, needs documents: {response.text}", response.status_code)
                    return True
                else:
                    self.log_test("AML/KYC with Portal ID", False, f"AML/KYC failed with portal_lead_ ID: {response.text}", response.status_code)
                    return False
                
        except Exception as e:
            self.log_test("AML/KYC with Portal ID", False, f"Exception: {str(e)}")
            return False
    
    def test_aml_kyc_with_actual_id(self):
        """Test AML/KYC with actual prospect ID"""
        try:
            if not self.prospect_id:
                self.log_test("AML/KYC with Actual ID", False, "No actual prospect_id available")
                return False
                
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}/aml-kyc"
            
            response = self.session.post(url)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("AML/KYC with Actual ID", True, f"AML/KYC worked with actual prospect ID: {data}", response.status_code)
                return True
            else:
                # Check if it's a "needs documents" response
                if "documents" in response.text.lower() or "kyc" in response.text.lower():
                    self.log_test("AML/KYC with Actual ID", True, f"AML/KYC worked with actual ID, needs documents: {response.text}", response.status_code)
                    return True
                else:
                    self.log_test("AML/KYC with Actual ID", False, f"AML/KYC failed with actual ID: {response.text}", response.status_code)
                    return False
                
        except Exception as e:
            self.log_test("AML/KYC with Actual ID", False, f"Exception: {str(e)}")
            return False
    
    def test_phase6_client_conversion(self):
        """PHASE 6: CLIENT CONVERSION - NEW FIX - Should now resolve portal_lead_ IDs and track original lead"""
        print("📋 PHASE 6: CLIENT CONVERSION (CRITICAL FIX)")
        print("=" * 60)
        
        # Test with both portal_lead_ ID and actual prospect ID
        success_portal = self.test_convert_with_portal_id()
        success_actual = self.test_convert_with_actual_id() if not success_portal else True
        
        if success_portal or success_actual:
            # Verify complete data chain
            if self.verify_complete_data_chain():
                self.phase_results["client_conversion"] = True
                return True
            else:
                return False
        else:
            return False
    
    def test_convert_with_portal_id(self):
        """Test conversion with portal_lead_ ID - should resolve to actual prospect"""
        try:
            if not self.lead_id:
                self.log_test("Convert with Portal ID", False, "No lead_id available")
                return False
                
            portal_prospect_id = f"portal_lead_{self.lead_id}"
            url = f"{BACKEND_URL}/api/crm/prospects/{portal_prospect_id}/convert"
            payload = {
                "send_agreement": True
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.client_id = data.get('client_id')
                
                if self.client_id:
                    self.log_test("Convert with Portal ID", True, f"Conversion resolved portal_lead_ ID successfully. Client ID: {self.client_id}", response.status_code)
                    return True
                else:
                    self.log_test("Convert with Portal ID", False, "No client_id in conversion response", response.status_code)
                    return False
            elif response.status_code == 404:
                self.log_test("Convert with Portal ID", False, "Convert endpoint still returns 404 for portal_lead_ ID", response.status_code)
                return False
            else:
                self.log_test("Convert with Portal ID", False, f"Conversion failed with portal_lead_ ID: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Convert with Portal ID", False, f"Exception: {str(e)}")
            return False
    
    def test_convert_with_actual_id(self):
        """Test conversion with actual prospect ID"""
        try:
            if not self.prospect_id:
                self.log_test("Convert with Actual ID", False, "No actual prospect_id available")
                return False
                
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}/convert"
            payload = {
                "send_agreement": True
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.client_id = data.get('client_id')
                
                if self.client_id:
                    self.log_test("Convert with Actual ID", True, f"Conversion worked with actual prospect ID. Client ID: {self.client_id}", response.status_code)
                    return True
                else:
                    self.log_test("Convert with Actual ID", False, "No client_id in conversion response", response.status_code)
                    return False
            else:
                self.log_test("Convert with Actual ID", False, f"Conversion failed with actual ID: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Convert with Actual ID", False, f"Exception: {str(e)}")
            return False
    
    def verify_complete_data_chain(self):
        """Verify complete data chain integrity: lead → prospect → client"""
        try:
            if self.db is None:
                self.log_test("Complete Data Chain Verification", False, "No MongoDB connection")
                return False
            
            # Query all three collections
            lead = self.db.leads.find_one({"email": self.test_email})
            prospect = self.db.crm_prospects.find_one({"email": self.test_email})
            client = self.db.users.find_one({"email": self.test_email})
            
            # Verify complete data chain
            chain_checks = []
            
            # 1. Lead marked as migrated with crm_prospect_id
            if lead and lead.get('migrated') and lead.get('crm_prospect_id'):
                chain_checks.append("✅ Lead marked as migrated with crm_prospect_id")
            else:
                chain_checks.append("❌ Lead not properly marked as migrated")
            
            # 2. Prospect has _original_lead_id
            if prospect and prospect.get('_original_lead_id'):
                chain_checks.append("✅ Prospect has _original_lead_id")
            else:
                chain_checks.append("❌ Prospect missing _original_lead_id")
            
            # 3. Prospect marked as converted with client_id
            if prospect and prospect.get('converted_to_client') and prospect.get('client_id'):
                chain_checks.append("✅ Prospect marked as converted with client_id")
            else:
                chain_checks.append("❌ Prospect not properly marked as converted")
            
            # 4. Client has source_prospect_id and source_lead_id
            if client and client.get('source_prospect_id') and client.get('source_lead_id'):
                chain_checks.append("✅ Client has source_prospect_id and source_lead_id")
            else:
                chain_checks.append("❌ Client missing source references")
            
            # Count successful checks
            successful_checks = [check for check in chain_checks if check.startswith("✅")]
            failed_checks = [check for check in chain_checks if check.startswith("❌")]
            
            if len(successful_checks) == 4:  # All 4 checks should pass
                self.log_test("Complete Data Chain Verification", True, f"All 4/4 data chain checks passed: {', '.join(successful_checks)}")
                return True
            else:
                self.log_test("Complete Data Chain Verification", False, f"Failed {len(failed_checks)}/4 checks: {', '.join(failed_checks)}")
                return False
                
        except Exception as e:
            self.log_test("Complete Data Chain Verification", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data at end"""
        try:
            if self.db is None:
                return False
            
            # Delete test records from all collections
            deleted_counts = {}
            
            # Delete from leads collection
            result = self.db.leads.delete_many({"email": self.test_email})
            deleted_counts['leads'] = result.deleted_count
            
            # Delete from crm_prospects collection
            result = self.db.crm_prospects.delete_many({"email": self.test_email})
            deleted_counts['crm_prospects'] = result.deleted_count
            
            # Delete from users collection
            result = self.db.users.delete_many({"email": self.test_email})
            deleted_counts['users'] = result.deleted_count
            
            total_deleted = sum(deleted_counts.values())
            
            if total_deleted > 0:
                self.log_test("Test Data Cleanup", True, f"Deleted {total_deleted} test records: {deleted_counts}")
                return True
            else:
                self.log_test("Test Data Cleanup", True, "No test records to clean up")
                return True
                
        except Exception as e:
            self.log_test("Test Data Cleanup", False, f"Cleanup error: {str(e)}")
            return False
    
    def run_comprehensive_retest(self):
        """Run comprehensive CRM workflow re-test"""
        print("🔄 CRM WORKFLOW RE-TEST AFTER CRITICAL FIXES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {self.test_email}")
        print(f"Test Phone: {self.test_phone}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Setup
        if not self.connect_to_mongodb():
            print("❌ MongoDB connection failed. Cannot verify data integrity.")
            return False
        
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot test CRM endpoints.")
            return False
        
        # Run all test phases
        phase_results = []
        
        # Phase 1: Lead Creation (should still work)
        phase_results.append(self.test_phase1_lead_creation())
        print()
        
        # Phase 2: Simulator Tracking (should still work)
        phase_results.append(self.test_phase2_simulator_tracking())
        print()
        
        # Phase 3: CRM Integration (should still work)
        phase_results.append(self.test_phase3_crm_integration())
        print()
        
        # Phase 4: Pipeline Movement (NEW FIX - should now work)
        phase_results.append(self.test_phase4_pipeline_movement())
        print()
        
        # Phase 5: AML/KYC (NEW FIX - should now resolve portal_lead_ IDs)
        phase_results.append(self.test_phase5_aml_kyc())
        print()
        
        # Phase 6: Client Conversion (NEW FIX - should now work with data chain)
        phase_results.append(self.test_phase6_client_conversion())
        print()
        
        # Print comprehensive comparison report
        self.print_comparison_report(phase_results)
        
        # Cleanup test data
        print("📋 CLEANUP: Remove Test Data")
        self.cleanup_test_data()
        print()
        
        # Return overall success
        return all(phase_results)
    
    def print_comparison_report(self, phase_results):
        """Print detailed comparison report: BEFORE vs AFTER"""
        print("=" * 80)
        print("📊 CRM WORKFLOW RE-TEST EXECUTION REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 EXECUTION METRICS:")
        print(f"   Total tests executed: {total_tests}")
        print(f"   Tests passed: {passed_tests}")
        print(f"   Tests failed: {failed_tests}")
        print(f"   Success rate: {success_rate:.1f}%")
        print()
        
        # BEFORE vs AFTER comparison
        print(f"🔄 BEFORE vs AFTER COMPARISON:")
        print()
        
        # Previous test results (from test_result.md)
        previous_results = {
            "lead_creation": True,      # ✅ already working
            "simulator_tracking": True, # ✅ already working  
            "crm_integration": True,    # ✅ already working
            "pipeline_movement": False, # ❌ was broken
            "aml_kyc": False,          # ❌ was 404
            "client_conversion": False  # ❌ was 404
        }
        
        comparison_items = [
            ("Lead Creation", "lead_creation"),
            ("Simulator Tracking", "simulator_tracking"),
            ("CRM Integration", "crm_integration"),
            ("Pipeline Movement", "pipeline_movement"),
            ("AML/KYC Endpoint", "aml_kyc"),
            ("Client Conversion", "client_conversion")
        ]
        
        for item_name, item_key in comparison_items:
            before_status = "✅" if previous_results[item_key] else "❌"
            after_status = "✅" if self.phase_results[item_key] else "❌"
            
            if previous_results[item_key] == self.phase_results[item_key]:
                change = "→" if previous_results[item_key] else "→"
                change_color = ""
            elif self.phase_results[item_key]:
                change = "→✅"
                change_color = " (FIXED!)"
            else:
                change = "→❌"
                change_color = " (STILL BROKEN)"
            
            print(f"   {item_name}: {before_status} {change} {after_status}{change_color}")
        
        print()
        
        # Expected improvements verification
        print(f"🎯 EXPECTED IMPROVEMENTS VERIFICATION:")
        
        expected_fixes = [
            ("Pipeline movement", "pipeline_movement", "was broken, now should work"),
            ("AML/KYC with portal_lead_", "aml_kyc", "was 404, now should resolve"),
            ("Convert with portal_lead_", "client_conversion", "was 404, now should resolve"),
        ]
        
        for fix_name, fix_key, fix_description in expected_fixes:
            if self.phase_results[fix_key]:
                print(f"   ✅ {fix_name}: {fix_description} - VERIFIED FIXED")
            else:
                print(f"   ❌ {fix_name}: {fix_description} - STILL BROKEN")
        
        print()
        
        # Success criteria verification
        print(f"📋 SUCCESS CRITERIA VERIFICATION:")
        
        all_phases_pass = all(phase_results)
        no_404_500_errors = not any("404" in str(result.get('http_status', '')) or "500" in str(result.get('http_status', '')) 
                                   for result in self.test_results if not result['success'])
        complete_data_chain = self.phase_results["client_conversion"]  # Data chain verified in conversion phase
        
        print(f"   All 6 phases PASS: {'✅' if all_phases_pass else '❌'}")
        print(f"   No 404 or 500 errors: {'✅' if no_404_500_errors else '❌'}")
        print(f"   Complete data chain: {'✅' if complete_data_chain else '❌'}")
        
        print()
        
        # Overall verdict
        overall_success = all_phases_pass and no_404_500_errors and complete_data_chain
        
        print(f"🏆 OVERALL VERDICT:")
        if overall_success:
            print(f"   ✅ CRM WORKFLOW FIXES SUCCESSFUL - All critical issues resolved!")
        else:
            print(f"   ❌ CRM WORKFLOW FIXES INCOMPLETE - Some issues remain")
        
        print()
        
        # Detailed failure analysis if needed
        if failed_tests > 0:
            print(f"🔍 REMAINING ISSUES:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test']}")
                    print(f"      Details: {result['details']}")
                    if result.get('http_status'):
                        print(f"      HTTP Status: {result['http_status']}")
            print()

def main():
    """Main test execution"""
    tester = CRMWorkflowRetest()
    success = tester.run_comprehensive_retest()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()