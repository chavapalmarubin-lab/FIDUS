#!/usr/bin/env python3
"""
Test Email Alert Script
Verifies that SMTP configuration is working correctly
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from alert_service import AlertService

async def test_email_alert():
    print("\n" + "="*60)
    print("🧪 TESTING FIDUS ALERT SYSTEM")
    print("="*60 + "\n")
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb+srv://chavapalmarubin_db_user:2170Tenoch!@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority')
    db_name = os.getenv('DB_NAME', 'fidus_production')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Create AlertService instance
    alert_service = AlertService(db)
    
    try:
        print("📧 Triggering test email alert...")
        print(f"   To: {alert_service.admin_email}")
        print(f"   SMTP: {alert_service.smtp_host}:{alert_service.smtp_port}")
        print(f"   Username: {alert_service.smtp_username}")
        print(f"   Password configured: {'Yes' if alert_service.smtp_password else 'No'}")
        print()
        
        # Trigger test alert
        alert_id = await alert_service.trigger_alert(
            component="test_system",
            component_name="TEST SYSTEM",
            severity="info",
            status="TESTING",
            message="FIDUS Alert System is now active! Email alerts are working correctly.",
            details={
                "test": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "recipient": alert_service.admin_email,
                "smtp_configured": True,
                "test_type": "Initial SMTP Configuration Test"
            }
        )
        
        print("✅ Test alert triggered successfully!")
        print(f"   Alert ID: {alert_id}")
        print(f"\n📬 Check email at: {alert_service.admin_email}")
        print(f"   Subject: ℹ️ INFO: TEST SYSTEM - FIDUS Platform")
        print(f"   Expected arrival: Within 1-2 minutes")
        print()
        print("="*60)
        print("✅ SMTP CONFIGURATION TEST COMPLETE")
        print("="*60 + "\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST ALERT FAILED")
        print("="*60)
        print(f"\nError: {str(e)}\n")
        
        import traceback
        print("Full traceback:")
        print("-"*60)
        traceback.print_exc()
        print("-"*60 + "\n")
        
        print("Troubleshooting:")
        print("  1. Verify SMTP credentials in .env file")
        print("  2. Ensure Gmail App Password is correct")
        print("  3. Check that 2-Step Verification is enabled on Gmail")
        print("  4. Verify backend has internet access")
        print()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_email_alert())
