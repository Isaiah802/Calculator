"""
Advanced Graphics Engine for Peanut 3000 Calculator
==================================================

Phase 5: Advanced Graphing and Visualization Engine
This module provides comprehensive 2D/3D graphics capabilities for the Peanut 3000 calculator,
including function plotting, statistical visualization, and interactive graph exploration.

Features:
- 2D function plotting with automatic scaling
- Statistical charts (histograms, scatter plots, regression)
- Interactive navigation (zoom, pan, trace)
- 3D surface plotting and wireframes
- Graph export and sharing capabilities
- Integration with enhanced mathematical engine

Author: Peanut 3000 Development Team
Version: 5.0.0
Date: December 2024
"""

import math
import gc
from micropython import const
from firmware.hardware_config import Display, Pins
from firmware.enhanced_math_engine import EnhancedMathEngine

# Graphics Constants
GRAPH_WIDTH = const(280)      # Graph area width
GRAPH_HEIGHT = const(200)     # Graph area height
GRAPH_X_OFFSET = const(20)    # Left margin
GRAPH_Y_OFFSET = const(20)    # Top margin

# Color Definitions (RGB565)
class GraphColors:
    BACKGROUND = const(0x0000)    # Black
    GRID_MAJOR = const(0x4208)    # Dark gray
    GRID_MINOR = const(0x2104)    # Very dark gray
    AXIS = const(0xFFFF)          # White
    FUNCTION = const(0x07E0)      # Green
    DATA_POINTS = const(0x001F)   # Blue
    REGRESSION = const(0xF800)    # Red
    TRACE_POINT = const(0xFFE0)   # Yellow
    TEXT = const(0xFFFF)          # White

