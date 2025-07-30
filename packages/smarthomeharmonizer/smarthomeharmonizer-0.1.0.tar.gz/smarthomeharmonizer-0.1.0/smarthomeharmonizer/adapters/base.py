"""Base adapter class for device implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DeviceAdapter(ABC):
    """Abstract base class for device adapters.
    
    All device adapters must inherit from this class and implement
    the required methods for device control and state management.
    """
    
    def __init__(self, device_id: str, name: str, **kwargs):
        """Initialize the device adapter.
        
        Args:
            device_id: Unique identifier for the device
            name: Human-readable name for the device
            **kwargs: Additional device-specific configuration
        """
        self.device_id = device_id
        self.name = name
        self._state = self._initialize_state()
        self._config = kwargs
        logger.info(f"Initialized {self.__class__.__name__} for device {device_id}")
    
    @abstractmethod
    def _initialize_state(self) -> Dict[str, Any]:
        """Initialize the device state.
        
        Returns:
            Initial state dictionary for the device
        """
        pass
    
    @abstractmethod
    def get_supported_commands(self) -> List[str]:
        """Get list of commands supported by this device.
        
        Returns:
            List of command names
        """
        pass
    
    @abstractmethod
    def execute_command(self, command: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command on the device.
        
        Args:
            command: Command name to execute
            parameters: Optional parameters for the command
            
        Returns:
            Updated device state
            
        Raises:
            InvalidCommandError: If command is not supported
            AdapterError: If command execution fails
        """
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """Get current device state.
        
        Returns:
            Current state dictionary
        """
        return self._state.copy()
    
    def validate_command(self, command: str) -> bool:
        """Check if a command is supported.
        
        Args:
            command: Command name to validate
            
        Returns:
            True if command is supported, False otherwise
        """
        return command in self.get_supported_commands()
