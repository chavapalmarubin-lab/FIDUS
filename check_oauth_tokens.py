#!/usr/bin/env python3
"""
Script to check OAuth tokens in MongoDB
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_oauth_tokens():
    """Check OAuth tokens in MongoDB"""
    
    # Get MongoDB URL from environment
    mongo_url = os.getenv('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
    db_name = os.getenv('DB_NAME', 'fidus_production')
    
    print(f"\n{'='*60}")
    print("CHECKING OAUTH TOKENS IN MONGODB")
    print(f"{'='*60}\n")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print(f"✅ Connected to MongoDB: {db_name}\n")
        
        # Check google_tokens collection
        print("Checking 'google_tokens' collection...")
        tokens = await db.google_tokens.find({}).to_list(length=10)
        print(f"📊 Found {len(tokens)} OAuth token(s) in google_tokens collection\n")
        
        for idx, token in enumerate(tokens, 1):
            print(f"--- OAuth Token {idx} ---")
            print(f"Admin User ID: {token.get('admin_user_id', 'N/A')}")
            print(f"Has Access Token: {'Yes' if token.get('access_token') else 'No'}")
            print(f"Has Refresh Token: {'Yes' if token.get('refresh_token') else 'No'}")
            print(f"Scopes: {len(token.get('scopes', []))} scopes")
            print(f"Created At: {token.get('created_at', 'N/A')}")
            print(f"Updated At: {token.get('updated_at', 'N/A')}")
            print(f"Expiry: {token.get('expiry', 'N/A')}")
            print()
        
        # Check admin_google_sessions collection (legacy)
        print("Checking 'admin_google_sessions' collection (legacy)...")
        sessions = await db.admin_google_sessions.find({}).to_list(length=10)
        print(f"📊 Found {len(sessions)} OAuth session(s) in admin_google_sessions collection\n")
        
        for idx, session in enumerate(sessions, 1):
            print(f"--- OAuth Session {idx} ---")
            print(f"Admin User ID: {session.get('admin_user_id', 'N/A')}")
            print(f"Google Email: {session.get('google_email', 'N/A')}")
            print(f"Has Access Token: {'Yes' if session.get('access_token') else 'No'}")
            print(f"Has Refresh Token: {'Yes' if session.get('refresh_token') else 'No'}")
            print(f"Created At: {session.get('created_at', 'N/A')}")
            print(f"Expires At: {session.get('expires_at', 'N/A')}")
            print()
        
        if len(tokens) == 0 and len(sessions) == 0:
            print("⚠️  NO OAUTH TOKENS FOUND!")
            print("   This means Google OAuth has never been completed successfully.")
            print("   User needs to complete OAuth flow to connect Google account.")
        
        print(f"{'='*60}")
        print("CHECK COMPLETE")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_oauth_tokens())
