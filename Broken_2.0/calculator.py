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

# Import hardware abstraction layer
from hardware import SPIManager, DisplayManager, KeypadManager, PowerManager

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
        # System Configuration
        MAX_EXPRESSION_LENGTH = 128
        EVAL_TIMEOUT_MS = 1000
        MEMORY_GC_INTERVAL = 50
        SLEEP_TIMEOUT_MS = 300000  # 5 minutes
        SD_MOUNT_PATH = "/sd"
        RESULTS_FILE = "calculations.txt"
        GRAPH_HISTORY_FILE = "graphs.txt"
        
    class UI:
        # UI Colors (RGB565)
        BACKGROUND = 0x0000      # Black
        FOREGROUND = 0xFFFF      # White
        ACCENT = 0x07FF          # Cyan
        SUCCESS = 0x07E0         # Green
        WARNING = 0xFD20         # Orange
        INFO = 0x001F            # Blue
        LEGEND_BG = 0x2104       # Dark grey
        
        # UI Layout
        TEXT_MARGIN = 10
        MENU_ITEM_HEIGHT = 25
        BATTERY_WIDTH = 70
        BATTERY_HEIGHT = 30
        BLINK_INTERVAL_MS = 500

# Global config instance
config = Config()

# Custom exceptions
class HardwareError(Exception):
    """Hardware-related errors"""
    pass

# Helper functions
def constrain(value, min_value, max_value):
    """Constrain value within range"""
    return max(min_value, min(max_value, value))

# ================= LOGGING SYSTEM =================
class Logger:
    """Simple logging system for debugging and monitoring"""
    
    def __init__(self, debug_enabled: bool = True):
        self.debug_enabled = debug_enabled
        self.operation_count = 0
        
    def debug(self, message: str):
        if self.debug_enabled:
            print(f"[DEBUG] {message}")
            
    def info(self, message: str):
        print(f"[INFO] {message}")
        
    def warning(self, message: str):
        print(f"[WARNING] {message}")
        
    def error(self, message: str):
        print(f"[ERROR] {message}")
        
    def operation(self, operation: str):
        """Log mathematical operations"""
        self.operation_count += 1
        if self.debug_enabled:
            print(f"[OP {self.operation_count}] {operation}")

# Global logger instance
logger = Logger()

# ================= HARDWARE ABSTRACTION LAYER =================
# Hardware classes have been extracted to hardware/ module
# See: hardware/spi_manager.py, hardware/display.py, hardware/keypad.py, hardware/power.py

