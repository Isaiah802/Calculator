# Calculator Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Calculator Application                   │
│                      (calculator.py)                         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│  Hardware    │      │   Core       │     │   Features   │
│  Layer       │      │   Logic      │     │   Layer      │
└──────────────┘      └──────────────┘     └──────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│ - Display    │      │ - Math       │     │ - Graphing   │
│ - Keypad     │      │ - Security   │     │ - Games      │
│ - Power      │      │ - State      │     │ - USB        │
│ - SPI        │      │ - UI         │     │ - Settings   │
└──────────────┘      └──────────────┘     └──────────────┘
```

## Current File Structure

```
Calculator/
├── Broken_2.0/                    # Main application directory
│   ├── calculator.py              # Main app (~1,300 lines) - REFACTORED
│   │   ├── Config                 # Configuration management
│   │   ├── Logger                 # Logging system
│   │   └── CalculatorApp          # Main application class
│   │
│   ├── hardware/                  # Hardware abstraction layer
│   │   ├── __init__.py
│   │   ├── spi_manager.py         # SPI bus management
│   │   ├── display.py             # ILI9341 display control
│   │   ├── keypad.py              # 6x4 keypad input
│   │   └── power.py               # Battery & power management
│   │
│   ├── storage/                   # File system management
│   │   ├── __init__.py
│   │   └── filesystem.py          # SD card operations
│   │
│   ├── math/                      # Mathematical engine
│   │   ├── __init__.py
│   │   └── secure_engine.py       # Safe expression evaluation
│   │
│   ├── ui/                        # User interface
│   │   ├── __init__.py
│   │   └── ui_manager.py          # UI rendering
│   │
│   ├── core/                      # Core application components
│   │   ├── __init__.py
│   │   └── app_state.py           # Application state management
│   │
│   ├── enhanced_math_engine.py    # Advanced math (992 lines)
│   │   └── EnhancedMathEngine     # Complex, matrix, statistics
│   │
│   ├── graphics_engine.py         # 2D graphics (461 lines)
│   │   ├── GraphicsEngine         # Plotting engine
│   │   ├── GraphColors            # Color management
│   │   └── Point2D                # Point representation
│   │
│   ├── statistical_plots.py       # Statistical plots (389 lines)
│   │   ├── StatisticalPlotter     # Histogram, scatter, etc.
│   │   └── ComplexPlotter         # Complex number plots
│   │
│   ├── interactive_3d.py          # 3D graphics (456 lines)
│   │   ├── Surface3D              # 3D surface representation
│   │   ├── Plot3DEngine           # 3D rendering
│   │   └── InteractiveGraphControls # 3D interaction
│   │
│   ├── usb_interface.py           # USB connectivity (661 lines)
│   │   ├── USBInterfaceManager    # USB management
│   │   └── create_usb_interface   # Factory function
│   │
│   ├── performance_optimizer.py   # Performance tuning (356 lines)
│   │   └── Performance modes & optimization
│   │
│   ├── phase5_integration.py      # Graphing integration (456 lines)
│   │   └── Phase5GraphingSystem   # Graph system integration
│   │
│   ├── hardware_config.py         # Hardware config wrapper
│   ├── hardware_validator.py      # Hardware validation wrapper
│   │
│   ├── basic/                     # Basic calculator mode
│   │   ├── calculator.py          # Basic calc implementation
│   │   ├── display.py             # Simple display
│   │   ├── main.py                # Entry point
│   │   ├── simple_calc.py         # Simple calculator
│   │   ├── hardware_config.py     # Hardware configuration
│   │   └── hardware_validator.py  # Hardware validation
│   │
│   ├── games/                     # Games module (EMPTY)
│   │   ├── __init__.py
│   │   └── README.md
│   │
│   ├── graphing/                  # Graphing module (EMPTY)
│   │   ├── __init__.py
│   │   └── README.md
│   │
│   ├── scientific/                # Scientific calc (EMPTY)
│   │   ├── __init__.py
│   │   └── README.md
│   │
│   ├── sd/                        # SD card module (EMPTY)
│   │   ├── __init__.py
│   │   └── README.md
│   │
│   ├── settings/                  # Settings module (EMPTY)
│   │   ├── __init__.py
│   │   └── README.md
│   │
│   └── pc_companion/              # PC companion app
│       ├── pc_companion.py
│       └── __init__.py
│
├── calculator_backup_working_*/   # Backup of working version
├── README.md                      # Project README
└── .gitignore                     # Git ignore rules
```

## Target Architecture (After Refactoring)

```
Calculator/
├── Broken_2.0/
│   ├── calculator.py              # Main entry point (simplified)
│   │
│   ├── core/                      # Core application logic
│   │   ├── __init__.py
│   │   ├── app_state.py           # Application state management
│   │   └── config.py              # Configuration classes
│   │
│   ├── hardware/                  # Hardware abstraction layer
│   │   ├── __init__.py
│   │   ├── hardware_layer.py      # SPIManager, DisplayManager, etc.
│   │   ├── keypad.py              # Keypad management
│   │   ├── power.py               # Power management
│   │   └── validation.py          # Hardware validation
│   │
│   ├── math/                      # Mathematical engines
│   │   ├── __init__.py
│   │   ├── secure_engine.py       # Safe evaluation
│   │   ├── enhanced_engine.py     # Advanced math
│   │   ├── complex_math.py        # Complex numbers
│   │   ├── matrix_math.py         # Matrix operations
│   │   └── statistics.py          # Statistical functions
│   │
│   ├── ui/                        # User interface
│   │   ├── __init__.py
│   │   ├── ui_manager.py          # UI rendering
│   │   ├── menu_system.py         # Menu management
│   │   └── themes.py              # Color themes
│   │
│   ├── storage/                   # File system & persistence
│   │   ├── __init__.py
│   │   ├── filesystem.py          # File operations
│   │   └── history.py             # Calculation history
│   │
│   ├── graphics/                  # Graphics & plotting
│   │   ├── __init__.py
│   │   ├── graphics_engine.py     # 2D graphics
│   │   ├── plot_2d.py             # 2D plotting
│   │   ├── plot_3d.py             # 3D plotting
│   │   ├── statistical_plots.py   # Statistical plots
│   │   └── interactive.py         # Interactive controls
│   │
│   ├── scientific/                # Scientific calculator
│   │   ├── __init__.py
│   │   ├── functions.py           # Trig, log, exp functions
│   │   └── units.py               # Unit conversions
│   │
│   ├── graphing/                  # Graphing functionality
│   │   ├── __init__.py
│   │   ├── graph_manager.py       # Graph management
│   │   ├── function_parser.py     # Function parsing
│   │   └── plot_controller.py     # Plot control
│   │
│   ├── games/                     # Games
│   │   ├── __init__.py
│   │   ├── snake.py               # Snake game
│   │   └── pong.py                # Pong game
│   │
│   ├── settings/                  # Settings management
│   │   ├── __init__.py
│   │   └── settings_manager.py    # Settings persistence
│   │
│   ├── sd/                        # SD card functionality
│   │   ├── __init__.py
│   │   └── sd_manager.py          # SD operations
│   │
│   ├── usb/                       # USB connectivity
│   │   ├── __init__.py
│   │   ├── usb_interface.py       # USB management
│   │   └── hid_keyboard.py        # HID emulation
│   │
│   ├── performance/               # Performance optimization
│   │   ├── __init__.py
│   │   └── optimizer.py           # Performance tuning
│   │
│   └── tests/                     # Test suite
│       ├── __init__.py
│       ├── test_hardware.py
│       ├── test_math.py
│       ├── test_graphics.py
│       └── test_integration.py
│
└── docs/                          # Documentation
    ├── API.md
    ├── USER_GUIDE.md
    └── HARDWARE_SETUP.md
