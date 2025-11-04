"""
FIDUS Referral System Migration Script
Creates Salvador Palma and generates commission schedule for Alejandro
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'fidus_production')

async def generate_payment_schedule_for_investment(investment: dict) -> list:
    """Generate payment schedule based on investment product type"""
    fund_config = {
        "FIDUS_CORE": {
            "rate": 0.015,
            "frequency_days": 30,
            "first_payment_days": 90
        },
        "FIDUS_BALANCE": {
            "rate": 0.025,
            "frequency_days": 90,
            "first_payment_days": 150
        },
        "FIDUS_DYNAMIC": {
            "rate": 0.035,
            "frequency_days": 180,
            "first_payment_days": 240
        }
    }
    
    product = investment.get("product", "")
    if product not in fund_config:
        raise ValueError(f"Unknown product: {product}")
    
    config = fund_config[product]
    amount = float(investment.get("amount", 0))
    start_date = investment.get("investment_date")
    
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    
    contract_end = start_date + timedelta(days=426)
    monthly_interest = amount * config["rate"]
    
    schedule = []
    payment_date = start_date + timedelta(days=config["first_payment_days"])
    payment_num = 1
    
    # Calculate interest per payment
    if config["frequency_days"] == 30:
        interest_per_payment = monthly_interest
    elif config["frequency_days"] == 90:
        interest_per_payment = monthly_interest * 3
    elif config["frequency_days"] == 180:
        interest_per_payment = monthly_interest * 6
    else:
        interest_per_payment = monthly_interest
    
    # Regular payments
    while payment_date < contract_end:
        schedule.append({
            "payment_number": payment_num,
            "date": payment_date,
            "interest_amount": interest_per_payment,
            "type": "interest"
        })
        payment_date = payment_date + timedelta(days=config["frequency_days"])
        payment_num += 1
    
    # Final payment
    schedule.append({
        "payment_number": payment_num,
        "date": contract_end,
        "interest_amount": interest_per_payment,
        "principal": amount,
        "type": "final"
    })
    
    return schedule

async def migrate_referral_system():
    """
    One-time migration to:
    1. Create Salvador Palma as salesperson
    2. Update Alejandro's client record
    3. Generate commission schedules for both investments
    """
    
    print("🚀 Starting Referral System Migration...")
    print("=" * 70)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Step 1: Create Salvador Palma
    print("\n1️⃣ Creating Salvador Palma...")
    
    salvador = {
        "name": "Salvador Palma",
        "email": "chava@alyarglobal.com",
        "phone": "+1917-456-2151",
        "referral_code": "SP-2025",
        "referral_link": "https://fidus-investment-platform.onrender.com/prospects?ref=SP-2025",
        "total_clients_referred": 0,
        "total_sales_volume": 0,
        "active_clients": 0,
        "active_investments": 0,
        "total_commissions_earned": 0,
        "commissions_paid_to_date": 0,
        "commissions_pending": 0,
        "preferred_payment_method": "crypto_wallet",
        "wallet_details": {
            "wallet_type": "USDT",
            "wallet_address": "",
            "network": "TRC20"
        },
        "active": True,
        "joined_date": datetime(2025, 1, 1, tzinfo=timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "notes": "Migration - First salesperson"
    }
    
    # Check if already exists
    existing = await db.salespeople.find_one({"email": salvador["email"]})
    if existing:
        print(f"   ✅ Salvador Palma already exists: {existing['_id']}")
        salvador_id = existing["_id"]
    else:
        result = await db.salespeople.insert_one(salvador)
        salvador_id = result.inserted_id
        print(f"   ✅ Created Salvador Palma: {salvador_id}")
    
    # Step 2: Find Alejandro
    print("\n2️⃣ Finding Alejandro Mariscal Romero...")
    
    alejandro = await db.clients.find_one({"name": {"$regex": "Alejandro.*Mariscal", "$options": "i"}})
    
    if not alejandro:
        # Try alternate search
        alejandro = await db.users.find_one({"username": "alejandro_mariscal"})
        if alejandro:
            # Create client record if only user exists
            client_data = {
                "name": "Alejandro Mariscal Romero",
                "email": alejandro.get("email", "alejandro@email.com"),
                "phone": "+525555555555",
                "status": "active",
                "created_at": datetime.now(timezone.utc)
            }
            result = await db.clients.insert_one(client_data)
            alejandro = await db.clients.find_one({"_id": result.inserted_id})
    
    if not alejandro:
        print("   ❌ Could not find Alejandro's client record")
        print("   Please check client name and update script")
        return
    
    print(f"   ✅ Found Alejandro: {alejandro['_id']}")
    print(f"      Name: {alejandro.get('name', 'N/A')}")
    
    # Step 3: Update Alejandro's client record
    print("\n3️⃣ Updating Alejandro's referral...")
    
    await db.clients.update_one(
        {"_id": alejandro["_id"]},
        {
            "$set": {
                "referred_by": salvador_id,
                "referred_by_name": "Salvador Palma",
                "referral_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "referral_code": "SP-2025"
            }
        }
    )
    print("   ✅ Updated Alejandro's client record")
    
    # Step 4: Find Alejandro's investments
    print("\n4️⃣ Finding Alejandro's investments...")
    
    investments = await db.investments.find({"client_id": alejandro["_id"]}).to_list(None)
    
    if not investments or len(investments) == 0:
        print("   ⚠️  No investments found for Alejandro")
        print("   Creating sample investments for testing...")
        
        import uuid
        
        # Create sample investments
        sample_investments = [
            {
                "investment_id": str(uuid.uuid4()),
                "client_id": alejandro["_id"],
                "product": "FIDUS_CORE",
                "amount": 18151.41,
                "investment_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "status": "active",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "investment_id": str(uuid.uuid4()),
                "client_id": alejandro["_id"],
                "product": "FIDUS_BALANCE",
                "amount": 100000.00,
                "investment_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "status": "active",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        for inv in sample_investments:
            result = await db.investments.insert_one(inv)
            print(f"   ✅ Created {inv['product']}: ${inv['amount']:,.2f}")
        
        investments = await db.investments.find({"client_id": alejandro["_id"]}).to_list(None)
    
    print(f"   ✅ Found {len(investments)} investments")
    
    for inv in investments:
        print(f"      - {inv.get('product', 'Unknown')}: ${float(inv.get('amount', 0)):,.2f}")
    
    # Step 5: Update investments and generate commission schedules
    print("\n5️⃣ Generating commission schedules...")
    
    total_commissions = 0
    first_commission_date = None
    first_commission_amount = None
    COMMISSION_RATE = 0.10
    
    for investment in investments:
        print(f"\n   Processing {investment.get('product', 'Unknown')}...")
        
        # Update investment with referral
        await db.investments.update_one(
            {"_id": investment["_id"]},
            {
                "$set": {
                    "referred_by": salvador_id,
                    "referred_by_name": "Salvador Palma"
                }
            }
        )
        
        # Generate payment schedule
        try:
            payment_schedule = await generate_payment_schedule_for_investment(investment)
            print(f"      Generated {len(payment_schedule)} payments")
        except Exception as e:
            print(f"      ❌ Error generating schedule: {e}")
            continue
        
        # Generate commissions
        commissions = []
        investment_total = 0
        
        for payment in payment_schedule:
            if payment.get("interest_amount", 0) > 0:
                commission_amount = float(payment["interest_amount"]) * COMMISSION_RATE
                
                commission = {
                    "salesperson_id": salvador_id,
                    "salesperson_name": "Salvador Palma",
                    "client_id": alejandro["_id"],
                    "client_name": alejandro.get("name", "Alejandro Mariscal Romero"),
                    "investment_id": investment["_id"],
                    "product_type": investment.get("product", ""),
                    
                    "commission_rate": COMMISSION_RATE,
                    "client_interest_amount": payment["interest_amount"],
                    "commission_amount": commission_amount,
                    
                    "payment_number": payment["payment_number"],
                    "client_payment_date": payment["date"],
                    "commission_due_date": payment["date"],
                    
                    "status": "pending",
                    "included_in_cash_flow": True,
                    "cash_flow_month": payment["date"].strftime("%Y-%m"),
                    
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                commissions.append(commission)
                investment_total += commission_amount
                
                # Track first commission
                if first_commission_date is None or payment["date"] < first_commission_date:
                    first_commission_date = payment["date"]
                    first_commission_amount = commission_amount
        
        # Insert commissions
        if commissions:
            await db.referral_commissions.insert_many(commissions)
            print(f"      ✅ Created {len(commissions)} commission records")
            print(f"      💰 Total commissions: ${investment_total:,.2f}")
            
            # Update investment
            await db.investments.update_one(
                {"_id": investment["_id"]},
                {
                    "$set": {
                        "total_commissions_due": investment_total,
                        "commissions_paid_to_date": 0,
                        "commissions_pending": investment_total,
                        "next_commission_date": commissions[0]["commission_due_date"],
                        "next_commission_amount": commissions[0]["commission_amount"]
                    }
                }
            )
            
            total_commissions += investment_total
    
    # Step 6: Update Salvador's totals
    print("\n6️⃣ Updating Salvador Palma's metrics...")
    
    await db.salespeople.update_one(
        {"_id": salvador_id},
        {
            "$set": {
                "total_clients_referred": 1,
                "active_clients": 1,
                "total_sales_volume": sum(float(inv.get("amount", 0)) for inv in investments),
                "active_investments": len(investments),
                "total_commissions_earned": total_commissions,
                "commissions_pending": total_commissions,
                "next_commission_date": first_commission_date,
                "next_commission_amount": first_commission_amount
            }
        }
    )
    print("   ✅ Updated Salvador's metrics")
    
    # Step 7: Update Alejandro's commission totals
    print("\n7️⃣ Updating Alejandro's commission totals...")
    
    await db.clients.update_one(
        {"_id": alejandro["_id"]},
        {
            "$set": {
                "total_commissions_generated": total_commissions,
                "commissions_paid_to_date": 0,
                "commissions_pending": total_commissions,
                "next_commission_date": first_commission_date,
                "next_commission_amount": first_commission_amount
            }
        }
    )
    print("   ✅ Updated Alejandro's commission totals")
    
    # Create indexes
    print("\n8️⃣ Creating database indexes...")
    
    try:
        await db.salespeople.create_index([("referral_code", 1)], unique=True)
        await db.salespeople.create_index([("email", 1)], unique=True)
        await db.salespeople.create_index([("active", 1)])
        print("   ✅ Created salespeople indexes")
    except Exception as e:
        print(f"   ⚠️  Index creation skipped (may already exist): {e}")
    
    try:
        await db.referral_commissions.create_index([("salesperson_id", 1), ("status", 1)])
        await db.referral_commissions.create_index([("client_id", 1)])
        await db.referral_commissions.create_index([("investment_id", 1)])
        await db.referral_commissions.create_index([("commission_due_date", 1)])
        await db.referral_commissions.create_index([("status", 1), ("commission_due_date", 1)])
        print("   ✅ Created referral_commissions indexes")
    except Exception as e:
        print(f"   ⚠️  Index creation skipped (may already exist): {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print(f"Salvador Palma ID: {salvador_id}")
    print(f"Referral Code: SP-2025")
    print(f"Referral Link: https://fidus-investment-platform.onrender.com/prospects?ref=SP-2025")
    print(f"Client: {alejandro.get('name', 'Alejandro Mariscal Romero')}")
    print(f"Investments: {len(investments)}")
    print(f"Total Commissions: ${total_commissions:,.2f}")
    if first_commission_date:
        print(f"First Payment: {first_commission_date.strftime('%B %d, %Y')}")
        print(f"First Amount: ${first_commission_amount:,.2f}")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_referral_system())
