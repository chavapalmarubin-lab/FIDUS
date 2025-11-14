"""
Migration: Add CRM fields to leads collection
Adds fields needed for agent lead management
"""

import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def migrate_leads():
    """Add CRM fields to all existing leads"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
    client = AsyncIOMotorClient(mongo_url)
    db = client.fidus_production
    
    print("\n" + "="*80)
    print("Starting leads CRM fields migration...")
    print("="*80 + "\n")
    
    # Default CRM fields for existing leads
    default_crm_fields = {
        "crm_status": "Nuevo Lead",  # Default status
        "crm_status_history": [
            {
                "status": "Nuevo Lead",
                "changed_at": datetime.now(timezone.utc),
                "changed_by": "system",
                "changed_by_name": "System Migration"
            }
        ],
        "agent_notes": [],
        "last_contacted": None,
        "next_follow_up": None,
        "priority": "medium",
        "utm_source": None,
        "utm_medium": None,
        "utm_campaign": None,
        "ip_address": None,
        "user_agent": None
    }
    
    # Get all leads
    leads = await db.leads.find({}).to_list(length=None)
    print(f"Found {len(leads)} leads to migrate\n")
    
    updated_count = 0
    skipped_count = 0
    
    for lead in leads:
        # Check if already migrated
        if "crm_status" in lead:
            skipped_count += 1
            continue
        
        # Add CRM fields
        await db.leads.update_one(
            {"_id": lead["_id"]},
            {"$set": default_crm_fields}
        )
        updated_count += 1
        
        if updated_count % 10 == 0:
            print(f"  Migrated {updated_count} leads...")
    
    print(f"\n✅ Migration complete!")
    print(f"   - Updated: {updated_count} leads")
    print(f"   - Skipped (already migrated): {skipped_count} leads\n")
    
    # Create indexes for performance
    print("Creating indexes...")
    
    await db.leads.create_index("referred_by")
    await db.leads.create_index("crm_status")
    await db.leads.create_index("next_follow_up")
    await db.leads.create_index([("referred_by", 1), ("crm_status", 1)])
    
    print("✅ Indexes created\n")
    print("="*80)
    print("Migration completed successfully!")
    print("="*80 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_leads())
