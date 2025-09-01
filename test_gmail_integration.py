#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from backend_test import FidusAPITester

def test_gmail_integration():
    print("🚀 Testing Gmail Integration Endpoints...")
    print("=" * 50)
    
    tester = FidusAPITester()
    
    # First, login to get users
    print("\n📋 AUTHENTICATION SETUP")
    print("-" * 30)
    tester.test_client_login()
    tester.test_admin_login()
    
    # Upload a document first for testing
    print("\n📋 DOCUMENT SETUP")
    print("-" * 30)
    tester.test_document_upload()
    
    # Test Gmail Integration endpoints
    print("\n📋 GMAIL INTEGRATION TESTS")
    print("-" * 30)
    
    # Test 1: Gmail Authentication
    tester.test_gmail_authenticate()
    
    # Test 2: Document View for Email Links
    tester.test_document_view_for_email_links()
    tester.test_document_view_nonexistent()
    
    # Test 3: Send Document for Signature with Gmail
    tester.test_send_document_for_signature_gmail()
    
    # Test 4: Document Status with Gmail Message Tracking
    tester.test_document_status_gmail_tracking()
    
    # Test 5: Gmail Error Handling
    tester.test_gmail_error_handling()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 GMAIL INTEGRATION RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Gmail integration tests passed!")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} Gmail test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(test_gmail_integration())