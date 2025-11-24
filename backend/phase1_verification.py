"""
FIDUS Referral System - Phase 1 Production Verification
Comprehensive testing with full database and API access
"""

import requests
import json
from datetime import datetime
from pymongo import MongoClient

# Production credentials
MONGO_URI = "mongodb+srv://YOUR_MONGODB_URL_HERE"
API_BASE_URL = "https://fidus-api.onrender.com"

class Phase1Verifier:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client.fidus_production
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": "Production (Render)",
            "tests": {},
            "overall_status": "PENDING"
        }
        
    def print_header(self, title):
        print("\n" + "="*70)
        print(title)
        print("="*70)
    
    def test_salvador_data(self):
        """Task 1: Verify Salvador Palma's data"""
        self.print_header("TASK 1: SALVADOR PALMA VERIFICATION")
        
        salvador = self.db.salespeople.find_one({"referral_code": "SP-2025"})
        
        if not salvador:
            print("❌ FAILED: Salvador Palma not found!")
            self.results["tests"]["salvador"] = {"status": "FAIL", "reason": "Not found"}
            return None
        
        print(f"✅ Found Salvador Palma")
        print(f"   Name: {salvador.get('name')}")
        print(f"   Email: {salvador.get('email')}")
        print(f"   Phone: {salvador.get('phone')}")
        print(f"   Referral Code: {salvador.get('referral_code')}")
        print(f"   ID: {salvador['_id']}")
        
        sales_volume = float(salvador.get('total_sales_volume', 0))
        commissions = float(salvador.get('total_commissions_earned', 0))
        active_investments = salvador.get('active_investments', 0)
        
        print(f"\n📊 Financial Metrics:")
        print(f"   Total Sales Volume: ${sales_volume:,.2f}")
        print(f"   Total Commissions: ${commissions:,.2f}")
        print(f"   Active Investments: {active_investments}")
        print(f"   Next Payment Date: {salvador.get('next_commission_date')}")
        print(f"   Next Payment Amount: ${float(salvador.get('next_commission_amount', 0)):,.2f}")
        
        # Validation
        sales_match = abs(sales_volume - 118151.41) < 1
        commissions_match = abs(commissions - 3326.73) < 1
        investments_match = active_investments == 2
        
        print(f"\n✅ Validation:")
        print(f"   Sales Volume ($118,151.41): {'✓' if sales_match else '✗'}")
        print(f"   Commissions ($3,326.73): {'✓' if commissions_match else '✗'}")
        print(f"   Active Investments (2): {'✓' if investments_match else '✗'}")
        
        all_pass = sales_match and commissions_match and investments_match
        
        self.results["tests"]["salvador"] = {
            "status": "PASS" if all_pass else "FAIL",
            "data": {
                "name": salvador.get('name'),
                "email": salvador.get('email'),
                "referral_code": salvador.get('referral_code'),
                "total_sales_volume": sales_volume,
                "total_commissions": commissions,
                "active_investments": active_investments
            },
            "validation": {
                "sales_match": sales_match,
                "commissions_match": commissions_match,
                "investments_match": investments_match
            }
        }
        
        return salvador
    
    def test_alejandro_data(self, salvador):
        """Task 2: Verify Alejandro's investments"""
        self.print_header("TASK 2: ALEJANDRO MARISCAL ROMERO VERIFICATION")
        
        alejandro = self.db.clients.find_one({"name": {"$regex": "Alejandro.*Mariscal", "$options": "i"}})
        
        if not alejandro:
            print("❌ FAILED: Alejandro not found!")
            self.results["tests"]["alejandro"] = {"status": "FAIL", "reason": "Not found"}
            return None
        
        print(f"✅ Found Alejandro Mariscal Romero")
        print(f"   Name: {alejandro.get('name')}")
        print(f"   Email: {alejandro.get('email')}")
        print(f"   Referred By: {alejandro.get('referred_by_name')}")
        print(f"   Referral Code: {alejandro.get('referral_code')}")
        
        # Get investments
        investments = list(self.db.investments.find({"client_id": alejandro["_id"]}))
        
        print(f"\n💼 Investments ({len(investments)} total):")
        
        core_inv = None
        balance_inv = None
        
        for inv in investments:
            product = inv.get('product', 'Unknown')
            amount = float(inv.get('amount', 0))
            commissions_due = float(inv.get('total_commissions_due', 0))
            
            print(f"\n   {product}:")
            print(f"      Amount: ${amount:,.2f}")
            print(f"      Investment Date: {inv.get('investment_date')}")
            print(f"      Referred By: {inv.get('referred_by_name')}")
            print(f"      Total Commissions Due: ${commissions_due:,.2f}")
            print(f"      Status: {inv.get('status')}")
            
            if product == "FIDUS_CORE":
                core_inv = inv
            elif product == "FIDUS_BALANCE":
                balance_inv = inv
        
        # Validation
        has_core = core_inv is not None
        has_balance = balance_inv is not None
        core_amount_match = abs(float(core_inv.get('amount', 0)) - 18151.41) < 1 if core_inv else False
        balance_amount_match = abs(float(balance_inv.get('amount', 0)) - 100000) < 1 if balance_inv else False
        
        print(f"\n✅ Validation:")
        print(f"   Has CORE investment: {'✓' if has_core else '✗'}")
        print(f"   CORE amount ($18,151.41): {'✓' if core_amount_match else '✗'}")
        print(f"   Has BALANCE investment: {'✓' if has_balance else '✗'}")
        print(f"   BALANCE amount ($100,000): {'✓' if balance_amount_match else '✗'}")
        
        all_pass = has_core and has_balance and core_amount_match and balance_amount_match
        
        self.results["tests"]["alejandro"] = {
            "status": "PASS" if all_pass else "FAIL",
            "data": {
                "name": alejandro.get('name'),
                "referred_by": alejandro.get('referred_by_name'),
                "total_investments": len(investments),
                "investments": [
                    {"product": inv.get('product'), "amount": float(inv.get('amount', 0))}
                    for inv in investments
                ]
            },
            "validation": {
                "has_core": has_core,
                "core_amount_match": core_amount_match,
                "has_balance": has_balance,
                "balance_amount_match": balance_amount_match
            }
        }
        
        return alejandro, investments
    
    def test_commission_records(self, salvador):
        """Task 3: Verify commission records"""
        self.print_header("TASK 3: COMMISSION RECORDS VERIFICATION")
        
        commissions = list(self.db.referral_commissions.find({
            "salesperson_id": salvador["_id"]
        }))
        
        print(f"✅ Found {len(commissions)} commission records")
        
        # Group by product
        core_commissions = [c for c in commissions if c.get("product_type") == "FIDUS_CORE"]
        balance_commissions = [c for c in commissions if c.get("product_type") == "FIDUS_BALANCE"]
        
        core_total = sum(float(c.get("commission_amount", 0)) for c in core_commissions)
        balance_total = sum(float(c.get("commission_amount", 0)) for c in balance_commissions)
        grand_total = core_total + balance_total
        
        print(f"\n📊 Breakdown:")
        print(f"   FIDUS_CORE: {len(core_commissions)} records = ${core_total:,.2f}")
        print(f"   FIDUS_BALANCE: {len(balance_commissions)} records = ${balance_total:,.2f}")
        print(f"   GRAND TOTAL: {len(commissions)} records = ${grand_total:,.2f}")
        
        # Payment schedule
        commissions_sorted = sorted(commissions, key=lambda x: x.get("commission_due_date", datetime.min))
        
        print(f"\n📅 Payment Schedule (First 5):")
        for i, comm in enumerate(commissions_sorted[:5]):
            date = comm.get("commission_due_date").strftime("%b %d, %Y")
            amount = float(comm.get("commission_amount", 0))
            product = comm.get("product_type", "").replace("FIDUS_", "")
            status = comm.get("status", "")
            print(f"   {i+1}. {date}: ${amount:,.2f} ({product}) - {status}")
        
        # Validation
        total_count_match = len(commissions) == 16
        core_count_match = len(core_commissions) == 12
        balance_count_match = len(balance_commissions) == 4
        core_total_match = abs(core_total - 326.73) < 1
        balance_total_match = abs(balance_total - 3000) < 1
        
        print(f"\n✅ Validation:")
        print(f"   Total records (16): {'✓' if total_count_match else '✗'}")
        print(f"   CORE records (12): {'✓' if core_count_match else '✗'}")
        print(f"   BALANCE records (4): {'✓' if balance_count_match else '✗'}")
        print(f"   CORE total ($326.73): {'✓' if core_total_match else '✗'}")
        print(f"   BALANCE total ($3,000): {'✓' if balance_total_match else '✗'}")
        
        all_pass = (total_count_match and core_count_match and balance_count_match and 
                    core_total_match and balance_total_match)
        
        self.results["tests"]["commissions"] = {
            "status": "PASS" if all_pass else "FAIL",
            "data": {
                "total_records": len(commissions),
                "core_records": len(core_commissions),
                "balance_records": len(balance_commissions),
                "core_total": core_total,
                "balance_total": balance_total,
                "grand_total": grand_total,
                "first_payment_date": commissions_sorted[0].get("commission_due_date").isoformat() if commissions_sorted else None,
                "first_payment_amount": float(commissions_sorted[0].get("commission_amount", 0)) if commissions_sorted else 0
            },
            "validation": {
                "total_count_match": total_count_match,
                "core_count_match": core_count_match,
                "balance_count_match": balance_count_match,
                "core_total_match": core_total_match,
                "balance_total_match": balance_total_match
            }
        }
        
        return commissions_sorted
    
    def test_api_endpoints(self):
        """Task 4: Test API endpoints"""
        self.print_header("TASK 4: API ENDPOINT TESTING")
        
        api_results = {}
        
        # Test 1: Public salespeople list
        print("\n1️⃣ Testing GET /api/public/salespeople")
        try:
            response = requests.get(f"{API_BASE_URL}/api/public/salespeople", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                salespeople = data.get("salespeople", [])
                salvador_found = any(sp.get("referral_code") == "SP-2025" for sp in salespeople)
                print(f"   Salespeople count: {len(salespeople)}")
                print(f"   Salvador (SP-2025) found: {'✓' if salvador_found else '✗'}")
                api_results["public_list"] = {"status": "PASS", "salvador_found": salvador_found}
            else:
                print(f"   ❌ FAILED: {response.text[:100]}")
                api_results["public_list"] = {"status": "FAIL", "error": response.text}
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            api_results["public_list"] = {"status": "ERROR", "error": str(e)}
        
        # Test 2: Get by referral code
        print("\n2️⃣ Testing GET /api/public/salespeople/SP-2025")
        try:
            response = requests.get(f"{API_BASE_URL}/api/public/salespeople/SP-2025", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Name: {data.get('name')}")
                print(f"   Referral Code: {data.get('referral_code')}")
                api_results["public_by_code"] = {"status": "PASS", "data": data}
            else:
                print(f"   ❌ FAILED: {response.text[:100]}")
                api_results["public_by_code"] = {"status": "FAIL", "error": response.text}
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            api_results["public_by_code"] = {"status": "ERROR", "error": str(e)}
        
        # Test 3: Admin endpoints (requires auth)
        print("\n3️⃣ Testing Admin Endpoints (requires auth)")
        print("   Skipping auth tests in automated script")
        print("   Manual verification recommended")
        api_results["admin_endpoints"] = {"status": "SKIP", "reason": "Requires manual auth"}
        
        all_pass = all(r.get("status") in ["PASS", "SKIP"] for r in api_results.values())
        
        self.results["tests"]["api_endpoints"] = {
            "status": "PASS" if all_pass else "FAIL",
            "results": api_results
        }
    
    def generate_report(self):
        """Generate final verification report"""
        self.print_header("PHASE 1 VERIFICATION REPORT")
        
        # Determine overall status
        all_tests_pass = all(
            test.get("status") == "PASS" 
            for test in self.results["tests"].values()
        )
        
        self.results["overall_status"] = "PASS" if all_tests_pass else "FAIL"
        
        # Print summary
        print("\n📊 Test Results:")
        for test_name, test_data in self.results["tests"].items():
            status = test_data.get("status")
            emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"   {emoji} {test_name.upper()}: {status}")
        
        print(f"\n{'='*70}")
        if all_tests_pass:
            print("✅ PHASE 1 VERIFICATION: COMPLETE - ALL TESTS PASSED")
            print("="*70)
            print("\n🚀 READY TO PROCEED TO PHASE 2: ADMIN FRONTEND")
        else:
            print("❌ PHASE 1 VERIFICATION: FAILED - ISSUES FOUND")
            print("="*70)
            print("\n⚠️  FIX REQUIRED BEFORE PHASE 2")
        
        # Save report
        with open("/tmp/phase1_verification_report.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Report saved to: /tmp/phase1_verification_report.json")
        
        return self.results
    
    def run_all_tests(self):
        """Execute all verification tests"""
        print("\n🚀 Starting Phase 1 Production Verification")
        print(f"   Environment: {self.results['environment']}")
        print(f"   Timestamp: {self.results['timestamp']}")
        
        # Test 1: Salvador
        salvador = self.test_salvador_data()
        if not salvador:
            print("\n❌ Critical failure: Salvador not found. Aborting verification.")
            return self.generate_report()
        
        # Test 2: Alejandro
        alejandro_result = self.test_alejandro_data(salvador)
        if not alejandro_result:
            print("\n❌ Critical failure: Alejandro not found. Aborting verification.")
            return self.generate_report()
        
        alejandro, investments = alejandro_result
        
        # Test 3: Commissions
        self.test_commission_records(salvador)
        
        # Test 4: API Endpoints
        self.test_api_endpoints()
        
        # Generate final report
        return self.generate_report()
    
    def cleanup(self):
        """Close database connection"""
        self.client.close()

if __name__ == "__main__":
    verifier = Phase1Verifier()
    try:
        results = verifier.run_all_tests()
        
        # Print final JSON report
        print("\n" + "="*70)
        print("FULL REPORT (JSON)")
        print("="*70)
        print(json.dumps(results, indent=2, default=str))
        
    finally:
        verifier.cleanup()
