#!/usr/bin/env python3
"""
API Key Generator for MT5 Bridge Service
Generates secure API keys for production use
"""

import secrets
import string
from cryptography.fernet import Fernet

def generate_api_key(length=32):
    """Generate secure API key"""
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_encryption_key():
    """Generate encryption key for MT5 passwords"""
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    print("🔐 FIDUS MT5 Bridge - Security Key Generator")
    print("=" * 50)
    
    # Generate API key
    api_key = generate_api_key()
    print(f"API Key: {api_key}")
    
    # Generate encryption key
    encryption_key = generate_encryption_key()
    print(f"Encryption Key: {encryption_key}")
    
    print("\n📝 Add these to your .env file:")
    print(f"MT5_BRIDGE_API_KEY={api_key}")
    print(f"MT5_ENCRYPTION_KEY={encryption_key}")
    
    print("\n⚠️  Keep these keys secure and never share them!")
