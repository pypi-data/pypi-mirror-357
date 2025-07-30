"""Flask application and API endpoints."""

from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import logging

from smarthomeharmonizer.core.device_manager import DeviceManager
from smarthomeharmonizer.core.exceptions import (
    SmartHomeHarmonizerError, DeviceNotFoundError, InvalidCommandError
)

logger = logging.getLogger(__name__)


def create_app(device_manager: Optional[DeviceManager] = None) -> Flask:
    """Create and configure Flask application.
    
    Args:
        device_manager: Optional DeviceManager instance (creates new if None)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Use provided device manager or create new one
    if device_manager is None:
        device_manager = DeviceManager()
    
    app.device_manager = device_manager
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    @app.errorhandler(DeviceNotFoundError)
    def handle_device_not_found(e):
        """Handle device not found errors."""
        return jsonify({'success': False, 'error': str(e)}), 404
    
    @app.errorhandler(InvalidCommandError)
    def handle_invalid_command(e):
        """Handle invalid command errors."""
        return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.errorhandler(SmartHomeHarmonizerError)
    def handle_app_error(e):
        """Handle general application errors."""
        return jsonify({'success': False, 'error': str(e)}), 400
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'version': '0.1.0'})
    
    @app.route('/api/v1/devices', methods=['GET'])
    def list_devices():
        """List all registered devices."""
        devices = app.device_manager.list_devices()
        return jsonify({'success': True, 'devices': devices})
    
    @app.route('/api/v1/devices/<device_id>', methods=['GET'])
    def get_device(device_id: str):
        """Get device information and state."""
        device = app.device_manager.get_device(device_id)
        return jsonify({
            'success': True,
            'deviceId': device_id,
            'name': device.name,
            'type': device.__class__.__name__,
            'supportedCommands': device.get_supported_commands(),
            'state': device.get_state()
        })
    
    @app.route('/api/v1/devices/<device_id>/state', methods=['GET'])
    def get_device_state(device_id: str):
        """Get device state."""
        state = app.device_manager.get_device_state(device_id)
        return jsonify({'success': True, 'deviceId': device_id, 'state': state})
    
    @app.route('/api/v1/devices/<device_id>/command', methods=['POST'])
    def execute_command(device_id: str):
        """Execute command on device."""
        data = request.get_json()
        
        if not data or 'command' not in data:
            return jsonify({'success': False, 'error': 'Missing command'}), 400
        
        command = data['command']
        parameters = data.get('parameters', {})
        
        state = app.device_manager.execute_command(device_id, command, parameters)
        
        return jsonify({
            'success': True,
            'deviceId': device_id,
            'command': command,
            'state': state
        })
    
    return app
