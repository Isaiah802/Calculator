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
│   ├── calculator.py    # Main calculator application (2,395 lines)
│   ├── basic/           # Basic calculator mode
│   ├── games/           # Game modules (Snake, Pong) - TO BE IMPLEMENTED
│   ├── graphing/        # Graphing functionality - TO BE IMPLEMENTED
│   ├── scientific/      # Scientific calculator features - TO BE IMPLEMENTED
│   ├── sd/              # SD card interface - TO BE IMPLEMENTED
│   └── settings/        # Settings management - TO BE IMPLEMENTED
├── tasks/               # Individual task specifications for AI agents
│   ├── README.md        # Task index and status
│   ├── TASK_1.1_Hardware_Layer.md
│   └── TASK_2.1_Games_Module.md
├── TASK_BREAKDOWN.md    # Complete project breakdown (20 tasks)
├── ARCHITECTURE.md      # System architecture and design
├── AI_AGENT_GUIDE.md    # Coding standards and patterns
├── calculator_backup_working_2025-11-07_11-23-39/  # Working backup
└── README.md            # This file
```

## Project Breakdown for AI Agents

This repository includes comprehensive documentation to break down the calculator project into smaller, manageable tasks that can be assigned to multiple AI agents:

### 📋 Main Documentation
- **[TASK_BREAKDOWN.md](TASK_BREAKDOWN.md)** - Complete breakdown of 20 tasks across 5 categories
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture, design patterns, and data flow
- **[AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md)** - Quick reference, code patterns, and best practices

### 📁 Task Directory
- **[tasks/](tasks/)** - Individual detailed task specifications
  - [Task Index](tasks/README.md) - Status tracking and assignment order
  - [Task 1.1: Hardware Layer](tasks/TASK_1.1_Hardware_Layer.md) - Extract hardware abstraction
  - [Task 2.1: Games Module](tasks/TASK_2.1_Games_Module.md) - Implement Snake and Pong
  - _More tasks to be detailed..._

### 📊 Project Metrics
- **Main file:** 2,395 lines (needs refactoring)
- **Total tasks:** 20 (across 5 categories)
- **Current modules:** 24 Python files
- **Empty modules:** 5 (games, graphing, scientific, sd, settings)

## Recent Improvements

### Task Breakdown System (Latest - 2025-11-07)

1. **Comprehensive Documentation**
   - Created TASK_BREAKDOWN.md with 20 detailed tasks
   - Created ARCHITECTURE.md with system design
   - Created AI_AGENT_GUIDE.md with coding standards

2. **Task Organization**
   - Category 1: Code Refactoring (5 tasks)
   - Category 2: Feature Implementation (5 tasks)
   - Category 3: Integration & Polish (4 tasks)
   - Category 4: Documentation & Testing (3 tasks)
   - Category 5: Hardware & Configuration (2 tasks)

3. **Ready for Assignment**
   - Individual task files with detailed specifications
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
