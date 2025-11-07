"""
3D Visualization and Interactive Controls for Peanut 3000 Calculator
====================================================================

Advanced 3D surface plotting, wireframe rendering, and interactive navigation
controls for mathematical visualization and exploration.
"""

import math
from micropython import const
from firmware.graphics_engine import GraphicsEngine, Point3D, GraphColors

class Surface3D:
    """3D surface representation"""
    
    def __init__(self, function_expr: str, x_range: tuple = (-5, 5), 
                 y_range: tuple = (-5, 5), resolution: int = 20):
        self.function_expr = function_expr
        self.x_min, self.x_max = x_range
        self.y_min, self.y_max = y_range
        self.resolution = resolution
        self.points = []
        self.triangles = []  # Triangle faces for rendering
        
    def generate_mesh(self, math_engine):
        """Generate 3D mesh points from function"""
        self.points.clear()
        self.triangles.clear()
        
        x_step = (self.x_max - self.x_min) / (self.resolution - 1)
        y_step = (self.y_max - self.y_min) / (self.resolution - 1)
        
        # Generate grid points
        point_grid = []
        for i in range(self.resolution):
            row = []
            for j in range(self.resolution):
                x = self.x_min + i * x_step
                y = self.y_min + j * y_step
                
                try:
                    # Evaluate function at (x, y)
                    expr = self.function_expr.replace('x', str(x)).replace('y', str(y))
                    z = math_engine.safe_evaluate(expr)
                    if isinstance(z, complex):
                        z = z.real
                    
                    if not (math.isnan(z) or math.isinf(z)):
                        point = Point3D(x, y, float(z))
                    else:
                        point = Point3D(x, y, 0.0)
                        
                except:
                    point = Point3D(x, y, 0.0)
                
                row.append(point)
                self.points.append(point)
            point_grid.append(row)
        
        # Generate triangular faces
        for i in range(self.resolution - 1):
            for j in range(self.resolution - 1):
                # Two triangles per grid cell
                p1 = i * self.resolution + j
                p2 = i * self.resolution + j + 1
                p3 = (i + 1) * self.resolution + j
                p4 = (i + 1) * self.resolution + j + 1
                
                # Triangle 1: p1, p2, p3
                self.triangles.append((p1, p2, p3))
                # Triangle 2: p2, p4, p3
                self.triangles.append((p2, p4, p3))

