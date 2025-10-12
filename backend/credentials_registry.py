"""
FIDUS Platform Credentials Registry
Metadata-only registry for credential management
NO ACTUAL CREDENTIALS STORED HERE - Only references to environment variables
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel

class CredentialMetadata(BaseModel):
    """Metadata for a credential entry"""
    name: str
    type: str  # database, infrastructure, integration, service
    category: str
    fields: List[str]
    storage: str  # environment_variable, secret_file, vault
    env_keys: Optional[List[str]] = None
    status: str  # configured, partial, missing
    dashboard_url: Optional[str] = None
    documentation_url: Optional[str] = None
    last_rotated: Optional[str] = None
    rotation_recommended_days: Optional[int] = None
    public_info: Optional[Dict] = None
    notes: Optional[str] = None

# Credentials Registry - Metadata Only
CREDENTIALS_REGISTRY = {
    'mongodb_atlas': {
        'name': 'MongoDB Atlas',
        'type': 'database',
        'category': 'Core Infrastructure',
        'fields': ['connection_string', 'database_name', 'username', 'password'],
        'storage': 'environment_variable',
        'env_keys': ['MONGO_URL', 'DB_NAME'],
        'status': 'configured',
        'dashboard_url': 'https://cloud.mongodb.com',
        'documentation_url': 'https://www.mongodb.com/docs/atlas/',
        'last_rotated': None,
        'rotation_recommended_days': 90,
        'public_info': {
            'cluster': 'fidus.y1p9be2.mongodb.net',
            'region': 'US East'
        },
        'notes': 'Production database. Credentials stored in Render environment variables.'
    },
    
    'vps_server': {
        'name': 'Windows VPS (ForexVPS)',
        'type': 'infrastructure',
        'category': 'Core Infrastructure',
        'fields': ['ip_address', 'rdp_port', 'ssh_port', 'username', 'password'],
        'storage': 'secure_vault',
        'env_keys': ['VPS_IP', 'VPS_USERNAME'],
        'status': 'configured',
        'dashboard_url': 'https://forexvps.net',
        'last_rotated': None,
        'rotation_recommended_days': 180,
        'public_info': {
            'ip': '217.197.163.11',
            'hostname': 'VMI0594978015651953-1.forexvps.net',
            'rdp_port': 3389,
            'ssh_port': 22
        },
        'notes': 'RDP access for MT5 terminal and bridge service. Password stored securely.'
    },
    
    'google_oauth': {
        'name': 'Google Workspace OAuth 2.0',
        'type': 'integration',
        'category': 'External Services',
        'fields': ['client_id', 'client_secret', 'redirect_uris'],
        'storage': 'environment_variable',
        'env_keys': ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'],
        'status': 'configured',
        'dashboard_url': 'https://console.cloud.google.com',
        'documentation_url': 'https://developers.google.com/identity/protocols/oauth2',
        'last_rotated': None,
        'rotation_recommended_days': 365,
        'public_info': {
            'project': 'shaped-canyon-470822-b3',
            'enabled_apis': ['Gmail API', 'Calendar API', 'Drive API', 'Meet API']
        },
        'notes': 'OAuth credentials for Google Workspace integration. Client ID and secret in env vars.'
    },
    
    'google_service_account': {
        'name': 'Google Service Account',
        'type': 'integration',
        'category': 'External Services',
        'fields': ['service_account_email', 'private_key_json'],
        'storage': 'secret_file',
        'env_keys': ['GOOGLE_SERVICE_ACCOUNT_FILE'],
        'status': 'partial',
        'dashboard_url': 'https://console.cloud.google.com/iam-admin/serviceaccounts',
        'last_rotated': None,
        'rotation_recommended_days': 90,
        'public_info': {
            'email': 'fidus-gmail-service@shaped-canyon-470822-b3.iam.gserviceaccount.com',
            'project': 'shaped-canyon-470822-b3'
        },
        'notes': 'Service account for server-to-server Google API calls. JSON key file needed.'
    },
    
    'render_api': {
        'name': 'Render.com API',
        'type': 'service',
        'category': 'Hosting & Deployment',
        'fields': ['api_key', 'account_email'],
        'storage': 'environment_variable',
        'env_keys': ['RENDER_API_KEY'],
        'status': 'configured',
        'dashboard_url': 'https://dashboard.render.com',
        'documentation_url': 'https://render.com/docs',
        'last_rotated': None,
        'rotation_recommended_days': 180,
        'public_info': {
            'account': 'chavapalmarubin2025 (FIDUS HEDGE FUND)',
            'backend_service': 'fidus-api',
            'backend_url': 'https://fidus-api.onrender.com'
        },
        'notes': 'API key for programmatic deployment and management.'
    },
    
    'emergent_host': {
        'name': 'Emergent.host Platform',
        'type': 'service',
        'category': 'Hosting & Deployment',
        'fields': ['api_token', 'workspace_id'],
        'storage': 'environment_variable',
        'env_keys': ['EMERGENT_API_TOKEN'],
        'status': 'missing',
        'dashboard_url': 'https://app.emergent.host',
        'documentation_url': 'https://docs.emergent.host',
        'last_rotated': None,
        'rotation_recommended_days': 90,
        'public_info': {
            'frontend_url': 'https://fidus-invest.emergent.host',
            'platform': 'Kubernetes'
        },
        'notes': 'API token needed from Emergent.host dashboard for programmatic access.'
    },
    
    'mt5_trading': {
        'name': 'MT5 Trading Accounts (MEXAtlantic)',
        'type': 'trading',
        'category': 'Trading Infrastructure',
        'fields': ['broker', 'server', 'account_numbers', 'investor_passwords'],
        'storage': 'secure_vault',
        'env_keys': None,
        'status': 'configured',
        'dashboard_url': 'https://mexatlantic.com',
        'last_rotated': None,
        'rotation_recommended_days': 90,
        'public_info': {
            'broker': 'MEXAtlantic',
            'server': 'MEXAtlantic-Real',
            'accounts': ['886557', '886066', '886602', '885822', '886528'],
            'warning': '🚨 ONLY USE INVESTOR PASSWORDS (READ-ONLY)'
        },
        'notes': 'CRITICAL: MT5 has two password types - NEVER use trading passwords. Investor passwords are read-only for monitoring only.'
    },
    
    'smtp_email': {
        'name': 'SMTP Email Service (Gmail)',
        'type': 'service',
        'category': 'Communication',
        'fields': ['smtp_host', 'smtp_port', 'username', 'app_password'],
        'storage': 'environment_variable',
        'env_keys': ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD'],
        'status': 'partial',
        'dashboard_url': 'https://mail.google.com',
        'documentation_url': 'https://support.google.com/mail/answer/185833',
        'last_rotated': None,
        'rotation_recommended_days': 180,
        'public_info': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'chavapalmarubin@gmail.com'
        },
        'notes': 'App-specific password needed from Gmail security settings. Do not use account password.'
    },
    
    'github_repo': {
        'name': 'GitHub Repository',
        'type': 'service',
        'category': 'Version Control',
        'fields': ['repository_url', 'personal_access_token', 'webhook_secret'],
        'storage': 'environment_variable',
        'env_keys': ['GITHUB_TOKEN', 'GITHUB_WEBHOOK_SECRET'],
        'status': 'missing',
        'dashboard_url': 'https://github.com',
        'documentation_url': 'https://docs.github.com',
        'last_rotated': None,
        'rotation_recommended_days': 90,
        'public_info': {
            'repository': 'TBD'
        },
        'notes': 'GitHub personal access token and webhook secret needed for CI/CD integration.'
    },
    
    'document_signing': {
        'name': 'Document Signing Service',
        'type': 'service',
        'category': 'Legal & Compliance',
        'fields': ['api_key', 'workspace_id'],
        'storage': 'environment_variable',
        'env_keys': None,
        'status': 'not_configured',
        'dashboard_url': None,
        'last_rotated': None,
        'rotation_recommended_days': None,
        'notes': 'Service not yet selected. Options: DocuSign, HelloSign, Adobe Sign.'
    },
    
    'payment_gateway': {
        'name': 'Payment Gateway',
        'type': 'service',
        'category': 'Financial Services',
        'fields': ['api_key', 'secret_key', 'publishable_key'],
        'storage': 'environment_variable',
        'env_keys': None,
        'status': 'not_configured',
        'dashboard_url': None,
        'last_rotated': None,
        'rotation_recommended_days': None,
        'notes': 'Service not yet selected. Options: Stripe, PayPal, Square.'
    }
}

# Category definitions
CREDENTIAL_CATEGORIES = {
    'Core Infrastructure': ['mongodb_atlas', 'vps_server'],
    'External Services': ['google_oauth', 'google_service_account'],
    'Hosting & Deployment': ['render_api', 'emergent_host'],
    'Trading Infrastructure': ['mt5_trading'],
    'Communication': ['smtp_email'],
    'Version Control': ['github_repo'],
    'Legal & Compliance': ['document_signing'],
    'Financial Services': ['payment_gateway']
}

# Status definitions
CREDENTIAL_STATUSES = {
    'configured': {
        'label': 'Configured',
        'color': 'green',
        'icon': '✅',
        'description': 'Credentials configured and working'
    },
    'partial': {
        'label': 'Partial',
        'color': 'yellow',
        'icon': '⚠️',
        'description': 'Some credentials missing or need action'
    },
    'missing': {
        'label': 'Missing',
        'color': 'orange',
        'icon': '🔴',
        'description': 'Credentials need to be added'
    },
    'not_configured': {
        'label': 'Not Configured',
        'color': 'gray',
        'icon': '⚪',
        'description': 'Service not yet set up'
    }
}

def get_all_credentials():
    """Get all credential metadata"""
    return CREDENTIALS_REGISTRY

def get_credential_by_id(credential_id: str):
    """Get specific credential metadata"""
    return CREDENTIALS_REGISTRY.get(credential_id)

def get_credentials_by_category(category: str):
    """Get credentials for a specific category"""
    credential_ids = CREDENTIAL_CATEGORIES.get(category, [])
    return {cid: CREDENTIALS_REGISTRY[cid] for cid in credential_ids if cid in CREDENTIALS_REGISTRY}

def get_credentials_by_status(status: str):
    """Get all credentials with a specific status"""
    return {
        cid: cred for cid, cred in CREDENTIALS_REGISTRY.items()
        if cred.get('status') == status
    }

def get_credentials_summary():
    """Get summary of credential statuses"""
    summary = {
        'total': len(CREDENTIALS_REGISTRY),
        'by_status': {},
        'by_category': {}
    }
    
    for credential_id, credential in CREDENTIALS_REGISTRY.items():
        status = credential.get('status', 'unknown')
        summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
    
    for category, credential_ids in CREDENTIAL_CATEGORIES.items():
        summary['by_category'][category] = len(credential_ids)
    
    return summary
