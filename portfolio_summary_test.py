#!/usr/bin/env python3

import requests
import json
from datetime import datetime

class PortfolioSummaryTester:
    def __init__(self, base_url="https://equity-peak-tracker.preview.emergentagent.com"):
        self.base_url = base_url
        
    def test_admin_portfolio_summary_detailed(self):
        """Test GET /api/admin/portfolio-summary to verify AUM calculation and field names"""
        print("🔍 TESTING ADMIN PORTFOLIO SUMMARY ENDPOINT")
        print("=" * 60)
        
        try:
            url = f"{self.base_url}/api/admin/portfolio-summary"
            print(f"URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n📊 RESPONSE DATA STRUCTURE:")
                print(json.dumps(data, indent=2))
                
                print("\n🔍 FIELD ANALYSIS:")
                
                # Check for different AUM field names
                aum_fields = ['aum', 'total_aum']
                aum_value = None
                aum_field_name = None
                
                for field in aum_fields:
                    if field in data:
                        aum_value = data[field]
                        aum_field_name = field
                        print(f"✅ Found AUM field: '{field}' = ${aum_value:,.2f}")
                        break
                
                if not aum_value:
                    print("❌ NO AUM FIELD FOUND!")
                    return False
                
                # Check expected AUM calculation
                expected_aum = 161825  # CORE $86,825 + BALANCE $75,000
                print(f"\n💰 AUM CALCULATION VERIFICATION:")
                print(f"Expected AUM: ${expected_aum:,.2f}")
                print(f"Actual AUM: ${aum_value:,.2f}")
                
                if aum_value == expected_aum:
                    print("✅ AUM CALCULATION CORRECT!")
                elif aum_value == 0:
                    print("❌ AUM IS ZERO - CALCULATION ISSUE!")
                else:
                    print(f"⚠️  AUM MISMATCH - Difference: ${abs(aum_value - expected_aum):,.2f}")
                
                # Check allocation breakdown
                if 'allocation' in data:
                    allocation = data['allocation']
                    print(f"\n📈 FUND ALLOCATION:")
                    for fund, percentage in allocation.items():
                        print(f"  {fund}: {percentage}%")
                
                # Check fund breakdown if available
                if 'fund_breakdown' in data:
                    fund_breakdown = data['fund_breakdown']
                    print(f"\n💼 FUND BREAKDOWN:")
                    total_breakdown = 0
                    for fund, details in fund_breakdown.items():
                        amount = details.get('amount', 0)
                        percentage = details.get('percentage', 0)
                        total_breakdown += amount
                        print(f"  {fund}: ${amount:,.2f} ({percentage}%)")
                    
                    print(f"\nTotal from breakdown: ${total_breakdown:,.2f}")
                    
                    # Verify breakdown matches total AUM
                    if abs(total_breakdown - aum_value) < 0.01:
                        print("✅ Fund breakdown matches total AUM")
                    else:
                        print("❌ Fund breakdown doesn't match total AUM")
                
                # Check client count
                if 'client_count' in data:
                    client_count = data['client_count']
                    print(f"\n👥 CLIENT COUNT: {client_count}")
                    
                    if client_count > 0:
                        print("✅ Clients found in calculation")
                    else:
                        print("❌ No clients found - may indicate data issue")
                
                print("\n" + "=" * 60)
                print("🎯 SUMMARY:")
                print(f"Field name used: '{aum_field_name}'")
                print(f"AUM Value: ${aum_value:,.2f}")
                print(f"Expected: ${expected_aum:,.2f}")
                
                if aum_value == 0:
                    print("🚨 CRITICAL: AUM is showing $0 - this matches the frontend issue!")
                    return False
                elif aum_value == expected_aum:
                    print("✅ SUCCESS: AUM calculation is correct!")
                    return True
                else:
                    print("⚠️  WARNING: AUM value doesn't match expected amount")
                    return False
                    
            else:
                print(f"❌ Request failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            return False

def main():
    tester = PortfolioSummaryTester()
    success = tester.test_admin_portfolio_summary_detailed()
    
    if success:
        print("\n🎉 Portfolio summary endpoint working correctly!")
    else:
        print("\n🚨 Portfolio summary endpoint has issues!")
    
    return success

if __name__ == "__main__":
    main()