class FileSystemManager:
    """Secure SD card operations with transaction support"""
    
    def __init__(self, spi_manager: SPIManager):
        self.spi_manager = spi_manager
        self.cs_sd = Pin(config.Hardware.SD_CS, Pin.OUT)
        self.sd = None
        self.vfs = None
        self.mounted = False
        self.mount_path = config.System.SD_MOUNT_PATH
        
        self._initialize_sd_card()
        
    def _initialize_sd_card(self, retries: int = 3) -> bool:
        """Initialize and mount SD card"""
        logger.info("Initializing SD card...")
        
        for attempt in range(retries):
            try:
                self.spi_manager.switch_to_sd()
                spi = self.spi_manager.get_spi()
                
                # Ensure chip selects are deselected
                self.cs_sd(1)
                time.sleep_ms(10)
                
                # Initialize SD card
                self.sd = sdcard.SDCard(spi, self.cs_sd)
                self.vfs = os.VfsFat(self.sd)
                
                # Mount filesystem
                try:
                    os.mount(self.vfs, self.mount_path)
                except OSError:
                    # Already mounted or mount point exists
                    pass
                    
                # Verify mount and create directories
                self._create_directory_structure()
                self.mounted = True
                
                logger.info(f"SD card mounted successfully at {self.mount_path}")
                return True
                
            except Exception as e:
                logger.warning(f"SD mount attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(1)
                    
        self.mounted = False
        logger.error("SD card mount failed after all retries")
        return False
        
    def _create_directory_structure(self):
        """Create required directory structure"""
        directories = [
            self.mount_path,
            f"{self.mount_path}/programs",
            f"{self.mount_path}/memos", 
            f"{self.mount_path}/graphs",
            f"{self.mount_path}/backups"
        ]
        
        for directory in directories:
            try:
                os.listdir(directory)
            except OSError:
                try:
                    os.mkdir(directory)
                    logger.debug(f"Created directory: {directory}")
                except OSError as e:
                    logger.warning(f"Failed to create directory {directory}: {e}")
                    
        # Ensure required files exist
        required_files = [
            f"{self.mount_path}/{config.System.RESULTS_FILE}",
            f"{self.mount_path}/{config.System.GRAPH_HISTORY_FILE}"
        ]
        
        for file_path in required_files:
            try:
                with open(file_path, "a") as f:
                    pass  # Touch file
            except Exception as e:
                logger.warning(f"Failed to create file {file_path}: {e}")
                
    def ensure_mounted(self) -> bool:
        """Ensure SD card is mounted"""
        if not self.mounted:
            return self._initialize_sd_card()
        return True
        
    def write_line(self, file_path: str, line: str, append: bool = True) -> bool:
        """Write line to file with transaction safety"""
        if not self.ensure_mounted():
            return False
            
        try:
            self.spi_manager.switch_to_sd()
            
            full_path = f"{self.mount_path}/{file_path}"
            mode = "a" if append else "w"
            
            with open(full_path, mode) as f:
                f.write(line + "\n")
                f.flush()
                
            logger.debug(f"Wrote to {full_path}: {line[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"File write failed: {e}")
            return False
        finally:
            self.spi_manager.switch_to_display()
            
    def read_file(self, file_path: str) -> Optional[List[str]]:
        """Read file and return lines"""
        if not self.ensure_mounted():
            return None
            
        try:
            self.spi_manager.switch_to_sd()
            
            full_path = f"{self.mount_path}/{file_path}"
            with open(full_path, "r") as f:
                lines = f.read().splitlines()
                
            logger.debug(f"Read {len(lines)} lines from {full_path}")
            return lines
            
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return None
        finally:
            self.spi_manager.switch_to_display()
            
    def list_files(self, directory: str = "") -> List[str]:
        """List files in directory"""
        if not self.ensure_mounted():
            return []
            
        try:
            self.spi_manager.switch_to_sd()
            
            full_path = f"{self.mount_path}/{directory}" if directory else self.mount_path
            files = os.listdir(full_path)
            files = [f for f in files if not f.startswith('.')]
            files.sort()
            
            logger.debug(f"Listed {len(files)} files in {full_path}")
            return files
            
        except Exception as e:
            logger.error(f"Directory listing failed: {e}")
            return []
        finally:
            self.spi_manager.switch_to_display()
            
    def delete_file(self, file_path: str) -> bool:
        """Delete file safely"""
        if not self.ensure_mounted():
            return False
            
        try:
            self.spi_manager.switch_to_sd()
            
            full_path = f"{self.mount_path}/{file_path}"
            os.remove(full_path)
            
            logger.info(f"Deleted file: {full_path}")
            return True
            
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False
        finally:
            self.spi_manager.switch_to_display()

# ================= MATHEMATICAL ENGINE =================
class SecureMathEngine:
    """Enhanced mathematical engine with Phase 4 capabilities"""
    
    def __init__(self):
        self.operation_count = 0
        self.last_result = None
        self.precision = 10  # Default decimal places
        
        # Initialize enhanced math engine if available
        if ENHANCED_MATH_AVAILABLE:
            self.enhanced_engine = EnhancedMathEngine()
            print("[INFO] Enhanced mathematical engine initialized")
        else:
            self.enhanced_engine = None
        
        # Safe function whitelist (expanded for Phase 4)
        self.safe_functions = {
            'abs', 'round', 'min', 'max', 'sum',
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
            'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
            'exp', 'log', 'log10', 'log2', 'sqrt', 'pow',
            'floor', 'ceil', 'trunc', 'degrees', 'radians',
            'factorial', 'gamma', 'lgamma', 'erf', 'erfc',
            # Phase 4 additions
            'complex', 'real', 'imag', 'conjugate', 'phase',
            'gcd', 'lcm', 'isfinite', 'isinf', 'isnan',
            'fmod', 'remainder', 'copysign', 'ldexp', 'frexp'
        }
        
        # Create safe globals for eval
        self.safe_globals = {
            "__builtins__": {},
            "math": self._create_safe_math_module(),
            "cmath": self._create_safe_cmath_module() if ENHANCED_MATH_AVAILABLE else {},
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau if hasattr(math, 'tau') else 2 * math.pi,
            "i": 1j if ENHANCED_MATH_AVAILABLE else None,
            "j": 1j if ENHANCED_MATH_AVAILABLE else None
        }
        
        # Phase 4 features
        self.complex_mode = False
        self.angle_mode = "DEG"  # DEG or RAD
        self.statistics_data = []
        self.last_matrix = None
        
    def _create_safe_math_module(self) -> Dict:
        """Create safe math module with whitelisted functions"""
        safe_math = {}
        for func_name in self.safe_functions:
            if hasattr(math, func_name):
                safe_math[func_name] = getattr(math, func_name)
        return safe_math
    
    def _create_safe_cmath_module(self) -> Dict:
        """Create safe complex math module"""
        if not ENHANCED_MATH_AVAILABLE:
            return {}
        
        import cmath
        safe_cmath = {}
        complex_functions = [
            'phase', 'polar', 'rect', 'exp', 'log', 'log10',
            'sqrt', 'acos', 'acosh', 'asin', 'asinh', 'atan', 'atanh',
            'cos', 'cosh', 'sin', 'sinh', 'tan', 'tanh'
        ]
        
        for func_name in complex_functions:
            if hasattr(cmath, func_name):
                safe_cmath[func_name] = getattr(cmath, func_name)
        
        return safe_cmath
        
    def preprocess_expression(self, expr: str) -> str:
        """Preprocess mathematical expression for safety and compatibility"""
        if not expr:
            return expr
            
        # Basic sanitization
        expr = expr.strip()
        
        # Replace common symbols
        replacements = {
            '√': 'math.sqrt',
            'π': str(math.pi),
            '^2': '**2',
            '^': '**',
            '÷': '/',
            '×': '*'
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
            
        # Add math. prefix to known functions
        for func in self.safe_functions:
            if func in expr:
                # Use word boundaries to avoid partial matches
                import re
                pattern = r'\b' + re.escape(func) + r'\('
                replacement = f'math.{func}('
                expr = re.sub(pattern, replacement, expr)
                
        # Handle special cases
        expr = expr.replace('ln(', 'math.log(')
        expr = expr.replace('log(', 'math.log10(')
        
        return expr
        
    def evaluate_expression(self, expr: str) -> Tuple[bool, str]:
        """Safely evaluate mathematical expression"""
        if not expr:
            return False, "Empty expression"
            
        # Security checks
        if len(expr) > config.System.MAX_EXPRESSION_LENGTH:
            return False, "Expression too long"
            
        # Dangerous keywords check
        dangerous = ['import', 'exec', 'eval', '__', 'open', 'file']
        for keyword in dangerous:
            if keyword in expr.lower():
                return False, "Invalid expression"
                
        try:
            # Preprocess expression
            processed_expr = self.preprocess_expression(expr)
            logger.operation(f"Evaluating: {processed_expr}")
            
            # Evaluate with timeout protection (simulated)
            start_time = time.ticks_ms()
            result = eval(processed_expr, self.safe_globals, {})
            eval_time = time.ticks_diff(time.ticks_ms(), start_time)
            
            if eval_time > config.System.EVAL_TIMEOUT_MS:
                return False, "Calculation timeout"
                
            # Validate result
            if isinstance(result, (int, float)):
                if not math.isfinite(result):
                    return False, "Result is infinite or NaN"
                    
                # Format result
                if isinstance(result, float):
                    if abs(result) > 1e10 or (abs(result) < 1e-6 and result != 0):
                        # Scientific notation for very large or small numbers
                        formatted = f"{result:.{self.precision}e}"
                    else:
                        # Regular formatting
                        formatted = f"{result:.{self.precision}g}"
                else:
                    formatted = str(result)
                    
                self.last_result = result
                self.operation_count += 1
                
                # Garbage collection periodically
                if self.operation_count % config.System.MEMORY_GC_INTERVAL == 0:
                    gc.collect()
                    logger.debug("Garbage collection performed")
                    
                return True, formatted
            else:
                return False, "Invalid result type"
                
        except ZeroDivisionError:
            return False, "Division by zero"
        except ValueError as e:
            return False, f"Math error: {str(e)[:20]}"
        except OverflowError:
            return False, "Number too large"
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return False, "Error"
            
    def evaluate_live(self, expr: str) -> str:
        """Evaluate expression for live preview (non-blocking)"""
        success, result = self.evaluate_expression(expr)
        return result if success else ""
        
    def set_precision(self, digits: int):
        """Set calculation precision"""
        self.precision = constrain(digits, 1, 15)
        if self.enhanced_engine:
            self.enhanced_engine.set_precision(digits)
        logger.info(f"Precision set to {self.precision} digits")
    
    # ================= PHASE 4: ENHANCED MATHEMATICAL FEATURES =================
    
    def set_complex_mode(self, enabled: bool):
        """Enable or disable complex number support"""
        self.complex_mode = enabled
        if self.enhanced_engine:
            self.enhanced_engine.set_complex_mode(enabled)
        logger.info(f"Complex mode {'enabled' if enabled else 'disabled'}")
    
    def set_angle_mode(self, mode: str):
        """Set angle mode (DEG or RAD)"""
        if mode not in ["DEG", "RAD"]:
            raise ValueError("Angle mode must be 'DEG' or 'RAD'")
        self.angle_mode = mode
        if self.enhanced_engine:
            self.enhanced_engine.set_angle_mode(mode)
        logger.info(f"Angle mode set to {mode}")
    
    def evaluate_enhanced_expression(self, expr: str) -> Tuple[bool, str]:
        """Evaluate expression using enhanced math engine"""
        if not self.enhanced_engine:
            return self.evaluate_expression(expr)
        
        try:
            result = self.enhanced_engine.evaluate_complex_expression(expr)
            
            if isinstance(result, str) and result.startswith("Error"):
                return False, result
            elif isinstance(result, ComplexNumber):
                if abs(result.imag) < 1e-10:
                    # Effectively real number
                    return True, f"{result.real:.{self.precision}g}"
                else:
                    return True, str(result)
            elif isinstance(result, complex):
                if abs(result.imag) < 1e-10:
                    return True, f"{result.real:.{self.precision}g}"
                else:
                    return True, f"{result.real:.{self.precision}g}{result.imag:+.{self.precision}g}i"
            else:
                return True, f"{result:.{self.precision}g}" if isinstance(result, float) else str(result)
        
        except Exception as e:
            logger.error(f"Enhanced evaluation error: {e}")
            return False, f"Error: {str(e)[:30]}"
    
    def add_statistics_data(self, value: float):
        """Add value to statistics dataset"""
        try:
            self.statistics_data.append(float(value))
            logger.info(f"Added {value} to statistics data (n={len(self.statistics_data)})")
        except ValueError:
            logger.error(f"Invalid value for statistics: {value}")
    
    def clear_statistics_data(self):
        """Clear statistics dataset"""
        self.statistics_data.clear()
        logger.info("Statistics data cleared")
    
    def calculate_statistics(self) -> Tuple[bool, Dict[str, Any]]:
        """Calculate comprehensive statistics"""
        if not self.enhanced_engine or not self.statistics_data:
            return False, {"error": "No data or enhanced engine unavailable"}
        
        try:
            stats = self.enhanced_engine.statistical_analysis(self.statistics_data)
            logger.info(f"Statistics calculated for {len(self.statistics_data)} values")
            return True, stats
        except Exception as e:
            logger.error(f"Statistics calculation error: {e}")
            return False, {"error": str(e)}
    
    def create_matrix(self, data: List[List[float]]) -> Tuple[bool, str]:
        """Create and store matrix"""
        if not self.enhanced_engine:
            return False, "Enhanced math engine required for matrix operations"
        
        try:
            matrix = self.enhanced_engine.create_matrix(data)
            self.last_matrix = matrix
            logger.info(f"Created {matrix.rows}x{matrix.cols} matrix")
            return True, f"Matrix {matrix.rows}x{matrix.cols} created"
        except Exception as e:
            logger.error(f"Matrix creation error: {e}")
            return False, f"Error: {str(e)[:30]}"
    
    def matrix_operation(self, operation: str, other_data: List[List[float]] = None) -> Tuple[bool, str]:
        """Perform matrix operations"""
        if not self.enhanced_engine or not self.last_matrix:
            return False, "No matrix available or enhanced engine required"
        
        try:
            if operation == "determinant":
                det = self.last_matrix.determinant()
                return True, f"det = {det:.{self.precision}g}"
            
            elif operation == "transpose":
                result = self.last_matrix.transpose()
                self.last_matrix = result
                return True, f"Matrix transposed ({result.rows}x{result.cols})"
            
            elif operation == "inverse":
                result = self.last_matrix.inverse()
                self.last_matrix = result
                return True, "Matrix inverted"
            
            elif operation == "eigenvalues" and self.last_matrix.rows == 2 and self.last_matrix.cols == 2:
                λ1, λ2 = self.last_matrix.eigenvalues_2x2()
                return True, f"λ₁={λ1}, λ₂={λ2}"
            
            elif operation in ["add", "subtract", "multiply"] and other_data:
                other_matrix = self.enhanced_engine.create_matrix(other_data)
                
                if operation == "add":
                    result = self.last_matrix + other_matrix
                elif operation == "subtract":
                    result = self.last_matrix - other_matrix
                elif operation == "multiply":
                    result = self.last_matrix * other_matrix
                
                self.last_matrix = result
                return True, f"Matrix {operation} completed"
            
            else:
                return False, "Invalid operation or missing operand"
        
        except Exception as e:
            logger.error(f"Matrix operation error: {e}")
            return False, f"Error: {str(e)[:30]}"
    
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Tuple[bool, str]:
        """Convert between units"""
        if not self.enhanced_engine:
            return False, "Enhanced engine required for unit conversion"
        
        try:
            result = self.enhanced_engine.unit_conversion(value, from_unit, to_unit)
            conversion_str = f"{value} {from_unit} = {result:.{self.precision}g} {to_unit}"
            logger.info(f"Unit conversion: {conversion_str}")
            return True, conversion_str
        except Exception as e:
            logger.error(f"Unit conversion error: {e}")
            return False, f"Error: {str(e)[:30]}"
    
    def get_available_units(self, category: str = None) -> Dict[str, List[str]]:
        """Get available units by category"""
        if not self.enhanced_engine:
            return {}
        return self.enhanced_engine.get_available_units(category)
    
    def get_constants(self) -> Dict[str, float]:
        """Get mathematical and physical constants"""
        if self.enhanced_engine:
            return self.enhanced_engine.constants
        else:
            return {
                'pi': math.pi,
                'e': math.e,
                'phi': (1 + math.sqrt(5)) / 2
            }

# ================= USER INTERFACE SYSTEM =================
class UIManager:
    """Modern user interface management system"""
    
    def __init__(self, display: DisplayManager, power: PowerManager):
        self.display = display
        self.power = power
        self.blink_state = False
        self.last_blink = 0
        
    def draw_status_bar(self, shift_mode: bool, battery_voltage: float, battery_percent: int):
        """Draw modern status bar with system information"""
        # Title centered
        title = "Peanut 3000"
        title_x = (self.display.width - len(title) * 8) // 2
        self.display.draw_text(title_x, 4, title, config.UI.FOREGROUND)
        
        # Shift indicator
        if shift_mode:
            self.display.fill_rect(4, 4, 44, 16, config.UI.LEGEND_BG)
            self.display.draw_rect(4, 4, 44, 16, config.UI.ACCENT)
            self.display.draw_text(8, 8, 'SHIFT', config.UI.ACCENT)
            
        # Battery indicator (modern design)
        batt_x = self.display.width - config.UI.BATTERY_WIDTH - 4
        batt_y = 4
        
        # Battery background
        self.display.fill_rect(batt_x, batt_y, config.UI.BATTERY_WIDTH, 
                              config.UI.BATTERY_HEIGHT, config.UI.LEGEND_BG)
        self.display.draw_rect(batt_x, batt_y, config.UI.BATTERY_WIDTH,
                              config.UI.BATTERY_HEIGHT, config.UI.ACCENT)
        
        # Battery voltage
        self.display.draw_text(batt_x + 4, batt_y + 4, f"{battery_voltage:.2f}V",
                              config.UI.FOREGROUND)
        
        # Battery level bar
        bar_x, bar_y = batt_x + 4, batt_y + 16
        bar_w, bar_h = 60, 8
        
        self.display.draw_rect(bar_x, bar_y, bar_w, bar_h, config.UI.FOREGROUND)
        
        # Fill bar based on percentage
        fill_w = int(constrain(battery_percent, 0, 100) / 100 * (bar_w - 2))
        if fill_w > 0:
            # Color based on battery level
            if battery_percent > 50:
                bar_color = config.UI.SUCCESS
            elif battery_percent > 20:
                bar_color = config.UI.FOREGROUND
            else:
                bar_color = config.UI.WARNING
                
            self.display.fill_rect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, bar_color)
            
        # Charging indicator (blinking)
        charge_x = bar_x + bar_w + 6
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_blink) > config.UI.BLINK_INTERVAL_MS:
            self.blink_state = not self.blink_state
            self.last_blink = now
            
        if self.blink_state:
            self.display.fill_rect(charge_x, bar_y, 10, bar_h, config.UI.INFO)
        else:
            self.display.draw_rect(charge_x, bar_y, 10, bar_h, config.UI.INFO)
            
    def draw_menu_item(self, x: int, y: int, text: str, selected: bool, width: int = 200):
        """Draw a menu item with modern styling"""
        if selected:
            self.display.fill_rect(x - 4, y - 2, width, config.UI.MENU_ITEM_HEIGHT, 
                                  config.UI.LEGEND_BG)
            self.display.draw_rect(x - 4, y - 2, width, config.UI.MENU_ITEM_HEIGHT,
                                  config.UI.ACCENT)
            prefix = "► "
        else:
            prefix = "  "
            
        self.display.draw_text(x, y, prefix + text, config.UI.FOREGROUND)
        
    def draw_input_field(self, x: int, y: int, label: str, value: str, focused: bool = False):
        """Draw input field with label"""
        # Label
        self.display.draw_text(x, y, f"{label}:", config.UI.FOREGROUND)
        
        # Value with cursor
        value_y = y + 20
        display_value = value if len(value) <= 35 else "..." + value[-32:]
        
        if focused and self.blink_state:
            display_value += "_"
            
        self.display.draw_text(x, value_y, display_value, config.UI.FOREGROUND)
        
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """Show temporary message overlay"""
        # Choose color based on type
        color_map = {
            "info": config.UI.INFO,
            "warning": config.UI.WARNING,
            "error": config.UI.WARNING,
            "success": config.UI.SUCCESS
        }
        
        color = color_map.get(msg_type, config.UI.INFO)
        
        # Center message box
        box_w, box_h = 280, 80
        box_x = (self.display.width - box_w) // 2
        box_y = (self.display.height - box_h) // 2
        
        # Draw message box
        self.display.fill_rect(box_x, box_y, box_w, box_h, config.UI.LEGEND_BG)
        self.display.draw_rect(box_x, box_y, box_w, box_h, color)
        
        # Title
        title_x = box_x + (box_w - len(title) * 8) // 2
        self.display.draw_text(title_x, box_y + 10, title, color)
        
        # Message (wrap if needed)
        msg_x = box_x + 10
        msg_y = box_y + 30
        
        if len(message) <= 30:
            self.display.draw_text(msg_x, msg_y, message, config.UI.FOREGROUND)
        else:
            # Simple word wrapping
            words = message.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + word) <= 30:
                    current_line += word + " "
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
                    
            if current_line:
                lines.append(current_line.strip())
                
            for i, line in enumerate(lines[:2]):  # Max 2 lines
                self.display.draw_text(msg_x, msg_y + i * 12, line, config.UI.FOREGROUND)

