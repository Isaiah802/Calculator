# Development Workflow & User Requirements Guide

**Last Updated:** November 11, 2025  
**Purpose:** Document user workflow, testing approach, and specific requirements

---

## 🔄 User Development Workflow

### Testing Environment
The Peanut 3000 calculator is tested on **actual Raspberry Pi Pico 2W hardware** without continuous PC connection:

1. **Development Phase**
   - Code changes made in repository
   - Syntax checking with `python3 -m py_compile`
   - Review changes before deployment

2. **Deployment Phase**
   - Upload files to Pico using Thonny IDE or ampy
   - Disconnect from PC (if desired)
   - Calculator runs standalone

3. **Testing Phase**
   - **Periodic testing WITHOUT PC connection**
   - Test on actual hardware with real buttons and display
   - Re-connect only when issues need debugging

### Why This Matters for AI Agents
- Code must work standalone on MicroPython
- Cannot rely on Python standard library modules not in MicroPython
- Must handle hardware limitations (memory, processing power)
- User feedback comes from actual hardware testing, not simulated environments

---

## 🎯 Critical User Requirements

### 1. Calculation Evaluation Behavior
**Requirement:** Expressions should evaluate ONLY when "=" button is pressed

**Implementation:**
- Located in: `calculator.py` → `handle_calculator_mode()`
- Key behavior: Build expression string, evaluate on "=" key
- Do NOT evaluate on-the-fly as user types

**Why:** User explicitly requested this behavior change

### 2. Mode Selection Functionality
**Requirement:** Mode switching must work properly

**Implementation:**
- Located in: `core/app_state.py` → `AppState.switch_mode()`
- Modes: Calculator, Menu, Graph, File Browser, Games, Statistics, etc.
- Must handle state transitions cleanly

**Why:** User reported issues with mode selection not working

### 3. Button Assignments
**Requirement:** Proper positioning of "=" and "ON" buttons

**Implementation:**
- Located in: `hardware/keypad.py` → `KeypadManager`
- Button mapping for 6x4 matrix keypad
- Specific attention to "=" and "ON" button locations

**Why:** User requested repositioning of these critical buttons

### 4. Error Handling
**Requirement:** Handle missing MicroPython modules gracefully

**Common Issues:**
- `ImportError: no module named 'typing'` - Use type hints without import
- `ImportError: no module named 'statistics'` - Use enhanced_math_engine
- `ImportError: no module named 'firmware'` - No MicroPython equivalent

**Pattern:**
```python
try:
    from optional_module import Feature
    FEATURE_AVAILABLE = True
except ImportError:
    FEATURE_AVAILABLE = False
    print("[WARNING] Feature not available")
```

**Why:** User encountered multiple ImportError issues during testing

---

## 📝 User Feedback History

### Branch Management Issues
**Issue:** User had multiple branches with merge problems  
**Context:** Working on improvements across different branches  
**Resolution:** Code consolidated in main working branch

### File Management
**Feedback:** "Please remember to delete and or replace the old files."  
**Action Taken:** Removed 1,278 lines of unused/broken code  
**Status:** ✅ Complete (November 2025)

### Calculator Functionality
**Feedback:** "I need you to change the fundamental function of the calculations."  
**Specific Request:** Evaluate only on "=" button press  
**Status:** ✅ Implemented in calculator.py

### Mode Selection
**Feedback:** "I need you to get the mode selection to work."  
**Action Required:** Ensure AppState.switch_mode() works correctly  
**Status:** ✅ Implemented in core/app_state.py

### Testing Approach Change
**Feedback:** "From now on, I will not have the calc connected to the pc."  
**Impact:** All testing done standalone on hardware  
**Consideration:** Code must be fully functional without debugging connection

---

## 🧪 Testing Checklist for AI Agents

When making code changes, verify:

### Syntax & Compilation
- [ ] `python3 -m py_compile [file.py]` passes for all changed files
- [ ] No syntax errors or indentation issues
- [ ] All imports resolve correctly

### MicroPython Compatibility
- [ ] No use of unsupported standard library modules
- [ ] Type hints used without importing `typing`
- [ ] Graceful fallback for optional imports
- [ ] Memory-efficient code (MicroPython has limited RAM)

### Hardware Integration
- [ ] Display operations use DisplayManager properly
- [ ] Keypad input handled through KeypadManager
- [ ] SPI operations managed through SPIManager
- [ ] Power management respects battery state

### User Requirements
- [ ] Calculator evaluates on "=" press only
- [ ] Mode switching works via AppState
- [ ] Button assignments correct
- [ ] Error messages user-friendly

