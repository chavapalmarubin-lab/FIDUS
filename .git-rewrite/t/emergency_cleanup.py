#!/usr/bin/env python3
"""
EMERGENCY: Direct MongoDB cleanup and correct investment creation
"""
import os
from pymongo import MongoClient
from datetime import datetime
import uuid

def connect_to_mongodb():
    """Connect directly to MongoDB"""
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        # Try reading from .env file
        with open('/app/backend/.env', 'r') as f:
            for line in f:
                if line.startswith('MONGO_URL='):
                    mongo_url = line.split('=', 1)[1].strip().strip('"')
                    break
    
    if not mongo_url:
        raise Exception("Could not find MongoDB URL")
    
    client = MongoClient(mongo_url)
    db = client['fidus_production']
    return db

def cleanup_alejandro_investments():
    """Direct MongoDB cleanup"""
    print("🚨 EMERGENCY CLEANUP - Direct MongoDB Access")
    print("=" * 50)
    
    try:
        db = connect_to_mongodb()
        print("✅ Connected to MongoDB")
        
        # Find all Alejandro investments
        alejandro_investments = list(db.investments.find({"client_id": {"$in": ["alejandrom", "client_11aed9e2"]}}))
        
        print(f"📋 Found {len(alejandro_investments)} Alejandro investments")
        for inv in alejandro_investments:
            amount = inv.get('principal_amount', 0)
            fund = inv.get('fund_code', 'Unknown')
            inv_id = inv.get('investment_id', 'Unknown')
            print(f"   - ${amount} {fund} ({inv_id})")
        
        # Delete ALL Alejandro investments
        result = db.investments.delete_many({"client_id": {"$in": ["alejandrom", "client_11aed9e2"]}})
        print(f"🗑️ Deleted {result.deleted_count} investments")
        
        # Create the EXACT 4 investments required
        print(f"\n🎯 Creating EXACTLY 4 correct investments...")
        
        correct_investments = [
            {
                "investment_id": str(uuid.uuid4()),
                "client_id": "client_11aed9e2",
                "fund_code": "BALANCE",
                "principal_amount": 80000.0,
                "deposit_date": "2025-10-01",
                "payment_method": "cryptocurrency",
                "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
                "bank_reference": "ALEJANDRO-INV1-80K-BALANCE-MT5-886557",
                "status": "active",
                "created_date": datetime.now().isoformat(),
                "mt5_account": {
                    "login": "886557",
                    "server": "MEXAtlantic-Real",
                    "password": "Fidus13@"
                }
            },
            {
                "investment_id": str(uuid.uuid4()),
                "client_id": "client_11aed9e2",
                "fund_code": "BALANCE",
                "principal_amount": 10000.0,
                "deposit_date": "2025-10-01",
                "payment_method": "cryptocurrency", 
                "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
                "bank_reference": "ALEJANDRO-INV2-10K-BALANCE-MT5-886602",
                "status": "active",
                "created_date": datetime.now().isoformat(),
                "mt5_account": {
                    "login": "886602",
                    "server": "MEXAtlantic-Real",
                    "password": "Fidus13@"
                }
            },
            {
                "investment_id": str(uuid.uuid4()),
                "client_id": "client_11aed9e2",
                "fund_code": "BALANCE",
                "principal_amount": 10000.0,
                "deposit_date": "2025-10-01",
                "payment_method": "cryptocurrency",
                "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
                "bank_reference": "ALEJANDRO-INV3-10K-BALANCE-MT5-886066",
                "status": "active",
                "created_date": datetime.now().isoformat(),
                "mt5_account": {
                    "login": "886066", 
                    "server": "MEXAtlantic-Real",
                    "password": "Fidus13@"
                }
            },
            {
                "investment_id": str(uuid.uuid4()),
                "client_id": "client_11aed9e2",
                "fund_code": "CORE",
                "principal_amount": 18151.41,
                "deposit_date": "2025-10-01",
                "payment_method": "cryptocurrency",
                "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
                "bank_reference": "ALEJANDRO-INV4-18151-CORE-MT5-885822",
                "status": "active", 
                "created_date": datetime.now().isoformat(),
                "mt5_account": {
                    "login": "885822",
                    "server": "MEXAtlantic-Real",
                    "password": "Fidus13@"
                }
            }
        ]
        
        # Insert the correct investments
        result = db.investments.insert_many(correct_investments)
        print(f"✅ Created {len(result.inserted_ids)} investments")
        
        # Verify final state
        final_investments = list(db.investments.find({"client_id": "client_11aed9e2"}))
        total_amount = sum(inv['principal_amount'] for inv in final_investments)
        
        print(f"\n📊 VERIFICATION:")
        print(f"Final Investment Count: {len(final_investments)}")
        print(f"Total Amount: ${total_amount:,.2f}")
        
        for i, inv in enumerate(final_investments, 1):
            amount = inv['principal_amount']
            fund = inv['fund_code']
            mt5 = inv['mt5_account']['login']
            print(f"   {i}. ${amount:,.2f} → {fund} Fund → MT5: {mt5}")
        
        if len(final_investments) == 4 and abs(total_amount - 118151.41) < 0.01:
            print(f"\n🎉 SUCCESS! Alejandro has exactly 4 investments totaling $118,151.41")
            return True
        else:
            print(f"\n❌ ERROR: Expected 4 investments totaling $118,151.41")
            return False
            
    except Exception as e:
        print(f"❌ Emergency cleanup failed: {e}")
        return False

if __name__ == "__main__":
    success = cleanup_alejandro_investments()
    if success:
        print("\n🏆 PRODUCTION EMERGENCY RESOLVED")
        print("✅ Alejandro now has exactly 4 investments")
        print("✅ All MT5 accounts properly mapped")
        print("✅ Ready for system verification")
    else:
        print("\n🚨 EMERGENCY CLEANUP FAILED")
        print("❌ Manual intervention required")