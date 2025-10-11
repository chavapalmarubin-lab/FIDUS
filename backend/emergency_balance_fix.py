"""
EMERGENCY BALANCE FIX - AUTONOMOUS RECOVERY SYSTEM
Critical fix for account 886528 $521.88 discrepancy while MT5 bridge is offline
"""

import asyncio
from datetime import datetime, timezone
from config.database import get_database

async def emergency_update_account_886528():
    """
    EMERGENCY: Update account 886528 balance from $3,405.53 to $3,927.41
    This resolves the critical $521.88 discrepancy while MT5 bridge is restored
    """
    try:
        # Get database connection
        db = await get_database()
        
        # Find account 886528
        account = await db.mt5_accounts.find_one({"account": 886528})
        
        if not account:
            print("❌ Account 886528 not found")
            return False
            
        print(f"📊 Current balance: ${account.get('balance', 0):.2f}")
        
        # Update with live MEX Atlantic balance
        update_data = {
            'balance': 3927.41,
            'current_equity': 3927.41,
            'profit_loss': 3927.41,  # Since it's an Interest Separation account
            'updated_at': datetime.now(timezone.utc),
            'sync_status': 'emergency_manual_update',
            'sync_source': 'MEX_Atlantic_Live_Data_2025-10-11',
            'emergency_fix_applied': True,
            'emergency_fix_timestamp': datetime.now(timezone.utc).isoformat(),
            'emergency_fix_reason': 'Resolved $521.88 discrepancy while MT5 bridge offline',
            'previous_balance': account.get('balance', 0),
            'balance_change': 3927.41 - account.get('balance', 0)
        }
        
        result = await db.mt5_accounts.update_one(
            {"account": 886528},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            print(f"✅ Emergency fix applied!")
            print(f"   Old Balance: ${account.get('balance', 0):.2f}")
            print(f"   New Balance: $3,927.41") 
            print(f"   Change: ${3927.41 - account.get('balance', 0):+.2f}")
            print(f"   Timestamp: {datetime.now(timezone.utc).isoformat()}")
            return True
        else:
            print("❌ Update failed - no documents modified")
            return False
            
    except Exception as e:
        print(f"❌ Emergency fix failed: {str(e)}")
        return False

# Run the emergency fix
if __name__ == "__main__":
    print("🚨 EXECUTING EMERGENCY BALANCE FIX FOR ACCOUNT 886528")
    result = asyncio.run(emergency_update_account_886528())
    if result:
        print("✅ EMERGENCY FIX SUCCESSFUL - $521.88 DISCREPANCY RESOLVED")
    else:
        print("❌ EMERGENCY FIX FAILED")