"""
Phase 5 Performance Optimization
===============================

Optimized rendering and computation routines for Raspberry Pi Pico 2W hardware
to ensure smooth real-time graphing performance.
"""

import micropython
import gc
import time
from micropython import const

# Performance constants
PERFORMANCE_MODE_ECO = const(0)      # Balanced performance/quality
PERFORMANCE_MODE_FAST = const(1)     # Maximum speed
PERFORMANCE_MODE_QUALITY = const(2)  # Maximum quality

# Rendering optimization levels
RENDER_SKIP_PIXELS = const(2)        # Skip every N pixels in fast mode
RENDER_MIN_DETAIL = const(10)        # Minimum function samples
RENDER_MAX_DETAIL = const(500)       # Maximum function samples

class PerformanceOptimizer:
    """Performance optimization manager for graphing operations"""
    
    def __init__(self):
        self.mode = PERFORMANCE_MODE_ECO
        self.frame_times = []
        self.target_fps = 10  # Target frames per second
        self.max_frame_time = 1000 // self.target_fps  # ms
        
        # Adaptive quality settings
        self.function_samples = 200
        self.surface_resolution = 20
        self.mandelbrot_iterations = 50
        
        # Memory monitoring
        self.memory_threshold = 10000  # Reserve 10KB
        
    def set_performance_mode(self, mode: int):
        """Set performance optimization mode"""
        self.mode = mode
        
        if mode == PERFORMANCE_MODE_ECO:
            self.function_samples = 200
            self.surface_resolution = 20
            self.mandelbrot_iterations = 50
        elif mode == PERFORMANCE_MODE_FAST:
            self.function_samples = 100
            self.surface_resolution = 15
            self.mandelbrot_iterations = 30
        elif mode == PERFORMANCE_MODE_QUALITY:
            self.function_samples = 400
            self.surface_resolution = 30
            self.mandelbrot_iterations = 100
    
    def start_frame(self):
        """Start frame timing"""
        return time.ticks_ms()
    
    def end_frame(self, start_time: int) -> bool:
        """End frame timing and adapt quality"""
        end_time = time.ticks_ms()
        frame_time = time.ticks_diff(end_time, start_time)
        
        # Track frame times
        self.frame_times.append(frame_time)
        if len(self.frame_times) > 10:
            self.frame_times.pop(0)
        
        # Adaptive quality adjustment
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        
        if avg_frame_time > self.max_frame_time * 1.5:
            # Too slow - reduce quality
            self._reduce_quality()
            return False
        elif avg_frame_time < self.max_frame_time * 0.5:
            # Fast enough - can increase quality
            self._increase_quality()
            return True
        
        return True
    
    def _reduce_quality(self):
        """Reduce rendering quality for better performance"""
        if self.function_samples > RENDER_MIN_DETAIL:
            self.function_samples = max(RENDER_MIN_DETAIL, self.function_samples - 20)
        
        if self.surface_resolution > 10:
            self.surface_resolution = max(10, self.surface_resolution - 2)
        
        if self.mandelbrot_iterations > 10:
            self.mandelbrot_iterations = max(10, self.mandelbrot_iterations - 5)
    
    def _increase_quality(self):
        """Increase rendering quality when performance allows"""
        if self.function_samples < RENDER_MAX_DETAIL:
            self.function_samples = min(RENDER_MAX_DETAIL, self.function_samples + 10)
        
        if self.surface_resolution < 40:
            self.surface_resolution = min(40, self.surface_resolution + 1)
        
        if self.mandelbrot_iterations < 150:
            self.mandelbrot_iterations = min(150, self.mandelbrot_iterations + 5)
    
    def check_memory_pressure(self) -> bool:
        """Check if memory usage is too high"""
        gc.collect()
        free_mem = gc.mem_free()
        return free_mem < self.memory_threshold
    
    def optimize_function_sampling(self, x_min: float, x_max: float) -> int:
        """Calculate optimal function sampling based on performance"""
        base_samples = self.function_samples
        
        # Adjust based on domain size
        domain_factor = (x_max - x_min) / 10  # Normalize to typical range
        adjusted_samples = int(base_samples * min(2.0, max(0.5, domain_factor)))
        
        return max(RENDER_MIN_DETAIL, min(RENDER_MAX_DETAIL, adjusted_samples))

