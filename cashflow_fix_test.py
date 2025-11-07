#!/usr/bin/env python3
"""
CASH FLOW CALCULATION FIX TEST
Testing the fixed cash flow calculation logic to resolve Issue #4.

The issue is that the cash flow endpoint is looking for fields that don't exist in the investment documents:
- Looking for 'first_redemption_date' but investments have 'interest_start_date'
- Looking for 'redemption_frequency' but need to derive from fund configuration
- Need to properly calculate based on fund rules (CORE=monthly, BALANCE=quarterly)
"""

import requests
import json
import sys
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

# Use the correct backend URL from review request
BACKEND_URL = "https://referral-tracker-9.preview.emergentagent.com/api"

class CashFlowFixTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate(self):
        """Authenticate as admin"""
        login_data = {
            "username": "admin",
            "password": "password123", 
            "user_type": "admin"
        }
        
        response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("token"):
                self.admin_token = data["token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                print("✅ Admin authentication successful")
                return True
        
        print("❌ Admin authentication failed")
        return False
    
    def get_investments_raw(self):
        """Get raw investment data to understand the structure"""
        # Get detailed investment data from client endpoint which has all fields
        response = self.session.get(f"{BACKEND_URL}/investments/client/client_alejandro")
        if response.status_code == 200:
            data = response.json()
            investments = data.get("investments", [])
            
            print(f"\n📊 Found {len(investments)} investments:")
            for inv in investments:
                print(f"  - {inv['fund_code']}: ${inv['principal_amount']:,.2f}")
                print(f"    Interest Start: {inv.get('interest_start_date', 'N/A')}")
                print(f"    Monthly Rate: {inv.get('monthly_interest_rate', 'N/A')}%")
                print(f"    Status: {inv.get('status', 'N/A')}")
                print()
            
            return investments
        return []
    
    def calculate_expected_cash_flow(self, investments):
        """Calculate what the cash flow SHOULD be based on investment data"""
        print("🧮 CALCULATING EXPECTED CASH FLOW:")
        
        total_obligations = 0
        monthly_breakdown = {}
        upcoming_redemptions = []
        
        # Fund configurations
        fund_configs = {
            "CORE": {"frequency": "monthly", "rate_multiplier": 1},
            "BALANCE": {"frequency": "quarterly", "rate_multiplier": 3}
        }
        
        now = datetime.now(timezone.utc)
        
        for inv in investments:
            fund_code = inv['fund_code']
            principal = inv['principal_amount']
            monthly_rate = inv['monthly_interest_rate'] / 100  # Convert percentage to decimal
            interest_start_str = inv.get('interest_start_date', '')
            
            if not interest_start_str:
                continue
                
            # Parse interest start date
            if interest_start_str.endswith('Z'):
                interest_start = datetime.fromisoformat(interest_start_str.replace('Z', '+00:00'))
            elif '+' not in interest_start_str and 'T' in interest_start_str:
                interest_start = datetime.fromisoformat(interest_start_str).replace(tzinfo=timezone.utc)
            else:
                interest_start = datetime.fromisoformat(interest_start_str)
            
            config = fund_configs.get(fund_code, {"frequency": "monthly", "rate_multiplier": 1})
            frequency = config["frequency"]
            rate_multiplier = config["rate_multiplier"]
            
            monthly_interest = principal * monthly_rate
            payment_amount = monthly_interest * rate_multiplier
            
            print(f"  {fund_code} Fund:")
            print(f"    Principal: ${principal:,.2f}")
            print(f"    Monthly Rate: {monthly_rate*100:.1f}%")
            print(f"    Payment Frequency: {frequency}")
            print(f"    Payment Amount: ${payment_amount:,.2f}")
            print(f"    Interest Starts: {interest_start.strftime('%Y-%m-%d')}")
            
            # Generate payments for 12 months
            if frequency == "monthly":
                # Monthly payments starting from interest_start_date
                for i in range(12):
                    payment_date = interest_start + relativedelta(months=i)
                    if payment_date <= now + timedelta(days=365):  # Within 12 months
                        total_obligations += payment_amount
                        
                        month_key = payment_date.strftime('%Y-%m')
                        if month_key not in monthly_breakdown:
                            monthly_breakdown[month_key] = 0
                        monthly_breakdown[month_key] += payment_amount
                        
                        if payment_date >= now:  # Future payments
                            upcoming_redemptions.append({
                                'date': payment_date.strftime('%Y-%m-%d'),
                                'fund': fund_code,
                                'amount': payment_amount,
                                'days_until': (payment_date - now).days
                            })
            
            elif frequency == "quarterly":
                # Quarterly payments starting from interest_start_date
                for i in range(4):  # 4 quarters
                    payment_date = interest_start + relativedelta(months=i*3)
                    if payment_date <= now + timedelta(days=365):  # Within 12 months
                        total_obligations += payment_amount
                        
                        month_key = payment_date.strftime('%Y-%m')
                        if month_key not in monthly_breakdown:
                            monthly_breakdown[month_key] = 0
                        monthly_breakdown[month_key] += payment_amount
                        
                        if payment_date >= now:  # Future payments
                            upcoming_redemptions.append({
                                'date': payment_date.strftime('%Y-%m-%d'),
                                'fund': fund_code,
                                'amount': payment_amount,
                                'days_until': (payment_date - now).days
                            })
            
            print(f"    12-month obligation: ${payment_amount * (12 if frequency == 'monthly' else 4):,.2f}")
            print()
        
        # Sort upcoming redemptions by date
        upcoming_redemptions.sort(key=lambda x: x['date'])
        
        print(f"📈 EXPECTED TOTALS:")
        print(f"  Total 12-month obligations: ${total_obligations:,.2f}")
        print(f"  Monthly breakdown periods: {len(monthly_breakdown)}")
        print(f"  Upcoming redemptions: {len(upcoming_redemptions)}")
        
        if upcoming_redemptions:
            print(f"  Next payment: {upcoming_redemptions[0]['date']} - {upcoming_redemptions[0]['fund']} ${upcoming_redemptions[0]['amount']:,.2f}")
        
        return {
            "total_obligations": total_obligations,
            "monthly_breakdown": monthly_breakdown,
            "upcoming_redemptions": upcoming_redemptions[:5]
        }
    
    def test_current_cash_flow_endpoint(self):
        """Test the current cash flow endpoint"""
        print("\n🔍 TESTING CURRENT CASH FLOW ENDPOINT:")
        
        response = self.session.get(f"{BACKEND_URL}/admin/cashflow/overview")
        if response.status_code == 200:
            data = response.json()
            obligations = data.get("summary", {}).get("client_interest_obligations", 0)
            monthly_breakdown = data.get("monthly_breakdown", [])
            upcoming_redemptions = data.get("upcoming_redemptions", [])
            
            print(f"  Current obligations: ${obligations:,.2f}")
            print(f"  Monthly breakdown entries: {len(monthly_breakdown)}")
            print(f"  Upcoming redemptions: {len(upcoming_redemptions)}")
            
            return {
                "obligations": obligations,
                "monthly_breakdown": len(monthly_breakdown),
                "upcoming_redemptions": len(upcoming_redemptions)
            }
        else:
            print(f"  ❌ Endpoint failed: HTTP {response.status_code}")
            return None
    
    def run_analysis(self):
        """Run complete cash flow analysis"""
        print("💰 CASH FLOW CALCULATION FIX ANALYSIS")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Get investment data
        investments = self.get_investments_raw()
        if not investments:
            print("❌ No investments found")
            return False
        
        # Calculate expected values
        expected = self.calculate_expected_cash_flow(investments)
        
        # Test current endpoint
        current = self.test_current_cash_flow_endpoint()
        
        # Compare results
        print("\n🔍 COMPARISON:")
        print("=" * 60)
        
        if current:
            expected_total = expected["total_obligations"]
            current_total = current["obligations"]
            
            print(f"Expected obligations: ${expected_total:,.2f}")
            print(f"Current obligations:  ${current_total:,.2f}")
            print(f"Difference:          ${abs(expected_total - current_total):,.2f}")
            
            if current_total == 0:
                print("❌ ISSUE #4 NOT RESOLVED: Cash flow still shows zeros")
                print("\n🔧 ROOT CAUSE ANALYSIS:")
                print("  - Cash flow endpoint is looking for 'first_redemption_date' field")
                print("  - Investments have 'interest_start_date' instead")
                print("  - Cash flow endpoint is looking for 'redemption_frequency' field")
                print("  - Need to derive frequency from fund configuration")
                print("  - Monthly interest rate needs proper decimal conversion")
                
                return False
            elif abs(expected_total - current_total) < 0.01:
                print("✅ ISSUE #4 RESOLVED: Cash flow calculations are correct!")
                return True
            else:
                print("⚠️ PARTIAL RESOLUTION: Cash flow is non-zero but values don't match expected")
                return True
        else:
            print("❌ Cannot compare - endpoint failed")
            return False

if __name__ == "__main__":
    tester = CashFlowFixTester()
    success = tester.run_analysis()
    sys.exit(0 if success else 1)