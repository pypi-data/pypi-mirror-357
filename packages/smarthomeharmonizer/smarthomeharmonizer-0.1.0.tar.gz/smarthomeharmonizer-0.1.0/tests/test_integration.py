"""Integration tests for SmartHomeHarmonizer."""

import pytest
import json
from smarthomeharmonizer.core.app import create_app
from smarthomeharmonizer.core.device_manager import DeviceManager
from smarthomeharmonizer.adapters.smart_light import SmartLightAdapter


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def app(self):
        """Create test app with multiple devices."""
        manager = DeviceManager()
        
        # Register multiple devices
        light1 = SmartLightAdapter('light1', 'Living Room Light')
        light2 = SmartLightAdapter('light2', 'Bedroom Light')
        
        manager.register_device(light1)
        manager.register_device(light2)
        
        app = create_app(manager)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_complete_device_workflow(self, client):
        """Test complete device control workflow."""
        # List devices
        response = client.get('/api/v1/devices')
        assert response.status_code == 200
        devices = response.get_json()['devices']
        assert len(devices) == 2
        
        # Get specific device
        response = client.get('/api/v1/devices/light1')
        assert response.status_code == 200
        device = response.get_json()
        assert device['state']['powerState'] == 'OFF'
        
        # Turn on light
        response = client.post('/api/v1/devices/light1/command',
                             json={'command': 'turnOn'})
        assert response.status_code == 200
        assert response.get_json()['state']['powerState'] == 'ON'
        
        # Set brightness
        response = client.post('/api/v1/devices/light1/command',
                             json={'command': 'setBrightness', 
                                   'parameters': {'brightness': 60}})
        assert response.status_code == 200
        assert response.get_json()['state']['brightness'] == 60
        
        # Set color
        response = client.post('/api/v1/devices/light1/command',
                             json={'command': 'setColor',
                                   'parameters': {'color': {'r': 255, 'g': 0, 'b': 0}}})
        assert response.status_code == 200
        assert response.get_json()['state']['color'] == {'r': 255, 'g': 0, 'b': 0}
        
        # Get final state
        response = client.get('/api/v1/devices/light1/state')
        assert response.status_code == 200
        state = response.get_json()['state']
        assert state['powerState'] == 'ON'
        assert state['brightness'] == 60
        assert state['color'] == {'r': 255, 'g': 0, 'b': 0}
    
    def test_multiple_devices_independence(self, client):
        """Test that device states are independent."""
        # Turn on light1
        client.post('/api/v1/devices/light1/command',
                   json={'command': 'turnOn'})
        
        # Check light2 is still off
        response = client.get('/api/v1/devices/light2/state')
        assert response.get_json()['state']['powerState'] == 'OFF'
        
        # Turn on light2
        client.post('/api/v1/devices/light2/command',
                   json={'command': 'turnOn'})
        
        # Both should be on
        response1 = client.get('/api/v1/devices/light1/state')
        response2 = client.get('/api/v1/devices/light2/state')
        
        assert response1.get_json()['state']['powerState'] == 'ON'
        assert response2.get_json()['state']['powerState'] == 'ON'
    
    def test_error_handling_workflow(self, client):
        """Test error handling in workflow."""
        # Try to control non-existent device
        response = client.post('/api/v1/devices/nonexistent/command',
                             json={'command': 'turnOn'})
        assert response.status_code == 404
        
        # Try invalid command
        response = client.post('/api/v1/devices/light1/command',
                             json={'command': 'explode'})
        assert response.status_code == 400
        
        # Try invalid parameters
        response = client.post('/api/v1/devices/light1/command',
                             json={'command': 'setBrightness',
                                   'parameters': {'brightness': 'very bright'}})
        assert response.status_code == 400
