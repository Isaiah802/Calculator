# Calculator Project - Task Breakdown for AI Agents

**Last Updated:** November 11, 2025  
**Status:** Phase 1 Complete ✅ | Phase 2 Ready 🔨

## Project Overview
The Peanut 3000 is an advanced scientific calculator for Raspberry Pi Pico 2W with:
- Hardware: ILI9341 Display, 6x4 Keypad, SD Card, Battery monitoring
- Mathematical Features: Basic/scientific calculations, complex numbers, statistics, matrix operations
- Advanced Features: Graphing, USB connectivity, games, file management
- Modular architecture with hardware abstraction layers

**Current State (November 2025):**
- Main application: **1,291 lines** in `calculator.py` (reduced from 2,395)
- Extracted modules: 5 packages with 1,414 lines
- **Phase 1 COMPLETE:** All refactoring tasks (1.1-1.5) done ✅
- **Phase 2 READY:** Feature implementation tasks (2.1-2.5) can begin
- Additional modules: 5,354 total lines across 6 major files (graphics engines, USB, etc.)

---

## Task Categories

### ✅ Category 1: Code Refactoring & Architecture (COMPLETE)

#### Task 1.1: Extract Hardware Abstraction Layer ✅ COMPLETE
**Complexity:** Medium  
**Estimated Lines:** 600  
**Dependencies:** None  
**Status:** ✅ **COMPLETED** - November 2025

**Description:**  
Extract hardware management classes from `calculator.py` into separate module `hardware/hardware_layer.py`.

**Classes to Extract:**
- `SPIManager` (lines 152-197) ✅
- `DisplayManager` (lines 199-376) ✅
- `KeypadManager` (lines 377-472) ✅
- `PowerManager` (lines 473-551) ✅

**Deliverables:** ✅ ALL COMPLETE
- ✅ Created `Broken_2.0/hardware/` directory
- ✅ Created `hardware/spi_manager.py` (62 lines)
- ✅ Created `hardware/display.py` (195 lines)
- ✅ Created `hardware/keypad.py` (111 lines)
- ✅ Created `hardware/power.py` (97 lines)
- ✅ Created `hardware/__init__.py` with proper exports
- ✅ Updated imports in `calculator.py`
- ✅ All functionality working

**Testing:** ✅ PASSED
- ✅ Display initialization works
- ✅ Keypad input detection operational
- ✅ Power management functions validated
- ✅ Syntax check passes: `python3 -m py_compile`

---

#### Task 1.2: Extract File System Management ✅ COMPLETE
**Complexity:** Low  
**Estimated Lines:** 180  
**Dependencies:** None  
**Status:** ✅ **COMPLETED** - November 2025

**Description:**  
Move `FileSystemManager` class into dedicated module for SD card operations.

**Classes to Extract:**
- `FileSystemManager` (lines 552-731) ✅

**Deliverables:** ✅ ALL COMPLETE
- ✅ Created `Broken_2.0/storage/filesystem.py` (197 lines)
- ✅ Created `storage/__init__.py`
- ✅ Updated imports and dependencies
- ✅ SD card functionality preserved

**Testing:** ✅ PASSED
- ✅ SD card mounting operational
- ✅ File read/write operations working
- ✅ Calculations save feature functional
- ✅ Syntax check passes

---

#### Task 1.3: Extract Security & Math Engine ✅ COMPLETE
**Complexity:** High  
**Estimated Lines:** 350  
**Dependencies:** None  
**Status:** ✅ **COMPLETED** - November 2025

**Description:**  
Separate `SecureMathEngine` from main calculator file.

**Classes to Extract:**
- `SecureMathEngine` (lines 732-1081) ✅

**Deliverables:** ✅ ALL COMPLETE
- ✅ Created `Broken_2.0/mathengine/secure_engine.py` (417 lines)
- ✅ Created `mathengine/__init__.py`
- ✅ Integrated with existing `enhanced_math_engine.py`
- ✅ Updated calculator.py imports

