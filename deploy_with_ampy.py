#!/usr/bin/env python3
"""
Deploy Calculator to Raspberry Pi Pico via COM port using ampy
"""

import subprocess
import sys
import time
from pathlib import Path

# Configuration
COM_PORT = "COM3"
SOURCE_DIR = Path(__file__).parent / "Broken_2.0"

# Files and directories to upload (in order)
UPLOAD_PLAN = [
    # Step 1: Create directories
    {
        'type': 'mkdir',
        'dirs': ['core', 'math', 'storage', 'ui', 'hardware', 'games', 
                'graphing', 'scientific', 'sd', 'settings']
    },
    
    # Step 2: Upload module __init__ files first
    {
        'type': 'files',
        'files': [
            ('core/__init__.py', 'core/__init__.py'),
            ('math/__init__.py', 'math/__init__.py'),
            ('storage/__init__.py', 'storage/__init__.py'),
            ('ui/__init__.py', 'ui/__init__.py'),
            ('hardware/__init__.py', 'hardware/__init__.py'),
            ('games/__init__.py', 'games/__init__.py'),
            ('graphing/__init__.py', 'graphing/__init__.py'),
            ('scientific/__init__.py', 'scientific/__init__.py'),
            ('sd/__init__.py', 'sd/__init__.py'),
            ('settings/__init__.py', 'settings/__init__.py'),
        ]
    },
    
    # Step 3: Upload module implementations
    {
        'type': 'files',
        'files': [
            ('core/app_state.py', 'core/app_state.py'),
            ('math/secure_engine.py', 'math/secure_engine.py'),
            ('storage/filesystem.py', 'storage/filesystem.py'),
            ('ui/ui_manager.py', 'ui/ui_manager.py'),
            ('hardware/display.py', 'hardware/display.py'),
            ('hardware/keypad.py', 'hardware/keypad.py'),
            ('hardware/power.py', 'hardware/power.py'),
            ('hardware/spi_manager.py', 'hardware/spi_manager.py'),
        ]
    },
    
    # Step 4: Upload supporting files
    {
        'type': 'files',
        'files': [
            ('enhanced_math_engine.py', 'enhanced_math_engine.py'),
            ('graphics_engine.py', 'graphics_engine.py'),
            ('statistical_plots.py', 'statistical_plots.py'),
            ('interactive_3d.py', 'interactive_3d.py'),
            ('hardware_config.py', 'hardware_config.py'),
            ('hardware_validator.py', 'hardware_validator.py'),
            ('usb_interface.py', 'usb_interface.py'),
        ]
    },
    
    # Step 5: Upload main calculator (last)
    {
        'type': 'files',
        'files': [
            ('calculator.py', 'calculator.py'),
        ]
    },
]

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
        # Ampy often returns error even on success for mkdir
        if 'mkdir' in description:
            print("✅ (may exist)")
            return True
        print(f"❌")
        if e.stderr:
            print(f"      Error: {e.stderr.strip()}")
        return False

def upload_file(local_file, remote_file):
    """Upload a single file"""
    local_path = SOURCE_DIR / local_file
    
    if not local_path.exists():
        print(f"  ⚠️  Skipping {local_file} (not found)")
        return True
    
    return run_ampy(['put', str(local_path), remote_file], f"Upload {local_file}")

def main():
    print("\n" + "="*70)
    print("  PEANUT 3000 CALCULATOR - DEPLOYMENT TO PICO")
    print("="*70)
    print(f"\n📍 Target Device: {COM_PORT}")
    print(f"📂 Source Directory: {SOURCE_DIR}")
    
    # Test connection
    print(f"\n📡 Testing connection...")
    try:
        result = subprocess.run(['ampy', '--port', COM_PORT, 'ls'], 
                              capture_output=True, text=True, timeout=10, check=True)
        print("✅ Connected to Pico successfully!")
        print(f"\nCurrent files on Pico:")
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                print(f"  • {line}")
        else:
            print("  (empty)")
    except Exception as e:
        print(f"\n❌ Failed to connect to {COM_PORT}")
        print("\nPlease check:")
        print("  1. Pico is connected to COM3")
        print("  2. No other program (Thonny, etc.) is using the port")
        print("  3. Pico is running MicroPython")
        return 1
    
    input("\n⚠️  Press ENTER to start upload (or Ctrl+C to cancel)...")
    
    success_count = 0
    fail_count = 0
    
    # Execute upload plan
    for step in UPLOAD_PLAN:
        if step['type'] == 'mkdir':
            print(f"\n📁 Creating directories...")
            for dir_name in step['dirs']:
                if run_ampy(['mkdir', dir_name], f"Create /{dir_name}"):
                    success_count += 1
                else:
                    fail_count += 1
                time.sleep(0.2)
                
        elif step['type'] == 'files':
            print(f"\n📤 Uploading files...")
            for local_file, remote_file in step['files']:
                if upload_file(local_file, remote_file):
                    success_count += 1
                else:
                    fail_count += 1
                time.sleep(0.3)
    
    # Summary
    print("\n" + "="*70)
    print("  DEPLOYMENT SUMMARY")
    print("="*70)
    print(f"✅ Successful operations: {success_count}")
    if fail_count > 0:
        print(f"❌ Failed operations: {fail_count}")
    
    if fail_count == 0:
        print("\n🎉 Deployment complete! Your calculator is ready.")
        print(f"\nTo run it, connect via serial and import calculator or reset the Pico.")
    else:
        print("\n⚠️  Some files failed to upload. You may need to retry.")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        sys.exit(1)
