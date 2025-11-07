"""
Hardware configuration moved into basic mode namespace.

This is a copy of `firmware/hardware_config.py` so basic-mode code can
import a localized copy. Keep this file self-contained and small.
"""

import machine
from micropython import const

# ================= HARDWARE CONSTANTS =================

# MCU Specifications
MCU_FREQUENCY = const(125_000_000)  # 125MHz default
MCU_CORES = const(2)                # Dual core ARM Cortex-M33

# SPI Configuration
SPI_BUS = const(1)
SPI_BAUDRATE_DISPLAY = const(32_000_000)  # 32MHz for display (fast)
SPI_BAUDRATE_SD = const(2_000_000)        # 2MHz for SD card (safe)
SPI_PHASE = const(0)
SPI_POLARITY = const(0)

# Pin Assignments
class Pins:
    """Hardware pin assignments for Pico 2W"""
    SPI_SCK = const(10)
    SPI_MOSI = const(11)
    SPI_MISO = const(12)
    DISPLAY_CS = const(13)
    DISPLAY_DC = const(15)
    DISPLAY_RST = const(14)
    BACKLIGHT_PWM = const(28)
    SD_CS = const(17)
    KEYPAD_ROWS = [6, 7, 8, 9, 21, 27]
    KEYPAD_COLS = [2, 3, 4, 5]
    BATTERY_ADC = const(26)
    LED_ONBOARD = const(25)

class Display:
    WIDTH = const(320)
    HEIGHT = const(240)
    COLOR_DEPTH = const(16)
    PIXEL_FORMAT = "RGB565"
    BYTES_PER_PIXEL = const(2)
    RESET_DELAY_US = const(100_000)
    INIT_DELAY_US = const(120_000)
    ROTATION_0 = const(0)
    ROTATION_90 = const(1)
    ROTATION_180 = const(2)
    ROTATION_270 = const(3)
    DEFAULT_ROTATION = ROTATION_90

class Keypad:
    ROWS = const(6)
    COLS = const(4)
    TOTAL_KEYS = const(24)
    DEBOUNCE_MS = const(40)
    LONG_PRESS_MS = const(600)
    REPEAT_DELAY_MS = const(500)
    REPEAT_RATE_MS = const(100)
    SCAN_SETTLE_US = const(5)
    SCAN_FREQUENCY_HZ = const(100)
    KEY_MAP = {
        (0, 0): 'C',    (0, 1): '±',    (0, 2): '%',    (0, 3): '÷',
        (1, 0): '7',    (1, 1): '8',    (1, 2): '9',    (1, 3): '×',
        (2, 0): '4',    (2, 1): '5',    (2, 2): '6',    (2, 3): '−',
        (3, 0): '1',    (3, 1): '2',    (3, 2): '3',    (3, 3): '+',
        (4, 0): '0',    (4, 1): '.',    (4, 2): '=',    (4, 3): 'MENU',
        (5, 0): 'F1',   (5, 1): 'F2',   (5, 2): 'F3',   (5, 3): 'ENTER'
    }

class Power:
    BATTERY_MIN = const(3000)
    BATTERY_LOW = const(3300)
    BATTERY_GOOD = const(3700)
    BATTERY_MAX = const(4200)
    ADC_RESOLUTION = const(12)
    ADC_VREF = const(3300)
    ADC_SAMPLES = const(16)
    SLEEP_TIMEOUT_MS = const(90_000)
    DIM_TIMEOUT_MS = const(30_000)
    MIN_BRIGHTNESS = const(10)
    MAX_BRIGHTNESS = const(100)

class Memory:
    HEAP_SIZE_KB = const(264)
    STACK_SIZE_KB = const(8)
    GC_THRESHOLD_KB = const(32)
    MAX_EXPRESSION_LENGTH = const(128)
    MAX_HISTORY_ENTRIES = const(50)
    MAX_VARIABLES = const(26)
    FLASH_SIZE_MB = const(4)
    RESERVED_FLASH_KB = const(1024)

class Communication:
    USB_VID = const(0x2E8A)
    USB_PID = const(0x0005)
    UART_BAUDRATE = const(115200)
    UART_TX = const(0)
    UART_RX = const(1)
    WIFI_COUNTRY = 'US'
    WIFI_TIMEOUT_MS = const(10_000)

class Performance:
    FREQ_LOW = const(48_000_000)
    FREQ_NORMAL = const(125_000_000)
    FREQ_HIGH = const(250_000_000)
    ENABLE_CACHE = True
    PREFETCH_ENABLED = True
    EVAL_TIMEOUT_MS = const(5000)
    MAX_RECURSION_DEPTH = const(100)
    TARGET_FPS = const(30)
    VSYNC_ENABLED = True

class Validation:
    VCC_MIN = const(3100)
    VCC_MAX = const(3500)
    VCC_NOMINAL = const(3300)
    TEMP_MIN = const(-20)
    TEMP_MAX = const(70)
    TEMP_WARNING = const(60)
    CLOCK_TOLERANCE_PPM = const(100)
    GPIO_DRIVE_2MA = const(0)
    GPIO_DRIVE_4MA = const(1)
    GPIO_DRIVE_8MA = const(2)
    GPIO_DRIVE_12MA = const(3)

class ErrorCodes:
    ERR_NONE = const(0)
    ERR_INIT_FAILED = const(1)
    ERR_SPI_TIMEOUT = const(2)
    ERR_DISPLAY_INIT = const(3)
    ERR_KEYPAD_INIT = const(4)
    ERR_SD_MOUNT = const(5)
    ERR_MEMORY_LOW = const(6)
    ERR_VOLTAGE_LOW = const(7)
    ERR_TEMPERATURE_HIGH = const(8)
    ERR_WATCHDOG_TIMEOUT = const(9)
    ERR_STACK_OVERFLOW = const(10)

def get_hardware_info() -> dict:
    return {
        'mcu': 'Raspberry Pi Pico 2W',
        'chip': 'RP2350',
        'cores': MCU_CORES,
        'frequency': MCU_FREQUENCY,
        'ram_kb': Memory.HEAP_SIZE_KB,
        'flash_mb': Memory.FLASH_SIZE_MB,
        'display': f"{Display.WIDTH}x{Display.HEIGHT} ILI9341",
        'keypad': f"{Keypad.ROWS}x{Keypad.COLS} matrix",
        'interfaces': ['SPI', 'USB', 'WiFi', 'ADC', 'PWM']
    }

def validate_hardware() -> tuple:
    errors = []
    all_pins = []
    all_pins.extend([Pins.SPI_SCK, Pins.SPI_MOSI, Pins.SPI_MISO])
    all_pins.extend([Pins.DISPLAY_CS, Pins.DISPLAY_DC, Pins.DISPLAY_RST])
    all_pins.extend([Pins.SD_CS, Pins.BACKLIGHT_PWM, Pins.BATTERY_ADC])
    all_pins.extend(Pins.KEYPAD_ROWS)
    all_pins.extend(Pins.KEYPAD_COLS)
    if len(set(all_pins)) != len(all_pins):
        errors.append("Pin conflict detected")
    for pin in all_pins:
        if pin < 0 or pin > 29:
            errors.append(f"Invalid pin number: {pin}")
    return len(errors) == 0, errors

__all__ = [
    'Pins', 'Display', 'Keypad', 'Power', 'Memory',
    'Communication', 'Performance', 'Validation', 'ErrorCodes',
    'get_hardware_info', 'validate_hardware'
]