**Testing:** ✅ PASSED
- ✅ Expression parsing and evaluation working
- ✅ Security features validated (input sanitization)
- ✅ Timeout functionality operational
- ✅ All math operations tested
- ✅ Syntax check passes

---

#### Task 1.4: Extract UI Management Layer ✅ COMPLETE
**Complexity:** Medium  
**Estimated Lines:** 146  
**Dependencies:** Task 1.1 (DisplayManager) ✅  
**Status:** ✅ **COMPLETED** - November 2025

**Description:**  
Move UI rendering logic into separate module.

**Classes to Extract:**
- `UIManager` (lines 1082-1227) ✅

**Deliverables:** ✅ ALL COMPLETE
- ✅ Created `Broken_2.0/ui/ui_manager.py` (178 lines)
- ✅ Created `ui/__init__.py`
- ✅ Proper integration with DisplayManager
- ✅ Updated calculator.py

**Testing:** ✅ PASSED
- ✅ Menu rendering working
- ✅ Text display functions operational
- ✅ Battery indicator display validated
- ✅ All UI elements tested
- ✅ Syntax check passes

---

#### Task 1.5: Extract Application State Management ✅ COMPLETE
**Complexity:** Low  
**Estimated Lines:** 60  
**Dependencies:** None  
**Status:** ✅ **COMPLETED** - November 2025

**Description:**  
Separate state management into dedicated module.

**Classes to Extract:**
- `AppState` (lines 1228-1287) ✅

**Deliverables:** ✅ ALL COMPLETE
- ✅ Created `Broken_2.0/core/app_state.py` (81 lines)
- ✅ Created `core/__init__.py`
- ✅ Updated state management imports

**Testing:** ✅ PASSED
- ✅ State transitions verified
- ✅ Mode switching operational
- ✅ Variable storage working
- ✅ Syntax check passes

**Summary of Phase 1 Completion:**
- ✅ All 5 refactoring tasks complete
- ✅ Calculator.py reduced from 2,395 → 1,291 lines (46% reduction)
- ✅ 1,414 lines extracted into 5 modular packages
- ✅ No compilation errors
- ✅ No security vulnerabilities
- ✅ Ready for Phase 2 feature implementation

---

### 🔨 Category 2: Feature Implementation (READY TO START)

#### Task 2.1: Implement Games Module ⏭️ NEXT PRIORITY
**Complexity:** Medium  
**Estimated Lines:** 400  
**Dependencies:** Task 1.1 (DisplayManager, KeypadManager) ✅ COMPLETE  
**Status:** ❌ **NOT STARTED** - Ready to implement

**Description:**  
Implement Snake and Pong games referenced in code but not yet created.

**Current State:**
- Games directory exists with README only
- Import attempted in calculator.py but modules don't exist
- Placeholder: `GAMES_AVAILABLE = False` when imports fail

**Deliverables:**
- Create `Broken_2.0/games/snake.py`
- Create `Broken_2.0/games/pong.py`
- Implement `play_snake()` function
- Implement `play_pong()` function
- Update `games/__init__.py`

**Testing:**
- Test game launching from calculator
- Verify keypad controls work
- Test game display rendering
- Check game exit functionality

---

#### Task 2.2: Complete Scientific Calculator Module
**Complexity:** Medium  
**Estimated Lines:** 300  
**Dependencies:** Task 1.3 (SecureMathEngine)  

**Description:**  
Implement missing scientific functions in the scientific module.

**Current State:**
- Directory exists with README only
- Need actual implementation

**Deliverables:**
- Create `Broken_2.0/scientific/functions.py`
- Implement trigonometric functions
- Implement logarithmic/exponential functions
- Implement statistical functions
- Update `scientific/__init__.py`

**Testing:**
- Test all scientific functions
- Verify accuracy of calculations
- Check angle mode (deg/rad)
- Test edge cases

---

#### Task 2.3: Implement Settings Management
**Complexity:** Low  
**Estimated Lines:** 200  
**Dependencies:** Task 1.2 (FileSystemManager)  

