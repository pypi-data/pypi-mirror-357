"""Tests for core functionality."""

import pytest
from flask import Flask
from smarthomeharmonizer.core.app import create_app
from smarthomeharmonizer.core.device_manager import DeviceManager
from smarthomeharmonizer.core.exceptions import DeviceNotFoundError, InvalidCommandError
from smarthomeharmonizer.adapters.smart_light import SmartLightAdapter


class TestDeviceManager:
    """Test DeviceManager functionality."""
    
    def test_register_device(self):
        """Test device registration."""
        manager = DeviceManager()
        adapter = SmartLightAdapter('light1', 'Living Room Light')
        
        manager.register_device(adapter)
        
        assert 'light1' in [d['deviceId'] for d in manager.list_devices()]
    
    def test_register_duplicate_device(self):
        """Test that duplicate device IDs raise error."""
        manager = DeviceManager()
        adapter1 = SmartLightAdapter('light1', 'Light 1')
        adapter2 = SmartLightAdapter('light1', 'Light 2')
        
        manager.register_device(adapter1)
        
        with pytest.raises(ValueError, match="already registered"):
            manager.register_device(adapter2)
    
    def test_unregister_device(self):
        """Test device unregistration."""
        manager = DeviceManager()
        adapter = SmartLightAdapter('light1', 'Living Room Light')
        
        manager.register_device(adapter)
        manager.unregister_device('light1')
        
        assert 'light1' not in [d['deviceId'] for d in manager.list_devices()]
    
    def test_unregister_nonexistent_device(self):
        """Test unregistering non-existent device raises error."""
        manager = DeviceManager()
        
        with pytest.raises(DeviceNotFoundError):
            manager.unregister_device('nonexistent')
    
    def test_get_device(self):
        """Test retrieving device by ID."""
        manager = DeviceManager()
        adapter = SmartLightAdapter('light1', 'Living Room Light')
        
        manager.register_device(adapter)
        retrieved = manager.get_device('light1')
        
        assert retrieved.device_id == 'light1'
        assert retrieved.name == 'Living Room Light'
    
    def test_execute_command(self):
        """Test command execution through manager."""
        manager = DeviceManager()
        adapter = SmartLightAdapter('light1', 'Living Room Light')
        
        manager.register_device(adapter)
        state = manager.execute_command('light1', 'turnOn')
        
        assert state['powerState'] == 'ON'
    
    def test_execute_invalid_command(self):
        """Test invalid command raises error."""
        manager = DeviceManager()
        adapter = SmartLightAdapter('light1', 'Living Room Light')
        
        manager.register_device(adapter)
        
        with pytest.raises(InvalidCommandError):
            manager.execute_command('light1', 'invalidCommand')


class TestFlaskApp:
    """Test Flask application endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        manager = DeviceManager()
        adapter = SmartLightAdapter('light1', 'Living Room Light')
        manager.register_device(adapter)
        
        app = create_app(manager)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_list_devices(self, client):
        """Test device listing endpoint."""
        response = client.get('/api/v1/devices')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['devices']) == 1
        assert data['devices'][0]['deviceId'] == 'light1'
    
    def test_get_device(self, client):
        """Test get device endpoint."""
        response = client.get('/api/v1/devices/light1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['deviceId'] == 'light1'
        assert data['name'] == 'Living Room Light'
    
    def test_get_nonexistent_device(self, client):
        """Test get non-existent device returns 404."""
        response = client.get('/api/v1/devices/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_execute_command(self, client):
        """Test command execution endpoint."""
        response = client.post('/api/v1/devices/light1/command', 
                             json={'command': 'turnOn'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['state']['powerState'] == 'ON'
    
    def test_execute_command_with_parameters(self, client):
        """Test command execution with parameters."""
        response = client.post('/api/v1/devices/light1/command', 
                             json={'command': 'setBrightness', 'parameters': {'brightness': 50}})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['state']['brightness'] == 50
    
    def test_execute_invalid_command(self, client):
        """Test invalid command returns 400."""
        response = client.post('/api/v1/devices/light1/command', 
                             json={'command': 'invalidCommand'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_execute_command_missing_data(self, client):
        """Test missing command data returns 400."""
        response = client.post('/api/v1/devices/light1/command', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Missing command' in data['error']
