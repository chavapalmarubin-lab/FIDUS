"""
Migration Script: Add Referral Agent Portal Fields
Date: November 14, 2025
Purpose: Add authentication and portal fields to existing salespeople

BEFORE RUNNING: Backup salespeople collection!
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timezone
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initial password for both agents (send via secure channel)
INITIAL_PASSWORD = "FidusAgent2025!"

async def migrate_add_portal_fields():
    """Add portal fields to existing salespeople"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("\n" + "="*80)
    print("MIGRATION: Add Referral Agent Portal Fields")
    print("="*80 + "\n")
    
    # Get existing salespeople
    salespeople = await db.salespeople.find({
        "email": {"$in": ["chava@alyarglobal.com", "Jazioni@yahoo.com.mx"]}
    }).to_list(length=None)
    
    if len(salespeople) != 2:
        print(f"❌ Expected 2 salespeople, found {len(salespeople)}")
        print("   Aborting migration!")
        return
    
    print(f"✓ Found {len(salespeople)} salespeople to migrate:\n")
    for sp in salespeople:
        print(f"  - {sp.get('name')} ({sp.get('email')})")
    
    print("\n" + "-"*80)
    print("Adding portal fields...\n")
    
    # Hash the initial password
    password_hash = pwd_context.hash(INITIAL_PASSWORD)
    
    # Fields to add
    portal_fields = {
        # Authentication fields
        "password_hash": password_hash,
        "password_reset_token": None,
        "password_reset_expires": None,
        "last_login": None,
        "login_count": 0,
        
        # Portal preferences
        "portal_settings": {
            "email_notifications": True,
            "sms_notifications": False,
            "language": "es",
            "timezone": "America/Mexico_City"
        },
        
        # CRM configuration
        "lead_pipeline_stages": [
            "Nuevo Lead",
            "Contactado",
            "Interesado",
            "Simulación Enviada",
            "Negociando",
            "Invertido"
        ],
        
        # Performance tracking (initialize to zeros)
        "stats": {
            "total_leads": 0,
            "leads_this_month": 0,
            "total_clients": 0,
            "clients_this_month": 0,
            "total_volume": 0,
            "total_commissions_earned": 0,
            "total_commissions_paid": 0,
            "total_commissions_pending": 0,
            "average_conversion_rate": 0,
            "link_clicks": 0,
            "last_stats_update": datetime.now(timezone.utc)
        }
    }
    
    # Update each salesperson
    for sp in salespeople:
        sp_name = sp.get('name')
        sp_email = sp.get('email')
        
        # Check if fields already exist
        if sp.get('password_hash'):
            print(f"⚠️  {sp_name} already has portal fields - skipping")
            continue
        
        # Update with portal fields
        result = await db.salespeople.update_one(
            {"_id": sp["_id"]},
            {"$set": portal_fields}
        )
        
        if result.modified_count == 1:
            print(f"✓ {sp_name} ({sp_email})")
            print(f"  - Added password_hash")
            print(f"  - Added portal_settings")
            print(f"  - Added lead_pipeline_stages")
            print(f"  - Added stats tracking")
        else:
            print(f"❌ Failed to update {sp_name}")
    
    print("\n" + "="*80)
    print("MIGRATION COMPLETE")
    print("="*80 + "\n")
    
    # Verify migration
    print("Verification:\n")
    updated_salespeople = await db.salespeople.find({
        "email": {"$in": ["chava@alyarglobal.com", "Jazioni@yahoo.com.mx"]}
    }).to_list(length=None)
    
    for sp in updated_salespeople:
        has_password = "password_hash" in sp
        has_settings = "portal_settings" in sp
        has_stages = "lead_pipeline_stages" in sp
        has_stats = "stats" in sp
        
        print(f"{sp.get('name')}:")
        print(f"  password_hash: {'✓' if has_password else '✗'}")
        print(f"  portal_settings: {'✓' if has_settings else '✗'}")
        print(f"  lead_pipeline_stages: {'✓' if has_stages else '✗'}")
        print(f"  stats: {'✓' if has_stats else '✗'}")
        print()
    
    print("="*80)
    print("Initial Password (send to agents via secure channel):")
    print(f"  {INITIAL_PASSWORD}")
    print("="*80 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_add_portal_fields())
