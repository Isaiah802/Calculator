#!/usr/bin/env python3
"""
Graphing Module - Unified Graph Management for Peanut 3000 Calculator
=====================================================================

This module provides a unified interface to all graphing capabilities:
- 2D function plotting (via GraphicsEngine)
- Statistical visualization (via StatisticalPlotter)
- Complex number plotting (via ComplexPlotter)
- 3D surface rendering (via Plot3DEngine)
- Interactive graph controls (via InteractiveGraphControls)

The GraphManager class serves as a facade/wrapper that simplifies access
to the existing graphics engines and provides a cleaner API for the calculator.

Classes:
    GraphManager: Unified graph management interface

Example:
    >>> graph_mgr = GraphManager(display_manager)
    >>> graph_mgr.plot_function("sin(x)", x_min=-10, x_max=10)
    >>> graph_mgr.plot_histogram([1, 2, 3, 4, 5])
"""

from typing import Optional, List, Tuple, Any

# Import existing graphics engines
try:
    from graphics_engine import GraphicsEngine, GraphColors, Point2D, GraphBounds
    GRAPHICS_AVAILABLE = True
except ImportError:
    GRAPHICS_AVAILABLE = False
    print("[WARNING] graphics_engine not available")

try:
    from statistical_plots import StatisticalPlotter, ComplexPlotter
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False
    print("[WARNING] statistical_plots not available")

try:
    from interactive_3d import Surface3D, Plot3DEngine, InteractiveGraphControls
    PLOT3D_AVAILABLE = True
except ImportError:
    PLOT3D_AVAILABLE = False
    print("[WARNING] interactive_3d not available")


