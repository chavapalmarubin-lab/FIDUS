"""
Multi-Factor Authentication Service for FIDUS Investment Platform
Implements TOTP, SMS, and email-based MFA with backup codes
"""

import pyotp
import qrcode
import io
import base64
import secrets
import string
import hashlib
import hmac
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

# Import for SMS (would need Twilio or similar in production)
# from twilio.rest import Client

@dataclass
class MFASetup:
    user_id: str
    secret: str
    qr_code: str
    backup_codes: List[str]
    setup_token: str

@dataclass
class MFAValidation:
    is_valid: bool
    method: str
    remaining_attempts: int
    locked_until: Optional[datetime] = None

class MFAService:
    """Multi-Factor Authentication Service"""
    
    def __init__(self):
        self.app_name = "FIDUS Investment Management"
        self.max_attempts = 3
        self.lockout_duration = 300  # 5 minutes in seconds
        
        # In production, store these in secure database
        self.user_secrets = {}  # user_id -> secret
        self.backup_codes = {}  # user_id -> [hashed_codes]
        self.failed_attempts = {}  # user_id -> {count, locked_until}
        
        logging.info("MFA Service initialized")
    
    def generate_secret(self, user_id: str) -> str:
        """Generate a new TOTP secret for user"""
        secret = pyotp.random_base32()
        self.user_secrets[user_id] = secret
        return secret
    
    def generate_qr_code(self, user_id: str, user_email: str) -> str:
        """Generate QR code for TOTP setup"""
        secret = self.user_secrets.get(user_id)
        if not secret:
            secret = self.generate_secret(user_id)
        
        # Create TOTP provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=self.app_name
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Convert to base64 image
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{qr_code_data}"
    
    def generate_backup_codes(self, user_id: str, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery"""
        codes = []
        hashed_codes = []
        
        for _ in range(count):
            # Generate 8-character backup code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(8))
            
            # Insert hyphen for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
            
            # Store hashed version
            hashed_code = hashlib.sha256(code.encode()).hexdigest()
            hashed_codes.append(hashed_code)
        
        self.backup_codes[user_id] = hashed_codes
        return codes
    
    def setup_mfa(self, user_id: str, user_email: str) -> MFASetup:
        """Complete MFA setup for user"""
        secret = self.generate_secret(user_id)
        qr_code = self.generate_qr_code(user_id, user_email)
        backup_codes = self.generate_backup_codes(user_id)
        
        # Generate setup token for verification
        setup_token = secrets.token_urlsafe(32)
        
        setup = MFASetup(
            user_id=user_id,
            secret=secret,
            qr_code=qr_code,
            backup_codes=backup_codes,
            setup_token=setup_token
        )
        
        logging.info(f"MFA setup initiated for user {user_id}")
        return setup
    
    def verify_totp(self, user_id: str, token: str) -> MFAValidation:
        """Verify TOTP token"""
        if self.is_user_locked(user_id):
            locked_until = self.failed_attempts[user_id]['locked_until']
            return MFAValidation(
                is_valid=False,
                method='totp',
                remaining_attempts=0,
                locked_until=locked_until
            )
        
        secret = self.user_secrets.get(user_id)
        if not secret:
            return MFAValidation(is_valid=False, method='totp', remaining_attempts=0)
        
        totp = pyotp.TOTP(secret)
        
        # Verify token with window for time drift
        is_valid = totp.verify(token, valid_window=1)
        
        if is_valid:
            self.reset_failed_attempts(user_id)
            logging.info(f"TOTP verification successful for user {user_id}")
        else:
            self.record_failed_attempt(user_id)
            logging.warning(f"TOTP verification failed for user {user_id}")
        
        remaining_attempts = max(0, self.max_attempts - self.get_failed_attempts(user_id))
        
        return MFAValidation(
            is_valid=is_valid,
            method='totp',
            remaining_attempts=remaining_attempts
        )
    
    def verify_backup_code(self, user_id: str, code: str) -> MFAValidation:
        """Verify backup code (one-time use)"""
        if self.is_user_locked(user_id):
            locked_until = self.failed_attempts[user_id]['locked_until']
            return MFAValidation(
                is_valid=False,
                method='backup_code',
                remaining_attempts=0,
                locked_until=locked_until
            )
        
        user_codes = self.backup_codes.get(user_id, [])
        if not user_codes:
            return MFAValidation(is_valid=False, method='backup_code', remaining_attempts=0)
        
        # Remove hyphens and hash the code
        clean_code = code.replace('-', '').upper()
        code_hash = hashlib.sha256(clean_code.encode()).hexdigest()
        
        is_valid = code_hash in user_codes
        
        if is_valid:
            # Remove used backup code
            user_codes.remove(code_hash)
            self.reset_failed_attempts(user_id)
            logging.info(f"Backup code verification successful for user {user_id}")
        else:
            self.record_failed_attempt(user_id)
            logging.warning(f"Backup code verification failed for user {user_id}")
        
        remaining_attempts = max(0, self.max_attempts - self.get_failed_attempts(user_id))
        
        return MFAValidation(
            is_valid=is_valid,
            method='backup_code',
            remaining_attempts=remaining_attempts
        )
    
    def send_sms_code(self, user_id: str, phone_number: str) -> bool:
        """Send SMS verification code (mock implementation)"""
        # Generate 6-digit code
        sms_code = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        # Store code with expiration (5 minutes)
        if not hasattr(self, 'sms_codes'):
            self.sms_codes = {}
        
        self.sms_codes[user_id] = {
            'code': sms_code,
            'expires': datetime.now(timezone.utc) + timedelta(minutes=5),
            'phone': phone_number
        }
        
        # In production, send via SMS service
        logging.info(f"SMS code {sms_code} generated for {phone_number} (user {user_id})")
        
        # Mock SMS sending - in production, use Twilio or similar
        return True
    
    def verify_sms_code(self, user_id: str, code: str) -> MFAValidation:
        """Verify SMS code"""
        if self.is_user_locked(user_id):
            locked_until = self.failed_attempts[user_id]['locked_until']
            return MFAValidation(
                is_valid=False,
                method='sms',
                remaining_attempts=0,
                locked_until=locked_until
            )
        
        if not hasattr(self, 'sms_codes') or user_id not in self.sms_codes:
            return MFAValidation(is_valid=False, method='sms', remaining_attempts=0)
        
        sms_data = self.sms_codes[user_id]
        
        # Check expiration
        if datetime.now(timezone.utc) > sms_data['expires']:
            del self.sms_codes[user_id]
            return MFAValidation(is_valid=False, method='sms', remaining_attempts=0)
        
        is_valid = sms_data['code'] == code
        
        if is_valid:
            del self.sms_codes[user_id]  # One-time use
            self.reset_failed_attempts(user_id)
            logging.info(f"SMS verification successful for user {user_id}")
        else:
            self.record_failed_attempt(user_id)
            logging.warning(f"SMS verification failed for user {user_id}")
        
        remaining_attempts = max(0, self.max_attempts - self.get_failed_attempts(user_id))
        
        return MFAValidation(
            is_valid=is_valid,
            method='sms',
            remaining_attempts=remaining_attempts
        )
    
    def is_user_locked(self, user_id: str) -> bool:
        """Check if user is locked due to failed attempts"""
        if user_id not in self.failed_attempts:
            return False
        
        attempt_data = self.failed_attempts[user_id]
        
        if 'locked_until' not in attempt_data:
            return False
        
        return datetime.now(timezone.utc) < attempt_data['locked_until']
    
    def record_failed_attempt(self, user_id: str):
        """Record failed MFA attempt"""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = {'count': 0}
        
        self.failed_attempts[user_id]['count'] += 1
        
        # Lock user if max attempts reached
        if self.failed_attempts[user_id]['count'] >= self.max_attempts:
            self.failed_attempts[user_id]['locked_until'] = (
                datetime.now(timezone.utc) + timedelta(seconds=self.lockout_duration)
            )
            logging.warning(f"User {user_id} locked due to failed MFA attempts")
    
    def reset_failed_attempts(self, user_id: str):
        """Reset failed attempts counter"""
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
    
    def get_failed_attempts(self, user_id: str) -> int:
        """Get number of failed attempts"""
        return self.failed_attempts.get(user_id, {}).get('count', 0)
    
    def disable_mfa(self, user_id: str) -> bool:
        """Disable MFA for user"""
        removed_items = 0
        
        if user_id in self.user_secrets:
            del self.user_secrets[user_id]
            removed_items += 1
        
        if user_id in self.backup_codes:
            del self.backup_codes[user_id]
            removed_items += 1
        
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
            removed_items += 1
        
        if hasattr(self, 'sms_codes') and user_id in self.sms_codes:
            del self.sms_codes[user_id]
            removed_items += 1
        
        logging.info(f"MFA disabled for user {user_id} ({removed_items} items removed)")
        return removed_items > 0
    
    def get_user_mfa_status(self, user_id: str) -> Dict:
        """Get MFA status for user"""
        has_totp = user_id in self.user_secrets
        backup_codes_count = len(self.backup_codes.get(user_id, []))
        is_locked = self.is_user_locked(user_id)
        failed_attempts = self.get_failed_attempts(user_id)
        
        status = {
            'user_id': user_id,
            'totp_enabled': has_totp,
            'backup_codes_remaining': backup_codes_count,
            'is_locked': is_locked,
            'failed_attempts': failed_attempts,
            'max_attempts': self.max_attempts,
        }
        
        if is_locked:
            status['locked_until'] = self.failed_attempts[user_id]['locked_until'].isoformat()
        
        return status
    
    def generate_recovery_codes(self, user_id: str) -> List[str]:
        """Generate new recovery codes (invalidates old ones)"""
        return self.generate_backup_codes(user_id)

# Global MFA service instance
mfa_service = MFAService()