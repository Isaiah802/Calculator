#!/usr/bin/env python3
"""
Simple cleanup - paste this into Thonny REPL
"""

cleanup_code = """
import os

def safe_remove(path):
    try:
        os.remove(path)
        print(f"Removed: {path}")
    except:
        pass

def safe_rmdir(path):
    try:
        # Remove files first
        try:
            for f in os.listdir(path):
                try:
                    os.remove(path + '/' + f)
                except:
                    pass
        except:
            pass
        os.rmdir(path)
        print(f"Removed dir: {path}")
    except:
        pass

# Remove old files
safe_remove('/__init__.py')
safe_remove('/boot.py')
safe_remove('/config.json')
safe_remove('/pico_manifest.json')
safe_remove('/main_launcher.py')
safe_remove('/device_smoke.py')
safe_remove('/pico_updater.py')
safe_remove('/periodic_ota.py')
safe_remove('/pico_net_test.py')
safe_remove('/network_helper.py')
safe_remove('/display_sd.py')
safe_remove('/file_browser.py')
safe_remove('/decimal.py')
safe_remove('/fractions.py')
safe_remove('/statistics.py')
safe_remove('/typing.py')
safe_remove('/urequests.py')
safe_remove('/ili9341.py')

# Remove old directories
safe_rmdir('/math')
safe_rmdir('/firmware/games')
safe_rmdir('/firmware')
safe_rmdir('/libs')
safe_rmdir('/drivers')
safe_rmdir('/tools')

print("Cleanup complete!")
"""

print("="*70)
print("PICO CLEANUP CODE")
print("="*70)
print("\n1. Open Thonny")
print("2. Connect to your Pico (COM3)")
print("3. Copy the code below and paste it into the Thonny Shell")
print("4. Press Enter\n")
print("="*70)
print(cleanup_code)
print("="*70)

# Also save to file
with open('pico_cleanup_code.txt', 'w') as f:
    f.write(cleanup_code)
    
print("\n✅ Code also saved to: pico_cleanup_code.txt")
print("You can open it and copy/paste from there!")
