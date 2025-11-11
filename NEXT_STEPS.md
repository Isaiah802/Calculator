# Next Steps for AI Agent - November 11, 2025

**Last Updated:** November 11, 2025  
**Current Status:** Phase 1 Complete ✅ | Tasks 2.1-2.2 Complete ✅ | Ready for Task 2.3

---

## 🎯 IMMEDIATE TASK: Task 2.3 - Settings Management Module

### Overview
Implement the settings management module to persist user preferences and calculator settings to SD card.

### Current State ✅
- **Phase 1 Complete:** All refactoring tasks (1.1-1.5) are done
- **Task 2.1 Complete:** Games module (Snake and Pong) implemented and working ✅
- **Task 2.2 Complete:** Scientific calculator module with 30+ functions implemented ✅
- **All code compiles successfully:** No syntax errors
- **Mode switching works:** `AppState.switch_mode()` is functional
- **Calculation behavior correct:** Expressions evaluate only on "=" press
- **No ImportErrors:** All problematic imports have been handled with try/except

### What's Already Available
1. **File System Manager:** `storage/filesystem.py` (206 lines) - Working
   - SD card read/write operations
   - File creation and deletion
   - Transaction support
   
2. **Configuration System:** `Config` class in `calculator.py` - Working
   - Centralized configuration management
   - Hardware, System, and UI settings
   
3. **Enhanced Math Engine:** `enhanced_math_engine.py` (992 lines) - Working
   - Advanced mathematical functions already available
   
4. **Scientific Calculator:** `scientific/functions.py` (575 lines) - Complete ✅
   - Angle mode management (degrees/radians)
   - 30+ scientific functions
   
5. **Modular Architecture:** All hardware and core modules extracted and working
   - `core/app_state.py` - State management ✅
   - `hardware/` - Display, Keypad, SPI, Power ✅
   - `mathengine/secure_engine.py` - Math evaluation ✅
   - `storage/filesystem.py` - SD card operations ✅
   - `ui/ui_manager.py` - UI rendering ✅
   - `games/` - Snake and Pong games ✅
   - `scientific/` - Scientific calculator functions ✅

---

## 📋 Task 2.3 Requirements

### Objective
Create a settings management module that stores and retrieves user preferences and calculator settings, with persistence to SD card.

### What to Implement

#### 1. Create `Broken_2.0/settings/settings_manager.py`
This file should contain:

```python
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
- UI theme/colors (if applicable)
"""

import json

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
        if not self.fs_manager:
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
        if not self.fs_manager:
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
```

#### 2. Update `Broken_2.0/settings/__init__.py`
```python
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
```

#### 3. Integration Points

**In calculator.py**, you may need to:
- Import the settings module
- Create an instance: `self.settings = create_settings_manager(self.filesystem)`
- Load settings on startup
- Use settings throughout the application (angle mode, display format, etc.)
- Optionally add a settings menu for user configuration

---

## ✅ Testing Checklist

Before marking Task 2.3 complete, ensure:

- [ ] `python3 -m py_compile Broken_2.0/settings/settings_manager.py` passes
- [ ] `python3 -m py_compile Broken_2.0/settings/__init__.py` passes
- [ ] Test settings creation with defaults
- [ ] Test loading/saving settings to SD card (or mock file system)
- [ ] Test individual setting getters and setters
- [ ] Test reset_to_defaults() functionality
- [ ] Test settings validation (e.g., brightness 0-100)
- [ ] Integration with calculator.py works (if implemented)
- [ ] No syntax errors in any file
- [ ] Update TASK_COMPLETION_SUMMARY.md to mark Task 2.3 as complete

---

## 📝 Documentation Updates Required

After completing Task 2.3, update these files:

1. **TASK_COMPLETION_SUMMARY.md**
   - Mark Task 2.3 as ✅ COMPLETE
   - Add completion date
   - Update metrics (lines added, files created)

2. **QUICK_STATUS.md** (if exists)
   - Update Phase 2 progress (from 40% to 60%)
   - Update file structure showing new settings files
   - Update next action to Task 2.4

3. **AI_AGENT_GUIDE.md**
   - Update "Current Project State" section
   - Update Phase 2 status
   - Update metrics table

4. **This file (NEXT_STEPS.md)**
   - Update to point to Task 2.4 as the next task
   - Archive Task 2.3 completion details

---

## 🚨 Important Reminders

### MicroPython Compatibility
- ✅ Do NOT import `typing` module (type hints work without import)
- ✅ Do NOT import `statistics` module (not available in MicroPython)
- ✅ Do NOT import `firmware` module (does not exist)
- ✅ Use try/except for optional features
- ✅ All code must work on Raspberry Pi Pico 2W hardware

### Code Quality
- Follow existing code patterns (see AI_AGENT_GUIDE.md)
- Add proper docstrings to all functions
- Use type hints (without importing typing)
- Add error handling with try/except
- Test on actual hardware if possible
- Memory efficiency matters (MicroPython has limited RAM)

### Testing Workflow
The calculator is tested **without PC connection** on Raspberry Pi Pico 2W:
- Deploy to Pico using Thonny or ampy
- Test standalone operation after deployment
- Serial debugging available but not always used
- Focus on standalone functionality

---

## 🔗 Related Documentation

For detailed information, see:
- **TASK_BREAKDOWN.md** - Complete task details and specifications
- **AI_AGENT_GUIDE.md** - Code patterns and best practices
- **WORKFLOW_GUIDE.md** - User requirements and testing approach
- **ARCHITECTURE.md** - System design and architecture
- **TASK_COMPLETION_SUMMARY.md** - Current completion status

---

## 📊 Current Project Metrics

| Metric | Value |
|--------|-------|
| Phase 1 Tasks Complete | 5/5 (100%) ✅ |
| Phase 2 Tasks Complete | 2/5 (40%) |
| Total Tasks Complete | 7/20 (35%) |
| Main calculator.py | 1,329 lines |
| Extracted modules | 1,414 lines |
| Games module | 602 lines ✅ |
| Scientific module | 575 lines ✅ |
| Compilation errors | 0 ✅ |

---

## 💪 You Can Do This!

Task 2.3 is a **Medium complexity** task with an estimated **200 lines** of code. You have:
- ✅ All dependencies complete (Task 1.2 FileSystemManager is done)
- ✅ File system manager already available
- ✅ Clear specifications above
- ✅ Example code structure provided
- ✅ Clean codebase with no errors
- ✅ Good documentation to reference

**Estimated time:** 1-2 hours for a focused AI agent

**Next task after this:** Task 2.4 - SD Card Module (easier, LOW complexity) or Task 2.5 - Graphing Module (medium, HIGH priority)

---

## 🎯 Summary

**What to do:**
1. Create `settings/settings_manager.py` with SettingsManager class
2. Update `settings/__init__.py` with exports
3. Integrate with calculator.py (optional but recommended)
4. Test all settings functions
5. Update documentation (TASK_COMPLETION_SUMMARY.md, AI_AGENT_GUIDE.md, etc.)

**What NOT to do:**
- Don't import typing, statistics, or firmware modules
- Don't break existing functionality
- Don't add unnecessary complexity
- Don't skip testing

**Success looks like:**
- All Python files compile without errors
- Settings can be saved and loaded from SD card (or mock file system)
- Default settings work properly
- Setting validation works (e.g., brightness 0-100)
- Integration with main calculator is clean (if implemented)
- Documentation is updated
- Ready for Task 2.4 or 2.5

---

**Good luck! The codebase is in excellent shape and ready for your contributions. 🚀**
