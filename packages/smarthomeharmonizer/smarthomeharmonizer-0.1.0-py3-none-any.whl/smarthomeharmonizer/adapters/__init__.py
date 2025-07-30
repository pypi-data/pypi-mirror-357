"""Device adapters for SmartHomeHarmonizer."""

from smarthomeharmonizer.adapters.base import DeviceAdapter
from smarthomeharmonizer.adapters.smart_light import SmartLightAdapter
from smarthomeharmonizer.adapters.thermostat import ThermostatAdapter
from smarthomeharmonizer.adapters.coffee_maker import CoffeeMakerAdapter

__all__ = [
    'DeviceAdapter',
    'SmartLightAdapter',
    'ThermostatAdapter',
    'CoffeeMakerAdapter'
]
