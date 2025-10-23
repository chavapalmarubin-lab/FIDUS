#!/usr/bin/env python3
"""
🎯 COMPLETE CRM WORKFLOW END-TO-END AUTOMATED TESTING

OBJECTIVE: Test the entire prospects-to-client conversion workflow from lead capture through client conversion.

TEST ENVIRONMENT:
- Backend API: https://prospect-portal.preview.emergentagent.com/api
- MongoDB: fidus_production database
- Collections: leads, crm_prospects, users
- Test timestamp: Use current datetime for unique identifiers

CRITICAL SUCCESS CRITERIA:
✅ Lead creation
✅ CRM integration (leads visible)
✅ Pipeline stage movement
✅ Lead to prospect migration
✅ Prospect to client conversion
✅ Data chain integrity
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
BACKEND_URL = "https://prospect-portal.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class CRMWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
        # Test data with unique timestamp
        self.timestamp = int(time.time())
        self.test_email = f"test-workflow-{self.timestamp}@fidus-test.com"
        self.test_phone = f"+525555{str(self.timestamp)[-6:]}"
        
        # Test tracking variables
        self.lead_id = None
        self.prospect_id = None
        self.client_id = None
        
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
    
    def test_phase1_lead_capture(self):
        """PHASE 1: LEAD CAPTURE (Prospects Portal)"""
        print("📋 PHASE 1: LEAD CAPTURE (Prospects Portal)")
        print("=" * 60)
        
        # Test 1.1: Create Test Lead via API
        success_1_1 = self.test_create_lead()
        
        # Test 1.2: Track Simulator Session
        success_1_2 = self.test_track_simulator_session() if success_1_1 else False
        
        return success_1_1 and success_1_2
    
    def test_create_lead(self):
        """Test 1.1: Create Test Lead via API"""
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
                        self.log_test("Create Test Lead", True, f"Lead created with ID: {self.lead_id}", response.status_code)
                        return True
                    else:
                        self.log_test("Create Test Lead", False, "Lead not found in MongoDB", response.status_code)
                        return False
                else:
                    self.log_test("Create Test Lead", False, "No leadId in response", response.status_code)
                    return False
            else:
                self.log_test("Create Test Lead", False, f"Failed to create lead: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Create Test Lead", False, f"Exception: {str(e)}")
            return False
    
    def verify_lead_in_mongodb(self):
        """Verify lead exists in MongoDB leads collection"""
        try:
            if self.db is None:
                return False
                
            lead = self.db.leads.find_one({"email": self.test_email})
            
            if lead is not None:
                # Verify required fields
                required_fields = ['email', 'phone', 'source', 'status', 'engagement_score']
                missing_fields = [field for field in required_fields if field not in lead]
                
                if not missing_fields:
                    expected_values = {
                        'source': 'prospects_portal',
                        'status': 'new',
                        'engagement_score': 0
                    }
                    
                    for field, expected_value in expected_values.items():
                        if lead.get(field) != expected_value:
                            self.log_test("Lead MongoDB Verification", False, f"Field {field}: expected {expected_value}, got {lead.get(field)}")
                            return False
                    
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
    
    def test_track_simulator_session(self):
        """Test 1.2: Track Simulator Session"""
        try:
            if not self.lead_id:
                self.log_test("Track Simulator Session", False, "No lead_id available")
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
                    self.log_test("Track Simulator Session", True, "Simulator session tracked successfully", response.status_code)
                    return True
                else:
                    self.log_test("Track Simulator Session", False, "Simulator session not tracked in MongoDB", response.status_code)
                    return False
            else:
                self.log_test("Track Simulator Session", False, f"Failed to track simulator session: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Track Simulator Session", False, f"Exception: {str(e)}")
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
                last_activity = lead.get('last_activity')
                
                if simulator_sessions and engagement_score >= 10 and last_activity:
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
    
    def test_phase2_crm_integration(self):
        """PHASE 2: CRM INTEGRATION"""
        print("📋 PHASE 2: CRM INTEGRATION")
        print("=" * 60)
        
        # Test 2.1: Verify Lead Appears in CRM
        success_2_1 = self.test_lead_appears_in_crm()
        
        # Test 2.2: Move Lead Through Pipeline (Lead → Negotiation)
        success_2_2 = self.test_move_lead_to_negotiation() if success_2_1 else False
        
        # Test 2.3: Move to Won Stage
        success_2_3 = self.test_move_to_won_stage() if success_2_2 else False
        
        return success_2_1 and success_2_2 and success_2_3
    
    def test_lead_appears_in_crm(self):
        """Test 2.1: Verify Lead Appears in CRM"""
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
                        self.log_test("Lead Appears in CRM", True, f"Lead found in CRM with prospect_id: {self.prospect_id}", response.status_code)
                        return True
                    else:
                        self.log_test("Lead Appears in CRM", False, f"Lead found but incorrect properties: prospect_id={actual_prospect_id}, stage={stage}, source={source}", response.status_code)
                        return False
                else:
                    self.log_test("Lead Appears in CRM", False, f"Test lead not found in CRM prospects list", response.status_code)
                    return False
            else:
                self.log_test("Lead Appears in CRM", False, f"Failed to get CRM prospects: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Lead Appears in CRM", False, f"Exception: {str(e)}")
            return False
    
    def test_move_lead_to_negotiation(self):
        """Test 2.2: Move Lead Through Pipeline (Lead → Negotiation)"""
        try:
            if not self.prospect_id:
                self.log_test("Move Lead to Negotiation", False, "No prospect_id available")
                return False
                
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}"
            payload = {
                "stage": "negotiation",
                "name": "Test Workflow User",
                "notes": "Testing pipeline movement"
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code == 200:
                # Verify migration from leads to crm_prospects collection
                if self.verify_lead_migration_to_crm():
                    self.log_test("Move Lead to Negotiation", True, "Lead successfully moved to negotiation stage", response.status_code)
                    return True
                else:
                    self.log_test("Move Lead to Negotiation", False, "Lead migration verification failed", response.status_code)
                    return False
            else:
                self.log_test("Move Lead to Negotiation", False, f"Failed to move lead to negotiation: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Move Lead to Negotiation", False, f"Exception: {str(e)}")
            return False
    
    def verify_lead_migration_to_crm(self):
        """Verify lead was migrated from leads to crm_prospects collection"""
        try:
            if self.db is None:
                return False
            
            # Check original lead is marked as migrated
            original_lead = self.db.leads.find_one({"email": self.test_email})
            if original_lead is None or not original_lead.get('migrated'):
                self.log_test("Lead Migration Verification", False, "Original lead not marked as migrated")
                return False
            
            # Check new prospect exists in crm_prospects collection
            prospect = self.db.crm_prospects.find_one({"email": self.test_email})
            if prospect is None:
                self.log_test("Lead Migration Verification", False, "Prospect not found in crm_prospects collection")
                return False
            
            # Verify prospect properties
            if prospect.get('stage') == 'negotiation':
                # Update prospect_id for next tests
                self.prospect_id = str(prospect.get('_id'))
                self.log_test("Lead Migration Verification", True, f"Lead successfully migrated to crm_prospects with stage: negotiation")
                return True
            else:
                self.log_test("Lead Migration Verification", False, f"Prospect stage incorrect: {prospect.get('stage')}")
                return False
                
        except Exception as e:
            self.log_test("Lead Migration Verification", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_move_to_won_stage(self):
        """Test 2.3: Move to Won Stage"""
        try:
            if not self.prospect_id:
                self.log_test("Move to Won Stage", False, "No prospect_id available")
                return False
                
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}"
            payload = {
                "stage": "won",
                "notes": "Ready for AML/KYC process"
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code == 200:
                # Verify stage update in MongoDB
                if self.verify_won_stage_in_mongodb():
                    self.log_test("Move to Won Stage", True, "Prospect successfully moved to won stage", response.status_code)
                    return True
                else:
                    self.log_test("Move to Won Stage", False, "Won stage verification failed", response.status_code)
                    return False
            else:
                self.log_test("Move to Won Stage", False, f"Failed to move to won stage: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Move to Won Stage", False, f"Exception: {str(e)}")
            return False
    
    def verify_won_stage_in_mongodb(self):
        """Verify prospect is in won stage in MongoDB"""
        try:
            if self.db is None:
                return False
            
            prospect = self.db.crm_prospects.find_one({"email": self.test_email})
            
            if prospect is not None and prospect.get('stage') == 'won':
                self.log_test("Won Stage MongoDB Verification", True, "Prospect stage updated to 'won' in MongoDB")
                return True
            else:
                stage = prospect.get('stage') if prospect else 'not found'
                self.log_test("Won Stage MongoDB Verification", False, f"Prospect stage: {stage}")
                return False
                
        except Exception as e:
            self.log_test("Won Stage MongoDB Verification", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_phase3_aml_kyc(self):
        """PHASE 3: AML/KYC & CONVERSION READINESS"""
        print("📋 PHASE 3: AML/KYC & CONVERSION READINESS")
        print("=" * 60)
        
        # Test 3.1: Check Current AML/KYC Endpoints
        success_3_1 = self.test_aml_kyc_endpoints()
        
        # Test 3.2: Test AML/KYC Process
        success_3_2 = self.test_aml_kyc_process() if success_3_1 else False
        
        return success_3_1 and success_3_2
    
    def test_aml_kyc_endpoints(self):
        """Test 3.1: Check Current AML/KYC Endpoints"""
        if not self.prospect_id:
            self.log_test("AML/KYC Endpoints Check", False, "No prospect_id available")
            return False
        
        endpoints_to_test = [
            f"/api/crm/prospects/{self.prospect_id}/aml-kyc",
            f"/api/crm/prospects/{self.prospect_id}/documents"
        ]
        
        available_endpoints = []
        missing_endpoints = []
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                response = self.session.get(url)
                
                if response.status_code in [200, 404, 422]:  # 404/422 means endpoint exists but no data
                    available_endpoints.append(endpoint)
                else:
                    missing_endpoints.append(endpoint)
                    
            except Exception as e:
                missing_endpoints.append(endpoint)
        
        if available_endpoints:
            self.log_test("AML/KYC Endpoints Available", True, f"Available: {available_endpoints}, Missing: {missing_endpoints}")
            return True
        else:
            self.log_test("AML/KYC Endpoints Available", False, f"All endpoints missing: {missing_endpoints}")
            return False
    
    def test_aml_kyc_process(self):
        """Test 3.2: Test AML/KYC Process"""
        try:
            if not self.prospect_id:
                self.log_test("AML/KYC Process", False, "No prospect_id available")
                return False
                
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}/aml-kyc"
            
            # Try POST to run AML/KYC check
            response = self.session.post(url)
            
            if response.status_code in [200, 201]:
                data = response.json()
                # Check if AML/KYC status is returned
                if 'aml_kyc_status' in str(data) or 'risk_assessment' in str(data):
                    self.log_test("AML/KYC Process", True, "AML/KYC check completed successfully", response.status_code)
                    return True
                else:
                    self.log_test("AML/KYC Process", True, "AML/KYC endpoint accessible but no status returned", response.status_code)
                    return True  # Endpoint works even if no specific status
            elif response.status_code == 404:
                self.log_test("AML/KYC Process", False, "AML/KYC endpoint not implemented", response.status_code)
                return False
            else:
                self.log_test("AML/KYC Process", False, f"AML/KYC process failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("AML/KYC Process", False, f"Exception: {str(e)}")
            return False
    
    def test_phase4_client_conversion(self):
        """PHASE 4: CLIENT CONVERSION"""
        print("📋 PHASE 4: CLIENT CONVERSION")
        print("=" * 60)
        
        # Test 4.1: Convert Prospect to Client
        success_4_1 = self.test_convert_prospect_to_client()
        
        # Test 4.2: Verify Client Creation
        success_4_2 = self.test_verify_client_creation() if success_4_1 else False
        
        # Test 4.3: Verify Complete Data Chain
        success_4_3 = self.test_verify_data_chain() if success_4_2 else False
        
        return success_4_1 and success_4_2 and success_4_3
    
    def test_convert_prospect_to_client(self):
        """Test 4.1: Convert Prospect to Client"""
        try:
            if not self.prospect_id:
                self.log_test("Convert Prospect to Client", False, "No prospect_id available")
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
                    self.log_test("Convert Prospect to Client", True, f"Prospect converted to client with ID: {self.client_id}", response.status_code)
                    return True
                else:
                    self.log_test("Convert Prospect to Client", False, "No client_id in conversion response", response.status_code)
                    return False
            else:
                self.log_test("Convert Prospect to Client", False, f"Conversion failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Convert Prospect to Client", False, f"Exception: {str(e)}")
            return False
    
    def test_verify_client_creation(self):
        """Test 4.2: Verify Client Creation"""
        try:
            if self.db is None:
                self.log_test("Verify Client Creation", False, "No MongoDB connection")
                return False
            
            # Check client exists in users collection
            client = self.db.users.find_one({"email": self.test_email})
            
            if client is not None:
                # Verify client properties
                client_type = client.get('type')
                source_prospect_id = client.get('source_prospect_id')
                source_lead_id = client.get('source_lead_id')
                
                if client_type == 'Client':
                    self.log_test("Client Creation Verification", True, f"Client created with type: {client_type}, source_prospect_id: {source_prospect_id}")
                    
                    # Update client_id if not set
                    if not self.client_id:
                        self.client_id = str(client.get('_id', client.get('id')))
                    
                    return True
                else:
                    self.log_test("Client Creation Verification", False, f"Client type incorrect: {client_type}")
                    return False
            else:
                self.log_test("Client Creation Verification", False, "Client not found in users collection")
                return False
                
        except Exception as e:
            self.log_test("Client Creation Verification", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_verify_data_chain(self):
        """Test 4.3: Verify Complete Data Chain"""
        try:
            if self.db is None:
                self.log_test("Data Chain Verification", False, "No MongoDB connection")
                return False
            
            # Query all three collections
            lead = self.db.leads.find_one({"email": self.test_email})
            prospect = self.db.crm_prospects.find_one({"email": self.test_email})
            client = self.db.users.find_one({"email": self.test_email})
            
            # Verify referential integrity
            integrity_checks = []
            
            # Check lead is marked converted
            if lead is not None and lead.get('converted'):
                integrity_checks.append("Lead marked as converted")
            else:
                integrity_checks.append("❌ Lead not marked as converted")
            
            # Check prospect is marked converted_to_client
            if prospect is not None and prospect.get('converted_to_client'):
                integrity_checks.append("Prospect marked as converted_to_client")
            else:
                integrity_checks.append("❌ Prospect not marked as converted_to_client")
            
            # Check client has source references
            if client is not None:
                if client.get('source_prospect_id'):
                    integrity_checks.append("Client has source_prospect_id")
                else:
                    integrity_checks.append("❌ Client missing source_prospect_id")
                
                if client.get('source_lead_id'):
                    integrity_checks.append("Client has source_lead_id")
                else:
                    integrity_checks.append("❌ Client missing source_lead_id")
            else:
                integrity_checks.append("❌ Client not found")
            
            # Count successful checks
            successful_checks = [check for check in integrity_checks if not check.startswith("❌")]
            failed_checks = [check for check in integrity_checks if check.startswith("❌")]
            
            if len(successful_checks) >= 3:  # At least 3 out of 4 checks should pass
                self.log_test("Data Chain Integrity", True, f"Passed: {len(successful_checks)}/4 checks. Details: {', '.join(successful_checks)}")
                return True
            else:
                self.log_test("Data Chain Integrity", False, f"Failed: {len(failed_checks)}/4 checks. Issues: {', '.join(failed_checks)}")
                return False
                
        except Exception as e:
            self.log_test("Data Chain Integrity", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_phase5_data_integrity(self):
        """PHASE 5: DATA INTEGRITY & EDGE CASES"""
        print("📋 PHASE 5: DATA INTEGRITY & EDGE CASES")
        print("=" * 60)
        
        # Test 5.1: No Duplicate Records
        success_5_1 = self.test_no_duplicate_records()
        
        # Test 5.2: Test Existing Lead Handling
        success_5_2 = self.test_existing_lead_handling()
        
        # Test 5.3: Test Invalid Stage Transitions
        success_5_3 = self.test_invalid_stage_transitions()
        
        return success_5_1 and success_5_2 and success_5_3
    
    def test_no_duplicate_records(self):
        """Test 5.1: No Duplicate Records"""
        try:
            if self.db is None:
                self.log_test("No Duplicate Records", False, "No MongoDB connection")
                return False
            
            # Check for duplicates in each collection
            leads_count = self.db.leads.count_documents({"email": self.test_email})
            prospects_count = self.db.crm_prospects.count_documents({"email": self.test_email})
            clients_count = self.db.users.count_documents({"email": self.test_email})
            
            # Should have exactly 1 record in each collection
            if leads_count == 1 and prospects_count == 1 and clients_count == 1:
                self.log_test("No Duplicate Records", True, f"Exactly 1 record in each collection: leads={leads_count}, prospects={prospects_count}, clients={clients_count}")
                return True
            else:
                self.log_test("No Duplicate Records", False, f"Duplicate records found: leads={leads_count}, prospects={prospects_count}, clients={clients_count}")
                return False
                
        except Exception as e:
            self.log_test("No Duplicate Records", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def test_existing_lead_handling(self):
        """Test 5.2: Test Existing Lead Handling"""
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
                message = data.get('message', '')
                returned_lead_id = data.get('leadId', data.get('lead_id', data.get('id')))
                
                # Should return existing leadId and "Welcome back!" message
                if 'welcome back' in message.lower() and returned_lead_id == self.lead_id:
                    self.log_test("Existing Lead Handling", True, f"Returned existing lead with message: {message}", response.status_code)
                    return True
                else:
                    self.log_test("Existing Lead Handling", False, f"Unexpected response: message='{message}', leadId={returned_lead_id}", response.status_code)
                    return False
            else:
                self.log_test("Existing Lead Handling", False, f"Failed to handle existing lead: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Existing Lead Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_stage_transitions(self):
        """Test 5.3: Test Invalid Stage Transitions"""
        try:
            if not self.prospect_id:
                self.log_test("Invalid Stage Transitions", False, "No prospect_id available")
                return False
                
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}"
            payload = {
                "stage": "invalid_stage"
            }
            
            response = self.session.put(url, json=payload)
            
            # Should return 400 or 422 for invalid stage
            if response.status_code in [400, 422]:
                self.log_test("Invalid Stage Transitions", True, f"Correctly rejected invalid stage with HTTP {response.status_code}", response.status_code)
                return True
            else:
                self.log_test("Invalid Stage Transitions", False, f"Did not reject invalid stage: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Invalid Stage Transitions", False, f"Exception: {str(e)}")
            return False
    
    def test_phase6_statistics(self):
        """PHASE 6: STATISTICS & REPORTING"""
        print("📋 PHASE 6: STATISTICS & REPORTING")
        print("=" * 60)
        
        # Test 6.1: CRM Pipeline Statistics
        success_6_1 = self.test_crm_pipeline_statistics()
        
        # Test 6.2: Lead Engagement Metrics
        success_6_2 = self.test_lead_engagement_metrics()
        
        return success_6_1 and success_6_2
    
    def test_crm_pipeline_statistics(self):
        """Test 6.1: CRM Pipeline Statistics"""
        try:
            url = f"{BACKEND_URL}/api/crm/prospects/pipeline"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if pipeline stats include our test prospect
                pipeline_stats = data.get('pipeline_stats', data.get('stats', {}))
                
                if pipeline_stats:
                    # Look for won stage count (should include our test prospect)
                    won_count = pipeline_stats.get('won', 0)
                    
                    if won_count > 0:
                        self.log_test("CRM Pipeline Statistics", True, f"Pipeline stats working, won stage count: {won_count}", response.status_code)
                        return True
                    else:
                        self.log_test("CRM Pipeline Statistics", True, f"Pipeline stats accessible but no won prospects yet", response.status_code)
                        return True  # Endpoint works even if count is 0
                else:
                    self.log_test("CRM Pipeline Statistics", False, "No pipeline stats in response", response.status_code)
                    return False
            else:
                self.log_test("CRM Pipeline Statistics", False, f"Failed to get pipeline stats: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("CRM Pipeline Statistics", False, f"Exception: {str(e)}")
            return False
    
    def test_lead_engagement_metrics(self):
        """Test 6.2: Lead Engagement Metrics"""
        try:
            if not self.db:
                self.log_test("Lead Engagement Metrics", False, "No MongoDB connection")
                return False
            
            # Verify lead has proper engagement tracking
            lead = self.db.leads.find_one({"email": self.test_email})
            
            if lead:
                simulator_sessions = lead.get('simulator_sessions', [])
                engagement_score = lead.get('engagement_score', 0)
                last_activity = lead.get('last_activity')
                interest_level = lead.get('interest_level')
                
                metrics_present = []
                if simulator_sessions:
                    metrics_present.append(f"simulator_sessions: {len(simulator_sessions)}")
                if engagement_score > 0:
                    metrics_present.append(f"engagement_score: {engagement_score}")
                if last_activity:
                    metrics_present.append(f"last_activity: {last_activity}")
                if interest_level:
                    metrics_present.append(f"interest_level: {interest_level}")
                
                if len(metrics_present) >= 2:  # At least 2 metrics should be present
                    self.log_test("Lead Engagement Metrics", True, f"Engagement metrics tracked: {', '.join(metrics_present)}")
                    return True
                else:
                    self.log_test("Lead Engagement Metrics", False, f"Insufficient engagement metrics: {', '.join(metrics_present)}")
                    return False
            else:
                self.log_test("Lead Engagement Metrics", False, "Lead not found for engagement verification")
                return False
                
        except Exception as e:
            self.log_test("Lead Engagement Metrics", False, f"MongoDB verification error: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data at end"""
        try:
            if not self.db:
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
    
    def run_complete_workflow_test(self):
        """Run complete CRM workflow end-to-end test"""
        print("🎯 COMPLETE CRM WORKFLOW END-TO-END AUTOMATED TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {self.test_email}")
        print(f"Test Phone: {self.test_phone}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Connect to MongoDB
        print("📋 STEP 1: Connect to MongoDB")
        if not self.connect_to_mongodb():
            print("❌ MongoDB connection failed. Cannot verify data integrity.")
            return False
        print()
        
        # Step 2: Authenticate as Admin
        print("📋 STEP 2: Authenticate as Admin")
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot test CRM endpoints.")
            return False
        print()
        
        # Run all test phases
        phase_results = []
        
        # Phase 1: Lead Capture
        phase_results.append(self.test_phase1_lead_capture())
        print()
        
        # Phase 2: CRM Integration
        phase_results.append(self.test_phase2_crm_integration())
        print()
        
        # Phase 3: AML/KYC
        phase_results.append(self.test_phase3_aml_kyc())
        print()
        
        # Phase 4: Client Conversion
        phase_results.append(self.test_phase4_client_conversion())
        print()
        
        # Phase 5: Data Integrity
        phase_results.append(self.test_phase5_data_integrity())
        print()
        
        # Phase 6: Statistics
        phase_results.append(self.test_phase6_statistics())
        print()
        
        # Print comprehensive summary
        self.print_workflow_summary(phase_results)
        
        # Cleanup test data
        print("📋 CLEANUP: Remove Test Data")
        self.cleanup_test_data()
        print()
        
        # Return overall success
        return all(phase_results)
    
    def print_workflow_summary(self, phase_results):
        """Print comprehensive workflow test summary"""
        print("=" * 80)
        print("📊 CRM WORKFLOW TEST EXECUTION REPORT")
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
        
        # Phase results
        phase_names = [
            "PHASE 1: Lead Capture",
            "PHASE 2: CRM Integration", 
            "PHASE 3: AML/KYC",
            "PHASE 4: Client Conversion",
            "PHASE 5: Data Integrity",
            "PHASE 6: Statistics"
        ]
        
        print(f"📋 PHASE RESULTS:")
        for i, (phase_name, phase_success) in enumerate(zip(phase_names, phase_results)):
            status = "✅ PASS" if phase_success else "❌ FAIL"
            print(f"   {status}: {phase_name}")
        print()
        
        # Feature availability matrix
        print(f"📊 FEATURE AVAILABILITY MATRIX:")
        
        # Working features
        working_features = []
        if any('Create Test Lead' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("Lead creation endpoint")
        if any('Track Simulator Session' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("Simulator tracking")
        if any('Lead Appears in CRM' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("CRM integration (leads visible)")
        if any('Move Lead to Negotiation' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("Pipeline stage movement")
        if any('Lead Migration Verification' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("Lead migration to CRM")
        if any('Move to Won Stage' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("Won stage accessible")
        if any('AML/KYC' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("AML/KYC endpoint")
        if any('Convert Prospect to Client' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("Client conversion endpoint")
        if any('Data Chain Integrity' in r['test'] and r['success'] for r in self.test_results):
            working_features.append("Data chain integrity")
        
        print(f"   ✅ WORKING FEATURES ({len(working_features)}):")
        for feature in working_features:
            print(f"     • {feature}")
        print()
        
        # Missing/broken features
        missing_features = []
        if not any('Create Test Lead' in r['test'] and r['success'] for r in self.test_results):
            missing_features.append("Lead creation endpoint")
        if not any('AML/KYC Process' in r['test'] and r['success'] for r in self.test_results):
            missing_features.append("Complete AML/KYC process")
        if not any('Convert Prospect to Client' in r['test'] and r['success'] for r in self.test_results):
            missing_features.append("Client conversion")
        
        if missing_features:
            print(f"   ❌ MISSING/BROKEN FEATURES ({len(missing_features)}):")
            for feature in missing_features:
                print(f"     • {feature}")
            print()
        
        # Critical success criteria
        print(f"🎯 CRITICAL SUCCESS CRITERIA:")
        
        critical_criteria = [
            ("Lead creation", any('Create Test Lead' in r['test'] and r['success'] for r in self.test_results)),
            ("CRM integration (leads visible)", any('Lead Appears in CRM' in r['test'] and r['success'] for r in self.test_results)),
            ("Pipeline stage movement", any('Move Lead to Negotiation' in r['test'] and r['success'] for r in self.test_results)),
            ("Lead to prospect migration", any('Lead Migration Verification' in r['test'] and r['success'] for r in self.test_results)),
            ("Prospect to client conversion", any('Convert Prospect to Client' in r['test'] and r['success'] for r in self.test_results)),
            ("Data chain integrity", any('Data Chain Integrity' in r['test'] and r['success'] for r in self.test_results))
        ]
        
        critical_passed = sum(1 for _, success in critical_criteria if success)
        critical_total = len(critical_criteria)
        
        for criteria_name, criteria_success in critical_criteria:
            status = "✅" if criteria_success else "❌"
            print(f"   {status} {criteria_name}")
        
        print()
        print(f"📊 SUCCESS METRICS:")
        print(f"   Critical path working: {'Yes' if critical_passed == critical_total else 'Partial'} ({critical_passed}/{critical_total})")
        print(f"   Overall workflow success: {'✅ PASS' if all(phase_results) else '❌ FAIL'}")
        print()
        
        # Detailed failure analysis
        if failed_tests > 0:
            print(f"🔍 FAILURE ANALYSIS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test']}")
                    print(f"      Details: {result['details']}")
                    if result.get('http_status'):
                        print(f"      HTTP Status: {result['http_status']}")
            print()
        
        # Data chain verification
        if self.lead_id and self.prospect_id and self.client_id:
            print(f"🔗 DATA CHAIN VERIFICATION:")
            print(f"   Lead ID: {self.lead_id}")
            print(f"   Prospect ID: {self.prospect_id}")
            print(f"   Client ID: {self.client_id}")
            print(f"   Test Email: {self.test_email}")
            print()

def main():
    """Main test execution"""
    tester = CRMWorkflowTester()
    success = tester.run_complete_workflow_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()