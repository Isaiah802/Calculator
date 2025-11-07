"""
Statistical Visualization Module for Peanut 3000 Calculator
===========================================================

Specialized statistical plotting and data visualization capabilities
including histograms, scatter plots, box plots, and statistical analysis charts.
"""

import math
from micropython import const
from firmware.graphics_engine import GraphicsEngine, GraphColors, Point2D

class StatisticalPlotter:
    """Statistical data visualization and plotting"""
    
    def __init__(self, graphics_engine: GraphicsEngine):
        self.graphics = graphics_engine
        self.data = []
        self.bins = 10  # Default number of histogram bins
        
    def set_data(self, data_list: list):
        """Set data for statistical analysis"""
        self.data = [float(x) for x in data_list if x is not None]
        
    def calculate_histogram(self, bins: int = None) -> tuple:
        """Calculate histogram bins and frequencies"""
        if not self.data:
            return [], []
        
        if bins is None:
            bins = self.bins
        
        data_min = min(self.data)
        data_max = max(self.data)
        
        if data_min == data_max:
            return [data_min], [len(self.data)]
        
        # Calculate bin edges
        bin_width = (data_max - data_min) / bins
        bin_edges = [data_min + i * bin_width for i in range(bins + 1)]
        
        # Count frequencies
        frequencies = [0] * bins
        for value in self.data:
            bin_index = min(int((value - data_min) / bin_width), bins - 1)
            frequencies[bin_index] += 1
        
        # Calculate bin centers
        bin_centers = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(bins)]
        
        return bin_centers, frequencies
    
    def plot_histogram(self, bins: int = None, color: int = GraphColors.FUNCTION, 
                      show_outline: bool = True):
        """Plot histogram of data"""
        bin_centers, frequencies = self.calculate_histogram(bins)
        
        if not bin_centers:
            return
        
        # Set appropriate bounds
        x_min = min(bin_centers) - (bin_centers[1] - bin_centers[0])
        x_max = max(bin_centers) + (bin_centers[1] - bin_centers[0])
        y_max = max(frequencies) * 1.1 if frequencies else 1
        
        self.graphics.bounds.x_min = x_min
        self.graphics.bounds.x_max = x_max
        self.graphics.bounds.y_min = 0
        self.graphics.bounds.y_max = y_max
        
        # Clear and draw grid/axes
        self.graphics.render_complete_graph(show_function=False, show_data=False)
        
        # Draw histogram bars
        if len(bin_centers) > 1:
            bar_width = bin_centers[1] - bin_centers[0]
            
            for i, (center, freq) in enumerate(zip(bin_centers, frequencies)):
                if freq > 0:
                    # Calculate bar coordinates
                    left_x = center - bar_width / 2
                    right_x = center + bar_width / 2
                    
                    # Convert to screen coordinates
                    left_screen, bottom_screen = self.graphics.world_to_screen(left_x, 0)
                    right_screen, top_screen = self.graphics.world_to_screen(right_x, freq)
                    
                    # Draw filled rectangle
                    for y in range(top_screen, bottom_screen + 1):
                        self.graphics.draw_line(left_screen, y, right_screen, y, color)
                    
                    # Draw outline if requested
                    if show_outline:
                        self.graphics.draw_line(left_screen, bottom_screen, left_screen, top_screen, GraphColors.AXIS)
                        self.graphics.draw_line(left_screen, top_screen, right_screen, top_screen, GraphColors.AXIS)
                        self.graphics.draw_line(right_screen, top_screen, right_screen, bottom_screen, GraphColors.AXIS)
                        self.graphics.draw_line(right_screen, bottom_screen, left_screen, bottom_screen, GraphColors.AXIS)
    
    def plot_scatter(self, x_data: list, y_data: list, color: int = GraphColors.DATA_POINTS,
                    size: int = 2, show_regression: bool = False):
        """Plot scatter plot with optional regression line"""
        if len(x_data) != len(y_data):
            return
        
        # Prepare data points
        points = list(zip(x_data, y_data))
        
        # Auto-scale bounds
        if points:
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            
            x_range = max(x_vals) - min(x_vals)
            y_range = max(y_vals) - min(y_vals)
            
            self.graphics.bounds.x_min = min(x_vals) - x_range * 0.1
            self.graphics.bounds.x_max = max(x_vals) + x_range * 0.1
            self.graphics.bounds.y_min = min(y_vals) - y_range * 0.1
            self.graphics.bounds.y_max = max(y_vals) + y_range * 0.1
        
        # Clear and draw grid/axes
        self.graphics.render_complete_graph(show_function=False, show_data=False)
        
        # Plot data points
        self.graphics.plot_data_points(points, color, size)
        
        # Add regression line if requested
        if show_regression:
            regression_result = self.graphics.plot_regression_line(points)
            return regression_result
        
        return None
    
    def plot_box_plot(self, data_list: list = None, color: int = GraphColors.FUNCTION):
        """Plot box and whisker plot"""
        if data_list is None:
            data_list = self.data
        
        if not data_list:
            return
        
        # Calculate statistics
        sorted_data = sorted(data_list)
        n = len(sorted_data)
        
        # Calculate quartiles
        q1_index = n // 4
        q2_index = n // 2
        q3_index = 3 * n // 4
        
        q1 = sorted_data[q1_index]
        q2 = sorted_data[q2_index]  # Median
        q3 = sorted_data[q3_index]
        
        iqr = q3 - q1
        lower_whisker = max(min(sorted_data), q1 - 1.5 * iqr)
        upper_whisker = min(max(sorted_data), q3 + 1.5 * iqr)
        
        # Set bounds
        data_range = max(sorted_data) - min(sorted_data)
        self.graphics.bounds.x_min = min(sorted_data) - data_range * 0.1
        self.graphics.bounds.x_max = max(sorted_data) + data_range * 0.1
        self.graphics.bounds.y_min = -1
        self.graphics.bounds.y_max = 1
        
        # Clear and draw grid/axes
        self.graphics.render_complete_graph(show_function=False, show_data=False)
        
        # Draw box plot elements
        box_top = 0.4
        box_bottom = -0.4
        
        # Box
        q1_screen, top_screen = self.graphics.world_to_screen(q1, box_top)
        q3_screen, bottom_screen = self.graphics.world_to_screen(q3, box_bottom)
        
        # Draw box outline
        self.graphics.draw_line(q1_screen, top_screen, q3_screen, top_screen, color)
        self.graphics.draw_line(q3_screen, top_screen, q3_screen, bottom_screen, color)
        self.graphics.draw_line(q3_screen, bottom_screen, q1_screen, bottom_screen, color)
        self.graphics.draw_line(q1_screen, bottom_screen, q1_screen, top_screen, color)
        
        # Median line
        q2_screen, _ = self.graphics.world_to_screen(q2, 0)
        self.graphics.draw_line(q2_screen, top_screen, q2_screen, bottom_screen, GraphColors.AXIS)
        
        # Whiskers
        lower_screen, _ = self.graphics.world_to_screen(lower_whisker, 0)
        upper_screen, _ = self.graphics.world_to_screen(upper_whisker, 0)
        
        # Whisker lines
        self.graphics.draw_line(q1_screen, 0, lower_screen, 0, color)
        self.graphics.draw_line(q3_screen, 0, upper_screen, 0, color)
        
        # Whisker caps
        cap_size = 5
        self.graphics.draw_line(lower_screen, -cap_size, lower_screen, cap_size, color)
        self.graphics.draw_line(upper_screen, -cap_size, upper_screen, cap_size, color)
        
        # Outliers
        outliers = [x for x in sorted_data if x < lower_whisker or x > upper_whisker]
        outlier_points = [(x, 0) for x in outliers]
        self.graphics.plot_data_points(outlier_points, GraphColors.WARNING, 1)
        
        return {
            'q1': q1, 'median': q2, 'q3': q3,
            'lower_whisker': lower_whisker, 'upper_whisker': upper_whisker,
            'outliers': outliers
        }
    
    def plot_time_series(self, time_data: list, value_data: list, 
                        color: int = GraphColors.FUNCTION, connect_points: bool = True):
        """Plot time series data"""
        if len(time_data) != len(value_data):
            return
        
        points = list(zip(time_data, value_data))
        
        # Auto-scale
        if points:
            t_vals = [p[0] for p in points]
            v_vals = [p[1] for p in points]
            
            t_range = max(t_vals) - min(t_vals)
            v_range = max(v_vals) - min(v_vals)
            
            self.graphics.bounds.x_min = min(t_vals) - t_range * 0.05
            self.graphics.bounds.x_max = max(t_vals) + t_range * 0.05
            self.graphics.bounds.y_min = min(v_vals) - v_range * 0.1
            self.graphics.bounds.y_max = max(v_vals) + v_range * 0.1
        
        # Clear and draw grid/axes
        self.graphics.render_complete_graph(show_function=False, show_data=False)
        
        # Plot points
        self.graphics.plot_data_points(points, color, 1)
        
        # Connect points if requested
        if connect_points and len(points) > 1:
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                
                screen_x1, screen_y1 = self.graphics.world_to_screen(x1, y1)
                screen_x2, screen_y2 = self.graphics.world_to_screen(x2, y2)
                
                self.graphics.draw_line(screen_x1, screen_y1, screen_x2, screen_y2, color)
    
    def plot_bar_chart(self, categories: list, values: list, color: int = GraphColors.FUNCTION):
        """Plot bar chart"""
        if len(categories) != len(values):
            return
        
        if not categories:
            return
        
        # Set bounds
        max_val = max(values) if values else 1
        min_val = min(min(values), 0)
        
        self.graphics.bounds.x_min = -0.5
        self.graphics.bounds.x_max = len(categories) - 0.5
        self.graphics.bounds.y_min = min_val - abs(min_val) * 0.1
        self.graphics.bounds.y_max = max_val + abs(max_val) * 0.1
        
        # Clear and draw grid/axes
        self.graphics.render_complete_graph(show_function=False, show_data=False)
        
        # Draw bars
        bar_width = 0.6  # Width of each bar
        
        for i, (category, value) in enumerate(zip(categories, values)):
            if value != 0:  # Only draw non-zero bars
                # Calculate bar coordinates
                left_x = i - bar_width / 2
                right_x = i + bar_width / 2
                
                # Convert to screen coordinates
                left_screen, bottom_screen = self.graphics.world_to_screen(left_x, 0)
                right_screen, top_screen = self.graphics.world_to_screen(right_x, value)
                
                # Draw filled rectangle
                if value > 0:
                    for y in range(top_screen, bottom_screen + 1):
                        self.graphics.draw_line(left_screen, y, right_screen, y, color)
                else:
                    for y in range(bottom_screen, top_screen + 1):
                        self.graphics.draw_line(left_screen, y, right_screen, y, color)
                
                # Draw outline
                self.graphics.draw_line(left_screen, bottom_screen, left_screen, top_screen, GraphColors.AXIS)
                self.graphics.draw_line(left_screen, top_screen, right_screen, top_screen, GraphColors.AXIS)
                self.graphics.draw_line(right_screen, top_screen, right_screen, bottom_screen, GraphColors.AXIS)
                self.graphics.draw_line(right_screen, bottom_screen, left_screen, bottom_screen, GraphColors.AXIS)

