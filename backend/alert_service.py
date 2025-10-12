"""
Alert and Notification Service
Phase 5: Real-time System Health Dashboard
Handles automated alerts via email and in-app notifications
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Literal, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing system alerts and notifications"""
    
    def __init__(self, db):
        self.db = db
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_APP_PASSWORD", "")
        self.admin_email = os.getenv("ALERT_RECIPIENT_EMAIL", "chavapalmarubin@gmail.com")
        self.frontend_url = os.getenv("FRONTEND_URL", "https://fidus-investment-platform.onrender.com")
    
    async def trigger_alert(
        self,
        component: str,
        component_name: str,
        severity: Literal["critical", "warning", "info"],
        status: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Main alert triggering function
        
        Args:
            component: Component ID (e.g., 'frontend', 'backend')
            component_name: Human-readable name (e.g., 'FIDUS Frontend')
            severity: Alert severity level
            status: Current status (e.g., 'OFFLINE', 'DEGRADED', 'ONLINE')
            message: Alert message
            details: Additional details dictionary
        
        Returns:
            Alert ID
        """
        try:
            # 1. Store alert in database
            alert_id = await self.store_alert(
                component, component_name, severity, status, message, details
            )
            
            # 2. Send notifications based on severity
            if severity == "critical":
                # Critical: Email + In-app notification
                await self.send_email_alert(component_name, status, message, details, "CRITICAL")
                await self.send_in_app_notification(alert_id, component, component_name, severity, message)
                logger.critical(f"🚨 CRITICAL ALERT: {component_name} - {message}")
                
            elif severity == "warning":
                # Warning: Email + In-app notification
                await self.send_email_alert(component_name, status, message, details, "WARNING")
                await self.send_in_app_notification(alert_id, component, component_name, severity, message)
                logger.warning(f"⚠️ WARNING ALERT: {component_name} - {message}")
                
            elif severity == "info":
                # Info: In-app notification only
                await self.send_in_app_notification(alert_id, component, component_name, severity, message)
                logger.info(f"ℹ️ INFO ALERT: {component_name} - {message}")
            
            return alert_id
            
        except Exception as e:
            logger.error(f"❌ Error triggering alert for {component}: {str(e)}")
            raise
    
    async def store_alert(
        self,
        component: str,
        component_name: str,
        severity: str,
        status: str,
        message: str,
        details: Optional[Dict[str, Any]]
    ) -> str:
        """Store alert in MongoDB"""
        try:
            alert = {
                "component": component,
                "component_name": component_name,
                "severity": severity,
                "status": status,
                "message": message,
                "details": details or {},
                "timestamp": datetime.now(timezone.utc),
                "acknowledged": False,
                "acknowledged_at": None,
                "acknowledged_by": None,
                "resolved": False,
                "resolved_at": None,
                "created_at": datetime.now(timezone.utc)
            }
            
            result = await self.db.system_alerts.insert_one(alert)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Error storing alert: {str(e)}")
            raise
    
    async def send_email_alert(
        self,
        component_name: str,
        status: str,
        message: str,
        details: Optional[Dict[str, Any]],
        priority: str
    ) -> None:
        """Send email notification"""
        
        # Skip if SMTP not configured
        if not self.smtp_username or not self.smtp_password:
            logger.warning("⚠️ SMTP not configured, skipping email alert")
            return
        
        try:
            # Determine emoji and priority
            if priority == "CRITICAL":
                emoji = "🚨"
                color = "red"
            else:
                emoji = "⚠️"
                color = "orange"
            
            subject = f"{emoji} {priority}: {component_name} - FIDUS Platform"
            
            # Format details
            details_text = self._format_details(details) if details else "No additional details"
            
            # Create HTML email body
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: {color}; color: white; padding: 20px; border-radius: 5px; }}
                    .content {{ padding: 20px; background: #f9f9f9; border-radius: 5px; margin: 20px 0; }}
                    .details {{ background: white; padding: 15px; border-left: 4px solid {color}; margin: 10px 0; }}
                    .button {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                    .footer {{ color: #666; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{emoji} {priority} ALERT</h1>
                    <h2>{component_name}</h2>
                </div>
                
                <div class="content">
                    <p><strong>Status:</strong> {status}</p>
                    <p><strong>Time:</strong> {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                    <p><strong>Message:</strong> {message}</p>
                    
                    <div class="details">
                        <h3>Details:</h3>
                        <pre>{details_text}</pre>
                    </div>
                    
                    <p style="margin-top: 20px;">
                        <a href="{self.frontend_url}/admin" class="button">View System Health Dashboard →</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated alert from FIDUS Health Monitoring System.</p>
                    <p>To manage alert preferences, visit: <a href="{self.frontend_url}/admin/settings">{self.frontend_url}/admin/settings</a></p>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_body = f"""
{emoji} {priority} ALERT

Component: {component_name}
Status: {status}
Time: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}

