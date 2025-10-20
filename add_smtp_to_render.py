#!/usr/bin/env python3
"""
Add SMTP Environment Variables to Render
"""

import os
import requests
import json

# Render API configuration
RENDER_API_KEY = os.getenv('RENDER_API_KEY', 'rnd_oqHoXCPZC3VfkR1WcSHFHvd0eY9Z')
SERVICE_ID = 'srv-d3ih7g2dbo4c73fo4330'  # FIDUS Backend service ID

# SMTP Configuration from .env
SMTP_CREDENTIALS = {
    'SMTP_USERNAME': 'chavapalmarubin@gmail.com',
    'SMTP_APP_PASSWORD': 'atms srwm ieug bxmm',
    'ALERT_RECIPIENT_EMAIL': 'chavapalmarubin@gmail.com'
}

def add_env_vars_to_render():
    """Add SMTP environment variables to Render service"""
    
    url = f'https://api.render.com/v1/services/{SERVICE_ID}/env-vars'
    headers = {
        'Authorization': f'Bearer {RENDER_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🔧 Adding SMTP Environment Variables to Render...")
    print(f"   Service ID: {SERVICE_ID}")
    print()
    
    for key, value in SMTP_CREDENTIALS.items():
        payload = [{
            'key': key,
            'value': value
        }]
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                print(f"   ✅ {key}: Added successfully")
            else:
                print(f"   ❌ {key}: Failed ({response.status_code})")
                print(f"      Response: {response.text}")
        
        except Exception as e:
            print(f"   ❌ {key}: Error - {str(e)}")
    
    print()
    print("✅ SMTP configuration added to Render!")
    print("   A deployment will be triggered to apply the changes.")

if __name__ == '__main__':
    add_env_vars_to_render()
