# AI Agent Quick Reference Guide

**Last Updated:** November 11, 2025  
**Project Status:** Phase 1 Complete (Tasks 1.1-1.5 ✅) - Phase 2 In Progress (Task 2.1 ✅)

---

## 🚨 Important Project Context

### Current Project State
- **Phase 1 (Refactoring) COMPLETE** - All 5 tasks done (1.1-1.5)
- **Phase 2 (Features) IN PROGRESS** - Task 2.1 Games Module complete ✅
- **Calculator.py reduced:** 2,395 → 1,291 lines (46% reduction)
- **Modules created:** core, hardware, mathengine, storage, ui, games
- **Next task:** Task 2.2 Scientific Calculator Module

### Testing & Deployment Workflow
⚠️ **CRITICAL**: This calculator runs on **Raspberry Pi Pico 2W hardware**
- Testing is done **WITHOUT PC CONNECTION** on actual hardware
- Deploy to Pico using Thonny or ampy
- Serial debugging available but not always used
- Focus on standalone operation after deployment

### Key User Requirements
1. **Calculation Behavior**: Expressions evaluate ONLY when "=" is pressed
2. **Mode Selection**: AppState.switch_mode() must work correctly
3. **Button Assignments**: Special attention to "=" and "ON" button positions
4. **MicroPython Compatibility**: Avoid modules not available in MicroPython (typing, statistics, firmware)

---

## Quick Start Checklist

When assigned a task:
- [ ] Read the task description in TASK_BREAKDOWN.md
- [ ] Review TASK_COMPLETION_SUMMARY.md for current status
- [ ] Review ARCHITECTURE.md for context
- [ ] Check dependency tasks are complete
- [ ] Understand current code structure
- [ ] Follow coding patterns in existing code
- [ ] Test incrementally (syntax check minimum)
- [ ] Consider MicroPython limitations
- [ ] Document changes
- [ ] Verify integration points

---

## Common Commands

### Syntax Check
```bash
python3 -m py_compile Broken_2.0/calculator.py
python3 -m py_compile Broken_2.0/[your_module].py
```

### Find Classes/Functions
```bash
# Find all classes
grep -n "^class " Broken_2.0/calculator.py

# Find all functions
grep -n "^def " Broken_2.0/calculator.py

# Search for specific term
grep -rn "DisplayManager" Broken_2.0/
```

### Line Counts
```bash
wc -l Broken_2.0/*.py
wc -l Broken_2.0/[module]/*.py
```

### Check Imports
```bash
# Find all imports
grep "^import\|^from" Broken_2.0/calculator.py
```

---

## 🔧 MicroPython Compatibility Guide

### Modules NOT Available in MicroPython
These standard Python modules will cause ImportError on Pico:
- ❌ `typing` - Type hints work without importing
- ❌ `statistics` - Implement manually or use enhanced_math_engine
- ❌ `firmware` - No equivalent in MicroPython
- ❌ `asyncio` (limited support) - Use uasyncio instead
- ❌ `threading` - Use `_thread` instead

### Modules Available in MicroPython
- ✅ `machine` - Pin, SPI, PWM, ADC (hardware access)
- ✅ `framebuf` - Frame buffer operations
- ✅ `time`, `utime` - Time and delays
- ✅ `math` - Basic math functions
- ✅ `os`, `uos` - File system operations
- ✅ `gc` - Garbage collection
- ✅ `json`, `ujson` - JSON encoding/decoding
- ✅ `sdcard` - SD card support (requires library)

### Using Type Hints in MicroPython
```python
# Type hints work WITHOUT importing typing module
def calculate(value: int, mode: str) -> float:
    """Type hints are parsed but not enforced."""
    return float(value)

# Optional, List, Dict can be used in comments instead
def process_data(items):  # type: List[int] -> None
    """Process list of items."""
    pass
```

