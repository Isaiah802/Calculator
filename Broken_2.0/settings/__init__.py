"""
Settings Management Module

This module provides settings management functionality including:
- User preference storage and retrieval
- Calculator settings persistence to SD card
- Default settings management
- Settings validation
"""

from .settings_manager import SettingsManager, create_settings_manager

__all__ = ['SettingsManager', 'create_settings_manager']
