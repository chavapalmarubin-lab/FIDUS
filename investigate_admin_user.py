#!/usr/bin/env python3
"""
Script to investigate the admin user in MongoDB
Checking for wrong email association issue
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def investigate_admin_user():
    """Investigate admin user email in MongoDB"""
    
    # Get MongoDB URL from environment
    mongo_url = os.getenv('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
    db_name = os.getenv('DB_NAME', 'fidus_production')
    
    print(f"\n{'='*60}")
    print("FIDUS ADMIN USER INVESTIGATION")
    print(f"{'='*60}\n")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print(f"✅ Connected to MongoDB: {db_name}")
        print(f"\n{'='*60}")
        print("SEARCHING FOR ADMIN USER...")
        print(f"{'='*60}\n")
        
        # Try different queries to find admin user
        queries = [
            {"username": "admin"},
            {"role": "admin"},
            {"user_type": "admin"},
            {"email": "chavapalmarubin@gmail.com"}
        ]
        
        found_users = []
        
        for query in queries:
            print(f"🔍 Query: {query}")
            users = await db.users.find(query).to_list(length=10)
            if users:
                print(f"   ✅ Found {len(users)} user(s)")
                for user in users:
                    if user not in found_users:
                        found_users.append(user)
            else:
                print(f"   ❌ No users found")
            print()
        
        if not found_users:
            print("\n⚠️  NO ADMIN USERS FOUND IN DATABASE!")
            print("\nLet's check all users in the database:")
            all_users = await db.users.find({}).to_list(length=20)
            print(f"\n📊 Total users in database: {len(all_users)}")
            for idx, user in enumerate(all_users, 1):
                print(f"\n--- User {idx} ---")
                print(f"ID: {user.get('_id')}")
                print(f"Username: {user.get('username', 'N/A')}")
                print(f"Email: {user.get('email', 'N/A')}")
                print(f"Role: {user.get('role', 'N/A')}")
                print(f"User Type: {user.get('user_type', 'N/A')}")
        else:
            print(f"\n{'='*60}")
            print(f"ADMIN USER DETAILS ({len(found_users)} user(s) found)")
            print(f"{'='*60}\n")
            
            for idx, user in enumerate(found_users, 1):
                print(f"\n--- Admin User {idx} ---")
                print(f"ID: {user.get('_id')}")
                print(f"User ID: {user.get('user_id', 'N/A')}")
                print(f"Username: {user.get('username', 'N/A')}")
                print(f"Email: {user.get('email', 'N/A')}")
                print(f"Google Email: {user.get('googleEmail', 'N/A')}")
                print(f"Google Connected: {user.get('googleConnected', 'N/A')}")
                print(f"Role: {user.get('role', 'N/A')}")
                print(f"User Type: {user.get('user_type', 'N/A')}")
                print(f"Created At: {user.get('created_at', 'N/A')}")
                
                # Check for placeholder or wrong email
                email = user.get('email', '').lower()
                google_email = user.get('googleEmail', '').lower()
                target_email = 'chavapalmarubin@gmail.com'
                
                print(f"\n🔍 EMAIL ANALYSIS:")
                print(f"   Current Email: {email}")
                print(f"   Target Email: {target_email}")
                if email != target_email:
                    print(f"   ⚠️  MISMATCH DETECTED!")
                    print(f"   ❌ Email should be: {target_email}")
                else:
                    print(f"   ✅ Email is correct!")
                
                if google_email:
                    print(f"\n   Current Google Email: {google_email}")
                    if google_email != target_email:
                        print(f"   ⚠️  GOOGLE EMAIL MISMATCH!")
                        print(f"   ❌ Google Email should be: {target_email}")
                    else:
                        print(f"   ✅ Google Email is correct!")
        
        # Check Google OAuth sessions
        print(f"\n{'='*60}")
        print("CHECKING GOOGLE OAUTH SESSIONS...")
        print(f"{'='*60}\n")
        
        oauth_sessions = await db.admin_google_sessions.find({}).to_list(length=10)
        print(f"📊 Found {len(oauth_sessions)} OAuth session(s)")
        
        for idx, session in enumerate(oauth_sessions, 1):
            print(f"\n--- OAuth Session {idx} ---")
            print(f"Admin User ID: {session.get('admin_user_id', 'N/A')}")
            print(f"Google Email: {session.get('google_email', 'N/A')}")
            print(f"Created At: {session.get('created_at', 'N/A')}")
            print(f"Expires At: {session.get('expires_at', 'N/A')}")
            print(f"Has Access Token: {'Yes' if session.get('access_token') else 'No'}")
            print(f"Has Refresh Token: {'Yes' if session.get('refresh_token') else 'No'}")
        
        print(f"\n{'='*60}")
        print("INVESTIGATION COMPLETE")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(investigate_admin_user())
