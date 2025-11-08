#!/usr/bin/env python3
"""
PowerManager - Battery monitoring and backlight control

Part of the Hardware Abstraction Layer for Peanut 3000 Calculator.
Manages battery voltage monitoring, backlight PWM control, and auto-dim functionality.
"""

from machine import Pin, PWM, ADC


def constrain(value, min_value, max_value):
    """Constrain value within range"""
    return max(min_value, min(max_value, value))


class PowerManager:
    """Battery monitoring and power management"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        self.adc = ADC(Pin(self.config.Hardware.BATTERY_ADC))
        self.backlight_pwm = PWM(Pin(self.config.Hardware.BACKLIGHT_PWM))
        self.backlight_pwm.freq(1000)
        
        # Battery monitoring
        self.voltage_filter = None
        self.filter_alpha = 0.2
        
        # Power settings
        self.brightness = 60
        self.auto_dim_enabled = True
        self.sleep_timeout = self.config.System.SLEEP_TIMEOUT_MS
        
        self.set_brightness(self.brightness)
        
    def read_battery_voltage(self) -> float:
        """Read and filter battery voltage"""
        # Read ADC (0-65535 for 0-3.3V)
        raw = self.adc.read_u16()
        voltage = (raw / 65535.0) * 3.3 * 2.0  # Account for voltage divider
        
        # Apply low-pass filter
        if self.voltage_filter is None:
            self.voltage_filter = voltage
        else:
            self.voltage_filter = ((1 - self.filter_alpha) * self.voltage_filter + 
                                 self.filter_alpha * voltage)
            
        return round(self.voltage_filter, 3)
        
    def get_battery_percentage(self, voltage: float) -> int:
        """Convert voltage to percentage"""
        # LiPo battery curve approximation
        voltage_points = [
            (4.20, 100), (4.10, 90), (4.00, 80), (3.90, 70), (3.80, 60),
            (3.70, 50), (3.60, 40), (3.50, 30), (3.40, 20), (3.30, 10), (3.00, 0)
        ]
        
        for i in range(len(voltage_points) - 1):
            v_high, p_high = voltage_points[i]
            v_low, p_low = voltage_points[i + 1]
            
            if voltage >= v_low:
                if voltage >= v_high:
                    return p_high
                # Linear interpolation
                ratio = (voltage - v_low) / (v_high - v_low)
                return int(p_low + ratio * (p_high - p_low))
                
        return 0
        
    def set_brightness(self, percent: int):
        """Set backlight brightness (0-100%)"""
        self.brightness = constrain(percent, 0, 100)
        duty = int(self.brightness / 100 * 65535)
        try:
            self.backlight_pwm.duty_u16(duty)
        except Exception as e:
            self.logger.error(f"Failed to set brightness: {e}")
            
    def auto_dim(self, inactive_time_ms: int):
        """Automatically dim display based on inactivity"""
        if not self.auto_dim_enabled:
            return
            
        if inactive_time_ms > self.sleep_timeout:
            # Deep sleep mode
            self.set_brightness(5)
        elif inactive_time_ms > self.sleep_timeout // 2:
            # Dim mode
            self.set_brightness(max(10, self.brightness // 3))
        else:
            # Normal brightness
            self.set_brightness(self.brightness)