# ================= APPLICATION STATE MANAGEMENT =================
class AppState:
    """Application state manager"""
    
    def __init__(self):
        # Calculator state
        self.current_expression = ""
        self.last_result = ""
        self.shift_mode = False
        
        # UI state
        self.current_mode = "calc"  # calc, menu, files, settings, graph, viewer
        self.menu_index = 0
        self.settings_index = 0
        
        # File browser state
        self.file_list = []
        self.file_index = 0
        self.viewer_file = None
        self.viewer_scroll = 0
        
        # Graph state
        self.graph_expression = "sin(x)"
        self.graph_x_min = -10.0
        self.graph_y_min = -5.0
        self.graph_x_range = 20.0
        self.graph_y_range = 10.0
        
        # System state
        self.last_activity = time.ticks_ms()
        self.brightness = 60
        self.debug_mode = True
        self.sleep_timeout = config.System.SLEEP_TIMEOUT_MS
        
        # Menu items (Phase 4 enhanced)
        self.menu_items = ["Calculator", "File Browser", "Settings", "Graph"]
        if GAMES_AVAILABLE:
            self.menu_items.append("Games")
        
        # Phase 4 menu items
        if ENHANCED_MATH_AVAILABLE:
            self.menu_items.extend(["Statistics", "Matrix", "Units", "Complex"])
        
        self.phase4_mode = None  # Track Phase 4 submodes
            
    def reset_activity(self):
        """Reset activity timer"""
        self.last_activity = time.ticks_ms()
        
    def get_inactive_time(self) -> int:
        """Get time since last activity in milliseconds"""
        return time.ticks_diff(time.ticks_ms(), self.last_activity)
        
    def switch_mode(self, new_mode: str):
        """Switch application mode"""
        if new_mode in ["calc", "menu", "files", "settings", "graph", "viewer"]:
            self.current_mode = new_mode
            logger.info(f"Switched to {new_mode} mode")
            self.reset_activity()

