#!/usr/bin/env python3
"""
Settings Management Module

This module provides settings management functionality including:
- User preference storage and retrieval
- Calculator settings persistence
- SD card integration for settings file
- Default settings management
- Settings validation

Settings managed:
- Angle mode (degrees/radians)
- Display format (decimal places, scientific notation)
- Brightness level
- Auto-sleep timeout
- Calculation history size
"""

import json
# typing module not available in MicroPython - type hints work without import


class SettingsManager:
    """Manage calculator settings with SD card persistence."""
    
    DEFAULT_SETTINGS = {
        "angle_mode": "deg",  # "deg" or "rad"
        "decimal_places": 4,
        "scientific_notation": False,
        "brightness": 80,  # 0-100
        "auto_sleep_minutes": 5,
        "history_size": 50,
        "theme": "default"
    }
    
    def __init__(self, filesystem_manager=None, settings_file="settings.json"):
        """
        Initialize settings manager.
        
        Args:
            filesystem_manager: FileSystemManager instance for SD card access
            settings_file: Name of settings file on SD card
        """
        self.fs_manager = filesystem_manager
        self.settings_file = settings_file
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from SD card, use defaults if file doesn't exist."""
        if not self.fs_manager or not self.fs_manager.mounted:
            return
        
        try:
            content = self.fs_manager.read_file(self.settings_file)
            if content:
                loaded = json.loads(content)
                # Merge with defaults to handle new settings
                for key in self.DEFAULT_SETTINGS:
                    if key in loaded:
                        self.settings[key] = loaded[key]
        except Exception as e:
            print(f"[WARNING] Could not load settings: {e}")
            # Keep default settings
    
    def save_settings(self):
        """Save current settings to SD card."""
        if not self.fs_manager or not self.fs_manager.mounted:
            return False
        
        try:
            content = json.dumps(self.settings)
            return self.fs_manager.write_file(self.settings_file, content)
        except Exception as e:
            print(f"[ERROR] Could not save settings: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and save to SD card."""
        self.settings[key] = value
        return self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save_settings()
    
    # Convenience methods for common settings
    def get_angle_mode(self):
        """Get current angle mode."""
        return self.get("angle_mode", "deg")
    
    def set_angle_mode(self, mode):
        """Set angle mode (deg or rad)."""
        if mode not in ["deg", "rad"]:
            raise ValueError("Angle mode must be 'deg' or 'rad'")
        return self.set("angle_mode", mode)
    
    def toggle_angle_mode(self):
        """Toggle between degrees and radians."""
        current = self.get_angle_mode()
        new_mode = "rad" if current == "deg" else "deg"
        return self.set_angle_mode(new_mode)
    
    def get_decimal_places(self):
        """Get number of decimal places for display."""
        return self.get("decimal_places", 4)
    
    def set_decimal_places(self, places):
        """Set number of decimal places (0-10)."""
        places = max(0, min(10, int(places)))
        return self.set("decimal_places", places)
    
    def get_brightness(self):
        """Get brightness level (0-100)."""
        return self.get("brightness", 80)
    
    def set_brightness(self, level):
        """Set brightness level (0-100)."""
        level = max(0, min(100, int(level)))
        return self.set("brightness", level)
    
    def get_auto_sleep_minutes(self):
        """Get auto-sleep timeout in minutes."""
        return self.get("auto_sleep_minutes", 5)
    
    def set_auto_sleep_minutes(self, minutes):
        """Set auto-sleep timeout (0-60 minutes, 0=disabled)."""
        minutes = max(0, min(60, int(minutes)))
        return self.set("auto_sleep_minutes", minutes)
    
    def get_history_size(self):
        """Get maximum calculation history size."""
        return self.get("history_size", 50)
    
    def set_history_size(self, size):
        """Set maximum calculation history size (10-200)."""
        size = max(10, min(200, int(size)))
        return self.set("history_size", size)
    
    def get_scientific_notation(self):
        """Get whether scientific notation is enabled."""
        return self.get("scientific_notation", False)
    
    def set_scientific_notation(self, enabled):
        """Set whether to use scientific notation."""
        return self.set("scientific_notation", bool(enabled))
    
    def toggle_scientific_notation(self):
        """Toggle scientific notation on/off."""
        current = self.get_scientific_notation()
        return self.set_scientific_notation(not current)


def create_settings_manager(filesystem_manager=None, settings_file="settings.json"):
    """
    Create and return a SettingsManager instance.
    
    Args:
        filesystem_manager: FileSystemManager instance
        settings_file: Settings file name
        
    Returns:
        SettingsManager instance
    """
    return SettingsManager(filesystem_manager, settings_file)
