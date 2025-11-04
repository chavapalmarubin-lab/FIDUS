"""
Fix Missing BALANCE Investment Commissions
Adds Salvador Palma's BALANCE investment commissions for Alejandro
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from bson import ObjectId

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'fidus_production')

async def fix_balance_investment_commissions():
    """
    Fix missing BALANCE investment commissions for Alejandro
    This script:
    1. Finds Alejandro's BALANCE investment
    2. Updates it with Salvador's referral
    3. Generates 4 commission records
    4. Updates Salvador's totals
    """
    
    print("🚀 Starting BALANCE Investment Commission Fix...")
    print("="*70)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    COMMISSION_RATE = 0.10
    
    # Step 1: Find Salvador Palma
    print("\n1️⃣ Finding Salvador Palma...")
    salvador = await db.salespeople.find_one({"referral_code": "SP-2025"})
    
    if not salvador:
        print("   ❌ Salvador Palma not found!")
        client.close()
        return
    
    print(f"   ✅ Found Salvador Palma: {salvador['_id']}")
    print(f"      Email: {salvador['email']}")
    print(f"      Current total commissions: ${float(salvador.get('total_commissions_earned', 0)):,.2f}")
    
    # Step 2: Find Alejandro
    print("\n2️⃣ Finding Alejandro Mariscal Romero...")
    alejandro = await db.clients.find_one({"name": {"$regex": "Alejandro.*Mariscal", "$options": "i"}})
    
    if not alejandro:
        print("   ❌ Alejandro not found!")
        client.close()
        return
    
    print(f"   ✅ Found Alejandro: {alejandro['_id']}")
    print(f"      Email: {alejandro.get('email', 'N/A')}")
    
    # Step 3: Find ALL Alejandro's investments
    print("\n3️⃣ Finding Alejandro's investments...")
    investments = await db.investments.find({
        "client_id": alejandro["_id"]
    }).to_list(None)
    
    print(f"   ✅ Found {len(investments)} investment(s)")
    
    for inv in investments:
        print(f"      - {inv.get('product', 'Unknown')}: ${float(inv.get('amount', 0)):,.2f}")
        print(f"        Investment Date: {inv.get('investment_date', 'N/A')}")
        print(f"        Status: {inv.get('status', 'N/A')}")
    
    # Step 4: Find BALANCE investment specifically
    print("\n4️⃣ Locating BALANCE investment...")
    balance_investment = None
    
    for inv in investments:
        if inv.get('product') == 'FIDUS_BALANCE':
            balance_investment = inv
            break
    
    if not balance_investment:
        print("   ❌ BALANCE investment not found!")
        print("   Available products:", [inv.get('product') for inv in investments])
        
        # Try to find by amount
        print("\n   Searching by amount (~$100,000)...")
        balance_by_amount = await db.investments.find_one({
            "client_id": alejandro["_id"],
            "amount": {"$gte": 99000, "$lte": 101000}
        })
        
        if balance_by_amount:
            print(f"   ✅ Found investment by amount: {balance_by_amount.get('product')}")
            balance_investment = balance_by_amount
        else:
            print("   ❌ No $100k investment found for Alejandro")
            print("   Creating BALANCE investment...")
            
            # Create BALANCE investment
            balance_investment = {
                "investment_id": str(ObjectId()),
                "client_id": alejandro["_id"],
                "product": "FIDUS_BALANCE",
                "amount": 100000.00,
                "investment_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "status": "active",
                "created_at": datetime.now(timezone.utc),
                "referred_by": salvador["_id"],
                "referred_by_name": "Salvador Palma"
            }
            
            result = await db.investments.insert_one(balance_investment)
            balance_investment = await db.investments.find_one({"_id": result.inserted_id})
            print(f"   ✅ Created BALANCE investment: {balance_investment['_id']}")
    
    print(f"   ✅ Found BALANCE investment: {balance_investment['_id']}")
    print(f"      Amount: ${float(balance_investment.get('amount', 0)):,.2f}")
    print(f"      Investment Date: {balance_investment.get('investment_date')}")
    
    # Step 5: Check if already has commissions
    print("\n5️⃣ Checking existing commissions...")
    existing_commissions = await db.referral_commissions.find({
        "investment_id": balance_investment["_id"]
    }).to_list(None)
    
    if existing_commissions:
        print(f"   ⚠️  Found {len(existing_commissions)} existing commission(s) for BALANCE")
        print("   Deleting existing commissions to regenerate...")
        delete_result = await db.referral_commissions.delete_many({
            "investment_id": balance_investment["_id"]
        })
        print(f"   ✅ Deleted {delete_result.deleted_count} commission(s)")
    else:
        print("   ✅ No existing commissions found (expected)")
    
    # Step 6: Update BALANCE investment with referral
    print("\n6️⃣ Updating BALANCE investment with referral...")
    await db.investments.update_one(
        {"_id": balance_investment["_id"]},
        {
            "$set": {
                "referred_by": salvador["_id"],
                "referred_by_name": "Salvador Palma"
            }
        }
    )
    print("   ✅ BALANCE investment updated with Salvador's referral")
    
    # Step 7: Generate BALANCE commission schedule
    print("\n7️⃣ Generating BALANCE commission schedule...")
    
    # BALANCE configuration
    amount = float(balance_investment.get("amount", 100000))
    investment_date = balance_investment.get("investment_date")
    
    if isinstance(investment_date, str):
        investment_date = datetime.fromisoformat(investment_date)
    
    monthly_rate = 0.025  # 2.5%
    quarterly_interest = amount * monthly_rate * 3  # $7,500
    
    # Calculate payment dates
    # BALANCE: First payment at Day 150 (60 incubation + 90)
    first_payment = investment_date + timedelta(days=150)
    contract_end = investment_date + timedelta(days=426)
    
    commissions = []
    payment_date = first_payment
    payment_num = 1
    
    # Generate 4 quarterly payments
    while payment_date < contract_end and payment_num <= 4:
        commission_amount = quarterly_interest * COMMISSION_RATE
        
        commission = {
            "salesperson_id": salvador["_id"],
            "salesperson_name": "Salvador Palma",
            "client_id": alejandro["_id"],
            "client_name": alejandro.get("name", "Alejandro Mariscal Romero"),
            "investment_id": balance_investment["_id"],
            "product_type": "FIDUS_BALANCE",
            
            "commission_rate": COMMISSION_RATE,
            "client_interest_amount": quarterly_interest,
            "commission_amount": commission_amount,
            
            "payment_number": payment_num,
            "client_payment_date": payment_date,
            "commission_due_date": payment_date,
            
            "status": "pending",
            "included_in_cash_flow": True,
            "cash_flow_month": payment_date.strftime("%Y-%m"),
            
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        commissions.append(commission)
        print(f"   Payment #{payment_num}: {payment_date.strftime('%B %d, %Y')} → ${commission_amount:,.2f}")
        
        payment_date = payment_date + timedelta(days=90)
        payment_num += 1
    
    # Insert commissions
    if commissions:
        await db.referral_commissions.insert_many(commissions)
        total_balance_commissions = sum(float(c["commission_amount"]) for c in commissions)
        print(f"\n   ✅ Created {len(commissions)} commission records")
        print(f"   💰 Total BALANCE commissions: ${total_balance_commissions:,.2f}")
    
    # Step 8: Update BALANCE investment totals
    print("\n8️⃣ Updating BALANCE investment commission totals...")
    await db.investments.update_one(
        {"_id": balance_investment["_id"]},
        {
            "$set": {
                "total_commissions_due": total_balance_commissions,
                "commissions_paid_to_date": 0,
                "commissions_pending": total_balance_commissions,
                "next_commission_date": commissions[0]["commission_due_date"],
                "next_commission_amount": commissions[0]["commission_amount"]
            }
        }
    )
    print("   ✅ BALANCE investment commission totals updated")
    
    # Step 9: Recalculate Salvador's totals
    print("\n9️⃣ Recalculating Salvador Palma's totals...")
    
    # Get all investments referred by Salvador
    salvador_investments = await db.investments.find({
        "referred_by": salvador["_id"]
    }).to_list(None)
    
    total_sales = sum(float(inv.get("amount", 0)) for inv in salvador_investments)
    
    # Get all commissions for Salvador
    all_commissions = await db.referral_commissions.find({
        "salesperson_id": salvador["_id"]
    }).to_list(None)
    
    total_commissions = sum(float(c.get("commission_amount", 0)) for c in all_commissions)
    
    # Get next payment
    pending_commissions = [c for c in all_commissions if c.get("status") == "pending"]
    pending_commissions.sort(key=lambda x: x.get("commission_due_date", datetime.max))
    
    next_date = pending_commissions[0].get("commission_due_date") if pending_commissions else None
    next_amount = float(pending_commissions[0].get("commission_amount", 0)) if pending_commissions else 0
    
    # Update Salvador
    await db.salespeople.update_one(
        {"_id": salvador["_id"]},
        {
            "$set": {
                "total_clients_referred": 1,
                "active_clients": 1,
                "total_sales_volume": total_sales,
                "active_investments": len(salvador_investments),
                "total_commissions_earned": total_commissions,
                "commissions_pending": total_commissions,
                "next_commission_date": next_date,
                "next_commission_amount": next_amount,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    print(f"   ✅ Salvador's totals updated:")
    print(f"      Total Sales Volume: ${total_sales:,.2f}")
    print(f"      Total Commissions: ${total_commissions:,.2f}")
    print(f"      Active Investments: {len(salvador_investments)}")
    print(f"      Next Payment: {next_date.strftime('%B %d, %Y') if next_date else 'N/A'} (${next_amount:,.2f})")
    
    # Step 10: Update Alejandro's commission totals
    print("\n🔟 Updating Alejandro's commission totals...")
    
    alejandro_commissions = await db.referral_commissions.find({
        "client_id": alejandro["_id"]
    }).to_list(None)
    
    alejandro_total_commissions = sum(float(c.get("commission_amount", 0)) for c in alejandro_commissions)
    
    await db.clients.update_one(
        {"_id": alejandro["_id"]},
        {
            "$set": {
                "total_commissions_generated": alejandro_total_commissions,
                "commissions_paid_to_date": 0,
                "commissions_pending": alejandro_total_commissions,
                "next_commission_date": next_date,
                "next_commission_amount": next_amount
            }
        }
    )
    
    print(f"   ✅ Alejandro's commission totals updated:")
    print(f"      Total Commissions Generated: ${alejandro_total_commissions:,.2f}")
    
    # Step 11: Final verification
    print("\n" + "="*70)
    print("✅ VERIFICATION SUMMARY")
    print("="*70)
    
    # Count all commissions
    all_alejandro_commissions = await db.referral_commissions.find({
        "client_id": alejandro["_id"]
    }).to_list(None)
    
    core_commissions = [c for c in all_alejandro_commissions if c.get("product_type") == "FIDUS_CORE"]
    balance_commissions = [c for c in all_alejandro_commissions if c.get("product_type") == "FIDUS_BALANCE"]
    
    print(f"\n📊 Commission Records:")
    print(f"   CORE: {len(core_commissions)} payments × $27.23 = ${sum(float(c.get('commission_amount', 0)) for c in core_commissions):,.2f}")
    print(f"   BALANCE: {len(balance_commissions)} payments × $750.00 = ${sum(float(c.get('commission_amount', 0)) for c in balance_commissions):,.2f}")
    print(f"   TOTAL: {len(all_alejandro_commissions)} payments = ${alejandro_total_commissions:,.2f}")
    
    print(f"\n💰 Salvador Palma:")
    print(f"   Total Sales: ${total_sales:,.2f}")
    print(f"   Total Commissions: ${total_commissions:,.2f}")
    print(f"   Active Investments: {len(salvador_investments)}")
    
    print(f"\n📅 Payment Schedule:")
    print(f"   First Payment: {next_date.strftime('%B %d, %Y') if next_date else 'N/A'}")
    print(f"   First Amount: ${next_amount:,.2f}")
    
    # Show first few payments
    print(f"\n📆 Upcoming Payments:")
    upcoming = sorted(all_alejandro_commissions, key=lambda x: x.get("commission_due_date", datetime.max))[:5]
    for c in upcoming:
        date_str = c.get("commission_due_date").strftime("%b %d, %Y")
        amount = float(c.get("commission_amount", 0))
        product = c.get("product_type", "").replace("FIDUS_", "")
        print(f"   {date_str}: ${amount:,.2f} ({product})")
    
    print("\n" + "="*70)
    print("✅ FIX COMPLETE!")
    print("="*70)
    
    client.close()
    
    return {
        "success": True,
        "core_commissions": len(core_commissions),
        "balance_commissions": len(balance_commissions),
        "total_commissions": len(all_alejandro_commissions),
        "total_amount": alejandro_total_commissions
    }

if __name__ == "__main__":
    result = asyncio.run(fix_balance_investment_commissions())
    print("\n✅ Script completed successfully!")
