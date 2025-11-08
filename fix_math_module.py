#!/usr/bin/env python3
"""
Fix math module name conflict - upload mathengine instead
"""

import subprocess
import sys
import time

COM_PORT = "COM3"

def run_ampy(args, description):
    """Run ampy command"""
    cmd = ['ampy', '--port', COM_PORT] + args
    print(f"  → {description}...", end=' ', flush=True)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
        print("✅")
        return True
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout")
        return False
    except subprocess.CalledProcessError as e:
        if 'mkdir' in description or 'rm' in description:
            print("✅ (ok)")
            return True
        print(f"❌")
        if e.stderr:
            print(f"      Error: {e.stderr.strip()}")
        return False

print("\n" + "="*70)
print("  Fix Math Module Name Conflict")
print("="*70)
print("\nClose Thonny before continuing!")
input("Press ENTER when ready...")

print("\n📤 Uploading fixes...")

# Remove old math directory
run_ampy(['rm', '-r', 'math'], "Remove old /math directory")
time.sleep(0.5)

# Create mathengine directory
run_ampy(['mkdir', 'mathengine'], "Create /mathengine directory")
time.sleep(0.3)

# Upload mathengine files
run_ampy(['put', 'Broken_2.0/mathengine/__init__.py', 'mathengine/__init__.py'], 
         "Upload mathengine/__init__.py")
time.sleep(0.3)

run_ampy(['put', 'Broken_2.0/mathengine/secure_engine.py', 'mathengine/secure_engine.py'], 
         "Upload mathengine/secure_engine.py")
time.sleep(0.3)

# Upload updated calculator.py
run_ampy(['put', 'Broken_2.0/calculator.py', 'calculator.py'], 
         "Upload updated calculator.py")

print("\n✅ Fix complete! Now you can import calculator in Thonny.")