**Description:**  
Create settings management system for calculator preferences.

**Current State:**
- Directory exists with README only

**Deliverables:**
- Create `Broken_2.0/settings/settings_manager.py`
- Implement settings persistence (SD card)
- Add brightness control
- Add calculation mode settings
- Add display preferences
- Update `settings/__init__.py`

**Testing:**
- Test settings save/load
- Verify settings persistence
- Test all setting options

---

#### Task 2.4: Complete SD Card Module
**Complexity:** Low  
**Estimated Lines:** 150  
**Dependencies:** Task 1.2 (FileSystemManager)  

**Description:**  
Implement full SD card functionality.

**Current State:**
- Directory exists with README only
- Some functionality in FileSystemManager

**Deliverables:**
- Create `Broken_2.0/sd/sd_manager.py`
- Implement file browser
- Add calculation history export
- Implement graph export
- Update `sd/__init__.py`

**Testing:**
- Test file operations
- Verify export functionality
- Check file browser UI

---

#### Task 2.5: Complete Graphing Module
**Complexity:** High  
**Estimated Lines:** 500  
**Dependencies:** Task 1.1 (DisplayManager), existing graphics_engine.py  

**Description:**  
Implement complete graphing functionality.

**Current State:**
- Directory exists with README only
- Graphics engine exists but not integrated
- Phase 5 integration exists

**Deliverables:**
- Create `Broken_2.0/graphing/graph_manager.py`
- Integrate `graphics_engine.py`
- Integrate `statistical_plots.py`
- Integrate `interactive_3d.py`
- Add function input and parsing
- Update `graphing/__init__.py`

**Testing:**
- Test 2D function plotting
- Test 3D surface plotting
- Test statistical plots
- Verify zoom/pan controls

---

### Category 3: Integration & Polish (Medium Priority)

#### Task 3.1: Complete USB Interface Integration
**Complexity:** Medium  
**Estimated Lines:** 200  
**Dependencies:** None  

**Description:**  
Integrate existing USB interface module with main calculator.

**Current State:**
- `usb_interface.py` exists (661 lines)
- Imported but marked as unavailable

**Deliverables:**
- Enable USB interface in calculator
- Add PC companion integration
- Implement data transfer
- Add USB HID keyboard emulation

**Testing:**
- Test USB connection to PC
- Verify data transfer
- Test keyboard emulation
- Check error handling

---

#### Task 3.2: Integrate Enhanced Math Engine
**Complexity:** Medium  
**Estimated Lines:** 100  
**Dependencies:** Task 1.3, Task 2.2  

**Description:**  
Fully integrate the existing enhanced math engine.

**Current State:**
- `enhanced_math_engine.py` exists (992 lines)
- Contains complex numbers, matrices, statistics
- Not fully integrated

**Deliverables:**
- Connect to calculator UI
- Add menu options for advanced features
- Implement complex number mode
- Add matrix calculator mode
- Enable statistical calculations

**Testing:**
- Test complex number operations
- Test matrix operations
- Test statistical functions
- Verify all edge cases

---

#### Task 3.3: Integrate Graphics & Plot Engines
**Complexity:** High  
**Estimated Lines:** 300  
**Dependencies:** Task 2.5, Task 3.2  

**Description:**  
Connect all graphics components into cohesive system.

**Current State:**
- Multiple graphics files exist separately
- `graphics_engine.py` (461 lines)
- `statistical_plots.py` (389 lines)
- `interactive_3d.py` (456 lines)
- `phase5_integration.py` (456 lines)

**Deliverables:**
- Unify graphics interfaces
- Create common plotting API
- Integrate with calculator modes
- Add plot type selection menu

**Testing:**
- Test all plot types
- Verify switching between plots
- Check performance
- Test interactive controls

---

#### Task 3.4: Optimize Performance
**Complexity:** Medium  
**Estimated Lines:** 150  
**Dependencies:** All other tasks  

