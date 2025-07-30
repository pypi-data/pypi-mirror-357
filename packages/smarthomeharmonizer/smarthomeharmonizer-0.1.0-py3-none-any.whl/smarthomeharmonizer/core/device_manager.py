"""Device registry and management."""

from typing import Dict, Optional, List, Any
from threading import RLock
import logging

from smarthomeharmonizer.adapters.base import DeviceAdapter
from smarthomeharmonizer.core.exceptions import DeviceNotFoundError

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages device registry and command routing."""
    
    def __init__(self):
        """Initialize the device manager."""
        self._devices: Dict[str, DeviceAdapter] = {}
        self._lock = RLock()
        logger.info("DeviceManager initialized")
    
    def register_device(self, adapter: DeviceAdapter) -> None:
        """Register a device adapter.
        
        Args:
            adapter: Device adapter instance to register
            
        Raises:
            ValueError: If device_id already exists
        """
        with self._lock:
            if adapter.device_id in self._devices:
                raise ValueError(f"Device {adapter.device_id} already registered")
            
            self._devices[adapter.device_id] = adapter
            logger.info(f"Registered device {adapter.device_id} ({adapter.name})")
    
    def unregister_device(self, device_id: str) -> None:
        """Unregister a device.
        
        Args:
            device_id: ID of device to unregister
            
        Raises:
            DeviceNotFoundError: If device not found
        """
        with self._lock:
            if device_id not in self._devices:
                raise DeviceNotFoundError(f"Device {device_id} not found")
            
            del self._devices[device_id]
            logger.info(f"Unregistered device {device_id}")
    
    def get_device(self, device_id: str) -> DeviceAdapter:
        """Get a device adapter by ID.
        
        Args:
            device_id: Device ID to retrieve
            
        Returns:
            Device adapter instance
            
        Raises:
            DeviceNotFoundError: If device not found
        """
        with self._lock:
            if device_id not in self._devices:
                raise DeviceNotFoundError(f"Device {device_id} not found")
            return self._devices[device_id]
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List all registered devices.
        
        Returns:
            List of device information dictionaries
        """
        with self._lock:
            return [
                {
                    'deviceId': device_id,
                    'name': adapter.name,
                    'type': adapter.__class__.__name__,
                    'supportedCommands': adapter.get_supported_commands(),
                    'state': adapter.get_state()
                }
                for device_id, adapter in self._devices.items()
            ]
    
    def execute_command(self, device_id: str, command: str, 
                       parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command on a device.
        
        Args:
            device_id: Target device ID
            command: Command to execute
            parameters: Optional command parameters
            
        Returns:
            Updated device state
            
        Raises:
            DeviceNotFoundError: If device not found
            InvalidCommandError: If command not supported
            AdapterError: If command execution fails
        """
        device = self.get_device(device_id)
        return device.execute_command(command, parameters)
    
    def get_device_state(self, device_id: str) -> Dict[str, Any]:
        """Get current state of a device.
        
        Args:
            device_id: Device ID to query
            
        Returns:
            Current device state
            
        Raises:
            DeviceNotFoundError: If device not found
        """
        device = self.get_device(device_id)
        return device.get_state()
