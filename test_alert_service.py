"""
Test script for the alert service
Run this to verify email alerts are working
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, '/app/backend')

async def test_alert_service():
    """Test the alert service email functionality"""
    
    print("=" * 60)
    print("TESTING FIDUS ALERT SERVICE")
    print("=" * 60)
    print()
    
    # Check environment variables
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_APP_PASSWORD')
    alert_recipient = os.getenv('ALERT_RECIPIENT_EMAIL', 'chavapalmarubin@gmail.com')
    
    print(f"SMTP Username: {smtp_username or 'NOT SET'}")
    print(f"SMTP Password: {'***' + smtp_password[-4:] if smtp_password else 'NOT SET'}")
    print(f"Alert Recipient: {alert_recipient}")
    print()
    
    if not smtp_username or not smtp_password:
        print("❌ ERROR: SMTP credentials not configured!")
        print("Please set SMTP_USERNAME and SMTP_APP_PASSWORD in backend/.env")
        return False
    
    # Import MongoDB connection
    from config.database import get_database
    db = await get_database()
    
    print("✅ Connected to MongoDB")
    print()
    
    # Import AlertService
    from alert_service import AlertService
    alert_service = AlertService(db)
    
    print("📧 Sending test alert email...")
    print()
    
    try:
        # Send test alert
        alert_id = await alert_service.trigger_alert(
            component="test_system",
            component_name="Alert System Test",
            severity="warning",
            status="TESTING",
            message="This is a test alert to verify email delivery is working correctly",
            details={
                "test_time": datetime.now(timezone.utc).isoformat(),
                "reason": "Manual test via test script",
                "smtp_host": alert_service.smtp_host,
                "smtp_port": alert_service.smtp_port,
                "recipient": alert_recipient
            }
        )
        
        print(f"✅ SUCCESS! Test alert sent successfully")
        print(f"   Alert ID: {alert_id}")
        print(f"   Recipient: {alert_recipient}")
        print()
        print("📬 Check your email inbox for the test alert!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to send alert")
        print(f"   Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    
    # Run test
    success = asyncio.run(test_alert_service())
    
    sys.exit(0 if success else 1)
