"""Validation utilities for SmartHomeHarmonizer."""

import re
from typing import Any, Dict, List, Optional


def validate_device_id(device_id: str) -> bool:
    """Validate device ID format.
    
    Args:
        device_id: Device ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(device_id, str):
        return False
    
    # Device ID should be alphanumeric with underscores and hyphens
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, device_id)) and len(device_id) <= 64


def validate_command(command: str) -> bool:
    """Validate command name format.
    
    Args:
        command: Command name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(command, str):
        return False
    
    # Command should be camelCase or snake_case
    pattern = r'^[a-z][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, command)) and len(command) <= 32


def validate_brightness(brightness: Any) -> bool:
    """Validate brightness value.
    
    Args:
        brightness: Brightness value to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        brightness_float = float(brightness)
        return 0 <= brightness_float <= 100
    except (ValueError, TypeError):
        return False


def validate_color(color: Dict[str, Any]) -> bool:
    """Validate RGB color values.
    
    Args:
        color: Color dictionary with 'r', 'g', 'b' keys
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(color, dict):
        return False
    
    required_keys = {'r', 'g', 'b'}
    if not all(key in color for key in required_keys):
        return False
    
    try:
        r, g, b = int(color['r']), int(color['g']), int(color['b'])
        return all(0 <= val <= 255 for val in [r, g, b])
    except (ValueError, TypeError):
        return False


def validate_parameters(parameters: Dict[str, Any], required_keys: Optional[List[str]] = None) -> bool:
    """Validate command parameters.
    
    Args:
        parameters: Parameters dictionary to validate
        required_keys: List of required parameter keys
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(parameters, dict):
        return False
    
    if required_keys:
        return all(key in parameters for key in required_keys)
    
    return True


def sanitize_device_name(name: str) -> str:
    """Sanitize device name for safe display.
    
    Args:
        name: Raw device name
        
    Returns:
        Sanitized device name
    """
    if not isinstance(name, str):
        return "Unknown Device"
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', name.strip())
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."
    
    return sanitized or "Unknown Device"
