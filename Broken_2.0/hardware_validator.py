"""Compatibility wrapper for `firmware.hardware_validator`.

This wrapper re-exports the implementation from
`Calculator.modes.basic.hardware_validator` to preserve the original
import path while the implementation lives under modes/basic.
"""

from Calculator.modes.basic.hardware_validator import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]
        """Test display initialization and basic functionality"""
        try:
            # Test display control pins
            cs_pin = machine.Pin(Pins.DISPLAY_CS, machine.Pin.OUT)
            dc_pin = machine.Pin(Pins.DISPLAY_DC, machine.Pin.OUT)
            rst_pin = machine.Pin(Pins.DISPLAY_RST, machine.Pin.OUT)
            
            # Test pin operations
            cs_pin.value(1)
            dc_pin.value(0)
            rst_pin.value(1)
            
            # Test backlight PWM
            pwm = machine.PWM(machine.Pin(Pins.BACKLIGHT_PWM))
            pwm.freq(1000)  # 1kHz PWM
            pwm.duty_u16(32768)  # 50% duty cycle
            
            return {
                'status': True,
                'message': "Display pins configured successfully",
                'resolution': f"{Display.WIDTH}x{Display.HEIGHT}",
                'backlight': "PWM configured"
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f"Display test failed: {e}",
                'error_code': ErrorCodes.ERR_DISPLAY_INIT
            }
    
    def _test_keypad(self) -> dict:
        """Test keypad matrix configuration"""
        try:
            # Configure row pins as inputs with pull-ups
            row_pins = []
            for pin_num in Pins.KEYPAD_ROWS:
                pin = machine.Pin(pin_num, machine.Pin.IN, machine.Pin.PULL_UP)
                row_pins.append(pin)
            
            # Configure column pins as outputs
            col_pins = []
            for pin_num in Pins.KEYPAD_COLS:
                pin = machine.Pin(pin_num, machine.Pin.OUT)
                pin.value(1)  # Set high initially
                col_pins.append(pin)
            
            # Test keypad scanning
            scan_results = []
            for col_idx, col_pin in enumerate(col_pins):
                col_pin.value(0)  # Activate column
                time.sleep_us(Keypad.SCAN_SETTLE_US)
                
                for row_idx, row_pin in enumerate(row_pins):
                    if row_pin.value() == 0:  # Key pressed
                        scan_results.append((row_idx, col_idx))
                
                col_pin.value(1)  # Deactivate column
            
            return {
                'status': True,
                'message': f"Keypad configured: {Keypad.ROWS}x{Keypad.COLS} matrix",
                'active_keys': len(scan_results),
                'matrix_size': f"{Keypad.ROWS}x{Keypad.COLS}"
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f"Keypad test failed: {e}",
                'error_code': ErrorCodes.ERR_KEYPAD_INIT
            }
    
    def _test_gpio_config(self) -> dict:
        """Test GPIO pin configuration and conflicts"""
        try:
            # Collect all used pins
            used_pins = set()
            
            # SPI pins
            used_pins.update([Pins.SPI_SCK, Pins.SPI_MOSI, Pins.SPI_MISO])
            
            # Display pins
            used_pins.update([Pins.DISPLAY_CS, Pins.DISPLAY_DC, Pins.DISPLAY_RST])
            
            # Other pins
            used_pins.update([Pins.SD_CS, Pins.BACKLIGHT_PWM, Pins.BATTERY_ADC])
            
            # Keypad pins
            used_pins.update(Pins.KEYPAD_ROWS)
            used_pins.update(Pins.KEYPAD_COLS)
            
            # Check for conflicts
            all_pins = []
            all_pins.extend([Pins.SPI_SCK, Pins.SPI_MOSI, Pins.SPI_MISO])
            all_pins.extend([Pins.DISPLAY_CS, Pins.DISPLAY_DC, Pins.DISPLAY_RST])
            all_pins.extend([Pins.SD_CS, Pins.BACKLIGHT_PWM, Pins.BATTERY_ADC])
            all_pins.extend(Pins.KEYPAD_ROWS)
            all_pins.extend(Pins.KEYPAD_COLS)
            
            conflicts = []
            for pin in all_pins:
                if all_pins.count(pin) > 1:
                    conflicts.append(pin)
            
            if conflicts:
                return {
                    'status': False,
                    'message': f"Pin conflicts detected: {conflicts}",
                    'error_code': ErrorCodes.ERR_INIT_FAILED,
                    'conflicts': conflicts
                }
            
            # Check pin ranges
            invalid_pins = [pin for pin in used_pins if pin < 0 or pin > 29]
            if invalid_pins:
                return {
                    'status': False,
                    'message': f"Invalid pin numbers: {invalid_pins}",
                    'error_code': ErrorCodes.ERR_INIT_FAILED
                }
            
            return {
                'status': True,
                'message': f"GPIO configuration valid, {len(used_pins)} pins used",
                'total_pins_used': len(used_pins),
                'available_pins': 30 - len(used_pins)
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f"GPIO test failed: {e}",
                'error_code': ErrorCodes.ERR_INIT_FAILED
            }
    
    def _test_memory(self) -> dict:
        """Test memory availability and allocation"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Get memory info
            free_mem = gc.mem_free()
            alloc_mem = gc.mem_alloc()
            total_mem = free_mem + alloc_mem
            
            # Check memory levels
            if free_mem < 32 * 1024:  # Less than 32KB free
                self.warnings.append(f"Low memory: {free_mem} bytes free")
            
            # Test memory allocation
            try:
                test_buffer = bytearray(1024)  # Allocate 1KB
                del test_buffer
                gc.collect()
            except MemoryError:
                return {
                    'status': False,
                    'message': "Memory allocation test failed",
                    'error_code': ErrorCodes.ERR_MEMORY_LOW
                }
            
            return {
                'status': True,
                'message': f"Memory OK: {free_mem} bytes free, {total_mem} total",
                'free_bytes': free_mem,
                'allocated_bytes': alloc_mem,
                'total_bytes': total_mem,
                'free_percent': int((free_mem / total_mem) * 100)
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f"Memory test failed: {e}",
                'error_code': ErrorCodes.ERR_MEMORY_LOW
            }
    
    def _test_clock_system(self) -> dict:
        """Test system clock and timing"""
        try:
            # Get system frequency
            freq = machine.freq()
            
            # Test timing accuracy with a simple delay
            start_time = time.ticks_ms()
            time.sleep_ms(100)  # 100ms delay
            end_time = time.ticks_ms()
            
            actual_delay = time.ticks_diff(end_time, start_time)
            timing_error = abs(actual_delay - 100)
            
            if timing_error > 5:  # More than 5ms error
                self.warnings.append(f"Clock timing error: {timing_error}ms")
            
            return {
                'status': True,
                'message': f"Clock system OK: {freq}Hz, timing error: {timing_error}ms",
                'frequency_hz': freq,
                'timing_error_ms': timing_error
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f"Clock test failed: {e}",
                'error_code': ErrorCodes.ERR_INIT_FAILED
            }
    
    def _test_temperature(self) -> dict:
        """Test temperature sensor if available"""
        try:
            # Pico 2W has internal temperature sensor on ADC channel 4
            try:
                temp_sensor = machine.ADC(4)
                temp_reading = temp_sensor.read_u16()
                
                # Convert to temperature (approximate formula for RP2040/RP2350)
                voltage = temp_reading * 3.3 / 65535
                temperature = 27 - (voltage - 0.706) / 0.001721
                
                if temperature > 70:  # Above 70°C
                    return {
                        'status': False,
                        'message': f"Temperature too high: {temperature:.1f}°C",
                        'error_code': ErrorCodes.ERR_TEMPERATURE_HIGH,
                        'temperature_c': temperature
                    }
                elif temperature > 60:  # Above 60°C
                    self.warnings.append(f"High temperature: {temperature:.1f}°C")
                
                return {
                    'status': True,
                    'message': f"Temperature OK: {temperature:.1f}°C",
                    'temperature_c': temperature
                }
                
            except:
                # Temperature sensor not available or failed
                return {
                    'status': True,
                    'message': "Temperature sensor not available",
                    'temperature_c': None
                }
                
        except Exception as e:
            return {
                'status': False,
                'message': f"Temperature test failed: {e}",
                'error_code': ErrorCodes.ERR_INIT_FAILED
            }
    
    def _generate_summary(self) -> dict:
        """Generate comprehensive diagnostic summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'])
        failed_tests = total_tests - passed_tests
        
        # Overall status
        overall_status = failed_tests == 0
        
        # Collect all error codes
        error_codes = []
        for result in self.test_results.values():
            if not result['status'] and 'error_code' in result:
                error_codes.append(result['error_code'])
        
        summary = {
            'overall_status': overall_status,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'warnings': len(self.warnings),
            'error_codes': list(set(error_codes)),
            'test_results': self.test_results,
            'warning_messages': self.warnings,
            'success_rate': int((passed_tests / total_tests) * 100) if total_tests > 0 else 0
        }
        
        # Print summary
        print("\n" + "=" * 50)
        print("🏁 Hardware Diagnostic Summary")
        print("=" * 50)
        print(f"Overall Status: {'✅ PASS' if overall_status else '❌ FAIL'}")
        print(f"Tests Passed: {passed_tests}/{total_tests} ({summary['success_rate']}%)")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if error_codes:
            print(f"\n❌ Error Codes: {error_codes}")
        
        return summary

# Convenience function for quick hardware check
def quick_hardware_check() -> bool:
    """Perform quick hardware validation"""
    validator = HardwareValidator()
    result = validator.run_full_diagnostic()
    return result['overall_status']

# Export
__all__ = ['HardwareValidator', 'quick_hardware_check']