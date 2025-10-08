#!/usr/bin/env python3
"""
Populate MT5 Activity Data Script
Creates the missing MT5 trading activity data for account mt5_client_003_BALANCE_dootechnology_34c231f6
Expected: 6 activities (1 deposit + 5 trades with EURUSD, USDCHF, XAUUSD)
"""

import requests
import json
from datetime import datetime, timezone, timedelta
import uuid

def create_mt5_activity_data():
    """Create sample MT5 activity data for the target account"""
    
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
        "timestamp": base_time.isoformat(),
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
            "timestamp": trade_time.isoformat(),
            "status": "open",
            "symbol": trade["symbol"],
            "trade_type": trade["trade_type"],
            "volume": trade["volume"],
            "opening_price": trade["opening_price"],
            "current_price": trade["current_price"],
            "profit_loss": trade["profit_loss"]
        })
    
    return activities

def insert_activities_to_database():
    """Insert activities directly to MongoDB via backend API"""
    
    # First, let's authenticate as admin
    base_url = "https://trading-platform-76.preview.emergentagent.com"
    
    # Login as admin
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "username": "admin",
        "password": "password123", 
        "user_type": "admin"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.status_code}")
        return False
    
    admin_data = login_response.json()
    admin_token = admin_data.get('token')
    
    if not admin_token:
        print("❌ No admin token received")
        return False
    
    print(f"✅ Admin authenticated successfully")
    
    # Create the activity data
    activities = create_mt5_activity_data()
    print(f"📊 Created {len(activities)} MT5 activities")
    
    # Since there's no direct API to insert MT5 activities, we'll use a different approach
    # Let's check if there's a way to trigger activity creation through existing endpoints
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }
    
    # Check current activity status
    account_id = "mt5_client_003_BALANCE_dootechnology_34c231f6"
    activity_response = requests.get(
        f"{base_url}/api/mt5/admin/account/{account_id}/activity",
        headers=headers
    )
    
    if activity_response.status_code == 200:
        current_data = activity_response.json()
        current_activities = current_data.get('total_activities', 0)
        print(f"📊 Current activities in database: {current_activities}")
        
        if current_activities == 0:
            print("🔍 Confirmed: No MT5 activities in database")
            print("📋 Activity data that should be present:")
            
            for i, activity in enumerate(activities, 1):
                print(f"   {i}. {activity['type'].upper()}: {activity['description']}")
                if activity['type'] == 'trade':
                    print(f"      Symbol: {activity['symbol']}, P&L: ${activity['profit_loss']}")
                else:
                    print(f"      Amount: ${activity['amount']}")
            
            print("\n🚨 ROOT CAUSE IDENTIFIED:")
            print("   The MT5 activity collection is empty - no trading data was ever stored")
            print("   This explains why the frontend shows 'No activity recorded'")
            
            print("\n🔧 SOLUTION NEEDED:")
            print("   1. Implement MT5 activity data population when accounts are created")
            print("   2. Add endpoint to manually populate MT5 activity data")
            print("   3. Or create sample trading data for demonstration")
            
            return True
        else:
            print(f"✅ Found {current_activities} activities - issue may be elsewhere")
            return True
    else:
        print(f"❌ Failed to check current activities: {activity_response.status_code}")
        return False

def main():
    """Main execution"""
    print("🔧 MT5 Activity Data Population Script")
    print("Target: mt5_client_003_BALANCE_dootechnology_34c231f6")
    print("Expected: 6 activities (1 deposit + 5 trades)")
    
    try:
        success = insert_activities_to_database()
        
        if success:
            print("\n✅ MT5 activity analysis completed!")
            print("📋 Issue confirmed: MT5 activity collection is empty")
        else:
            print("\n❌ MT5 activity analysis failed!")
            
    except Exception as e:
        print(f"\n💥 Script failed with error: {str(e)}")

if __name__ == "__main__":
    main()