"""
Application State Management Module

This module contains the AppState class which manages the application's
state including calculator state, UI state, file browser state, graph state,
and system state.
"""

import time


class AppState:
    """Application state manager"""
    
    def __init__(self, config, logger, games_available=False, enhanced_math_available=False):
        """
        Initialize application state
        
        Args:
            config: Configuration object with System.SLEEP_TIMEOUT_MS attribute
            logger: Logger object for logging state changes
            games_available: Whether games module is available
            enhanced_math_available: Whether enhanced math module is available
        """
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
        
        # Store dependencies
        self._logger = logger
        
        # Menu items (Phase 4 enhanced)
        self.menu_items = ["Calculator", "File Browser", "Settings", "Graph"]
        if games_available:
            self.menu_items.append("Games")
        
        # Phase 4 menu items
        if enhanced_math_available:
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
            self._logger.info(f"Switched to {new_mode} mode")
            self.reset_activity()
