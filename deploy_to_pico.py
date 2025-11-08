#!/usr/bin/env python3
"""
Deploy Calculator to Raspberry Pi Pico via COM port
Uses mpremote to upload all necessary files
"""

import subprocess
import sys
import time
from pathlib import Path

# Configuration
COM_PORT = "COM3"
SOURCE_DIR = Path(__file__).parent / "Broken_2.0"

# Files and directories to upload
FILES_TO_UPLOAD = [
    # Main calculator file
    "calculator.py",
    
    # Core modules
    "core/__init__.py",
    "core/app_state.py",
    
    # Math module
    "math/__init__.py",
    "math/secure_engine.py",
    
    # Storage module
    "storage/__init__.py",
    "storage/filesystem.py",
    
    # UI module
    "ui/__init__.py",
    "ui/ui_manager.py",
    
    # Hardware module
    "hardware/__init__.py",
    "hardware/display.py",
    "hardware/keypad.py",
    "hardware/power.py",
    "hardware/spi_manager.py",
    
    # Additional modules
    "enhanced_math_engine.py",
    "graphics_engine.py",
    "statistical_plots.py",
    "interactive_3d.py",
    "hardware_config.py",
    "hardware_validator.py",
    "performance_optimizer.py",
    "phase5_integration.py",
    "usb_interface.py",
    
    # Game modules
    "games/__init__.py",
    
    # Other modules
    "graphing/__init__.py",
    "scientific/__init__.py",
    "sd/__init__.py",
    "settings/__init__.py",
]

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: Command not found. Make sure mpremote is installed.")
        print(f"Install with: pip install mpremote")
        return False

def create_directory(dir_path):
    """Create a directory on the Pico"""
    cmd = ["mpremote", "connect", COM_PORT, "mkdir", f":{dir_path}"]
    # Don't fail if directory already exists
    subprocess.run(cmd, capture_output=True)

def upload_file(local_file, remote_file):
    """Upload a single file to the Pico"""
    local_path = SOURCE_DIR / local_file
    
    if not local_path.exists():
        print(f"⚠️  Skipping {local_file} (not found)")
        return True
    
    # Create parent directory if needed
    remote_dir = str(Path(remote_file).parent).replace('\\', '/')
    if remote_dir and remote_dir != '.':
        create_directory(remote_dir)
    
    cmd = ["mpremote", "connect", COM_PORT, "cp", str(local_path), f":{remote_file}"]
    return run_command(cmd, f"Uploading {local_file}")

def main():
    print("\n" + "="*60)
    print("  PEANUT 3000 CALCULATOR - DEPLOYMENT SCRIPT")
    print("="*60)
    print(f"\nTarget: {COM_PORT}")
    print(f"Source: {SOURCE_DIR}")
    
    # Test connection
    print("\n📡 Testing connection to Pico...")
    test_cmd = ["mpremote", "connect", COM_PORT, "version"]
    if not run_command(test_cmd, "Testing connection"):
        print("\n❌ Failed to connect to Pico. Please check:")
        print("   1. Pico is connected to COM3")
        print("   2. No other program is using the COM port")
        print("   3. Pico is running MicroPython")
        return 1
    
    print("\n✅ Connection successful!")
    
    # Create base directories
    print("\n📁 Creating directory structure...")
    directories = ["core", "math", "storage", "ui", "hardware", "games", 
                   "graphing", "scientific", "sd", "settings"]
    for dir_name in directories:
        create_directory(dir_name)
    
    # Upload files
    print("\n📤 Uploading files...")
    success_count = 0
    fail_count = 0
    
    for file in FILES_TO_UPLOAD:
        remote_path = file.replace('\\', '/')
        if upload_file(file, remote_path):
            success_count += 1
        else:
            fail_count += 1
        time.sleep(0.1)  # Small delay between uploads
    
    # Summary
    print("\n" + "="*60)
    print("  DEPLOYMENT SUMMARY")
    print("="*60)
    print(f"✅ Successfully uploaded: {success_count} files")
    if fail_count > 0:
        print(f"❌ Failed to upload: {fail_count} files")
    print("\n🎉 Deployment complete!")
    print("\nTo run the calculator:")
    print(f"  mpremote connect {COM_PORT} run calculator.py")
    print("\nOr reset the Pico to auto-run if main.py is configured.")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        sys.exit(1)