class ComplexPlotter:
    """Complex number visualization"""
    
    def __init__(self, graphics_engine: GraphicsEngine):
        self.graphics = graphics_engine
        
    def plot_complex_plane(self, complex_numbers: list, color: int = GraphColors.FUNCTION):
        """Plot complex numbers on complex plane"""
        if not complex_numbers:
            return
        
        # Extract real and imaginary parts
        real_parts = []
        imag_parts = []
        
        for z in complex_numbers:
            if isinstance(z, complex):
                real_parts.append(z.real)
                imag_parts.append(z.imag)
            elif isinstance(z, (list, tuple)) and len(z) >= 2:
                real_parts.append(z[0])
                imag_parts.append(z[1])
        
        if not real_parts:
            return
        
        # Auto-scale
        real_range = max(real_parts) - min(real_parts)
        imag_range = max(imag_parts) - min(imag_parts)
        
        self.graphics.bounds.x_min = min(real_parts) - real_range * 0.1
        self.graphics.bounds.x_max = max(real_parts) + real_range * 0.1
        self.graphics.bounds.y_min = min(imag_parts) - imag_range * 0.1
        self.graphics.bounds.y_max = max(imag_parts) + imag_range * 0.1
        
        # Clear and draw grid/axes
        self.graphics.render_complete_graph(show_function=False, show_data=False)
        
        # Plot complex numbers as points
        points = list(zip(real_parts, imag_parts))
        self.graphics.plot_data_points(points, color, 2)
        
        # Draw vectors from origin to each point
        for real, imag in zip(real_parts, imag_parts):
            origin_screen = self.graphics.world_to_screen(0, 0)
            point_screen = self.graphics.world_to_screen(real, imag)
            
            self.graphics.draw_line(origin_screen[0], origin_screen[1], 
                                  point_screen[0], point_screen[1], color)
    
    def plot_mandelbrot_zoom(self, center_real: float = -0.5, center_imag: float = 0.0,
                           zoom: float = 1.0, max_iterations: int = 50):
        """Plot zoomed view of Mandelbrot set"""
        width = 2.0 / zoom
        height = 2.0 / zoom
        
        self.graphics.bounds.x_min = center_real - width / 2
        self.graphics.bounds.x_max = center_real + width / 2
        self.graphics.bounds.y_min = center_imag - height / 2
        self.graphics.bounds.y_max = center_imag + height / 2
        
        # Clear graph area
        self.graphics.clear_graph_area()
        
        # Calculate Mandelbrot set pixel by pixel
        for screen_y in range(20, 220, 2):  # Graph area with step for performance
            for screen_x in range(20, 300, 2):
                # Convert screen to world coordinates
                real, imag = self.graphics.screen_to_world(screen_x, screen_y)
                
                # Calculate Mandelbrot iterations
                c = complex(real, imag)
                z = 0
                iterations = 0
                
                while abs(z) <= 2 and iterations < max_iterations:
                    z = z * z + c
                    iterations += 1
                
                # Color based on iterations
                if iterations == max_iterations:
                    color = GraphColors.BACKGROUND  # Inside set
                else:
                    # Outside set - color by iteration count
                    intensity = min(255, iterations * 5)
                    color = (intensity >> 3) << 11  # Red channel for RGB565
                
                self.graphics.draw_pixel(screen_x, screen_y, color)
                self.graphics.draw_pixel(screen_x + 1, screen_y, color)
                self.graphics.draw_pixel(screen_x, screen_y + 1, color)
                self.graphics.draw_pixel(screen_x + 1, screen_y + 1, color)

# Export classes
__all__ = ['StatisticalPlotter', 'ComplexPlotter']