@micropython.native
def fast_line_draw(display, x0: int, y0: int, x1: int, y1: int, color: int):
    """Optimized line drawing using Bresenham's algorithm"""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    if dx == 0 and dy == 0:
        display.pixel(x0, y0, color)
        return
    
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    x, y = x0, y0
    
    while True:
        display.pixel(x, y, color)
        
        if x == x1 and y == y1:
            break
        
        e2 = 2 * err
        
        if e2 > -dy:
            err -= dy
            x += sx
        
        if e2 < dx:
            err += dx
            y += sy

@micropython.native
def fast_function_plot(graphics_engine, optimizer) -> bool:
    """Optimized function plotting with adaptive sampling"""
    start_time = optimizer.start_frame()
    
    if not graphics_engine.function_expression:
        return False
    
    bounds = graphics_engine.bounds
    
    # Calculate optimal sample count
    samples = optimizer.optimize_function_sampling(bounds.x_min, bounds.x_max)
    
    # Check memory before starting
    if optimizer.check_memory_pressure():
        samples = min(samples, RENDER_MIN_DETAIL * 2)
        gc.collect()
    
    step = (bounds.x_max - bounds.x_min) / samples
    
    prev_screen_x = None
    prev_screen_y = None
    
    # Fast sampling with early termination on performance issues
    for i in range(samples):
        # Check if we're taking too long
        if i % 50 == 0 and time.ticks_diff(time.ticks_ms(), start_time) > optimizer.max_frame_time:
            break
        
        x = bounds.x_min + i * step
        
        try:
            y = graphics_engine.evaluate_function(x, graphics_engine.function_expression)
            
            if y is None or not (-1e6 < y < 1e6):  # Skip invalid/infinite values
                prev_screen_x = None
                continue
            
            screen_x, screen_y = graphics_engine.world_to_screen(x, y)
            
            # Skip if point is off-screen
            if not (20 <= screen_x <= 300 and 20 <= screen_y <= 220):
                prev_screen_x = None
                continue
            
            if prev_screen_x is not None:
                # Use fast line drawing
                fast_line_draw(graphics_engine.display, 
                              prev_screen_x, prev_screen_y,
                              screen_x, screen_y, 
                              graphics_engine.function_color)
            
            prev_screen_x = screen_x
            prev_screen_y = screen_y
            
        except:
            prev_screen_x = None
            continue
    
    return optimizer.end_frame(start_time)

@micropython.native
def fast_surface_render(plot_3d, surface, optimizer):
    """Optimized 3D surface rendering"""
    start_time = optimizer.start_frame()
    
    if not surface or not surface.triangles:
        return False
    
    # Sort triangles by depth (painter's algorithm)
    triangles_with_depth = []
    
    for triangle in surface.triangles:
        # Calculate average Z of triangle vertices
        avg_z = sum(surface.points[i].z for i in triangle) / 3
        triangles_with_depth.append((triangle, avg_z))
    
    # Sort by depth (farthest first)
    triangles_with_depth.sort(key=lambda x: x[1], reverse=True)
    
    # Render triangles
    rendered_triangles = 0
    max_triangles = len(triangles_with_depth)
    
    # Adaptive triangle culling for performance
    if optimizer.mode == PERFORMANCE_MODE_FAST:
        max_triangles = min(max_triangles, 200)
    elif optimizer.mode == PERFORMANCE_MODE_ECO:
        max_triangles = min(max_triangles, 400)
    
    for i, (triangle, _) in enumerate(triangles_with_depth[:max_triangles]):
        # Check performance every 20 triangles
        if i % 20 == 0 and time.ticks_diff(time.ticks_ms(), start_time) > optimizer.max_frame_time:
            break
        
        # Get triangle vertices
        p1 = surface.points[triangle[0]]
        p2 = surface.points[triangle[1]]
        p3 = surface.points[triangle[2]]
        
        # Project to screen
        sx1, sy1, sz1 = plot_3d.project_point(p1)
        sx2, sy2, sz2 = plot_3d.project_point(p2)
        sx3, sy3, sz3 = plot_3d.project_point(p3)
        
        # Simple backface culling
        if plot_3d._is_backface(p1, p2, p3):
            continue
        
        # Draw triangle edges
        color = plot_3d._calculate_triangle_color(p1, p2, p3)
        
        fast_line_draw(plot_3d.graphics.display, sx1, sy1, sx2, sy2, color)
        fast_line_draw(plot_3d.graphics.display, sx2, sy2, sx3, sy3, color)
        fast_line_draw(plot_3d.graphics.display, sx3, sy3, sx1, sy1, color)
        
        rendered_triangles += 1
    
    return optimizer.end_frame(start_time)