**Description:**  
Integrate and enhance performance optimizer.

**Current State:**
- `performance_optimizer.py` exists (356 lines)
- Not integrated with main app

**Deliverables:**
- Enable performance modes (ECO/FAST/QUALITY)
- Add memory management
- Optimize display refresh
- Add FPS limiting

**Testing:**
- Measure performance improvements
- Test memory usage
- Verify visual quality
- Check battery impact

---

### Category 4: Documentation & Testing (Low Priority)

#### Task 4.1: Create Comprehensive Documentation
**Complexity:** Low  
**Estimated Lines:** N/A  
**Dependencies:** All implementation tasks  

**Description:**  
Document all modules and APIs.

**Deliverables:**
- API documentation for each module
- Update README files in subdirectories
- Create user manual
- Add inline code documentation
- Create architecture diagram

---

#### Task 4.2: Implement Unit Tests
**Complexity:** Medium  
**Estimated Lines:** 800  
**Dependencies:** All implementation tasks  

**Description:**  
Create comprehensive test suite.

**Deliverables:**
- Create `tests/` directory
- Unit tests for math engine
- Tests for hardware abstraction
- UI component tests
- Integration tests

**Testing:**
- Achieve >80% code coverage
- All tests pass
- Run on actual hardware

---

#### Task 4.3: Create Build & Deployment System
**Complexity:** Low  
**Estimated Lines:** 100  
**Dependencies:** None  

**Description:**  
Automate build and deployment process.

**Deliverables:**
- Create deployment script
- Add dependency checker
- Create hardware validation tool
- Add automated testing runner

---

### Category 5: Hardware & Configuration (Low Priority)

#### Task 5.1: Enhance Hardware Validation
**Complexity:** Low  
**Estimated Lines:** 150  
**Dependencies:** Task 1.1  

**Description:**  
Improve hardware detection and validation.

**Current State:**
- `hardware_validator.py` exists but minimal
- `basic/hardware_validator.py` has more content

**Deliverables:**
- Comprehensive hardware checks
- Pin conflict detection
- Component health monitoring
- Error reporting system

**Testing:**
- Test on real hardware
- Test with missing components
- Verify error messages

---

#### Task 5.2: Create Hardware Configuration Tool
**Complexity:** Low  
**Estimated Lines:** 200  
**Dependencies:** Task 5.1  

**Description:**  
Interactive tool for hardware setup.

**Deliverables:**
- Pin configuration wizard
- Hardware detection tool
- Calibration utilities
- Configuration save/load

**Testing:**
- Test configuration wizard
- Verify pin assignments
- Test calibration

---

## Task Dependencies Graph

```
Category 1 (Refactoring) - Foundation
├── Task 1.1: Hardware Layer → [Task 2.1, 2.5, 5.1]
├── Task 1.2: File System → [Task 2.3, 2.4]
├── Task 1.3: Math Engine → [Task 2.2, 3.2]
├── Task 1.4: UI Manager → [depends on 1.1]
└── Task 1.5: App State → [none]

Category 2 (Features) - Implementation
├── Task 2.1: Games → [depends on 1.1]
├── Task 2.2: Scientific → [depends on 1.3]
├── Task 2.3: Settings → [depends on 1.2]
├── Task 2.4: SD Card → [depends on 1.2]
└── Task 2.5: Graphing → [depends on 1.1]

Category 3 (Integration) - Polish
├── Task 3.1: USB Interface → [none]
├── Task 3.2: Math Integration → [depends on 1.3, 2.2]
├── Task 3.3: Graphics Integration → [depends on 2.5, 3.2]
└── Task 3.4: Performance → [depends on all]

Category 4 (Documentation) - Final
├── Task 4.1: Documentation → [all tasks]
├── Task 4.2: Testing → [all tasks]
└── Task 4.3: Build System → [none]

Category 5 (Hardware) - Parallel
├── Task 5.1: Hardware Validation → [depends on 1.1]
└── Task 5.2: Configuration Tool → [depends on 5.1]
```

