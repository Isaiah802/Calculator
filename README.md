# Calculator

Advanced Scientific Calculator for Raspberry Pi Pico 2W

## Overview

The Peanut 3000 is an advanced scientific calculator built for the Raspberry Pi Pico 2W microcontroller. It features:

- **Hardware**: ILI9341 Display, 6x4 Keypad, SD Card support, Battery monitoring
- **Mathematical Capabilities**: Basic arithmetic, scientific functions, complex numbers, statistics, matrix operations
- **Advanced Features**: Graphing, USB PC connectivity, games, file management
- **Modular Architecture**: Clean separation of concerns with hardware abstraction layers

## Project Structure

```
Calculator/
├── Broken_2.0/          # Main application directory
│   ├── calculator.py    # Main calculator application (1,469 lines - refactored)
│   ├── core/            # Core state management ✅
│   ├── hardware/        # Hardware abstraction layer ✅
│   ├── mathengine/      # Secure math engine ✅
│   ├── storage/         # File system management ✅
│   ├── ui/              # UI rendering ✅
│   ├── games/           # Game modules (Snake, Pong) ✅ COMPLETE
│   ├── scientific/      # Scientific calculator features ✅ COMPLETE
│   ├── settings/        # Settings management ✅ COMPLETE
│   ├── graphing/        # Graphing functionality ✅ COMPLETE
│   └── sd/              # SD card interface - TO BE IMPLEMENTED
├── tasks/               # Individual task specifications for AI agents
│   ├── README.md        # Task index and status
│   ├── TASK_1.1_Hardware_Layer.md
│   └── TASK_2.1_Games_Module.md
├── TASK_BREAKDOWN.md    # Complete project breakdown (20 tasks)
├── ARCHITECTURE.md      # System architecture and design
├── AI_AGENT_GUIDE.md    # Coding standards and patterns
└── README.md            # This file
```

## Project Breakdown for AI Agents

This repository includes comprehensive documentation to break down the calculator project into smaller, manageable tasks that can be assigned to multiple AI agents.

### 🚀 Quick Start
- **NEW AGENT?** Start here → **[NEXT_STEPS.md](NEXT_STEPS.md)** (Immediate next task with detailed guide)
- **GETTING STARTED?** See → [Getting Started Guide](GETTING_STARTED.md)
- **OVERVIEW?** See → [Project Summary](PROJECT_SUMMARY.md) (Visual overview with diagrams)
- **MANAGING?** See → [Task Breakdown](TASK_BREAKDOWN.md) (All 20 tasks detailed)
- **CODING?** See → [AI Agent Guide](AI_AGENT_GUIDE.md) (Quick reference & patterns)
- **WORKFLOW?** See → [Workflow Guide](WORKFLOW_GUIDE.md) (User requirements & testing)

### 📋 Main Documentation
- **[NEXT_STEPS.md](NEXT_STEPS.md)** - **⭐ START HERE** for next AI agent - Detailed guide for immediate next task
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Step-by-step guide for managers, agents, and reviewers
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Visual summary with diagrams and metrics
- **[TASK_BREAKDOWN.md](TASK_BREAKDOWN.md)** - Complete breakdown of 20 tasks across 5 categories
- **[TASK_COMPLETION_SUMMARY.md](TASK_COMPLETION_SUMMARY.md)** - Current status and completion tracking
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture, design patterns, and data flow
- **[AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md)** - Quick reference, code patterns, and best practices
- **[WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)** - Development workflow, user requirements, and testing approach

### 📝 Task Completion Reports
- **[TASK_2.1_COMPLETION_REPORT.md](TASK_2.1_COMPLETION_REPORT.md)** - Games Module completion
- **[TASK_2.3_COMPLETION_REPORT.md](TASK_2.3_COMPLETION_REPORT.md)** - Settings Management completion & verification
- **[TASK_2.5_COMPLETION_REPORT.md](TASK_2.5_COMPLETION_REPORT.md)** - Graphing Module completion ✅ NEW
- **[CODE_REVIEW_1X_TASKS.md](CODE_REVIEW_1X_TASKS.md)** - Phase 1 comprehensive review

### 📁 Task Directory
- **[tasks/](tasks/)** - Individual detailed task specifications
  - [Task Index](tasks/README.md) - Status tracking and assignment order
  - [Task 1.1: Hardware Layer](tasks/TASK_1.1_Hardware_Layer.md) - Extract hardware abstraction (READY)
  - [Task 2.1: Games Module](tasks/TASK_2.1_Games_Module.md) - Implement Snake and Pong (READY)
  - _18 more tasks documented in TASK_BREAKDOWN.md_

### 📊 Project At a Glance
```
Total Tasks: 20 across 5 categories
├─ Category 1: Refactoring (5 tasks) ✅ COMPLETE
├─ Category 2: Features (5 tasks) - 4/5 complete (80%) ✅
│  ├─ Task 2.1: Games Module ✅ COMPLETE
│  ├─ Task 2.2: Scientific Calculator ✅ COMPLETE
│  ├─ Task 2.3: Settings Management ✅ COMPLETE
│  ├─ Task 2.4: SD Card Module ⏭️ READY (LOW Priority)
│  └─ Task 2.5: Graphing Module ✅ COMPLETE
├─ Category 3: Integration (4 tasks) - Ready ⭐ RECOMMENDED
├─ Category 4: Documentation (3 tasks) - Pending
└─ Category 5: Hardware (2 tasks) - Pending

Current State: 1,469 lines main file, 8 modular packages created
Progress: Phase 1 Complete + 4 Phase 2 tasks (9/20 tasks) - 45% done
Next: Task 2.4 (SD Card) OR Phase 3 Integration (Recommended ⭐)
```

