# Task 1.1: Extract Hardware Abstraction Layer

## Task Information
- **ID:** 1.1
- **Category:** Code Refactoring & Architecture
- **Priority:** High
- **Complexity:** Medium
- **Estimated Lines:** 600
- **Estimated Time:** 4-6 hours

## Context
- **Project:** Peanut 3000 Calculator
- **Repository:** Isaiah802/Calculator
- **Working Directory:** `Broken_2.0/`
- **Main File:** `calculator.py` (2,395 lines)

## Objective
Extract hardware management classes from the monolithic `calculator.py` file into a dedicated hardware abstraction layer. This will improve code organization, maintainability, and enable better hardware testing.

## Current State
All hardware management is currently embedded in `calculator.py`:
- **SPIManager** (lines 152-197): Thread-safe SPI bus management
- **DisplayManager** (lines 199-376): ILI9341 display control with framebuffer
- **KeypadManager** (lines 377-472): 6x4 matrix keypad input handling
- **PowerManager** (lines 473-551): Battery monitoring and backlight control

These classes are tightly coupled within the main file but have clear boundaries.

## Requirements

### 1. Create Hardware Module Structure
```
Broken_2.0/
├── hardware/
│   ├── __init__.py
│   ├── spi_manager.py
│   ├── display.py
│   ├── keypad.py
│   └── power.py
```

### 2. Extract Classes

#### SPIManager → `hardware/spi_manager.py`
- Lines 152-197 from calculator.py
- Manages SPI bus switching between display and SD card
- Methods: `switch_to_display()`, `switch_to_sd()`, `get_spi()`
- Dependencies: Config, Logger, HardwareError

#### DisplayManager → `hardware/display.py`
- Lines 199-376 from calculator.py
- ILI9341 display initialization and control
- Framebuffer management with fallback for low memory
- Methods: `clear()`, `show()`, `fill()`, `text()`, `rect()`, `pixel()`, etc.
- Dependencies: Config, Logger, HardwareError, SPIManager

#### KeypadManager → `hardware/keypad.py`
- Lines 377-472 from calculator.py
- 6x4 matrix keypad scanning
- Debouncing and long-press detection
- Methods: `scan()`, `get_key()`, `wait_for_key()`
- Dependencies: Config, Logger

#### PowerManager → `hardware/power.py`
- Lines 473-551 from calculator.py
- Battery voltage monitoring
- Backlight PWM control
- Methods: `read_battery_voltage()`, `get_battery_percentage()`, `set_brightness()`
- Dependencies: Config, Logger

### 3. Update Main File
- Remove extracted classes from `calculator.py`
- Add imports from new hardware module
- Ensure all references are updated
- Keep HardwareError exception in main file (or move to hardware/__init__.py)

## Deliverables

- [ ] `Broken_2.0/hardware/__init__.py` - Package initialization with exports
- [ ] `Broken_2.0/hardware/spi_manager.py` - SPIManager class
- [ ] `Broken_2.0/hardware/display.py` - DisplayManager class
- [ ] `Broken_2.0/hardware/keypad.py` - KeypadManager class
- [ ] `Broken_2.0/hardware/power.py` - PowerManager class
- [ ] Updated `Broken_2.0/calculator.py` - Removed classes, added imports
- [ ] All functionality working as before

## Dependencies

### Required Before This Task
- None (foundation task)

### Blocks These Tasks
- Task 1.4: Extract UI Manager (needs DisplayManager)
- Task 2.1: Implement Games (needs DisplayManager, KeypadManager)
- Task 2.5: Complete Graphing Module (needs DisplayManager)
- Task 5.1: Enhance Hardware Validation (needs hardware layer)

## Implementation Steps

### Step 1: Create Directory Structure
```bash
mkdir -p Broken_2.0/hardware
touch Broken_2.0/hardware/__init__.py
```

### Step 2: Extract SPIManager
1. Create `hardware/spi_manager.py`
2. Copy lines 152-197 from calculator.py
3. Add proper imports (Config, Logger, HardwareError)
4. Add module docstring
5. Test syntax: `python3 -m py_compile Broken_2.0/hardware/spi_manager.py`

### Step 3: Extract DisplayManager
1. Create `hardware/display.py`
2. Copy lines 199-376 from calculator.py
3. Import SPIManager from hardware module
4. Add proper imports
5. Test syntax

### Step 4: Extract KeypadManager
1. Create `hardware/keypad.py`
2. Copy lines 377-472 from calculator.py
3. Add proper imports
4. Test syntax

### Step 5: Extract PowerManager
1. Create `hardware/power.py`
2. Copy lines 473-551 from calculator.py
3. Add proper imports
4. Test syntax

