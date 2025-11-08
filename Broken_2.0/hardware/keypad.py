#!/usr/bin/env python3
"""
KeypadManager - 6x4 matrix keypad input handling

Part of the Hardware Abstraction Layer for Peanut 3000 Calculator.
Manages keypad scanning, debouncing, and long-press detection.
"""

from machine import Pin
# typing module not available in MicroPython - type hints work without import
import time


class KeypadManager:
    """Enhanced keypad handling with debouncing and events"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        self.cols = [Pin(c, Pin.IN, Pin.PULL_UP) for c in self.config.Hardware.KEYPAD_COLS]
        self.rows = [Pin(r, Pin.OUT) for r in self.config.Hardware.KEYPAD_ROWS]
        
        # State tracking
        self.pressed_keys = set()
        self.key_down_times = {}
        self.last_scan = 0
        
        # Key mappings
        self.base_map = {
            (5,0): 'ON',  (5,1): '0',   (5,2): '.',   (5,3): '=',
            (4,0): '+',   (4,1): '3',   (4,2): '2',   (4,3): '1',
            (3,0): '-',   (3,1): '6',   (3,2): '5',   (3,3): '4',
            (2,0): '*',   (2,1): '9',   (2,2): '8',   (2,3): '7',
            (1,0): '/',   (1,1): ')',   (1,2): '(',   (1,3): 'C',
            (0,0): 'Save', (0,1): 'DEL', (0,2): 'π',  (0,3): 'S'
        }
        
        self.shift_map = self.base_map.copy()
        self.shift_map.update({
            (5,0): 'ON',     (5,1): '0',      (5,2): '.',      (5,3): '=',
            (4,0): '+',      (4,1): 'tan(',   (4,2): 'cos(',   (4,3): 'sin(',
            (3,0): '/',      (3,1): '^2',     (3,2): 'ln(',    (3,3): 'log(',
            (2,0): '*',      (2,1): '9',      (2,2): '8',      (2,3): '7',
            (1,0): '√',      (1,1): ')',      (1,2): '(',      (1,3): 'C',
            (0,0): 'exp(',   (0,1): 'DEL',    (0,2): 'π',      (0,3): 'S'
        })
        
    def scan_keys(self):  # Returns set of (row, col) tuples
        """Scan keypad and return pressed keys"""
        pressed = set()
        
        # Set all rows high first
        for row_pin in self.rows:
            row_pin.value(1)
            
        # Scan each row
        for row_idx, row_pin in enumerate(self.rows):
            # Set current row low
            for r in self.rows:
                r.value(1)
            row_pin.value(0)
            
            # Small settling time
            time.sleep_us(self.config.Hardware.SCAN_SETTLE_US)
            
            # Check columns
            for col_idx, col_pin in enumerate(self.cols):
                if col_pin.value() == 0:  # Key pressed (pulled low)
                    pressed.add((row_idx, col_idx))
                    
        return pressed
        
    def get_events(self) -> List[Tuple[Tuple[int, int], str]]:
        """Get key events with debouncing"""
        now = time.ticks_ms()
        events = []
        
        # Throttle scanning
        if time.ticks_diff(now, self.last_scan) < self.config.Hardware.DEBOUNCE_MS // 2:
            return events
            
        self.last_scan = now
        current_pressed = self.scan_keys()
        
        # Detect new key presses
        for key in current_pressed:
            if key not in self.pressed_keys:
                self.pressed_keys.add(key)
                self.key_down_times[key] = now
                events.append((key, 'down'))
                
        # Detect key releases and long presses
        for key in list(self.pressed_keys):
            if key not in current_pressed:
                # Key released
                down_time = self.key_down_times.pop(key, now)
                duration = time.ticks_diff(now, down_time)
                self.pressed_keys.remove(key)
                
                if duration >= self.config.Hardware.LONG_PRESS_MS:
                    events.append((key, 'long'))
                else:
                    events.append((key, 'tap'))
                    
        return events
        
    def get_key_label(self, key: Tuple[int, int], shift_mode: bool) -> Optional[str]:
        """Get label for key position"""
        key_map = self.shift_map if shift_mode else self.base_map
        return key_map.get(key)