```

## Component Responsibilities

### Hardware Layer
**Purpose:** Abstract hardware interactions  
**Components:**
- SPI bus management (shared between display and SD)
- Display driver (ILI9341)
- Keypad input (6x4 matrix)
- Power management (battery monitoring, backlight)
- Hardware validation

**Key Patterns:**
- Thread-safe SPI switching
- Buffered display updates
- Debounced keypad input
- Graceful degradation on hardware failure

### Core Logic
**Purpose:** Central application management  
**Components:**
- Application state machine
- Configuration management
- Event loop
- Mode switching (calculator, graph, games, etc.)

**Key Patterns:**
- State pattern for modes
- Observer pattern for events
- Singleton for configuration

### Math Engine
**Purpose:** Safe and powerful mathematical operations  
**Components:**
- Expression parser and evaluator
- Security (input sanitization, timeout)
- Complex number support
- Matrix operations
- Statistical functions

**Key Patterns:**
- Sandboxed evaluation
- Timeout mechanism
- Error handling and reporting

### UI Layer
**Purpose:** User interface rendering and interaction  
**Components:**
- Menu system
- Text rendering
- Battery indicator
- Status displays

**Key Patterns:**
- Component-based rendering
- Dirty region optimization
- Theme support

### Graphics/Plotting
**Purpose:** Data visualization  
**Components:**
- 2D function plotting
- 3D surface rendering
- Statistical plots
- Interactive controls

**Key Patterns:**
- Viewport transformation
- Clipping and culling
- Performance optimization
- Interactive manipulation

### Storage
**Purpose:** Persistent data management  
**Components:**
- SD card interface
- File operations
- Calculation history
- Settings persistence

**Key Patterns:**
- Lazy mounting
- Graceful failure
- Data serialization

## Data Flow

### Input Processing
```
Keypad Press → KeypadManager.get_key()
              ↓
        Debouncing & Long Press Detection
              ↓
        AppState.handle_input()
              ↓
        Mode-specific Handler
              ↓
        Action Execution
