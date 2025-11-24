#!/usr/bin/env python3
"""
Check which Google account is associated with OAuth tokens
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_google_account():
    """Check Google account associated with OAuth"""
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
    db_name = os.getenv('DB_NAME', 'fidus_production')
    
    print(f"\n{'='*60}")
    print("CHECKING GOOGLE ACCOUNT ASSOCIATION")
    print(f"{'='*60}\n")
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Check all possible token collections
        print("Checking google_tokens collection...")
        google_tokens = await db.google_tokens.find({}).to_list(length=10)
        
        if google_tokens:
            for idx, token in enumerate(google_tokens, 1):
                print(f"\n--- Token {idx} ---")
                print(f"Admin User ID: {token.get('admin_user_id')}")
                print(f"Client ID: {token.get('client_id', 'N/A')[:50]}...")
                print(f"Has Access Token: {'Yes' if token.get('access_token') else 'No'}")
                print(f"Scopes: {token.get('scopes', [])[:3]}")  # First 3 scopes
                print(f"Created: {token.get('created_at', 'N/A')}")
                
                # Try to decode the token to see which account it's for
                access_token = token.get('access_token', '')
                if access_token:
                    print(f"Access Token (first 30 chars): {access_token[:30]}...")
        else:
            print("❌ No tokens in google_tokens collection")
        
        print("\n" + "="*60)
        print("Checking admin_google_sessions collection...")
        sessions = await db.admin_google_sessions.find({}).to_list(length=10)
        
        if sessions:
            for idx, session in enumerate(sessions, 1):
                print(f"\n--- Session {idx} ---")
                print(f"Admin User ID: {session.get('admin_user_id')}")
                print(f"Google Email: {session.get('google_email', 'N/A')}")
                print(f"Google Info: {session.get('google_info', {})}")
                print(f"Has Tokens: {'Yes' if session.get('google_tokens') else 'No'}")
                print(f"Created: {session.get('created_at', 'N/A')}")
        else:
            print("❌ No sessions in admin_google_sessions collection")
        
        print("\n" + "="*60)
        print("Checking admin user record...")
        admin = await db.users.find_one({"username": "admin"})
        
        if admin:
            print(f"\nAdmin User:")
            print(f"  Username: {admin.get('username')}")
            print(f"  Email: {admin.get('email')}")
            print(f"  Google Email: {admin.get('googleEmail', 'Not set')}")
            print(f"  Google Connected: {admin.get('googleConnected', False)}")
        
        print("\n" + "="*60)
        print("\nDIAGNOSIS:")
        
        if google_tokens or sessions:
            print("✅ OAuth tokens found in database")
            print("⚠️  Check if the Google Email matches: chavapalmarubin@gmail.com")
            print("⚠️  If NOT, you need to DISCONNECT and RECONNECT with correct account")
        else:
            print("❌ NO OAuth tokens found")
            print("💡 Need to complete OAuth flow with chavapalmarubin@gmail.com")
        
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_google_account())
