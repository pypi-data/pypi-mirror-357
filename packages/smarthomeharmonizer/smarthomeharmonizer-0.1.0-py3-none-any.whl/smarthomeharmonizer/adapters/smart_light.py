"""Smart light adapter implementation."""

from typing import Dict, Any, List, Optional
from smarthomeharmonizer.adapters.base import DeviceAdapter
from smarthomeharmonizer.core.exceptions import InvalidCommandError, AdapterError
import logging

logger = logging.getLogger(__name__)


class SmartLightAdapter(DeviceAdapter):
    """Adapter for smart light devices."""
    
    SUPPORTED_COMMANDS = ['turnOn', 'turnOff', 'setBrightness', 'setColor', 'getStatus']
    
    def _initialize_state(self) -> Dict[str, Any]:
        """Initialize smart light state."""
        return {
            'powerState': 'OFF',
            'brightness': 100,
            'color': {'r': 255, 'g': 255, 'b': 255}
        }
    
    def get_supported_commands(self) -> List[str]:
        """Get supported commands for smart light."""
        return self.SUPPORTED_COMMANDS
    
    def execute_command(self, command: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute command on smart light."""
        if not self.validate_command(command):
            raise InvalidCommandError(f"Command '{command}' not supported by smart light")
        
        parameters = parameters or {}
        
        try:
            if command == 'turnOn':
                self._state['powerState'] = 'ON'
                logger.info(f"Smart light {self.device_id} turned ON")
                
            elif command == 'turnOff':
                self._state['powerState'] = 'OFF'
                logger.info(f"Smart light {self.device_id} turned OFF")
                
            elif command == 'setBrightness':
                brightness = parameters.get('brightness')
                if not isinstance(brightness, (int, float)) or not 0 <= brightness <= 100:
                    raise ValueError("Brightness must be between 0 and 100")
                self._state['brightness'] = int(brightness)
                logger.info(f"Smart light {self.device_id} brightness set to {brightness}")
                
            elif command == 'setColor':
                color = parameters.get('color', {})
                if not all(k in color for k in ['r', 'g', 'b']):
                    raise ValueError("Color must contain 'r', 'g', 'b' values")
                if not all(0 <= color[k] <= 255 for k in ['r', 'g', 'b']):
                    raise ValueError("Color values must be between 0 and 255")
                self._state['color'] = color
                logger.info(f"Smart light {self.device_id} color set to RGB({color['r']}, {color['g']}, {color['b']})")
                
            elif command == 'getStatus':
                # No state change, just return current state
                pass
                
        except Exception as e:
            logger.error(f"Error executing {command} on {self.device_id}: {str(e)}")
            raise AdapterError(f"Failed to execute {command}: {str(e)}")
        
        return self.get_state()
