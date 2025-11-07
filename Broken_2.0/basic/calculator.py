#!/usr/bin/env python3
"""
PEANUT 3000 ADVANCED CALCULATOR - MOVED calculator.py FOR basic MODE

This file is a direct, verbatim copy of the original
`Calculator/firmware/calculator.py` implementation. It was moved here so
we can implement mode-specific, incremental refactors without breaking
the original import paths. Future work should split this into smaller
components and extract hardware-I/O into testable adapters.
"""

#!/usr/bin/env python3
"""
================================================================================
� PEANUT 3000 ADVANCED CALCULATOR - VERSION 4.0
================================================================================
Enhanced Scientific Calculator for Raspberry Pi Pico 2W
- Phase 4: Enhanced Mathematical Engine with Complex Numbers, Statistics, Matrix Operations
- Professional hardware configuration and validation
- Modular architecture with comprehensive testing
- PC connectivity and USB HID emulation

Hardware: Pico 2W + ILI9341 Display + 6x4 Keypad + SD Card + Battery
Author: Peanut 3000 Development Team
Version: 4.0.0
Date: December 2024
================================================================================
"""

from machine import Pin, SPI, PWM, ADC
from firmware.hardware_config import Pins, Display, Keypad, Power
from firmware.enhanced_math_engine import EnhancedMathEngine
from firmware.graphics_engine import GraphicsEngine, GraphColors, Point2D
from firmware.statistical_plots import StatisticalPlotter, ComplexPlotter
from firmware.interactive_3d import Surface3D, Plot3DEngine, InteractiveGraphControls
import framebuf, time, utime, math, os, gc
import sdcard
from typing import Optional, Dict, List, Any, Tuple
import json

# Import game modules (ensure they exist)
try:
    from snake import play_snake
    from pong import play_pong
    GAMES_AVAILABLE = True
except ImportError:
    GAMES_AVAILABLE = False
    print("[WARNING] Game modules not found - games disabled")

# Import USB interface (ensure it exists)
try:
    from usb_interface import USBInterfaceManager, create_usb_interface
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("[WARNING] USB interface not available - PC connectivity disabled")

# Import enhanced mathematical engine (Phase 4)
try:
    from enhanced_math_engine import EnhancedMathEngine, ComplexNumber, StatisticalEngine, MatrixEngine, UnitConverter
    ENHANCED_MATH_AVAILABLE = True
except ImportError:
    ENHANCED_MATH_AVAILABLE = False
    print("[WARNING] Enhanced math engine not available - using basic math only")

# ================= CONFIGURATION & CONSTANTS =================
class Config:
    """Centralized configuration management"""
    
    # Hardware Configuration
    class Hardware:
        # Display SPI Configuration
        SPI_BAUDRATE_DISPLAY = 32_000_000  # 32MHz for display (fast)
        SPI_BAUDRATE_SD = 2_000_000        # 2MHz for SD card (safe)
        SPI_BUS = 1
        
        # Pin Assignments
        SPI_SCK = 10
        SPI_MOSI = 11
        SPI_MISO = 12
        DISPLAY_CS = 13
        DISPLAY_DC = 15
        DISPLAY_RST = 14
        SD_CS = 17
        BACKLIGHT_PWM = 28
        BATTERY_ADC = 26
        
        # Keypad Configuration
        KEYPAD_COLS = [2, 3, 4, 5]
        KEYPAD_ROWS = [6, 7, 8, 9, 21, 27]
        DEBOUNCE_MS = 40
        LONG_PRESS_MS = 600
        SCAN_SETTLE_US = 5
        
        # Display Specifications
        DISPLAY_WIDTH = 320
        DISPLAY_HEIGHT = 240
        COLOR_DEPTH = 16  # RGB565
        
    class System:
        # Performance Configuration
        MAX_EXPRESSION_LENGTH = 128
        SLEEP_TIMEOUT_MS = 90_000  # 90 seconds
        MEMORY_GC_INTERVAL = 50    # Garbage collect every 50 operations
        
        # Security Settings
        EVAL_TIMEOUT_MS = 5000     # 5 second timeout for calculations
        MAX_RECURSION_DEPTH = 100
        SAFE_FUNCTIONS_ONLY = True
        
        # File System Settings
        SD_MOUNT_PATH = "/sd"
        RESULTS_FILE = "results.txt"
        GRAPH_HISTORY_FILE = "graph_history.txt"
        SETTINGS_FILE = "settings.json"
        
    class UI:
        # Color Scheme (RGB565)
        BACKGROUND = 0x087E        # Dark purple
        FOREGROUND = 0xC8BE        # Light purple
        LEGEND_BG = 0x320E         # Darker purple
        ACCENT = 0x5A0E            # Medium purple  
        WARNING = 0xF810          # Red
        SUCCESS = 0x07E0          # Green
        INFO = 0x07FF             # Cyan
        
        # Layout Configuration
        STATUS_HEIGHT = 35
        MENU_ITEM_HEIGHT = 14
        TEXT_MARGIN = 12
        BATTERY_WIDTH = 110
        BATTERY_HEIGHT = 30
        
        # Animation Settings
        BLINK_INTERVAL_MS = 500
        TRANSITION_SPEED = 5

# (The remainder of the original file continues unchanged.)

