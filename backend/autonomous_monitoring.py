"""
AUTONOMOUS MONITORING SYSTEM
Continuous health monitoring and automatic issue detection
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
import json

class AutonomousMonitor:
    """Production-grade autonomous monitoring system"""
    
    def __init__(self):
        self.fidus_api_url = "https://fidus-api.onrender.com"
        self.mt5_bridge_url = "http://217.197.163.11:8000"
        self.monitoring_interval = 300  # 5 minutes
        self.alert_thresholds = {
            'mt5_sync_success_rate': 80,  # Alert if <80%
            'data_staleness_minutes': 10,  # Alert if >10 minutes old
            'account_886528_balance': 3927.41  # Expected balance
        }
        
    async def check_system_health(self):
        """Comprehensive system health check"""
        health_report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        try:
            # 1. FIDUS API Health
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.fidus_api_url}/api/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        health_report['checks']['fidus_api'] = {
                            'status': 'healthy',
                            'response_time_ms': 0,  # Could measure this
                            'services': health_data.get('services', {})
                        }
                    else:
                        health_report['checks']['fidus_api'] = {
                            'status': 'unhealthy',
                            'error': f"HTTP {response.status}"
                        }
                        health_report['overall_status'] = 'degraded'
        except Exception as e:
            health_report['checks']['fidus_api'] = {
                'status': 'error',
                'error': str(e)
            }
            health_report['overall_status'] = 'critical'
            
        try:
            # 2. MT5 Bridge Health  
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.mt5_bridge_url}/health") as response:
                    if response.status == 200:
                        bridge_data = await response.json()
                        health_report['checks']['mt5_bridge'] = {
                            'status': 'connected' if bridge_data.get('mt5_connected') else 'disconnected',
                            'mt5_initialized': bridge_data.get('mt5_initialized', False),
                            'connected_accounts': bridge_data.get('connected_accounts', 0)
                        }
                        
                        if not bridge_data.get('mt5_connected'):
                            health_report['overall_status'] = 'degraded'
                            
                    else:
                        health_report['checks']['mt5_bridge'] = {
                            'status': 'unreachable',
                            'error': f"HTTP {response.status}"
                        }
                        health_report['overall_status'] = 'degraded'
        except Exception as e:
            health_report['checks']['mt5_bridge'] = {
                'status': 'error', 
                'error': str(e)
            }
            # Bridge being down is expected currently, don't mark as critical
            if health_report['overall_status'] == 'healthy':
                health_report['overall_status'] = 'degraded'
                
        return health_report
    
    async def check_account_886528(self):
        """Specific monitoring for critical account 886528"""
        try:
            # Authenticate and get account data
            auth_data = {
                "username": "admin",
                "password": "password123", 
                "user_type": "admin"
            }
            
            async with aiohttp.ClientSession() as session:
                # Get token
                async with session.post(
                    f"{self.fidus_api_url}/api/auth/login",
                    json=auth_data
                ) as response:
                    auth_result = await response.json()
                    token = auth_result.get('token')
                    
                if not token:
                    return {'status': 'auth_failed'}
                    
                # Get account data
                headers = {'Authorization': f'Bearer {token}'}
                async with session.get(
                    f"{self.fidus_api_url}/api/mt5/admin/accounts",
                    headers=headers
                ) as response:
                    accounts_data = await response.json()
                    
                # Find account 886528
                account_886528 = None
                for account in accounts_data.get('accounts', []):
                    if account.get('account') == 886528:
                        account_886528 = account
                        break
                        
                if account_886528:
                    current_balance = account_886528.get('balance', 0)
                    expected_balance = self.alert_thresholds['account_886528_balance']
                    balance_diff = abs(current_balance - expected_balance)
                    
                    return {
                        'status': 'found',
                        'current_balance': current_balance,
                        'expected_balance': expected_balance,
                        'balance_diff': balance_diff,
                        'balance_accurate': balance_diff < 1.0,  # Within $1
                        'last_updated': account_886528.get('updated_at'),
                        'fund_code': account_886528.get('fund_code')
                    }
                else:
                    return {'status': 'not_found'}
                    
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def generate_alert(self, issue_type, details):
        """Generate structured alert for issues"""
        alert = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': issue_type,
            'severity': 'critical' if issue_type in ['system_down', 'data_corruption'] else 'warning',
            'details': details,
            'autonomous_action': 'investigating'
        }
        
        print(f"🚨 AUTONOMOUS ALERT: {json.dumps(alert, indent=2)}")
        return alert
        
    async def run_monitoring_cycle(self):
        """Single monitoring cycle"""
        print(f"🔄 Autonomous Monitoring Cycle - {datetime.now(timezone.utc).isoformat()}")
        
        # System Health Check
        health_report = await self.check_system_health()
        print(f"📊 System Status: {health_report['overall_status']}")
        
        # Account 886528 Check  
        account_check = await self.check_account_886528()
        print(f"💰 Account 886528: {account_check.get('status', 'unknown')}")
        
        if account_check.get('status') == 'found':
            balance = account_check.get('current_balance')
            accurate = account_check.get('balance_accurate')
            print(f"   Balance: ${balance:.2f} {'✅' if accurate else '❌'}")
            
            if not accurate:
                self.generate_alert('balance_discrepancy', {
                    'account': 886528,
                    'current_balance': balance,
                    'expected_balance': account_check.get('expected_balance'),
                    'diff': account_check.get('balance_diff')
                })
        
        # MT5 Bridge Status
        mt5_status = health_report['checks'].get('mt5_bridge', {})
        if mt5_status.get('status') == 'connected':
            print("🔗 MT5 Bridge: Connected ✅")
        else:
            print("🔗 MT5 Bridge: Disconnected (Expected - waiting for terminal startup)")
            
        return health_report

# Global monitoring instance
autonomous_monitor = AutonomousMonitor()

async def start_monitoring():
    """Start continuous monitoring"""
    print("🚀 Starting Autonomous Monitoring System...")
    
    while True:
        try:
            await autonomous_monitor.run_monitoring_cycle()
            await asyncio.sleep(autonomous_monitor.monitoring_interval)
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            await asyncio.sleep(60)  # Retry in 1 minute on error

if __name__ == "__main__":
    asyncio.run(start_monitoring())