### Handling Import Errors
```python
# Pattern: Try import with fallback
try:
    from enhanced_feature import AdvancedClass
    FEATURE_AVAILABLE = True
except ImportError:
    FEATURE_AVAILABLE = False
    print("[WARNING] Feature not available")

# Later in code
if FEATURE_AVAILABLE:
    obj = AdvancedClass()
else:
    # Fallback behavior
    pass
```

---

## Code Patterns to Follow

### Module Structure
```python
#!/usr/bin/env python3
"""
Module description.

This module provides [functionality].
"""

from machine import Pin, SPI
from typing import Optional, List, Dict
import time

# Constants
CONSTANT_NAME = 42

class ClassName:
    """Class description."""
    
    def __init__(self, param: Type):
        """Initialize with parameter."""
        self.param = param
    
    def method(self, arg: Type) -> ReturnType:
        """Method description."""
        # Implementation
        pass
```

### Hardware Access Pattern
```python
class HardwareComponent:
    """Component that accesses hardware."""
    
    def __init__(self):
        """Initialize hardware pins/interfaces."""
        try:
            # Initialize hardware
            self.pin = Pin(10, Pin.OUT)
            logger.info("Component initialized")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise HardwareError(f"Init failed: {e}")
    
    def operation(self):
        """Perform hardware operation."""
        try:
            # Do operation
            self.pin.value(1)
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            raise HardwareError(f"Op failed: {e}")
```

### Error Handling Pattern
```python
def risky_operation():
    """Operation that might fail."""
    try:
        # Risky code
        result = complex_operation()
        return result
    except SpecificError as e:
        logger.error(f"Specific error: {e}")
        # Handle or re-raise
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Generic handling
        return None
```

### Logging Pattern
```python
# At start of operation
logger.debug("Starting operation with param={param}")

# Info for important events
logger.info("Successfully completed initialization")

# Warnings for non-critical issues
logger.warning("Low memory: falling back to reduced mode")

# Errors for failures
logger.error(f"Operation failed: {error_message}")

# Operation tracking
logger.operation(f"Calculate: {expression}")
```

### Config Access Pattern
```python
# Use centralized config
baudrate = config.Hardware.SPI_BAUDRATE_DISPLAY
width = config.Hardware.DISPLAY_WIDTH
timeout = config.System.EVAL_TIMEOUT_MS
color = config.UI.BACKGROUND
```

---

## Common Extraction Patterns

### Extract Class to New Module

**Before (in calculator.py):**
```python
class MyClass:
    """My class."""
    def __init__(self):
        pass
```

**After:**

**1. Create new file:** `Broken_2.0/module/my_class.py`
```python
#!/usr/bin/env python3
"""My class module."""

from typing import Optional

class MyClass:
    """My class."""
    def __init__(self):
        pass
```

**2. Create __init__.py:** `Broken_2.0/module/__init__.py`
```python
"""Module package."""
from .my_class import MyClass

__all__ = ['MyClass']
```

**3. Update calculator.py:**
```python
# Change from:
class MyClass:
    ...

# To:
from module import MyClass
```

### Preserve Compatibility

When extracting, ensure backward compatibility:

```python
# In new module location
# Broken_2.0/hardware/display.py
class DisplayManager:
    """Display manager."""
    pass

# In old location (compatibility wrapper)
# Broken_2.0/hardware_config.py
"""Compatibility wrapper."""
from .hardware.display import DisplayManager

# This allows old imports to still work:
# from hardware_config import DisplayManager
```

---

## Testing Patterns

### Manual Testing
```python
if __name__ == '__main__':
    """Test code when run directly."""
    # Simple test
    obj = MyClass()
    result = obj.method()
    print(f"Result: {result}")
```

### Integration Testing
```python
# Test with dependencies
def test_integration():
    """Test component integration."""
    # Setup
    display = DisplayManager(spi_manager)
    keypad = KeypadManager()
    
    # Test
    keypad.scan()
    display.show()
    
    print("Integration test passed")
```