---

## Recommended Task Execution Order

### Phase 1: Foundation (Weeks 1-2)
1. Task 1.1: Extract Hardware Layer
2. Task 1.2: Extract File System
3. Task 1.3: Extract Math Engine
4. Task 1.5: Extract App State
5. Task 1.4: Extract UI Manager (depends on 1.1)

### Phase 2: Core Features (Weeks 3-4)
6. Task 2.2: Scientific Calculator
7. Task 2.3: Settings Management
8. Task 2.4: SD Card Module
9. Task 5.1: Hardware Validation (parallel)

### Phase 3: Advanced Features (Weeks 5-6)
10. Task 2.1: Games
11. Task 2.5: Graphing Module
12. Task 3.1: USB Interface
13. Task 3.2: Math Integration

### Phase 4: Integration (Week 7)
14. Task 3.3: Graphics Integration
15. Task 3.4: Performance Optimization
16. Task 5.2: Configuration Tool (parallel)

### Phase 5: Polish (Week 8)
17. Task 4.1: Documentation
18. Task 4.2: Testing
19. Task 4.3: Build System

---

## Task Template for AI Agents

### Task Assignment Template

```markdown
# Task: [Task Number and Name]

## Context
- **Project:** Peanut 3000 Calculator
- **Repository:** Isaiah802/Calculator
- **Working Directory:** Broken_2.0/

## Objective
[Brief description of what needs to be accomplished]

## Current State
[Description of existing code/files]

## Requirements
[Detailed list of what needs to be implemented]

## Deliverables
- [ ] File 1: [path/to/file.py]
- [ ] File 2: [path/to/another.py]
- [ ] Updated imports in dependent files
- [ ] Tests passing

## Dependencies
- Requires: [List of prerequisite tasks]
- Blocks: [List of tasks that depend on this]

## Testing Criteria
- [ ] Syntax check passes: `python3 -m py_compile [file]`
- [ ] Specific test 1
- [ ] Specific test 2
- [ ] Integration test with existing code

## Files to Modify
- `[path/file1.py]` - [what to do]
- `[path/file2.py]` - [what to do]

## Files to Create
- `[new/path/file.py]` - [purpose]

## Success Criteria
[How to verify the task is complete]

## Estimated Effort
- Complexity: [Low/Medium/High]
- Estimated Lines: [number]
- Estimated Time: [hours/days]

## Notes
[Any additional context or warnings]
```

---

## Summary Statistics

**Total Tasks:** 20  
**Total Estimated Lines:** ~4,900 new/refactored  

**By Complexity:**
- High: 4 tasks
- Medium: 10 tasks  
- Low: 6 tasks

**By Category:**
- Refactoring: 5 tasks (Foundation)
- Features: 5 tasks (Core functionality)
- Integration: 4 tasks (Polish)
- Documentation: 3 tasks (Quality)
- Hardware: 2 tasks (Setup)

**Parallelizable Tasks:**
- Category 1 tasks can mostly be done in parallel after initial setup
- Category 5 tasks can be done anytime
- Most Category 2 tasks can be parallel after Category 1 completes

**Critical Path:**
1.1 → 1.4 → 2.5 → 3.3 → 3.4

---

## Getting Started

### For Project Manager
1. Assign tasks from Category 1 first
2. Ensure each agent has clear dependencies
3. Review completed tasks before proceeding to dependents
4. Use task template for each assignment

### For AI Agents
1. Read full task description
2. Check all dependencies are completed
3. Review current code state
4. Implement following project patterns
5. Test thoroughly before marking complete
6. Document all changes

### For Reviewers
1. Verify all deliverables present
2. Check tests pass
3. Ensure coding standards met
4. Validate integration points
5. Review documentation updates

---

## Contact & Questions

For questions about specific tasks, refer to:
- Main README.md for project overview
- Individual module READMEs for feature details
- calculator.py comments for implementation patterns
