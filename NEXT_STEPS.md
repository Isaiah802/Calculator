# Next Steps for AI Agent - November 11, 2025

**Last Updated:** November 11, 2025  
**Current Status:** Phase 1 Complete ✅ | Task 2.1 Complete ✅ | Ready for Task 2.2

---

## 🎯 IMMEDIATE TASK: Task 2.2 - Scientific Calculator Module

### Overview
Implement the scientific calculator module with trigonometric, logarithmic, exponential, and statistical functions.

### Current State ✅
- **Phase 1 Complete:** All refactoring tasks (1.1-1.5) are done
- **Task 2.1 Complete:** Games module (Snake and Pong) implemented and working
- **All code compiles successfully:** No syntax errors
- **Mode switching works:** `AppState.switch_mode()` is functional
- **Calculation behavior correct:** Expressions evaluate only on "=" press
- **No ImportErrors:** All problematic imports have been handled with try/except

### What's Already Available
1. **Enhanced Math Engine:** `enhanced_math_engine.py` (992 lines) - Already imported and working
   - Contains advanced mathematical functions
   - Complex number support
   - Matrix operations
   - Statistical functions
   - Unit conversions

2. **Secure Math Engine:** `mathengine/secure_engine.py` (435 lines) - Working
   - Input sanitization
   - Timeout protection
   - Integration with EnhancedMathEngine

3. **Modular Architecture:** All hardware and core modules extracted and working
   - `core/app_state.py` - State management ✅
   - `hardware/` - Display, Keypad, SPI, Power ✅
   - `mathengine/secure_engine.py` - Math evaluation ✅
   - `storage/filesystem.py` - SD card operations ✅
   - `ui/ui_manager.py` - UI rendering ✅
   - `games/` - Snake and Pong games ✅

---

## 📋 Task 2.2 Requirements

### Objective
Create a scientific calculator module that organizes and exposes scientific functions in a clean, easy-to-use interface.

### What to Implement

#### 1. Create `Broken_2.0/scientific/functions.py`
This file should contain:

```python
#!/usr/bin/env python3
"""
Scientific Calculator Functions Module

This module provides scientific calculator functions including:
- Trigonometric functions (sin, cos, tan, etc.)
- Inverse trigonometric functions (asin, acos, atan)
- Hyperbolic functions (sinh, cosh, tanh)
- Logarithmic and exponential functions
- Statistical functions
- Angle mode conversion (degrees/radians)

The module integrates with the EnhancedMathEngine for advanced calculations.
"""

import math
from typing import Optional, Tuple

class ScientificCalculator:
    """Scientific calculator functions with angle mode support."""
    
    def __init__(self, enhanced_math_engine=None):
        """
        Initialize scientific calculator.
        
        Args:
            enhanced_math_engine: Optional EnhancedMathEngine instance for advanced features
        """
        self.angle_mode = "deg"  # "deg" or "rad"
        self.enhanced_engine = enhanced_math_engine
    
    # Trigonometric functions
    def sin(self, x: float) -> float:
        """Calculate sine of x (respects angle mode)."""
        if self.angle_mode == "deg":
            x = math.radians(x)
        return math.sin(x)
    
    def cos(self, x: float) -> float:
        """Calculate cosine of x (respects angle mode)."""
        if self.angle_mode == "deg":
            x = math.radians(x)
        return math.cos(x)
    
    def tan(self, x: float) -> float:
        """Calculate tangent of x (respects angle mode)."""
        if self.angle_mode == "deg":
            x = math.radians(x)
        return math.tan(x)
    
    # Inverse trigonometric functions
    def asin(self, x: float) -> float:
        """Calculate arcsine of x (returns in current angle mode)."""
        result = math.asin(x)
        if self.angle_mode == "deg":
            result = math.degrees(result)
        return result
    
    def acos(self, x: float) -> float:
        """Calculate arccosine of x (returns in current angle mode)."""
        result = math.acos(x)
        if self.angle_mode == "deg":
            result = math.degrees(result)
        return result
    
    def atan(self, x: float) -> float:
        """Calculate arctangent of x (returns in current angle mode)."""
        result = math.atan(x)
        if self.angle_mode == "deg":
            result = math.degrees(result)
        return result
    
    # Hyperbolic functions
    def sinh(self, x: float) -> float:
        """Calculate hyperbolic sine of x."""
        return math.sinh(x)
    
    def cosh(self, x: float) -> float:
        """Calculate hyperbolic cosine of x."""
        return math.cosh(x)
    
    def tanh(self, x: float) -> float:
        """Calculate hyperbolic tangent of x."""
        return math.tanh(x)
    
    # Logarithmic and exponential functions
    def log(self, x: float, base: float = 10) -> float:
        """Calculate logarithm of x with specified base (default 10)."""
        return math.log(x, base)
    
    def ln(self, x: float) -> float:
        """Calculate natural logarithm of x."""
        return math.log(x)
    
    def exp(self, x: float) -> float:
        """Calculate e^x."""
        return math.exp(x)
    
    def pow(self, x: float, y: float) -> float:
        """Calculate x^y."""
        return math.pow(x, y)
    
    def sqrt(self, x: float) -> float:
        """Calculate square root of x."""
        return math.sqrt(x)
    
    # Angle mode management
    def set_angle_mode(self, mode: str):
        """
        Set angle mode for trigonometric functions.
        
        Args:
            mode: Either "deg" or "rad"
        """
        if mode in ["deg", "rad"]:
            self.angle_mode = mode
    
    def get_angle_mode(self) -> str:
        """Get current angle mode."""
        return self.angle_mode
    
    # Statistical functions (if enhanced engine available)
    def mean(self, data: list) -> float:
        """Calculate mean of data."""
        if self.enhanced_engine:
            return self.enhanced_engine.calculate_mean(data)
        return sum(data) / len(data)
    
    def median(self, data: list) -> float:
        """Calculate median of data."""
        if self.enhanced_engine:
            return self.enhanced_engine.calculate_median(data)
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid-1] + sorted_data[mid]) / 2
        return sorted_data[mid]
    
    def std_dev(self, data: list) -> float:
        """Calculate standard deviation of data."""
        if self.enhanced_engine:
            return self.enhanced_engine.calculate_std_dev(data)
        mean_val = self.mean(data)
        variance = sum((x - mean_val) ** 2 for x in data) / len(data)
        return math.sqrt(variance)


# Convenience functions for direct use
def create_scientific_calculator(enhanced_math_engine=None) -> ScientificCalculator:
    """Create and return a ScientificCalculator instance."""
    return ScientificCalculator(enhanced_math_engine)
```

