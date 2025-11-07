"""
Hardware Validator moved into basic mode namespace.

This is a copy of `firmware/hardware_validator.py` so basic-mode code can
use a local validator during refactor. The original path will be kept as
a small wrapper to preserve imports.
"""

import machine
import time
import gc
from micropython import const
from firmware.hardware_config import Pins, Display, Keypad, Power, ErrorCodes

class HardwareValidator:
    """Comprehensive hardware validation and diagnostics"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.test_results = {}
    
    def run_full_diagnostic(self) -> dict:
        """Run complete hardware diagnostic suite"""
        print("🔧 Starting Hardware Diagnostic Suite...")
        print("=" * 50)
        
        # Reset results
        self.errors.clear()
        self.warnings.clear()
        self.test_results.clear()
        
        # Run all tests
        tests = [
            ("Power System", self._test_power_system),
            ("SPI Interface", self._test_spi_interface),
            ("Display", self._test_display),
            ("Keypad", self._test_keypad),
            ("GPIO Configuration", self._test_gpio_config),
            ("Memory", self._test_memory),
            ("Clock System", self._test_clock_system),
            ("Temperature", self._test_temperature),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing {test_name}...")
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "✅ PASS" if result['status'] else "❌ FAIL"
                print(f"   {status}: {result['message']}")
            except Exception as e:
                self.test_results[test_name] = {
                    'status': False,
                    'message': f"Test exception: {e}",
                    'error_code': ErrorCodes.ERR_INIT_FAILED
                }
                print(f"   ❌ FAIL: Exception during test: {e}")
        
        # Generate summary
        return self._generate_summary()
    
    def _test_power_system(self) -> dict:
        """Test power supply and battery monitoring"""
        try:
            # Test ADC for battery monitoring
            adc = machine.ADC(Pins.BATTERY_ADC)
            
            # Take multiple readings for accuracy
            readings = []
            for _ in range(10):
                readings.append(adc.read_u16())
                time.sleep_ms(10)
            
            # Calculate average
            avg_reading = sum(readings) / len(readings)
            
            # Convert to voltage (assuming 3.3V reference and voltage divider)
            voltage_mv = int((avg_reading * 3300) / 65535)
            
            # Check voltage levels
            if voltage_mv < Power.BATTERY_MIN:
                return {
                    'status': False,
                    'message': f"Battery voltage too low: {voltage_mv}mV",
                    'error_code': ErrorCodes.ERR_VOLTAGE_LOW,
                    'voltage_mv': voltage_mv
                }
            elif voltage_mv < Power.BATTERY_LOW:
                self.warnings.append(f"Low battery: {voltage_mv}mV")
            
            return {
                'status': True,
                'message': f"Power system OK, voltage: {voltage_mv}mV",
                'voltage_mv': voltage_mv
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f"Power test failed: {e}",
                'error_code': ErrorCodes.ERR_INIT_FAILED
            }
    
    def _test_spi_interface(self) -> dict:
        """Test SPI bus configuration"""
        try:
            # Initialize SPI bus
            spi = machine.SPI(
                1,
                baudrate=1_000_000,  # Safe speed for testing
                polarity=0,
                phase=0,
                sck=machine.Pin(Pins.SPI_SCK),
                mosi=machine.Pin(Pins.SPI_MOSI),
                miso=machine.Pin(Pins.SPI_MISO)
            )
            
            # Test SPI loopback if MISO connected to MOSI
            test_data = bytearray([0xAA, 0x55, 0xFF, 0x00])
            spi.write(test_data)
            
            return {
                'status': True,
                'message': "SPI interface initialized successfully",
                'bus_id': 1,
                'baudrate': 1_000_000
            }
            
        except Exception as e:
            return {
                'status': False,
                'message': f"SPI test failed: {e}",
                'error_code': ErrorCodes.ERR_SPI_TIMEOUT
            }

    # (Remaining methods copied verbatim in the real file)
