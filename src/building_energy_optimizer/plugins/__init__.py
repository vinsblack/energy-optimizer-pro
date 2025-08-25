"""
Plugin system for Building Energy Optimizer.
Extensible architecture for adding custom functionality.
"""
from .base import (
    PluginBase,
    PluginInfo,
    DataProcessorPlugin,
    NotificationPlugin,
    AnalyticsPlugin,
    IoTPlugin,
    PluginManager,
    get_plugin_manager
)

from .notifications import (
    EmailNotificationPlugin,
    SlackNotificationPlugin,
    WebhookNotificationPlugin,
    NotificationManager,
    notify_on_completion,
    notify_on_threshold
)

from .iot_integration import (
    MQTTIoTPlugin,
    LoRaWANPlugin,
    SimulatedIoTPlugin,
    IoTDataConverter
)

from .advanced_analytics import (
    AdvancedAnalyticsPlugin,
    ClusteringPlugin
)

# Initialize global plugin manager and load default plugins
def initialize_default_plugins(config: dict = None) -> PluginManager:
    """Initialize plugin system with default plugins."""
    if config is None:
        config = {}
    
    manager = get_plugin_manager()
    
    # Load default plugins
    default_plugins = [
        ('simulated_iot', SimulatedIoTPlugin(), config.get('iot', {})),
        ('advanced_analytics', AdvancedAnalyticsPlugin(), config.get('analytics', {})),
        ('clustering', ClusteringPlugin(), config.get('clustering', {})),
    ]
    
    # Add optional plugins based on configuration
    if config.get('notifications', {}).get('email'):
        default_plugins.append(
            ('email_notifications', EmailNotificationPlugin(), config['notifications']['email'])
        )
    
    if config.get('notifications', {}).get('slack'):
        default_plugins.append(
            ('slack_notifications', SlackNotificationPlugin(), config['notifications']['slack'])
        )
    
    if config.get('notifications', {}).get('webhook'):
        default_plugins.append(
            ('webhook_notifications', WebhookNotificationPlugin(), config['notifications']['webhook'])
        )
    
    if config.get('iot', {}).get('mqtt'):
        default_plugins.append(
            ('mqtt_iot', MQTTIoTPlugin(), config['iot']['mqtt'])
        )
    
    if config.get('iot', {}).get('lorawan'):
        default_plugins.append(
            ('lorawan_iot', LoRaWANPlugin(), config['iot']['lorawan'])
        )
    
    # Load plugins
    loaded_count = 0
    for name, plugin, plugin_config in default_plugins:
        try:
            if plugin.initialize(plugin_config):
                manager.plugins[name] = plugin
                loaded_count += 1
                print(f"✅ Loaded plugin: {name}")
            else:
                print(f"⚠️ Failed to load plugin: {name}")
        except Exception as e:
            print(f"❌ Error loading plugin {name}: {e}")
    
    print(f"🧩 Plugin system initialized with {loaded_count} plugins")
    return manager

__all__ = [
    # Base classes
    'PluginBase',
    'PluginInfo', 
    'DataProcessorPlugin',
    'NotificationPlugin',
    'AnalyticsPlugin',
    'IoTPlugin',
    'PluginManager',
    'get_plugin_manager',
    
    # Notification plugins
    'EmailNotificationPlugin',
    'SlackNotificationPlugin', 
    'WebhookNotificationPlugin',
    'NotificationManager',
    'notify_on_completion',
    'notify_on_threshold',
    
    # IoT plugins
    'MQTTIoTPlugin',
    'LoRaWANPlugin',
    'SimulatedIoTPlugin',
    'IoTDataConverter',
    
    # Analytics plugins
    'AdvancedAnalyticsPlugin',
    'ClusteringPlugin',
    
    # Initialization
    'initialize_default_plugins'
]
