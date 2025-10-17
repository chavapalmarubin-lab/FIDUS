"""
FIDUS Platform System Registry
Complete inventory of all system components, connections, and metadata
This serves as the source of truth for the Technical Documentation system
"""

from datetime import datetime
from typing import Dict, List, Any

SYSTEM_COMPONENTS = {
    'applications': [
        {
            'id': 'frontend',
            'name': 'FIDUS Frontend',
            'type': 'application',
            'category': 'Application Layer',
            'status': 'online',
            'url': 'https://fidus-investment-platform.onrender.com',
            'platform': 'Render Static Site',
            'description': 'React-based client portal for investors and administrators',
            'tech_stack': ['React 19.0+', 'Tailwind CSS', 'Yarn', 'JavaScript/JSX'],
            'environment': {
                'platform': 'Render.com',
                'deployment': 'Static Site (Built-in CDN)',
                'auto_scaling': True,
                'region': 'Global (Render CDN)'
            },
            'credentials_ref': 'render_frontend',
            'dependencies': ['backend'],
            'health_check': {
                'endpoint': 'https://fidus-investment-platform.onrender.com',
                'method': 'GET',
                'expected_status': 200,
                'timeout': 5
            },
            'management': {
                'dashboard': 'https://dashboard.render.com',
                'logs': 'Available via Render dashboard',
                'restart': 'Auto-deploy on git push',
                'features': ['Built-in SSL/TLS', 'Built-in CDN', 'Auto-deploy from GitHub', 'Zero-downtime deploys']
            },
            'quick_actions': ['viewLogs', 'deploy', 'viewMetrics'],
            'documentation': 'Frontend serves the investor portal with responsive design. Hosted on Render with built-in CDN and SSL.'
        },
        {
            'id': 'backend',
            'name': 'FIDUS Backend API',
            'type': 'application',
            'category': 'Application Layer',
            'status': 'online',
            'url': 'https://fidus-api.onrender.com',
            'platform': 'Render.com',
            'description': 'FastAPI-based REST API handling all business logic and data operations',
            'tech_stack': ['Python 3.11+', 'FastAPI', 'Motor (MongoDB Driver)', 'Pydantic'],
            'environment': {
                'platform': 'Render.com',
                'deployment': 'Docker Container',
                'auto_scaling': False,
                'region': 'US East'
            },
            'credentials_ref': 'render_backend',
            'dependencies': ['mongodb'],
            'health_check': {
                'endpoint': 'https://fidus-api.onrender.com/api/health',
                'method': 'GET',
                'expected_status': 200,
                'timeout': 5
            },
            'management': {
                'dashboard': 'https://dashboard.render.com',
                'logs': 'Available via Render dashboard',
                'restart': 'Via Render dashboard or API'
            },
            'api_docs': {
                'swagger': 'https://fidus-api.onrender.com/docs',
                'redoc': 'https://fidus-api.onrender.com/redoc'
            },
            'quick_actions': ['viewLogs', 'restart', 'deploy', 'viewMetrics', 'testAPI'],
            'documentation': 'Backend API handles authentication, investments, MT5 integration, and all business logic'
        }
    ],
    
    'databases': [
        {
            'id': 'mongodb',
            'name': 'MongoDB Atlas',
            'type': 'database',
            'category': 'Data Layer',
            'status': 'online',
            'url': 'mongodb+srv://fidus.y1p9be2.mongodb.net',
            'platform': 'MongoDB Atlas (AWS)',
            'description': 'Primary database storing all application data',
            'tech_stack': ['MongoDB 7.0+', 'Atlas Cloud'],
            'environment': {
                'platform': 'MongoDB Atlas',
                'deployment': 'Managed Cloud (AWS)',
                'cluster_tier': 'M0 (Free Tier)',
                'region': 'US East',
                'replica_set': True
            },
            'database_info': {
                'database_name': 'fidus_production',
                'collections': [
                    'users',
                    'prospects',
                    'investments',
                    'mt5_accounts',
                    'sessions',
                    'documents',
                    'mt5_update_log',
                    'redemptions',
                    'deals',  # Historical deal data
                    'money_managers',  # Trading strategy managers
                    'fund_allocations',  # Fund allocation records
                    'mt5_deals_history',  # MT5 deal history for analytics
                    'mt5_trades'  # Closed trades for performance calculations
                ],
                'backup_enabled': True,
                'backup_frequency': 'Daily',
                'indexes_optimized': True  # Added in Phase 7
            },
            'credentials_ref': 'mongodb_atlas',
            'dependencies': [],
            'health_check': {
                'method': 'connection_test',
                'timeout': 3
            },
            'management': {
                'dashboard': 'https://cloud.mongodb.com',
                'admin_user': 'emergent-ops',
                'connection_string': 'Protected - See Credentials Vault'
            },
            'quick_actions': ['testConnection', 'viewMetrics', 'viewCollections', 'backup'],
            'documentation': 'MongoDB Atlas hosts all application data with automatic backups and monitoring'
        }
    ],
    
    'services': [
        {
            'id': 'vps',
            'name': 'Windows VPS Server',
            'type': 'infrastructure',
            'category': 'Services Layer',
            'status': 'online',
            'url': '217.197.163.11',
            'platform': 'Windows Server 2022',
            'description': 'Dedicated VPS hosting MT5 Terminal and Bridge Service',
            'tech_stack': ['Windows Server 2022', 'Python 3.12', 'MetaTrader 5', 'Task Scheduler'],
            'environment': {
                'platform': 'VPS Hosting',
                'os': 'Windows Server 2022',
                'ram': '8GB',
                'cpu': '4 vCPU',
                'storage': '160GB SSD'
            },
            'services_running': [
                {
                    'name': 'MT5 Bridge Service',
                    'type': 'Python Script',
                    'schedule': 'Every 15 minutes',
                    'manager': 'Windows Task Scheduler',
                    'log_location': 'C:\\mt5_bridge_service\\logs\\'
                },
                {
                    'name': 'MT5 Terminal',
                    'type': 'Trading Platform',
                    'executable': 'terminal64.exe',
                    'path': 'C:\\Program Files\\MEX Atlantic MT5 Terminal\\',
                    'accounts_connected': 5
                }
            ],
            'credentials_ref': 'vps_access',
            'dependencies': ['mt5_terminal', 'mt5_bridge'],
            'health_check': {
                'method': 'ping',
                'timeout': 2
            },
            'management': {
                'rdp_access': '217.197.163.11:3389',
                'ssh_access': 'Available',
                'admin_users': ['Administrator', 'EmergentOps']
            },
            'quick_actions': ['pingServer', 'viewLogs', 'restartService', 'checkMT5Status'],
            'documentation': 'VPS hosts the MT5 Bridge Service and MetaTrader 5 terminal for trading operations'
        },
        {
            'id': 'mt5_bridge',
            'name': 'MT5 Bridge Service',
            'type': 'service',
            'category': 'Services Layer',
            'status': 'online',
            'url': 'http://217.197.163.11:8000',
            'platform': 'Python Script (Windows Task Scheduler)',
            'description': 'Syncs MT5 account data to MongoDB every 15 minutes',
            'tech_stack': ['Python 3.12', 'MetaTrader5 Library', 'pymongo', 'Task Scheduler'],
            'environment': {
                'platform': 'Windows VPS',
                'execution': 'Task Scheduler',
                'frequency': 'Every 15 minutes (900 seconds)',
                'log_retention': '30 days'
            },
            'sync_config': {
                'accounts': [886557, 886066, 886602, 885822, 886528],
                'data_synced': ['balance', 'equity', 'profit', 'margin', 'free_margin'],
                'target_database': 'fidus_production.mt5_accounts',
                'sync_log': 'fidus_production.mt5_update_log'
            },
            'credentials_ref': 'vps_access',
            'dependencies': ['vps', 'mt5_terminal', 'mongodb'],
            'health_check': {
                'method': 'check_last_sync',
                'max_staleness_minutes': 20
            },
            'management': {
                'script_location': 'C:\\mt5_bridge_service\\mt5_bridge_service_production.py',
                'logs': 'C:\\mt5_bridge_service\\logs\\service_output.log',
                'task_name': 'MT5 Bridge Service'
            },
            'quick_actions': ['viewLogs', 'runManualSync', 'checkTaskScheduler', 'viewSyncHistory'],
            'documentation': 'Automated service that syncs MT5 account data to MongoDB for real-time fund tracking'
        },
        {
            'id': 'mt5_terminal',
            'name': 'MetaTrader 5 Terminal',
            'type': 'service',
            'category': 'Services Layer',
            'status': 'online',
            'url': 'C:\\Program Files\\MEX Atlantic MT5 Terminal\\terminal64.exe',
            'platform': 'MEXAtlantic Broker',
            'description': 'Trading platform connected to 5 MT5 accounts',
            'tech_stack': ['MetaTrader 5', 'MQL5', 'Windows Desktop App'],
            'environment': {
                'platform': 'Windows VPS',
                'broker': 'MEXAtlantic',
                'server': 'MEXAtlantic-Real',
                'accounts_connected': 5
            },
            'trading_accounts': [
                {'account': 886557, 'fund_type': 'BALANCE', 'description': 'Primary trading account'},
                {'account': 886066, 'fund_type': 'BALANCE', 'description': 'Secondary trading account'},
                {'account': 886602, 'fund_type': 'BALANCE', 'description': 'Tertiary trading account'},
                {'account': 885822, 'fund_type': 'CORE', 'description': 'Core fund trading account'},
                {'account': 886528, 'fund_type': 'INTEREST_SEPARATION', 'description': 'Interest reserve account'}
            ],
            'credentials_ref': 'mt5_accounts',
            'dependencies': ['vps'],
            'health_check': {
                'method': 'check_process',
                'process_name': 'terminal64.exe'
            },
            'management': {
                'executable': 'C:\\Program Files\\MEX Atlantic MT5 Terminal\\terminal64.exe',
                'data_folder': 'C:\\Users\\Administrator\\AppData\\Roaming\\MetaQuotes\\Terminal\\',
                'restart': 'Via VPS RDP'
            },
            'quick_actions': ['checkProcess', 'viewAccounts', 'restartTerminal'],
            'documentation': 'MT5 Terminal manages all trading operations across 5 accounts with live market data'
        }
    ],
    
    'integrations': [
        {
            'id': 'google_workspace',
            'name': 'Google Workspace',
            'type': 'integration',
            'category': 'External Integrations',
            'status': 'online',
            'url': 'https://workspace.google.com',
            'platform': 'Google Cloud',
            'description': 'Integrated Google services: Gmail, Calendar, Drive, Meet',
            'tech_stack': ['Google APIs', 'OAuth 2.0', 'REST APIs'],
            'environment': {
                'platform': 'Google Cloud',
                'oauth_version': '2.0',
                'scopes': ['Gmail', 'Calendar', 'Drive', 'Meet']
            },
            'apis_used': [
                {'name': 'Gmail API', 'purpose': 'Email communications'},
                {'name': 'Calendar API', 'purpose': 'Scheduling and reminders'},
                {'name': 'Drive API', 'purpose': 'Document storage'},
                {'name': 'Meet API', 'purpose': 'Video conferencing'}
            ],
            'credentials_ref': 'google_workspace',
            'dependencies': ['backend'],
            'health_check': {
                'method': 'oauth_token_check',
                'timeout': 3
            },
            'management': {
                'admin_console': 'https://admin.google.com',
                'api_console': 'https://console.cloud.google.com',
                'oauth_client': 'Configured in Google Cloud Console'
            },
            'quick_actions': ['testOAuth', 'viewScopes', 'refreshToken', 'viewAPIUsage'],
            'documentation': 'Google Workspace integration provides email, calendar, document management, and video conferencing'
        },
        {
            'id': 'email_service',
            'name': 'Email SMTP Service',
            'type': 'integration',
            'category': 'External Integrations',
            'status': 'online',
            'url': 'smtp.gmail.com:587',
            'platform': 'Gmail SMTP',
            'description': 'SMTP service for sending automated emails to clients',
            'tech_stack': ['SMTP', 'TLS/SSL', 'Gmail App Passwords'],
            'environment': {
                'platform': 'Gmail',
                'protocol': 'SMTP',
                'port': 587,
                'encryption': 'TLS'
            },
            'email_config': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'authentication': 'App Password',
                'from_addresses': ['notifications@fidus.com', 'support@fidus.com']
            },
            'credentials_ref': 'email_smtp',
            'dependencies': ['backend'],
            'health_check': {
                'method': 'smtp_connect',
                'timeout': 3
            },
            'management': {
                'smtp_server': 'smtp.gmail.com',
                'security': 'App Passwords (2FA)',
                'configuration': 'Backend environment variables'
            },
            'quick_actions': ['testConnection', 'sendTestEmail', 'viewEmailLog'],
            'documentation': 'SMTP service handles all automated email notifications for investment updates and client communications'
        },
        {
            'id': 'github',
            'name': 'GitHub Repository',
            'type': 'version_control',
            'category': 'Development & Deployment',
            'status': 'online',
            'url': 'https://github.com/chavapalmarubin/fidus-platform',
            'platform': 'GitHub',
            'description': 'Source of truth for all code. Central repository for version control with auto-deployment to Render.',
            'tech_stack': ['Git', 'GitHub', 'Auto-Deploy'],
            'environment': {
                'platform': 'GitHub.com',
                'branches': {
                    'main': 'Production (auto-deploys to Render)',
                    'develop': 'Active development'
                },
                'automation_status': 'Active - Auto-deploy to Render on push'
            },
            'repository_structure': {
                'frontend/': 'React application (auto-deploys to Render Static Site)',
                'backend/': 'FastAPI application (auto-deploys to Render Web Service)',
                'vps-services/': 'VPS scripts and MT5 bridge service',
                'infrastructure/': 'System configuration and registry',
                'docs/': 'Documentation and guides'
            },
            'active_automation': [
                'Auto-deploy frontend to Render on push to main',
                'Auto-deploy backend to Render on push to main',
                'Zero-downtime deployments via Render',
                'Automatic SSL certificate renewal'
            ],
            'credentials_ref': 'github_access',
            'dependencies': ['render_platform'],
            'health_check': {
                'method': 'always_available',
                'status': 'GitHub services are highly available',
                'uptime': '99.99%'
            },
            'management': {
                'repository': 'https://github.com/chavapalmarubin/fidus-platform',
                'access': 'Team members with appropriate permissions',
                'deployment': 'Auto-deploy via Render integration'
            },
            'quick_actions': ['viewRepository', 'viewCommits', 'viewBranches', 'triggerDeploy'],
            'documentation': 'GitHub serves as the central version control system with automatic deployments to Render on every push to main branch'
        }
    ],
    
    'infrastructure': [
        {
            'id': 'render_platform',
            'name': 'Render Hosting Platform',
            'type': 'infrastructure',
            'category': 'Infrastructure',
            'status': 'online',
            'url': 'https://dashboard.render.com',
            'platform': 'Render.com',
            'description': 'Cloud hosting platform with built-in SSL, CDN, load balancing, and auto-deploy',
            'tech_stack': ['Docker', 'Git Auto-Deploy', 'Built-in SSL/TLS', 'Global CDN', 'Load Balancing'],
            'environment': {
                'platform': 'Render.com',
                'type': 'Managed Cloud Platform',
                'regions': 'US East (Backend), Global CDN (Frontend)'
            },
            'services': {
                'backend_api': {
                    'name': 'FIDUS Backend API',
                    'url': 'https://fidus-api.onrender.com',
                    'type': 'Web Service',
                    'auto_deploy': True
                },
                'frontend_app': {
                    'name': 'FIDUS Frontend',
                    'url': 'https://fidus-investment-platform.onrender.com',
                    'type': 'Static Site',
                    'auto_deploy': True,
                    'cdn_enabled': True
                }
            },
            'features': {
                'auto_deploy_from_github': True,
                'zero_downtime_deploys': True,
                'built_in_ssl': True,
                'built_in_cdn': True,
                'built_in_load_balancing': True,
                'health_checks': True,
                'ddos_protection': True,
                'automatic_ssl_renewal': True
            },
            'credentials_ref': 'render_api_token',
            'dependencies': [],
            'health_check': {
                'method': 'platform_monitoring',
                'monitored_by': 'Render Platform'
            },
            'management': {
                'dashboard': 'https://dashboard.render.com',
                'logs': 'Real-time logs in Render dashboard',
                'deploy': 'Auto-deploy on git push',
                'configuration': 'render.yaml or dashboard'
            },
            'quick_actions': ['viewDashboard', 'viewLogs', 'viewMetrics', 'triggerDeploy'],
            'documentation': 'Render platform hosts both frontend and backend with built-in SSL, CDN, load balancing, and auto-deploy from GitHub. No separate load balancer or CDN configuration needed.'
        }
,
        {
            'id': 'trading-analytics',
            'name': 'Trading Analytics System',
            'type': 'feature',
            'category': 'Applications',
            'status': 'online',
            'description': 'Manager-level performance analytics with risk-adjusted metrics for capital allocation decisions',
            'version': '1.0.0',
            'features': [
                'Portfolio overview aggregating all funds',
                'Fund performance tracking (BALANCE/CORE)',
                'Manager rankings with Sharpe/Sortino/Calmar ratios',
                'Capital allocation recommendations',
                'Automated risk alerts and warnings',
                'Period selection (7d, 30d, 90d, 6m, 1y)',
                'Export capabilities',
                'Real-time performance metrics'
            ],
            'endpoints': [
                '/api/admin/trading-analytics/portfolio',
                '/api/admin/trading-analytics/funds/{fund_name}',
                '/api/admin/trading-analytics/managers',
                '/api/admin/trading-analytics/managers/{manager_id}'
            ],
            'tech_stack': ['React 19', 'FastAPI', 'MongoDB', 'Tailwind CSS'],
            'performance': {
                'page_load': '~1s (67% faster with lazy loading)',
                'api_response_cached': '<50ms (16x faster)',
                'api_response_uncached': '<500ms',
                'caching_ttl': '5 minutes'
            },
            'components': [
                'PortfolioView.js - Aggregate fund metrics',
                'FundsView.js - Individual fund analysis',
                'ManagersView.js - Manager rankings (primary)',
                'AccountsView.js - Account-level details'
            ],
            'last_updated': '2025-10-17',
            'phase': 'Production',
            'documentation': '/docs/TRADING_ANALYTICS_USER_GUIDE.md',
            'quick_actions': ['viewManagers', 'exportReports', 'clearCache']
        },
        {
            'id': 'money-managers',
            'name': 'Money Managers System',
            'type': 'data_model',
            'category': 'Services',
            'status': 'online',
            'description': 'Trading strategy managers with performance tracking and risk management',
            'managers': [
                {
                    'name': 'UNO14 MAM Manager',
                    'account': 886602,
                    'fund': 'BALANCE',
                    'strategy': 'MAM Execution',
                    'risk': 'Medium',
                    'return_pct': 11.40,
                    'sharpe_ratio': 1.85,
                    'status': '⭐ Best Performer'
                },
                {
                    'name': 'TradingHub Gold Provider',
                    'account': 886557,
                    'fund': 'BALANCE',
                    'strategy': 'Copy Trade',
                    'risk': 'Medium',
                    'return_pct': 6.21,
                    'sharpe_ratio': 1.34,
                    'status': '✓ Solid'
                },
                {
                    'name': 'GoldenTrade Provider',
                    'account': 886066,
                    'fund': 'BALANCE',
                    'strategy': 'Copy Trade',
                    'risk': 'High',
                    'return_pct': 6.92,
                    'sharpe_ratio': 0.87,
                    'status': '⚠️ High Risk'
                },
                {
                    'name': 'CP Strategy Provider',
                    'account': 885822,
                    'fund': 'CORE',
                    'strategy': 'Copy Trade',
                    'risk': 'Medium',
                    'return_pct': 1.01,
                    'sharpe_ratio': 1.12,
                    'status': 'Monitor'
                }
            ],
            'total_managers': 4,
            'active_managers': 4,
            'collection': 'money_managers',
            'metrics_tracked': [
                'Return percentage',
                'Sharpe ratio (risk-adjusted return)',
                'Sortino ratio (downside risk)',
                'Calmar ratio (return vs drawdown)',
                'Maximum drawdown',
                'Win rate',
                'Profit factor'
            ],
            'last_updated': '2025-10-17',
            'documentation': 'Managers tracked in money_managers MongoDB collection with performance calculated from mt5_trades'
        },
        {
            'id': 'ui-component-library',
            'name': 'FIDUS UI Component Library',
            'type': 'library',
            'category': 'Frontend',
            'status': 'online',
            'description': 'Shared style system and reusable UI components for consistent FIDUS branding',
            'version': '1.0.0',
            'components': [
                'Button - 7 variants (primary, secondary, success, danger, warning, outline, ghost)',
                'LoadingSpinner - 3 sizes (sm, md, lg) with customizable text',
                'Badge - Auto-styling based on type (status, fund, risk)',
                'Card - Standard layouts with header, content, footer'
            ],
            'style_constants': {
                'colors': {
                    'primary_cyan': '#00bcd4',
                    'secondary_orange': '#ffa726',
                    'success_green': '#4caf50',
                    'danger_red': '#ef4444'
                },
                'spacing': 'Consistent padding/margins (4px increments)',
                'typography': 'Standard sizes (3xl, 2xl, xl, lg, base, sm)',
                'transitions': 'Smooth animations (200ms ease-in-out)'
            },
            'location': '/app/frontend/src/constants/styles.js',
            'usage': 'import { Button, Badge, LoadingSpinner } from "@/components/ui"',
            'benefits': [
                'Consistent FIDUS brand identity',
                'Reduced code duplication',
                'Easy maintenance',
                'Faster development',
                'Professional appearance'
            ],
            'documentation': 'In-code JSDoc documentation with usage examples',
            'last_updated': '2025-10-17'
        }
    ]
}

