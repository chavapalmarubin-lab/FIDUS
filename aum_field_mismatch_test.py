#!/usr/bin/env python3

import requests
import json

class AUMFieldMismatchTester:
    def __init__(self, base_url="https://trading-platform-76.preview.emergentagent.com"):
        self.base_url = base_url
        
    def test_aum_field_mismatch_issue(self):
        """Test to verify the AUM field name mismatch between backend and frontend"""
        print("🔍 TESTING AUM FIELD NAME MISMATCH ISSUE")
        print("=" * 60)
        
        try:
            url = f"{self.base_url}/api/admin/portfolio-summary"
            print(f"URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print("\n🔍 FIELD NAME ANALYSIS:")
                
                # Check what the backend returns
                has_aum = 'aum' in data
                has_total_aum = 'total_aum' in data
                
                print(f"Backend returns 'aum' field: {has_aum}")
                print(f"Backend returns 'total_aum' field: {has_total_aum}")
                
                if has_aum:
                    aum_value = data['aum']
                    print(f"Value of 'aum': ${aum_value:,.2f}")
                
                if has_total_aum:
                    total_aum_value = data['total_aum']
                    print(f"Value of 'total_aum': ${total_aum_value:,.2f}")
                
                print("\n🎯 ISSUE DIAGNOSIS:")
                
                if has_total_aum and not has_aum:
                    print("❌ FIELD MISMATCH CONFIRMED!")
                    print("   Backend returns: 'total_aum'")
                    print("   Frontend expects: 'aum'")
                    print("   This explains why frontend shows $0!")
                    print(f"   Actual AUM value: ${total_aum_value:,.2f}")
                    
                    print("\n💡 SOLUTION:")
                    print("   Option 1: Change backend to return 'aum' instead of 'total_aum'")
                    print("   Option 2: Change frontend to read 'total_aum' instead of 'aum'")
                    print("   Option 3: Return both fields for compatibility")
                    
                    return {
                        'issue_confirmed': True,
                        'backend_field': 'total_aum',
                        'frontend_expected': 'aum',
                        'actual_value': total_aum_value,
                        'solution_needed': True
                    }
                    
                elif has_aum and not has_total_aum:
                    print("✅ Backend returns 'aum' field as expected by frontend")
                    return {
                        'issue_confirmed': False,
                        'backend_field': 'aum',
                        'frontend_expected': 'aum',
                        'actual_value': aum_value,
                        'solution_needed': False
                    }
                    
                elif has_aum and has_total_aum:
                    print("✅ Backend returns both 'aum' and 'total_aum' fields")
                    print("   This provides compatibility for both field names")
                    return {
                        'issue_confirmed': False,
                        'backend_field': 'both',
                        'frontend_expected': 'aum',
                        'actual_value': data['aum'],
                        'solution_needed': False
                    }
                    
                else:
                    print("❌ Neither 'aum' nor 'total_aum' field found!")
                    return {
                        'issue_confirmed': True,
                        'backend_field': 'none',
                        'frontend_expected': 'aum',
                        'actual_value': 0,
                        'solution_needed': True
                    }
                    
            else:
                print(f"❌ Request failed with status {response.status_code}")
                return {
                    'issue_confirmed': True,
                    'error': f"HTTP {response.status_code}",
                    'solution_needed': True
                }
                
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            return {
                'issue_confirmed': True,
                'error': str(e),
                'solution_needed': True
            }

def main():
    tester = AUMFieldMismatchTester()
    result = tester.test_aum_field_mismatch_issue()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL DIAGNOSIS:")
    
    if result.get('issue_confirmed'):
        print("🚨 ISSUE CONFIRMED: Field name mismatch causing frontend to show $0")
        print(f"   Backend field: '{result.get('backend_field', 'unknown')}'")
        print(f"   Frontend expects: '{result.get('frontend_expected', 'aum')}'")
        if 'actual_value' in result:
            print(f"   Actual AUM: ${result['actual_value']:,.2f}")
    else:
        print("✅ No field mismatch issue detected")
    
    return result

if __name__ == "__main__":
    main()