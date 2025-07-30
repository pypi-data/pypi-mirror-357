"""SmartHomeHarmonizer - Bridge IoT devices with voice and GenAI assistants."""

from smarthomeharmonizer.__version__ import __version__
from smarthomeharmonizer.core.app import create_app
from smarthomeharmonizer.core.device_manager import DeviceManager
from smarthomeharmonizer.adapters.base import DeviceAdapter

__all__ = ['__version__', 'create_app', 'DeviceManager', 'DeviceAdapter']
