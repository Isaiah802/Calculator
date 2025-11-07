"""Compatibility wrapper for firmware.hardware_config.

This wrapper keeps the original import path working while the real
implementation lives under `Calculator.modes.basic.hardware_config`.
Do not add logic here; keep it minimal so it runs quickly on-device.
"""

from Calculator.modes.basic.hardware_config import *

__all__ = [
    'Pins', 'Display', 'Keypad', 'Power', 'Memory', 
    'Communication', 'Performance', 'Validation', 'ErrorCodes',
    'get_hardware_info', 'validate_hardware'
]