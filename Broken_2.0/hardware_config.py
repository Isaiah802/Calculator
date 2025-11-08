"""
Hardware Configuration for Peanut 3000 Calculator
Defines pin assignments and hardware settings for Raspberry Pi Pico 2W
"""

from machine import Pin

class Pins:
    """Pin assignments for hardware components"""
    # SPI Pins
    SPI_SCK = 10
    SPI_MOSI = 11
    SPI_MISO = 12
    
    # Display pins
    DISPLAY_CS = 13
    DISPLAY_DC = 15
    DISPLAY_RST = 14
    BACKLIGHT_PWM = 28
    
    # SD Card
    SD_CS = 17
    
    # Power
    BATTERY_ADC = 26
    
    # Keypad
    KEYPAD_COLS = [2, 3, 4, 5]
    KEYPAD_ROWS = [6, 7, 8, 9, 21, 27]

class Display:
    """Display configuration"""
    WIDTH = 320
    HEIGHT = 240
    SPI_BAUDRATE = 32_000_000  # 32MHz
    ROTATION = 0

class Keypad:
    """Keypad configuration"""
    DEBOUNCE_MS = 40
    LONG_PRESS_MS = 600
    SCAN_SETTLE_US = 5

class Power:
    """Power management configuration"""
    BATTERY_MIN_VOLTAGE = 3.0
    BATTERY_MAX_VOLTAGE = 4.2
    LOW_BATTERY_THRESHOLD = 3.3
    CRITICAL_BATTERY_THRESHOLD = 3.1

class Memory:
    """Memory configuration"""
    GC_THRESHOLD = 50000
    MAX_EXPRESSION_LENGTH = 128

class Communication:
    """Communication settings"""
    USB_ENABLED = False
    NETWORK_ENABLED = False

class Performance:
    """Performance settings"""
    MAIN_LOOP_DELAY_MS = 20
    SD_BAUDRATE = 2_000_000  # 2MHz

class Validation:
    """Hardware validation settings"""
    VALIDATE_ON_BOOT = True
    RETRY_COUNT = 3

class ErrorCodes:
    """Error codes for hardware issues"""
    DISPLAY_INIT_FAILED = 1001
    SD_MOUNT_FAILED = 1002
    KEYPAD_INIT_FAILED = 1003
    BATTERY_CRITICAL = 1004

def get_hardware_info():
    """Return hardware information"""
    return {
        'device': 'Raspberry Pi Pico 2W',
        'display': f'{Display.WIDTH}x{Display.HEIGHT}',
        'keypad': f'{len(Keypad.KEYPAD_ROWS)}x{len(Keypad.KEYPAD_COLS)}'
    }

def validate_hardware():
    """Validate hardware configuration"""
    # Basic validation
    assert Display.WIDTH > 0 and Display.HEIGHT > 0
    assert len(Keypad.KEYPAD_ROWS) > 0 and len(Keypad.KEYPAD_COLS) > 0
    return True

__all__ = [
    'Pins', 'Display', 'Keypad', 'Power', 'Memory', 
    'Communication', 'Performance', 'Validation', 'ErrorCodes',
    'get_hardware_info', 'validate_hardware'
]
