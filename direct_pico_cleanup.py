#!/usr/bin/env python3
"""
Direct cleanup using MicroPython REPL
"""

import serial
import time

COM_PORT = "COM3"
BAUD_RATE = 115200

# Files/directories to remove
TO_REMOVE = [
    "import os",
    "try:",
    "    os.rmdir('/firmware/games')",
    "except: pass",
    "try:",
    "    os.rmdir('/firmware')",
    "except: pass",
    "try:",
    "    os.rmdir('/libs')",
    "except: pass",
    "try:",
    "    os.rmdir('/drivers')",
    "except: pass",
    "try:",
    "    os.rmdir('/tools')",
    "except: pass",
    "try:",
    "    os.remove('/__init__.py')",
    "except: pass",
    "try:",
    "    os.remove('/boot.py')",
    "except: pass",
    "try:",
    "    os.remove('/config.json')",
    "except: pass",
    "try:",
    "    os.remove('/pico_manifest.json')",
    "except: pass",
    "try:",
    "    os.remove('/main_launcher.py')",
    "except: pass",
    "try:",
    "    os.remove('/device_smoke.py')",
    "except: pass",
    "try:",
    "    os.remove('/pico_updater.py')",
    "except: pass",
    "try:",
    "    os.remove('/periodic_ota.py')",
    "except: pass",
    "try:",
    "    os.remove('/pico_net_test.py')",
    "except: pass",
    "try:",
    "    os.remove('/network_helper.py')",
    "except: pass",
    "try:",
    "    os.remove('/display_sd.py')",
    "except: pass",
    "try:",
    "    os.remove('/file_browser.py')",
    "except: pass",
    "try:",
    "    os.remove('/decimal.py')",
    "except: pass",
    "try:",
    "    os.remove('/fractions.py')",
    "except: pass",
    "try:",
    "    os.remove('/statistics.py')",
    "except: pass",
    "try:",
    "    os.remove('/typing.py')",
    "except: pass",
    "try:",
    "    os.remove('/urequests.py')",
    "except: pass",
    "try:",
    "    os.remove('/ili9341.py')",
    "except: pass",
    "try:",
    "    import os",
    "    for f in os.listdir('/math'):",
    "        os.remove('/math/' + f)",
    "    os.rmdir('/math')",
    "except: pass",
    "print('Cleanup complete')",
]

def main():
    print("Connecting to Pico...")
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        time.sleep(0.5)
        
        # Send Ctrl+C to interrupt any running program
        ser.write(b'\x03')
        time.sleep(0.1)
        
        # Clear input buffer
        ser.read_all()
        
        print("Executing cleanup commands...")
        for cmd in TO_REMOVE:
            ser.write((cmd + '\r\n').encode())
            time.sleep(0.05)
            
        # Wait for execution
        time.sleep(2)
        
        # Read response
        response = ser.read_all().decode('utf-8', errors='ignore')
        print("\nPico Response:")
        print(response)
        
        ser.close()
        print("\n✅ Cleanup commands sent!")
        
    except serial.SerialException as e:
        print(f"❌ Error: {e}")
        print("Make sure Thonny is closed!")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