# Component connections/dependencies map
COMPONENT_CONNECTIONS = [
    {'from': 'frontend', 'to': 'backend', 'type': 'REST API', 'protocol': 'HTTPS'},
    {'from': 'backend', 'to': 'mongodb', 'type': 'Database', 'protocol': 'MongoDB Protocol'},
    {'from': 'backend', 'to': 'google_workspace', 'type': 'API Integration', 'protocol': 'REST/OAuth'},
    {'from': 'backend', 'to': 'email_service', 'type': 'SMTP', 'protocol': 'SMTP/TLS'},
    {'from': 'mt5_bridge', 'to': 'mt5_terminal', 'type': 'Data Sync', 'protocol': 'MetaTrader5 API'},
    {'from': 'mt5_bridge', 'to': 'mongodb', 'type': 'Database', 'protocol': 'MongoDB Protocol'},
    {'from': 'render_platform', 'to': 'frontend', 'type': 'Hosting & CDN', 'protocol': 'HTTPS'},
    {'from': 'render_platform', 'to': 'backend', 'type': 'Hosting & Load Balancing', 'protocol': 'HTTPS'},
    {'from': 'github', 'to': 'render_platform', 'type': 'Auto-Deploy', 'protocol': 'Git/HTTPS'},
    # Phase 7 additions
    {'from': 'frontend', 'to': 'trading-analytics', 'type': 'Component', 'protocol': 'React'},
    {'from': 'trading-analytics', 'to': 'backend', 'type': 'REST API', 'protocol': 'HTTPS'},
    {'from': 'trading-analytics', 'to': 'money-managers', 'type': 'Data Query', 'protocol': 'MongoDB'},
    {'from': 'trading-analytics', 'to': 'mongodb', 'type': 'Database', 'protocol': 'MongoDB Protocol'},
    {'from': 'frontend', 'to': 'ui-component-library', 'type': 'Import', 'protocol': 'ES6 Modules'},
]

def get_all_components() -> Dict[str, List[Dict[str, Any]]]:
    """Get all system components organized by category"""
    return SYSTEM_COMPONENTS

def get_component_by_id(component_id: str) -> Dict[str, Any]:
    """Get a specific component by ID"""
    for category, components in SYSTEM_COMPONENTS.items():
        for component in components:
            if component['id'] == component_id:
                return component
    return None

def get_component_count() -> int:
    """Get total number of components"""
    total = 0
    for components in SYSTEM_COMPONENTS.values():
        total += len(components)
    return total

def get_connections() -> List[Dict[str, str]]:
    """Get all component connections"""
    return COMPONENT_CONNECTIONS

# Metadata
REGISTRY_VERSION = '1.0.0'
LAST_UPDATED = datetime.now().isoformat()
TOTAL_COMPONENTS = get_component_count()
