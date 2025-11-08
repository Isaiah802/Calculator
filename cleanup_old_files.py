#!/usr/bin/env python3
"""
Cleanup old/duplicate files from Pico before running new modular calculator
"""

import subprocess
import sys
import time

# Configuration
COM_PORT = "COM3"

# Old files to remove (that are now in modules or duplicates)
OLD_FILES_TO_REMOVE = [
    # Old firmware directory structure
    '/firmware',
    '/firmware/games',
    
    # Old standalone files
    '/libs',
    '/drivers',
    '/tools',
    
    # Config files that might conflict
    '/config.json',
    '/pico_manifest.json',
    
    # Old launcher/test files
    '/main_launcher.py',
    '/device_smoke.py',
    '/pico_updater.py',
    '/periodic_ota.py',
    '/pico_net_test.py',
    '/network_helper.py',
    
    # Old SD/display files
    '/display_sd.py',
    '/file_browser.py',
    '/sdcard.py',  # We have our own in storage module
    
    # Old standalone library files
    '/decimal.py',
    '/fractions.py',
    '/statistics.py',
    '/typing.py',
    '/urequests.py',
    '/ili9341.py',
    
    # Misc
    '/__init__.py',  # Root level init not needed
    '/boot.py',  # Unless you need it for boot config
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
        print(f"⚠️ (may not exist)")
        return True  # Don't fail if file doesn't exist

def list_files():
    """List current files on Pico"""
    try:
        result = subprocess.run(['ampy', '--port', COM_PORT, 'ls'], 
                              capture_output=True, text=True, timeout=10, check=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        return []

def main():
    print("\n" + "="*70)
    print("  PICO CLEANUP - Remove Old Files")
    print("="*70)
    print(f"\n📍 Target Device: {COM_PORT}")
    
    # Test connection
    print(f"\n📡 Testing connection...")
    current_files = list_files()
    if not current_files:
        print(f"\n❌ Failed to connect to {COM_PORT}")
        return 1
    
    print("✅ Connected!")
    print(f"\nCurrent files/directories on Pico: {len(current_files)}")
    
    print("\n⚠️  This will DELETE old files from your Pico.")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        return 0
    
    removed_count = 0
    
    print(f"\n🗑️  Removing old files...")
    for file_path in OLD_FILES_TO_REMOVE:
        if run_ampy(['rm', '-r', file_path], f"Remove {file_path}"):
            removed_count += 1
        time.sleep(0.2)
    
    # Summary
    print("\n" + "="*70)
    print("  CLEANUP SUMMARY")
    print("="*70)
    print(f"🗑️  Attempted to remove: {removed_count} items")
    
    print("\n✅ Cleanup complete!")
    print("\nRemaining important files:")
    final_files = list_files()
    for f in sorted(final_files):
        if not f.startswith('/_'):  # Hide hidden files
            print(f"  • {f}")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup cancelled by user")
        sys.exit(1)