---

## File Organization Tips

### Directory Creation
```bash
mkdir -p Broken_2.0/new_module
touch Broken_2.0/new_module/__init__.py
touch Broken_2.0/new_module/component.py
```

### Import Organization
```python
# Standard library
import os
import time
import json

# Third-party (MicroPython)
from machine import Pin, SPI
import framebuf

# Local application
from config import Config
from hardware.display import DisplayManager
from math.secure_engine import SecureMathEngine
```

---

## Common Issues & Solutions

### Issue: Import Error
**Problem:** `ImportError: no module named 'module'`

**Solution:**
- Check `__init__.py` exists
- Verify path is correct
- Check for circular imports
- Ensure module is in Python path

### Issue: Memory Error
**Problem:** `MemoryError` when allocating buffer

**Solution:**
```python
try:
    gc.collect()  # Force garbage collection
    buffer = bytearray(size)
except MemoryError:
    # Fallback to smaller size
    buffer = bytearray(size // 2)
```

### Issue: Hardware Not Responding
**Problem:** Hardware component not working

**Solution:**
```python
# Add validation
def _initialize(self):
    try:
        # Init code
        self.pin = Pin(10)
        # Test pin
        self.pin.value(1)
        self.pin.value(0)
        logger.info("Hardware OK")
    except Exception as e:
        logger.error(f"Hardware failed: {e}")
        raise HardwareError(e)
```

### Issue: Indentation Error
**Problem:** `IndentationError: unexpected indent`

**Solution:**
- Use consistent spacing (4 spaces)
- Check for tabs vs spaces
- Verify proper nesting
- Use syntax checker

---

## Dependencies Between Components

### Safe Import Order

1. **Standard library & MicroPython**
   - No dependencies

2. **Configuration**
   - `config.py`, constants

3. **Utilities**
   - `logger.py`, helper functions

4. **Hardware Layer**
   - Depends on: config, logger
   - `hardware/`, `spi_manager.py`

5. **Storage Layer**
   - Depends on: hardware (SPI)
   - `storage/`, `filesystem.py`

6. **Math Layer**
   - Depends on: config, logger
   - `math/`, `secure_engine.py`

7. **UI Layer**
   - Depends on: hardware (display)
   - `ui/`, `ui_manager.py`

8. **Feature Modules**
   - Depends on: all above
   - `graphing/`, `games/`, etc.

9. **Main Application**
   - Depends on: all above
   - `calculator.py`

---

## Code Quality Checklist

Before submitting:
- [ ] Code compiles without errors
- [ ] No syntax errors
- [ ] Follows existing patterns
- [ ] Proper error handling
- [ ] Logging added where appropriate
- [ ] Type hints used
- [ ] Docstrings present
- [ ] No hardcoded values (use config)
- [ ] Memory efficient
- [ ] Integration tested
- [ ] Comments for complex logic
- [ ] Imports organized
- [ ] No unused imports
- [ ] Backward compatible (if applicable)

---

## Module Template

### Complete Module Template

