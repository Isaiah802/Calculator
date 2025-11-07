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
├── Broken_2.0/          # Fixed version with improvements
│   ├── calculator.py    # Main calculator application (FIXED)
│   ├── basic/           # Basic calculator mode
│   ├── games/           # Game modules (Snake, Pong)
│   ├── graphing/        # Graphing functionality
│   ├── scientific/      # Scientific calculator features
│   ├── sd/              # SD card interface
│   └── settings/        # Settings management
├── calculator_backup_working_2025-11-07_11-23-39/  # Working backup
└── README.md            # This file
```

## Recent Improvements

### Syntax and Code Quality Fixes (Latest)

1. **Fixed Critical Syntax Errors**
   - Removed orphaned compatibility wrapper code that was causing IndentationError
   - Fixed indentation in `_send_command()` and `_set_window()` methods
   - Added missing class definitions (Config, Logger, HardwareError)
   - Added missing helper functions (constrain)

2. **Added Configuration Management**
   - Centralized Config class with Hardware, System, and UI settings
   - Proper RGB565 color definitions
   - Hardware pin assignments and timing parameters

3. **Code Quality Improvements**
   - File now compiles without syntax errors
   - Added .gitignore for Python artifacts
   - Maintains proper code structure with 15 classes and 106 methods

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
