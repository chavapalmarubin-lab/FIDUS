#!/usr/bin/env python3
"""
FIDUS System Health Monitor - Production Oversight
================================================

Real-time monitoring script for production environment.
Monitors all critical system components and sends alerts.

Usage:
    python system_health_monitor.py --config production.yml
    python system_health_monitor.py --dashboard  # Start web dashboard
"""

import asyncio
import aiohttp
import asyncpg
import logging
import time
import psutil
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse
import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@dataclass
class HealthMetrics:
    """System health metrics"""
    timestamp: str
    system_status: str
    api_response_time: float
    database_status: str
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    active_sessions: int
    rate_limiter_stats: Dict[str, Any]
    mt5_accounts_status: Dict[str, Any]
    error_count_last_hour: int
    uptime_seconds: int

@dataclass
class AlertConfig:
    """Alert configuration"""
    email_alerts: bool = True
    slack_webhook: Optional[str] = None
    sms_alerts: bool = False
    alert_threshold_cpu: float = 80.0
    alert_threshold_memory: float = 85.0
    alert_threshold_disk: float = 90.0
    alert_threshold_response_time: float = 2.0
    alert_cooldown_minutes: int = 15

class SystemHealthMonitor:
    """Production system health monitoring"""
    
    def __init__(self, config_file: str = None):
        self.config = self.load_config(config_file)
        self.base_url = self.config.get('base_url', 'https://your-domain.com')
        self.alert_config = AlertConfig(**self.config.get('alerts', {}))
        self.last_alerts = {}
        self.start_time = time.time()
        self.setup_logging()
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
            except FileNotFoundError:
                print(f"Config file {config_file} not found, using defaults")
        
        # Default configuration
        return {
            'base_url': 'https://your-production-domain.com',
            'monitoring_interval': 60,  # seconds
            'alerts': {
                'email_alerts': True,
                'alert_threshold_cpu': 80.0,
                'alert_threshold_memory': 85.0,
                'alert_threshold_disk': 90.0,
                'alert_threshold_response_time': 2.0
            },
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'alerts@yourcompany.com',
                'password': 'your-app-password',
                'recipients': ['cto@yourcompany.com', 'devops@yourcompany.com']
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/fidus/health_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def check_api_health(self) -> Dict[str, Any]:
        """Check API endpoint health and response time"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health/metrics", timeout=10) as response:
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'status': 'healthy',
                            'response_time': response_time,
                            'data': data
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'response_time': response_time,
                            'error': f'HTTP {response.status}'
                        }
        except asyncio.TimeoutError:
            return {
                'status': 'timeout',
                'response_time': 10.0,
                'error': 'API timeout after 10 seconds'
            }
        except Exception as e:
            return {
                'status': 'error',
                'response_time': 0,
                'error': str(e)
            }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            # This would connect to your actual MongoDB instance
            # For now, we'll check via the API health endpoint
            api_health = await self.check_api_health()
            
            if api_health['status'] == 'healthy':
                db_info = api_health.get('data', {}).get('database', {})
                return {
                    'status': db_info.get('status', 'unknown'),
                    'collections': db_info.get('collections', 0),
                    'data_size': db_info.get('data_size', 0),
                    'index_size': db_info.get('index_size', 0)
                }
            else:
                return {
                    'status': 'unreachable',
                    'error': 'API endpoint unavailable'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_free_gb': disk.free / (1024**3)
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'memory_available_gb': 0,
                'disk_free_gb': 0
            }
    
    async def get_mt5_status(self) -> Dict[str, Any]:
        """Check MT5 integration status"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check MT5 system status
                async with session.get(f"{self.base_url}/api/mt5/admin/system-status", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('system_status', {})
                    else:
                        return {
                            'collector_status': 'api_error',
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'collector_status': 'connection_error',
                'error': str(e)
            }
    
    async def collect_health_metrics(self) -> HealthMetrics:
        """Collect comprehensive health metrics"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Collect metrics concurrently
        api_health_task = self.check_api_health()
        db_health_task = self.check_database_health()
        mt5_status_task = self.get_mt5_status()
        
        api_health, db_health, mt5_status = await asyncio.gather(
            api_health_task, db_health_task, mt5_status_task
        )
        
        system_metrics = self.get_system_metrics()
        uptime = int(time.time() - self.start_time)
        
        # Extract rate limiter stats from API health data
        rate_limiter_stats = {}
        if api_health['status'] == 'healthy':
            rate_limiter_stats = api_health.get('data', {}).get('rate_limiter', {})
        
        # Determine overall system status
        overall_status = 'healthy'
        if (api_health['status'] != 'healthy' or 
            db_health['status'] != 'connected' or
            system_metrics['cpu_usage'] > 90 or
            system_metrics['memory_usage'] > 95):
            overall_status = 'unhealthy'
        elif (system_metrics['cpu_usage'] > 70 or
              system_metrics['memory_usage'] > 80 or
              api_health['response_time'] > 1.0):
            overall_status = 'warning'
        
        return HealthMetrics(
            timestamp=timestamp,
            system_status=overall_status,
            api_response_time=api_health.get('response_time', 0),
            database_status=db_health.get('status', 'unknown'),
            memory_usage=system_metrics['memory_usage'],
            cpu_usage=system_metrics['cpu_usage'],
            disk_usage=system_metrics['disk_usage'],
            active_sessions=rate_limiter_stats.get('active_clients', 0),
            rate_limiter_stats=rate_limiter_stats,
            mt5_accounts_status=mt5_status,
            error_count_last_hour=0,  # Would need to implement error counting
            uptime_seconds=uptime
        )
    
    def should_send_alert(self, alert_type: str) -> bool:
        """Check if alert should be sent (cooldown logic)"""
        now = time.time()
        last_alert = self.last_alerts.get(alert_type, 0)
        cooldown = self.alert_config.alert_cooldown_minutes * 60
        
        if now - last_alert > cooldown:
            self.last_alerts[alert_type] = now
            return True
        return False
    
    async def send_email_alert(self, subject: str, message: str):
        """Send email alert"""
        if not self.alert_config.email_alerts:
            return
            
        try:
            email_config = self.config.get('email', {})
            
            msg = MIMEMultipart()
            msg['From'] = email_config.get('username', 'alerts@fidus.com')
            msg['Subject'] = f"[FIDUS ALERT] {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(email_config.get('smtp_server', 'smtp.gmail.com'), 
                                email_config.get('smtp_port', 587))
            server.starttls()
            server.login(email_config.get('username'), email_config.get('password'))
            
            recipients = email_config.get('recipients', [])
            for recipient in recipients:
                msg['To'] = recipient
                text = msg.as_string()
                server.sendmail(msg['From'], recipient, text)
            
            server.quit()
            self.logger.info(f"Alert email sent: {subject}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    async def check_and_send_alerts(self, metrics: HealthMetrics):
        """Check metrics and send alerts if needed"""
        alerts_sent = []
        
        # CPU usage alert
        if (metrics.cpu_usage > self.alert_config.alert_threshold_cpu and 
            self.should_send_alert('high_cpu')):
            await self.send_email_alert(
                "High CPU Usage",
                f"CPU usage is {metrics.cpu_usage:.1f}% (threshold: {self.alert_config.alert_threshold_cpu}%)"
            )
            alerts_sent.append('high_cpu')
        
        # Memory usage alert
        if (metrics.memory_usage > self.alert_config.alert_threshold_memory and
            self.should_send_alert('high_memory')):
            await self.send_email_alert(
                "High Memory Usage",
                f"Memory usage is {metrics.memory_usage:.1f}% (threshold: {self.alert_config.alert_threshold_memory}%)"
            )
            alerts_sent.append('high_memory')
        
        # Disk usage alert
        if (metrics.disk_usage > self.alert_config.alert_threshold_disk and
            self.should_send_alert('high_disk')):
            await self.send_email_alert(
                "High Disk Usage",
                f"Disk usage is {metrics.disk_usage:.1f}% (threshold: {self.alert_config.alert_threshold_disk}%)"
            )
            alerts_sent.append('high_disk')
        
        # API response time alert
        if (metrics.api_response_time > self.alert_config.alert_threshold_response_time and
            self.should_send_alert('slow_api')):
            await self.send_email_alert(
                "Slow API Response",
                f"API response time is {metrics.api_response_time:.2f}s (threshold: {self.alert_config.alert_threshold_response_time}s)"
            )
            alerts_sent.append('slow_api')
        
        # System unhealthy alert
        if (metrics.system_status == 'unhealthy' and
            self.should_send_alert('system_unhealthy')):
            await self.send_email_alert(
                "System Unhealthy",
                f"System status: {metrics.system_status}\n"
                f"Database: {metrics.database_status}\n"
                f"API Response Time: {metrics.api_response_time:.2f}s\n"
                f"CPU: {metrics.cpu_usage:.1f}%\n"
                f"Memory: {metrics.memory_usage:.1f}%"
            )
            alerts_sent.append('system_unhealthy')
        
        if alerts_sent:
            self.logger.warning(f"Alerts sent: {', '.join(alerts_sent)}")
    
    def format_metrics_report(self, metrics: HealthMetrics) -> str:
        """Format metrics for console output"""
        uptime_hours = metrics.uptime_seconds / 3600
        
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'unhealthy': '❌'
        }
        
        return f"""
{'='*60}
FIDUS SYSTEM HEALTH REPORT
{'='*60}
Timestamp: {metrics.timestamp}
Status: {status_emoji.get(metrics.system_status, '❓')} {metrics.system_status.upper()}
Uptime: {uptime_hours:.1f} hours

PERFORMANCE METRICS:
- API Response Time: {metrics.api_response_time:.3f}s
- CPU Usage: {metrics.cpu_usage:.1f}%
- Memory Usage: {metrics.memory_usage:.1f}%
- Disk Usage: {metrics.disk_usage:.1f}%

DATABASE:
- Status: {metrics.database_status}

RATE LIMITER:
- Active Clients: {metrics.active_sessions}
- Total Requests: {metrics.rate_limiter_stats.get('total_requests', 0)}
- Blocked Requests: {metrics.rate_limiter_stats.get('blocked_requests', 0)}

MT5 INTEGRATION:
- Collector Status: {metrics.mt5_accounts_status.get('collector_status', 'unknown')}
- Accounts Monitored: {metrics.mt5_accounts_status.get('accounts_monitored', 0)}
- Data Quality: {metrics.mt5_accounts_status.get('data_quality', 'unknown')}
{'='*60}
        """
    
    async def run_monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting FIDUS system health monitoring...")
        
        interval = self.config.get('monitoring_interval', 60)
        
        while True:
            try:
                # Collect health metrics
                metrics = await self.collect_health_metrics()
                
                # Log metrics
                self.logger.info(f"System Status: {metrics.system_status}, "
                               f"API: {metrics.api_response_time:.3f}s, "
                               f"CPU: {metrics.cpu_usage:.1f}%, "
                               f"Mem: {metrics.memory_usage:.1f}%")
                
                # Check for alerts
                await self.check_and_send_alerts(metrics)
                
                # Save metrics to file for historical analysis
                with open('/var/log/fidus/health_metrics.jsonl', 'a') as f:
                    f.write(json.dumps(asdict(metrics)) + '\n')
                
                # Print report if in verbose mode
                if self.config.get('verbose', False):
                    print(self.format_metrics_report(metrics))
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
            
            # Wait for next iteration
            await asyncio.sleep(interval)

def create_sample_config():
    """Create sample configuration file"""
    config = {
        'base_url': 'https://your-production-domain.com',
        'monitoring_interval': 60,
        'verbose': False,
        'alerts': {
            'email_alerts': True,
            'alert_threshold_cpu': 80.0,
            'alert_threshold_memory': 85.0,
            'alert_threshold_disk': 90.0,
            'alert_threshold_response_time': 2.0,
            'alert_cooldown_minutes': 15
        },
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'alerts@yourcompany.com',
            'password': 'your-app-password',
            'recipients': [
                'cto@yourcompany.com',
                'devops@yourcompany.com'
            ]
        }
    }
    
    with open('monitoring_config.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("Sample configuration created: monitoring_config.yml")
    print("Please update with your actual settings before running.")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='FIDUS System Health Monitor')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--create-config', action='store_true', help='Create sample configuration file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    # Initialize monitor
    monitor = SystemHealthMonitor(args.config)
    
    if args.verbose:
        monitor.config['verbose'] = True
    
    try:
        await monitor.run_monitoring_loop()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Monitoring error: {e}")

if __name__ == "__main__":
    asyncio.run(main())