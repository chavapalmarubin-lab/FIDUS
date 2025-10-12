#!/usr/bin/env python3
"""
Debug SMTP Connection Test
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
load_dotenv(Path('.env'))

async def test_smtp_directly():
    """Test SMTP connection and send email directly"""
    
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_APP_PASSWORD')
    recipient = os.getenv('ALERT_RECIPIENT_EMAIL')
    
    print("\n" + "="*60)
    print("📧 DIRECT SMTP CONNECTION TEST")
    print("="*60 + "\n")
    
    print(f"Configuration:")
    print(f"   SMTP Server: smtp.gmail.com:587")
    print(f"   Username: {smtp_username}")
    print(f"   Password Length: {len(smtp_password) if smtp_password else 0}")
    print(f"   Password (first 8 chars): {smtp_password[:8] if smtp_password else 'NOT SET'}...")
    print(f"   Recipient: {recipient}")
    print()
    
    if not smtp_username or not smtp_password or not recipient:
        print("❌ Missing SMTP configuration!")
        print("   Check .env file for SMTP_USERNAME, SMTP_APP_PASSWORD, ALERT_RECIPIENT_EMAIL")
        return
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_username
        msg['To'] = recipient
        msg['Subject'] = '🧪 FIDUS Direct SMTP Test - Troubleshooting'
        
        text_body = """
FIDUS Alert System - Direct SMTP Test

This is a direct SMTP connection test from the FIDUS Health Monitoring System.

If you receive this email, SMTP is configured correctly!

Test Details:
- SMTP Server: smtp.gmail.com:587
- TLS: Enabled
- Authentication: Gmail App Password
- Test Type: Direct troubleshooting test

Next Steps:
If you receive this, the alert system is fully operational!

FIDUS Health Monitoring System
Automated Alert Service
        """
        
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🧪 FIDUS Alert System - Direct SMTP Test</h2>
            <p>This is a direct SMTP connection test from the FIDUS Health Monitoring System.</p>
            <p><strong>If you receive this email, SMTP is configured correctly!</strong></p>
            
            <h3>Test Details:</h3>
            <ul>
                <li>SMTP Server: smtp.gmail.com:587</li>
                <li>TLS: Enabled</li>
                <li>Authentication: Gmail App Password</li>
                <li>Test Type: Direct troubleshooting test</li>
            </ul>
            
            <h3>Next Steps:</h3>
            <p>If you receive this, the alert system is fully operational!</p>
            
            <hr>
            <p style="font-size: 12px; color: #666;">
                FIDUS Health Monitoring System<br>
                Automated Alert Service
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        print("📤 Step 1: Connecting to SMTP server...")
        
        # Connect and send
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
            print("   ✅ Connected to smtp.gmail.com:587")
            
            print("📤 Step 2: Enabling TLS...")
            server.starttls()
            print("   ✅ TLS enabled")
            
            print("📤 Step 3: Authenticating...")
            server.login(smtp_username, smtp_password)
            print("   ✅ Authentication successful")
            
            print("📤 Step 4: Sending email...")
            server.send_message(msg)
            print("   ✅ Email sent successfully!")
            
            print()
            print("="*60)
            print("✅ SMTP TEST SUCCESSFUL!")
            print("="*60)
            print()
            print(f"📬 Check email at: {recipient}")
            print("   Expected arrival: Within 1-2 minutes")
            print()
            
    except smtplib.SMTPAuthenticationError as e:
        print()
        print("="*60)
        print("❌ SMTP AUTHENTICATION FAILED!")
        print("="*60)
        print(f"\nError Code: {e.smtp_code}")
        print(f"Error Message: {e.smtp_error.decode() if hasattr(e, 'smtp_error') else str(e)}")
        print()
        print("Possible issues:")
        print("  1. App password incorrect")
        print("  2. App password has extra spaces or quotes")
        print("  3. 2-Step Verification not enabled on Gmail")
        print("  4. App password was revoked")
        print()
        print("Verify .env file:")
        print("  SMTP_APP_PASSWORD=atms srwm ieug bxmm")
        print("  (no quotes, can have spaces)")
        print()
        
    except smtplib.SMTPException as e:
        print()
        print("="*60)
        print("❌ SMTP ERROR!")
        print("="*60)
        print(f"\nError: {e}")
        print()
        
    except Exception as e:
        print()
        print("="*60)
        print("❌ UNEXPECTED ERROR!")
        print("="*60)
        print(f"\nError: {e}")
        print()
        import traceback
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_smtp_directly())
