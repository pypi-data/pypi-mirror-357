"""Coffee maker adapter implementation."""

from typing import Dict, Any, List, Optional
from smarthomeharmonizer.adapters.base import DeviceAdapter
from smarthomeharmonizer.core.exceptions import InvalidCommandError, AdapterError
import logging
import random

logger = logging.getLogger(__name__)


class CoffeeMakerAdapter(DeviceAdapter):
    """Adapter for coffee maker devices."""
    
    SUPPORTED_COMMANDS = ['turnOn', 'turnOff', 'brew', 'setStrength', 'setSize', 'clean', 'getStatus']
    
    BREW_STRENGTHS = ['light', 'medium', 'strong', 'extra_strong']
    BREW_SIZES = ['small', 'medium', 'large']
    
    def _initialize_state(self) -> Dict[str, Any]:
        """Initialize coffee maker state."""
        return {
            'powerState': 'OFF',
            'brewing': False,
            'brewStrength': 'medium',
            'brewSize': 'medium',
            'waterLevel': 100,  # Percentage
            'coffeeBeans': 100,  # Percentage
            'needsCleaning': False,
            'lastBrewTime': None
        }
    
    def get_supported_commands(self) -> List[str]:
        """Get supported commands for coffee maker."""
        return self.SUPPORTED_COMMANDS
    
    def execute_command(self, command: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute command on coffee maker."""
        if not self.validate_command(command):
            raise InvalidCommandError(f"Command '{command}' not supported by coffee maker")
        
        parameters = parameters or {}
        
        try:
            if command == 'turnOn':
                self._state['powerState'] = 'ON'
                logger.info(f"Coffee maker {self.device_id} turned ON")
                
            elif command == 'turnOff':
                self._state['powerState'] = 'OFF'
                self._state['brewing'] = False
                logger.info(f"Coffee maker {self.device_id} turned OFF")
                
            elif command == 'brew':
                if self._state['powerState'] == 'OFF':
                    raise ValueError("Coffee maker must be turned on first")
                if self._state['waterLevel'] < 20:
                    raise ValueError("Water level too low")
                if self._state['coffeeBeans'] < 10:
                    raise ValueError("Not enough coffee beans")
                if self._state['brewing']:
                    raise ValueError("Already brewing")
                
                self._state['brewing'] = True
                # Simulate resource consumption
                self._state['waterLevel'] -= 20
                self._state['coffeeBeans'] -= 10
                
                # Simulate cleaning need
                if random.random() > 0.7:
                    self._state['needsCleaning'] = True
                
                logger.info(f"Coffee maker {self.device_id} started brewing")
                
            elif command == 'setStrength':
                strength = parameters.get('strength')
                if strength not in self.BREW_STRENGTHS:
                    raise ValueError(f"Invalid strength. Must be one of: {self.BREW_STRENGTHS}")
                self._state['brewStrength'] = strength
                logger.info(f"Coffee maker {self.device_id} strength set to {strength}")
                
            elif command == 'setSize':
                size = parameters.get('size')
                if size not in self.BREW_SIZES:
                    raise ValueError(f"Invalid size. Must be one of: {self.BREW_SIZES}")
                self._state['brewSize'] = size
                logger.info(f"Coffee maker {self.device_id} size set to {size}")
                
            elif command == 'clean':
                self._state['needsCleaning'] = False
                logger.info(f"Coffee maker {self.device_id} cleaned")
                
            elif command == 'getStatus':
                # No state change, just return current state
                pass
                
        except Exception as e:
            logger.error(f"Error executing {command} on {self.device_id}: {str(e)}")
            raise AdapterError(f"Failed to execute {command}: {str(e)}")
        
        return self.get_state()