class Plot3DEngine:
    """3D plotting and visualization engine"""
    
    def __init__(self, graphics_engine: GraphicsEngine):
        self.graphics = graphics_engine
        
        # 3D viewing parameters
        self.view_distance = 15.0
        self.rotation_x = 0.3  # Tilt angle
        self.rotation_y = 0.8  # Azimuth angle
        self.rotation_z = 0.0  # Roll angle
        
        # Rendering settings
        self.show_wireframe = True
        self.show_surface = False
        self.show_axes = True
        self.cull_backfaces = True
        
        # Current surface
        self.current_surface = None
        
    def set_view_angles(self, angle_x: float, angle_y: float, angle_z: float = 0.0):
        """Set 3D viewing angles"""
        self.rotation_x = angle_x
        self.rotation_y = angle_y
        self.rotation_z = angle_z
        
    def project_point(self, point: Point3D) -> tuple:
        """Project 3D point to 2D screen coordinates"""
        # Apply rotations
        x, y, z = point.x, point.y, point.z
        
        # Rotation around X axis
        cos_x, sin_x = math.cos(self.rotation_x), math.sin(self.rotation_x)
        y1 = y * cos_x - z * sin_x
        z1 = y * sin_x + z * cos_x
        
        # Rotation around Y axis  
        cos_y, sin_y = math.cos(self.rotation_y), math.sin(self.rotation_y)
        x2 = x * cos_y + z1 * sin_y
        z2 = -x * sin_y + z1 * cos_y
        
        # Rotation around Z axis
        cos_z, sin_z = math.cos(self.rotation_z), math.sin(self.rotation_z)
        x3 = x2 * cos_z - y1 * sin_z
        y3 = x2 * sin_z + y1 * cos_z
        
        # Perspective projection
        if z2 + self.view_distance == 0:
            z2 = 0.001  # Avoid division by zero
            
        factor = self.view_distance / (z2 + self.view_distance)
        
        # Scale and center on screen
        screen_x = 160 + int(x3 * factor * 20)  # Center X with scaling
        screen_y = 120 + int(-y3 * factor * 20)  # Center Y with scaling (inverted)
        
        return screen_x, screen_y, z2
    
    def draw_3d_axes(self, length: float = 5.0):
        """Draw 3D coordinate axes"""
        origin = Point3D(0, 0, 0)
        
        # X axis (red)
        x_axis = Point3D(length, 0, 0)
        origin_2d = self.project_point(origin)
        x_axis_2d = self.project_point(x_axis)
        self.graphics.draw_line(origin_2d[0], origin_2d[1], x_axis_2d[0], x_axis_2d[1], 
                               GraphColors.WARNING)
        
        # Y axis (green)
        y_axis = Point3D(0, length, 0)
        y_axis_2d = self.project_point(y_axis)
        self.graphics.draw_line(origin_2d[0], origin_2d[1], y_axis_2d[0], y_axis_2d[1], 
                               GraphColors.SUCCESS)
        
        # Z axis (blue)
        z_axis = Point3D(0, 0, length)
        z_axis_2d = self.project_point(z_axis)
        self.graphics.draw_line(origin_2d[0], origin_2d[1], z_axis_2d[0], z_axis_2d[1], 
                               GraphColors.INFO)
    
    def draw_wireframe(self, surface: Surface3D, color: int = GraphColors.FUNCTION):
        """Draw wireframe representation of 3D surface"""
        if not surface.points or not surface.triangles:
            return
        
        # Project all points
        projected_points = []
        for point in surface.points:
            proj_x, proj_y, proj_z = self.project_point(point)
            projected_points.append((proj_x, proj_y, proj_z))
        
        # Draw triangle edges
        drawn_edges = set()  # Avoid drawing same edge twice
        
        for triangle in surface.triangles:
            p1_idx, p2_idx, p3_idx = triangle
            
            # Skip if any point is out of bounds
            if (p1_idx >= len(projected_points) or 
                p2_idx >= len(projected_points) or 
                p3_idx >= len(projected_points)):
                continue
            
            p1 = projected_points[p1_idx]
            p2 = projected_points[p2_idx] 
            p3 = projected_points[p3_idx]
            
            # Backface culling (simple z-test)
            if self.cull_backfaces:
                avg_z = (p1[2] + p2[2] + p3[2]) / 3
                if avg_z < -2:  # Behind viewer
                    continue
            
            # Draw edges
            edges = [(p1_idx, p2_idx), (p2_idx, p3_idx), (p3_idx, p1_idx)]
            
            for edge in edges:
                # Create consistent edge key (smaller index first)
                edge_key = tuple(sorted(edge))
                
                if edge_key not in drawn_edges:
                    drawn_edges.add(edge_key)
                    
                    pt1 = projected_points[edge[0]]
                    pt2 = projected_points[edge[1]]
                    
                    # Only draw if both points are on screen
                    if (0 <= pt1[0] < 320 and 0 <= pt1[1] < 240 and
                        0 <= pt2[0] < 320 and 0 <= pt2[1] < 240):
                        self.graphics.draw_line(pt1[0], pt1[1], pt2[0], pt2[1], color)
    
    def plot_parametric_3d(self, x_expr: str, y_expr: str, z_expr: str,
                          t_range: tuple = (0, 2*math.pi), resolution: int = 100,
                          color: int = GraphColors.FUNCTION):
        """Plot 3D parametric curve"""
        t_min, t_max = t_range
        t_step = (t_max - t_min) / resolution
        
        points_3d = []
        t = t_min
        
        for _ in range(resolution + 1):
            try:
                # Substitute parameter t
                x_eval = x_expr.replace('t', str(t))
                y_eval = y_expr.replace('t', str(t))  
                z_eval = z_expr.replace('t', str(t))
                
                x = self.graphics.math_engine.safe_evaluate(x_eval)
                y = self.graphics.math_engine.safe_evaluate(y_eval)
                z = self.graphics.math_engine.safe_evaluate(z_eval)
                
                if isinstance(x, complex): x = x.real
                if isinstance(y, complex): y = y.real
                if isinstance(z, complex): z = z.real
                
                if not any(math.isnan(val) or math.isinf(val) for val in [x, y, z]):
                    points_3d.append(Point3D(float(x), float(y), float(z)))
                    
            except:
                pass  # Skip invalid points
            
            t += t_step
        
        # Project and draw curve
        if len(points_3d) > 1:
            prev_screen = None
            
            for point_3d in points_3d:
                screen_x, screen_y, screen_z = self.project_point(point_3d)
                
                # Draw line to previous point
                if (prev_screen is not None and 
                    0 <= screen_x < 320 and 0 <= screen_y < 240):
                    self.graphics.draw_line(prev_screen[0], prev_screen[1], 
                                          screen_x, screen_y, color)
                
                prev_screen = (screen_x, screen_y, screen_z)
    
    def render_3d_scene(self, surface: Surface3D = None):
        """Render complete 3D scene"""
        # Clear screen
        self.graphics.clear_graph_area()
        
        # Draw 3D axes
        if self.show_axes:
            self.draw_3d_axes()
        
        # Draw surface
        if surface:
            if self.show_wireframe:
                self.draw_wireframe(surface)

