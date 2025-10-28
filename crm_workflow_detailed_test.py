#!/usr/bin/env python3
"""
🔍 DETAILED CRM WORKFLOW INVESTIGATION

This test will investigate the specific issues found in the re-test:
1. Pipeline movement not marking leads as migrated
2. Conversion requiring "won" stage
3. Data chain integrity issues

We'll test step-by-step to identify exactly where the fixes are working and where they're not.
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
BACKEND_URL = "https://oauth-debugger.preview.emergentagent.com"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB connection
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"

class DetailedCRMTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.mongo_client = None
        self.db = None
        
        # Test data with unique timestamp
        self.timestamp = int(time.time())
        self.test_email = f"detailed-test-{self.timestamp}@fidus-test.com"
        self.test_phone = f"+525555{str(self.timestamp)[-6:]}"
        
        # Test tracking variables
        self.lead_id = None
        self.prospect_id = None
        self.client_id = None
        
    def setup(self):
        """Setup MongoDB and authentication"""
        try:
            # Connect to MongoDB
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client['fidus_production']
            self.mongo_client.admin.command('ping')
            print("✅ MongoDB connected")
            
            # Authenticate as admin
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
                    print("✅ Admin authenticated")
                    return True
            
            print("❌ Admin authentication failed")
            return False
            
        except Exception as e:
            print(f"❌ Setup failed: {str(e)}")
            return False
    
    def create_test_lead(self):
        """Create a test lead"""
        try:
            print("\n📋 STEP 1: Creating test lead")
            
            url = f"{BACKEND_URL}/api/prospects/lead"
            payload = {
                "email": self.test_email,
                "phone": self.test_phone,
                "source": "prospects_portal"
            }
            
            response = self.session.post(url, json=payload)
            print(f"   Lead creation response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.lead_id = data.get('leadId', data.get('lead_id', data.get('id')))
                print(f"   ✅ Lead created with ID: {self.lead_id}")
                
                # Check in MongoDB
                lead = self.db.leads.find_one({"email": self.test_email})
                if lead:
                    print(f"   ✅ Lead found in MongoDB: {lead.get('_id')}")
                    print(f"   Lead status: {lead.get('status')}")
                    print(f"   Lead migrated: {lead.get('migrated', False)}")
                    return True
                else:
                    print("   ❌ Lead not found in MongoDB")
                    return False
            else:
                print(f"   ❌ Lead creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False
    
    def check_crm_integration(self):
        """Check if lead appears in CRM"""
        try:
            print("\n📋 STEP 2: Checking CRM integration")
            
            url = f"{BACKEND_URL}/api/crm/prospects"
            response = self.session.get(url)
            print(f"   CRM prospects response: {response.status_code}")
            
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
                    self.prospect_id = test_prospect.get('prospect_id')
                    print(f"   ✅ Lead found in CRM with prospect_id: {self.prospect_id}")
                    print(f"   Prospect stage: {test_prospect.get('stage')}")
                    print(f"   Prospect source: {test_prospect.get('source')}")
                    return True
                else:
                    print("   ❌ Test lead not found in CRM prospects list")
                    return False
            else:
                print(f"   ❌ Failed to get CRM prospects: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False
    
    def test_pipeline_movement_step_by_step(self):
        """Test pipeline movement step by step"""
        try:
            print("\n📋 STEP 3: Testing pipeline movement step by step")
            
            if not self.prospect_id:
                print("   ❌ No prospect_id available")
                return False
            
            # Step 3.1: Move to negotiation
            print("\n   3.1: Moving to negotiation stage")
            url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}"
            payload = {
                "stage": "negotiation",
                "name": "Detailed Test User",
                "notes": "Testing pipeline movement to negotiation"
            }
            
            response = self.session.put(url, json=payload)
            print(f"   Pipeline update response: {response.status_code}")
            print(f"   Response body: {response.text}")
            
            if response.status_code == 200:
                print("   ✅ Pipeline update API call successful")
                
                # Check MongoDB state after negotiation update
                self.check_mongodb_state_after_update("negotiation")
                
                # Step 3.2: Move to won
                print("\n   3.2: Moving to won stage")
                payload = {
                    "stage": "won",
                    "notes": "Testing pipeline movement to won"
                }
                
                response = self.session.put(url, json=payload)
                print(f"   Won stage update response: {response.status_code}")
                print(f"   Response body: {response.text}")
                
                if response.status_code == 200:
                    print("   ✅ Won stage update API call successful")
                    
                    # Check MongoDB state after won update
                    self.check_mongodb_state_after_update("won")
                    return True
                else:
                    print(f"   ❌ Won stage update failed: {response.text}")
                    return False
            else:
                print(f"   ❌ Negotiation stage update failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False
    
    def check_mongodb_state_after_update(self, expected_stage):
        """Check MongoDB state after pipeline update"""
        try:
            print(f"\n   📊 MongoDB state check after {expected_stage} update:")
            
            # Check leads collection
            lead = self.db.leads.find_one({"email": self.test_email})
            if lead:
                print(f"   Lead collection:")
                print(f"     - _id: {lead.get('_id')}")
                print(f"     - status: {lead.get('status')}")
                print(f"     - migrated: {lead.get('migrated', False)}")
                print(f"     - crm_prospect_id: {lead.get('crm_prospect_id', 'None')}")
            else:
                print("   ❌ Lead not found in leads collection")
            
            # Check crm_prospects collection
            prospect = self.db.crm_prospects.find_one({"email": self.test_email})
            if prospect:
                print(f"   CRM Prospects collection:")
                print(f"     - _id: {prospect.get('_id')}")
                print(f"     - stage: {prospect.get('stage')}")
                print(f"     - _original_lead_id: {prospect.get('_original_lead_id', 'None')}")
                print(f"     - converted_to_client: {prospect.get('converted_to_client', False)}")
                print(f"     - client_id: {prospect.get('client_id', 'None')}")
                
                # Update prospect_id to actual MongoDB _id for future operations
                self.prospect_id = str(prospect.get('_id'))
                print(f"     - Updated prospect_id to: {self.prospect_id}")
            else:
                print("   ❌ Prospect not found in crm_prospects collection")
            
            # Check users collection
            client = self.db.users.find_one({"email": self.test_email})
            if client:
                print(f"   Users collection:")
                print(f"     - _id: {client.get('_id')}")
                print(f"     - type: {client.get('type')}")
                print(f"     - source_prospect_id: {client.get('source_prospect_id', 'None')}")
                print(f"     - source_lead_id: {client.get('source_lead_id', 'None')}")
            else:
                print("   No client record found in users collection (expected at this stage)")
                
        except Exception as e:
            print(f"   ❌ MongoDB state check error: {str(e)}")
    
    def test_aml_kyc_endpoints(self):
        """Test AML/KYC endpoints with both portal_lead_ and actual IDs"""
        try:
            print("\n📋 STEP 4: Testing AML/KYC endpoints")
            
            # Test 4.1: AML/KYC with portal_lead_ ID
            print("\n   4.1: Testing AML/KYC with portal_lead_ ID")
            portal_prospect_id = f"portal_lead_{self.lead_id}"
            url = f"{BACKEND_URL}/api/crm/prospects/{portal_prospect_id}/aml-kyc"
            
            response = self.session.post(url)
            print(f"   AML/KYC portal_lead_ response: {response.status_code}")
            print(f"   Response body: {response.text[:200]}...")
            
            if response.status_code in [200, 201]:
                print("   ✅ AML/KYC with portal_lead_ ID successful")
            else:
                print(f"   ❌ AML/KYC with portal_lead_ ID failed")
            
            # Test 4.2: AML/KYC with actual prospect ID
            print("\n   4.2: Testing AML/KYC with actual prospect ID")
            if self.prospect_id:
                url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}/aml-kyc"
                
                response = self.session.post(url)
                print(f"   AML/KYC actual ID response: {response.status_code}")
                print(f"   Response body: {response.text[:200]}...")
                
                if response.status_code in [200, 201]:
                    print("   ✅ AML/KYC with actual prospect ID successful")
                    return True
                else:
                    print(f"   ❌ AML/KYC with actual prospect ID failed")
            else:
                print("   ❌ No actual prospect ID available")
            
            return False
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False
    
    def test_client_conversion_endpoints(self):
        """Test client conversion endpoints with both portal_lead_ and actual IDs"""
        try:
            print("\n📋 STEP 5: Testing client conversion endpoints")
            
            # Test 5.1: Conversion with portal_lead_ ID
            print("\n   5.1: Testing conversion with portal_lead_ ID")
            portal_prospect_id = f"portal_lead_{self.lead_id}"
            url = f"{BACKEND_URL}/api/crm/prospects/{portal_prospect_id}/convert"
            payload = {"send_agreement": True}
            
            response = self.session.post(url, json=payload)
            print(f"   Conversion portal_lead_ response: {response.status_code}")
            print(f"   Response body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                client_id = data.get('client_id')
                if client_id:
                    self.client_id = client_id
                    print(f"   ✅ Conversion with portal_lead_ ID successful. Client ID: {client_id}")
                    return True
                else:
                    print("   ❌ No client_id in conversion response")
            else:
                print(f"   ❌ Conversion with portal_lead_ ID failed")
            
            # Test 5.2: Conversion with actual prospect ID
            print("\n   5.2: Testing conversion with actual prospect ID")
            if self.prospect_id:
                url = f"{BACKEND_URL}/api/crm/prospects/{self.prospect_id}/convert"
                
                response = self.session.post(url, json=payload)
                print(f"   Conversion actual ID response: {response.status_code}")
                print(f"   Response body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    client_id = data.get('client_id')
                    if client_id:
                        self.client_id = client_id
                        print(f"   ✅ Conversion with actual prospect ID successful. Client ID: {client_id}")
                        return True
                    else:
                        print("   ❌ No client_id in conversion response")
                else:
                    print(f"   ❌ Conversion with actual prospect ID failed")
            else:
                print("   ❌ No actual prospect ID available")
            
            return False
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False
    
    def verify_final_data_chain(self):
        """Verify final data chain integrity"""
        try:
            print("\n📋 STEP 6: Verifying final data chain integrity")
            
            # Final MongoDB state check
            lead = self.db.leads.find_one({"email": self.test_email})
            prospect = self.db.crm_prospects.find_one({"email": self.test_email})
            client = self.db.users.find_one({"email": self.test_email})
            
            print("\n   📊 Final data chain state:")
            
            # Lead analysis
            if lead:
                print(f"   Lead (leads collection):")
                print(f"     - migrated: {lead.get('migrated', False)}")
                print(f"     - crm_prospect_id: {lead.get('crm_prospect_id', 'None')}")
            else:
                print("   ❌ Lead not found")
            
            # Prospect analysis
            if prospect:
                print(f"   Prospect (crm_prospects collection):")
                print(f"     - stage: {prospect.get('stage')}")
                print(f"     - _original_lead_id: {prospect.get('_original_lead_id', 'None')}")
                print(f"     - converted_to_client: {prospect.get('converted_to_client', False)}")
                print(f"     - client_id: {prospect.get('client_id', 'None')}")
            else:
                print("   ❌ Prospect not found")
            
            # Client analysis
            if client:
                print(f"   Client (users collection):")
                print(f"     - type: {client.get('type')}")
                print(f"     - source_prospect_id: {client.get('source_prospect_id', 'None')}")
                print(f"     - source_lead_id: {client.get('source_lead_id', 'None')}")
            else:
                print("   No client record found")
            
            # Data chain integrity checks
            print("\n   🔗 Data chain integrity analysis:")
            
            integrity_issues = []
            
            if not lead or not lead.get('migrated'):
                integrity_issues.append("Lead not marked as migrated")
            
            if not lead or not lead.get('crm_prospect_id'):
                integrity_issues.append("Lead missing crm_prospect_id")
            
            if not prospect or not prospect.get('_original_lead_id'):
                integrity_issues.append("Prospect missing _original_lead_id")
            
            if client and (not client.get('source_prospect_id') or not client.get('source_lead_id')):
                integrity_issues.append("Client missing source references")
            
            if integrity_issues:
                print("   ❌ Data chain integrity issues:")
                for issue in integrity_issues:
                    print(f"     - {issue}")
                return False
            else:
                print("   ✅ Data chain integrity verified")
                return True
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up test data"""
        try:
            print("\n📋 CLEANUP: Removing test data")
            
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
            print(f"   ✅ Deleted {total_deleted} test records: {deleted_counts}")
            
        except Exception as e:
            print(f"   ❌ Cleanup error: {str(e)}")
    
    def run_detailed_investigation(self):
        """Run detailed CRM workflow investigation"""
        print("🔍 DETAILED CRM WORKFLOW INVESTIGATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {self.test_email}")
        print(f"Test Time: {datetime.now().isoformat()}")
        
        if not self.setup():
            return False
        
        success_steps = []
        
        # Step 1: Create test lead
        success_steps.append(self.create_test_lead())
        
        # Step 2: Check CRM integration
        success_steps.append(self.check_crm_integration())
        
        # Step 3: Test pipeline movement
        success_steps.append(self.test_pipeline_movement_step_by_step())
        
        # Step 4: Test AML/KYC endpoints
        success_steps.append(self.test_aml_kyc_endpoints())
        
        # Step 5: Test client conversion
        success_steps.append(self.test_client_conversion_endpoints())
        
        # Step 6: Verify final data chain
        success_steps.append(self.verify_final_data_chain())
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DETAILED INVESTIGATION SUMMARY")
        print("=" * 80)
        
        step_names = [
            "Lead Creation",
            "CRM Integration", 
            "Pipeline Movement",
            "AML/KYC Endpoints",
            "Client Conversion",
            "Data Chain Integrity"
        ]
        
        for i, (step_name, step_success) in enumerate(zip(step_names, success_steps)):
            status = "✅" if step_success else "❌"
            print(f"{status} Step {i+1}: {step_name}")
        
        passed_steps = sum(success_steps)
        total_steps = len(success_steps)
        
        print(f"\nOverall: {passed_steps}/{total_steps} steps passed ({passed_steps/total_steps*100:.1f}%)")
        
        # Cleanup
        self.cleanup()
        
        return all(success_steps)

def main():
    """Main test execution"""
    tester = DetailedCRMTester()
    success = tester.run_detailed_investigation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()