## Recent Improvements

### Phase 2: Feature Implementation (In Progress - November 2025)

**Tasks 2.1-2.3, 2.5 Complete ✅** (80% of Phase 2)

1. **Task 2.1: Games Module** ✅ COMPLETE
   - Implemented Snake game (289 lines)
   - Implemented Pong vs AI game (313 lines)
   - Full integration with calculator
   - Working game controls and menus

2. **Task 2.2: Scientific Calculator Module** ✅ COMPLETE
   - Implemented ScientificCalculator class (575 lines)
   - 30+ scientific functions
   - Trigonometric, hyperbolic, logarithmic functions
   - Statistical functions (mean, median, std_dev, variance)
   - Angle mode management (deg/rad)

3. **Task 2.3: Settings Management Module** ✅ COMPLETE & VERIFIED
   - Implemented SettingsManager class (171 lines)
   - SD card persistence for all settings
   - Full calculator integration with UI
   - All tests passing, no security issues
   - **See:** [TASK_2.3_COMPLETION_REPORT.md](TASK_2.3_COMPLETION_REPORT.md)

4. **Task 2.5: Graphing Module** ✅ COMPLETE
   - Implemented GraphManager class (570 lines)
   - Unified API for all graphing operations
   - 2D function plotting, statistical plots, 3D surfaces
   - Interactive controls (zoom, pan, trace)
   - Full backward compatibility
   - Zero security vulnerabilities
   - **See:** [TASK_2.5_COMPLETION_REPORT.md](TASK_2.5_COMPLETION_REPORT.md)

**Next:** Task 2.4 (SD Card Module - LOW priority) OR Phase 3 Integration (RECOMMENDED ⭐)

### Phase 1: Refactoring Complete (November 2025) ✅

1. **Code Refactoring Completed**
   - ✅ Task 1.1: Hardware layer extracted (487 lines)
   - ✅ Task 1.2: File system management extracted (206 lines)
   - ✅ Task 1.3: Math engine extracted (435 lines)
   - ✅ Task 1.4: UI management extracted (196 lines)
   - ✅ Task 1.5: App state management extracted (90 lines)
   - **Result:** calculator.py reduced from 2,395 → 1,469 lines (39% reduction)
   - **Created:** 2,732 lines across 8 modular packages

2. **Modular Architecture Established**
   - Created 8 packages: core, hardware, mathengine, storage, ui, games, scientific, settings, graphing
   - Clean import structure with no circular dependencies
   - Proper error handling and logging throughout
   - All code compiles without errors
   - Total extracted code: 2,732 lines

3. **Repository Cleanup**
   - Removed 1,278 lines of unused/broken code
   - Cleaned up deployment scripts
   - Updated all documentation to reflect current state

### Task Breakdown System (2025-11-07)

1. **Comprehensive Documentation**
   - Created TASK_BREAKDOWN.md with 20 detailed tasks
   - Created ARCHITECTURE.md with system design
   - Created AI_AGENT_GUIDE.md with coding standards
   - Created WORKFLOW_GUIDE.md with user requirements
   - Created TASK_COMPLETION_SUMMARY.md for status tracking

2. **Task Organization**
   - Category 1: Code Refactoring (5 tasks) ✅ COMPLETE
   - Category 2: Feature Implementation (5 tasks) - Ready
   - Category 3: Integration & Polish (4 tasks) - Pending
   - Category 4: Documentation & Testing (3 tasks) - Pending
   - Category 5: Hardware & Configuration (2 tasks) - Pending

3. **Ready for Phase 2**
   - All refactoring dependencies complete
   - Clear dependencies and execution order
   - Testing criteria and success metrics
   - Code patterns and templates

### Previous Improvements

1. **Fixed Critical Syntax Errors**
   - Removed orphaned compatibility wrapper code
   - Fixed indentation issues
   - Added missing class definitions (Config, Logger, HardwareError)

2. **Added Configuration Management**
   - Centralized Config class with Hardware, System, and UI settings
   - Proper RGB565 color definitions
   - Hardware pin assignments and timing parameters

3. **Code Quality**
   - File compiles without syntax errors
   - Added .gitignore for Python artifacts
   - Maintains proper code structure

## Usage

This calculator is designed to run on MicroPython-compatible hardware (Raspberry Pi Pico 2W). 

### For Development
```bash
# Check syntax
python3 -m py_compile Broken_2.0/calculator.py

# The file should compile without errors
```

### For Deployment
Upload to your Raspberry Pi Pico 2W using:
- Thonny IDE
- ampy: `ampy --port /dev/ttyUSB0 put Broken_2.0/calculator.py`
- rshell

## Features

- **Calculator Mode**: Standard and scientific calculations
- **Graph Mode**: Function plotting with interactive controls
- **Statistics**: Data analysis and statistical calculations
- **Matrix Operations**: Matrix math including determinant, transpose, inverse
- **Unit Conversion**: Convert between various units
- **Complex Numbers**: Full support for complex number operations
- **File Management**: Save calculations to SD card
- **Games**: Snake and Pong (when modules are available)
- **Power Management**: Battery monitoring and auto-dim

## Hardware Requirements

- Raspberry Pi Pico 2W
- ILI9341 320x240 TFT Display
- 6x4 Matrix Keypad
- SD Card module
- LiPo battery (optional)

## Contributing

When making changes:
1. Test syntax with `python3 -m py_compile`
2. Follow existing code structure and patterns
3. Update documentation
4. Test on actual hardware when possible

## License

See project repository for license information.
