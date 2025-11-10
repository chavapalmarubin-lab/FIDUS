"""
Set a simple password for Alejandro for testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

async def set_password():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    # Set simple password: Alejandro123
    password = "Alejandro123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    result = await db.users.update_one(
        {"username": "alejandro_mariscal"},
        {"$set": {"password": hashed.decode('utf-8')}}
    )
    
    print("="*80)
    print("ALEJANDRO'S LOGIN CREDENTIALS SET")
    print("="*80)
    print()
    print("✅ Password updated successfully")
    print()
    print("LOGIN CREDENTIALS:")
    print("-"*80)
    print(f"Username: alejandro_mariscal")
    print(f"Password: Alejandro123")
    print()
    print("Login URL: https://financial-api-fix.preview.emergentagent.com")
    print()
    
    client.close()

asyncio.run(set_password())
