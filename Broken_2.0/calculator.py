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
from core import AppState

# Import UI module
from ui import UIManager

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

# Import math engine module
from math.secure_engine import SecureMathEngine

# Enhanced math engine is imported directly, so it's always available
ENHANCED_MATH_AVAILABLE = True

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

# ================= STORAGE LAYER =================
# FileSystemManager has been extracted to storage/ module
from storage.filesystem import FileSystemManager

# ================= USER INTERFACE SYSTEM =================
# UIManager has been extracted to ui/ui_manager.py

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
        self.math_engine.set_config(config)
        self.math_engine.set_logger(logger)
        self.ui = UIManager(self.display, self.power)
        
        # Phase 5: Initialize Advanced Graphing System
        self.graphics_engine = GraphicsEngine(self.display)
        self.statistical_plotter = StatisticalPlotter(self.graphics_engine)
        self.complex_plotter = ComplexPlotter(self.graphics_engine)
        self.interactive_controls = InteractiveGraphControls(self.graphics_engine)
        
        # Current surface for 3D plotting
        self.current_3d_surface = None
        self.state = AppState(config, logger, GAMES_AVAILABLE, ENHANCED_MATH_AVAILABLE)
        
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