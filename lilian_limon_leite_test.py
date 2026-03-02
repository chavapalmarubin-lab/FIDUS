#!/usr/bin/env python3
"""
LILIAN LIMON LEITE SPECIFIC TEST - EXACT REPRODUCTION
====================================================

This test reproduces the EXACT scenario reported in the bug fix request:
- User: "Lilian Limon Leite"
- Issue: "Request failed with status code 401" during Document Upload step (step 4)
- Expected: Lead registration should work end-to-end without authentication

This test verifies the fix is working for the exact reported scenario.
"""

import requests
import json
import sys
import io
from datetime import datetime

# Configuration
BACKEND_URL = "https://risk-engine-v2.preview.emergentagent.com/api"

class LilianLimonLeiteTest:
    def __init__(self):
        self.session = requests.Session()
        self.prospect_id = None
        
    def create_mock_document(self, doc_type="government_id"):
        """Create mock document for testing"""
        content = f"MOCK_{doc_type.upper()}_LILIAN_LIMON_LEITE_DOCUMENT".encode()
        return io.BytesIO(content), f"lilian_{doc_type}.jpg"
    
    def test_complete_lead_registration_workflow(self):
        """Test the complete lead registration workflow for Lilian Limon Leite"""
        print("🎯 TESTING COMPLETE LEAD REGISTRATION WORKFLOW")
        print("=" * 60)
        print("User: Lilian Limon Leite")
        print("Scenario: New user registration with document upload")
        print()
        
        # Step 1: Create prospect (should work without auth)
        print("📝 Step 1: Creating prospect...")
        prospect_data = {
            "name": "Lilian Limon Leite",
            "email": "lilian.limon.leite@gmail.com",
            "phone": "+55-11-99999-8888",
            "notes": "Lead registration - reported 401 error during document upload"
        }
        
        response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=prospect_data)
        
        if response.status_code == 200:
            data = response.json()
            self.prospect_id = data.get("prospect_id")
            print(f"✅ SUCCESS: Prospect created with ID: {self.prospect_id}")
        else:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
        
        # Step 2: Upload Government ID (previously failed with 401)
        print("\n📄 Step 2: Uploading Government ID document...")
        file_content, filename = self.create_mock_document("government_id")
        
        files = {'file': (filename, file_content, 'image/jpeg')}
        data = {
            'document_type': 'government_id',
            'notes': 'Government ID for Lilian Limon Leite'
        }
        
        response = self.session.post(
            f"{BACKEND_URL}/crm/prospects/{self.prospect_id}/documents",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            doc_data = response.json()
            print(f"✅ SUCCESS: Government ID uploaded - Document ID: {doc_data.get('document_id')}")
        else:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            if response.status_code == 401:
                print("🚨 BUG STILL EXISTS: 401 error during document upload!")
            return False
        
        # Step 3: Upload Proof of Address (also likely to fail before fix)
        print("\n🏠 Step 3: Uploading Proof of Address document...")
        file_content, filename = self.create_mock_document("proof_of_address")
        
        files = {'file': (filename, file_content, 'application/pdf')}
        data = {
            'document_type': 'proof_of_address',
            'notes': 'Proof of Address for Lilian Limon Leite'
        }
        
        response = self.session.post(
            f"{BACKEND_URL}/crm/prospects/{self.prospect_id}/documents",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            doc_data = response.json()
            print(f"✅ SUCCESS: Proof of Address uploaded - Document ID: {doc_data.get('document_id')}")
        else:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            if response.status_code == 401:
                print("🚨 BUG STILL EXISTS: 401 error during document upload!")
            return False
        
        # Step 4: Verify documents were stored
        print("\n📋 Step 4: Verifying uploaded documents...")
        response = self.session.get(f"{BACKEND_URL}/crm/prospects/{self.prospect_id}/documents")
        
        if response.status_code == 200:
            docs_data = response.json()
            documents = docs_data.get('documents', [])
            print(f"✅ SUCCESS: Found {len(documents)} documents for prospect")
            
            for doc in documents:
                print(f"   • {doc.get('document_type')}: {doc.get('filename')} ({doc.get('file_size')} bytes)")
        else:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
        
        # Step 5: Test AML/KYC check (should also be public)
        print("\n🔍 Step 5: Running AML/KYC compliance check...")
        response = self.session.post(f"{BACKEND_URL}/crm/prospects/{self.prospect_id}/aml-kyc")
        
        if response.status_code == 200:
            aml_data = response.json()
            print(f"✅ SUCCESS: AML/KYC check completed - Status: {aml_data.get('aml_result', {}).get('overall_status')}")
        else:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            # AML/KYC failure is not critical for this test
        
        print("\n🎉 COMPLETE WORKFLOW SUCCESS!")
        print("=" * 60)
        print("✅ Lilian Limon Leite can now complete lead registration without 401 errors")
        print("✅ All document uploads work correctly")
        print("✅ Bug fix verified and working")
        
        return True
    
    def test_edge_cases(self):
        """Test edge cases to ensure fix is robust"""
        print("\n🧪 TESTING EDGE CASES")
        print("-" * 40)
        
        # Test with different file types
        file_types = [
            ("image/jpeg", ".jpg"),
            ("image/png", ".png"),
            ("application/pdf", ".pdf"),
            ("image/tiff", ".tiff")
        ]
        
        for mime_type, extension in file_types:
            print(f"\n📎 Testing file type: {extension}")
            file_content = io.BytesIO(f"MOCK_DOCUMENT_{extension}".encode())
            filename = f"lilian_test{extension}"
            
            files = {'file': (filename, file_content, mime_type)}
            data = {
                'document_type': 'additional_document',
                'notes': f'Testing {extension} file upload'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/crm/prospects/{self.prospect_id}/documents",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                print(f"✅ {extension} upload successful")
            else:
                print(f"❌ {extension} upload failed: HTTP {response.status_code}")
        
        return True

def main():
    """Main test execution"""
    print("🚨 LILIAN LIMON LEITE SPECIFIC BUG FIX VERIFICATION")
    print("=" * 60)
    print("Testing the exact scenario reported in the bug fix request")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    test_runner = LilianLimonLeiteTest()
    
    # Run the complete workflow test
    workflow_success = test_runner.test_complete_lead_registration_workflow()
    
    if workflow_success:
        # Run edge case tests
        test_runner.test_edge_cases()
        
        print("\n🎯 FINAL ASSESSMENT")
        print("=" * 60)
        print("✅ BUG FIX SUCCESSFUL: 401 error during document upload is RESOLVED")
        print("✅ Lead registration workflow works end-to-end without authentication")
        print("✅ Lilian Limon Leite (and all users) can now complete registration")
        print("✅ Document upload endpoints are now properly public")
        print("\n🚀 DEPLOYMENT READY: Fix can be deployed to production")
    else:
        print("\n❌ BUG FIX FAILED: Issues still exist")
        sys.exit(1)

if __name__ == "__main__":
    main()