@micropython.native
def fast_histogram_render(stats_plotter, bins: int, optimizer):
    """Optimized histogram rendering"""
    start_time = optimizer.start_frame()
    
    if not stats_plotter.data:
        return False
    
    # Calculate histogram with adaptive binning
    if optimizer.mode == PERFORMANCE_MODE_FAST:
        bins = min(bins, 20)
    
    bin_centers, frequencies = stats_plotter.calculate_histogram(bins)
    
    if not bin_centers or not frequencies:
        return False
    
    # Find scale factors
    max_freq = max(frequencies)
    if max_freq == 0:
        return False
    
    # Draw histogram bars
    bar_width = 240 // bins
    
    for i, freq in enumerate(frequencies):
        if time.ticks_diff(time.ticks_ms(), start_time) > optimizer.max_frame_time:
            break
        
        if freq == 0:
            continue
        
        # Calculate bar dimensions
        bar_height = int((freq / max_freq) * 160)
        x = 40 + i * bar_width
        y = 200 - bar_height
        
        # Draw bar outline (optimized rectangle)
        color = stats_plotter.bar_color
        
        # Draw efficient rectangle
        for dy in range(0, bar_height, 2 if optimizer.mode == PERFORMANCE_MODE_FAST else 1):
            fast_line_draw(stats_plotter.graphics.display,
                          x, y + dy, x + bar_width - 1, y + dy, color)
    
    return optimizer.end_frame(start_time)

class OptimizedGraphicsEngine:
    """Graphics engine with built-in performance optimization"""
    
    def __init__(self, base_graphics_engine):
        self.base = base_graphics_engine
        self.optimizer = PerformanceOptimizer()
        
    def plot_function_optimized(self) -> bool:
        """Plot function with performance optimization"""
        return fast_function_plot(self.base, self.optimizer)
    
    def render_3d_optimized(self, plot_3d, surface) -> bool:
        """Render 3D surface with optimization"""
        return fast_surface_render(plot_3d, surface, self.optimizer)
    
    def plot_histogram_optimized(self, stats_plotter, bins: int) -> bool:
        """Plot histogram with optimization"""
        return fast_histogram_render(stats_plotter, bins, self.optimizer)
    
    def set_performance_mode(self, mode: int):
        """Set performance mode"""
        self.optimizer.set_performance_mode(mode)
    
    def get_performance_stats(self) -> dict:
        """Get current performance statistics"""
        if not self.optimizer.frame_times:
            return {"avg_frame_time": 0, "fps": 0}
        
        avg_time = sum(self.optimizer.frame_times) / len(self.optimizer.frame_times)
        fps = 1000 / max(1, avg_time)
        
        return {
            "avg_frame_time": avg_time,
            "fps": fps,
            "function_samples": self.optimizer.function_samples,
            "surface_resolution": self.optimizer.surface_resolution,
            "mandelbrot_iterations": self.optimizer.mandelbrot_iterations,
            "memory_free": gc.mem_free()
        }

def create_optimized_graphics_engine(display):
    """Factory function to create optimized graphics engine"""
    from firmware.graphics_engine import GraphicsEngine
    
    base_engine = GraphicsEngine(display)
    return OptimizedGraphicsEngine(base_engine)