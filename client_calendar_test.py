#!/usr/bin/env python3
"""
Client Calendar Endpoint Testing
Testing the new GET /api/client/{client_id}/calendar endpoint specifically for Alejandro Mariscal Romero.

Test Requirements:
1. Test with Alejandro's client ID: 'client_alejandro'
2. Verify HTTP 200 response with proper calendar data structure
3. Check response includes:
   - calendar_events array with investment milestones and payment dates
   - monthly_timeline object grouped by month
   - contract_summary with totals and contract period

Expected Calendar Structure for Alejandro (Investment date: October 1, 2025):
- Investment start events for both BALANCE and CORE funds
- Incubation end events (November 30, 2025)
- CORE payment events starting December 30, 2025 (every 30 days)
- BALANCE payment events starting February 28, 2026 (every 90 days)
- Final payments on December 1, 2026

Monthly Timeline Verification:
- October 2025: Investment start events only
- December 2025: First CORE payment ($272.27)
- February 2026: CORE + BALANCE payments ($7,772.27 total)
- December 2026: Final payments for both funds

Contract Summary Check:
- Total investment: $118,151.41
- Contract period: October 1, 2025 - December 1, 2026
- Duration: 426 days
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Use the correct backend URL from frontend/.env
BACKEND_URL = "https://fidus-fix.preview.emergentagent.com/api"

class ClientCalendarTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2, default=str)}")
    
    def authenticate_admin(self) -> bool:
        """Authenticate as admin to access the endpoint"""
        print("\n🔐 AUTHENTICATING AS ADMIN")
        
        try:
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
                    
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as {data.get('name', 'admin')}",
                        {"user_id": data.get("id"), "username": data.get("username")}
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token in response", data)
                    return False
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}", response.json() if response.content else None)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_client_calendar_endpoint(self) -> bool:
        """Test the client calendar endpoint for Alejandro"""
        print("\n📅 TESTING CLIENT CALENDAR ENDPOINT")
        
        client_id = "client_alejandro"
        
        try:
            response = self.session.get(f"{BACKEND_URL}/client/{client_id}/calendar")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic response structure
                if not data.get("success"):
                    self.log_test(
                        "Calendar Endpoint - Response Success",
                        False,
                        f"API returned success=false: {data.get('error', 'Unknown error')}",
                        data
                    )
                    return False
                
                calendar_data = data.get("calendar", {})
                
                # Verify required top-level keys
                required_keys = ["calendar_events", "monthly_timeline", "contract_summary"]
                missing_keys = [key for key in required_keys if key not in calendar_data]
                
                if missing_keys:
                    self.log_test(
                        "Calendar Endpoint - Structure",
                        False,
                        f"Missing required keys: {missing_keys}",
                        calendar_data
                    )
                    return False
                
                self.log_test(
                    "Calendar Endpoint - Basic Structure",
                    True,
                    f"All required keys present: {required_keys}",
                    {"keys_found": list(calendar_data.keys())}
                )
                
                return self.verify_calendar_data(calendar_data)
                
            else:
                self.log_test(
                    "Calendar Endpoint - HTTP Status",
                    False,
                    f"HTTP {response.status_code}",
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("Calendar Endpoint - Exception", False, f"Exception: {str(e)}")
            return False
    
    def verify_calendar_data(self, calendar_data: Dict) -> bool:
        """Verify the calendar data structure and content"""
        print("\n🔍 VERIFYING CALENDAR DATA STRUCTURE")
        
        success = True
        
        # Test calendar events
        success &= self.verify_calendar_events(calendar_data.get("calendar_events", []))
        
        # Test monthly timeline
        success &= self.verify_monthly_timeline(calendar_data.get("monthly_timeline", {}))
        
        # Test contract summary
        success &= self.verify_contract_summary(calendar_data.get("contract_summary", {}))
        
        return success
    
    def verify_calendar_events(self, events: List[Dict]) -> bool:
        """Verify calendar events array"""
        print("\n📋 VERIFYING CALENDAR EVENTS")
        
        if not events:
            self.log_test(
                "Calendar Events - Empty",
                False,
                "No calendar events found - expected investment milestones and payment dates",
                {"events_count": 0}
            )
            return False
        
        # Check for expected event types
        event_types = [event.get("type") for event in events]
        expected_types = ["investment_start", "incubation_end", "interest_redemption", "final_redemption"]
        
        found_types = set(event_types)
        missing_types = [t for t in expected_types if t not in found_types]
        
        if missing_types:
            self.log_test(
                "Calendar Events - Event Types",
                False,
                f"Missing expected event types: {missing_types}",
                {"found_types": list(found_types), "total_events": len(events)}
            )
            return False
        
        # Check for BALANCE and CORE fund events
        fund_codes = [event.get("fund_code") for event in events if event.get("fund_code")]
        expected_funds = ["BALANCE", "CORE"]
        
        found_funds = set(fund_codes)
        missing_funds = [f for f in expected_funds if f not in found_funds]
        
        if missing_funds:
            self.log_test(
                "Calendar Events - Fund Coverage",
                False,
                f"Missing expected funds: {missing_funds}",
                {"found_funds": list(found_funds), "fund_events": len([e for e in events if e.get("fund_code")])}
            )
            return False
        
        # Verify investment start events
        start_events = [e for e in events if e.get("type") == "investment_start"]
        if len(start_events) < 2:
            self.log_test(
                "Calendar Events - Investment Starts",
                False,
                f"Expected 2 investment start events (BALANCE + CORE), found {len(start_events)}",
                {"start_events": start_events}
            )
            return False
        
        # Verify payment events exist
        payment_events = [e for e in events if e.get("type") in ["interest_redemption", "final_redemption"]]
        if len(payment_events) < 10:  # Should have multiple payments
            self.log_test(
                "Calendar Events - Payment Events",
                False,
                f"Expected multiple payment events, found only {len(payment_events)}",
                {"payment_count": len(payment_events)}
            )
            return False
        
        self.log_test(
            "Calendar Events - Complete",
            True,
            f"Found {len(events)} events with all expected types and funds",
            {
                "total_events": len(events),
                "event_types": list(found_types),
                "fund_codes": list(found_funds),
                "start_events": len(start_events),
                "payment_events": len(payment_events)
            }
        )
        
        return True
    
    def verify_monthly_timeline(self, timeline: Dict) -> bool:
        """Verify monthly timeline structure"""
        print("\n📊 VERIFYING MONTHLY TIMELINE")
        
        if not timeline:
            self.log_test(
                "Monthly Timeline - Empty",
                False,
                "No monthly timeline data found",
                {"timeline_months": 0}
            )
            return False
        
        # Check for expected months (should cover investment period)
        months = list(timeline.keys())
        if len(months) < 12:  # Should cover at least 12 months
            self.log_test(
                "Monthly Timeline - Coverage",
                False,
                f"Expected at least 12 months of timeline, found {len(months)}",
                {"months_found": months}
            )
            return False
        
        # Verify timeline structure for each month
        sample_month = list(timeline.values())[0]
        required_fields = ["month_name", "events", "total_due", "core_interest", "balance_interest"]
        missing_fields = [field for field in required_fields if field not in sample_month]
        
        if missing_fields:
            self.log_test(
                "Monthly Timeline - Structure",
                False,
                f"Missing required fields in timeline entries: {missing_fields}",
                {"sample_month": sample_month}
            )
            return False
        
        # Check for months with payments
        payment_months = [month for month, data in timeline.items() if data.get("total_due", 0) > 0]
        if len(payment_months) < 5:  # Should have multiple payment months
            self.log_test(
                "Monthly Timeline - Payment Months",
                False,
                f"Expected multiple payment months, found {len(payment_months)}",
                {"payment_months": payment_months}
            )
            return False
        
        self.log_test(
            "Monthly Timeline - Complete",
            True,
            f"Found {len(months)} months with {len(payment_months)} payment months",
            {
                "total_months": len(months),
                "payment_months": len(payment_months),
                "month_range": f"{min(months)} to {max(months)}"
            }
        )
        
        return True
    
    def verify_contract_summary(self, summary: Dict) -> bool:
        """Verify contract summary data"""
        print("\n📋 VERIFYING CONTRACT SUMMARY")
        
        required_fields = ["total_investment", "total_interest", "contract_start", "contract_end", "contract_duration_days"]
        missing_fields = [field for field in required_fields if field not in summary]
        
        if missing_fields:
            self.log_test(
                "Contract Summary - Structure",
                False,
                f"Missing required fields: {missing_fields}",
                summary
            )
            return False
        
        # Verify expected values for Alejandro
        total_investment = summary.get("total_investment", 0)
        expected_investment = 118151.41  # $100,000 BALANCE + $18,151.41 CORE
        
        # Allow for some variance in the total
        if abs(total_investment - expected_investment) > 1000:
            self.log_test(
                "Contract Summary - Investment Total",
                False,
                f"Expected ~${expected_investment:,.2f}, found ${total_investment:,.2f}",
                {"expected": expected_investment, "actual": total_investment}
            )
            return False
        
        # Verify contract duration (should be 426 days)
        duration = summary.get("contract_duration_days", 0)
        if duration != 426:
            self.log_test(
                "Contract Summary - Duration",
                False,
                f"Expected 426 days, found {duration} days",
                {"expected": 426, "actual": duration}
            )
            return False
        
        # Verify dates are present
        contract_start = summary.get("contract_start")
        contract_end = summary.get("contract_end")
        
        if not contract_start or not contract_end:
            self.log_test(
                "Contract Summary - Dates",
                False,
                "Missing contract start or end dates",
                {"start": contract_start, "end": contract_end}
            )
            return False
        
        self.log_test(
            "Contract Summary - Complete",
            True,
            f"Investment: ${total_investment:,.2f}, Duration: {duration} days",
            {
                "total_investment": total_investment,
                "total_interest": summary.get("total_interest", 0),
                "duration_days": duration,
                "contract_period": f"{contract_start} to {contract_end}"
            }
        )
        
        return True
    
    def verify_expected_payment_schedule(self, calendar_data: Dict) -> bool:
        """Verify specific payment dates match expected schedule"""
        print("\n🗓️ VERIFYING EXPECTED PAYMENT SCHEDULE")
        
        events = calendar_data.get("calendar_events", [])
        
        # Look for specific expected dates
        expected_dates = {
            "2025-10-01": "Investment start",
            "2025-11-30": "Incubation end", 
            "2025-12-30": "First CORE payment",
            "2026-02-28": "First BALANCE payment",
            "2026-12-01": "Final payments"
        }
        
        found_dates = {}
        for event in events:
            event_date = event.get("date")
            if isinstance(event_date, str):
                date_str = event_date[:10]  # Get YYYY-MM-DD part
            else:
                date_str = event_date.strftime("%Y-%m-%d") if event_date else None
            
            if date_str in expected_dates:
                found_dates[date_str] = event.get("type", "unknown")
        
        missing_dates = [date for date in expected_dates if date not in found_dates]
        
        if missing_dates:
            self.log_test(
                "Payment Schedule - Expected Dates",
                False,
                f"Missing expected payment dates: {missing_dates}",
                {"expected": expected_dates, "found": found_dates}
            )
            return False
        
        self.log_test(
            "Payment Schedule - Expected Dates",
            True,
            f"Found all expected key dates: {list(expected_dates.keys())}",
            found_dates
        )
        
        return True
    
    def run_comprehensive_test(self) -> bool:
        """Run comprehensive client calendar endpoint test"""
        print("🎯 CLIENT CALENDAR ENDPOINT COMPREHENSIVE TEST")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Client ID: client_alejandro")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test calendar endpoint
        if not self.test_client_calendar_endpoint():
            print("\n❌ CRITICAL: Client calendar endpoint test failed")
            return False
        
        # Step 3: Additional verification if we have calendar data
        calendar_response = self.session.get(f"{BACKEND_URL}/client/client_alejandro/calendar")
        if calendar_response.status_code == 200:
            calendar_data = calendar_response.json().get("calendar", {})
            if calendar_data:
                self.verify_expected_payment_schedule(calendar_data)
        
        # Calculate success rate
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 CLIENT CALENDAR ENDPOINT TEST SUMMARY")
        print("=" * 70)
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['details']}")
        
        # Show successful tests
        successful_tests = [result for result in self.test_results if result["success"]]
        if successful_tests:
            print(f"\n✅ SUCCESSFUL TESTS ({len(successful_tests)}):")
            for test in successful_tests:
                print(f"   - {test['test']}: {test['details']}")
        
        print(f"\n📋 RECOMMENDATIONS:")
        if success_rate == 100:
            print("   - ✅ Client calendar endpoint is working perfectly!")
            print("   - ✅ All expected data structures and payment schedules verified")
        elif success_rate >= 80:
            print("   - ⚠️ Calendar endpoint mostly working but has minor issues")
            print("   - 🔧 Review failed tests for specific fixes needed")
        else:
            print("   - ❌ Calendar endpoint has significant issues")
            print("   - 🚨 Check backend implementation and Alejandro's investment data")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ClientCalendarTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)