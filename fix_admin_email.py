#!/usr/bin/env python3
"""
Script to fix admin user email in MongoDB
Update from hq@getfidus.com to chavapalmarubin@gmail.com
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def fix_admin_email():
    """Fix admin user email in MongoDB"""
    
    # Get MongoDB URL from environment
    mongo_url = os.getenv('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
    db_name = os.getenv('DB_NAME', 'fidus_production')
    
    target_email = 'chavapalmarubin@gmail.com'
    
    print(f"\n{'='*60}")
    print("FIDUS ADMIN EMAIL FIX")
    print(f"{'='*60}\n")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print(f"✅ Connected to MongoDB: {db_name}\n")
        
        # Find admin user
        admin_user = await db.users.find_one({"username": "admin"})
        
        if not admin_user:
            print("❌ Admin user not found!")
            return
        
        print(f"📊 CURRENT ADMIN USER DATA:")
        print(f"   Username: {admin_user.get('username')}")
        print(f"   Email: {admin_user.get('email')}")
        print(f"   Google Email: {admin_user.get('googleEmail', 'Not Set')}")
        print(f"   Google Connected: {admin_user.get('googleConnected', 'Not Set')}")
        print(f"\n{'='*60}")
        print(f"APPLYING FIX...")
        print(f"{'='*60}\n")
        
        # Update admin user with correct email
        update_result = await db.users.update_one(
            {"username": "admin"},
            {
                "$set": {
                    "email": target_email,
                    "googleEmail": target_email,
                    "googleConnected": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if update_result.modified_count > 0:
            print(f"✅ Successfully updated admin user!")
            print(f"   ✓ Email: {target_email}")
            print(f"   ✓ Google Email: {target_email}")
            print(f"   ✓ Google Connected: True")
        else:
            print(f"⚠️  No changes made (already correct?)")
        
        # Verify the update
        print(f"\n{'='*60}")
        print(f"VERIFYING UPDATE...")
        print(f"{'='*60}\n")
        
        updated_user = await db.users.find_one({"username": "admin"})
        
        print(f"📊 UPDATED ADMIN USER DATA:")
        print(f"   Username: {updated_user.get('username')}")
        print(f"   Email: {updated_user.get('email')}")
        print(f"   Google Email: {updated_user.get('googleEmail')}")
        print(f"   Google Connected: {updated_user.get('googleConnected')}")
        
        # Verify correctness
        print(f"\n🔍 VERIFICATION:")
        if updated_user.get('email') == target_email:
            print(f"   ✅ Email correct: {target_email}")
        else:
            print(f"   ❌ Email incorrect: {updated_user.get('email')}")
        
        if updated_user.get('googleEmail') == target_email:
            print(f"   ✅ Google Email correct: {target_email}")
        else:
            print(f"   ❌ Google Email incorrect: {updated_user.get('googleEmail')}")
        
        if updated_user.get('googleConnected') == True:
            print(f"   ✅ Google Connected: True")
        else:
            print(f"   ❌ Google Connected: {updated_user.get('googleConnected')}")
        
        print(f"\n{'='*60}")
        print("FIX COMPLETE!")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_admin_email())
