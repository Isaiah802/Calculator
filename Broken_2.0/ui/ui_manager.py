"""
UI Manager Module
=================
Modern user interface management system for the Peanut 3000 Calculator.

This module provides the UIManager class which handles all UI rendering
including status bars, menu items, input fields, and message overlays.

Author: Peanut 3000 Development Team
Version: 4.0.0
"""

import time


class UIManager:
    """Modern user interface management system"""
    
    def __init__(self, display, power):
        """
        Initialize UIManager with display and power managers.
        
        Args:
            display: DisplayManager instance for rendering
            power: PowerManager instance for power-related UI elements
        """
        self.display = display
        self.power = power
        self.blink_state = False
        self.last_blink = 0
        
    def draw_status_bar(self, shift_mode: bool, battery_voltage: float, battery_percent: int):
        """Draw modern status bar with system information"""
        # Import config here to avoid circular dependencies
        from calculator import config, constrain
        
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
        # Import config here to avoid circular dependencies
        from calculator import config
        
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
        # Import config here to avoid circular dependencies
        from calculator import config
        
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
        # Import config here to avoid circular dependencies
        from calculator import config
        
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