### Code Quality
- [ ] Follows existing code patterns
- [ ] Proper error handling with try/except
- [ ] Logging for important events
- [ ] Documentation/comments for complex logic

---

## 🚀 Deployment Notes

### Files to Deploy to Pico
**Core Files:**
- `calculator.py` - Main application
- `hardware_config.py` - Hardware configuration
- `enhanced_math_engine.py` - Advanced math
- All module directories: `core/`, `hardware/`, `mathengine/`, `storage/`, `ui/`

**Optional Files (if implemented):**
- `games/` - Snake and Pong games
- `scientific/` - Scientific functions
- `settings/` - Settings manager
- `graphing/` - Graph manager
- Graphics engines (if using graphing)
- USB interface (if using PC connectivity)

**Not Needed on Pico:**
- Documentation files (*.md)
- Git files (.git, .gitignore)
- Python cache (__pycache__)
- Development scripts

### Using Thonny
1. Connect Pico to PC via USB
2. Open Thonny IDE
3. Select "Raspberry Pi Pico" interpreter
4. Upload files to Pico file system
5. Run `calculator.py` to test
6. Disconnect PC (optional)

### Using ampy
```bash
# Upload main file
ampy --port /dev/ttyUSB0 put Broken_2.0/calculator.py

# Upload module directory
ampy --port /dev/ttyUSB0 put Broken_2.0/hardware hardware

# List files on Pico
ampy --port /dev/ttyUSB0 ls
```

---

## 🎮 Current Feature Status

### Working Features ✅
- Basic calculator operations
- Scientific functions (via EnhancedMathEngine)
- Complex numbers
- Matrix operations
- Statistics mode
- Unit conversions
- Graph mode (basic)
- File system (SD card)
- Power management
- Display system
- Keypad input

### Partially Working 🔶
- Games (directory exists, modules not implemented)
- USB interface (file exists, not fully integrated)
- Advanced graphing (engines exist, need integration)

### Not Implemented ❌
- Scientific calculator module (empty)
- Settings management (empty)
- SD card module enhancements (empty)
- Performance optimizer (not integrated)

---

## 📚 Important Files for AI Agents

### Must Read Before Starting Work
1. **TASK_COMPLETION_SUMMARY.md** - What's done vs what's pending
2. **TASK_BREAKDOWN.md** - All 20 tasks with details
3. **AI_AGENT_GUIDE.md** - Code patterns and quick reference
4. **WORKFLOW_GUIDE.md** - This file (user requirements)

### For Understanding Architecture
1. **ARCHITECTURE.md** - System design and structure
2. **CODE_REVIEW_1X_TASKS.md** - Review of refactoring work
3. **calculator.py** - Main application code

### For Specific Tasks
1. **tasks/README.md** - Task index and status
2. **tasks/TASK_X.X_*.md** - Individual task specifications

---

## 💡 Tips for Success

### Do's ✅
- Test syntax with py_compile before committing
- Follow existing code patterns in the repository
- Use try/except for optional features
- Add logging for debugging
- Document complex logic
- Consider memory constraints
- Use hardware abstraction layers

### Don'ts ❌
- Import modules not in MicroPython
- Ignore hardware limitations
- Remove working code unnecessarily
- Create dependencies on PC connection
- Use inefficient algorithms (limited CPU)
- Hardcode values (use Config class)
- Break existing functionality

---

## 🔍 Troubleshooting Common Issues

### ImportError: no module named 'X'
**Cause:** Module not available in MicroPython  
**Solution:** Use try/except with fallback or find MicroPython alternative

### MemoryError
**Cause:** MicroPython has limited RAM  
**Solution:** Use `gc.collect()`, reduce buffer sizes, optimize algorithms

### IndentationError
**Cause:** Inconsistent spacing  
**Solution:** Use 4 spaces consistently, check for tabs vs spaces

### Hardware not responding
**Cause:** Pin configuration or SPI issues  
**Solution:** Verify pin assignments in Config, check SPI mode switching

### Mode switching not working
**Cause:** State management issue  
**Solution:** Check AppState.switch_mode(), verify mode string matches

---

## 📞 When to Ask for User Clarification

Ask the user when:
- Requirements are ambiguous or conflicting
- Multiple implementation approaches exist
- Breaking changes might affect existing functionality
- User preference needed (UI/UX decisions)
- Hardware behavior unclear
- Testing results unexpected

Do NOT ask when:
- Standard coding decisions can be inferred from existing code
- Documentation provides clear guidance
- Pattern exists in codebase to follow
- Change is clearly beneficial and non-breaking

---

**Remember:** The user tests on actual hardware without constant PC connection. Code must be robust, efficient, and fully functional standalone.