# ================= CALCULATOR APPLICATION =================
class CalculatorApp:
    """Main calculator application class"""
    
    def __init__(self):
        logger.info("Initializing Peanut 3000 Calculator...")
        
        # Initialize hardware managers
        self.spi_manager = SPIManager(config, logger, HardwareError)
        self.display = DisplayManager(self.spi_manager, config, logger, HardwareError)
        self.keypad = KeypadManager(config, logger)
        self.power = PowerManager(config, logger)
        self.filesystem = FileSystemManager(self.spi_manager)
        
        # Initialize software systems
        self.math_engine = SecureMathEngine()
        self.ui = UIManager(self.display, self.power)
        
        # Phase 5: Initialize Advanced Graphing System
        self.graphics_engine = GraphicsEngine(self.display)
        self.statistical_plotter = StatisticalPlotter(self.graphics_engine)
        self.complex_plotter = ComplexPlotter(self.graphics_engine)
        self.interactive_controls = InteractiveGraphControls(self.graphics_engine)
        
        # Current surface for 3D plotting
        self.current_3d_surface = None
        self.state = AppState()
        
        # Initialize USB interface (PC connectivity)
        self.usb_interface = None
        if USB_AVAILABLE:
            try:
                self.usb_interface = create_usb_interface()
                if self.usb_interface:
                    logger.info("USB PC connectivity enabled")
                else:
                    logger.warning("USB interface creation failed")
            except Exception as e:
                logger.error(f"USB initialization failed: {e}")
                
        # Application running flag
        self.running = True
        
        logger.info("Calculator initialization complete")
        
    def handle_calculator_mode(self, key: str, event_type: str):
        """Handle calculator mode input"""
        if event_type != "tap":
            return
            
        if key == "=":
            # Use enhanced evaluation if available and complex mode is enabled
            if ENHANCED_MATH_AVAILABLE and self.math_engine.complex_mode:
                success, result = self.math_engine.evaluate_enhanced_expression(self.state.current_expression)
            else:
                success, result = self.math_engine.evaluate_expression(self.state.current_expression)
            
            self.state.last_result = result
            
            # Save successful calculations
            if success and result != "Error":
                calculation = f"{self.state.current_expression} = {result}"
                self.filesystem.write_line(config.System.RESULTS_FILE, calculation)
                
            # Send to PC via USB
            if self.usb_interface:
                self.usb_interface.process_calculator_input(
                    key, self.state.current_expression, result
                )
                
        elif key == "DEL":
            if self.state.current_expression:
                self.state.current_expression = self.state.current_expression[:-1]
                
        elif key == "C":
            self.state.current_expression = ""
            self.state.last_result = ""
            
        elif key == "Save":
            if self.state.current_expression and self.state.last_result:
                calculation = f"{self.state.current_expression} = {self.state.last_result}"
                self.filesystem.write_line(config.System.RESULTS_FILE, calculation)
                
        else:
            # Add to expression with length limit
            if len(self.state.current_expression) < config.System.MAX_EXPRESSION_LENGTH:
                # Handle special symbols
                if key == "^2":
                    self.state.current_expression += "**2"
                elif key == "√":
                    self.state.current_expression += "√("
                else:
                    self.state.current_expression += key
                    
        # Send all keystrokes to PC (numpad emulation)
        if self.usb_interface:
            self.usb_interface.process_calculator_input(
                key, self.state.current_expression, self.state.last_result
            )
                    
    def handle_menu_mode(self, key: str, event_type: str):
        """Handle menu mode input"""
        if event_type != "tap":
            return
            
        if key == "2":  # Up
            self.state.menu_index = (self.state.menu_index - 1) % len(self.state.menu_items)
        elif key == "8":  # Down
            self.state.menu_index = (self.state.menu_index + 1) % len(self.state.menu_items)
        elif key == "=":  # Select
            selected = self.state.menu_items[self.state.menu_index]
            if selected == "Calculator":
                self.state.switch_mode("calc")
            elif selected == "File Browser":
                self.refresh_file_list()
                self.state.switch_mode("files")
            elif selected == "Settings":
                self.state.switch_mode("settings")
            elif selected == "Graph":
                self.state.switch_mode("graph")
            elif selected == "Games" and GAMES_AVAILABLE:
                self.run_game_menu()
            # Phase 4 menu items
            elif selected == "Statistics" and ENHANCED_MATH_AVAILABLE:
                self.state.phase4_mode = "statistics"
                self.state.switch_mode("phase4")
            elif selected == "Matrix" and ENHANCED_MATH_AVAILABLE:
                self.state.phase4_mode = "matrix"
                self.state.switch_mode("phase4")
            elif selected == "Units" and ENHANCED_MATH_AVAILABLE:
                self.state.phase4_mode = "units"
                self.state.switch_mode("phase4")
            elif selected == "Complex" and ENHANCED_MATH_AVAILABLE:
                self.state.phase4_mode = "complex"
                self.math_engine.set_complex_mode(True)
                self.state.switch_mode("calc")  # Return to calculator with complex mode
        elif key == "C":  # Back
            self.state.switch_mode("calc")
            
    def handle_graph_mode(self, key: str, event_type: str):
        """Handle advanced graph mode input - Phase 5 Enhanced"""
        if event_type != "tap":
            return
        
        # Handle interactive graph controls
        redraw_needed = self.interactive_controls.handle_key_press(key)
        
        # Mode-specific actions
        if key == "C":
            # Return to main menu
            self.state.switch_mode("menu")
            return
        elif key == "=":
            # Render the current graph
            self._render_current_graph()
        elif key == "F3":
            # Switch between graph types
            self._cycle_graph_type()
            redraw_needed = True
        elif key == "ENTER":
            # Auto-scale or execute function
            if self.graphics_engine.function_expression:
                self.graphics_engine.auto_scale()
                redraw_needed = True
        elif key == "MENU":
            # Graph options menu
            self._show_graph_options()
        elif key == "DEL":
            # Edit function expression
            if self.state.graph_expression:
                self.state.graph_expression = self.state.graph_expression[:-1]
                self.graphics_engine.function_expression = self.state.graph_expression
                redraw_needed = True
        else:
            # Function expression input
            if len(self.state.graph_expression) < 64:  # Function length limit
                if key == "^2":
                    self.state.graph_expression += "**2"
                elif key == "√":
                    self.state.graph_expression += "sqrt("
                elif key == "sin":
                    self.state.graph_expression += "sin("
                elif key == "cos":
                    self.state.graph_expression += "cos("
                elif key == "π":
                    self.state.graph_expression += "pi"
                elif key == "e":
                    self.state.graph_expression += "e"
                elif key == "ln":
                    self.state.graph_expression += "log("
                else:
                    self.state.graph_expression += key
                
                # Update graphics engine
                self.graphics_engine.function_expression = self.state.graph_expression
                redraw_needed = True
        
        # Redraw if needed
        if redraw_needed:
            self._render_current_graph()
    
    def _render_current_graph(self):
        """Render the current graph based on mode"""
        try:
            if self.interactive_controls.mode == "3D":
                # Render 3D surface
                if self.current_3d_surface:
                    self.interactive_controls.plot_3d.render_3d_scene(self.current_3d_surface)
                else:
                    # Create surface from current function
                    if self.graphics_engine.function_expression:
                        # For 3D, assume function of x and y
                        expr_3d = self.graphics_engine.function_expression.replace('x', 'x').replace('y', 'y')
                        self.current_3d_surface = Surface3D(expr_3d)
                        self.current_3d_surface.generate_mesh(self.graphics_engine.math_engine)
                        self.interactive_controls.plot_3d.render_3d_scene(self.current_3d_surface)
            else:
                # Render 2D graph
                show_data = len(self.graphics_engine.data_points) > 0
                show_regression = hasattr(self.state, 'show_regression') and self.state.show_regression
                
                self.graphics_engine.render_complete_graph(
                    show_grid=True,
                    show_axes=True,
                    show_function=bool(self.graphics_engine.function_expression),
                    show_data=show_data,
                    show_regression=show_regression
                )
            
            # Show status information
            self._show_graph_status()
            
        except Exception as e:
            # Error handling
            self.ui.draw_message(f"Graph Error: {str(e)[:20]}", config.UI.WARNING)
    
    def _cycle_graph_type(self):
        """Cycle through different graph visualization types"""
        if not hasattr(self.state, 'graph_type'):
            self.state.graph_type = "function"
        
        types = ["function", "scatter", "histogram", "3D", "complex"]
        current_index = types.index(self.state.graph_type) if self.state.graph_type in types else 0
        next_index = (current_index + 1) % len(types)
        self.state.graph_type = types[next_index]
        
        # Configure graphics engine for new type
        if self.state.graph_type == "3D":
            self.interactive_controls.mode = "3D"
        elif self.state.graph_type == "complex":
            # Switch to complex plane visualization
            if hasattr(self.graphics_engine.math_engine, 'complex_numbers'):
                complex_data = self.graphics_engine.math_engine.complex_numbers
                self.complex_plotter.plot_complex_plane(complex_data)
        elif self.state.graph_type == "scatter":
            # Use data points for scatter plot
            if self.graphics_engine.data_points:
                x_data = [p[0] for p in self.graphics_engine.data_points]
                y_data = [p[1] for p in self.graphics_engine.data_points]
                self.statistical_plotter.plot_scatter(x_data, y_data, show_regression=True)
        elif self.state.graph_type == "histogram":
            # Generate histogram from y-values
            if self.graphics_engine.data_points:
                y_values = [p[1] for p in self.graphics_engine.data_points]
                self.statistical_plotter.set_data(y_values)
                self.statistical_plotter.plot_histogram()
        else:
            # Standard function plotting
            self.interactive_controls.mode = "2D"
    
    def _show_graph_options(self):
        """Show graph configuration options"""
        options = [
            "Grid: ON/OFF",
            "Trace: ON/OFF", 
            "Auto-Scale",
            "Reset View",
            "Export Graph",
            "3D Settings"
        ]
        
        # Simple menu display (would be enhanced with proper UI)
        self.ui.draw_menu(options)
    
    def _show_graph_status(self):
        """Show current graph status and coordinates"""
        status_text = self.interactive_controls.get_mode_status()
        
        # Show bounds information
        bounds = self.graphics_engine.bounds
        bounds_text = f"X:[{bounds.x_min:.2f},{bounds.x_max:.2f}] Y:[{bounds.y_min:.2f},{bounds.y_max:.2f}]"
        
        # Display status (would be rendered properly on actual display)
        self.ui.draw_text(status_text, 10, 10, config.UI.INFO)
        self.ui.draw_text(bounds_text, 10, 25, config.UI.FOREGROUND)
                    
    def handle_phase4_mode(self, key: str, event_type: str):
        """Handle Phase 4 enhanced mathematical features"""
        if event_type != "tap":
            return
            
        if key == "C":  # Back to menu
            self.state.switch_mode("menu")
            return
            
        if not ENHANCED_MATH_AVAILABLE:
            self.display.clear()
            self.display.draw_text(10, 100, "Enhanced math not available", config.UI.WARNING)
            self.display.update()
            return
            
        submode = self.state.phase4_mode
        
        if submode == "statistics":
            self.handle_statistics_mode(key)
        elif submode == "matrix":
            self.handle_matrix_mode(key)
        elif submode == "units":
            self.handle_units_mode(key)
        elif submode == "complex":
            self.handle_complex_mode(key)
    
    def handle_statistics_mode(self, key: str):
        """Handle statistics operations"""
        if key == "1":  # Add current result to dataset
            if self.state.last_result and self.state.last_result != "Error":
                try:
                    value = float(self.state.last_result)
                    self.math_engine.add_statistics_data(value)
                    self.state.status_message = f"Added {value} to dataset"
                except ValueError:
                    self.state.status_message = "Invalid number for statistics"
        
        elif key == "2":  # Calculate statistics
            success, stats = self.math_engine.calculate_statistics()
            if success:
                # Display key statistics
                self.state.last_result = f"n={stats['count']} μ={stats['mean']:.3f} σ={stats['std_dev']:.3f}"
                self.state.status_message = "Statistics calculated"
            else:
                self.state.status_message = stats.get('error', 'Statistics error')
        
        elif key == "3":  # Clear dataset
            self.math_engine.clear_statistics_data()
            self.state.status_message = "Statistics data cleared"
        
        elif key == "=":  # Show detailed statistics
            success, stats = self.math_engine.calculate_statistics()
            if success:
                # Cycle through different statistics
                stat_keys = ['mean', 'median', 'std_dev', 'variance', 'skewness', 'kurtosis']
                if not hasattr(self.state, 'stat_index'):
                    self.state.stat_index = 0
                
                if self.state.stat_index < len(stat_keys):
                    key_name = stat_keys[self.state.stat_index]
                    value = stats[key_name]
                    self.state.last_result = f"{key_name}: {value:.6g}"
                    self.state.stat_index = (self.state.stat_index + 1) % len(stat_keys)
    
    def handle_matrix_mode(self, key: str):
        """Handle matrix operations"""
        if key == "1":  # Create 2x2 matrix from current values
            # Simple 2x2 identity matrix for demo
            matrix_data = [[1, 0], [0, 1]]
            success, result = self.math_engine.create_matrix(matrix_data)
            self.state.status_message = result
        
        elif key == "2":  # Matrix determinant
            success, result = self.math_engine.matrix_operation("determinant")
            if success:
                self.state.last_result = result
            self.state.status_message = result if not success else "Determinant calculated"
        
        elif key == "3":  # Matrix transpose
            success, result = self.math_engine.matrix_operation("transpose")
            self.state.status_message = result
        
        elif key == "4":  # Matrix inverse
            success, result = self.math_engine.matrix_operation("inverse")
            self.state.status_message = result
        
        elif key == "5":  # Eigenvalues (2x2 only)
            success, result = self.math_engine.matrix_operation("eigenvalues")
            if success:
                self.state.last_result = result
            self.state.status_message = result if not success else "Eigenvalues calculated"
    
    def handle_units_mode(self, key: str):
        """Handle unit conversions"""
        # Simple demonstration - more sophisticated input needed for full implementation
        conversions = {
            "1": ("100", "cm", "m"),      # 100 cm to m
            "2": ("32", "F", "C"),        # 32°F to °C
            "3": ("1", "hp", "W"),        # 1 hp to W
            "4": ("1", "mi", "km"),       # 1 mile to km
            "5": ("1", "gal", "L"),       # 1 gallon to L
            "6": ("1", "lb", "kg"),       # 1 pound to kg
        }
        
        if key in conversions:
            value_str, from_unit, to_unit = conversions[key]
            value = float(value_str)
            success, result = self.math_engine.convert_units(value, from_unit, to_unit)
            if success:
                self.state.last_result = result
                self.state.status_message = "Conversion complete"
            else:
                self.state.status_message = result
        
        elif key == "=":  # Show available unit categories
            units = self.math_engine.get_available_units()
            categories = list(units.keys())
            if not hasattr(self.state, 'unit_cat_index'):
                self.state.unit_cat_index = 0
            
            if self.state.unit_cat_index < len(categories):
                cat = categories[self.state.unit_cat_index]
                self.state.last_result = f"{cat}: {len(units[cat])} units"
                self.state.unit_cat_index = (self.state.unit_cat_index + 1) % len(categories)
    
    def handle_complex_mode(self, key: str):
        """Handle complex number operations"""
        # Complex mode is handled in regular calculator mode
        # This is just for demonstration
        if key == "1":
            self.state.current_expression = "3+4j"
            
    def handle_phase5_mode(self, key: str, event_type: str):
        """Handle Phase 5 Advanced Graphing mode"""
        if event_type != "tap":
            return
        
        # Get current Phase 5 submode
        submode = getattr(self.state, 'phase5_submode', 'main')
        
        if submode == "main":
            # Main Phase 5 menu
            if key == "1":
                # 2D Function Graphing
                self.state.phase5_submode = "function_2d"
                self.state.switch_mode("graph")  # Switch to enhanced graph mode
                self.interactive_controls.mode = "2D"
            elif key == "2":
                # 3D Surface Plotting
                self.state.phase5_submode = "surface_3d"
                self.state.switch_mode("graph")
                self.interactive_controls.mode = "3D"
            elif key == "3":
                # Statistical Plots
                self.state.phase5_submode = "statistics"
                self._show_statistical_plots_menu()
            elif key == "4":
                # Complex Number Visualization
                self.state.phase5_submode = "complex"
                self._show_complex_plots()
            elif key == "5":
                # Interactive Data Analysis
                self.state.phase5_submode = "data_analysis"
                self._show_data_analysis_menu()
            elif key == "6":
                # Graph Export Options
                self.state.phase5_submode = "export"
                self._show_export_menu()
            elif key == "C":
                # Return to main menu
                self.state.switch_mode("menu")
        
        elif submode == "statistics":
            self.handle_statistical_plots(key)
        elif submode == "complex":
            self.handle_complex_plots(key)
        elif submode == "data_analysis":
            self.handle_data_analysis(key)
        elif submode == "export":
            self.handle_graph_export(key)
    
    def handle_statistical_plots(self, key: str):
        """Handle statistical plotting options"""
        if key == "1":
            # Histogram
            if hasattr(self.math_engine, 'statistics_data') and self.math_engine.statistics_data:
                self.statistical_plotter.set_data(self.math_engine.statistics_data)
                self.statistical_plotter.plot_histogram()
                self.state.status_message = "Histogram plotted"
            else:
                self.state.status_message = "No data for histogram"
        
        elif key == "2":
            # Scatter Plot (need x,y data pairs)
            if len(self.graphics_engine.data_points) > 0:
                x_data = [p[0] for p in self.graphics_engine.data_points]
                y_data = [p[1] for p in self.graphics_engine.data_points]
                self.statistical_plotter.plot_scatter(x_data, y_data, show_regression=True)
                self.state.status_message = "Scatter plot with regression"
            else:
                self.state.status_message = "Need data points for scatter plot"
        
        elif key == "3":
            # Box Plot
            if hasattr(self.math_engine, 'statistics_data') and self.math_engine.statistics_data:
                self.statistical_plotter.set_data(self.math_engine.statistics_data)
                result = self.statistical_plotter.plot_box_plot()
                if result:
                    self.state.last_result = f"Q1={result['q1']:.2f} Med={result['median']:.2f} Q3={result['q3']:.2f}"
                self.state.status_message = "Box plot displayed"
            else:
                self.state.status_message = "No data for box plot"
        
        elif key == "4":
            # Time Series
            if len(self.graphics_engine.data_points) > 0:
                # Assume first column is time, second is value
                time_data = [p[0] for p in self.graphics_engine.data_points]
                value_data = [p[1] for p in self.graphics_engine.data_points]
                self.statistical_plotter.plot_time_series(time_data, value_data)
                self.state.status_message = "Time series plotted"
            else:
                self.state.status_message = "Need time-series data"
        
        elif key == "C":
            self.state.phase5_submode = "main"
    
    def handle_complex_plots(self, key: str):
        """Handle complex number visualization"""
        if key == "1":
            # Complex Plane Plot
            # Generate some complex numbers for demonstration
            complex_numbers = [
                complex(1, 2), complex(-1, 1), complex(2, -1),
                complex(-2, -2), complex(0, 3), complex(3, 0)
            ]
            self.complex_plotter.plot_complex_plane(complex_numbers)
            self.state.status_message = "Complex plane plotted"
        
        elif key == "2":
            # Mandelbrot Set
            self.complex_plotter.plot_mandelbrot_zoom()
            self.state.status_message = "Mandelbrot set rendered"
        
        elif key == "3":
            # Complex Function Visualization
            if self.graphics_engine.function_expression:
                # Parse complex function and visualize
                self.state.status_message = "Complex function plotting"
            else:
                self.state.status_message = "Enter complex function"
        
        elif key == "C":
            self.state.phase5_submode = "main"
    
    def handle_data_analysis(self, key: str):
        """Handle interactive data analysis"""
        if key == "1":
            # Add current result as data point
            if self.state.last_result and self.state.last_result != "Error":
                try:
                    # Add as (index, value) pair
                    index = len(self.graphics_engine.data_points)
                    value = float(self.state.last_result)
                    self.graphics_engine.data_points.append((index, value))
                    self.state.status_message = f"Added point ({index}, {value})"
                except ValueError:
                    self.state.status_message = "Invalid data point"
        
        elif key == "2":
            # Clear all data points
            self.graphics_engine.data_points.clear()
            self.state.status_message = "Data points cleared"
        
        elif key == "3":
            # Analyze current data
            if len(self.graphics_engine.data_points) > 1:
                x_data = [p[0] for p in self.graphics_engine.data_points]
                y_data = [p[1] for p in self.graphics_engine.data_points]
                
                # Calculate correlation
                from firmware.enhanced_math_engine import StatisticalEngine
                stats = StatisticalEngine()
                correlation = stats.correlation(x_data, y_data)
                slope, intercept, r_squared = stats.linear_regression(x_data, y_data)
                
                self.state.last_result = f"r={correlation:.3f} R²={r_squared:.3f}"
                self.state.status_message = "Data analysis complete"
            else:
                self.state.status_message = "Need more data points"
        
        elif key == "C":
            self.state.phase5_submode = "main"
    
    def handle_graph_export(self, key: str):
        """Handle graph export options"""
        if key == "1":
            # Save to SD card
            try:
                self.filesystem.save_graph_data(self.graphics_engine.data_points)
                self.state.status_message = "Graph saved to SD card"
            except:
                self.state.status_message = "SD card save failed"
        
        elif key == "2":
            # Export via USB
            if self.usb_interface:
                try:
                    self.usb_interface.send_graph_data(self.graphics_engine.data_points)
                    self.state.status_message = "Graph data sent to PC"
                except:
                    self.state.status_message = "USB export failed"
            else:
                self.state.status_message = "USB not available"
        
        elif key == "3":
            # Print graph parameters
            bounds = self.graphics_engine.bounds
            self.state.last_result = f"X:[{bounds.x_min:.2f},{bounds.x_max:.2f}] Y:[{bounds.y_min:.2f},{bounds.y_max:.2f}]"
            self.state.status_message = "Graph bounds displayed"
        
        elif key == "C":
            self.state.phase5_submode = "main"
    
    def _show_statistical_plots_menu(self):
        """Display statistical plots menu"""
        menu_items = [
            "1: Histogram",
            "2: Scatter Plot", 
            "3: Box Plot",
            "4: Time Series",
            "C: Back"
        ]
        self.ui.draw_menu(menu_items)
    
    def _show_complex_plots(self):
        """Display complex plotting options"""
        menu_items = [
            "1: Complex Plane",
            "2: Mandelbrot Set",
            "3: Complex Function",
            "C: Back"
        ]
        self.ui.draw_menu(menu_items)
    
    def _show_data_analysis_menu(self):
        """Display data analysis options"""
        menu_items = [
            "1: Add Data Point",
            "2: Clear Data",
            "3: Analyze Data",
            "C: Back"
        ]
        self.ui.draw_menu(menu_items)
    
    def _show_export_menu(self):
        """Display export options"""
        menu_items = [
            "1: Save to SD",
            "2: Export USB",
            "3: Show Bounds",
            "C: Back"
        ]
        self.ui.draw_menu(menu_items)
                    
    def handle_global_keys(self, key: str, event_type: str) -> bool:
        """Handle global key combinations, return True if handled"""
        if key == "S" and event_type == "tap":
            self.state.shift_mode = not self.state.shift_mode
            return True
            
        if key == "ON":
            if self.state.shift_mode and event_type in ("tap", "long"):
                # SHIFT+ON -> Main menu
                self.state.switch_mode("menu")
                self.state.shift_mode = False
                return True
            elif event_type == "long":
                # Long ON -> Settings
                self.state.switch_mode("settings")
                return True
                
        return False
        
    def refresh_file_list(self):
        """Refresh file browser list"""
        self.state.file_list = self.filesystem.list_files()
        if self.state.file_index >= len(self.state.file_list):
            self.state.file_index = max(0, len(self.state.file_list) - 1)
            
    def run_game_menu(self):
        """Simple game menu"""
        if not GAMES_AVAILABLE:
            return
            
        # This would be expanded with proper game integration
        logger.info("Games feature - implementation pending")
        
    def draw_calculator_screen(self):
        """Draw calculator mode screen"""
        self.display.clear()
        
        # Status bar
        voltage = self.power.read_battery_voltage()
        percentage = self.power.get_battery_percentage(voltage)
        self.ui.draw_status_bar(self.state.shift_mode, voltage, percentage)
        
        # Expression input
        self.ui.draw_input_field(10, 50, "Input", self.state.current_expression, True)
        
        # Live result preview
        live_result = self.math_engine.evaluate_live(self.state.current_expression)
        result_display = live_result if live_result else self.state.last_result
        self.ui.draw_input_field(10, 90, "Output", result_display)
        
        self.display.show()
        
    def draw_menu_screen(self):
        """Draw menu screen"""
        self.display.clear()
        
        # Status bar  
        voltage = self.power.read_battery_voltage()
        percentage = self.power.get_battery_percentage(voltage)
        self.ui.draw_status_bar(self.state.shift_mode, voltage, percentage)
        
        # Menu title
        self.display.draw_text(config.UI.TEXT_MARGIN, 40, "Main Menu", config.UI.FOREGROUND)
        
        # Menu items
        y = 65
        for i, item in enumerate(self.state.menu_items):
            selected = (i == self.state.menu_index)
            self.ui.draw_menu_item(config.UI.TEXT_MARGIN, y, item, selected)
            y += config.UI.MENU_ITEM_HEIGHT + 2
            
        # Help text
        help_text = "Use ↑/↓ to navigate, = to select, C to exit"
        self.display.draw_text(config.UI.TEXT_MARGIN, self.display.height - 20, 
                              help_text[:40], config.UI.FOREGROUND)
        
        self.display.show()
        
    def draw_graph_screen(self):
        """Draw graph mode screen"""
        self.display.clear()
        
        # Status bar
        voltage = self.power.read_battery_voltage()
        percentage = self.power.get_battery_percentage(voltage)
        self.ui.draw_status_bar(self.state.shift_mode, voltage, percentage)
        
        # Graph expression
        expr_display = self.state.graph_expression[:35]
        self.display.draw_text(config.UI.TEXT_MARGIN, 40, f"y = {expr_display}", 
                              config.UI.FOREGROUND)
        
        # Plot area
        plot_x, plot_y = 10, 60
        plot_w, plot_h = self.display.width - 20, self.display.height - 100
        
        self.display.draw_rect(plot_x, plot_y, plot_w, plot_h, config.UI.FOREGROUND)
        
        # Simple function plotting
        plot_points = []  # For USB transmission
        try:
            processed_expr = self.math_engine.preprocess_expression(self.state.graph_expression)
            
            for px in range(plot_x + 1, plot_x + plot_w - 1, 2):
                # Convert pixel to world coordinate
                x_world = (self.state.graph_x_min + 
                          (px - plot_x) / plot_w * self.state.graph_x_range)
                
                try:
                    # Evaluate function
                    y_world = eval(processed_expr, self.math_engine.safe_globals, {"x": x_world})
                    
                    if isinstance(y_world, (int, float)) and math.isfinite(y_world):
                        # Convert world to pixel coordinate
                        py = (plot_y + plot_h - 
                             int((y_world - self.state.graph_y_min) / self.state.graph_y_range * plot_h))
                        
                        # Draw point if within bounds
                        if plot_y <= py <= plot_y + plot_h:
                            self.display.draw_pixel(px, py, config.UI.ACCENT)
                            
                        # Collect points for USB transmission
                        plot_points.append((x_world, y_world))
                            
                except:
                    continue  # Skip invalid points
                    
        except Exception as e:
            logger.error(f"Graph plotting error: {e}")
            
        # Send graph data to PC via USB
        if self.usb_interface and plot_points:
            # Send every 10th point to reduce data volume
            sampled_points = plot_points[::10]
            self.usb_interface.process_graph_update(self.state.graph_expression, sampled_points)
            
        # Help text
        self.display.draw_text(config.UI.TEXT_MARGIN, self.display.height - 20,
                              "Arrow keys: pan, S: zoom, C: back", config.UI.FOREGROUND)
        
        self.display.show()
    
    def draw_phase4_screen(self):
        """Draw Phase 4 enhanced mathematical features screen"""
        self.display.clear()
        
        # Draw status bar
        battery_voltage, battery_percent = self.power.get_battery_info()
        self.ui.draw_status_bar(self.state.shift_mode, battery_voltage, battery_percent)
        
        if not ENHANCED_MATH_AVAILABLE:
            self.display.draw_text(10, 80, "Enhanced Math Engine", config.UI.WARNING)
            self.display.draw_text(10, 100, "Not Available", config.UI.WARNING)
            self.display.draw_text(10, 140, "Press C to return", config.UI.FOREGROUND)
            self.display.show()
            return
        
        submode = self.state.phase4_mode or "unknown"
        
        if submode == "statistics":
            self.draw_statistics_interface()
        elif submode == "matrix":
            self.draw_matrix_interface()
        elif submode == "units":
            self.draw_units_interface()
        elif submode == "complex":
            self.draw_complex_interface()
        else:
            self.display.draw_text(10, 100, f"Unknown mode: {submode}", config.UI.WARNING)
            
        self.display.show()
    
    def draw_statistics_interface(self):
        """Draw statistics mode interface"""
        y_pos = 40
        
        # Title
        self.display.draw_text(10, y_pos, "Statistics Mode", config.UI.ACCENT)
        y_pos += 25
        
        # Dataset info
        n_data = len(self.math_engine.statistics_data)
        self.display.draw_text(10, y_pos, f"Dataset: {n_data} values", config.UI.FOREGROUND)
        y_pos += 20
        
        if n_data > 0:
            # Show last few values
            last_values = self.math_engine.statistics_data[-3:]
            values_str = ", ".join(f"{v:.2g}" for v in last_values)
            if n_data > 3:
                values_str = "..." + values_str
            self.display.draw_text(10, y_pos, f"Values: {values_str}", config.UI.FOREGROUND)
            y_pos += 20
        
        # Current result
        if hasattr(self.state, 'last_result') and self.state.last_result:
            self.display.draw_text(10, y_pos, f"Result: {self.state.last_result}", config.UI.ACCENT)
            y_pos += 25
        
        # Instructions
        y_pos += 10
        instructions = [
            "1: Add current result",
            "2: Calculate stats", 
            "3: Clear data",
            "=: Cycle statistics",
            "C: Back to menu"
        ]
        
        for instruction in instructions:
            self.display.draw_text(10, y_pos, instruction, config.UI.FOREGROUND)
            y_pos += 15
        
        # Status message
        if hasattr(self.state, 'status_message') and self.state.status_message:
            self.display.draw_text(10, self.display.height - 30, 
                                  self.state.status_message, config.UI.ACCENT)
    
    def draw_matrix_interface(self):
        """Draw matrix mode interface"""
        y_pos = 40
        
        # Title
        self.display.draw_text(10, y_pos, "Matrix Mode", config.UI.ACCENT)
        y_pos += 25
        
        # Matrix info
        if self.math_engine.last_matrix:
            matrix = self.math_engine.last_matrix
            self.display.draw_text(10, y_pos, f"Matrix: {matrix.rows}x{matrix.cols}", config.UI.FOREGROUND)
            y_pos += 20
            
            # Show matrix elements (if small enough)
            if matrix.rows <= 3 and matrix.cols <= 3:
                for i in range(matrix.rows):
                    row_str = "[" + ", ".join(f"{matrix.data[i][j]:.2g}" for j in range(matrix.cols)) + "]"
                    self.display.draw_text(10, y_pos, row_str, config.UI.FOREGROUND)
                    y_pos += 15
        else:
            self.display.draw_text(10, y_pos, "No matrix loaded", config.UI.FOREGROUND)
            y_pos += 20
        
        # Current result
        if hasattr(self.state, 'last_result') and self.state.last_result:
            result_lines = str(self.state.last_result).split('\n')
            for line in result_lines[:3]:  # Show max 3 lines
                self.display.draw_text(10, y_pos, line[:25], config.UI.ACCENT)  # Truncate long lines
                y_pos += 15
            y_pos += 10
        
        # Instructions
        instructions = [
            "1: Create identity 2x2",
            "2: Determinant",
            "3: Transpose", 
            "4: Inverse",
            "5: Eigenvalues",
            "C: Back to menu"
        ]
        
        for instruction in instructions:
            if y_pos < self.display.height - 45:  # Leave room for status
                self.display.draw_text(10, y_pos, instruction, config.UI.FOREGROUND)
                y_pos += 15
        
        # Status message
        if hasattr(self.state, 'status_message') and self.state.status_message:
            self.display.draw_text(10, self.display.height - 30, 
                                  self.state.status_message[:35], config.UI.ACCENT)
    
    def draw_units_interface(self):
        """Draw unit conversion interface"""
        y_pos = 40
        
        # Title
        self.display.draw_text(10, y_pos, "Unit Converter", config.UI.ACCENT)
        y_pos += 25
        
        # Current result
        if hasattr(self.state, 'last_result') and self.state.last_result:
            result_lines = str(self.state.last_result).split('\n')
            for line in result_lines[:2]:
                self.display.draw_text(10, y_pos, line[:30], config.UI.ACCENT)
                y_pos += 15
            y_pos += 10
        
        # Quick conversions
        conversions = [
            "1: 100 cm → m",
            "2: 32 °F → °C", 
            "3: 1 hp → W",
            "4: 1 mi → km",
            "5: 1 gal → L",
            "6: 1 lb → kg",
            "=: Unit categories",
            "C: Back to menu"
        ]
        
        for conversion in conversions:
            if y_pos < self.display.height - 45:
                self.display.draw_text(10, y_pos, conversion, config.UI.FOREGROUND)
                y_pos += 15
        
        # Status message
        if hasattr(self.state, 'status_message') and self.state.status_message:
            self.display.draw_text(10, self.display.height - 30, 
                                  self.state.status_message[:35], config.UI.ACCENT)
    
    def draw_complex_interface(self):
        """Draw complex number interface"""
        y_pos = 40
        
        # Title
        self.display.draw_text(10, y_pos, "Complex Numbers", config.UI.ACCENT)
        y_pos += 25
        
        # Mode indicator
        mode_text = "COMPLEX MODE ON" if self.math_engine.complex_mode else "COMPLEX MODE OFF"
        self.display.draw_text(10, y_pos, mode_text, config.UI.ACCENT)
        y_pos += 25
        
        # Example expressions
        examples = [
            "1: 3+4j",
            "2: (1+2j)*(3+4j)",
            "3: abs(3+4j)",
            "4: phase(1+1j)",
            "",
            "Use 'j' for imaginary unit",
            "All functions support complex",
            "C: Back to calculator"
        ]
        
        for example in examples:
            if y_pos < self.display.height - 30:
                self.display.draw_text(10, y_pos, example, config.UI.FOREGROUND)
                y_pos += 15
        
    def render_current_screen(self):
        """Render the current application screen"""
        if self.state.current_mode == "calc":
            self.draw_calculator_screen()
        elif self.state.current_mode == "menu":
            self.draw_menu_screen()
        elif self.state.current_mode == "graph":
            self.draw_graph_screen()
        elif self.state.current_mode == "phase4":
            self.draw_phase4_screen()
        else:
            # Fallback to calculator
            self.state.current_mode = "calc"
            self.draw_calculator_screen()
            
    def process_input(self):
        """Process keypad input"""
        events = self.keypad.get_events()
        
        for key_pos, event_type in events:
            key_label = self.keypad.get_key_label(key_pos, self.state.shift_mode)
            
            if not key_label:
                continue
                
            logger.debug(f"Key event: {key_label} ({event_type})")
            
            # Reset activity timer
            self.state.reset_activity()
            
            # Handle global keys first
            if self.handle_global_keys(key_label, event_type):
                continue
                
            # Handle mode-specific keys
            if self.state.current_mode == "calc":
                self.handle_calculator_mode(key_label, event_type)
            elif self.state.current_mode == "menu":
                self.handle_menu_mode(key_label, event_type)
            elif self.state.current_mode == "graph":
                self.handle_graph_mode(key_label, event_type)
            elif self.state.current_mode == "phase4":
                self.handle_phase4_mode(key_label, event_type)
                
    def update_power_management(self):
        """Update power management based on activity"""
        inactive_time = self.state.get_inactive_time()
        self.power.auto_dim(inactive_time)
        
    def run(self):
        """Main application loop"""
        logger.info("Starting calculator main loop...")
        
        # Initial screen render
        self.render_current_screen()
        
        try:
            while self.running:
                # Process input
                self.process_input()
                
                # Update USB interface
                if self.usb_interface:
                    self.usb_interface.update()
                
                # Update display
                self.render_current_screen()
                
                # Power management
                self.update_power_management()
                
                # Small delay to prevent excessive CPU usage
                time.sleep_ms(20)
                
        except KeyboardInterrupt:
            logger.info("Calculator shutdown requested")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}")
            self.ui.show_message("Error", "System Error", "error")
            self.display.show()
            time.sleep(3)
        finally:
            logger.info("Calculator shutdown complete")

# ================= MAIN ENTRY POINT =================
def main():
    """Main entry point for the calculator application"""
    print("=" * 60)
    print("🧮 PEANUT 3000 ADVANCED CALCULATOR v2.0")
    print("   Enhanced with Security & Performance")
    print("=" * 60)
    
    try:
        # Create and run calculator application
        calculator = CalculatorApp()
        calculator.run()
        
    except Exception as e:
        print(f"❌ Fatal startup error: {e}")
        # Attempt basic error display
        try:
            import time
            print("System will restart in 5 seconds...")
            time.sleep(5)
        except:
            pass

if __name__ == "__main__":
    main()

# ================= END OF CALCULATOR.PY =================