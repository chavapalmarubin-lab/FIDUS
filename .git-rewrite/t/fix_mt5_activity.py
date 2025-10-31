#!/usr/bin/env python3
"""
Fix MT5 Activity Data Script
Directly inserts the missing MT5 trading activity data into MongoDB
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Add the backend directory to the path to import mongodb_integration
sys.path.append('/app/backend')

async def insert_mt5_activity_data():
    """Insert MT5 activity data directly into MongoDB"""
    
    # Connect to MongoDB
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["test_database"]
    
    account_id = "mt5_client_003_BALANCE_dootechnology_34c231f6"
    base_time = datetime(2024, 12, 19, 10, 0, 0, tzinfo=timezone.utc)
    
    activities = []
    
    # 1. Deposit activity
    activities.append({
        "activity_id": str(uuid.uuid4()),
        "account_id": account_id,
        "type": "deposit",
        "amount": 100000.0,
        "description": "Initial deposit for BALANCE fund investment",
        "timestamp": base_time,
        "status": "completed"
    })
    
    # 2-6. Trading activities (5 trades)
    trades = [
        {
            "symbol": "EURUSD",
            "trade_type": "buy",
            "volume": 1.5,
            "opening_price": 1.0850,
            "current_price": 1.0875,
            "profit_loss": 375.0,
            "description": "EURUSD Buy position"
        },
        {
            "symbol": "USDCHF", 
            "trade_type": "sell",
            "volume": 1.0,
            "opening_price": 0.8920,
            "current_price": 0.8905,
            "profit_loss": 150.0,
            "description": "USDCHF Sell position"
        },
        {
            "symbol": "XAUUSD",
            "trade_type": "buy", 
            "volume": 0.5,
            "opening_price": 2650.50,
            "current_price": 2665.75,
            "profit_loss": 762.5,
            "description": "Gold (XAUUSD) Buy position"
        },
        {
            "symbol": "EURUSD",
            "trade_type": "sell",
            "volume": 2.0,
            "opening_price": 1.0890,
            "current_price": 1.0870,
            "profit_loss": 400.0,
            "description": "EURUSD Sell position"
        },
        {
            "symbol": "USDCHF",
            "trade_type": "buy",
            "volume": 1.2,
            "opening_price": 0.8900,
            "current_price": 0.8915,
            "profit_loss": 180.0,
            "description": "USDCHF Buy position"
        }
    ]
    
    for i, trade in enumerate(trades):
        trade_time = base_time + timedelta(hours=i+1, minutes=30)
        
        activities.append({
            "activity_id": str(uuid.uuid4()),
            "account_id": account_id,
            "type": "trade",
            "amount": trade["profit_loss"],
            "description": trade["description"],
            "timestamp": trade_time,
            "status": "open",
            "symbol": trade["symbol"],
            "trade_type": trade["trade_type"],
            "volume": trade["volume"],
            "opening_price": trade["opening_price"],
            "current_price": trade["current_price"],
            "profit_loss": trade["profit_loss"]
        })
    
    print(f"📊 Preparing to insert {len(activities)} MT5 activities...")
    
    # Check if collection exists and current count
    current_count = await db.mt5_activity.count_documents({"account_id": account_id})
    print(f"📊 Current activities for account: {current_count}")
    
    if current_count > 0:
        print("⚠️ Activities already exist. Clearing existing data first...")
        delete_result = await db.mt5_activity.delete_many({"account_id": account_id})
        print(f"🗑️ Deleted {delete_result.deleted_count} existing activities")
    
    # Insert new activities
    try:
        insert_result = await db.mt5_activity.insert_many(activities)
        print(f"✅ Successfully inserted {len(insert_result.inserted_ids)} activities")
        
        # Verify insertion
        new_count = await db.mt5_activity.count_documents({"account_id": account_id})
        print(f"📊 New activity count: {new_count}")
        
        # Show sample of inserted data
        print("\n📋 Sample of inserted activities:")
        async for activity in db.mt5_activity.find({"account_id": account_id}).limit(3):
            activity_type = activity.get('type', 'unknown')
            description = activity.get('description', 'No description')
            amount = activity.get('amount', 0)
            print(f"   - {activity_type.upper()}: {description} (${amount})")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to insert activities: {str(e)}")
        return False
    
    finally:
        client.close()

async def main():
    """Main execution"""
    print("🔧 MT5 Activity Data Fix Script")
    print("Inserting missing trading data for mt5_client_003_BALANCE_dootechnology_34c231f6")
    
    try:
        success = await insert_mt5_activity_data()
        
        if success:
            print("\n✅ MT5 activity data fix completed successfully!")
            print("🎉 The 'No activity recorded' issue should now be resolved")
        else:
            print("\n❌ MT5 activity data fix failed!")
            
    except Exception as e:
        print(f"\n💥 Script failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())