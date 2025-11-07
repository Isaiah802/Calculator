# AI Agent Quick Reference Guide

## Quick Start Checklist

When assigned a task:
- [ ] Read the task description in TASK_BREAKDOWN.md
- [ ] Review ARCHITECTURE.md for context
- [ ] Check dependency tasks are complete
- [ ] Understand current code structure
- [ ] Follow coding patterns in existing code
- [ ] Test incrementally
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

## Quick Reference: Current Classes

### In calculator.py (2,395 lines)

| Class | Lines | Purpose | Extract To |
|-------|-------|---------|------------|
| Config | 48-109 | Configuration | core/config.py |
| Logger | 122-147 | Logging | core/logger.py |
| SPIManager | 152-197 | SPI bus | hardware/spi.py |
| DisplayManager | 199-376 | Display | hardware/display.py |
| KeypadManager | 377-472 | Keypad | hardware/keypad.py |
| PowerManager | 473-551 | Power | hardware/power.py |
| FileSystemManager | 552-731 | Files | storage/filesystem.py |
| SecureMathEngine | 732-1081 | Math eval | math/secure_engine.py |
| UIManager | 1082-1227 | UI render | ui/ui_manager.py |
| AppState | 1228-1287 | State | core/app_state.py |
| CalculatorApp | 1288-end | Main app | Keep in calculator.py |

### Other Files

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| enhanced_math_engine.py | 992 | Advanced math | Integrate |
| graphics_engine.py | 461 | 2D graphics | Reorganize |
| statistical_plots.py | 389 | Stat plots | Reorganize |
| interactive_3d.py | 456 | 3D graphics | Reorganize |
| usb_interface.py | 661 | USB | Integrate |
| performance_optimizer.py | 356 | Performance | Integrate |

---

## Contact

For questions or clarifications:
- Review TASK_BREAKDOWN.md for task details
- Check ARCHITECTURE.md for system design
- Examine existing code for patterns
- Ask project maintainer if stuck

---

**Remember:** The goal is clean, maintainable, well-tested code that follows existing patterns!
