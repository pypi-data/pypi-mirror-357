"""Tests for device adapters."""

import pytest
from smarthomeharmonizer.adapters.smart_light import SmartLightAdapter
from smarthomeharmonizer.core.exceptions import InvalidCommandError, AdapterError


class TestSmartLightAdapter:
    """Test SmartLightAdapter functionality."""
    
    def test_initialization(self):
        """Test adapter initialization."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        
        assert adapter.device_id == 'light1'
        assert adapter.name == 'Test Light'
        state = adapter.get_state()
        assert state['powerState'] == 'OFF'
        assert state['brightness'] == 100
        assert state['color'] == {'r': 255, 'g': 255, 'b': 255}
    
    def test_supported_commands(self):
        """Test getting supported commands."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        commands = adapter.get_supported_commands()
        
        expected = ['turnOn', 'turnOff', 'setBrightness', 'setColor', 'getStatus']
        assert set(commands) == set(expected)
    
    def test_turn_on(self):
        """Test turning light on."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        state = adapter.execute_command('turnOn')
        
        assert state['powerState'] == 'ON'
    
    def test_turn_off(self):
        """Test turning light off."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        adapter.execute_command('turnOn')
        state = adapter.execute_command('turnOff')
        
        assert state['powerState'] == 'OFF'
    
    def test_set_brightness(self):
        """Test setting brightness."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        state = adapter.execute_command('setBrightness', {'brightness': 75})
        
        assert state['brightness'] == 75
    
    def test_set_brightness_invalid_value(self):
        """Test setting invalid brightness raises error."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        
        with pytest.raises(AdapterError, match="Failed to execute setBrightness"):
            adapter.execute_command('setBrightness', {'brightness': 150})
        
        with pytest.raises(AdapterError, match="Failed to execute setBrightness"):
            adapter.execute_command('setBrightness', {'brightness': -10})
    
    def test_set_color(self):
        """Test setting color."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        color = {'r': 100, 'g': 150, 'b': 200}
        state = adapter.execute_command('setColor', {'color': color})
        
        assert state['color'] == color
    
    def test_set_color_invalid_values(self):
        """Test setting invalid color raises error."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        
        # Missing color component
        with pytest.raises(AdapterError, match="Failed to execute setColor"):
            adapter.execute_command('setColor', {'color': {'r': 100, 'g': 150}})
        
        # Invalid color value
        with pytest.raises(AdapterError, match="Failed to execute setColor"):
            adapter.execute_command('setColor', {'color': {'r': 300, 'g': 150, 'b': 200}})
    
    def test_invalid_command(self):
        """Test invalid command raises error."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        
        with pytest.raises(InvalidCommandError):
            adapter.execute_command('invalidCommand')
    
    def test_validate_command(self):
        """Test command validation."""
        adapter = SmartLightAdapter('light1', 'Test Light')
        
        assert adapter.validate_command('turnOn') is True
        assert adapter.validate_command('invalidCommand') is False