Message: {message}

Details:
{details_text}

View System Health Dashboard:
{self.frontend_url}/admin

This is an automated alert from FIDUS Health Monitoring System.
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_username
            msg['To'] = self.admin_email
            msg['Subject'] = subject
            
            # Attach both plain text and HTML versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email alert sent to {self.admin_email} for {component_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {str(e)}")
            # Don't raise - we don't want email failures to break health checks
    
    async def send_in_app_notification(
        self,
        alert_id: str,
        component: str,
        component_name: str,
        severity: str,
        message: str
    ) -> None:
        """Store in-app notification in database"""
        try:
            notification = {
                "alert_id": alert_id,
                "component": component,
                "component_name": component_name,
                "severity": severity,
                "message": message,
                "timestamp": datetime.now(timezone.utc),
                "read": False,
                "read_at": None,
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.db.notifications.insert_one(notification)
            logger.info(f"✅ In-app notification created for {component_name}")
            
        except Exception as e:
            logger.error(f"❌ Error creating in-app notification: {str(e)}")
    
    def _format_details(self, details: Optional[Dict[str, Any]]) -> str:
        """Format details dictionary for display"""
        if not details:
            return "No additional details"
        
        formatted = ""
        for key, value in details.items():
            formatted += f"  • {key.replace('_', ' ').title()}: {value}\n"
        return formatted.strip()
    
    async def get_previous_status(self, component: str) -> Optional[str]:
        """Get the most recent status for a component from health history"""
        try:
            # Get the most recent health check for this component
            recent_check = await self.db.system_health_history.find_one(
                {},
                sort=[("timestamp", -1)]
            )
            
            if recent_check and "components" in recent_check:
                for comp in recent_check["components"]:
                    if comp.get("component") == component:
                        return comp.get("status")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting previous status for {component}: {str(e)}")
            return None
    
    async def check_and_alert(
        self,
        component: str,
        component_name: str,
        current_status: str,
        current_data: Dict[str, Any]
    ) -> None:
        """Check component status and trigger alerts if needed"""
        try:
            # Get previous status
            previous_status = await self.get_previous_status(component)
            
            # Skip if this is the first check
            if previous_status is None:
                logger.info(f"ℹ️ First health check for {component}, no alert triggered")
                return
            
            # Status changed from healthy to degraded/offline
            if previous_status == "healthy" and current_status in ["degraded", "slow", "offline", "timeout", "error"]:
                
                if current_status in ["offline", "timeout", "error"]:
                    # CRITICAL ALERT
                    await self.trigger_alert(
                        component=component,
                        component_name=component_name,
                        severity="critical",
                        status="OFFLINE",
                        message=f"{component_name} has gone offline and is not responding",
                        details={
                            "previous_status": previous_status,
                            "current_status": current_status,
                            "error": current_data.get("error", "No response"),
                            "response_time": current_data.get("response_time", "N/A"),
                            "url": current_data.get("url", "N/A")
                        }
                    )
                    
                elif current_status in ["degraded", "slow"]:
                    # WARNING ALERT
                    await self.trigger_alert(
                        component=component,
                        component_name=component_name,
                        severity="warning",
                        status="DEGRADED",
                        message=f"{component_name} is experiencing performance issues",
                        details={
                            "previous_status": previous_status,
                            "current_status": current_status,
                            "response_time": f"{current_data.get('response_time', 'N/A')}ms",
                            "threshold": "1000ms",
                            "message": current_data.get("message", "Slow response")
                        }
                    )
            
            # Status changed from offline/error to healthy (recovery)
            elif previous_status in ["offline", "timeout", "error", "degraded", "slow"] and current_status == "healthy":
                # INFO ALERT - System recovered
                await self.trigger_alert(
                    component=component,
                    component_name=component_name,
                    severity="info",
                    status="ONLINE",
                    message=f"{component_name} has recovered and is now healthy",
                    details={
                        "previous_status": previous_status,
                        "current_status": current_status,
                        "response_time": f"{current_data.get('response_time', 'N/A')}ms"
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ Error checking alerts for {component}: {str(e)}")
            # Don't raise - we don't want alert failures to break health checks