```python
#!/usr/bin/env python3
"""
[Module Name]

This module provides [description of functionality].

Classes:
    ClassName: [Brief description]
    
Functions:
    function_name: [Brief description]

Example:
    >>> from module import ClassName
    >>> obj = ClassName()
    >>> obj.method()
"""

# Standard library imports
import time
import json
from typing import Optional, List, Dict, Tuple, Any

# MicroPython imports
from machine import Pin, SPI
import framebuf

# Local imports
from core.config import Config, config
from core.logger import Logger, logger
from hardware.exceptions import HardwareError

# Module constants
MODULE_VERSION = "1.0.0"
DEFAULT_TIMEOUT = 1000

# Type aliases
ConfigType = Dict[str, Any]


class ClassName:
    """
    Brief description of class.
    
    This class handles [detailed description].
    
    Attributes:
        attr1 (type): Description of attr1
        attr2 (type): Description of attr2
        
    Example:
        >>> obj = ClassName(param=value)
        >>> result = obj.method()
    """
    
    def __init__(self, param: str, optional: int = 42):
        """
        Initialize the class.
        
        Args:
            param: Description of param
            optional: Description of optional param
            
        Raises:
            ValueError: If param is invalid
            HardwareError: If hardware init fails
        """
        self.param = param
        self.optional = optional
        self._initialize()
        
    def _initialize(self):
        """Initialize internal state (private method)."""
        try:
            # Initialization code
            logger.info(f"{self.__class__.__name__} initialized")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
            
    def public_method(self, arg: int) -> str:
        """
        Public method description.
        
        Args:
            arg: Argument description
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: Description of when this is raised
        """
        try:
            # Method implementation
            result = self._private_method(arg)
            return result
        except Exception as e:
            logger.error(f"Method failed: {e}")
            raise
            
    def _private_method(self, arg: int) -> str:
        """Private helper method."""
        return f"Result: {arg}"
        
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(param={self.param})"


def module_function(param: str) -> bool:
    """
    Standalone module function.
    
    Args:
        param: Parameter description
        
    Returns:
        Success status
    """
    logger.debug(f"Function called with {param}")
    return True


# Module initialization
logger.debug(f"Module loaded: {__name__}")


if __name__ == '__main__':
    """Module test code."""
    print(f"Testing {__name__}")
    obj = ClassName("test")
    print(obj.public_method(123))
    print("Tests passed")
```

---

## 📊 Current Project Status (November 2025)

### ✅ COMPLETED - Phase 1: Refactoring (Tasks 1.1-1.5)

All classes have been extracted from the monolithic calculator.py:

