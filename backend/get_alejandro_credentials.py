"""
Get Alejandro's login credentials
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def get_credentials():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("ALEJANDRO'S LOGIN CREDENTIALS")
    print("="*80)
    print()
    
    # Find Alejandro's user
    user = await db.users.find_one({"username": "alejandro_mariscal"})
    
    if user:
        print("✅ User found:")
        print()
        print(f"Username: {user.get('username')}")
        print(f"User ID: {user.get('id')}")
        print(f"Name: {user.get('name')}")
        print(f"Email: {user.get('email')}")
        print(f"Type: {user.get('type')}")
        print()
        
        # Check if password is hashed or plain
        password = user.get('password')
        if password:
            if password.startswith('$2b$') or password.startswith('$2a$'):
                print("Password: [HASHED - cannot retrieve]")
                print()
                print("⚠️  Password is hashed for security.")
                print("   To reset password, we need to update it in the database.")
            else:
                print(f"Password: {password}")
        else:
            print("Password: [NOT SET]")
    else:
        print("❌ User not found")
        print()
        print("Checking all client users...")
        
        all_clients = await db.users.find({"type": "client"}).to_list(None)
        print(f"\nFound {len(all_clients)} client users:")
        for u in all_clients:
            print(f"  - {u.get('username')} (ID: {u.get('id')}, Name: {u.get('name')})")
    
    client.close()

asyncio.run(get_credentials())
