"""
FIDUS System Compliance Verification
Verifies MongoDB data and API responses follow SYSTEM_MASTER.md specifications
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from bson import ObjectId
from bson.decimal128 import Decimal128

async def verify_system_compliance():
    try:
        MONGO_URL = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(MONGO_URL)
        db = client['fidus_investment']
        
        print("\n" + "="*80)
        print("FIDUS SYSTEM COMPLIANCE VERIFICATION")
        print("Checking MongoDB Data Against SYSTEM_MASTER.md")
        print("="*80 + "\n")
        
        compliance_report = {
            "salespeople": {"pass": True, "issues": []},
            "clients": {"pass": True, "issues": []},
            "investments": {"pass": True, "issues": []},
            "commissions": {"pass": True, "issues": []},
            "field_naming": {"pass": True, "issues": []}
        }
        
        # ========================================================================
        # 1. VERIFY SALVADOR PALMA (SYSTEM_MASTER.md Section 7.3)
        # ========================================================================
        print("📋 1. VERIFYING SALESPERSON - Salvador Palma")
        print("-" * 80)
        
        salvador = await db.salespeople.find_one({"referral_code": "SP-2025"})
        if not salvador:
            print("❌ FAILED: Salvador Palma not found")
            compliance_report["salespeople"]["pass"] = False
            compliance_report["salespeople"]["issues"].append("Salvador Palma missing")
        else:
            # Check required fields per SYSTEM_MASTER.md
            required_fields = {
                "salesperson_id": "sp_6909e8eaaaf69606babea151",
                "referral_code": "SP-2025",
                "email": "chava@alyarglobal.com",
                "phone": "+1234567891"
            }
            
            all_correct = True
            for field, expected_value in required_fields.items():
                actual_value = salvador.get(field)
                if actual_value != expected_value:
                    print(f"   ⚠️  {field}: Expected '{expected_value}', got '{actual_value}'")
                    compliance_report["salespeople"]["issues"].append(f"{field} mismatch")
                    all_correct = False
                else:
                    print(f"   ✅ {field}: {actual_value}")
            
            # Check financial data
            total_sales = float(salvador.get('total_sales_volume', Decimal128('0')).to_decimal() if isinstance(salvador.get('total_sales_volume'), Decimal128) else salvador.get('total_sales_volume', 0))
            total_commissions = float(salvador.get('total_commissions_earned', Decimal128('0')).to_decimal() if isinstance(salvador.get('total_commissions_earned'), Decimal128) else salvador.get('total_commissions_earned', 0))
            
            print(f"\n   💰 Financial Data:")
            print(f"      Total Sales: ${total_sales:,.2f} (Expected: $118,151.41)")
            print(f"      Total Commissions: ${total_commissions:,.2f} (Expected: $3,326.73)")
            
            if abs(total_sales - 118151.41) > 0.01:
                compliance_report["salespeople"]["issues"].append(f"Total sales mismatch: ${total_sales:,.2f}")
            if abs(total_commissions - 3326.73) > 0.01:
                compliance_report["salespeople"]["issues"].append(f"Total commissions mismatch: ${total_commissions:,.2f}")
        
        # ========================================================================
        # 2. VERIFY ALEJANDRO MARISCAL ROMERO (SYSTEM_MASTER.md Section 6.1)
        # ========================================================================
        print("\n📋 2. VERIFYING CLIENT - Alejandro Mariscal Romero")
        print("-" * 80)
        
        alejandro = await db.clients.find_one({"name": {"$regex": "Alejandro", "$options": "i"}})
        if not alejandro:
            print("❌ FAILED: Alejandro not found")
            compliance_report["clients"]["pass"] = False
            compliance_report["clients"]["issues"].append("Alejandro missing")
        else:
            print(f"   ✅ Client ID: {alejandro['_id']}")
            print(f"   ✅ Name: {alejandro.get('name')}")
            print(f"   ✅ Email: {alejandro.get('email')}")
            print(f"   ✅ Referred by: {alejandro.get('referred_by_name', 'Not set')}")
            
            # Check if user account exists
            client_id_str = str(alejandro['_id'])
            user = await db.users.find_one({"client_id": client_id_str})
            if user:
                print(f"   ✅ User Account: username='{user.get('username')}', type='{user.get('type')}', status='{user.get('status')}'")
            else:
                print(f"   ⚠️  No user account for login")
                compliance_report["clients"]["issues"].append("Missing user account")
        
        # ========================================================================
        # 3. VERIFY INVESTMENTS (SYSTEM_MASTER.md Section 8)
        # ========================================================================
        print("\n📋 3. VERIFYING INVESTMENTS")
        print("-" * 80)
        
        if alejandro:
            client_id_str = str(alejandro['_id'])
            investments = await db.investments.find({"client_id": client_id_str}).to_list(None)
            
            print(f"   Found {len(investments)} investments")
            
            expected_investments = {
                "CORE": {"amount": 18151.41, "interest_rate": 0.015, "payment_frequency": "monthly"},
                "BALANCE": {"amount": 100000.00, "interest_rate": 0.025, "payment_frequency": "quarterly"}
            }
            
            for inv in investments:
                fund_type = inv.get('fund_type')
                fund_code = inv.get('fund_code')
                
                # Check Decimal128 handling
                if isinstance(inv.get('amount'), Decimal128):
                    amount = float(inv.get('amount').to_decimal())
                else:
                    amount = float(inv.get('amount', 0))
                
                print(f"\n   📊 {fund_type} Investment:")
                print(f"      Investment ID: {inv.get('investment_id')}")
                print(f"      Fund Code: {fund_code} (should match fund_type)")
                print(f"      Amount: ${amount:,.2f}")
                print(f"      Interest Rate: {inv.get('interest_rate', 0)*100}%")
                print(f"      Payment Frequency: {inv.get('payment_frequency', 'N/A')}")
                print(f"      Start Date: {inv.get('start_date', 'N/A')}")
                print(f"      Current Value: ${inv.get('current_value', 0):,.2f}")
                
                # Verify against expected values
                if fund_type in expected_investments:
                    expected = expected_investments[fund_type]
                    if abs(amount - expected["amount"]) > 0.01:
                        compliance_report["investments"]["issues"].append(f"{fund_type} amount mismatch")
                    if inv.get('interest_rate') != expected["interest_rate"]:
                        compliance_report["investments"]["issues"].append(f"{fund_type} interest rate mismatch")
                
                # Check field naming (should be snake_case)
                if fund_code != fund_type:
                    print(f"      ⚠️  fund_code '{fund_code}' != fund_type '{fund_type}'")
                    compliance_report["field_naming"]["issues"].append(f"Investment {inv.get('investment_id')}: fund_code mismatch")
        
        # ========================================================================
        # 4. VERIFY COMMISSION RECORDS (SYSTEM_MASTER.md Section 7.4)
        # ========================================================================
        print("\n📋 4. VERIFYING COMMISSION RECORDS")
        print("-" * 80)
        
        commissions = await db.referral_commissions.find({"salesperson_id": "sp_6909e8eaaaf69606babea151"}).to_list(None)
        
        print(f"   Total Commission Records: {len(commissions)}")
        print(f"   Expected: 16 records (12 CORE monthly + 4 BALANCE quarterly)")
        
        if len(commissions) != 16:
            print(f"   ⚠️  Commission count mismatch!")
            compliance_report["commissions"]["issues"].append(f"Expected 16, found {len(commissions)}")
        
        # Group by fund type
        core_commissions = [c for c in commissions if c.get('fund_type') == 'CORE']
        balance_commissions = [c for c in commissions if c.get('fund_type') == 'BALANCE']
        
        print(f"\n   CORE Fund Commissions: {len(core_commissions)} (Expected: 12)")
        print(f"   BALANCE Fund Commissions: {len(balance_commissions)} (Expected: 4)")
        
        # Check commission amounts per SYSTEM_MASTER.md
        if core_commissions:
            sample_core = core_commissions[0]
            if isinstance(sample_core.get('commission_amount'), Decimal128):
                core_amount = float(sample_core.get('commission_amount').to_decimal())
            else:
                core_amount = float(sample_core.get('commission_amount', 0))
            print(f"   CORE Monthly Amount: ${core_amount:.2f} (Expected: $27.23)")
            if abs(core_amount - 27.23) > 0.01:
                compliance_report["commissions"]["issues"].append(f"CORE commission amount: ${core_amount:.2f}")
        
        if balance_commissions:
            sample_balance = balance_commissions[0]
            if isinstance(sample_balance.get('commission_amount'), Decimal128):
                balance_amount = float(sample_balance.get('commission_amount').to_decimal())
            else:
                balance_amount = float(sample_balance.get('commission_amount', 0))
            print(f"   BALANCE Quarterly Amount: ${balance_amount:.2f} (Expected: $750.00)")
            if abs(balance_amount - 750.00) > 0.01:
                compliance_report["commissions"]["issues"].append(f"BALANCE commission amount: ${balance_amount:.2f}")
        
        # Show next 5 payment dates
        print(f"\n   📅 Next 5 Commission Payment Dates:")
        upcoming = sorted(commissions, key=lambda x: x.get('payment_date', datetime.max))[:5]
        for comm in upcoming:
            pay_date = comm.get('payment_date')
            if isinstance(comm.get('commission_amount'), Decimal128):
                amt = float(comm.get('commission_amount').to_decimal())
            else:
                amt = float(comm.get('commission_amount', 0))
            fund = comm.get('fund_type')
            status = comm.get('status')
            print(f"      {pay_date.strftime('%Y-%m-%d')}: ${amt:.2f} ({fund}) - Status: {status}")
        
        # ========================================================================
        # 5. VERIFY FIELD NAMING STANDARDS
        # ========================================================================
        print("\n📋 5. VERIFYING FIELD NAMING STANDARDS")
        print("-" * 80)
        print("   Rule: MongoDB uses snake_case (per DATABASE_FIELD_STANDARDS.md)")
        print("   Rule: API responses use camelCase")
        
        # Check a few documents for proper snake_case
        field_checks = []
        
        if salvador:
            for key in salvador.keys():
                if key != '_id' and '-' in key:
                    field_checks.append(f"Salesperson: '{key}' contains hyphen (should be underscore)")
                if key != '_id' and key[0].isupper():
                    field_checks.append(f"Salesperson: '{key}' starts with uppercase (should be lowercase)")
        
        if investments:
            for inv in investments:
                for key in inv.keys():
                    if key != '_id' and '-' in key:
                        field_checks.append(f"Investment: '{key}' contains hyphen")
                    if key != '_id' and key[0].isupper():
                        field_checks.append(f"Investment: '{key}' starts with uppercase")
        
        if field_checks:
            print(f"   ⚠️  Found {len(field_checks)} field naming issues:")
            for issue in field_checks[:5]:  # Show first 5
                print(f"      - {issue}")
                compliance_report["field_naming"]["issues"].append(issue)
        else:
            print(f"   ✅ All fields follow snake_case convention")
        
        # ========================================================================
        # COMPLIANCE SUMMARY
        # ========================================================================
        print("\n" + "="*80)
        print("COMPLIANCE SUMMARY")
        print("="*80 + "\n")
        
        all_passed = True
        for category, result in compliance_report.items():
            status = "✅ PASS" if result["pass"] and len(result["issues"]) == 0 else "⚠️  ISSUES"
            print(f"{category.upper()}: {status}")
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"   - {issue}")
                all_passed = False
        
        if all_passed:
            print(f"\n🎉 ALL CHECKS PASSED - System is compliant with SYSTEM_MASTER.md")
        else:
            print(f"\n⚠️  Some issues found - review above details")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_system_compliance())
