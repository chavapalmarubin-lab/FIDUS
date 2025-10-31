#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from backend_test import FidusAPITester

def test_gmail_oauth_only():
    """Test only Gmail OAuth endpoints"""
    print("🚀 Testing Gmail OAuth Integration...")
    print("=" * 50)
    
    tester = FidusAPITester()
    
    # Test Gmail OAuth Integration endpoints
    print("\n📋 GMAIL OAUTH INTEGRATION TESTS")
    print("-" * 30)
    
    results = []
    
    # Test 1: Auth URL Generation
    print("\n1. Testing Gmail OAuth Auth URL Generation...")
    result1 = tester.test_gmail_auth_url()
    results.append(("Gmail Auth URL Generation", result1))
    
    # Test 2: OAuth Callback Structure
    print("\n2. Testing Gmail OAuth Callback Structure...")
    result2 = tester.test_gmail_oauth_callback_structure()
    results.append(("Gmail OAuth Callback Structure", result2))
    
    # Test 3: Authentication OAuth Flow
    print("\n3. Testing Gmail Authentication OAuth Flow...")
    result3 = tester.test_gmail_authenticate_oauth_flow()
    results.append(("Gmail Authentication OAuth Flow", result3))
    
    # Test 4: Client ID Verification
    print("\n4. Testing Gmail Client ID Verification...")
    result4 = tester.test_gmail_client_id_verification()
    results.append(("Gmail Client ID Verification", result4))
    
    # Test 5: Error Handling
    print("\n5. Testing Gmail Error Handling...")
    result5 = tester.test_gmail_error_handling()
    results.append(("Gmail Error Handling", result5))
    
    # Test 6: Security Measures
    print("\n6. Testing Gmail Security Measures...")
    result6 = tester.test_gmail_security_measures()
    results.append(("Gmail Security Measures", result6))
    
    # Print results summary
    print("\n" + "=" * 50)
    print("📊 GMAIL OAUTH TEST RESULTS:")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 FINAL RESULTS: {passed}/{total} Gmail OAuth tests passed")
    
    if passed == total:
        print("🎉 All Gmail OAuth tests passed!")
        return 0
    else:
        failed = total - passed
        print(f"⚠️  {failed} Gmail OAuth test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(test_gmail_oauth_only())