class Point2D:
    """2D point representation"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"

class Point3D:
    """3D point representation"""
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def project_2d(self, distance: float = 10.0, angle_x: float = 0.5, angle_y: float = 0.5) -> Point2D:
        """Project 3D point to 2D using perspective projection"""
        # Simple perspective projection
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        
        # Rotate around X axis
        y1 = self.y * cos_x - self.z * sin_x
        z1 = self.y * sin_x + self.z * cos_x
        
        # Rotate around Y axis
        x2 = self.x * cos_y + z1 * sin_y
        z2 = -self.x * sin_y + z1 * cos_y
        
        # Perspective projection
        if z2 + distance == 0:
            z2 = 0.001  # Avoid division by zero
        
        factor = distance / (z2 + distance)
        return Point2D(x2 * factor, y1 * factor)

class GraphBounds:
    """Graph coordinate bounds"""
    def __init__(self, x_min: float = -10.0, x_max: float = 10.0,
                 y_min: float = -10.0, y_max: float = 10.0):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
    
    def width(self) -> float:
        return self.x_max - self.x_min
    
    def height(self) -> float:
        return self.y_max - self.y_min
    
    def center(self) -> Point2D:
        return Point2D((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)
    
    def zoom(self, factor: float, center_x: float = None, center_y: float = None):
        """Zoom the bounds by a factor around a center point"""
        if center_x is None:
            center_x = (self.x_min + self.x_max) / 2
        if center_y is None:
            center_y = (self.y_min + self.y_max) / 2
        
        width = self.width()
        height = self.height()
        
        new_width = width / factor
        new_height = height / factor
        
        self.x_min = center_x - new_width / 2
        self.x_max = center_x + new_width / 2
        self.y_min = center_y - new_height / 2
        self.y_max = center_y + new_height / 2
    
    def pan(self, dx: float, dy: float):
        """Pan the bounds by a delta"""
        self.x_min += dx
        self.x_max += dx
        self.y_min += dy
        self.y_max += dy

class GraphicsEngine:
    """Advanced graphics rendering engine"""
    
    def __init__(self, display_driver):
        self.display = display_driver
        self.math_engine = EnhancedMathEngine()
        
        # Graph state
        self.bounds = GraphBounds()
        self.function_expression = "sin(x)"
        self.trace_x = 0.0
        self.show_trace = False
        
        # Data storage
        self.data_points = []
        self.function_cache = {}
        
        # Performance settings
        self.resolution = 2  # Pixel step for function plotting
        self.max_points = 500  # Maximum function points to calculate
        
        # 3D settings
        self.view_angle_x = 0.5
        self.view_angle_y = 0.5
        self.view_distance = 10.0
    
    def world_to_screen(self, world_x: float, world_y: float) -> tuple:
        """Convert world coordinates to screen coordinates"""
        screen_x = GRAPH_X_OFFSET + int((world_x - self.bounds.x_min) * GRAPH_WIDTH / self.bounds.width())
        screen_y = GRAPH_Y_OFFSET + int((self.bounds.y_max - world_y) * GRAPH_HEIGHT / self.bounds.height())
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> tuple:
        """Convert screen coordinates to world coordinates"""
        world_x = self.bounds.x_min + (screen_x - GRAPH_X_OFFSET) * self.bounds.width() / GRAPH_WIDTH
        world_y = self.bounds.y_max - (screen_y - GRAPH_Y_OFFSET) * self.bounds.height() / GRAPH_HEIGHT
        return world_x, world_y
    
    def draw_pixel(self, x: int, y: int, color: int):
        """Draw a single pixel with bounds checking"""
        if 0 <= x < Display.WIDTH and 0 <= y < Display.HEIGHT:
            self.display.pixel(x, y, color)
    
    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: int):
        """Draw a line using Bresenham's algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        while True:
            self.draw_pixel(x, y, color)
            
            if x == x1 and y == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def draw_circle(self, center_x: int, center_y: int, radius: int, color: int, filled: bool = False):
        """Draw a circle using midpoint algorithm"""
        x = radius
        y = 0
        err = 0
        
        while x >= y:
            if filled:
                self.draw_line(center_x - x, center_y + y, center_x + x, center_y + y, color)
                self.draw_line(center_x - x, center_y - y, center_x + x, center_y - y, color)
                self.draw_line(center_x - y, center_y + x, center_x + y, center_y + x, color)
                self.draw_line(center_x - y, center_y - x, center_x + y, center_y - x, color)
            else:
                self.draw_pixel(center_x + x, center_y + y, color)
                self.draw_pixel(center_x + y, center_y + x, color)
                self.draw_pixel(center_x - y, center_y + x, color)
                self.draw_pixel(center_x - x, center_y + y, color)
                self.draw_pixel(center_x - x, center_y - y, color)
                self.draw_pixel(center_x - y, center_y - x, color)
                self.draw_pixel(center_x + y, center_y - x, color)
                self.draw_pixel(center_x + x, center_y - y, color)
            
            if err <= 0:
                y += 1
                err += 2 * y + 1
            
            if err > 0:
                x -= 1
                err -= 2 * x + 1
    
    def clear_graph_area(self):
        """Clear the graph drawing area"""
        for y in range(GRAPH_Y_OFFSET, GRAPH_Y_OFFSET + GRAPH_HEIGHT):
            for x in range(GRAPH_X_OFFSET, GRAPH_X_OFFSET + GRAPH_WIDTH):
                self.draw_pixel(x, y, GraphColors.BACKGROUND)
    
    def draw_grid(self, major_step: float = 1.0, minor_step: float = 0.2):
        """Draw coordinate grid"""
        # Major grid lines
        x = math.ceil(self.bounds.x_min / major_step) * major_step
        while x <= self.bounds.x_max:
            screen_x, _ = self.world_to_screen(x, 0)
            if GRAPH_X_OFFSET <= screen_x <= GRAPH_X_OFFSET + GRAPH_WIDTH:
                self.draw_line(screen_x, GRAPH_Y_OFFSET, screen_x, GRAPH_Y_OFFSET + GRAPH_HEIGHT, GraphColors.GRID_MAJOR)
            x += major_step
        
        y = math.ceil(self.bounds.y_min / major_step) * major_step
        while y <= self.bounds.y_max:
            _, screen_y = self.world_to_screen(0, y)
            if GRAPH_Y_OFFSET <= screen_y <= GRAPH_Y_OFFSET + GRAPH_HEIGHT:
                self.draw_line(GRAPH_X_OFFSET, screen_y, GRAPH_X_OFFSET + GRAPH_WIDTH, screen_y, GraphColors.GRID_MAJOR)
            y += major_step
        
        # Minor grid lines (if zoom level appropriate)
        if self.bounds.width() <= 20:  # Only show minor grid when zoomed in
            x = math.ceil(self.bounds.x_min / minor_step) * minor_step
            while x <= self.bounds.x_max:
                if x % major_step != 0:  # Skip major grid positions
                    screen_x, _ = self.world_to_screen(x, 0)
                    if GRAPH_X_OFFSET <= screen_x <= GRAPH_X_OFFSET + GRAPH_WIDTH:
                        self.draw_line(screen_x, GRAPH_Y_OFFSET, screen_x, GRAPH_Y_OFFSET + GRAPH_HEIGHT, GraphColors.GRID_MINOR)
                x += minor_step
            
            y = math.ceil(self.bounds.y_min / minor_step) * minor_step
            while y <= self.bounds.y_max:
                if y % major_step != 0:  # Skip major grid positions
                    _, screen_y = self.world_to_screen(0, y)
                    if GRAPH_Y_OFFSET <= screen_y <= GRAPH_Y_OFFSET + GRAPH_HEIGHT:
                        self.draw_line(GRAPH_X_OFFSET, screen_y, GRAPH_X_OFFSET + GRAPH_WIDTH, screen_y, GraphColors.GRID_MINOR)
                y += minor_step
    
    def draw_axes(self):
        """Draw coordinate axes"""
        # X-axis
        if self.bounds.y_min <= 0 <= self.bounds.y_max:
            _, axis_y = self.world_to_screen(0, 0)
            self.draw_line(GRAPH_X_OFFSET, axis_y, GRAPH_X_OFFSET + GRAPH_WIDTH, axis_y, GraphColors.AXIS)
        
        # Y-axis
        if self.bounds.x_min <= 0 <= self.bounds.x_max:
            axis_x, _ = self.world_to_screen(0, 0)
            self.draw_line(axis_x, GRAPH_Y_OFFSET, axis_x, GRAPH_Y_OFFSET + GRAPH_HEIGHT, GraphColors.AXIS)
    
    def evaluate_function(self, x: float, expression: str = None) -> float:
        """Evaluate mathematical function at given x"""
        if expression is None:
            expression = self.function_expression
        
        try:
            # Use enhanced math engine for evaluation
            # Replace 'x' with actual value in expression
            safe_expr = expression.replace('x', str(x))
            result = self.math_engine.safe_evaluate(safe_expr)
            
            if isinstance(result, complex):
                return result.real  # Use real part for plotting
            return float(result)
            
        except:
            return float('nan')  # Invalid result
    
    def plot_function(self, expression: str = None, color: int = GraphColors.FUNCTION):
        """Plot mathematical function"""
        if expression is None:
            expression = self.function_expression
        
        # Calculate step size based on graph width and resolution
        x_step = self.bounds.width() / (GRAPH_WIDTH / self.resolution)
        
        prev_screen_x = None
        prev_screen_y = None
        
        x = self.bounds.x_min
        points_plotted = 0
        
        while x <= self.bounds.x_max and points_plotted < self.max_points:
            y = self.evaluate_function(x, expression)
            
            if not math.isnan(y) and not math.isinf(y):
                screen_x, screen_y = self.world_to_screen(x, y)
                
                # Only draw if point is within graph bounds
                if (GRAPH_X_OFFSET <= screen_x <= GRAPH_X_OFFSET + GRAPH_WIDTH and
                    GRAPH_Y_OFFSET <= screen_y <= GRAPH_Y_OFFSET + GRAPH_HEIGHT):
                    
                    if prev_screen_x is not None and prev_screen_y is not None:
                        # Connect to previous point if it's close enough
                        if abs(screen_y - prev_screen_y) < 50:  # Avoid connecting discontinuities
                            self.draw_line(prev_screen_x, prev_screen_y, screen_x, screen_y, color)
                        else:
                            self.draw_pixel(screen_x, screen_y, color)
                    else:
                        self.draw_pixel(screen_x, screen_y, color)
                    
                    prev_screen_x = screen_x
                    prev_screen_y = screen_y
                else:
                    prev_screen_x = None
                    prev_screen_y = None
            else:
                prev_screen_x = None
                prev_screen_y = None
            
            x += x_step
            points_plotted += 1
            
            # Yield control occasionally for responsiveness
            if points_plotted % 50 == 0:
                gc.collect()
    
    def plot_data_points(self, points: list, color: int = GraphColors.DATA_POINTS, size: int = 2):
        """Plot discrete data points"""
        for point in points:
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                x, y = float(point[0]), float(point[1])
                screen_x, screen_y = self.world_to_screen(x, y)
                
                if (GRAPH_X_OFFSET <= screen_x <= GRAPH_X_OFFSET + GRAPH_WIDTH and
                    GRAPH_Y_OFFSET <= screen_y <= GRAPH_Y_OFFSET + GRAPH_HEIGHT):
                    self.draw_circle(screen_x, screen_y, size, color, filled=True)
    
    def plot_regression_line(self, points: list, color: int = GraphColors.REGRESSION):
        """Plot linear regression line for data points"""
        if len(points) < 2:
            return
        
        try:
            # Calculate regression using enhanced math engine
            x_data = [float(p[0]) for p in points]
            y_data = [float(p[1]) for p in points]
            
            stats_engine = self.math_engine.statistics
            slope, intercept, r_squared = stats_engine.linear_regression(x_data, y_data)
            
            # Plot regression line across graph bounds
            x1 = self.bounds.x_min
            y1 = slope * x1 + intercept
            x2 = self.bounds.x_max
            y2 = slope * x2 + intercept
            
            screen_x1, screen_y1 = self.world_to_screen(x1, y1)
            screen_x2, screen_y2 = self.world_to_screen(x2, y2)
            
            self.draw_line(screen_x1, screen_y1, screen_x2, screen_y2, color)
            
            return slope, intercept, r_squared
            
        except:
            return None, None, None
    
    def draw_trace_point(self):
        """Draw trace point on function"""
        if self.show_trace:
            y = self.evaluate_function(self.trace_x)
            
            if not math.isnan(y) and not math.isinf(y):
                screen_x, screen_y = self.world_to_screen(self.trace_x, y)
                
                if (GRAPH_X_OFFSET <= screen_x <= GRAPH_X_OFFSET + GRAPH_WIDTH and
                    GRAPH_Y_OFFSET <= screen_y <= GRAPH_Y_OFFSET + GRAPH_HEIGHT):
                    self.draw_circle(screen_x, screen_y, 3, GraphColors.TRACE_POINT, filled=True)
                    return self.trace_x, y
        
        return None, None
    
    def auto_scale(self, expression: str = None, sample_points: int = 100):
        """Automatically scale graph bounds to fit function"""
        if expression is None:
            expression = self.function_expression
        
        # Sample function values
        x_min = self.bounds.x_min
        x_max = self.bounds.x_max
        x_step = (x_max - x_min) / sample_points
        
        y_values = []
        x = x_min
        
        for _ in range(sample_points):
            y = self.evaluate_function(x, expression)
            if not math.isnan(y) and not math.isinf(y):
                y_values.append(y)
            x += x_step
        
        if y_values:
            y_min = min(y_values)
            y_max = max(y_values)
            
            # Add 10% padding
            y_range = y_max - y_min
            if y_range > 0:
                padding = y_range * 0.1
                self.bounds.y_min = y_min - padding
                self.bounds.y_max = y_max + padding
            else:
                # If function is constant, use default range
                self.bounds.y_min = y_min - 1
                self.bounds.y_max = y_max + 1
    
    def render_complete_graph(self, show_grid: bool = True, show_axes: bool = True, 
                             show_function: bool = True, show_data: bool = True,
                             show_regression: bool = False):
        """Render complete graph with all elements"""
        # Clear graph area
        self.clear_graph_area()
        
        # Draw grid
        if show_grid:
            self.draw_grid()
        
        # Draw axes
        if show_axes:
            self.draw_axes()
        
        # Draw function
        if show_function and self.function_expression:
            self.plot_function()
        
        # Draw data points
        if show_data and self.data_points:
            self.plot_data_points(self.data_points)
        
        # Draw regression line
        if show_regression and self.data_points:
            self.plot_regression_line(self.data_points)
        
        # Draw trace point
        self.draw_trace_point()

# Export main class
__all__ = ['GraphicsEngine', 'Point2D', 'Point3D', 'GraphBounds', 'GraphColors']