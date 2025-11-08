#!/usr/bin/env python3
"""
Hardware Abstraction Layer

Provides interfaces for:
- SPI bus management
- Display control (ILI9341)
- Keypad input (6x4 matrix)
- Power management (battery, backlight)
"""

from .spi_manager import SPIManager
from .display import DisplayManager
from .keypad import KeypadManager
from .power import PowerManager

__all__ = [
    'SPIManager',
    'DisplayManager',
    'KeypadManager',
    'PowerManager',
]