#### 2. Update `Broken_2.0/scientific/__init__.py`
```python
"""
Scientific Calculator Module

This module provides scientific calculator functionality including:
- Trigonometric functions
- Logarithmic and exponential functions
- Statistical calculations
- Angle mode management (degrees/radians)
"""

from .functions import ScientificCalculator, create_scientific_calculator

__all__ = ['ScientificCalculator', 'create_scientific_calculator']
```

#### 3. Integration Points

**In calculator.py**, you may need to:
- Import the scientific calculator module
- Create an instance: `self.scientific_calc = create_scientific_calculator(self.math_engine.enhanced_engine)`
- Add scientific functions to the calculator mode or create a dedicated scientific mode
- Update the UI to show angle mode (DEG/RAD indicator)

---

## ✅ Testing Checklist

Before marking Task 2.2 complete, ensure:

- [ ] `python3 -m py_compile Broken_2.0/scientific/functions.py` passes
- [ ] `python3 -m py_compile Broken_2.0/scientific/__init__.py` passes
- [ ] Test basic trig functions: sin(30°) = 0.5, cos(0°) = 1, tan(45°) = 1
- [ ] Test angle mode switching: sin(π/2 rad) = 1
- [ ] Test logarithms: log(100) = 2, ln(e) = 1
- [ ] Test inverse trig: asin(0.5) = 30° (in deg mode)
- [ ] Test statistical functions if implemented
- [ ] Integration with calculator.py works
- [ ] No syntax errors in any file
- [ ] Update TASK_COMPLETION_SUMMARY.md to mark Task 2.2 as complete

---

## 📝 Documentation Updates Required

After completing Task 2.2, update these files:

1. **TASK_COMPLETION_SUMMARY.md**
   - Mark Task 2.2 as ✅ COMPLETE
   - Add completion date
   - Update metrics (lines added, files created)

2. **QUICK_STATUS.md**
   - Update Phase 2 progress (from 20% to 40%)
   - Update file structure showing new scientific files
   - Update next action to Task 2.3

3. **AI_AGENT_GUIDE.md**
   - Update "Current Project State" section
   - Update Phase 2 status

4. **This file (NEXT_STEPS.md)**
   - Update to point to Task 2.3 as the next task
   - Archive Task 2.2 completion details

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
| Phase 2 Tasks Complete | 1/5 (20%) |
| Total Tasks Complete | 6/20 (30%) |
| Main calculator.py | 1,291 lines |
| Extracted modules | 1,414 lines |
| Games module | 602 lines ✅ |
| Compilation errors | 0 ✅ |

---

## 💪 You Can Do This!

Task 2.2 is a **Medium complexity** task with an estimated **300 lines** of code. You have:
- ✅ All dependencies complete (Task 1.3 SecureMathEngine is done)
- ✅ Enhanced math engine already available
- ✅ Clear specifications above
- ✅ Example code structure provided
- ✅ Clean codebase with no errors
- ✅ Good documentation to reference

**Estimated time:** 2-3 hours for a focused AI agent

**Next task after this:** Task 2.3 - Settings Management (easier, LOW complexity)

---

## 🎯 Summary

**What to do:**
1. Create `scientific/functions.py` with ScientificCalculator class
2. Update `scientific/__init__.py` with exports
3. Integrate with calculator.py
4. Test all scientific functions
5. Update documentation (TASK_COMPLETION_SUMMARY.md, etc.)

**What NOT to do:**
- Don't import typing, statistics, or firmware modules
- Don't break existing functionality
- Don't add unnecessary complexity
- Don't skip testing

**Success looks like:**
- All Python files compile without errors
- Scientific functions work correctly
- Angle mode (deg/rad) switching works
- Integration with main calculator is clean
- Documentation is updated
- Ready for Task 2.3

---

**Good luck! The codebase is in excellent shape and ready for your contributions. 🚀**
