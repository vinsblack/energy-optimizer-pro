"""
IoT Integration Plugin for Building Energy Optimizer.
Supports MQTT, LoRaWAN, and other IoT protocols.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from .base import IoTPlugin

logger = logging.getLogger(__name__)

class MQTTIoTPlugin(IoTPlugin):
    """MQTT IoT integration plugin."""
    
    @property
    def name(self) -> str:
        return "MQTT IoT Integration"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Collect energy data from IoT devices via MQTT protocol"
    
    @property
    def author(self) -> str:
        return "Building Energy Optimizer Team"
    
    @property
    def dependencies(self) -> List[str]:
        return ["paho-mqtt"]
    
    def __init__(self):
        self.mqtt_client = None
        self.config = {}
        self.data_buffer = []
        self.device_registry = {}
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize MQTT connection."""
        if not HAS_MQTT:
            logger.error("paho-mqtt not installed")
            return False
        
        self.config = config
        
        try:
            # MQTT configuration
            broker_host = config.get('mqtt_broker', 'localhost')
            broker_port = config.get('mqtt_port', 1883)
            username = config.get('mqtt_username')
            password = config.get('mqtt_password')
            
            # Create MQTT client
            self.mqtt_client = mqtt.Client()
            
            if username and password:
                self.mqtt_client.username_pw_set(username, password)
            
            # Set callbacks
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_disconnect = self._on_disconnect
            
            # Connect to broker
            self.mqtt_client.connect(broker_host, broker_port, 60)
            self.mqtt_client.loop_start()
            
            logger.info(f"MQTT plugin initialized - connected to {broker_host}:{broker_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MQTT plugin: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            logger.info("MQTT connected successfully")
            
            # Subscribe to device topics
            topics = self.config.get('subscribe_topics', [
                'building/+/energy',
                'building/+/temperature',
                'building/+/humidity',
                'building/+/occupancy'
            ])
            
            for topic in topics:
                client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback."""
        try:
            # Parse topic
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 3:
                building_id = topic_parts[1]
                sensor_type = topic_parts[2]
                
                # Parse payload
                payload = json.loads(msg.payload.decode())
                
                # Create data point
                data_point = {
                    'timestamp': datetime.now().isoformat(),
                    'building_id': building_id,
                    'sensor_type': sensor_type,
                    'value': payload.get('value'),
                    'unit': payload.get('unit'),
                    'device_id': payload.get('device_id'),
                    'topic': msg.topic
                }
                
                # Add to buffer
                self.data_buffer.append(data_point)
                
                # Keep buffer size manageable
                if len(self.data_buffer) > 1000:
                    self.data_buffer = self.data_buffer[-500:]
                
                logger.debug(f"Received IoT data: {building_id}/{sensor_type} = {payload.get('value')}")
                
        except Exception as e:
            logger.error(f"Failed to process MQTT message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnect callback."""
        logger.warning(f"MQTT disconnected with code {rc}")
    
    def collect_data(self) -> Dict[str, Any]:
        """Collect buffered IoT data."""
        # Return and clear buffer
        data = {
            'iot_data': self.data_buffer.copy(),
            'collection_time': datetime.now().isoformat(),
            'device_count': len(self.device_registry),
            'data_points': len(self.data_buffer)
        }
        
        self.data_buffer.clear()
        return data
    
    def send_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Send command to IoT device via MQTT."""
        if not self.mqtt_client:
            return False
        
        try:
            # Construct command topic
            topic = f"building/{device_id}/command"
            
            # Prepare command payload
            payload = {
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'source': 'energy_optimizer'
            }
            
            # Publish command
            result = self.mqtt_client.publish(topic, json.dumps(payload))
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Command sent to device {device_id}: {command}")
                return True
            else:
                logger.error(f"Failed to send command to device {device_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending command to device {device_id}: {e}")
            return False
    
    def register_device(self, device_id: str, device_info: Dict[str, Any]) -> bool:
        """Register a new IoT device."""
        self.device_registry[device_id] = {
            'info': device_info,
            'registered_at': datetime.now().isoformat(),
            'last_seen': None
        }
        
        logger.info(f"Registered IoT device: {device_id}")
        return True
    
    def get_device_status(self) -> Dict[str, Any]:
        """Get status of all registered devices."""
        return {
            'total_devices': len(self.device_registry),
            'devices': self.device_registry,
            'active_connections': 1 if self.mqtt_client and self.mqtt_client.is_connected() else 0
        }
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute IoT plugin functionality."""
        action = data.get('action', 'collect_data')
        
        if action == 'collect_data':
            return self.collect_data()
        elif action == 'send_command':
            device_id = data.get('device_id')
            command = data.get('command')
            if device_id and command:
                success = self.send_command(device_id, command)
                return {'success': success, 'device_id': device_id}
        elif action == 'device_status':
            return self.get_device_status()
        elif action == 'register_device':
            device_id = data.get('device_id')
            device_info = data.get('device_info', {})
            if device_id:
                success = self.register_device(device_id, device_info)
                return {'success': success, 'device_id': device_id}
        
        return {'error': 'Unknown action'}
    
    def cleanup(self):
        """Cleanup MQTT resources."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("MQTT plugin cleanup completed")

class LoRaWANPlugin(IoTPlugin):
    """LoRaWAN IoT integration plugin."""
    
    @property
    def name(self) -> str:
        return "LoRaWAN Integration"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Collect energy data from LoRaWAN devices"
    
    @property
    def dependencies(self) -> List[str]:
        return ["requests"]
    
    def __init__(self):
        self.config = {}
        self.gateway_url = None
        self.api_key = None
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize LoRaWAN connection."""
        if not HAS_REQUESTS:
            logger.error("requests library not installed")
            return False
        
        self.config = config
        self.gateway_url = config.get('lorawan_gateway_url', 'http://localhost:8080')
        self.api_key = config.get('lorawan_api_key')
        
        if not self.api_key:
            logger.warning("LoRaWAN API key not provided")
        
        logger.info("LoRaWAN plugin initialized")
        return True
    
    def collect_data(self) -> Dict[str, Any]:
        """Collect data from LoRaWAN devices."""
        if not self.gateway_url:
            return {'error': 'Gateway URL not configured'}
        
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
            
            # Get device data from LoRaWAN gateway
            response = requests.get(
                f"{self.gateway_url}/api/devices/data",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                device_data = response.json()
                
                # Process LoRaWAN data
                processed_data = []
                for device in device_data.get('devices', []):
                    for reading in device.get('readings', []):
                        processed_data.append({
                            'timestamp': reading.get('timestamp'),
                            'device_id': device.get('device_id'),
                            'sensor_type': reading.get('sensor_type'),
                            'value': reading.get('value'),
                            'rssi': reading.get('rssi'),
                            'snr': reading.get('snr')
                        })
                
                return {
                    'lorawan_data': processed_data,
                    'collection_time': datetime.now().isoformat(),
                    'devices_count': len(device_data.get('devices', []))
                }
            else:
                return {'error': f'Gateway returned status {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Failed to collect LoRaWAN data: {e}")
            return {'error': str(e)}
    
    def send_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Send command to LoRaWAN device."""
        if not self.gateway_url:
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
            
            payload = {
                'device_id': device_id,
                'command': command,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.gateway_url}/api/devices/{device_id}/command",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to send LoRaWAN command: {e}")
            return False
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LoRaWAN functionality."""
        action = data.get('action', 'collect_data')
        
        if action == 'collect_data':
            return self.collect_data()
        elif action == 'send_command':
            device_id = data.get('device_id')
            command = data.get('command')
            if device_id and command:
                success = self.send_command(device_id, command)
                return {'success': success}
        
        return {'error': 'Unknown action'}

class SimulatedIoTPlugin(IoTPlugin):
    """Simulated IoT plugin for testing and demonstration."""
    
    @property
    def name(self) -> str:
        return "Simulated IoT Devices"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Simulated IoT devices for testing and demonstration"
    
    @property
    def dependencies(self) -> List[str]:
        return []  # No external dependencies
    
    def __init__(self):
        self.devices = {}
        self.data_buffer = []
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize simulated devices."""
        device_count = config.get('device_count', 5)
        
        # Create simulated devices
        for i in range(device_count):
            device_id = f"sim_device_{i:03d}"
            self.devices[device_id] = {
                'type': 'energy_meter',
                'location': f'Floor {i//2 + 1}, Room {i%2 + 1}',
                'status': 'active',
                'last_reading': None
            }
        
        logger.info(f"Simulated IoT plugin initialized with {device_count} devices")
        return True
    
    def collect_data(self) -> Dict[str, Any]:
        """Simulate data collection from IoT devices."""
        import random
        
        collected_data = []
        
        for device_id, device_info in self.devices.items():
            # Simulate realistic energy readings
            base_consumption = random.uniform(50, 150)
            
            # Add time-based variation
            hour = datetime.now().hour
            if 8 <= hour <= 18:  # Working hours
                consumption_factor = random.uniform(1.2, 1.8)
            else:
                consumption_factor = random.uniform(0.5, 0.8)
            
            energy_reading = base_consumption * consumption_factor
            
            # Create data point
            data_point = {
                'timestamp': datetime.now().isoformat(),
                'device_id': device_id,
                'sensor_type': 'energy_consumption',
                'value': round(energy_reading, 2),
                'unit': 'kWh',
                'location': device_info['location'],
                'device_status': device_info['status']
            }
            
            collected_data.append(data_point)
            device_info['last_reading'] = data_point['timestamp']
        
        # Add some temperature and occupancy sensors
        for i in range(3):
            temp_data = {
                'timestamp': datetime.now().isoformat(),
                'device_id': f'temp_sensor_{i:02d}',
                'sensor_type': 'temperature',
                'value': round(random.uniform(18, 26), 1),
                'unit': '°C',
                'location': f'Zone {i+1}'
            }
            collected_data.append(temp_data)
            
            occupancy_data = {
                'timestamp': datetime.now().isoformat(),
                'device_id': f'occupancy_sensor_{i:02d}',
                'sensor_type': 'occupancy',
                'value': random.randint(0, 50),
                'unit': 'people',
                'location': f'Zone {i+1}'
            }
            collected_data.append(occupancy_data)
        
        return {
            'iot_data': collected_data,
            'collection_time': datetime.now().isoformat(),
            'devices_online': len([d for d in self.devices.values() if d['status'] == 'active']),
            'total_devices': len(self.devices)
        }
    
    def send_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Simulate sending command to IoT device."""
        if device_id not in self.devices:
            logger.error(f"Device {device_id} not found")
            return False
        
        # Simulate command execution
        command_type = command.get('type')
        
        if command_type == 'reset':
            self.devices[device_id]['status'] = 'active'
            logger.info(f"Simulated reset command for device {device_id}")
        elif command_type == 'shutdown':
            self.devices[device_id]['status'] = 'offline'
            logger.info(f"Simulated shutdown command for device {device_id}")
        elif command_type == 'calibrate':
            logger.info(f"Simulated calibration command for device {device_id}")
        else:
            logger.warning(f"Unknown command type: {command_type}")
            return False
        
        return True
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simulated IoT functionality."""
        action = data.get('action', 'collect_data')
        
        if action == 'collect_data':
            return self.collect_data()
        elif action == 'send_command':
            device_id = data.get('device_id')
            command = data.get('command')
            if device_id and command:
                success = self.send_command(device_id, command)
                return {'success': success, 'device_id': device_id}
        elif action == 'list_devices':
            return {
                'devices': self.devices,
                'total_devices': len(self.devices)
            }
        elif action == 'device_status':
            device_id = data.get('device_id')
            if device_id in self.devices:
                return {
                    'device_id': device_id,
                    'status': self.devices[device_id]
                }
            else:
                return {'error': f'Device {device_id} not found'}
        
        return {'error': 'Unknown action'}
    
    def cleanup(self):
        """Cleanup simulated devices."""
        self.devices.clear()
        self.data_buffer.clear()
        logger.info("Simulated IoT plugin cleanup completed")

# IoT data converter
class IoTDataConverter:
    """Convert IoT data to optimizer format."""
    
    @staticmethod
    def convert_iot_to_optimizer_format(iot_data: List[Dict]) -> Dict[str, Any]:
        """Convert IoT data to building optimizer format."""
        converted_data = {
            'timestamp': [],
            'energy_consumption': [],
            'temperature': [],
            'humidity': [],
            'occupancy': []
        }
        
        # Group by timestamp
        data_by_timestamp = {}
        
        for reading in iot_data:
            timestamp = reading['timestamp']
            sensor_type = reading['sensor_type']
            value = reading['value']
            
            if timestamp not in data_by_timestamp:
                data_by_timestamp[timestamp] = {}
            
            data_by_timestamp[timestamp][sensor_type] = value
        
        # Convert to lists
        for timestamp, sensors in data_by_timestamp.items():
            converted_data['timestamp'].append(timestamp)
            converted_data['energy_consumption'].append(sensors.get('energy_consumption', 0))
            converted_data['temperature'].append(sensors.get('temperature', 20))
            converted_data['humidity'].append(sensors.get('humidity', 50))
            converted_data['occupancy'].append(sensors.get('occupancy', 0))
        
        return converted_data

if __name__ == "__main__":
    # Test IoT plugins
    print("🌐 Testing IoT plugins...")
    
    # Test simulated IoT
    sim_plugin = SimulatedIoTPlugin()
    if sim_plugin.initialize({'device_count': 3}):
        print("✅ Simulated IoT plugin initialized")
        
        # Collect data
        data = sim_plugin.collect_data()
        print(f"✅ Collected {len(data['iot_data'])} IoT data points")
        
        # Send command
        success = sim_plugin.send_command('sim_device_001', {'type': 'reset'})
        print(f"✅ Command sent successfully: {success}")
        
        # Convert data
        converter = IoTDataConverter()
        converted = converter.convert_iot_to_optimizer_format(data['iot_data'])
        print(f"✅ Converted IoT data for optimizer")
        
        sim_plugin.cleanup()
    
    print("🌐 IoT plugin test complete!")
