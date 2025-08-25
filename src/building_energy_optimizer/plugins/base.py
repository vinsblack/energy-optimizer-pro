"""
Plugin system for Building Energy Optimizer.
Allows extending functionality through modular plugins.
"""
import abc
import importlib
import inspect
import logging
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
import json
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class PluginInfo:
    """Plugin information structure."""
    name: str
    version: str
    description: str
    author: str
    category: str
    dependencies: List[str]
    enabled: bool = True
    loaded: bool = False
    load_time: Optional[datetime] = None
    error: Optional[str] = None

class PluginBase(abc.ABC):
    """Base class for all plugins."""
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass
    
    @property
    def author(self) -> str:
        """Plugin author."""
        return "Unknown"
    
    @property
    def category(self) -> str:
        """Plugin category."""
        return "general"
    
    @property
    def dependencies(self) -> List[str]:
        """Plugin dependencies."""
        return []
    
    @abc.abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration."""
        pass
    
    @abc.abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin functionality."""
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        return True

class DataProcessorPlugin(PluginBase):
    """Base class for data processing plugins."""
    
    @property
    def category(self) -> str:
        return "data_processor"
    
    @abc.abstractmethod
    def process_data(self, data: Any) -> Any:
        """Process input data and return processed data."""
        pass

class NotificationPlugin(PluginBase):
    """Base class for notification plugins."""
    
    @property
    def category(self) -> str:
        return "notification"
    
    @abc.abstractmethod
    def send_notification(self, message: str, priority: str = "medium") -> bool:
        """Send notification."""
        pass

class AnalyticsPlugin(PluginBase):
    """Base class for analytics plugins."""
    
    @property
    def category(self) -> str:
        return "analytics"
    
    @abc.abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analytics on data."""
        pass

class IoTPlugin(PluginBase):
    """Base class for IoT integration plugins."""
    
    @property
    def category(self) -> str:
        return "iot"
    
    @abc.abstractmethod
    def collect_data(self) -> Dict[str, Any]:
        """Collect data from IoT devices."""
        pass
    
    @abc.abstractmethod
    def send_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Send command to IoT device."""
        pass

