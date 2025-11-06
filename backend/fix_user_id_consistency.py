"""
Fix user_id consistency - there should be ONE Alejandro with correct ID
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("FIXING USER ID CONSISTENCY")
    print("="*80)
    print()
    
    # Find all Alejandro users
    all_users = await db.users.find({
        "$or": [
            {"username": {"$regex": "alejandro", "$options": "i"}},
            {"name": {"$regex": "alejandro", "$options": "i"}},
            {"id": {"$regex": "alejandro", "$options": "i"}}
        ]
    }).to_list(None)
    
    print(f"Found {len(all_users)} users matching 'alejandro':")
    for u in all_users:
        print(f"\n  User:")
        print(f"    _id: {u.get('_id')}")
        print(f"    id: {u.get('id')}")
        print(f"    username: {u.get('username')}")
        print(f"    name: {u.get('name')}")
        print(f"    type: {u.get('type')}")
    
    print("\n" + "="*80)
    print("FIXING: Setting correct user to use 'client_alejandro' everywhere")
    print("="*80)
    print()
    
    # Update the correct user
    result = await db.users.update_one(
        {"username": "alejandro_mariscal"},
        {"$set": {
            "id": "client_alejandro",  # FIXED: Use consistent ID
            "name": "Alejandro Mariscal Romero",
            "email": "alejandro.mariscal@email.com",
            "type": "client",
            "status": "active"
        }}
    )
    
    print(f"✅ Updated user: {result.modified_count} document(s)")
    
    # Delete any duplicate Alejandro users
    delete_result = await db.users.delete_many({
        "username": {"$ne": "alejandro_mariscal"},
        "$or": [
            {"id": {"$regex": "alejandro", "$options": "i"}},
            {"name": {"$regex": "alejandro", "$options": "i"}}
        ]
    })
    
    print(f"✅ Deleted {delete_result.deleted_count} duplicate user(s)")
    
    print()
    print("VERIFICATION:")
    print("-"*80)
    
    correct_user = await db.users.find_one({"username": "alejandro_mariscal"})
    if correct_user:
        print(f"✅ Correct user found:")
        print(f"   id: {correct_user.get('id')}")
        print(f"   username: {correct_user.get('username')}")
        print(f"   name: {correct_user.get('name')}")
        print(f"   email: {correct_user.get('email')}")
    
    print()
    print("✅ FIXED! User will now login with user_id: 'client_alejandro'")
    
    client.close()

asyncio.run(fix())