```

### Display Update
```
State Change → Mark Dirty
             ↓
        UIManager.render()
             ↓
        Draw to FrameBuffer
             ↓
        DisplayManager.show()
             ↓
        SPI Transfer to Display
```

### Calculation Flow
```
Expression Input → SecureMathEngine.evaluate()
                  ↓
              Parse & Sanitize
                  ↓
              Timeout Protection
                  ↓
              Eval in Safe Context
                  ↓
              Format Result
                  ↓
              Display & Store
```

## Hardware Interface

### Pin Assignments
```
SPI Bus 1:
- SCK:  Pin 10
- MOSI: Pin 11  
- MISO: Pin 12

Display (ILI9341):
- CS:  Pin 13
- DC:  Pin 15
- RST: Pin 14

SD Card:
- CS:  Pin 17

Keypad Matrix (6x4):
- Cols: Pins 2, 3, 4, 5
- Rows: Pins 6, 7, 8, 9, 21, 27

Other:
- Backlight PWM: Pin 28
- Battery ADC:   Pin 26
```

### Memory Management
- Display buffer: 320×240×2 = 153,600 bytes
- Framebuffer fallback: 160×120×2 = 38,400 bytes
- Garbage collection every 50 operations
- SD card operations done in chunks

## Performance Considerations

### Display Optimization
- Buffered updates (write full frame at once)
- Dirty region tracking (planned)
- Reduced resolution fallback for low memory
- Fast SPI (32 MHz)

### Math Performance
- Timeout protection (1 second default)
- Limited recursion depth
- Cached results (planned)

### Memory Management
- Regular garbage collection
- Careful buffer allocation
- Graceful degradation strategies

## Security Features

### Math Engine Security
- Input sanitization (whitelist approach)
- Function call restrictions
- Timeout mechanism
- Resource limits

### File System Security
- Path validation
- Safe file operations
- Error handling

## Error Handling

### Hardware Errors
- Graceful degradation
- User notification
- Retry mechanisms
- Fallback modes

### Calculation Errors
- Safe error messages
- State preservation
- Recovery options

## Future Enhancements

### Planned Features
- WiFi connectivity
- Cloud sync
- Advanced graphing modes
- Custom functions
- Programming mode
- More games

### Architecture Improvements
- Plugin system
- Event-driven architecture
- Better memory management
- Multi-threaded operations (if supported)

## Development Guidelines

### Code Style
- Follow existing patterns
- Use type hints
- Document complex logic
- Keep functions focused

### Testing
- Unit tests for all modules
- Integration tests for workflows
- Hardware testing on actual device
- Memory leak testing

### Documentation
- Docstrings for all public functions
- Architecture decision records
- API documentation
- User guides

## Migration Path

### Phase 1: Extract Core Components
1. Hardware abstraction layer
2. File system management
3. Math engine
4. UI management

### Phase 2: Implement Missing Features
1. Scientific functions
2. Games
3. Settings
4. SD card features

### Phase 3: Integration
1. USB interface
2. Graphics engines
3. Performance optimization

### Phase 4: Polish
1. Documentation
2. Testing
3. Build system
4. Deployment tools

---

**Last Updated:** 2025-11-07  
**Version:** 4.0.0  
**Status:** Refactoring in progress
