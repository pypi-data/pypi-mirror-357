"""Thermostat adapter implementation."""

from typing import Dict, Any, List, Optional
from smarthomeharmonizer.adapters.base import DeviceAdapter
from smarthomeharmonizer.core.exceptions import InvalidCommandError, AdapterError
import logging

logger = logging.getLogger(__name__)


class ThermostatAdapter(DeviceAdapter):
    """Adapter for thermostat devices."""
    
    SUPPORTED_COMMANDS = ['turnOn', 'turnOff', 'setTemperature', 'setMode', 'getStatus']
    
    MODES = ['heat', 'cool', 'auto', 'off']
    
    def _initialize_state(self) -> Dict[str, Any]:
        """Initialize thermostat state."""
        return {
            'powerState': 'OFF',
            'mode': 'off',
            'targetTemperature': 72.0,
            'currentTemperature': 70.0,
            'humidity': 50.0,
            'fanRunning': False
        }
    
    def get_supported_commands(self) -> List[str]:
        """Get supported commands for thermostat."""
        return self.SUPPORTED_COMMANDS
    
    def execute_command(self, command: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute command on thermostat."""
        if not self.validate_command(command):
            raise InvalidCommandError(f"Command '{command}' not supported by thermostat")
        
        parameters = parameters or {}
        
        try:
            if command == 'turnOn':
                self._state['powerState'] = 'ON'
                if self._state['mode'] == 'off':
                    self._state['mode'] = 'auto'
                logger.info(f"Thermostat {self.device_id} turned ON")
                
            elif command == 'turnOff':
                self._state['powerState'] = 'OFF'
                self._state['mode'] = 'off'
                self._state['fanRunning'] = False
                logger.info(f"Thermostat {self.device_id} turned OFF")
                
            elif command == 'setTemperature':
                temperature = parameters.get('temperature')
                if not isinstance(temperature, (int, float)) or not 50 <= temperature <= 90:
                    raise ValueError("Temperature must be between 50 and 90 degrees")
                self._state['targetTemperature'] = float(temperature)
                logger.info(f"Thermostat {self.device_id} target temperature set to {temperature}°F")
                
            elif command == 'setMode':
                mode = parameters.get('mode', '').lower()
                if mode not in self.MODES:
                    raise ValueError(f"Mode must be one of: {', '.join(self.MODES)}")
                self._state['mode'] = mode
                if mode == 'off':
                    self._state['powerState'] = 'OFF'
                    self._state['fanRunning'] = False
                else:
                    self._state['powerState'] = 'ON'
                logger.info(f"Thermostat {self.device_id} mode set to {mode}")
                
            elif command == 'getStatus':
                # No state change, just return current state
                pass
                
        except Exception as e:
            logger.error(f"Error executing {command} on {self.device_id}: {str(e)}")
            raise AdapterError(f"Failed to execute {command}: {str(e)}")
        
        return self.get_state()