class PluginManager:
    """Plugin management system."""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.enabled_plugins: Dict[str, bool] = {}
        
        # Create plugin directory if it doesn't exist
        self.plugin_dir.mkdir(exist_ok=True)
        
        # Load plugin configuration
        self._load_plugin_config()
        
    def _load_plugin_config(self):
        """Load plugin configuration from file."""
        config_file = self.plugin_dir / "config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.enabled_plugins = config.get('enabled_plugins', {})
            except Exception as e:
                logger.error(f"Failed to load plugin config: {e}")
        
    def _save_plugin_config(self):
        """Save plugin configuration to file."""
        config_file = self.plugin_dir / "config.json"
        
        config = {
            'enabled_plugins': self.enabled_plugins,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin config: {e}")
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in plugin directory."""
        discovered = []
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
                
            plugin_name = plugin_file.stem
            discovered.append(plugin_name)
            
        logger.info(f"Discovered {len(discovered)} plugins: {discovered}")
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin."""
        try:
            # Import plugin module
            plugin_path = f"{self.plugin_dir.name}.{plugin_name}"
            plugin_module = importlib.import_module(plugin_path)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(plugin_module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj != PluginBase):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise ValueError(f"No plugin class found in {plugin_name}")
            
            # Instantiate plugin
            plugin_instance = plugin_class()
            
            # Create plugin info
            info = PluginInfo(
                name=plugin_instance.name,
                version=plugin_instance.version,
                description=plugin_instance.description,
                author=plugin_instance.author,
                category=plugin_instance.category,
                dependencies=plugin_instance.dependencies,
                enabled=self.enabled_plugins.get(plugin_name, True),
                loaded=True,
                load_time=datetime.now()
            )
            
            # Check dependencies
            missing_deps = self._check_dependencies(plugin_instance.dependencies)
            if missing_deps:
                info.error = f"Missing dependencies: {missing_deps}"
                info.loaded = False
                logger.warning(f"Plugin {plugin_name} missing dependencies: {missing_deps}")
            
            # Initialize plugin if enabled and dependencies met
            if info.enabled and not missing_deps:
                try:
                    if plugin_instance.initialize({}):
                        self.plugins[plugin_name] = plugin_instance
                        logger.info(f"Plugin {plugin_name} loaded and initialized successfully")
                    else:
                        info.error = "Initialization failed"
                        info.loaded = False
                except Exception as e:
                    info.error = f"Initialization error: {str(e)}"
                    info.loaded = False
                    logger.error(f"Plugin {plugin_name} initialization failed: {e}")
            
            self.plugin_info[plugin_name] = info
            return info.loaded
            
        except Exception as e:
            error_info = PluginInfo(
                name=plugin_name,
                version="unknown",
                description="Failed to load",
                author="unknown",
                category="unknown",
                dependencies=[],
                enabled=False,
                loaded=False,
                error=str(e)
            )
            self.plugin_info[plugin_name] = error_info
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """Check if plugin dependencies are available."""
        missing = []
        
        for dep in dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing.append(dep)
        
        return missing
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins."""
        discovered = self.discover_plugins()
        results = {}
        
        for plugin_name in discovered:
            results[plugin_name] = self.load_plugin(plugin_name)
        
        self._save_plugin_config()
        return results
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].cleanup()
                del self.plugins[plugin_name]
                
                if plugin_name in self.plugin_info:
                    self.plugin_info[plugin_name].loaded = False
                
                logger.info(f"Plugin {plugin_name} unloaded")
                return True
                
            except Exception as e:
                logger.error(f"Failed to unload plugin {plugin_name}: {e}")
                return False
        
        return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        self.enabled_plugins[plugin_name] = True
        self._save_plugin_config()
        
        # Load if not already loaded
        if plugin_name not in self.plugins:
            return self.load_plugin(plugin_name)
        
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        self.enabled_plugins[plugin_name] = False
        self._save_plugin_config()
        
        # Unload if loaded
        if plugin_name in self.plugins:
            return self.unload_plugin(plugin_name)
        
        return True
    
    def get_plugins_by_category(self, category: str) -> List[PluginBase]:
        """Get all loaded plugins in a category."""
        return [
            plugin for plugin in self.plugins.values()
            if plugin.category == category
        ]
    
    def execute_plugin(self, plugin_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific plugin."""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin {plugin_name} not loaded")
        
        plugin = self.plugins[plugin_name]
        
        try:
            result = plugin.execute(data)
            logger.debug(f"Plugin {plugin_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Plugin {plugin_name} execution failed: {e}")
            raise
    
    def execute_category(self, category: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all plugins in a category."""
        plugins = self.get_plugins_by_category(category)
        results = {}
        
        for plugin in plugins:
            try:
                result = plugin.execute(data)
                results[plugin.name] = result
            except Exception as e:
                logger.error(f"Plugin {plugin.name} failed: {e}")
                results[plugin.name] = {"error": str(e)}
        
        return results
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a plugin."""
        return self.plugin_info.get(plugin_name)
    
    def list_plugins(self) -> Dict[str, PluginInfo]:
        """List all plugins with their information."""
        return {name: asdict(info) for name, info in self.plugin_info.items()}
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get plugin system status summary."""
        total_plugins = len(self.plugin_info)
        loaded_plugins = len(self.plugins)
        enabled_plugins = sum(1 for info in self.plugin_info.values() if info.enabled)
        
        categories = {}
        for info in self.plugin_info.values():
            category = info.category
            if category not in categories:
                categories[category] = {'total': 0, 'loaded': 0}
            categories[category]['total'] += 1
            if info.loaded:
                categories[category]['loaded'] += 1
        
        return {
            'total_plugins': total_plugins,
            'loaded_plugins': loaded_plugins,
            'enabled_plugins': enabled_plugins,
            'categories': categories,
            'plugin_directory': str(self.plugin_dir)
        }

# Global plugin manager instance
plugin_manager = PluginManager()

def get_plugin_manager() -> PluginManager:
    """Get global plugin manager instance."""
    return plugin_manager

if __name__ == "__main__":
    # Test plugin system
    print("🧩 Testing plugin system...")
    
    manager = PluginManager()
    
    # Discover plugins
    discovered = manager.discover_plugins()
    print(f"Discovered plugins: {discovered}")
    
    # Load all plugins
    results = manager.load_all_plugins()
    print(f"Load results: {results}")
    
    # Show status
    status = manager.get_status_summary()
    print(f"Plugin system status: {status}")