class InteractiveGraphControls:
    """Interactive graph navigation and control system"""
    
    def __init__(self, graphics_engine: GraphicsEngine):
        self.graphics = graphics_engine
        self.plot_3d = Plot3DEngine(graphics_engine)
        
        # Navigation state
        self.zoom_level = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        
        # Interaction modes
        self.mode = "2D"  # "2D", "3D", "trace", "zoom", "pan"
        
        # Trace state
        self.trace_active = False
        self.trace_x = 0.0
        self.trace_step = 0.1
        
    def handle_key_press(self, key: str):
        """Handle keypad input for graph navigation"""
        
        if self.mode == "2D":
            return self._handle_2d_controls(key)
        elif self.mode == "3D":
            return self._handle_3d_controls(key)
        elif self.mode == "trace":
            return self._handle_trace_controls(key)
        else:
            return False
    
    def _handle_2d_controls(self, key: str) -> bool:
        """Handle 2D graph navigation"""
        redraw_needed = False
        
        if key == "+":
            # Zoom in
            self.graphics.bounds.zoom(1.5)
            redraw_needed = True
            
        elif key == "-":
            # Zoom out
            self.graphics.bounds.zoom(0.67)
            redraw_needed = True
            
        elif key == "8":  # Up arrow
            # Pan up
            pan_amount = self.graphics.bounds.height() * 0.1
            self.graphics.bounds.pan(0, pan_amount)
            redraw_needed = True
            
        elif key == "2":  # Down arrow
            # Pan down
            pan_amount = self.graphics.bounds.height() * 0.1
            self.graphics.bounds.pan(0, -pan_amount)
            redraw_needed = True
            
        elif key == "4":  # Left arrow
            # Pan left
            pan_amount = self.graphics.bounds.width() * 0.1
            self.graphics.bounds.pan(-pan_amount, 0)
            redraw_needed = True
            
        elif key == "6":  # Right arrow
            # Pan right
            pan_amount = self.graphics.bounds.width() * 0.1
            self.graphics.bounds.pan(pan_amount, 0)
            redraw_needed = True
            
        elif key == "5":  # Center
            # Reset view
            self.graphics.bounds = self.graphics.bounds.__class__()  # Reset to default
            redraw_needed = True
            
        elif key == "ENTER":
            # Auto-scale
            self.graphics.auto_scale()
            redraw_needed = True
            
        elif key == "F1":
            # Toggle trace mode
            self.mode = "trace"
            self.trace_active = True
            self.graphics.show_trace = True
            redraw_needed = True
            
        elif key == "F2":
            # Switch to 3D mode
            self.mode = "3D"
            redraw_needed = True
            
        return redraw_needed
    
    def _handle_3d_controls(self, key: str) -> bool:
        """Handle 3D visualization controls"""
        redraw_needed = False
        
        if key == "8":  # Rotate up
            self.plot_3d.rotation_x -= 0.1
            redraw_needed = True
            
        elif key == "2":  # Rotate down
            self.plot_3d.rotation_x += 0.1
            redraw_needed = True
            
        elif key == "4":  # Rotate left
            self.plot_3d.rotation_y -= 0.1
            redraw_needed = True
            
        elif key == "6":  # Rotate right
            self.plot_3d.rotation_y += 0.1
            redraw_needed = True
            
        elif key == "+":  # Zoom in
            self.plot_3d.view_distance *= 0.9
            redraw_needed = True
            
        elif key == "-":  # Zoom out
            self.plot_3d.view_distance *= 1.1
            redraw_needed = True
            
        elif key == "F1":
            # Toggle wireframe/surface
            self.plot_3d.show_wireframe = not self.plot_3d.show_wireframe
            redraw_needed = True
            
        elif key == "F2":
            # Switch back to 2D mode
            self.mode = "2D"
            redraw_needed = True
            
        elif key == "5":  # Reset view
            self.plot_3d.rotation_x = 0.3
            self.plot_3d.rotation_y = 0.8
            self.plot_3d.view_distance = 15.0
            redraw_needed = True
            
        return redraw_needed
    
    def _handle_trace_controls(self, key: str) -> bool:
        """Handle function tracing controls"""
        redraw_needed = False
        
        if key == "4":  # Move trace left
            self.graphics.trace_x -= self.trace_step
            redraw_needed = True
            
        elif key == "6":  # Move trace right
            self.graphics.trace_x += self.trace_step
            redraw_needed = True
            
        elif key == "+":  # Finer steps
            self.trace_step *= 0.5
            
        elif key == "-":  # Coarser steps
            self.trace_step *= 2.0
            
        elif key == "ENTER":
            # Jump to specific X value (would need input system)
            pass
            
        elif key == "F1":
            # Exit trace mode
            self.mode = "2D"
            self.trace_active = False
            self.graphics.show_trace = False
            redraw_needed = True
            
        # Ensure trace X is within bounds
        self.graphics.trace_x = max(self.graphics.bounds.x_min,
                                   min(self.graphics.bounds.x_max, self.graphics.trace_x))
        
        return redraw_needed
    
    def get_mode_status(self) -> str:
        """Get current interaction mode status"""
        if self.mode == "2D":
            return "2D Graph"
        elif self.mode == "3D":
            return "3D View"
        elif self.mode == "trace":
            trace_y = self.graphics.evaluate_function(self.graphics.trace_x)
            return f"Trace: X={self.graphics.trace_x:.3f}, Y={trace_y:.3f}"
        else:
            return "Graph Mode"

# Export classes
__all__ = ['Surface3D', 'Plot3DEngine', 'InteractiveGraphControls']