"""Custom exceptions for SmartHomeHarmonizer."""


class SmartHomeHarmonizerError(Exception):
    """Base exception for SmartHomeHarmonizer."""
    pass


class DeviceNotFoundError(SmartHomeHarmonizerError):
    """Raised when a device is not found in the registry."""
    pass


class InvalidCommandError(SmartHomeHarmonizerError):
    """Raised when an invalid command is sent to a device."""
    pass


class AdapterError(SmartHomeHarmonizerError):
    """Raised when there's an error in a device adapter."""
    pass
