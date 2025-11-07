"""
Phase 5 Complete Integration
==========================

Final integration of all Phase 5 advanced graphing components with the Peanut 3000 Calculator.
This module ensures seamless operation of 2D/3D graphing, statistical visualization,
complex number plotting, and interactive navigation controls.
"""

import gc
from firmware.graphics_engine import GraphicsEngine
from firmware.statistical_plots import StatisticalPlotter, ComplexPlotter
from firmware.interactive_3d import Surface3D, Plot3DEngine, InteractiveGraphControls
from firmware.performance_optimizer import OptimizedGraphicsEngine, PERFORMANCE_MODE_ECO

class Phase5GraphingSystem:
    """Complete Phase 5 graphing system integration"""
    
    def __init__(self, display, hardware_config):
        """Initialize complete graphing system"""
        self.display = display
        self.hardware_config = hardware_config
        
        # Initialize core graphics engine with optimization
        self.base_graphics = GraphicsEngine(display)
        self.graphics_engine = OptimizedGraphicsEngine(self.base_graphics)
        
        # Initialize specialized plotters
        self.stats_plotter = StatisticalPlotter(self.base_graphics)
        self.complex_plotter = ComplexPlotter(self.base_graphics)
        
        # Initialize 3D system
        self.plot_3d = Plot3DEngine(self.base_graphics)
        self.surface_cache = {}
        
        # Initialize interactive controls
        self.controls = InteractiveGraphControls(self.base_graphics)
        self.controls.plot_3d = self.plot_3d
        
        # Current state
        self.current_mode = "2D"
        self.current_function = ""
        self.current_data = []
        self.performance_mode = PERFORMANCE_MODE_ECO
        
        print("✅ Phase 5 Advanced Graphing System initialized")
    
    def set_performance_mode(self, mode: int):
        """Set system-wide performance mode"""
        self.performance_mode = mode
        self.graphics_engine.set_performance_mode(mode)
        print(f"🚀 Performance mode set to: {['ECO', 'FAST', 'QUALITY'][mode]}")
    
    def plot_function_2d(self, expression: str) -> bool:
        """Plot 2D mathematical function"""
        try:
            self.current_mode = "2D"
            self.current_function = expression
            self.controls.mode = "2D"
            
            # Clear display
            self.display.clear()
            
            # Set function in graphics engine
            self.base_graphics.function_expression = expression
            
            # Auto-scale if needed
            self.base_graphics.auto_scale()
            
            # Draw coordinate system
            self.base_graphics.draw_axes()
            self.base_graphics.draw_grid()
            
            # Plot function with optimization
            success = self.graphics_engine.plot_function_optimized()
            
            if success:
                print(f"📈 Plotted 2D function: {expression}")
            else:
                print(f"⚠️ Failed to plot function: {expression}")
            
            return success
            
        except Exception as e:
            print(f"❌ 2D plotting error: {e}")
            return False
    
    def plot_statistical_data(self, data: list, plot_type: str = "histogram") -> bool:
        """Plot statistical data visualization"""
        try:
            self.current_mode = "stats"
            self.current_data = data
            
            if not data:
                print("⚠️ No data provided for statistical plot")
                return False
            
            # Clear display
            self.display.clear()
            
            # Set data in plotter
            self.stats_plotter.set_data(data)
            
            # Draw coordinate system
            self.base_graphics.draw_axes()
            
            success = False
            
            if plot_type == "histogram":
                bins = min(20, len(set(data)))  # Adaptive bin count
                success = self.graphics_engine.plot_histogram_optimized(
                    self.stats_plotter, bins)
            
            elif plot_type == "box_plot":
                result = self.stats_plotter.plot_box_plot(data)
                success = result is not None
            
            elif plot_type == "scatter":
                # For scatter plot, split data into x,y pairs
                if len(data) >= 2:
                    mid = len(data) // 2
                    x_data = data[:mid]
                    y_data = data[mid:]
                    regression_result = self.stats_plotter.plot_scatter(
                        x_data, y_data, show_regression=True)
                    success = regression_result is not None
            
            if success:
                print(f"📊 Plotted {plot_type} for {len(data)} data points")
            else:
                print(f"⚠️ Failed to plot {plot_type}")
            
            return success
            
        except Exception as e:
            print(f"❌ Statistical plotting error: {e}")
            return False
    
    def plot_3d_surface(self, expression: str, x_range: tuple = (-5, 5), 
                       y_range: tuple = (-5, 5)) -> bool:
        """Plot 3D surface"""
        try:
            self.current_mode = "3D"
            self.current_function = expression
            self.controls.mode = "3D"
            
            # Check cache for existing surface
            cache_key = f"{expression}_{x_range}_{y_range}_{self.graphics_engine.optimizer.surface_resolution}"
            
            if cache_key in self.surface_cache:
                surface = self.surface_cache[cache_key]
                print("📦 Using cached 3D surface")
            else:
                # Generate new surface
                surface = Surface3D(expression, x_range, y_range, 
                                  self.graphics_engine.optimizer.surface_resolution)
                surface.generate_mesh(self.base_graphics.math_engine)
                
                # Cache surface if it's valid
                if surface.points and surface.triangles:
                    self.surface_cache[cache_key] = surface
                    # Limit cache size
                    if len(self.surface_cache) > 5:
                        oldest_key = next(iter(self.surface_cache))
                        del self.surface_cache[oldest_key]
                
                print(f"🏗️ Generated 3D surface: {len(surface.points)} points, {len(surface.triangles)} triangles")
            
            if not surface.points:
                print("⚠️ Failed to generate 3D surface")
                return False
            
            # Clear display
            self.display.clear()
            
            # Draw 3D axes
            self.plot_3d.draw_3d_axes()
            
            # Render surface with optimization
            success = self.graphics_engine.render_3d_optimized(self.plot_3d, surface)
            
            if success:
                print(f"🎯 Rendered 3D surface: {expression}")
            else:
                print(f"⚠️ Failed to render 3D surface")
            
            return success
            
        except Exception as e:
            print(f"❌ 3D plotting error: {e}")
            return False
    
    def plot_complex_numbers(self, complex_list: list = None, 
                           mandelbrot_zoom: float = 1.0) -> bool:
        """Plot complex number visualization"""
        try:
            self.current_mode = "complex"
            
            # Clear display
            self.display.clear()
            
            # Draw complex plane axes
            self.complex_plotter.draw_complex_axes()
            
            success = False
            
            if complex_list:
                # Plot specific complex numbers
                self.complex_plotter.plot_complex_plane(complex_list)
                success = True
                print(f"🔢 Plotted {len(complex_list)} complex numbers")
            else:
                # Plot Mandelbrot set
                iterations = self.graphics_engine.optimizer.mandelbrot_iterations
                self.complex_plotter.plot_mandelbrot_zoom(
                    center_real=-0.5, center_imag=0.0, 
                    zoom=mandelbrot_zoom, max_iterations=iterations)
                success = True
                print(f"🌀 Plotted Mandelbrot set (zoom: {mandelbrot_zoom:.2f})")
            
            return success
            
        except Exception as e:
            print(f"❌ Complex plotting error: {e}")
            return False
    
    def handle_key_input(self, key: str) -> bool:
        """Handle interactive navigation input"""
        try:
            # Pass key to controls system
            redraw_needed = self.controls.handle_key_press(key)
            
            if redraw_needed:
                # Redraw current content based on mode
                if self.current_mode == "2D" and self.current_function:
                    self.plot_function_2d(self.current_function)
                elif self.current_mode == "3D" and self.current_function:
                    # Don't regenerate surface, just re-render
                    self.display.clear()
                    self.plot_3d.draw_3d_axes()
                    
                    # Find cached surface
                    for surface in self.surface_cache.values():
                        if surface.expression == self.current_function:
                            self.graphics_engine.render_3d_optimized(self.plot_3d, surface)
                            break
                elif self.current_mode == "stats" and self.current_data:
                    self.plot_statistical_data(self.current_data, "histogram")
                elif self.current_mode == "complex":
                    self.plot_complex_numbers()
            
            return redraw_needed
            
        except Exception as e:
            print(f"❌ Input handling error: {e}")
            return False
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        try:
            perf_stats = self.graphics_engine.get_performance_stats()
            
            status = {
                "mode": self.current_mode,
                "function": self.current_function,
                "data_points": len(self.current_data),
                "performance": perf_stats,
                "cache_size": len(self.surface_cache),
                "memory_free": gc.mem_free(),
                "controls_mode": self.controls.mode,
            }
            
            # Add mode-specific status
            if self.current_mode == "2D":
                bounds = self.base_graphics.bounds
                status["bounds"] = {
                    "x_min": bounds.x_min,
                    "x_max": bounds.x_max,
                    "y_min": bounds.y_min,
                    "y_max": bounds.y_max
                }
                if hasattr(self.base_graphics, 'trace_x'):
                    status["trace_x"] = self.base_graphics.trace_x
            
            elif self.current_mode == "3D":
                status["3d_rotation"] = {
                    "x": self.plot_3d.rotation_x,
                    "y": self.plot_3d.rotation_y,
                    "z": self.plot_3d.rotation_z
                }
                status["3d_zoom"] = self.plot_3d.zoom
            
            return status
            
        except Exception as e:
            print(f"❌ Status error: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Cleanup resources and cache"""
        try:
            # Clear surface cache
            self.surface_cache.clear()
            
            # Force garbage collection
            gc.collect()
            
            print("🧹 Phase 5 system cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

# Global system instance for easy access
_phase5_system = None

def get_phase5_system():
    """Get the global Phase 5 system instance"""
    global _phase5_system
    return _phase5_system

def initialize_phase5_system(display, hardware_config):
    """Initialize the global Phase 5 system"""
    global _phase5_system
    _phase5_system = Phase5GraphingSystem(display, hardware_config)
    return _phase5_system

def demo_phase5_capabilities(system):
    """Demonstrate Phase 5 graphing capabilities"""
    print("\n🚀 Phase 5 Advanced Graphing Demo")
    print("=" * 40)
    
    # 2D function plotting demo
    print("\n1. 2D Function Plotting:")
    system.plot_function_2d("sin(x) * cos(x)")
    
    # Statistical plotting demo  
    print("\n2. Statistical Visualization:")
    import random
    test_data = [random.gauss(50, 15) for _ in range(100)]
    system.plot_statistical_data(test_data, "histogram")
    
    # 3D surface plotting demo
    print("\n3. 3D Surface Plotting:")
    system.plot_3d_surface("x**2 + y**2", (-3, 3), (-3, 3))
    
    # Complex number plotting demo
    print("\n4. Complex Number Visualization:")
    complex_numbers = [complex(i*0.5, j*0.5) for i in range(-4, 5) for j in range(-4, 5)]
    system.plot_complex_numbers(complex_numbers)
    
    # Performance status
    print("\n5. System Status:")
    status = system.get_system_status()
    print(f"   Memory Free: {status['memory_free']} bytes")
    print(f"   FPS: {status['performance']['fps']:.1f}")
    print(f"   Cache Size: {status['cache_size']} surfaces")
    
    print("\n✅ Phase 5 demo completed successfully!")

# Export key components for easy importing
__all__ = [
    'Phase5GraphingSystem',
    'initialize_phase5_system', 
    'get_phase5_system',
    'demo_phase5_capabilities'
]