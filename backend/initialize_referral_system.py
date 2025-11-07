"""
Initialize FIDUS Referral System with Salvador Palma and Alejandro Mariscal Romero
Based on SYSTEM_MASTER.md specifications
Run this script to populate the database with correct referral data
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from bson.decimal128 import Decimal128

async def initialize_referral_system():
    try:
        MONGO_URL = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(MONGO_URL)
        db = client['fidus_investment']
        
        print("\n" + "="*80)
        print("FIDUS REFERRAL SYSTEM INITIALIZATION")
        print("Based on SYSTEM_MASTER.md v2.0")
        print("="*80 + "\n")
        
        # ========================================================================
        # STEP 1: Create Salvador Palma (Salesperson)
        # ========================================================================
        print("📋 STEP 1: Creating Salvador Palma (Salesperson)")
        print("-" * 80)
        
        salvador_id = ObjectId("6909e8eaaaf69606babea151")
        
        # Check if Salvador already exists
        existing_salvador = await db.salespeople.find_one({"_id": salvador_id})
        if existing_salvador:
            print("⚠️  Salvador already exists, deleting old record...")
            await db.salespeople.delete_one({"_id": salvador_id})
        
        salvador = {
            "_id": salvador_id,
            "salesperson_id": "sp_6909e8eaaaf69606babea151",
            "name": "Salvador Palma",
            "email": "chava@alyarglobal.com",
            "phone": "+1234567891",
            "referral_code": "SP-2025",
            "referral_link": "https://fidus-investment-platform.onrender.com/prospects?ref=SP-2025",
            "total_clients_referred": 1,
            "total_sales_volume": Decimal128("118151.41"),
            "active_clients": 1,
            "active_investments": 2,
            "total_commissions_earned": Decimal128("1326.73"),
            "commissions_paid_to_date": Decimal128("0"),
            "commissions_pending": Decimal128("1326.73"),
            "preferred_payment_method": "crypto_wallet",
            "wallet_details": {},
            "active": True,
            "joined_date": datetime(2025, 9, 1, tzinfo=timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "notes": "Primary salesperson for FIDUS Investment Management"
        }
        
        await db.salespeople.insert_one(salvador)
        print(f"✅ Created Salvador Palma")
        print(f"   ID: {salvador_id}")
        print(f"   Referral Code: SP-2025")
        print(f"   Total Sales: $118,151.41")
        print(f"   Total Commissions: $1,326.73")
        
        # ========================================================================
        # STEP 2: Create Alejandro Mariscal Romero (Client)
        # ========================================================================
        print("\n📋 STEP 2: Creating Alejandro Mariscal Romero (Client)")
        print("-" * 80)
        
        alejandro_id = ObjectId()
        
        # Delete existing Alejandro if any
        existing_alejandro = await db.clients.find_one({"name": {"$regex": "Alejandro", "$options": "i"}})
        if existing_alejandro:
            print("⚠️  Alejandro already exists, deleting old record...")
            await db.clients.delete_one({"_id": existing_alejandro["_id"]})
        
        alejandro = {
            "_id": alejandro_id,
            "client_id": str(alejandro_id),
            "name": "Alejandro Mariscal Romero",
            "email": "alejandro@example.com",
            "phone": "+1234567890",
            "referred_by": salvador_id,
            "referred_by_name": "Salvador Palma",
            "referral_code": "SP-2025",
            "referral_date": datetime(2025, 9, 15, tzinfo=timezone.utc),
            "status": "active",
            "kyc_status": "approved",
            "created_at": datetime(2025, 9, 15, tzinfo=timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.clients.insert_one(alejandro)
        print(f"✅ Created Alejandro Mariscal Romero")
        print(f"   Client ID: {alejandro_id}")
        print(f"   Referred by: Salvador Palma")
        
        # ========================================================================
        # STEP 3: Create Investments
        # ========================================================================
        print("\n📋 STEP 3: Creating Investments")
        print("-" * 80)
        
        investment_date = datetime(2025, 10, 1, tzinfo=timezone.utc)
        
        # CORE Fund Investment
        core_investment_id = ObjectId()
        core_investment = {
            "_id": core_investment_id,
            "investment_id": f"INV-{str(core_investment_id)[:8]}",
            "client_id": str(alejandro_id),
            "client_name": "Alejandro Mariscal Romero",
            "fund_type": "CORE",
            "product": "FIDUS_CORE",
            "amount": Decimal128("18151.41"),
            "principal_amount": Decimal128("18151.41"),
            "start_date": investment_date,
            "investment_date": investment_date,
            "contract_end_date": investment_date + timedelta(days=426),  # 14 months
            "first_payment_date": investment_date + timedelta(days=90),  # After 2-month incubation
            "status": "active",
            "referral_salesperson_id": "sp_6909e8eaaaf69606babea151",
            "referred_by": salvador_id,
            "referred_by_name": "Salvador Palma",
            "interest_rate": 0.015,  # 1.5% monthly
            "payment_frequency": "monthly",
            "total_expected_return": Decimal128("3267.25"),  # 12 months × $272.27
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.investments.insert_one(core_investment)
        print(f"✅ Created CORE Investment")
        print(f"   Amount: $18,151.41")
        print(f"   Interest Rate: 1.5% monthly")
        print(f"   First Payment: {core_investment['first_payment_date'].strftime('%Y-%m-%d')}")
        
        # BALANCE Fund Investment
        balance_investment_id = ObjectId()
        balance_investment = {
            "_id": balance_investment_id,
            "investment_id": f"INV-{str(balance_investment_id)[:8]}",
            "client_id": str(alejandro_id),
            "client_name": "Alejandro Mariscal Romero",
            "fund_type": "BALANCE",
            "product": "FIDUS_BALANCE",
            "amount": Decimal128("100000.00"),
            "principal_amount": Decimal128("100000.00"),
            "start_date": investment_date,
            "investment_date": investment_date,
            "contract_end_date": investment_date + timedelta(days=426),  # 14 months
            "first_payment_date": investment_date + timedelta(days=150),  # After 2-month incubation, then quarterly
            "status": "active",
            "referral_salesperson_id": "sp_6909e8eaaaf69606babea151",
            "referred_by": salvador_id,
            "referred_by_name": "Salvador Palma",
            "interest_rate": 0.025,  # 2.5% monthly (paid quarterly)
            "payment_frequency": "quarterly",
            "total_expected_return": Decimal128("30000.00"),  # 4 quarters × $7,500
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.investments.insert_one(balance_investment)
        print(f"✅ Created BALANCE Investment")
        print(f"   Amount: $100,000.00")
        print(f"   Interest Rate: 2.5% monthly (paid quarterly)")
        print(f"   First Payment: {balance_investment['first_payment_date'].strftime('%Y-%m-%d')}")
        
        # ========================================================================
        # STEP 4: Generate Commission Records
        # ========================================================================
        print("\n📋 STEP 4: Generating Commission Records")
        print("-" * 80)
        
        # Delete existing commissions
        await db.referral_commissions.delete_many({"salesperson_id": "sp_6909e8eaaaf69606babea151"})
        
        commissions = []
        commission_summary = {
            "core_monthly": 0,
            "balance_quarterly": 0,
            "total": 0
        }
        
        # CORE Fund Commissions (12 monthly payments)
        # Monthly interest: $18,151.41 × 1.5% = $272.27
        # Commission: $272.27 × 10% = $27.23
        monthly_interest = 18151.41 * 0.015
        monthly_commission = monthly_interest * 0.10
        
        first_core_payment = investment_date + timedelta(days=90)  # Dec 30, 2025
        
        for i in range(12):
            payment_date = first_core_payment + timedelta(days=30*i)
            commission = {
                "_id": ObjectId(),
                "commission_id": f"COMM-CORE-{i+1:02d}",
                "salesperson_id": "sp_6909e8eaaaf69606babea151",
                "salesperson_name": "Salvador Palma",
                "client_id": alejandro_id,
                "client_name": "Alejandro Mariscal Romero",
                "investment_id": core_investment_id,
                "fund_type": "CORE",
                "product_type": "FIDUS_CORE",
                "commission_rate": 0.10,
                "client_interest_amount": Decimal128(f"{monthly_interest:.2f}"),
                "commission_amount": Decimal128(f"{monthly_commission:.2f}"),
                "payment_number": i + 1,
                "payment_month": payment_date.strftime("%Y-%m"),
                "payment_date": payment_date,
                "commission_due_date": payment_date,
                "status": "pending",
                "included_in_cash_flow": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            commissions.append(commission)
            commission_summary["core_monthly"] += monthly_commission
        
        print(f"✅ Generated 12 CORE monthly commissions")
        print(f"   Monthly Amount: ${monthly_commission:.2f}")
        print(f"   Total CORE: ${commission_summary['core_monthly']:.2f}")
        
        # BALANCE Fund Commissions (4 quarterly payments)
        # Quarterly interest: $100,000 × 2.5% × 3 = $7,500
        # Commission: $7,500 × 10% = $750
        quarterly_interest = 100000 * 0.025 * 3
        quarterly_commission = quarterly_interest * 0.10
        
        first_balance_payment = investment_date + timedelta(days=150)  # Feb 28, 2026
        
        for i in range(4):
            payment_date = first_balance_payment + timedelta(days=90*i)
            commission = {
                "_id": ObjectId(),
                "commission_id": f"COMM-BALANCE-{i+1:02d}",
                "salesperson_id": "sp_6909e8eaaaf69606babea151",
                "salesperson_name": "Salvador Palma",
                "client_id": alejandro_id,
                "client_name": "Alejandro Mariscal Romero",
                "investment_id": balance_investment_id,
                "fund_type": "BALANCE",
                "product_type": "FIDUS_BALANCE",
                "commission_rate": 0.10,
                "client_interest_amount": Decimal128(f"{quarterly_interest:.2f}"),
                "commission_amount": Decimal128(f"{quarterly_commission:.2f}"),
                "payment_number": i + 1,
                "payment_month": payment_date.strftime("%Y-%m"),
                "payment_date": payment_date,
                "commission_due_date": payment_date,
                "status": "pending",
                "included_in_cash_flow": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            commissions.append(commission)
            commission_summary["balance_quarterly"] += quarterly_commission
        
        print(f"✅ Generated 4 BALANCE quarterly commissions")
        print(f"   Quarterly Amount: ${quarterly_commission:.2f}")
        print(f"   Total BALANCE: ${commission_summary['balance_quarterly']:.2f}")
        
        # Insert all commissions
        if commissions:
            await db.referral_commissions.insert_many(commissions)
            commission_summary["total"] = commission_summary["core_monthly"] + commission_summary["balance_quarterly"]
            
            print(f"\n📊 Commission Summary:")
            print(f"   Total Commissions: ${commission_summary['total']:.2f}")
            print(f"   Total Records: {len(commissions)}")
        
        # ========================================================================
        # STEP 5: Verify Data
        # ========================================================================
        print("\n📋 STEP 5: Verifying Database")
        print("-" * 80)
        
        # Verify Salvador
        salvador_check = await db.salespeople.find_one({"_id": salvador_id})
        if salvador_check:
            print(f"✅ Salvador verified:")
            print(f"   Total Sales: ${float(salvador_check['total_sales_volume'].to_decimal()):,.2f}")
            print(f"   Total Commissions: ${float(salvador_check['total_commissions_earned'].to_decimal()):,.2f}")
        
        # Verify Alejandro
        alejandro_check = await db.clients.find_one({"_id": alejandro_id})
        if alejandro_check:
            print(f"✅ Alejandro verified:")
            print(f"   Client ID: {alejandro_check['_id']}")
            print(f"   Referred by: {alejandro_check['referred_by_name']}")
        
        # Verify Investments
        investment_count = await db.investments.count_documents({"client_id": str(alejandro_id)})
        print(f"✅ Investments verified: {investment_count} records")
        
        # Verify Commissions
        commission_count = await db.referral_commissions.count_documents({"salesperson_id": "sp_6909e8eaaaf69606babea151"})
        print(f"✅ Commissions verified: {commission_count} records")
        
        # Show next 5 commission dates
        upcoming_commissions = await db.referral_commissions.find(
            {"salesperson_id": "sp_6909e8eaaaf69606babea151"}
        ).sort("payment_date", 1).limit(5).to_list(5)
        
        print(f"\n📅 Next 5 Commission Payment Dates:")
        for comm in upcoming_commissions:
            pay_date = comm['payment_date']
            amount = float(comm['commission_amount'].to_decimal())
            fund = comm['fund_type']
            print(f"   {pay_date.strftime('%Y-%m-%d')}: ${amount:.2f} ({fund})")
        
        print("\n" + "="*80)
        print("✅ INITIALIZATION COMPLETE")
        print("="*80 + "\n")
        
        print("Summary:")
        print(f"  • 1 Salesperson (Salvador Palma)")
        print(f"  • 1 Client (Alejandro Mariscal Romero)")
        print(f"  • 2 Investments ($118,151.41 total)")
        print(f"  • {len(commissions)} Commission Records ($1,326.73 total)")
        print(f"\nReferral System is now ready for use!")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(initialize_referral_system())