| Module | Status | Files Created | Lines | Purpose |
|--------|--------|---------------|-------|---------|
| **core/** | ✅ DONE | app_state.py | 90 | Application state management |
| **hardware/** | ✅ DONE | spi_manager.py, display.py, keypad.py, power.py | 487 | Hardware abstraction layer |
| **mathengine/** | ✅ DONE | secure_engine.py | 435 | Secure math evaluation |
| **storage/** | ✅ DONE | filesystem.py | 206 | SD card file operations |
| **ui/** | ✅ DONE | ui_manager.py | 196 | UI rendering system |

**Result:** calculator.py reduced from 2,395 → 1,291 lines (46% reduction)

### 🔨 TODO - Phase 2: Feature Implementation (Tasks 2.1-2.5)

These modules exist but are empty (only README files):

| Module | Status | Priority | Estimated Lines | What's Needed |
|--------|--------|----------|----------------|---------------|
| **games/** | ✅ DONE | HIGH | 602 | Snake and Pong games implemented and working |
| **scientific/** | ❌ TODO | MEDIUM | 300 | Scientific calculator functions (trig, log, exp) |
| **settings/** | ❌ TODO | MEDIUM | 200 | Settings manager with SD persistence |
| **sd/** | ❌ TODO | LOW | 150 | Enhanced SD card features (file browser, export) |
| **graphing/** | ❌ TODO | HIGH | 500 | Graph manager integrating existing graphics engines |

### 📦 Available But Not Integrated

These files exist and contain working code but need integration:

| File | Lines | Status | What's Needed |
|------|-------|--------|---------------|
| enhanced_math_engine.py | 992 | Available | Already imported and used ✅ |
| graphics_engine.py | 461 | Partial | Needs graphing module integration |
| statistical_plots.py | 389 | Partial | Needs graphing module integration |
| interactive_3d.py | 456 | Partial | Needs graphing module integration |
| usb_interface.py | 661 | Partial | Import exists but `USB_AVAILABLE = False` |
| performance_optimizer.py | 356 | Available | Not currently integrated |

---

## 🎯 Next Task Recommendations

### COMPLETED: Task 2.1 - Games Module ✅
**Status:** Complete - November 11, 2025

**What was done:**
1. Created `Broken_2.0/games/snake.py` (289 lines)
2. Created `Broken_2.0/games/pong.py` (313 lines)
3. Implemented `play_snake()` function with grid-based movement and collision detection
4. Implemented `play_pong()` function with AI opponent and ball physics
5. Updated `games/__init__.py` to export both functions
6. Fixed calculator.py import from "from snake import" to "from games import"
7. Implemented game selection menu in calculator
8. Result: `GAMES_AVAILABLE = True` ✅

### IMMEDIATE PRIORITY: Task 2.2 - Scientific Calculator Module
**Why:** Enhanced math engine available, need to organize scientific functions

**What to do:**
1. Create `Broken_2.0/scientific/functions.py`
2. Implement trigonometric functions (sin, cos, tan, etc.)
3. Implement logarithmic/exponential functions
4. Implement statistical functions
5. Update `scientific/__init__.py`
6. Integrate with calculator modes

**Dependencies:** Math engine (✅ complete)

### SECOND PRIORITY: Task 2.5 - Graphing Module
**Why:** Graphics engines already exist, just need integration

**What to do:**
1. Create `Broken_2.0/graphing/graph_manager.py`
2. Integrate graphics_engine.py, statistical_plots.py, interactive_3d.py
3. Create unified graphing API
4. Connect to calculator modes

**Dependencies:** Hardware layer (✅ complete), Math engine (✅ complete)

---

## Quick Reference: Current Classes

### ✅ In Extracted Modules (COMPLETE)

| Original Location | New Location | Status |
|-------------------|--------------|--------|
| Config | Still in calculator.py | ✅ Centralized config |
| Logger | Still in calculator.py | ✅ Centralized logging |
| SPIManager | hardware/spi_manager.py | ✅ Extracted |
| DisplayManager | hardware/display.py | ✅ Extracted |
| KeypadManager | hardware/keypad.py | ✅ Extracted |
| PowerManager | hardware/power.py | ✅ Extracted |
| FileSystemManager | storage/filesystem.py | ✅ Extracted |
| SecureMathEngine | mathengine/secure_engine.py | ✅ Extracted |
| UIManager | ui/ui_manager.py | ✅ Extracted |
| AppState | core/app_state.py | ✅ Extracted |
| Snake | games/snake.py | ✅ Implemented |
| Pong | games/pong.py | ✅ Implemented |
| CalculatorApp | calculator.py | ✅ Main app (kept) |

### 📚 Other Files (Integration Pending)

| File | Lines | Purpose | Integration Status |
|------|-------|---------|-------------------|
| games/snake.py | 289 | Snake game | ✅ Complete & integrated |
| games/pong.py | 313 | Pong vs AI | ✅ Complete & integrated |
| enhanced_math_engine.py | 992 | Advanced math | ✅ Imported & working |
| graphics_engine.py | 461 | 2D graphics | 🔶 Needs Task 2.5 |
| statistical_plots.py | 389 | Stat plots | 🔶 Needs Task 2.5 |
| interactive_3d.py | 456 | 3D graphics | 🔶 Needs Task 2.5 |
| usb_interface.py | 661 | USB | 🔶 Needs Task 3.1 |
| performance_optimizer.py | 356 | Performance | 🔶 Needs Task 3.4 |

---

## Contact

For questions or clarifications:
- Review **TASK_COMPLETION_SUMMARY.md** for what's done
- Review **TASK_BREAKDOWN.md** for task details
- Check **ARCHITECTURE.md** for system design
- Examine existing code for patterns
- Ask project maintainer if stuck

---

**Remember:** The goal is clean, maintainable, well-tested code that follows existing patterns!

**Current Focus:** Implement Phase 2 features (games, scientific, settings, SD, graphing modules)
