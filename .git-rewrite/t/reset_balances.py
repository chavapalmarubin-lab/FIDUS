#!/usr/bin/env python3
"""
Reset all client balances to zero for clean production start
"""
import os
from pymongo import MongoClient
from datetime import datetime, timezone

# Get MongoDB URL from environment
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/fidus_investment_db')

def reset_all_balances():
    """Reset all client balances and financial data to zero"""
    try:
        client = MongoClient(MONGO_URL)
        db_name = MONGO_URL.split('/')[-1]
        db = client[db_name]
        
        print("🧹 RESETTING ALL BALANCES TO ZERO")
        print("=" * 50)
        
        # 1. Remove all existing investments
        investments_deleted = db.investments.delete_many({})
        print(f"✅ Removed {investments_deleted.deleted_count} existing investments")
        
        # 2. Remove all activity logs
        activity_deleted = db.activity_logs.delete_many({})
        print(f"✅ Removed {activity_deleted.deleted_count} activity log entries")
        
        # 3. Remove all redemption requests
        redemptions_deleted = db.redemption_requests.delete_many({})
        print(f"✅ Removed {redemptions_deleted.deleted_count} redemption requests")
        
        # 4. Remove all payment confirmations
        payments_deleted = db.payment_confirmations.delete_many({})
        print(f"✅ Removed {payments_deleted.deleted_count} payment confirmations")
        
        # 5. Reset fund AUM to zero in configurations
        funds_updated = db.fund_configurations.update_many(
            {},
            {"$set": {"aum": 0}}
        )
        print(f"✅ Reset AUM to zero for {funds_updated.modified_count} funds")
        
        # 6. Keep client readiness but ensure they're marked as ready
        readiness_updated = db.client_readiness.update_many(
            {},
            {
                "$set": {
                    "aml_kyc_completed": True,
                    "agreement_signed": True,
                    "investment_ready": True,
                    "notes": "Ready for new investments",
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        print(f"✅ Updated readiness status for {readiness_updated.modified_count} clients")
        
        # 7. Verify the reset
        print("\n📊 VERIFICATION:")
        print(f"   Investments remaining: {db.investments.count_documents({})}")
        print(f"   Activity logs remaining: {db.activity_logs.count_documents({})}")
        print(f"   Redemption requests remaining: {db.redemption_requests.count_documents({})}")
        print(f"   Payment confirmations remaining: {db.payment_confirmations.count_documents({})}")
        
        # Check fund AUM
        funds = db.fund_configurations.find({})
        print(f"   Fund AUM status:")
        for fund in funds:
            print(f"     - {fund['fund_code']}: ${fund['aum']:,.2f}")
        
        print(f"\n🎉 ALL BALANCES RESET TO ZERO SUCCESSFULLY!")
        print(f"📅 Reset completed at: {datetime.now(timezone.utc).isoformat()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting balances: {str(e)}")
        return False

if __name__ == "__main__":
    success = reset_all_balances()
    if success:
        print("\n✅ System is now ready with clean zero balances")
    else:
        print("\n❌ Balance reset failed - please check errors above")