### Step 6: Create Package __init__.py
```python
"""
Hardware Abstraction Layer

Provides interfaces for:
- SPI bus management
- Display control (ILI9341)
- Keypad input (6x4 matrix)
- Power management (battery, backlight)
"""

from .spi_manager import SPIManager
from .display import DisplayManager
from .keypad import KeypadManager
from .power import PowerManager

__all__ = [
    'SPIManager',
    'DisplayManager',
    'KeypadManager',
    'PowerManager',
]
```

### Step 7: Update calculator.py
1. Remove extracted class definitions (lines 152-551)
2. Add import: `from hardware import SPIManager, DisplayManager, KeypadManager, PowerManager`
3. Verify all references still work
4. Test syntax: `python3 -m py_compile Broken_2.0/calculator.py`

### Step 8: Handle HardwareError Exception
Option A: Keep in calculator.py (simple)
Option B: Move to hardware/__init__.py (cleaner)

If Option B:
```python
# In hardware/__init__.py
class HardwareError(Exception):
    """Hardware-related errors"""
    pass

# In calculator.py
from hardware import HardwareError
```

## Testing Criteria

### Syntax Tests
- [ ] `python3 -m py_compile Broken_2.0/hardware/spi_manager.py` - No errors
- [ ] `python3 -m py_compile Broken_2.0/hardware/display.py` - No errors
- [ ] `python3 -m py_compile Broken_2.0/hardware/keypad.py` - No errors
- [ ] `python3 -m py_compile Broken_2.0/hardware/power.py` - No errors
- [ ] `python3 -m py_compile Broken_2.0/calculator.py` - No errors

### Import Tests
```python
# Test imports work
from hardware import SPIManager, DisplayManager, KeypadManager, PowerManager
from hardware import HardwareError  # if moved

# Test instantiation
spi = SPIManager()
display = DisplayManager(spi)
keypad = KeypadManager()
power = PowerManager()
```

### Integration Test
- [ ] CalculatorApp still initializes
- [ ] Display operations work
- [ ] Keypad scanning works
- [ ] Power monitoring works
- [ ] No broken imports
- [ ] No circular dependencies

## Files to Modify

### Create New Files
1. `Broken_2.0/hardware/__init__.py` - Package init with exports
2. `Broken_2.0/hardware/spi_manager.py` - SPIManager class
3. `Broken_2.0/hardware/display.py` - DisplayManager class
4. `Broken_2.0/hardware/keypad.py` - KeypadManager class
5. `Broken_2.0/hardware/power.py` - PowerManager class

### Modify Existing Files
1. `Broken_2.0/calculator.py` - Remove classes, add imports

## Success Criteria

✅ Task is complete when:
1. All hardware classes extracted to separate files
2. All files compile without syntax errors
3. Import structure is clean and logical
4. calculator.py is ~400 lines shorter
5. No functionality is broken
6. Code follows existing patterns
7. Documentation is updated

## Code Patterns to Follow

### Module Header
```python
#!/usr/bin/env python3
"""
[Class Name] - [Brief Description]

Part of the Hardware Abstraction Layer for Peanut 3000 Calculator.
[Detailed description]
"""

from machine import Pin, SPI, PWM, ADC
from typing import Optional
import time

# Import shared dependencies
# Note: Adjust these based on where Config/Logger end up
from calculator import Config, Logger, HardwareError
# OR
from core.config import Config, config
from core.logger import Logger, logger
from hardware import HardwareError
```

### Error Handling
```python
try:
    # Hardware operation
    self.pin.value(1)
    logger.debug("Operation successful")
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise HardwareError(f"Failed: {e}")
```

## Common Pitfalls to Avoid

1. **Circular Imports:** Don't import calculator.py from hardware modules
2. **Missing Dependencies:** Ensure Config, Logger accessible
3. **Copy-Paste Errors:** Verify all code copied correctly
4. **Indentation:** Maintain consistent 4-space indentation
5. **Line Numbers:** Line numbers in this task are approximate, verify actual code
6. **Global State:** Keep global logger, config usage consistent

## Notes

- This is a foundation task - get it right!
- Focus on clean extraction, not new features
- Maintain backward compatibility
- Document any deviations from plan
- Test thoroughly before marking complete
- Line numbers may shift slightly, use class names to locate code

## Verification Commands

```bash
# Check line counts (should decrease)
wc -l Broken_2.0/calculator.py

# List new files
ls -la Broken_2.0/hardware/

# Test all syntax
for f in Broken_2.0/hardware/*.py; do python3 -m py_compile "$f" && echo "✓ $f"; done

# Check imports
grep "from hardware import" Broken_2.0/calculator.py
```

## Related Documentation
- See ARCHITECTURE.md for overall system design
- See AI_AGENT_GUIDE.md for code patterns
- See TASK_BREAKDOWN.md for context

---

**Ready to start? Follow the implementation steps carefully and test frequently!**
