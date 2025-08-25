"""
Notification Plugin for Building Energy Optimizer.
Supports Email, Slack, Telegram, and Webhook notifications.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from .base import NotificationPlugin

logger = logging.getLogger(__name__)

class EmailNotificationPlugin(NotificationPlugin):
    """Email notification plugin."""
    
    @property
    def name(self) -> str:
        return "Email Notifications"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Send notifications via email (SMTP)"
    
    @property
    def dependencies(self) -> List[str]:
        return []  # Uses built-in smtplib
    
    def __init__(self):
        self.smtp_config = {}
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize email configuration."""
        self.smtp_config = {
            'server': config.get('smtp_server', 'smtp.gmail.com'),
            'port': config.get('smtp_port', 587),
            'username': config.get('smtp_username'),
            'password': config.get('smtp_password'),
            'use_tls': config.get('smtp_use_tls', True),
            'from_email': config.get('from_email'),
            'from_name': config.get('from_name', 'Building Energy Optimizer')
        }
        
        if not self.smtp_config['username'] or not self.smtp_config['password']:
            logger.warning("Email credentials not provided - email notifications disabled")
            return False
        
        # Test connection
        try:
            self._test_connection()
            logger.info("Email notification plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize email plugin: {e}")
            return False
    
    def _test_connection(self):
        """Test SMTP connection."""
        server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
        if self.smtp_config['use_tls']:
            server.starttls()
        server.login(self.smtp_config['username'], self.smtp_config['password'])
        server.quit()
    
    def send_notification(self, message: str, priority: str = "medium", 
                         recipients: Optional[List[str]] = None, 
                         subject: Optional[str] = None) -> bool:
        """Send email notification."""
        if not recipients:
            recipients = [self.smtp_config['username']]  # Send to self if no recipients
        
        if not subject:
            subject = f"Energy Optimizer Alert - {priority.title()} Priority"
        
        try:
            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.smtp_config['from_name']} <{self.smtp_config['from_email'] or self.smtp_config['username']}>"
            msg['To'] = ', '.join(recipients)
            
            # Create HTML and text versions
            text_body = self._create_text_email(message, priority)
            html_body = self._create_html_email(message, priority)
            
            # Attach parts
            msg.attach(MimeText(text_body, 'plain'))
            msg.attach(MimeText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            if self.smtp_config['use_tls']:
                server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.smtp_config['username'], recipients, text)
            server.quit()
            
            logger.info(f"Email notification sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _create_text_email(self, message: str, priority: str) -> str:
        """Create plain text email."""
        return f"""
Building Energy Optimizer Notification
Priority: {priority.title()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{message}

---
Building Energy Optimizer v2.0
"""
    
    def _create_html_email(self, message: str, priority: str) -> str:
        """Create HTML email."""
        priority_colors = {
            'low': '#28a745',
            'medium': '#ffc107', 
            'high': '#dc3545'
        }
        
        color = priority_colors.get(priority, '#6c757d')
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Energy Optimizer Notification</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto;">
        <div style="background-color: {color}; color: white; padding: 15px; border-radius: 5px 5px 0 0;">
            <h2 style="margin: 0;">🏢 Building Energy Optimizer</h2>
            <p style="margin: 5px 0 0 0;">Priority: {priority.title()}</p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #dee2e6;">
            <div style="background-color: white; padding: 15px; border-radius: 5px; border-left: 4px solid {color};">
                {message.replace(chr(10), '<br>')}
            </div>
            
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px;">
                <p>Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Building Energy Optimizer v2.0</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email notification."""
        message = data.get('message', 'No message provided')
        priority = data.get('priority', 'medium')
        recipients = data.get('recipients')
        subject = data.get('subject')
        
        success = self.send_notification(message, priority, recipients, subject)
        return {'success': success, 'notification_type': 'email'}

class SlackNotificationPlugin(NotificationPlugin):
    """Slack notification plugin."""
    
    @property
    def name(self) -> str:
        return "Slack Notifications"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Send notifications to Slack channels"
    
    @property
    def dependencies(self) -> List[str]:
        return ["requests"]
    
    def __init__(self):
        self.webhook_url = None
        self.channel = None
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Slack configuration."""
        if not HAS_REQUESTS:
            logger.error("requests library not available")
            return False
        
        self.webhook_url = config.get('slack_webhook_url')
        self.channel = config.get('slack_channel', '#energy-alerts')
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not provided")
            return False
        
        # Test webhook
        try:
            self._test_webhook()
            logger.info("Slack notification plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Slack plugin: {e}")
            return False
    
    def _test_webhook(self):
        """Test Slack webhook."""
        test_payload = {
            'text': 'Building Energy Optimizer notification test',
            'channel': self.channel,
            'username': 'Energy Optimizer',
            'icon_emoji': ':zap:'
        }
        
        response = requests.post(self.webhook_url, json=test_payload, timeout=10)
        response.raise_for_status()
    
    def send_notification(self, message: str, priority: str = "medium", 
                         channel: Optional[str] = None) -> bool:
        """Send Slack notification."""
        if not self.webhook_url:
            return False
        
        # Priority colors and emojis
        priority_config = {
            'low': {'color': 'good', 'emoji': ':information_source:'},
            'medium': {'color': 'warning', 'emoji': ':warning:'},
            'high': {'color': 'danger', 'emoji': ':rotating_light:'}
        }
        
        config = priority_config.get(priority, priority_config['medium'])
        
        # Create Slack message
        payload = {
            'channel': channel or self.channel,
            'username': 'Energy Optimizer',
            'icon_emoji': ':zap:',
            'attachments': [{
                'color': config['color'],
                'title': f"{config['emoji']} Energy Optimization Alert",
                'text': message,
                'footer': 'Building Energy Optimizer v2.0',
                'ts': int(datetime.now().timestamp()),
                'fields': [
                    {
                        'title': 'Priority',
                        'value': priority.title(),
                        'short': True
                    },
                    {
                        'title': 'Time',
                        'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'short': True
                    }
                ]
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent to {channel or self.channel}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack notification."""
        message = data.get('message', 'No message provided')
        priority = data.get('priority', 'medium')
        channel = data.get('channel')
        
        success = self.send_notification(message, priority, channel)
        return {'success': success, 'notification_type': 'slack'}

class WebhookNotificationPlugin(NotificationPlugin):
    """Generic webhook notification plugin."""
    
    @property
    def name(self) -> str:
        return "Webhook Notifications"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Send notifications via HTTP webhooks"
    
    @property
    def dependencies(self) -> List[str]:
        return ["requests"]
    
    def __init__(self):
        self.webhook_urls = []
        self.headers = {}
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize webhook configuration."""
        if not HAS_REQUESTS:
            logger.error("requests library not available")
            return False
        
        self.webhook_urls = config.get('webhook_urls', [])
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        
        if not self.webhook_urls:
            logger.warning("No webhook URLs configured")
            return False
        
        logger.info(f"Webhook plugin initialized with {len(self.webhook_urls)} URLs")
        return True
    
    def send_notification(self, message: str, priority: str = "medium") -> bool:
        """Send webhook notification."""
        payload = {
            'message': message,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'source': 'building_energy_optimizer',
            'version': '2.0.0'
        }
        
        success_count = 0
        
        for webhook_url in self.webhook_urls:
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    logger.debug(f"Webhook notification sent to {webhook_url}")
                else:
                    logger.warning(f"Webhook {webhook_url} returned status {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Failed to send webhook to {webhook_url}: {e}")
        
        total_webhooks = len(self.webhook_urls)
        logger.info(f"Webhook notifications: {success_count}/{total_webhooks} successful")
        
        return success_count > 0
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute webhook notification."""
        message = data.get('message', 'No message provided')
        priority = data.get('priority', 'medium')
        
        success = self.send_notification(message, priority)
        return {'success': success, 'notification_type': 'webhook'}

class NotificationManager:
    """Manages multiple notification channels."""
    
    def __init__(self):
        self.plugins: Dict[str, NotificationPlugin] = {}
        self.config = {}
        
    def add_plugin(self, name: str, plugin: NotificationPlugin, config: Dict[str, Any]) -> bool:
        """Add a notification plugin."""
        try:
            if plugin.initialize(config):
                self.plugins[name] = plugin
                self.config[name] = config
                logger.info(f"Notification plugin {name} added successfully")
                return True
            else:
                logger.error(f"Failed to initialize notification plugin {name}")
                return False
        except Exception as e:
            logger.error(f"Error adding notification plugin {name}: {e}")
            return False
    
    def send_to_all(self, message: str, priority: str = "medium") -> Dict[str, bool]:
        """Send notification to all configured channels."""
        results = {}
        
        for name, plugin in self.plugins.items():
            try:
                success = plugin.send_notification(message, priority)
                results[name] = success
            except Exception as e:
                logger.error(f"Notification plugin {name} failed: {e}")
                results[name] = False
        
        return results
    
    def send_to_channel(self, channel: str, message: str, priority: str = "medium") -> bool:
        """Send notification to specific channel."""
        if channel not in self.plugins:
            logger.error(f"Notification channel {channel} not found")
            return False
        
        try:
            return self.plugins[channel].send_notification(message, priority)
        except Exception as e:
            logger.error(f"Failed to send notification via {channel}: {e}")
            return False
    
    def send_optimization_alert(self, building_name: str, savings_percent: float, 
                              cost_savings: float, suggestions_count: int) -> Dict[str, bool]:
        """Send optimization completion alert."""
        message = f"""
🏢 Energy Optimization Complete - {building_name}

💰 Potential Savings: {savings_percent:.1f}% (€{cost_savings:.2f})
💡 Optimization Suggestions: {suggestions_count}
📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

The building energy analysis has identified significant optimization opportunities.
Review the detailed suggestions to implement energy-saving measures.
"""
        
        priority = "high" if savings_percent > 20 else "medium" if savings_percent > 10 else "low"
        return self.send_to_all(message, priority)
    
    def send_system_alert(self, alert_type: str, details: str) -> Dict[str, bool]:
        """Send system alert."""
        message = f"""
🚨 System Alert - {alert_type}

Details: {details}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check the system logs for more information.
"""
        
        return self.send_to_all(message, "high")
    
    def send_daily_summary(self, summary_data: Dict[str, Any]) -> Dict[str, bool]:
        """Send daily summary notification."""
        message = f"""
📊 Daily Energy Summary

🏢 Buildings Analyzed: {summary_data.get('buildings_count', 0)}
⚡ Total Consumption: {summary_data.get('total_consumption', 0):.1f} kWh
💰 Potential Savings: €{summary_data.get('potential_savings', 0):.2f}
🎯 Optimization Runs: {summary_data.get('optimization_count', 0)}

Top Performing Building: {summary_data.get('top_building', 'N/A')}
Avg Savings Opportunity: {summary_data.get('avg_savings_percent', 0):.1f}%
"""
        
        return self.send_to_all(message, "low")
    
    def list_channels(self) -> List[str]:
        """List available notification channels."""
        return list(self.plugins.keys())
    
    def get_channel_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all notification channels."""
        status = {}
        
        for name, plugin in self.plugins.items():
            status[name] = {
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description,
                'category': plugin.category,
                'enabled': True  # If loaded, it's enabled
            }
        
        return status

# Notification decorators
def notify_on_completion(notification_manager: NotificationManager, 
                        message_template: str = "Task completed: {func_name}"):
    """Decorator to send notification when function completes."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Send success notification
                message = message_template.format(
                    func_name=func.__name__,
                    result=result
                )
                notification_manager.send_to_all(message, "low")
                
                return result
                
            except Exception as e:
                # Send error notification
                error_message = f"Task failed: {func.__name__}\nError: {str(e)}"
                notification_manager.send_to_all(error_message, "high")
                raise
        
        return wrapper
    return decorator

def notify_on_threshold(notification_manager: NotificationManager, 
                       threshold_field: str, threshold_value: float,
                       comparison: str = "greater"):
    """Decorator to send notification when threshold is exceeded."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Check threshold
            if isinstance(result, dict) and threshold_field in result:
                value = result[threshold_field]
                
                triggered = False
                if comparison == "greater" and value > threshold_value:
                    triggered = True
                elif comparison == "less" and value < threshold_value:
                    triggered = True
                elif comparison == "equal" and value == threshold_value:
                    triggered = True
                
                if triggered:
                    message = f"""
🚨 Threshold Alert: {threshold_field}

Current Value: {value}
Threshold: {threshold_value} ({comparison})
Function: {func.__name__}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    notification_manager.send_to_all(message, "medium")
            
            return result
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test notification system
    print("📢 Testing notification system...")
    
    # Create notification manager
    manager = NotificationManager()
    
    # Test email plugin (with dummy config)
    email_plugin = EmailNotificationPlugin()
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': 'test@example.com',
        'smtp_password': 'test_password',
        'from_email': 'test@example.com'
    }
    
    # Test webhook plugin
    webhook_plugin = WebhookNotificationPlugin()
    webhook_config = {
        'webhook_urls': ['https://httpbin.org/post'],  # Test webhook
        'headers': {'Content-Type': 'application/json'}
    }
    
    # Add plugins (will fail due to dummy config, but tests structure)
    manager.add_plugin('email', email_plugin, email_config)
    manager.add_plugin('webhook', webhook_plugin, webhook_config)
    
    # Test notifications
    print("📧 Testing notification channels...")
    channels = manager.list_channels()
    print(f"Available channels: {channels}")
    
    status = manager.get_channel_status()
    print(f"Channel status: {status}")
    
    print("📢 Notification system test complete!")