class GraphManager:
    """
    Unified graphing interface for all calculator graphics operations.
    
    This class wraps the existing graphics engines (GraphicsEngine,
    StatisticalPlotter, Plot3DEngine, etc.) and provides a simplified
    API for common graphing operations.
    
    Attributes:
        display: DisplayManager instance for rendering
        graphics: GraphicsEngine instance for 2D plotting
        stats: StatisticalPlotter instance for statistical plots
        complex: ComplexPlotter instance for complex number visualization
        plot3d: Plot3DEngine instance for 3D surface rendering
        interactive: InteractiveGraphControls instance for graph interaction
        
    Example:
        >>> from hardware.display import DisplayManager
        >>> display = DisplayManager(spi_manager)
        >>> graph_mgr = GraphManager(display)
        >>> graph_mgr.plot_function("x**2", -5, 5)
    """
    
    def __init__(self, display_manager):
        """
        Initialize GraphManager with display manager.
        
        Args:
            display_manager: DisplayManager instance for rendering
            
        Raises:
            ImportError: If required graphics modules are not available
        """
        self.display = display_manager
        
        # Initialize graphics engines if available
        if GRAPHICS_AVAILABLE:
            self.graphics = GraphicsEngine(display_manager)
        else:
            self.graphics = None
            
        if STATS_AVAILABLE and self.graphics:
            self.stats = StatisticalPlotter(self.graphics)
            self.complex = ComplexPlotter(self.graphics)
        else:
            self.stats = None
            self.complex = None
            
        if PLOT3D_AVAILABLE and self.graphics:
            self.plot3d = Plot3DEngine(self.graphics)
            self.interactive = InteractiveGraphControls(self.graphics)
        else:
            self.plot3d = None
            self.interactive = None
    
    # === 2D Function Plotting ===
    
    def plot_function(self, expression: str, x_min: float = -10.0, 
                     x_max: float = 10.0, auto_scale_y: bool = True) -> bool:
        """
        Plot a 2D function expression.
        
        Args:
            expression: Mathematical expression (e.g., "sin(x)", "x**2")
            x_min: Minimum x value
            x_max: Maximum x value
            auto_scale_y: Whether to automatically scale y-axis
            
        Returns:
            True if plot succeeded, False otherwise
            
        Example:
            >>> graph_mgr.plot_function("sin(x) + cos(x)", -10, 10)
        """
        if not self.graphics:
            return False
            
        try:
            self.graphics.function_expression = expression
            self.graphics.bounds.x_min = x_min
            self.graphics.bounds.x_max = x_max
            
            if auto_scale_y:
                self.graphics.auto_scale()
                
            self.graphics.render_complete_graph(show_function=True, show_data=False)
            return True
        except Exception as e:
            print(f"[ERROR] plot_function failed: {e}")
            return False
    
    def set_bounds(self, x_min: float, x_max: float, 
                   y_min: float, y_max: float) -> bool:
        """
        Set graph coordinate bounds.
        
        Args:
            x_min: Minimum x value
            x_max: Maximum x value
            y_min: Minimum y value
            y_max: Maximum y value
            
        Returns:
            True if successful
        """
        if not self.graphics:
            return False
            
        self.graphics.bounds.x_min = x_min
        self.graphics.bounds.x_max = x_max
        self.graphics.bounds.y_min = y_min
        self.graphics.bounds.y_max = y_max
        return True
    
    def add_data_point(self, x: float, y: float) -> bool:
        """
        Add a data point to the graph.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful
        """
        if not self.graphics:
            return False
            
        self.graphics.data_points.append((x, y))
        return True
    
    def clear_data_points(self) -> bool:
        """
        Clear all data points from the graph.
        
        Returns:
            True if successful
        """
        if not self.graphics:
            return False
            
        self.graphics.data_points.clear()
        return True
    
    def render_graph(self, show_function: bool = True, 
                    show_data: bool = True) -> bool:
        """
        Render the complete graph with current settings.
        
        Args:
            show_function: Whether to plot the function
            show_data: Whether to plot data points
            
        Returns:
            True if successful
        """
        if not self.graphics:
            return False
            
        try:
            self.graphics.render_complete_graph(
                show_function=show_function,
                show_data=show_data
            )
            return True
        except Exception as e:
            print(f"[ERROR] render_graph failed: {e}")
            return False
    
    # === Statistical Plotting ===
    
    def plot_histogram(self, data: List[float], bins: int = 10, 
                      color: int = None) -> bool:
        """
        Plot a histogram of data.
        
        Args:
            data: List of numerical data values
            bins: Number of histogram bins
            color: Optional color for bars (uses default if None)
            
        Returns:
            True if plot succeeded
            
        Example:
            >>> graph_mgr.plot_histogram([1, 2, 2, 3, 3, 3, 4, 4, 5])
        """
        if not self.stats:
            return False
            
        try:
            self.stats.set_data(data)
            if color is None:
                self.stats.plot_histogram(bins=bins)
            else:
                self.stats.plot_histogram(bins=bins, color=color)
            return True
        except Exception as e:
            print(f"[ERROR] plot_histogram failed: {e}")
            return False
    
    def plot_scatter(self, x_data: List[float], y_data: List[float], 
                    color: int = None) -> bool:
        """
        Plot a scatter plot of x,y data pairs.
        
        Args:
            x_data: List of x values
            y_data: List of y values
            color: Optional color for points
            
        Returns:
            True if plot succeeded
            
        Example:
            >>> x = [1, 2, 3, 4, 5]
            >>> y = [2, 4, 5, 4, 6]
            >>> graph_mgr.plot_scatter(x, y)
        """
        if not self.stats:
            return False
            
        try:
            if color is None:
                self.stats.plot_scatter(x_data, y_data)
            else:
                self.stats.plot_scatter(x_data, y_data, color=color)
            return True
        except Exception as e:
            print(f"[ERROR] plot_scatter failed: {e}")
            return False
    
    def plot_box(self, data: List[float]) -> bool:
        """
        Plot a box plot of data.
        
        Args:
            data: List of numerical data values
            
        Returns:
            True if plot succeeded
        """
        if not self.stats:
            return False
            
        try:
            self.stats.set_data(data)
            self.stats.plot_box()
            return True
        except Exception as e:
            print(f"[ERROR] plot_box failed: {e}")
            return False
    
    def plot_regression(self, x_data: List[float], y_data: List[float],
                       degree: int = 1) -> bool:
        """
        Plot regression line/curve with data points.
        
        Args:
            x_data: List of x values
            y_data: List of y values
            degree: Polynomial degree (1=linear, 2=quadratic, etc.)
            
        Returns:
            True if plot succeeded
        """
        if not self.stats:
            return False
            
        try:
            self.stats.plot_regression(x_data, y_data, degree=degree)
            return True
        except Exception as e:
            print(f"[ERROR] plot_regression failed: {e}")
            return False
    
    # === Complex Number Plotting ===
    
    def plot_complex(self, complex_numbers: List[complex]) -> bool:
        """
        Plot complex numbers on complex plane.
        
        Args:
            complex_numbers: List of complex number objects
            
        Returns:
            True if plot succeeded
            
        Example:
            >>> nums = [1+2j, 2+3j, 3+1j]
            >>> graph_mgr.plot_complex(nums)
        """
        if not self.complex:
            return False
            
        try:
            self.complex.plot_complex_plane(complex_numbers)
            return True
        except Exception as e:
            print(f"[ERROR] plot_complex failed: {e}")
            return False
    
    # === 3D Plotting ===
    
    def plot_3d_surface(self, expression: str, 
                       x_range: Tuple[float, float] = (-5, 5),
                       y_range: Tuple[float, float] = (-5, 5),
                       resolution: int = 20) -> bool:
        """
        Plot a 3D surface from a function z=f(x,y).
        
        Args:
            expression: Function expression with x and y variables
            x_range: Tuple of (x_min, x_max)
            y_range: Tuple of (y_min, y_max)
            resolution: Mesh resolution (number of grid points)
            
        Returns:
            True if plot succeeded
            
        Example:
            >>> graph_mgr.plot_3d_surface("sin(x) * cos(y)")
        """
        if not self.plot3d:
            return False
            
        try:
            surface = Surface3D(expression, x_range, y_range, resolution)
            surface.generate_mesh(self.graphics.math_engine)
            self.plot3d.current_surface = surface
            self.plot3d.render_surface()
            return True
        except Exception as e:
            print(f"[ERROR] plot_3d_surface failed: {e}")
            return False
    
    def rotate_3d_view(self, angle_x: float = None, 
                      angle_y: float = None) -> bool:
        """
        Rotate the 3D view angles.
        
        Args:
            angle_x: X rotation angle (tilt)
            angle_y: Y rotation angle (azimuth)
            
        Returns:
            True if successful
        """
        if not self.plot3d:
            return False
            
        try:
            if angle_x is not None:
                self.plot3d.rotation_x = angle_x
            if angle_y is not None:
                self.plot3d.rotation_y = angle_y
                
            if self.plot3d.current_surface:
                self.plot3d.render_surface()
            return True
        except Exception as e:
            print(f"[ERROR] rotate_3d_view failed: {e}")
            return False
    
    # === Interactive Controls ===
    
    def zoom_in(self) -> bool:
        """Zoom in on the graph."""
        if not self.interactive:
            return False
            
        try:
            self.interactive.zoom_in()
            return True
        except Exception as e:
            print(f"[ERROR] zoom_in failed: {e}")
            return False
    
    def zoom_out(self) -> bool:
        """Zoom out on the graph."""
        if not self.interactive:
            return False
            
        try:
            self.interactive.zoom_out()
            return True
        except Exception as e:
            print(f"[ERROR] zoom_out failed: {e}")
            return False
    
    def pan(self, dx: float, dy: float) -> bool:
        """
        Pan the graph view.
        
        Args:
            dx: X direction pan amount
            dy: Y direction pan amount
            
        Returns:
            True if successful
        """
        if not self.interactive:
            return False
            
        try:
            self.interactive.pan(dx, dy)
            return True
        except Exception as e:
            print(f"[ERROR] pan failed: {e}")
            return False
    
    def trace_point(self, x: float) -> Optional[float]:
        """
        Trace function value at specific x coordinate.
        
        Args:
            x: X coordinate to trace
            
        Returns:
            Y value at x, or None if failed
        """
        if not self.interactive:
            return None
            
        try:
            return self.interactive.trace_function(x)
        except Exception as e:
            print(f"[ERROR] trace_point failed: {e}")
            return None
    
    # === Utility Methods ===
    
    def is_available(self) -> bool:
        """
        Check if graphing capabilities are available.
        
        Returns:
            True if at least basic graphics are available
        """
        return self.graphics is not None
    
    def has_statistical_plotting(self) -> bool:
        """Check if statistical plotting is available."""
        return self.stats is not None
    
    def has_3d_plotting(self) -> bool:
        """Check if 3D plotting is available."""
        return self.plot3d is not None
    
    def get_current_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Get current graph bounds.
        
        Returns:
            Tuple of (x_min, x_max, y_min, y_max) or None
        """
        if not self.graphics:
            return None
            
        bounds = self.graphics.bounds
        return (bounds.x_min, bounds.x_max, bounds.y_min, bounds.y_max)
    
    def __repr__(self) -> str:
        """String representation of GraphManager."""
        return (f"GraphManager(graphics={self.graphics is not None}, "
                f"stats={self.stats is not None}, "
                f"3d={self.plot3d is not None})")


def create_graph_manager(display_manager):
    """
    Factory function to create a GraphManager instance.
    
    This is a convenience function that can be used instead of
    directly instantiating GraphManager.
    
    Args:
        display_manager: DisplayManager instance
        
    Returns:
        GraphManager instance
        
    Example:
        >>> from graphing import create_graph_manager
        >>> graph_mgr = create_graph_manager(display)
    """
    return GraphManager(display_manager)


# Module initialization
if __name__ == '__main__':
    """Test module when run directly."""
    print("GraphManager module loaded")
    print(f"Graphics available: {GRAPHICS_AVAILABLE}")
    print(f"Statistics available: {STATS_AVAILABLE}")
    print(f"3D plotting available: {PLOT3D_AVAILABLE}")
